# MAMS Research — Scope Document v1.0

**Project code:** [MAMS] — Multi-Agent Marketing System
**Author:** Claude (Cowork) under direction of Alex
**Date:** 2026-04-20
**Skill:** `research-via-notebooklm` v2.6
**Status:** LOCKED — all 8 methodological decisions pre-approved by user in prior session

---

## 0. Methodological Decisions (LOCKED)

| # | Decision | Value |
|---|---|---|
| 1 | Scenario | **B (Deep-Academic) + C (Market) hybrid** |
| 2 | Corpus target | 140 sources, no hard cap (may exceed if quality holds) |
| 3 | NotebookLM notebook | Create new: `MAMS_Research_2026-04` |
| 4 | Apify budget | Unlimited (fallback for bulk / paywall only; egress fixed → WebSearch+WebFetch primary) |
| 5 | Publisher caps | Anthropic ≤ 35%, Google ≤ 35%, default 25%, Substacks (sum) ≤ 15% |
| 6 | [FOUNDATIONAL] exception | Academic papers older than cutoff 2025-10-01 allowed up to 15% of corpus, tagged `[FOUNDATIONAL]` |
| 7 | Deliverables order | Architecture Report → Agent Specs → Skill Inventory → Sample E2E → Notion Template |
| 8 | Human checkpoints | Stage 1 (auto-approve if Scope matches these decisions), **Stage 5 (Architecture draft — hard stop)**, Stage 7 (Final). Stage 3 ranked-list approval SKIPPED. |

**Gate-0 (connectivity):** PASS on 2026-04-20 — all 5 probe domains reachable via WebFetch (developers.google.com, arxiv.org, searchengineland.com, ahrefs.com/blog, kevin-indig.com). Route = WebSearch + WebFetch primary; Apify fallback only.

---

## 1. Research Goal (Restated)

Design a universal multi-agent AI team, under a PM-Agent ("Интернет-маркетолог"), capable of running **any** full-cycle internet-marketing project: web dev, SEO (organic + AI-search), content, SMM, PPC, CRO/UX, link-building, and analytics-driven iteration. The system must (a) connect to live analytics APIs (GA4, GSC, Ahrefs, Meta Ads, Google Ads), (b) act on real data not assumptions, (c) self-improve via a dedicated Meta-Agent (Skill-Updater) that scans the market and patches peer agents' skills, and (d) operate through Notion as the orchestration layer with a Kanban/sprint workflow.

**Human-budget model:** front-loaded. Strategy phase = human-active (2–5 h/week). Execution phase = human-passive (30–60 min/week digest approvals). Escalation triggers: budget > threshold, new access/resource, or Red-tier risk events.

---

## 2. Scenario & Temporal Window

- **Scenario:** B (Deep-Academic) + C (Market) hybrid — per S0 skill taxonomy. Justification: topic spans foundational multi-agent orchestration research AND rapidly shifting SEO/AEO/GEO/Ads market in 2026.
- **Hard cutoff:** `published_at >= 2025-10-01`
- **Soft exception:** `[FOUNDATIONAL]` tag for pre-cutoff academic papers, ≤ 15% of final corpus
- **Retractions:** strict exclusion per M3-protocol (cross-check arxiv withdrawal notices, publisher retraction lists)
- **Language policy:** corpus EN-only; deliverables RU; citation tags `[FACT]`/`[EXPERT-CLAIM]`/`[CONTESTED]` EN; URLs/author names/titles original EN; technical terms (agent, skill, AEO, GEO, INP, RACI) EN inline

---

## 3. Sub-Questions — 9 Blocks × 28 Items

