#!/usr/bin/env bash
# Keep the team KB clone(s) present and fresh. Ships inside the ds-team `kb-access`
# plugin; runs async at SessionStart in every project where the plugin is enabled
# (Claude Code runs hooks through Git Bash on Windows, so one script works everywhere).
#
# Self-bootstrapping: if no clone exists, it clones — so a new teammate needs only the
# plugin, nothing else. Never destructive: a clone that can't fast-forward is left
# untouched and gets a `.kb-sync-stuck` marker (the kb-doctor skill knows the fixes);
# the marker clears itself on the next successful pull. The internal companion gets
# the same protocol, plus a marker when GitHub answers for the public clone but
# refuses the private one (D123).
#
# Clone location — DELIBERATELY no default and no auto-detection: this script only
# ever acts on a location the user explicitly set. First match wins:
#   1. $KB_REPOS_DIR                  (env; can also come from a repo's settings `env`)
#   2. ~/.claude/.kb-repos-dir        (state file — the explicit per-machine choice)
# If neither is set, exit without touching the filesystem; the kb-search skill walks
# the user through choosing (an existing clone anywhere is picked up by pointing the
# state file at its parent dir), and the next session start takes it from there.
set -u

STATE="$HOME/.claude/.kb-repos-dir"
DIR="${KB_REPOS_DIR:-}"
[ -z "$DIR" ] && [ -f "$STATE" ] && DIR="$(head -n1 "$STATE")"
[ -z "$DIR" ] && exit 0      # no location chosen -> do nothing, loudly documented
PUB="$DIR/ds-knowledge-base"
INT="$DIR/ds-knowledge-base-internal"

