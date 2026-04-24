#!/usr/bin/env bash
# MAMS single-file recovery. Drop this on a fresh WSL Ubuntu + Claude Code installed,
# run `bash recovery.sh`, paste age private key when asked — and everything comes back.
#
# Prerequisites on host machine (you do ONCE manually):
#   1. Windows + WSL2 Ubuntu installed, user `team` created
#   2. Google Drive Desktop installed, logged into your account, G: drive visible
#   3. Claude Code CLI installed (`claude --version` works)
#   4. You have the age private key saved in 1Password (or anywhere safe)
#
# Then: download this file (lives at /mnt/g/Shared drives/ai/mams-state-backup/recovery.sh)
#       and run it. Script will:
#   - install apt packages
#   - mount G: (asks sudo)
#   - ask you for age private key (paste 3 lines, Ctrl+D)
#   - decrypt the latest backup, restore .env + Claude Code auth + git creds + memory
#   - git clone mams repo
#   - build Python venv, install bot deps
#   - install systemd services (mnt-g-drvfs + mams-tg-bot)
#   - set up cron auto-backup
#   - report status

set -euo pipefail

# --- config ---
BACKUP_DIR="/mnt/g/Shared drives/ai/mams-state-backup"
MAMS_REPO="https://github.com/GaranAgency/mams.git"
MAMS_DIR="$HOME/mams"
AGE_VERSION="v1.2.0"
AGE_URL="https://github.com/FiloSottile/age/releases/download/${AGE_VERSION}/age-${AGE_VERSION}-linux-amd64.tar.gz"
LOG="/tmp/mams-recovery.log"

log() { echo -e "\n\033[1;36m▸ $*\033[0m" | tee -a "$LOG"; }
ok() { echo -e "  \033[1;32m✓\033[0m $*" | tee -a "$LOG"; }
warn() { echo -e "  \033[1;33m⚠\033[0m $*" | tee -a "$LOG"; }
die() { echo -e "\n\033[1;31m✗ $*\033[0m" | tee -a "$LOG"; exit 1; }

echo "=== MAMS recovery started $(date -u +%FT%TZ) ===" | tee "$LOG"

# --- preflight ---
log "Preflight checks"
[[ "$(whoami)" == "team" ]] || warn "running as $(whoami), not 'team' — paths may differ"
command -v claude >/dev/null || die "Claude Code CLI not found. Install it first (https://docs.anthropic.com/claude-code/installation)"
ok "claude CLI: $(claude --version 2>&1 | head -1)"

# --- install apt packages ---
log "Installing prerequisites (sudo prompt incoming)"
sudo apt update -qq
sudo apt install -y -qq python3-pip python3-venv cron git curl tar
ok "apt packages ready"

# --- install age ---
if command -v age >/dev/null 2>&1; then
  ok "age already installed: $(age --version)"
else
  log "Installing age"
  mkdir -p "$HOME/.local/bin" "$HOME/.age"
  curl -fsSL "$AGE_URL" -o /tmp/age.tgz
  tar xzf /tmp/age.tgz -C /tmp
  mv /tmp/age/age /tmp/age/age-keygen "$HOME/.local/bin/"
  chmod 755 "$HOME/.local/bin/age" "$HOME/.local/bin/age-keygen"
  rm -rf /tmp/age /tmp/age.tgz
  export PATH="$HOME/.local/bin:$PATH"
  grep -q 'HOME/.local/bin' ~/.bashrc 2>/dev/null || \
    echo 'export PATH=$HOME/.local/bin:$PATH' >> ~/.bashrc
  ok "age installed: $(age --version)"
fi
export PATH="$HOME/.local/bin:$PATH"

# --- mount G: if needed ---
if mountpoint -q /mnt/g 2>/dev/null; then
  ok "/mnt/g already mounted"
else
  log "Mounting G: at /mnt/g"
  sudo mkdir -p /mnt/g
  sudo mount -t drvfs G: /mnt/g || die "Could not mount G:. Is Google Drive Desktop running in Windows?"
  ok "/mnt/g mounted"
fi

[[ -d "$BACKUP_DIR" ]] || die "Backup dir not found: $BACKUP_DIR"

# --- prompt for age private key ---
log "Paste your age private key (from 1Password)"
echo "    Expected 3 lines — the full block including '# created:' and 'AGE-SECRET-KEY-...'."
echo "    Paste, then press Enter, then Ctrl+D."
echo ""
mkdir -p "$HOME/.age"
cat > "$HOME/.age/key.txt"
chmod 600 "$HOME/.age/key.txt"

