# ds-team activity notices — design

**Date:** 2026-08-03 · **Status:** approved · **Decision log:** D95 in [DESIGN.md](../../DESIGN.md)

## Problem

Team members can't tell when the `ds-team` plugins are actually being invoked, so
they can't assess whether the plugins help or hinder their workflow. The plugin's
work (skill launches, KB consultations, the session-start sync) is invisible unless
you open the transcript view.

## Goal

Make plugin activity visible — full-funnel: *should it have triggered* (prompt looks
KB-relevant) → *did it trigger* (skill invoked) → *was the KB actually consulted*
(clone reads) → *is the clone fresh* (sync outcome). Two surfaces:

1. **Inline chat notices** (`systemMessage`) — zero setup, every teammate sees them.
   Emoji-coded (🧭 📚 📖 ⚠️), because ANSI doesn't render on all surfaces.
2. **A colored log file** — `~/.claude/ds-team-activity.log`, ANSI-colored, for
   anyone who wants a dedicated `tail -f` activity pane.

Everything ships **inside the `kb-access` plugin** (hooks travel with the plugin);
personal `~/.claude/settings.json` is never touched.

## Non-goals

- **No behavior nudging.** The prompt-routing hook emits via `systemMessage` only,
  never stdout — stdout would inject into Claude's context and change the behavior
  being measured. A "nudge mode" is a possible future, separate toggle.
- No status-line integration (that's a personal setting a plugin can't ship).
- No central telemetry — this is local observability, not the `kb_usage` pipeline.

## Design

One new script, `claude/plugins/kb-access/scripts/kb_activity.sh <event>`, invoked
by three new entries in the existing `kb-access/hooks/hooks.json`. It reads the
hook's JSON from stdin, appends an ANSI-colored line to the log, and emits
`{"systemMessage": "…"}` when the event warrants an inline notice.

### Hooks

| event | matcher | behavior |
|---|---|---|
| PreToolUse | `Skill` | Skill name prefix ∈ `kb-access\|data-access\|data-conventions\|aa-methods\|infra-ops` → inline `📚 ds-team: <skill> invoked` + cyan log line. Prefix matching = new skills covered automatically. |
| PreToolUse | `Read\|Grep\|Glob` | Target path inside the public or internal KB clone → green log line (relative path); inline `📖 ds-team: consulting KB (…)` only on the **first** KB read of the turn (flag file `$TMPDIR/ds-team-turn-<session_id>`). |
| UserPromptSubmit | — | Deletes the turn flag (turn boundary). Keyword regex over the prompt → inline `🧭 ds-team: prompt looks KB-relevant`. Also warns `⚠️ KB auto-sync stuck — run kb-doctor` once per session if `.kb-sync-stuck` exists (the sync hook is async, so its own output can't reliably reach chat; the next prompt is the dependable path). |

`kb_sync.sh` additionally appends its outcome (ok @ SHA / stuck / cloned) to the
same log — that plus the stuck warning covers the sync-visibility signal.

### Clone-path resolution

Same as `kb_sync.sh`, deliberately: `$KB_REPOS_DIR`, else `~/.claude/.kb-repos-dir`,
else exit 0 silently. Both `ds-knowledge-base` and `ds-knowledge-base-internal`
count as KB reads.

### Error handling & portability

- Never break a session: every path exits 0, all writes best-effort, hook timeouts
  ~10 s.
- Same portability discipline as `kb_sync.sh`: plain bash, runs under Git Bash on
  Windows, **no jq** — the three fields needed (skill name, file path, prompt) are
  pulled with sed. Crude, but the failure mode is a missed/spurious notice, never a
  broken hook.
- Log size-capped: rotate to `.old` at ~1 MB (`wc -c`, portable).

### Testing

Smoke tests pipe canned hook-JSON into the script per event (commands documented in
the script header); then one live-session verification (🧭 → 📚 → 📖 inline,
colored stream in `tail -f`).

### Docs

- `docs/USING.md`: "Watching the plugins work" — what each emoji means, the
  `tail -f` command.
- `docs/DESIGN.md`: dated D95 entry (observation-only rationale).

## Alternatives rejected

- **Separate opt-in `ds-team-activity` plugin** — cleanly separable, but default-off
  for existing installs defeats the purpose (discovery requires it to be on).
- **Hooks in each of the five plugins** — best attribution, but 5× boilerplate and
  plugins can't share scripts. One hook in `kb-access` (the anchor plugin) matching
  on plugin prefix covers all five.
