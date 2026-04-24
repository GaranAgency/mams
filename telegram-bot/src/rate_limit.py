import threading
from datetime import datetime, timezone
from typing import Dict


class DailyRateLimiter:
    def __init__(self):
        self._counts: Dict[int, Dict[str, int]] = {}
        self._lock = threading.Lock()

    def _today(self) -> str:
        return datetime.now(timezone.utc).date().isoformat()

    def check_and_incr(self, user_id: int, limit: int) -> tuple[bool, int]:
        if limit <= 0:
            return True, 0
        today = self._today()
        with self._lock:
            rec = self._counts.get(user_id, {})
            if rec.get("date") != today:
                rec = {"date": today, "count": 0}
            if rec["count"] >= limit:
                self._counts[user_id] = rec
                return False, rec["count"]
            rec["count"] += 1
            self._counts[user_id] = rec
            return True, rec["count"]
