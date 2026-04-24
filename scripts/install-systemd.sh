#!/usr/bin/env bash
# One-time install of MAMS systemd units (requires sudo).
# Run: bash /home/team/mams/scripts/install-systemd.sh
set -euo pipefail

REPO=/home/team/mams
UNIT_DIR=$REPO/telegram-bot/systemd

if [[ $EUID -ne 0 ]]; then
  echo "Re-running with sudo..."
  exec sudo -E bash "$0" "$@"
fi

echo "=== installing systemd units ==="
cp $UNIT_DIR/mnt-g-drvfs.service /etc/systemd/system/
cp $UNIT_DIR/mams-tg-bot.service /etc/systemd/system/

systemctl daemon-reload

echo "=== killing old foreground bot process (if any) ==="
pkill -f "src.bot" 2>/dev/null || true
sleep 2

echo "=== enabling & starting services ==="
systemctl enable mnt-g-drvfs.service
systemctl enable mams-tg-bot.service
systemctl start mnt-g-drvfs.service
sleep 2
systemctl start mams-tg-bot.service
sleep 3

echo "=== status ==="
systemctl status mnt-g-drvfs.service --no-pager | head -8
echo ""
systemctl status mams-tg-bot.service --no-pager | head -10
echo ""
echo "=== mount check ==="
ls -la /mnt/g/ 2>&1 | head -3
