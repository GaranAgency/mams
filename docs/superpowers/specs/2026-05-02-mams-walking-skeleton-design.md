# MAMS Walking Skeleton — Design (Phase A.1)

**Date:** 2026-05-02
**Author:** Alex (digitalgaran@gmail.com), drafted by Claude Code
**Project (Notion):** AI & Claude (page_id `353326fe-46c5-813d-bbaf-fe2f094691c1`)
**Project code prefix:** `[MAMS]`
**Status:** approved for implementation
**Supersedes:** none
**Ships ahead of:** Phase A.2 (PM delegation, separate spec)

---

## 1. Goal

Доставить **первое реальное сообщение** от MAMS в Telegram-группу проекта **GRN** ("garan ai", chat_id `-5229557142`) — короткий неформальный standup со статусом застрявших задач, сгенерированный LLM'ом по данным из Notion Tasks DB.

Walking skeleton проверяет одну сторону системы — **proactive monitoring** (`/mams-standup`). Вторая сторона — **reactive PM delegation** — ship'ится отдельным spec'ом в Phase A.2.

### Definition of done для Phase A.1

1. `/mams-standup` запускается из Claude Code сессии вручную
2. Слэш-команда инструктирует Claude: прочитать Tasks DB и Projects Registry через Bash+curl, отфильтровать stuck-задачи, **сгенерировать сообщение в-контексте** (без отдельного API-ключа), запостить в Telegram, записать в Activity Log
3. Сообщение попадает в Telegram-группу GRN
4. Activity Log содержит запись `Category=Note`, `Entry="[MAMS] /mams-standup sent to GRN (N stuck tasks)"`
5. Smoke-test: 3 последовательных запуска возвращают **разные** формулировки, все упоминают каждое stuck-task имя
6. Empty-state policy: в Phase A.1 сообщение **всегда** отправляется (даже если 0 stuck-задач) — Alex должен видеть что команда отработала. Подавление при 0 — Phase B feature (когда добавим scheduling)

---

## 2. Architecture

```
┌──────────────────────────────────────────────────────────────┐
│  /mams-standup (Claude Code slash-command, markdown only)    │
│  → instructs Claude (current session) to execute steps:      │
│                                                              │
│   1. Bash+curl: read Notion Projects Registry                │
│      filter: Status=Active AND Channel ∈ {telegram}          │
│      AND Channel Address != ""                               │
│   2. for each qualifying project:                            │
│        Bash+curl: read Notion Tasks DB                       │
│        filter: Status ∈ {in_progress, blocked, review}       │
│          AND ( Status ∈ {blocked, review}                    │
│                OR last_edited_time < now - 3 days )          │
│        client-side group_by Ball With                        │
│        client-side sort by last_edited_time ASC              │
│   3. for each project (always, even if 0 stuck tasks):       │
│        Claude generates message in-context using §5.3 prompt │
│        Bash+curl: POST to Telegram Bot API                   │
│        Bash+curl: write Activity Log entry                   │
│   4. report summary line per project to Alex                 │
│                                                              │
│  No Python script. No daemon. No state between invocations.  │
│  All credentials read at runtime from existing files.        │
└──────────────────────────────────────────────────────────────┘
```

