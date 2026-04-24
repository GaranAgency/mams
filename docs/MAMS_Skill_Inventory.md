# MAMS — Skill Inventory v2.0

**Companion to:** `MAMS_Architecture_Report.md` v2.0, `MAMS_Agent_Specs.md` v2.0
**NotebookLM corpus:** `d63a00bc-4188-4794-89b6-958361902bbb` (~88 sources, bulk-loaded April 2026)
**Skill model:** filesystem-based, `SKILL.md` headline + progressive-disclosure body (Anthropic Agent Skills pattern [FACT]: three-level disclosure — name+description ≤100 words preloaded, SKILL.md loaded on trigger, `references/*.md` + `scripts/*` loaded by Read/Bash only when skill needs them).
**Registry storage:** Supabase (metadata + pointers) + immutable versioned files in Git-backed vault (`/skills/{category}/{skill_id}/v{semver}/`).
**Versioning:** semver — patch auto, minor digest-approve, major sync-approve.
**Validation:** 4 Trust Gates (G1 Static → G2 Semantic → G3 Sandbox → G4 Permission Manifest) + golden-set eval + canary traffic staging before prod-rollout.

Citation tags: **[FACT]** verifiable primary/vendor doc · **[EXPERT-CLAIM]** practitioner consensus · **[CONTESTED]** ≥2 conflicting expert positions · **[FOUNDATIONAL]** pre-2026 methodology still current.

---

## 0. Executive Decisions (Skill Governance)

1. **Three-level progressive disclosure is non-negotiable** — violates Anthropic's canonical pattern and blows context budget otherwise [FACT].
2. **Skills are filesystem, not prompts** — each skill = folder with `SKILL.md` + optional `references/` + `scripts/`, so they compose deterministically with version control [FACT].
3. **Registry = Supabase metadata + Git vault for files** — Supabase handles ACL/versioning queries at latency; Git gives immutable audit trail and diff-ability for regulators.
4. **4 Trust Gates are sequential AND gating** — any G1-G4 red → rollout blocked; no Gate skipping even for "trivial patch" [FOUNDATIONAL, cross-domain SRE practice].
5. **Golden-set eval ≥90% pass-rate + 100% safety** — Anthropic's published rigor bar for production-grade skills; relax only with explicit sync approval logged to Activity Log [EXPERT-CLAIM].
6. **Per-agent allowlist + denylist hardcoded in system-prompt + enforced at PreToolUse hook** — defense in depth; prompt alone is insufficient (LLMs can be coerced), hook alone loses debuggability [FACT, SDK docs].
7. **Skill-creator/mcp-builder are Red-tier exclusive** — any agent authoring new capability surface must pass synchronous human approval; exception = Skill-Updater agent operating on pre-authorized patch scope (patch-level semver only).
8. **Skills follow the METAAGENT/SICA self-improving pattern cautiously** — MAMS allows automated patch-level updates (typo fixes, threshold tweaks) but minor/major changes require human digest or sync approval to avoid the documented drift failure modes in SICA (arXiv 2504.15228) [EXPERT-CLAIM].

---

## 1. Skill Registry Schema (per-skill metadata)

Stored in Supabase `skills.manifest` table with file-backed SKILL.md committed to Git vault. Every row JOINs to `skills.evaluations`, `skills.audit`, and `skills.permissions`.

