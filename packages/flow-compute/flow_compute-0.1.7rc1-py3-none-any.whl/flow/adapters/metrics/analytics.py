"""Minimal async analytics sink (Amplitude-compatible).

This module lives under adapters/** to keep IO/network usage outside of
utils/** per repository architecture rules. It mirrors the original
implementation previously located in flow.utils.analytics.
"""

from __future__ import annotations

import atexit
import contextlib
import os
import queue
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType
from typing import Any, Final

_requests: ModuleType | None = None
try:  # requests is already a dependency in this project
    import requests as _req

    _requests = _req
except Exception:  # pragma: no cover - extremely defensive  # noqa: BLE001
    _requests = None


DEFAULT_INGEST_URL: Final[str] = "https://api2.amplitude.com/2/httpapi"
# Tunables for batching and timeouts (kept small to avoid blocking UX)
BATCH_MAX: Final[int] = 20
BATCH_INTERVAL_SECONDS: Final[float] = 1.0
REQUEST_TIMEOUT_SECONDS: Final[float] = 0.75
FINAL_DRAIN_TIMEOUT_SECONDS: Final[float] = 0.50


def _read_yaml(path: Path) -> dict[str, Any]:
    try:
        if not path.exists():
            return {}
        import yaml  # local import to avoid global import cost

        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        return data if isinstance(data, dict) else {}
    except Exception:  # noqa: BLE001
        return {}


def _boolish(v: Any) -> bool:
    try:
        s = str(v).strip().lower()
        return s in {"1", "true", "yes", "on"}
    except Exception:  # noqa: BLE001
        return False


def _load_telemetry_settings() -> dict[str, Any]:
    base: dict[str, Any] = {
        "enabled": False,
        "amplitude": {"api_key": "", "url": DEFAULT_INGEST_URL},
    }

    home = Path.home() / ".flow"
    telem_path = home / "telemetry.yaml"
    config_path = home / "config.yaml"

    data = _read_yaml(telem_path)
    if not data:
        cfg = _read_yaml(config_path)
        if isinstance(cfg.get("telemetry"), dict):
            data = cfg.get("telemetry", {})

    if isinstance(data, dict):
        try:
            enabled = data.get("enabled")
            if enabled is not None:
                base["enabled"] = bool(enabled) if isinstance(enabled, bool) else _boolish(enabled)
            amp = data.get("amplitude") or {}
            if isinstance(amp, dict):
                if isinstance(amp.get("api_key"), str):
                    base["amplitude"]["api_key"] = amp.get("api_key")
                if isinstance(amp.get("url"), str) and amp.get("url"):
                    base["amplitude"]["url"] = amp.get("url")
        except Exception:  # noqa: BLE001
            pass

    try:
        env_enabled = os.environ.get("FLOW_TELEMETRY")
        if env_enabled is not None and str(env_enabled).strip() != "":
            base["enabled"] = _boolish(env_enabled)
    except Exception:  # noqa: BLE001
        pass
    try:
        env_key = os.environ.get("FLOW_AMPLITUDE_API_KEY")
        if env_key is not None and str(env_key).strip() != "":
            base["amplitude"]["api_key"] = str(env_key)
    except Exception:  # noqa: BLE001
        pass
    try:
        env_url = os.environ.get("FLOW_AMPLITUDE_URL")
        if env_url is not None and str(env_url).strip() != "":
            base["amplitude"]["url"] = str(env_url)
    except Exception:  # noqa: BLE001
        pass

    return base


def telemetry_enabled() -> bool:
    try:
        settings = _load_telemetry_settings()
        return bool(settings.get("enabled"))
    except Exception:  # noqa: BLE001
        return False


def _get_flow_version() -> str:
    try:
        from flow._version import get_version  # local import

        return get_version()
    except Exception:  # noqa: BLE001
        return "0.0.0+unknown"


def _get_device_id() -> str:
    try:
        path = Path.home() / ".flow" / "analytics_id"
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            data = path.read_text(encoding="utf-8").strip()
            if data:
                return data
        import uuid

        new_id = str(uuid.uuid4())
        path.write_text(new_id, encoding="utf-8")
        try:
            if os.name == "posix":
                os.chmod(path, 0o600)
        except Exception:  # noqa: BLE001
            pass
        return new_id
    except Exception:  # noqa: BLE001
        return f"ephemeral-{int(time.time())}"


@dataclass
class AnalyticsEvent:
    event_type: str
    event_properties: dict[str, Any]
    time_ms: int | None = None
    insert_id: str | None = None


