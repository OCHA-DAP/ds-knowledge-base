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

then start Claude Code anywhere and say **"finish my KB setup"**. The `kb-doctor`
skill you just installed takes it from there: it installs the remaining team
plugins (`data-access`, `data-conventions`, `aa-methods`, `infra-ops`, plus
`hdx@hdx-ai-hub` for the HDX design system — or just the subset you want), asks
where on your machine the KB should live (required — nothing is cloned until you
choose; an existing `ds-knowledge-base` clone is picked up by naming its parent
directory), clones the KB then and there, and verifies the result. From then on
every session start keeps it current.

Prefer to do it by hand? Each plugin is one `claude plugin install <name>@ds-team`
(the table below says what each does; `hdx` needs
`claude plugin marketplace add OCHA-DAP/hdx-ai-hub` first), and the KB location is
one line: `echo "$HOME/path/to/your/repos" > ~/.claude/.kb-repos-dir`. (Opening a
team repo that already carries `.claude/settings.json` works too — accept the
trust prompt and you're done, zero commands.)

---

The detail: team Claude config ships as **Claude Code plugins** from this repo (it
doubles as a plugin marketplace named `ds-team`; manifest at
`/.claude-plugin/marketplace.json`, payload in [`claude/`](../claude/README.md),
decision D85). Five plugins from this marketplace plus `hdx@hdx-ai-hub`, each
independently adoptable:

| plugin | what it gives every session | enable it when |
|---|---|---|
| `kb-access@ds-team` | `kb-search` + `kb-doctor` skills, and a session-start hook that **clones and updates the KB automatically** (plus the internal companion if you have access) | almost always — this is the KB pointer |
| `data-access@ds-team` | `blob-io` (stratus blob/Postgres I/O + data semantics: `valid_time`, CRS, boundaries) + `datasets` (third-party sources we have loaders for) | any repo touching team or humanitarian data — facts, minimally opinionated |
| `data-conventions@ds-team` | advisory house style: `uv` + `ruff`, `ocha-lens` first, geo stack, static-first interactive surfaces | where the team defaults help; switch off in divergent repos |
| `aa-methods@ds-team` | `trigger-design` + `return-periods` — the AA methodology discipline (vocabulary, mandatory backtesting, Weibull/three-level RPs) | framework & trigger-analysis repos |
| `infra-ops@ds-team` | `pipeline-ops` — two-axis dev/prod model, DAB conventions, registry-first debugging | repos that deploy/maintain scheduled pipelines |
| `hdx@hdx-ai-hub` | the HDX design system (real tokens + full component CSS + retrofit workflow) — **maintained by the HDX team in [`hdx-ai-hub`](https://github.com/OCHA-DAP/hdx-ai-hub)**, a separate marketplace we don't duplicate | anything visual |

**Per repo (the team default)** — check this into the repo's `.claude/settings.json`
and everyone who opens the repo gets the plugins after a one-time trust prompt, with
zero per-machine setup (new repos inherit it from the repo template; this repo's own
[`.claude/settings.json`](../.claude/settings.json) is the reference copy — trim
`enabledPlugins` to the parts the repo wants):

```json
{
  "extraKnownMarketplaces": {
    "ds-team":    { "source": { "source": "github", "repo": "OCHA-DAP/ds-knowledge-base" } },
    "hdx-ai-hub": { "source": { "source": "github", "repo": "OCHA-DAP/hdx-ai-hub" } }
  },
  "enabledPlugins": {
    "kb-access@ds-team": true,
    "data-access@ds-team": true,
    "data-conventions@ds-team": true,
    "aa-methods@ds-team": true,
    "infra-ops@ds-team": true,
    "hdx@hdx-ai-hub": true
  }
}
```

(Note `hdx-ai-hub` is org-internal: teammates' `gh`/git auth covers it; someone
outside the org opening the repo just won't get that one plugin.)

**Per user (always-on everywhere)** — if you want the KB in *every* project on your
machine, not just team repos:

```bash
claude plugin marketplace add OCHA-DAP/ds-knowledge-base
claude plugin install kb-access@ds-team        # user scope = all projects
# then "finish my KB setup" in any session installs the rest user-wide
```

Either way, the first session start after install **clones the KB for you** — but
only to a location you've explicitly set: `KB_REPOS_DIR` (env, incl. via a repo's
settings `env` block) or `~/.claude/.kb-repos-dir`. **There is no default and no
auto-detection** — with no location set, nothing happens on disk and Claude walks
you through choosing one (existing clones anywhere are picked up by pointing the
state file at their parent dir). From then on the clone stays on current
`main` — local grep stays fast and offline-friendly.

**Turning parts off.** Every plugin is an independent switch, at three levels —
most specific wins (local > project > user):

- **For everyone in a repo** — in the repo's checked-in `.claude/settings.json`,
  set the plugin to `false` (or simply leave it out of `enabledPlugins`):

  ```json
  { "enabledPlugins": { "data-conventions@ds-team": false } }
  ```

  A deliberately-divergent repo can switch off everything this way — a checked-in
  `false` **also overrides teammates' always-on user installs** inside that repo
  (verified), so the repo's choice genuinely wins for everyone.
- **Just for you, in one repo** — same keys in that repo's
  `.claude/settings.local.json` (gitignored, yours alone), or from inside the repo:
  `claude plugin disable data-conventions@ds-team --scope local`. Invisible to
  teammates; lets you opt out of (or into) a plugin somewhere without touching the
  repo's shared config.
- **Just for you, everywhere** — `claude plugin disable <name>@ds-team` (user
  scope), or `claude plugin uninstall <name>@ds-team` to remove it entirely.

Re-enabling is the same commands with `enable`, or flipping `false` to `true`.

**Updates**: plugins have no version pins — every merge to `main` is a new version,
picked up by background auto-update; `/plugin marketplace update ds-team` forces it.
If that update instead **errors with `couldn't find remote ref`**, or a plugin seems
**frozen at an old version** (new skills/hooks never arrive), your marketplace is
pinned to the retired `kb-plugin` branch — some registrations from the mid-2026
rollout set `"ref": "kb-plugin"`, which has since been merged to `main` and deleted.
kb-doctor detects this; the fix re-registers on the default branch (removing a
marketplace drops its plugins' enablement, so reinstall after):

```bash
claude plugin marketplace remove ds-team
claude plugin marketplace add OCHA-DAP/ds-knowledge-base
claude plugin install kb-access@ds-team   # re-enable at user scope; rebuilds the cache
```

then `/reload-plugins`. Anything else off? Ask Claude to run **kb-doctor**. No plugins at all? The manual
fallback is a few lines of your own in `~/.claude/CLAUDE.md`: where your clone of
this repo lives, "search it before answering team-knowledge questions", and
"update the affected page after real work". (The old copyable block,
`docs/global-claude-pointer.md`, predated the plugins and had rotted — removed, D95.)

With either a clone or the MCP connector, Claude Code answers things like *"what's the
trigger for Chad drought?"*, *"which pipelines write storms tables?"*, *"what are the
HDX brand colors?"* — grounded and cited, whichever surface (local grep or MCP) it picks.

## Watching the plugins work

`kb-access` ships activity hooks (D96) so you can *see* the plugins working instead
of taking it on faith — the point is judging whether they help your workflow. Inline
notices in chat:

- 🧭 *prompt looks team-KB-relevant* — your prompt matched KB keywords. If no 📚/📖
  follows on a question the KB should answer, that's a triggering gap — please
  report it (`kb-feedback` issue).
- 📚 *`<skill>` invoked* — a ds-team plugin skill actually launched.
- 📖 *consulting KB (…)* — Claude is reading your local KB clone (shown once per
  turn; every individual file is in the log).
- ⚠️ *KB auto-sync is stuck* — your clone can't fast-forward; `kb-doctor` has the fix.

The full firehose — every KB file read, sync outcomes — goes to an ANSI-colored log
you can keep open in a side pane:

```bash
tail -f ~/.claude/ds-team-activity.log
```

Observation only: notices go to **you**, never into Claude's context, so watching
doesn't change the behavior you're judging.

## No-install options

- **Public MCP only** — works anywhere. Claude Code:
  `claude mcp add --scope user --transport http ds-kb https://chd-ds-kb-mcp.azurewebsites.net/mcp`.
  On claude.ai (Team/Enterprise) an org Owner can add it as a **No authentication**
  custom connector; only the *internal* tier is still blocked from claude.ai (it needs
  OAuth, which our Entra setup can't do yet).
- **The KB chatbot** — ask in the browser, no setup:
  [`chd-ds-kb-chat`](https://chd-ds-kb-chat.azurewebsites.net) (password with the
  team; `/private` adds live DB + blob, the internal Drive extracts, and sandboxed
  `run_python`). The token-gated internal MCP tier (`chd-ds-kb-mcp-internal`) behind
  `/private` is a real HTTP endpoint — ask a maintainer for the token to use it from
  Claude Code directly.
- **The team hub** — [every dashboard, app & published analysis on one page](https://ocha-dap.github.io/ds-knowledge-base/), with thumbnails and hazard/country/hosting filters; generated from the KB, so to fix a card you fix the KB page (`surfaces:` / `purpose` on the owning page)
- **The public AA site** — [AA map + trigger stats](https://ocha-dap.github.io/ds-knowledge-base/anticipatory-action/)
  for the portfolio at a glance.

## Want something changed or added?

**Open an issue** on this repo describing it — the steward drafts the change as a PR for
human review (or answers your question on the issue). Comment on a bot PR to have it
revised. Details: [automation.md](../infrastructure/automation.md).

## Editing the KB locally? Use a worktree

Your KB clone is **shared infrastructure**: every Claude Code session on your machine
reads it, and it stays current via `git pull --ff-only`. That only works while the
clone sits on a **pristine** `main` — so **never edit the clone in place, not even on
main, and never switch branches there**. Uncommitted edits or a checked-out feature
branch block updates (the sync drops a `.kb-sync-stuck` marker and Claude will nag
you) and make files appear/vanish under concurrent sessions mid-task.

Instead, give each change its own worktree (from inside the clone):

```bash
git worktree add ../ds-knowledge-base.worktrees/<branch> -b <branch> origin/main
```

Work and commit **there** (with explicit pathspecs — another session may have files
staged), push, open a PR, and `git worktree remove` the directory after merge. Scripts
and loaders run fine from a worktree path.

**Changes already stranded in the clone?** Rescue them losslessly — stashes are
shared across worktrees:

```bash
git stash push -m "rescue"          # in the clone; sync now works again
git worktree add ../ds-knowledge-base.worktrees/<branch> -b <branch> origin/main
cd ../ds-knowledge-base.worktrees/<branch> && git stash pop   # your edits, on a branch
```

Local *commits* on main instead: `git branch <branch>` to save them, then
`git reset --hard origin/main` in the clone (only after the branch exists).

## What's where (30 seconds)

| you want | look in |
|---|---|
| a framework's trigger, funding, activations | `frameworks/<country-hazard>/` + [catalog](../catalog.md) |
| other orgs' AA frameworks (IFRC/WFP/FAO…), cross-org view | `external-frameworks/` + [catalog-global](../catalog-global.md) |
| how a pipeline runs / what broke | `pipelines/<name>.md` + `infrastructure/pipeline-registry.md` |
| a deployed app / dashboard | `apps/<name>.md` |
| ad-hoc activations, regional overviews, pre-framework work | `analysis/` |
| how we do things (triggers, return periods, style) | `methods/` |
| DB schemas, deployments, dependency graph, datasets | `infrastructure/` |
| what data is in blob for a project | `assets/<project>/` |
| Drive docs, style-reference mirror (internal) | `ds-knowledge-base-internal` |
