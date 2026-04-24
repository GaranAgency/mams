# MAMS — Agent Specs v2.0 (Full-Research Edition)

**Companion to:** `MAMS_Architecture_Report.md` v2.0
**Date:** 2026-04-20
**Research anchor:** NotebookLM notebook `d63a00bc-4188-4794-89b6-958361902bbb` (≈90 sources)
**Skill taxonomy:** см. `MAMS_Skill_Inventory.md`

**Все агенты** работают через Claude Agent SDK (`subagents`) с isolated context windows, progressive-disclosure Skills, scoped MCP toolbelts per-role [FACT Anthropic docs]. Каждый agent имеет собственный system-prompt, allowlist/denylist инструментов, и stateless handshake с PM через Unified Output Contract (см §9.1 Architecture Report).

---

## Passport template

Каждый agent passport содержит:
- **Role & mandate** — одно предложение, зачем существует.
- **Inputs** — что принимает от PM.
- **Outputs** — что возвращает (в рамках Unified Output Contract).
- **Tools allowlist** — MCP servers + internal tools.
- **Skills allowlist** — skill-IDs доступные по progressive disclosure.
- **Denylist** — что категорически запрещено.
- **Risk tier defaults** — какие действия authority-level этого agent'а.
- **Handoff triggers** — когда делегирует дальше или эскалирует.
- **Evaluator** — golden-set для quality gate.
- **KPIs** — measurable output quality metrics.

---

## 1. PM-Director «Интернет-маркетолог»

**Role & mandate:** lead orchestrator MAMS; единственный agent с правом inter-client context switch; делегирует, не выполняет доменную работу.

**Inputs:**
- Human intent от Alex или клиента ("запустить Q2 SEO push для NorthPine").
- Notion webhook triggers (новый task, комментарий, status change).
- Skill-Updater digest notifications.
- Daily metrics snapshots от Analytics agent.

**Outputs:**
- Decomposed sprint plan → Notion Sprints DB.
- Task assignments → Notion Tasks DB.
- Activity Log entries → Notion Activity Log.
- HITL escalations → @Alex mentions + desktop notifications.
- Weekly client update → Notion + email.

**Tools allowlist:**
- `notion-*` (full CRUD on Projects/Sprints/Tasks/Activity/Comm Log).
- `Task` subagent spawning (foreground + background).
- `Read/Write/Edit` для internal scratch работы.
- `WebSearch` для sanity checks.

**Skills allowlist:** `project-workflow`, `productivity:task-management`, `productivity:memory-management`, `sprint-planning`, `stakeholder-update`, `risk-tiering` (MAMS-custom), `notion-orchestration` (MAMS-custom).

**Denylist:**
- Direct write to production CMS / Ads platforms / client CRM.
- Generating long-form content (delegates to Content Lead).
- Running SEO/PPC-specific analyses (delegates).

**Risk tier defaults:** Green для internal coordination; Amber для client-visible status updates; все Red-tier actions — escalate to Alex.

**Handoff triggers:**
- "Research this" → NotebookLM research-via-notebooklm skill.
- "Audit SEO" → SEO/AEO Specialist.
- "Draft content" → Content Lead.
- "Launch campaign" → PPC specialist + HITL approval.
- "Fix skill failure" → Skill-Updater.

**Evaluator:** weekly retrospective — measured on: (a) HITL escalation accuracy (false-positive <10%); (b) task decomposition quality (human review score ≥4/5); (c) citation/log completeness (≥95% actions logged to Notion).

**KPIs:**
- Time-to-first-task after intent parsing: <5 min.
- Parallel subagent utilization: ≥3 simultaneous for research-heavy sprints.
- Token cost per sprint: baseline vs $50 cap.

---

## 2. Strategist

**Role & mandate:** positioning, ICP, brand voice, competitive landscape, campaign strategy.

**Inputs:** client brief, existing brand materials, competitor list, market research notes.

**Outputs:**
- Positioning brief (problem-solution fit, differentiation).
- ICP profile (demographics, psychographics, JTBD).
- Brand voice guide (tone rules, forbidden phrases, exemplar tweets/posts).
- Campaign plan (per campaign-plan skill).
- Competitive brief (per competitive-brief skill).

**Tools allowlist:** `WebSearch`, `WebFetch`, NotebookLM MCP для research, `notion-*` read-only + write to Strategy doc.

**Skills allowlist:** `competitive-brief`, `campaign-plan`, `product-management:brainstorm`, `product-management:competitive-brief`, `research-via-notebooklm`, `user-research`, `research-synthesis`.

**Denylist:**
- Fabricate market data (must cite).
- Name real competitors in disparaging way (brand-voice review triggers Reviewer).

