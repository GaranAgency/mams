# 01 — Notion DBs bootstrap (DG-1)

**Цель:** создать 6 новых Notion DB, которые MAMS использует в оркестрации, + верифицировать 3 existing (Projects Registry, Activity Log, Communication Log).

**Источник истины по схемам:** `docs/MAMS_Notion_Template.md` §2.

**Кто делает:** после запуска Claude Code на сервере — PM-Agent (через skill `notion-orchestration`) либо Claude Code напрямую. Можно делать вручную в Notion UI — без разницы, главное чтобы schema совпадала.

## DG-1 acceptance criteria

- [ ] Все 9 DB созданы и видны в Notion
- [ ] Notion integration расшарен со всеми 9 DB
- [ ] Все DB IDs записаны в `.env`
- [ ] Project "MAMS — Multi-Agent Marketing System" создан в Projects Registry (code: `MAMS`, status: "In Progress")
- [ ] Один тестовый Task ("DG-1 verification") создан и связан со sprint "MAMS S0 — Bootstrap"
- [ ] Activity Log entry "DG-1 completed" записан
- [ ] Claude Code может прочитать Projects Registry row MAMS через Notion MCP (`notion-fetch` test)

## 1. Existing DBs — проверить alignment

| DB | ID (в `.env`) | Что проверить |
|---|---|---|
| Projects Registry | `NOTION_DB_PROJECTS_REGISTRY_ID` | есть поля `Code`, `Summary`, `Master Page URL`, `Task Tracker URL`, `Status`, `Tier` |
| Activity Log | `NOTION_DB_ACTIVITY_LOG_ID` = `a8f3ad98-9a8f-4809-996d-cf5441cd5f6a` | поля из CLAUDE.md + `Tier`, `Decision Link`, `Skill used`, `Tokens`, `Cost USD` (см. Template §2.2) |
| Communication Log | `NOTION_DB_COMMUNICATION_LOG_ID` | поля из CLAUDE.md (§2.3) |

Если каких-то полей не хватает — добавить через Notion UI (Properties → Add property).

## 2. Создать 6 новых DBs

Схемы — в `docs/MAMS_Notion_Template.md` §2.4–2.9. Ниже — краткий план-чеклист.

### 2.1 Sprints (`NOTION_DB_SPRINTS_ID`)

Location: внутри `📁 MAMS` master page.

Properties: `Name (title)`, `Project (relation → Projects Registry)`, `Start Date`, `End Date`, `Goal (rich_text)`, `Status (select: planning / active / closing / closed / canceled)`, `Tasks (relation → Tasks)`, `Tasks Done (rollup)`, `Tasks Total (rollup)`, `Completion % (formula)`, `Retrospective (relation → Retrospectives)`.

### 2.2 Tasks (`NOTION_DB_TASKS_ID`)

Properties: `Name`, `Project (relation)`, `Sprint (relation)`, `Status (select: backlog/in_progress/blocked/review/done/canceled)`, `Priority (P0-P3)`, `Owner Agent (select)`, `Reviewer Agent (select, optional)`, `Tier (Green/Amber/Red)`, `Approver Needed (none/digest/sync)`, `Decision (relation → Decisions & Approvals)`, `Dependencies (relation → Tasks self)`, `Estimate (h) number`, `Actual (h) number`, `Artifacts (url/files)`, `Skill(s) used (relation → Skills Registry multi)`, `Started At (created_time)`, `Completed At (date)`, `Activity Entries (relation → Activity Log)`.

**Owner Agent options (copy-paste):**
```
pm-director, strategist, seo-aeo-specialist, content-lead, smm-specialist, ppc-specialist, cro-ux-specialist, dev-qa, link-builder, analytics-specialist, niche-expert, skill-updater
```

### 2.3 Skills Registry (`NOTION_DB_SKILLS_REGISTRY_ID`)

Properties: `Skill ID (title)`, `Version (rich_text, semver)`, `Status (draft/canary/stable/deprecated/blocked/retired)`, `Owner Agent`, `Category (shared-core/seo-content/paid-social-growth/analytics-data/dev-cro-ux/pm-workflow-meta/specialized)`, `Default Tier`, `Last Eval Pass Rate (number 0..1)`, `Last Eval Safety Rate (number 0..1)`, `Last Eval Date (date)`, `Last Eval Run ID`, `Golden Set ID`, `Dependencies`, `Supabase Row URL (url, Phase 2)`, `Git Commit SHA`, `G1/G2/G3/G4 Last Runs (rich_text)`, `Rollout % (number, canary only)`, `Changelog (rich_text)`.

### 2.4 Decisions & Approvals (`NOTION_DB_DECISIONS_ID`)

Properties: `Name (title)`, `Project (relation)`, `Tier`, `Requester (select)`, `Approver Required (digest/sync/automated)`, `Approver Human (people)`, `Approver Agent (select)`, `Status (requested/digest_pending/sync_pending/approved/rejected/expired)`, `Requested At (created_time)`, `SLA Deadline (formula)`, `Resolved At (date)`, `Details (rich_text)`, `Artifact(s) (url/files)`, `Linked Task (relation)`, `Rollback Plan (rich_text; required for Amber/Red)`.

