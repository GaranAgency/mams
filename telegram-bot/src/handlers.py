import asyncio
import logging
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from telegram import Update, Message
from telegram.constants import ChatAction, ChatType, ParseMode
from telegram.ext import ContextTypes

from . import config
from .claude_bridge import run_claude, ClaudeError
from .project_map import ProjectMap
from .rate_limit import DailyRateLimiter
from .sessions import SessionStore

log = logging.getLogger(__name__)

project_map = ProjectMap(config.PROJECT_MAP_PATH)
sessions = SessionStore(config.SESSIONS_PATH, config.SESSION_TTL_HOURS)
rate_limit = DailyRateLimiter()

_chat_locks: dict[int, asyncio.Lock] = defaultdict(asyncio.Lock)


def _is_alex(update: Update) -> bool:
    u = update.effective_user
    if not u:
        return False
    if config.ALEX_TG_USER_ID and u.id == config.ALEX_TG_USER_ID:
        return True
    if config.ALEX_TG_USERNAME and u.username and u.username.lower() == config.ALEX_TG_USERNAME:
        return True
    return False


def _bot_mentioned(message: Message, bot_username: str) -> bool:
    if not message.text and not message.caption:
        return False
    if message.reply_to_message and message.reply_to_message.from_user:
        if message.reply_to_message.from_user.is_bot:
            return True
    text = (message.text or message.caption or "")
    if bot_username and f"@{bot_username}" in text:
        return True
    if message.entities:
        for e in message.entities:
            if e.type in ("mention", "text_mention"):
                mention = text[e.offset: e.offset + e.length]
                if bot_username and mention.lstrip("@").lower() == bot_username.lower():
                    return True
    return False


def _strip_mention(text: str, bot_username: str) -> str:
    if not text or not bot_username:
        return text or ""
    return text.replace(f"@{bot_username}", "").strip()


async def _download_files(message: Message, chat_id: int, bot) -> list[str]:
    paths: list[str] = []
    chat_dir = config.INBOX_DIR / str(chat_id)
    chat_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")

    if message.document:
        file = await bot.get_file(message.document.file_id)
        name = message.document.file_name or f"file_{message.document.file_id}"
        target = chat_dir / f"{ts}_{name}"
        await file.download_to_drive(target)
        paths.append(str(target))

    if message.photo:
        photo = message.photo[-1]
        file = await bot.get_file(photo.file_id)
        target = chat_dir / f"{ts}_photo_{photo.file_id}.jpg"
        await file.download_to_drive(target)
        paths.append(str(target))

    return paths


def _build_prompt(
    user_text: str,
    project_code: str,
    chat_type: str,
    chat_title: str,
    user_name: str,
    is_alex: bool,
    file_paths: list[str],
) -> str:
    file_section = ""
    if file_paths:
        lines = "\n".join(f"- {p}" for p in file_paths)
        file_section = f"\n\nAttached files (use Read tool to inspect):\n{lines}"

    alex_note = " (владелец MAMS, Alex)" if is_alex else " (участник команды)"

    return f"""[TG-BOT CONTEXT — inject before handling user intent]

Source: Telegram bot
Chat type: {chat_type}
Chat: {chat_title}
Active project: {project_code}
User: {user_name}{alex_note}

ТВОЯ ПЕРСОНА:
Твоё имя — {config.BOT_PERSONA_NAME} (по-русски: {config.BOT_PERSONA_NAME_RU}).
Ты — orchestrator системы MAMS (Multi-Agent Marketing System) агентства Garan.
Если пользователь пишет по-русски — называй себя «{config.BOT_PERSONA_NAME_RU}».
Если по-английски — «{config.BOT_PERSONA_NAME}».
Не называй себя «Claude Code», «main session», «assistant» в пользовательских ответах.

ПРОЕКТНЫЕ ПРАВИЛА (mandatory):
1. Ты работаешь в контексте проекта {project_code} и только его.
2. Перед любым действием прочитай запись {project_code} в Projects Registry Notion (Summary, Master Page URL, Task Tracker URL). Используй эти ссылки.
3. Если пользователь спрашивает про другой проект/клиента — вежливо откажи одной фразой:
   «Эта группа/диалог привязан к проекту {project_code}. По другим проектам — пиши в соответствующую группу или в DM.»
4. Все записи в Activity Log проставляй Project={project_code}, Source=Chat (via Telegram bot), Who=Claude Code (main session via TG bot).
5. Для маркетинговых intent'ов делегируй через Task tool в mams:pm-director.
6. Для инфраструктурных/meta-вопросов про MAMS сам отвечай напрямую.
7. Respect tiered HITL: Red-tier actions не исполняй без approval, флагни в ответе.
8. Ответ для Telegram — на русском, лаконично, без большого markdown (только жирный *text* и списки). Длинные ответы разбивай логически, но один ответ = одно сообщение.

USER MESSAGE:
{user_text}{file_section}
""".strip()


