# ds-team Activity Notices Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make ds-team plugin activity visible — inline emoji chat notices + an ANSI-colored log file — via hooks shipped inside the `kb-access` plugin.

**Architecture:** One event-dispatching bash script (`kb_activity.sh`) driven by three new hook entries in `kb-access/hooks/hooks.json` (PreToolUse×2, UserPromptSubmit); `kb_sync.sh` gains log-append lines. Spec: `docs/superpowers/specs/2026-08-03-ds-team-activity-notices-design.md`.

**Tech Stack:** Plain bash (Git-Bash-portable, no jq), Claude Code plugin hooks.

## Global Constraints

- Never break a session: every script path exits 0; all writes best-effort (`2>/dev/null || true`); hook timeouts 10 s.
- No jq / python dependency in hook scripts — sed/grep field extraction only (matches `kb_sync.sh` discipline).
- Inline notices via `{"systemMessage": …}` **only** — never plain stdout on UserPromptSubmit (plain stdout would inject into model context; observation must not nudge behavior).
- At most ONE JSON object on stdout per hook run.
- Clone-dir resolution identical to `kb_sync.sh`: `$KB_REPOS_DIR` else `~/.claude/.kb-repos-dir` else silent exit.
- Log file `~/.claude/ds-team-activity.log`, rotate to `.old` above 1 MB.
- No `version` fields anywhere (CI rejects them); do not declare `./hooks/hooks.json` in `plugin.json` (CI rejects that too — auto-loaded by convention).
- Commits: no Co-Authored-By / AI attribution lines.

---

### Task 1: `kb_activity.sh` — the event dispatcher

**Files:**
- Create: `claude/plugins/kb-access/scripts/kb_activity.sh` (mode 755)

**Interfaces:**
- Consumes: hook JSON on stdin; `$1` ∈ `skill|read|prompt`.
- Produces: at most one `{"systemMessage":"…"}` on stdout; ANSI lines appended to `~/.claude/ds-team-activity.log`. Task 2 wires it into `hooks.json` as `bash "${CLAUDE_PLUGIN_ROOT}/scripts/kb_activity.sh" <event>`.

- [ ] **Step 1: Write the script**

```bash
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
# Design (spec: docs/superpowers/specs/2026-08-03-ds-team-activity-notices-design.md):
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
#   KB_REPOS_DIR=/tmp/kbsmoke printf '{"session_id":"s1","tool_name":"Read","tool_input":{"file_path":"/tmp/kbsmoke/ds-knowledge-base/methods/x.md"}}' \
#     | bash claude/plugins/kb-access/scripts/kb_activity.sh read
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
  [ "$(wc -c < "$LOG" 2>/dev/null || echo 0)" -gt 1048576 ] 2>/dev/null \
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
```

- [ ] **Step 2: `chmod +x` the script**