```yaml
# Example row, materialised view
skill_id: seo-audit
version: 1.3.2
semver_level_last_change: patch     # patch|minor|major → gates which approval regime applies
owner_agent: seo-aeo-specialist
category: seo
status: stable                      # draft|canary|stable|deprecated|blocked|retired
created_at: 2026-02-04T09:12:00Z
updated_at: 2026-04-18T14:03:00Z
last_eval:
  golden_set_id: gs-seo-v3
  pass_rate: 0.94
  safety_rate: 1.00
  run_id: eval-2026-04-18-0142
  evaluator: golden-set-seo-v3
permissions:
  read: [gsc, ahrefs, semrush, web, notion:read]
  write: [notion:activity-log, notion:sprints-db, files:/audit/**]
  denied: [prod-cms, prod-ads-budget-change, client-slack:broadcast]
dependencies:
  - research-via-notebooklm@>=2.6
  - data:analyze@>=1.0
  - seo-content@>=1.1
evaluator: golden-set-seo-v3
gate_results:
  g1_static:  { pass: true, run: static-2026-04-18-0001 }
  g2_semantic: { pass: true, run: sem-2026-04-18-0031, judge_model: claude-sonnet-4-6 }
  g3_sandbox: { pass: true, run: sbx-2026-04-18-0012, fake_mcp_profile: seo-fake-v2 }
  g4_permission_manifest: { pass: true, run: pm-2026-04-18-0005, drift_delta: 0 }
canary:
  pct: 0          # 0 = fully stable, >0 while in canary phase
  started: null
  end_criteria: { min_runs: 50, min_pass_rate: 0.92 }
changelog: |
  1.3.2 (2026-04-18) — INP 2026 threshold added; golden-set regenerated for new metric
  1.3.1 (2026-03-22) — AEO/AI-citation checklist integrated (post-March 2026 core update)
  1.3.0 (2026-02-18) — merged topical-authority detector from research-via-notebooklm
```

---

## 2. Skill Catalog — 7 Categories

Skills inherit the base Anthropic progressive-disclosure pattern. Each entry notes **primary users** (agents), MAMS-tier (Green/Amber/Red default risk), and **primary eval type**.

### Category 1. Shared Core (any agent, load on-demand)

| Skill ID | Purpose | Primary users | Default tier | Eval |
|---|---|---|---|---|
| `research-via-notebooklm` v2.6 | End-to-end research with corpus-ranking, saturation detection, audit-and-regenerate [EXPERT-CLAIM] | Niche-Expert, Skill-Updater, Strategist | Green (read-only) | Golden methodology — do not patch without sync approval |
| `consolidate-memory` | Periodic KB reflection, dedup, stale-fact fix (inspired by METAAGENT reflection step) | Skill-Updater, Niche-Expert | Amber | Golden set on retention fidelity; before/after F1 |
| `synthesize-research` | Interview/survey/SERP → insight distillation | Strategist, Niche-Expert, PM | Green | Manual review on first 10 synths per domain |
| `humanizer` | Strip AI-pattern tells from final text | Content, SMM, Link-Builder | Green | Pre/post perplexity+pattern score |
| `doc-coauthoring` | Structured doc-write workflow (brief → draft → refine → verify) | PM, Strategist | Green | Manual review |
| `skill-creator` | Create/update skill files (Anthropic canonical authoring pattern) [FACT] | **Skill-Updater ONLY** | **Red default** | Sandbox mandatory; G1–G4 gated |

### Category 2. SEO & Content (post-March-2026 update aware)

| Skill ID | Purpose | Primary users | Default tier |
|---|---|---|---|
| `seo-audit` | Technical + content + AEO + topical-authority audit (March 2026 core update signals) | SEO-AEO-GEO, Strategist | Green |
| `seo-content` | E-E-A-T readiness + AEO-chunk format check + thin-content detection | Content, SEO, Reviewer | Green |
| `ahrefs-seo` | Ahrefs MCP/API toolkit (DR, backlinks, keywords, SERP, rank-tracker, Brand Radar for AI citations) | SEO, Analytics, Link-Builder | Green (read) / Amber (rank-tracker writes) |
| `semrush-api` | Semrush data: domain, keyword, backlink, competitor, ad copies, trends | SEO, Analytics | Green |
| `content-creation` | Channel-specific long-form drafting with voice governance | Content, SMM, Strategist | Green |
| `draft-content` | Blog/email/landing/press drafting | Content, SMM, Link-Builder | Green |
| `brand-review` | Voice/style/legal compliance check | Reviewer, Content | Green |
| `landing-page-designer` | Two landing-page variants under paid traffic constraints | CRO/UX, Content, PPC | Green |

