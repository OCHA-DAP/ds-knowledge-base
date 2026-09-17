#!/usr/bin/env bash
# Smoke tests for claude/plugins/kb-access/scripts/kb_activity.sh (D96/D112).
#
# Every case below is a regression test for a bug found in review of #630 or a
# behaviour the visibility design promises. Runs in a sandboxed HOME + TMPDIR, so
# it never touches the real activity log or a real clone. Usage, from the repo root:
#
#     bash scripts/test_kb_activity.sh
#
# Exits non-zero on the first failure, printing expected vs actual.
set -u

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SCRIPT="$ROOT/claude/plugins/kb-access/scripts/kb_activity.sh"
SANDBOX="$(mktemp -d)"
trap 'rm -rf "$SANDBOX"' EXIT

export HOME="$SANDBOX/home"
export TMPDIR="$SANDBOX/tmp"
export KB_REPOS_DIR="$SANDBOX/repos"
mkdir -p "$HOME/.claude" "$TMPDIR" "$KB_REPOS_DIR/ds-knowledge-base/methods" \
         "$KB_REPOS_DIR/ds-knowledge-base-internal/drive"
LOG="$HOME/.claude/ds-team-activity.log"
KB="$KB_REPOS_DIR/ds-knowledge-base"

pass=0
fail() { printf '\n\033[31mFAIL\033[0m %s\n  expected: %s\n  actual:   %s\n' "$1" "$2" "$3"; exit 1; }
ok()   { pass=$((pass + 1)); printf '.'; }

run() { printf '%s' "$2" | bash "$SCRIPT" "$1"; }          # run <event> <json>
logtail() { sed 's/\x1b\[[0-9;]*m//g' "$LOG" 2>/dev/null | tail -n "${1:-1}"; }

payload() { # payload <tool> <path> [response] [event]
  printf '{"session_id":"sess1234abcd","cwd":"/x/myproj","hook_event_name":"%s","tool_name":"%s","tool_input":{"file_path":"%s"},"tool_response":"%s"}' \
    "${4:-PostToolUse}" "$1" "$2" "${3:-body}"
}

# --- skill arm -------------------------------------------------------------
out="$(run skill '{"session_id":"sess1234abcd","cwd":"/x/myproj","tool_name":"Skill","tool_input":{"skill":"kb-access:kb-search"}}')"
case "$out" in *"kb-access:kb-search invoked"*) ok ;; *) fail "ds-team skill notice" "📚 notice" "$out" ;; esac

out="$(run skill '{"tool_input":{"skill":"superpowers:brainstorming"}}')"
[ -z "$out" ] && ok || fail "non-ds-team skill is silent" "" "$out"

# --- prompt starts a turn --------------------------------------------------
run prompt '{"session_id":"sess1234abcd","cwd":"/x/myproj","prompt":"how does the chad trigger work"}' >/dev/null
case "$(logtail 1)" in *"PROMPT looks KB-relevant: how does the chad trigger work"*) ok ;;
  *) fail "KB-keyword prompt logs (no notice)" "PROMPT line" "$(logtail 1)" ;; esac

out="$(run prompt '{"session_id":"sess1234abcd","cwd":"/x/myproj","prompt":"unrelated question"}')"
[ -z "$out" ] && ok || fail "prompt arm never notices (🧭 is log-only)" "" "$out"

# --- reads: first notices, repeat is silent, both tally --------------------
out="$(run read "$(payload Read "$KB/methods/x.md" "0123456789")")"
case "$out" in *"consulting KB (ds-knowledge-base/methods/x.md)"*) ok ;;
  *) fail "first KB read notices" "📖 notice" "$out" ;; esac

out="$(run read "$(payload Read "$KB/methods/y.md" "0123456789")")"
[ -z "$out" ] && ok || fail "second KB read is silent" "" "$out"

out="$(run read "$(payload Read "/x/elsewhere/other.md" "0123456789")")"
[ -z "$out" ] && ok || fail "non-KB read ignored" "" "$out"

# REGRESSION (#630 review): a Grep whose *pattern* contains the literal string
# tool_response used to truncate the parse head and vanish entirely.
out="$(run read '{"session_id":"sess1234abcd","cwd":"/x/myproj","tool_name":"Grep","tool_input":{"pattern":"tool_response","path":"'"$KB"'"},"tool_response":"hit"}')"
case "$(logtail 1)" in *"READ   Grep ds-knowledge-base"*) ok ;;
  *) fail "grep for 'tool_response' still tracked" "READ line" "$(logtail 1)" ;; esac

# A tool result cannot spoof file_path: JSON escapes quotes in content.
out="$(run read '{"session_id":"sess1234abcd","cwd":"/x/myproj","tool_name":"Read","tool_input":{"file_path":"/x/elsewhere/other.md"},"tool_response":"\"file_path\": \"'"$KB"'/evil.md\""}')"
[ -z "$out" ] && case "$(logtail 1)" in *evil.md*) fail "content cannot spoof a KB path" "no evil.md" "$(logtail 1)" ;; *) ok ;; esac

# --- attempts (PostToolUseFailure / PermissionDenied) ----------------------
run attempt "$(payload Read "$KB/methods/missing.md" "" PostToolUseFailure)" >/dev/null
case "$(logtail 1)" in *"ATTEMPT PostToolUseFailure Read ds-knowledge-base/methods/missing.md — not read"*) ok ;;
  *) fail "failed read logged as ATTEMPT" "ATTEMPT line" "$(logtail 1)" ;; esac

