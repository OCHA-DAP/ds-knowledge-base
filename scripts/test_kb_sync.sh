#!/usr/bin/env bash
# Smoke tests for claude/plugins/kb-access/scripts/kb_sync.sh — chiefly the
# internal-clone flagging of D123, plus the public stuck marker it shares code with.
#
# Runs in a sandboxed HOME with local bare repos standing in for GitHub, a fake
# `gh` and a fake git remote helper (to replay GitHub's auth errors) on PATH, so it
# never touches the network, a real clone or the real activity log. Usage, from
# the repo root:
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
export GIT_CONFIG_NOSYSTEM=1
export GIT_AUTHOR_NAME=t GIT_AUTHOR_EMAIL=t@example.org
export GIT_COMMITTER_NAME=t GIT_COMMITTER_EMAIL=t@example.org
mkdir -p "$HOME/.claude" "$KB_REPOS_DIR" "$SANDBOX/bin" "$SANDBOX/remotes"
LOG="$HOME/.claude/ds-team-activity.log"
PUB="$KB_REPOS_DIR/ds-knowledge-base"
INT="$KB_REPOS_DIR/ds-knowledge-base-internal"
PUBR="$SANDBOX/remotes/pub.git"
INTR="$SANDBOX/remotes/int.git"

# Fake gh: FAKE_GH=noauth|noaccess|noclone fails at that step; `repo clone` clones $INTR.
cat > "$SANDBOX/bin/gh" <<EOF
#!/usr/bin/env bash
case "\$1 \$2" in
  "auth status") [ "\${FAKE_GH:-}" != noauth ] ;;
  "repo view")   [ "\${FAKE_GH:-}" != noaccess ] ;;
  "repo clone")  [ "\${FAKE_GH:-}" != noclone ] && git clone --quiet "$INTR" "\$4" ;;
  *) exit 1 ;;
esac
EOF
# Fake remote helper: a remote URL `fake::x` fails every fetch with $FAKE_REMOTE_ERR.
cat > "$SANDBOX/bin/git-remote-fake" <<'EOF'
#!/usr/bin/env bash
echo "${FAKE_REMOTE_ERR:-fatal: Authentication failed for 'https://github.com/OCHA-DAP/x.git/'}" >&2
exit 128
EOF
chmod +x "$SANDBOX/bin/gh" "$SANDBOX/bin/git-remote-fake"
export PATH="$SANDBOX/bin:$PATH"

pass=0
fail() { printf '\n\033[31mFAIL\033[0m %s\n  expected: %s\n  actual:   %s\n' "$1" "$2" "$3"; exit 1; }
ok()   { pass=$((pass + 1)); printf '.'; }

sync() { printf '%s' '{"session_id":"sync1234abcd","cwd":"/x/myproj"}' | bash "$SCRIPT"; }
synclog() { sed 's/\x1b\[[0-9;]*m//g' "$LOG" 2>/dev/null | tail -n "${1:-1}"; }
marker() { cat "$1/.kb-sync-stuck" 2>&1; }
remote_commit() { # remote_commit <bare> <file> — push one commit changing <file>
  local w="$SANDBOX/work-$$-$RANDOM"
  git clone --quiet "$1" "$w" && echo "$RANDOM" >> "$w/$2" \
    && git -C "$w" add "$2" && git -C "$w" commit --quiet -m "$2" \
    && git -C "$w" push --quiet origin HEAD:main && rm -rf "$w"
}

# Seed both "GitHub" repos with one commit on main (no `init -b`: works on old git).
git init --quiet "$SANDBOX/seed"
git -C "$SANDBOX/seed" symbolic-ref HEAD refs/heads/main
echo seed > "$SANDBOX/seed/f.md"
git -C "$SANDBOX/seed" add f.md && git -C "$SANDBOX/seed" commit --quiet -m seed
git clone --quiet --bare "$SANDBOX/seed" "$PUBR"
git clone --quiet --bare "$SANDBOX/seed" "$INTR"
git clone --quiet "$PUBR" "$PUB"
git clone --quiet "$INTR" "$INT"
[ "$(git -C "$INT" branch --show-current)" = main ] || fail "sandbox setup" "clone on main" "$(git -C "$INT" branch --show-current)"

