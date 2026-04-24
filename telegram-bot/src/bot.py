import logging
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from telegram import BotCommand
from telegram.ext import Application, CommandHandler, MessageHandler, filters

from src import config
from src.handlers import (
    on_message,
    cmd_start,
    cmd_help,
    cmd_project,
    cmd_bind,
    cmd_unbind,
    cmd_status,
    cmd_reset,
)

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    level=getattr(logging, config.LOG_LEVEL, logging.INFO),
    handlers=[
        logging.FileHandler(config.LOG_DIR / "bot.log"),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger("mams-tg-bot")


async def post_init(app: Application):
    me = await app.bot.get_me()
    if not config.TELEGRAM_BOT_USERNAME:
        config.TELEGRAM_BOT_USERNAME = me.username or ""
    log.info("bot authenticated as @%s (id=%s)", me.username, me.id)

    await app.bot.set_my_commands([
        BotCommand("start", "Знакомство (в DM)"),
        BotCommand("project", "Активный проект для DM: /project GRN"),
        BotCommand("bind", "Привязать группу к проекту: /bind GRN"),
        BotCommand("unbind", "Отвязать группу"),
        BotCommand("status", "Текущий проект и сессия"),
        BotCommand("reset", "Новая Claude-сессия"),
        BotCommand("help", "Справка"),
    ])


def main():
    app = (
        Application.builder()
        .token(config.TELEGRAM_BOT_TOKEN)
        .post_init(post_init)
        .build()
    )

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CommandHandler("project", cmd_project))
    app.add_handler(CommandHandler("bind", cmd_bind))
    app.add_handler(CommandHandler("unbind", cmd_unbind))
    app.add_handler(CommandHandler("status", cmd_status))
    app.add_handler(CommandHandler("reset", cmd_reset))

    app.add_handler(
        MessageHandler(
            (filters.TEXT | filters.Document.ALL | filters.PHOTO | filters.CAPTION)
            & ~filters.COMMAND,
            on_message,
        )
    )

    log.info("starting MAMS TG bot — polling mode")
    app.run_polling(allowed_updates=["message", "edited_message"])


if __name__ == "__main__":
    main()