### Category 3. Paid / Social / Growth

| Skill ID | Purpose | Primary users | Default tier |
|---|---|---|---|
| `campaign-plan` | Campaign brief + audience + creative + calendar (cross-channel) | Strategist, PPC, SMM | Green |
| `email-sequence` | Multi-touch nurture/onboarding/launch/win-back | Content, Link-Builder | Green |
| `performance-report` | Channel performance with optimization recommendations | PPC, SMM, Analytics | Green |
| `forecast` | Weighted pipeline/budget forecast (best/likely/worst) | PPC, Strategist | Amber (budget-impact) |
| `competitive-brief` | Competitor positioning + gap + battlecards | Strategist, SEO | Green |

### Category 4. Analytics / Data

| Skill ID | Purpose | Primary users | Default tier |
|---|---|---|---|
| `data:analyze` | Metric lookup → full analysis → insight | Analytics, all (via Analytics handoff) | Green |
| `data:explore-data` | Dataset profiling, quality, null-rate, duplicate check | Analytics | Green |
| `data:statistical-analysis` | Descriptive, trend, outlier detection, hypothesis testing | Analytics, CRO | Green |
| `data:create-viz` / `data:data-visualization` | Publication-quality charts (matplotlib, seaborn, plotly) | Analytics, Content | Green |
| `data:build-dashboard` | Self-contained HTML dashboard | Analytics, PM | Green |
| `data:sql-queries` / `data:write-query` | Cross-dialect SQL (Snowflake, BigQuery, Databricks, Postgres) | Analytics, Dev | Green (read) / Amber (write/DDL) |
| `data:validate-data` | QA analysis pre-share (methodology, bias, math) | Analytics, Reviewer | Green |
| `metrics-review` | Periodic product/marketing metrics review with scorecard | Analytics, PM, Strategist | Green |
| `data:data-context-extractor` | Bootstrap a company-data-knowledge skill from analyst interviews | Analytics, Skill-Updater | Amber |

### Category 5. Dev / CRO / UX

| Skill ID | Purpose | Primary users | Default tier |
|---|---|---|---|
| `architecture` | ADR creation/evaluation with trade-off tables | Dev, Strategist | Green |
| `testing-strategy` | Test plans (unit/integration/E2E/perf/security) | Dev, QA | Green |
| `deploy-checklist` | Pre-deploy verification (CI, migrations, flags, rollback triggers) | Dev | Amber (touches prod) |
| `webapp-testing` | Playwright-driven frontend testing with screenshot diffs | Dev, QA, CRO | Green |
| `code-review` | Security/perf/correctness review | Dev, Reviewer | Green |
| `debug` | Structured diagnosis (reproduce → isolate → diagnose → fix) | Dev | Green |
| `design-critique` | Design feedback (usability, hierarchy, consistency) | CRO/UX, Reviewer | Green |
| `design-handoff` | Developer handoff spec (tokens, states, responsive, edge cases) | CRO/UX | Green |
| `ux-copy` | Microcopy, CTAs, empty states, error messages | Content, CRO/UX | Green |
| `accessibility-review` | WCAG 2.1 AA audit (contrast, keyboard, screen-reader, touch target) | CRO/UX, Reviewer, Dev | Green |
| `user-research` | Plan/conduct/synthesize user research | CRO/UX, Strategist | Green |

### Category 6. PM / Workflow / Meta

