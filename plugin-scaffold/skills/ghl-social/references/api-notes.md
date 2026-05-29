# GHL Social Planner API — implementation notes

Endpoint base: `https://services.leadconnectorhq.com`
Required headers on every call:

```
Authorization: Bearer <PIT>
Version: 2021-07-28
Accept: application/json
```

PIT = Private Integration Token for the specific sub-account. Stored in
`~/.claude-secrets/ghl-<code>.key` (chmod 600). Never put it in code or config.

## Endpoints used by this skill

| Purpose | Method | Path |
|---|---|---|
| List connected social accounts | GET | `/social-media-posting/{locationId}/accounts` |
| Create a post (draft / schedule / publish) | POST | `/social-media-posting/{locationId}/posts` |

### accounts response shape
```jsonc
{
  "success": true,
  "results": {
    "accounts": [
      {
        "id": "<ACCOUNT_ID — use this as accountIds[]>",
        "platform": "facebook" | "instagram" | "linkedin" | ...,
        "type": "page" | "profile" | "group",
        "name": "Garan Agency",
        "isExpired": false,
        "deleted": false,
        ...
      }
    ]
  }
}
```

The client refreshes this list on every post — IDs change when a user
reconnects a platform, so caching them is a trap.

### posts request body (what we send)
```jsonc
{
  "accountIds": ["<one or more account IDs from /accounts>"],
  "summary": "Post text body",
  "type": "post",
  "status": "draft" | "scheduled" | "published",
  "media": [{"url": "https://...", "type": "image"}],   // optional
  "scheduleDate": "2026-06-01T15:30:00Z"                // required iff status=scheduled
}
```

GHL accepts media as already-hosted URLs. If you need to upload from a local
file, use the `/medias/upload` endpoint first (not implemented here yet — add
when needed).

## Status semantics

- `draft` — sits in Social Planner, not published, not scheduled. Default
  when no `--schedule` is given. This is the safe default per the workflow:
  Claude builds the draft, the human reviews and publishes from the GHL UI
  (or re-runs with `--status published`).
- `scheduled` — needs `scheduleDate`. Default when `--schedule` is passed.
- `published` — posts immediately. Only do this after explicit user confirmation.

## Gotchas

- 401 "location not accessible" → wrong locationId for this token. The PIT is
  scoped to one sub-account; using it against another location's id fails.
- Instagram requires a media item for image posts (text-only is rejected by IG
  itself, not by GHL). GHL will accept the API call but the post will fail at
  publish time. For IG-only posts always pass `--media`.
- LinkedIn page posts work; personal-profile posts may need `urn` in `meta` —
  see what `/accounts` returns for that channel.
- `scheduleDate` must be in the future (with a small buffer — GHL rejects
  schedules less than ~5 min from now).
