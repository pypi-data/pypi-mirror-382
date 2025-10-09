"""Users service: fetches user data with a small TTL cache.

Extracted from the provider facade to decouple from CLI caches and expose a
focused API for user info retrieval.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any


@dataclass
class _CacheEntry:
    value: Any
    expires_at: float


class UsersService:
    def __init__(self, api_client: Any, *, cache_ttl_seconds: float = 3600.0) -> None:
        self._api = api_client
        self._ttl = float(cache_ttl_seconds)
        self._cache: dict[str, _CacheEntry] = {}

    def _now(self) -> float:
        return time.time()

    def _get_cached(self, key: str) -> Any | None:
        entry = self._cache.get(key)
        if not entry:
            return None
        if self._now() >= entry.expires_at:
            try:
                del self._cache[key]
            except Exception:  # noqa: BLE001
                pass
            return None
        return entry.value

    def _set_cached(self, key: str, value: Any) -> None:
        self._cache[key] = _CacheEntry(value=value, expires_at=self._now() + self._ttl)

    def get_user(self, user_id: str) -> Any:
        """Fetch user info from API with TTL caching and minimal fallbacks.

        Notes:
            - Prefer the canonical Mithril path: GET /v2/users/{id}
            - Only fallback is to retry with a stripped "user_" prefix
            - Avoids probing legacy or alternate routes that cause noisy 404/405s
        """
        cache_key = f"user:{user_id}"
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached

        data = None
        # Normalize common id forms: accept both 'user_ClUS...' and 'ClUS...'
        uid_raw = str(user_id)
        try:
            import re as _re

            uid_stripped = _re.sub(r"^user_", "", uid_raw)
        except Exception:  # noqa: BLE001
            uid_stripped = uid_raw
        # Primary path per client wrapper
        try:
            response = self._api.get_user(uid_raw)
            data = response.get("data", response) if isinstance(response, dict) else response
        except Exception:  # noqa: BLE001
            data = None

        # Retry with stripped id if first attempt didn't yield a useful dict
        if not isinstance(data, dict) or (not data.get("email") and not data.get("username")):
            try:
                response2 = self._api.get_user(uid_stripped)
                data2 = (
                    response2.get("data", response2) if isinstance(response2, dict) else response2
                )
                if isinstance(data2, dict) and (data2.get("email") or data2.get("username")):
                    data = data2
            except Exception:  # noqa: BLE001
                pass

        # Final fallback: when the requested id refers to the current user, synthesize from /v2/me
        if not isinstance(data, dict) or (not data.get("email") and not data.get("username")):
            try:
                me_resp = self._api.get_me()
                me_data = me_resp.get("data", me_resp) if isinstance(me_resp, dict) else me_resp
                if isinstance(me_data, dict):
                    fid = str(
                        me_data.get("fid") or me_data.get("id") or me_data.get("user_id") or ""
                    )
                    # Normalize tokens for comparison
                    import re as _re

                    req_tok = _re.sub(r"[^a-z0-9]", "", str(user_id).lower())
                    fid_tok = _re.sub(r"[^a-z0-9]", "", fid.lower())
                    if (
                        req_tok
                        and fid_tok
                        and (
                            req_tok == fid_tok
                            or fid_tok.startswith(req_tok)
                            or req_tok.startswith(fid_tok)
                        )
                    ):
                        data = me_data
            except Exception:  # noqa: BLE001
                pass

        self._set_cached(cache_key, data)
        return data

    def get_user_teammates(self, user_id: str) -> Any:
        """Fetch teammates list for a user (not cached; often dynamic).

        Normalizes the return shape to a list for callers by unwrapping
        common response envelopes: {data: [...]}, {teammates: [...]}, etc.
        Returns an empty list on error.
        """
        try:
            resp = self._api.get_user_teammates(user_id)
            if isinstance(resp, list):
                return resp
            if isinstance(resp, dict):
                for key in ("data", "teammates", "users", "members", "results", "items"):
                    try:
                        val = resp.get(key)
                        if isinstance(val, list):
                            return val
                        if isinstance(val, dict) and isinstance(val.get("items"), list):
                            return val.get("items")
                    except Exception:  # noqa: BLE001
                        continue
            return []
        except Exception:  # noqa: BLE001
            return []

    def invalidate(self, user_id: str | None = None) -> None:
        if user_id is None:
            self._cache.clear()
        else:
            try:
                del self._cache[f"user:{user_id}"]
            except Exception:  # noqa: BLE001
                pass