| Skill ID | Purpose | Primary users | Default tier |
|---|---|---|---|
| `sprint-planning` | Sprint scope + capacity (accounting for PTO, meetings) | PM | Green |
| `stakeholder-update` | Exec/client/internal updates with audience-tailored versions | PM, Strategist | Green |
| `roadmap-update` | Roadmap reprioritization (Now/Next/Later) | PM, Strategist | Amber (commit-impact) |
| `write-spec` | PRD/feature spec from problem statement | PM, Strategist, Dev | Green |
| `project-workflow:project-workflow` | Long-running task methodology (cross-session context) | PM, Skill-Updater | Green |
| `productivity:task-management` | TASKS.md cross-session task tracking | PM | Green |
| `productivity:memory-management` | Working memory (CLAUDE.md) + KB tier (memory/) | PM, all | Green |
| `productivity:update` | Task sync from trackers (Notion, Linear, Asana) | PM | Green |
| **`risk-tiering`** (MAMS-custom) | Green/Amber/Red decision classifier (§12 Architecture) | PM | Green (meta-skill) |
| **`notion-orchestration`** (MAMS-custom) | Notion DB/webhook/MCP management, cross-link artifacts | PM | Amber (writes to shared system) |

### Category 7. Specialized / Tool-specific

| Skill ID | Purpose | Primary users | Default tier |
|---|---|---|---|
| `hunter-io` | Email find + verify via Hunter.io | Link-Builder | Amber (touches contact surface) |
| `apify-api` | Apify actor fallback (rotate across 4 keys on quota/rate limit) | Niche-Expert, Skill-Updater | Amber (budget-capped) |
| `schedule` | Scheduled/recurring task registration | PM, Skill-Updater | Green |
| `mcp-builder` | Build new MCP servers (FastMCP Python or MCP SDK TS) [FACT] | Dev, Skill-Updater | **Red** |
| `canvas-design` | Static visual art PNG/PDF | Content, Design | Green |
| `pptx` / `docx` / `xlsx` / `pdf` | Office-format artifact creation (canonical Anthropic skills) [FACT] | All (via PM) | Green |
| `theme-factory` | Artifact theming (10 pre-set themes + custom) | Content, Design | Green |
| `obsidian-connector:obsidian-notes` | Obsidian vault read/write via Local REST API | PM (orchestration), Skill-Updater | Amber (writes to personal KB) |
| `ahrefs-seo` / `semrush-api` / `hunter-io` / `apify-api` | External vendor APIs with fallback ladders | Respective specialists | As per row above |

---

## 3. MAMS-Custom Skill Specifications

### 3.1 `risk-tiering` v1.0

**Purpose:** Classify any decision as Green/Amber/Red per the tier framework in `MAMS_Architecture_Report.md` §12.

**Inputs (JSON):**
```json
{
  "intent_type": "content_publish | budget_change | scope_change | client_broadcast | tech_migration | skill_update | ... ",
  "magnitude": { "unit": "USD | posts | percent | files", "value": 1200 },
  "reversibility": "instant | <24h | <7d | irreversible",
  "legal_sensitivity": "none | disclosure | claims | medical/financial | regulatory",
  "client_visibility": "internal | client | public"
}
```

**Outputs:**
```json
{ "tier": "green|amber|red",
  "reason": "≥80% budget delta triggers Amber per §12 matrix",
  "approver_needed": "digest|sync|none",
  "sla_hours": 4 }
```

**Rules:** static lookup matrix + LLM-judge for ambiguous cases (e.g., medium-budget medical disclaimer lands Amber by magnitude, Red by legal — LLM-judge breaks tie conservatively).

**Eval:** 50 historical test cases (manually tiered by human PM) → accuracy ≥0.95; conservative-bias check (false-Green ≤1%).

**Gate profile:** G1 static ✓, G2 semantic ✓ (judge asks "does description match rules-applied?"), G3 sandbox not applicable (pure reasoning, no side-effects), G4 permission manifest trivial (no external calls).

---

### 3.2 `notion-orchestration` v1.0

**Purpose:** Manage Notion as orchestration layer — create Sprints, Tasks, Activity Log rows, Comm Log rows; set up webhooks; cross-link artifacts between Notion pages, Obsidian notes, Google Drive docs, and file outputs.

