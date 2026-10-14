#!/usr/bin/env python3
"""Render mandates/registry.yml into the mandates/ pages and check it.

    python scripts/mandates_registry.py            # rewrite the tables between markers
    python scripts/mandates_registry.py --check    # only verify (extracts exist, markers resolve); exit 1 on problems

Each page may contain blocks of the form

    <!-- registry:ga-coordination -->
    ...generated table...
    <!-- /registry -->

The block name is a series key under `series:`, or one of `security-council`,
`general-assembly-addressed`, `budget-annual`, `budget-biennial`, `reference-guides`.
Everything outside the markers is hand-written and left alone (D121).
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    sys.exit("Needs pyyaml (run with ~/.config/ds-kb/venv/bin/python)")

ROOT = Path(__file__).resolve().parents[1]
REG = ROOT / "mandates" / "registry.yml"
RAW = ROOT / "raw" / "mandates"
PAGES = sorted((ROOT / "mandates").glob("*.md"))
MARK = re.compile(r"(<!-- registry:([a-z-]+) -->\n)(.*?)(<!-- /registry -->)", re.S)


def ext(name: str | None) -> str:
    if not name:
        return "—"
    return f"[`{name}`](../raw/mandates/{name})"


def series_table(block: dict) -> str:
    key = "session" if block["body"] == "General Assembly" else "session"
    head = "Session" if block["body"] == "General Assembly" else "ECOSOC session"
    rows = [f"| {head} | Symbol | Adopted | Meeting | Draft | Extract | Note |", "|---|---|---|---|---|---|---|"]
    for it in block["items"]:
        sym = it.get("symbol") or "*none*"
        adopted = it.get("adopted") or ""
        note = it.get("note", "")
        if it.get("status"):
            note = (it["status"] + (" — " + note if note else "")).strip()
            if it.get("source"):
                note += f" (source: {it['source']})"
        rows.append(f"| {it[key]} | {sym} | {adopted} | {it.get('meeting','')} | {it.get('draft','')} | {ext(it.get('extract'))} | {note} |")
    return "\n".join(rows) + "\n"


def addressed_table(items: list[dict]) -> str:
    rows = ["| Symbol | Adopted | Subject | Paragraph | What the text does with the ERC/OCHA | Extract |", "|---|---|---|---|---|---|"]
    for it in items:
        rows.append(f"| {it['symbol']} | {it.get('adopted','')} | {it.get('subject','')} | {it.get('paragraph','')} | {it.get('what','')} | {ext(it.get('extract'))} |")
    return "\n".join(rows) + "\n"


def budget_annual(items: list[dict]) -> str:
    rows = ["| Budget year | Fascicle (issued) | CPC report (session) | CPC outcome on programme 23 | Programme planning resolution | Programme budget resolution |", "|---|---|---|---|---|---|"]
    for it in items:
        rows.append(
            f"| {it['budget_year']} | {it['fascicle']} ({it['fascicle_date']}) {ext(it['fascicle_extract'])} "
            f"| {it['cpc_report']} ({it['cpc_session']}) {ext(it['cpc_extract'])} | {it['cpc_outcome']} "
            f"| {it['planning_resolution']} ({it['planning_date']}) {ext(it['planning_extract'])} "
            f"| {it['budget_resolution']} ({it['budget_date']}) {ext(it['budget_extract'])} |"
        )
    return "\n".join(rows) + "\n"


def budget_biennial(items: list[dict]) -> str:
    rows = ["| Biennium | Fascicle (issued) | Section | Extract (overview only) |", "|---|---|---|---|"]
    for it in items:
        rows.append(f"| {it['biennium']} | {it['fascicle']} ({it['fascicle_date']}) | {it['section']} | {ext(it['extract'])} |")
    return "\n".join(rows) + "\n"


def guides_table(items: list[dict]) -> str:
    rows = ["| Edition | Published | Pages | Bodies covered | Extract | Note |", "|---|---|---|---|---|---|"]
    for it in items:
        note = it.get("note", "")
        if it.get("url"):
            note = (note + " " if note else "") + f"<{it['url']}>"
        rows.append(f"| {it['edition']} | {it['published']} | {it['pages']} | {it['scope']} | {ext(it.get('extract'))} | {note} |")
    return "\n".join(rows) + "\n"


def render(name: str, reg: dict) -> str:
    if name in reg["series"]:
        return series_table(reg["series"][name])
    if name == "security-council":
        return addressed_table(reg["security-council"]["items"])
    if name == "general-assembly-addressed":
        return addressed_table(reg["general-assembly-addressed"]["items"])
    if name == "budget-annual":
        return budget_annual(reg["budget"]["annual"])
    if name == "budget-biennial":
        return budget_biennial(reg["budget"]["biennial"])
    if name == "reference-guides":
        return guides_table(reg["reference-guides"])
    raise KeyError(name)


def all_extracts(reg: dict):
    for blk in reg["series"].values():
        for it in blk["items"]:
            yield it.get("extract"), it.get("symbol") or it.get("draft")
    for k in ("security-council", "general-assembly-addressed"):
        for it in reg[k]["items"]:
            yield it.get("extract"), it["symbol"]
    for it in reg["budget"]["annual"]:
        for f in ("fascicle_extract", "cpc_extract", "planning_extract", "budget_extract"):
            yield it.get(f), it["fascicle"]
    for it in reg["budget"]["biennial"]:
        yield it.get("extract"), it["fascicle"]
    for it in reg["reference-guides"]:
        yield it.get("extract"), it["edition"]


def main(check_only: bool) -> int:
    reg = yaml.safe_load(REG.read_text())
    problems: list[str] = []
    for name, who in all_extracts(reg):
        if name and not (RAW / name).exists():
            problems.append(f"missing extract {name} ({who})")
    seen = set()
    for page in PAGES:
        text = page.read_text()
        def sub(m: re.Match) -> str:
            seen.add(m.group(2))
            try:
                body = render(m.group(2), reg)
            except KeyError:
                problems.append(f"{page.name}: unknown registry block {m.group(2)}")
                return m.group(0)
            return m.group(1) + body + m.group(4)
        new = MARK.sub(sub, text)
        if new != text:
            if check_only:
                problems.append(f"{page.name}: generated tables are stale (run without --check)")
            else:
                page.write_text(new)
                print(f"updated {page.relative_to(ROOT)}")
    for p in problems:
        print("PROBLEM:", p)
    if not problems:
        print(f"ok — {len(seen)} blocks, {sum(1 for n,_ in all_extracts(reg) if n)} extracts present")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main("--check" in sys.argv))
