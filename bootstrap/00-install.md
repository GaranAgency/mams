# 00 — Install prerequisites on server

**Цель:** подготовить сервер к тому, чтобы Claude Code мог запуститься в папке `mams-bootstrap/` и увидеть все MCP-сервера.

> **Важно:** это инструкция для человека (Alex). После этого шага дальше работает Claude Code по HANDOFF.md.

## 1. Системные требования

| Компонент | Версия | Зачем |
|---|---|---|
| Node.js | ≥ 20.x LTS | Claude Code CLI + большинство MCP npx-пакетов |
| Python | ≥ 3.11 | Skill scripts, Agent SDK fallback |
| Git | ≥ 2.40 | Skill vault versioning |
| `jq` | any | Plugin validation, JSON parsing в хуках |
| `curl` | any | Obsidian REST fallback, health checks |

Проверить:

```bash
node --version && python3 --version && git --version && jq --version && curl --version | head -1
```

## 2. Install Claude Code CLI

Официальный путь (Anthropic docs):

```bash
# macOS/Linux
curl -fsSL https://claude.ai/install.sh | bash

# или через npm
npm install -g @anthropic-ai/claude-code
```

Проверить:

```bash
claude --version
```

## 3. Clone / распаковать архив

```bash
# Если передали архив
cd ~
tar -xzf mams-bootstrap-2026-04-21.tar.gz
cd mams-bootstrap
ls -la
# должно быть видно: CLAUDE.md, HANDOFF.md, docs/, plugin-scaffold/, .env.example, bootstrap/
```

## 4. Заполнить `.env`

```bash
cp .env.example .env
chmod 600 .env
# редактировать: vi .env / nano .env
```

Минимум для старта (DG-1):

- `ANTHROPIC_API_KEY` — взять в console.anthropic.com
- `NOTION_API_KEY` — создать integration на https://www.notion.so/profile/integrations → Share её со всеми MAMS-страницами

Остальные ключи добавлять по мере надобности (см. priority-аннотации `# P0/P1/P2/P3` в `.env.example`).

## 5. Настроить `.mcp.json`

```bash
cd plugin-scaffold
cp .mcp.json.example .mcp.json
# в .mcp.json env-refs вида ${NOTION_API_KEY} разрешатся из корневого .env
```

Отключить на старте всё, кроме **notion** (остальные — как только понадобятся):

```bash
# в .mcp.json — либо удалить блок, либо оставить только notion
```

## 6. MCP: детали по серверам

Полный список — в `plugin-scaffold/.mcp.json.example`. Ниже — что проверять при включении каждого.

### 6.1 Notion MCP (P0, обязательно)

- Package: `@notionhq/notion-mcp-server` (official)
- Установить integration token в Notion: `New internal integration` → name `MAMS-Agents` → capabilities: Read/Update/Insert content + comments
- Share integration с каждой из DB, которые создаются в DG-1 (01-notion-dbs.md)
- Sanity check на сервере:

```bash
export NOTION_API_KEY=secret_REPLACE
curl -s https://api.notion.com/v1/users/me \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2026-03-11" | jq .
```

### 6.2 Obsidian MCP (P1, опционально)

Obsidian работает на **локальной машине Alex**, не на сервере. Варианты доступа:

**A. SSH reverse tunnel (рекомендовано при долгой работе):**

На локальной машине Alex:
```bash
ssh -R 27124:127.0.0.1:27124 user@server
```

На сервере теперь `https://127.0.0.1:27124` — это Obsidian Alex'а.

**B. Fallback — не трогать Obsidian с сервера.** Все заметки writeback через Notion Activity Log, а Cowork-сессии позже синкают всё в Obsidian.

Sanity check (при tunnel):

```bash
curl -s -k https://127.0.0.1:27124/vault/ \
  -H "Authorization: Bearer $OBSIDIAN_API_KEY" | head -20
```

### 6.3 SEO MCPs (P2 — Ahrefs, Semrush)

- Ahrefs: `@ahrefs/mcp-server` — нужен API token с API Advanced планом
- Semrush: community `semrush-mcp-community` — нужен API key (premium)
- Включать **только когда** первый SEO-агент начинает production работу (после DG-3)

### 6.4 Apify MCP (P2 — niche-expert, skill-updater)

- Package: `@apify/actors-mcp-server`
- Skill `apify-api` на сервере уже заточен под rotation 4-х ключей — они идут в `APIFY_TOKEN_PRIMARY/2/3/4`
- Включать после DG-3, когда niche-expert стартует

### 6.5 Hunter.io MCP (P2 — link-builder)

- Community package: `hunter-io-mcp`
- Требует `HUNTER_API_KEY`

### 6.6 Dev MCPs (P3 — Vercel/Netlify/Figma/Supabase)

- Включать только когда dev-qa или cro-ux-specialist начинают работу
- Supabase нужен только для Phase 2 (Skill Registry backend)

## 7. Git repo (опционально, но рекомендовано)

После распаковки — сразу init git для трекинга изменений в плагине:

```bash
cd mams-bootstrap
git init -b main
git add .
git commit -m "chore: initial MAMS bootstrap from Cowork research"
# создать GitHub private repo и push
```

## 8. Первый запуск Claude Code

```bash
cd mams-bootstrap
claude
# CLI автоматически подхватит CLAUDE.md, .env, .mcp.json из plugin-scaffold/
```

Первая команда — прочитать `HANDOFF.md` и идти по checklist.

Готовый prompt для первой сессии — в `bootstrap/02-first-session-prompt.md`.

## 9. Troubleshooting

| Симптом | Решение |
|---|---|
| `npx: command not found` | установить Node ≥ 20 |
| MCP сервер не стартует | проверить env var разрешился (`echo $NOTION_API_KEY` внутри Claude Code shell), проверить Notion-Version header |
| `Notion 401 Unauthorized` | integration не расшарен с pages/DBs |
| Obsidian `connection refused` | tunnel не проброшен, либо Obsidian не запущен, либо Local REST API plugin выключен |
| `claude: no MCP servers found` | CLI запущен не из той директории — должна быть `mams-bootstrap/plugin-scaffold/` либо CLI настроен на родительскую |

## 10. Next

→ `01-notion-dbs.md` — создать 6 новых Notion DBs (и заполнить ID в `.env`)
→ `02-first-session-prompt.md` — prompt для Claude Code на сервере
→ `03-deployment-gates.md` — критерии прохождения DG-1..DG-4