**Inputs:** action verb + payload (action ∈ {create_sprint, create_task, complete_task, log_activity, log_comm, attach_artifact, setup_webhook, cross_link, batch_update_status}).

**Outputs:** Notion page-id + confirmation record `{object_id, type, action_taken, at_utc, audit_ref}`.

**Capabilities (notion-api 2026-03-11):**
- Block operations support `position` object for precise insertion [FACT].
- `in_trash` property recognized on all objects [FACT].
- `data_source.*` webhook events subscribed (added 2025-09-03) [FACT].
- Webhook aggregation: 5-minute window to handle out-of-order delivery [FACT].
- Legacy `parent.database_id` remains accepted; internal translation to `data_source_id` [FACT].

**Denylist (hardcoded):** delete Projects Registry row; workspace-settings changes; member-permission changes; cross-workspace moves.

**Eval:** integration tests against staging workspace:
1. Round-trip create → update → delete Task, asserting data_source events arrive within 5-min aggregation window.
2. Webhook out-of-order robustness: inject duplicate/reorder → dedup by `request_id`.
3. ACL drift: attempt denied operation → verify PreToolUse hook blocks and audit logs refusal.

**Gate profile:** G3 sandbox mandatory (staging workspace with fake MCP profile); G4 permission manifest critical — any write outside `notion:read`, `notion:write:{activity-log, comm-log, sprints-db, tasks-db}` triggers block.

---

### 3.3 `skill-updater-pipeline` v1.0 (internal, used by Skill-Updater agent only)

**Purpose:** End-to-end patch pipeline — detect signal → draft diff → validate via G1–G4 → canary rollout → full rollout → audit log.

**Pipeline stages:**

| Stage | Input | Action | Output | Gate |
|---|---|---|---|---|
| 1. Detect | news URL / retrospective finding / rollback event / manual request | Parse trigger + classify patch/minor/major | Skill candidate + intent bundle | — |
| 2. Draft | intent bundle + current skill version | Generate diff via `skill-creator`; update SKILL.md/references/scripts | Git branch `skill/{id}/v{next-semver}` | — |
| 3. Static validate | branch | Run linters + regex deny-pattern check + license compliance | Pass/fail + lint report | G1 |
| 4. Semantic validate | branch + description | LLM-judge: does body match claimed description? Intent drift? | Pass/fail + judge rationale | G2 |
| 5. Sandbox validate | branch | Isolated worktree + fake MCP tools + behavior suite | Pass/fail + execution trace | G3 |
| 6. Permission manifest validate | observed calls vs declared | Compare declared `permissions.read/write` vs actual calls in G3 | Pass/fail + drift-delta | G4 |
| 7. Golden-set eval | branch | Run domain golden set (20-100 cases) | pass_rate, safety_rate | ≥0.9 / 1.0 |
| 8. Canary | branch | 5% traffic for N runs (default N=50) | canary pass_rate | ≥0.92 |
| 9. Promote | canary stats | Merge to stable; Git tag v{semver}; Supabase manifest update | Stable version | — |
| 10. Audit | all above | Activity Log entry + Obsidian chronology + rollback plan committed | Audit ref | — |

**Inputs:** trigger descriptor; **Outputs:** Registry commit + Activity Log entry with evaluator-run-id, Gate runs, rollout events, rollback plan.

**Abort/rollback:** any Gate fail → branch marked `blocked` + Activity Log entry Category=Blocker; revert to previous stable in <10 min (driven by `schedule`-registered watcher).

**Gate profile on itself (meta):** `skill-updater-pipeline` runs under sandbox with its own G1-G4 applied to the pipeline code — turtles all the way down.

---

### 3.4 `agent-as-evaluator` v1.0 (MAMS-custom, mirrors subagent-judge pattern from SDK)

