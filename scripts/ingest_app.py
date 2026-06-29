#!/usr/bin/env python3
"""Draft an `apps/<name>.md` KB page for one Azure web app via headless Claude Code.

The CI-friendly, single-app counterpart of the interactive `workflows/ingest-systems.mjs`
(which is a multi-agent Workflow script that only runs inside a Claude Code session). This
runs **headless `claude -p`** billed to the **Max plan** (`CLAUDE_CODE_OAUTH_TOKEN`), the same
mechanism `gen_framework_captions.py` uses — so it can run in a GHA (`ingest-app.yml`).

What it does (the plumbing; Claude does the prose):
  1. Resolve the source repo for the app (chd-<x> → <x> / <x>-app heuristic, or --repo).
  2. Clone it (gh, shallow) and survey the active branch + sha (work is usually NOT on main).
  3. Gather deployment facts from `.infra-baseline.json` (runtime/state/plan/host).
  4. Hand Claude the app template + INGESTION.md + deployments.md + the cloned code and have
     it WRITE `apps/<name>.md` (and add the deployments.md Azure-table row) in place.
  5. YAML-gate the result.
The workflow then branches + opens a PR — human review is the QA gate (replacing the Opus
review agent of the full ingest).

Usage:  python scripts/ingest_app.py --app chd-ds-foo [--repo ocha-dap/ds-foo]
        [--model opus] [--dry-run]   # --dry-run = resolve+clone+build prompt, no Claude call
Exit:   0 = page written (or dry-run ok) · 2 = couldn't resolve/clone/draft
Needs:  claude CLI (Max auth / CLAUDE_CODE_OAUTH_TOKEN), gh, git, pyyaml.
"""
from __future__ import annotations
import argparse
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASELINE = ROOT / "infrastructure" / ".infra-baseline.json"


def sh(args: list[str], **kw) -> subprocess.CompletedProcess:
    return subprocess.run(args, capture_output=True, text=True, **kw)


def resolve_repo(app: str, override: str | None) -> str | None:
    """ocha-dap/<slug> for the app. --override wins; else try chd-/-app heuristics and
    keep the first that actually exists on GitHub."""
    if override:
        slug = override if "/" in override else f"ocha-dap/{override}"
        return slug if sh(["gh", "repo", "view", slug]).returncode == 0 else None
    base = re.sub(r"^chd-", "", app)
    cands = [base, f"{base}-app", re.sub(r"-app$", "", base), f"pa-{base}", f"chd-{base}"]
    seen, ordered = set(), []
    for c in cands:                       # de-dupe, preserve order
        if c not in seen:
            seen.add(c); ordered.append(c)
    for c in ordered:
        slug = f"ocha-dap/{c}"
        if sh(["gh", "repo", "view", slug]).returncode == 0:
            return slug
    return None


def clone_and_survey(slug: str) -> tuple[Path, str, str] | None:
    """Clone (full, so branch survey works) → (path, active_branch, short_sha). The active
    branch = most-recently-committed (work is usually off main — the storms-pipeline lesson)."""
    d = Path(tempfile.mkdtemp(prefix="kb-app-"))
    dest = d / slug.split("/")[-1]
    if sh(["gh", "repo", "clone", slug, str(dest), "--", "--quiet"]).returncode != 0:
        return None
    refs = sh(["git", "-C", str(dest), "for-each-ref", "--sort=-committerdate",
               "--format=%(refname:short)", "refs/remotes"]).stdout.splitlines()
    branch = "main"
    for r in refs:
        r = r.strip()
        if r and "HEAD" not in r:
            branch = re.sub(r"^origin/", "", r); break
    sh(["git", "-C", str(dest), "checkout", branch], )  # best-effort
    sha = sh(["git", "-C", str(dest), "rev-parse", "--short", "HEAD"]).stdout.strip()
    return dest, branch, sha


def deploy_facts(app: str) -> dict:
    if not BASELINE.exists():
        return {}
    try:
        return json.loads(BASELINE.read_text()).get("azure", {}).get(app, {})
    except json.JSONDecodeError:
        return {}


