---
name: kb-doctor
description: Check and repair this machine's team-KB local setup — clone freshness, auto-update hook, config import, team skills link. Use when the user asks whether their KB setup is working, team knowledge seems stale, ds-team skills are missing, or after a failed setup run.
---

# KB setup doctor

The setup contract (installed by `scripts/setup_team_claude.sh`; consumer docs in
`docs/USING.md`): KB clone(s) under the repos dir (default `~/OCHA/repos`, per-machine
override recorded in `~/.claude/.kb-repos-dir`), one `@import` of `claude/CLAUDE.team.md`
in `~/.claude/CLAUDE.md`, a `ds-team` entry in `~/.claude/skills/` pointing into the
clone's `claude/skills/`, and an async SessionStart hook in `~/.claude/settings.json`
that pulls the clones at each session start.

Run these checks read-only first, report a short table, then fix what the user approves:

1. **Clone present + fresh** — repos dir from `~/.claude/.kb-repos-dir` (else the
   default). `git -C <pub> fetch --quiet` then
   `git -C <pub> rev-list --count HEAD..origin/main` — >0 means behind.
   A `.kb-sync-stuck` file at the clone root means the hook has been failing.
2. **Clone clean** — `git status --porcelain`; local changes block the ff-only pull.
   Fix by committing/stashing — never discard someone's changes without asking.
3. **Import line** — `~/.claude/CLAUDE.md` contains an `@` import ending in
   `ds-knowledge-base/claude/CLAUDE.team.md`.
4. **Skills link** — `~/.claude/skills/ds-team` exists and resolves into the clone
   (symlink on macOS/Linux; a copied directory on Windows — if a copy, diff it against
   the clone's `claude/skills/`).
5. **Hook** — `.hooks.SessionStart` in `~/.claude/settings.json` contains a command
   mentioning the clone path.
6. **Internal repo** (optional tier) — present next to the public clone? If not and the
   user has OCHA-DAP access, suggest re-running setup.

Standard fix for most breakage — re-run setup (idempotent; repairs hook/link/import):

    bash <(gh api repos/OCHA-DAP/ds-knowledge-base/contents/scripts/setup_team_claude.sh \
           -H "Accept: application/vnd.github.raw")

Full removal: the same script with `--uninstall` (keeps the clones).