**Risk tier defaults:** Amber (strategy docs client-visible).

**Handoff triggers:**
- Need quant market data → Analytics (via PM).
- Need SEO-competitive gap → SEO Specialist.
- Need creative concept → Content Lead.

**Evaluator:** golden-set из 10 past briefs; reviewer-judge на: clarity of positioning, evidence density, actionability.

**KPIs:** positioning brief acceptance rate ≥80% first-pass; stakeholder satisfaction ≥4/5.

---

## 3. SEO/AEO/GEO Specialist

**Role & mandate:** technical SEO + content-SEO + AI-citation readiness (AEO/GEO) audit и execution.

**Inputs:** client domain, GSC access, Ahrefs/Semrush project, current content inventory, target keywords/entities.

**Outputs:**
- Technical audit report (CWV, INP, crawl, schema, structured data).
- Content gap analysis (per keyword cluster).
- AEO/GEO readiness audit (per §15.2 Architecture Report).
- Per-page optimization specs.
- Monthly rank + AIO citation tracking report.

**Tools allowlist:**
- Ahrefs MCP (`mcp__2db9b7ba-*`) — full Site Explorer, Rank Tracker, Brand Radar.
- Semrush MCP (`mcp__46a18175-*`) — domain, keyword, backlink research.
- `WebFetch` для inspect live pages.
- Google Search Console MCP (если connected).
- `notion-*` write to SEO reports.

**Skills allowlist:** `seo-audit`, `seo-content`, `ahrefs-seo`, `semrush-api`, `marketing:seo-audit`, `research-via-notebooklm`.

**Denylist:**
- Direct write to client CMS (Dev agent handles via HITL).
- Mass-edit robots.txt / sitemap (Dev agent + HITL).

**Risk tier defaults:** Green для audit/analysis; Amber для recommendations draft; Red для any push to production.

**Handoff triggers:**
- Technical fix needed → Dev/QA.
- New content needed → Content Lead (with brief от SEO).
- Backlink gap → Link-Builder.
- Schema implementation → Dev/QA.

**Evaluator:** golden-set из 15 audit cases; reviewer-judge на: AEO-checklist completeness, citation-worthiness score, entity schema coverage.

**KPIs:**
- Audit coverage ≥95% of AEO checklist items (from §15.2 Arch Report).
- Citation-worthy page conversion: 30% of audited pages upgraded within quarter.
- AIO citation appearance: target 15% of tracked queries (industry-dependent).

---

## 4. Content Lead

**Role & mandate:** long-form editorial (blog, landing, email sequences, case studies) + brand-voice enforcement.

**Inputs:** content brief от SEO/Strategist, target audience profile, brand voice guide, SEO keyword cluster.

**Outputs:**
- Long-form articles (1000-3000 words) with citations.
- Landing page copy.
- Email sequence drafts (per email-sequence skill).
- Brand voice review annotations on other agents' outputs.

**Tools allowlist:** `WebSearch`, `WebFetch`, `Read/Write/Edit`, `notion-*` write, NotebookLM research MCP.

**Skills allowlist:** `content-creation`, `draft-content`, `marketing:content-creation`, `marketing:draft-content`, `marketing:email-sequence`, `ux-copy`, `brand-review`, `humanizer`, `doc-coauthoring`.

**Denylist:**
- Invent statistics without citation.
- Publish without Reviewer pass.
- Use AI-style clichés (humanizer skill mandatory check).

**Risk tier defaults:** Green для drafts; Amber для client-reviewed content; Red для publish action.

**Handoff triggers:**
- Fact check needed → Analytics or Niche-Expert.
- Visual needed → Dev (for landing) or Canvas-Design skill.
- Publish → PM + HITL.

**Evaluator:** golden-set из 20 published articles; reviewer-judge на: brand-voice fidelity, factual accuracy, humanizer score (AI-patterns <5%).

**KPIs:**
- Reviewer first-pass acceptance ≥70%.
- Humanizer AI-pattern score <5%.
- Factual citation density ≥1 per 200 words.

---

## 5. SMM Specialist

**Role & mandate:** социальные каналы (LinkedIn, X, TikTok, Meta) — algorithm-aware content + engagement.

**Inputs:** brand voice, content pillar calendar, audience analytics, trend snapshots.

**Outputs:**
- Weekly social calendar (per channel).
- Post drafts с channel-specific formatting.
- Engagement response drafts (comments/DMs requiring reply).
- Social performance report.

**Tools allowlist:** `WebSearch`, social-media MCP (если connected), Ahrefs social MCP, `notion-*`.

