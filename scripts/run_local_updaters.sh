#!/usr/bin/env bash
# Run the secret-dependent KB updaters LOCALLY (the ones whose GHA workflows are dormant
# until org secrets exist): the pipeline registry + health, and the infra-drift checker.
# Uses your local `az` + `databricks` auth instead of CI secrets, commits the regenerated
# artifacts, pushes, and maintains the `kb-infra-drift` tracking issue via `gh` — i.e. it
# does locally exactly what pipeline-registry.yml + infra-drift.yml would do in CI.
#
# The other updaters (drift-check, pdf-freshness, db-schema, refresh-site, framework-sync)
# already run fine in CI and are deliberately NOT duplicated here (running drift-check
# locally too would fight CI over the same kb-drift issue).
#
# Run from the repo:  scripts/run_local_updaters.sh   (or schedule it — see the launchd
# plist scripts/com.ocha.ds-kb.updaters.plist and scripts/README.md).
set -uo pipefail

# launchd/cron run with a bare PATH — make the tools reachable. Adjust if yours differ.
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:$HOME/.local/bin:$PATH"

REPO="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO"
PY=(uv run --with pyyaml python)   # the proven local invocation (pyyaml on demand)
log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"; }

# --- preflight: auth must be live, else bail without clobbering committed artifacts ----
command -v az >/dev/null         || { log "az not found — install/az login"; exit 2; }
command -v databricks >/dev/null || { log "databricks CLI not found"; exit 2; }
az account show >/dev/null 2>&1   || { log "az not logged in — run: az login"; exit 2; }
# the databricks OAuth token EXPIRES; refresh with: databricks auth login --profile default
databricks current-user me -p default >/dev/null 2>&1 \
  || { log "databricks profile 'default' invalid — run: databricks auth login --profile default"; exit 2; }

# --- always start from a clean, current main -------------------------------------------
git pull --rebase --autostash origin main || { log "git pull failed"; exit 2; }

# --- 1. pipeline registry + health -----------------------------------------------------
log "refreshing pipeline registry…"
DATABRICKS_PROFILE=default "${PY[@]}" scripts/gen_pipeline_registry.py \
  || log "WARN: registry gen had errors (auth/token expired?)"

# --- 2. infra drift (Azure + pipelines) ------------------------------------------------
log "checking infra drift…"
"${PY[@]}" scripts/check_infra_drift.py --report /tmp/kb-infra-report.md \
  --update-baseline --emit-new-apps /tmp/kb-new-apps.txt
DRIFT=$?   # 0 = no drift / first run · 2 = drift

# --- chain: for each NEW Azure app, kick the headless-Claude app-ingest GHA -------------
if command -v gh >/dev/null 2>&1 && [ -s /tmp/kb-new-apps.txt ]; then
  while IFS= read -r app; do
    [ -z "$app" ] && continue
    log "new app '$app' → dispatching ingest-app.yml"
    gh workflow run ingest-app.yml -f app="$app" 2>&1 | sed 's/^/   /' || log "   dispatch failed for $app"
  done < /tmp/kb-new-apps.txt
fi

# --- maintain the kb-infra-drift tracking issue (same logic as the workflow) -----------
if command -v gh >/dev/null 2>&1; then
  num="$(gh issue list --label kb-infra-drift --state open --json number --jq '.[0].number' 2>/dev/null)"
  if [ "$DRIFT" -eq 2 ]; then
    gh label create kb-infra-drift --color 1D76DB --description "Deployed estate (Azure/dbx) changed" 2>/dev/null || true
    if [ -n "$num" ]; then
      gh issue edit "$num" --body-file /tmp/kb-infra-report.md && log "updated infra-drift issue #$num"
    else
      gh issue create --title "KB infra drift: deployed estate changed" --label kb-infra-drift \
        --body-file /tmp/kb-infra-report.md && log "opened infra-drift issue"
    fi
  elif [ -n "$num" ]; then
    gh issue comment "$num" --body "✅ No more infra drift — closing." && gh issue close "$num"
    log "closed infra-drift issue #$num"
  fi
else
  log "gh not found — skipping issue tracking (report at /tmp/kb-infra-report.md)"
fi

# --- commit + push the regenerated artifacts -------------------------------------------
git add infrastructure/.infra-baseline.json \
        infrastructure/pipeline-registry.md infrastructure/.pipeline-registry.json
if git diff --staged --quiet; then
  log "no artifact changes — nothing to commit."
else
  git commit -q -m "chore: local updaters — refresh registry + advance infra baseline"
  git push -q && log "committed + pushed." || log "push failed (pull/rebase + retry)."
fi
log "done."
