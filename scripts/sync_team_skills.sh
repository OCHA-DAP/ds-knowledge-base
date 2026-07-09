#!/usr/bin/env bash
# Link the team skills from this KB clone into ~/.claude/skills — one entry PER SKILL.
# Claude Code discovers personal skills exactly one level deep (~/.claude/skills/<name>/
# SKILL.md); a grouping-directory symlink is never scanned, and colon namespacing is
# plugin-only — so per-skill links are the only layout that works.
#
# Run by setup_team_claude.sh AND by the session-start hook (after the pull), so a skill
# merged to main appears on every machine's next session with zero user action — and
# because this script rides the clone, the sync logic itself self-updates too.
#
# Never clobbers a personal skill: only touches symlinks into this repo and (Windows)
# copies carrying the .kb-team-skill marker.
set -u

PUB="$(cd "$(dirname "$0")/.." && pwd)"
SK="$HOME/.claude/skills"
mkdir -p "$SK"

# migrate away the earlier grouped layout (a ds-team dir symlink — never discovered)
[ -L "$SK/ds-team" ] && rm "$SK/ds-team"
[ -d "$SK/ds-team" ] && rm -rf "$SK/ds-team"

case "$(uname -s)" in MINGW*|MSYS*|CYGWIN*) WIN=1 ;; *) WIN=0 ;; esac

for d in "$PUB/claude/skills"/*/; do
  [ -f "$d/SKILL.md" ] || continue
  n="$(basename "$d")"
  t="$SK/$n"
  if [ "$WIN" = 1 ]; then
    # symlinks need Developer Mode on Windows → keep a marker-tagged copy in sync
    if [ -e "$t" ] && [ ! -f "$t/.kb-team-skill" ]; then
      echo "  skip $n — a personal skill with this name exists" >&2
      continue
    fi
    rm -rf "$t"
    cp -R "${d%/}" "$t"
    touch "$t/.kb-team-skill"
  else
    if [ -L "$t" ]; then
      case "$(readlink "$t")" in
        *"/ds-knowledge-base/claude/skills/"*) ln -sfn "${d%/}" "$t" ;;  # ours (or stale) → repoint
        *) echo "  skip $n — a personal skill with this name exists" >&2 ;;
      esac
    elif [ -e "$t" ]; then
      echo "  skip $n — a personal skill with this name exists" >&2
    else
      ln -s "${d%/}" "$t"
    fi
  fi
done
exit 0