class _AmplitudeWorker:
    def __init__(self) -> None:
        self._queue: queue.Queue[AnalyticsEvent] = queue.Queue(maxsize=1024)
        self._thread: threading.Thread | None = None
        self._stop = threading.Event()
        self._device_id = _get_device_id()
        self._app_version = _get_flow_version()
        self._debug = os.environ.get("FLOW_TELEMETRY_DEBUG") == "1"

    def enabled(self) -> bool:
        try:
            if _requests is None:
                return False
            settings = _load_telemetry_settings()
            if not bool(settings.get("enabled")):
                return False
            api_key = str(settings.get("amplitude", {}).get("api_key") or "")
            return api_key.strip() != ""
        except Exception:  # noqa: BLE001
            return False

    def start(self) -> None:
        if not self.enabled() or self._thread is not None:
            return
        self._thread = threading.Thread(target=self._run, name="flow-amplitude", daemon=True)
        self._thread.start()
        atexit.register(self.stop)

    def enqueue(self, event: AnalyticsEvent) -> None:
        if not self.enabled():
            return
        with contextlib.suppress(Exception):
            self._queue.put_nowait(event)

    def flush(self) -> None:
        if not self.enabled():
            return
        deadline = time.time() + 1.0
        while not self._queue.empty() and time.time() < deadline:
            time.sleep(0.02)

    def stop(self) -> None:
        try:
            if not self.enabled():
                return
            self._stop.set()
            self.flush()
        except Exception:  # noqa: BLE001
            pass

    def _run(self) -> None:
        settings = _load_telemetry_settings()
        url = str(settings.get("amplitude", {}).get("url") or DEFAULT_INGEST_URL)
        if not url.startswith("https://"):
            url = DEFAULT_INGEST_URL
        api_key = str(settings.get("amplitude", {}).get("api_key") or "").strip()
        session = None
        if _requests is not None:
            try:
                session = _requests.Session()
            except Exception:  # noqa: BLE001
                session = None

        batch: list[dict[str, Any]] = []
        last_send = time.time()
        try:
            while not self._stop.is_set():
                try:
                    ev = self._queue.get(timeout=0.25)
                    batch.append(self._to_amplitude(ev))
                except queue.Empty:
                    pass

                now = time.time()
                if batch and (
                    len(batch) >= BATCH_MAX or (now - last_send) > BATCH_INTERVAL_SECONDS
                ):
                    self._send(session, url, api_key, batch)
                    batch = []
                    last_send = now

            if batch:
                self._send(session, url, api_key, batch, timeout=FINAL_DRAIN_TIMEOUT_SECONDS)
        finally:
            try:
                if session is not None:
                    session.close()
            except Exception:  # noqa: BLE001
                pass

    def _to_amplitude(self, ev: AnalyticsEvent) -> dict[str, Any]:
        t_ms = ev.time_ms if isinstance(ev.time_ms, int) else int(time.time() * 1000)
        out = {
            "event_type": ev.event_type,
            "time": t_ms,
            "device_id": self._device_id,
            "event_properties": ev.event_properties,
            "app_version": self._app_version,
            "platform": "python",
        }
        try:
            if not ev.insert_id:
                import uuid

                ev.insert_id = str(uuid.uuid4())
            out["insert_id"] = ev.insert_id
        except Exception:  # noqa: BLE001
            pass
        try:
            import platform
            import sys

            out["os_name"] = platform.system()
            out["os_version"] = platform.version()[:64]
            out["python"] = (
                f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
            )
        except Exception:  # noqa: BLE001
            pass
        return out

    def _send(
        self,
        session: Any,
        url: str,
        api_key: str,
        events: list[dict[str, Any]],
        *,
        timeout: float = REQUEST_TIMEOUT_SECONDS,
    ) -> None:
        if not events:
            return
        payload = {"api_key": api_key, "events": events}
        try:
            if session is not None:
                resp = session.post(url, json=payload, timeout=timeout)
            else:
                if _requests is None:
                    return
                resp = _requests.post(url, json=payload, timeout=timeout)
            code = getattr(resp, "status_code", 0)
            if code in (429, 500, 502, 503, 504):
                time.sleep(0.1)
                if session is not None:
                    session.post(url, json=payload, timeout=timeout)
                elif _requests is not None:
                    _requests.post(url, json=payload, timeout=timeout)
        except Exception:  # noqa: BLE001
            pass


_worker = _AmplitudeWorker()


def start() -> None:
    with contextlib.suppress(Exception):
        _worker.start()


def track(
    event_type: str, properties: dict[str, Any] | None = None, *, time_ms: int | None = None
) -> None:
    try:
        if not _worker.enabled():
            return
        start()
        _worker.enqueue(
            AnalyticsEvent(
                event_type=event_type, event_properties=properties or {}, time_ms=time_ms
            )
        )
    except Exception:  # noqa: BLE001
        pass
