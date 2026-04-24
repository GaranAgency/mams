#!/usr/bin/env bash
set -euo pipefail

# MAMS git auto-backup: daily commit + push of /home/team/mams/
# Runs via cron. Skips if nothing to commit.

export HOME="${HOME:-/home/team}"
REPO="$HOME/mams"
LOG="$HOME/mams/logs/git-backup.log"

mkdir -p "$HOME/mams/logs"
exec >> "$LOG" 2>&1
echo ""
echo "==== $(date -u +%FT%TZ) git-backup start ===="

cd "$REPO"

# Stage everything respecting .gitignore
git add -A

if git diff --cached --quiet; then
  echo "no changes to commit"
  echo "==== $(date -u +%FT%TZ) git-backup done (noop) ===="
  exit 0
fi

# Summary of what's being committed
STAT=$(git diff --cached --stat | tail -1)
TS=$(date -u +%FT%TZ)
git commit -m "chore(backup): auto ${TS}" -m "$STAT" || {
  echo "commit failed"
  exit 1
}

# Push
git push origin main || {
  echo "push failed — check credentials"
  exit 1
}

echo "committed + pushed: $STAT"
echo "==== $(date -u +%FT%TZ) git-backup done ===="
