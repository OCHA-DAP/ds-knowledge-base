---
name: kb-search
description: Search the OCHA CHD Data Science team knowledge base (the local ds-knowledge-base clone) before answering ANY team question — AA frameworks and triggers, pipelines, apps, infrastructure, blob/DB layout, methods, libraries, past decisions. Also covers how to update the KB after real work and how to report gaps. If a .kb-sync-stuck file exists at the clone root, tell the user their KB auto-sync is failing (this skill has the fix steps). If no clone exists yet, help the user choose where it goes (this skill has the steps) — it is never cloned to an unchosen location.
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

- **Search the KB first** for team questions (frameworks/triggers, what feeds a
  pipeline, blob/DB conventions, past decisions) — grep/read the clone rather than
  answering from memory. Start from the repo's `CLAUDE.md` map.
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
  `<!-- TODO: ... -->` stub in the page.
- **Editing the KB locally: never `git switch` the clone — use a worktree.** The clone
  is shared (concurrent sessions + this plugin's auto-sync read it in place):
  `git worktree add ../ds-knowledge-base.worktrees/<branch> -b <branch> origin/main`,
  commit there with explicit pathspecs, push, PR (merge commit, not squash), remove
  the worktree after merge.
- If `.kb-sync-stuck` exists at the clone root, auto-sync is failing on this machine —
  tell the user and run the `kb-doctor` skill. Usual cause: local changes or a
  checked-out branch blocking the ff-only pull.