### Block A — Multi-Agent Architecture (4)
- **A1.** Production-ready orchestration patterns for an LLM PM with specialist subordinates? (hierarchical, swarm, blackboard, actor-model, graph-based)
- **A2.** Claude Agent SDK vs LangGraph vs CrewAI vs AutoGen vs Semantic Kernel — which for a 10–12-agent team with human-in-the-loop?
- **A3.** Delegation protocol: when PM delegates to a specialist, when executes itself, when runs parallel specialists, how it consolidates output.
- **A4.** Context/state management: shared memory, handoff summaries, persistent KB — how to pass state without context bloat.

### Block B — SEO 2026 (Organic + AI-Search) (4)
- **B1.** Ranking factors 2026: critical shifts vs 2024. (AI Overviews, E-E-A-T, helpful content v3+, site reputation abuse)
- **B2.** GEO/AEO: how to optimize for ChatGPT / Perplexity / Claude / Gemini citations. What's measured vs hype.
- **B3.** Technical SEO 2026: Core Web Vitals v3, INP, Schema updates, AI-crawler budget, `llm.txt` / `robots.txt` for AI agents.
- **B4.** Content strategy for AI citations: topic clusters vs entity-based vs AEO format; length and structure.

### Block C — Dev, CRO, UX (3)
- **C1.** Build-or-renovate diagnostic framework 2026: when legacy improvement beats rebuild; decision matrix and signals.
- **C2.** CRO frontiers 2026: personalization, adaptive layouts, AI-driven A/B, behavioral triggers, predictive UX.
- **C3.** UX/UI patterns simultaneously boosting CR and SEO (non-conflicting).

### Block D — Dynamic Niche Expertise (3)
- **D1.** Fast (1–2-session) KB build for arbitrary client niche; Niche-Expert agent onboarding workflow.
- **D2.** RAG vs fine-tune vs structured ontology vs hybrid — optimal for niche-switching agent.
- **D3.** Expert-in-the-loop: quality gates, approval flows, fact-check for domain-specific content.

### Block E — Human-in-the-Loop Governance (Front-Loaded) (3)
- **E1.** Risk-tier frameworks for marketing decisions: autonomous / approval / always-Red.
- **E2.** Human-burden minimization: batch approvals, digest notifications, async checkpoints, time-boxed auto-approve.
- **E3.** Strategy-phase vs execution-phase governance: how autonomy ramps.

### Block F — Self-Improving Systems (Meta-Agent / Skill-Updater) (4)
- **F1.** Continuous market-intel agent: scanning SEL/SEJ/Moz/Ahrefs/arXiv/Anthropic/Google releases without false positives / signal fatigue.
- **F2.** Skill-update protocol: news → skill patch pipeline; validation, A/B, rollback.
- **F3.** Meta-learning: retrospective analysis, post-mortem → skill-patch pipelines.
- **F4.** Versioning & change management for live skill registry — rolling updates without breaking active projects.

### Block G — SMM + PPC (3)
- **G1.** SMM 2026: TikTok / IG / LinkedIn / X algorithm changes; AI-content policies; organic vs paid mix; posting cadence.
- **G2.** PPC 2026: Google Ads PMax, Meta Advantage+, automated bidding, Conversions API, privacy-first attribution.
- **G3.** Cross-channel orchestration: SEO + SMM + PPC coordination without duplication or budget cannibalization.

### Block H — Analytics Integration (3)
- **H1.** Critical metrics per task type (SEO/SMM/PPC/CRO) and 2026 APIs (GA4, GSC, Ahrefs, Semrush, Meta Graph, Google Ads, Mixpanel, PostHog, Amplitude).
- **H2.** Attribution 2026: consent-mode v2, server-side tagging, ML attribution; interpreting data with signal loss.
- **H3.** Anomaly detection & alert design: separating noise from signal; no alert spam.

### Block I — Notion-as-Orchestration-Layer (3)
- **I1.** Notion best-practices for AI-team PM 2026: DB structure, Kanban flows, sprint templates, metrics dashboards.
- **I2.** Notion API capabilities for AI agents: autonomous vs limited actions.
- **I3.** Linking Notion tasks to external execution (code deploys, content publishes, ad launches) via MCPs / webhooks.