async def _process_message(update: Update, context: ContextTypes.DEFAULT_TYPE, project_code: str):
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat
    chat_id = chat.id

    is_alex = _is_alex(update)
    limit = config.ALEX_DAILY_LIMIT if is_alex else config.USER_DAILY_LIMIT
    allowed, count = rate_limit.check_and_incr(user.id, limit)
    if not allowed:
        await message.reply_text(
            f"Дневной лимит ({limit} сообщений) исчерпан. Сбросится в 00:00 UTC."
        )
        return

    user_text = _strip_mention(
        message.text or message.caption or "", config.TELEGRAM_BOT_USERNAME
    )
    if not user_text and not (message.document or message.photo):
        return

    async with _chat_locks[chat_id]:
        await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)

        try:
            file_paths = await _download_files(message, chat_id, context.bot)
        except Exception as e:
            log.exception("file download failed")
            await message.reply_text(f"Не смог скачать файл: {e}")
            return

        chat_title = chat.title or chat.username or "DM"
        user_name = user.full_name + (f" @{user.username}" if user.username else "")

        prompt = _build_prompt(
            user_text=user_text or "(без текста, только файл)",
            project_code=project_code,
            chat_type=chat.type,
            chat_title=chat_title,
            user_name=user_name,
            is_alex=is_alex,
            file_paths=file_paths,
        )

        session_id = sessions.get(chat_id, project_code)

        try:
            new_sid, response = await run_claude(
                prompt=prompt,
                cwd=config.CLAUDE_CWD,
                claude_bin=config.CLAUDE_BIN,
                session_id=session_id,
            )
        except ClaudeError as e:
            log.exception("claude failed")
            await message.reply_text(f"⚠️ Claude вернул ошибку: {e}")
            return

        if new_sid:
            sessions.update(chat_id, project_code, new_sid)

        if not response:
            await message.reply_text("(пустой ответ от Claude)")
            return

        for chunk in _chunk_text(response, limit=3900):
            try:
                await message.reply_text(chunk)
            except Exception:
                await message.reply_text(chunk)


def _chunk_text(text: str, limit: int = 3900) -> list[str]:
    if len(text) <= limit:
        return [text]
    chunks = []
    remaining = text
    while len(remaining) > limit:
        cut = remaining.rfind("\n\n", 0, limit)
        if cut < limit // 2:
            cut = remaining.rfind("\n", 0, limit)
        if cut < limit // 2:
            cut = remaining.rfind(" ", 0, limit)
        if cut < limit // 2:
            cut = limit
        chunks.append(remaining[:cut].rstrip())
        remaining = remaining[cut:].lstrip()
    if remaining:
        chunks.append(remaining)
    return chunks


