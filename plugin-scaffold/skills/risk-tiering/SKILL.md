---
name: risk-tiering
description: >
  Classify any proposed agent action into Green / Amber / Red HITL tier before
  execution. Invoked by pm-director (and optionally by any specialist before
  side-effectful steps) to decide whether to auto-proceed, send a digest to Alex,
  or block on synchronous approval. Returns {tier, reasoning, hitl_required,
  triggers_matched}. Full rules: MAMS_Skill_Inventory.md §3.1.
version: 0.1.0
owner: pm-director
status: draft
---

# risk-tiering

Read the proposed action as a JSON object with fields: `intent`, `surface`
(internal-file | notion | obsidian | external-api | prod-cms | ads-platform |
client-comm), `scope` (single-item | batch | site-wide), `reversible`
(yes | partial | no), `money_at_risk_usd` (number or null), `affects_client`
(yes | no), `agent` (caller id).

## Classification rules

Apply the rules **in order**. First match wins.

1. **Red** if any of:
   - `surface in {prod-cms, ads-platform, client-comm}` and `reversible != yes`
   - `money_at_risk_usd >= 100`
   - `scope == site-wide` on any external surface
   - Action touches robots.txt, canonical tags, llm.txt, agents.txt, DNS
   - Bulk delete in Notion (>10 rows) or any deletion from Projects Registry
   - First-time skill patch rollout (Skill-Updater G4 promote)

2. **Amber** if any of (and not Red):
   - `surface in {notion, obsidian}` with `scope == batch` (>5 writes)
   - Content publish with custom brand voice (needs brand-reviewer)
   - Meta/title changes on traffic-sensitive pages
   - Budget shift 10-100 USD
   - Experiment launch (A/B, canary) before golden-set pass
   - Any `affects_client == yes` read action that generates new external
     commitment (proposal, SOW, deadline)

3. **Green** otherwise:
   - Read-only audits, research, internal artifact drafts
   - Notion Activity Log / Tasks create/update in normal cadence
   - Skill dry-run in sandbox
   - Inter-agent handoffs within same project

## Output contract

Return valid JSON:

```json
{
  "tier": "Green|Amber|Red",
  "hitl_required": true|false,
  "hitl_mode": "none|digest|sync",
  "reasoning": "one-sentence why",
  "triggers_matched": ["rule-id-1", "rule-id-2"],
  "recommended_timeout_hours": 0
}
```

- `hitl_mode`: `none` for Green, `digest` for Amber (4h auto-approve per
  Architecture Report §15), `sync` for Red (blocking).
- `recommended_timeout_hours`: 0 Green, 4 Amber, null Red (wait indefinitely).

## Examples

Input: `{intent: "Log weekly KPI summary to Activity Log", surface: "notion", scope: "single-item", reversible: "yes", affects_client: "no"}` → Green.

Input: `{intent: "Update meta titles on 40 blog pages", surface: "prod-cms", scope: "batch", reversible: "partial", affects_client: "yes", money_at_risk_usd: 0}` → Amber (digest, 4h timeout).

Input: `{intent: "Push updated llm.txt live on garan.agency", surface: "prod-cms", scope: "site-wide", reversible: "yes"}` → Red (rule: touches llm.txt).

## Logging

After classification, caller logs one line to Activity Log:
`Category=Note, Details="risk-tiering v0.1 → tier=<X>, reasoning=<Y>, run_id=<uuid>"`.

## Failure modes

- If input malformed: return `tier: Red, hitl_mode: sync, reasoning: "risk-tiering input invalid; defaulting to Red for safety"`.
- If ambiguous (e.g. money_at_risk null and surface external-api): default to Amber.

## Known limitations (v0.1)

- No learning from historical false positives yet (deferred to v0.3 with
  Skill-Updater feedback loop).
- No multi-tenant tier override table (Phase 2: per-client risk profile).
