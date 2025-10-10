"""Centralized SSH endpoint resolver for Mithril provider.

Resolves the best SSH host and port for a bid (task) by consulting provider
APIs with correct scoping, normalizing statuses, and performing an optional
TCP probe to prefer endpoints that are already accepting connections.

This module is intentionally provider-scoped but free of CLI/UI coupling. Both
the CLI and provider remote ops should use this resolver for consistent
behavior.
"""

from __future__ import annotations

import logging
import time as _t
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from flow.adapters.providers.builtin.mithril.api.client import MithrilApiClient
from flow.adapters.providers.builtin.mithril.domain.instances import InstanceService
from flow.adapters.transport.ssh.ssh_stack import SshStack

logger = logging.getLogger(__name__)


def _safe_parse_iso8601(ts: object) -> datetime | None:
    try:
        if isinstance(ts, datetime):
            return ts
        if isinstance(ts, str):
            return datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except Exception:  # noqa: BLE001
        return None
    return None


def _is_dead_status(status: object) -> bool:
    try:
        s = str(status or "").strip().lower()
    except Exception:  # noqa: BLE001
        return False
    if s.startswith("status_"):
        s = s.replace("status_", "")
    if "termin" in s or "cancel" in s:
        return True
    return s in {"terminated", "cancelled", "failed"}


def _is_public_ipv4(ip: str) -> bool:
    """Return True only for literal, public IPv4 addresses.

    Previous logic treated any non-RFC1918-looking string as "public", which
    incorrectly included DNS hostnames (e.g., bastion endpoints). That caused
    the resolver to prefer a bastion hostname over the instance's actual
    public IPv4, leading to SSH resets when the bastion wasn't the correct
    target for direct SSH.

    Use ipaddress parsing to ensure the value is an IPv4 literal and is
    globally routable (not private, loopback, link-local, multicast, or
    reserved).
    """
    try:
        from ipaddress import ip_address

        addr = ip_address(str(ip))
        # is_global implies not private/loopback/link-local/multicast/reserved
        return getattr(addr, "version", 0) == 4 and getattr(addr, "is_global", False)
    except Exception:  # noqa: BLE001
        # Not a literal IP (likely a hostname) → not a public IPv4
        return False


