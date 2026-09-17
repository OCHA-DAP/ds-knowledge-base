#!/usr/bin/env bash
# Local observability for the ds-team plugins: make it VISIBLE when they work,
# what they read, and how much. Ships inside `kb-access`; wired to PreToolUse
# (Skill), PostToolUse (Read|Grep|Glob), UserPromptSubmit and Stop in
# hooks/hooks.json. Two surfaces:
#   - inline chat notices ({"systemMessage": ...}; emoji-coded, ANSI-safe everywhere)
#   - an ANSI-colored activity log: tail -f ~/.claude/ds-team-activity.log
#     (lines stamped <project>/<session8> so concurrent sessions stay legible)
# Observation ONLY: notices go to the human, never into Claude's context (no
# stdout other than the systemMessage JSON — plain stdout would nudge the model
# and contaminate the "is the plugin helping?" signal). The model-side "why"
# (announce/close lines) lives in the kb-search SKILL, not here — two channels:
# the skill self-reports intent, these hooks are the trustless audit (D105).
#
# Design (specs: docs/superpowers/specs/2026-08-03-ds-team-activity-notices-design.md,
# D96; visibility v2: 2026-09-17-kb-visibility-v2-design.md, D105):
#   skill   PreToolUse(Skill): ds-team plugin skill launched -> notice + log
#   read    PostToolUse(Read|Grep|Glob): target inside a KB clone -> log every
#           hit with its response size (post-tool so the size is real); tally
#           per turn; inline notice only on the FIRST KB read of the turn
#   prompt  UserPromptSubmit: reset the turn tally; stash a prompt snippet for
#           the rollup; keyword-match -> LOG ONLY (the 🧭 inline notice cried
#           wolf — a word match can't tell a team question from an unrelated
#           project that says "pipeline"; the skill's announce line replaced it);
#           warn once per session if sync is stuck
#   stop    Stop: turn had KB reads -> one rollup notice (count, ~tokens, pages)
# Field extraction is deliberately crude (sed, no jq — team Windows machines);
# on read events fields are pulled from the JSON BEFORE "tool_response" so file
# contents can't spoof them. Worst failure = a missed/spurious notice, never a
# broken hook. Always exit 0.
#
# Smoke tests (run from the repo root; expect the commented output):
#   printf '{"session_id":"s1","cwd":"/x/myproj","tool_name":"Skill","tool_input":{"skill":"kb-access:kb-search"}}' \
#     | bash claude/plugins/kb-access/scripts/kb_activity.sh skill
#     # -> {"systemMessage":"📚 ds-team: kb-access:kb-search invoked"}
#   printf '{"tool_input":{"skill":"superpowers:brainstorming"}}' \
#     | bash claude/plugins/kb-access/scripts/kb_activity.sh skill
#     # -> (nothing: not a ds-team plugin)
#   printf '{"session_id":"s1","cwd":"/x/myproj","tool_name":"Read","tool_input":{"file_path":"/tmp/kbsmoke/ds-knowledge-base/methods/x.md"},"tool_response":"0123456789"}' \
#     | KB_REPOS_DIR=/tmp/kbsmoke bash claude/plugins/kb-access/scripts/kb_activity.sh read
#     # -> first call: {"systemMessage":"📖 ds-team: consulting KB (ds-knowledge-base/methods/x.md)"}; repeat: nothing (tally still grows)
#   printf '{"session_id":"s1"}' \
#     | bash claude/plugins/kb-access/scripts/kb_activity.sh stop
#     # -> {"systemMessage":"📖 ds-team: turn read 2× from KB (~7 tok est.) — ds-knowledge-base/methods/x.md"}; repeat: nothing
#   printf '{"session_id":"s1","prompt":"how does the chad trigger work"}' \
#     | bash claude/plugins/kb-access/scripts/kb_activity.sh prompt
#     # -> (no notice; log gains a PROMPT line, turn tally resets)
set -u

EVENT="${1:-}"
LOG="$HOME/.claude/ds-team-activity.log"
INPUT="$(cat 2>/dev/null || true)"
# everything before tool_response: field extraction runs on this so a read
# file's CONTENT (which may contain "file_path": ...) can't spoof a field
HEAD="${INPUT%%\"tool_response\"*}"

STATE="$HOME/.claude/.kb-repos-dir"
DIR="${KB_REPOS_DIR:-}"
[ -z "$DIR" ] && [ -f "$STATE" ] && DIR="$(head -n1 "$STATE")"
PUB="${DIR:+$DIR/ds-knowledge-base}"
INT="${DIR:+$DIR/ds-knowledge-base-internal}"

