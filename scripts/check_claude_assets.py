#!/usr/bin/env python3
"""CI gate for the ds-team plugin marketplace (.claude-plugin/ + claude/plugins/).

Merging to main auto-deploys these to every enabled machine's next session (git-SHA
plugin versioning: no `version` fields anywhere, every commit IS a new version — keep
it that way), so a malformed manifest or a bloated skill surface is a team-wide
incident. Checks (stdlib only — runs inside the lint-docs job):

  marketplace  .claude-plugin/marketplace.json parses; plugin names kebab-case and
               unique; each `source` dir exists and carries a matching plugin.json;
               no `version` fields (they'd freeze auto-deploy until bumped).
  plugins      plugin.json parses and its name matches the directory + marketplace
               entry; hooks.json (if declared) parses and its scripts exist and are
               executable.
  skills       every skills/*/SKILL.md has frontmatter with a kebab-case `name`
               matching its directory and a non-empty single-line `description`
               under the per-skill cap.
  budget       the eagerly-loaded surface stays bounded: total skill count and the
               SUM of all description chars (descriptions load in every session
               where a plugin is enabled).
  settings     .claude/settings.json (this repo's own enablement) parses and only
               enables plugins that exist in the marketplace.
  paths        no absolute user paths anywhere in claude/ (break on other machines).

Exit non-zero with ::error:: lines on failure.
"""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MARKETPLACE = ROOT / ".claude-plugin" / "marketplace.json"
SETTINGS = ROOT / ".claude" / "settings.json"

DESC_CHAR_CAP = 1024          # Claude Code truncates long skill descriptions
AGG_DESC_CHAR_CAP = 6144      # ~1.5k est. tokens eagerly loaded if everything's enabled
SKILL_COUNT_CAP = 12          # a growing skill fleet needs a deliberate decision
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
USER_PATH_RE = re.compile(r"(/Users/|/home/[a-z]|C:\\\\Users)")

errors: list[str] = []


def err(path: Path, msg: str) -> None:
    errors.append(f"::error file={path.relative_to(ROOT)}::{msg}")


def load_json(path: Path) -> dict | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        err(path, f"unreadable or invalid JSON: {e}")
        return None


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


def check_skill(sk: Path, seen_names: set[str]) -> int:
    """Validate one SKILL.md; return its description length (0 on error)."""
    fm = parse_frontmatter(sk.read_text(encoding="utf-8"))
    if fm is None:
        err(sk, "missing or unterminated YAML frontmatter (--- ... ---)")
        return 0
    name, desc = fm.get("name", ""), fm.get("description", "")
    if not NAME_RE.match(name):
        err(sk, f"frontmatter name {name!r} is not kebab-case")
    elif name != sk.parent.name:
        err(sk, f"frontmatter name {name!r} != directory name {sk.parent.name!r}")
    elif name in seen_names:
        err(sk, f"duplicate skill name {name!r} across plugins — confusing even namespaced")
    seen_names.add(name)
    if not desc:
        err(sk, "frontmatter description is empty — it is the trigger; say WHEN to use the skill")
    elif len(desc) > DESC_CHAR_CAP:
        err(sk, f"description is {len(desc)} chars (cap {DESC_CHAR_CAP}) — it gets truncated")
    return len(desc)


