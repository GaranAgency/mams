# MAMS Plugin (scaffold)

**Status:** `0.1.0` — skeleton scaffolded in Cowork, iterative buildout on server (Claude Code).

Полный контекст — в родительской папке: `../CLAUDE.md`, `../HANDOFF.md`, `../docs/`.

## Что это

Claude Code plugin для MAMS (Multi-Agent Marketing System) — команда из 12 специализированных subagents под управлением PM-Director «Интернет-маркетолог», оркестрирующая полный цикл интернет-маркетинга.

## Структура

```
plugin-scaffold/
├── .claude-plugin/
│   └── plugin.json         # manifest v0.1.0
├── agents/                 # 12 subagent definitions (stubs — full passports в docs/)
│   ├── pm-director.md          ← lead orchestrator
│   ├── strategist.md
│   ├── seo-aeo-specialist.md
│   ├── content-lead.md
│   ├── smm-specialist.md
│   ├── ppc-specialist.md
│   ├── cro-ux-specialist.md
│   ├── dev-qa.md
│   ├── link-builder.md
│   ├── analytics-specialist.md
│   ├── niche-expert.md
│   └── skill-updater.md        ← meta-agent
├── skills/                 # пусто — наполняется на сервере (P0 из Skill Inventory)
├── commands/               # пусто — зарезервировано для legacy single-file /-команд
├── hooks/
│   └── hooks.json          # stub — активируется после DG-2
└── .mcp.json.example       # MCP-сервера, которые плагин рассчитывает найти
```

## Что делать на сервере

1. Открыть `../HANDOFF.md` — там пошаговый чек-лист.
2. В корне плагина на сервере создать `.mcp.json` (скопировав `.mcp.json.example` и заполнив env-refs).
3. Пройти Deployment Gates: DG-1 (Notion DBs) → DG-2 (plugin валиден, PM-Agent запускается) → DG-3 (первая задача проходит через pipeline) → DG-4 (E2E scenario воспроизведён).
4. По мере добавления агентов — наполнять `skills/` из Skill Inventory P0 (см. `../docs/MAMS_Skill_Inventory.md` §2).

## Как валидировать

```bash
# Если Claude Code CLI поддерживает plugin validate:
claude plugin validate .claude-plugin/plugin.json

# Или вручную:
test -f .claude-plugin/plugin.json
test "$(jq -r .name .claude-plugin/plugin.json)" = "mams"
test -d agents && ls agents/*.md | wc -l   # должно быть 12
```

## Как установить (после DG-2)

Упаковать плагин и установить локально:

```bash
cd plugin-scaffold
zip -r /tmp/mams.plugin . -x "*.DS_Store" "skills/.gitkeep" "commands/.gitkeep"
cp /tmp/mams.plugin ~/mams.plugin
# Установка — через Claude Code plugin install UI / команду (см. docs Claude Code)
```

## References

- Полный контекст проекта: `../CLAUDE.md`
- Руководство по развёртыванию: `../HANDOFF.md`
- Архитектура и обоснования: `../docs/MAMS_Architecture_Report.md`
- Агенты (passports): `../docs/MAMS_Agent_Specs.md`
- Скиллы (catalog + specs): `../docs/MAMS_Skill_Inventory.md`
- E2E walkthrough: `../docs/MAMS_Sample_E2E_Scenario.md`
- Notion DBs: `../docs/MAMS_Notion_Template.md`
