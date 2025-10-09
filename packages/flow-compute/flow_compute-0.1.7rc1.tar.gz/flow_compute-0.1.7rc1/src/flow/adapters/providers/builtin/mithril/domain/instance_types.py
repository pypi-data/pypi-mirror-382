"""Mithril-specific instance type adapter with dynamic region overrides."""

from __future__ import annotations

import logging
import time
from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING

from flow.adapters.providers.builtin.mithril.core.constants import (
    INSTANCE_TYPE_MAPPINGS,
    INSTANCE_TYPE_NAMES,
    VALID_REGIONS,
)
from flow.domain.parsers.instance_parser import InstanceParser
from flow.errors import FlowError
from flow.protocols.instance_types import InstanceTypeResolverProtocol

if TYPE_CHECKING:  # pragma: no cover - import cycle guard for type checkers only
    from flow.adapters.providers.builtin.mithril.api.client import MithrilApiClient


logger = logging.getLogger(__name__)


class InstanceTypeResolver(InstanceTypeResolverProtocol):
    """Mithril-specific instance type resolver.

    Adapts domain InstanceTypeRegistry to work with Mithril's
    specific mappings and IDs.
    """

    def __init__(
        self,
        api: MithrilApiClient,
        *,
        ttl: float = 300.0,
    ):
        """Initialize resolver with static mappings and dynamic hydration."""
        self._api = api
        self._ttl = float(ttl)
        self._regions: tuple[str, ...] = tuple(
            dict.fromkeys(region.strip() for region in VALID_REGIONS if region and region.strip())
        )
        if not self._regions:
            raise ValueError("Mithril InstanceTypeResolver requires at least one valid region")

        # Static baseline mappings (lower-case keys for consistency)
        self._map: dict[str, str] = {k.lower(): v for k, v in INSTANCE_TYPE_MAPPINGS.items()}
        self._static_map: dict[str, str] = dict(self._map)
        self._names: dict[str, str] = dict(INSTANCE_TYPE_NAMES or {})
        self._family_ids: dict[str, list[str]] = self._build_family_index(self._names)
        self._last_refresh: float | None = None

    def resolve(self, user_spec: str) -> str:
        """Resolve user-friendly spec (e.g., "a100", "4xa100") to a Mithril ID.

        Raises FlowError with helpful suggestions when resolution fails.
        """
        if not user_spec:
            raise FlowError("Instance type specification is required")

        normalized_spec = user_spec.lower().strip()

        # Direct ID passthrough does not need hydration.
        if normalized_spec.startswith("it_"):
            return user_spec.strip()

        self._ensure_region_overrides()

        for key in self._iter_lookup_keys(normalized_spec):
            mapped = self._map.get(key)
            if mapped:
                return mapped

        available_types = list(self._map.keys())
        raise FlowError(
            f"Unknown instance type: {user_spec}",
            suggestions=[
                f"Available: {', '.join(available_types[:5])}...",
                "Use 'flow pricing --list' to see all available instance types",
                "Examples: 'a100', '4xa100', '8xh100'",
            ],
        )

    def resolve_simple(self, spec: str) -> str:
        """Simple exact resolution using the static mapping (no canonicalization)."""
        normalized = spec.lower().strip()
        if normalized.startswith("it_"):
            return spec.strip()
        self._ensure_region_overrides()
        if normalized in self._map:
            return self._map[normalized]
        available = sorted(self._map.keys())
        raise ValueError(f"Unknown instance type: {spec}. Available: {', '.join(available)}")

    def candidate_ids(self, user_spec: str) -> list[str]:
        """Return candidate instance type IDs for a spec, covering variants.

        For H100, consider both SXM and PCIe 8x variants to allow region-specific
        availability differences.
        """
        candidates: list[str] = []
        primary = self.resolve(user_spec)
        candidates.append(primary)

        spec_lower = (user_spec or "").lower()
        if any(token in spec_lower for token in ("h100", "xh100")):
            for alt_id in self._family_ids.get("h100", []):
                if alt_id not in candidates:
                    candidates.append(alt_id)
        if spec_lower in {"a100", "1xa100"}:
            for alt in (
                "a100-80gb.sxm.1x",
                "a100-80gb.sxm.2x",
                "a100-80gb.sxm.4x",
                "a100-80gb.sxm.8x",
            ):
                try:
                    alt_id = self.resolve(alt)
                except FlowError:
                    continue
                if alt_id not in candidates:
                    candidates.append(alt_id)

        # Fallback to just returning any that resolved
        return candidates

    def normalize_request(
        self, gpu_count: int, gpu_type: str | None = None
    ) -> tuple[str, int, str | None]:
        """Normalize a (count, type) request into (instance_type, num_instances, warning).

        Enforces provider-specific constraints (e.g., H100 only in 8x nodes).
        """
        if not gpu_type:
            gpu_type = "h100"
        gpu_type = gpu_type.lower().strip()

        # H100: only 8x nodes; round up to nearest multiple of 8
        if gpu_type == "h100":
            num_nodes = (gpu_count + 7) // 8
            actual_gpus = num_nodes * 8
            warning: str | None = None
            if actual_gpus != gpu_count:
                warning = (
                    "H100s only available in 8-GPU nodes. Allocating "
                    f"{actual_gpus} GPUs ({num_nodes} node{'s' if num_nodes > 1 else ''})."
                )
            return "8xh100", num_nodes, warning

        # Prefer 8x, then 4x, then 2x, else 1x
        if gpu_count >= 8 and gpu_count % 8 == 0:
            return f"8x{gpu_type}", gpu_count // 8, None
        if gpu_count >= 4 and gpu_count % 4 == 0:
            return f"4x{gpu_type}", gpu_count // 4, None
        if gpu_count >= 2 and gpu_count % 2 == 0:
            return f"2x{gpu_type}", gpu_count // 2, None
        return gpu_type, gpu_count, None

    @staticmethod
    def _parse_key(user_spec: str) -> str:
        """Parse user spec into a normalized key present in mapping.

        Accepts inputs like "a100", "4xa100", "8xh100", or canonical long forms
        like "h100-80gb.sxm.8x" and returns the same when appropriate.
        """
        s = (user_spec or "").strip().lower()
        if not s:
            return s
        # If already in dotted long form, return as-is
        if "." in s and any(tok in s for tok in ("sxm", "pcie")):
            return s
        # If it looks like N x gpu
        if "x" in s:
            left, right = s.split("x", 1)
            try:
                _ = int(left)
                return f"{left}x{right}"
            except ValueError:
                return s
        return s

    def _ensure_region_overrides(self) -> None:
        """Load region overrides if configured."""
        now = time.monotonic()
        if self._last_refresh is not None and (now - self._last_refresh) < self._ttl:
            return
        self._hydrate_overrides()
        self._last_refresh = time.monotonic()

    def _hydrate_overrides(self) -> None:
        """Fetch availability once and merge overrides across all regions."""
        payloads = self._fetch_availability()
        overrides: set[str] = set()

        for raw_payload in payloads:
            if not isinstance(raw_payload, Mapping):
                raise FlowError(f"Unexpected spot availability payload type: {type(raw_payload)!r}")

            instance_fid = raw_payload.get("instance_type")
            if not isinstance(instance_fid, str) or not instance_fid.startswith("it_"):
                raise FlowError("Spot availability payload missing valid instance_type fid")

            region = raw_payload.get("region")
            if not isinstance(region, str) or not region:
                raise FlowError("Spot availability payload missing region")
            if region not in self._regions:
                continue

            display_name = INSTANCE_TYPE_NAMES.get(instance_fid)
            if not display_name:
                continue

            aliases = self._derive_aliases(display_name)
            if not aliases:
                continue

            self._names[instance_fid] = display_name
            family = self._detect_family(display_name) or self._detect_family(",".join(aliases))
            if family:
                self._record_family_member(family, instance_fid)

            for alias in aliases:
                key = alias.lower().strip()
                if not key:
                    continue

                original_fid = self._static_map.get(key)
                if key in overrides and original_fid and instance_fid == original_fid:
                    continue

                if instance_fid != self._map.get(key):
                    if original_fid is None or instance_fid != original_fid:
                        overrides.add(key)
                    self._map[key] = instance_fid

        if not overrides:
            logger.debug("Mithril availability returned no overrides; using existing mappings")
            return

        logger.debug("Hydrated Mithril instance overrides: %s", ", ".join(sorted(overrides)))

    def _fetch_availability(self) -> Sequence[Mapping[str, object]]:
        try:
            response = self._api.list_spot_availability({})
        except Exception as exc:
            raise FlowError("Failed to query Mithril spot availability") from exc

        if not isinstance(response, Sequence):
            raise FlowError(f"Unexpected spot availability response type: {type(response)!r}")
        if not response:
            logger.debug("No Mithril availability data returned from spot availability endpoint")
        return response

    def _iter_lookup_keys(self, normalized_spec: str) -> list[str]:
        keys = [normalized_spec]
        parsed = self._parse_key(normalized_spec)
        if parsed and parsed not in keys:
            keys.append(parsed)
        return keys

    @staticmethod
    def _derive_aliases(display_name: str) -> set[str]:
        aliases: set[str] = set()
        if not display_name:
            return aliases

        name = display_name.strip()
        if not name:
            return aliases

        lowered = name.lower()
        aliases.add(lowered)

        try:
            components = InstanceParser.parse(lowered)
        except Exception:  # noqa: BLE001
            components = None

        if components:
            if components.gpu_count > 1:
                aliases.add(f"{components.gpu_count}x{components.gpu_type}")
            aliases.add(components.gpu_type)

        return {alias for alias in aliases if alias}

    @staticmethod
    def _detect_family(value: str | None) -> str | None:
        if not value:
            return None
        lowered = value.lower()
        for family in ("h100", "a100"):
            if family in lowered:
                return family
        return None

    @staticmethod
    def _synthesize_display_name(instance_fid: str) -> str:
        if not instance_fid or "_" not in instance_fid:
            return instance_fid or "unknown-instance"
        return instance_fid.split("_", 1)[1]

    @staticmethod
    def _build_family_index(names: Mapping[str, str]) -> dict[str, list[str]]:
        index: dict[str, list[str]] = {}
        for instance_fid, display_name in names.items():
            family = InstanceTypeResolver._detect_family(display_name)
            if not family:
                continue
            members = index.setdefault(family, [])
            if instance_fid not in members:
                members.append(instance_fid)
        return index

    def _record_family_member(self, family: str, instance_fid: str) -> None:
        members = self._family_ids.setdefault(family, [])
        if instance_fid not in members:
            members.append(instance_fid)