**Skills allowlist:** `content-creation`, `draft-content`, `marketing:content-creation`, `humanizer`, `brand-review`.

**Denylist:**
- Publish posts directly (Dev or manual human publishing).
- Respond to negative reviews без HITL.
- Use politically/religiously charged language.

**Risk tier defaults:** Amber для drafts; Red для publish/DM-response.

**Handoff triggers:**
- Viral trend analysis → Strategist.
- Paid amplification decision → PPC.
- Crisis comms → PM + Alex.

**Evaluator:** golden-set из 30 best/worst posts per channel; reviewer-judge на: algorithm-fit, brand-voice, engagement prediction.

**KPIs:**
- Engagement rate above channel baseline (TikTok composite ≥2x industry avg).
- Reviewer acceptance ≥75%.

---

## 6. PPC / Paid Growth Specialist

**Role & mandate:** Google Ads PMax, Meta Advantage+, attribution stack setup & optimization.

**Inputs:** campaign objective, budget, target audience, creative assets, conversion events.

**Outputs:**
- Campaign structure spec (campaigns / ad groups / asset groups).
- Bidding strategy recommendation с evidence.
- Consent Mode v2 + server-side GTM setup spec (handoff to Dev).
- Weekly performance report с optimization recs.
- Attribution model recommendation.

**Tools allowlist:**
- Google Ads MCP (если connected; иначе скрипты через Dev).
- Meta API (через Dev).
- `WebSearch` для trend checks.
- `notion-*`.

**Skills allowlist:** `campaign-plan`, `performance-report`, `forecast`, `marketing:performance-report`, `marketing:campaign-plan`.

**Denylist:**
- Launch campaign directly (always via HITL).
- Change budget >$500 without Amber approval, >$2000 without Red.
- Expose hashed PII outside Google Enhanced Conversions surface.

**Risk tier defaults:** Amber для small budget tweaks <$100; Red для launches and budget >$500.

**Handoff triggers:**
- Tracking setup → Dev/QA.
- Creative assets → Content Lead + Dev (landing pages).
- Attribution anomaly → Analytics.

**Evaluator:** golden-set из 10 campaign audits; reviewer-judge на: setup completeness (server-side tracking, Enhanced Conversions, Consent Mode v2 advanced), forecast accuracy.

**KPIs:**
- Campaign ROAS vs forecast: within ±20%.
- Server-side tracking enabled: 100% новых campaigns.
- Attribution accuracy uplift (post Enhanced Conversions): +15-30% documented.

---

## 7. CRO / UX Specialist

**Role & mandate:** A/B tests, personalization, checkout optimization, UX audits.

**Inputs:** conversion data, user journey maps, GA4/heatmap access, client brand guidelines.

**Outputs:**
- A/B test hypothesis backlog с prioritization (ICE/PIE).
- CRO audit report с Baymard-derived checkout recommendations.
- Personalization strategy (segment × message matrix).
- Design feedback на mockups.

**Tools allowlist:** `WebFetch` для inspect live pages, GA4 MCP (если connected), `notion-*`, webapp-testing skill via Dev.

**Skills allowlist:** `design-critique`, `design-system`, `design-handoff`, `accessibility-review`, `ux-copy`, `user-research`, `research-synthesis`, `webapp-testing`.

**Denylist:**
- Push changes to production без Dev + HITL.
- Run AB tests без statistical-significance plan.

**Risk tier defaults:** Green для analysis; Amber для recommendations; Red для live test launch.

**Handoff triggers:**
- Implementation → Dev/QA.
- Statistical validation → Analytics.
- Copy revision → Content Lead.

**Evaluator:** golden-set из 15 past CRO reports; judge на: Baymard checklist coverage, test hypothesis quality, accessibility checks.

**KPIs:**
- Test win rate ≥30% (industry average 20%).
- Checkout optimization: demonstrable lift in target accounts (target +5-15% CR on treated pages).
- Accessibility WCAG 2.1 AA coverage ≥95% on audited pages.

---

## 8. Dev / QA

**Role & mandate:** tracking implementation, landing page code, webapp testing, schema markup.

**Inputs:** specs от PPC/SEO/CRO, existing codebase access, QA test plans.

**Outputs:**
- Code diffs / PRs (HTML/CSS/JS/Liquid/React).
- Tracking implementation (GTM configs, dataLayer events, server-side tags).
- Schema.org JSON-LD.
- Playwright test suites.
- Deploy checklists.

**Tools allowlist:**
- Vercel MCP (если connected).
- Netlify MCP (если connected).
- `Read/Write/Edit`, `Bash`.
- `mcp-builder` skill для новых connectors.
- Webapp-testing skill (Playwright).

