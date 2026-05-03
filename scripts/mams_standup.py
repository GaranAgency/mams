#!/usr/bin/env python3
"""
MAMS /mams-standup — proactive Telegram standup for projects with bound channels.

Reads stuck tasks from Notion Tasks DB (per project that has Internal Notification
Channel = telegram), generates a casual colleague-tone message via headless Claude,
posts to the project's Telegram channel, logs to Notion Activity Log.

Designed to run from systemd timer OR Claude Code slash-command. Idempotent —
each invocation is independent (no state between runs in Phase A.1).

Spec: docs/superpowers/specs/2026-05-02-mams-walking-skeleton-design.md
"""
import argparse
import datetime as dt
import json
import os
import socket
import subprocess
import sys
import urllib.request
import urllib.error
from pathlib import Path

# --- Paths
SECRETS_DIR = Path('/home/team/.claude-secrets')
ENV_FILE = Path('/home/team/mams/.env')
BOT_ENV_FILE = Path('/home/team/mams/telegram-bot/.env')
CLAUDE_BIN = '/home/team/.local/bin/claude'

STALE_DAYS = 3
NOTION_API_BASE = 'https://api.notion.com/v1'
NOTION_VERSION = '2022-06-28'

# --- System prompt for Claude (LLM message generator)
SYSTEM_PROMPT = """Ты пишешь короткое неформальное сообщение в внутреннюю Telegram-группу
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
   - Если ball_with = null или не указан, но в owner_agent есть имя агента
     → адресуй Egor'у про этого агента.
   - Если оба null → адресуй Alex'у про задачу.

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

Если связанные задачи имеют один общий блокер — можешь объединить их
нарративно в один пинок, не обязательно перечислять списком.

Формат вывода: ТОЛЬКО чистый HTML-текст готовый к Telegram parse_mode=HTML.
Никаких code-fence обёрток, комментариев, преамбул, объяснений.
ПЕРВЫЙ символ ответа — первая буква сообщения."""


# --- Helpers
def parse_env_file(path):
    out = {}
    if not path.exists():
        return out
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        k, v = line.split('=', 1)
        out[k.strip()] = v.strip()
    return out


def notion_request(method, url, key, body=None):
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(
        url, method=method, data=data,
        headers={
            'Authorization': f'Bearer {key}',
            'Notion-Version': NOTION_VERSION,
            'Content-Type': 'application/json',
        }
    )
    try:
        return json.loads(urllib.request.urlopen(req).read())
    except urllib.error.HTTPError as e:
        print(f'Notion API error: {e.code} {e.reason}', file=sys.stderr)
        print(e.read().decode(), file=sys.stderr)
        raise


def get_telegram_channel_projects(key, projects_db):
    body = {
        'filter': {'and': [
            {'property': 'Status', 'select': {'equals': '🟢 Active'}},
            {'property': 'Internal Notification Channel', 'select': {'equals': 'telegram'}}
        ]},
        'page_size': 50,
    }
    res = notion_request('POST', f'{NOTION_API_BASE}/databases/{projects_db}/query', key, body)
    out = []
    for p in res['results']:
        info = {'page_id': p['id']}
        for pname, pval in p['properties'].items():
            if pval['type'] == 'title' and pval['title']:
                info['name'] = pval['title'][0]['plain_text']
            if pval['type'] == 'rich_text' and pval['rich_text']:
                txt = pval['rich_text'][0]['plain_text']
                if 'short code' in pname.lower():
                    info['code'] = txt
                if 'channel address' in pname.lower():
                    info['channel_address'] = txt
        if info.get('channel_address'):
            out.append(info)
    return out


