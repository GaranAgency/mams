#!/usr/bin/env bash
set -euo pipefail

# MAMS secrets backup: collects sensitive state, age-encrypts, uploads to Drive.
# Runs weekly via cron. Recovery: decrypt with ~/.age/key.txt (kept in 1Password).

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

if [[ ! -f "$PUBKEY_FILE" ]]; then
  echo "ERROR: public key missing at $PUBKEY_FILE"
  exit 1
fi

PUBKEY=$(cat "$PUBKEY_FILE")

if [[ ! -d "$BACKUP_DIR" ]]; then
  echo "ERROR: backup dir unreachable: $BACKUP_DIR (is /mnt/g mounted?)"
  exit 1
fi

# Staging directory with structure preserved
cd "$WORK_DIR"
mkdir -p staging

# .env files under mams/
find "$HOME/mams" -name ".env" -type f 2>/dev/null | while read -r f; do
  rel=${f#$HOME/}
  mkdir -p "staging/$(dirname "$rel")"
  cp "$f" "staging/$rel"
done

# /home/team/.mams/ (bindings, sessions, outbox)
if [[ -d "$HOME/.mams" ]]; then
  mkdir -p staging/.mams
  cp -r "$HOME/.mams/." "staging/.mams/" 2>/dev/null || true
fi

# Claude memory (both projects)
for proj_memory in "$HOME/.claude/projects"/*/memory; do
  [[ -d "$proj_memory" ]] || continue
  rel=${proj_memory#$HOME/}
  mkdir -p "staging/$(dirname "$rel")"
  cp -r "$proj_memory" "staging/$rel" 2>/dev/null || true
done

# age identity (circular, but convenient for single-laptop recovery if 1Password lost)
# Encrypted with same key → user still needs key to decrypt. So don't include private key.
# Include ONLY public key for reference.
if [[ -f "$HOME/.age/public.key" ]]; then
  mkdir -p staging/.age
  cp "$HOME/.age/public.key" staging/.age/
fi

# Manifest
cat > staging/MANIFEST.txt <<EOF
MAMS secrets backup
Date: $(date -u +%FT%TZ)
Host: $(hostname)
User: $USER
Public key: $PUBKEY

Contents:
$(cd staging && find . -type f | sort)

Recovery:
  age -d -i ~/.age/key.txt mams-secrets-YYYY-MM-DD.age > extracted.tar.gz
  tar xzf extracted.tar.gz
  # Place files back to their original paths under \$HOME
EOF

# Create archive + encrypt
tar czf "$ARCHIVE" -C staging .
ARCHIVE_SIZE=$(stat -c%s "$ARCHIVE")
echo "archive: $ARCHIVE ($ARCHIVE_SIZE bytes)"

age -r "$PUBKEY" -o "$ENCRYPTED" "$ARCHIVE"
ENCRYPTED_SIZE=$(stat -c%s "$ENCRYPTED")
echo "encrypted: $ENCRYPTED ($ENCRYPTED_SIZE bytes)"

# Upload (copy) to Drive
cp "$ENCRYPTED" "$BACKUP_DIR/$ENCRYPTED"
echo "uploaded: $BACKUP_DIR/$ENCRYPTED"

# Retention: keep last 8 weekly backups (~2 months)
cd "$BACKUP_DIR"
ls -1t mams-secrets-*.age 2>/dev/null | tail -n +9 | while read -r old; do
  rm -f "$old"
  echo "pruned: $old"
done

# Cleanup
cd /
rm -rf "$WORK_DIR"

echo "==== $(date -u +%FT%TZ) secrets-backup done ===="