**Purpose:** Run second-pass LLM-judge evaluation on any agent output (content, audit, code review, spec) via isolated subagent context.

**Inputs:** artifact + rubric (YAML with criteria, weight, pass threshold).

**Outputs:** `{score, criterion_scores[], rationale, blocking: bool, fix_suggestions}`.

**Eval:** human-labeled rubric set (30 artifacts × 5 rubrics); judge-vs-human kappa ≥0.75.

**Tier:** Green (pure reasoning); may flag Amber/Red artifacts for human escalation but does not itself execute writes.

---

## 4. Governance & Lifecycle

### 4.1 Status machine

```
   [draft]
      │
      ▼
  [canary] ──── ≥0.92 pass-rate + min runs ───▶ [stable]
      │                                              │
      │  pass<0.85 or safety<1.0                     │  pass<0.85 × 3 runs
      ▼                                              ▼
  [blocked] ◀─── any G1-G4 fail ─── [stable] ─▶ [deprecated]
                                                     │
                                            auto-migration absent
                                                     ▼
                                                [retired]
```

### 4.2 Trust Gates (pre-rollout; no skipping)

| Gate | What it does | Tooling | Blocking threshold |
|---|---|---|---|
| **G1 Static** | Linter + regex for known-bad patterns (unrestricted network, `eval`, untrusted imports, hardcoded secrets, disallowed env vars) | ruff/eslint + custom patterns | any error → block |
| **G2 Semantic** | LLM-judge: body ↔ description alignment; intent-drift detection; refusal-bypass scan | Claude Sonnet 4-6 judge (cached; deterministic temp) | judge says "drift" → block |
| **G3 Sandbox** | Isolated worktree + fake MCP tools + behavior suite + deterministic input/output recording | Agent SDK with mock MCP server | any uncaught exception or policy violation → block |
| **G4 Permission Manifest** | Declared `permissions.read/write` ≡ observed calls during G3 | diff declared vs observed | any unlisted call → block |

### 4.3 Golden-set eval

**Composition:** 20–100 curated `(input, expected_output, safety_criteria)` triples per skill, with:
- ≥70% baseline/common-case pass examples
- ≥20% edge/hard examples
- ≥10% adversarial/safety examples (prompt injection, role-elevation attempts, off-domain requests)

**Thresholds:** pass_rate ≥ 0.90 and safety_rate = 1.00 for canary→stable promotion.

**Regeneration trigger:** core update (e.g., March 2026 Google core update mandated `seo-audit` golden-set regen to include topical-authority signal evaluation).

### 4.4 Deprecation & retirement

**Auto-deprecate** on pass-rate < 0.85 for 3 consecutive runs OR any safety_rate < 1.0. Auto-migration path defined by Skill-Updater:
- If replacement skill exists → generate migration wrapper + notify owner agents.
- If no replacement → PM escalation → sync human decision.

**Retire** ≥30 days after deprecate with no call-sites in last 14 days.

### 4.5 Immutable audit trail

Every Registry commit logs to Activity Log (Notion) **and** Obsidian chronology with:
- `skill_id`, `from_version`, `to_version`, `semver_level`, `trigger_source`
- G1–G4 run_ids + outcomes; golden-set run_id + pass/safety rates
- Canary rollout metrics; any rollback event with cause + timing
- Approver identity (agent/human) and approval source (digest/sync/automated-patch)

---

## 5. Skill Access Policy (Security)

### 5.1 Allowlist + denylist, per agent

Hardcoded in system-prompt, enforced via PreToolUse hook in SDK [FACT, Agent SDK docs]:

- **Allowlist** = exhaustive list of `(skill_id, version-range)` the agent may invoke.
- **Denylist** = exhaustive list of `(skill_id, op-scope)` the agent must refuse even if theoretically allowed elsewhere.
- **PreToolUse hook** intercepts every tool/skill invocation, cross-checks manifest, blocks + audit-logs any violation.

