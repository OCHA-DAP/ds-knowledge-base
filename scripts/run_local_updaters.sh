#!/usr/bin/env bash
# Run the ONE KB updater that still can't run in CI: the infra-drift checker
# (infra-drift.yml is dormant until AZURE_CREDENTIALS exists). Uses your local `az` auth,
# commits the advanced baseline, pushes, and maintains the `kb-infra-drift` tracking issue
# via `gh` — i.e. does locally what infra-drift.yml would do in CI.
#
# The pipeline registry is CI's job (pipeline-registry.yml, daily 06:47 UTC, repo PAT
# `DSCI_DATABRICKS_TOKEN`); this script `git pull`s that morning's copy and the drift checker reads
# it. It regenerates the registry itself ONLY AS A FALLBACK — when CI's copy is stale (>30 h) AND
# the local `databricks` OAuth profile happens to be valid — so a dead CI token (2026-08-13 →
# 09-02 went unnoticed; the job now fails red) degrades to "a day late", not "frozen", while an
# expired local login no longer bails the whole run (infra drift included) as it did before 09-02.
# Status of the CI credential: the workspace denies PAT use to ordinary users (`User does not have
# permission to use tokens`) — an admin must grant `dsci` Can-Use on tokens or mint an SP secret.
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
az account show >/dev/null 2>&1   || { log "az not logged in — run: az login"; exit 2; }

# --- always start from a clean, current main -------------------------------------------
# refuse to run off main: committing onto a stray checked-out branch strands the
# artifacts there AND blocks the kb-access ff-only sync (seen 2026-08-11)
BRANCH="$(git branch --show-current)"
[ "$BRANCH" = "main" ] || { log "clone is on '$BRANCH', not main — refusing to run (fix: kb-doctor)"; exit 2; }
git pull --rebase --autostash origin main || { log "git pull failed"; exit 2; }

# --- 1. pipeline registry: comes from CI via the pull above; regenerate locally only as a fallback.
REG_AGE_H=$(( ( $(date +%s) - $(git log -1 --format=%ct -- infrastructure/.pipeline-registry.json) ) / 3600 ))
if [ "$REG_AGE_H" -le 30 ]; then
  log "pipeline registry is ${REG_AGE_H}h old (CI) — not regenerating."
elif command -v databricks >/dev/null && databricks current-user me -p default >/dev/null 2>&1; then
  log "WARN: committed registry is ${REG_AGE_H}h old — CI (pipeline-registry.yml) is not writing it; regenerating locally as fallback."
  DATABRICKS_PROFILE=default "${PY[@]}" scripts/gen_pipeline_registry.py || log "WARN: local registry fallback failed too"
else
  log "WARN: committed registry is ${REG_AGE_H}h old and no local databricks login to fall back on — fix the CI token (DSCI_DATABRICKS_TOKEN) or run: databricks auth login --profile default"
fi

# --- 2. infra drift (Azure + pipelines) ------------------------------------------------
log "checking infra drift…"
"${PY[@]}" scripts/check_infra_drift.py --report /tmp/kb-infra-report.md \
  --update-baseline --emit-new-apps /tmp/kb-new-apps.txt
DRIFT=$?   # 0 = no drift / first run · 2 = drift

# --- chain: for each NEW Azure app, kick the headless-Claude app-ingest GHA -------------
if command -v gh >/dev/null 2>&1 && [ -s /tmp/kb-new-apps.txt ]; then
  while IFS= read -r app || [ -n "$app" ]; do
    [ -z "$app" ] && continue
    log "new app '$app' → dispatching kb-ingest.yml"
    gh workflow run kb-ingest.yml -f kind=app -f target="$app" 2>&1 | sed 's/^/   /' || log "   dispatch failed for $app"
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
        infrastructure/pipeline-registry.md infrastructure/.pipeline-registry.json   # registry only changes on the fallback path
if git diff --staged --quiet; then
  log "no artifact changes — nothing to commit."
else
  git commit -q -m "chore: local updater — advance infra baseline"
  git push -q && log "committed + pushed." || log "push failed (pull/rebase + retry)."
fi
log "done."
