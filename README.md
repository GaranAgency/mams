# MAMS — Multi-Agent Marketing System (bootstrap package)

**Version:** 0.1.0 (bootstrap, pre-production)
**Date:** 2026-04-21
**Origin:** Cowork research session (Gate-0 → Gate-9 all PASS)
**Owner:** Alex (digitalgaran@gmail.com)
**Target:** deploy to personal server, continue buildout with Claude Code

## Что это

MAMS — универсальная AI-команда из 12 специализированных subagents под управлением PM-Agent «Интернет-маркетолог», которая закрывает полный цикл интернет-маркетинга: стратегия → SEO/AEO/GEO → content → SMM → PPC → CRO/UX → dev → link-building → analytics → self-improvement.

Проект уже прошёл research-фазу в Cowork. Все архитектурные решения и artifacts — в `docs/`. Этот архив содержит всё необходимое, чтобы **перенести работу на сервер и продолжить** в Claude Code без потери контекста.

## Структура пакета

```
mams-bootstrap/
├── README.md                    ← ЭТОТ ФАЙЛ (начни отсюда)
├── CLAUDE.md                    ← auto-loaded Claude Code'ом как project context
├── HANDOFF.md                   ← пошаговый checklist развёртывания
├── .env.example                 ← все env переменные с приоритетами
│
├── bootstrap/                   ← инструкции для сервера (для Alex)
│   ├── 00-install.md            ← prerequisites, MCP setup
│   ├── 01-notion-dbs.md         ← DG-1: создание 6 новых Notion DB
│   ├── 02-first-session-prompt.md  ← готовые prompts для первой сессии Claude Code
│   └── 03-deployment-gates.md   ← DG-1..DG-4 acceptance criteria
│
├── docs/                        ← research deliverables (source of truth)
│   ├── MAMS_Architecture_Report.md (+ .docx)  ← главный архитектурный документ
│   ├── MAMS_Agent_Specs.md (+ .docx)          ← passport'ы 12 агентов
│   ├── MAMS_Skill_Inventory.md (+ .docx)      ← каталог 50+ скиллов
│   ├── MAMS_Sample_E2E_Scenario.md (+ .docx)  ← полный walkthrough NPO S3
│   ├── MAMS_Notion_Template.md (+ .docx)      ← schemas 9 Notion DBs
│   ├── MAMS_Scope_v1.md                       ← изначальный scope
│   ├── MAMS_Research_Prompt_v2.md             ← research prompt
│   └── 00-session-transcript.docx             ← полная переписка research phase
│
└── plugin-scaffold/             ← Claude Code plugin (скелет, наполняется на сервере)
    ├── .claude-plugin/plugin.json
    ├── agents/                  ← 12 agent passports (stubs)
    ├── skills/                  ← пусто, P0 список в skills/README.md
    ├── commands/                ← пусто (legacy slot)
    ├── hooks/hooks.json         ← stub, активируется после DG-2
    ├── .mcp.json.example        ← MCP-сервера конфиг
    └── README.md                ← plugin-level instructions
```

## Quick start (сервер)

```bash
# 1. Распаковать архив
tar -xzf mams-bootstrap-2026-04-21.tar.gz
cd mams-bootstrap

# 2. Прочитать checklist
cat HANDOFF.md                       # общий checklist
cat bootstrap/00-install.md          # prerequisites
cat bootstrap/02-first-session-prompt.md  # prompt для Claude Code

# 3. Настроить env
cp .env.example .env
chmod 600 .env
# → заполнить ANTHROPIC_API_KEY, NOTION_API_KEY (минимум для DG-1)

# 4. Настроить MCP
cd plugin-scaffold
cp .mcp.json.example .mcp.json
# → оставить только notion блок, остальные — включить по мере надобности

# 5. Запустить Claude Code
cd ..
claude
# → скопировать prompt A из bootstrap/02-first-session-prompt.md
```

## Deployment Gates

Проект переходит через 4 gates, каждый — с acceptance criteria:

