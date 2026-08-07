#!/usr/bin/env python3
"""Deterministic drift check for the KB's *how-it-works* docs (the meta-docs).

The content layer self-maintains (drift / freshness / discovery → kb-ingest). The
meta-docs — DESIGN, ROADMAP, INGESTION, automation, the READMEs — had no detector
and rotted silently (stale counts, dangling script refs). This is their drift axis.

It is the *mechanical* half (high-signal, no judgment); the prose-staleness half
(shipped phases still marked todo, superseded rationale) is the monthly Claude
audit in `docs-audit.yml`. Two checks here:

  MISSING-REF   a meta-doc mentions a `scripts/<x>.py|.sh` or `.github/workflows/<x>.yml`
                that no longer exists on disk (renamed/deleted but the doc still names it).
  STALE-COUNTS  a doc's <!-- COUNTS --> block disagrees with the live corpus
                (someone added pages but didn't run gen_doc_counts.py).
  STALE-INFRA   a hand-written infrastructure/ page's `last_reviewed` is > 6 months old
                (generated pages are exempt — their generators keep them current). Fix by
                re-verifying the page against reality and bumping the date (or via kb-ingest).
  NO-REVIEW-STAMP  a hand-written infrastructure/ page has no `last_reviewed` frontmatter —
                it's invisible to staleness tracking; add the stamp.
  NO-CENTROID   a framework page's country_iso3 has no entry in gen_public_site.COUNTRY —
                the country silently vanishes from the public AA map (real miss: Nicaragua).
  PDF-LINK      an OCHA framework page's `framework_doc` is a direct `/attachments/…` PDF
                download instead of the document's landing page — clicking it downloads the
                file instead of opening a page. Link the ReliefWeb/unocha *report page*
                (find it via the ReliefWeb API by matching the attachment UUID). OCHA
                frameworks only; `external-frameworks/` is exempt.
  WORKFLOW-UNDOCUMENTED  a `.github/workflows/*.yml` exists that automation.md never
                mentions — the "every automation at a glance" table is the map of every
                path into the repo, so an unlisted workflow is invisible (real miss:
                hub-backlog-fill.yml ran daily for weeks undocumented).
  WORKFLOW-CADENCE  automation.md's row for a workflow disagrees with the file's actual
                `schedule:` — a cron time the row doesn't mention, or a row implying a
                schedule for a workflow whose cron is commented out / absent (real miss:
                infra-drift.yml shown as a live daily cron while ⏸ dispatch-only).
  WORKFLOW-GONE  automation.md names a `<name>.yml` that isn't in `.github/workflows/`.
  FUTURE-CLAIM  a forward-looking claim ("will add", "not yet", "planned", "once
                enabled"…) in a meta-doc is > FUTURE_CLAIM_AGE_DAYS old by git blame —
                forward-looking claims rot fastest (real miss: "a separate tier will add
                DB access" sat 5+ weeks after the tier shipped). Verify it still holds,
                then reword to present tense or re-date the line (editing the line resets
                its blame age — that's the ack mechanism). Timeless procedural rules and
                external-project roadmap facts opt out with an inline `<!-- timeless -->`.
                Needs full git history (fetch-depth: 0 in CI); silently skipped on
                shallow clones.

Broken *markdown* links are covered by `lint-docs.yml` (`scripts/check_links.py`), so
they're not re-checked here.

Usage:  python scripts/check_docs.py [--report docs-report.md]
Exit:   0 = clean · 2 = at least one finding
Needs:  pyyaml.
"""
from __future__ import annotations
import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
import gen_doc_counts as gdc  # noqa: E402  (sibling module; reuse its COUNTS logic)

# The meta-docs: "how the KB works", not the content pages.
META_DOCS = [
    "README.md", "CLAUDE.md",
    "docs/DESIGN.md", "docs/INGESTION.md", "docs/ROADMAP.md", "docs/PRIVACY.md",
    "docs/README.md", "docs/glossary.md", "docs/USING.md", "docs/I18N.md",
    "docs/repo-manifest.md", "docs/repo-doc-crosswalk.md",
    "infrastructure/automation.md", "scripts/README.md",
]

