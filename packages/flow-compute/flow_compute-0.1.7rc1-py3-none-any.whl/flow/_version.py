"""Version utilities for Flow SDK.

Provides a single source of truth for the SDK version that is lightweight to
import from both runtime code and CLI entry points.
"""

from __future__ import annotations

import re
from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as metadata_version
from pathlib import Path

# Canonical package name as published on PyPI
PACKAGE_NAME = "flow-compute"


def _read_version_from_pyproject(pyproject_path: Path) -> str | None:
    """Best-effort read of project.version from a pyproject.toml file.

    Avoids adding a dependency on tomli/tomllib for Python 3.10 by using a
    minimal parse that looks for the first 'version = "..."' under [project].
    """
    try:
        if not pyproject_path.exists():
            return None
        in_project_table = False
        for raw_line in pyproject_path.read_text(encoding="utf-8", errors="ignore").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("[") and line.endswith("]"):
                in_project_table = line == "[project]"
                continue
            if in_project_table and line.startswith("version"):
                # e.g., version = "0.0.19"
                try:
                    _, value = line.split("=", 1)
                    value = value.strip().strip("'\"")
                    if value:
                        return value
                except Exception:  # noqa: BLE001
                    return None
        return None
    except Exception:  # noqa: BLE001
        return None


def get_version() -> str:
    """Return the installed package version or a sensible fallback.

    - First tries importlib.metadata for the installed distribution.
    - Falls back to reading pyproject.toml when running from a source checkout.
    - Ultimately returns "0.0.0+unknown" if neither is available.
    """
    try:
        return metadata_version(PACKAGE_NAME)
    except PackageNotFoundError:
        # Likely running from source; try to read pyproject.toml near repo root
        try:
            this_file = Path(__file__).resolve()
            # src/flow/_version.py -> repo_root/pyproject.toml
            pyproject = this_file.parents[2] / "pyproject.toml"
            parsed = _read_version_from_pyproject(pyproject)
            if parsed:
                return parsed
        except Exception:  # noqa: BLE001
            pass
        return "0.0.0+unknown"
    except Exception:  # noqa: BLE001
        return "0.0.0+unknown"


def parse_version(version_str: str | None) -> tuple[int, int, int, int, tuple]:
    """Parse version string into a tuple for safe comparison without packaging.

    Handles semantic versions like '1.2.3', optionally with pre-release/build
    metadata. Non-numeric parts are handled so that stable releases sort after
    pre-releases (e.g., 1.0.0 > 1.0.0rc1).

    Args:
        version_str: Version string to parse (e.g., "1.2.3", "1.0.0rc1")

    Returns:
        Tuple of (major, minor, patch, is_stable, (pre_rank, pre_num)) for comparison.
        Higher tuples represent newer versions.

    Examples:
        >>> parse_version("1.2.3") > parse_version("1.2.2")
        True
        >>> parse_version("1.0.0") > parse_version("1.0.0rc1")
        True
    """
    if not version_str:
        return (0, 0, 0, 1, ())

    # Extract core numeric parts and pre-release tag
    match = re.match(r"^(\d+)\.(\d+)(?:\.(\d+))?(.*)$", version_str)
    if not match:
        # Fallback: try to parse any digits we see
        digits = [int(x) for x in re.findall(r"\d+", version_str)[:3]]
        while len(digits) < 3:
            digits.append(0)
        # Treat unknown suffix as pre-release to keep it below stable
        return (digits[0], digits[1], digits[2], 0, (version_str,))

    major = int(match.group(1))
    minor = int(match.group(2))
    patch = int(match.group(3) or 0)
    suffix = match.group(4) or ""

    # Stable releases sort after pre-releases: use flag 1 for stable, 0 for pre
    # Post-releases (e.g., 1.0.0.post1 or 1.0.0post1) are also considered stable
    is_stable = (
        1
        if (
            suffix == ""
            or suffix.startswith(".post")
            or suffix.startswith("post")
            or suffix.startswith("+")
        )
        else 0
    )

    # Normalize well-known pre-release tags so they sort correctly
    # rc > beta > alpha
    if "rc" in suffix:
        pre_rank = 2
    elif "b" in suffix or "beta" in suffix:
        pre_rank = 1
    elif "a" in suffix or "alpha" in suffix:
        pre_rank = 0
    else:
        pre_rank = -1  # unknown; keep lowest

    # Extract any trailing number in the suffix, e.g., rc1 -> 1
    pre_num_match = re.search(r"(\d+)", suffix)
    pre_num = int(pre_num_match.group(1)) if pre_num_match else 0

    return (major, minor, patch, is_stable, (pre_rank, pre_num))


def is_stable_version(version_str: str | None) -> bool:
    """Check if a version string represents a stable release.

    Stable releases have no pre-release identifiers (alpha, beta, rc, etc.).

    Args:
        version_str: Version string to check (e.g., "1.2.3", "1.0.0rc1")

    Returns:
        True if the version is stable (no pre-release tags), False otherwise

    Examples:
        >>> is_stable_version("1.2.3")
        True
        >>> is_stable_version("1.0.0rc1")
        False
        >>> is_stable_version("1.0.0beta1")
        False
    """
    if not version_str:
        return False

    parsed = parse_version(version_str)
    # The 4th element (index 3) is the is_stable flag: 1 for stable, 0 for pre-release
    return parsed[3] == 1


# Public constant for convenient imports
__version__ = get_version()