# first "key":"value" string field from the pre-tool_response JSON (greedy .*
# -> last match; fine for the singleton fields we read)
jfield() {
  printf '%s' "$HEAD" | tr -d '\n' \
    | sed -n 's/.*"'"$1"'"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' | head -n1
}

SID="$(jfield session_id)"
CWD="$(jfield cwd)"
STAMP="${CWD##*/}/${SID:0:8}"   # <project>/<session8> on every log line

alog() { # alog <ansi-color-num> <TAG> <text>
  [ -d "$(dirname "$LOG")" ] || return 0
  [ -f "$LOG" ] && [ "$(wc -c < "$LOG" 2>/dev/null || echo 0)" -gt 1048576 ] 2>/dev/null \
    && mv -f "$LOG" "$LOG.old" 2>/dev/null
  printf '\033[2m%s %s\033[0m \033[%sm%-6s\033[0m %s\n' \
    "$(date '+%H:%M:%S')" "$STAMP" "$1" "$2" "$3" >> "$LOG" 2>/dev/null || true
}

notice() { # inline chat notice; must be the ONLY stdout of the run
  t="$1"; t="${t//\\/}"; t="${t//\"/}"
  printf '{"systemMessage":"%s"}' "$t"
}

TMP="${TMPDIR:-/tmp}"
TURNFLAG="$TMP/ds-team-turn-${SID:-nosession}"
TALLY="$TMP/ds-team-tally-${SID:-nosession}"     # per-turn: "<resp_bytes> <rel_path>" lines
PSNIP="$TMP/ds-team-prompt-${SID:-nosession}"    # current turn's prompt, first ~70 chars
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
        RESPB=$(( ${#INPUT} - ${#HEAD} ))   # ~bytes the tool returned into context
        printf '%s %s\n' "$RESPB" "$REL" >> "$TALLY" 2>/dev/null || true
        alog 32 READ "$(jfield tool_name) $REL (~$((RESPB / 4)) tok)"
        if [ ! -f "$TURNFLAG" ]; then
          : > "$TURNFLAG" 2>/dev/null || true
          notice "📖 ds-team: consulting KB ($REL)"
        fi
        ;;
    esac
    ;;

  prompt)
    rm -f "$TURNFLAG" "$TALLY" 2>/dev/null || true
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
    # snippet stops at the first quote (escaped quotes truncate it — fine for 70 chars)
    SNIP="${P%%\"*}"; SNIP="${SNIP:0:70}"; SNIP="${SNIP//\\/}"
    printf '%s' "$SNIP" > "$PSNIP" 2>/dev/null || true
    if printf '%s' "$P" | grep -qwiE 'kb|knowledge base|framework|trigger|anticipatory|activation|return period|pipeline|blob|stratus|codab|databricks|ocha-lens|ibtracs|marimo'; then
      alog 35 PROMPT "looks KB-relevant: $SNIP"
    fi
    ;;

  stop)
    [ -s "$TALLY" ] || { rm -f "$TALLY" 2>/dev/null || true; exit 0; }
    N="$(grep -c . "$TALLY" 2>/dev/null || echo 0)"
    B="$(awk '{b += $1} END {print b + 0}' "$TALLY" 2>/dev/null || echo 0)"
    TOK=$(( B / 4 ))
    [ "$TOK" -ge 1000 ] && TOKS="$(( TOK / 1000 ))k" || TOKS="$TOK"
    PAGES="$(awk '{sub(/^[0-9]+ /,""); if (!s[$0]++) print}' "$TALLY" 2>/dev/null | head -n2 \
      | tr '\n' '|' | sed 's/|$//; s/|/, /g')"
    DIST="$(awk '{sub(/^[0-9]+ /,""); if (!s[$0]++) n++} END {print n + 0}' "$TALLY" 2>/dev/null || echo 0)"
    MORE=""; [ "$DIST" -gt 2 ] 2>/dev/null && MORE=" +$(( DIST - 2 )) more"
    SNIP=""; [ -f "$PSNIP" ] && SNIP="$(head -c 70 "$PSNIP" 2>/dev/null || true)"
    alog 34 ROLLUP "$N reads, ~$TOKS tok — $PAGES$MORE${SNIP:+ — prompt: $SNIP}"
    rm -f "$TALLY" 2>/dev/null || true
    notice "📖 ds-team: turn read ${N}× from KB (~$TOKS tok est.) — $PAGES$MORE"
    ;;
esac
exit 0
