"""Deprecated: moved to flow.cli.ui.presentation.status_presenter.

This legacy module remains temporarily to ease migration.
"""

from __future__ import annotations

import warnings

from flow.cli.ui.presentation.status_presenter import (  # noqa: F401
    StatusDisplayOptions,
    StatusPresenter,
)

warnings.warn(
    "flow.cli.ui.presentation.status_presenter is deprecated; "
    "use flow.cli.ui.presentation.status_presenter instead",
    DeprecationWarning,
    stacklevel=2,
)
