# Pointing local Claude Code at the KB

Add this block to your **global** `~/.claude/CLAUDE.md` (not a project one) so the KB is available from *any* repo you work in.

```markdown
## Team knowledge base

The DS team knowledge base lives at `~/OCHA/repos/ds-knowledge-base/`. It is the
shared home for our methods, past frameworks, pipeline runbooks, and infra
conventions.

- Before answering team-knowledge questions (how a framework/trigger works, what
  feeds a pipeline, blob/DB conventions, past project decisions), **search the KB
  first** — grep/read it rather than answering from memory.
- It's organized as `frameworks/`, `pipelines/`, `methods/`, `infrastructure/`.
  Read the specific page you need; follow each page's `code_ref`/`source_repo`
  down into the actual repo for depth.
- After completing framework or pipeline work, update the affected KB page
  (capture-as-you-go). The repo's own CLAUDE.md first, the KB summary second.
- If a lookup turns up nothing or something stale, leave a `<!-- TODO -->` stub.
```

This manual block is the current stopgap. A team-wide distribution of it — a config kernel + skills riding the KB clone itself, replacing both this block and the retired `setup_team_claude.sh` (D81) — is proposed in [PR #221](https://github.com/OCHA-DAP/ds-knowledge-base/pull/221), pending team agreement on how our local Claudes should be configured.
