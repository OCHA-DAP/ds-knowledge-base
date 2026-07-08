#!/usr/bin/env bash
# Redeploy the PUBLIC KB MCP app (chd-ds-kb-mcp) from the current main — Oryx zip path
# (same recipe as DEPLOY.md § "Deployed instance"). Run BY A HUMAN from the repo root.
#
# Why you'd run this: the box only serves what was in the zip at deploy time — e.g. the
# usage-telemetry middleware (#105) does nothing until the code containing it is deployed.
#
# The INTERNAL app (chd-ds-kb-mcp-internal) is NOT touched: its zip bundles the internal
# Drive store, so redeploy it from wherever that assembly was done (see mcp-connectors.md).
set -euo pipefail

RG=IMB-CHD-DataScience-EastUS2
APP=chd-ds-kb-mcp

cd "$(git rev-parse --show-toplevel)"
test -d mcp_server || { echo "run from the ds-knowledge-base repo"; exit 1; }

TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

# clean tree of HEAD (no .git, no venv, no local junk); include raw/ (small, useful to code-nav)
git archive --format=tar HEAD | tar -x -C "$TMP"

# root requirements.txt for the Oryx build = the server's REAL requirements file (plus the
# psycopg2 driver for the usage middleware). Never inline a separate list here — an inline
# copy silently bypassed the fastmcp<3.4.3 pin and 421'd the live box (2026-07-07/08).
cp mcp_server/requirements.txt "$TMP/requirements.txt"
grep -q psycopg2 "$TMP/requirements.txt" || echo "psycopg2-binary>=2.9" >> "$TMP/requirements.txt"

(cd "$TMP" && zip -qr app.zip . -x "*.pyc" -x "__pycache__/*")
echo "deploying $(du -h "$TMP/app.zip" | cut -f1) to $APP …"
az webapp deploy -g "$RG" -n "$APP" --src-path "$TMP/app.zip" --type zip

echo "verify:"
echo "  python mcp_server/deploy/check_remote.py https://$APP.azurewebsites.net/mcp"
echo "  # then: SELECT ts, tier, tool FROM kb_usage.events ORDER BY ts DESC LIMIT 5;"