def check_plugin(pdir: Path, mkt_name: str, seen_skills: set[str]) -> tuple[int, int]:
    """Validate one plugin dir; return (skill_count, total_desc_chars)."""
    manifest = pdir / ".claude-plugin" / "plugin.json"
    pj = load_json(manifest) if manifest.exists() else None
    if not manifest.exists():
        err(pdir, "plugin has no .claude-plugin/plugin.json")
    elif pj is not None:
        if pj.get("name") != pdir.name or pj.get("name") != mkt_name:
            err(manifest, f"plugin.json name {pj.get('name')!r} must match directory "
                          f"{pdir.name!r} and marketplace entry {mkt_name!r}")
        if "version" in pj:
            err(manifest, "remove `version` — git-SHA versioning is what makes merge=deploy work")
        hooks_ref = pj.get("hooks")
        if isinstance(hooks_ref, str) and hooks_ref.lstrip("./") == "hooks/hooks.json":
            # live-tested 2026-07-14: the conventional file is auto-loaded, and declaring
            # it too makes the whole plugin fail with "Duplicate hooks file detected"
            err(manifest, "do not declare ./hooks/hooks.json in plugin.json — it is "
                          "auto-loaded, and declaring it double-loads and BREAKS the plugin")

    hooks_file = pdir / "hooks" / "hooks.json"  # auto-loaded by convention
    if hooks_file.exists():
        hj = load_json(hooks_file)
        if hj is not None:
            for script in re.findall(r"\$\{CLAUDE_PLUGIN_ROOT\}/([^\"'\\ ]+)",
                                     json.dumps(hj)):
                sp = pdir / script
                if not sp.exists():
                    err(hooks_file, f"hook references missing script {script!r}")
                elif not os.access(sp, os.X_OK):
                    err(sp, "hook script is not executable (chmod +x)")

    count, chars = 0, 0
    skills_dir = pdir / "skills"
    for d in sorted(skills_dir.iterdir()) if skills_dir.exists() else []:
        if not d.is_dir():
            continue
        sk = d / "SKILL.md"
        if not sk.exists():
            err(d, "skill directory without SKILL.md")
            continue
        count += 1
        chars += check_skill(sk, seen_skills)
    root_skill = pdir / "SKILL.md"  # single-skill shortcut layout
    if root_skill.exists():
        count += 1
        chars += check_skill(root_skill, seen_skills)
    if count == 0:
        err(pdir, "plugin bundles no skills")
    return count, chars


def main() -> None:
    mkt = load_json(MARKETPLACE) if MARKETPLACE.exists() else None
    if not MARKETPLACE.exists():
        errors.append("::error::.claude-plugin/marketplace.json missing")
    plugin_names: set[str] = set()
    total_skills, total_chars = 0, 0
    if mkt is not None:
        if "version" in json.dumps(mkt.get("plugins", [])):
            err(MARKETPLACE, "remove per-plugin `version` fields — git-SHA versioning "
                             "is what makes merge=deploy work")
        for entry in mkt.get("plugins", []):
            name, source = entry.get("name", ""), entry.get("source", "")
            if not NAME_RE.match(name):
                err(MARKETPLACE, f"plugin name {name!r} is not kebab-case")
            if name in plugin_names:
                err(MARKETPLACE, f"duplicate plugin name {name!r}")
            plugin_names.add(name)
            pdir = (ROOT / source).resolve() if isinstance(source, str) else None
            if pdir is None or not pdir.is_dir():
                err(MARKETPLACE, f"plugin {name!r} source {source!r} is not a directory")
                continue
            seen_skills: set[str] = set()
            c, ch = check_plugin(pdir, name, seen_skills)
            total_skills += c
            total_chars += ch
        if not mkt.get("plugins"):
            err(MARKETPLACE, "marketplace lists no plugins")

    if total_skills > SKILL_COUNT_CAP:
        errors.append(f"::error::{total_skills} skills across plugins (cap {SKILL_COUNT_CAP}) — "
                      "growing the always-candidate surface needs a deliberate cap bump")
    if total_chars > AGG_DESC_CHAR_CAP:
        errors.append(f"::error::skill descriptions total {total_chars} chars "
                      f"(cap {AGG_DESC_CHAR_CAP}) — they load eagerly in every enabled "
                      "session; tighten descriptions or split plugins")

    st = load_json(SETTINGS) if SETTINGS.exists() else None
    if st is not None:
        mkt_name = (mkt or {}).get("name", "ds-team")
        for key in st.get("enabledPlugins", {}):
            pname, _, source = key.partition("@")
            # plugins from other marketplaces (e.g. hdx@hdx-ai-hub) aren't ours to validate
            if source == mkt_name and pname not in plugin_names:
                err(SETTINGS, f"enables unknown plugin {key!r}")

    claude_dir = ROOT / "claude"
    for f in sorted(claude_dir.rglob("*")) if claude_dir.exists() else []:
        if f.suffix not in {".md", ".json", ".sh"} or not f.is_file():
            continue
        for i, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            if USER_PATH_RE.search(line):
                err(f, f"line {i}: absolute user path — breaks on other machines; "
                       "use ~/, the repos-dir convention, or relative wording")

    if errors:
        print("\n".join(errors))
        sys.exit(1)
    print(f"claude assets OK — {len(plugin_names)} plugins, {total_skills} skills, "
          f"{total_chars} desc chars (~{total_chars // 4} est. eager tokens)")


if __name__ == "__main__":
    main()
