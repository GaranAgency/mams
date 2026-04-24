---
name: notion-orchestration
description: >
  Standardized wrapper for all MAMS Notion Command Center writes: Activity Log,
  Tasks, Sprints, Decisions & Approvals, Risks & Incidents, Communication Log,
  Retrospectives. Provides canonical payload schemas, relation lookup helpers,
  and outbox fallback when Notion MCP or API is unavailable. Primary consumer:
  pm-director; secondary: all specialist agents when they log their own work.
  Full spec: MAMS_Skill_Inventory.md §3.2.
version: 0.1.0
owner: pm-director
status: draft
---

# notion-orchestration

## Canonical payloads

### Activity Log entry
Always include: `Entry` (≤160 char), `Date` (YYYY-MM-DD), `Project` (relation,
look up by Code in Projects Registry), `Who` (agent id or "Alex"), `Source`
(Agent | Chat | Code | System), `Category` (Task Done | Task Created | Task
Deleted | Task Updated | Decision | Communication | Blocker | Note | Gate-Event),
`Details` (free text, include skill versions + run_ids), `Related Task`
(optional relation), `Tier` (Green | Amber | Red | n/a).

### Task
Required: `Title` (format `[CODE] Description`), `Project` (relation),
`Sprint` (relation if active), `Owner` (agent id or human), `Priority`
(P0 | P1 | P2 | P3), `Due` (YYYY-MM-DD), `Tier`, `Status` (Backlog | Ready |
In Progress | Blocked | Review | Done | Cancelled), `Dependencies`
(self-relation). Optional: `Description`, `Category`, `Cost USD`.

### Sprint
`Name` (format `[CODE] S{n} — {theme}`), `Project`, `Start`, `End`, `Goal`,
`Status` (Planned | Active | Completed | Retro Done).

### Decision
`Title`, `Date`, `Tier`, `Status` (Proposed | Approved | Rejected | Superseded),
`Proposer`, `Approver`, `Rationale`, `Options` (array), `Outcome`.

### Risk / Incident
`Title`, `Type` (Risk | Incident), `Severity` (Low | Medium | High | Critical),
`Root Cause` (enum per template), `Status`, `Owner`, `Detection Date`,
`Resolution`, `Related Project`, `Postmortem URL`.

### Communication Log
`Subject`, `Date`, `Channel` (Email | Chat | Call | Meeting | Slack),
`Direction` (Inbound | Outbound | Internal), `Party`, `Project`,
`Action Required`, `Next Step`, `Artifacts`.

## Write protocol

1. Read the target DB schema once per session (cache in memory).
2. Resolve relation IDs by title-match on cached index.
3. Attempt Notion MCP call (`notion-create-pages` or `notion-update-page`).
4. On failure:
   - Network/timeout → retry up to 3 times with exp backoff.
   - Auth error → write payload to `~/.mams/outbox/<date>_<agent>.jsonl`,
     emit Blocker Activity Log entry (locally cached too).
   - Schema error → log error, DO NOT retry, surface to caller for fix.
5. On success: return `{ok: true, page_id, url}`. On cached: return
   `{ok: false, cached: true, path: "~/.mams/outbox/..."}`.

## Outbox flush

When Notion credentials are restored, call flush procedure:
- Iterate JSONL lines in outbox chronologically.
- Re-apply each op; on success, remove line; on failure, keep and continue.
- Emit single summary Activity Log entry: `"Outbox flush: N ops applied, M failed"`.

## Read helpers

- `findProjectByCode(code)` → relation id or null (searches Projects Registry).
- `findActiveSprint(projectCode)` → sprint relation id.
- `findTaskByTitle(title)` → task relation id (exact match).
- `listRecentActivity(projectCode, daysBack)` → array of entries for context
  priming by PM-Director before decomposition.

## Naming + conventions

- Task titles ALWAYS `[CODE] Description` (e.g. `[MAMS] Author P0 skill risk-tiering`).
- Sprint names `[CODE] S{n} — {theme}`.
- Dates in ISO `YYYY-MM-DD`, UTC.
- Activity Log Entry must be ≤160 chars; overflow goes to Details.

## Failure-mode logging

Every time this skill caches to outbox, the caller MUST also:
1. Surface the blocker in the current agent response.
2. Add a row to Risks & Incidents DB (Type=Incident, Severity=Medium,
   Root Cause=infra) unless Alex already acknowledged the same blocker today.

## Version / changelog

- v0.1.0 (2026-04-23) — initial draft during DG-3 start. Outbox fallback first
  exercised in this very session (no live Notion token).