run attempt "$(payload Read "$KB_REPOS_DIR/ds-knowledge-base-internal/drive/x.md" "" PermissionDenied)" >/dev/null
case "$(logtail 1)" in *"ATTEMPT PermissionDenied"*internal*) ok ;;
  *) fail "denied internal-clone read logged" "ATTEMPT line" "$(logtail 1)" ;; esac

# --- rollup ----------------------------------------------------------------
out="$(run stop '{"session_id":"sess1234abcd","cwd":"/x/myproj"}')"
# 3 successful reads (x.md, y.md, the grep) — the 2 attempts must NOT be counted
case "$out" in *"turn read 3× from KB"*) ok ;; *) fail "rollup counts successful reads only" "3×" "$out" ;; esac
case "$out" in *"+1 more"*) ok ;; *) fail "rollup names 2 pages + remainder" "+1 more" "$out" ;; esac
case "$(logtail 1)" in *"prompt: unrelated question"*) ok ;;
  *) fail "rollup log carries the turn's prompt" "prompt: unrelated question" "$(logtail 1)" ;; esac

out="$(run stop '{"session_id":"sess1234abcd","cwd":"/x/myproj"}')"
[ -z "$out" ] && ok || fail "second Stop with no new reads is silent" "" "$out"

# A blocking Stop hook elsewhere can continue the turn: the next read must
# re-announce rather than be silently merged into the reported rollup.
out="$(run read "$(payload Read "$KB/methods/z.md" "0123456789")")"
case "$out" in *"consulting KB"*) ok ;; *) fail "post-rollup read re-announces" "📖 notice" "$out" ;; esac

# --- interrupted turn (Esc: Stop never fires) ------------------------------
run prompt '{"session_id":"sess1234abcd","cwd":"/x/myproj","prompt":"next question"}' >/dev/null
case "$(logtail 1)" in *"ROLLUP interrupted turn: 1 reads"*) ok ;;
  *) fail "interrupted turn flushed to log" "interrupted ROLLUP" "$(logtail 1)" ;; esac

# --- stuck sync does not steal the turn's prompt ---------------------------
# REGRESSION (#630 review): the stuck branch used to exit before the snippet was
# written, so the next rollup was attributed to an older prompt.
: > "$KB/.kb-sync-stuck"
out="$(run prompt '{"session_id":"sess1234abcd","cwd":"/x/myproj","prompt":"prompt after stuck"}')"
case "$out" in *"auto-sync is stuck"*) ok ;; *) fail "stuck warning notices" "⚠️ notice" "$out" ;; esac
run read "$(payload Read "$KB/methods/x.md" "0123456789")" >/dev/null
run stop '{"session_id":"sess1234abcd","cwd":"/x/myproj"}' >/dev/null
case "$(logtail 1)" in *"prompt: prompt after stuck"*) ok ;;
  *) fail "rollup uses the CURRENT prompt when sync is stuck" "prompt after stuck" "$(logtail 1)" ;; esac
rm -f "$KB/.kb-sync-stuck"

# --- log hygiene -----------------------------------------------------------
# REGRESSION (#630 review): a 70-char snippet re-read as 70 BYTES split a UTF-8
# sequence, making the whole log line un-greppable in a UTF-8 locale.
acc="$(printf 'a%.0s' $(seq 1 69))é"
run prompt "$(printf '{"session_id":"sess1234abcd","cwd":"/x/myproj","prompt":"%s trigger"}' "$acc")" >/dev/null
run read "$(payload Read "$KB/methods/x.md" "0123456789")" >/dev/null
run stop '{"session_id":"sess1234abcd","cwd":"/x/myproj"}' >/dev/null
if command -v iconv >/dev/null 2>&1; then
  iconv -f UTF-8 -t UTF-8 < "$LOG" >/dev/null 2>&1 && ok || fail "log stays valid UTF-8" "valid UTF-8" "invalid byte sequence"
else ok; fi
case "$(logtail 1)" in *"myproj/sess1234"*) ok ;;
  *) fail "log lines stamped <project>/<session8>" "myproj/sess1234" "$(logtail 1)" ;; esac

# --- the tally holds prompt text: must not be world-readable ---------------
perms="$(ls -l "$TMPDIR"/ds-team-tally-* 2>/dev/null | head -1 | cut -c1-10)"
case "$perms" in -rw-------) ok ;; *) fail "tally file is 0600" "-rw-------" "$perms" ;; esac

# --- SessionEnd cleans up --------------------------------------------------
run end '{"session_id":"sess1234abcd","cwd":"/x/myproj"}' >/dev/null
ls "$TMPDIR"/ds-team-tally-* >/dev/null 2>&1 && fail "SessionEnd removes temp files" "no tally file" "$(ls "$TMPDIR")" || ok

# --- no clone configured: the hot path must not touch anything -------------
before="$(wc -c < "$LOG")"
out="$(printf '%s' "$(payload Read "$KB/methods/x.md" "body")" | KB_REPOS_DIR="" HOME="$SANDBOX/empty" bash "$SCRIPT" read)"
[ -z "$out" ] && [ "$(wc -c < "$LOG")" = "$before" ] && ok \
  || fail "no clone configured -> no output, no log write" "silent" "$out"

printf '\n\033[32mOK\033[0m — %d checks passed\n' "$pass"
