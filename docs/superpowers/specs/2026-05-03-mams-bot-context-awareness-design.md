# MAMS Telegram Bot — Context Awareness (Phase A.3)

**Date:** 2026-05-03
**Author:** Alex (digitalgaran@gmail.com), drafted by Claude Code
**Project (Notion):** AI & Claude (`353326fe-46c5-813d-bbaf-fe2f094691c1`)
**Project code prefix:** `[MAMS]`
**Status:** approved for implementation
**Parallel to:** Phase A.2 (PM delegation) — independent, can ship in any order
**Builds on:** Phase A.1 walking-skeleton (Notion DBs, GRN binding, systemd ecosystem)

---

## 1. Goal

Бот сейчас в группах **отвечает** только на @-mention'ы и reply'и, но также **видит** только их (Telegram bot privacy mode). Все остальные сообщения проходят мимо.

После этой фичи бот:
1. **Видит каждое сообщение** в группах после того как privacy mode выключен в BotFather и бот заново добавлен (в DM ничего не меняется — он и так видит всё)
2. **Хранит только сообщения из проектно-привязанных групп** (`/bind <CODE>` сделан) в JSONL ленте per-chat (append-only, навсегда). DM **не сохраняем** — нет стабильного project-context (Alex может переключать `/project` свободно). Группы без `/bind` тоже не сохраняем — нет проекта вообще.
3. **Перед каждым своим ответом в group-bound чате** читает recent history `с момента последнего своего ответа`, добавляет в Claude prompt как «вот что обсуждалось пока меня не было»

Триггеры ответов **не меняются** — бот по-прежнему отвечает только на @-mention/reply. Меняется качество ответа: теперь учитывает контекст разговора.

### Definition of Done

1. Каждое сообщение в группе `garan ai` (chat -5229557142, привязана к проекту GRN) пишется в `inbox/-5229557142/messages.jsonl` (одна строка per сообщение)
2. **DM с Alex'ом (chat 490844407) НЕ capture'ится** — нет стабильного project-context
3. Файл `state.json` per-group содержит `last_responded_message_id` — обновляется после каждого успешного ответа бота в этой группе
4. При @-mention/reply в group-bound чате бот собирает context block из сообщений `between last_responded и current`, ограниченный 50 сообщ или 6000 симв (что наступит раньше)
5. Context block передаётся в Claude prompt; бот в ответе явно опирается на свежий контекст когда уместно
6. Smoke-test: написать в группе 3 не-mention сообщения «креативы готовы / дизайн поправил / завтра встреча 11 утра», потом @mention «что у нас по статусу?» → ответ бота упоминает все 3 темы

---

## 2. Architecture changes

```
┌──────────────────────────────────────────────────────────────┐
│  on_message(update) — единая точка входа для group + DM      │
│                                                              │
│  STEP A — CAPTURE (всегда, для каждого Update)               │
│    1. Извлечь поля: ts, message_id, from_id, from_name,      │
│       text/caption/media_placeholder, reply_to_message_id    │
│    2. Открыть inbox/<chat_id>/messages.jsonl в режиме 'a'    │
│    3. Сериализовать запись в одну строку JSON, append, flush │
│    4. Закрыть файл                                           │
│    (если шаг A падает по любой причине — логируем warning,   │
│     не прерываем step B)                                     │
│                                                              │
│  STEP B — RESPOND (только если уже было: mention/reply/DM)   │
│    Текущая логика остаётся:                                  │
│    - В DM: отвечает на каждое сообщение от Alex'a            │
│    - В группе: отвечает только если @mentioned или reply     │
│                                                              │
│    Но _process_message() теперь:                             │
│    1. Читает inbox/<chat_id>/state.json → last_responded_id  │
│    2. Читает inbox/<chat_id>/messages.jsonl → recent[]       │
│       filter: message_id > last_responded_id                 │
│              AND message_id != current_message_id            │
│    3. Truncate to last 50 (по message_id desc) ИЛИ <6000     │
│       символов после форматирования (что меньше)              │
│    4. Если recent[] пустой → context_block = "" (как раньше) │
│       Иначе → context_block = format_history(recent)         │
│    5. Передаёт user_prompt = context_block + current_message │
│    6. После Claude reply + успешного TG send →               │
│       обновить state.json: last_responded = current_message_id│
└──────────────────────────────────────────────────────────────┘
```