def get_stuck_tasks(key, tasks_db, project_id, now):
    body = {
        'filter': {'and': [
            {'property': 'Project', 'relation': {'contains': project_id}},
            {'or': [
                {'property': 'Status', 'select': {'equals': 'in_progress'}},
                {'property': 'Status', 'select': {'equals': 'blocked'}},
                {'property': 'Status', 'select': {'equals': 'review'}},
            ]},
        ]},
        'page_size': 100,
    }
    res = notion_request('POST', f'{NOTION_API_BASE}/databases/{tasks_db}/query', key, body)
    out = []
    for t in res['results']:
        props = t['properties']
        last_edit = dt.datetime.fromisoformat(t['last_edited_time'].replace('Z', '+00:00'))
        days_since = (now - last_edit).total_seconds() / 86400
        status_obj = props.get('Status', {}).get('select')
        status = status_obj['name'] if status_obj else ''
        if not (status in ('blocked', 'review') or (status == 'in_progress' and days_since >= STALE_DAYS)):
            continue
        title_arr = props.get('Name', {}).get('title', [])
        name = title_arr[0]['plain_text'] if title_arr else '(no title)'
        bw_obj = props.get('Ball With', {}).get('select')
        oa_obj = props.get('Owner Agent', {}).get('select')
        due_obj = props.get('Due', {}).get('date')
        # description_lead from page body
        try:
            children = notion_request('GET', f'{NOTION_API_BASE}/blocks/{t["id"]}/children?page_size=5', key)
            description_lead = ''
            for child in children.get('results', []):
                if child.get('type') == 'paragraph':
                    rt = child['paragraph'].get('rich_text', [])
                    if rt:
                        description_lead = ''.join(r.get('plain_text', '') for r in rt)[:200]
                        break
        except Exception:
            description_lead = ''
        out.append({
            'name': name,
            'ball_with': bw_obj['name'] if bw_obj else None,
            'owner_agent': oa_obj['name'] if oa_obj else None,
            'status': status,
            'days_since_update': int(days_since),
            'due': due_obj['start'] if due_obj else None,
            'description_lead': description_lead,
        })
    out.sort(key=lambda x: x['days_since_update'], reverse=True)
    return out


def generate_message(structured_tasks):
    """Call headless claude with system prompt + structured task list."""
    user_input = json.dumps(structured_tasks, ensure_ascii=False, indent=2)
    full_prompt = f"{SYSTEM_PROMPT}\n\n--- Input data:\n{user_input}\n\n--- Generate the message body now:"
    proc = subprocess.run(
        [CLAUDE_BIN, '-p', full_prompt],
        capture_output=True, text=True, timeout=120,
    )
    if proc.returncode != 0:
        raise RuntimeError(f'claude -p failed: rc={proc.returncode}\nstderr={proc.stderr}')
    return proc.stdout.strip()


def post_telegram(bot_token, chat_id, html_text):
    body = {'chat_id': chat_id, 'parse_mode': 'HTML', 'text': html_text}
    req = urllib.request.Request(
        f'https://api.telegram.org/bot{bot_token}/sendMessage',
        method='POST',
        headers={'Content-Type': 'application/json'},
        data=json.dumps(body).encode(),
    )
    try:
        res = json.loads(urllib.request.urlopen(req).read())
    except urllib.error.HTTPError as e:
        print(f'Telegram API error: {e.code} {e.reason}', file=sys.stderr)
        print(e.read().decode(), file=sys.stderr)
        raise
    if not res.get('ok'):
        raise RuntimeError(f'Telegram returned not-ok: {res}')
    return res['result']['message_id']


