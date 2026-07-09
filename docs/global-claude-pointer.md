# Pointing local Claude Code at the KB

**Superseded (2026-07, D75)** — don't add a manual pointer block anymore. The one-command
setup wires everything (KB clone, always-loaded team config via `claude/CLAUDE.team.md`,
team skills, self-updating hook):

```bash
bash <(gh api repos/OCHA-DAP/ds-knowledge-base/contents/scripts/setup_team_claude.sh \
       -H "Accept: application/vnd.github.raw")
```

See **[USING.md](USING.md)**. If your `~/.claude/CLAUDE.md` still has an old hand-pasted
`## Team knowledge base` block, the setup run removes it automatically.
