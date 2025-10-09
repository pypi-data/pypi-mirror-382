"""Periodic update check with stateful tracking for CLI notifications.

Checks PyPI to stay informed about new versions of Flow and notifies users.
"""

from __future__ import annotations

import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import Literal, TypedDict, cast

from flow._version import get_version as get_sdk_version
from flow._version import is_stable_version, parse_version
from flow.cli.utils.update_checker import UpdateChecker

logger = logging.getLogger(__name__)

# Environment variable names
# Seconds between PyPI checks (default: 6 hours)
ENV_UPDATE_CHECK_INTERVAL = "FLOW_UPDATE_CHECK_INTERVAL"
# Seconds between notifications (default: 3 days)
ENV_UPDATE_NOTIFICATION_INTERVAL = "FLOW_UPDATE_NOTIFICATION_INTERVAL"
# Force immediate check, bypassing cooldown (for testing)
ENV_UPDATE_CHECK_FORCE = "FLOW_UPDATE_CHECK_FORCE"
# Enable/disable update checks (set to 0/false/no to disable)
ENV_UPDATE_CHECK_ENABLED = "FLOW_UPDATE_CHECK"

# State storage configuration
STATE_DIR_NAME = ".flow"
STATE_FILE_NAME = "updates.json"
STATE_TMP_SUFFIX = ".tmp"

# State dictionary keys
STATE_KEY_LAST_CHECK_TIME = "last_check_time"
STATE_KEY_LATEST_KNOWN_VERSION = "latest_known_version"
STATE_KEY_LATEST_KNOWN_STABLE_VERSION = "latest_known_stable_version"
STATE_KEY_LAST_NOTIFIED_VERSION = "last_notified_version"
STATE_KEY_LAST_NOTIFICATION_TIME = "last_notification_time"
STATE_KEY_PREFERRED_RELEASE_TRACK = "preferred_release_track"

# Environment variable values
ENV_VALUE_TRUE = "1"
ENV_VALUE_FALSE = "0"
ENV_VALUES_DISABLED = {"0", "false", "no"}

# Check PyPI every 6 hours to stay informed
CHECK_INTERVAL_SECONDS = 6 * 60 * 60  # 6 hours
# Show notifications at most once per 3 days
NOTIFICATION_INTERVAL_SECONDS = 3 * 24 * 60 * 60  # 3 days

# Release track preferences
RELEASE_TRACK_STABLE = "stable"
RELEASE_TRACK_UNSTABLE = "unstable"


class UpdateState(TypedDict, total=False):
    """State dictionary for update tracking."""

    last_check_time: float
    latest_known_version: str
    latest_known_stable_version: str
    last_notified_version: str
    last_notification_time: float
    preferred_release_track: str  # "stable" or "unstable"