### Что меняется в файлах кода

| File | Change |
|---|---|
| `bot.py` | Расширить `MessageHandler` filter — добавить voice/video/sticker/audio/animation чтобы capture был полным |
| `handlers.py` | `on_message`: добавить вызов `capture.append(...)` ВСЕГДА (до текущей логики). `_process_message`: добавить чтение history + state, передачу context block в Claude. После reply — `state.update(...)` |
| `claude_bridge.py` | Принимать опциональный `context_block` параметр, инжектить в prompt перед текущим сообщением |
| **NEW** `capture.py` | Новый модуль: `append(chat_id, message)`, `read_recent(chat_id, since_id, cap)`, `update_state(chat_id, last_id)`, `get_state(chat_id)`, `format_for_prompt(messages)` |

Никаких новых зависимостей. Стандартная библиотека Python (`json`, `pathlib`).

---

## 3. Storage layout

```
/home/team/mams/telegram-bot/inbox/
  -5229557142/                    ← chat_id GRN group (привязана через /bind GRN)
    messages.jsonl                 ← append-only, ever-growing
    state.json                     ← {"last_responded_message_id": int, "last_responded_at": "ISO8601"}
  <future_bound_group_chat_id>/   ← новые группы автоматически когда им сделают /bind
    messages.jsonl
    state.json

  490844407/                      ← Alex DM — directory may exist but messages.jsonl
                                     and state.json НЕ создаются (capture skipped per §1)
                                     (other files like downloaded photos могут быть)
```

**Capture-eligible chat:** `chat.type ∈ {GROUP, SUPERGROUP}` AND `project_map.get_group_project(chat.id)` returns non-empty project code. Implemented as `_capture_enabled(chat_type, chat_id)` helper в handlers.py.

### messages.jsonl format

Одна строка JSON per сообщение, encoded UTF-8, no pretty-printing:

```json
{"ts":"2026-05-03T16:42:31.123Z","message_id":331,"from_id":490844407,"from_name":"Alex","text":"@mams что у нас по дизайну?","reply_to":null}
{"ts":"2026-05-03T16:43:05.456Z","message_id":332,"from_id":777111222,"from_name":"Anastasia","text":"я готовлю креативы","reply_to":331}
{"ts":"2026-05-03T16:44:10.789Z","message_id":333,"from_id":888555444,"from_name":"Egor","text":"[photo + caption: вот mockup]","reply_to":null}
```

Поля:
- `ts` — UTC ISO8601 with milliseconds
- `message_id` — Telegram int
- `from_id` — Telegram user_id (int). Бот сам себя НЕ пишет в Phase A (см. §9 Phase B deferred)
- `from_name` — `first_name` + (`last_name`) если есть, fallback `username`, fallback `f"user_{from_id}"`
- `text` — фактический текст ИЛИ caption ИЛИ media placeholder (см. §4)
- `reply_to` — `int message_id` если reply, иначе `null`

### state.json format

```json
{
  "last_responded_message_id": 331,
  "last_responded_at": "2026-05-03T16:42:35.000Z"
}
```

Файл опциональный — если отсутствует, считаем что бот никогда тут не отвечал.

---

## 4. Media placeholder rules

Сообщение без `text` и без `caption` (только медиа) сохраняется с placeholder в поле `text`:

| Тип | Placeholder |
|---|---|
| `photo` без caption | `"[photo]"` |
| `photo` с caption | `"[photo + caption: <caption text>]"` |
| `voice` | `"[voice <duration>s]"` (например `"[voice 12s]"`) |
| `video` | `"[video <duration>s]"` |
| `video_note` ("кружок") | `"[video_note <duration>s]"` |
| `audio` | `"[audio: <title or filename> <duration>s]"` |
| `document` | `"[document: <filename>]"` |
| `sticker` | `"[sticker <emoji>]"` (например `"[sticker 👍]"`) |
| `animation` (gif) | `"[animation]"` |
| Other / unknown | `"[unsupported media]"` |

