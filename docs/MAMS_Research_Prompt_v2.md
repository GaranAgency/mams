Проведи исследование через research-via-notebooklm v2.6 для проектирования
универсальной мульти-агентной системы комплексного интернет-маркетинга.

===========================================
[CODE]: [MAMS] Multi-Agent Marketing System
===========================================

КОНЕЧНАЯ ЦЕЛЬ (для меня, не для скила):
Спроектировать универсальную команду AI-агентов под управлением
"Интернет-маркетолога" (PM-агент), которая ведёт ЛЮБОЙ интернет-проект
полного цикла:
- Веб-разработка или доработка существующего сайта
- SEO (organic search + AI-search: ChatGPT, Perplexity, Gemini, AIO)
- Контент-маркетинг (статьи, лендинги, email)
- SMM (социальные сети, постинг, engagement)
- PPC (Google Ads, Meta Ads, LinkedIn Ads)
- CRO и UX-оптимизация
- Линкбилдинг и PR-аутрич
- Analytics-driven итерации на основе реальных метрик

Ключевое требование — СИСТЕМА НЕ ЗАМКНУТА:
- Агенты подключаются к реальным системам аналитики (GA4, GSC, Ahrefs API,
  Meta Ads Manager, Google Ads API) и видят live-метрики
- Вносят правки на основе данных, не на основе предположений
- Самообучаются: отдельный Meta-Agent (Skill-Updater) мониторит рынок,
  находит новые подходы/инструменты/алгоритмы и обновляет скилы
  остальных агентов
- Работают по спринтам через Notion (Kanban, tasks, metrics)

HUMAN-BUDGET-MODEL (front-loaded):
- Стадия стратегии (старт проекта + квартальные ревью) — human active,
  2-5 часов в неделю, согласования обязательны
- Execution phase — human passive, 30-60 минут в неделю на digest-аппрувки,
  AI действует максимально автономно в рамках согласованной стратегии
- Escalation к human: (a) бюджетные решения выше пороа, (b) новый доступ/ресурс,
  (c) risk-tier Red события (retraction, penalty, PR incident)

===========================================
СЦЕНАРИЙ: B (Deep-Academic) + C (Market) ГИБРИД
===========================================
Причина гибрида: тема требует и академической базы (multi-agent orchestration,
self-improving systems, LLM agent architectures), и свежего рыночного
понимания (SEO/AEO/GEO 2026, production-ready фреймворки, Claude Agent SDK).

===========================================
ВРЕМЕННОЕ ОКНО
===========================================
- Hard cutoff: published_at >= 2025-10-01 (последние ~6-7 месяцев)
- Soft exception: foundational academic papers допустимы старше, но
  помечены [FOUNDATIONAL], max 15% корпуса
- Retractions/supersessions: жёсткое исключение (M3-protocol)

===========================================
SUB-QUESTIONS (9 блоков, 28 вопросов)
===========================================

БЛОК A: Архитектура мульти-агентных систем
  A1. Production-готовые patterns для LLM-оркестратора с подчинёнными
      специалистами? (hierarchical, swarm, blackboard, actor-model, graph-based)
  A2. Claude Agent SDK vs LangGraph vs CrewAI vs AutoGen vs Semantic Kernel —
      что выбрать для команды из 10-12 агентов с human-in-the-loop?
  A3. Delegation protocol: когда PM делегирует специалисту, когда выполняет сам,
      когда вовлекает нескольких параллельно, как консолидирует output?
  A4. Context/State management: shared memory, handoff summaries, persistent
      knowledge base — как передавать state между агентами без раздувания
      контекста?

БЛОК B: SEO 2026 (organic + AI-search)
  B1. Ranking factors 2026: что критично сдвинулось относительно 2024?
      (AI Overviews, E-E-A-T shifts, helpful content v3+, site reputation abuse)
  B2. GEO/AEO: как оптимизировать под ChatGPT/Perplexity/Claude/Gemini citations?
      Что РЕАЛЬНО работает (measured), что hype?
  B3. Технический SEO 2026: Core Web Vitals v3, INP, Schema.org updates,
      crawl-budget для AI-ботов, llm.txt / robots.txt для AI-agents.
  B4. Контент-стратегия под AI-citations: topic clusters vs entity-based vs
      answer-engine-optimization формат, длина контента, структура.