**Total:** 28 sub-questions.

---

## 4. Probe Queries — 84 (3 per sub-question)

> Types: **D** = direct, **C** = comparative, **S** = scenario.

### A — Architecture
- **A1-D.** "Production-grade orchestration patterns for multi-agent LLM systems 2026"
- **A1-C.** "Hierarchical vs swarm vs blackboard vs graph — trade-offs for 10-agent marketing team"
- **A1-S.** "PM-Agent delegates SEO audit to specialist while running parallel content brief — which topology minimizes lock contention?"
- **A2-D.** "Claude Agent SDK feature matrix 2026 subagents tools skills MCP"
- **A2-C.** "Claude Agent SDK vs LangGraph vs CrewAI vs AutoGen vs Semantic Kernel 2026 benchmark"
- **A2-S.** "Framework choice for 12-agent team with async human-in-the-loop approvals and persistent Notion state"
- **A3-D.** "LLM agent delegation protocols patterns 2025 2026"
- **A3-C.** "Consensus vs majority vote vs supervisor reconciliation for parallel agent outputs"
- **A3-S.** "PM receives conflicting SEO audit and CRO recommendation for same page — arbitration protocol"
- **A4-D.** "Agent context state management shared memory handoff summaries 2026"
- **A4-C.** "Full-context sharing vs summarized handoff vs external KB lookup — token cost and fidelity"
- **A4-S.** "Week-3 sprint, PM must brief new Niche-Expert on 20 prior decisions without blowing context window"

### B — SEO 2026
- **B1-D.** "Google ranking factors changes 2025 2026 core updates AI Overviews"
- **B1-C.** "E-E-A-T 2024 vs 2026 — signal weighting shifts"
- **B1-S.** "Site hit by March 2026 core update — diagnostic protocol"
- **B2-D.** "AEO GEO optimization ChatGPT Perplexity Gemini citations 2026"
- **B2-C.** "Content strategies measured to increase LLM citations vs unverified tactics"
- **B2-S.** "B2B SaaS page wants ChatGPT citation — what to change this quarter"
- **B3-D.** "Core Web Vitals 2026 INP thresholds Schema.org updates llm.txt standard"
- **B3-C.** "robots.txt AI-bot directives vs llm.txt vs agents.txt emerging standards"
- **B3-S.** "Site with 50k URLs — AI-crawler budget allocation strategy"
- **B4-D.** "Content structure for AI citation 2026 entity-based topic clusters AEO"
- **B4-C.** "Long-form pillar vs answer-first short-form — which ranks better in AIOs"
- **B4-S.** "Client with thin content library — 90-day AEO-first content plan"

### C — Dev / CRO / UX
- **C1-D.** "When to rebuild vs renovate legacy website 2026 decision framework"
- **C1-C.** "Headless migration vs CMS upgrade vs full rebuild — ROI and risk"
- **C1-S.** "Client WordPress site with 40k pages and tech debt — rebuild decision rubric"
- **C2-D.** "CRO 2026 personalization AI A/B testing adaptive layouts"
- **C2-C.** "Rule-based vs ML-driven personalization — lift and complexity"
- **C2-S.** "E-commerce PDP — which 3 CRO tests to prioritize this sprint"
- **C3-D.** "UX patterns that improve both conversion rate and SEO 2026"
- **C3-C.** "Sticky CTA vs inline CTA — CR vs SEO trade-off"
- **C3-S.** "Landing page fails CWV — redesign that keeps conversion lift"

