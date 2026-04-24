# MAMS — Multi-Agent Marketing System

**Project code:** `MAMS`
**Владелец:** Alex (digitalgaran@gmail.com)
**Статус (на 2026-04-21):** research-фаза закрыта (Gate-0 → Gate-9 PASS), 5 deliverables в `docs/`. Стадия деплоя: разворачивание плагина на сервере (Claude Code).
**Язык сессии:** русский для диалога, английский для технических терминов, кода, цитат и PR/commit-сообщений.

---

## Что это за проект

MAMS — универсальная AI-команда из 12 агентов под управлением PM-Агента «Интернет-маркетолог» для полного цикла интернет-маркетинга: SEO/AEO/GEO, контент, SMM, PPC, CRO/UX, аналитика, разработка, link-building, self-improvement через Skill-Updater мета-агента.

**Главные архитектурные решения (см. `docs/MAMS_Architecture_Report.md` для деталей):**

1. **Orchestrator-worker + DAG-гибрид** — PM декомпозирует, специалисты исполняют, консилидация через Unified Output Contract
2. **Claude Agent SDK как runtime** — subagents с isolated context, Skills с progressive disclosure, MCP для connectivity
3. **Skill-Updater мета-агент** — detect → draft → G1-G4 Trust Gates → canary → rollout; вдохновлён SICA / METAAGENT / ERL / SKILL-RL
4. **Tiered HITL governance** — Green (auto) / Amber (digest) / Red (sync approval), pre-tool interrupts, immutable audit
5. **Hybrid RAG + FT** для niche-expertise
6. **Notion — orchestration-слой** с известными ограничениями (API 2026-03-11, webhook aggregation 5 мин)
7. **AEO/GEO как first-class** — chunk-retrieval, answer-synthesis, citation-worthiness, entity schema
8. **Server-side conversion tracking** по умолчанию

---

## 12 агентов (см. `docs/MAMS_Agent_Specs.md` для passports)

| # | Agent | Role одной фразой |
|---|---|---|
| 1 | **PM-Director** «Интернет-маркетолог» | Lead orchestrator; делегирует, не исполняет доменную работу |
| 2 | **Strategist** | Positioning, ICP, brand voice, competitive landscape, campaign strategy |
| 3 | **SEO/AEO/GEO Specialist** | Organic + AI-search (ChatGPT/Perplexity/Gemini citations) |
| 4 | **Content Lead** | Long-form, blog, landing copy, email, case studies |
| 5 | **SMM Specialist** | TikTok/IG/LinkedIn/X — organic + paid creative, community |
| 6 | **PPC / Paid Growth** | Google Ads PMax, Meta Advantage+, Conversions API |
| 7 | **CRO / UX Specialist** | Funnel audits, A/B, personalization, accessibility |
| 8 | **Dev / QA** | Web dev, deploy, testing-strategy, Playwright |
| 9 | **Link-Builder** | Outreach, digital PR, broken-link, Hunter.io |
| 10 | **Analytics Specialist** | GA4, GSC, Mixpanel, attribution, anomaly detection |
| 11 | **Niche-Expert** | Dynamic domain KB per client (hybrid RAG+FT) |
| 12 | **Skill-Updater (Meta)** | Continuous market-intel → skill-patch pipeline |

---

## Правила сессии (mandatory)

### Notion Command Center

Central hub: https://www.notion.so/327326fe46c58134a1e7c388b86020ed

Базовые 3 DBs (существующие):
- 📋 **Projects Registry** — все проекты с Code, Summary, Master Page, Task Tracker URL
- 📝 **Activity Log** — все действия (DB `a8f3ad98-9a8f-4809-996d-cf5441cd5f6a`, data source `ac08f18a-1fe4-4acf-a598-06a594f1f9b0`)
- 💬 **Communication Log** — все коммуникации

Новые DBs для MAMS (см. `docs/MAMS_Notion_Template.md` §2.4-2.9):
- Sprints, Tasks, Skills Registry, Decisions & Approvals, Risks & Incidents, Retrospectives

**Правило:**
- ПЕРЕД любой проектной задачей — найти проект в Projects Registry, прочитать Summary + Master Page URL + Task Tracker URL.
- ПОСЛЕ любого значимого действия — создать запись в Activity Log (Entry / Date / Project / Who / Source / Category / Details / Related Task).
- При коммуникации — запись в Communication Log.
- Naming convention: `[CODE] Description` (например, `[MAMS] Scaffold PM-Agent`).

### Obsidian sync

