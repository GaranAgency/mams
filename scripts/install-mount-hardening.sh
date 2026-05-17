#!/usr/bin/env bash
# install-mount-hardening.sh — one-shot installer.
# Replaces mnt-g-drvfs.service with the self-healing version and installs
# /etc/sudoers.d/mams-services so cron can re-trigger the mount without password.
# Run as: sudo bash install-mount-hardening.sh

set -euo pipefail

SRC_SVC=/home/team/mams/telegram-bot/systemd/mnt-g-drvfs.service
SRC_SUDO=/home/team/mams/scripts/install-mams-sudoers

DST_SVC=/etc/systemd/system/mnt-g-drvfs.service
DST_SUDO=/etc/sudoers.d/mams-services

[[ $EUID -eq 0 ]] || { echo "Must be run via sudo"; exit 1; }

visudo -cf "$SRC_SUDO"

cp "$SRC_SVC" "$DST_SVC"
install -m 0440 -o root -g root "$SRC_SUDO" "$DST_SUDO"

systemctl daemon-reload
systemctl restart mnt-g-drvfs.service

sleep 2
mountpoint /mnt/g && echo "OK installed; /mnt/g mounted"