### D — Niche Expertise
- **D1-D.** "Rapid domain knowledge base build for new client niche AI agent onboarding"
- **D1-C.** "Top-down ontology vs bottom-up document ingestion for niche KB"
- **D1-S.** "Onboard Niche-Expert for dental practice client in 2 sessions — checklist"
- **D2-D.** "RAG vs fine-tune vs structured ontology vs hybrid for domain-switching LLM agent"
- **D2-C.** "Cost / latency / accuracy comparison across KB architectures 2026"
- **D2-S.** "Agent must switch from legal to SaaS niche mid-quarter — architecture choice"
- **D3-D.** "Expert-in-the-loop quality gates domain specific content fact-check"
- **D3-C.** "Pre-publish gate vs post-publish audit — cost and defect rate"
- **D3-S.** "Medical niche — mandatory human gates before publishing any article"

### E — Governance
- **E1-D.** "Risk tier framework AI agent decisions marketing 2026"
- **E1-C.** "Budget threshold autonomy vs capability-based autonomy"
- **E1-S.** "Agent wants to reallocate $5k from Google Ads to Meta — approval path"
- **E2-D.** "Batch approvals digest async checkpoint patterns AI human-in-the-loop"
- **E2-C.** "Time-boxed auto-approve vs manual gate — approval latency vs risk"
- **E2-S.** "Friday digest format for a 5-project portfolio — content and threshold"
- **E3-D.** "Strategy vs execution phase governance autonomy ramp AI team"
- **E3-C.** "Quarterly strategy review cadence vs continuous adaptation"
- **E3-S.** "Quarterly review triggers — when does strategy-phase re-engage mid-execution"

### F — Self-Improving
- **F1-D.** "Continuous market intelligence agent SEO news scanning false positive reduction"
- **F1-C.** "Keyword-triggered vs semantic relevance filter for market-intel scanner"
- **F1-S.** "Scanner encounters 'new Google leak' rumor — verification and signal protocol"
- **F2-D.** "Skill update protocol LLM agent news-to-patch pipeline 2026"
- **F2-C.** "A/B vs shadow deployment for skill patches in production agent team"
- **F2-S.** "New AI-search directive discovered — propagate to SEO agent without breaking current projects"
- **F3-D.** "Meta-learning agent retrospective post-mortem to skill patch"
- **F3-C.** "Self-critique loop vs peer-critique vs human-critique for skill evolution"
- **F3-S.** "SEO agent missed an issue on last audit — post-mortem to durable skill fix"
- **F4-D.** "Skill registry versioning rollout rollback AI agent system"
- **F4-C.** "Semver vs calver vs changelog-only for skill versioning"
- **F4-S.** "Active client project on skill v1.3 while v1.4 rolls out — compatibility guarantee"

### G — SMM + PPC
- **G1-D.** "TikTok Instagram LinkedIn X algorithm changes 2026 AI-content policy"
- **G1-C.** "Organic vs paid mix benchmarks by platform 2026"
- **G1-S.** "B2C DTC brand launching on TikTok + IG — 30-day posting cadence and format"
- **G2-D.** "Google Ads Performance Max Meta Advantage+ updates 2026 privacy-first attribution"
- **G2-C.** "Automated bidding vs manual bidding on low-volume niche 2026"
- **G2-S.** "Signal-loss post iOS 18 — Conversions API + server-side tagging migration"
- **G3-D.** "Cross-channel SEO SMM PPC coordination budget cannibalization 2026"
- **G3-C.** "Funnel-stage allocation vs last-click vs incremental-lift orchestration"
- **G3-S.** "Brand launch — SEO foundation + PPC bursts + SMM content calendar — sequencing"

### H — Analytics
- **H1-D.** "Critical SEO SMM PPC CRO metrics 2026 API sources GA4 GSC Ahrefs Meta"
- **H1-C.** "Mixpanel vs PostHog vs Amplitude product analytics 2026 AI agent integration"
- **H1-S.** "Minimal metric set for weekly digest across 4 channels"
- **H2-D.** "Attribution consent-mode v2 server-side tagging ML attribution 2026"
- **H2-C.** "Data-driven attribution vs MMM vs incrementality tests"
- **H2-S.** "EU client, strict consent regime — attribution stack design"
- **H3-D.** "Marketing analytics anomaly detection alert design 2026"
- **H3-C.** "Threshold alerts vs statistical (z-score / seasonal) vs ML anomaly"
- **H3-S.** "Traffic -40% overnight — triage protocol for Analytics-Agent"

