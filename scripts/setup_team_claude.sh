#!/usr/bin/env bash
# One-command Claude Code setup for DS-team members — wires YOUR Claude Code into the KB.
#
#   bash <(gh api repos/OCHA-DAP/ds-knowledge-base/contents/scripts/setup_team_claude.sh \
#          -H "Accept: application/vnd.github.raw")
#   …or, from a clone:  bash scripts/setup_team_claude.sh
#   Remove everything it configured (clones are kept):  … setup_team_claude.sh --uninstall
#
# Idempotent — re-run anytime; it repairs/refreshes whatever it previously set up.
# Clone location is configurable per machine: KB_REPOS_DIR=/your/dir bash … (the choice
# is remembered in ~/.claude/.kb-repos-dir for later runs and for the kb-doctor skill).
#
# What it does:
#   1. clone ds-knowledge-base (+ ds-knowledge-base-internal if your GitHub access allows)
#   2. add ONE @import line to ~/.claude/CLAUDE.md → the team config (claude/CLAUDE.dsci.md)
#      loads straight from the clone — always current main, no copies to go stale.
#      Migrates away the legacy setup (old pointer block + ~/.claude/CLAUDE.dsci.md copy).
#   3. link the team skills (claude/skills/ → ~/.claude/skills/ds-team, listed as ds-team:*)
#   4. install an async SessionStart hook that pulls both clones whenever a Claude Code
#      session starts (zero startup delay; Windows runs hooks through Git Bash, so the same
#      hook works everywhere). A clone that can't fast-forward gets a .kb-sync-stuck marker
#      so Claude can warn the user instead of the KB rotting silently.
#
# MCP connectors are deliberately NOT registered: with a fresh local clone, Claude Code
# always prefers local grep. The connectors remain for claude.ai / no-clone use — docs/USING.md.
set -euo pipefail

STATE="$HOME/.claude/.kb-repos-dir"
if [ -n "${KB_REPOS_DIR:-}" ]; then REPOS="$KB_REPOS_DIR"
elif [ -s "$STATE" ]; then REPOS="$(head -1 "$STATE")"
else REPOS="$HOME/OCHA/repos"; fi
PUB="$REPOS/ds-knowledge-base"
INT="$REPOS/ds-knowledge-base-internal"
IMPORT_LINE="@$PUB/claude/CLAUDE.dsci.md"
LEGACY_MARKER="## Team knowledge base"
SKILLS_LINK="$HOME/.claude/skills/ds-team"
step() { printf '\n\033[1m%s\033[0m\n' "$*"; }

PY="$(command -v python3 || command -v python || true)"
[ -n "$PY" ] || { echo "needs python (3.x) on PATH"; exit 1; }

# ---------------------------------------------------------------- uninstall
if [ "${1:-}" = "--uninstall" ]; then
  step "uninstall (clones under $REPOS are kept)"
  "$PY" - "$PUB" <<'PYEOF'
import json, os, sys

pub = sys.argv[1]
# hook
sp = os.path.expanduser("~/.claude/settings.json")
if os.path.exists(sp):
    try:
        with open(sp, encoding="utf-8") as f:
            cfg = json.load(f)
        groups = cfg.get("hooks", {}).get("SessionStart", [])
        kept = [g for g in groups
                if not any("ds-knowledge-base" in h.get("command", "")
                           for h in g.get("hooks", []))]
        if len(kept) != len(groups):
            if kept:
                cfg["hooks"]["SessionStart"] = kept
            else:
                cfg["hooks"].pop("SessionStart", None)
                if not cfg["hooks"]:
                    cfg.pop("hooks", None)
            with open(sp, "w", encoding="utf-8") as f:
                json.dump(cfg, f, indent=2)
                f.write("\n")
            print("  hook removed")
    except ValueError:
        print("  ~/.claude/settings.json unparseable — hook not touched")
# import line + legacy block
cm = os.path.expanduser("~/.claude/CLAUDE.md")
if os.path.exists(cm):
    with open(cm, encoding="utf-8") as f:
        lines = f.read().splitlines(keepends=True)
    out, skip = [], False
    for ln in lines:
        s = ln.strip()
        if s.startswith("## "):
            skip = s == "## Team knowledge base"
        if skip or s.rstrip("/").endswith("ds-knowledge-base/claude/CLAUDE.dsci.md"):
            continue
        out.append(ln)
    if out != lines:
        with open(cm, "w", encoding="utf-8") as f:
            f.writelines(out)
        print("  ~/.claude/CLAUDE.md: import/pointer removed")
PYEOF
  if [ -L "$SKILLS_LINK" ]; then rm "$SKILLS_LINK"; echo "  skills link removed"
  elif [ -d "$SKILLS_LINK" ]; then rm -rf "$SKILLS_LINK"; echo "  skills copy removed"; fi
  rm -f "$STATE"
  printf '\n\033[1mUninstalled.\033[0m Clones left at %s — delete them yourself if wanted.\n' "$REPOS"
  exit 0
fi

command -v gh >/dev/null || { echo "needs the GitHub CLI (brew install gh; gh auth login)"; exit 1; }
command -v claude >/dev/null || { echo "needs Claude Code (https://claude.com/claude-code)"; exit 1; }

step "1/4 repos → $REPOS  (re-running = refresh; KB_REPOS_DIR overrides)"
mkdir -p "$REPOS" "$HOME/.claude"
printf '%s\n' "$REPOS" > "$STATE"
if [ -d "$PUB/.git" ]; then
  git -C "$PUB" pull --ff-only --quiet 2>/dev/null && echo "  ds-knowledge-base: updated" \
    || echo "  ds-knowledge-base: present (local changes — not touched)"