БЛОК C: Разработка, CRO, UX
  C1. Build-or-renovate diagnostic framework 2026: когда legacy-сайт лучше
      доработать, когда полностью переделать? Signals и decision matrix.
  C2. CRO frontiers 2026: personalization, adaptive layouts, AI-driven A/B
      testing, behavioral triggers, predictive UX.
  C3. UX/UI patterns дающие ОДНОВРЕМЕННО высокий CR и хороший SEO-score
      (без конфликта).

БЛОК D: Нишевая экспертиза (dynamic, не статичная)
  D1. Как БЫСТРО (за 1-2 сессии) построить Knowledge Base для произвольной
      новой ниши клиента? Onboarding workflow для Niche-Expert агента.
  D2. RAG vs fine-tune vs structured ontology vs hybrid — что оптимально для
      агента, который может переключаться между нишами?
  D3. Expert-in-the-loop patterns: quality gates, approval workflows,
      fact-check protocols для контента с доменной спецификой.

БЛОК E: Human-in-the-Loop governance (front-loaded)
  E1. Risk-tier frameworks для маркетинговых решений: что можно автономно,
      что требует human approval, что всегда Red (escalation).
  E2. Patterns минимизации human burden: batch approvals, digest notifications,
      async checkpoints, time-boxed auto-approve (если human не ответил за N часов).
  E3. Strategy-phase vs execution-phase governance: как менять модель
      автономии агентов от высокого human involvement в начале к полной
      автономии в day-to-day?

БЛОК F: Self-Improving Systems (Meta-Agent / Skill-Updater)
  F1. Continuous market intelligence: как отдельный агент сканирует
      SEL/SEJ/Moz/Ahrefs/arXiv/Anthropic/Google releases на новые подходы
      без false positives и signal fatigue?
  F2. Skill-update protocol: когда найденная новость → обновление скила
      другого агента? Validation, A/B testing, rollback механика.
  F3. Meta-learning patterns: как агенты учатся на собственных ошибках
      (retrospective analysis, post-mortem-to-skill-patch pipelines)?
  F4. Versioning и change management для live skill registry — как катить
      обновления без разрушения текущих проектов.

БЛОК G: SMM + PPC Specifics
  G1. SMM 2026: algorithmic changes на TikTok/Instagram/LinkedIn/X,
      AI-generated content policies, organic vs paid mix, posting frequency.
  G2. PPC 2026: Google Ads Performance Max updates, Meta Advantage+,
      automated bidding strategies, conversion API, privacy-first attribution.
  G3. Cross-channel orchestration: как SEO + SMM + PPC агенты
      координируются без дублирования усилий и budget cannibalization?

БЛОК H: Analytics Integration
  H1. Какие метрики критичны для каждого типа задачи (SEO/SMM/PPC/CRO)
      и где их брать API-ми в 2026?
      (GA4, GSC, Ahrefs API, Semrush API, Meta Graph API, Google Ads API,
      Mixpanel, PostHog, Amplitude)
  H2. Attribution 2026: consent-mode v2, server-side tagging, ML attribution
      models — как агенты интерпретируют данные с учётом signal loss?
  H3. Anomaly detection и alert design: как Analytics-Agent отличает
      шум от реальных сигналов и не спамит human alert'ами?

БЛОК I: Notion-as-Orchestration-Layer
  I1. Best practices проектного управления AI-teams в Notion 2026:
      databases structure, Kanban flows, sprint templates, metrics dashboards.
  I2. Notion API capabilities для AI-агентов: что агенты могут делать
      автономно (создавать tasks, обновлять статусы, логировать), где
      упираются в limits.
  I3. Как связать Notion tasks с external execution (code deploys, content
      publishes, ad launches) через MCPs и webhooks.

===========================================
СТРУКТУРА КОРПУСА (целевая — 100-140 sources)
===========================================

Tier S Primary / Platform:
  - docs.anthropic.com (Agent SDK, Subagents, Skills, Claude Code, MCP)
  - openai.com/docs (Assistants, Swarm, Agents SDK)
  - developers.google.com/search (Search Central, Quality Raters)
  - google.com/search/howsearchworks
  - developers.google.com/analytics (GA4), search.google.com (GSC docs)
  - developers.facebook.com (Graph API, Ads API)
  - developers.google.com/google-ads (Ads API)
  - developers.notion.com (Notion API)
  - schema.org, web.dev, ahrefs.com/api, semrush.com/api

