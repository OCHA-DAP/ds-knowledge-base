#!/usr/bin/env python3
"""Re-draft one existing **framework** KB page via headless Claude Code (Max plan).

Frameworks differ from apps/pipelines: their AUTHORITY is the published PDF, not the code. So this
re-ingests an existing framework-version page from (a) the cached PDF text extract
`raw/frameworks/<fw>/<version>.txt` (+ `.captions.txt` for the visuals) and (b) the analysis code in
the source repo — conforming to `frameworks/_TEMPLATE.md`, in place.

Driven by:
  - drift-check (a framework page flagged STALE because its code_ref moved) — the PDF is unchanged,
    so re-drafting from the extract + current code refreshes the code-derived sections.
  - pdf-freshness (a framework's doc is aging / a newer doc was spotted) — this refreshes the
    CURRENT version's page; **adopting a genuinely NEW published version is still a human step**
    (it needs a new <version> page file + a fresh extract), which the PR body flags.

Usage:  python scripts/ingest_framework.py --page frameworks/<fw>/<version>.md [--repo ocha-dap/<x>]
        [--model opus] [--dry-run]
Exit:   0 = page written (or dry-run) · 2 = couldn't resolve/clone/draft
Needs:  claude CLI (Max auth), gh, git, pyyaml.
"""
from __future__ import annotations
import argparse
import re
import subprocess
import sys
import tempfile
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("Needs pyyaml")

ROOT = Path(__file__).resolve().parent.parent
SLUG_RE = re.compile(r"((?:ocha-dap|OCHA-DAP)/[A-Za-z0-9._-]+)")


def sh(args, **kw):
    return subprocess.run(args, capture_output=True, text=True, **kw)


def frontmatter(path: Path) -> dict:
    t = path.read_text(encoding="utf-8")
    if not t.startswith("---"):
        return {}
    e = t.find("\n---", 3)
    try:
        return yaml.safe_load(t[3:e]) or {}
    except yaml.YAMLError:
        return {}


def clone_and_survey(slug: str):
    d = Path(tempfile.mkdtemp(prefix="kb-fw-"))
    dest = d / slug.split("/")[-1]
    if sh(["gh", "repo", "clone", slug, str(dest), "--", "--quiet"]).returncode != 0:
        return None
    refs = sh(["git", "-C", str(dest), "for-each-ref", "--sort=-committerdate",
               "--format=%(refname:short)", "refs/remotes/origin"]).stdout.splitlines()
    branch = "main"
    for r in refs:
        r = r.strip()
        if not r or "HEAD" in r or r == "origin":
            continue
        cand = re.sub(r"^origin/", "", r)
        if cand:
            branch = cand; break
    sh(["git", "-C", str(dest), "checkout", branch])
    sha = sh(["git", "-C", str(dest), "rev-parse", "--short", "HEAD"]).stdout.strip()
    return dest, branch, sha


