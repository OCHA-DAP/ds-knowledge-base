#!/usr/bin/env python3
"""CI gate for the `claude/` distribution directory (team config kernel + skills).

Merging to main auto-deploys these to every team machine's next Claude Code session
(clone auto-pull → @import / skills link), so a malformed SKILL.md or a bloated kernel
is a team-wide incident. Checks (stdlib only — runs inside the lint-docs job):

  kernel   claude/CLAUDE.dsci.md exists and stays under the token budget. It is loaded
           into EVERY session of EVERY project for EVERY person — link to KB pages
           instead of inlining detail.
  skills   every claude/skills/*/SKILL.md has frontmatter with a kebab-case `name`
           matching its directory and a non-empty single-line `description` under the
           listing cap.
  paths    no absolute user paths anywhere in claude/ (they'd break on other machines).

Exit non-zero with ::error:: lines on failure.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KERNEL = ROOT / "claude" / "CLAUDE.dsci.md"
SKILLS = ROOT / "claude" / "skills"

KERNEL_TOKEN_BUDGET = 900          # est. tokens ≈ chars / 4
DESC_CHAR_CAP = 1024               # Claude Code truncates long skill descriptions
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
USER_PATH_RE = re.compile(r"(/Users/|/home/[a-z]|C:\\\\Users)")

errors: list[str] = []


def err(path: Path, msg: str) -> None:
    errors.append(f"::error file={path.relative_to(ROOT)}::{msg}")


def parse_frontmatter(text: str) -> dict[str, str] | None:
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---", 4)
    if end == -1:
        return None
    fm: dict[str, str] = {}
    for line in text[4:end].splitlines():
        if ":" in line:
            k, _, v = line.partition(":")
            fm[k.strip()] = v.strip()
    return fm


def main() -> None:
    if not KERNEL.exists():
        errors.append("::error::claude/CLAUDE.dsci.md missing — the team config kernel")
    else:
        est = len(KERNEL.read_text(encoding="utf-8")) / 4
        if est > KERNEL_TOKEN_BUDGET:
            err(KERNEL, f"kernel is ~{est:.0f} est. tokens (budget {KERNEL_TOKEN_BUDGET}) — "
                        "it loads in every session; move detail to KB pages and link")

    skill_dirs = sorted(p for p in SKILLS.iterdir() if p.is_dir()) if SKILLS.exists() else []
    if not skill_dirs:
        errors.append("::error::claude/skills/ has no skills")
    for d in skill_dirs:
        sk = d / "SKILL.md"
        if not sk.exists():
            err(d, "skill directory without SKILL.md")
            continue
        fm = parse_frontmatter(sk.read_text(encoding="utf-8"))
        if fm is None:
            err(sk, "missing or unterminated YAML frontmatter (--- ... ---)")
            continue
        name, desc = fm.get("name", ""), fm.get("description", "")
        if not NAME_RE.match(name):
            err(sk, f"frontmatter name {name!r} is not kebab-case")
        elif name != d.name:
            err(sk, f"frontmatter name {name!r} != directory name {d.name!r}")
        if not desc:
            err(sk, "frontmatter description is empty — it is the trigger; say WHEN to use the skill")
        elif len(desc) > DESC_CHAR_CAP:
            err(sk, f"description is {len(desc)} chars (cap {DESC_CHAR_CAP}) — it gets truncated")

    for f in sorted((ROOT / "claude").rglob("*.md")):
        for i, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            if USER_PATH_RE.search(line):
                err(f, f"line {i}: absolute user path — breaks on other machines; "
                       "use ~/, the repos-dir convention, or relative wording")

    if errors:
        print("\n".join(errors))
        sys.exit(1)
    print(f"claude/ assets OK — kernel ~{len(KERNEL.read_text(encoding='utf-8')) / 4:.0f} "
          f"est. tokens, {len(skill_dirs)} skills")


if __name__ == "__main__":
    main()
