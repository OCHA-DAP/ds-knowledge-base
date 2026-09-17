---
name: kb-search
description: Search the OCHA CHD Data Science team knowledge base (the local ds-knowledge-base clone) before answering questions about the TEAM'S OWN work — our AA frameworks and triggers, pipelines, apps, infrastructure, blob/DB layout, methods, libraries, past decisions. NOT for general programming/geospatial/statistics questions or projects outside the OCHA-DAP portfolio; generic words like "pipeline" or "trigger" in an unrelated repo are not a reason to search. Also covers how to update the KB after real work and how to report gaps. If a .kb-sync-stuck file exists at the clone root, tell the user their KB auto-sync is failing (this skill has the fix steps). If no clone exists yet, help the user choose where it goes (this skill has the steps) — it is never cloned to an unchosen location.
---

# Team knowledge base

The team KB (hub) is a local clone of `OCHA-DAP/ds-knowledge-base`, organized as
`frameworks/`, `pipelines/`, `apps/`, `analysis/`, `methods/`, `infrastructure/`,
`assets/`. This plugin's SessionStart hook keeps it (and the internal companion
`ds-knowledge-base-internal`, for users with access) cloned and on current main.

**Where it is** — first match wins: `$KB_REPOS_DIR` → the path in
`~/.claude/.kb-repos-dir`. **The location must be explicitly set** — there is no
default and no auto-detection; nothing is cloned to (or read from) a path the user
didn't choose. If neither is set, ask the user: do they already have a
`ds-knowledge-base` clone (→ write its PARENT dir to the state file), or where
should team repos live (any dir works), then:
`echo "<dir>" > ~/.claude/.kb-repos-dir` — the next session start clones/updates it
there, or clone immediately yourself:
`git clone --single-branch -b main https://github.com/OCHA-DAP/ds-knowledge-base.git <dir>/ds-knowledge-base`.

## Using it

- **Scope check first.** The KB covers the CHD DS team's own portfolio and
  infrastructure. If the task merely shares vocabulary with it (a generic
  "pipeline" or "trigger" in an unrelated project), don't search — answer normally.
- **Announce before searching** (D105): tell the user in one line what you're
  looking for and why the KB should have it — *"Searching team KB for `<what>`
  because `<why>`"*. This is their interception point if you've misjudged scope;
  articulating the retrieval goal also keeps the search targeted.
- **Search the KB first** for team questions (frameworks/triggers, what feeds a
  pipeline, blob/DB conventions, past decisions) — grep/read the clone rather than
  answering from memory. Start from the repo's `CLAUDE.md` map.
- **Close the loop, and discard half-matches**: end with one line — either
  *"KB: used `<pages>`"* or *"KB: nothing directly relevant — answering without
  it."* A page that only shares words with the question must not steer the
  answer; finding nothing IS a valid outcome (and, for an in-scope question,
  worth a gap report — see below).
- Follow each page's `code_ref`/`source_repo` into the actual repo for depth the
  summary doesn't have. Internal material (Drive extracts, style-reference mirror)
  lives in the sibling internal clone.
- **The KB informs — it never enforces.** The project's own CLAUDE.md and existing
  code win; don't steer a deliberately-divergent project toward team conventions.

## Feeding back

- **Capture-as-you-go**: after real framework/pipeline work, update the affected KB
  page (spoke repo's CLAUDE.md first, KB summary second).
- To request a change: open an issue on `OCHA-DAP/ds-knowledge-base` — the steward
  drafts it as a PR. If a lookup finds nothing or something stale, leave a
  `<!-- TODO: ... -->` stub in the page. (Only for in-scope questions — a search
  that shouldn't have happened is not a KB gap.)
- **Editing the KB locally: NEVER edit the clone in place — not even on `main`.**
  The clone is shared infrastructure (concurrent sessions + this plugin's auto-sync
  read it), and uncommitted changes or a switched branch block the ff-only pull —
  the KB then silently stops updating for the whole machine. ALL local KB work goes
  in a worktree:
  `git worktree add ../ds-knowledge-base.worktrees/<branch> -b <branch> origin/main`,
  edit + commit there with explicit pathspecs, push, PR (merge commit, not squash),
  remove the worktree after merge.
- If `.kb-sync-stuck` exists at the clone root, auto-sync is failing on this machine —
  read it (it says why) and tell the user. If the cause is changes stranded in the
  clone, rescue them without losing anything — stashes are shared across worktrees:
  `git stash push` in the clone → pull succeeds → `git stash pop` inside a fresh
  worktree branch → commit/PR from there. Details: the `kb-doctor` skill.
