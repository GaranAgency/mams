# 03 — Deployment Gates (DG-1 .. DG-4)

Полная архитектура gates — в `docs/MAMS_Architecture_Report.md` §12-§14. Ниже — acceptance criteria для сервера.

Правило: **не переходим к следующему gate без approval от Alex** (tier: Red для gate promotion).

---

## DG-1 — Notion DBs ready

**Goal:** 9 DBs provisioned, IDs populated in `.env`, integration shared, MAMS project registered.

### Acceptance
- [ ] 3 existing DBs (Projects Registry / Activity Log / Communication Log) extended per template §2.1-2.3
- [ ] 6 new DBs created per template §2.4-2.9: Sprints, Tasks, Skills Registry, Decisions & Approvals, Risks & Incidents, Retrospectives
- [ ] `NOTION_DB_*_ID` вариаблес заполнены в `.env` (все 9)
- [ ] Notion integration "MAMS-Agents" shared со всеми 9 DBs
- [ ] `notion-fetch` по любому DB возвращает valid schema
- [ ] Projects Registry имеет entry `MAMS` (code: `MAMS`, status: In Progress)
- [ ] Sprint `MAMS S0 — Bootstrap` создан
- [ ] Первая Task `DG-1 verification` создана и marked done
- [ ] Activity Log имеет entry `DG-1 PASSED`
- [ ] Decision `Move to DG-2` создана и approved Alex'ом

### Артефакты
- Notion URLs всех 9 DBs (в `README.md` secrets-section)
- Git commit `chore: DG-1 passed — Notion DBs ready`

### Блокеры → Risks & Incidents
- Integration permission errors → `Type: Risk, Root Cause: webhook`
- Schema mismatch (formula errors, etc.) → `Type: Risk, Root Cause: data`

---

## DG-2 — Plugin valid + PM-Agent starts

**Goal:** плагин установлен, pm-director subagent отвечает на тестовый prompt.

### Acceptance
- [ ] `.claude-plugin/plugin.json` валиден (jq parse OK, `name == "mams"`)
- [ ] `agents/` содержит 12 `.md` файлов
- [ ] Каждый agent.md имеет valid YAML frontmatter с полями `name`, `description`, `tools`
- [ ] `.mcp.json` (не `.example`) создан, все P0 env-refs разрешаются
- [ ] Plugin упакован: `/tmp/mams.plugin` (zip) создан
- [ ] Plugin установлен в Claude Code локально
- [ ] Test prompt работает: `pm-director` вызван через Task tool → отвечает summary по MAMS project без ошибок
- [ ] Logs: Activity Log entry `DG-2 dry-run OK` (Source: Code, Category: Note)
- [ ] Decision `Move to DG-3` approved

### Артефакты
- `/tmp/mams.plugin` (+ копия в `mams-bootstrap/releases/mams-0.1.0.plugin`)
- dry-run transcript (Obsidian Meeting note если доступен)

### Блокеры
- YAML frontmatter invalid → читать docs Claude Code plugins + fix
- MCP npm packages not published → fallback на curl + skill wrapper
- PM-Agent hallucinates Notion data → baseline fail, увеличить explicit read steps в system prompt

---

## DG-3 — First end-to-end task through PM + 1 specialist

**Goal:** реальная задача (mini-SEO audit) проходит цикл `PM → seo-aeo-specialist → PM → Activity Log → done`.

### Prerequisites (P0 skills ready)
- [ ] `risk-tiering` (MAMS-custom) в `skills/` с SKILL.md
- [ ] `notion-orchestration` (MAMS-custom)
- [ ] `project-workflow` (imported from public Anthropic skills)
- [ ] `productivity:task-management`, `productivity:memory-management` (imported)
- [ ] `seo-audit` (public + 2026 signals extension)
- [ ] `seo-content`, `content-creation`, `humanizer` (public)
- [ ] `doc-coauthoring` (public)

Каждый skill имеет entry в Skills Registry DB (status: draft на старте, canary после первого успешного invocation).

