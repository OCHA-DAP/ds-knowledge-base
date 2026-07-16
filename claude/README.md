# claude/ — the ds-team plugin payload

This repo doubles as a **Claude Code plugin marketplace** (`ds-team`, manifest at
`/.claude-plugin/marketplace.json`). The plugins themselves live here:

| plugin | ships | enable it when |
|---|---|---|
| `kb-access` | `kb-search` + `kb-doctor` skills, SessionStart hook that clones/updates the KB clones | you want sessions to know the KB exists (most team work) |
| `data-access` | `blob-io` (stratus I/O + data semantics) + `datasets` (third-party loaders) — facts, minimally opinionated | any repo touching team/humanitarian data |
| `data-conventions` | advisory house style: uv, layout, lens-first, geo stack, marimo | where the defaults help; off in divergent repos |

HDX styling is deliberately **not** here: it's the `hdx` plugin in the HDX team's own
[`hdx-ai-hub`](https://github.com/OCHA-DAP/hdx-ai-hub) marketplace (D82: knowledge
lives with its source of truth). Don't add a style skill to this marketplace.

Consumers: see the KB's [docs/USING.md](../docs/USING.md) (per-repo `.claude/settings.json`
vs per-user install). Design rationale: DESIGN.md **D85**.

Contributor rules (CI-enforced by `scripts/check_claude_assets.py` in the lint-docs job):

- **No `version` fields** in `plugin.json` or marketplace entries — git-SHA versioning is
  what makes every merged commit auto-deploy. Adding a version would freeze updates
  until someone remembers to bump it.
- Skill `description`s are **eagerly loaded** in every enabled session — keep them tight;
  there's an aggregate budget and a skill-count cap.
- No absolute user paths anywhere (breaks on other machines).
- Merging to main deploys to the whole team's next update — treat changes here like
  production.
