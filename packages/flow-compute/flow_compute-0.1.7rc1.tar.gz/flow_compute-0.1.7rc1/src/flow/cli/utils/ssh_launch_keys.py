"""Shared helpers for resolving SSH keys for launches.

This module centralizes the logic for determining which SSH keys to use when
starting a dev VM or submitting a task from the CLI. It keeps the CLI policy
simple, consistent, and provider-agnostic while allowing providers to perform
the heavy lifting (e.g., uploading local keys, auto-generating, and mapping
platform key IDs to local private keys).

Resolution order (first hit wins):
1) Explicit CLI values (``-k/--ssh-keys``), if any.
2) ``MITHRIL_SSH_KEYS`` environment (comma-separated list).
3) ``MITHRIL_SSH_KEY`` environment (single path or platform ID).
4) Provider config ``ssh_keys`` (e.g., under ``mithril`` provider).
5) Best-effort ensure of a default project SSH key (returns a key id) via
   ``Flow.ensure_default_ssh_key``.

The output is a list of key references suitable for passing directly into
``TaskConfig.ssh_keys`` or provider submission APIs. Providers are responsible
for ensuring platform representation for local key references.
"""

from __future__ import annotations

from collections.abc import Iterable


def ensure_default_project_ssh_key(flow_client) -> str | None:
    """Attempt to ensure a default SSH key exists for the current project.

    Wraps ``Flow.ensure_default_ssh_key`` safely. Returns the created key id
    when one is created; returns None if a key already exists or if the
    operation is unsupported/unavailable.

    Args:
        flow_client: An instance of ``flow.sdk.client.Flow``.

    Returns:
        Optional[str]: The created key id, or None on no-op/unsupported.
    """
    try:
        if hasattr(flow_client, "ensure_default_ssh_key"):
            return flow_client.ensure_default_ssh_key()
    except Exception:  # noqa: BLE001
        # Best-effort only; failures should not block the caller
        return None
    return None


def _parse_env_list(value: str | None) -> list[str]:
    """Parse a comma-separated env var into a list of non-empty values.

    Args:
        value: Raw string (e.g., ``"a,b , c"``) or None.

    Returns:
        List[str]: Trimmed, non-empty items.
    """
    if not value:
        return []
    try:
        parts = [p.strip() for p in value.split(",")]
        return [p for p in parts if p]
    except Exception:  # noqa: BLE001
        return []


def resolve_launch_ssh_keys(flow_client, cli_keys: Iterable[str] | None) -> list[str]:
    """Resolve effective SSH keys to use for a launch from CLI/context.

    The helper is deliberately conservative: it avoids performing network calls
    beyond a best-effort default key ensure and relies on the provider to
    normalize references into platform key IDs later in the submission flow.

    Args:
        flow_client: An instance of ``flow.sdk.client.Flow``.
        cli_keys: Iterable of key references provided explicitly via CLI
            (``-k/--ssh-keys``). May be a tuple from Click.

    Returns:
        List[str]: Effective key references. Empty when none resolve.
    """
    # 1) CLI explicit values (highest precedence)
    if cli_keys:
        try:
            keys_list = [k for k in list(cli_keys) if isinstance(k, str) and k.strip()]
        except Exception:  # noqa: BLE001
            keys_list = []
        if keys_list:
            return keys_list

    # 2) MITHRIL_SSH_KEYS (plural env)
    try:
        import os as _os

        env_keys = _os.getenv("MITHRIL_SSH_KEYS")
        parsed_env_keys = _parse_env_list(env_keys)
        if parsed_env_keys:
            return parsed_env_keys
    except Exception:  # noqa: BLE001
        pass

    # 3) MITHRIL_SSH_KEY (singular env) — single reference
    try:
        import os as _os

        single_key = _os.getenv("MITHRIL_SSH_KEY")
        if not single_key:
            # Back-compat for legacy env name
            single_key = _os.getenv("Mithril_SSH_KEY")
        if single_key and single_key.strip():
            return [single_key.strip()]
    except Exception:  # noqa: BLE001
        pass

    # 4) Provider config (e.g., mithril.ssh_keys)
    provider_cfg = {}
    try:
        cfg = getattr(flow_client, "config", None)
        pcfg = getattr(cfg, "provider_config", None)
        if isinstance(pcfg, dict):
            provider_cfg = pcfg
    except Exception:  # noqa: BLE001
        provider_cfg = {}
    cfg_keys = provider_cfg.get("ssh_keys") if isinstance(provider_cfg, dict) else None
    if isinstance(cfg_keys, list) and cfg_keys:
        return [str(k) for k in cfg_keys if str(k).strip()]

    # 5) Best-effort ensure a default project key and use it when created
    created_key_id = ensure_default_project_ssh_key(flow_client)
    if created_key_id:
        return [created_key_id]

    # Nothing resolved
    return []
