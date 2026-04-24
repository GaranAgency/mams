# MAMS — Multi-Agent Marketing System
## Architecture Report v2.0 (Full-Research Edition)

**Авторство:** Claude (Opus 4.7) под руководством Alex · Scope: MAMS Stage 5 deliverable #1 of 5
**Дата:** 2026-04-20
**Исследовательская база:** NotebookLM `[MAMS] Multi-Agent Marketing System — Full Research 2026-04` (≈90 источников, 9 тематических блоков A-I)
**Версия:** 2.0 (full redo v1.0 на основе расширенного корпуса NotebookLM + WebSearch 2026)
**Статус:** Draft for human checkpoint (Gate-5)

---

## Таблица содержания

1. Резюме и цели документа
2. Глоссарий и ключевые понятия
3. Методологические рамки и доказательная база
4. Архитектурный выбор: orchestrator-worker + DAG-гибрид
5. Контр-доказательства: когда single-agent выигрывает
6. Stack-выбор: Claude Agent SDK + MCP + Skills
7. PM-Agent «Интернет-маркетолог» — функции и эскалации
8. Команда агентов: обзор 12 ролей
9. Коммуникации, контракты, Shared Heuristics
10. Память, RAG, fine-tune, hybrid для ниш
11. Самообучение агентов и Skill-Updater
12. HITL-governance и tiered approval (Green/Amber/Red)
13. Skill-lifecycle pipeline и Trust Gates
14. Notion как orchestration-слой: возможности и ограничения
15. SEO/AEO/GEO, CRO, PPC — что должна уметь система в 2026
16. Analytics, аномалии, attribution 2026
17. Безопасность, аудит, compliance
18. Риски, open questions, следующие шаги

---

## 1. Резюме и цели документа

MAMS (Multi-Agent Marketing System) — универсальная AI-команда для полного цикла интернет-маркетинга (SEO/AEO/GEO, контент, SMM, PPC, CRO/UX, аналитика, разработка, link-building) под управлением PM-агента «Интернет-маркетолог». Система предназначена для параллельного ведения нескольких клиентов в любых нишах при соблюдении governance, auditability и способности к самообучению.

**Ключевые архитектурные решения v2.0 (обоснование — в соответствующих разделах):**

1. **Иерархический orchestrator-worker с DAG-гибридом** — доказательная база: arXiv 2603.22651 (Pareto-frontier F1=0.921 @ 1.4x cost vs reflexive F1=0.943 @ 2.3x cost) [FACT]; Anthropic multi-agent research system [FACT].
2. **Claude Agent SDK как первичный runtime** — subagents с изолированным context, Skills с трёхуровневым progressive disclosure, MCP для connectivity [FACT] Anthropic 2025-2026 docs.
3. **Skill-Updater мета-агент** — автономный pipeline detect→draft→validate→canary→rollout с 4 Trust Gates и golden-set эвалами, вдохновлённый SICA (arXiv 2504.15228), METAAGENT (2508.00271), ERL (2603.24639), SKILL-RL (2602.08234) [FACT academic].
4. **Tiered HITL governance (Green/Amber/Red)** — с pre-tool interrupts, immutable audit trail, one-click rollback [FACT] strata.io, prefactor.tech, AWS healthcare blog.
5. **Hybrid RAG+FT для niche-expertise** — на основании AWS benchmark (RAG=0.82, FT=0.56, Hybrid=0.86) и agriculture case (FT +6pp, +RAG +5pp, cumulative) [FACT] arXiv 2401.08406, AWS ML blog.
6. **Notion как orchestration-слой с известными ограничениями** — API 2026-03-11, webhooks с out-of-order delivery и aggregation delays до 5 мин, data_source events с 2025-09-03 [FACT] developers.notion.com.
7. **AEO/GEO как first-class подсистема** — chunk-retrieval, answer-synthesis, citation-worthiness, entity schema [FACT] Frase/Jasper + Ahrefs 1.4M prompt study.
8. **Server-side conversion tracking по умолчанию** — Google Tag Gateway +14% conversion signals, Enhanced Conversions +15-30% attribution accuracy [FACT] Google Ads Help.

**Что изменилось vs v1.0:**
Расширена доказательная база (с ~20 до ~90 источников в NotebookLM). Уточнены численные бенчмарки (CRO benchmarks Food & Beverage 6.1%, Beauty 5.1%; AI-assistant conv 4x; мобильный конверсионный разрыв 1.8-2.8% vs 3.2-3.9% desktop; Baymard cart abandon 70.19% = $260B opportunity). Добавлены операционные AEO checklists. Пересобран раздел HITL governance с конкретными time-boxed lanes. Усилен раздел self-improving agents с механикой gating per SICA/METAAGENT/ERL/SKILL-RL.