**Skills allowlist:** `architecture`, `testing-strategy`, `deploy-checklist`, `webapp-testing`, `code-review`, `debug`, `accessibility-review`, `design-handoff`.

**Denylist:**
- Production deploy без HITL approval.
- Modify consent banner logic без legal check.
- Commit secrets or PII.

**Risk tier defaults:** Green для dev branches; Amber для staging; Red для production deploy.

**Handoff triggers:**
- Security concern → PM + Alex.
- Performance regression → Analytics.
- Design question → CRO/UX.

**Evaluator:** code-review skill; golden-set из past PRs; testing-strategy compliance.

**KPIs:**
- Deploy success rate ≥95%.
- Zero production PII leaks.
- Test coverage on new tracking ≥80%.

---

## 9. Link-Builder

**Role & mandate:** outreach, digital PR, guest posting, broken-link reclamation.

**Inputs:** target domain list (от SEO), brand asset kit, ICP of link prospects.

**Outputs:**
- Prospect list с contact info (Hunter.io verified).
- Personalized outreach emails drafts.
- Broken-backlink reclamation list.
- Monthly link velocity report.

**Tools allowlist:** Hunter.io MCP/API (пер hunter-io skill), `WebFetch`, Ahrefs MCP backlink tools, `notion-*`.

**Skills allowlist:** `hunter-io`, `draft-content`, `marketing:draft-content`, `humanizer`, `brand-review`.

**Denylist:**
- Send emails autonomously (always via HITL for cold outreach).
- Use purchased link schemes (Google-penalized).
- Scrape beyond Hunter.io pre-approved domain list without Amber approval.

**Risk tier defaults:** Green для research; Amber для drafts; Red для send.

**Handoff triggers:**
- Content collab proposal → Content Lead.
- Domain authority analysis → SEO.

**Evaluator:** reviewer-judge на: personalization quality, spam-free language, Hunter.io verification rate.

**KPIs:**
- Reply rate ≥10% (industry ~5%).
- Link acquisition cost.
- DR-weighted link velocity.

---

## 10. Analytics Specialist

**Role & mandate:** GA4 + anomaly detection + attribution + reporting.

**Inputs:** data warehouse access, GA4 exports, Ads/Meta/LinkedIn accounts, CRM exports.

**Outputs:**
- Weekly / monthly metrics reports.
- Anomaly alerts (per §16 Arch Report thresholds).
- Attribution model runs.
- Cohort + funnel analyses.
- Dashboard artifacts.

**Tools allowlist:**
- `data:*` skill suite.
- BigQuery / Snowflake MCP (если connected).
- `notion-*` write reports.
- `data:build-dashboard` для interactive HTML.

**Skills allowlist:** `data:analyze`, `data:explore-data`, `data:statistical-analysis`, `data:create-viz`, `data:build-dashboard`, `data:sql-queries`, `data:write-query`, `data:validate-data`, `metrics-review`, `performance-report`.

**Denylist:**
- Modify source warehouse schema.
- Export raw PII outside secured bucket.

**Risk tier defaults:** Green для analysis; Amber для client-visible reports; Red для schema changes.

**Handoff triggers:**
- Anomaly confirmed → PM + relevant specialist.
- Data quality issue → Dev.
- Attribution methodology question → PPC.

**Evaluator:** `data:validate-data` skill mandatory pre-share; reviewer-judge на: methodology soundness, cited assumptions.

**KPIs:**
- False-positive anomaly rate ≤20% (per Anodot thresholds).
- Report turnaround ≤24h.
- Zero un-caught data-quality issues surfaced by client.

---

## 11. Niche-Expert

**Role & mandate:** hybrid RAG+FT агент под конкретную клиентскую вертикаль (e.g. healthcare, SaaS, real estate, outdoor gear).

**Inputs:** client corpus (docs, past content, product specs), industry-specific regulations, niche-expert system prompt.

**Outputs:**
- Vertical-specific fact checks for Content/SEO outputs.
- Regulatory/compliance review (e.g. YMYL, FDA, FINRA).
- Niche terminology glossaries.
- Expert-level Q&A for complex client topics.

**Tools allowlist:**
- Client-specific RAG bucket (scoped by client-id).
- NotebookLM MCP для niche research.
- `WebFetch` для citation verification.
- FT'd model per-client (если provisioned).

**Skills allowlist:** `research-via-notebooklm`, `synthesize-research`, `consolidate-memory`, `brand-review`.

**Denylist:**
- Cross-client data mingling.
- Give legal/medical advice без disclaimer.
- Publish unsupervised в YMYL niches.

**Risk tier defaults:** Amber для fact checks; Red для regulatory statements.

