#!/usr/bin/env bash
# Run the ONE KB updater that still can't run in CI: the infra-drift checker
# (infra-drift.yml is dormant until AZURE_CREDENTIALS exists). Uses your local `az` auth,
# commits the advanced baseline, pushes, and maintains the `kb-infra-drift` tracking issue
# via `gh` — i.e. does locally what infra-drift.yml would do in CI.
#
# The pipeline registry is NOT generated here any more (since 2026-09-02): pipeline-registry.yml
# runs it daily in CI with the repo's `DSCI_DATABRICKS_TOKEN` PAT (live 2026-08-05; the token then
# died 08-13 → 09-02 unnoticed — the job masked the failure as a warning; now it fails red), so this
# script just `git pull`s that morning's registry (CI 06:47 UTC, this 07:45 local) and the
# drift checker reads it. That removes the only local Databricks dependency — the interactive
# `databricks auth login` OAuth token, whose expiry used to bail the WHOLE run (`exit 2`,
# infra drift included; last seen 2026-09-02).
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

# --- 1. pipeline registry: comes from CI (pipeline-registry.yml, 06:47 UTC) via the pull above.
# Warn, don't bail, if today's CI run hasn't landed — the drift check then compares against
# yesterday's registry, which only means a Databricks change is reported a day late.
REG_AGE_H=$(( ( $(date +%s) - $(git log -1 --format=%ct -- infrastructure/.pipeline-registry.json) ) / 3600 ))
[ "$REG_AGE_H" -le 30 ] || log "WARN: committed pipeline registry is ${REG_AGE_H}h old — check pipeline-registry.yml in CI"

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
git add infrastructure/.infra-baseline.json
if git diff --staged --quiet; then
  log "no artifact changes — nothing to commit."
else
  git commit -q -m "chore: local updater — advance infra baseline"
  git push -q && log "committed + pushed." || log "push failed (pull/rebase + retry)."
fi
log "done."