---

## 2. Глоссарий и ключевые понятия

- **Agent** — LLM-система, автономно планирующая и выполняющая задачи через tool-use, reflection, memory [Weng 2023 foundational].
- **Subagent** — изолированный специализированный агент с собственным context window, custom system prompt, tool-permissions, model [FACT] Anthropic claude-code/sub-agents.
- **Orchestrator-Worker** — паттерн, где lead-agent декомпозирует задачу и делегирует специализированным workers [FACT] Anthropic multi-agent research.
- **Skill** — composable, portable package процедурного знания (SKILL.md + scripts + resources), загружаемый по трёхуровневой progressive disclosure [FACT] Anthropic Skills docs.
- **MCP (Model Context Protocol)** — стандарт connectivity между LLM и внешними системами; AAIF (Agentic AI Foundation) с 2026 управляет стандартом [FACT] Anthropic donation announcement + modelcontextprotocol.io.
- **AEO/GEO** — Answer Engine Optimization / Generative Engine Optimization: стратегия чтобы бренд становился authoritative source для AI tools (ChatGPT, Perplexity, Gemini, Claude, AI Overviews) [FACT] Frase, Jasper.
- **Trust Gate** — валидационный шлюз в lifecycle skill/patch (G1 Static, G2 Semantic, G3 Sandbox, G4 Permission Manifest).
- **Golden Set** — curated dataset 20-100 (input, expected-output, safety-criteria) пар per skill для эваляции.
- **HITL / HOTL** — Human-in-the-Loop (synchronous approval) / Human-on-the-Loop (asynchronous monitoring).
- **Green/Amber/Red tier** — риск-классификация действий; Green = авто, Amber = HOTL, Red = HITL blocking approval.

---

## 3. Методологические рамки и доказательная база

**Research stack:** NotebookLM `[MAMS] Multi-Agent Marketing System — Full Research 2026-04` (ID `d63a00bc-4188-4794-89b6-958361902bbb`) — ≈90 источников, покрывающих 9 тематических блоков:

- A. Multi-agent architecture (Anthropic docs, arXiv, Willison, Weng)
- B. SEO/AEO/GEO 2026 (SEL, SEJ, Ahrefs studies, Kevin Indig, Aleyda, Frase, Jasper)
- C. CRO / AI personalization 2026 (CXL, Baymard, Stormy.ai, WebFX)
- D. RAG vs FT vs hybrid (AWS, arXiv 2401.08406, 2403.01432, 2312.05934, 2504.13425, Glean, InfoQ)
- E. HITL governance (strata.io, prefactor.tech, AWS healthcare, responsibleaifoundation.com, Raconteur)
- F. Self-improving agents (arXiv METAAGENT/SICA/ERL/SKILL-RL, survey 2507.21046)
- G. PPC/SMM 2026 (Google Ads Help, ALM Corp, Criteo, Hootsuite, Summit)
- H. Analytics/anomaly/attribution (Anodot, Adobe, Google Consent Mode v2, Data Manager)
- I. Notion API / MCP (developers.notion.com, MCP blog roadmap, Anthropic MCP donation)

**Citation tags:**
- `[FACT]` — утверждение из authoritative primary source (Anthropic, Google, Notion, arXiv peer-reviewed/technical report) или независимо верифицированный multi-source.
- `[EXPERT-CLAIM]` — утверждение от named эксперта без независимой проверки (Simon Willison, Kevin Indig, Aleyda Solis, Peep Laja и т.д.).
- `[CONTESTED]` — существуют counter-claims в корпусе (например single-agent vs multi-agent при равном thinking budget).
- `[FOUNDATIONAL]` — базовое концептуальное происхождение (Weng 2023 Agent post), допущено в budget 15%.

**SIFT/lateral reading:** публикации с anonymous авторством и listicle-ферм исключены. Ретракций среди выбранных источников не зафиксировано на 2026-04-20.

**Publisher caps (при ≈90 URL):**
- Anthropic ≈12% (cap 35%) — OK
- Google ≈9% (cap 35%) — OK
- MCP Foundation ≈5% — OK
- Ahrefs ≈6% (cap 25%) — OK
- SEL/SEJ ≈5% — OK
- arXiv ≈23% (cap 25%, [FOUNDATIONAL] subset 1%) — OK
- Substack sum (Kevin Indig + Aleyda) ≈4% (cap 15%) — OK
- ALM Corp ≈6% — OK