| Gate | Что | Блокер | Approver |
|---|---|---|---|
| **DG-1** | Notion DBs провижнинг (9 DB) | без этого нет orchestration | Alex manual |
| **DG-2** | Plugin валиден, PM-Agent отвечает | без этого нет агентов | Alex manual |
| **DG-3** | Первая E2E задача через PM → specialist | baseline продуктивности | Alex manual |
| **DG-4** | Полный E2E сценарий (NPO S3) воспроизведён | production-ready signal | Alex manual |

Детали — `bootstrap/03-deployment-gates.md`.

## Ключевые концепции (30-секунд)

- **12 агентов:** PM-Director (orchestrator), Strategist, SEO/AEO/GEO, Content Lead, SMM, PPC, CRO/UX, Dev/QA, Link-Builder, Analytics, Niche-Expert (RAG-специалист по вертикали), Skill-Updater (meta-agent).
- **Паттерн:** Orchestrator-worker + DAG-hybrid (см. Architecture §4).
- **HITL:** Tiered Green/Amber/Red gates (Green=auto, Amber=digest approval, Red=sync approval).
- **Skill versioning:** Semver, Git-vault primary + Notion mirror (Phase 1), Supabase (Phase 2). Skill-Updater pipeline с 4 Trust Gates: G1 Static → G2 Semantic → G3 Sandbox → G4 Permission Manifest.
- **Orchestration substrate:** Notion (9 DBs) + Obsidian (knowledge layer) + `.claude/` (plugin layer).
- **Niche expertise:** Hybrid RAG + optional FT (Niche-Expert собирает corpus per vertical, citation tags: [FACT] / [EXPERT-CLAIM] / [CONTESTED] / [FOUNDATIONAL]).
- **Cost budget:** `MAMS_SPRINT_TOKEN_CAP_USD=50` hard cap per sprint (Architecture §12).

## Что работает сейчас (после распаковки)

✅ Полный research corpus (все 5 deliverables)
✅ Plugin manifest + 12 agent stubs с description и tools
✅ Notion DB schemas готовы к creation
✅ `.env.example` с приоритетами всех 20+ ключей
✅ Bootstrap checklists для DG-1 → DG-4
✅ Готовые prompts для первой сессии Claude Code

## Что НЕ работает ещё (TODO на сервере)

⚠️ `skills/` пуст — нужно написать или импортировать P0 skills (risk-tiering, notion-orchestration, seo-audit, etc.)
⚠️ `hooks/hooks.json` — stubs, все disabled; активировать после DG-2
⚠️ `.mcp.json` реальный (не `.example`) — создать при setup
⚠️ Notion DBs ещё не созданы — это первая задача (DG-1)
⚠️ Plugin не упакован и не установлен — DG-2
⚠️ PM-Agent не тестирован end-to-end — DG-3
⚠️ Skill-Updater pipeline не активен — Phase 1 final / Phase 2

## References

Внутренние:
- `docs/MAMS_Architecture_Report.md` — детальная архитектура, все решения с обоснованиями
- `docs/MAMS_Agent_Specs.md` — passports для 12 агентов
- `docs/MAMS_Skill_Inventory.md` — full catalog skills + MAMS-custom specs
- `docs/MAMS_Sample_E2E_Scenario.md` — как выглядит production sprint
- `docs/MAMS_Notion_Template.md` — Notion orchestration details
- `HANDOFF.md` — server-side operational checklist
- `CLAUDE.md` — project context auto-loaded by Claude Code

Внешние (для онбординга сервер-клода):
- Claude Code docs: https://docs.claude.com/en/docs/claude-code
- Claude Code plugins: https://docs.claude.com/en/docs/claude-code/plugins
- Agent SDK: https://docs.claude.com/en/docs/agents-and-tools/claude-code-sdk
- Notion API (2026-03-11): https://developers.notion.com/

## Безопасность

- `.env` в `.gitignore` (check!) — **никогда** не коммить secrets
- Notion integration с минимальными capabilities (Read/Update/Insert, без admin)
- SSH tunnel для Obsidian — только с trusted машины Alex
- Red-tier actions требуют sync approval в Decisions DB **до** execution (enforced хуками после DG-2)

## Лицензия / приватность

Внутренний проект, UNLICENSED. Research artifacts могут содержать confidential business context (NPO, MFR clients). Не шарить за пределы команды MAMS.

## Контакт

Alex — digitalgaran@gmail.com
