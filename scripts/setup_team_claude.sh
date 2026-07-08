#!/usr/bin/env bash
# One-command Claude Code setup for DS-team members — wires YOUR Claude Code into the KB.
#
#   bash <(gh api repos/OCHA-DAP/ds-knowledge-base/contents/scripts/setup_team_claude.sh \
#          -H "Accept: application/vnd.github.raw")
#   …or, from a clone:  bash scripts/setup_team_claude.sh
#
# Idempotent — RE-RUN ANYTIME to update (pulls both repos + refreshes the org config).
# Does, skipping anything already in place:
#   1. clone ds-knowledge-base (and ds-knowledge-base-internal if your GitHub access allows)
#      under ~/OCHA/repos/
#   2. add the KB pointer block to your ~/.claude/CLAUDE.md (so every Claude Code session
#      knows to search the KB first)
#   3. register the PUBLIC KB MCP connector (user scope — all your projects)
#   4. register the INTERNAL MCP connector (read-only DB/blob + Drive extracts) if the
#      shared token is available (internal repo mcp/internal-token, or az CLI)
set -euo pipefail

REPOS="${KB_REPOS_DIR:-$HOME/OCHA/repos}"
PUB="$REPOS/ds-knowledge-base"
INT="$REPOS/ds-knowledge-base-internal"
MARKER="## Team knowledge base"
step() { printf '\n\033[1m%s\033[0m\n' "$*"; }

command -v gh >/dev/null || { echo "needs the GitHub CLI (brew install gh; gh auth login)"; exit 1; }
command -v claude >/dev/null || { echo "needs Claude Code (https://claude.com/claude-code)"; exit 1; }

step "1/4 repos → $REPOS  (re-running = refresh)"
mkdir -p "$REPOS"
if [ -d "$PUB/.git" ]; then
  git -C "$PUB" pull --ff-only --quiet 2>/dev/null && echo "  ds-knowledge-base: updated" \
    || echo "  ds-knowledge-base: present (local changes — not touched)"
else
  gh repo clone OCHA-DAP/ds-knowledge-base "$PUB" -- --quiet
fi
if [ -d "$INT/.git" ]; then
  git -C "$INT" pull --ff-only --quiet 2>/dev/null && echo "  ds-knowledge-base-internal: updated" \
    || echo "  ds-knowledge-base-internal: present (local changes — not touched)"
elif gh repo view OCHA-DAP/ds-knowledge-base-internal >/dev/null 2>&1; then
  gh repo clone OCHA-DAP/ds-knowledge-base-internal "$INT" -- --quiet
else
  echo "  ds-knowledge-base-internal: no access (ask for OCHA-DAP org membership) — skipping"
fi
# org-wide config: refresh ~/.claude/CLAUDE.dsci.md from ds-claude-config when it's in use,
# so the team config stops drifting per-machine
if [ -f "$HOME/.claude/CLAUDE.dsci.md" ]; then
  if gh api repos/OCHA-DAP/ds-claude-config/contents/CLAUDE.dsci.md \
       -H "Accept: application/vnd.github.raw" > "$HOME/.claude/CLAUDE.dsci.md.new" 2>/dev/null \
     && [ -s "$HOME/.claude/CLAUDE.dsci.md.new" ]; then
    mv "$HOME/.claude/CLAUDE.dsci.md.new" "$HOME/.claude/CLAUDE.dsci.md"
    echo "  CLAUDE.dsci.md: refreshed from ds-claude-config"
  else
    rm -f "$HOME/.claude/CLAUDE.dsci.md.new"
  fi
fi

step "2/4 global pointer → ~/.claude/CLAUDE.md"
mkdir -p "$HOME/.claude"
# the org-wide config (ds-claude-config's CLAUDE.dsci.md) now carries the KB pointer too —
# skip if it's present there (directly or via the common @import) to avoid a duplicate block
if grep -qsF "$MARKER" "$HOME/.claude/CLAUDE.md" 2>/dev/null \
   || grep -qsF "$MARKER" "$HOME/.claude/CLAUDE.dsci.md" 2>/dev/null; then
  echo "  pointer already present (directly or via the org config)"
else
  cat >> "$HOME/.claude/CLAUDE.md" <<EOF

$MARKER

The DS team knowledge base lives at \`$PUB/\`. It is the shared home for our
methods, past frameworks, pipeline runbooks, and infra conventions.

- Before answering team-knowledge questions (how a framework/trigger works, what feeds a
  pipeline, blob/DB conventions, past decisions), **search the KB first** — grep/read it
  rather than answering from memory.
- It's organized as \`frameworks/\`, \`pipelines/\`, \`apps/\`, \`analysis/\`, \`methods/\`,
  \`infrastructure/\`, \`assets/\`. Follow each page's \`code_ref\`/\`source_repo\` into the
  actual repo for depth. Internal-sourced material (Drive extracts, style-reference mirror)
  is in \`$INT/\`.
- After completing framework or pipeline work, update the affected KB page
  (capture-as-you-go). The repo's own CLAUDE.md first, the KB summary second.
- To change the KB: open an issue on OCHA-DAP/ds-knowledge-base — the steward drafts it
  as a PR (see infrastructure/automation.md).
EOF
  echo "  pointer appended"
fi

step "3/4 public KB MCP connector (user scope)"
if claude mcp list 2>/dev/null | grep -q "chd-ds-kb-mcp.azurewebsites.net"; then
  echo "  already registered"
else
  claude mcp add --scope user --transport http ds-kb "https://chd-ds-kb-mcp.azurewebsites.net/mcp"
fi

step "4/4 internal KB MCP connector (DB/blob/Drive — token-gated)"
if claude mcp list 2>/dev/null | grep -q "chd-ds-kb-mcp-internal"; then
  echo "  already registered"
else
  TOKEN=""
  if [ -f "$INT/mcp/internal-token" ]; then
    TOKEN="$(tr -d '[:space:]' < "$INT/mcp/internal-token")"
  elif command -v az >/dev/null 2>&1; then
    TOKEN="$(az webapp config appsettings list -g IMB-CHD-DataScience-EastUS2 \
      -n chd-ds-kb-mcp-internal --query "[?name=='KB_MCP_STATIC_TOKEN'].value" -o tsv 2>/dev/null || true)"
  fi
  if [ -n "$TOKEN" ]; then
    claude mcp add --scope user --transport http ds-kb-internal \
      "https://chd-ds-kb-mcp-internal.azurewebsites.net/mcp" \
      --header "Authorization: Bearer $TOKEN"
    echo "  registered"
  else
    echo "  token not found (needs internal-repo access w/ mcp/internal-token, or az login) — skipped."
    echo "  The public connector + local clones cover most use; ask a maintainer for the token to add later."
  fi
fi

printf '\n\033[1mDone.\033[0m Try: claude → "what is the trigger for the Chad drought framework?"\n'