---

## 4. Архитектурный выбор: orchestrator-worker + DAG-гибрид

### 4.1 Базовый паттерн — иерархический orchestrator-worker

**Обоснование:** arXiv 2603.22651 «Benchmarking Multi-Agent LLM Architectures» даёт следующие числа на задаче извлечения структурных данных из SEC filings [FACT]:

| Architecture | F1 (field-level) | Cost multiplier |
|---|---|---|
| Sequential baseline | 0.83 | 1.0x |
| Hierarchical supervisor-worker | 0.921 | 1.4x |
| Reflexive self-correcting | 0.943 | 2.3x |
| Hybrid (89% of reflexive gains) | ~0.931 | 1.15x |

**Вывод:** hierarchical supervisor-worker занимает наиболее выгодную точку на Pareto frontier. Hybrid-конфигурации могут выдавать 89% от reflexive accuracy при всего 1.15x cost — это нужно учитывать для critical steps (review-loop перед outbound action).

**Anthropic multi-agent research system** описывает тот же паттерн: LeadResearcher анализирует query, пишет strategic plan в memory, параллельно спавнит специализированных subagents, которые возвращают synthesized findings [FACT].

### 4.2 DAG / graph-гибрид для production workflows

Чистая иерархия работает для discrete research queries, но для production-маркетинговых воркфлоу (например, «запустить Q2 campaign») типичный граф — это DAG с fork-join, conditional routing и retry-loops. Для этого MAMS использует гибрид: PM-агент = lead orchestrator, но специфичные под-графы (например SEO→Content→Reviewer→PPC) описаны как explicit DAG в Notion Sprints DB с зависимостями.

### 4.3 Reflexive review loop на critical steps

На Red-tier действиях (publish to production, send email to client list) применяется reflexive pattern: producer-agent → reviewer-agent → (conditional revise-loop) → approval-gate. По данным 2603.22651 это стоит 2.3x tokens, но для high-stakes action оправдано.

### 4.4 Parallel subagents для research/enrichment

В задачах deep research (например AEO-gap analysis клиентской ниши) PM-агент спавнит 3-5 parallel subagents для разных query ветвей, которые работают в изолированных context windows [FACT] Anthropic. Это решает две проблемы: context-bloat lead-agent'а и скорость.

---

## 5. Контр-доказательства: когда single-agent выигрывает

**arXiv 2604.02460 (Single-Agent vs Multi-Agent) [CONTESTED]:** когда «thinking token budget» нормализован, single-agent стабильно догоняет или обходит multi-agent на multi-hop reasoning tasks [FACT arXiv]. Авторы объясняют через Data Processing Inequality: разбивка рассуждения на множество агентов вводит communication-bottlenecks и приводит к информационным потерям.

**Практический вывод для MAMS:** не декомпозировать задачу в multi-agent автоматически. PM-агент применяет следующий эвристический gate:

| Признак задачи | Single-agent | Multi-agent |
|---|---|---|
| Linear reasoning, short context | ✅ | ❌ overkill |
| Context >50% ceiling, noise/misinfo risk | ❌ degradation | ✅ isolation |
| Parallel enrichment possible | ❌ | ✅ |
| Fault isolation нужен (regulated action) | ❌ | ✅ |
| Token budget критичен | ✅ | ❌ 15x higher |
| Structured output enforcement | ❌ | ✅ shorter prompts 50-100 tokens |

---

## 6. Stack-выбор: Claude Agent SDK + MCP + Skills

### 6.1 Claude Agent SDK — первичный runtime

**Почему:**
- **Subagents с изолированным context** — независимые tool-permissions, models, system prompts. Возвращают summary → не засоряют main context [FACT] Anthropic claude-code/sub-agents.
- **Foreground/background execution** — foreground блокирует main thread и прогоняет permission prompts к человеку; background — concurrent с pre-approved permissions [FACT].
- **No recursive spawning** — subagents не могут спавнить subagents (anti-loop guarantee) [FACT].
- **Skills** — динамически подключаемые процедурные знания с трёхуровневым progressive disclosure [FACT] Anthropic Skills engineering post.

### 6.2 Skills — progressive disclosure

Три уровня per Anthropic docs [FACT]:

1. **Metadata (startup):** YAML frontmatter (name + description) пре-загружается в system prompt всех агентов, у которых skill в allowlist.
2. **Instructions (on-demand):** когда агент решает что skill релевантен — читает полный SKILL.md.
3. **Deep context (lazy):** под-директории (scripts, references, examples) подгружаются только при явной навигации.

