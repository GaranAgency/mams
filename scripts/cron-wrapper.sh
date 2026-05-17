#!/usr/bin/env bash
# cron-wrapper.sh — pre-flight wrapper for cron-driven Claude jobs.
# Ensures /mnt/g is mounted (auto-heals via mnt-g-drvfs.service) before
# running the target script.
#
# Usage: cron-wrapper.sh <path-to-script>
#
# Crontab examples:
#   0 10 * * * /home/team/mams/scripts/cron-wrapper.sh \
#     '/mnt/g/Shared drives/ai/claude-system/sync/sync.sh' \
#     >> /home/team/.claude/sync-logs/cron-sync-stdout.log \
#     2>> /home/team/.claude/sync-logs/cron-sync-stderr.log

set -euo pipefail

TARGET="${1:-}"
[[ -n "$TARGET" ]] || { echo "Usage: $0 <script-path>"; exit 2; }

# cron's PATH lacks ~/.local/bin (age, gh, claude CLI live there). Export here
# so the target script and its children inherit the right environment.
export PATH="$HOME/.local/bin:$PATH"
export USER="${USER:-$(whoami)}"
export HOME="${HOME:-/home/team}"

# 1. Self-heal mount if needed (sudoers grants passwordless start of this svc)
/home/team/mams/scripts/ensure-drive-mounted.sh || {
  echo "$(date -u +%FT%TZ) cron-wrapper: drive mount failed for $TARGET — aborting" >&2
  exit 1
}

# 2. Target lives on the (now-mounted) drive
[[ -f "$TARGET" ]] || {
  echo "$(date -u +%FT%TZ) cron-wrapper: target missing after mount: $TARGET" >&2
  exit 1
}

# 3. Run it
exec /bin/bash "$TARGET"
