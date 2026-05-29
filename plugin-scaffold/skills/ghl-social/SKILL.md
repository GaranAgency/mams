---
name: ghl-social
description: Publish, schedule, and draft social-media posts (Facebook, Instagram, LinkedIn, TikTok, X, Google) for agency clients through the GoHighLevel Social Planner API. Use whenever the user asks to post / schedule / draft / cross-post to social, or mentions GHL / GoHighLevel / Social Planner / LeadConnector / Highlevel together with a project code like [GRN] / [MFR] / [KK]. Also use for "publish to FB", "schedule an IG post", "post to LinkedIn", "сделай пост в соцсети", "запланируй публикацию", "выложи в фейсбук". Strict [CODE] routing — each client posts only from its own GHL sub-account, never mixed.
metadata:
  type: integration
  client_routing: required
---

# ghl-social — post to social via GoHighLevel

This skill drives **GHL Social Planner** for agency clients. Each client (grn,
MFR, KK, …) is a separate GHL sub-account with its own PIT (Private Integration
Token). Routing by `[CODE]` is mandatory — you must never publish to one
client's accounts using another client's identity.

## When to use this skill

Use this skill when the user wants to:
- Post / draft / schedule on social media for an agency client
- Cross-post the same content to FB + IG + LinkedIn
- See what social accounts are connected in a client's GHL
- Bulk-schedule a content calendar
- Re-post existing content with edits

**Do NOT use this skill** for:
- Posting from the user's personal social profiles (no GHL there)
- Content that hasn't been approved for that client yet — always confirm
- Replying to comments / DMs (different GHL endpoints, not implemented here)

## Hard rules (read before doing anything)

1. **[CODE] routing is mandatory.** Every command needs a project code
   (`GRN`, `MFR`, `KK`, …). No code → ask. Never assume the default client.
2. **Secrets only in `~/.claude-secrets/ghl-<code>.key`.** Never echo, copy,
   commit, or log the token. The scripts read it at runtime — do not pass it
   on the command line.
3. **Drafts-only by default.** Without an explicit "publish now" from the user,
   a created post must have `status=draft` (so it sits in the GHL UI until a
   human clicks publish). `--confirm` actually sends the API call, but the
   default body produced by `post.py` is a draft unless `--status published`
   was explicitly requested.
4. **Account IDs are resolved at runtime.** Never hardcode them — they change
   when the client reconnects a platform. `ghl_client.py` always calls
   `/accounts` first and maps `platform → accountId`.
5. **One client per command.** No batch over multiple `[CODE]`s in one
   invocation, even if the same text. If the user wants the same post for
   GRN and MFR, run two separate commands.

## Quick map: routing + secrets

| Piece | Where | Secret? |
|---|---|---|
| GHL Private Integration Token | `~/.claude-secrets/ghl-<code>.key` (chmod 600) | yes |
| Location ID + keyfile name | `config/routing.json` | no |
| Social account IDs (FB/IG/LI) | fetched live from GHL on every call | n/a |

## Commands (all via `python3` from the skill's `scripts/` dir)

```bash
SKILL=~/.claude/skills/ghl-social
cd "$SKILL/scripts"
```

### 1) list-accounts — what's connected
```bash
python3 list_accounts.py GRN
# add --json for raw output
```
Shows platform, type, name, status, and the runtime account ID for each
connected channel.

### 2) publish-draft — build a draft, optionally publish

Step A — preview (dry-run is the default, nothing is sent):
```bash
python3 post.py GRN \
  --text "Post body goes here" \
  --platforms fb,ig,li \
  --media https://cdn.example.com/img.jpg
```
This prints the exact endpoint + body + the resolved account IDs.

Step B — actually create. Default status is `draft`:
```bash
python3 post.py GRN \
  --text "Post body goes here" \
  --platforms fb,ig,li \
  --media https://cdn.example.com/img.jpg \
  --confirm
```

Step C — publish immediately (only after user says "yes, post now"):
```bash
python3 post.py GRN \
  --text "..." --platforms fb,ig --media https://... \
  --status published --confirm
```

### 3) schedule-post — same as publish-draft but with a time