def write_activity_log(key, activity_db, code, channel_address, n_tasks, ball_grouping, message_id, message_preview, today):
    grouping_str = ', '.join(f'{k}:{v}' for k, v in ball_grouping.items())
    payload = {
        'parent': {'database_id': activity_db},
        'properties': {
            'Entry': {'title': [{'text': {'content': f'[MAMS] /mams-standup sent to {code} ({n_tasks} stuck task{"s" if n_tasks != 1 else ""})'}}]},
            'Date': {'date': {'start': today}},
            'Project': {'rich_text': [{'text': {'content': 'AI & Claude'}}]},
            'Who': {'rich_text': [{'text': {'content': 'Alex'}}]},
            'Source': {'select': {'name': 'Cowork'}},
            'Category': {'select': {'name': 'Note'}},
            'Details': {'rich_text': [{'text': {'content':
                f'Posted to telegram://{channel_address}. Grouped by Ball With: {grouping_str}. message_id={message_id}. Preview: {message_preview[:200]}...'
            }}]}
        }
    }
    return notion_request('POST', f'{NOTION_API_BASE}/pages', key, payload)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry-run', action='store_true', help='Generate message and print, do not POST or log')
    ap.add_argument('--ignore-host-guard', action='store_true', help='Bypass MAMS_CANONICAL_HOSTS check (manual override)')
    args = ap.parse_args()

    # Load creds
    notion_key = (SECRETS_DIR / 'notion.key').read_text().strip()
    env = parse_env_file(ENV_FILE)
    bot_env = parse_env_file(BOT_ENV_FILE)

    # Hostname guard — prevent duplicate runs from a second machine that pulled
    # the repo. Skipped silently with exit 0 so a misconfigured timer doesn't fail loudly.
    canonical_raw = env.get('MAMS_CANONICAL_HOSTS', '').strip()
    if canonical_raw and not args.ignore_host_guard:
        canonical = {h.strip() for h in canonical_raw.split(',') if h.strip()}
        host = socket.gethostname()
        if host not in canonical:
            print(f'Host "{host}" not in MAMS_CANONICAL_HOSTS={sorted(canonical)} — exiting (no-op).')
            return 0

    bot_token = bot_env['TELEGRAM_BOT_TOKEN']
    projects_db = env['NOTION_DB_PROJECTS_REGISTRY_ID']
    tasks_db = env['NOTION_DB_TASKS_ID']
    activity_db = env['NOTION_DB_ACTIVITY_LOG_ID']
    today = dt.date.today().isoformat()
    now = dt.datetime.now(dt.timezone.utc)

    # Step 2: find projects with telegram channel
    projects = get_telegram_channel_projects(notion_key, projects_db)
    if not projects:
        print('No projects with telegram channel configured.')
        return 0

    for proj in projects:
        code = proj.get('code', '?')
        addr = proj['channel_address']
        # Step 3-4: query + filter stuck tasks
        tasks = get_stuck_tasks(notion_key, tasks_db, proj['page_id'], now)
        # Step 5: ball-with grouping
        ball_grouping = {}
        for t in tasks:
            k = t['ball_with'] or 'null'
            ball_grouping[k] = ball_grouping.get(k, 0) + 1
        # Step 6: generate message
        try:
            message = generate_message(tasks)
        except Exception as e:
            print(f'[{code}] message generation failed: {e}', file=sys.stderr)
            continue

        if args.dry_run:
            print('=== DRY-RUN: proposed message ===')
            print(message)
            print('=== DRY-RUN: proposed Activity Log entry ===')
            print(json.dumps({
                'Entry': f'[MAMS] /mams-standup sent to {code} ({len(tasks)} stuck task{"s" if len(tasks) != 1 else ""})',
                'Date': today,
                'Project': 'AI & Claude',
                'Who': 'Alex',
                'Source': 'Cowork',
                'Category': 'Note',
                'Details': f'Posted to telegram://{addr}. Grouped: {ball_grouping}. message_id=<runtime>. Preview: {message[:200]}...'
            }, ensure_ascii=False, indent=2))
            print(f'[{code}] dry-run complete, would post to {addr}')
            continue

        # Step 8: POST to Telegram
        try:
            message_id = post_telegram(bot_token, addr, message)
        except Exception as e:
            print(f'[{code}] Telegram POST failed: {e}', file=sys.stderr)
            continue
        # Step 9: Activity Log
        try:
            write_activity_log(notion_key, activity_db, code, addr, len(tasks), ball_grouping, message_id, message, today)
        except Exception as e:
            print(f'[{code}] sent message_id={message_id} but Activity Log write failed: {e}', file=sys.stderr)
            continue
        grp_str = ', '.join(f'{k}:{v}' for k, v in ball_grouping.items())
        print(f'[{code}] sent message_id={message_id}, {len(tasks)} stuck task{"s" if len(tasks) != 1 else ""} ({grp_str}) · activity-log entry created')


if __name__ == '__main__':
    sys.exit(main() or 0)
