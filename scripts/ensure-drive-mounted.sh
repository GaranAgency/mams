#!/usr/bin/env bash
# ensure-drive-mounted.sh — cron pre-flight wrapper for backup/sync jobs.
#
# Verifies /mnt/g is mounted. If not, triggers the self-healing systemd
# service and waits up to 90s. Exits 0 once mounted, 1 if still not.
#
# Sudoers rule (/etc/sudoers.d/mams-services) lets team systemctl-start
# the mount unit without password.

set -euo pipefail

MOUNT="/mnt/g"
LOG_DIR="$HOME/.claude/sync-logs"
mkdir -p "$LOG_DIR"
LOG="$LOG_DIR/ensure-drive-mounted-$(date +%Y%m%d-%H%M%S).log"
exec >> "$LOG" 2>&1

echo "==== $(date -u +%FT%TZ) ensure-drive-mounted ===="

if mountpoint -q "$MOUNT"; then
  echo "$MOUNT already mounted"
  exit 0
fi

echo "$MOUNT not mounted — kicking mnt-g-drvfs.service"
sudo -n /bin/systemctl start mnt-g-drvfs.service 2>&1 || true

# Service is self-healing (loops); give the first tick up to 90s to land
for i in $(seq 1 9); do
  if mountpoint -q "$MOUNT"; then
    echo "$MOUNT mounted after ${i}0s"
    exit 0
  fi
  sleep 10
done

echo "ERROR: $MOUNT still not mounted after 90s — Google Drive Desktop on Windows likely not running"
exit 1