# Path-qualified references to project machinery. Anchored to the known dirs so we
# don't false-positive on prose. Trailing punctuation/backticks are trimmed.
REF_RE = re.compile(r"(scripts/[A-Za-z0-9_./-]+\.(?:py|sh)|\.github/workflows/[A-Za-z0-9_.-]+\.ya?ml)")

# Refs the docs name correctly but that are absent from this repo by design:
#   drive-sync.yml lives in the PRIVATE companion repo, ds-knowledge-base-internal (D46);
#   setup_team_claude.sh was deleted on purpose (D81) and DESIGN.md's decision log names it as
#   history — a decision log has to be able to talk about files that no longer exist.
EXEMPT_REFS = {".github/workflows/drive-sync.yml", "scripts/setup_team_claude.sh"}


def find_missing_refs() -> list[tuple[str, str, str]]:
    rows = []
    for rel in META_DOCS:
        path = ROOT / rel
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        seen = set()
        for m in REF_RE.finditer(text):
            ref = m.group(1).rstrip(".,)`")
            if ref in seen or ref in EXEMPT_REFS:
                continue
            seen.add(ref)
            if not (ROOT / ref).exists():
                rows.append((rel, "MISSING-REF", ref))
    return rows


STALE_AFTER_DAYS = 180
# Generated pages self-update on their own schedules; only hand-written reference pages rot silently.
_GENERATED_MARKERS = ("generated by", "DO NOT EDIT")


def find_stale_infra() -> list[tuple[str, str, str]]:
    import datetime
    import itertools

    import yaml

    rows = []
    today = datetime.date.today()
    # methods/ pages are hand-written reference too (same silent-rot class as infrastructure/)
    paths = itertools.chain(sorted((ROOT / "infrastructure").glob("*.md")),
                            sorted((ROOT / "methods").glob("*.md")))
    for path in paths:
        text = path.read_text(encoding="utf-8")
        head = "\n".join(text.splitlines()[:6])
        if any(m.lower() in head.lower() for m in _GENERATED_MARKERS):
            continue
        rel = path.relative_to(ROOT).as_posix()
        fm = {}
        if text.startswith("---"):
            try:
                fm = yaml.safe_load(text[3:text.find("\n---", 3)]) or {}
            except yaml.YAMLError:
                pass
        stamp = fm.get("last_reviewed")
        if not stamp:
            rows.append((rel, "NO-REVIEW-STAMP",
                         "no `last_reviewed` frontmatter — add it so staleness tracking sees this page"))
            continue
        try:
            age = (today - datetime.date.fromisoformat(str(stamp))).days
        except ValueError:
            rows.append((rel, "NO-REVIEW-STAMP", f"unparseable `last_reviewed: {stamp}` (want YYYY-MM-DD)"))
            continue
        if age > STALE_AFTER_DAYS:
            rows.append((rel, "STALE-INFRA",
                         f"`last_reviewed: {stamp}` is {age} days old — re-verify the page against reality and bump the date"))
    return rows


def find_missing_centroids() -> list[tuple[str, str, str]]:
    import yaml

    import gen_public_site as gps

    rows, seen = [], set()
    for path in sorted((ROOT / "frameworks").glob("*/*.md")):
        if path.name in ("README.md", "_TEMPLATE.md"):
            continue
        text = path.read_text(encoding="utf-8")
        if not text.startswith("---"):
            continue
        try:
            fm = yaml.safe_load(text[3:text.find("\n---", 3)]) or {}
        except yaml.YAMLError:
            continue
        if fm.get("content_type") != "framework":
            continue
        iso3s = fm.get("country_iso3")
        iso3s = iso3s if isinstance(iso3s, list) else [iso3s]
        for iso3 in iso3s:
            iso3 = str(iso3 or "").upper()
            if iso3 and iso3 not in gps.COUNTRY and iso3 not in seen:
                seen.add(iso3)
                rows.append((path.relative_to(ROOT).as_posix(), "NO-CENTROID",
                             f"`{iso3}` has no entry in gen_public_site.py COUNTRY/DIRECTIONS — "
                             "it will NOT render on the public AA map"))
    return rows


