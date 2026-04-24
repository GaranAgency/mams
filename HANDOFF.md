# MAMS — Handoff Guide (Cowork → Claude Code на сервере)

**Цель:** за 1 сессию на сервере развернуть MAMS до состояния "PM-Agent работает, первая задача прошла через Notion → Activity Log → Obsidian".

**Предыдущая стадия:** research-фаза закрыта в Cowork 2026-04-20/21. Все 5 deliverables — в `docs/`.

---

## Чек-лист на первый день

Пройди по пунктам сверху вниз. Если что-то не сошлось — не продолжай, спроси Claude Code.

### 0. Проверить, что у тебя есть на сервере

```bash
# Claude Code установлен (Anthropic CLI)
claude --version

# Node 20+ (для MCP серверов и Agent SDK)
node --version

# Python 3.11+ (для скиллов-скриптов и NotebookLM helpers)
python3 --version

# Git (для skill vault)
git --version

# jq, curl, tar (обычно есть)
which jq curl tar
```

Если чего-то нет — ставь через пакетный менеджер системы. Claude Code с Agent SDK — обязательно.

### 1. Распаковать пакет

```bash
cd ~/projects      # или куда ты хочешь положить MAMS
tar -xzf mams-bootstrap-2026-04-21.tar.gz
# ИЛИ
unzip mams-bootstrap-2026-04-21.zip

mv mams-bootstrap mams       # переименовать для короткого пути
cd mams
```

Проверить дерево: `ls -la`, должно быть `CLAUDE.md`, `docs/`, `plugin-scaffold/`, `bootstrap/`, `.env.example`, `README.md`.

### 2. Создать `.env` из примера

```bash
cp .env.example .env
# открыть .env редактором и заполнить ключи
```