### I — Notion Orchestration
- **I1-D.** "Notion AI team project management databases templates 2026"
- **I1-C.** "Single-DB task tracker vs multi-DB (Projects / Sprints / Tasks / Metrics) architecture"
- **I1-S.** "Set up Notion workspace for 5-project marketing portfolio with Kanban + metrics dashboard"
- **I2-D.** "Notion API 2026 capabilities limits AI agent integration"
- **I2-C.** "Notion native API vs MCP connector for agent writes"
- **I2-S.** "Agent needs to bulk-update 200 tasks after sprint close — rate-limit-safe pattern"
- **I3-D.** "Notion integrations external execution code deploy content publish ad launch webhooks MCP"
- **I3-C.** "Zapier vs Make vs native webhooks vs custom MCP — reliability and audit trail"
- **I3-S.** "Content-Writer agent marks task Done — trigger publish to CMS + announce to Slack"

**Total:** 84 probes.

---

## 5. Whitelist — Sources & Publisher Caps (LOCKED)

### Tier-S Primary Platform
- **Anthropic** (cap 35%): docs.anthropic.com (Agent SDK, Subagents, Skills, Claude Code, MCP, Memory), anthropic.com/news, anthropic.com/research
- **Google** (cap 35%): developers.google.com/search, developers.google.com/analytics, developers.google.com/google-ads, search.google.com (GSC), google.com/search/howsearchworks, web.dev, ai.google.dev (Gemini), schema.org (Google-hosted)
- **OpenAI** (cap 20% as part of non-Anthropic/Google bucket): openai.com/docs, platform.openai.com/docs (Assistants, Swarm, Agents SDK), openai.com/blog
- **Meta/Facebook** (cap 20%): developers.facebook.com (Graph API, Ads API, Conversions API)
- **Notion** (cap 10%): developers.notion.com, notion.so/blog
- **Ahrefs** (standalone, cap 25%): ahrefs.com/blog, ahrefs.com/api
- **Semrush/Backlinko** (one group, cap 25%): semrush.com, backlinko.com, semrush.com/api
- **Moz** (standalone, cap 25%): moz.com/blog, moz.com/learn

### Tier-S Gov / Standards
- **W3C, IETF, NIST** (cap 10%): w3.org, ietf.org, nist.gov (for llm.txt, agent.txt, AI safety)
- **Regulatory** (cap 10%): eur-lex.europa.eu (EU AI Act, GDPR), oag.ca.gov (CCPA)

### Tier-S Expert Authority (individual voices, all subject to default 25% per-publisher-group)
- **Agent architecture:** Simon Willison (simonwillison.net), Harrison Chase (LangChain blog), Jerry Liu (LlamaIndex blog), Andrew Ng (deeplearning.ai/The Batch), Lilian Weng (lilianweng.github.io), Yohei Nakajima, Dharmesh Shah
- **SEO:** Rand Fishkin (SparkToro), Aleyda Solis (SEOFOMO Substack — Substack bucket), Marie Haynes (mariehaynes.com), Kevin Indig (Growth Memo Substack — Substack bucket), Eli Schwartz (Product-Led SEO Substack — Substack bucket), Glenn Gabe (GSQI), Lily Ray (lilyray.nyc), Cyrus Shepard (zyppy.com)
- **CRO / UX:** Peep Laja (CXL), Baymard Institute (baymard.com), Jakob Nielsen (NN/g)
- **SMM / PPC:** Neil Patel (neilpatel.com), Avinash Kaushik (kaushik.net), Frederick Vallaeys (PPC Hero / Optmyzr)