# Sync outcomes also land in the shared activity log (see kb_activity.sh, D96/D112),
# stamped <project>/<session8> like every other line so concurrent session starts
# stay attributable and a column filter works on SYNC lines too.
ALOG="$HOME/.claude/ds-team-activity.log"
# SessionStart payload: session_id + cwd. Guarded on a TTY so a hand-run of this
# script can never block waiting for input it will not get.
HOOKJSON=""; [ -t 0 ] || HOOKJSON="$(cat 2>/dev/null || true)"
sfield() { # first "<key>": "<value>" from the payload ("" if absent)
  local r="${HOOKJSON#*\"$1\"}"
  [ "$r" = "$HOOKJSON" ] && return 0
  r="${r#*:}"; r="${r# }"
  case "$r" in \"*) r="${r#\"}"; printf '%s' "${r%%\"*}" ;; esac
}
SID="$(sfield session_id)"
SCWD="$(sfield cwd)"
STAMP="${SCWD##*/}/${SID:0:8}"
slog() {
  printf '\033[2m%s %s\033[0m \033[33m%-6s\033[0m %s\n' \
    "$(date '+%H:%M:%S')" "$STAMP" SYNC "$1" >> "$ALOG" 2>/dev/null || true
}

mkdir -p "$DIR" 2>/dev/null || exit 0

# ff_stuck <clone> <label> <behind> — say WHY the ff-only pull was refused;
# kb-search/kb-doctor read the marker to give the exact fix.
ff_stuck() {
  {
    echo "$2 auto-sync is failing on this machine (ff-only pull refused)."
    echo "since:  $(date -u +%Y-%m-%dT%H:%M:%SZ)"
    echo "branch: $(git -C "$1" branch --show-current 2>/dev/null || echo '?')"
    echo "behind origin/main by: $3 commit(s)"
    echo "local commits not on origin/main: $(git -C "$1" rev-list --count origin/main..HEAD 2>/dev/null || echo '?')"
    echo "local changes blocking the pull (never touched by this script):"
    git -C "$1" status --porcelain 2>/dev/null | grep -v '.kb-sync-stuck' | head -20
    echo "fix: see the kb-doctor skill (stash -> pull -> worktree -> stash pop)"
  } > "$1/.kb-sync-stuck" 2>/dev/null || true
}

# Public KB: clone if absent (quiet; a concurrent session's clone-in-progress just
# makes this one fail harmlessly), else ff-only pull with the stuck-marker protocol.
# NET records whether GitHub answered, so the internal block can tell a refused
# private repo from being offline.
NET=0
if [ ! -d "$PUB/.git" ]; then
  git clone --quiet --single-branch --branch main \
    "https://github.com/OCHA-DAP/ds-knowledge-base.git" "$PUB" 2>/dev/null || exit 0
  slog "cloned public KB -> $PUB"
  # remember the location — but only when it wasn't a one-off env override
  if [ -z "${KB_REPOS_DIR:-}" ]; then
    mkdir -p "$(dirname "$STATE")" && printf '%s\n' "$DIR" > "$STATE"
  fi
fi
if git -C "$PUB" pull --ff-only --quiet 2>/dev/null; then
  NET=1
  rm -f "$PUB/.kb-sync-stuck"
  slog "ok @ $(git -C "$PUB" rev-parse --short HEAD 2>/dev/null || echo '?')"
else
  git -C "$PUB" fetch --quiet 2>/dev/null && NET=1
  behind="$(git -C "$PUB" rev-list --count HEAD..origin/main 2>/dev/null || echo 0)"
  if [ "${behind:-0}" -gt 0 ] 2>/dev/null; then
    ff_stuck "$PUB" "KB" "$behind"
    slog "STUCK: ff-only pull refused, $behind behind (kb-doctor has the fix)"
  fi
fi

# Internal companion (private repo, only for users with access). Same marker
# protocol, plus the failure only a private repo has: GitHub answered the public
# sync but refuses this one — git's credentials are gone or the account lost
# access. Fully offline stays silent, as for the public clone. A credential prompt
# must fail fast here, never wait for input nobody will type.
if [ -d "$INT/.git" ]; then
  if GIT_TERMINAL_PROMPT=0 git -C "$INT" pull --ff-only --quiet 2>/dev/null; then
    rm -f "$INT/.kb-sync-stuck"
    slog "internal ok @ $(git -C "$INT" rev-parse --short HEAD 2>/dev/null || echo '?')"
  elif err="$(GIT_TERMINAL_PROMPT=0 git -C "$INT" fetch --quiet 2>&1)"; then
    behind="$(git -C "$INT" rev-list --count HEAD..origin/main 2>/dev/null || echo 0)"
    if [ "${behind:-0}" -gt 0 ] 2>/dev/null; then
      ff_stuck "$INT" "Internal KB" "$behind"
      slog "STUCK: internal KB ff-only pull refused, $behind behind (kb-doctor has the fix)"
    fi
  elif [ "$NET" = 1 ]; then
    {
      echo "Internal KB auto-sync is failing on this machine (fetch refused while GitHub answered for the public KB)."
      echo "since:  $(date -u +%Y-%m-%dT%H:%M:%SZ)"
      # last line of git's error, with any user:token@ stripped from a URL
      echo "git said: $(printf '%s\n' "$err" | grep -v '^$' | tail -n 1 | sed 's#://[^/@]*@#://#')"
      echo "likely: git has no working credentials for the private repo, or this GitHub account lost access"
      echo "fix: see the kb-doctor skill, check 5 (gh auth status -> gh auth setup-git)"
    } > "$INT/.kb-sync-stuck" 2>/dev/null || true
    slog "STUCK: internal KB fetch refused (credentials or access; kb-doctor has the fix)"
  fi
elif [ "$NET" = 1 ]; then
  # Not cloned: log why, never notify — having no access is a normal state.
  if ! command -v gh >/dev/null 2>&1; then
    slog "internal KB not cloned: gh not installed"
  elif ! gh auth status --hostname github.com >/dev/null 2>&1; then
    slog "internal KB not cloned: gh not logged in (gh auth login)"
  elif ! gh repo view OCHA-DAP/ds-knowledge-base-internal >/dev/null 2>&1; then
    slog "internal KB not cloned: this GitHub account has no access"
  elif gh repo clone OCHA-DAP/ds-knowledge-base-internal "$INT" \
    -- --quiet --single-branch --branch main >/dev/null 2>&1; then
    slog "cloned internal KB -> $INT"
  else
    slog "internal KB clone failed (gh repo clone)"
  fi
fi

exit 0
