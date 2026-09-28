#!/usr/bin/env bash
# Local observability for the ds-team plugins: make it VISIBLE when they work,
# what they read, and how much. Ships inside `kb-access`; wired in hooks/hooks.json
# to PreToolUse(Skill), PostToolUse(Read|Grep|Glob), PostToolUseFailure +
# PermissionDenied (same matcher), UserPromptSubmit, Stop and SessionEnd.
# Two surfaces:
#   - inline chat notices ({"systemMessage": ...}; emoji-coded, ANSI-safe everywhere)
#   - an ANSI-colored activity log: tail -f ~/.claude/ds-team-activity.log
#     (lines stamped <project>/<session8> so concurrent sessions stay legible)
# Observation ONLY: notices go to the human, never into Claude's context (no
# stdout other than the systemMessage JSON — plain stdout would nudge the model
# and contaminate the "is the plugin helping?" signal). The model-side "why"
# (announce/close lines) lives in the kb-search SKILL, not here — two channels:
# the skill self-reports intent, these hooks are the trustless audit (D112).
#
# Design (specs: docs/superpowers/specs/2026-08-03-ds-team-activity-notices-design.md,
# D96; visibility v2: 2026-09-17-kb-visibility-v2-design.md, D112):
#   skill    PreToolUse(Skill): ds-team plugin skill launched -> notice + log
#   read     PostToolUse(Read|Grep|Glob): target inside a KB clone -> log the hit
#            with its payload size, append to the turn tally; inline notice on the
#            FIRST KB read of the turn
#   attempt  PostToolUseFailure + PermissionDenied, same matcher: PostToolUse fires
#            only on SUCCESS, so denied/failed reads would otherwise be invisible —
#            exactly the cases worth seeing (a denied read of the internal clone, a
#            guessed non-existent page). Logged, never tallied: the rollup counts
#            what actually entered context.
#   prompt   UserPromptSubmit: flush an interrupted turn's tally to the log, start a
#            new tally stamped with the prompt snippet, keyword-match -> LOG ONLY
#            (the 🧭 inline notice cried wolf — a word match can't tell a team
#            question from an unrelated project that says "pipeline"; the skill's
#            announce line replaced it), then warn once per session if sync is stuck
#   stop     Stop: turn had KB reads -> one rollup notice (count, ~tokens, pages)
#   end      SessionEnd: delete this session's temp files
#
# Sizes are the WHOLE hook payload, not just the tool result: the payload key for
# tool output is not contractually documented (the hooks reference truncates before
# the PostToolUse schema), so keying off its name would silently report 0 bytes if
# it were ever renamed. Whole-payload bytes cost one O(1) length lookup, cannot be
# broken by key order or renames, and overstate by the few hundred bytes of hook
# metadata — hence "est." everywhere they surface.
#
# Hot path: Read/Grep/Glob fire constantly in every project. With no clone
# configured the script exits BEFORE reading stdin; when one is configured it reads
# stdin once, parses only the first 8 KiB (metadata + tool_input — a tool result
# cannot spoof a field there: JSON always escapes quotes in content, so `\"file_path\"`
# never matches the `"file_path"` we look for), extracts fields without forking, and
# skips the log-rotation stat. Field extraction stays crude on purpose (no jq — team
# Windows machines): worst failure = a missed/spurious notice, never a broken hook.
# Always exit 0.
#
# Smoke tests: scripts/test_kb_activity.sh (run it after any change to this file).
set -u

EVENT="${1:-}"
LOG="$HOME/.claude/ds-team-activity.log"

# Clone location — same resolution as kb_sync.sh: $KB_REPOS_DIR, else the state
# file, else nothing (no default, no auto-detection).
STATE="$HOME/.claude/.kb-repos-dir"
DIR="${KB_REPOS_DIR:-}"
[ -z "$DIR" ] && [ -f "$STATE" ] && { IFS= read -r DIR < "$STATE" || DIR=""; }

case "$EVENT" in
  read|attempt)
    [ -z "$DIR" ] && exit 0      # hot path: no clone -> no stdin read, no forks
    export LC_ALL=C              # bytes == chars: no multibyte decode over a big payload
    ;;
