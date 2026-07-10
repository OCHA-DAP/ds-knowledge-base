#!/usr/bin/env python3
"""Fetch the Anticipation Hub global-map inventory → external-frameworks/.hub-inventory.json.

The Hub's map is backed by a public JSON API (D76 README): an areas index
(55 countries, with ISO3) and a per-country detail endpoint whose
`category-statistic` block carries one child per framework — year, hazard,
coordinating + implementing orgs, people targeted, investment USD, doc link.
Layers: active-frameworks and under-development (same URL pattern).

This script only FETCHES + NORMALIZES (org/hazard vocab, ISO3). The stub
generator (`gen_hub_stubs.py`) consumes the inventory. Split so the network
step is re-runnable/cacheable independently of page generation.

Usage:  python scripts/fetch_hub_inventory.py   (repo root; stdlib only, ~1 min)
"""
from __future__ import annotations

import json
import re
import sys
import time
import urllib.request
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "external-frameworks" / ".hub-inventory.json"
BASE = "https://www.anticipation-hub.org"
LAYERS = ["active-frameworks", "under-development"]
UA = {"User-Agent": "Mozilla/5.0 (compatible; ds-knowledge-base inventory; OCHA-DAP)"}

# Hub icon slug / caption → our open hazard vocab (frameworks/ uses the same terms).
HAZARD_MAP = {
    "cyclone": "tropical-cyclone", "typhoon": "tropical-cyclone",
    "hurricane": "tropical-cyclone", "tropical-cyclone": "tropical-cyclone",
    "storm": "storm", "storm-surge": "storm-surge",
    "flood": "flood", "flash-flood": "flash-flood", "riverine-flood": "flood",
    "drought": "drought", "heatwave": "heatwave", "heat-wave": "heatwave",
    "cold-wave": "cold-wave", "coldwave": "cold-wave",
    "epidemic": "epidemic", "disease": "epidemic", "cholera": "cholera",
    "volcanic-eruption": "volcanic-eruption", "volcano": "volcanic-eruption",
    "landslide": "landslide", "earthquake": "earthquake",
    "food-insecurity": "food-insecurity", "dzud": "dzud",
}

# Coordinating-org caption → (display org, directory slug). Unknowns keep their
# caption and a slugified dir — open vocab, same spirit as the hazard field.
ORG_MAP = {
    "IFRC": ("IFRC", "ifrc"),
    "WFP": ("WFP", "wfp"),
    "FAO": ("FAO", "fao"),
    "Start Network": ("START", "start-network"),
    "OCHA": ("OCHA/CERF", "ocha"),
    "UNICEF": ("UNICEF", "unicef"),
    "Welthungerhilfe": ("WHH", "whh"),
}


def get_json(path: str) -> dict:
    req = urllib.request.Request(BASE + path, headers=UA)
    with urllib.request.urlopen(req, timeout=45) as r:
        return json.load(r)


def norm_hazard(icon: str, caption: str) -> str:
    m = re.search(r"category-hazard-([a-z-]+)", icon or "")
    raw = m.group(1) if m else re.sub(r"^[0-9: ]*", "", caption or "").split("(")[0].strip().lower().replace(" ", "-")
    return HAZARD_MAP.get(raw, raw or "unknown")


def value_by_label(values: list, label: str):
    for v in values or []:
        if v.get("label") == label:
            n = v.get("value")
            return int(n) if isinstance(n, (int, float)) and n else None
    return None


def main() -> None:
    records, errors = [], []
    for layer in LAYERS:
        try:
            areas = get_json(f"/experience/global-map/global-map/{layer}/areas/api.json")["areas"]
        except Exception as e:  # noqa: BLE001 — a whole layer missing is reportable, not fatal
            errors.append(f"{layer}: areas fetch failed ({e})")
            continue
        for area in areas:
            iso3, name, aid = area.get("isoCodeA3"), area.get("shortName"), area.get("id")
            try:
                detail = get_json(f"/experience/global-map/global-map/{layer}/area-detail-{aid}/api.json")
            except Exception as e:  # noqa: BLE001
                errors.append(f"{layer}/{iso3}: detail fetch failed ({e})")
                continue
            time.sleep(0.4)  # polite
            for block in detail.get("blocks", []):
                if block.get("type") != "category-statistic":
                    continue
                for ch in block.get("children", []):
                    org_raw = (ch.get("coordinating-organization") or {}).get("caption", "")
                    org, org_slug = ORG_MAP.get(org_raw, (org_raw or "unknown",
                                                          re.sub(r"[^a-z0-9]+", "-", (org_raw or "unknown").lower()).strip("-")))
                    records.append({
                        "layer": layer,
                        "country_iso3": iso3,
                        "country": name,
                        "hub_caption": ch.get("caption", ""),
                        "year": ch.get("year"),
                        "hazard": norm_hazard(ch.get("icon", ""), ch.get("caption", "")),
                        "org": org,
                        "org_slug": org_slug,
                        "org_raw": org_raw,
                        "implementing": [o.get("caption") for o in ch.get("implementing-organizations", []) if o.get("caption")],
                        "target_people": value_by_label(ch.get("values"), "People targeted"),
                        "investment_usd": value_by_label(ch.get("values"), "Investment"),
                        "framework_link": ch.get("framework-link") or None,
                    })
            print(f"  {layer} {iso3}: ok", file=sys.stderr)

    OUT.write_text(json.dumps({
        "fetched": date.today().isoformat(),
        "source": f"{BASE}/experience/global-map (JSON API, layers: {', '.join(LAYERS)})",
        "n_records": len(records),
        "errors": errors,
        "records": records,
    }, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    orgs = {}
    for r in records:
        orgs[r["org"]] = orgs.get(r["org"], 0) + 1
    print(f"{len(records)} records → {OUT.relative_to(ROOT)}  "
          f"({', '.join(f'{k}:{v}' for k, v in sorted(orgs.items(), key=lambda x: -x[1]))})"
          + (f"  [{len(errors)} errors]" if errors else ""))


if __name__ == "__main__":
    main()
