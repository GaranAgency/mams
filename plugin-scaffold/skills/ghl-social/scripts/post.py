#!/usr/bin/env python3
"""
CLI: post.py [CODE] --text "..." --platforms fb,ig,li [--media URL ...]
             [--schedule "2026-06-01T15:30:00Z"] [--dry-run] [--confirm]

Defaults to dry-run (just prints the payload). Pass --confirm to actually call
the GHL API. Without --schedule the post is created as a draft.

Platform aliases:
  fb / facebook        -> facebook
  ig / insta / instagram -> instagram
  li / linkedin        -> linkedin
"""
import argparse
import json
import sys

from ghl_client import (
    GHLError,
    create_post,
    dump_post_payload,
)

ALIASES = {
    "fb": "facebook", "facebook": "facebook",
    "ig": "instagram", "insta": "instagram", "instagram": "instagram",
    "li": "linkedin", "linkedin": "linkedin",
    "tw": "twitter", "x": "twitter", "twitter": "twitter",
    "tt": "tiktok", "tiktok": "tiktok",
    "gmb": "google", "google": "google",
}


def normalize_platforms(raw: str) -> list[str]:
    out = []
    for token in raw.replace(" ", "").split(","):
        if not token:
            continue
        norm = ALIASES.get(token.lower())
        if not norm:
            raise GHLError(f"Unknown platform alias: {token}")
        if norm not in out:
            out.append(norm)
    if not out:
        raise GHLError("No platforms given.")
    return out


def main() -> int:
    p = argparse.ArgumentParser(description="Create a GHL Social Planner post.")
    p.add_argument("code", help="Project code, e.g. GARAN")
    p.add_argument("--text", required=True, help="Post summary/body")
    p.add_argument(
        "--platforms", required=True,
        help="Comma-separated: fb,ig,li (or facebook,instagram,linkedin)",
    )
    p.add_argument("--media", action="append", default=[],
                   help="Media URL (repeatable). Must already be hosted somewhere reachable.")
    p.add_argument("--schedule", default=None,
                   help="ISO-8601 datetime, e.g. 2026-06-01T15:30:00Z")
    p.add_argument("--status", default=None,
                   choices=["draft", "scheduled", "published"],
                   help="Override status. Default: draft (no schedule) / scheduled (with schedule).")
    g = p.add_mutually_exclusive_group()
    g.add_argument("--dry-run", action="store_true", default=True,
                   help="(default) print payload only, don't call API")
    g.add_argument("--confirm", action="store_true",
                   help="Actually POST to GHL")

    args = p.parse_args()

    try:
        platforms = normalize_platforms(args.platforms)

        preview = dump_post_payload(
            code=args.code,
            summary=args.text,
            platforms=platforms,
            media_urls=args.media or None,
            scheduled_at=args.schedule,
            status=args.status,
        )

        print("=== PAYLOAD PREVIEW ===")
        print(json.dumps(preview, indent=2))
        print("=======================")

        if not args.confirm:
            print("\nDry-run only. Re-run with --confirm to actually post.")
            return 0

        result = create_post(
            code=args.code,
            summary=args.text,
            platforms=platforms,
            media_urls=args.media or None,
            scheduled_at=args.schedule,
            status=args.status,
        )
        print("\n=== GHL RESPONSE ===")
        print(json.dumps(result, indent=2))
        return 0

    except GHLError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