Run: `chmod +x claude/plugins/kb-access/scripts/kb_activity.sh` (matches `kb_sync.sh`'s mode).

- [ ] **Step 3: Run the header smoke tests**

Run each smoke-test command from the script header, from the worktree root, plus the negative cases. For the `read` test, first `mkdir -p /tmp/kbsmoke/ds-knowledge-base` and use `env KB_REPOS_DIR=… sh -c '…'` so the env var reaches the script. Expected outputs are in the header comments; also verify:
- second `read` call in the same "turn" prints nothing (flag file exists)
- `prompt` then `read` prints the 📖 notice again (flag was reset)
- `bash …/kb_activity.sh skill < /dev/null; echo $?` → `0` (empty stdin safe)
- `tail -3 ~/.claude/ds-team-activity.log` shows colored SKILL/READ/PROMPT lines

- [ ] **Step 4: Commit**

```bash
git add claude/plugins/kb-access/scripts/kb_activity.sh
git commit -m "feat(kb-access): activity dispatcher script for plugin observability"
```

---

### Task 2: Wire the hooks + sync-outcome logging

**Files:**
- Modify: `claude/plugins/kb-access/hooks/hooks.json` (add PreToolUse + UserPromptSubmit)
- Modify: `claude/plugins/kb-access/scripts/kb_sync.sh` (append outcomes to the log)

**Interfaces:**
- Consumes: `kb_activity.sh <event>` from Task 1.
- Produces: the live hook wiring; `SYNC` lines in the shared log.

- [ ] **Step 1: Replace `hooks.json` with**

```json
{
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "bash \"${CLAUDE_PLUGIN_ROOT}/scripts/kb_sync.sh\"",
            "timeout": 300,
            "async": true,
            "statusMessage": "Syncing team KB"
          }
        ]
      }
    ],
    "PreToolUse": [
      {
        "matcher": "Skill",
        "hooks": [
          {
            "type": "command",
            "command": "bash \"${CLAUDE_PLUGIN_ROOT}/scripts/kb_activity.sh\" skill",
            "timeout": 10
          }
        ]
      },
      {
        "matcher": "Read|Grep|Glob",
        "hooks": [
          {
            "type": "command",
            "command": "bash \"${CLAUDE_PLUGIN_ROOT}/scripts/kb_activity.sh\" read",
            "timeout": 10
          }
        ]
      }
    ],
    "UserPromptSubmit": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "bash \"${CLAUDE_PLUGIN_ROOT}/scripts/kb_activity.sh\" prompt",
            "timeout": 10
          }
        ]
      }
    ]
  }
}
```

- [ ] **Step 2: Add sync logging to `kb_sync.sh`**

After the `INT=` line (line 25), insert:

```bash
# sync outcomes also land in the shared activity log (see kb_activity.sh)
ALOG="$HOME/.claude/ds-team-activity.log"
slog() {
  printf '\033[2m%s\033[0m \033[33m%-6s\033[0m %s\n' \
    "$(date '+%H:%M:%S')" SYNC "$1" >> "$ALOG" 2>/dev/null || true
}
```

Then three call sites, each one line:
- inside the successful-clone branch (after the `git clone … || exit 0` line): `slog "cloned public KB -> $PUB"`
- in the pull-success branch (next to `rm -f "$PUB/.kb-sync-stuck"`): `slog "ok @ $(git -C "$PUB" rev-parse --short HEAD 2>/dev/null || echo '?')"`
- in the stuck branch (after the marker heredoc block): `slog "STUCK: ff-only pull refused, $behind behind (kb-doctor has the fix)"`

- [ ] **Step 3: Validate**

Run:
- `python3 -m json.tool claude/plugins/kb-access/hooks/hooks.json` → parses
- `bash -n claude/plugins/kb-access/scripts/kb_sync.sh` → no output
- `python3 scripts/check_claude_assets.py` → exit 0 (it verifies hook-referenced scripts exist)

- [ ] **Step 4: Commit**

```bash
git add claude/plugins/kb-access/hooks/hooks.json claude/plugins/kb-access/scripts/kb_sync.sh
git commit -m "feat(kb-access): wire activity hooks; log sync outcomes"
```

---

### Task 3: Docs — USING.md section + DESIGN.md D93

**Files:**
- Modify: `docs/USING.md` (new section immediately before `## No-install options`)
- Modify: `docs/DESIGN.md` (new dated section before `## Open questions`)

- [ ] **Step 1: Add to USING.md**

```markdown
## Watching the plugins work

`kb-access` ships activity hooks (D93) so you can *see* the plugins working instead
of taking it on faith — the point is judging whether they help your workflow. Inline
notices in chat:

- 🧭 *prompt looks team-KB-relevant* — your prompt matched KB keywords. If no 📚/📖
  follows on a question the KB should answer, that's a triggering gap — please
  report it (`kb-feedback` issue).
- 📚 *`<skill>` invoked* — a ds-team plugin skill actually launched.
- 📖 *consulting KB (…)* — Claude is reading your local KB clone (shown once per
  turn; every individual file is in the log).
- ⚠️ *KB auto-sync is stuck* — your clone can't fast-forward; `kb-doctor` has the fix.

The full firehose — every KB file read, sync outcomes — goes to an ANSI-colored log
you can keep open in a side pane:

​```bash
tail -f ~/.claude/ds-team-activity.log
​```

Observation only: notices go to **you**, never into Claude's context, so watching
doesn't change the behavior you're judging.
```

(Remove the zero-width guards around the inner code fence when pasting.)

- [ ] **Step 2: Add to DESIGN.md** (before `## Open questions`)

```markdown
### 2026-08-03 — plugin activity notices

- **D93 · The kb-access plugin ships observation-only activity hooks — inline emoji notices + a colored local log — so teammates can SEE the plugins working** (user, 2026-08-03). Problem: plugin activity is invisible, so nobody can judge whether ds-team plugins help or hinder (and D85's recorded gap stands: local-grep access produces no usage telemetry). Full-funnel visibility via three hooks in `kb-access` + `kb_activity.sh`: 🧭 UserPromptSubmit keyword match ("should it trigger?") → 📚 PreToolUse(Skill) with **plugin-prefix** matching, so all five plugins' skills are covered with no per-skill drift ("did it trigger?") → 📖 PreToolUse(Read|Grep|Glob) path-filtered to the clones, inline once per turn, every file to the log ("was the KB consulted?") → SYNC outcomes from `kb_sync.sh` + a once-per-session ⚠️ stuck warning ("is the clone fresh?"). Two surfaces: `systemMessage` inline (emoji-coded — ANSI doesn't render on all surfaces) and `~/.claude/ds-team-activity.log` (ANSI-colored, `tail -f`-able, 1 MB rotation). **Deliberately observation-only**: the routing notice goes out via `systemMessage`, never stdout — UserPromptSubmit stdout injects into model context and would *nudge* Claude toward the KB, contaminating the help-or-hinder measurement a notice exists to enable; a nudge mode would be a separate, explicit toggle. Ships in the plugin (hooks travel with it; personal settings untouched). Same portability discipline as `kb_sync.sh`: plain bash, Git-Bash-safe, no jq (sed extraction; worst failure = a missed notice, never a broken hook, always exit 0). Rejected: a separate opt-in `ds-team-activity` plugin (default-off defeats discovery); per-plugin hooks (5× boilerplate, plugins can't share scripts). Known limits, accepted: keyword list is static (tune as false hits/misses show up); Windows path-form mismatches may under-detect 📖 (benign); local-only — this is not the `kb_usage` telemetry pipeline, though it's a step toward D84's "qualitative team signal" revisit trigger.
```

- [ ] **Step 3: Verify + commit**

Run: `python3 scripts/check_links.py` (the CI link check) → no new errors.

```bash
git add docs/USING.md docs/DESIGN.md
git commit -m "docs: watching-the-plugins-work section + D93 decision entry"
```

---

### Task 4: Push + PR

- [ ] **Step 1:** `git push -u origin plugin-activity-notices`
- [ ] **Step 2:** `gh pr create` (title "kb-access: activity notices — see the plugins working"; body summarizes spec, links D93; note the plugin paths are code-ownered so the PR needs @t-downing/@zackarno review per the D85 ruleset).
