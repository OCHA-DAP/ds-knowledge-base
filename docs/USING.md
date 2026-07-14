# Using the KB — for team members

You're on the DS team and want answers (or want Claude Code to have them). This is the
consumer page — contributors see [INGESTION.md](INGESTION.md); how the KB maintains itself
is [infrastructure/automation.md](../infrastructure/automation.md).

## Local setup — the `ds-team` plugins

**Quick start.** In a terminal:

```bash
claude plugin marketplace add OCHA-DAP/ds-knowledge-base
claude plugin install kb-access@ds-team
```

That's it. Your next Claude Code session clones the team KB for you and keeps it
current; every session from then on knows to search it before answering team
questions. Working with data or making anything visual? Also install
`data-conventions@ds-team` and/or `hdx-brand@ds-team` the same way. (Opening a team
repo that already carries `.claude/settings.json` works too — accept the trust
prompt and you're done, zero commands.)

---

The detail: team Claude config ships as **Claude Code plugins** from this repo (it
doubles as a plugin marketplace named `ds-team`; manifest at
`/.claude-plugin/marketplace.json`, payload in [`claude/`](../claude/README.md),
decision D85). Three plugins, three independently adoptable parts:

| plugin | what it gives every session | enable it when |
|---|---|---|
| `kb-access` | `kb-search` + `kb-doctor` skills, and a session-start hook that **clones and updates the KB automatically** (plus the internal companion if you have access) | almost always — this is the KB pointer |
| `data-conventions` | `blob-io` (stratus blob/Postgres I/O) + advisory team defaults (paths, `valid_time`, CRS, `uv`, marimo) | data & pipeline repos |
| `hdx-brand` | HDX v2 design-system skill (tokens, components, dataviz ramps) | anything visual |

**Per repo (the team default)** — check this into the repo's `.claude/settings.json`
and everyone who opens the repo gets the plugins after a one-time trust prompt, with
zero per-machine setup (new repos inherit it from the repo template; this repo's own
[`.claude/settings.json`](../.claude/settings.json) is the reference copy — trim
`enabledPlugins` to the parts the repo wants):

```json
{
  "extraKnownMarketplaces": {
    "ds-team": { "source": { "source": "github", "repo": "OCHA-DAP/ds-knowledge-base" } }
  },
  "enabledPlugins": {
    "kb-access@ds-team": true,
    "data-conventions@ds-team": true,
    "hdx-brand@ds-team": true
  }
}
```

**Per user (always-on everywhere)** — if you want the KB in *every* project on your
machine, not just team repos:

```bash
claude plugin marketplace add OCHA-DAP/ds-knowledge-base
claude plugin install kb-access@ds-team        # user scope = all projects
```

Either way, the first session start after install **clones the KB for you** to
`~/OCHA/repos` (override with `KB_REPOS_DIR` or `~/.claude/.kb-repos-dir`) and keeps
it on current `main` thereafter — local grep stays fast and offline-friendly. A
deliberately-divergent repo opts back out in its own `.claude/settings.json`
(`"kb-access@ds-team": false`) or simply never enables anything.

**Updates**: plugins have no version pins — every merge to `main` is a new version,
picked up by background auto-update; `/plugin marketplace update ds-team` forces it.
Something off? Ask Claude to run **kb-doctor**. No plugins at all? The manual
fallback still works: clone this repo and add the pointer block from
[global-claude-pointer.md](global-claude-pointer.md) to `~/.claude/CLAUDE.md`.

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
