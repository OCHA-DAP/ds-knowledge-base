# claude/ — the ds-team plugin payload

This repo doubles as a **Claude Code plugin marketplace** (`ds-team`, manifest at
`/.claude-plugin/marketplace.json`). The plugins themselves live here:

| plugin | ships | enable it when |
|---|---|---|
| `kb-access` | `kb-search` + `kb-doctor` skills, SessionStart hook that clones/updates the KB clones | you want sessions to know the KB exists (most team work) |
| `data-conventions` | `blob-io` skill + advisory team data/Python/marimo defaults | data & pipeline repos |
| `hdx-brand` | HDX v2 design-system skill | repos that produce visual output |

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