### Tier-S Academic
- **arXiv** (cap 25%, `[FOUNDATIONAL]` fraction within 15% global): arxiv.org (cs.AI, cs.CL, cs.MA, cs.IR) — 2025-10-01+ primary, older only as `[FOUNDATIONAL]`
- **Venues:** ACL / EMNLP / NeurIPS / ICLR / AAAI proceedings — 2025-2026 preferred
- **Labs:** MIT CSAIL, Stanford HAI, CMU, DeepMind (deepmind.google/research), Anthropic Research

### Tier-S/A Trade Publications (each separate publisher_group, default cap 25%)
- **SEL / SEJ / SER:** searchengineland.com, searchenginejournal.com, seroundtable.com
- **Practitioner blogs:** moz.com/blog, ahrefs.com/blog, semrush.com/blog, backlinko.com
- **Web dev:** smashingmagazine.com, css-tricks.com, web.dev/blog
- **Agent dev:** blog.langchain.dev, openai.com/blog, anthropic.com/news
- **Social / PPC:** socialmediatoday.com, searchenginewatch.com, ppchero.com
- **Notion / Productivity:** notion.so/blog, superhuman.ai, every.to

### Tier-A Practitioner Guides
- Backlinko guides, Ahrefs guides, Moz Learn, Nielsen Norman Group, CXL Institute, Content Marketing Institute, Growth.Design

### Tier-A Discovery (Substacks — cap sum ≤ 15%)
- Kevin Indig — Growth Memo
- Aleyda Solis — SEOFOMO
- Eli Schwartz — Product-Led SEO
- Simon Willison (personal blog, NOT substack — sits in expert-authority bucket)
- Latent Space (Swyx + Alessio)

### Tier-A Video (verified transcripts ONLY)
- Ahrefs YouTube, Semrush YouTube, Google Search Central YouTube, Anthropic talks

### EXCLUDE (hard filter)
- Anonymous / AI-generated Medium posts
- LinkedIn posts without verified expert authorship
- Listicle SEO-spam sites without primary research
- Affiliate-heavy "best X tools" review farms
- Sites with <2024 last-updated dates on cited pages
- Retracted / superseded sources (M3 protocol)

### Publisher-Group Ledger (enforcement)
Tracked in `publisher_ledger.json` during harvest. On insertion check:
```
if group_count / corpus_size > cap: reject candidate, mark "cap-bounced"
```
Anthropic and Google hard caps = 35% each. Substacks-sum ≤ 15%. All other groups default 25% unless noted above.

---

## 6. Data-Need Matrix

> Mapping each sub-question → minimum source types required → acceptance threshold. Used by Stage 4 coverage probes.