# --- both clones healthy ---------------------------------------------------
remote_commit "$INTR" f.md
sync
[ ! -e "$INT/.kb-sync-stuck" ] && ok || fail "healthy internal clone has no marker" "no marker" "$(marker "$INT")"
[ "$(git -C "$INT" rev-parse HEAD)" = "$(git -C "$INTR" rev-parse main)" ] && ok \
  || fail "internal clone fast-forwarded" "at remote main" "$(git -C "$INT" log --oneline -1)"
case "$(synclog 1)" in *"SYNC   internal ok @"*) ok ;; *) fail "internal success logged" "internal ok @" "$(synclog 1)" ;; esac

# --- internal ff-only pull refused by a local edit -------------------------
remote_commit "$INTR" f.md
echo "local edit" >> "$INT/f.md"
sync
grep -q '^Internal KB auto-sync is failing on this machine (ff-only pull refused)' "$INT/.kb-sync-stuck" 2>/dev/null && ok \
  || fail "internal ff-only refusal writes a marker" "Internal KB ... ff-only pull refused" "$(marker "$INT")"
grep -q '^behind origin/main by: 1 commit' "$INT/.kb-sync-stuck" && grep -q '^ M f.md' "$INT/.kb-sync-stuck" && ok \
  || fail "marker says how far behind and what blocks it" "behind 1 + ' M f.md'" "$(marker "$INT")"
grep -q 'kb-sync-stuck' <(sed 1d "$INT/.kb-sync-stuck") && fail "marker does not list itself" "no self-listing" "$(marker "$INT")" || ok
case "$(synclog 1)" in *"STUCK: internal KB ff-only pull refused, 1 behind"*) ok ;;
  *) fail "internal refusal logged" "STUCK: internal KB ff-only" "$(synclog 1)" ;; esac
[ ! -e "$PUB/.kb-sync-stuck" ] && ok || fail "public clone unaffected" "no public marker" "$(marker "$PUB")"

# --- the next good pull clears it ------------------------------------------
git -C "$INT" checkout --quiet -- f.md
sync
[ ! -e "$INT/.kb-sync-stuck" ] && ok || fail "successful pull clears the internal marker" "no marker" "$(marker "$INT")"

# --- a clean main that lost a race with a concurrent sync is not flagged ----
remote_commit "$INTR" f.md
: > "$INT/.git/index.lock"
sync
[ ! -e "$INT/.kb-sync-stuck" ] && ok || fail "lock-file race is not flagged" "no marker" "$(marker "$INT")"
case "$(synclog 1)" in *"internal KB pull refused with nothing local blocking it"*) ok ;;
  *) fail "lock-file race logged" "nothing local blocking it" "$(synclog 1)" ;; esac
rm -f "$INT/.git/index.lock"
sync

# --- detached HEAD behind main is flagged, and says so ---------------------
remote_commit "$INTR" f.md
git -C "$INT" checkout --quiet --detach
sync
grep -q '^branch: (detached HEAD)' "$INT/.kb-sync-stuck" 2>/dev/null && ok \
  || fail "detached HEAD flagged and named" "branch: (detached HEAD)" "$(marker "$INT")"
git -C "$INT" checkout --quiet main
sync

# --- GitHub answers for the public clone, refuses the private one ----------
git -C "$INT" remote set-url origin fake::int
sync
grep -q '^Internal KB auto-sync is failing on this machine (fetch refused' "$INT/.kb-sync-stuck" 2>/dev/null && ok \
  || fail "auth-refused internal fetch writes a marker" "fetch refused" "$(marker "$INT")"
grep -q "^git said: fatal: Authentication failed for 'https://github.com/OCHA-DAP/x.git/'" "$INT/.kb-sync-stuck" && ok \
  || fail "marker quotes git's error" "git said: fatal: Authentication failed" "$(marker "$INT")"
