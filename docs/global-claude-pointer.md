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

Once the KB has proven out, the same pointer can move into the org-level config repo (`ds-claude-config`) so the whole team gets it, not just you.
