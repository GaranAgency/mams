#!/usr/bin/env python3
"""
GHL Social Planner API client with [CODE] routing.

Reads ~/.claude-secrets/<keyfile> at runtime — tokens are NEVER in code/config.
Resolves social account IDs at runtime via the /accounts endpoint, so reconnecting
a platform in GHL doesn't break anything here.
"""
from __future__ import annotations

import json
import os
import sys
import urllib.request
import urllib.error
from pathlib import Path
from typing import Any

API_BASE = "https://services.leadconnectorhq.com"
API_VERSION = "2021-07-28"
SECRETS_DIR = Path.home() / ".claude-secrets"
SKILL_DIR = Path(__file__).resolve().parent.parent
ROUTING_FILE = SKILL_DIR / "config" / "routing.json"


class GHLError(Exception):
    pass


def load_routing() -> dict[str, dict[str, str]]:
    with ROUTING_FILE.open() as f:
        data = json.load(f)
    return {k: v for k, v in data.items() if not k.startswith("_")}


def resolve_code(code: str) -> tuple[str, str, str]:
    """Return (token, location_id, label) for a [CODE]. Raises if unknown."""
    code = code.upper()
    routing = load_routing()
    if code not in routing:
        known = ", ".join(routing.keys()) or "(none)"
        raise GHLError(
            f"Unknown [CODE] '{code}'. Known codes: {known}. "
            f"Add it to {ROUTING_FILE} and put the PIT in "
            f"~/.claude-secrets/ghl-<code>.key (chmod 600)."
        )
    cfg = routing[code]
    keyfile = SECRETS_DIR / cfg["keyfile"]
    if not keyfile.exists():
        raise GHLError(
            f"Token file missing: {keyfile}. Create it (chmod 600) before posting."
        )
    token = keyfile.read_text().strip()
    if not token:
        raise GHLError(f"Token file {keyfile} is empty.")
    return token, cfg["locationId"], cfg.get("label", code)


def _request(
    method: str,
    path: str,
    token: str,
    body: dict[str, Any] | None = None,
) -> dict[str, Any]:
    url = f"{API_BASE}{path}"
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Version", API_VERSION)
    req.add_header("Accept", "application/json")
    if body is not None:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        detail = e.read().decode(errors="replace")
        raise GHLError(f"HTTP {e.code} on {method} {path}: {detail}") from None
    except urllib.error.URLError as e:
        raise GHLError(f"Network error on {method} {path}: {e.reason}") from None


def list_accounts(code: str) -> list[dict[str, Any]]:
    """Fetch live list of connected social accounts for the [CODE]."""
    token, loc, _ = resolve_code(code)
    resp = _request("GET", f"/social-media-posting/{loc}/accounts", token)
    if not resp.get("success"):
        raise GHLError(f"accounts endpoint returned: {resp}")
    return resp.get("results", {}).get("accounts", [])


def resolve_account_ids(
    code: str, platforms: list[str]
) -> tuple[list[str], list[dict[str, Any]]]:
    """
    Map platform names (facebook/instagram/linkedin/...) to live account IDs.
    Returns (account_ids, the matched account dicts).
    """
    wanted = {p.lower() for p in platforms}
    accounts = list_accounts(code)
    matched = [
        a for a in accounts
        if a.get("platform", "").lower() in wanted and not a.get("isExpired")
        and not a.get("deleted")
    ]
    found_platforms = {a["platform"].lower() for a in matched}
    missing = wanted - found_platforms
    if missing:
        raise GHLError(
            f"Platforms not connected (or expired) for [{code.upper()}]: "
            f"{sorted(missing)}. Connected: "
            f"{sorted({a['platform'] for a in accounts})}"
        )
    return [a["id"] for a in matched], matched


def create_post(
    code: str,
    summary: str,
    platforms: list[str],
    media_urls: list[str] | None = None,
    scheduled_at: str | None = None,
    status: str | None = None,
) -> dict[str, Any]:
    """
    Create a Social Planner post.

    - status: defaults to 'draft' when scheduled_at is None, 'scheduled' otherwise.
      Pass 'published' explicitly only after user confirmation.
    - scheduled_at: ISO-8601 string, e.g. '2026-06-01T15:30:00Z'.
    """
    token, loc, _ = resolve_code(code)
    account_ids, _ = resolve_account_ids(code, platforms)

    if status is None:
        status = "scheduled" if scheduled_at else "draft"

    body: dict[str, Any] = {
        "accountIds": account_ids,
        "summary": summary,
        "type": "post",
        "status": status,
    }
    if media_urls:
        body["media"] = [{"url": u, "type": "image"} for u in media_urls]
    if scheduled_at:
        body["scheduleDate"] = scheduled_at

    return _request("POST", f"/social-media-posting/{loc}/posts", token, body)


def dump_post_payload(
    code: str,
    summary: str,
    platforms: list[str],
    media_urls: list[str] | None = None,
    scheduled_at: str | None = None,
    status: str | None = None,
) -> dict[str, Any]:
    """Build the exact body that would be POSTed — for the pre-confirm preview."""
    account_ids, matched = resolve_account_ids(code, platforms)
    if status is None:
        status = "scheduled" if scheduled_at else "draft"
    body: dict[str, Any] = {
        "accountIds": account_ids,
        "summary": summary,
        "type": "post",
        "status": status,
    }
    if media_urls:
        body["media"] = [{"url": u, "type": "image"} for u in media_urls]
    if scheduled_at:
        body["scheduleDate"] = scheduled_at
    return {
        "endpoint": f"POST {API_BASE}/social-media-posting/"
                    f"{resolve_code(code)[1]}/posts",
        "body": body,
        "accounts_resolved": [
            {"platform": a["platform"], "name": a.get("name"), "id": a["id"]}
            for a in matched
        ],
    }


def main() -> int:
    """Small CLI for ad-hoc use: `ghl_client.py accounts GARAN`."""
    if len(sys.argv) < 3 or sys.argv[1] != "accounts":
        print("usage: ghl_client.py accounts <CODE>", file=sys.stderr)
        return 2
    try:
        accs = list_accounts(sys.argv[2])
        json.dump(accs, sys.stdout, indent=2)
        print()
    except GHLError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