def build_prompt(page: Path, fm: dict, slug: str, branch: str, sha: str,
                 clone: Path, extract: Path | None, captions: Path | None) -> str:
    out = page.as_posix()
    have_extract = extract and extract.exists()
    return f"""You RE-INGEST an existing OCHA anticipatory-action FRAMEWORK KB page. For frameworks the AUTHORITATIVE source is the published FRAMEWORK PDF (cached as a text extract), with the analysis code as secondary. Re-draft the page so it matches the sources again, keeping the SAME version/country/hazard/page id.

FRAMEWORK PAGE: {out}
  country_iso3={fm.get('country_iso3')}  hazard={fm.get('hazard')}  version={fm.get('version')}  status={fm.get('status')}
  framework_doc={fm.get('framework_doc')}
SOURCE REPO (analysis code; slug for frontmatter): {slug}   CLONED AT: {clone}  (branch {branch}, sha {sha})
PDF TEXT EXTRACT (authority): {extract if have_extract else "MISSING — draft from code + the existing page, and note in your report that the PDF extract was unavailable"}
VISUAL CAPTIONS: {captions if captions and captions.exists() else "(none)"}

STEP 0 — LEARN THE SCHEMA. Read in full and follow exactly:
  - {ROOT}/frameworks/_TEMPLATE.md   (EXACT frontmatter fields + body headings for a framework version)
  - {ROOT}/docs/INGESTION.md         (conventions; document authority & reconciliation; push deep detail DOWN to the repo)
  You MAY read the EXISTING page at {out} to preserve its id, cross-links, activation history and still-true context — but RE-VERIFY every claim against the extract + current code.

STEP 1 — READ THE SOURCES:
  - The PDF extract{f" at {extract}" if have_extract else ""} is the authority for the TRIGGER design, thresholds, lead times, geography, and the AA logic — read it closely.
  - The analysis code at {clone} (README + trigger/monitoring scripts + config) for how the trigger is computed/operationalised and the data it uses. Record source_branch={branch}, source_sha={sha}; source_repo MUST be {slug}.

STEP 2 — RE-WRITE THE PAGE to {out} (in place). CONFORMANCE — diff against frameworks/_TEMPLATE.md:
  - EVERY frontmatter field present; KEEP version/country_iso3/hazard/status/framework_doc/framework_doc_date as-is unless the sources clearly contradict them.
  - code_ref → the current trigger/monitoring paths in the repo. depends_on / data sources per the template.
  - EVERY body heading present; reconcile PDF vs code per INGESTION.md (PDF wins on design, code wins on implementation).
  - YAML PARSE GATE: python3 -c "import yaml; t=open('{out}').read(); e=t.find(chr(10)+'---',3); yaml.safe_load(t[3:e]); print('YAML OK')" — quote scalars until it passes.

Write ONLY {out}. When done, report what changed and any discrepancies (code moved, thresholds differ PDF-vs-code, extract missing, or signs this is a genuinely NEW published version that needs a new version page)."""


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--page", required=True, help="frameworks/<fw>/<version>.md")
    ap.add_argument("--repo", help="override source repo slug")
    ap.add_argument("--model", default="opus")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    page = (ROOT / args.page).resolve()
    if not page.exists():
        sys.exit(f"::error::page {args.page} not found")
    fm = frontmatter(page)
    slug = args.repo
    if slug and "/" not in slug:
        slug = f"ocha-dap/{slug}"
    if not slug:
        m = SLUG_RE.search(str(fm.get("source_repo", "")))
        slug = m.group(1) if m else None
    if not slug:
        sys.exit(f"::error::no source_repo on {args.page}; pass --repo ocha-dap/<slug>")
    if sh(["gh", "repo", "view", slug]).returncode != 0:
        sys.exit(f"::error::can't access {slug} (private spoke without a repo:read PAT?).")

    fw = page.parent.name
    ver = page.stem
    extract = ROOT / "raw" / "frameworks" / fw / f"{ver}.txt"
    captions = ROOT / "raw" / "frameworks" / fw / f"{ver}.captions.txt"

    surveyed = clone_and_survey(slug)
    if not surveyed:
        sys.exit(f"::error::couldn't clone {slug}")
    clone, branch, sha = surveyed
    print(f"re-ingesting {args.page} from {slug}@{branch} ({sha}); extract={'yes' if extract.exists() else 'MISSING'}")

    prompt = build_prompt(page, fm, slug, branch, sha, clone, extract, captions)
    if args.dry_run:
        print("--- DRY RUN ---\n" + prompt[:1400] + "\n…")
        return

    cmd = ["claude", "-p", prompt, "--allowedTools", "Read Edit Write",
           "--permission-mode", "acceptEdits", "--add-dir", str(clone), "--output-format", "json",
           "--model", args.model]
    print(f"drafting {args.page} with claude ({args.model})…")
    r = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, timeout=2400)
    if r.returncode != 0:
        sys.exit(f"::error::claude failed (rc={r.returncode}): {r.stderr[-500:]}")
    t = page.read_text(); e = t.find("\n---", 3)
    try:
        yaml.safe_load(t[3:e])
    except Exception as ex:
        sys.exit(f"::error::{page.name} frontmatter doesn't parse: {ex}")
    print(f"wrote {args.page} ✅")


if __name__ == "__main__":
    main()
