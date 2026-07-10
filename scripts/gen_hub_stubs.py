#!/usr/bin/env python3
"""Generate external-frameworks stub pages + coverage report from the Hub inventory.

Consumes external-frameworks/.hub-inventory.json (fetch_hub_inventory.py) and:

  1. collapses records to framework identity (org + country + hazard, D76) — the Hub
     lists one record per framework-YEAR revision and per layer; active beats
     under-development, latest year wins, lineage kept in extra.hub_years
  2. OCHA-coordinated records are NEVER stubbed — they're cross-checked against the
     OCHA portfolio (frameworks/, matching on country_iso3+hazard per D62) and any
     missing combo is reported as an aa-watch signal in the coverage report
  3. every other identity with no existing external page gets a STUB page: core
     frontmatter from the API, `trigger_summary: null` + `extra.hub_stub: true` mark
     it for enrichment; existing pages (hand-authored or enriched) are never touched
  4. writes external-frameworks/hub-inventory.md — the coverage report

Usage:  python scripts/gen_hub_stubs.py [--dry-run]   (repo root; needs pyyaml)
"""
from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("Needs pyyaml:  uv pip install pyyaml")

ROOT = Path(__file__).resolve().parents[1]
EXT = ROOT / "external-frameworks"
INV = EXT / ".hub-inventory.json"
REPORT = EXT / "hub-inventory.md"
HUB_MAP_URL = "https://www.anticipation-hub.org/experience/global-map"

# For the OCHA cross-check only: hazards that count as the same combo (D62 matching).
# The Hub says "epidemic" where our pages say cholera/plague (cod-infectious-disease).
HAZARD_SYNONYMS = {"epidemic": "epidemic", "cholera": "epidemic", "plague": "epidemic",
                   "disease": "epidemic", "infectious-disease": "epidemic"}


def canon_hazard(h: str) -> str:
    return HAZARD_SYNONYMS.get(h, h)


# Hub records whose org attribution a human has reviewed and disputed — reported in
# their own section instead of "OCHA missing" (which would imply a portfolio gap).
DISPUTED = {
    ("MLI", "food-insecurity"): "not an OCHA/CERF framework per CHD review (2026-07-10)"
                                " — Hub attribution unclear (FAO/UNICEF implementing);"
                                " revisit if the Hub adds a document link",
}


def parse_frontmatter(path: Path) -> dict | None:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    if end == -1:
        return None
    try:
        return yaml.safe_load(text[3:end]) or {}
    except yaml.YAMLError:
        return None


def as_list(v) -> list:
    if v is None:
        return []
    return v if isinstance(v, list) else [v]


def collapse(records: list[dict]) -> dict[tuple, dict]:
    """(org_slug, iso3, hazard) → merged record. Active layer > under-development;
    within a layer the latest year wins; all years/captions kept for lineage."""
    groups: dict[tuple, list[dict]] = {}
    for r in records:
        groups.setdefault((r["org_slug"], r["country_iso3"], r["hazard"]), []).append(r)
    merged = {}
    for key, rs in groups.items():
        rs.sort(key=lambda r: (r["layer"] == "active-frameworks", str(r.get("year") or "")))
        best = rs[-1]
        best = dict(best)
        best["hub_years"] = sorted({str(r.get("year")) for r in rs if r.get("year")})
        best["hub_captions"] = sorted({r["hub_caption"] for r in rs if r.get("hub_caption")})
        best["n_hub_records"] = len(rs)
        best["any_active"] = any(r["layer"] == "active-frameworks" for r in rs)
        merged[key] = best
    return merged


def stub_page(r: dict, today: str) -> str:
    fm = {
        "content_type": "framework-external",
        "framework": f"{r['org_slug']}-{r['country_iso3'].lower()}-{r['hazard']}",
        "org": r["org"],
        "country_iso3": r["country_iso3"],
        "hazard": r["hazard"],
        "status": "active" if r["any_active"] else "in-development",
        "valid_until": None,
        "trigger_summary": None,
        "data_sources": [],
        "prearranged_funding_usd": r.get("investment_usd"),
        "funding_by_source": {},
        "target_people": r.get("target_people"),
        "framework_doc": r.get("framework_link"),
        "framework_doc_date": None,
        "sources": [HUB_MAP_URL],
        "activations": [],
        "last_checked": today,
        "extra": {
            "hub_stub": True,
            "hub_captions": r["hub_captions"],
            "hub_years": r["hub_years"],
            "implementing": r.get("implementing") or [],
        },
        "visibility": "public",
    }
    body = f"""
# {r['org']} — {r['country']} {r['hazard'].replace('-', ' ')}

**Stub** — created from the [Anticipation Hub global map]({HUB_MAP_URL}) inventory
({today}); core facts only, pending enrichment (trigger, funding detail, activations —
see `external-frameworks/README.md`). Hub listing: {'; '.join(r['hub_captions']) or '—'}.

## Sources
- [Anticipation Hub global map]({HUB_MAP_URL}) (inventory record, fetched {today})
{f"- [Framework document]({r['framework_link']})" if r.get('framework_link') else ""}
"""
    return "---\n" + yaml.safe_dump(fm, sort_keys=False, allow_unicode=True, width=88) + "---\n" + body