Tier S Gov/Standards:
  - W3C, IETF (llm.txt / agent.txt standards если появятся)
  - EU AI Act, GDPR/CCPA consent frameworks

Tier S Expert Authority:
  - Agent architecture: Simon Willison, Harrison Chase, Jerry Liu, Andrew Ng,
    Lilian Weng, Yohei Nakajima, Dharmesh Shah
  - SEO: Rand Fishkin, Aleyda Solis, Marie Haynes, Kevin Indig, Eli Schwartz,
    Glen Gabe, Lily Ray, Cyrus Shepard
  - CRO/UX: Peep Laja (CXL), Baymard Institute, Jakob Nielsen
  - SMM/PPC: Neil Patel, Avinash Kaushik, Frederick Vallaeys (PPC)

Tier S Academic:
  - arXiv.org (cs.AI, cs.CL, cs.MA, cs.IR) — 2025-2026 only
  - ACL, EMNLP, NeurIPS, ICLR — LLM agents, self-improving systems
  - MIT CSAIL, Stanford HAI, CMU, DeepMind, Anthropic Research

Tier S/A Trade Publications:
  - Search Engine Land, Search Engine Journal, Search Engine Roundtable
  - Moz Blog, Ahrefs Blog, Semrush Blog, Backlinko
  - Smashing Magazine, CSS-Tricks, web.dev blog
  - LangChain Blog, OpenAI Blog, Anthropic News
  - Social Media Today, Search Engine Watch, PPC Hero
  - Notion Blog, Superhuman AI, Every.to

Tier A Practitioner Guides:
  - Backlinko, Ahrefs Guides, Moz Learn
  - Nielsen Norman Group, CXL Institute, Content Marketing Institute
  - Baymard Institute, Growth.Design

Tier A Discovery (SIFT-passed):
  - Substacks: Kevin Indig "Growth Memo", Aleyda Solis "SEOFOMO",
    Eli Schwartz "Product-Led SEO", Simon Willison, Latent Space
  - YouTube (только с verified transcripts): Ahrefs, Semrush, Google Search
    Central, Anthropic talks

EXCLUDE (жёстко):
  - Medium от анонимных / AI-generated contents
  - LinkedIn posts без verified expertise
  - Listicle SEO spam без primary research
  - Affiliate-heavy review sites

===========================================
PUBLISHER-CAP И ANTI-ECHO
===========================================
Default 25% per publisher_group.

Publisher groups (explicit):
  - "Anthropic" — cap 35% (primary platform, exception)
  - "Google" (all subdomains) — cap 35% (primary platform, exception)
  - "Meta/Facebook" — cap 20%
  - "Semrush/Backlinko" — one group (owned by same entity)
  - "Ahrefs" — standalone
  - "Moz" — standalone
  - "SEL/SEJ/SER" — treat as separate издатели
  - "Substack" — cap 15% по всем Substacks суммарно

===========================================
ЯЗЫК
===========================================
- Корпус: EN only
- Deliverable: RU (все итоговые документы на русском)
- Citation tags [FACT]/[EXPERT-CLAIM]/[CONTESTED] — на английском
- URL, имена авторов, заголовки — в оригинале EN
- Технические термины (agent, skill, pipeline, AIO, GEO, CRO, etc.) — EN

===========================================
DELIVERABLES (обязательные)
===========================================

1. MAMS_Architecture_Report.md (+ .docx) — полный аналитический отчёт:
   - §1 Executive Summary (1 страница)
   - §2 Проблема, цели, границы системы
   - §3 Обзор архитектурных паттернов (БЛОК A)
   - §4 SEO 2026 state-of-the-art (БЛОК B)
   - §5 Dev/CRO/UX требования (БЛОК C)
   - §6 Dynamic niche onboarding (БЛОК D)
   - §7 Human-in-the-Loop governance + front-loaded model (БЛОК E)
   - §8 Self-Improving Systems — Skill-Updater design (БЛОК F)
   - §9 SMM + PPC orchestration (БЛОК G)
   - §10 Analytics Integration layer (БЛОК H)
   - §11 Notion-as-Orchestration (БЛОК I)
   - §12 Рекомендуемая архитектура команды (финальный дизайн)
   - §13 Responsibility Matrix (RACI для всех агентов)
   - §14 Delegation/Handoff Protocols
   - §15 Human Checkpoints Catalog
   - §16 Risk Assessment
   - §17 Implementation Roadmap (фазы + milestones)
   - §18 Bibliography (L2 tier-structured template)

