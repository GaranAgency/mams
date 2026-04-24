import os
from pathlib import Path
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")


def _require(name: str) -> str:
    v = os.getenv(name, "").strip()
    if not v:
        raise RuntimeError(f"Missing env var: {name}")
    return v


def _int(name: str, default: int) -> int:
    v = os.getenv(name, "").strip()
    return int(v) if v else default


TELEGRAM_BOT_TOKEN = _require("TELEGRAM_BOT_TOKEN")
TELEGRAM_BOT_USERNAME = os.getenv("TELEGRAM_BOT_USERNAME", "").strip().lstrip("@")
ALEX_TG_USER_ID = _int("ALEX_TG_USER_ID", 0)
ALEX_TG_USERNAME = os.getenv("ALEX_TG_USERNAME", "").strip().lstrip("@").lower()

CLAUDE_CWD = os.getenv("CLAUDE_CWD", "/home/team/mams").strip()
CLAUDE_BIN = os.getenv("CLAUDE_BIN", "claude").strip()

SESSION_TTL_HOURS = _int("SESSION_TTL_HOURS", 24)
ALEX_DAILY_LIMIT = _int("ALEX_DAILY_LIMIT", 0)
USER_DAILY_LIMIT = _int("USER_DAILY_LIMIT", 30)

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").strip().upper()

BOT_PERSONA_NAME = os.getenv("BOT_PERSONA_NAME", "Claude").strip()
BOT_PERSONA_NAME_RU = os.getenv("BOT_PERSONA_NAME_RU", "Клод").strip()

PROJECT_MAP_PATH = Path(os.getenv("PROJECT_MAP_PATH", "/home/team/.mams/tg-project-map.json"))
SESSIONS_PATH = Path(os.getenv("SESSIONS_PATH", "/home/team/.mams/tg-sessions.json"))
INBOX_DIR = Path(os.getenv("INBOX_DIR", str(ROOT / "inbox")))
LOG_DIR = Path(os.getenv("LOG_DIR", str(ROOT / "logs")))

INBOX_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)
PROJECT_MAP_PATH.parent.mkdir(parents=True, exist_ok=True)
SESSIONS_PATH.parent.mkdir(parents=True, exist_ok=True)
