"""Utility functions for dev command instance type handling."""

from flow.sdk.client import Flow


def equivalent_instance_types(existing_type: str, requested_type: str, flow_client: Flow) -> bool:
    """
    Compare two instance types to determine if they are equivalent.

    Resolves both instance types to provider format for accurate comparison.
    This handles cases where the same instance type might be represented
    differently (e.g., '1xa100' vs 'a100-80gb.sxm.1x').

    Args:
        existing_type: The existing instance type (e.g., 'a100-80gb.sxm.1x')
        requested_type: The requested instance type (e.g., '1xa100')
        flow_client: Flow client for provider access

    Returns:
        True if the instance types are equivalent, False otherwise
    """
    if not existing_type or not requested_type:
        return existing_type == requested_type

    try:
        from flow.sdk.helpers.instance_resolution import resolve_instance_type

        provider = flow_client.get_remote_operations().provider
        resolved_existing_type = resolve_instance_type(provider, existing_type)
        resolved_requested_type = resolve_instance_type(provider, requested_type)

        # Compare both resolved types
        return resolved_existing_type.lower().strip() == resolved_requested_type.lower().strip()

    except Exception:  # noqa: BLE001
        # Fallback to simple string comparison if resolution fails
        return existing_type.lower().strip() == requested_type.lower().strip()
