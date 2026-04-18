"""
In-memory session key store.

Maps session_id -> {provider: api_key}.
Keys are never written to disk. On server restart all sessions are cleared.
For production, replace with Redis or an encrypted DB-backed store.
"""

from typing import Optional
import threading


class KeyStore:
    def __init__(self):
        self._store: dict[str, dict[str, str]] = {}
        self._lock = threading.Lock()

    def set(self, session_id: str, keys: dict[str, str]) -> None:
        with self._lock:
            existing = self._store.get(session_id, {})
            existing.update(keys)
            self._store[session_id] = existing

    def get(self, session_id: str) -> Optional[dict[str, str]]:
        with self._lock:
            return self._store.get(session_id)

    def delete(self, session_id: str) -> None:
        with self._lock:
            self._store.pop(session_id, None)

    def get_key(self, session_id: str, provider: str) -> Optional[str]:
        with self._lock:
            session = self._store.get(session_id, {})
            return session.get(provider)


# Singleton
key_store = KeyStore()
