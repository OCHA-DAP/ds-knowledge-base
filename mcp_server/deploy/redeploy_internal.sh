#!/usr/bin/env bash
# Redeploy the INTERNAL KB MCP app (chd-ds-kb-mcp-internal) — Oryx zip path.
# Assembly (matches the live app's layout: no KB_ROOT app setting → deploy root IS the KB root):
#   public repo tree (git archive HEAD) + the internal repo's drive/ store merged at drive/
#   + a root requirements.txt (the server's real deps; ocha-stratus pulls the heavy stack).
# Run from the ds-knowledge-base repo root, with ds-knowledge-base-internal cloned alongside
# (or set KB_INTERNAL_DIR). Pull the internal repo first for a fresh Drive store.
set -euo pipefail

RG=IMB-CHD-DataScience-EastUS2
APP=chd-ds-kb-mcp-internal
INTERNAL="${KB_INTERNAL_DIR:-$HOME/OCHA/repos/ds-knowledge-base-internal}"

cd "$(git rev-parse --show-toplevel)"
test -d mcp_server || { echo "run from the ds-knowledge-base repo"; exit 1; }
test -d "$INTERNAL/drive" || { echo "internal repo not found at $INTERNAL (set KB_INTERNAL_DIR)"; exit 1; }

TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

git archive --format=tar HEAD | tar -x -C "$TMP"
cp -R "$INTERNAL/drive" "$TMP/drive"

cp mcp_server/requirements.txt "$TMP/requirements.txt"
grep -q psycopg2 "$TMP/requirements.txt" || echo "psycopg2-binary>=2.9" >> "$TMP/requirements.txt"

(cd "$TMP" && zip -qr app.zip . -x "*.pyc" -x "__pycache__/*")
echo "deploying $(du -h "$TMP/app.zip" | cut -f1) to $APP (Oryx build is slow — stratus stack) …"
az webapp deploy -g "$RG" -n "$APP" --src-path "$TMP/app.zip" --type zip --timeout 900

echo "verify (401 on tools without the bearer = healthy fail-closed boot):"
echo "  python mcp_server/deploy/check_remote.py https://$APP.azurewebsites.net/mcp"
echo "  # internal-tier telemetry appears on next chatbot /private use:"
echo "  # SELECT ts, tier, tool FROM kb_usage.events WHERE tier='internal' ORDER BY ts DESC LIMIT 5;"
