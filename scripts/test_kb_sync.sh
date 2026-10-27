#!/usr/bin/env bash
# Smoke tests for claude/plugins/kb-access/scripts/kb_sync.sh — chiefly the
# internal-clone flagging of D123, plus the public stuck marker it shares code with.
#
# Runs in a sandboxed HOME with two local bare repos standing in for GitHub and a
# fake `gh` on PATH, so it never touches the network, a real clone or the real
# activity log. Usage, from the repo root:
#
#     bash scripts/test_kb_sync.sh
#
# Exits non-zero on the first failure, printing expected vs actual.
set -u

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SCRIPT="$ROOT/claude/plugins/kb-access/scripts/kb_sync.sh"
SANDBOX="$(mktemp -d)"
trap 'rm -rf "$SANDBOX"' EXIT

export HOME="$SANDBOX/home"
export KB_REPOS_DIR="$SANDBOX/repos"
export GIT_AUTHOR_NAME=t GIT_AUTHOR_EMAIL=t@example.org
export GIT_COMMITTER_NAME=t GIT_COMMITTER_EMAIL=t@example.org
mkdir -p "$HOME/.claude" "$KB_REPOS_DIR" "$SANDBOX/bin" "$SANDBOX/remotes"
LOG="$HOME/.claude/ds-team-activity.log"
PUB="$KB_REPOS_DIR/ds-knowledge-base"
INT="$KB_REPOS_DIR/ds-knowledge-base-internal"
PUBR="$SANDBOX/remotes/pub.git"
INTR="$SANDBOX/remotes/int.git"

# Fake gh: FAKE_GH=noauth|noaccess fails at that step; `repo clone` clones $INTR.
cat > "$SANDBOX/bin/gh" <<EOF
#!/usr/bin/env bash
case "\$1 \$2" in
  "auth status") [ "\${FAKE_GH:-}" != noauth ] ;;
  "repo view")   [ "\${FAKE_GH:-}" != noaccess ] ;;
  "repo clone")  git clone --quiet "$INTR" "\$4" ;;
  *) exit 1 ;;
esac
EOF
chmod +x "$SANDBOX/bin/gh"
export PATH="$SANDBOX/bin:$PATH"

pass=0
fail() { printf '\n\033[31mFAIL\033[0m %s\n  expected: %s\n  actual:   %s\n' "$1" "$2" "$3"; exit 1; }
ok()   { pass=$((pass + 1)); printf '.'; }

sync() { printf '%s' '{"session_id":"sync1234abcd","cwd":"/x/myproj"}' | bash "$SCRIPT"; }
synclog() { sed 's/\x1b\[[0-9;]*m//g' "$LOG" 2>/dev/null | tail -n "${1:-1}"; }
remote_commit() { # remote_commit <bare> <file> — push one commit changing <file>
  local w="$SANDBOX/work-$$-$RANDOM"
  git clone --quiet "$1" "$w" 2>/dev/null && echo "$RANDOM" >> "$w/$2" \
    && git -C "$w" add "$2" && git -C "$w" commit --quiet -m "$2" \
    && git -C "$w" push --quiet origin main && rm -rf "$w"
}

for r in "$PUBR" "$INTR"; do
  git init --quiet --bare -b main "$r"
  remote_commit "$r" f.md
done
git clone --quiet "$PUBR" "$PUB"
git clone --quiet "$INTR" "$INT"

# --- both clones healthy ---------------------------------------------------
remote_commit "$INTR" f.md
sync
[ ! -e "$INT/.kb-sync-stuck" ] && ok || fail "healthy internal clone has no marker" "no marker" "$(cat "$INT/.kb-sync-stuck")"
[ "$(git -C "$INT" rev-parse HEAD)" = "$(git -C "$INTR" rev-parse main)" ] && ok \
  || fail "internal clone fast-forwarded" "at remote main" "$(git -C "$INT" log --oneline -1)"
case "$(synclog 1)" in *"SYNC   internal ok @"*) ok ;; *) fail "internal success logged" "internal ok @" "$(synclog 1)" ;; esac

# --- internal ff-only pull refused by a local edit -------------------------
remote_commit "$INTR" f.md
echo "local edit" >> "$INT/f.md"
sync
grep -q '^Internal KB auto-sync is failing on this machine (ff-only pull refused)' "$INT/.kb-sync-stuck" 2>/dev/null && ok \
  || fail "internal ff-only refusal writes a marker" "Internal KB ... ff-only pull refused" "$(cat "$INT/.kb-sync-stuck" 2>&1)"