Placeholder embedded прямо в `text` поле, чтобы format-функция не ветвилась — единое поле для prompt.

`bot.py` filter тоже расширяется чтобы пропускать эти типы:

```python
MessageHandler(
    (filters.TEXT | filters.CAPTION | filters.PHOTO | filters.Document.ALL |
     filters.VOICE | filters.VIDEO | filters.VIDEO_NOTE | filters.AUDIO |
     filters.Sticker.ALL | filters.ANIMATION)
    & ~filters.COMMAND,
    on_message,
)
```

Service messages (member added/left, pinned, etc.) **не пропускаются** filter'ом и не capture'ятся (correct — это шум).

---

## 5. Context block format (для Claude prompt)

```
=== Что обсуждалось в группе с момента моего последнего ответа ===

[16:42 Alex] @mams что у нас по дизайну?
[16:43 Anastasia → Alex] я готовлю креативы
[16:44 Egor] [photo + caption: вот mockup]
[16:45 Alex] а текст для hero уже есть?

=== Конец истории. Ниже — обращение к тебе сейчас: ===

@mams резюмируй что мы обсудили за последние 3 минуты
```

**Формат строки:** `[HH:MM <from_name>] <text>` или `[HH:MM <from_name> → <reply_to_name>] <text>` если reply.

- Время в локальной TZ системы (America/New_York), HH:MM (без секунд, без даты — даты не нужно для recent context)
- `→ <reply_to_name>` извлекается через lookup в той же messages.jsonl: ищем по `reply_to` (message_id) → берём `from_name`. Если не нашли (старое сообщение вне ленты) → пишем просто `[16:43 Anastasia →]` (стрелка без имени).
- Если capture.jsonl truncated (>50 или >6000 chars) — добавляется первая строка: `[пропущено N более старых сообщений]`

**Truncation rule:**
- Берём `recent[]` отсортированные по message_id ASC
- Если `len(recent) > 50` или `total formatted chars > 6000`: оставляем последние 50 / последние ~5000 chars (с запасом на header `[пропущено...]`)
- Header добавляется только если truncation реально произошла

---

## 6. Claude prompt injection

Текущий путь: `claude_bridge.py` → `claude -p <prompt>`. Prompt = system_prompt + user_message.

После: `claude -p <prompt>` где prompt включает (если context_block есть):

```
<existing system prompt>

<existing user_message_handling instructions>

Если в начале user message есть блок «=== Что обсуждалось в группе...
=== Конец истории. ===» — учитывай это как контекст разговора. Отвечай
на сообщение которое идёт ПОСЛЕ блока «Конец истории.», но используя
информацию из блока выше. Не пересказывай контекст в ответе если тебя
явно не просят — просто учитывай.
```

Точная формулировка дополнения system prompt'а будет в `claude_bridge.py`. Само user message:

```
<context_block>

<original user message>
```

Если `context_block` пустой — user message передаётся как раньше (no extra wrapper).

---

## 7. Edge cases

