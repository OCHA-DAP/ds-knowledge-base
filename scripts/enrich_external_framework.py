#!/usr/bin/env python3
"""Enrich ONE external-frameworks stub into a full page, from public web sources.

Tier 2 of the Hub pipeline (D78): `fetch_hub_inventory.py` + `gen_hub_stubs.py` give
every Anticipation-Hub framework a deterministic core-fields stub; this runs headless
Claude Code (Max plan, WebSearch) to research the framework and rewrite the stub in
place — trigger_summary, funding, framework_doc, activation history, sourced prose.
Loose by design (D77): unknowns stay null with honest notes, never guessed.

Usage:  python scripts/enrich_external_framework.py --page external-frameworks/ifrc/ken-flood.md
        [--model opus] [--dry-run]
Exit:   0 = page enriched (or dry-run) · error otherwise
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


def build_prompt(page: Path, fm: dict) -> str:
    org, iso3, hazard = fm.get("org"), fm.get("country_iso3"), fm.get("hazard")
    captions = "; ".join((fm.get("extra") or {}).get("hub_captions") or [])
    doc = fm.get("framework_doc")
    return f"""You enrich ONE page in the OCHA Centre for Humanitarian Data knowledge base: an EXTERNAL anticipatory-action framework (run by another organisation, NOT OCHA/CERF). It is currently a STUB auto-created from the Anticipation Hub inventory — research it from PUBLIC sources with WebSearch and REWRITE it in place. Careful, sourced, loose-where-unknown.

FRAMEWORK: org={org}, country_iso3={iso3}, hazard={hazard}
Hub listing: {captions or "—"}
{"Known doc URL (start here): " + doc if doc else "Find the org's authoritative public document yourself."}
PAGE TO REWRITE (in place): {page}

STEP 0 — LEARN THE SCHEMA + RULES. Read in full:
  - {ROOT}/external-frameworks/_TEMPLATE.md   (the loose common-core schema — EXACT fields)
  - {ROOT}/external-frameworks/README.md      (the section's rules, esp. "Patterns learned")
  Read 1-2 non-stub pages under {ROOT}/external-frameworks/ifrc/ or wfp/ for house style.

STEP 1 — RESEARCH (WebSearch; good sources: the org's own site, reliefweb.int,
anticipation-hub.org — Hub-hosted PDF mirrors fetch best; for IFRC also the GO API
https://goadmin.ifrc.org/api/v2/appeal/?code=MDR…):
  - The trigger in plain language (indicator, threshold, lead time) → `trigger_summary`.
  - Pre-arranged funding + source (DREF/SFERA/donor), target people, validity period.
  - REAL activation history (dates, one-liners, URLs). Near-misses go in `extra`, not `activations`.
  - The authoritative public document + its date.
  - COMPONENT-OF-COLLECTIVE check: if this is the org's piece of an OCHA/CERF collective
    framework, say so in `extra.coordination` and cross-link the OCHA page under
    {ROOT}/frameworks/ — do NOT present it as independent.
  Cite every substantive claim. Unknown → null/[] plus a one-line `extra.schema_strain` note. NEVER guess.

STEP 2 — REWRITE {page} keeping the SAME frontmatter fields (loose schema — do not add
OCHA-only fields): fill trigger_summary, data_sources, funding, framework_doc(+date),
sources (every URL used), activations; keep `extra.hub_captions`/`hub_years`, REMOVE
`extra.hub_stub`, set `last_checked` to today. Body: Summary / Trigger / Funding & scope /
Activations / Sources headings, concise sourced prose.
  YAML PARSE GATE before finishing:
  python3 -c "import yaml; t=open('{page}').read(); e=t.find(chr(10)+'---',3); yaml.safe_load(t[3:e]); print('YAML OK')"

Touch ONLY {page}. When done, report the key facts found and what you could NOT source."""


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--page", required=True, help="external-frameworks/<org>/<iso3-hazard>.md")
    ap.add_argument("--model", default="opus")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    page = (ROOT / args.page).resolve()
    if not page.is_file() or ROOT / "external-frameworks" not in page.parents:
        sys.exit(f"::error::not an external-frameworks page: {args.page}")
    text = page.read_text(encoding="utf-8")
    fm = yaml.safe_load(text[3:text.find("\n---", 3)])
    if fm.get("content_type") != "framework-external":
        sys.exit("::error::page is not a framework-external page")
    if not (fm.get("extra") or {}).get("hub_stub"):
        print("::warning::page is not marked hub_stub — enriching anyway (refresh mode)")

    prompt = build_prompt(page, fm)
    if args.dry_run:
        print("--- DRY RUN ---\n" + prompt[:1500] + "\n…")
        return

    cmd = ["claude", "-p", prompt, "--allowedTools", "WebSearch WebFetch Read Write Edit",
           "--permission-mode", "acceptEdits", "--add-dir", str(ROOT), "--output-format", "json",
           "--model", args.model]
    print(f"enriching {args.page} with claude ({args.model})…")
    r = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, timeout=2400)
    if r.returncode != 0:
        sys.exit(f"::error::claude failed (rc={r.returncode}): {r.stderr[-500:]}")

    t = page.read_text(encoding="utf-8")
    try:
        fm2 = yaml.safe_load(t[3:t.find("\n---", 3)])
    except Exception as ex:  # noqa: BLE001
        sys.exit(f"::error::enriched frontmatter doesn't parse: {ex}")
    if not fm2.get("trigger_summary"):
        print("::warning::trigger_summary still empty after enrichment — sources may be thin")
    print(f"enriched {args.page} ✅")


if __name__ == "__main__":
    main()