**Key design choices and rationale (so we don't re-litigate later):**

- **Direct Telegram Bot API**, not outbox pattern. Walking-skeleton has one outbound use-case (1 group, manual frequency). Outbox overhead unjustified at this scale. Migration path: trivial (sendMessage signature is universal).
- **Slash-command-only, no Python script.** Claude Code session that invokes `/mams-standup` IS the LLM. Reading Notion + posting Telegram is plain Bash+curl. No separate Anthropic SDK call, no extra API key, no script-vs-command duality. When Phase B adds `/schedule`, scheduled background agent is also a Claude Code session — same approach works. Extract to Python only if/when we hit a real reason (running outside Claude Code).
- **LLM-generated message body**, not template. Same Claude that runs the command generates the prose, varying phrasing each time. Templates would feel robotic by 2nd reading.
- **Notion `last_edited_time`** as staleness signal. Built-in, no custom fields. PM-Director and humans both bump it whenever they touch a task. Snooze/escalation logic deferred to Phase B (will need a `Last reminder sent at` field).
- **Single `Ball With` enum field**, not two-field (category + name). Names of internal team are baked into enum (4 options); external party names live in task Description first line; agent name lives in existing `Owner Agent` field. One schema delta vs two.
- **Empty-state policy: always send.** Alex needs proof of life from each manual invocation. When Phase B adds scheduling and notification fatigue becomes a real concern, we revisit.

---

## 3. Notion schema deltas

### 3.1 Tasks DB (`5006980c-ad06-460d-872d-6de38142b5f2`)

**Add one field:**

| Field | Type | Options |
|---|---|---|
| `Ball With` | select | `Alex`, `Anastasia`, `Elena`, `Egor`, `Agent`, `Client`, `Vendor`, `Other` |

**Existing 19 fields untouched.** PM-Director walking-skeleton fills only 7 of them: Name (title), Project (relation), Status, Priority, Tier, Owner Agent, **Ball With**. Remaining 12 (Sprint, Estimate, Reviewer, Skills Used, Decisions, Risks, etc.) stay null until Phase B.

**Convention for `Ball With`:**
- Team member name (`Alex`/`Anastasia`/`Elena`/`Egor`) → that person owns the next move
- `Agent` → an AI agent owns it; specific agent identity in `Owner Agent` field
- `Vendor`/`Client` → external party; specific name in task Description first line, format suggestion: `Vendor: Маша. Telegram @masha_design.` or just `Vendor: Маша.`
- `Other` → catch-all (lawyer, accountant, anyone outside the above 4 categories)

### 3.2 Projects Registry (`9a9b6c9d-40bd-4d3d-8f99-56ef890a774e`)

**Add two fields:**

| Field | Type | Options / format |
|---|---|---|
| `Internal Notification Channel` | select | `telegram`, `slack`, `email`, `none` |
| `Channel Address` | rich_text | freeform; for telegram: numeric chat_id (e.g. `-5229557142`) |

**Set GRN row immediately:**
- `Internal Notification Channel = telegram`
- `Channel Address = -5229557142`

**Default for existing projects (one-time backfill):** programmatically set `Internal Notification Channel = none` for all 6 existing project rows except GRN (Klassikasa, Miami First Remodeling, Advanced TRT Clinic — Instagram, Advanced Vitality Group, Multi-Agent Marketing System, AI & Claude). For GRN: `telegram`. New projects entered later default to null until set explicitly — `/mams-standup` treats null and `none` identically (skip).

### 3.3 .env fix

`/home/team/mams/.env` line `NOTION_DB_COMMUNICATION_LOG_ID=` is empty. Real ID recovered: `ba097004-2960-4b95-be2c-0d76109fe755`. Populate.

---

## 4. Seed data (one task)

Created in Tasks DB before first /mams-standup run:

| Field | Value |
|---|---|
| Name | Стратегия и основной посыл сайта |
| Project | Garan Agency (GRN) — relation to Projects Registry row |
| Status | blocked |
| Priority | P0 |
| Tier | Amber |
| Ball With | Alex |
| Owner Agent | (null) |
| Description | Foundation для дизайна и копирайтинга. Прорабатывать с Claude в отдельной сессии — позиционирование, основной посыл, ключевые конверсионные блоки. Без этого вендор по дизайну (потенциально Маша или AI-агент) и content-lead не могут начать. |
| Due | (null) |

Один таск. Никаких синтетических Маш / Анастасий / Елен — это исказило бы первое реальное впечатление от системы.

---

## 5. `/mams-standup` implementation

### 5.1 File layout

```
/home/team/mams/
└── plugin-scaffold/
    └── commands/
        └── mams-standup.md      ← Claude Code slash-command (new, only file added)
```

No Python script. No script directory. The slash-command markdown contains all instructions Claude needs to execute the steps.

### 5.2 Runtime credentials (read fresh each invocation)

| Variable | Source | Purpose |
|---|---|---|
| `NOTION_KEY` | `cat ~/.claude-secrets/notion.key` | Notion API auth header |
| `TG_TOKEN` | `grep ^TELEGRAM_BOT_TOKEN= /home/team/mams/telegram-bot/.env \| cut -d= -f2` | Telegram Bot API auth path |
| `PROJECTS_DB` | `grep ^NOTION_DB_PROJECTS_REGISTRY_ID= /home/team/mams/.env \| cut -d= -f2` | Projects Registry DB ID |
| `TASKS_DB` | `grep ^NOTION_DB_TASKS_ID= /home/team/mams/.env \| cut -d= -f2` | Tasks DB ID |
| `ACTIVITY_DB` | `grep ^NOTION_DB_ACTIVITY_LOG_ID= /home/team/mams/.env \| cut -d= -f2` | Activity Log DB ID |
| `STALE_DAYS=3` | constant in slash-command | Staleness threshold for in_progress tasks |

All values read at runtime by Bash within the slash-command. Nothing is baked into the markdown.

### 5.3 Algorithm (executed by Claude in-session via Bash)

**Step-by-step:**

1. Bash: load credentials (§5.2 table).
2. Bash+curl: `POST https://api.notion.com/v1/databases/{PROJECTS_DB}/query` with filter `{Status=Active, Internal Notification Channel ∈ {telegram}, Channel Address is not empty}`. Parse JSON. Result: list of {project_name, project_code, channel, channel_address, project_id}.
3. For each qualifying project (today: GRN only):
   - Bash+curl: `POST https://api.notion.com/v1/databases/{TASKS_DB}/query` with filter `{Project relation contains project_id, Status in {in_progress, blocked, review}}`. Parse JSON.
   - Client-side filter: keep tasks where `Status ∈ {blocked, review}` OR `(Status=in_progress AND now - last_edited_time > 3 days)`.
   - Group by `Ball With` value, sort within groups by `last_edited_time` ascending (oldest first).
   - Build structured task list: `[{name, ball_with, status, days_since_update, due, description_lead}]`.
   - Claude (in-context, no extra API call): generate Telegram message body using §5.4 system prompt + structured list as input. Empty list → still generate per the empty-state rule.
   - Bash+curl: `POST https://api.telegram.org/bot{TG_TOKEN}/sendMessage` with `chat_id={channel_address}`, `parse_mode=HTML`, `text={generated message}`. Parse response, extract `result.message_id`.
   - Bash+curl: `POST https://api.notion.com/v1/pages` to create Activity Log row (§5.6 schema).
4. Print one summary line per project to Alex: `[GRN] sent message_id=<id>, N stuck tasks (Alex:1, Vendor:0, ...)`.

### 5.4 System prompt for Claude (LLM message generator) — final text

```
Ты пишешь короткое неформальное сообщение в внутреннюю Telegram-группу
проекта. В группе 4 человека: Alex (общий, основатель агентства),
Anastasia (head of paid traffic), Elena (head of dev), Egor (head of
PM/AI). Клиента в группе нет.

Тебе передаётся JSON со списком задач которые буксуют. Твоя цель:

1. Адресовать каждую задачу тому, у кого мяч (поле "ball_with"):
   - Если ball_with = одно из имён команды (Alex/Anastasia/Elena/Egor)
     → обращайся напрямую: "Anastasia, по этому креативу...".
   - Если ball_with = Vendor/Client/Other → адресуй Alex'у с готовой
     формулировкой пинка: "Alex, надо тыкнуть Машу — давно не отвечала.
     Черновик: ..."
   - Если ball_with = Agent → адресуй Egor'у (он за AI и PM):
     "Egor, агент <name> завис..."

2. По каждой задаче — постарайся найти конкретный мягкий пинок:
   что бы сделать чтобы сдвинуть. Не общими фразами ("ускорить",
   "продвинуть"), а конкретно ("закрыть хотя бы первый блок",
   "позвонить", "скинуть moodboard").

3. Тон коллега-коллеге, простыми словами, без штампов и канцелярита.
   Каждое сообщение должно отличаться формулировками от предыдущих —
   не используй одни и те же конструкции.

4. Открывай нейтрально: "На данный момент...", "Сейчас висят...",
   "Из открытых задач...". НЕ пиши "по проекту", "по GRN",
   "в текущем проекте" — получатели уже знают про что речь, лишняя
   обвязка раздражает.

5. Имена — жирным (HTML <b>имя</b>). Никаких @username — мы пока не
   собрали Telegram-юзернеймы. Просто жирное имя.

6. Эмодзи — 1-3 на всё сообщение, не больше. Не злоупотребляй.

7. Объём: 80-400 слов. Если задача одна — 80-150 слов хватит.

8. Если задач нет (пустой массив) — короткое нейтральное:
   "Сейчас всё под контролем — нечего пинать."

Формат вывода: чистый HTML-текст готовый к Telegram parse_mode=HTML.
Никаких code-fence обёрток или комментариев — только тело сообщения.
```

### 5.5 Slash-command markdown structure

`/home/team/mams/plugin-scaffold/commands/mams-standup.md` contains:

1. YAML frontmatter: `description`, `argument-hint: [--dry-run]`
2. Brief introduction (one paragraph for human readers)
3. Numbered task list for Claude to execute (mirrors §5.3 algorithm steps)
4. Reference to §5.4 system prompt — embedded verbatim in the slash-command file
5. Notion API filter JSON snippets (so Claude doesn't have to construct them from scratch each invocation)
6. Telegram API call template
7. Activity Log entry template (§5.6)
8. `--dry-run` mode: skip steps that POST to Telegram and write to Activity Log; print proposed message + entry to stdout instead

The slash-command file is the **complete operational spec** for one invocation. Claude follows it like a checklist, no improvisation.

### 5.6 Activity Log entry per invocation

```json
{
  "Entry": "[MAMS] /mams-standup sent to GRN (1 stuck task)",
  "Date": "2026-05-02",
  "Project": "AI & Claude",
  "Who": "Alex",
  "Source": "Cowork",
  "Category": "Note",
  "Details": "Posted to telegram://-5229557142. Grouped by Ball With: Alex:1. message_id=<runtime>. First 200 chars of generated text: <runtime>..."
}
```

`<runtime>` placeholders are filled by Claude at invocation time from the Telegram POST response and the generated message body — they are NOT TODOs in the spec.

---

## 6. Validation contract

After implementation, execute these tests inside the same Claude Code session that built the slash-command (so we can observe the actual messages):

1. **Dry-run test (run first):** `/mams-standup --dry-run` → prints proposed message + Activity Log entry to stdout, NO Telegram POST, NO Notion write. PASS if Alex eyeballs the proposed message and approves tone/content.

2. **Smoke test:** `/mams-standup` → message arrives in `garan ai` group within 30 seconds → Activity Log row visible in Notion. PASS / FAIL.

3. **Tone variance test:** invoke `/mams-standup` 3 times in a row.
   - PASS if: 3 messages have **different opening sentences** AND all 3 mention "Стратегия" or "посыл".
   - FAIL if: messages identical or seed task name missing.

4. **Empty case test:** temporarily set seed task Status to `done` via Notion UI → invoke `/mams-standup` → message says something like "всё под контролем" → revert task Status to `blocked`. PASS / FAIL.

---

## 7. Phase A.1 explicit non-goals

The following are **out of scope** and will not be built/tested in this spec:

- ❌ PM-Director delegation flow (→ Phase A.2 spec)
- ❌ Scheduling (`/schedule` wrapper, cron) (→ Phase B)
- ❌ @-mentions / push notifications via Telegram username (→ Phase B; collect usernames first)
- ❌ Snooze / escalation tone if same task appears 2+ standups (→ Phase B; needs `Last reminder sent at` field)
- ❌ Multi-channel (Slack, email) (→ Phase C)
- ❌ Multi-language (only Russian for now)
- ❌ Image/file attachments to messages
- ❌ Filling out Sprints / Decisions / Risks / Skills DBs (they exist, stay empty)
- ❌ Activating any plugin hook (all hooks remain `disabled: true` in plugin.json)

---

## 8. Phase A.2 stub (next spec, separate session)

PM-Director delegation flow. Briefly: Alex sends task intent → PM creates Task row in Notion (sets `Owner Agent`, `Ball With=Agent`) → invokes corresponding agent passport → agent works → PM updates Task with result + flips `Ball With` back to Alex if review needed → logs to Activity Log. First test case: delegate "Strategy worksheet draft" to `strategist` agent.

Will be specified in `docs/superpowers/specs/YYYY-MM-DD-mams-pm-delegation-design.md`.

---

## 9. Open questions deferred (intentionally not blockers for Phase A.1)

- Should empty-state message still be sent (avoiding notification fatigue) or suppressed when scheduled in Phase B? Defer to Phase B design.
- Telegram message edit-vs-resend if /mams-standup invoked twice within X minutes? Phase B.
- Should PM-Director know about /mams-standup output (i.e. read its own latest standup before suggesting next task)? Phase B.

---

## 10. Implementation checklist (will be expanded by writing-plans skill)

1. Add `Ball With` field to Tasks DB via Notion API (8 select options)
2. Add `Internal Notification Channel` + `Channel Address` fields to Projects Registry via Notion API
3. Backfill: set GRN row → `channel=telegram, address=-5229557142`; set all other 6 existing rows → `channel=none`
4. Fix `NOTION_DB_COMMUNICATION_LOG_ID` in `/home/team/mams/.env` to `ba097004-2960-4b95-be2c-0d76109fe755`
5. Create seed task in Tasks DB ("Стратегия и основной посыл сайта" / Project=GRN / Status=blocked / Priority=P0 / Tier=Amber / Ball With=Alex / Description per §4)
6. Write slash-command markdown at `/home/team/mams/plugin-scaffold/commands/mams-standup.md` per §5.5 structure (system prompt §5.4 embedded verbatim)
7. Run dry-run test (§6.1) → Alex approves proposed message tone
8. Run smoke test (§6.2) → verify message arrives in GRN group
9. Run tone variance test (§6.3)
10. Run empty case test (§6.4)
11. Log Activity Log entry: `[MAMS] Walking-skeleton Phase A.1 shipped`
12. Commit spec + slash-command file to git

---

## 11. Risk register

| Risk | Likelihood | Mitigation |
|---|---|---|
| Notion API rate-limit during multi-DB operations | low | space out calls; Notion limit is 3 req/sec, we do <10 total |
| Notion query + Telegram POST round-trips make /mams-standup feel slow | medium | accept; expect 3-8 sec total per invocation, Bash sequencing is unavoidable |
| Telegram message exceeds 4096 chars | low | system prompt caps at 400 words; even pathological case fits |
| GRN seed task Status=blocked stays Status=blocked forever, message identical-ish each invocation | medium | tone-variance test catches if LLM gets too repetitive; if so, augment prompt with "vary opening" |
| Bot's `rate_limit.py` does NOT apply to direct API calls (we bypass it) | low | walking-skeleton has 1 user (Alex), not a concern at this scale |

---

**End of spec.**