### 5.2 Sensitive-skill policy

| Skill | Rule | Escalation |
|---|---|---|
| `skill-creator` | ONLY Skill-Updater agent; Red tier | Always sync human approval except patch-level updates where pre-authorized |
| `mcp-builder` | Skill-Updater + Dev only; **Red** | Always sync approval |
| `apify-api` | Budget-capped; Amber if run projected > client budget / 10 | PM budget-guard hook |
| `hunter-io` | Amber if outside pre-approved domain list | Link-Builder→Reviewer→PM chain |
| `notion-orchestration` | Amber on writes; Red on Projects Registry delete (blocked by denylist) | PM sync for any cross-workspace or membership change |
| `data:sql-queries` | Green read-only; Amber on DDL/DML to prod | Analytics→Dev review |
| `deploy-checklist` + `webapp-testing` | Amber by default (touches prod surface) | Dev+QA sign-off |
| `forecast` | Amber (budget-impact decisions) | Strategist approval |

### 5.3 Budget & rate-limit guards

Client budgets registered in Notion `Projects Registry.budget_caps`. PM-agent watcher subscribes to `data_source.*` webhooks (Notion 2026-03-11 [FACT]); any spike >25% of remaining monthly budget → Amber escalation automatically.

Apify-api uses 4-key rotation fallback (per `apify-api` skill description) to maximize free-tier compute before paid spend.

---

## 6. Skill Composition Patterns

### 6.1 Load order

1. **Preload:** name + description (≤100 words) — always in the agent's system-prompt [FACT].
2. **Trigger:** SKILL.md loaded when Skill tool invoked.
3. **Drill-down:** `references/*.md`, `scripts/*` loaded by Read/Bash only as needed [FACT].

This three-level discipline is Anthropic's canonical progressive disclosure — violating it bloats context window and degrades agent performance.

### 6.2 Common compositions (MAMS-specific)

| Pattern | Skills | Agent(s) | Notes |
|---|---|---|---|
| "Full SEO audit" | `research-via-notebooklm` → `ahrefs-seo` + `semrush-api` → `seo-audit` → `seo-content` → `data:analyze` → `docx` | SEO-AEO-GEO (handoff Analytics, Reviewer) | Serial data collection, parallel metric pulls, serial synthesis |
| "Launch campaign" | `campaign-plan` → `draft-content` + `landing-page-designer` → `humanizer` → `brand-review` → `webapp-testing` → `deploy-checklist` | Strategist → Content + CRO → Reviewer → Dev | Parallelizes content & LP creation, serial review gates |
| "Incident retro + skill patch" | `debug` → `consolidate-memory` → `skill-updater-pipeline` → Registry commit | Dev → Skill-Updater | Dev isolates; Skill-Updater runs G1-G4 |
| "Weekly metrics review" | `data:analyze` → `data:statistical-analysis` → `metrics-review` → `stakeholder-update` → `pptx` | Analytics → PM | Auto-cadence via `schedule` |
| "Compliance check on content" | `brand-review` → `seo-content` (thin-content) → `agent-as-evaluator` (rubric=legal) | Reviewer | If `agent-as-evaluator` flags Red → PM sync approval |

### 6.3 Skill call graph (DAG)

MAMS keeps a per-agent DAG of skill dependencies (resolved at agent boot). Cycles forbidden; patch-level updates cannot introduce new dependencies (would elevate to minor).

---

## 7. Eval Harness

### 7.1 Evaluator registry

`skills.evaluators` table with `(evaluator_id, skill_ids[], test_set_path, judge_model, run_frequency)`:

