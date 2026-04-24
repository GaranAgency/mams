# MAMS — Notion Workspace Template v2.0

**Companion to:** `MAMS_Architecture_Report.md` v2.0 §16 (Notion Orchestration Layer), `MAMS_Agent_Specs.md` v2.0, `MAMS_Skill_Inventory.md` v2.0, `MAMS_Sample_E2E_Scenario.md` v2.0
**API version:** 2026-03-11 [FACT]
**Integration:** Notion MCP (official) + webhooks; Activity Log + Communication Log already live in master Command Center Alex (https://www.notion.so/327326fe46c58134a1e7c388b86020ed).
**Purpose:** concrete, copy-implementable schema + views + automations for running MAMS on Notion as orchestration layer.

Citation tags: **[FACT]** verifiable primary/vendor doc · **[EXPERT-CLAIM]** practitioner consensus · **[CONTESTED]** ≥2 conflicting positions · **[FOUNDATIONAL]** pre-2026 pattern still current.

---

## 0. Executive Decisions (Notion Orchestration)

1. **Notion = single source of truth for orchestration state**, not content storage. Content (SEO reports, articles, PRDs) lives in Drive/Obsidian/Git; Notion holds pointers + status + audit trail.
2. **API version pinned to 2026-03-11** [FACT]; upgrades scheduled quarterly with G1-G4 gate discipline from Skill Inventory.
3. **All DB writes go through `notion-orchestration` skill**, never raw API — enables PreToolUse guardrails + idempotent writes keyed by composite IDs.
4. **Webhook aggregation = 5-minute sliding window** [FACT] + dedup by `request_id` to tolerate out-of-order delivery (lesson from Scenario I-002).
5. **Data-source events (added 2025-09-03)** [FACT] subscribed for all 9 MAMS DBs to drive dashboards + anomaly watchers.
6. **No cross-workspace moves by agents** — denylist item on `notion-orchestration`; only humans.
7. **`in_trash` semantics** [FACT] respected in all queries — trashed rows excluded from active dashboards but retained for audit.
8. **Position-based block operations** [FACT] used for precise sprint-board layout and deterministic block ordering.

---

## 1. Workspace Structure

### 1.1 Top-level hierarchy

```
📂 MAMS Command Center  (root page, child of master Command Center)
  ├── 📋 Projects Registry          (DB — existing, shared)
  ├── 📝 Activity Log               (DB — existing, shared)
  ├── 💬 Communication Log          (DB — existing, shared)
  ├── 🗓️ Sprints                    (DB — new)
  ├── ✅ Tasks                       (DB — new)
  ├── 🧠 Skills Registry             (DB — new, mirrors Supabase)
  ├── 🔐 Decisions & Approvals      (DB — new, HITL audit)
  ├── ⚠️ Risks & Incidents          (DB — new)
  ├── 📊 Dashboards                  (page, hosts embedded dashboards)
  ├── 📅 Retrospectives              (DB — new)
  └── 📚 Runbooks & Playbooks       (page, links to Obsidian)
```

### 1.2 DB count summary

| # | DB | New vs existing | Primary purpose |
|---|---|---|---|
| 1 | Projects Registry | existing | Master list of projects with pointers |
| 2 | Activity Log | existing | Every significant action, any project |
| 3 | Communication Log | existing | Every key communication |
| 4 | Sprints | **new** | Sprint boundaries per project |
| 5 | Tasks | **new** | Individual task execution + audit |
| 6 | Skills Registry | **new** | Mirror of Supabase skill manifest |
| 7 | Decisions & Approvals | **new** | HITL tier approvals, audit trail |
| 8 | Risks & Incidents | **new** | Green/Amber/Red incidents with RCA |
| 9 | Retrospectives | **new** | Sprint/quarter retros with action items |

---

## 2. Database Schemas

Property types use Notion API 2026-03-11 conventions [FACT]. Foreign keys via `relation` properties (bidirectional where helpful). Rollups for aggregate views.

### 2.1 Projects Registry (existing — aligned)

| Property | Type | Notes |
|---|---|---|
| Name | title | Client-facing project name |
| Code | rich_text (unique) | Short code (e.g., NPO, MFR) — per CLAUDE.md naming convention |
| Status | select | `discovery \| active \| paused \| closed \| archived` |
| Summary | rich_text | 2-3 sentence elevator |
| Master Page URL | url | Top-level project page |
| Task Tracker URL | url | Legacy tracker (if any) |
| Owner | people | Human lead |
| Client Contact | relation → Communication Log | Primary contact person(s) |
| Start Date | date | |
| End Date | date | Nullable |
| Monthly Budget (USD) | number | For `risk-tiering` budget guards |
| Sprints | relation → Sprints | Rollup: current sprint |
| Tasks Open | rollup (count) | `Tasks` where status ≠ done & project = this |
| Incidents Open | rollup (count) | |
| Obsidian Folder | rich_text | Relative path in vault |

### 2.2 Activity Log (existing — aligned, extended)

Per CLAUDE.md spec. Extensions for MAMS:

| Property | Type | Notes |
|---|---|---|
| Entry | title | What was done (≤160 char) |
| Date | date | `date:Date:start` set at entry creation [FACT, compatible with 2026-03-11] |
| Project | relation → Projects Registry | Exact project |
| Who | select or people | PM-Director, Strategist, SEO-AEO-GEO, ... Skill-Updater, Human |
| Source | select | `Chat \| Cowork \| Code \| WhatsApp \| Manual \| Email \| Meeting \| Agent \| Webhook` |
| Category | select | `Task Done \| Task Created \| Task Deleted \| Task Updated \| Decision \| Communication \| Blocker \| Note \| Gate-Event \| Rollout-Event \| Rollback-Event` |
| Details | rich_text | Free-form; include skill versions + run_ids |
| Related Task | relation → Tasks | |
| Related Decision | relation → Decisions & Approvals | |
| Related Skill | relation → Skills Registry | When applicable |
| Tier | select | `Green \| Amber \| Red \| n/a` |
| Reversible | checkbox | |

**Index view:** "Last 14 days" sorted desc; grouped by Project.

### 2.3 Communication Log (existing — aligned)

Per CLAUDE.md spec. No schema change required. Add:

| Property | Type | Notes |
|---|---|---|
| Attachment | files | Optional (Loom link, PDF) |
| Sentiment | select | `positive \| neutral \| concerned \| escalating` — optional, filled by PM when notable |

### 2.4 Sprints (new)

| Property | Type | Notes |
|---|---|---|
| Name | title | e.g., "NPO S3 — Acceleration" |
| Project | relation → Projects Registry | |
| Start Date | date | |
| End Date | date | |
| Goal | rich_text | 2-3 sentences |
| Status | select | `planning \| active \| closing \| closed \| canceled` |
| Tasks | relation → Tasks | |
| Tasks Done | rollup (count where status=done) | |
| Tasks Total | rollup (count) | |
| Completion % | formula | `Tasks Done / Tasks Total` |
| Retrospective | relation → Retrospectives | |

### 2.5 Tasks (new)

| Property | Type | Notes |
|---|---|---|
| Name | title | |
| Project | relation → Projects Registry | |
| Sprint | relation → Sprints | |
| Status | select | `backlog \| in_progress \| blocked \| review \| done \| canceled` |
| Priority | select | `P0 \| P1 \| P2 \| P3` |
| Owner Agent | select | From MAMS agent list |
| Reviewer Agent | select | Optional |
| Tier | select | Green \| Amber \| Red |
| Approver Needed | select | `none \| digest \| sync` (auto from `risk-tiering`) |
| Decision | relation → Decisions & Approvals | For Amber/Red |
| Dependencies | relation → Tasks (self) | |
| Estimate (h) | number | |
| Actual (h) | number | |
| Artifacts | url[] or files | Drive/Git links |
| Skill(s) used | relation → Skills Registry | Multi |
| Started At | created_time | |
| Completed At | date | Set at status=done |
| Activity Entries | relation → Activity Log | |

### 2.6 Skills Registry (new, mirrors Supabase)

| Property | Type | Notes |
|---|---|---|
| Skill ID | title | e.g., `seo-audit` |
| Version | rich_text | semver e.g., `1.3.2` |
| Status | select | `draft \| canary \| stable \| deprecated \| blocked \| retired` |
| Owner Agent | select | |
| Category | select | shared-core \| seo-content \| paid-social-growth \| analytics-data \| dev-cro-ux \| pm-workflow-meta \| specialized |
| Default Tier | select | Green \| Amber \| Red |
| Last Eval Pass Rate | number | 0..1 |
| Last Eval Safety Rate | number | 0..1 |
| Last Eval Date | date | |
| Last Eval Run ID | rich_text | |
| Golden Set ID | rich_text | |
| Dependencies | rich_text | comma sep `skill@>=ver` |
| Supabase Row URL | url | Deep link |
| Git Commit SHA | rich_text | Immutable pointer |
| G1/G2/G3/G4 Last Runs | rich_text | `g1:ok g2:ok g3:ok g4:ok` shorthand |
| Rollout % (if canary) | number | 0 when stable |
| Changelog | rich_text | Last 3 versions summary |

### 2.7 Decisions & Approvals (new)

| Property | Type | Notes |
|---|---|---|
| Name | title | Decision headline |
| Project | relation → Projects Registry | |
| Tier | select | Green/Amber/Red |
| Requester | select | Owner agent |
| Approver Required | select | `digest \| sync \| automated` |
| Approver Human | people | Empty if automated |
| Approver Agent | select | For agent-to-agent approvals |
| Status | select | `requested \| digest_pending \| sync_pending \| approved \| rejected \| expired` |
| Requested At | created_time | |
| SLA Deadline | formula | `Requested At + tier SLA` |
| Resolved At | date | |
| Details | rich_text | Proposal + alternatives |
| Artifact(s) | url[] or files | |
| Linked Task | relation → Tasks | |
| Rollback Plan | rich_text | Required for Amber/Red |

### 2.8 Risks & Incidents (new)

| Property | Type | Notes |
|---|---|---|
| Name | title | Incident headline |
| Project | relation → Projects Registry | |
| Type | select | `Risk (potential) \| Incident (actual)` |
| Severity | select | `SEV-4 low \| SEV-3 medium \| SEV-2 high \| SEV-1 critical` |
| Status | select | `open \| investigating \| mitigated \| resolved \| postmortem-pending \| closed` |
| Owner Agent | select | |
| Detected By | select | Human \| Agent \| Watcher |
| First Detected | date | |
| Resolved | date | |
| Root Cause Category | select | `data \| skill \| budget \| ad-platform \| cms \| webhook \| human \| third-party \| other` |
| Postmortem URL | url | Obsidian or Notion page |
| Linked Tasks | relation → Tasks | |
| Linked Activity | relation → Activity Log | |

### 2.9 Retrospectives (new)

| Property | Type | Notes |
|---|---|---|
| Name | title | e.g., "NPO S3 Retro" |
| Scope | select | Sprint \| Quarter \| Incident |
| Project | relation → Projects Registry | |
| Sprint | relation → Sprints | Nullable (for quarter) |
| Incident | relation → Risks & Incidents | Nullable |
| Date | date | |
| What went well | rich_text | |
| What didn't | rich_text | |
| Action Items | relation → Tasks | Carried tasks |
| Skill-Updater Patches | relation → Skills Registry | Auto-created patches |

---

## 3. Webhook Configuration

### 3.1 Subscribed events

Per Notion 2026-03-11 [FACT]:
- `page.created`, `page.updated`, `page.deleted`, `page.undeleted`
- `data_source.content_updated`, `data_source.schema_updated`
- `comment.created`
- `database.created`, `database.updated`, `database.deleted`

### 3.2 Handler pipeline

```
Webhook receiver (Cloud Run endpoint)
     │
     ▼
Dedup by `request_id` (Redis, TTL 10 min)
     │
     ▼
Aggregation buffer (5-minute sliding window) [FACT]
     │
     ▼
Event classifier
  ├─ activity-log.created → propagate to downstream dashboards
  ├─ tasks.updated(status→done) → close loop w/ Activity Log entry if missing
  ├─ decisions.approved → unblock dependent tasks
  ├─ skills.status→stable → broadcast to agent pool (cache bust)
  └─ risks.severity→SEV-1 → page PM-Director + human on-call
     │
     ▼
Idempotent writers (composite keys)
```

### 3.3 Failure modes handled

| Failure | Handling |
|---|---|
| Duplicate delivery | Dedup by `request_id` |
| Out-of-order delivery | 5-min aggregation window reorders by `event_at` [FACT] |
| Missed event (outage) | Nightly reconciliation via `data_source.content_updated` full fetch; delta populated |
| Schema migration (2026-03-11 compatibility mode) | Translator: `parent.database_id` ↔ `data_source_id` [FACT] |

---

## 4. Views (canonical set per DB)

### 4.1 Projects Registry

- **Active Projects** — filter Status ∈ {discovery, active}, sort by End Date asc.
- **Billing view** — gallery grouped by Monthly Budget bucket.
- **Obsidian Sync Health** — table showing projects whose Last Activity Log < 48h ago (health beacon).

### 4.2 Activity Log

- **Today** — filter Date=today, all projects (answers "What was done today").
- **Last 7 days by Project** — group by Project.
- **Gate Events only** — filter Category ∈ {Gate-Event, Rollout-Event, Rollback-Event}.
- **Communications timeline** — Category=Communication, sort desc.

### 4.3 Communication Log

- **Action Required = yes** — outstanding actions.
- **By Channel** — group by Channel.
- **Client-inbound (30-day)** — filter Direction=Inbound, Date ≥ today-30.

### 4.4 Sprints

- **Active Sprints** — filter Status=active.
- **Sprint burn-down** — table showing Completion % over time (use linked rollup).

### 4.5 Tasks

- **My open tasks** — filter Owner Agent = (current viewer), Status ≠ done.
- **Blocked tasks** — filter Status=blocked.
- **Amber/Red awaiting approval** — filter Tier ∈ {Amber, Red}, Decision.Status=pending.
- **Sprint board** — Kanban grouped by Status.

### 4.6 Skills Registry

- **Stable skills** — filter Status=stable, sort by Last Eval Date.
- **Canary** — filter Status=canary with Rollout %.
- **Deprecation candidates** — pass-rate < 0.85 OR last-eval > 14d.
- **Red-tier skills** — filter Default Tier=Red (auditable).

### 4.7 Decisions & Approvals

- **Awaiting my digest** — filter Approver Human = me, Status=digest_pending.
- **Sync required** — Status=sync_pending.
- **SLA breach** — formula-based filter: SLA Deadline < now AND Status not in {approved, rejected}.

### 4.8 Risks & Incidents

- **Open incidents** — Type=Incident, Status ≠ closed.
- **SEV-1/SEV-2** — critical severity.
- **Postmortem pending** — Status=postmortem-pending.

### 4.9 Retrospectives

- **Last quarter** — Scope=Quarter, Date in last 90d.
- **Incident retros** — Scope=Incident.

---

## 5. Automations

### 5.1 Native Notion automations (formula + button)

| Trigger | Action |
|---|---|
| Task status → done | Formula auto-sets Completed At; button template "Log Activity" pre-fills Category=Task Done |
| Decision Approver Required = sync AND no Human | Notify Alex + PM-Director (Slack / Notion mention) |
| Risks & Incidents created with SEV-1 | Notion mention PM-Director + human on-call |

### 5.2 Agent-driven (via `notion-orchestration` skill)

| Source event | Skill action |
|---|---|
| PM creates Sprint | Skill populates sprint with carryover tasks + logs Activity (Category=Task Created) |
| Agent completes Task | Skill updates Status=done + logs Activity (Category=Task Done) + sets Completed At |
| `risk-tiering` returns Amber/Red | Skill creates Decision row + links to Task + notifies approver per tier |
| Skill-Updater promotes skill | Skill updates Skills Registry row (Status, Version, G1-G4) + Activity (Category=Rollout-Event) |
| Skill-Updater rollback | Activity entry Category=Rollback-Event + link to rollback plan in Decision |
| Incident created | Skill templates postmortem + assigns Owner Agent |

### 5.3 Watchers (scheduled)

Registered via `schedule` skill:

| Cadence | Watcher | Action |
|---|---|---|
| Hourly | Ad spend pacing | If >25% of remaining monthly budget in 1h → Activity entry, Amber escalation |
| Daily | KPI anomaly detection | GA4/Shopify/Klaviyo 2σ-drift → Activity entry + PM ping |
| Daily | Skill eval freshness | Any stable skill with Last Eval Date > 7d → candidate flag |
| Weekly | Sprint hygiene | Tasks in_progress > 5d → Blocker candidate |
| Weekly | Brand Radar pull | SOV delta → Activity entry |
| Monthly | Client-budget reconciliation | Actual vs budgeted → report to Strategist |
| Quarterly | Architecture retro scheduler | Opens retro row + invites |

---

## 6. Dashboards (page `📊 Dashboards`)

Built as embeds or linked-database blocks; can also be rendered as self-contained HTML via `data:build-dashboard` and embedded via URL unfurl.

1. **Portfolio Health** — rollups across Projects Registry (active projects, tasks open, incidents open, SLA compliance).
2. **Per-Project Dashboard** (templated) — current sprint status, recent Activity entries, open Decisions, KPIs from GA4 (embedded Looker Studio).
3. **Skill Health Dashboard** — eval pass rate trend per skill, canary progress, deprecation candidates, rollback count (30d).
4. **HITL Governance** — tier distribution (Green/Amber/Red) + SLA compliance heatmap; identifies approval bottlenecks.
5. **Incident Command** — open SEV-1/SEV-2, MTTD/MTTR trends, postmortem backlog.

---

## 7. Setup Playbook (for new project, per CLAUDE.md)

The `notion-orchestration` skill automates this end-to-end but the canonical human-auditable sequence is:

1. **Create Projects Registry row** (Name, Code, Summary, Start Date, Owner, Monthly Budget).
2. **Create Master Page** as child of Projects Registry row.
3. **Within Master Page, create child pages:**
   - Brief
   - Discovery Audits (placeholder; populated in Sprint 1)
   - Sprint Board (linked view of Tasks DB filtered by Project)
   - Runbooks (links to Obsidian)
4. **Filter views in shared DBs** to scope to this project:
   - Activity Log — Project-scoped view
   - Communication Log — Project-scoped view
   - Tasks — Project-scoped sprint board
   - Decisions — Project-scoped awaiting list
5. **Create first Sprint row** (e.g., S1 Discovery).
6. **Spawn first 4-6 Tasks** (parallel discovery tracks).
7. **Log Activity entries** for all Task creations (Category=Task Created, Source=Cowork).
8. **Create Obsidian folder** + `_MOC` + `_Chronology` + `People/{primary contact}.md`.
9. **Link Obsidian path** in Projects Registry row (Obsidian Folder field).
10. **Set up webhook subscriptions** for project-relevant DBs (data_source events).
11. **Register `schedule` watchers** for this project (ad spend, anomaly detection if applicable).

---

## 8. Migration Plan (existing master Command Center)

Alex already has Projects Registry + Activity Log + Communication Log in the master Command Center. Migration to full MAMS schema:

### Phase 1 (week 1)

- Add missing properties to Activity Log (Tier, Reversible, Related Skill, Related Decision). Notion allows non-breaking property additions [FACT].
- Create the 6 new DBs (Sprints, Tasks, Skills Registry, Decisions & Approvals, Risks & Incidents, Retrospectives).
- Populate Skills Registry from Supabase via `notion-orchestration` bulk import.

### Phase 2 (week 2)

- Wire webhook receiver; run dry-run with staging tokens.
- Migrate existing ad-hoc tasks from legacy trackers into Tasks DB, associating with proper Sprint rows.
- Onboard `schedule` watchers per active project.

### Phase 3 (week 3)

- Cut over first project (lowest-risk) to full MAMS — one sprint cycle.
- Retrospective + patch.
- Roll out to remaining projects one-by-one over 2-3 weeks.

Rollback plan per phase: keep legacy trackers read-only in parallel for 30 days; all writes via MAMS skills only; any data-loss incident triggers restore from daily Notion export.

---

## 9. Security & Permissions

Per Notion API 2026-03-11 [FACT] workspace permissions apply to integrations; MAMS bot integration is scoped to:

- Read: all 9 MAMS DBs + Projects Registry
- Write: Activity Log, Communication Log, Sprints, Tasks, Skills Registry, Decisions, Risks, Retrospectives
- No write: Projects Registry row deletion, workspace member management, cross-workspace moves — enforced via `notion-orchestration` denylist + PreToolUse hook.

Data-source events payloads contain change metadata only; full row reads require subsequent API call with access-checked token.

---

## 10. Eval Checklist (before first production use)

- [ ] All 9 DBs created with correct property types
- [ ] Relation properties bidirectional where specified
- [ ] Rollups tested against sample data
- [ ] Webhook receiver handles 3 out-of-order deliveries without double-counting
- [ ] `notion-orchestration` skill G1-G4 gates pass on staging workspace
- [ ] Dedup by request_id survives 500-event burst (load test)
- [ ] `risk-tiering` → Decision creation round-trip verified
- [ ] Template for each DB exported + version-controlled in Git
- [ ] MAMS bot integration permissions audited (least-privilege)
- [ ] Rollback exports running nightly
- [ ] Activity Log entry template pre-wired via Notion native template

---

## 11. Change Log (v1.0 → v2.0)

- Expanded to 9 DBs (added Sprints, Decisions & Approvals, Risks & Incidents, Retrospectives, Skills Registry) aligned with MAMS architecture §16.
- Pinned API version 2026-03-11 with explicit feature references (position object, in_trash, data_source events 2025-09-03, webhook aggregation 5-min) [FACT].
- Added webhook handler pipeline with dedup + aggregation + idempotent writers.
- Added views canon per DB and standard dashboards.
- Added setup playbook aligned with CLAUDE.md project creation rules.
- Added migration plan for existing master Command Center (additive, non-breaking).
- Added security model referencing `notion-orchestration` denylist + PreToolUse hook.
- Added pre-production eval checklist.

---

**End of Notion Workspace Template v2.0.**
