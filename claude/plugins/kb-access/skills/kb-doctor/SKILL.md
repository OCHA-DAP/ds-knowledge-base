---
name: kb-doctor
description: Check and repair this machine's team-KB setup — the ds-team plugins, the KB clone's presence/freshness, the sync hook, leftovers from older setups — and bootstrap a fresh machine ("finish my KB setup" installs the remaining team plugins and sets the KB location). Use when the user asks whether their KB setup works, asks to finish/complete setup or install all the team plugins, team knowledge seems stale, kb-search finds no clone, or a .kb-sync-stuck marker appears.
---

# KB setup doctor

The contract (everything ships via the `ds-team` plugin marketplace in
`OCHA-DAP/ds-knowledge-base`; consumer docs in the KB's `docs/USING.md`):

- **Plugins**: `kb-access` (this one), optionally `data-access`, `data-conventions`,
  `aa-methods`, and `infra-ops` from this marketplace, plus `hdx@hdx-ai-hub` for HDX styling (separate marketplace,
  maintained by the HDX team) — enabled either per repo (checked-in
  `.claude/settings.json`: `extraKnownMarketplaces` + `enabledPlugins`) or per user
  (`claude plugin install <name>@<marketplace>`, lands in `~/.claude/settings.json`).
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
   local changes or a checked-out branch block the ff-only pull — the sync only works
   while the clone sits on a pristine `main`. **Recovery recipe for changes stranded
   in the clone** (never discard anything without asking; stashes are shared across
   worktrees, so nothing is lost):

       git -C <clone> stash push -m "rescue: stranded KB edits"
       git -C <clone> pull --ff-only          # now succeeds; marker clears next sync
       git -C <clone> worktree add ../ds-knowledge-base.worktrees/<branch> -b <branch> origin/main
       cd ../ds-knowledge-base.worktrees/<branch> && git stash pop
       # review, commit with explicit pathspecs, push, PR (merge commit, not squash)

   A checked-out branch (not main) in the clone: move it to a worktree the same way —
   `git switch main` only after confirming with the user what the branch was for.
3. **Hook actually ran** — if the clone is missing entirely, the most common cause is
   **no location chosen yet** (`~/.claude/.kb-repos-dir` absent — fix per kb-search);
   otherwise the plugin may be installed but not enabled in this project (check
   `enabledPlugins`), or the machine has no `git`/network. Running `kb_sync.sh` from the plugin cache by hand shows the
   real error (drop the `2>/dev/null`s).
4. **Plugin cache fresh** — if team skills look stale relative to the KB repo,
   `/plugin marketplace update ds-team`. If that errors with
   `couldn't find remote ref`, see check 7.
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
7. **Marketplace tracks a live branch** — `~/.claude/plugins/known_marketplaces.json`
   → `ds-team.source.ref`. Normal state is **no `ref`** (the marketplace tracks the
   repo's default branch, `main`). If `ref` is set to a feature branch — most likely
   `kb-plugin`, the branch the plugins were built on during the D85 rollout
   (registrations added around 2026-07-20 pinned it) — and that branch has since been
   merged and deleted, then `/plugin marketplace update ds-team` fails with
   `couldn't find remote ref refs/heads/<ref>` and the plugin is **frozen at an old
   commit**: new skills and hooks never arrive, this skill's Bootstrap section is
   absent, the `~/.claude/ds-team-activity.log` never appears. Confirm the branch is
   gone — `git ls-remote --heads https://github.com/OCHA-DAP/ds-knowledge-base.git <ref>`
   returns nothing. Fix by re-registering on the default branch; **removing a
   marketplace drops its plugins' enablement, so reinstall after** (which also
   rebuilds the cache from `main`):

       claude plugin marketplace remove ds-team
       claude plugin marketplace add OCHA-DAP/ds-knowledge-base
       claude plugin install kb-access@ds-team      # re-enable at user scope

   then `/reload-plugins`. Re-enable any other ds-team plugins installed at user scope the
   same way (`claude plugin install <name>@ds-team`). Verify: the newest
   `~/.claude/plugins/cache/ds-team/kb-access/<sha>/hooks/hooks.json` now lists
   `PreToolUse`/`UserPromptSubmit`, and `scripts/kb_activity.sh` is present.

# Bootstrap — "finish my KB setup"

A fresh machine needs only the two commands from the `docs/USING.md` quick start:

    claude plugin marketplace add OCHA-DAP/ds-knowledge-base
    claude plugin install kb-access@ds-team

This skill completes the rest on request ("finish my KB setup", "install all the
team plugins"):

1. **Missing marketplace** — if `hdx-ai-hub` isn't in
   `~/.claude/plugins/known_marketplaces.json`:
   `claude plugin marketplace add OCHA-DAP/hdx-ai-hub`.
2. **Sibling plugins** — offer the full set from the USING.md table, then install
   whatever the user confirms that's missing from user-scope `enabledPlugins`
   (`~/.claude/settings.json`): `claude plugin install <name>@ds-team` for
   `data-access`, `data-conventions`, `aa-methods`, `infra-ops`, and
   `claude plugin install hdx@hdx-ai-hub`. One plugin per invocation — the CLI
   takes no batch argument; the default `--scope` is already `user`. Confirm the
   list once before installing — some users deliberately run a subset.
3. **KB location** — if `~/.claude/.kb-repos-dir` is absent, walk the user through
   choosing a directory exactly as kb-search does (never pick a default silently);
   an existing clone anywhere is adopted by writing its parent dir to the file.
4. **Clone now** — don't leave the clone to the next session start: once
   `.kb-repos-dir` is written, run `scripts/kb_sync.sh` from the plugin cache by
   hand (the same script check 3 uses to debug the hook), so bootstrap actually
   finishes with the KB on disk.
5. **Verify** — run checks 1–7 above and show the table; it should end green,
   clone included.

There is no setup script — the plugin IS the setup, and this skill is the
installer for the rest. Worst case, reinstall:
`claude plugin marketplace add OCHA-DAP/ds-knowledge-base` then
`claude plugin install kb-access@ds-team`.
