"""Standardized CLI exit codes for Flow commands.

These constants centralize exit semantics for tests and callers.
Adopt but do not yet enforce across all commands.
"""

# Success
SUCCESS = 0

# Common error classes
GENERIC_ERROR = 1
AUTH_ERROR = 2
VALIDATION_ERROR = 3
NOT_FOUND = 4
USAGE_ERROR = 64  # EX_USAGE convention

# Signals / interrupts
INTERRUPTED = 130

__all__ = [
    "AUTH_ERROR",
    "GENERIC_ERROR",
    "INTERRUPTED",
    "NOT_FOUND",
    "SUCCESS",
    "USAGE_ERROR",
    "VALIDATION_ERROR",
]
