# Skills (пусто на старте)

**Как наполнять:** итеративно на сервере, по мере того как агенты начинают использовать скилл. Полный каталог из 50+ скиллов — в `../../docs/MAMS_Skill_Inventory.md` §2.

## P0 — нужны для DG-2 / DG-3 (минимум для запуска PM + первого специалиста)

Эти скиллы нужно написать (или импортировать из публичных Anthropic skills repo) до первого продакшн-запуска:

| Skill ID | Для кого | Источник | Статус |
|---|---|---|---|
| `risk-tiering` | pm-director | MAMS-custom, spec в Skill Inventory §3.1 | TODO |
| `notion-orchestration` | pm-director | MAMS-custom, spec в Skill Inventory §3.2 | TODO |
| `project-workflow` | pm-director | импортировать из Anthropic examples | TODO |
| `productivity:task-management` | pm-director | import | TODO |
| `productivity:memory-management` | pm-director | import | TODO |
| `seo-audit` | seo-aeo-specialist | публичный Anthropic skills + расширить 2026 signals | TODO |
| `seo-content` | content-lead / seo | публичный + humanizer chain | TODO |
| `content-creation` | content-lead | import + brand voice adapter | TODO |
| `humanizer` | content-lead | публичный, готов к use | TODO |
| `doc-coauthoring` | strategist, pm | публичный | TODO |

## P1 — после DG-3 (расширение на 2-3 специалиста)

- `ahrefs-seo`, `semrush-api` (SEO + Analytics)
- `campaign-plan`, `performance-report` (SMM + PPC)
- `data:analyze`, `data:build-dashboard`, `data:statistical-analysis` (Analytics)
- `research-via-notebooklm` (Niche-Expert, Skill-Updater)

## P2 — после DG-4 (полный 12-агент roster)

- All design/CRO skills (`design-critique`, `accessibility-review`, `user-research`, `landing-page-designer`, `ux-copy`, `design-handoff`)
- All dev/QA skills (`architecture`, `testing-strategy`, `deploy-checklist`, `webapp-testing`, `code-review`, `debug`)
- Link-building (`hunter-io`, `email-sequence`)
- Meta (`skill-creator`, `mcp-builder`, `consolidate-memory`)

## P3 — Phase 2

- `skill-updater-pipeline` (MAMS-custom, Skill Inventory §3.3)
- `agent-as-evaluator` (MAMS-custom, Skill Inventory §3.4)

## Структура каждого скилла

Per Anthropic canonical pattern:

```
skills/
  {skill-id}/
    SKILL.md              # frontmatter (name, description <100 words) + body (≤3000 words)
    references/           # опционально — детальные refs, загружаются по запросу
      {topic}.md
    scripts/              # опционально — исполняемые helpers
      {helper}.py
    golden_set/           # опционально — eval data для G2/golden-eval
      cases.jsonl
```

**Правило:** skill body содержит инструкции ДЛЯ Claude (imperative voice, "Read the config file", not "You should read"), а не документацию для пользователя. См. Skills Inventory §0 решения.

## Versioning

- Semver (`1.0.0` → `1.0.1` patch, `1.1.0` minor, `2.0.0` major)
- Git-tag `skill/{id}/v{semver}` на каждом promote
- Supabase `skills.manifest` row на версию (Phase 2)