def build_prompt(app: str, slug: str, branch: str, sha: str, clone: Path, facts: dict) -> str:
    out = (ROOT / "apps" / f"{Path(app).name}.md").as_posix()
    return f"""You ingest ONE OCHA deployed app into a knowledge-base page. The AUTHORITATIVE source is the CODE + where it actually runs — there is NO framework PDF. Be a runbook author: capture what it shows, what feeds it, where it runs, and what breaks.

APP (Azure web app name): {app}
SOURCE REPO (slug for frontmatter — NOT the local path): {slug}
CLONED CODE TO READ: {clone}     (active branch {branch}, sha {sha})
DEPLOYMENT FACTS (from the live Azure fingerprint): {json.dumps(facts)}

STEP 0 — LEARN THE SCHEMA. Read in full and follow exactly:
  - {ROOT}/apps/_TEMPLATE.md   (the EXACT frontmatter fields + body headings for an app)
  - {ROOT}/docs/INGESTION.md   (conventions; hub-vs-spoke depth: push deep detail DOWN to the repo, this page is the comparative summary + pointers)
  - {ROOT}/infrastructure/deployments.md   (the deployment registry — find/agree the Azure row for {app})
  - {ROOT}/infrastructure/conventions.md   (stratus/lens/relay, dev-vs-prod slots) — if present
  Do NOT read or copy any existing page under {ROOT}/apps/ — produce your own from the sources.

STEP 1 — READ THE CODE at {clone} (README + entrypoints + config):
  - WHAT IT SHOWS: the pages, plots, controls, and the question it answers for a user. Set tech (marimo|dash|streamlit|quarto|other). Set related = the framework/pipeline id it serves (or 'standalone').
  - DATA (inputs): which DB tables / blobs / data sources it loads, and how fresh.
  - DEPLOYMENT: platform=azure-webapp, ref={app}, url + resource_group from the deployment facts / deployments.md. Note prod-vs-dev slot. code_ref = the entrypoint(s).

STEP 2 — WRITE THE PAGE to {out} (in place). CONFORMANCE — diff against apps/_TEMPLATE.md:
  - EVERY frontmatter field present (deployment block with ref/url/resource_group, inputs, tech, related, depends_on, source_repo={slug}, source_branch={branch}, source_sha={sha}, code_ref, extra: {{}}, visibility).
  - depends_on: the pipeline/framework whose data it reads (the thing it's a companion of), by KB node id. Powers infrastructure/dependency-graph.md.
  - EVERY body heading from the template present.
  - YAML PARSE GATE (line-anchored): python3 -c "import yaml; t=open('{out}').read(); e=t.find(chr(10)+'---',3); yaml.safe_load(t[3:e]); print('YAML OK')" — quote any ': '/brace/quote scalars until it passes.

STEP 3 — ADD THE DEPLOYMENTS ROW. Edit {ROOT}/infrastructure/deployments.md: if {app} is not already a row in the "Azure web apps" table, add it (app | state | repo | url) in alphabetical position, using the deployment facts. Do not touch other rows.

Write ONLY {out} and the one deployments.md row. When done, briefly report what the app does and any discrepancies (dev-slot, repo-mismatch, couldn't-find-entrypoint)."""


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--app", required=True, help="Azure web app name (e.g. chd-ds-foo)")
    ap.add_argument("--repo", help="override source repo slug (ocha-dap/<x> or <x>)")
    ap.add_argument("--model", default="opus", help="claude model for the draft (default opus)")
    ap.add_argument("--dry-run", action="store_true", help="resolve+clone+build prompt, skip the Claude call")
    args = ap.parse_args()

    slug = resolve_repo(args.app, args.repo)
    if not slug:
        # heuristics failed (app/repo names genuinely diverge, e.g. viewer↔estimates) —
        # surface search candidates so the human can re-run with --repo quickly.
        kw = re.sub(r"^chd-|-app$", "", args.app).replace("-", " ")
        hits = sh(["gh", "search", "repos", "--owner", "ocha-dap", kw,
                   "--limit", "5", "--json", "fullName", "--jq", ".[].fullName"]).stdout.strip()
        sug = ("\n  candidates: " + ", ".join(hits.split("\n"))) if hits else ""
        sys.exit(f"::error::couldn't resolve a source repo for '{args.app}' "
                 f"(tried chd-/-app heuristics). Re-run with --repo ocha-dap/<slug>.{sug}")
    print(f"resolved {args.app} → {slug}")

    surveyed = clone_and_survey(slug)
    if not surveyed:
        sys.exit(f"::error::couldn't clone {slug} (private spoke without a repo:read PAT?).")
    clone, branch, sha = surveyed
    print(f"cloned {slug} @ {branch} ({sha})")

    facts = deploy_facts(args.app)
    prompt = build_prompt(args.app, slug, branch, sha, clone, facts)

    if args.dry_run:
        print("--- DRY RUN: prompt built, skipping Claude ---")
        print(prompt[:1200] + "\n…")
        return

    cmd = ["claude", "-p", prompt, "--allowedTools", "Read Edit Write",
           "--permission-mode", "acceptEdits", "--add-dir", str(clone),
           "--output-format", "json"]
    if args.model:
        cmd += ["--model", args.model]
    print(f"drafting apps/{Path(args.app).name}.md with claude ({args.model})…")
    r = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, timeout=2400)
    if r.returncode != 0:
        sys.exit(f"::error::claude failed (rc={r.returncode}): {r.stderr[-500:]}")

    page = ROOT / "apps" / f"{Path(args.app).name}.md"
    if not page.exists():
        sys.exit(f"::error::claude finished but {page.relative_to(ROOT)} was not written.")
    # YAML gate (belt-and-braces; the prompt also asks Claude to run it).
    t = page.read_text()
    e = t.find("\n---", 3)
    try:
        import yaml
        yaml.safe_load(t[3:e])
    except Exception as ex:
        sys.exit(f"::error::{page.name} frontmatter doesn't parse: {ex}")
    print(f"wrote {page.relative_to(ROOT)} ✅")


if __name__ == "__main__":
    main()
