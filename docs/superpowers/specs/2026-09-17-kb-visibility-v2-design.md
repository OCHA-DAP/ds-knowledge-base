# KB access visibility v2 — intent + measurement — design

**Date:** 2026-09-17 · **Status:** approved · **Decision log:** D105 in [DESIGN.md](../../DESIGN.md)
· Builds on [2026-08-03-ds-team-activity-notices-design.md](2026-08-03-ds-team-activity-notices-design.md) (D96)

## Problem

Two failure modes surfaced in real use of the D96 notices:

1. **False triggering, invisible in kind.** `kb-search`'s description had no
   boundaries ("ANY team question — triggers, pipelines, apps…"), so sessions in
   unrelated projects searched the KB on vocabulary overlap alone (grep "trigger" →
   393 files match), reading half-related pages that can steer answers
   (contamination), waste ~8–15k tokens per false trigger, and — worst — file fake
   "gap reports" or stumble into the internal clone from unrelated repos.
2. **Black-box connections.** The notices say *that* the KB is being read, never
   *why* or *how much*: the 📖 notice fires on the first read only (1 page and 15
   pages look identical), PreToolUse can't see result sizes, the shared log has no
   session/project attribution, and 🧭 (a 15-word regex) cries wolf on any prompt
   containing "kb"/"pipeline"/"trigger" — eroding trust in all four emoji.

## Goal

Make every KB consultation **legible in real time** — what it's looking for, why,
and what it cost — via **two complementary channels**:

- **The skill self-reports intent** (the only true "why"): announce before
  searching, verdict after. Real-time, interruptible, but only as reliable as the
  model following instructions.
- **The hooks stay the trustless audit** (the "what, exactly"): observation-only,
  can't lie, can't know intent. A *mismatch* between the two channels is itself
  the contamination signal.

Plus: stop false triggers upstream with description scoping and an in-skill
relevance gate.

## Changes

### Skill channel (`kb-search/SKILL.md`)

- **Description scoped with negative triggers**: "questions about the TEAM'S OWN
  work… NOT for general programming/geospatial/statistics questions or projects
  outside the OCHA-DAP portfolio; generic words like 'pipeline' or 'trigger' in an
  unrelated repo are not a reason to search."
- **Scope check first** bullet: vocabulary overlap alone ≠ reason to search.
- **Announce line** before touching the clone: *"Searching team KB for `<what>`
  because `<why>`"* — the user's interception point; articulating a retrieval goal
  also reduces aimless grepping.
- **Close-the-loop line** after: *"KB: used `<pages>`"* or *"KB: nothing directly
  relevant — answering without it"* — forces an explicit relevance verdict; **half-
  matches are discarded, not used**; finding nothing is a valid outcome.
- Gap reports qualified: only for in-scope questions (a search that shouldn't have
  happened is not a KB gap — protects the feedback channel from false-trigger noise).

**Relation to D96's "no behavior nudging" non-goal:** that rule is about the *hook
channel* (hook stdout would inject into context and contaminate the "is the plugin
helping?" measurement). Instructing behavior through the *skill* is what skills are
for; the announce/close lines change what's measured (deliberately — visibility of
intent now outranks purity of the adoption signal). Recorded as D105.

### Hook channel (`kb_activity.sh` + `hooks.json`)

| change | why |
|---|---|
| Log lines stamped `<project>/<session8>` (from the hook JSON's `cwd`/`session_id`) | concurrent sessions were indistinguishable in the shared log |
| Read tracking moves PreToolUse → **PostToolUse** | the hook now sees `tool_response`, so sizes are real (bytes returned into context), not tool-launch counts |
| Per-turn tally file (`$TMPDIR/ds-team-tally-<sid>`: `bytes rel_path` lines) | feeds the rollup |
| New **Stop** event: one rollup notice per turn with KB reads — *"📖 turn read N× from KB (~X tok est.) — page1, page2 +k more"*; log line adds the prompt snippet | "how much" was invisible: 1 read and 15 reads looked identical in chat |
| 🧭 **demoted to log-only** (PROMPT line keeps the snippet) | a word match can't tell a team question from an unrelated project that says "pipeline"; its inline false positives trained users to ignore all notices. The skill's announce line is the replacement "should it have fired" signal in chat; the log keeps the funnel analysis |
| Field extraction runs on the JSON **before** `"tool_response"` | a read file's *content* containing `"file_path": …` could otherwise spoof the path match |
| Token estimate = response bytes / 4, labeled "est." | honest proxy; includes ~5 tok of JSON-overhead per read, negligible vs real page reads |

Everything else from D96 carries over unchanged: systemMessage-only output, no jq
(sed/awk, Git Bash on Windows), always exit 0, 1 MB log rotation, stuck-sync warning
once per session, first-KB-read notice (kept — it's the real-time mid-turn signal;
the rollup is the retrospective).

## Out of scope (deliberate)

- **MCP-path visibility** — sessions reaching the KB via MCP have no hooks; the
  equivalent there is announce-intent in tool descriptions + `kb_usage` telemetry
  (same two-channel pattern, different plumbing). Separate change if wanted.
- **Central telemetry for the local-clone path** (the D85 flagged gap): an opt-in
  ping into `kb_usage.events` remains open — privacy questions first.
- **Per-user enablement scope**: user-scope installs fire in unrelated projects by
  construction; the fix is enabling per-repo (D85's dial), not more notices.

## Alternatives rejected

- **Rollup-only, no skill announce** — hooks can never know intent; the "why" would
  stay inferred from prompt keywords, which is exactly what cried wolf.
- **Announce via hook stdout ("nudge mode")** — injects into context on every
  prompt, contaminating measurement and costing tokens session-wide; the skill
  instruction fires only when the skill does.
- **Removing 🧭 entirely** — the log line still feeds funnel analysis
  (PROMPT-without-READ = triggering gap; READ-without-PROMPT = suspicious).
- **jq / structured parsing for sizes** — same portability rule as D96; byte
  arithmetic on the raw JSON is enough for an estimate.

## Testing

Smoke tests in the script header (all four events + spoof-guard + silent-repeat
cases); `scripts/check_claude_assets.py` green (description caps, hook scripts
executable, no absolute user paths); one live-session verification.
