import json
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


class ProjectMap:
    def __init__(self, path: Path):
        self.path = path
        self._lock = threading.RLock()
        if not self.path.exists():
            self._write({"groups": {}, "dm_users": {}})

    def _read(self) -> dict:
        with self.path.open("r", encoding="utf-8") as f:
            return json.load(f)

    def _write(self, data: dict) -> None:
        tmp = self.path.with_suffix(".tmp")
        with tmp.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        tmp.replace(self.path)

    def get_group_project(self, chat_id: int) -> Optional[str]:
        with self._lock:
            data = self._read()
            g = data["groups"].get(str(chat_id))
            return g["project_code"] if g else None

    def bind_group(self, chat_id: int, chat_name: str, project_code: str, added_by: int) -> None:
        with self._lock:
            data = self._read()
            data["groups"][str(chat_id)] = {
                "project_code": project_code.upper(),
                "chat_name": chat_name,
                "added_by": added_by,
                "added_date": datetime.now(timezone.utc).isoformat(),
            }
            self._write(data)

    def unbind_group(self, chat_id: int) -> bool:
        with self._lock:
            data = self._read()
            if str(chat_id) in data["groups"]:
                del data["groups"][str(chat_id)]
                self._write(data)
                return True
            return False

    def get_dm_user(self, user_id: int) -> Optional[dict]:
        with self._lock:
            return self._read()["dm_users"].get(str(user_id))

    def register_dm_user(self, user_id: int, username: str, is_alex: bool) -> None:
        with self._lock:
            data = self._read()
            existing = data["dm_users"].get(str(user_id), {})
            existing.update({
                "username": username,
                "is_alex": is_alex,
                "first_seen": existing.get("first_seen", datetime.now(timezone.utc).isoformat()),
                "last_seen": datetime.now(timezone.utc).isoformat(),
            })
            if "active_project" not in existing:
                existing["active_project"] = None
            data["dm_users"][str(user_id)] = existing
            self._write(data)

    def set_dm_project(self, user_id: int, project_code: Optional[str]) -> None:
        with self._lock:
            data = self._read()
            if str(user_id) in data["dm_users"]:
                data["dm_users"][str(user_id)]["active_project"] = (
                    project_code.upper() if project_code else None
                )
                self._write(data)

    def get_dm_project(self, user_id: int) -> Optional[str]:
        u = self.get_dm_user(user_id)
        return u.get("active_project") if u else None

    def group_info(self, chat_id: int) -> Optional[dict]:
        with self._lock:
            return self._read()["groups"].get(str(chat_id))