def main() -> None:
    dry = "--dry-run" in sys.argv
    today = date.today().isoformat()
    inv = json.loads(INV.read_text(encoding="utf-8"))
    merged = collapse(inv["records"])

    # existing coverage
    ext_pages = {}
    for p in EXT.glob("*/*.md"):
        fm = parse_frontmatter(p)
        if fm and fm.get("content_type") == "framework-external":
            for iso in as_list(fm.get("country_iso3")):
                ext_pages[(str(fm.get("org")), str(iso), str(fm.get("hazard")))] = p
    ocha_combos = set()
    for p in (ROOT / "frameworks").glob("*/*.md"):
        if p.name == "README.md":
            continue
        fm = parse_frontmatter(p)
        if fm and fm.get("content_type") == "framework":
            for iso in as_list(fm.get("country_iso3")):
                ocha_combos.add((str(iso), canon_hazard(str(fm.get("hazard")))))

    stubs, held, ocha_ok, ocha_missing, disputed = [], [], [], [], []
    for (org_slug, iso3, hazard), r in sorted(merged.items()):
        if r["org"] == "OCHA/CERF":
            if (iso3, hazard) in DISPUTED:
                r["dispute"] = DISPUTED[(iso3, hazard)]
                disputed.append(r)
            elif (iso3, canon_hazard(hazard)) in ocha_combos:
                ocha_ok.append(r)
            else:
                ocha_missing.append(r)
            continue
        if (r["org"], iso3, hazard) in ext_pages:
            held.append(r)
            continue
        stubs.append(r)
        if not dry:
            out = EXT / org_slug / f"{iso3.lower()}-{hazard}.md"
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(stub_page(r, today), encoding="utf-8")

    # coverage report
    by_org: dict[str, dict] = {}
    for r in merged.values():
        d = by_org.setdefault(r["org"], {"n": 0, "active": 0})
        d["n"] += 1
        d["active"] += 1 if r["any_active"] else 0
    lines = [
        "# Anticipation Hub inventory — coverage report",
        "",
        f"_Generated by `scripts/gen_hub_stubs.py` from `.hub-inventory.json` (fetched"
        f" {inv['fetched']}; {inv['n_records']} raw records → {len(merged)} frameworks"
        f" after identity collapse). Do not edit by hand._",
        "",
        f"**Coverage:** {len(held)} full/hand pages · {len(stubs)} stubs (awaiting"
        f" enrichment) · {len(ocha_ok)} OCHA-coordinated matched to the OCHA portfolio ·"
        f" **{len(ocha_missing)} OCHA-coordinated NOT in our portfolio** (aa-watch signal"
        " — see below).",
        "",
        "| org | frameworks (hub) | of which active |",
        "|---|---|---|",
    ]
    for org, d in sorted(by_org.items(), key=lambda x: -x[1]["n"]):
        lines.append(f"| {org} | {d['n']} | {d['active']} |")
    if ocha_missing:
        lines += ["", "## OCHA-coordinated on the Hub but NOT in `frameworks/` (investigate)", ""]
        for r in ocha_missing:
            lines.append(f"- **{r['country_iso3']} {r['hazard']}** — {'; '.join(r['hub_captions'])}"
                         f" (years {', '.join(r['hub_years'])})")
    if disputed:
        lines += ["", "## Hub attribution disputed (human-reviewed — no action)", ""]
        for r in disputed:
            lines.append(f"- **{r['country_iso3']} {r['hazard']}** — {'; '.join(r['hub_captions'])}: {r['dispute']}")

    # enrichment queue: every page still marked hub_stub, prioritized (IFRC/WFP/FAO
    # first per the 2026-07-09 direction, then by people targeted)
    PRIORITY = {"ifrc": 0, "wfp": 1, "fao": 2, "start-network": 3}
    queue = []
    for p in sorted(EXT.glob("*/*.md")):
        fm = parse_frontmatter(p)
        if fm and (fm.get("extra") or {}).get("hub_stub"):
            queue.append((PRIORITY.get(p.parent.name, 9),
                          -(fm.get("target_people") or 0), p.relative_to(ROOT).as_posix()))
    queue.sort()
    lines += ["", f"## Enrichment queue ({len(queue)} stubs, prioritized)", "",
              "_One dispatch per stub (headless Claude web-research → rewrite in place →"
              " PR). Run in small batches; each takes ~5-10 min:_", "", "```bash"]
    lines += [f"gh workflow run kb-ingest.yml -f page={rel}" for _, _, rel in queue]
    lines += ["```", ""]
    if not dry:
        REPORT.write_text("\n".join(lines), encoding="utf-8")
    print(f"{len(stubs)} stubs written · {len(held)} already held · {len(ocha_ok)} OCHA matched"
          f" · {len(ocha_missing)} OCHA MISSING{' (dry-run: nothing written)' if dry else ''}")


if __name__ == "__main__":
    main()