**SLA Deadline formula (suggested):**
```
dateAdd(prop("Requested At"), if(prop("Tier") == "Red", 24, if(prop("Tier") == "Amber", 72, 0)), "hours")
```

### 2.5 Risks & Incidents (`NOTION_DB_RISKS_ID`)

Properties: `Name (title)`, `Project (relation)`, `Type (Risk / Incident)`, `Severity (SEV-1..4)`, `Status (open/investigating/mitigated/resolved/postmortem-pending/closed)`, `Owner Agent`, `Detected By (Human/Agent/Watcher)`, `First Detected`, `Resolved`, `Root Cause Category (data/skill/budget/ad-platform/cms/webhook/human/third-party/other)`, `Postmortem URL`, `Linked Tasks (relation)`, `Linked Activity (relation)`.

### 2.6 Retrospectives (`NOTION_DB_RETROSPECTIVES_ID`)

Properties: `Name`, `Scope (Sprint/Quarter/Incident)`, `Project (relation)`, `Sprint (relation, nullable)`, `Incident (relation → Risks & Incidents, nullable)`, `Date`, `What went well (rich_text)`, `What didn't (rich_text)`, `Action Items (relation → Tasks)`, `Skill-Updater Patches (relation → Skills Registry)`.

## 3. Share integration

Для каждой новой DB:

Settings → Connections → MAMS-Agents → `Connect`.

Либо один раз на родительскую страницу `📁 MAMS` (наследование).

## 4. Заполнить IDs в `.env`

Скопировать database_id (в URL после `www.notion.so/` → `...?v=...` — длинный UUID) в соответствующие переменные:

```bash
NOTION_DB_SPRINTS_ID=...
NOTION_DB_TASKS_ID=...
NOTION_DB_SKILLS_REGISTRY_ID=...
NOTION_DB_DECISIONS_ID=...
NOTION_DB_RISKS_ID=...
NOTION_DB_RETROSPECTIVES_ID=...
```

## 5. Views (canonical, рекомендованно)

Минимум на старте:

- **Tasks**: `My Queue` (filter: Owner Agent = current), `This Sprint` (filter: Sprint = active), `Blocked`, `Red Tier Pending Approval` (filter: Tier = Red AND Status != done)
- **Decisions**: `SLA At Risk` (filter: SLA Deadline < now() + 6h AND Status != approved)
- **Risks**: `Open High Severity` (filter: SEV-1/SEV-2 AND Status != closed)
- **Skills Registry**: `Canary` (filter: Status = canary), `Stable` (Status = stable)

Полный список views — §4 template doc.

## 6. Создать project entry "MAMS" в Projects Registry

```
Name: MAMS — Multi-Agent Marketing System
Code: MAMS
Summary: Универсальная AI-команда из 12 агентов под управлением PM-Director для полного цикла digital-маркетинга. Self-improving через Skill-Updater + Niche-Expert.
Master Page URL: https://www.notion.so/... (создать master page внутри 📁 MAMS)
Task Tracker URL: → ссылка на Tasks DB view filtered by Project = MAMS
Status: In Progress
Tier: High strategic priority
```

## 7. Создать sprint "MAMS S0 — Bootstrap"

```
Name: MAMS S0 — Bootstrap
Project: MAMS
Start Date: 2026-04-21
End Date: 2026-05-05 (2 недели на DG-1..DG-4)
Goal: Пройти все 4 deployment gates — от Notion DBs до первой end-to-end задачи через PM-Agent
Status: active
```

## 8. Создать первую Task для верификации

```
Name: DG-1 — Notion DBs verification
Project: MAMS
Sprint: MAMS S0 — Bootstrap
Status: in_progress
Priority: P0
Owner Agent: pm-director
Tier: Green
Estimate: 2h
```

## 9. Activity Log entry

```
Entry: DG-1 started — Notion DBs being provisioned
Date: 2026-04-21
Project: MAMS
Who: Alex + Claude Code
Source: Code
Category: Task Created
Details: 6 new DBs created per MAMS_Notion_Template §2.4-2.9. IDs populated in .env.
Related Task: DG-1 — Notion DBs verification
```

## 10. DG-1 PASS signal

Когда всё сделано — PM-Agent (или Claude Code) должен:

1. Обновить Task "DG-1 verification" → Status = `done`, Completed At = now
2. Создать Activity Log entry `Category: Task Done`, `Entry: DG-1 PASSED`
3. Записать в Decisions DB решение "Move to DG-2" (tier: Green, approver: Alex manual)
4. После approval → перейти к DG-2 (см. `03-deployment-gates.md`)

## 11. Troubleshooting

| Симптом | Решение |
|---|---|
| Relation dropdown не видит target DB | Notion integration не расшарен → Share with integration |
| `Notion-Version` mismatch | В `.mcp.json` notion server установить `Notion-Version: 2026-03-11` |
| Formula parse error в SLA Deadline | проверить имена свойств (кейс-сенситив), использовать `prop(...)` |
| Rollup Tasks Done показывает 0 | добавить filter в rollup: `Status == "done"` |

## 12. Next

→ `02-first-session-prompt.md` — готовый prompt для первой сессии Claude Code, который проведёт агента через весь DG-1 checklist автоматически.
