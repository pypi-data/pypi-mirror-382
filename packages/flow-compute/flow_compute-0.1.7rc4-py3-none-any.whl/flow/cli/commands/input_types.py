"""Custom Click parameter types and validators for the CLI.

Includes helpers for environment variable items (``KEY=VALUE``) and parsing
port expressions into validated integers. Docstrings follow Google style.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence

import click


class EnvItem(click.ParamType):
    name = "KEY=VALUE"

    def convert(self, value, param, ctx):  # type: ignore[override]
        try:
            text = str(value)
        except Exception:  # noqa: BLE001
            self.fail("Invalid env item", param, ctx)
        if "=" not in text:
            self.fail("Expected KEY=VALUE (e.g., FOO=bar)", param, ctx)
        key, val = text.split("=", 1)
        key = key.strip()
        if not key:
            self.fail("KEY cannot be empty in KEY=VALUE", param, ctx)
        return (key, val)


def parse_ports_expression(expression: str) -> list[int]:
    """Parse a ports expression into a sorted unique list of ports.

    Supports comma/space separated numbers and ranges like ``3000-3002``.

    Args:
        expression: Ports expression, e.g. ``"8080,8888 3000-3002"``.

    Returns:
        Sorted list of unique port numbers.

    Raises:
        ValueError: If the input contains invalid numbers or ranges.
    """
    import re

    tokens = re.split(r"[\s,]+", (expression or "").strip())
    parsed: list[int] = []
    for token in tokens:
        if not token:
            continue
        if "-" in token:
            left, right = token.split("-", 1)
            try:
                start = int(left.strip())
                end = int(right.strip())
            except Exception:  # noqa: BLE001
                raise ValueError(f"Invalid range format: '{token}'")
            if start > end:
                start, end = end, start
            if end - start + 1 > 2000:
                raise ValueError(f"Range too large (max 2000): '{token}'")
            parsed.extend(range(start, end + 1))
        else:
            try:
                parsed.append(int(token))
            except Exception:  # noqa: BLE001
                raise ValueError(f"Invalid port number: '{token}'")
    return sorted(set(parsed))


class PortsExpr(click.ParamType):
    """Parses comma/space/range expressions into a list of ports.

    Example: "8080,8888 3000-3002" -> [3000, 3001, 3002, 8080, 8888]
    """

    name = "PORTS"

    def convert(self, value, param, ctx):  # type: ignore[override]
        try:
            ports = parse_ports_expression(str(value))
        except ValueError as ve:
            raise click.BadParameter(str(ve))
        return ports


def merge_ports_expr(values: Sequence[Sequence[int]]) -> list[int]:
    """Merge multiple port lists into a single sorted unique list."""
    merged: list[int] = []
    for seq in values or ():
        merged.extend(seq or [])
    return sorted({int(p) for p in merged})


def validate_ports_range(
    ports: Iterable[int], *, min_port: int, max_port: int, allowed_extras: set[int] | None = None
) -> list[int]:
    """Validate that all ports fall within a range, allowing extras.

    Args:
        ports: Iterable of port integers to validate.
        min_port: Minimum allowed port value.
        max_port: Maximum allowed port value.
        allowed_extras: Specific ports allowed outside the range.

    Returns:
        Sorted list of unique, validated ports.

    Raises:
        click.BadParameter: If a port is outside the allowed values.
    """
    allowed_extras = allowed_extras or set()
    cleaned: list[int] = []
    for p in ports or ():
        pi = int(p)
        if pi in allowed_extras:
            cleaned.append(pi)
            continue
        if pi < min_port or pi > max_port:
            raise click.BadParameter(
                f"Invalid port {pi}. Allowed: {', '.join(map(str, sorted(allowed_extras)))} or {min_port}-{max_port}"
            )
        cleaned.append(pi)
    return sorted(set(cleaned))


class PortNumber(click.ParamType):
    """Validates a single port number in range 1-65535 by default."""

    name = "PORT"

    def __init__(self, *, min_port: int = 1, max_port: int = 65535):
        self.min_port = int(min_port)
        self.max_port = int(max_port)

    def convert(self, value, param, ctx):  # type: ignore[override]
        try:
            pi = int(value)
        except Exception:  # noqa: BLE001
            raise click.BadParameter("Port must be an integer")
        if pi < self.min_port or pi > self.max_port:
            raise click.BadParameter(f"Port must be in range {self.min_port}-{self.max_port}")
        return pi