# Validate by regenerating public key
if ! age-keygen -y "$HOME/.age/key.txt" > "$HOME/.age/public.key" 2>/dev/null; then
  die "age key invalid — can't derive public key. Check that you pasted all 3 lines."
fi
PUBKEY=$(cat "$HOME/.age/public.key")
ok "age key loaded, public: ${PUBKEY:0:24}..."

# --- find latest backup ---
log "Looking for latest backup"
LATEST=$(ls -1t "$BACKUP_DIR"/mams-secrets-*.age 2>/dev/null | head -1)
[[ -n "$LATEST" ]] || die "No backup .age files in $BACKUP_DIR"
ok "latest: $(basename "$LATEST")"

# --- decrypt + restore ---
log "Decrypting + restoring"
TMP=$(mktemp -d)
age -d -i "$HOME/.age/key.txt" "$LATEST" > "$TMP/secrets.tar.gz" || die "decryption failed (wrong key?)"
tar xzf "$TMP/secrets.tar.gz" -C "$HOME"
rm -rf "$TMP"
ok "files restored: $(find ~/.mams ~/.git-credentials ~/.claude/settings.json ~/.claude/.credentials.json 2>/dev/null | wc -l) key artefacts"

# --- ensure git uses the restored credentials ---
git config --global credential.helper store 2>/dev/null || true
if [[ -f "$HOME/.gitconfig" ]]; then
  ok ".gitconfig restored"
else
  git config --global user.name "Alex Garan"
  git config --global user.email "digitalgaran@gmail.com"
  git config --global init.defaultBranch main
fi

# --- clone repo ---
if [[ -d "$MAMS_DIR/.git" ]]; then
  ok "repo already cloned at $MAMS_DIR — pulling latest"
  cd "$MAMS_DIR" && git pull --ff-only
else
  log "Cloning MAMS repo"
  git clone "$MAMS_REPO" "$MAMS_DIR" || die "git clone failed (bad PAT in .git-credentials?)"
  ok "repo cloned to $MAMS_DIR"
fi

# --- restore .env files (they were in tarball, placed under $HOME paths) ---
# The tarball contained staging/mams/telegram-bot/.env etc. placed at ~/mams/telegram-bot/.env
# But ~/mams/ was just created by git clone. So the .env from backup may be at ~/mams/telegram-bot/.env already.
# Let's verify:
if [[ -f "$MAMS_DIR/telegram-bot/.env" ]]; then
  ok "$MAMS_DIR/telegram-bot/.env present"
else
  warn "$MAMS_DIR/telegram-bot/.env missing — backup tarball didn't restore here"
fi

# --- build Python venv ---
log "Building Python venv + installing bot deps"
cd "$MAMS_DIR/telegram-bot"
if [[ ! -d .venv ]]; then
  python3 -m venv .venv
fi
.venv/bin/pip install --quiet --upgrade pip
.venv/bin/pip install --quiet -r requirements.txt
ok "venv + deps ready"

# --- install systemd ---
log "Installing systemd services"
if systemctl is-active --quiet mams-tg-bot.service 2>/dev/null; then
  ok "mams-tg-bot.service already active"
else
  bash "$MAMS_DIR/scripts/install-systemd.sh" || warn "systemd install had issues — see above"
fi

# --- cron ---
log "Setting up cron auto-backups"
(crontab -l 2>/dev/null | grep -v "mams/scripts/"; cat <<'EOF'
# MAMS auto-backups
0 3 * * * /home/team/mams/scripts/git-backup.sh
0 4 * * 0 /home/team/mams/scripts/secrets-backup.sh
EOF
) | crontab -
ok "cron installed"

# --- verify ---
log "Verification"
echo ""
echo "▸ bot service:"
systemctl status mams-tg-bot.service --no-pager 2>&1 | head -5 || true
echo ""
echo "▸ /mnt/g mount:"
ls "$BACKUP_DIR" 2>&1 | head -3
echo ""
echo "▸ backup paths ready:"
[[ -f "$HOME/.age/key.txt" ]] && echo "  ✓ age key"
[[ -f "$HOME/.git-credentials" ]] && echo "  ✓ git credentials"
[[ -f "$HOME/.claude/.credentials.json" ]] && echo "  ✓ Claude Code auth"
[[ -f "$MAMS_DIR/telegram-bot/.env" ]] && echo "  ✓ bot .env (tokens)"

echo ""
echo "=== MAMS recovery done $(date -u +%FT%TZ) ==="
echo "Next steps:"
echo "  1. In Telegram, write /start to your bot in DM — should reply"
echo "  2. sudo systemctl status mams-tg-bot  — should be 'active (running)'"
echo "  3. If WSL auto-start not set up on Windows: follow guide in RECOVERY.md"