2. MAMS_Agent_Specs.md — детальная спецификация каждого агента:
   - PM-Agent (Интернет-маркетолог, head orchestrator)
   - Strategy-Agent (стратегия + quarterly reviews + pivot decisions)
   - SEO-Specialist (organic + GEO/AEO)
   - Content-Writer (статьи, лендинги, email)
   - SMM-Specialist (соцсети, постинг, community)
   - PPC-Specialist (Google/Meta/LinkedIn Ads)
   - Niche-Expert (dynamic per-project KB builder + fact-checker)
   - Designer (UI/UX/visual)
   - Developer (frontend/backend/CMS/integrations)
   - QA/Tester (functional + SEO audit + a11y)
   - Analytics-Agent (GA4/GSC/Ads API integration + metrics interpretation)
   - Skill-Updater (Meta-Agent, continuous market scanning + skill patches)

   Для каждого: role, inputs, outputs, tools, skills required, MCPs used,
   delegation patterns, escalation rules.

3. MAMS_Skill_Inventory.md — таблица:
   - Существующие скилы из моего репозитория, подходящие каждому агенту
     (mapping: agent → skill list)
   - Скилы, которые нужно дописать с нуля (с priority P0/P1/P2)
   - Скилы, требующие моего input'а (доступы, preferences, нестандартные настройки)
   - Dependency graph между скилами

4. MAMS_Sample_E2E_Scenario.md — end-to-end пример (универсальный):
   "Клиент приходит с запросом X, команда агентов ведёт проект от онбординга
   до Q2 результатов" — walkthrough с указанием каждого handoff,
   human checkpoint, и activity log entry.

5. MAMS_Notion_Template.md — спецификация Notion-проекта:
   - Структура databases (Projects, Tasks, Sprints, Metrics, Skills Registry,
     Market Intelligence, Decisions Log)
   - Связи между databases
   - Views (Kanban, Sprint, Metrics Dashboard, Risk Dashboard)
   - Автоматизации (Notion formulas + integrations)

===========================================
ГЛУБИНА И БЮДЖЕТ
===========================================
- Глубина: deep (target 100-140 sources in final corpus)
- Harvest budget: до 400 candidates pre-SIFT
- Gap-fill iterations: max 3 (S13 rule)
- Reserve pool: агрессивная активация (L5 rule)
- Expected time: 3-4 сессии research + 2 на synthesis + 1 на Notion template

===========================================
СОГЛАСОВАНИЕ (human checkpoints в research-процессе)
===========================================
- После Stage 1 (Scope) — покажи мне финальный scope-doc до harvest
- После Stage 3 (Ranked list) — покажи ranked-source-list, аппрувлю
  Tier S выборку и reserve pool
- После Stage 5 (Answer draft) — покажи §12 Recommended Architecture
  и §2 MAMS_Agent_Specs (список агентов и их границы) до финализации —
  это ключевые дизайн-решения
- После Stage 7 (Final deliverables) — финальная сдача всех 5 документов

===========================================
POST-DELIVERY (за пределами этого research)
===========================================
После получения 5 документов — отдельная фаза имплементации:
1. На основе MAMS_Skill_Inventory.md пройдёмся по каждому скилу,
   решим распределение работы (что я пишу, что ты, что нужно от меня)
2. По одному агенту за итерацию: draft → ревизия → пакет
3. Notion-проект создаётся из MAMS_Notion_Template.md
4. Интеграционный тест на реальном проекте из пайплайна
5. Финальная поставка — zip-архив с набором готовых Claude skills
   + Notion workspace template

===========================================
СТАРТ
===========================================
Начинай с Stage 0 (Gate-0 connectivity check) → Stage 1 (Scope confirmation).
Покажи мне полный scope-doc до того, как уйдёшь в harvest.
