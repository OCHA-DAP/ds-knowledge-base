#!/usr/bin/env bash
# Local observability for the ds-team plugins: make it VISIBLE when they work.
# Ships inside `kb-access`; wired to PreToolUse (Skill, Read|Grep|Glob) and
# UserPromptSubmit in hooks/hooks.json. Two surfaces:
#   - inline chat notices ({"systemMessage": ...}; emoji-coded, ANSI-safe everywhere)
#   - an ANSI-colored activity log: tail -f ~/.claude/ds-team-activity.log
# Observation ONLY: notices go to the human, never into Claude's context (no
# stdout other than the systemMessage JSON — plain stdout on UserPromptSubmit
# would nudge the model and contaminate the "is the plugin helping?" signal).
#
# Design (spec: docs/superpowers/specs/2026-08-03-ds-team-activity-notices-design.md, D93):
#   skill   PreToolUse(Skill): ds-team plugin skill launched -> notice + log
#   read    PreToolUse(Read|Grep|Glob): target inside a KB clone -> log every
#           hit; inline notice only on the FIRST KB read of the turn
#   prompt  UserPromptSubmit: reset the turn flag; keyword-match the prompt
#           ("looks KB-relevant"); warn once per session if sync is stuck
# Field extraction is deliberately crude (sed, no jq — team Windows machines):
# worst failure = a missed/spurious notice, never a broken hook. Always exit 0.
#
# Smoke tests (run from the repo root; expect the commented output):
#   printf '{"session_id":"s1","tool_name":"Skill","tool_input":{"skill":"kb-access:kb-search"}}' \
#     | bash claude/plugins/kb-access/scripts/kb_activity.sh skill
#     # -> {"systemMessage":"📚 ds-team: kb-access:kb-search invoked"}
#   printf '{"tool_input":{"skill":"superpowers:brainstorming"}}' \
#     | bash claude/plugins/kb-access/scripts/kb_activity.sh skill
#     # -> (nothing: not a ds-team plugin)
#   printf '{"session_id":"s1","tool_name":"Read","tool_input":{"file_path":"/tmp/kbsmoke/ds-knowledge-base/methods/x.md"}}' \
#     | KB_REPOS_DIR=/tmp/kbsmoke bash claude/plugins/kb-access/scripts/kb_activity.sh read
#     # -> first call: {"systemMessage":"📖 ds-team: consulting KB (ds-knowledge-base/methods/x.md)"}; repeat: nothing
#   printf '{"session_id":"s1","prompt":"how does the chad trigger work"}' \
#     | bash claude/plugins/kb-access/scripts/kb_activity.sh prompt
#     # -> {"systemMessage":"🧭 ds-team: prompt looks team-KB-relevant"} (and resets the turn flag)
set -u

EVENT="${1:-}"
LOG="$HOME/.claude/ds-team-activity.log"
INPUT="$(cat 2>/dev/null || true)"

STATE="$HOME/.claude/.kb-repos-dir"
DIR="${KB_REPOS_DIR:-}"
[ -z "$DIR" ] && [ -f "$STATE" ] && DIR="$(head -n1 "$STATE")"
PUB="${DIR:+$DIR/ds-knowledge-base}"
INT="${DIR:+$DIR/ds-knowledge-base-internal}"

# first "key":"value" string field from the hook JSON (greedy .* -> last match;
# fine for the singleton fields we read)
jfield() {
  printf '%s' "$INPUT" | tr -d '\n' \
    | sed -n 's/.*"'"$1"'"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' | head -n1
}

alog() { # alog <ansi-color-num> <TAG> <text>
  [ -d "$(dirname "$LOG")" ] || return 0
  [ -f "$LOG" ] && [ "$(wc -c < "$LOG" 2>/dev/null || echo 0)" -gt 1048576 ] 2>/dev/null \
    && mv -f "$LOG" "$LOG.old" 2>/dev/null
  printf '\033[2m%s\033[0m \033[%sm%-6s\033[0m %s\n' \
    "$(date '+%H:%M:%S')" "$1" "$2" "$3" >> "$LOG" 2>/dev/null || true
}

notice() { # inline chat notice; must be the ONLY stdout of the run
  t="$1"; t="${t//\\/}"; t="${t//\"/}"
  printf '{"systemMessage":"%s"}' "$t"
}

SID="$(jfield session_id)"
TMP="${TMPDIR:-/tmp}"
TURNFLAG="$TMP/ds-team-turn-${SID:-nosession}"
STUCKFLAG="$TMP/ds-team-stuckwarn-${SID:-nosession}"

case "$EVENT" in
  skill)
    SKILL="$(jfield skill)"
    case "$SKILL" in
      kb-access:*|data-access:*|data-conventions:*|aa-methods:*|infra-ops:*)
        alog 36 SKILL "$SKILL invoked"
        notice "📚 ds-team: $SKILL invoked"
        ;;
    esac
    ;;

  read)
    [ -z "$DIR" ] && exit 0
    FP="$(jfield file_path)"; [ -z "$FP" ] && FP="$(jfield path)"
    [ -z "$FP" ] && exit 0
    case "$FP" in
      "$PUB"*|"$INT"*)
        REL="${FP#"$DIR"/}"
        alog 32 READ "$(jfield tool_name) $REL"
        if [ ! -f "$TURNFLAG" ]; then
          : > "$TURNFLAG" 2>/dev/null || true
          notice "📖 ds-team: consulting KB ($REL)"
        fi
        ;;
    esac
    ;;

  prompt)
    rm -f "$TURNFLAG" 2>/dev/null || true
    if [ -n "$DIR" ] && [ -f "$PUB/.kb-sync-stuck" ] && [ ! -f "$STUCKFLAG" ]; then
      : > "$STUCKFLAG" 2>/dev/null || true
      alog 31 WARN "KB auto-sync stuck (kb-doctor has the fix)"
      notice "⚠️ ds-team: KB auto-sync is stuck — ask kb-doctor for the fix"
      exit 0
    fi
    # match the prompt field only — cwd/transcript_path often contain repo names
    # (ds-aa-*, ...-pipeline) that would false-positive on the whole JSON
    P="$(printf '%s' "$INPUT" | tr -d '\n' \
      | sed -n 's/.*"prompt"[[:space:]]*:[[:space:]]*"\(.*\)/\1/p')"
    if printf '%s' "$P" | grep -qwiE 'kb|knowledge base|framework|trigger|anticipatory|activation|return period|pipeline|blob|stratus|codab|databricks|ocha-lens|ibtracs|marimo'; then
      alog 35 PROMPT "looks KB-relevant"
      notice "🧭 ds-team: prompt looks team-KB-relevant"
    fi
    ;;
esac
exit 0