| Случай | Поведение |
|---|---|
| Первый mention в чате (state.json не существует) | `recent[]` = пустой → context block не строится → обычный prompt |
| Бот был перезагружен (рестарт systemd, рестарт WSL) | Работает нормально — state.json + JSONL на диске, не в RAM |
| messages.jsonl отсутствует или пустой | `recent[]` = пустой → как первый mention |
| messages.jsonl повреждён (битая JSON-строка) | Skip битые строки с warning в bot.log, продолжаем с валидными |
| Capture (Step A) падает с exception | Логируем warning в bot.log, продолжаем к Step B (responds work even if capture broken) |
| Concurrent updates (PTB `concurrent_updates=True`) | append + flush на короткой строке атомарен на ext4 — race-condition-free для capture. Для state.json — last write wins (для walking-skeleton ок) |
| Edit message (`edited_message` Update) | **Phase A: ignore** — обновление не записываем. Phase B: добавим update-логику (отдельная строка с `"edit_of": <orig_message_id>`) |
| Бот сам инициирует сообщение (например `/mams-standup`) | **Phase A: НЕ записываем** — бот не получает свои собственные исходящие как Update. Если хотим — можно вручную писать в JSONL после `sendMessage` от standup'а. Голосуем отложить в Phase B |
| Сообщение от другого бота (например, GitHub bot пишет в группу) | Capture'ится как обычное сообщение (`is_bot=true`, но мы это не фильтруем — для контекста это полезно) |
| Сообщение в DM с ботом | **НЕ capture'ится** — нет стабильного project-context. Reason: Alex переключает `/project` свободно, message 5 минут назад мог относиться к другому проекту. |
| Сообщение в группе без /bind | **НЕ capture'ится** — нет проекта вообще. После /bind будущие сообщения начнут capture'иться. |
| Service message (chat_member, pinned, etc.) | Filter'ом не пропускается → не capture'ится |
| Gap > 50 сообщений с прошлого ответа | Берём последние 50, header `[пропущено N старых сообщений]` |
| Gap > 6000 chars текста | Берём последние ~5000 chars, header `[пропущено N старых сообщений]` |
| Reply на сообщение которое было ДО `last_responded_message_id` | Стрелка `→ <name>` отрабатывает (lookup идёт по всей messages.jsonl, не только recent) |

---

## 8. Configuration (.env additions)

```bash
# Maximum messages included in context block (preserves token budget)
MAMS_CONTEXT_MAX_MESSAGES=50

# Maximum characters of formatted context block before truncation
MAMS_CONTEXT_MAX_CHARS=6000
```

Дефолтные значения зашиты в код (`capture.py`), .env переопределяет если присутствует. Обновление .env требует `sudo systemctl restart mams-tg-bot.service` (PTB читает env один раз на старте).

---

## 9. Phase B deferred (для отдельного спека)

- **Compression:** cron-job раз в неделю (или по триггеру `messages.jsonl > 5MB`) агрегирует сообщения старше 30 дней через Claude в `summary_<YYYY-MM>.md` per-chat. Исходные строки в `messages.jsonl` остаются (требование: «храним вечно»). При чтении context block старые сообщения **не подгружаются** — только новые после summary cutoff
- **Edited messages tracking** — обновлять JSONL новой строкой с `"edit_of": <orig_message_id>`
- **Bot's own outbound capture** — при `bot.send_message()` или `/mams-standup` POST вручную писать в JSONL чтобы потом видеть свои исходящие в context
- **Smarter context selection** — не просто «since last_responded», а relevance-based (например для каждого reply подтягивать всю threading цепочку)
- **Multi-day timeline view** — slash command `/mams-history <chat>` показывает свёрнутую timeline за период
- **Privacy mode regression detector** — если за N часов в группе не было ни одного capture'нутого сообщения но бот точно онлайн — алерт что privacy mode мог быть включен обратно

---

## 10. Implementation checklist

1. Создать `src/capture.py` модуль с функциями: `append`, `read_recent`, `get_state`, `update_state`, `format_for_prompt`, `_lookup_name_by_msgid`
2. Расширить `bot.py` filter (добавить voice/video/sticker/audio/animation)
3. Модифицировать `handlers.py`:
   - `on_message`: вызов `capture.append(...)` перед существующей логикой (try/except, не fail-fast)
   - `_process_message`: вызвать `capture.read_recent + format_for_prompt`, передать как `context_block` в `claude_bridge`
   - После успешного reply: `capture.update_state(chat_id, current_message_id)`
4. Модифицировать `claude_bridge.py`:
   - Принимать optional `context_block: str = ""`
   - Если непустой — append к user prompt + расширить system prompt
