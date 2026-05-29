#!/usr/bin/env python3
"""
CLI: list-accounts [CODE]

Shows connected social accounts for the given [CODE].
"""
import argparse
import sys

from ghl_client import GHLError, list_accounts, resolve_code


def main() -> int:
    p = argparse.ArgumentParser(description="List GHL social accounts for a [CODE].")
    p.add_argument("code", help="Project code, e.g. GARAN")
    p.add_argument("--json", action="store_true", help="Raw JSON output")
    args = p.parse_args()

    try:
        _, loc, label = resolve_code(args.code)
        accounts = list_accounts(args.code)
    except GHLError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1

    if args.json:
        import json as _json
        _json.dump(accounts, sys.stdout, indent=2)
        print()
        return 0

    print(f"[{args.code.upper()}] {label} — location {loc}")
    print(f"Connected accounts: {len(accounts)}")
    print()
    for a in accounts:
        status = "expired" if a.get("isExpired") else ("deleted" if a.get("deleted") else "ok")
        print(
            f"  {a['platform']:10s} {a.get('type',''):8s} "
            f"{a.get('name',''):30s} [{status}]"
        )
        print(f"    id: {a['id']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
