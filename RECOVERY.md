# MAMS — Disaster Recovery Playbook

Пошаговая инструкция восстановления MAMS после полной потери локальной машины (переустановка Windows, новый комп, failed WSL).

---

## Что у тебя есть после фаталки

**Sources of truth, которые пережили катастрофу:**

| Что | Где | Как достать |
|---|---|---|
| Код, docs, plugin-scaffold, telegram-bot | GitHub: `GaranAgency/mams` (private) | `git clone` |
| Notion workspace (Projects, Tasks, Sprints, Activity Log, Skills, Decisions, Risks, Retros) | Notion cloud | логин в notion.so |
| Obsidian vault + MAMS chronology | Google Drive Shared Drive `ai/obsidian-claude/` | Google Drive Desktop |
| Secrets (`.env`, tokens, memory, bot bindings) | Google Drive Shared Drive `ai/mams-state-backup/*.age` | age-decrypt нужен приватный ключ |
| Приватный age ключ (восстановление секретов) | 1Password / Bitwarden → запись «MAMS age private key (recovery)» | вручную из vault |

---

## Полный recovery (первый запуск на свежей машине)

### 0. Prerequisites на Windows

1. Установи WSL2 Ubuntu: `wsl --install -d Ubuntu`
2. Установи Google Drive Desktop (https://www.google.com/drive/download/), залогинься в тот же Google аккаунт
3. Установи Obsidian (опционально, для человеческого использования vault)
4. Запусти WSL Ubuntu, создай пользователя `team` (или свой привычный)

### 1. Ставим базовые утилиты

```bash
sudo apt update && sudo apt install -y python3-pip python3-venv cron git curl
```

### 2. Монтируем Google Drive в WSL

```bash
sudo mkdir -p /mnt/g
sudo mount -t drvfs G: /mnt/g
ls "/mnt/g/Shared drives/ai/"   # должны увидеть obsidian-claude, mams-state-backup
```

### 3. Устанавливаем Claude Code и логинимся

```bash
# Следуй официальной инструкции Anthropic
# https://docs.anthropic.com/claude-code/installation
# После установки:
claude login   # OAuth или API key flow
```

### 4. Клонируем MAMS repo

Нужен **GitHub PAT** (новый, если старый потерял):
- https://github.com/settings/tokens → new classic token, scope `repo`
- Или SSH ключ

```bash
cd ~
git clone https://github.com/GaranAgency/mams.git
# или: git clone git@github.com:GaranAgency/mams.git  (если SSH)
cd ~/mams
```

### 5. Восстанавливаем `age` и секреты

```bash
# Устанавливаем age (static binary, без sudo)
mkdir -p ~/.local/bin ~/.age
curl -sSL https://github.com/FiloSottile/age/releases/download/v1.2.0/age-v1.2.0-linux-amd64.tar.gz | tar xz -C /tmp
mv /tmp/age/age /tmp/age/age-keygen ~/.local/bin/
chmod 755 ~/.local/bin/age ~/.local/bin/age-keygen
export PATH=$HOME/.local/bin:$PATH
echo 'export PATH=$HOME/.local/bin:$PATH' >> ~/.bashrc

# Восстанавливаем приватный ключ из 1Password
# Открой запись «MAMS age private key (recovery)» → скопируй содержимое → вставь:
nano ~/.age/key.txt
chmod 600 ~/.age/key.txt

# Генерим public.key из приватного
age-keygen -y ~/.age/key.txt > ~/.age/public.key

# Находим свежайший backup в Drive и расшифровываем
LATEST=$(ls -1t "/mnt/g/Shared drives/ai/mams-state-backup/mams-secrets-"*.age | head -1)
age -d -i ~/.age/key.txt "$LATEST" > /tmp/secrets.tar.gz

# Разворачиваем файлы на место (tar сохраняет относительные пути от $HOME)
cd ~
tar xzvf /tmp/secrets.tar.gz
# Проверь что появились ~/mams/telegram-bot/.env, ~/.mams/*.json, ~/.claude/projects/*/memory/

rm /tmp/secrets.tar.gz
```

### 6. Настройка Python venv для бота

```bash
cd ~/mams/telegram-bot
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

### 7. Проверяем `claude` CLI работает

```bash
claude -p --dangerously-skip-permissions "ответь одним словом: pong"
# Должно вывести: {"result":"pong",...}
```

Если падает — проверь что ты залогинился в `claude login`.

### 8. Запускаем бота

```bash
cd ~/mams/telegram-bot
.venv/bin/python -m src.bot &
# Проверь логи: tail -f logs/bot.log — должно быть "bot authenticated as @garanaibot"
```

### 9. Переустанавливаем systemd service (если использовал)

```bash
sudo cp ~/mams/telegram-bot/systemd/mams-tg-bot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable mams-tg-bot
sudo systemctl start mams-tg-bot
sudo systemctl status mams-tg-bot
```

### 10. Восстанавливаем cron (auto-backups)

```bash
(crontab -l 2>/dev/null; cat <<'EOF'
# MAMS auto-backups
0 3 * * * /home/team/mams/scripts/git-backup.sh
0 4 * * 0 /home/team/mams/scripts/secrets-backup.sh
EOF
) | crontab -
crontab -l   # verify
```

### 11. Верификация E2E

- В TG пишешь боту `/start` — должен ответить приветствием
- В Notion открываешь Projects Registry → MAMS — всё на месте
- В Obsidian открываешь vault → MAMS/ — хронология актуальна

**Если всё работает — recovery завершён (~30 минут).**

---

## Частичные recovery сценарии

### Только сдох TG bot token (но WSL живёт)

1. `/revoke` у @BotFather → новый токен
2. Обновить `TELEGRAM_BOT_TOKEN` в `~/mams/telegram-bot/.env`
3. `sudo systemctl restart mams-tg-bot`

### Только сдох GitHub PAT

1. Создать новый PAT на https://github.com/settings/tokens
2. Обновить `~/.git-credentials`:
   ```bash
   echo "https://x-access-token:NEW_PAT@github.com" > ~/.git-credentials
   chmod 600 ~/.git-credentials
   ```

### Потерял приватный age ключ и его нет в 1Password

**Это катастрофа — secrets backups в Drive не расшифровать.**
- TG token придётся регенерить
- Claude Code потребует новый login
- Memory и prefs Клод забудет (но Notion/Obsidian state живёт)

Урок: **периодически проверяй что в 1Password запись `MAMS age private key` актуальна и открывается**.

---

## Что бекапится автоматически

| Что | Куда | Когда | Retention |
|---|---|---|---|
| Код `~/mams/` | GitHub `GaranAgency/mams` (private) | ежедневно 03:00 UTC (cron) | неограниченно (git history) |
| Secrets (`.env` + `.mams/` + memory) | GDrive `ai/mams-state-backup/*.age` | еженедельно Вс 04:00 UTC (cron) | 8 последних (~2 месяца) |
| Notion | Notion cloud | автомат (их бекапы) | как у них |
| Obsidian vault | GDrive `ai/obsidian-claude/` | real-time (Google Drive sync) | версионирование Drive |

---

## Проверка бекапов раз в квартал

Чтобы не обнаружить ломанный бекап в кризисный момент:

1. `tail /home/team/mams/logs/git-backup.log` — видишь свежие записи?
2. `tail /home/team/mams/logs/secrets-backup.log` — видишь свежие?
3. Открой https://github.com/GaranAgency/mams — последний коммит недавний?
4. `ls -la "/mnt/g/Shared drives/ai/mams-state-backup/"` — файлы свежие?
5. Раз в квартал: попробуй расшифровать свежайший .age на тестовой машине — убедись что ключ из 1Password работает

---

## Контакты / owners

- **Owner:** Alex Garan (digitalgaran@gmail.com)
- **Repo:** https://github.com/GaranAgency/mams
- **Notion master:** https://www.notion.so/349326fe46c581008981fb34adb9919f
- **TG bot:** @garanaibot
