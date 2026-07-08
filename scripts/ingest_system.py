#!/usr/bin/env python3
"""Draft (or re-draft) one KB **app or pipeline** page via headless Claude Code.

The CI-friendly, single-target counterpart of the interactive `workflows/ingest-systems.mjs`.
Runs headless `claude -p` billed to the **Max plan** (`CLAUDE_CODE_OAUTH_TOKEN`), so it works in
a GHA. Two modes:
  - **new**  (`--type app|pipeline --target <name> [--repo <slug>]`): draft a page that doesn't
    exist yet — driven by infra-drift when a new app/pipeline appears.
  - **re-ingest** (`--page <apps|pipelines>/<file>.md`): re-draft an EXISTING page whose spoke
    moved — driven by drift-check when it flags the page STALE. type/name/repo come from the
    page's own frontmatter; the page is rewritten in place.

The workflow then branches + opens a PR — human review is the QA gate (replacing the Opus review
agent of the full ingest). Frameworks have their own re-ingest (`ingest_framework.py`) because
their authority is the PDF, not the code.

Usage:
  python scripts/ingest_system.py --type pipeline --target raster-stats [--repo ocha-dap/ds-raster-stats]
  python scripts/ingest_system.py --page pipelines/raster-stats.md         # re-ingest a stale page
  [--model opus] [--dry-run]
Exit: 0 = page written (or dry-run ok) · 2 = couldn't resolve/clone/draft
Needs: claude CLI (Max auth), gh, git, pyyaml.
"""
from __future__ import annotations
import argparse
import json
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
BASELINE = ROOT / "infrastructure" / ".infra-baseline.json"
SLUG_RE = re.compile(r"((?:ocha-dap|OCHA-DAP)/[A-Za-z0-9._-]+)")


def sh(args: list[str], **kw) -> subprocess.CompletedProcess:
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


def resolve_repo(target: str, override: str | None) -> str | None:
    """ocha-dap/<slug>. --override wins; else try chd-/-app/pa- heuristics, keep the first
    that exists. Returns None on miss (caller suggests search candidates)."""
    if override:
        slug = override if "/" in override else f"ocha-dap/{override}"
        return slug if sh(["gh", "repo", "view", slug]).returncode == 0 else None
    base = re.sub(r"^chd-", "", target)
    cands, seen = [], set()
    for c in (base, f"{base}-app", re.sub(r"-app$", "", base), f"pa-{base}", f"ds-{base}", f"chd-{base}"):
        if c not in seen:
            seen.add(c); cands.append(c)
    for c in cands:
        slug = f"ocha-dap/{c}"
        if sh(["gh", "repo", "view", slug]).returncode == 0:
            return slug
    return None


def clone_and_survey(slug: str) -> tuple[Path, str, str] | None:
    d = Path(tempfile.mkdtemp(prefix="kb-sys-"))
    dest = d / slug.split("/")[-1]
    if sh(["gh", "repo", "clone", slug, str(dest), "--", "--quiet"]).returncode != 0:
        return None
    refs = sh(["git", "-C", str(dest), "for-each-ref", "--sort=-committerdate",
               "--format=%(refname:short)", "refs/remotes/origin"]).stdout.splitlines()
    branch = "main"
    for r in refs:
        r = r.strip()
        if not r or "HEAD" in r or r == "origin":   # skip origin/HEAD symref + bare 'origin'
            continue
        cand = re.sub(r"^origin/", "", r)
        if cand:
            branch = cand; break
    sh(["git", "-C", str(dest), "checkout", branch])
    sha = sh(["git", "-C", str(dest), "rev-parse", "--short", "HEAD"]).stdout.strip()
    return dest, branch, sha


def deploy_facts(name: str) -> dict:
    if not BASELINE.exists():
        return {}
    try:
        b = json.loads(BASELINE.read_text())
    except json.JSONDecodeError:
        return {}
    return b.get("azure", {}).get(name, {})


KIND_DIRS = {"app": "apps", "pipeline": "pipelines", "analysis": "analysis"}


