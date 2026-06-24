#!/usr/bin/env bash
# Weekly Drive-manifest drift guard (Phase 7d). Re-crawls the DS team shared
# drive and diffs against the committed manifest; on any change it opens (or
# comments on) a `kb-drive-drift` GitHub issue — it NEVER auto-commits, mirroring
# the Phase-5 drift pattern. A human reruns `gen_drive_index.py` to refresh.
#
# Intended for launchd/cron. Zero secrets: it reuses the local read-only Drive
# ADC (see scripts/README.md → "Drive manifest"). Needs `gh` authenticated.
#
# Manual:  scripts/drive_drift_check.sh
set -euo pipefail

REPO="$(cd "$(dirname "$0")/.." && pwd)"
PY="${DS_KB_VENV:-$HOME/.config/ds-kb/venv}/bin/python"
ISSUE_TITLE="kb-drive-drift"
cd "$REPO"

[ -x "$PY" ] || { echo "venv python not found at $PY (see scripts/README.md)"; exit 2; }

# --check writes nothing; exit 1 == drift, 0 == clean.
set +e
OUT="$(GOOGLE_APPLICATION_CREDENTIALS= "$PY" scripts/gen_drive_index.py --check 2>&1)"
CODE=$?
set -e
echo "$OUT"

[ "$CODE" -eq 0 ] && { echo "no drift — manifest current."; exit 0; }

# Drift: surface it as an issue (dedup on an open one), never edit the manifest here.
BODY=$(printf 'The DS team shared drive has drifted from the last internal manifest (\`drive/drive-index.md\`, gitignored).\n\nRefresh: \x60GOOGLE_APPLICATION_CREDENTIALS= %s scripts/gen_drive_index.py\x60 (rewrites the internal store; nothing to commit).\n\n```\n%s\n```\n' "$PY" "$OUT")
if command -v gh >/dev/null 2>&1; then
  EXISTING=$(gh issue list --state open --search "$ISSUE_TITLE in:title" --json number --jq '.[0].number' 2>/dev/null || true)
  if [ -n "${EXISTING:-}" ]; then
    gh issue comment "$EXISTING" --body "$BODY" >/dev/null && echo "commented on #$EXISTING"
  else
    gh issue create --title "$ISSUE_TITLE" --label kb-drift --body "$BODY" >/dev/null 2>&1 \
      || gh issue create --title "$ISSUE_TITLE" --body "$BODY" >/dev/null   # label may not exist
    echo "opened a $ISSUE_TITLE issue"
  fi
else
  echo "gh not found — drift detected but not reported. Output above."
fi
exit 1
