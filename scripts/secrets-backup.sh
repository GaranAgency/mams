#!/usr/bin/env bash
set -euo pipefail

# MAMS secrets backup: collects ALL sensitive state (env, auth, plugins, memory),
# age-encrypts, uploads to Drive. Runs weekly via cron.
# Recovery: bash recovery.sh  (asks for age private key, restores everything)

export PATH="$HOME/.local/bin:$PATH"
export HOME="${HOME:-/home/team}"

PUBKEY_FILE="$HOME/.age/public.key"
BACKUP_DIR="/mnt/g/Shared drives/ai/mams-state-backup"
WORK_DIR=$(mktemp -d)
STAMP=$(date -u +%Y-%m-%d)
ARCHIVE="mams-secrets-${STAMP}.tar.gz"
ENCRYPTED="mams-secrets-${STAMP}.age"
LOG="$HOME/mams/logs/secrets-backup.log"

mkdir -p "$HOME/mams/logs"
exec >> "$LOG" 2>&1
echo ""
echo "==== $(date -u +%FT%TZ) secrets-backup start ===="

[[ -f "$PUBKEY_FILE" ]] || { echo "ERROR: $PUBKEY_FILE missing"; exit 1; }
[[ -d "$BACKUP_DIR" ]] || { echo "ERROR: $BACKUP_DIR unreachable (drvfs not mounted?)"; exit 1; }

PUBKEY=$(cat "$PUBKEY_FILE")

cd "$WORK_DIR"
mkdir -p staging

# 1. .env files under mams/
find "$HOME/mams" -name ".env" -type f 2>/dev/null | while read -r f; do
  rel=${f#$HOME/}
  mkdir -p "staging/$(dirname "$rel")"
  cp "$f" "staging/$rel"
done

# 2. /home/team/.mams/ — bot bindings, sessions, outbox
if [[ -d "$HOME/.mams" ]]; then
  mkdir -p staging/.mams
  cp -r "$HOME/.mams/." "staging/.mams/" 2>/dev/null || true
fi

# 3. Claude Code auth + config + plugins
mkdir -p staging/.claude/plugins
for f in .credentials.json settings.json settings.local.json mcp-needs-auth-cache.json; do
  [[ -f "$HOME/.claude/$f" ]] && cp "$HOME/.claude/$f" "staging/.claude/$f"
done
for f in installed_plugins.json known_marketplaces.json; do
  [[ -f "$HOME/.claude/plugins/$f" ]] && cp "$HOME/.claude/plugins/$f" "staging/.claude/plugins/$f"
done

# 4. Claude memory (per-project)
for proj_memory in "$HOME/.claude/projects"/*/memory; do
  [[ -d "$proj_memory" ]] || continue
  rel=${proj_memory#$HOME/}
  mkdir -p "staging/$(dirname "$rel")"
  cp -r "$proj_memory" "staging/$rel" 2>/dev/null || true
done

# 5. git-credentials (contains GitHub PAT)
[[ -f "$HOME/.git-credentials" ]] && cp "$HOME/.git-credentials" staging/.git-credentials
if [[ -f "$HOME/.gitconfig" ]]; then
  cp "$HOME/.gitconfig" staging/.gitconfig
fi

# 6. age public key (for reference — private key is required separately via 1Password)
[[ -f "$HOME/.age/public.key" ]] && mkdir -p staging/.age && cp "$HOME/.age/public.key" staging/.age/

# 7. Manifest + version tag
cat > staging/MANIFEST.txt <<EOF
MAMS secrets backup
Date: $(date -u +%FT%TZ)
Host: $(hostname)
User: $USER
Public key: $PUBKEY
Backup format version: 2

Contents (tree from \$HOME):
$(cd staging && find . -type f | sort)

Recovery:
  # Download recovery.sh from Drive (it's unencrypted, next to .age files):
  cp "/mnt/g/Shared drives/ai/mams-state-backup/recovery.sh" ~/
  bash ~/recovery.sh
  # Script will ask for age private key once — that's it.
EOF

# Archive + encrypt
tar czf "$ARCHIVE" -C staging .
age -r "$PUBKEY" -o "$ENCRYPTED" "$ARCHIVE"
echo "archive: $(stat -c%s "$ARCHIVE") bytes → encrypted: $(stat -c%s "$ENCRYPTED") bytes"

# Upload
cp "$ENCRYPTED" "$BACKUP_DIR/$ENCRYPTED"
echo "uploaded: $BACKUP_DIR/$ENCRYPTED"

# Also copy/update recovery.sh on Drive (unencrypted — it has no secrets)
cp "$HOME/mams/scripts/recovery.sh" "$BACKUP_DIR/recovery.sh" 2>/dev/null && \
  echo "refreshed: $BACKUP_DIR/recovery.sh" || \
  echo "NOTE: $HOME/mams/scripts/recovery.sh not found yet"

# Retention: keep last 8 weekly backups
cd "$BACKUP_DIR"
ls -1t mams-secrets-*.age 2>/dev/null | tail -n +9 | while read -r old; do
  rm -f "$old"
  echo "pruned: $old"
done

cd /
rm -rf "$WORK_DIR"
echo "==== $(date -u +%FT%TZ) secrets-backup done ===="