| Evaluator | Skills covered | Cadence |
|---|---|---|
| `golden-set-seo-v3` | `seo-audit`, `seo-content`, `ahrefs-seo` | Weekly + on-patch |
| `golden-set-content-v2` | `content-creation`, `draft-content`, `humanizer`, `brand-review` | Weekly + on-patch |
| `golden-set-data-v4` | `data:analyze`, `data:statistical-analysis`, `data:validate-data`, `data:sql-queries` | Weekly + on-patch |
| `golden-set-paid-v2` | `campaign-plan`, `performance-report`, `forecast` | Weekly + on-patch |
| `golden-set-dev-v3` | `code-review`, `debug`, `testing-strategy`, `deploy-checklist` | Weekly + on-patch |
| `golden-set-pm-v2` | `sprint-planning`, `stakeholder-update`, `roadmap-update`, `write-spec` | Monthly + on-patch |
| `golden-set-risk-v1` | `risk-tiering` | Monthly + on-patch |
| `golden-set-notion-v2` | `notion-orchestration` | Weekly + on-patch |
| `skill-updater-self-test` | `skill-updater-pipeline` meta | Daily |

### 7.2 Scoring

Pass = exact-match OR semantic-match (LLM-judge w/ rubric) above threshold. Safety = zero violations across adversarial subset.

### 7.3 Dashboards

Built via `data:build-dashboard` skill; hosted as Notion-embedded artifact. Exec summary weekly; full per-skill view on demand.

---

## 8. Onboarding a New Skill (Checklist)

1. **Draft** via `skill-creator`: name + description ≤100 words + SKILL.md + `references/*.md` if needed.
2. **Declare permissions** in manifest — read/write/denied scopes explicit.
3. **Write golden set** — ≥20 cases, ≥10% adversarial.
4. **Run G1-G4** via `skill-updater-pipeline`; must all pass.
5. **Run golden-set eval** — pass ≥0.9, safety =1.0.
6. **Canary** — 5% traffic, min 50 runs, pass ≥0.92.
7. **Promote** to stable; Supabase manifest `status=stable`; Git tag.
8. **Audit** — log to Activity Log (Notion) + Obsidian chronology.
9. **Announce** — digest approval summary to PM for Green/Amber; sync approval for Red.

---

## 9. Known Anti-patterns (Avoid)

Documented from MAMS early rollout retrospectives and corpus literature:

| Anti-pattern | Failure mode | Fix |
|---|---|---|
| Putting full skill body in system-prompt | Context bloat; degraded agent reasoning | Enforce progressive-disclosure pattern [FACT] |
| Skipping G3 for "trivial patch" | Runtime regression; silent tool-contract break | Block merge if G3 unrun |
| Permission-manifest drift (G4) | Skill calls new MCP; governance blind | Permission diff blocks merge |
| Golden-set pass-rate drift unnoticed | Skill decays over core updates (e.g., March 2026) | Weekly scheduled eval + alert |
| Skill-creator used by wrong agent | Unauthorized capability creation | Red-tier gate + PreToolUse block |
| Sync approver = owner agent | Self-approval (governance theater) | RACI requires external approver |
| Canary traffic too low | Insufficient signal → false positive promotion | Min-run threshold enforced |
| Retirement w/o migration | Call-site breakage | 30-day deprecate window + auto-wrapper generation |

---

## 10. Change Log (v1.0 → v2.0)

- Added executive-decisions §0 and progressive-disclosure enforcement note.
- Expanded skill registry schema with G1-G4 gate_results and canary fields.
- Added `data:data-context-extractor` and `obsidian-connector:obsidian-notes` to catalog.
- Added `agent-as-evaluator` MAMS-custom skill (mirrors subagent-judge pattern).
- Added full Trust Gate mechanics table (§4.2).
- Added skill composition patterns §6 with concrete DAGs.
- Added evaluator registry §7 with cadence table.
- Added onboarding checklist §8 and anti-patterns §9.
- Switched permission tiering to Green/Amber/Red default with explicit escalation paths.
- Aligned `notion-orchestration` with 2026-03-11 API capabilities (position, in_trash, data_source webhooks, 5-min aggregation).

---

**End of Skill Inventory v2.0.**
