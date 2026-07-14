---
name: kb-search
description: Search the OCHA CHD Data Science team knowledge base (the local ds-knowledge-base clone) before answering ANY team question — AA frameworks and triggers, pipelines, apps, infrastructure, blob/DB layout, methods, libraries, past decisions. Also covers how to update the KB after real work and how to report gaps.
---

# Team knowledge base

The team KB (hub) is a local clone of `OCHA-DAP/ds-knowledge-base`, organized as
`frameworks/`, `pipelines/`, `apps/`, `analysis/`, `methods/`, `infrastructure/`,
`assets/`. This plugin's SessionStart hook keeps it (and the internal companion
`ds-knowledge-base-internal`, for users with access) cloned and on current main.

**Where it is** — first match wins: `$KB_REPOS_DIR` → the path in
`~/.claude/.kb-repos-dir` → `~/OCHA/repos`. If it's missing everywhere, the hook
hasn't run yet or failed — see the `kb-doctor` skill.

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
