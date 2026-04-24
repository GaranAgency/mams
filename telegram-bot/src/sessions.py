import json
import threading
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional


class SessionStore:
    def __init__(self, path: Path, ttl_hours: int):
        self.path = path
        self.ttl = timedelta(hours=ttl_hours)
        self._lock = threading.RLock()
        if not self.path.exists():
            self._write({})

    def _read(self) -> dict:
        with self.path.open("r", encoding="utf-8") as f:
            return json.load(f)

    def _write(self, data: dict) -> None:
        tmp = self.path.with_suffix(".tmp")
        with tmp.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        tmp.replace(self.path)

    def _key(self, chat_id: int, project_code: str) -> str:
        return f"{chat_id}:{project_code}"

    def get(self, chat_id: int, project_code: str) -> Optional[str]:
        with self._lock:
            data = self._read()
            entry = data.get(self._key(chat_id, project_code))
            if not entry:
                return None
            last = datetime.fromisoformat(entry["last_activity"])
            if datetime.now(timezone.utc) - last > self.ttl:
                return None
            return entry["claude_session_id"]

    def update(self, chat_id: int, project_code: str, session_id: str) -> None:
        with self._lock:
            data = self._read()
            key = self._key(chat_id, project_code)
            existing = data.get(key, {"message_count": 0})
            data[key] = {
                "claude_session_id": session_id,
                "last_activity": datetime.now(timezone.utc).isoformat(),
                "message_count": existing.get("message_count", 0) + 1,
                "project_code": project_code,
            }
            self._write(data)

    def clear(self, chat_id: int, project_code: Optional[str] = None) -> None:
        with self._lock:
            data = self._read()
            if project_code:
                data.pop(self._key(chat_id, project_code), None)
            else:
                keys = [k for k in data if k.startswith(f"{chat_id}:")]
                for k in keys:
                    del data[k]
            self._write(data)