Это важно для MAMS т.к. позволяет держать SOP-bank на сотни skills без context-bloat.

### 6.3 MCP — стандартизованный connectivity layer

**Разделение ответственности:** Skills = "что делать" (процедура), MCP = "как подключиться" (connector) [FACT] Anthropic engineering.

**MCP 2026 roadmap:** AAIF (Agentic AI Foundation) — Anthropic передал MCP foundation для multi-vendor governance [FACT]. Понимание extensions: MCP-Apps позволяют server-side rendering рекламных surfaces/dashboards на стороне MCP сервера [FACT] blog.modelcontextprotocol.io 2026-01-26 + 2026-03-11.

**MCP per subagent scoping:** subagent конфиг может содержать `mcpServers` поле, чтобы tool descriptions не кушали context у других subagents [FACT].

### 6.4 Memory patterns

Три уровня памяти per Anthropic best practices [FACT]:

1. **In-session** — auto-compaction при приближении к context limit.
2. **Persistent subagent memory (`project` scope)** — `.claude/agent-memory/` сохраняется через сессии, версионируется в git.
3. **External vault** — для очень long-horizon задач: summary-extract в external store (Notion/Obsidian), spawn fresh subagent который делает retrieve.

**Agentic search > semantic search:** Anthropic рекомендует `grep`-based навигацию по filesystem как primary retrieval (более точно и transparent чем semantic vector search) [FACT].

---

## 7. PM-Agent «Интернет-маркетолог» — функции и эскалации

**Role:** lead orchestrator MAMS, entry-point для human. Единственный агент, которому разрешено inter-client context switching. Не выполняет доменную работу (не пишет контент, не считает SEO) — только координирует и эскалирует.