def _dedupe_preserve_order(values: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for v in values:
        if v not in seen:
            seen.add(v)
            out.append(v)
    return out


@dataclass
class ResolveOptions:
    node: int | None = None
    tcp_probe: bool = True
    max_ids_to_check: int = 5
    debug: bool = False


class SshEndpointResolver:
    """Resolves SSH host/port for Mithril tasks (bids)."""

    def __init__(
        self,
        api: MithrilApiClient,
        get_project_id: Callable[[], str],
        instance_service: InstanceService,
    ) -> None:
        self._api = api
        self._get_project_id = get_project_id
        self._instances = instance_service
        # lightweight cache: (bid_id, node) -> (host, port, ts)
        self._cache: dict[tuple[str, int], tuple[str, int, float]] = {}

    def resolve(
        self, bid_id: str, *, node: int | None = None, tcp_probe: bool = True, debug: bool = False
    ) -> tuple[str, int]:
        opts = ResolveOptions(node=node, tcp_probe=tcp_probe, debug=debug)
        bid = self._fetch_bid(bid_id)
        instances = bid.get("instances", []) or []

        if not isinstance(instances, list) or not instances:
            try:
                docs = self._instances.list_project_instances_by_bid(bid_id, max_pages=3)
                # Use these enriched docs directly as the instance list
                instances = docs if isinstance(docs, list) else []
            except Exception:  # noqa: BLE001
                instances = []
        if not isinstance(instances, list) or not instances:
            raise ValueError("No instances associated with bid")

        # Node-specific selection overrides generic selection
        if opts.node is not None:
            if opts.node < 0 or opts.node >= len(instances):
                raise ValueError(
                    f"Invalid node index {opts.node}; bid has {len(instances)} instances"
                )
            chosen_raw = instances[opts.node]
            chosen = self._enrich_instance(chosen_raw)

            # If the chosen instance doesn't have a valid SSH endpoint, fall back to best instance
            # This can happen when specific node isn't fully provisioned yet
            if chosen:
                _, _, candidates = self._extract_endpoint_candidates(chosen)
                if not candidates:
                    if opts.debug:
                        logger.debug(
                            "ssh-resolver node %d has no SSH endpoint, falling back to best instance",
                            opts.node,
                        )
                    chosen = self._select_best_instance(instances, opts)
        else:
            chosen = self._select_best_instance(instances, opts)

        if not isinstance(chosen, dict):
            raise TypeError("Unable to select a valid instance for SSH resolution")

        host, port, candidates = self._extract_endpoint_candidates(chosen)
        if opts.debug:
            try:
                logger.debug(
                    "ssh-resolver bid=%s selected_instance=%s status=%s candidates=%s",
                    bid_id,
                    chosen.get("fid") or chosen.get("id"),
                    chosen.get("status"),
                    candidates,
                )
            except Exception:  # noqa: BLE001
                pass

        if not candidates and not host:
            raise ValueError("No public endpoint available yet")

        # Build final candidate list: prefer parsed host first if present
        ordered_candidates: list[str] = []
        if host:
            ordered_candidates.append(str(host))
        for c in candidates:
            if c not in ordered_candidates:
                ordered_candidates.append(str(c))

        # Prefer public IPv4s first
        public_candidates = [c for c in ordered_candidates if _is_public_ipv4(str(c))]
        if opts.tcp_probe:
            # 1) Prefer endpoints that present a real SSH banner
            for ip in public_candidates:
                has_banner = SshStack.has_ssh_banner(str(ip), port)
                if opts.debug:
                    logger.debug(
                        "ssh-resolver banner %s:%s -> %s",
                        ip,
                        port,
                        "ssh" if has_banner else "none",
                    )
                if has_banner:
                    if opts.debug:
                        logger.debug("ssh-resolver selected host (banner): %s:%s", ip, port)
                    return str(ip), port
            for ip in ordered_candidates:
                has_banner = SshStack.has_ssh_banner(str(ip), port)
                if opts.debug:
                    logger.debug(
                        "ssh-resolver banner (non-public) %s:%s -> %s",
                        ip,
                        port,
                        "ssh" if has_banner else "none",
                    )
                if has_banner:
                    if opts.debug:
                        logger.debug(
                            "ssh-resolver selected host (banner, non-public): %s:%s", ip, port
                        )
                    return str(ip), port

            # 2) Fallback to plain TCP-open preference
            for ip in public_candidates:
                is_open = SshStack.tcp_port_open(str(ip), port)
                if opts.debug:
                    logger.debug(
                        "ssh-resolver tcp %s:%s -> %s", ip, port, "open" if is_open else "closed"
                    )
                if is_open:
                    if opts.debug:
                        logger.debug("ssh-resolver selected host (open): %s:%s", ip, port)
                    return str(ip), port
            for ip in ordered_candidates:
                is_open = SshStack.tcp_port_open(str(ip), port)
                if opts.debug:
                    logger.debug(
                        "ssh-resolver tcp (non-public) %s:%s -> %s",
                        ip,
                        port,
                        "open" if is_open else "closed",
                    )
                if is_open:
                    if opts.debug:
                        logger.debug(
                            "ssh-resolver selected host (open, non-public): %s:%s", ip, port
                        )
                    return str(ip), port

        # Fallback to first public, else first overall
        if public_candidates:
            if opts.debug:
                logger.debug(
                    "ssh-resolver selected host (first public): %s:%s", public_candidates[0], port
                )
            return str(public_candidates[0]), port
        if ordered_candidates:
            if opts.debug:
                logger.debug(
                    "ssh-resolver selected host (first overall): %s:%s", ordered_candidates[0], port
                )
            return str(ordered_candidates[0]), port

        raise ValueError("No suitable SSH endpoint found")

    def resolve_with_cache(
        self,
        bid_id: str,
        *,
        node: int | None = None,
        tcp_probe: bool = True,
        debug: bool = False,
        ttl_seconds: float = 15.0,
    ) -> tuple[str, int]:
        """Resolve with a small in-memory TTL cache.

        Caches the (host, port) per (bid_id, node) for ttl_seconds to reduce
        repeated API calls and TCP probes during frequent lookups.
        """
        key = (bid_id, int(node or -1))
        now = _t.time()
        try:
            cached = self._cache.get(key)
            if cached:
                host, port, ts = cached
                if now - ts < ttl_seconds:
                    return host, port
        except Exception:  # noqa: BLE001
            pass

        host, port = self.resolve(bid_id, node=node, tcp_probe=tcp_probe, debug=debug)
        try:
            self._cache[key] = (host, port, now)
        except Exception:  # noqa: BLE001
            pass
        return host, port

    # -------------------------- helpers --------------------------

    def _fetch_bid(self, bid_id: str) -> dict[str, Any]:
        """Spec-compliant fetch: page by project and filter locally by fid/id."""
        next_cursor: str | None = None
        project: str | None = None
        try:
            project = self._get_project_id()
        except Exception:  # noqa: BLE001
            project = None
        for _ in range(10):
            params: dict[str, Any] = {}
            if project:
                params["project"] = project
            if next_cursor:
                params["next_cursor"] = next_cursor
            # Prefer newest first when supported
            params["sort_by"] = "created_at"
            params["sort_dir"] = "desc"
            # Be tolerant of strict servers: on 422 validation, retry with minimal params
            try:
                response = self._api.list_bids(params)
            except Exception as e:  # narrow to ValidationAPIError when importable  # noqa: BLE001
                try:
                    from flow.errors import ValidationAPIError  # local import

                    if isinstance(e, ValidationAPIError):
                        minimal: dict[str, Any] = {}
                        if project:
                            minimal["project"] = project
                        if next_cursor:
                            minimal["next_cursor"] = next_cursor
                        response = self._api.list_bids(minimal)
                    else:
                        raise
                except Exception:
                    # If importing error types fails or retry also fails, bubble up
                    raise
            data = response.get("data", response) if isinstance(response, dict) else response
            if isinstance(data, list):
                for b in data:
                    if not isinstance(b, dict):
                        continue
                    fid = b.get("fid") or b.get("id")
                    if fid == bid_id:
                        return b
                next_cursor = response.get("next_cursor") if isinstance(response, dict) else None
                if not next_cursor:
                    break
            elif isinstance(data, dict):
                # Some servers may return a single object
                fid = data.get("fid") or data.get("id")
                if fid == bid_id:
                    return data
                break
            else:
                break
        raise ValueError("Bid not found")

    def _enrich_instance(self, instance_like: Any) -> dict[str, Any] | None:
        if isinstance(instance_like, dict):
            return instance_like
        if isinstance(instance_like, str):
            try:
                return self._instances.get_instance(instance_like)
            except Exception:  # noqa: BLE001
                return None
        return None

    def _select_best_instance(
        self, instances: list[Any], opts: ResolveOptions
    ) -> dict[str, Any] | None:
        enriched: list[dict[str, Any]] = []
        for checked, inst in enumerate(reversed(instances)):
            item = self._enrich_instance(inst)
            if item:
                enriched.append(item)
            if checked + 1 >= opts.max_ids_to_check:
                break

        if not enriched:
            return None

        # Prefer non-terminated, newest by created_at when available
        live = [e for e in enriched if not _is_dead_status(e.get("status"))]

        def sort_key(e: dict[str, Any]):
            ts = _safe_parse_iso8601(e.get("created_at")) or _safe_parse_iso8601(e.get("createdAt"))
            return (ts or datetime.min,)

        if live:
            live_sorted = sorted(live, key=sort_key, reverse=True)
            return live_sorted[0]
        enriched_sorted = sorted(enriched, key=sort_key, reverse=True)
        return enriched_sorted[0]

    def _extract_endpoint_candidates(
        self, instance_doc: dict[str, Any]
    ) -> tuple[str | None, int, list[str]]:
        host: str | None = None
        port: int = 22
        candidates: list[str] = []

        ssh_destination = instance_doc.get("ssh_destination")
        if isinstance(ssh_destination, str) and ssh_destination:
            parts = ssh_destination.split(":")
            host = parts[0]
            try:
                port = int(parts[1]) if len(parts) > 1 else 22
            except Exception:  # noqa: BLE001
                port = 22

        try:
            ssh_port_val = instance_doc.get("ssh_port")
            if ssh_port_val is not None:
                p = int(ssh_port_val)
                if p > 0:
                    port = p
        except Exception:  # noqa: BLE001
            pass

        def add(val: Any) -> None:
            from re import fullmatch as _fullmatch

            if isinstance(val, str) and _fullmatch(r"\d+\.\d+\.\d+\.\d+", val):
                candidates.append(val)
            elif isinstance(val, list):
                for v in val:
                    add(v)
            elif isinstance(val, dict):
                for v in val.values():
                    add(v)

        add(instance_doc.get("public_ip"))
        add(instance_doc.get("publicIp"))
        add(instance_doc.get("publicIpAddress"))
        add(instance_doc.get("ip"))
        add(instance_doc.get("ip_address"))
        add(instance_doc.get("network"))
        add(instance_doc.get("addresses"))

        candidates = _dedupe_preserve_order(candidates)
        return host, port, candidates
