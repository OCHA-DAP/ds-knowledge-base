# KB access visibility v2 — intent + measurement — design

**Date:** 2026-09-17 (revised 2026-09-28 after review of [#630](https://github.com/OCHA-DAP/ds-knowledge-base/pull/630))
· **Status:** approved · **Decision log:** D112 in [DESIGN.md](../../DESIGN.md)
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
intent now outranks purity of the adoption signal). Recorded as D112.

### Hook channel (`kb_activity.sh` + `hooks.json`)

| change | why |
|---|---|
| Log lines stamped `<project>/<session8>` — in `kb_sync.sh`'s `slog` as well as `kb_activity.sh` | concurrent sessions were indistinguishable in the shared log; a stamp on only some lines would break a column filter |
| Read tracking moves PreToolUse → **PostToolUse** | the hook now runs after the call, so it can size what actually came back |
| **`PostToolUseFailure` + `PermissionDenied`** registered on the same matcher, logged as `ATTEMPT` and never tallied | `PostToolUse` fires *only on success*, so the move above would have silently dropped the two cases the visibility work most wants — a denied read of the internal clone from an unrelated project, and a guessed non-existent page (the missing/mis-titled-page signal). Logging but not tallying keeps the rollup honest: it counts what actually entered context |
| Per-turn tally file (`$TMPDIR/ds-team-tally-<sid>`): line 1 `#<prompt snippet>`, then `bytes rel_path` per read | one file per session instead of three; it doubles as the turn flag (no read lines yet = first read of the turn), and the snippet travels with the reads it explains |
| New **Stop** event: one rollup notice per turn with KB reads — *"📖 turn read N× from KB (~X tok est.) — page1, page2 +k more"*; log line adds the prompt snippet | "how much" was invisible: 1 read and 15 reads looked identical in chat |
| An **interrupted turn** (Esc — Stop never fires) is flushed to the log as `ROLLUP interrupted turn: …` at the next UserPromptSubmit | otherwise those reads were discarded at the next prompt, so the audit trail silently lost a turn the chat never reported either |
| **Stop keeps the snippet, drops the reads** | a blocking Stop hook elsewhere can continue the same turn; the continued reads then tally fresh and re-announce 📖 under the same prompt (two rollups, both attributed correctly) rather than merging into a rollup already sent |
| The **stuck-sync warning moves to the end of the prompt arm** (no early `exit 0`) | it used to return before the snippet was written, so the next rollup was attributed to a *previous* turn's prompt (worse on `--resume`: a days-old snippet) and the PROMPT line was skipped, manufacturing the spec's own "READ without PROMPT = suspicious" case |
| Sizes are the **whole hook payload**, not a slice at the result key | the payload key for tool output is not contractually documented (the hooks reference truncates before the PostToolUse schema), so keying off its name risks silently reporting 0 bytes if it is ever renamed — and the earlier `${INPUT%%"tool_response"*}` split truncated at the *first* literal occurrence anywhere, so a `Grep` whose **pattern** was `tool_response` vanished from tracking entirely. Whole-payload bytes cannot be broken by key order or renames; they overstate by a few hundred bytes of hook metadata, hence "est." wherever they surface |
| Prompt snippet capped at 70 **characters in the caller's locale**, read back whole | capping at 70 chars but re-reading with `head -c 70` split a UTF-8 sequence, making the entire log line un-greppable in a UTF-8 locale (any accented/French prompt) |
| Tally written under `umask 077`; **`SessionEnd`** removes the session's temp files | the file holds prompt text and was world-readable, and nothing ever deleted it (`%TEMP%` on Windows is never auto-cleared) |
| 🧭 **demoted to log-only** | a word match can't tell a team question from an unrelated project that says "pipeline"; its inline false positives trained users to ignore all notices. The skill's announce line is the replacement "should it have fired" signal in chat; the log keeps the funnel analysis |
| **Hot path**: exit before reading stdin when no clone is configured; `LC_ALL=C` on read events; parse only the first 8 KiB; fork-free field extraction; log rotation only on the once-per-turn arms | Read/Grep/Glob fire constantly in *every* project. Measured on an 840 KB payload: 143 → 43 ms per KB read, and 115 → 13 ms in projects with no clone configured (the majority case, where the script should do nothing at all) |

The spoof rationale from the first draft is **dropped, not fixed**: JSON always
escapes quotes inside content, so `\"file_path\"` in a file's text can never match
the `"file_path"` the extractor looks for — verified. The guard it justified was
buying nothing and cost the `Grep`-for-`tool_response` bug above.

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

## Known limits, accepted

- A turn continued by another plugin's blocking Stop hook reports as two rollups
  under one prompt (see the table) — legible, but not one line.
- Interrupted turns reach the log, never the chat: no hook fires at interrupt time.
- `PermissionDenied` is documented as firing when *auto mode* denies a call; whether
  every interactive denial reaches a hook is unverified, so ATTEMPT coverage of
  denials is best-effort, not a guarantee.

## Alternatives rejected

- **Rollup-only, no skill announce** — hooks can never know intent; the "why" would
  stay inferred from prompt keywords, which is exactly what cried wolf.
- **Announce via hook stdout ("nudge mode")** — injects into context on every
  prompt, contaminating measurement and costing tokens session-wide; the skill
  instruction fires only when the skill does.
- **Removing 🧭 entirely** — the log line still feeds funnel analysis
  (PROMPT-without-READ = triggering gap; READ-without-PROMPT = suspicious).
- **Keeping PreToolUse *alongside* PostToolUse** to preserve attempt logging — two
  hook runs per read on the hot path, for what the failure/denied events give with
  one (and only when something actually goes wrong).
- **jq / structured parsing** — same portability rule as D96; byte arithmetic plus
  fork-free prefix stripping is enough, and faster than the sed pipelines it replaces.

## Testing

`scripts/test_kb_activity.sh` — 24 checks in a sandboxed `HOME`/`TMPDIR`, including a
named regression case for each bug found in review (the `tool_response` grep, the
UTF-8 log truncation, the stuck-sync prompt misattribution, attempts excluded from the
rollup, the 0600 tally, SessionEnd cleanup, and the no-clone no-op).
`scripts/check_claude_assets.py` covers the plugin manifest, description caps, hook
scripts' existence and executability, and absolute-path leaks.