| Sub-Q | Primary doc | Expert voice | Academic | Case-study | Min distinct sources |
|---|---|---|---|---|---|
| A1 | docs.anthropic.com (SDK, Subagents), LangGraph docs | Simon Willison, Harrison Chase, Lilian Weng | arXiv cs.MA 2025-2026 | — | 5 |
| A2 | All 5 framework docs | Willison, Ng, Chase | benchmark arXiv | prod war stories | 7 |
| A3 | Agent SDK delegation guide | Weng, Willison | arXiv cs.MA orchestration | — | 4 |
| A4 | Context management docs | Willison, LangChain | arXiv context-compression | — | 4 |
| B1 | developers.google.com/search Essentials, helpful-content | Aleyda, Glenn Gabe, Lily Ray | — | SEL algo-update coverage | 6 |
| B2 | — | Kevin Indig, Aleyda, Rand Fishkin | AEO / LLM-citation research 2025-2026 | Ahrefs "ChatGPT citations" study | 6 |
| B3 | web.dev CWV, Schema.org, Google crawler docs | Cyrus Shepard, Glenn Gabe | — | — | 5 |
| B4 | Search Central content guidance | Eli Schwartz, Aleyda | entity-based SEO research | case studies | 5 |
| C1 | — | Peep Laja, Baymard | — | rebuild case studies | 4 |
| C2 | — | CXL, Baymard, NN/g | CRO research 2025-2026 | — | 4 |
| C3 | web.dev UX | NN/g, Baymard | — | — | 4 |
| D1 | — | Willison, Jerry Liu | RAG onboarding research | — | 4 |
| D2 | — | Jerry Liu (LlamaIndex), Andrew Ng | RAG vs fine-tune arXiv 2025-2026 | — | 5 |
| D3 | — | — | human-in-the-loop QA research | medical-legal case studies | 4 |
| E1 | Anthropic safety guidance | — | AI-governance research | — | 4 |
| E2 | Anthropic human-in-the-loop docs | Dharmesh Shah | — | ops playbooks | 4 |
| E3 | — | Andrew Ng, Ethan Mollick | — | — | 3 |
| F1 | — | Simon Willison (news-filtering), Latent Space | market-intel research | — | 4 |
| F2 | MCP docs, skill-versioning guides | Willison | continual-learning research | — | 4 |
| F3 | — | Weng, Dharmesh Shah | self-improvement arXiv 2025-2026 | — | 4 |
| F4 | Anthropic Skills versioning | LangChain skill registry | — | — | 3 |
| G1 | Platform developer docs (IG/TikTok/LinkedIn/X) | Neil Patel, Avinash Kaushik | — | SMT case studies | 5 |
| G2 | developers.google.com/google-ads, developers.facebook.com | Frederick Vallaeys | — | PPC Hero case studies | 5 |
| G3 | — | Avinash Kaushik | cross-channel attribution research | — | 4 |
| H1 | All analytics-platform docs | Kaushik | — | — | 6 |
| H2 | Google consent-mode v2 docs, server-side tagging | Simo Ahava (analytics expert), Kaushik | — | — | 4 |
| H3 | — | — | anomaly-detection research | ops blogs | 3 |
| I1 | developers.notion.com | Notion blog, every.to | — | case studies | 4 |
| I2 | Notion API docs + changelog | — | — | rate-limit blog posts | 3 |
| I3 | MCP docs, Notion webhooks | — | — | integration playbooks | 4 |

**Minimum aggregate coverage:** 120 sources after dedup (cutoff allowances within 15%). Reserve pool: 40 sources on standby for gap-fill.

---

## 7. Deliverables — Final Form (LOCKED)

All five files saved to `/sessions/affectionate-optimistic-faraday/mnt/outputs/`. RU language, EN citation tags, EN technical terms.

1. **`MAMS_Architecture_Report.md`** + **`.docx`** — 18 sections (see §9 below)
2. **`MAMS_Agent_Specs.md`** — 12 agents: PM-Agent, Strategy-Agent, SEO-Specialist, Content-Writer, SMM-Specialist, PPC-Specialist, Niche-Expert, Designer, Developer, QA/Tester, Analytics-Agent, Skill-Updater. Each: role / inputs / outputs / tools / required skills / MCPs / delegation patterns / escalation rules.
3. **`MAMS_Skill_Inventory.md`** — table: existing skills in user repo mapped to agents; missing skills with P0/P1/P2; skills requiring user input (access / prefs / custom); dependency graph.
4. **`MAMS_Sample_E2E_Scenario.md`** — universal end-to-end walkthrough from client-intake → Q2 results, showing every handoff / human checkpoint / Activity-Log entry.
5. **`MAMS_Notion_Template.md`** — DB structure (Projects / Tasks / Sprints / Metrics / Skills Registry / Market Intelligence / Decisions Log), relations, views (Kanban / Sprint / Metrics Dashboard / Risk Dashboard), automations (formulas + integrations).

---

## 8. Build Order (LOCKED per Decision #7)

1. Architecture Report (anchors all design decisions)
2. Agent Specs (references Architecture §12 + §13)
3. Skill Inventory (derives from Agent Specs inputs/tools/skills)
4. Sample E2E Scenario (uses agent roster + skills to run a narrative)
5. Notion Template (encodes the orchestration described in 1–4)