def find_pdf_download_links() -> list[tuple[str, str, str]]:
    """Framework pages must link the doc's landing page, not the raw PDF.

    A `framework_doc` of the form …/attachments/<uuid>/<file>.pdf (or any URL
    whose path ends in .pdf) force-downloads on click; human-facing links
    (catalog, AA site, READMEs — all generated from this field) should open the
    report page instead. The extract/freshness chain resolves landing pages fine
    (ReliefWeb API + committed raw/.pdf-cache), so a direct PDF is never needed
    here. Applies to OCHA frameworks/ AND — going forward — external-frameworks/
    (D90 addendum): existing external offenders are grandfathered below rather
    than retro-fixed (user, 2026-07-25); new pages must use landing pages.
    """
    import urllib.parse

    import yaml

    grandfathered = {
        "external-frameworks/fao/afg-drought.md",
        "external-frameworks/fao/mdg-drought.md",
        "external-frameworks/fao/pak-drought.md",
        "external-frameworks/fao/phl-typhoon.md",
        "external-frameworks/fao/yem-drought.md",
        "external-frameworks/ifrc/kaz-cold-wave.md",
        "external-frameworks/ifrc/lso-cold-wave.md",
        "external-frameworks/wfp/eth-drought.md",
        "external-frameworks/wfp/mdg-drought.md",
        "external-frameworks/world-vision-international/irq-drought.md",
    }
    rows = []
    for pattern in ("frameworks/*/*.md", "external-frameworks/*/*.md"):
        for path in sorted(ROOT.glob(pattern)):
            rel = path.relative_to(ROOT).as_posix()
            if path.name in ("README.md", "_TEMPLATE.md") or rel in grandfathered:
                continue
            text = path.read_text(encoding="utf-8")
            if not text.startswith("---"):
                continue
            try:
                fm = yaml.safe_load(text[3:text.find("\n---", 3)]) or {}
            except yaml.YAMLError:
                continue
            if fm.get("content_type") not in ("framework", "framework-external"):
                continue
            doc = fm.get("framework_doc")
            if not isinstance(doc, str):
                continue
            if "/attachments/" in doc or urllib.parse.urlparse(doc).path.lower().endswith(".pdf"):
                rows.append((rel, "PDF-LINK",
                             "`framework_doc` is a direct PDF download — link the document's "
                             "landing page (report/publication page) instead"))
    return rows


AUTOMATION_MD = "infrastructure/automation.md"
# Workflows that live elsewhere by design (drive-sync.yml → the private companion repo).
EXEMPT_WORKFLOW_NAMES = {"drive-sync.yml"}

_CRON_RE = re.compile(r'^(\s*#?\s*)-\s*cron:\s*["\']([^"\']+)["\']')


def _workflow_crons(path: Path) -> tuple[list[str], bool]:
    """(active cron exprs, has_commented_cron) for a workflow file."""
    active, commented = [], False
    for line in path.read_text(encoding="utf-8").splitlines():
        m = _CRON_RE.match(line)
        if not m:
            continue
        if "#" in m.group(1):
            commented = True
        else:
            active.append(m.group(2))
    return active, commented


def _cron_hhmm(expr: str) -> str | None:
    parts = expr.split()
    if len(parts) == 5 and parts[0].isdigit() and parts[1].isdigit():
        return f"{int(parts[1]):02d}:{int(parts[0]):02d}"
    return None


