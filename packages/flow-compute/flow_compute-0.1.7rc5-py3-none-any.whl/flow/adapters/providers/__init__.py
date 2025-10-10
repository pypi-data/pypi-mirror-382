from __future__ import annotations

# Namespace for provider adapter entry points.

# Import builtin providers to ensure they register themselves
try:
    import flow.adapters.providers.builtin.local
except ImportError:
    pass

try:
    import flow.adapters.providers.builtin.mithril
except ImportError:
    pass

try:
    import flow.adapters.providers.mock  # noqa: F401
except ImportError:
    pass