async def on_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    chat = update.effective_chat
    user = update.effective_user
    if not message or not chat or not user:
        return
    if user.is_bot:
        return

    if chat.type == ChatType.PRIVATE:
        if not _is_alex(update):
            await message.reply_text(
                "Извини, бот доступен только Alex (garanalex) и в привязанных группах."
            )
            return
        project_map.register_dm_user(user.id, user.username or "", is_alex=True)
        project_code = project_map.get_dm_project(user.id)
        if not project_code:
            await message.reply_text(
                "В DM не выбран проект. Укажи: `/project GRN` (или MAMS, MFR...).",
            )
            return
        await _process_message(update, context, project_code)
        return

    if chat.type in (ChatType.GROUP, ChatType.SUPERGROUP):
        project_code = project_map.get_group_project(chat.id)
        if not project_code:
            if _bot_mentioned(message, config.TELEGRAM_BOT_USERNAME) and _is_alex(update):
                await message.reply_text(
                    "Группа не привязана к проекту. Alex, выполни: `/bind <CODE>` (пример: `/bind GRN`).",
                )
            return
        if not _bot_mentioned(message, config.TELEGRAM_BOT_USERNAME):
            return
        await _process_message(update, context, project_code)


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat = update.effective_chat
    if chat.type != ChatType.PRIVATE:
        return
    if not _is_alex(update):
        await update.message.reply_text(
            "Привет. Этот бот сейчас доступен только Alex в DM и в привязанных проектных группах."
        )
        return
    project_map.register_dm_user(user.id, user.username or "", is_alex=True)
    await update.message.reply_text(
        f"Привет, {user.first_name}. Твой user_id {user.id} запомнен.\n\n"
        "Команды:\n"
        "• `/project <CODE>` — выбрать активный проект для этого DM (пример: `/project MAMS`)\n"
        "• `/status` — текущий проект и сессия\n"
        "• `/bind <CODE>` — привязать группу к проекту (из группы)\n"
        "• `/unbind` — отвязать группу (из группы)\n"
        "• `/reset` — сбросить сессию Claude\n"
        "• `/help` — справка\n\n"
        "Выбери проект: `/project MAMS`",
    )


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "MAMS Telegram bot.\n\n"
        "*В DM (только Alex):*\n"
        "• `/project <CODE>` — активный проект\n"
        "• `/status` — статус\n"
        "• `/reset` — новая Claude-сессия\n"
        "Просто пиши — отвечу в контексте активного проекта.\n\n"
        "*В группах:*\n"
        "• `/bind <CODE>` (Alex) — привязать группу к проекту\n"
        "• `/unbind` (Alex) — отвязать\n"
        "Отвечаю только когда тегают или отвечают на моё сообщение.",
    )


async def cmd_project(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user
    if chat.type != ChatType.PRIVATE:
        await update.message.reply_text("Команда работает только в DM.")
        return
    if not _is_alex(update):
        return
    args = context.args or []
    if not args:
        current = project_map.get_dm_project(user.id) or "не выбран"
        await update.message.reply_text(f"Активный проект: {current}")
        return
    code = args[0].upper()
    project_map.register_dm_user(user.id, user.username or "", is_alex=True)
    project_map.set_dm_project(user.id, code)
    sessions.clear(chat.id)
    await update.message.reply_text(f"Активный проект: {code}. Сессия Claude сброшена.")


async def cmd_bind(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    if chat.type not in (ChatType.GROUP, ChatType.SUPERGROUP):
        await update.message.reply_text("Команда работает только в группе.")
        return
    if not _is_alex(update):
        await update.message.reply_text("Только Alex может привязывать группы.")
        return
    args = context.args or []
    if not args:
        await update.message.reply_text("Использование: `/bind <CODE>` (пример: `/bind GRN`)")
        return
    code = args[0].upper()
    project_map.bind_group(
        chat_id=chat.id,
        chat_name=chat.title or "",
        project_code=code,
        added_by=update.effective_user.id,
    )
    sessions.clear(chat.id)
    await update.message.reply_text(
        f"Группа «{chat.title}» (chat_id {chat.id}) привязана к проекту *{code}*. "
        "Теперь @mention меня или reply — отвечаю в контексте этого проекта.",
    )


async def cmd_unbind(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    if chat.type not in (ChatType.GROUP, ChatType.SUPERGROUP):
        await update.message.reply_text("Команда работает только в группе.")
        return
    if not _is_alex(update):
        return
    ok = project_map.unbind_group(chat.id)
    sessions.clear(chat.id)
    await update.message.reply_text("Группа отвязана." if ok else "Эта группа и не была привязана.")


async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user
    if chat.type == ChatType.PRIVATE:
        code = project_map.get_dm_project(user.id) or "не выбран"
        sid = sessions.get(chat.id, code) if code != "не выбран" else None
        await update.message.reply_text(
            f"DM с {user.first_name}\n"
            f"Активный проект: {code}\n"
            f"Claude session: {'есть' if sid else 'новая при следующем сообщении'}"
        )
        return
    info = project_map.group_info(chat.id)
    if info:
        sid = sessions.get(chat.id, info["project_code"])
        await update.message.reply_text(
            f"Группа: {chat.title}\n"
            f"Проект: {info['project_code']}\n"
            f"Привязана: {info['added_date'][:10]}\n"
            f"Claude session: {'есть' if sid else 'будет создана'}"
        )
    else:
        await update.message.reply_text("Группа не привязана к проекту. Alex: `/bind <CODE>`")


async def cmd_reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user
    if chat.type == ChatType.PRIVATE:
        if not _is_alex(update):
            return
        sessions.clear(chat.id)
    else:
        if not _is_alex(update):
            return
        sessions.clear(chat.id)
    await update.message.reply_text("Claude-сессия сброшена. Следующее сообщение начнёт новую.")
