# MAMS Telegram Bot

Мост между Telegram и Claude Code с плагином MAMS. Каждое сообщение в разрешённом чате идёт в `claude -p` с MAMS-контекстом, ответ возвращается в Telegram.

## Архитектура

- **DM** с Alex (по whitelist: `ALEX_TG_USER_ID` или `ALEX_TG_USERNAME`): cross-project, активный проект переключается через `/project`
- **Группы**: одна группа = один проект. Привязка через `/bind <CODE>`. Бот отвечает только на @mention или reply
- **Сессии**: одна Claude-сессия на `(chat_id, project_code)`, TTL 24 часа
- **Файлы**: бот скачивает documents/photos в `inbox/<chat_id>/`, передаёт путь Claude через Read tool

## Установка

```bash
cd /home/team/mams/telegram-bot

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# .env уже содержит TELEGRAM_BOT_TOKEN, ALEX_TG_USERNAME=garanalex
# TELEGRAM_BOT_USERNAME автоматически определится при старте
# ALEX_TG_USER_ID определится при первом /start в DM

python -m src.bot
```

## Первый запуск (manual)

1. `python -m src.bot` → должно вывести `bot authenticated as @<username>`
2. В Telegram DM → найти бота → `/start`
3. Бот запишет твой `user_id` в `/home/team/.mams/tg-project-map.json`
4. `/project MAMS` — выбрать активный проект для DM
5. Напиши что-нибудь — должен прийти ответ от Claude с MAMS-контекстом

## Привязка группы «garan ai» к GRN

1. Добавить бота в группу (уже сделано)
2. В группе написать: `/bind GRN`
3. Бот подтвердит: «Группа привязана к GRN»
4. Теперь в этой группе: `@<bot_username> сделай SEO audit garan.agency` → бот делегирует PM-Director в GRN-контексте

## Автозапуск через systemd

```bash
sudo cp /home/team/mams/telegram-bot/systemd/mams-tg-bot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable mams-tg-bot
sudo systemctl start mams-tg-bot
sudo systemctl status mams-tg-bot
```

Логи: `journalctl -u mams-tg-bot -f` или `/home/team/mams/telegram-bot/logs/bot.log`.

## Настройка в @BotFather

После создания бота через `/newbot`:

- `/setprivacy` → **Enable** (бот видит в группе только @mentions и replies — это нужно)
- `/setcommands` → вставить:
  ```
  start - Знакомство (в DM)
  project - Активный проект DM: /project GRN
  bind - Привязать группу к проекту: /bind GRN
  unbind - Отвязать группу
  status - Текущий проект и сессия
  reset - Новая Claude-сессия
  help - Справка
  ```
- `/setjoingroups` → **Enable**
- `/setdescription` → `MAMS orchestrator: делегирует задачи PM-Director и специалистам. 1 группа = 1 проект.`

## Конфигурация (.env)

| Ключ | Значение |
|---|---|
| `TELEGRAM_BOT_TOKEN` | от @BotFather |
| `TELEGRAM_BOT_USERNAME` | auto-fill при старте, можно оставить пустым |
| `ALEX_TG_USER_ID` | твой numeric ID, auto-fill на первом `/start` |
| `ALEX_TG_USERNAME` | `garanalex` |
| `CLAUDE_CWD` | `/home/team/mams` (для MAMS-контекста) |
| `CLAUDE_BIN` | `claude` |
| `SESSION_TTL_HOURS` | `24` |
| `ALEX_DAILY_LIMIT` | `0` = без лимита |
| `USER_DAILY_LIMIT` | `30` сообщений/день для остальных |

## Troubleshooting

**«claude: command not found»** — бот запускается под user `team`, убедись что `which claude` из-под `team` работает. Если нужен абсолютный путь — замени `CLAUDE_BIN` в `.env`.

**«claude exit 1: Authentication required»** — `claude` не залогинен под user `team`. Запусти `claude login` под `team` или пропиши `ANTHROPIC_API_KEY` в `.env` (и передай в systemd unit через `Environment=`).

**Бот не отвечает в группе** — проверь что (а) privacy mode=enable у @BotFather, (б) ты его @mention или reply'ишь, (в) группа привязана через `/bind`.

**Conflict 409 при запуске** — старый инстанс ещё запущен. `pkill -f 'src.bot'` или `sudo systemctl stop mams-tg-bot`.

## Ограничения v1

- Не поддерживает voice/video (игнорирует)
- Rate limit только в памяти (сбрасывается при рестарте бота)
- Нет webhook mode, только polling
- Нет Notion Task auto-creation per message (но Claude сам логирует в Activity Log через MAMS rules)

## Следующий шаг (v2)

- `🤖 TG Bot Bindings` Notion DB для маппинга групп — замена JSON файла
- Persistent rate limit через файл/Redis
- Streaming responses (частичный ответ пока Claude думает)
- Voice messages через Whisper
