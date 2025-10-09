"""Legacy `_internal` package compatibility.

This namespace previously housed implementation details. Public modules were
relocated under `flow.core.*`. Minimal shims are provided here to maintain
backwards compatibility for tests and downstream users.
"""

__all__ = ["data"]