esac

PUB="${DIR:+$DIR/ds-knowledge-base}"
INT="${DIR:+$DIR/ds-knowledge-base-internal}"

# TTY guard: a hand-run of this script must not block waiting for a payload.
INPUT=""; [ -t 0 ] || INPUT="$(cat 2>/dev/null || true)"
BYTES=${#INPUT}
H="${INPUT:0:8192}"   # metadata + tool_input; result content is never parsed

jf() { # jf <key> -> first "<key>": "<value>" in $H ("" if absent)
  local r="${H#*\"$1\"}"
  [ "$r" = "$H" ] && return 0
  r="${r#*:}"; r="${r# }"
  case "$r" in \"*) r="${r#\"}"; printf '%s' "${r%%\"*}" ;; esac
}

SID="$(jf session_id)"
CWD="$(jf cwd)"
STAMP="${CWD##*/}/${SID:0:8}"   # <project>/<session8> on every log line

rotate_log() { # only called from the once-per-turn arms
  [ -f "$LOG" ] && [ "$(wc -c < "$LOG" 2>/dev/null || echo 0)" -gt 1048576 ] 2>/dev/null \
    && mv -f "$LOG" "$LOG.old" 2>/dev/null
  return 0
}

alog() { # alog <ansi-color-num> <TAG> <text>
  [ -d "$(dirname "$LOG")" ] || return 0
  printf '\033[2m%s %s\033[0m \033[%sm%-6s\033[0m %s\n' \
    "$(date '+%H:%M:%S')" "$STAMP" "$1" "$2" "$3" >> "$LOG" 2>/dev/null || true
}

notice() { # inline chat notice; must be the ONLY stdout of the run
  t="$1"; t="${t//\\/}"; t="${t//\"/}"
  printf '{"systemMessage":"%s"}' "$t"
}

TMP="${TMPDIR:-/tmp}"
# One file per session holds the turn: line 1 is "#<prompt snippet>", then one
# "<bytes> <relpath>" line per KB read. It is the turn flag too (no reads yet =
# first read of the turn). Written with umask 077 — it carries prompt text.
TALLY="$TMP/ds-team-tally-${SID:-nosession}"
STUCKFLAG="$TMP/ds-team-stuckwarn-${SID:-nosession}"

kb_rel() { # echo the clone-relative path if $1 is inside a KB clone, else nothing
  case "$1" in "$PUB"*|"$INT"*) printf '%s' "${1#"$DIR"/}" ;; esac
}

# one pass over the tally -> "<reads> <bytes> <distinct> <first two pages>"
tally_summary() {
  awk '
    /^#/ { next }
    {
      n++; b += $1; p = $0; sub(/^[0-9]+ /, "", p)
      if (!seen[p]++) { d++; if (d <= 2) list = (list == "" ? p : list ", " p) }
    }
    END { printf "%d %d %d %s", n + 0, b + 0, d + 0, list }
  ' "$1" 2>/dev/null
}

case "$EVENT" in
  skill)
    SKILL="$(jf skill)"
    case "$SKILL" in
      kb-access:*|data-access:*|data-conventions:*|aa-methods:*|infra-ops:*)
        alog 36 SKILL "$SKILL invoked"
        notice "📚 ds-team: $SKILL invoked"
        ;;
    esac
    ;;

  read)
    FP="$(jf file_path)"; [ -z "$FP" ] && FP="$(jf path)"
    [ -z "$FP" ] && exit 0
    REL="$(kb_rel "$FP")"; [ -z "$REL" ] && exit 0
    FIRST=0
    [ ! -s "$TALLY" ] && FIRST=1
    [ -s "$TALLY" ] && ! grep -qv '^#' "$TALLY" 2>/dev/null && FIRST=1
    ( umask 077; printf '%s %s\n' "$BYTES" "$REL" >> "$TALLY" ) 2>/dev/null || true
    alog 32 READ "$(jf tool_name) $REL (~$((BYTES / 4)) tok)"
    [ "$FIRST" = 1 ] && notice "📖 ds-team: consulting KB ($REL)"
    ;;

  attempt)
    FP="$(jf file_path)"; [ -z "$FP" ] && FP="$(jf path)"
    [ -z "$FP" ] && exit 0
    REL="$(kb_rel "$FP")"; [ -z "$REL" ] && exit 0
    # not tallied: the rollup counts what actually entered context
    alog 33 ATTEMPT "$(jf hook_event_name) $(jf tool_name) $REL — not read"
    ;;

  prompt)
    rotate_log
    # An Esc-interrupted turn never reaches Stop; flush what it read to the log so
    # the audit trail is complete even when the chat rollup never appeared.
    if [ -s "$TALLY" ]; then
      read -r N B D PAGES <<< "$(tally_summary "$TALLY")"
      [ "${N:-0}" -gt 0 ] 2>/dev/null && {
        MORE=""; [ "${D:-0}" -gt 2 ] 2>/dev/null && MORE=" +$((D - 2)) more"
        alog 34 ROLLUP "interrupted turn: $N reads, ~$((B / 4)) tok — $PAGES$MORE"
      }
    fi
    P="$(printf '%s' "$INPUT" | tr -d '\n' \
      | sed -n 's/.*"prompt"[[:space:]]*:[[:space:]]*"\(.*\)/\1/p')"
    # 70 CHARACTERS in the caller's locale (LC_ALL is not forced on this arm), so the
    # snippet never splits a UTF-8 sequence; read back whole, never re-truncated.
    SNIP="${P%%\"*}"; SNIP="${SNIP:0:70}"; SNIP="${SNIP//\\/}"
    ( umask 077; printf '#%s\n' "$SNIP" > "$TALLY" ) 2>/dev/null || true
    if printf '%s' "$P" | grep -qwiE 'kb|knowledge base|framework|trigger|anticipatory|activation|return period|pipeline|blob|stratus|codab|databricks|ocha-lens|ibtracs|marimo'; then
      alog 35 PROMPT "looks KB-relevant: $SNIP"
    fi
    # last, so its notice is the only stdout and the tally/snippet above always run
    if [ -n "$DIR" ] && [ -f "$PUB/.kb-sync-stuck" ] && [ ! -f "$STUCKFLAG" ]; then
      : > "$STUCKFLAG" 2>/dev/null || true
      alog 31 WARN "KB auto-sync stuck (kb-doctor has the fix)"
      notice "⚠️ ds-team: KB auto-sync is stuck — ask kb-doctor for the fix"
    fi
    ;;

  stop)
    [ -s "$TALLY" ] || exit 0
    read -r N B D PAGES <<< "$(tally_summary "$TALLY")"
    [ "${N:-0}" -gt 0 ] 2>/dev/null || exit 0
    rotate_log
    # line 1 is the snippet only if the turn began with a prompt: a session can read
    # before any UserPromptSubmit (resume, sub-agent), and a data line there is not a prompt
    SNIP=""; IFS= read -r LINE1 < "$TALLY" 2>/dev/null || LINE1=""
    case "$LINE1" in \#*) SNIP="${LINE1#\#}" ;; esac
    TOK=$((B / 4))
    [ "$TOK" -ge 1000 ] && TOKS="$((TOK / 1000))k" || TOKS="$TOK"
    MORE=""; [ "${D:-0}" -gt 2 ] 2>/dev/null && MORE=" +$((D - 2)) more"
    alog 34 ROLLUP "$N reads, ~$TOKS tok — $PAGES$MORE${SNIP:+ — prompt: $SNIP}"
    # Keep the snippet, drop the reads: if a blocking Stop hook elsewhere continues
    # this turn, the next reads tally fresh and re-announce 📖 (two rollups, both
    # attributed to the same prompt) rather than being silently merged or lost.
    ( umask 077; printf '#%s\n' "$SNIP" > "$TALLY" ) 2>/dev/null || true
    notice "📖 ds-team: turn read ${N}× from KB (~$TOKS tok est.) — $PAGES$MORE"
    ;;

  end)
    rm -f "$TALLY" "$STUCKFLAG" 2>/dev/null || true
    ;;
esac
exit 0
