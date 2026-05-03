---
description: MAMS proactive standup — read Tasks DB, identify stuck tasks per project, generate casual-tone message in-context, post to bound Telegram channel, log to Activity Log. On-demand only.
argument-hint: [--dry-run]
---

# /mams-standup

You are executing the MAMS walking-skeleton standup command. This command reads stuck tasks from Notion, generates a casual colleague-tone message in-context, and posts it to each project's bound Telegram channel. Spec: `docs/superpowers/specs/2026-05-02-mams-walking-skeleton-design.md`.

If `$ARGUMENTS` contains `--dry-run`: do everything EXCEPT the Telegram POST and the Activity Log write — print the proposed message body and the proposed Activity Log entry to stdout instead, so Alex can review.

Today's date: use `date +%Y-%m-%d` from Bash.

---

## Step 1 — Load runtime credentials via Bash

```bash
NOTION_KEY=$(cat ~/.claude-secrets/notion.key)
TG_TOKEN=$(grep '^TELEGRAM_BOT_TOKEN=' /home/team/mams/telegram-bot/.env | cut -d= -f2)
PROJECTS_DB=$(grep '^NOTION_DB_PROJECTS_REGISTRY_ID=' /home/team/mams/.env | cut -d= -f2)
TASKS_DB=$(grep '^NOTION_DB_TASKS_ID=' /home/team/mams/.env | cut -d= -f2)
ACTIVITY_DB=$(grep '^NOTION_DB_ACTIVITY_LOG_ID=' /home/team/mams/.env | cut -d= -f2)
TODAY=$(date +%Y-%m-%d)
```

Don't echo the keys. Just confirm they loaded (non-empty check is enough).

## Step 2 — Query Projects Registry for telegram-bound active projects

POST to `https://api.notion.com/v1/databases/$PROJECTS_DB/query` with this filter body:

```json
{
  "filter": {
    "and": [
      { "property": "Status", "select": { "equals": "🟢 Active" } },
      { "property": "Internal Notification Channel", "select": { "equals": "telegram" } }
    ]
  },
  "page_size": 50
}
```

For each result extract: `page_id`, `Project` (title), `Short Code` (rich_text), `Channel Address` (rich_text). Skip rows where Channel Address is empty.

Today this should return exactly one row: GRN / Garan Agency / `-5229557142`.

## Step 3 — For each qualifying project, query Tasks DB

POST to `https://api.notion.com/v1/databases/$TASKS_DB/query` with this filter body (substitute `<project_page_id>`):

```json
{
  "filter": {
    "and": [
      { "property": "Project", "relation": { "contains": "<project_page_id>" } },
      { "or": [
        { "property": "Status", "select": { "equals": "in_progress" } },
        { "property": "Status", "select": { "equals": "blocked" } },
        { "property": "Status", "select": { "equals": "review" } }
      ]}
    ]
  },
  "page_size": 100
}
```

For each task, extract: `Name` (title), `Status` (select), `Ball With` (select; null if not set), `Owner Agent` (select; null if not set), `last_edited_time` (system field), `Due` (date; null if not set), and the first paragraph of the task's body (page children, type=paragraph) — call this `description_lead`. Truncate description_lead to 200 chars.

## Step 4 — Client-side filter for staleness

```
For each task:
  days_since_update = floor((now - last_edited_time) / 86400)
  if Status in {"blocked", "review"}:
    keep
  elif Status == "in_progress" and days_since_update >= 3:
    keep
  else:
    drop
```

## Step 5 — Build structured task list

For each kept task, build this object:

```json
{
  "name": "<task title>",
  "ball_with": "<Ball With value or 'null'>",
  "owner_agent": "<Owner Agent value or null>",
  "status": "<status>",
  "days_since_update": <integer>,
  "due": "<YYYY-MM-DD or null>",
  "description_lead": "<first 200 chars of page body>"
}
```

Sort by `days_since_update` descending (most stale first).

## Step 6 — Generate Telegram message body in-context

You (Claude) compose the message yourself, following this system prompt exactly:

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

Take the structured task list from Step 5 as your input, produce the message body as your output. Vary the opening sentence each invocation (don't reuse the same opener twice in a row).

Save the message body to a variable, e.g. `MSG_BODY`.

## Step 7 — Branch on --dry-run

**If `--dry-run` was passed:**
- Print to stdout:
  - `=== DRY-RUN: proposed message ===`
  - The MSG_BODY
  - `=== DRY-RUN: proposed Activity Log entry ===`
  - The JSON body of the Activity Log create (Step 9)
- Do NOT execute Steps 8 or 9.
- Print final line: `[<project_code>] dry-run complete, would post to <channel_address>`.

**Otherwise (live mode):** continue to Step 8.

## Step 8 — POST to Telegram

Use Python (more reliable JSON escaping than raw curl for HTML body):

```python
import json, urllib.request
TG_TOKEN = "<from step 1>"
chat_id = "<channel_address>"
text = """<MSG_BODY>"""

req = urllib.request.Request(
    f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage",
    method="POST",
    headers={"Content-Type": "application/json"},
    data=json.dumps({"chat_id": chat_id, "parse_mode": "HTML", "text": text}).encode()
)
res = json.loads(urllib.request.urlopen(req).read())
assert res["ok"] is True, res
message_id = res["result"]["message_id"]
print(message_id)
```

Save `message_id`.

## Step 9 — Write Activity Log entry

POST to `https://api.notion.com/v1/pages` with this body:

```json
{
  "parent": { "database_id": "<ACTIVITY_DB>" },
  "properties": {
    "Entry": { "title": [{ "text": { "content": "[MAMS] /mams-standup sent to <CODE> (<N> stuck tasks)" }}]},
    "Date": { "date": { "start": "<TODAY>" }},
    "Project": { "rich_text": [{ "text": { "content": "AI & Claude" }}]},
    "Who": { "rich_text": [{ "text": { "content": "Alex" }}]},
    "Source": { "select": { "name": "Cowork" }},
    "Category": { "select": { "name": "Note" }},
    "Details": { "rich_text": [{ "text": { "content": "Posted to telegram://<channel_address>. Grouped by Ball With: <Alex:N, Vendor:M, ...>. message_id=<id>. Message preview: <first 200 chars>..." }}]}
  }
}
```

## Step 10 — Report summary line(s) to Alex

For each project processed, print one line to stdout:

```
[GRN] sent message_id=12345, 1 stuck task (Alex:1) · activity-log entry created
```

For dry-run:

```
[GRN] dry-run, would have sent to -5229557142, 1 stuck task (Alex:1)
```

---

## Error handling guidance

- If Notion query returns 0 active+telegram projects → print `no projects with telegram channel configured` and exit 0.
- If a project has 0 stuck tasks → still execute Steps 6/8/9 with empty list → message says "всё под контролем" → Activity Log records 0 stuck tasks.
- If Telegram POST returns non-200 → print error verbatim, do NOT write Activity Log for failed send, do NOT silently swallow. Report to Alex.
- If Activity Log write fails → message was sent, so do NOT retry the message. Print the activity log payload to stdout so Alex can manually create it.

## Reference

Spec: `docs/superpowers/specs/2026-05-02-mams-walking-skeleton-design.md`
GRN chat_id: `-5229557142` (group "garan ai")
Tasks DB: `5006980c-ad06-460d-872d-6de38142b5f2`
Projects Registry DB: `9a9b6c9d-40bd-4d3d-8f99-56ef890a774e`
Activity Log DB: `a8f3ad98-9a8f-4809-996d-cf5441cd5f6a`
