---
name: kb-doctor
description: Check and repair this machine's team-KB local setup — clone freshness, auto-update hook, config import, team skills link. Use when the user asks whether their KB setup is working, team knowledge seems stale, ds-team skills are missing, or after a failed setup run.
---

# KB setup doctor

The setup contract (installed by `scripts/setup_team_claude.sh`; consumer docs in
`docs/USING.md`): KB clone(s) under the repos dir (default `~/OCHA/repos`, per-machine
override recorded in `~/.claude/.kb-repos-dir`), one `@import` of `claude/CLAUDE.team.md`
in `~/.claude/CLAUDE.md`, **one symlink per team skill** in `~/.claude/skills/<name>`
pointing into the clone's `claude/skills/<name>` (Claude Code discovers personal skills
exactly one level deep — a grouping-dir symlink never works; Windows uses copies tagged
with a `.kb-team-skill` marker), and an async SessionStart hook in
`~/.claude/settings.json` that pulls the clones and re-runs
`scripts/sync_team_skills.sh` at each session start.

Run these checks read-only first, report a short table, then fix what the user approves:

1. **Clone present + fresh** — repos dir from `~/.claude/.kb-repos-dir` (else the
   default). `git -C <pub> fetch --quiet` then
   `git -C <pub> rev-list --count HEAD..origin/main` — >0 means behind.
   A `.kb-sync-stuck` file at the clone root means the hook has been failing.
2. **Clone clean** — `git status --porcelain`; local changes block the ff-only pull.
   Fix by committing/stashing — never discard someone's changes without asking.
3. **Import line** — `~/.claude/CLAUDE.md` contains an `@` import ending in
   `ds-knowledge-base/claude/CLAUDE.team.md`.
4. **Skills links** — for each dir in the clone's `claude/skills/`, `~/.claude/skills/<name>`
   exists and resolves into the clone (symlink on macOS/Linux; on Windows a copy with a
   `.kb-team-skill` marker — diff copies against the clone). A leftover
   `~/.claude/skills/ds-team` entry is the broken pre-fix layout — remove it.
   A same-named personal skill (plain dir, no marker) shadows the team one — report it,
   never delete it.
5. **Hook** — `.hooks.SessionStart` in `~/.claude/settings.json` contains a command
   mentioning the clone path.
6. **Internal repo** (optional tier) — present next to the public clone? If not and the
   user has OCHA-DAP access, suggest re-running setup.

Standard fix for most breakage — re-run setup (idempotent; repairs hook/link/import):

    bash <(gh api repos/OCHA-DAP/ds-knowledge-base/contents/scripts/setup_team_claude.sh \
           -H "Accept: application/vnd.github.raw")

Full removal: the same script with `--uninstall` (keeps the clones).