case "$(synclog 1)" in *"STUCK: internal KB fetch refused"*) ok ;;
  *) fail "refused internal fetch logged" "STUCK: internal KB fetch refused" "$(synclog 1)" ;; esac
rm -f "$INT/.kb-sync-stuck"
FAKE_REMOTE_ERR="remote: Repository not found." sync
[ -e "$INT/.kb-sync-stuck" ] && ok || fail "'Repository not found' counts as no access" "marker" "none"
rm -f "$INT/.kb-sync-stuck"
FAKE_REMOTE_ERR="fatal: unable to access 'https://x:tok@github.com/OCHA-DAP/x.git/': The requested URL returned error: 502" sync
[ ! -e "$INT/.kb-sync-stuck" ] && ok || fail "a 5xx is transient, not flagged" "no marker" "$(marker "$INT")"
case "$(synclog 1)" in *"internal KB fetch failed, not an access error"*"https://github.com/OCHA-DAP"*) ok ;;
  *) fail "transient fetch error logged, token stripped" "not an access error … https://github.com/…" "$(synclog 1)" ;; esac

# --- a stale marker clears once the fetch works and nothing is behind ------
echo "Internal KB auto-sync is failing on this machine (fetch refused …)." > "$INT/.kb-sync-stuck"
git -C "$INT" remote set-url origin "$INTR"
git -C "$INT" checkout --quiet --detach   # pull refused, but nothing to fetch
sync
[ ! -e "$INT/.kb-sync-stuck" ] && ok || fail "stale marker cleared when fetch works, 0 behind" "no marker" "$(marker "$INT")"
git -C "$INT" checkout --quiet main

# --- fully offline: nothing to report for either clone ---------------------
git -C "$PUB" remote set-url origin "$SANDBOX/remotes/gone.git"
git -C "$INT" remote set-url origin fake::int
sync
[ ! -e "$INT/.kb-sync-stuck" ] && [ ! -e "$PUB/.kb-sync-stuck" ] && ok \
  || fail "offline is not flagged" "no markers" "$(marker "$INT"; marker "$PUB")"
git -C "$PUB" remote set-url origin "$PUBR"
git -C "$INT" remote set-url origin "$INTR"

# --- the public stuck marker still works (shares ff_stuck) -----------------
remote_commit "$PUBR" f.md
echo "local edit" >> "$PUB/f.md"
sync
grep -q '^KB auto-sync is failing on this machine (ff-only pull refused)' "$PUB/.kb-sync-stuck" 2>/dev/null && ok \
  || fail "public refusal keeps its marker text" "KB auto-sync is failing" "$(marker "$PUB")"
git -C "$PUB" checkout --quiet -- f.md
sync
[ ! -e "$PUB/.kb-sync-stuck" ] && ok || fail "public marker clears" "no marker" "$(marker "$PUB")"

# --- no internal clone: each skip reason is logged, never a marker ---------
rm -rf "$INT"
FAKE_GH=noauth sync
case "$(synclog 1)" in *"internal KB not cloned: gh not logged in"*) ok ;;
  *) fail "gh not logged in is logged" "gh not logged in" "$(synclog 1)" ;; esac
FAKE_GH=noaccess sync
case "$(synclog 1)" in *"internal KB not cloned: this GitHub account has no access"*) ok ;;
  *) fail "no access is logged" "no access" "$(synclog 1)" ;; esac
FAKE_GH=noclone sync
case "$(synclog 1)" in *"internal KB clone failed"*) ok ;;
  *) fail "failed clone is logged" "clone failed" "$(synclog 1)" ;; esac
[ ! -e "$INT/.kb-sync-stuck" ] && ok || fail "skips write no marker" "no marker" "$(ls -a "$INT")"
sync
[ -d "$INT/.git" ] && ok || fail "with access, the internal KB is cloned" "$INT/.git" "missing"
case "$(synclog 1)" in *"cloned internal KB ->"*) ok ;; *) fail "clone logged" "cloned internal KB" "$(synclog 1)" ;; esac

printf '\n\033[32mOK\033[0m — %d checks passed\n' "$pass"