def find_workflow_drift() -> list[tuple[str, str, str]]:
    """Diff .github/workflows/ (ground truth) against automation.md's claims.

    Deterministic rules only:
      - every workflow file must be mentioned in automation.md somewhere;
      - if a workflow has an active cron, the table row naming it must contain
        that cron's HH:MM;
      - if it has NO active cron, a row containing an HH:MM time must also say
        ⏸ / manual / dispatch / local (i.e. admit the schedule isn't CI's);
      - every `<name>.yml` automation.md names must exist on disk.
    """
    rows = []
    doc_path = ROOT / AUTOMATION_MD
    doc = doc_path.read_text(encoding="utf-8")
    doc_lines = doc.splitlines()
    wf_dir = ROOT / ".github" / "workflows"

    for wf in sorted(wf_dir.glob("*.y*ml")):
        name = wf.name
        if name in EXEMPT_WORKFLOW_NAMES:
            continue
        # Word-boundary match so `site.yml` doesn't ride along on `refresh-site.yml`.
        name_re = re.compile(rf"(?<![A-Za-z0-9_-]){re.escape(name)}")
        if not name_re.search(doc):
            rows.append((AUTOMATION_MD, "WORKFLOW-UNDOCUMENTED",
                         f"`.github/workflows/{name}` exists but automation.md never mentions it — "
                         "add a row to the 'every automation at a glance' table"))
            continue
        # The glance-table row (first table line naming the workflow).
        row = next((ln for ln in doc_lines if ln.startswith("|") and name_re.search(ln)), None)
        if row is None:
            continue  # mentioned in prose only — presence is enough
        active, _ = _workflow_crons(wf)
        times = [t for t in (_cron_hhmm(c) for c in active) if t]
        if active:
            missing = [t for t in times if t not in row]
            if missing:
                rows.append((AUTOMATION_MD, "WORKFLOW-CADENCE",
                             f"`{name}` runs at {', '.join(missing)} UTC but its table row doesn't "
                             f"say so (row cadence text disagrees with the file's `schedule:`)"))
        elif re.search(r"\d{2}:\d{2}", row) and not re.search(r"⏸|manual|dispatch|local", row):
            rows.append((AUTOMATION_MD, "WORKFLOW-CADENCE",
                         f"`{name}` has no active cron (dispatch/push only) but its table row "
                         "implies a schedule — mark it ⏸ / manual-only"))

    on_disk = {p.name for p in wf_dir.glob("*.y*ml")}
    seen = set()
    for m in re.finditer(r"`([a-z0-9_-]+\.ya?ml)`", doc):
        name = m.group(1)
        if name in seen or name in EXEMPT_WORKFLOW_NAMES or name in on_disk:
            continue
        seen.add(name)
        rows.append((AUTOMATION_MD, "WORKFLOW-GONE",
                     f"automation.md names `{name}` but no such file exists in `.github/workflows/`"))
    return rows


FUTURE_CLAIM_AGE_DAYS = 45
# Lines carrying this marker are exempt: timeless procedural rules ("a trigger may not
# yet be endorsed") or external-project roadmap facts, which would otherwise nag forever.
# Our own systems' status claims should never need it — they either ship or get re-dated.
_TIMELESS_MARKER = "<!-- timeless -->"
# Tight patterns — forward-looking phrasing that should either ship or be re-dated.
_FUTURE_RES = [
    re.compile(p, re.IGNORECASE)
    for p in (r"\bnot yet\b", r"\bwill (?:add|be able|become|gain|get|start|support)\b",
              r"\bcoming soon\b", r"\bplanned\b", r"\bdormant until\b",
              r"\bonce (?:enabled|set|added|created|trusted|merged)\b")
]
# Append-only / frozen docs legitimately contain old forward-looking prose.
FUTURE_CLAIM_EXEMPT = {"docs/DESIGN.md", "docs/repo-manifest.md", "docs/repo-doc-crosswalk.md"}