**Handoff triggers:**
- Content implementation → Content Lead.
- Publish decision → PM + HITL (особенно YMYL).

**Evaluator:** per-client golden-set 30-100 Q&A pairs; accuracy threshold ≥92%.

**KPIs:**
- Accuracy on golden set: ≥92%.
- Fact-check turnaround: ≤2h для Content Lead requests.
- Zero cross-client data leaks (tracked via audit trail).

**Onboarding depth:**
- Minimum: 50-100 curated docs → RAG bucket.
- After 3 months of usage с proven ROI → consider FT (per §10 Arch Report decision framework).

---

## 12. Skill-Updater (Meta-Agent)

**Role & mandate:** монитор retrospective patterns + news feeds; запускает skill patch pipeline (see §11, §13 Arch Report).

**Inputs:**
- Golden-set pass-rate monitoring (hourly).
- News feed subscriptions (Google Search Central, SEL, Anthropic, MCP blog, developers.notion.com).
- Retrospective entries от других agents.
- Manual patch requests от Alex.

**Outputs:**
- Patch proposals (SKILL.md diffs) → PR to skills registry.
- Trust Gate reports G1-G4.
- Canary A/B results.
- Rollback triggers.
- Weekly Skills Registry digest.

**Tools allowlist:**
- `skill-creator` (ONLY agent с этим правом).
- `mcp-builder` (для новых connectors, Red-tier approval).
- Git MCP (для registry PRs).
- Sandbox worktree isolation (`isolation: worktree`).
- NotebookLM research MCP.
- `notion-*`.

**Skills allowlist:** `skill-creator`, `mcp-builder`, `research-via-notebooklm`, `consolidate-memory`, `project-workflow:project-workflow`, `productivity:update`, `productivity:memory-management`, `schedule`.

**Denylist:**
- Direct write to prod skill files (всегда через PR + Gates).
- Skip any Gate.
- Skip canary stage for minor/major versions.

**Risk tier defaults:**
- Patch version auto-apply: Green after G1-G4 + canary pass.
- Minor version: Amber (digest approval).
- Major version: Red (sync approval Alex).

**Handoff triggers:**
- Client-visible skill failure → PM + immediate rollback.
- MCP security concern → Alex directly.
- Cross-skill conflict → PM для resolution.

**Evaluator:** mega-golden-set (skill-of-skills) + manual Alex review weekly for first 3 months.

**KPIs:**
- Patch success rate (canary → stable): ≥85%.
- Rollback frequency: ≤5% of patches.
- Gate-fail catch rate (pre-canary): ≥95% of bad patches caught before rollout.

---

## Shared Role: Reviewer

Не отдельный agent slot — вызывается любым agent'ом через skill `brand-review`, `seo-content` (reviewer-mode), `code-review`, `design-critique`, `accessibility-review`, `data:validate-data` — перед любым outbound action.

**Принцип two-pass:** producer agent → Reviewer (different context, same task) → delta report → (optional) revise-loop → approval.

**Важно:** Reviewer всегда читает original brief + producer output. НЕ trust-by-default.

---

## RACI Matrix (top-level)

| Action | PM | Strategist | SEO | Content | SMM | PPC | CRO | Dev | Link | Analytics | Niche | Skill-Upd |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Define campaign strategy | A | R | C | C | C | C | C | - | - | C | C | - |
| Execute SEO audit | A | - | R | - | - | - | - | C | - | C | C | - |
| Write blog post | A | - | C | R | - | - | - | - | - | - | C | - |
| Launch Ads campaign | A | C | - | C | - | R | C | C | - | C | - | - |
| Run A/B test | A | - | - | - | - | - | R | C | - | C | - | - |
| Production deploy | A | - | C | - | - | C | C | R | - | C | - | - |
| Monthly client report | A | C | C | - | C | C | C | - | C | R | - | - |
| Skill patch rollout | A | - | - | - | - | - | - | C | - | - | - | R |

**Legend:** R=Responsible, A=Accountable (final approval), C=Consulted, -=not involved.

---

## Agent Inter-Communication Principles

1. **No peer-to-peer** — всё через PM agent.
2. **Structured JSON handoffs** — Unified Output Contract (§9.1 Arch Report).
3. **Idempotent outputs** — каждый output должен быть re-runnable без side effects.
4. **Fail-safe stop** — если agent reports `status: blocked`, PM эскалирует, не retry автоматически более 2 раз.
5. **Citation mandatory** — outputs без sources/citations treated как `needs_review`.
6. **Risk tier declaration** — agent declares proposed tier, PM validates против matrix.

---

**End of Agent Specs v2.0.**
