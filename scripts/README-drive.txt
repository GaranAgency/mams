═══════════════════════════════════════════════════════════════
  MAMS — инструкция для disaster recovery
  Версия: auto-updated weekly by secrets-backup.sh
═══════════════════════════════════════════════════════════════

ЧТО ЭТО ЗА ПАПКА
────────────────
Эта папка (`ai/` в Shared Drive) — хранилище для полного восстановления
MAMS (Multi-Agent Marketing System Garan Agency) при потере локальной
машины Alex'а.

СТРУКТУРА
─────────
  ai/
  ├── obsidian-claude/              — Obsidian vault (живой, real-time sync)
  ├── mams-state-backup/            — еженедельные encrypted бекапы секретов
  │   ├── mams-secrets-YYYY-MM-DD.age   (зашифрованные .env, tokens, memory)
  │   └── recovery.sh               (копия recovery-скрипта, сами без секретов)
  ├── recovery.sh                   — тот же recovery-скрипт, здесь для удобства
  └── README.txt                    — этот файл


КОГДА ПРИМЕНЯТЬ
───────────────
Если комп Alex'а пропал/сломан/переустановлен и MAMS надо поднимать
на свежей машине с нуля.


ЧТО ДЕЛАТЬ
──────────
1. На новой машине: установить Windows + WSL2 Ubuntu + Google Drive
   Desktop (залогиниться в этот же Google аккаунт) + Claude Code CLI.

2. В WSL (как пользователь team):

      sudo mkdir -p /mnt/g
      sudo mount -t drvfs G: /mnt/g
      cp "/mnt/g/Shared drives/ai/recovery.sh" ~/
      bash ~/recovery.sh

3. Скрипт попросит **age private key** — это 3 строки из 1Password
   (запись «MAMS age private key»). Вставить, Enter, Ctrl+D.

4. Дальше всё сделается само: расшифровка секретов, git clone репы
   с GitHub, установка Python venv, systemd для бота, cron для auto-
   backup. ~5-10 минут до «бот отвечает в Telegram».


ЧТО ВОССТАНАВЛИВАЕТСЯ
─────────────────────
• Все .env с токенами (Telegram bot, Vercel, GitHub, Anthropic, …)
• Claude Code auth (не нужен `claude login`)
• MAMS plugin + subagents
• Память Клода (что он выучил про проекты + предпочтения)
• Привязки TG-групп к проектам
• GitHub credentials (не нужно создавать новый PAT)


ЕДИНСТВЕННОЕ ЧТО НУЖНО ПОМНИТЬ
──────────────────────────────
• Age private key из 1Password (запись «MAMS age private key»)

Всё остальное — в этой папке или в GitHub
(https://github.com/GaranAgency/mams).


ПОЛНАЯ ДОКУМЕНТАЦИЯ
───────────────────
После `git clone GaranAgency/mams` — читай:
  ~/mams/RECOVERY.md      (детальный playbook)
  ~/mams/CLAUDE.md        (описание проекта MAMS)
  ~/mams/HANDOFF.md       (что делать в первой сессии)


ЕСЛИ ПОТЕРЯН И AGE KEY
──────────────────────
(надеемся что нет, но на всякий случай)
• Код в GitHub жив → `git clone`
• Notion workspace жив → логин в notion.so
• Obsidian vault жив → папка ai/obsidian-claude/
• Секреты придётся пересоздать руками:
  - TG bot token: @BotFather → /revoke → /token
  - Vercel token: vercel.com/account/tokens → new
  - GitHub PAT: github.com/settings/tokens → new
  - Anthropic: claude login (OAuth)
• Память Клода потеряется, но быстро наработается заново
═══════════════════════════════════════════════════════════════