def build_prompt(kind: str, target: str, slug: str, branch: str, sha: str,
                 clone: Path, out: str, facts: dict, reingest: bool) -> str:
    is_app = kind == "app"
    dir_ = KIND_DIRS.get(kind, "pipelines")
    head = (f"You RE-INGEST an existing OCHA {kind} KB page whose source repo has MOVED — re-draft it "
            f"from the CURRENT code so the summary matches reality again. Keep the same page id/path."
            if reingest else
            f"You ingest ONE OCHA {kind} into a knowledge-base page.")
    if is_app:
        type_step = f"""  - WHAT IT SHOWS: read the app code (marimo/Dash/Streamlit/Quarto/other) — pages, plots, controls, the question it answers. Set tech + related (the framework/pipeline id it serves, or 'standalone').
  - DATA (inputs): DB tables / blobs / sources it loads, and freshness.
  - DEPLOYMENT: platform=azure-webapp, ref={target}, url + resource_group from the facts / deployments.md. Note prod-vs-dev slot. code_ref = entrypoint(s)."""
        depends_hint = "the pipeline/framework whose data it reads (the companion-of)"
    elif kind == "analysis":
        type_step = """  - WHAT WAS ANALYZED & WHY: the question the analysis answers, and why it is NOT (or not yet) a framework or a living pipeline (no published framework doc / no schedule / no deployment). Set analysis_type (exploratory | ad-hoc-activation | pre-framework | regional-overview) and an honest status (active | dormant | one-off | superseded-by-framework) — frozen inputs, stub notebooks and stale branches usually mean dormant.
  - FINDINGS: candidate triggers explored, thresholds, comparisons, conclusions — the substance, from the notebooks/scripts themselves. If a notebook is an empty stub, SAY SO.
  - RELATION TO FRAMEWORKS: which framework(s)/pipeline(s) this feeds or pre-figures → the `feeds` field ([] if standalone), and name the closest KB neighbours in prose.
  - DATA: sources pulled, where staged (blob paths), and whether anything refreshes them (usually nothing — note frozen extract dates)."""
        depends_hint = "upstream pipelines/datasets it reads ([] is common — most analyses are standalone)"
    else:
        type_step = f"""  - JOBS & SCHEDULE: a pipeline repo is OFTEN several jobs. Find them in databricks.yml/.yaml (DAB job names, crons, tasks), .github/workflows/*.yml (GHA crons), and the entrypoint (run_pipeline.py / main.py / a CLI). deployment.jobs[] = ONE ENTRY PER job/workflow {{name, ref (databricks job_id | GHA workflow path | azure app), schedule (cron|event|on-demand), status (live|paused|retired)}}. Cross-check infrastructure/pipeline-registry.md for the actual job_id(s), schedule, paused state.
  - INPUTS: data sources, blob paths, DB tables read. OUTPUTS: DB tables (src/schemas/sql, upserts), blob writes, email lists (Listmonk), dashboards. DEPENDENCIES: ocha-stratus/lens/relay, key libs, Listmonk list ids, secret scopes. DOWNSTREAM: which frameworks' monitoring / which apps consume this output.
  - deployment.platform = the dominant one (databricks-job|github-actions|azure-webapp|manual); resource_group for Azure."""
        depends_hint = "upstream pipelines/datasets it reads, and comms it sends through ('listmonk')"
    return f"""{head} The AUTHORITATIVE source is the CODE + where it actually runs — there is NO framework PDF. Be a runbook author: capture what it shows/does, what feeds it, what it emits, where it runs, and what breaks.

{kind.upper()}: {target}
SOURCE REPO (slug for frontmatter — NOT the local path): {slug}
CLONED CODE TO READ: {clone}     (active branch {branch}, sha {sha})
{"DEPLOYMENT FACTS (live Azure fingerprint): " + json.dumps(facts) if facts else ""}
TARGET PAGE: {out}

STEP 0 — LEARN THE SCHEMA. Read in full and follow exactly:
  - {ROOT}/{dir_}/_TEMPLATE.md   (EXACT frontmatter fields + body headings for a {kind})
  - {ROOT}/docs/INGESTION.md     (conventions; push deep detail DOWN to the repo, this page is the comparative summary + pointers)
  - {ROOT}/infrastructure/deployments.md   (deployment registry — find/agree this {kind}'s row)
  - {ROOT}/infrastructure/conventions.md   (stratus/lens/relay, dev-vs-prod slots) — if present
  {"You MAY read the EXISTING page at " + out + " to preserve its id, cross-links and any still-true context, but RE-VERIFY every claim against the current code." if reingest else "Do NOT read or copy any existing page under " + str(ROOT / dir_) + " — produce your own from the sources."}

STEP 1 — READ THE CODE at {clone} (README + entrypoints + config):
{type_step}

STEP 2 — WRITE THE PAGE to {out} (in place). CONFORMANCE — diff against {dir_}/_TEMPLATE.md:
  - EVERY frontmatter field present ({"analysis_type, status, country_iso3, hazard, summary, data_sources, feeds, " if kind == "analysis" else "deployment block, inputs, "}{"tech, related, " if is_app else "" if kind == "analysis" else "outputs, dependencies, downstream, "}depends_on, source_repo={slug}, source_branch={branch}, source_sha={sha}, code_ref, extra: {{}}, visibility).
  - depends_on: canonical KB node ids this DIRECTLY needs (upstream) — {depends_hint}; powers infrastructure/dependency-graph.md.
  - EVERY body heading from the template present.
  - YAML PARSE GATE: python3 -c "import yaml; t=open('{out}').read(); e=t.find(chr(10)+'---',3); yaml.safe_load(t[3:e]); print('YAML OK')" — quote scalars until it passes.

STEP 3 — {"Confirm the deployments.md row for this " + kind + " is still accurate; fix only its row if wrong." if is_app else "Sanity-check `feeds`/neighbour links against catalog.md (does the framework/pipeline you name exist?)." if kind == "analysis" else "Cross-check the deployment/jobs against pipeline-registry.md; note dev-slot / paused / branch-mismatch in failure-modes."}

Write ONLY {out}{" and at most the one deployments.md row" if is_app else ""}. When done, briefly report what it does and any discrepancies (dev-slot, repo-mismatch, branch-mismatch, couldn't-find-entrypoint)."""


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--page", help="re-ingest this existing page (apps/..|pipelines/..); type/repo from its frontmatter")
    ap.add_argument("--type", choices=["app", "pipeline", "analysis"], help="for NEW pages")
    ap.add_argument("--target", help="app/pipeline name (for NEW pages)")
    ap.add_argument("--repo", help="override source repo slug")
    ap.add_argument("--model", default="opus")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    reingest = bool(args.page)
    repo_override = args.repo
    if reingest:
        page = (ROOT / args.page).resolve()
        if not page.exists():
            sys.exit(f"::error::page {args.page} not found")
        fm = frontmatter(page)
        kind = fm.get("content_type") or ("app" if "apps/" in args.page else "pipeline")
        target = fm.get("name") or page.stem
        if not repo_override:
            m = SLUG_RE.search(str(fm.get("source_repo", "")))
            repo_override = m.group(1) if m else None
        out = page.as_posix()
    else:
        if not (args.type and args.target):
            sys.exit("::error::need --page OR (--type and --target)")
        kind, target = args.type, args.target
        # KB page names drop the repo's ds-/pa- prefix (convention: pipelines/acled-trends.md
        # for ocha-dap/ds-acled-trends) — using the raw repo name leaks the prefix into the KB.
        page_stem = re.sub(r"^(ds-|pa-)", "", Path(target).name)
        out = (ROOT / KIND_DIRS.get(kind, "pipelines") / f"{page_stem}.md").as_posix()

    slug = resolve_repo(target, repo_override)
    if not slug:
        kw = re.sub(r"^chd-|-app$", "", target).replace("-", " ")
        hits = sh(["gh", "search", "repos", "--owner", "ocha-dap", kw, "--limit", "5",
                   "--json", "fullName", "--jq", ".[].fullName"]).stdout.strip()
        sug = ("\n  candidates: " + ", ".join(hits.split("\n"))) if hits else ""
        sys.exit(f"::error::couldn't resolve a repo for '{target}'. Re-run with --repo ocha-dap/<slug>.{sug}")
    print(f"resolved {target} → {slug}  (kind={kind}, mode={'reingest' if reingest else 'new'})")

    surveyed = clone_and_survey(slug)
    if not surveyed:
        sys.exit(f"::error::couldn't clone {slug} (private spoke without a repo:read PAT?).")
    clone, branch, sha = surveyed
    print(f"cloned {slug} @ {branch} ({sha})")

    facts = deploy_facts(target) if kind == "app" else {}
    prompt = build_prompt(kind, target, slug, branch, sha, clone, out, facts, reingest)

    if args.dry_run:
        print("--- DRY RUN: prompt built, skipping Claude ---")
        print(prompt[:1400] + "\n…")
        return

    cmd = ["claude", "-p", prompt, "--allowedTools", "Read Edit Write",
           "--permission-mode", "acceptEdits", "--add-dir", str(clone), "--output-format", "json"]
    if args.model:
        cmd += ["--model", args.model]
    print(f"drafting {Path(out).relative_to(ROOT)} with claude ({args.model})…")
    r = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, timeout=2400)
    if r.returncode != 0:
        sys.exit(f"::error::claude failed (rc={r.returncode}): {r.stderr[-500:]}")

    page = Path(out)
    if not page.exists():
        sys.exit(f"::error::claude finished but {page.relative_to(ROOT)} was not written.")
    t = page.read_text(); e = t.find("\n---", 3)
    try:
        yaml.safe_load(t[3:e])
    except Exception as ex:
        sys.exit(f"::error::{page.name} frontmatter doesn't parse: {ex}")
    print(f"wrote {page.relative_to(ROOT)} ✅")


if __name__ == "__main__":
    main()