grep -q '^behind origin/main by: 1 commit' "$INT/.kb-sync-stuck" && grep -q '^ M f.md' "$INT/.kb-sync-stuck" && ok \
  || fail "marker says how far behind and what blocks it" "behind 1 + ' M f.md'" "$(cat "$INT/.kb-sync-stuck")"
grep -q 'kb-sync-stuck' <(sed 1d "$INT/.kb-sync-stuck") && fail "marker does not list itself" "no self-listing" "$(cat "$INT/.kb-sync-stuck")" || ok
case "$(synclog 1)" in *"STUCK: internal KB ff-only pull refused, 1 behind"*) ok ;;
  *) fail "internal refusal logged" "STUCK: internal KB ff-only" "$(synclog 1)" ;; esac
[ ! -e "$PUB/.kb-sync-stuck" ] && ok || fail "public clone unaffected" "no public marker" "$(cat "$PUB/.kb-sync-stuck")"

# --- the next good pull clears it ------------------------------------------
git -C "$INT" checkout --quiet -- f.md
sync
[ ! -e "$INT/.kb-sync-stuck" ] && ok || fail "successful pull clears the internal marker" "no marker" "$(cat "$INT/.kb-sync-stuck")"

# --- GitHub answers for the public clone, refuses the private one ----------
git -C "$INT" remote set-url origin "$SANDBOX/remotes/gone.git"
sync
grep -q '^Internal KB auto-sync is failing on this machine (fetch refused' "$INT/.kb-sync-stuck" 2>/dev/null && ok \
  || fail "refused internal fetch writes a marker" "fetch refused" "$(cat "$INT/.kb-sync-stuck" 2>&1)"
grep -q '^git said: .\+' "$INT/.kb-sync-stuck" && ok || fail "marker quotes git's error" "git said: <msg>" "$(cat "$INT/.kb-sync-stuck")"
case "$(synclog 1)" in *"STUCK: internal KB fetch refused"*) ok ;;
  *) fail "refused internal fetch logged" "STUCK: internal KB fetch refused" "$(synclog 1)" ;; esac

# --- fully offline: nothing to report --------------------------------------
rm -f "$INT/.kb-sync-stuck"
git -C "$PUB" remote set-url origin "$SANDBOX/remotes/gone.git"
sync
[ ! -e "$INT/.kb-sync-stuck" ] && ok || fail "offline is not flagged" "no marker" "$(cat "$INT/.kb-sync-stuck")"
git -C "$PUB" remote set-url origin "$PUBR"
git -C "$INT" remote set-url origin "$INTR"

# --- the public stuck marker still works (shares ff_stuck) -----------------
remote_commit "$PUBR" f.md
echo "local edit" >> "$PUB/f.md"
sync
grep -q '^KB auto-sync is failing on this machine (ff-only pull refused)' "$PUB/.kb-sync-stuck" 2>/dev/null && ok \
  || fail "public refusal keeps its marker text" "KB auto-sync is failing" "$(cat "$PUB/.kb-sync-stuck" 2>&1)"
git -C "$PUB" checkout --quiet -- f.md
sync
[ ! -e "$PUB/.kb-sync-stuck" ] && ok || fail "public marker clears" "no marker" "$(cat "$PUB/.kb-sync-stuck")"

# --- no internal clone: each skip reason is logged, never a marker ---------
rm -rf "$INT"
FAKE_GH=noauth sync
case "$(synclog 1)" in *"internal KB not cloned: gh not logged in"*) ok ;;
  *) fail "gh not logged in is logged" "gh not logged in" "$(synclog 1)" ;; esac
FAKE_GH=noaccess sync
case "$(synclog 1)" in *"internal KB not cloned: this GitHub account has no access"*) ok ;;
  *) fail "no access is logged" "no access" "$(synclog 1)" ;; esac
[ ! -e "$INT" ] && ok || fail "skips create nothing" "no internal dir" "$(ls -a "$INT")"
sync
[ -d "$INT/.git" ] && ok || fail "with access, the internal KB is cloned" "$INT/.git" "missing"
case "$(synclog 1)" in *"cloned internal KB ->"*) ok ;; *) fail "clone logged" "cloned internal KB" "$(synclog 1)" ;; esac

printf '\n\033[32mOK\033[0m — %d checks passed\n' "$pass"