### Acceptance
- [ ] PM-Agent получил request типа `Сделай мини-SEO аудит {URL}`
- [ ] Decompose: PM создал 3 subtask в Tasks DB (content/technical/links), все assigned to seo-aeo-specialist
- [ ] Spawn: subagent seo-aeo-specialist запустился через Task tool
- [ ] Specialist использовал skill `seo-audit` (или эквивалент) — не писал аудит «из головы»
- [ ] PM консолидировал report, положил в `artifacts/` (Notion attach или Obsidian file)
- [ ] Tasks перешли в `done`, Activity Log имеет полную цепочку
- [ ] Если PM пытался делать SEO сам (не делегировал) — это **FAIL**, исправь system prompt pm-director

### Артефакты
- SEO audit deliverable (MD или Notion page)
- Full Activity Log chain (минимум 8-10 entries)
- Decision `Move to DG-4` approved

### Cost checkpoint
Сумма `Cost USD` по всем Activity entries DG-3 run ≤ 2 USD. Если выше — фикси context bloat / retries.

---

## DG-4 — E2E scenario from Sample reproduced

**Goal:** полный сценарий из `docs/MAMS_Sample_E2E_Scenario.md` воспроизведён end-to-end (NeuroPsychoOptimum Tier 1, Week 8 — комплексный sprint).

### Prerequisites
- DG-3 passed
- Больше специалистов активны: минимум strategist, seo-aeo-specialist, content-lead, link-builder, analytics-specialist
- Skills P1 expanded: +`ahrefs-seo` или `semrush-api`, `campaign-plan`, `performance-report`, `data:analyze`

### Acceptance
- [ ] Sprint-level task `NPO S3 — Acceleration` провёден end-to-end
- [ ] Все 5 участвующих специалистов вызывались в правильном порядке (DAG per E2E scenario)
- [ ] Artifacts produced соответствуют sample (content calendar, SEO audit + recommendations, link outreach targets, analytics dashboard template)
- [ ] Tiered HITL сработал: хотя бы один Amber approval прошёл через digest, хотя бы один Red — через sync
- [ ] Skills Registry показывает ≥ 3 skills в `canary`, ≥ 5 в `stable`
- [ ] Sprint Retrospective создана с `What went well / What didn't / Action Items`

### Артефакты
- Sprint retro page
- Artifacts bundle (content calendar .md, SEO report .pdf, ads brief etc.)
- Budget report: cumulative cost ≤ `MAMS_SPRINT_TOKEN_CAP_USD` × 0.9

### Sign-off
Alex подписывает Decision `MAMS Phase 1 — production-ready`. С этого момента можно запускать реальные клиентские проекты через MAMS.

---

## После DG-4 (Phase 1 → Phase 2)

Не блокирующие рекомендации для следующей итерации:

1. **Skill-Updater pipeline live.** Включить `skill-updater` agent в production — он автоматически мониторит performance skills и предлагает patches через G1-G4 gates.
2. **Niche-Expert first RAG ingest.** Для каждого нового клиента — niche-expert собирает corpus (см. Skill Inventory §7), строит hybrid RAG.
3. **Supabase Skill Registry backend.** Мигрировать Skills Registry Notion-only → Supabase primary + Notion mirror.
4. **Webhooks live.** Настроить Notion webhooks → server → hook handlers (из `plugin-scaffold/hooks/`).
5. **Golden-eval CI.** GitHub Actions workflow запускает `agent-as-evaluator` на каждый PR в `skills/`.

---

## Emergency rollback

Если что-то идёт сильно не так на любом gate:

1. Остановить текущие агент-сессии (Ctrl+C в Claude Code).
2. Открыть Decisions & Approvals DB → создать Decision `Emergency rollback to DG-{N-1}` (tier: Red, approver: Alex sync).
3. Revert git commits до предыдущего gate's commit.
4. Restore `.env` и Notion DBs если трогали schemas.
5. Записать postmortem в Retrospectives DB (Scope: Incident) в течение 24h.

---

## Git tags

На каждый gate — git tag `dg-{N}` на commit где gate passed:

```bash
git tag -a dg-1 -m "DG-1 passed — Notion DBs ready"
git tag -a dg-2 -m "DG-2 passed — Plugin + PM-Agent OK"
git tag -a dg-3 -m "DG-3 passed — First E2E task OK"
git tag -a dg-4 -m "DG-4 passed — Full E2E scenario reproduced"
git push --tags
```