---

## 9. Architecture Report — 18-Section Structure

| § | Section | Source block(s) |
|---|---|---|
| 1 | Executive Summary (1 page) | cross-cut |
| 2 | Проблема, цели, границы системы | brief + A |
| 3 | Обзор архитектурных паттернов | A |
| 4 | SEO 2026 state-of-the-art | B |
| 5 | Dev / CRO / UX требования | C |
| 6 | Dynamic niche onboarding | D |
| 7 | Human-in-the-Loop governance (front-loaded) | E |
| 8 | Self-Improving Systems — Skill-Updater design | F |
| 9 | SMM + PPC orchestration | G |
| 10 | Analytics Integration layer | H |
| 11 | Notion-as-Orchestration | I |
| 12 | **Рекомендуемая архитектура команды** (финал-дизайн) | A + E + F synthesis |
| 13 | Responsibility Matrix (RACI) для всех агентов | §12 derivative |
| 14 | Delegation / Handoff Protocols | A3 + A4 |
| 15 | Human Checkpoints Catalog | E |
| 16 | Risk Assessment (incl. Red-tier catalog) | E1 |
| 17 | Implementation Roadmap (phases + milestones) | cross-cut |
| 18 | Bibliography (L2 tier-structured template) | all |

---

## 10. Workflow — 9 Stages & Gates

| Stage | Name | Gate | Human approval |
|---|---|---|---|
| 0 | Connectivity pre-flight | Gate-0 egress PASS | n/a |
| 1 | Scope v1.0 (this doc) | Gate-1 matches 8 locked decisions | AUTO (pre-approved) |
| 2 | Source shortlist (candidate pool to ~400) | — | — |
| 3 | Ranked list + SIFT + retraction filter | Gate-3 SIFT/M3 pass | **SKIP** per Decision #8 |
| 4 | Harvest + NotebookLM load + coverage probes | Gate-4 coverage ≥ Data-Need Matrix | — |
| 5 | Architecture synthesis draft (§12 + Agent Specs §2) | Gate-5 internal-consistency pass | **HARD STOP — user review** |
| 6 | Full synthesis (remaining sections 1–11, 13–18) | — | — |
| 7 | Final 5 deliverables | Gate-7 citation audit + consistency | **FINAL user approval** |
| 8 | Post-delivery hand-off (out of research scope) | — | — |
| 9 | Verification / audit archive | Gate-9 retention | — |

---

## 11. Logging Rules (binding for every significant action)

**Notion Activity Log** (DB `a8f3ad98-9a8f-4809-996d-cf5441cd5f6a`, data source `ac08f18a-1fe4-4acf-a598-06a594f1f9b0`):
- Entry (short what-was-done)
- Date (today)
- Project = "MAMS — Multi-Agent Marketing System"
- Who = "Claude"
- Source = "Cowork"
- Category (Task Done / Task Created / Task Updated / Decision / Communication / Blocker / Note)
- Details
- Related Task

Trigger points: Gate-0, Gate-1, Gate-3 (attempted → Skipped), Gate-4, Gate-5, Gate-7, Gate-9.

**Obsidian chronology** — via Chrome MCP `https://127.0.0.1:27124`, append to `MAMS/_Chronology MAMS.md` with `## 2026-MM-DD (Alex via Claude)` header per entry. Use `[[wikilinks]]` to People/Meetings/Processes notes where applicable. If Obsidian unavailable → warn Alex, continue Notion-only.

---

## 12. Acceptance Criteria

- **Scope doc** must reproduce all 8 locked decisions verbatim, 28 sub-questions, 84 probes, whitelist with caps, Data-Need Matrix, deliverables list, 18-section structure.
- **Scope is self-approved** if contents match the 8 decisions — per Decision #8. User reviews only if inconsistency is visible.

---

**END OF SCOPE v1.0.**