else
  gh repo clone OCHA-DAP/ds-knowledge-base "$PUB" -- --quiet
  echo "  ds-knowledge-base: cloned"
fi
if [ -d "$INT/.git" ]; then
  git -C "$INT" pull --ff-only --quiet 2>/dev/null && echo "  ds-knowledge-base-internal: updated" \
    || echo "  ds-knowledge-base-internal: present (local changes — not touched)"
elif gh repo view OCHA-DAP/ds-knowledge-base-internal >/dev/null 2>&1; then
  gh repo clone OCHA-DAP/ds-knowledge-base-internal "$INT" -- --quiet
  echo "  ds-knowledge-base-internal: cloned"
else
  echo "  ds-knowledge-base-internal: no access (ask for OCHA-DAP org membership) — skipping"
fi

step "2/4 team config import → ~/.claude/CLAUDE.md  (one line; content rides the clone)"
"$PY" - "$IMPORT_LINE" <<'PYEOF'
import os, sys

imp = sys.argv[1]
cm = os.path.expanduser("~/.claude/CLAUDE.md")
lines = []
if os.path.exists(cm):
    with open(cm, encoding="utf-8") as f:
        lines = f.read().splitlines(keepends=True)
out, skip, changed = [], False, False
for ln in lines:
    s = ln.strip()
    if s.startswith("## "):
        skip = s == "## Team knowledge base"          # legacy appended pointer block
        if skip:
            changed = True
    if skip:
        continue
    if s == "@~/.claude/CLAUDE.dsci.md":              # legacy copy import
        changed = True
        continue
    out.append(ln)
if imp not in (ln.strip() for ln in out):
    out.insert(0, imp + "\n")
    changed = True
if changed or not os.path.exists(cm):
    with open(cm, "w", encoding="utf-8") as f:
        f.writelines(out)
    print("  import line ensured; legacy pointer/import cleaned up")
else:
    print("  already in place")
old = os.path.expanduser("~/.claude/CLAUDE.dsci.md")
if os.path.exists(old):
    os.remove(old)
    print("  legacy ~/.claude/CLAUDE.dsci.md copy removed (content now lives in the clone)")
PYEOF

step "3/4 team skills → ~/.claude/skills/ds-team  (listed as ds-team:*)"
mkdir -p "$HOME/.claude/skills"
case "$(uname -s)" in MINGW*|MSYS*|CYGWIN*) WIN=1 ;; *) WIN=0 ;; esac
if [ "$WIN" = 0 ]; then
  [ -L "$SKILLS_LINK" ] && rm "$SKILLS_LINK"
  if [ -e "$SKILLS_LINK" ]; then
    echo "  $SKILLS_LINK exists and is not a symlink — move it aside and re-run"
  else
    ln -s "$PUB/claude/skills" "$SKILLS_LINK"
    echo "  linked (auto-updates with the clone)"
  fi
else
  mkdir -p "$SKILLS_LINK"
  cp -R "$PUB/claude/skills/." "$SKILLS_LINK/"
  echo "  copied (Windows — the session hook re-copies after each pull)"
fi

step "4/4 auto-refresh hook (pulls both clones at every Claude Code session start)"
# async: zero startup delay. ff-only + silenced: a dirty/diverged clone is never clobbered —
# but then a .kb-sync-stuck marker is dropped so Claude tells the user instead of rotting silently.
PULL_PUB="git -C \"$PUB\" pull --ff-only --quiet 2>/dev/null && rm -f \"$PUB/.kb-sync-stuck\" || { git -C \"$PUB\" fetch --quiet 2>/dev/null || true; [ \"\$(git -C \"$PUB\" rev-list --count HEAD..origin/main 2>/dev/null || echo 0)\" -gt 0 ] && touch \"$PUB/.kb-sync-stuck\" || true; }"
COPY_SKILLS=""
[ "$WIN" = 1 ] && COPY_SKILLS="cp -R \"$PUB/claude/skills/.\" \"$SKILLS_LINK/\" 2>/dev/null || true; "
HOOK_CMD="$PULL_PUB; git -C \"$INT\" pull --ff-only --quiet 2>/dev/null; ${COPY_SKILLS}exit 0"
"$PY" - "$HOOK_CMD" <<'PYEOF'
import json, os, sys

cmd = sys.argv[1]
path = os.path.expanduser("~/.claude/settings.json")
cfg = {}
if os.path.exists(path):
    try:
        with open(path, encoding="utf-8") as f:
            cfg = json.load(f)
    except ValueError:
        print("  ~/.claude/settings.json is not valid JSON — fix it, then re-run (skipped)")
        sys.exit(0)
groups = cfg.setdefault("hooks", {}).setdefault("SessionStart", [])
kept = [g for g in groups
        if not any("ds-knowledge-base" in h.get("command", "")
                   for h in g.get("hooks", []))]
refreshed = len(kept) != len(groups)
kept.append({"hooks": [{"type": "command", "command": cmd, "async": True,
                        "timeout": 120, "statusMessage": "Refreshing team KB"}]})
cfg["hooks"]["SessionStart"] = kept
with open(path, "w", encoding="utf-8") as f:
    json.dump(cfg, f, indent=2)
    f.write("\n")
print("  hook " + ("refreshed" if refreshed else "installed") + " — KB clones now self-update")
PYEOF

printf '\n\033[1mDone.\033[0m From your next session: team config + ds-team:* skills load from the clone,\n'
printf 'which refreshes itself at every session start. Try: claude → "what is the trigger for\n'
printf 'the Chad drought framework?" · Health check anytime: ask Claude to run kb-doctor.\n'
