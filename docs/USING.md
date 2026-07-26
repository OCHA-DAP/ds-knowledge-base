# Using the KB — for team members

You're on the DS team and want answers (or want Claude Code to have them). This is the
consumer page — contributors see [INGESTION.md](INGESTION.md); how the KB maintains itself
is [infrastructure/automation.md](../infrastructure/automation.md).

## Local setup — manual for now

There is **no one-command local setup**. The earlier `setup_team_claude.sh` was removed
(D81): it installed a config model we've since moved away from (`ds-claude-config`
copies, an appended pointer block, per-machine MCP registration). Its proposed
replacement — team config + skills riding the KB clone itself —
([PR #221](https://github.com/OCHA-DAP/ds-knowledge-base/pull/221)) was **closed
unmerged** (2026-07-14, D84): the team didn't converge on whether shared config should be
global/opt-out or per-repo/opt-in, so no team-wide mechanism ships for now.

Use the no-install options below, or wire a clone up manually:
clone this repo and add the pointer block from
[global-claude-pointer.md](global-claude-pointer.md) to your global `~/.claude/CLAUDE.md`
(every session then searches the KB before answering team questions). Keep the clone
fresh with `git pull` — it only stays pullable if it stays on `main` (see the worktree
rule below).

With either a clone or the MCP connector, Claude Code answers things like *"what's the
trigger for Chad drought?"*, *"which pipelines write storms tables?"*, *"what are the
HDX brand colors?"* — grounded and cited, whichever surface (local grep or MCP) it picks.

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

## Editing the KB locally? Use a worktree

Your KB clone is **shared infrastructure**: every Claude Code session on your machine
reads it, and it stays current via `git pull --ff-only`. That only
works while the clone sits on `main` — so **never switch branches in the clone itself**.
A feature branch checked out there blocks updates
and makes files appear/vanish under concurrent sessions mid-task.

Instead, give each change its own worktree (from inside the clone):

```bash
git worktree add ../ds-knowledge-base.worktrees/<branch> -b <branch> origin/main
```

Work and commit **there** (with explicit pathspecs — another session may have files
staged), push, open a PR, and `git worktree remove` the directory after merge. Scripts
and loaders run fine from a worktree path.

If a pull ever refuses to fast-forward: move any local commits onto a branch, get the
clone back onto a clean `main`, and `git pull --ff-only` again.

## What's where (30 seconds)

| you want | look in |
|---|---|
| a framework's trigger, funding, activations | `frameworks/<country-hazard>/` + [catalog](../catalog.md) |
| other orgs' AA frameworks (IFRC/WFP/FAO…), cross-org view | `external-frameworks/` + [catalog-global](../catalog-global.md) |
| how a pipeline runs / what broke | `pipelines/<name>.md` + `infrastructure/pipeline-registry.md` |
| how we do things (triggers, return periods, style) | `methods/` |
| DB schemas, deployments, dependency graph, datasets | `infrastructure/` |
| what data is in blob for a project | `assets/<project>/` |
| Drive docs, style-reference mirror (internal) | `ds-knowledge-base-internal` |