```bash
python3 post.py GRN \
  --text "..." \
  --platforms fb,ig,li \
  --media https://... \
  --schedule "2026-06-01T15:30:00Z" \
  --confirm
```
Adding `--schedule` flips the default status to `scheduled`. Time must be
ISO-8601 in UTC (or with explicit offset) and at least ~5 minutes in the
future.

## Platform aliases accepted by `--platforms`

| Input | Resolved to |
|---|---|
| `fb`, `facebook` | facebook |
| `ig`, `insta`, `instagram` | instagram |
| `li`, `linkedin` | linkedin |
| `tw`, `x`, `twitter` | twitter |
| `tt`, `tiktok` | tiktok |
| `gmb`, `google` | google |

Only platforms that are *connected and not expired* in that client's GHL will
succeed; others fail loudly with the list of what's actually connected.

## Workflow you should follow with the user

1. Confirm the `[CODE]` (or pick the only configured one if there's only one).
2. Run `list_accounts.py <CODE>` if you don't already know which platforms are
   live. Mention which are connected.
3. Build the post text. If the user has not given final copy, show your draft
   and wait for approval. Do not invent a final version and post it.
4. Run `post.py` **without** `--confirm` first and show the payload preview.
5. Ask: "ok to send as a draft to GHL?" — wait for yes.
6. Run with `--confirm`. Show the response (post id, status).
7. Log to Notion per the agency workflow (see below).

If the user explicitly says "publish now" / "post live", add
`--status published --confirm` and confirm one more time before running.

## Adding a new client (MFR / KK / future)

1. Get the PIT from that client's GHL sub-account (Settings → Private
   Integrations) with scopes:
   `socialplanner/post.write`, `socialplanner/post.readonly`,
   `socialplanner/account.readonly`, `socialplanner/oauth.readonly`,
   `socialplanner/statistics.readonly`.
2. Save it:
   ```bash
   umask 077
   echo -n "<PIT-TOKEN>" > ~/.claude-secrets/ghl-mfr.key
   chmod 600 ~/.claude-secrets/ghl-mfr.key
   ```
   (Replace `mfr` with the actual lowercase code.) The next nightly
   `secrets-backup.sh` run will pick it up.
3. Get the Location ID from the URL inside that sub-account:
   `app.gohighlevel.com/v2/location/<ID>/...`.
4. Add an entry to `config/routing.json`:
   ```json
   "MFR": {
     "keyfile": "ghl-mfr.key",
     "locationId": "<20-char id>",
     "label": "MFR Construction"
   }
   ```
5. Validate with `python3 list_accounts.py MFR` — must return 200 and a
   non-empty list. 401 = wrong location for that token.

## Integration with the agency workflow

Per the `project-workflow` skill (which see for the canonical rules):

- **Activity Log (Notion)** — log each post that actually leaves the system
  (i.e., a `--confirm` succeeded): `Source=Code`, `Category=Communication`
  if it went out as published/scheduled, `Category=Task Done` if it landed
  in GHL as a draft. Include the GHL post id from the response.
- **Communication Log (Notion)** — every *outgoing* publish (status=published
  or status=scheduled) is an outbound communication; log it with the
  platform(s), the [CODE], and a link to the GHL post if available.
- **Obsidian** — content strategy / cadence notes / what-worked-what-didn't
  go to the client's project folder in the vault, not into this skill.
- Drafts that stay drafts (status=draft, sitting in GHL UI awaiting human
  review) get a *single* Activity Log row when created. Do not double-log
  when the human later publishes from the GHL UI.

## Files in this skill

```
ghl-social/
├── SKILL.md                — this file
├── config/routing.json     — [CODE] -> {keyfile, locationId}, no secrets
├── scripts/
│   ├── ghl_client.py       — API client, token + account resolution
│   ├── list_accounts.py    — list-accounts CLI
│   └── post.py             — publish-draft / schedule-post CLI
└── references/api-notes.md — endpoint shapes, body structure, gotchas
```

When something API-shaped breaks (unexpected status, weird payload error),
read `references/api-notes.md` first — the response shapes and known gotchas
are documented there.
