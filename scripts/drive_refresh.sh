#!/usr/bin/env bash
# Refresh the internal Drive manifest: re-crawl → commit to the private repo.
# `git diff` in that repo IS the drift record (no blob, no separate drift job).
# Zero secrets beyond the local read-only Drive ADC (see scripts/README.md).
#
# Run from the public ds-knowledge-base checkout:  scripts/drive_refresh.sh
# Optionally schedule weekly via launchd/cron.
set -euo pipefail

PUB="$(cd "$(dirname "$0")/.." && pwd)"
PRIV="${KB_INTERNAL_DIR:-$(cd "$PUB/.." && pwd)/ds-knowledge-base-internal}"
PY="${DS_KB_VENV:-$HOME/.config/ds-kb/venv}/bin/python"

[ -x "$PY" ]      || { echo "crawl venv python not found at $PY (see scripts/README.md)"; exit 2; }
[ -d "$PRIV/.git" ] || { echo "private repo not found at $PRIV — clone ds-knowledge-base-internal there"; exit 2; }

GOOGLE_APPLICATION_CREDENTIALS= KB_INTERNAL_DIR="$PRIV" "$PY" "$PUB/scripts/gen_drive_index.py"

cd "$PRIV"
git add drive/
# --porcelain catches new AND modified files (git diff --quiet misses untracked).
if [ -z "$(git status --porcelain -- drive/)" ]; then
  echo "no change — manifest already current."
  exit 0
fi
git commit -q -m "drive-manifest: refresh $(date +%Y-%m-%d)"
git push -q
echo "manifest refreshed + pushed (see git log / diff for the drift)."
