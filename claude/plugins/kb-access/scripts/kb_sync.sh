#!/usr/bin/env bash
# Keep the team KB clone(s) present and fresh. Ships inside the ds-team `kb-access`
# plugin; runs async at SessionStart in every project where the plugin is enabled
# (Claude Code runs hooks through Git Bash on Windows, so one script works everywhere).
#
# Self-bootstrapping: if no clone exists, it clones — so a new teammate needs only the
# plugin, nothing else. Never destructive: a clone that can't fast-forward is left
# untouched and gets a `.kb-sync-stuck` marker (the kb-doctor skill knows the fixes);
# the marker clears itself on the next successful pull.
#
# Clone location — DELIBERATELY no default: nothing is ever cloned to a path the
# user didn't choose. First match wins:
#   1. $KB_REPOS_DIR                  (env; can also come from a repo's settings `env`)
#   2. ~/.claude/.kb-repos-dir        (state file — the explicit per-machine choice)
#   3. an EXISTING clone at ~/OCHA/repos (adopted + recorded, never created)
# If none match, exit without touching the filesystem; the kb-search skill walks the
# user through choosing a location, and the next session start clones there.
set -u

STATE="$HOME/.claude/.kb-repos-dir"
DIR="${KB_REPOS_DIR:-}"
[ -z "$DIR" ] && [ -f "$STATE" ] && DIR="$(head -n1 "$STATE")"
if [ -z "$DIR" ]; then
  if [ -d "$HOME/OCHA/repos/ds-knowledge-base/.git" ]; then
    DIR="$HOME/OCHA/repos"   # pre-plugin machines: adopt the clone that's already there
    mkdir -p "$(dirname "$STATE")" && printf '%s\n' "$DIR" > "$STATE"
  else
    exit 0                   # no location chosen -> do nothing, loudly documented
  fi
fi
PUB="$DIR/ds-knowledge-base"
INT="$DIR/ds-knowledge-base-internal"

mkdir -p "$DIR" 2>/dev/null || exit 0

# Public KB: clone if absent (quiet; a concurrent session's clone-in-progress just
# makes this one fail harmlessly), else ff-only pull with the stuck-marker protocol.
if [ ! -d "$PUB/.git" ]; then
  git clone --quiet --single-branch --branch main \
    "https://github.com/OCHA-DAP/ds-knowledge-base.git" "$PUB" 2>/dev/null || exit 0
  # remember the location — but only when it wasn't a one-off env override
  if [ -z "${KB_REPOS_DIR:-}" ]; then
    mkdir -p "$(dirname "$STATE")" && printf '%s\n' "$DIR" > "$STATE"
  fi
fi
if git -C "$PUB" pull --ff-only --quiet 2>/dev/null; then
  rm -f "$PUB/.kb-sync-stuck"
else
  git -C "$PUB" fetch --quiet 2>/dev/null || true
  behind="$(git -C "$PUB" rev-list --count HEAD..origin/main 2>/dev/null || echo 0)"
  [ "${behind:-0}" -gt 0 ] 2>/dev/null && touch "$PUB/.kb-sync-stuck" || true
fi

# Internal companion: only for users with access — probe via gh, skip silently otherwise.
if [ -d "$INT/.git" ]; then
  git -C "$INT" pull --ff-only --quiet 2>/dev/null || true
elif command -v gh >/dev/null 2>&1 \
  && gh repo view OCHA-DAP/ds-knowledge-base-internal >/dev/null 2>&1; then
  gh repo clone OCHA-DAP/ds-knowledge-base-internal "$INT" \
    -- --quiet --single-branch --branch main >/dev/null 2>&1 || true
fi

exit 0