5. Расширить `.env.example` — добавить 2 новые переменные с комментарием
6. Тест локальный: запустить bot вручную (не через systemd), послать в группе тест-сообщения, проверить что JSONL растёт
7. `sudo systemctl restart mams-tg-bot.service`
8. Smoke test (per Definition of Done #5):
   - Написать в группе 3 не-mention сообщения подряд (без `@mams`)
   - Проверить journalctl что бот их получил и записал в JSONL
   - Написать `@mams резюмируй что обсуждалось`
   - Ожидание: бот в ответе упоминает все 3 предыдущих темы
9. Activity Log entry: `[MAMS] Bot context-awareness Phase A.3 shipped`
10. Commit code changes to git

---

## 11. Validation contract

### Test 1 — Capture works

1. `tail -f /home/team/mams/telegram-bot/inbox/-5229557142/messages.jsonl` (другая SSH-сессия / split tmux)
2. В группе написать «test message 1» (без mention)
3. **PASS:** новая строка появилась в JSONL в течение 2 сек, поля `from_name=Alex`, `text="test message 1"`, `reply_to=null`

### Test 2 — Media placeholder

1. Прислать в группу photo без подписи
2. **PASS:** в JSONL появилась строка с `"text":"[photo]"`
3. Прислать voice 5 секунд
4. **PASS:** строка с `"text":"[voice 5s]"`

### Test 3 — Context-aware response

1. Написать 3 не-mention сообщения подряд: `«креативы готовы»`, `«дизайн поправил»`, `«завтра встреча 11 утра»`
2. Подождать 5 сек
3. Написать `@mams резюмируй что у нас за последние 5 минут`
4. **PASS:** ответ бота упоминает все 3 темы (creatives ready, design fixed, meeting tomorrow at 11) хотя бы implicitly

### Test 4 — State tracking

1. Сразу после Test 3 проверить `cat /home/team/mams/telegram-bot/inbox/-5229557142/state.json`
2. **PASS:** `last_responded_message_id` = message_id от @mams reзюмируй (узнаётся через TG API или просто визуально)

### Test 5 — Truncation

1. Симулировать через ручную правку state.json на очень старый message_id (или посыл 60 сообщений за раз через скрипт)
2. Mention `@mams`
3. **PASS:** в логах `bot.log` видна запись `truncated context: kept 50 of N messages`. В ответе бот при необходимости может упомянуть «много активности было».

### Test 6 — Bot restart preserves state

1. После одного успешного цикла: `sudo systemctl restart mams-tg-bot`
2. Подождать 5 сек
3. Написать ещё одно non-mention сообщение
4. Проверить JSONL — строка добавилась (бот всё ещё пишет)
5. Mention бота
6. **PASS:** ответ учитывает messages между restart и mention (не только до restart)

---

## 12. Risk register

| Risk | Likelihood | Mitigation |
|---|---|---|
| Privacy mode не реально выключен в BotFather | medium | Test 1 вылетит сразу. Если за 2 мин в JSONL ничего нет — re-check BotFather settings + удалить/добавить бота в группу |
| messages.jsonl растёт безгранично | high (in time) | Phase B compression. До тех пор: на одну группу с активностью ~100 msgs/day → ~5 MB/year. Manageable |
| Claude prompt становится длинным → token costs ↑ | medium | CAP 6000 chars (≈1500 токенов) — accept. Если станет проблемой → раньше делать compression |
| Concurrent file writes повреждают JSONL | low | append + flush для коротких строк atomic on ext4. Если когда-то произойдёт — Test «парсим невалидные строки → skip» это ловит |
| Бот падает в Step A → caпture теряет сообщение | low | Step A в try/except. Worst case — пропуск одного сообщения. Не критично |
| Old JSONL без поля `reply_to` (если когда-то упростим schema) | low | Используем `.get('reply_to', None)` — обратная совместимость |
| Edge case: Anastasia/Elena/Egor пока не в группе → их сообщений нет | n/a | Сейчас в группе только Alex. Когда придут — auto-capture начнёт работать |

---

**End of spec.**