def _blame_ages(rel: str, line_nos: list[int]) -> dict[int, int]:
    """line_no -> age in days of its last edit, via one git blame pass. {} if unavailable."""
    import datetime
    import subprocess

    if not line_nos:
        return {}
    cmd = ["git", "blame", "--line-porcelain"]
    for n in line_nos:
        cmd += ["-L", f"{n},{n}"]
    cmd.append(rel)
    try:
        out = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, check=True).stdout
    except (subprocess.CalledProcessError, FileNotFoundError):
        return {}
    ages, ts = {}, None
    today = datetime.date.today()
    for line in out.splitlines():
        if line.startswith("committer-time "):
            ts = int(line.split()[1])
        elif line.startswith("\t") and ts is not None:
            n = line_nos[len(ages)] if len(ages) < len(line_nos) else None
            if n is not None:
                ages[n] = (today - datetime.date.fromtimestamp(ts)).days
            ts = None
    return ages


def find_future_claims() -> list[tuple[str, str, str]]:
    """Age-gated lint on forward-looking claims (skipped silently on shallow clones)."""
    import itertools

    rows = []
    infra = [p.relative_to(ROOT).as_posix() for p in sorted((ROOT / "infrastructure").glob("*.md"))
             if not any(m.lower() in "\n".join(p.read_text(encoding="utf-8").splitlines()[:6]).lower()
                        for m in _GENERATED_MARKERS)]
    for rel in itertools.chain(META_DOCS, infra):
        if rel in FUTURE_CLAIM_EXEMPT or not (ROOT / rel).exists():
            continue
        lines = (ROOT / rel).read_text(encoding="utf-8").splitlines()
        hits = [(i + 1, ln) for i, ln in enumerate(lines)
                if _TIMELESS_MARKER not in ln and any(rx.search(ln) for rx in _FUTURE_RES)]
        ages = _blame_ages(rel, [n for n, _ in hits])
        for n, ln in hits:
            age = ages.get(n)
            if age is not None and age > FUTURE_CLAIM_AGE_DAYS:
                snippet = ln.strip()[:100]
                rows.append((rel, "FUTURE-CLAIM",
                             f"line {n} ({age}d old): “{snippet}” — verify this is still pending; "
                             "if shipped, reword; if genuinely still future, re-date the line"))
    return rows


def find_stale_counts() -> list[tuple[str, str, str]]:
    rows = []
    body = gdc.block(gdc.counts())
    for path in gdc.TARGETS:
        if path.exists() and not gdc.is_current(path, body):
            rows.append((path.relative_to(ROOT).as_posix(), "STALE-COUNTS",
                         "COUNTS block disagrees with the live corpus — run `python scripts/gen_doc_counts.py`"))
    return rows


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", help="write the markdown report to this file")
    args = ap.parse_args()

    rows = (find_stale_counts() + find_missing_refs() + find_stale_infra()
            + find_missing_centroids() + find_pdf_download_links()
            + find_workflow_drift() + find_future_claims())

    lines = ["# KB meta-doc check", ""]
    if rows:
        lines.append(f"**{len(rows)} finding(s).**")
        lines += ["", "| doc | issue | detail |", "|---|---|---|"]
        lines += [f"| `{d}` | **{k}** | {v} |" for d, k, v in rows]
        lines += [
            "",
            "_Fix: `STALE-COUNTS` → run `python scripts/gen_doc_counts.py`. "
            "`MISSING-REF` → update the doc to the new path, or restore the file. "
            "`STALE-INFRA` / `NO-REVIEW-STAMP` → re-verify the infrastructure page and bump/add "
            "its `last_reviewed` date. "
            "`PDF-LINK` → replace the direct PDF link with the document's landing page. "
            "`WORKFLOW-*` → reconcile automation.md's glance table with `.github/workflows/`. "
            "`FUTURE-CLAIM` → verify the claim; reword if shipped, re-date the line if still pending. "
            "Prose staleness (shipped phases, superseded rationale) is handled by the monthly "
            "`docs-audit.yml` Claude pass._",
        ]
    else:
        lines.append("✅ Meta-docs clean: counts current, all script/workflow references resolve.")
    report = "\n".join(lines) + "\n"

    print(report)
    if args.report:
        Path(args.report).write_text(report, encoding="utf-8")
    sys.exit(2 if rows else 0)


if __name__ == "__main__":
    main()