Минимум для первой сессии:
- `ANTHROPIC_API_KEY` — для Agent SDK
- `NOTION_API_KEY` — integration token (https://www.notion.so/profile/integrations)
- `OBSIDIAN_API_KEY` — из Local REST API plugin (у тебя сейчас `95b3c9ea6dd0e64d1ef11b2ec49bc683d215b4ff10d68faec258c8dc220fd1e7`)
- `OBSIDIAN_URL` — `https://127.0.0.1:27124` если Claude Code на той же машине, что и Obsidian; иначе SSH-туннель (см. §6)

Остальные (Ahrefs, Semrush, Apify, Hunter, Meta, Google Ads и т.п.) — заполнишь по мере надобности.

### 3. Запустить Claude Code в директории проекта

```bash
cd ~/projects/mams
claude
```

Claude Code автоматически подхватит `CLAUDE.md` из корня — контекст проекта загрузится в систему.

### 4. Первое сообщение Claude Code

Скопируй целиком промпт из `bootstrap/02-first-session-prompt.md` и вставь в Claude Code. Он ориентирует его на состояние: "research закрыт, начинаем разворачивать плагин, первый шаг — создать Notion DBs и PM-Agent".

### 5. Пройти Deployment Gate-1 (Notion DBs)

Следовать `bootstrap/01-notion-dbs.md`. Там пошагово: подключить Notion MCP, создать 6 новых DBs (Sprints, Tasks, Skills Registry, Decisions & Approvals, Risks & Incidents, Retrospectives), настроить relations.

Критерий прохождения DG-1:
- 6 DBs созданы в workspace
- IDs всех DBs сохранены в `.env` (NOTION_DB_SPRINTS_ID и т.д.)
- Test row создана в Sprints, связана с MAMS project в Projects Registry

Записать PASS в Activity Log (Category = "Gate-Event", Details = "DG-1 PASS").

### 6. Obsidian — если сервер не та же машина

Варианты:

**A. Obsidian на локальной машине, Claude Code на сервере:**
Поднять SSH-туннель с локалки:

```bash
# с локальной машины
ssh -R 27124:127.0.0.1:27124 user@server
```

Тогда на сервере `OBSIDIAN_URL=https://127.0.0.1:27124` сработает.

**B. Obsidian и Claude Code на одной машине:**
Ничего не делать. Obsidian Local REST API уже слушает 127.0.0.1:27124.

**C. Obsidian выключен / недоступен:**
Claude Code должен продолжать работу, но писать только в Notion + предупреждать. Поведение зашито в `plugin-scaffold/hooks/` (будет активировано после DG-2).

### 7. Собрать плагин итеративно

После DG-1 Claude Code начнёт итеративно наполнять `plugin-scaffold/`:

1. **DG-2 (Plugin scaffold valid):** `plugin.json` корректный, структура валидируется, minimum один агент (PM) с полным system prompt.
2. **DG-3 (First agent working):** PM-Agent принимает intent через chat, декомпозирует на задачу, создаёт запись в Notion Tasks, логирует в Activity Log. Проверить на тестовом intent: "Запусти Q2 SEO audit для [MFR]".
3. **DG-4 (E2E reproduced):** прогнать сценарий из `docs/MAMS_Sample_E2E_Scenario.md` целиком или адаптировать на реальный проект.

После DG-4 — плагин упаковывается в `.plugin` файл, валидация через `claude plugin validate`, install локально.

### 8. MCP серверы (в какой последовательности подключать)

Приоритет 0 (для DG-1):
1. **Notion MCP** (`@notionhq/notion-mcp-server`) — обязательно для Notion Command Center.
2. **Obsidian MCP** — опционально (есть curl fallback через `obsidian-connector` скилл).

Приоритет 1 (для DG-3):
3. **Filesystem MCP** — для чтения/записи в репо плагина (встроен в Claude Code).
4. **Memory MCP** (Anthropic `memory` tool) — для persistent state агентов.

Приоритет 2 (по мере роли):
5. **Ahrefs MCP** — SEO specialist.
6. **Semrush MCP / API** — SEO specialist (fallback).
7. **NotebookLM MCP** — Niche-Expert, Skill-Updater.
8. **Apify MCP** — Niche-Expert, Skill-Updater (fallback).
9. **Hunter.io** — Link-Builder.
10. **Vercel / Netlify MCPs** — Dev.
11. **Figma MCP** — Designer / CRO.
12. **Supabase MCP** — Skills Registry backend.
13. **Chrome MCP** — CRO / QA (Playwright альтернатива).

Детали — в `bootstrap/00-install.md` § MCP.

---

## Что НЕ делать в первой сессии

- Не писать сразу все 12 агентов полноценно. Приоритет — PM-Agent + 1 специалист (SEO или Content). Остальные — заглушки, которые делегируют обратно PM с TODO.
- Не наполнять все скиллы. P0-скиллы (из Skill Inventory §2) — только те, что нужны PM и первому специалисту.
- Не настраивать CI/CD для skill vault с первого раза. Supabase registry + Git — это Phase 2. В Phase 1 skill-файлы лежат прямо в `plugin-scaffold/skills/`.
- Не запускать Skill-Updater автономно до DG-4. Его pipeline — последнее, что пускается в prod.

---

## Эскалация (когда спросить Alex)

Claude Code должен остановиться и спросить у тебя лично, если:

- Нужно согласие на Red-tier действие (budget change, content publish от лица клиента, любое изменение в production CMS).
- Notion DB с production-данными требует migration (существующий Projects Registry → новая структура).
- Skill-Updater впервые деплоит реальный patch.
- Конфликт между документами (например, Agent Specs говорит одно, Architecture Report — другое).
- Missing context, который нельзя найти в `docs/` или Notion.

---

## Следующие шаги после DG-4

1. Пилотный проект на реальном клиенте (например, [MFR]) — прогнать full sprint через MAMS.
2. Phase 2: вынести skill registry в Supabase (из Git-only), поднять golden-set harness, включить канарные A/B.
3. Phase 3: включить Skill-Updater автономно — market-intel scan → патчи → G1-G4 → canary.
4. Phase 4: расширить на мульти-клиентский портфель, Friday digest, weekly stakeholder updates.

---

## Где искать помощь

- Вся архитектура → `docs/MAMS_Architecture_Report.md`
- Как работает конкретный агент → `docs/MAMS_Agent_Specs.md` → agent passport
- Какой скилл нужен → `docs/MAMS_Skill_Inventory.md` §2 Catalog
- Как пройти end-to-end сценарий → `docs/MAMS_Sample_E2E_Scenario.md`
- Notion schemas, views, webhooks → `docs/MAMS_Notion_Template.md`
- Bootstrap-гайды → `bootstrap/00-install.md`, `bootstrap/01-notion-dbs.md`, `bootstrap/02-first-session-prompt.md`, `bootstrap/03-deployment-gates.md`

Если не нашёл — спроси Alex в чате.