**Access method (как работает сейчас, 2026-04-23):** filesystem через Google Drive mount. Vault расположен в Google Shared Drive `ai/obsidian-claude/`, Google Drive Desktop смонтирован на Windows как `G:\`, в WSL — `/mnt/g/Shared drives/ai/obsidian-claude/`. Обсидиан сам на Windows запущен и подхватывает изменения через file watcher в течение 1-3 сек.

**Vault root в WSL:** `/mnt/g/Shared drives/ai/obsidian-claude/`

**Папка этого проекта:** `/mnt/g/Shared drives/ai/obsidian-claude/MAMS/`

**Как писать:** напрямую через Read/Write/Edit tools. Никакого REST API, TLS, port-proxy не требуется.

```bash
# пример чтения chronology
cat "/mnt/g/Shared drives/ai/obsidian-claude/MAMS/_Chronology MAMS.md"
```

**Если `/mnt/g` не смонтирован** (после рестарта WSL): `sudo mount -t drvfs G: /mnt/g`

**Legacy REST API config** (архив, не используется): плагин `obsidian-local-rest-api` слушает на `127.0.0.1:27124` **на Windows**, API-key в `.env` (`OBSIDIAN_API_KEY`). Из WSL достать его без port-proxy невозможно. Если когда-нибудь понадобится — через `netsh portproxy` на Windows-стороне.

Обязательная структура на проект в vault:

```
MAMS/
  _MOC MAMS.md            # index
  _Chronology MAMS.md     # date-based event log
  People/{Name}.md
  Processes/{Process}.md
  Meetings/{YYYY-MM-DD Topic}.md
```

Каждая запись хронологии — заголовок `## 2026-MM-DD (Alex via Claude)`, wiki-links `[[...]]`, #tags.

**Важно:** Notion — первый (tasks, status), потом Obsidian (insights, chronology, people). Не дублировать. Если Obsidian недоступен — предупредить, не падать.

### Gates / HITL checkpoints

Research закрыт. Далее:
- **Deployment gates:** DG-1 (Notion DBs created) → DG-2 (Plugin scaffold valid) → DG-3 (First agent working) → DG-4 (E2E scenario reproduced)
- **Skill-Updater gates** (постоянные): G1 Static → G2 Semantic → G3 Sandbox → G4 Permission Manifest; golden-set ≥90% pass, 100% safety; canary 5% / N=50

---

## Структура репо / плагина

```
mams-bootstrap/
├── CLAUDE.md                   # этот файл — контекст проекта
├── HANDOFF.md                  # что делать на сервере в первый раз
├── README.md                   # как распаковать + оглавление
├── .env.example                # плейсхолдеры секретов
├── docs/                       # 5 deliverables + scope + research prompt + session-transcript
│   ├── MAMS_Architecture_Report.md
│   ├── MAMS_Agent_Specs.md
│   ├── MAMS_Skill_Inventory.md
│   ├── MAMS_Sample_E2E_Scenario.md
│   ├── MAMS_Notion_Template.md
│   ├── MAMS_Scope_v1.md
│   ├── MAMS_Research_Prompt_v2.md
│   └── 00-session-transcript.docx
├── plugin-scaffold/            # заготовка Claude Code plugin
│   ├── .claude-plugin/plugin.json
│   ├── agents/                 # 12 .md плейсхолдеров
│   ├── skills/                 # пустая + README
│   ├── commands/               # пустая
│   ├── hooks/                  # hooks.json stub
│   ├── .mcp.json.example
│   └── README.md
└── bootstrap/
    ├── 00-install.md           # шаги установки на сервере
    ├── 01-notion-dbs.md        # как создать новые Notion DBs
    ├── 02-first-session-prompt.md  # промпт для первой сессии Claude Code
    └── 03-deployment-gates.md  # DG-1 … DG-4 критерии
```

---

## Где что искать

- **Архитектурные вопросы** → `docs/MAMS_Architecture_Report.md`
- **Что должен уметь конкретный агент** → `docs/MAMS_Agent_Specs.md` → соответствующий passport
- **Какой скилл у кого** → `docs/MAMS_Skill_Inventory.md` §2 Catalog
- **Как агенты взаимодействуют по кейсу** → `docs/MAMS_Sample_E2E_Scenario.md`
- **Notion DB schemas, views, webhooks** → `docs/MAMS_Notion_Template.md`
- **Методология research** (для повторных запусков Skill-Updater) → `docs/MAMS_Scope_v1.md` + `docs/MAMS_Research_Prompt_v2.md`
- **Что происходило в предыдущих сессиях Cowork** → `docs/00-session-transcript.docx`

---

## Что делать прямо сейчас (первая сессия на сервере)

Открыть `HANDOFF.md` и следовать чек-листу. Там пошагово: распаковать, прописать `.env`, подключить MCP, создать Notion DBs, собрать плагин итеративно начиная с PM-Agent.

---

## Конвенции

- **Коды проектов:** `MAMS` (этот), `MFR` (Miami First Remodeling), и т.д. из Projects Registry.
- **Названия файлов:** kebab-case, semver для скиллов (`seo-audit/v1.3.2/`).
- **Commits:** conventional commits (`feat:`, `fix:`, `chore:`, `docs:`, `refactor:`).
- **PR:** каждый новый скилл/агент — отдельный PR, G1-G4 checkrun как CI gates.
- **Никаких секретов в репо.** Obsidian API key, Notion token, Ahrefs/Semrush keys — только `.env`, который в `.gitignore`.

---

## Источники и авторство

Research-корпус: NotebookLM `MAMS_Research_2026-04` (ID `13341521-e6a7-40ce-8433-868dd3288f5d`), ≈90 источников, покрытие 9 блоков A-I.

Citation tags в документах:
- `[FACT]` — authoritative primary source
- `[EXPERT-CLAIM]` — named expert, не проверено независимо
- `[CONTESTED]` — есть counter-claims
- `[FOUNDATIONAL]` — базовая концепция (pre-cutoff допустима до 15% корпуса)
