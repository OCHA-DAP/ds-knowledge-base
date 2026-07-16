---
name: kb-doctor
description: Check and repair this machine's team-KB setup — the ds-team plugin, the KB clone's presence/freshness, the sync hook, leftovers from older setups. Use when the user asks whether their KB setup works, team knowledge seems stale, kb-search finds no clone, or a .kb-sync-stuck marker appears.
---

# KB setup doctor

The contract (everything ships via the `ds-team` plugin marketplace in
`OCHA-DAP/ds-knowledge-base`; consumer docs in the KB's `docs/USING.md`):

- **Plugins**: `kb-access` (this one), optionally `data-conventions` and `hdx-brand` —
  enabled either per repo (checked-in `.claude/settings.json`:
  `extraKnownMarketplaces.ds-team` + `enabledPlugins`) or per user
  (`claude plugin install <name>@ds-team`, lands in `~/.claude/settings.json`).
- **Clones**: `ds-knowledge-base` (+ `ds-knowledge-base-internal` if the user has
  access) under the repos dir — `$KB_REPOS_DIR` → `~/.claude/.kb-repos-dir`, and
  nothing else — kept fresh by this plugin's SessionStart hook (`kb_sync.sh`).
  **The location must be explicitly set** (no default, no auto-detection): the hook
  does nothing until the user records a choice in `~/.claude/.kb-repos-dir`
  (the kb-search skill walks them through it; an existing clone anywhere is picked
  up by pointing the state file at its parent dir).
- **Plugin updates** ride git: no `version` fields, so every merged commit is a new
  version; background auto-update or `/plugin marketplace update ds-team` for a
  deterministic refresh.

Run these checks read-only first, report a short table, then fix what the user approves:

1. **Clone present + fresh** — resolve the repos dir (order above);
   `git -C <pub> fetch --quiet` then `git -C <pub> rev-list --count HEAD..origin/main`
   — >0 means behind. A `.kb-sync-stuck` file at the clone root means the hook has
   been failing.
2. **Clone clean + on main** — `git status --porcelain` and `git branch --show-current`;
   local changes or a checked-out branch block the ff-only pull. Fix by
   committing/stashing (never discard changes without asking) or moving the branch to
   a worktree — the sync only works while the clone sits on `main`.
3. **Hook actually ran** — if the clone is missing entirely, the most common cause is
   **no location chosen yet** (`~/.claude/.kb-repos-dir` absent — fix per kb-search);
   otherwise the plugin may be installed but not enabled in this project (check
   `enabledPlugins`), or the machine has no `git`/network. Running `kb_sync.sh` from the plugin cache by hand shows the
   real error (drop the `2>/dev/null`s).
4. **Plugin cache fresh** — if team skills look stale relative to the KB repo,
   `/plugin marketplace update ds-team`.
5. **Internal repo** (access-gated tier) — present next to the public clone? If not
   and `gh repo view OCHA-DAP/ds-knowledge-base-internal` succeeds, the next session
   start clones it; if `gh` isn't authed, that's the fix (`gh auth login`).
6. **Legacy leftovers** (pre-plugin layouts; remove only with the user's OK):
   symlinks in `~/.claude/skills/` pointing into `…/ds-knowledge-base/claude/skills/`
   (dead — that path no longer exists); an `@import` of
   `…/ds-knowledge-base/claude/CLAUDE.team.md` in `~/.claude/CLAUDE.md` (dead);
   a SessionStart hook in `~/.claude/settings.json` referencing
   `sync_team_skills.sh` (dead) — plain clone-pull hooks there are fine, just
   redundant with this plugin's.

There is no setup script — the plugin IS the setup. Worst case, reinstall:
`claude plugin marketplace add OCHA-DAP/ds-knowledge-base` then
`claude plugin install kb-access@ds-team`.