**Основные функции:**
- **Client-intent parsing** — превратить человеческое «поднять продажи» в decomposed sprint plan.
- **Risk tiering** — каждое решение/действие классифицируется как Green/Amber/Red (см §12).
- **Delegation to specialists** — SEO/AEO-Spec, Content, SMM, PPC, CRO, Dev, Analytics, Link-Builder, Niche-Expert.
- **Review-loop orchestration** — producer → Reviewer (shared role) → (optional revise) → approval/publish.
- **Notion sync** — каждый significant action → Activity Log; каждая communication → Communication Log (per user's Command Center protocol).
- **Escalation policy** — если agent reports blocker / golden-set pass-rate <90% / skill rollback triggered → HITL notification to Alex.

**Эскалация в HITL:**

| Триггер | Скорость | Канал |
|---|---|---|
| Red-tier action требует approval | Sync, blocking | Notion comment @Alex + desktop notification |
| Skill-Updater хочет rollout мажорной версии | Sync, 24h SLA | Notion Skills DB comment |
| Amber-tier аномалия в production метриках | Async, HOTL | Notion Activity Log entry + daily digest |
| Client communication требует стиля/позиции бренда | Sync, 4h SLA | Notion Comm Log + email |

---

## 8. Команда агентов: обзор 12 ролей

Полные спецификации каждого — в `MAMS_Agent_Specs.md`. Обзор:

1. **PM-Director «Интернет-маркетолог»** — lead orchestrator.
2. **Strategist** — positioning, ICP, brand voice, competitive brief.
3. **SEO/AEO/GEO Specialist** — technical + content + AI-citation audit.
4. **Content Lead** — long-form, editorial, brand-voice review.
5. **SMM Specialist** — channel algorithms, content calendar, engagement.
6. **PPC/Paid Growth** — Google Ads PMax, Meta Advantage+, attribution.
7. **CRO/UX Specialist** — A/B tests, personalization, checkout optimization.
8. **Dev/QA** — landing pages, tracking implementation, webapp testing.
9. **Link-Builder** — outreach, digital PR, guest posting, Hunter.io.
10. **Analytics Specialist** — GA4, anomaly detection, reporting.
11. **Niche-Expert** — hybrid RAG+FT под конкретную клиентскую вертикаль.
12. **Skill-Updater (meta-agent)** — монитор retrospective + news feeds, запускает skill patch pipeline.

**Shared role: Reviewer** — вызывается любым agent'ом как read-only review перед outbound action. Не отдельный слот, но отдельный skill-set.

---

## 9. Коммуникации, контракты, Shared Heuristics

### 9.1 Unified Output Contract

Каждый agent возвращает JSON:
```json
{
  "task_id": "...",
  "agent_id": "...",
  "status": "done|blocked|needs_review",
  "outputs": {...},
  "citations": [{"claim": "...", "source": "...", "tag": "FACT|EXPERT-CLAIM|CONTESTED"}],
  "risk_tier": "green|amber|red",
  "next_step": "...",
  "cost": {"input_tokens": N, "output_tokens": N, "total_usd": N}
}
```

### 9.2 Shared Heuristics — Notion DB

Cross-agent learnings живут в Notion DB `Shared Heuristics`:
- Каждая запись: trigger condition + recommended action + evidence source + last updated.
- Пример: «если GSC CTR падает >20% за 7 дней при стабильной position → проверить AI Overviews expansion в nichе (ref: ALM Corp 9-industry AIO surge)».
- Вдохновлено ERL (arXiv 2603.24639) pattern — heuristic-pool with relevance scoring [FACT academic].

### 9.3 Inter-agent communication

Не peer-to-peer — всё через PM-Agent. Это снижает communication-bottleneck риск (Data Processing Inequality) и даёт полный audit trail.

---

## 10. Память, RAG, fine-tune, hybrid для ниш

**Центральный source:** AWS ML blog «Tailoring foundation models» benchmark [FACT]:

| Approach | Evaluator score | Inference latency | Continuous cost |
|---|---|---|---|
| Fine-tune only | 0.5556 | ~4.1s (fastest) | High hosting |
| RAG only | 0.8200 | ~8.3s | Lower |
| Hybrid (RAG + FT) | 0.8556 | ~17.7s | Highest |

**Ключевой инсайт arXiv 2401.08406 (Agriculture case):** FT дал +6pp accuracy и +25pp answer similarity. RAG добавил ещё +5pp. Эффекты кумулятивные.

**SecMulti-RAG (arXiv 2504.13425):** enterprise-pattern: 3 retrieval sources (internal docs, expert answers, external LLM). Confidentiality-preserving filter маршрутизирует sensitive prompts на local Qwen-2.5-14B, безопасные — на external [FACT]. Win-rates 79.3-91.9% в richness/helpfulness vs стандартный RAG.

**Decision framework для MAMS Niche-Expert:**

| Триггер | Подход |
|---|---|
| Динамичные данные (prices, stock, daily news) | RAG |
| Стабильный domain + tone (legal, medical) | FT |
| Factual precision критична, domain narrow | RAG |
| Latency <5s требуется | FT only |
| Максимальная accuracy нужна, стоимость ок | Hybrid |
| PII/sensitive данные | SecMulti-RAG на local model |
| Distilled student нужен (tokens cheap) | RAG-to-FT trajectory distillation (ICLR 2026 2510.01375): 91% ALFWorld success at 10-60% fewer tokens |

---

## 11. Самообучение агентов и Skill-Updater

### 11.1 Академическая база

| System | Что делает | Gating mechanism |
|---|---|---|
| **METAAGENT** (2508.00271) | Dynamic context engineering, in-house tool накопление | Verified reflection только после ground-truth answer |
| **SICA** (2504.15228) | Агент редактирует свою Python codebase | Archive best-perf agent → meta-agent цикл, benchmark-driven selection |
| **ERL** (2603.24639) | Heuristic pool из success/failure trajectories | Binary environment-feedback обязателен; LLM scoring для top-k injection |
| **SKILL-RL** (2602.08234) | Co-evolves SKILLBANK during RL | Triggers only при sub-threshold success; KL-penalty anchor to reference policy |
| **Self-Improving LLM Agents at Test-Time** (2510.07841) | TextGrad / Reflexion variants | Validation on golden set pre-rollout |

### 11.2 Skill-Updater pipeline (MAMS adaption)

```
detect → draft → validate (4 Trust Gates) → canary (5% traffic) → rollout → audit
                                                       ↘ blocked if Gate fail
```

- **detect:** trigger source: (a) news feed (новый Google core update → B-block skill refresh); (b) retrospective anomaly (golden-set pass-rate <90%); (c) manual request.
- **draft:** Skill-Updater агент применяет skill-creator для патча SKILL.md + refs.
- **validate (§13):** G1 Static linter, G2 Semantic LLM-judge, G3 Sandbox run в isolated worktree, G4 Permission Manifest.
- **canary:** 5% traffic на новую версию + A/B measurement vs stable.
- **rollout:** если canary metrics ≥ stable через 48h window → promote.
- **rollback:** one-click revert to last-known-safe version [FACT] Raconteur 2026 governance norms.

### 11.3 Risk-sensitive автономность

Skill-Updater не получает полной автономии:
- **Patch version (X.Y.Z):** авто-apply после G1-G4 pass + canary OK.
- **Minor version:** digest-approval (автоматически если еженедельный digest не flagged Alex).
- **Major version:** sync approval Alex через Notion Skills DB comment.

---

## 12. HITL-governance и tiered approval (Green/Amber/Red)

**Доказательная база:** strata.io, prefactor.tech, AWS healthcare blog, responsibleaifoundation.com, Raconteur 2026 [FACT cross-source].

### 12.1 Tier definitions

| Tier | Тип решения | Примеры для MAMS | Approval pattern |
|---|---|---|---|
| **Green** | Reversible, low-impact, pre-approved | Draft blog post, keyword research запрос, внутренний отчёт | Авто, time-boxed 15s, logged |
| **Amber** | Reversible но client-visible или с budget impact < $500 | Publish internal doc, schedule social post (not yet live), small Ads budget tweak | HOTL async monitor, default-approve если human не response в 15 min |
| **Red** | Irreversible / legal / PII / budget >$500 / client-facing publish | Send client email, publish live on CMS, launch new Ads campaign, modify production CRM data | HITL sync blocking approval, time-boxed 2-15 min, default-deny |

### 12.2 Control placement

Per strata.io / prefactor.tech [FACT]:

- **Pre-tool interrupts** — hook immediately before sensitive tool executes; human может approve / deny / "trust for session".
- **Context-aware tool interrupts** — controls embedded in specific tools с role-based access (AWS healthcare pattern).
- **Async remote interrupts** — для third-party sign-off через Step Function / Slack / email while agent продолжает non-blocking работу.
- **Mid-task MCP elicitation** — MCP server может pause mid-task через SSE, требуя business justification / manual credential.

### 12.3 Structured approval gates

Против rubber-stamping [FACT responsibleaifoundation.com]:

- **Challenge-and-Response checklists:** approver явно acknowledge intent + blast radius + rollback plan.
- **Two-factor judgment:** для Red-tier — OR independent human review OR counter-model sanity check.
- **Context в prompt:** что triggered, какие data, recent behavior agent'а.

### 12.4 Audit trail requirements

Immutable logs должны содержать [FACT]:
- **Who** approved.
- **When** approved.
- **Rationale** (free-text).
- **Exact contextual data** presented at decision time.

### 12.5 Rollback mechanisms

- **One-click revert** — tested, reverts agent + environment to last safe version [FACT Raconteur].
- **Pre-flight verification** — human operator проверяет viability proposed rollback plan ПЕРЕД authorizing execution.

---

## 13. Skill-lifecycle pipeline и Trust Gates

```
draft → Gate G1 (Static linter) → Gate G2 (Semantic judge)
      → Gate G3 (Sandbox behavioral) → Gate G4 (Permission Manifest)
      → canary (5% @ 48h) → A/B delta check vs stable
      → stable → (later) deprecated → retired
      ↘ blocked if any Gate fail
```

| Gate | Механика |
|---|---|
| **G1 Static** | Linter + regex на known-bad patterns (unrestricted network, eval, untrusted imports) |
| **G2 Semantic** | LLM-judge: соответствует ли body заявленному description? intent drift? |
| **G3 Sandbox** | Isolated worktree run с fake MCP tools; behavioral checks |
| **G4 Permission Manifest** | Declared permissions ≡ observed calls; если fail → auto-blocked |

**Golden-set eval:** per-skill 20-100 (input, expected-output, safety-criteria) пар. Threshold: ≥90% accuracy + 100% safety. Blocker для canary→stable promotion.

**Deprecation trigger:** skill → deprecated если pass-rate <85% на 3 последних runs → sync approval Alex для migration plan.

---

## 14. Notion как orchestration-слой: возможности и ограничения

**Notion API 2026-03-11 breaking changes** [FACT developers.notion.com]:
- `after` string → `position` object с `after_block|start|end`.
- `archived` → `in_trash` (глобальный rename).
- `transcription` block type → `meeting_notes`.

**Data_source events (since 2025-09-03)** [FACT]:
- `data_source.created | content_updated | schema_updated | moved | deleted`.

**Webhooks — delivery model:**
- POST на public URL (localhost не работает).
- **Signal-only payloads** — metadata only, integration должен fetch full content via API.
- **HMAC-SHA256 signing** — `X-Notion-Signature` header для validation.
- **Retries:** at-most-once, exponential backoff до 24h, 8 попыток.

**⚠️ Known limitations для orchestration:**
- **Out-of-order delivery** — integration должен parse `timestamp` поля и re-sequence.
- **Event aggregation delay** — высокочастотные `page.content_updated` batched в short window; delivery до 5 min.
- **Data staleness** — к моменту delivery event payload может не отражать current state → всегда fetch latest via API.

**Implication для MAMS:** Notion = **source of truth для status, task graph, logs**, но не для real-time orchestration triggers. Real-time — через MCP callbacks / direct SDK tool calls. Notion webhooks — для async cross-system sync (Obsidian, email digest, external dashboards).

---

## 15. SEO/AEO/GEO, CRO, PPC — что должна уметь система в 2026

### 15.1 SEO 2026 после March core update

**March 2026 Core Update** [FACT SEL/SEJ]:
- Google не выпустил new specific guidance — standing advice: helpful, reliable, people-first content.
- **Shift away from intermediary sites** — aggregators, directories, comparison-driven platforms пострадали.
- **Reward strong brands + owned data + direct query value** — официальные и institutional sites, specialist/niche sources, dominant platforms выиграли.

**AI Overviews impact** [FACT Ahrefs + ALM Corp]:
- AI answer engines handle >40% information discovery queries.
- AI traffic = 1-2% referral (still small).
- AIOs harm organic CTR даже для featured sites.
- **80% commercial/transactional searches still click non-AIO results** — cost per click sustained там.
- Only ~38% URLs cited in AIOs rank top-10 organic для того же запроса → «query fan-out» pattern.
- AIO coverage высок в Health, минимальный в e-commerce.

### 15.2 AEO/GEO — operational checklist

**Chunk retrieval optimization** [FACT Frase/Jasper]:
- Semantically tight passages, one idea per section.
- Well-formatted HTML, clear H2/H3 subheadings.
- **Answer-synthesis format:** direct concise sentence at start, plain factual tone, natural-language Q&A.
- **Citation-worthiness:** specific verifiable claims + original data > vague generalities.
- Author credentials + source citations prominently displayed.
- **Technical crawlability:** server-side render essential content (AI bots don't execute CSR JavaScript).
- **Multi-modal:** descriptive alt text; HTML tables > image of tables; `<figure>` wrap.

**Entity/schema requirements:**
- Author + Organization structured data для entity salience + citation metadata.

### 15.3 CRO 2026 benchmarks

**Global e-commerce avg CR:** 2.5-3.3% [FACT Stormy.ai].
**By industry:** Food & Beverage 6.1% · Beauty 5.1% · Fashion 3.0-4.1% · Luxury/Jewelry 1.2%.
**Mobile gap:** 70% traffic, но CR 1.8-2.8% vs desktop 3.2-3.9%.
**Search vs browse:** 2-3x higher conv для search users.

**AI-driven lifts** [FACT Stormy.ai]:
- AI shopping assistant engaged users: **4x conv** vs unassisted.
- WoW case (AI personalization): **+20% conversions**.
- 89% marketers report positive ROI from personalization.

**Checkout optimization**:
- Baymard cart abandon 70.19% = $260B opportunity.
- **1-click checkout (Shop Pay / Apple Pay): +16-21% conv**.
- Product video on PDP: +21-34% conv.
- Free shipping (zero-party data trade): +28% conv.

### 15.4 PPC 2026

**Google Ads PMax + Conversions API setup** [FACT Google Ads Help]:
- Dual-container GTM (web + server).
- GA4 client в server container + Conversion Linker + Google Ads Conversion Tracking.
- **Enhanced Conversions** (hashed first-party data to Google) — must-have.
- Consent Mode v2 advanced: tags load regardless, dynamically adjust; denied users → cookieless pings to Google domains.
- **Modeled conversions** fill gap для denied consent users → protects Smart Bidding training.

**Measured lifts:**
- Server-side Google Tag Gateway: **+14% conversion signals**.
- Enhanced Conversions: **+15-30% attribution accuracy**.
- Без server-side tracking: data gap из-за ad blockers, ITP, cookie clearing — оценивается до 40% (browser-only dependency).

**Google Data Manager API (GA Oct 2025)** — unifies signals across websites, apps, stores, CRM [FACT].

---

## 16. Analytics, аномалии, attribution 2026

### 16.1 Anomaly detection — reduce false positives

**Core thresholding** [FACT Anodot]:
- Minimum 10% percentage delta.
- **PLUS absolute delta threshold** (e.g. 10% AND $500 absolute drop).
- Urgency/duration match: 5-min scale для payment success, hourly для revenue.
- Direction-specific: alert on failure rate increase, conversion decrease.

**Multi-metric "influencing factors"**:
- Ratio metrics: use denominator как filter (purchase rate drop triggers only если add-to-carts >100).
- Volume baselines: country revenue drop triggers only если prior-day revenue ≥$2,000.

### 16.2 Adobe Analytics patterns [FACT]

- Statistical baseline + seasonality aware (Black Friday, holidays).
- **Contribution Analysis** — ML scoring marketing variables для detected anomaly.
- **Contribution Scores** — normalized ranking of causal factors.

### 16.3 Attribution в эпоху cookie deprecation

Core stack для MAMS Analytics agent:
1. Server-side GTM dual-container.
2. Consent Mode v2 advanced.
3. Enhanced Conversions (hashed PII).
4. Google Data Manager API integration для cross-source unification.
5. Modeled conversions as baseline for Smart Bidding / Advantage+ training.

---

## 17. Безопасность, аудит, compliance

**Skill-security baseline** [FACT arXiv 2602.12430v3 Agent Skills architecture paper]:
- Каждый skill декларирует permission manifest (read/write/denied buckets).
- G4 Gate блокирует если observed calls ≠ declared.
- Особо чувствительные (`skill-creator`, `mcp-builder`) — только для Skill-Updater / Dev, Red-tier approval.

**Audit trail (per §12.4):**
- Immutable log каждого tool-call, approval, rollback.
- Attached к Notion Activity Log + external git-backed vault.

**Rollback (per §12.5):**
- One-click to last-known-safe version.
- Pre-flight verification by human перед Red-tier action.

**Data minimization:**
- PII detection filter на prompt input.
- Sensitive prompt → routed to local model (SecMulti-RAG pattern).
- Client data segregation — каждый клиент отдельный MCP bucket, cross-client agent invocation denied by default.

**Compliance references:**
- EU AI Act (ongoing 2026 enforcement) — high-risk agent workflows требуют transparency + human oversight [FACT Raconteur 2026].
- NIST AI RMF — voluntary framework, widely adopted [FACT responsibleaifoundation.com].

---

## 18. Риски, open questions, следующие шаги

### 18.1 Known risks

| Risk | Mitigation |
|---|---|
| Multi-agent overkill → 15x token cost | Gate §5 per task type; default single-agent |
| Notion webhook delays >5 min | Не использовать для real-time; MCP callbacks вместо |
| Skill drift после auto-patch | G1-G4 + golden-set + canary + one-click rollback |
| AI Overviews citation drift (brand не появляется) | AEO audit skill с ежемесячным refresh |
| Consent Mode v2 pitfalls (misconfigured tags) | Validation skill + Dev review |
| Niche fine-tune cost | Start RAG-only, FT только для стабильных domain с proven ROI |
| PM-agent bottleneck | Async parallel dispatch, bypass for pre-approved skill-chains |

### 18.2 Open questions for Alex

1. **Budget discipline per sprint:** какой hard cap token spend per client per sprint? (дефолт: $50/sprint Green-tier, approval выше).
2. **Skill-Updater autonomy level:** авто-apply patch versions ок? (дефолт: да, с daily digest).
3. **Client data isolation boundaries:** cross-client Shared Heuristics — по темам (SEO patterns) или только внутри клиента?
4. **Niche-Expert onboarding depth:** какой минимальный corpus для нового клиента перед spawn Niche-Expert? (дефолт: 50-100 curated docs RAG + после 3 месяцев — optional FT).
5. **Notion vs Obsidian boundary:** что source of truth для shared heuristics — Notion DB или Obsidian vault? (предложено: Notion для task/status, Obsidian для chronology/insights).

### 18.3 Next steps

1. Review этого документа Alex → уточнения (Gate-5 human checkpoint).
2. После approval: implement PM-Agent (Claude Agent SDK) + 3 первичных subagent (SEO, Content, Analytics).
3. Populate Notion template (см `MAMS_Notion_Template.md`).
4. Первый клиент dogfood 30-day pilot — измерить token costs, accuracy, HITL frequency, rollback rate.
5. После pilot: expand team до 12 ролей.

---

**End of Architecture Report v2.0.**

Companion documents:
- `MAMS_Agent_Specs.md` — 12 agent passports
- `MAMS_Skill_Inventory.md` — skill catalog + governance
- `MAMS_Sample_E2E_Scenario.md` — NorthPine Outdoor 6-month walk-through
- `MAMS_Notion_Template.md` — 9 databases + dashboards + clone protocol

**Research anchor:** NotebookLM notebook `d63a00bc-4188-4794-89b6-958361902bbb` (≈90 sources, 9 blocks).
