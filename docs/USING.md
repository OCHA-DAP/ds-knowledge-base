# Using the KB — for team members

You're on the DS team and want answers (or want Claude Code to have them). This is the
consumer page — contributors see [INGESTION.md](INGESTION.md); how the KB maintains itself
is [infrastructure/automation.md](../infrastructure/automation.md).

## One-command setup (recommended)

```bash
bash <(gh api repos/OCHA-DAP/ds-knowledge-base/contents/scripts/setup_team_claude.sh \
       -H "Accept: application/vnd.github.raw")
```

Idempotent; needs `gh` (logged in) + Claude Code. Four things, all riding the clone:

1. **Clones** the KB (and the private companion repo if your GitHub access allows).
   The first run asks where to put the repos (e.g. `~/OCHA/repos`); your choice is
   remembered in `~/.claude/.kb-repos-dir`, so re-runs never ask.
   (`KB_REPOS_DIR=/your/dir` skips the prompt, e.g. for scripted installs.)
2. **One `@import` line** in your global `~/.claude/CLAUDE.md` → the team config
   ([`claude/CLAUDE.team.md`](../claude/CLAUDE.team.md), which supersedes the old
   `ds-claude-config` repo) loads straight from the clone. No copies to go stale.
3. **Team skills** — each skill in `claude/skills/` is linked into `~/.claude/skills/`
   (one symlink per skill — that's the only layout Claude Code discovers), so
   `blob-io`, `hdx-brand`, `kb-doctor` are available in every session. The hook re-syncs
   the links after each pull, so skills merged later auto-appear; your own personal
   skills are never touched.
4. **Auto-refresh hook** — an async SessionStart hook pulls both clones whenever a
   Claude Code session starts (zero startup delay; Windows runs hooks through Git Bash,
   so it's the same mechanism everywhere).

**Updates are automatic**: merge to `main` → every machine's next session has it —
config, skills, and KB content alike. A clone that can't fast-forward (local edits) is
never clobbered; instead a `.kb-sync-stuck` marker makes Claude tell you it's stuck.
Re-run the same command anytime to repair things or pick up setup improvements; ask
Claude to run **kb-doctor** to health-check the setup; `--uninstall` removes everything
the script configured (clones stay).

**No MCP registration** — with a fresh local clone, Claude Code always prefers local
grep, so connectors add nothing there. They remain the right surface for claude.ai and
no-clone use (below).

After that, Claude Code answers things like *"what's the trigger for Chad drought?"*,
*"which pipelines write storms tables?"*, *"what are the HDX brand colors?"* — grounded
and cited, whichever surface (local grep or MCP) it picks.

## No-install options

- **Public MCP only** (works anywhere, incl. claude.ai custom connectors are blocked on
  org OAuth for now, but Claude Code takes it directly):
  `claude mcp add --scope user --transport http ds-kb https://chd-ds-kb-mcp.azurewebsites.net/mcp`
- **The KB chatbot** — ask in the browser, no setup: `chd-ds-kb-chat` (password with the
  team; `/private` adds live DB/blob).
- **The public site** — [AA map + trigger stats](https://ocha-dap.github.io/ds-knowledge-base/anticipatory-action/)
  for the portfolio at a glance.

## Want something changed or added?

**Open an issue** on this repo describing it — the steward drafts the change as a PR for
human review (or answers your question on the issue). Comment on a bot PR to have it
revised. Details: [automation.md](../infrastructure/automation.md).

## What's where (30 seconds)

| you want | look in |
|---|---|
| a framework's trigger, funding, activations | `frameworks/<country-hazard>/` + [catalog](../catalog.md) |
| how a pipeline runs / what broke | `pipelines/<name>.md` + `infrastructure/pipeline-registry.md` |
| how we do things (triggers, return periods, style) | `methods/` |
| DB schemas, deployments, dependency graph, datasets | `infrastructure/` |
| the always-loaded team config + team skills | `claude/` |
| what data is in blob for a project | `assets/<project>/` |
| Drive docs, style-reference mirror (internal) | `ds-knowledge-base-internal` |
