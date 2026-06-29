#!/usr/bin/env python3
"""Draft a framework page for a portfolio framework that has NO repo, from public web sources.

The comprehensiveness path (D51): the KB covers the full OCHA/CERF AA portfolio, including historical
pilots (Somalia drought, South Sudan flood, …) that predate the team's modeled-trigger repos — so
there's no spoke to clone. This runs headless Claude Code on the Max plan with **WebSearch** to
research the framework from public OCHA/CERF/ReliefWeb material and draft
`frameworks/<iso3>-<hazard>/<version>.md` conforming to the template, with `source_repo: null`.

The workflow then opens a PR — human review is the QA gate, and is especially important here since the
draft is from public reporting, not a repo.

Usage:  python scripts/ingest_framework_web.py --country SOM --hazard drought [--doc URL] [--version 2020]
        [--model opus] [--dry-run]
Exit:   0 = page written (or dry-run) · 2 = nothing written
Needs:  claude CLI (Max auth / CLAUDE_CODE_OAUTH_TOKEN), pyyaml.
"""
from __future__ import annotations
import argparse
import subprocess
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("Needs pyyaml")

ROOT = Path(__file__).resolve().parent.parent


def build_prompt(iso3: str, hazard: str, folder: Path, doc: str | None, version: str | None) -> str:
    return f"""You draft ONE anticipatory-action FRAMEWORK page for the OCHA Centre for Humanitarian Data knowledge base, for a framework that has NO code repo — research it from PUBLIC sources with WebSearch. Be a careful, sourced summary writer; this is OCHA/CERF institutional history.

FRAMEWORK: country_iso3={iso3}, hazard={hazard}
{"KNOWN DOC URL (start here): " + doc if doc else "Find the authoritative OCHA/CERF document(s) yourself."}
{"VERSION (use as the filename): " + version if version else "Determine the canonical version (endorsement/establishment date, YYYY-MM-DD or YYYY) from sources."}

STEP 0 — LEARN THE SCHEMA. Read in full and follow exactly:
  - {ROOT}/frameworks/_TEMPLATE.md   (EXACT frontmatter fields + body headings for a framework version)
  - {ROOT}/docs/INGESTION.md         (conventions; document authority; funding/scope facets; multi-country rule)
  Read 1–2 existing endorsed framework pages under {ROOT}/frameworks/ ONLY to learn the house style — do not copy content.

STEP 1 — RESEARCH (WebSearch; prefer unocha.org, cerf.un.org, reliefweb.int, anticipation-hub.org):
  - The framework's TRIGGER design (indicator(s), thresholds, lead time), geography, anticipatory actions, and pre-arranged finance (CERF amount).
  - ACTIVATION history: when it triggered, the allocation, who implemented, people targeted. Historical pilots often activated (e.g. Somalia drought triggered Jun 2020, ~$15M).
  - Status: endorsed / pilot / superseded / retired. Many 2020–21 pilots are historical — set status accordingly and note if a later version replaced it.
  Cite every substantive claim; if a fact isn't found, use null/[]/{{}} rather than guessing.

STEP 2 — WRITE THE PAGE to {folder}/<version>.md (mkdir -p {folder} first). CONFORMANCE — diff against frameworks/_TEMPLATE.md:
  - EVERY frontmatter field present. country_iso3={iso3}, hazard={hazard}. source_repo: null, code_ref: [] (no repo). framework_doc: the URL you found (or null). Fill framework_doc_date, version, status, funding fields, implementing_agencies, target_people, and activation history from sources; null when unknown.
  - extra: {{}}, visibility: public. EVERY body heading from the template present.
  - YAML PARSE GATE: python3 -c "import yaml,glob; f=sorted(glob.glob('{folder}/*.md'))[-1]; t=open(f).read(); e=t.find(chr(10)+'---',3); yaml.safe_load(t[3:e]); print('YAML OK')" — quote scalars until it passes.

Write ONLY the one page under {folder}. When done, report the version you chose, key trigger facts, activation history, and which facts you could NOT source (so the reviewer knows what to verify)."""


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--country", required=True, help="ISO3, e.g. SOM")
    ap.add_argument("--hazard", required=True, help="e.g. drought, flood, plague")
    ap.add_argument("--doc", help="known framework doc URL to start from")
    ap.add_argument("--version", help="explicit version (filename); else Claude determines it")
    ap.add_argument("--model", default="opus")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    iso3 = args.country.upper()
    slug = f"{iso3.lower()}-{args.hazard.lower()}"
    folder = ROOT / "frameworks" / slug
    before = set(folder.glob("*.md")) if folder.exists() else set()

    prompt = build_prompt(iso3, args.hazard.lower(), folder, args.doc, args.version)
    if args.dry_run:
        print(f"would write under frameworks/{slug}/\n--- DRY RUN ---\n" + prompt[:1500] + "\n…")
        return

    cmd = ["claude", "-p", prompt, "--allowedTools", "WebSearch Read Write",
           "--permission-mode", "acceptEdits", "--add-dir", str(ROOT), "--output-format", "json",
           "--model", args.model]
    print(f"researching + drafting frameworks/{slug}/ with claude ({args.model})…")
    r = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, timeout=2400)
    if r.returncode != 0:
        sys.exit(f"::error::claude failed (rc={r.returncode}): {r.stderr[-500:]}")

    new = sorted(set(folder.glob("*.md")) - before) if folder.exists() else []
    if not new:
        sys.exit(f"::error::claude finished but no new page under frameworks/{slug}/")
    page = new[-1]
    t = page.read_text(); e = t.find("\n---", 3)
    try:
        yaml.safe_load(t[3:e])
    except Exception as ex:
        sys.exit(f"::error::{page.name} frontmatter doesn't parse: {ex}")
    print(f"wrote {page.relative_to(ROOT)} ✅")


if __name__ == "__main__":
    main()
