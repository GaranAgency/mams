"""
Capture & context module for the MAMS Telegram bot.

Stores every message the bot sees (per-chat JSONL append-only) and provides
helpers to read recent context for inclusion in Claude prompts.

Spec: docs/superpowers/specs/2026-05-03-mams-bot-context-awareness-design.md
"""
import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from . import config

log = logging.getLogger(__name__)

# Caps — defaults overridable via .env
MAX_MESSAGES = int(os.getenv('MAMS_CONTEXT_MAX_MESSAGES', '50'))
MAX_CHARS = int(os.getenv('MAMS_CONTEXT_MAX_CHARS', '6000'))

HEADER = "=== Что обсуждалось в группе с момента моего последнего ответа ==="
FOOTER = "=== Конец истории. Ниже — обращение к тебе сейчас: ==="


def _chat_dir(chat_id: int) -> Path:
    d = config.INBOX_DIR / str(chat_id)
    d.mkdir(parents=True, exist_ok=True)
    return d


def _utc_iso_ms() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


def _media_placeholder(message) -> str:
    if message.photo:
        return "[photo]"
    if message.voice:
        return f"[voice {message.voice.duration}s]"
    if message.video:
        return f"[video {message.video.duration}s]"
    if message.video_note:
        return f"[video_note {message.video_note.duration}s]"
    if message.audio:
        title = message.audio.title or message.audio.file_name or "?"
        return f"[audio: {title} {message.audio.duration}s]"
    if message.document:
        name = message.document.file_name or "?"
        return f"[document: {name}]"
    if message.sticker:
        emoji = message.sticker.emoji or ""
        return f"[sticker {emoji}]" if emoji else "[sticker]"
    if message.animation:
        return "[animation]"
    return "[unsupported media]"


def _extract_text(message) -> str:
    """Return text/caption, or media placeholder if no textual content."""
    text = message.text or message.caption or ""
    if text:
        # Captioned media → wrap with media kind so context shows it was a photo etc.
        if not message.text and (message.photo or message.video or message.document
                                  or message.animation or message.audio):
            base = _media_placeholder(message).strip("[]")
            return f"[{base} + caption: {text}]"
        return text
    return _media_placeholder(message)


def _from_name(user) -> str:
    if not user:
        return "user_unknown"
    parts = []
    if user.first_name:
        parts.append(user.first_name)
    if user.last_name:
        parts.append(user.last_name)
    name = " ".join(parts).strip()
    if name:
        return name
    if user.username:
        return f"@{user.username}"
    return f"user_{user.id}"


def append(message) -> None:
    """
    Append the message to the chat's messages.jsonl. Never raises.

    Called from on_message for EVERY message the bot receives, regardless of
    whether the bot will respond. Best-effort: if write fails, log a warning
    and continue — capture must not block the response path.
    """
    try:
        chat = message.chat
        user = message.from_user
        if not chat or not user:
            return
        record = {
            "ts": _utc_iso_ms(),
            "message_id": message.message_id,
            "from_id": user.id,
            "from_name": _from_name(user),
            "text": _extract_text(message),
            "reply_to": (
                message.reply_to_message.message_id
                if message.reply_to_message else None
            ),
        }
        path = _chat_dir(chat.id) / "messages.jsonl"
        with open(path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
            f.flush()
    except Exception as e:
        log.warning("capture.append failed: %s", e)


def get_state(chat_id: int) -> dict:
    """Read state.json or return empty dict if absent/broken."""
    try:
        path = _chat_dir(chat_id) / "state.json"
        if not path.exists():
            return {}
        return json.loads(path.read_text(encoding='utf-8'))
    except Exception as e:
        log.warning("capture.get_state failed: %s", e)
        return {}


def update_state(chat_id: int, last_responded_message_id: int) -> None:
    """Write state.json with last responded message id. Never raises."""
    try:
        state = {
            "last_responded_message_id": last_responded_message_id,
            "last_responded_at": _utc_iso_ms(),
        }
        path = _chat_dir(chat_id) / "state.json"
        path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding='utf-8')
    except Exception as e:
        log.warning("capture.update_state failed: %s", e)


def _read_all(chat_id: int) -> list[dict]:
    """Read all messages from the chat's messages.jsonl. Skips broken JSON lines."""
    path = _chat_dir(chat_id) / "messages.jsonl"
    if not path.exists():
        return []
    out = []
    try:
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    out.append(json.loads(line))
                except json.JSONDecodeError as e:
                    log.warning("capture: skipping broken JSON line: %s", e)
    except Exception as e:
        log.warning("capture._read_all failed: %s", e)
    return out


def read_recent(
    chat_id: int,
    since_message_id: Optional[int],
    exclude_message_id: Optional[int] = None,
) -> list[dict]:
    """
    Return messages with message_id > since_message_id, excluding exclude_message_id.

    If since_message_id is None (first interaction in this chat), returns empty
    list — no context to provide.
    """
    if since_message_id is None:
        return []
    all_msgs = _read_all(chat_id)
    result = []
    for m in all_msgs:
        mid = m.get("message_id")
        if mid is None:
            continue
        if mid <= since_message_id:
            continue
        if exclude_message_id is not None and mid == exclude_message_id:
            continue
        result.append(m)
    return result


def _localtime_hhmm(ts: str) -> str:
    """Convert ISO8601 UTC string to local-zone HH:MM."""
    try:
        s = ts.rstrip('Z')
        dt = datetime.fromisoformat(s).replace(tzinfo=timezone.utc)
        return dt.astimezone().strftime('%H:%M')
    except Exception:
        return ts[11:16] if len(ts) >= 16 else "??:??"


def format_for_prompt(chat_id: int, recent: list[dict]) -> str:
    """
    Format recent messages into a context block for Claude prompt injection.
    Returns empty string if recent is empty.

    Truncation: caps at MAX_MESSAGES count and MAX_CHARS total formatted size.
    Drops oldest first.
    """
    if not recent:
        return ""

    recent = sorted(recent, key=lambda m: m.get("message_id", 0))
    dropped = 0

    if len(recent) > MAX_MESSAGES:
        dropped += len(recent) - MAX_MESSAGES
        recent = recent[-MAX_MESSAGES:]

    # Lookup table for reply-name resolution (read whole file once)
    all_msgs = _read_all(chat_id)
    msg_by_id = {m.get("message_id"): m for m in all_msgs if m.get("message_id") is not None}

    def fmt(m: dict) -> str:
        time_str = _localtime_hhmm(m.get("ts", ""))
        from_name = m.get("from_name", "?")
        text = m.get("text", "")
        reply_to_id = m.get("reply_to")
        if reply_to_id:
            replied = msg_by_id.get(reply_to_id)
            replied_name = replied.get("from_name") if replied else None
            arrow = f" → {replied_name}" if replied_name else " →"
            return f"[{time_str} {from_name}{arrow}] {text}"
        return f"[{time_str} {from_name}] {text}"

    lines = [fmt(m) for m in recent]

    # Char-cap: drop oldest until fits, leaving room for header/footer/marker.
    overhead = len(HEADER) + len(FOOTER) + 100
    while sum(len(l) + 1 for l in lines) > MAX_CHARS - overhead and len(lines) > 1:
        lines.pop(0)
        dropped += 1

    if dropped > 0:
        lines.insert(0, f"[пропущено {dropped} более старых сообщений]")

    return f"{HEADER}\n\n" + "\n".join(lines) + f"\n\n{FOOTER}"