class UpdateNotifier:
    """Manages periodic update checks with stateful tracking.

    Design:
    - Checks PyPI regularly to stay informed about new releases
    - Shows notifications less frequently to avoid spam
    - Only notifies about versions we haven't told the user about yet

    Key insight: Separate "knowing about updates" from "telling the user"
    """

    def __init__(
        self,
        state_dir: Path | None = None,
        check_interval: int | None = None,
        notification_interval: int | None = None,
    ) -> None:
        """Initialize the notifier.

        Args:
            state_dir: Directory for state file (defaults to ~/.flow)
            check_interval: Seconds between PyPI checks (defaults to 6 hours)
            notification_interval: Seconds between notifications (defaults to 3 days)
        """
        self.state_dir = state_dir or Path.home() / STATE_DIR_NAME
        self.state_file = self.state_dir / STATE_FILE_NAME
        self._cached_state: UpdateState | None = None

        # Allow environment variable to override check interval
        default_check_interval = CHECK_INTERVAL_SECONDS
        env_check_interval = os.environ.get(ENV_UPDATE_CHECK_INTERVAL)
        if env_check_interval and env_check_interval.isdigit():
            default_check_interval = int(env_check_interval)

        self.check_interval = check_interval or default_check_interval

        # Allow environment variable to override notification interval
        default_notification_interval = NOTIFICATION_INTERVAL_SECONDS
        env_notification_interval = os.environ.get(ENV_UPDATE_NOTIFICATION_INTERVAL)
        if env_notification_interval and env_notification_interval.isdigit():
            default_notification_interval = int(env_notification_interval)

        self.notification_interval = notification_interval or default_notification_interval

        # Force check mode (for testing)
        self.force_check = os.environ.get(ENV_UPDATE_CHECK_FORCE, ENV_VALUE_FALSE) == ENV_VALUE_TRUE

    def _should_check_pypi(self) -> bool:
        """Determine if we should check PyPI for updates now.

        Returns:
            True if PyPI check should be performed, False otherwise
        """
        # Force check if requested (for testing)
        if self.force_check:
            return True

        # Skip in non-interactive sessions
        if not sys.stdout.isatty():
            return False

        # Respect explicit opt-out
        if os.environ.get(ENV_UPDATE_CHECK_ENABLED, ENV_VALUE_TRUE).strip() in ENV_VALUES_DISABLED:
            return False

        # Check if enough time has passed since last PyPI check
        state = self._get_state()
        last_check_time = state.get(STATE_KEY_LAST_CHECK_TIME, 0)
        time_since_check = time.time() - last_check_time

        return time_since_check >= self.check_interval

    def _should_notify(self, current_version: str, state: UpdateState) -> tuple[bool, str | None]:
        """Determine if we should show a notification to the user.

        This method consolidates all logic for deciding:
        - Which version to notify about (stable vs unstable)
        - Whether notification should be shown

        Args:
            current_version: Currently installed version
            state: Current state data containing latest_known_version and latest_known_stable_version

        Returns:
            Tuple of (should_notify, version_to_notify):
            - should_notify: True if notification should be shown
            - version_to_notify: The version to notify about, or None if no notification
        """
        # Get user's preferred release track, defaulting based on their current version
        preferred_track = state.get(STATE_KEY_PREFERRED_RELEASE_TRACK)
        if not preferred_track:
            # No preference set yet - infer from current version
            current_is_stable = is_stable_version(current_version)
            preferred_track = RELEASE_TRACK_STABLE if current_is_stable else RELEASE_TRACK_UNSTABLE

        # Choose which version to consider based on user's preference
        if preferred_track == RELEASE_TRACK_STABLE:
            # Stable track users should be notified about stable updates only
            version_to_notify = state.get(STATE_KEY_LATEST_KNOWN_STABLE_VERSION)
        else:
            # Unstable track users should be notified about any updates (including unstable)
            version_to_notify = state.get(STATE_KEY_LATEST_KNOWN_VERSION)

        # No version available to notify about
        if not version_to_notify:
            return (False, None)

        # No update available
        current = parse_version(current_version)
        latest = parse_version(version_to_notify)
        if latest <= current:
            return (False, None)

        # Check if we've already notified about this version
        last_notified_version = state.get(STATE_KEY_LAST_NOTIFIED_VERSION)
        if last_notified_version:
            last_notified = parse_version(last_notified_version)
            # Already notified about this or a newer version
            if latest <= last_notified:
                return (False, None)

        # Check if enough time has passed since last notification
        last_notification_time = state.get(STATE_KEY_LAST_NOTIFICATION_TIME, 0)
        time_since_notification = time.time() - last_notification_time

        if time_since_notification >= self.notification_interval:
            return (True, version_to_notify)

        return (False, None)

    def check_and_notify(self) -> None:
        """Check for updates and display notification if appropriate.

        This implements the two-phase design:
        1. Check PyPI regularly to stay informed about both stable and unstable versions
        2. Notify less regularly and only for new versions appropriate to the user

        Version selection logic:
        - Users are notified based on their preferred_release_track setting
        - Stable track: notified about new stable versions only
        - Unstable track: notified about any new versions (including unstable)
        - If no preference is set, inferred from current installed version

        This is the main entry point.
        """
        state = self._get_state()
        current_version = get_sdk_version()

        # Phase 1: Check PyPI if needed
        if self._should_check_pypi():
            checker = UpdateChecker(quiet=True, timeout=2.0)
            # Always check for all versions to get complete picture
            result = checker.check_for_updates(include_unstable=True)

            # Update our knowledge of both versions
            if result.latest_version:
                state[STATE_KEY_LATEST_KNOWN_VERSION] = result.latest_version
            if result.latest_stable_version:
                state[STATE_KEY_LATEST_KNOWN_STABLE_VERSION] = result.latest_stable_version

            # Only update timestamp if we got at least one version
            if result.latest_version or result.latest_stable_version:
                state[STATE_KEY_LAST_CHECK_TIME] = time.time()
                self._save_state(state)

        # Phase 2: Notify if appropriate
        should_notify, version_to_notify = self._should_notify(current_version, state)
        if should_notify and version_to_notify:
            self._display_notification(current_version, version_to_notify)
            # Update notification timestamp and version
            state[STATE_KEY_LAST_NOTIFICATION_TIME] = time.time()
            state[STATE_KEY_LAST_NOTIFIED_VERSION] = version_to_notify
            self._save_state(state)

    def _get_state(self) -> UpdateState:
        """Get state data, using in-memory cache if available.

        Returns an empty dict on first call when no state file exists yet.
        Subsequent calls return the cached state. Fields are added to the
        state dict over time as checks and notifications occur.

        Returns:
            UpdateState dict (may be empty if never persisted before)
        """
        if self._cached_state is None:
            self._cached_state = self._load_state()
        return self._cached_state.copy()

    def _validate_state(self, state: dict) -> dict:
        """Validate state data.

        Args:
            state: Raw state dictionary from disk

        Returns:
            Validated state dictionary

        Raises:
            ValueError: If state contains invalid data that can't be recovered
        """
        # Validate timestamps
        for key in [STATE_KEY_LAST_CHECK_TIME, STATE_KEY_LAST_NOTIFICATION_TIME]:
            if key in state:
                value = state[key]
                if not isinstance(value, int | float):
                    raise ValueError(f"Invalid timestamp type for {key}")
                if value < 0:
                    raise ValueError(f"Negative timestamp for {key}")

        # Validate version strings can be parsed
        for key in [
            STATE_KEY_LATEST_KNOWN_VERSION,
            STATE_KEY_LATEST_KNOWN_STABLE_VERSION,
            STATE_KEY_LAST_NOTIFIED_VERSION,
        ]:
            if key in state:
                version_str = state[key]
                if not isinstance(version_str, str):
                    raise ValueError(f"Invalid version string type for {key}")
                # Verify it can be parsed (parse_version handles None/empty gracefully)
                try:
                    parse_version(version_str)
                except Exception as e:
                    raise ValueError(f"Invalid version string for {key}: {version_str}") from e

        # Validate preferred_release_track
        if STATE_KEY_PREFERRED_RELEASE_TRACK in state:
            track = state[STATE_KEY_PREFERRED_RELEASE_TRACK]
            if not isinstance(track, str):
                raise ValueError("Invalid preferred_release_track type")
            if track not in {RELEASE_TRACK_STABLE, RELEASE_TRACK_UNSTABLE}:
                raise ValueError(f"Invalid preferred_release_track value: {track}")

        return state

    def _load_state(self) -> UpdateState:
        """Load state data from disk.

        Reads and parses the state file if it exists. Returns an empty
        dict if the state file doesn't exist yet (first run scenario).
        Handles corrupted state files gracefully by returning empty state.

        Returns:
            UpdateState dict loaded from disk, or empty dict if no file exists
        """
        if not self.state_file.exists():
            return {}

        try:
            raw_state = json.loads(self.state_file.read_text())
            validated_state = self._validate_state(raw_state)
            return cast(UpdateState, validated_state)
        except json.JSONDecodeError as e:
            # Corrupted JSON - log and start fresh
            logger.warning(
                "Update notifier state file is corrupted (invalid JSON): %s. "
                "Starting with fresh state.",
                e,
            )
            return {}
        except OSError as e:
            # File read error - log and start fresh
            logger.warning(
                "Failed to read update notifier state file: %s. Starting with fresh state.",
                e,
            )
            return {}
        except (ValueError, TypeError) as e:
            # Invalid state data - log and start fresh
            logger.warning(
                "Update notifier state file contains invalid data: %s. Starting with fresh state.",
                e,
            )
            return {}

    def _save_state(self, state: UpdateState) -> None:
        """Save state data atomically.

        Args:
            state: State data to save
        """
        self.state_dir.mkdir(parents=True, exist_ok=True)

        tmp = self.state_file.with_suffix(STATE_TMP_SUFFIX)
        tmp.write_text(json.dumps(state, indent=2))
        tmp.replace(self.state_file)

        # Update in-memory cache
        self._cached_state = state

    def set_preferred_release_track(
        self, version_str: str, explicit_track: Literal["stable", "unstable"] | None = None
    ) -> None:
        """Set the user's preferred release track based on an installed version.

        This is called after a successful update to remember the user's preference.
        If they install a stable version, they prefer stable releases.
        If they install an unstable version (alpha/beta/rc), they prefer all releases.

        Args:
            version_str: The version that was just installed
            explicit_track: If provided, use this track instead of inferring from version
                           (either "stable" or "unstable")
        """
        state = self._get_state()

        # Use explicit track if provided, otherwise infer from version stability
        if explicit_track:
            state[STATE_KEY_PREFERRED_RELEASE_TRACK] = explicit_track
        else:
            # Determine track based on version stability
            if is_stable_version(version_str):
                state[STATE_KEY_PREFERRED_RELEASE_TRACK] = RELEASE_TRACK_STABLE
            else:
                state[STATE_KEY_PREFERRED_RELEASE_TRACK] = RELEASE_TRACK_UNSTABLE

        self._save_state(state)

    def _display_notification(self, current_version: str, latest_version: str) -> None:
        """Display a non-intrusive update notification."""
        try:
            from flow.cli.utils.theme_manager import theme_manager

            console = theme_manager.create_console()
            accent_color = theme_manager.get_color("accent")

            # Minimal one-line notification
            message = (
                f"[dim]Update available:[/dim] [{accent_color}]{latest_version}[/{accent_color}] "
                f"[dim](current: {current_version}) — Run[/dim] [{accent_color}]flow update[/{accent_color}]"
            )

            console.print()
            console.print(message)
        except Exception:  # noqa: BLE001
            # Fallback to plain text if rich formatting fails
            print(f"\nUpdate available: {latest_version} (current: {current_version})")
            print("   Run 'flow update' to upgrade\n")
