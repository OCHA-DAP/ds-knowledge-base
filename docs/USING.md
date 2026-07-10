# Using the KB — for team members

You're on the DS team and want answers (or want Claude Code to have them). This is the
consumer page — contributors see [INGESTION.md](INGESTION.md); how the KB maintains itself
is [infrastructure/automation.md](../infrastructure/automation.md).

## One-command setup (recommended)

```bash
bash <(gh api repos/OCHA-DAP/ds-knowledge-base/contents/scripts/setup_team_claude.sh \
       -H "Accept: application/vnd.github.raw")
```

Idempotent; needs `gh` (logged in) + Claude Code. It clones the KB (and the private
companion repo if your GitHub access allows), adds the **KB pointer** to your global
`~/.claude/CLAUDE.md` (every session searches the KB before answering team questions),
and registers the **MCP connectors** — public (KB search/read, no auth) and, when the
shared token is reachable, internal (read-only DB/blob + Drive extracts + style guide).

**Re-run the same command anytime to update** — it pulls both KB clones and refreshes
your `~/.claude/CLAUDE.dsci.md` from `ds-claude-config`, so local copies don't drift.
(The MCP connectors always serve current `main` — no update needed on that path.)

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

## Editing the KB locally? Use a worktree

Your KB clone is **shared infrastructure**: every Claude Code session on your machine
reads it, and the session-start hook keeps it fresh with `git pull --ff-only`. That only
works while the clone sits on `main` — so **never switch branches in the clone itself**.
A feature branch checked out there blocks auto-sync (that's the `.kb-sync-stuck` marker)
and makes files appear/vanish under concurrent sessions mid-task.

Instead, give each change its own worktree (from inside the clone):

```bash
git worktree add ../ds-knowledge-base.worktrees/<branch> -b <branch> origin/main
```

Work and commit **there** (with explicit pathspecs — another session may have files
staged), push, open a PR, and `git worktree remove` the directory after merge. Scripts
and loaders run fine from a worktree path.

If `.kb-sync-stuck` does appear: move any local commits onto a branch, get the clone
back onto a clean `main`, `git pull --ff-only`, delete the marker (or re-run the setup
command above, which does the safe parts for you).

## What's where (30 seconds)

| you want | look in |
|---|---|
| a framework's trigger, funding, activations | `frameworks/<country-hazard>/` + [catalog](../catalog.md) |
| how a pipeline runs / what broke | `pipelines/<name>.md` + `infrastructure/pipeline-registry.md` |
| how we do things (triggers, return periods, style) | `methods/` |
| DB schemas, deployments, dependency graph, datasets | `infrastructure/` |
| what data is in blob for a project | `assets/<project>/` |
| Drive docs, style-reference mirror (internal) | `ds-knowledge-base-internal` |
