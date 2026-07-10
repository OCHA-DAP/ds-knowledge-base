#!/usr/bin/env python3
"""Generate the PUBLIC-FACING frameworks site → ./index.html (repo root).

A self-contained static page with:
  * a status map (active / development / retired, with activations flagged);
  * an **Active frameworks** table (current version of each, multi-country
    frameworks split to one row per country);
  * an **All versions** table (every version incl. superseded/retired).

Each row: country (full name), hazard, AOI (admin areas), status, activations,
trigger windows, pre-arranged funding, target people, the published framework
doc, and a link to the source repo.

PUBLIC-SAFE BY CONSTRUCTION: only fields already in the published framework PDF
(or public CERF/AHF announcements) are emitted. It strips internal asides
(discrepancy notes, repo-implementation values) and NEVER emits discrepancies,
source_branch/sha, code_ref, repo_completeness, dev-slot notes, or visibility.
A private source repo is shown as "🔒 private" (name withheld), not linked.

GitHub Pages serves it from the main branch root (./index.html, with ./.nojekyll
so files are served as-is). Just regenerate and commit to main — no gh-pages branch.

Usage:  python scripts/gen_public_site.py   (from repo root)
"""
from __future__ import annotations
import datetime
import html
import json
import re
from pathlib import Path

try:
    import yaml
except ImportError:
    import sys
    sys.exit("Needs pyyaml")

ROOT = Path(__file__).resolve().parent.parent
FW = ROOT / "frameworks"
OUT = ROOT / "index.html"   # served by GitHub Pages from the main branch root
MAXLEN = 120

# Computed display statuses that count as "active" (shown in the Active table /
# coloured as a live pin). Expired / superseded / retired versions drop out.
ACTIVE_STATUSES = {"recently-triggered", "endorsed", "pre-development", "development"}
STATUS_RANK = {"recently-triggered": 0, "endorsed": 1, "pre-development": 2,
               "development": 3, "expired": 4, "superseded": 5, "retired": 6}

# iso3 → (display name, lat, lon centroid for the map)
COUNTRY = {
    "AFG": ("Afghanistan", 33.9, 67.7), "BFA": ("Burkina Faso", 12.2, -1.6),
    "BGD": ("Bangladesh", 23.7, 90.4), "COD": ("DR Congo", -2.9, 23.6),
    "CUB": ("Cuba", 21.7, -79.5), "ETH": ("Ethiopia", 9.1, 40.5),
    "FJI": ("Fiji", -17.7, 178.0), "GTM": ("Guatemala", 15.7, -90.2),
    "HND": ("Honduras", 15.0, -86.5), "HTI": ("Haiti", 19.0, -72.3),
    "KEN": ("Kenya", 0.2, 37.9), "MDG": ("Madagascar", -18.8, 46.9),
    "MMR": ("Myanmar", 21.0, 96.0), "MOZ": ("Mozambique", -18.0, 35.5),
    "MRT": ("Mauritania", 20.5, -10.9), "MWI": ("Malawi", -13.3, 34.3),
    "NIC": ("Nicaragua", 12.9, -85.2),
    "NER": ("Niger", 17.6, 9.4),
    "NGA": ("Nigeria", 9.1, 8.7), "NPL": ("Nepal", 28.2, 84.0),
    "PHL": ("Philippines", 12.9, 121.8), "PLW": ("Palau", 7.5, 134.6),
    "SLV": ("El Salvador", 13.8, -88.9), "SOM": ("Somalia", 5.2, 46.2),
    "SSD": ("South Sudan", 7.3, 30.3), "TCD": ("Chad", 15.5, 18.7),
    "VUT": ("Vanuatu", -16.5, 168.0), "YEM": ("Yemen", 15.6, 48.0),
}

# per-country CERF envelope for multi-country frameworks (doc-stated; total = sum)
COUNTRY_FUNDING_SPLIT = {
    "lac-dry-corridor": {"GTM": 4_000_000, "HND": 4_000_000, "SLV": 2_500_000},
}

# Preferred callout direction per country (screen vector, +y = down) — hand-set so
# labels fan into open sea / empty land like the OCHA portfolio graphic. The
# collision resolver only nudges from here, so the overall layout stays sensible.
DIRECTIONS = {
    "AFG": (0.2, -1), "BFA": (-1, 0.2), "BGD": (0.7, -0.8), "COD": (-0.9, 0.5),
    "CUB": (-0.9, -0.4), "ETH": (0.7, -0.5), "FJI": (-0.6, 0.8), "GTM": (-1, -0.3),
    "HND": (0.3, 1), "HTI": (1, 0.3), "KEN": (1, 0.25), "MDG": (1, 0.1),
    "MMR": (0.8, 0.5), "MOZ": (0.6, 0.8), "MRT": (-0.85, -0.5), "MWI": (-0.9, 0.3),
    "NER": (-0.2, -1),
    "NGA": (-0.6, 0.85), "NIC": (0.9, 0.6), "NPL": (0.1, -1), "PHL": (1, -0.1), "SLV": (-0.8, 0.7),
    "SOM": (1, 0.2), "SSD": (-0.5, -0.8),
    "TCD": (0.5, -1), "VUT": (-0.7, -0.5), "YEM": (1, -0.1),
}

# Map: pin colour = lifecycle state; a red dot flags activation.
MAP_COLOR = {"endorsed": "#2171b5", "recently-triggered": "#e0706a",
             "expired": "#b2a56e", "development": "#9ecae1", "retired": "#b6bcc4"}
ACT_COLOR = "#e3322d"

# Lifecycle (computed, NOT a stored status): development → endorsed → then,
# depending on what happens within the version's validity period —
#   • it ACTIVATES → "recently-triggered": stays there until a human updates the
#     version (a newer version supersedes it, or it's explicitly retired);
#   • validity ENDS without it ever firing → "expired": also stays until a human
#     updates it (re-opened as development, or explicitly retired).
# An activation only counts toward the version live when it fired (date ≥ version
# date), so a version re-endorsed AFTER an earlier trigger reads "endorsed".
# "retired" is only ever set explicitly (a deliberate human decision, e.g.
# Yemen) — never reached automatically; there is no time-based decay.
TODAY = datetime.date.today()
CURRENT_MONTH = TODAY.month  # drives the "currently monitored" green ring on the map
CURRENT_MONTH_LABEL = TODAY.strftime("%B %Y")  # e.g. "June 2026" — shown in the legend


def _parse_ym(s) -> tuple[int, int] | None:
    m = re.match(r"\s*(\d{4})(?:-(\d{1,2}))?", str(s or ""))
    return (int(m.group(1)), int(m.group(2) or 1)) if m else None


def own_activation_ym(acts: list, version) -> tuple[int, int] | None:
    """Latest activation that fired DURING this version's reign (date ≥ version
    date). Earlier activations belong to prior versions and don't count.

    Only a FULL ('all-in') activation flips a framework to recently-triggered.
    A partial window trigger — one window firing in a framework where that does
    NOT release the whole envelope — is recorded with `full_activation: false`
    and is ignored here, so the framework stays Active (e.g. tcd-drought)."""
    vintage = _parse_ym(version)
    yms = [ym for a in acts if isinstance(a, dict) and a.get("full_activation", True) is not False
           and (ym := _parse_ym(a.get("date"))) and (vintage is None or ym >= vintage)]
    return max(yms) if yms else None


def is_expired(valid_until) -> bool:
    """True once the validity period has fully elapsed. `valid_until` is a single
    end value: YYYY (→ end of that year), YYYY-MM, or YYYY-MM-DD. Anything else
    (null, a range, prose) → not expired."""
    m = re.match(r"(\d{4})(?:-(\d{1,2})(?:-\d{1,2})?)?$", str(valid_until or "").strip())
    if not m:
        return False
    mo = int(m.group(2)) if m.group(2) and 1 <= int(m.group(2)) <= 12 else 12
    return (int(m.group(1)), mo) < (TODAY.year, TODAY.month)


def display_status(stored: str, acts: list, version=None, valid_until=None) -> str:
    """Effective status for display, computed — never a stored field. Stored
    development/pre-development/superseded/retired pass through unchanged. An
    endorsed version that fired under its own reign reads 'recently-triggered'
    (until a human updates it); one whose validity period has ended without ever
    firing reads 'expired'. (Legacy stored 'triggered' is treated as endorsed.)"""
    if stored not in ("endorsed", "triggered", ""):
        return stored
    if own_activation_ym(acts, version):
        return "recently-triggered"
    if is_expired(valid_until):
        return "expired"
    return "endorsed"


# ---- "able to trigger" (capacity) — distinct from lifecycle status ----------
# After a framework activates it generally can't fire again this period (the pre-arranged envelope
# is spent). Exceptions, which stay able to trigger after an activation:
#   • cholera — recurring, designed to fire multiple times;
#   • multi-window SPLIT frameworks (not all-in) — each window has its own budget, so the windows
#     that haven't fired can still trigger. Default is all-in (one envelope); set frontmatter
#     `all_in: false` on the (few) split frameworks.
def _is_cholera(fm) -> bool:
    h = str(fm.get("hazard", "")).lower()
    return "cholera" in h or "infectious" in h or "cholera" in str(fm.get("framework", "")).lower()

def _n_windows(fm) -> int:
    try:
        return int((fm.get("trigger_facets") or {}).get("n_windows") or 0)
    except (TypeError, ValueError):
        return 0

def _is_all_in(fm) -> bool:
    v = fm.get("all_in")
    if v is None:
        return True                       # default: one envelope, exhausts on activation
    return str(v).strip().lower() in ("true", "yes", "1")

def retriggerable(fm) -> bool:
    """Can it still fire AFTER an activation? Cholera always; otherwise only multi-window split."""
    return _is_cholera(fm) or (_n_windows(fm) > 1 and not _is_all_in(fm))

def able_to_trigger(fm, disp: str) -> bool:
    """Capacity to fire now: a live version (endorsed / recently-triggered) that hasn't exhausted
    its envelope. A version that fired under its own reign is exhausted unless it can retrigger."""
    if disp not in ("endorsed", "recently-triggered"):
        return False                      # expired / superseded / retired / development → can't fire
    if disp == "recently-triggered" and not retriggerable(fm):
        return False                      # fired its single/all-in envelope → exhausted
    return True


def status_bucket(status: str) -> str:
    if status in ("recently-triggered", "expired"):
        return status
    if status in ("endorsed", "triggered"):
        return "endorsed"
    if status in ("development", "pre-development"):
        return "development"
    return "retired"


def pretty_hazard(h: str) -> str:
    return {"tropical-cyclone": "Trop. cyclones", "flood": "Floods", "drought": "Drought",
            "cholera": "Cholera"}.get(h, (h or "").replace("-", " ").capitalize())


# Hazard glyphs (white, viewBox 0 0 24 24) — stylised after the OCHA humanitarian
# icon set. Swap in the official SVGs here if exact marks are required.
HAZARD_SVG = {
    "drought": '<circle cx="12" cy="12" r="3.6" fill="#fff"/><g stroke="#fff" stroke-width="1.7" stroke-linecap="round">'
               '<line x1="12" y1="2.5" x2="12" y2="5.5"/><line x1="12" y1="18.5" x2="12" y2="21.5"/>'
               '<line x1="2.5" y1="12" x2="5.5" y2="12"/><line x1="18.5" y1="12" x2="21.5" y2="12"/>'
               '<line x1="5.2" y1="5.2" x2="7.3" y2="7.3"/><line x1="16.7" y1="16.7" x2="18.8" y2="18.8"/>'
               '<line x1="18.8" y1="5.2" x2="16.7" y2="7.3"/><line x1="7.3" y1="16.7" x2="5.2" y2="18.8"/></g>',
    "flood": '<g fill="none" stroke="#fff" stroke-width="1.8" stroke-linecap="round">'
             '<path d="M2 8.5c2 0 2 2 4 2s2-2 4-2 2 2 4 2 2-2 4-2 2 2 4 2"/>'
             '<path d="M2 13.5c2 0 2 2 4 2s2-2 4-2 2 2 4 2 2-2 4-2 2 2 4 2"/>'
             '<path d="M2 18.5c2 0 2 2 4 2s2-2 4-2 2 2 4 2 2-2 4-2 2 2 4 2"/></g>',
    "tropical-cyclone": '<circle cx="12" cy="12" r="2.2" fill="#fff"/>'
             '<g fill="none" stroke="#fff" stroke-width="1.8" stroke-linecap="round">'
             '<path d="M12 4.2c4.2 0 7 2.1 7 5 0 2-1.8 3.2-4 3.2"/>'
             '<path d="M12 19.8c-4.2 0-7-2.1-7-5 0-2 1.8-3.2 4-3.2"/></g>',
    "cholera": '<circle cx="12" cy="12" r="3.2" fill="#fff"/>'
             '<g stroke="#fff" stroke-width="1.6" stroke-linecap="round">'
             '<line x1="12" y1="4" x2="12" y2="6.4"/><line x1="12" y1="17.6" x2="12" y2="20"/>'
             '<line x1="4" y1="12" x2="6.4" y2="12"/><line x1="17.6" y1="12" x2="20" y2="12"/>'
             '<line x1="6.3" y1="6.3" x2="8" y2="8"/><line x1="16" y1="16" x2="17.7" y2="17.7"/>'
             '<line x1="17.7" y1="6.3" x2="16" y2="8"/><line x1="8" y1="16" x2="6.3" y2="17.7"/></g>'
             '<g fill="#fff"><circle cx="12" cy="3.6" r="1.1"/><circle cx="12" cy="20.4" r="1.1"/>'
             '<circle cx="3.6" cy="12" r="1.1"/><circle cx="20.4" cy="12" r="1.1"/></g>',
    "other": '<circle cx="12" cy="12" r="3.5" fill="#fff"/>',
}


def frontmatter(path: Path) -> dict | None:
    t = path.read_text(encoding="utf-8")
    if not t.startswith("---"):
        return None
    e = t.find("\n---", 3)
    if e == -1:
        return None
    try:
        return yaml.safe_load(t[3:e]) or {}
    except yaml.YAMLError:
        return None


def as_list(v) -> list:
    return [] if v is None else (v if isinstance(v, list) else [v])


def clean(s: str) -> str:
    s = str(s)
    s = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", s)
    s = s.replace("**", "").replace("`", "")
    s = re.sub(r"\s*\([^()]*discrepanc[^()]*\)", "", s, flags=re.I)
    s = re.sub(r"\s*[—-]+\s*see discrepanc\w*", "", s, flags=re.I)
    s = re.sub(r"\s*\([^()]*\bin code\b[^()]*\)", "", s, flags=re.I)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def truncate(s: str, n: int = MAXLEN) -> str:
    return s if len(s) <= n else s[: n - 1].rstrip() + "…"


def load_private_repos() -> set[str]:
    """Slugs flagged private/internal in the spoke-repo registry (lowercase)."""
    out = set()
    reg = ROOT / "infrastructure" / "spoke-repos.md"
    if reg.exists():
        for line in reg.read_text(encoding="utf-8").splitlines():
            if "private" in line.lower() or "internal" in line.lower():
                m = re.search(r"ocha-dap/[A-Za-z0-9._-]+", line, re.I)
                if m:
                    out.add(m.group(0).lower())
    return out


PRIVATE_REPOS = load_private_repos()


def parse_windows(path: Path) -> list[dict]:
    lines = path.read_text(encoding="utf-8").splitlines()
    try:
        start = next(i for i, l in enumerate(lines) if l.strip().lower().startswith("## trigger window"))
    except StopIteration:
        return []
    # Collect ONLY the first contiguous pipe-table under the heading. Some pages
    # put a second table (e.g. per-province thresholds) right after the windows
    # table — stop at the blank line between them so it isn't merged in.
    tbl, started = [], False
    for l in lines[start + 1:]:
        if l.strip().startswith("## "):
            break
        if l.lstrip().startswith("|"):
            started = True
            tbl.append(l)
        elif started:
            break
    if len(tbl) < 2:
        return []
    def cells(row):
        return [c.strip() for c in row.strip().strip("|").split("|")]
    header = [h.lower() for h in cells(tbl[0])]
    def col(*keys):
        for i, h in enumerate(header):
            if any(k in h for k in keys):
                return i
        return None
    ci = {"window": col("window"), "indicator": col("indicator"), "threshold": col("threshold")}
    out = []
    for row in tbl[2:]:
        if set(row.strip()) <= {"|", "-", " ", ":"}:
            continue
        c = cells(row)
        def g(key):
            i = ci[key]
            return clean(c[i]) if i is not None and i < len(c) else ""
        if g("window"):
            out.append({"window": g("window"), "indicator": g("indicator"), "threshold": g("threshold")})
    return out


MONTH_ABBR = ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun",
              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def fmt_months(months) -> str:
    """Compact a month-int list into season spans: [11,12,1,2,3,4] -> 'Nov–Apr'."""
    ms = sorted({int(m) for m in as_list(months) if isinstance(m, (int, float))})
    if not ms:
        return "—"
    if len(ms) == 12:
        return "year-round"
    runs, start, prev = [], ms[0], ms[0]
    for m in ms[1:]:
        if m == prev + 1:
            prev = m
        else:
            runs.append((start, prev))
            start = prev = m
    runs.append((start, prev))
    if len(runs) >= 2 and runs[0][0] == 1 and runs[-1][1] == 12:  # wrap Dec->Jan
        first, last = runs.pop(0), runs.pop(-1)
        runs.insert(0, (last[0], first[1]))
    fmt = lambda a, b: MONTH_ABBR[a] if a == b else f"{MONTH_ABBR[a]}–{MONTH_ABBR[b]}"
    return ", ".join(fmt(a, b) for a, b in runs)


def fmt_funding(v) -> str:
    return f"${v/1e6:.1f}M" if isinstance(v, (int, float)) and v > 0 else "—"


def fmt_people(v) -> str:
    return f"{int(v):,}" if isinstance(v, (int, float)) and v > 0 else "—"


def fmt_aoi(v) -> str:
    items = as_list(v)
    return "; ".join(clean(str(x)) for x in items) if items else "—"


def display_aoi(scope, iso3: str) -> str:
    """AOI for a single-country row; a bare country code/name → 'National'."""
    items = [clean(str(x)) for x in as_list(scope)]
    if not items:
        return "—"
    national = {iso3.upper(), cname(iso3).upper(), "NATIONAL"}
    if len(items) == 1 and items[0].upper() in national:
        return "National"
    return "; ".join(items)


def cname(iso3: str) -> str:
    return COUNTRY.get(iso3, (iso3 or "—",))[0]


def aoi_for_country(scope: list, iso3: str) -> str:
    for s in scope:
        s = str(s)
        if s.upper().startswith(iso3.upper() + ":"):
            return clean(s.split(":", 1)[1])
    return "—"


def acts_for_country(acts: list, iso3: str) -> list:
    name = cname(iso3)
    keep = []
    for a in acts:
        blob = f"{a.get('note', '')} {a.get('window', '')}"
        if iso3 in blob or (name and name in blob):
            keep.append(a)
    return keep


def acts_dates(acts: list) -> list[str]:
    return [str(a.get("date"))[:7] for a in acts if isinstance(a, dict) and a.get("date")]


def acts_objs(acts: list) -> list[dict]:
    """For the map popover: each activation as {d, url, full} so dates can be
    rendered as clickable links (url null when there were no public comms)."""
    out = []
    for a in acts:
        if not (isinstance(a, dict) and a.get("date")):
            continue
        url = a.get("url")
        out.append({
            "d": str(a.get("date"))[:7],
            "url": url if (url and str(url).startswith("http")) else None,
            "full": a.get("full_activation", True) is not False,
        })
    return out


def acts_cell(acts: list) -> str:
    if not acts:
        return "—"
    parts = []
    for a in acts:
        if not (isinstance(a, dict) and a.get("date")):
            continue
        d = str(a.get("date"))[:7]
        url = a.get("url")
        if url and str(url).startswith("http"):
            parts.append(f'<a href="{html.escape(str(url))}" target="_blank" rel="noopener" title="trigger announcement">{d}↗</a>')
        else:
            parts.append(d)
    dot = f'<span style="display:inline-block;width:7px;height:7px;border-radius:50%;background:{ACT_COLOR};margin-right:4px;vertical-align:middle"></span>'
    return ('<span class="act">' + dot + ", ".join(parts) + "</span>") if parts else "—"


def trigger_html(windows: list[dict]) -> str:
    if not windows:
        return '<span class="muted">see framework doc</span>'
    out = []
    for w in windows:
        body = truncate(": ".join(p for p in (w["indicator"], w["threshold"]) if p))
        out.append(f'<div class="win"><span class="wlabel">{html.escape(w["window"])}</span> {html.escape(body)}</div>')
    return "".join(out)


def doc_link(fm: dict) -> str:
    url = fm.get("framework_doc")
    if not url or not str(url).startswith("http"):
        return '<span class="muted">not public</span>'
    return f'<a href="{html.escape(str(url))}" target="_blank" rel="noopener">{html.escape(str(fm.get("framework_doc_date") or "doc"))} ↗</a>'


def repo_cell(fm: dict) -> str:
    m = re.search(r"ocha-dap/[A-Za-z0-9._-]+", str(fm.get("source_repo", "")), re.I)
    if not m:
        return "—"
    slug = m.group(0)
    if slug.lower() in PRIVATE_REPOS:
        return '<span class="muted">🔒 private</span>'
    short = slug.split("/", 1)[1]
    return f'<a href="https://github.com/{slug}" target="_blank" rel="noopener">{html.escape(short)} ↗</a>'


# Public-facing labels for the computed lifecycle statuses. The stored/data term
# stays `endorsed` (it means "has an endorsed framework doc"); the map just reads
# "Active" as the friendlier public label. Others fall back to the status text.
STATUS_LABEL = {"endorsed": "Active"}


def status_label(status: str) -> str:
    return STATUS_LABEL.get(status, status.replace("-", " "))


def badge(status: str) -> str:
    s = html.escape(status)
    return f'<span class="badge b-{s}">{html.escape(status_label(status))}</span>'


def entries(fm: dict) -> list[dict]:
    """One render-entry per row: split multi-country frameworks per country."""
    countries = [str(c) for c in as_list(fm.get("country_iso3"))]
    scope = as_list(fm.get("geographic_scope"))
    acts = [a for a in as_list(fm.get("activations")) if isinstance(a, dict)]
    if len(countries) > 1:
        split = COUNTRY_FUNDING_SPLIT.get(fm.get("framework"), {})
        return [{
            "iso3": iso3, "aoi": aoi_for_country(scope, iso3),
            "funding": split.get(iso3), "target": None,
            "acts": acts_for_country(acts, iso3),
        } for iso3 in sorted(countries)]
    iso3 = countries[0] if countries else ""
    return [{
        "iso3": iso3, "aoi": display_aoi(scope, iso3),
        "funding": fm.get("prearranged_funding_usd"), "target": fm.get("target_people"),
        "acts": acts,
    }]


def row_html(fm: dict, windows: list[dict], ent: dict, *, full: bool) -> str:
    fwk = str(fm.get("framework") or "")
    country = (f'<a href="frameworks/{html.escape(fwk)}.html" target="_top" title="framework page">'
               f'{html.escape(cname(ent["iso3"]))}</a>' if fwk else html.escape(cname(ent["iso3"])))
    cells = [
        f'<td class="ctry">{country}</td>',
        f'<td>{html.escape(str(fm.get("hazard", "—")))}</td>',
        f'<td class="mon" data-months="{",".join(str(int(x)) for x in as_list((fm.get("monitoring_period") or {}).get("months")) if isinstance(x, (int, float)))}" title="{html.escape(str((fm.get("monitoring_period") or {}).get("note") or ""))}">{html.escape(fmt_months((fm.get("monitoring_period") or {}).get("months")))}</td>',
        f'<td class="aoi">{html.escape(ent["aoi"])}</td>',
        f'<td>{badge(display_status(str(fm.get("status", "")), ent["acts"], fm.get("version"), fm.get("valid_until")))}</td>',
    ]
    if full:
        cells.append(f'<td>{html.escape(str(fm.get("version", "—")))}</td>')
    cells += [
        f'<td class="actcol">{acts_cell(ent["acts"])}</td>',
        f'<td class="trig">{trigger_html(windows)}</td>',
        f'<td class="num">{fmt_funding(ent["funding"])}</td>',
        f'<td class="num">{fmt_people(ent["target"])}</td>',
        f'<td>{doc_link(fm)}</td>',
        f'<td class="repo">{repo_cell(fm)}</td>',
    ]
    if full:
        sup = fm.get("supersedes")
        cells.append(f'<td>{html.escape(str(sup)) if sup else "—"}</td>')
    return "<tr>" + "".join(cells) + "</tr>"


def table(rows: list[str], *, full: bool, tid: str) -> str:
    head = ["Country", "Hazard", "Monitoring", "AOI", "Status"]
    if full:
        head.append("Version")
    head += ["Activations", "Trigger (per window)", "Pre-arranged", "Target people",
             'Framework doc<br><span class="thsub">(endorsed date)</span>', "Repo"]
    if full:
        head.append("Supersedes")
    ths = "".join(f'<th title="click to sort"><span class="thlab">{h}</span><span class="tharrow"></span></th>'
                  for h in head)
    return (f'<div class="tw"><table id="{tid}" class="ftable"><thead><tr>{ths}</tr></thead>'
            f'<tbody>{"".join(rows)}</tbody></table></div>')


def load_pages() -> list:
    """Every framework version page as (path, frontmatter, windows)."""
    pages = []
    for p in sorted(FW.rglob("*.md")):
        if p.name in ("_TEMPLATE.md", "README.md"):
            continue
        fm = frontmatter(p)
        if not fm or fm.get("content_type") != "framework":
            continue
        pages.append((p, fm, parse_windows(p)))
    return pages


DEV_STATUSES = {"development", "pre-development"}


def current_versions(pages: list) -> list:
    """One record per framework: the current operational version, carrying the framework's FULL
    activation history (union across versions). Shared by the map and the per-framework pages
    (gen_framework_pages.py) so both agree on what 'current' means."""
    by_fwk: dict[str, list] = {}
    for rec in pages:
        by_fwk.setdefault(rec[1].get("framework", rec[0].parent.name), []).append(rec)

    # current version per framework. The "current" operational version is the
    # latest ENDORSED-lineage version — NOT a newer-dated in-development successor
    # (those are future work and must not hide the endorsed version's status /
    # activations on the map and the active table). Fall back to in-development
    # only for frameworks that have no endorsed version yet.
    current = []
    for versions in by_fwk.values():
        # Activations belong to the COUNTRY-HAZARD framework, not a single version. Aggregate the
        # union across ALL versions (incl. superseded ones, which hold the historical activations),
        # deduped, and carry it onto whichever version is current. Otherwise an activation recorded
        # on a now-superseded version vanishes from the map (e.g. Niger drought 2022, Haiti 2025,
        # once the fired version was superseded by an in-development successor).
        agg, seen = [], set()
        for v in versions:
            for a in (v[1].get("activations") or []):
                k = ((str(a.get("date", "")).strip(), str(a.get("window", "")).strip(),
                      str(a.get("note", "")).strip()) if isinstance(a, dict) else (str(a),))
                if k not in seen:
                    seen.add(k); agg.append(a)

        non_super = [v for v in versions if v[1].get("status") != "superseded"]
        operational = [v for v in non_super if v[1].get("status") not in DEV_STATUSES]
        pool = operational or non_super or versions
        chosen = max(pool, key=lambda v: str(v[1].get("version", "")))
        # attach the framework's full activation history to the current pin (shallow-copy so we
        # don't mutate the source record); status is still computed per-version via own_activation_ym
        # (an old activation under a prior version won't flip the current version's status).
        cf = dict(chosen[1]); cf["activations"] = agg
        chosen = (chosen[0], cf, chosen[2])
        # If the current version is no longer live — it has FIRED (spent its envelope), EXPIRED,
        # or been RETIRED — and a NEWER in-development version exists, the framework is being
        # rebuilt for the next cycle → represent it by that development version, still carrying the
        # full activation history. (A genuinely-retired framework with no successor, e.g. Yemen,
        # has no newer_dev so it correctly stays retired.)
        if display_status(cf.get("status", ""), agg, cf.get("version"), cf.get("valid_until")) in ("recently-triggered", "expired", "retired"):
            newer_dev = [v for v in non_super if v[1].get("status") in DEV_STATUSES
                         and str(v[1].get("version", "")) > str(cf.get("version", ""))]
            if newer_dev:
                dev = max(newer_dev, key=lambda v: str(v[1].get("version", "")))
                dev_fm = dict(dev[1]); dev_fm["activations"] = agg
                chosen = (dev[0], dev_fm, dev[2])
        current.append(chosen)
    return current


def main() -> None:
    pages = load_pages()
    current = current_versions(pages)

    # ---- map markers: one per COUNTRY, holding an item per framework there ----
    mc: dict[str, dict] = {}
    for _, fm, windows in current:
        for ent in entries(fm):
            iso3 = ent["iso3"]
            if iso3 not in COUNTRY:
                # LOUD, not silent: a framework country with no centroid vanishes from the map
                # (real miss: Nicaragua, 2026-07-06). ::warning:: shows in the site.yml CI log.
                print(f"::warning::{fm.get('framework', '?')}: no COUNTRY centroid for '{iso3}' — "
                      f"add it to COUNTRY (and DIRECTIONS) in gen_public_site.py or it won't be on the map")
                continue
            name, lat, lon = COUNTRY[iso3]
            node = mc.setdefault(iso3, {"iso3": iso3, "country": name, "lat": lat, "lon": lon,
                                        "dir": DIRECTIONS.get(iso3, (1, -0.4)), "items": []})
            disp = display_status(fm.get("status", ""), ent["acts"], fm.get("version"), fm.get("valid_until"))
            months = [int(x) for x in as_list((fm.get("monitoring_period") or {}).get("months")) if isinstance(x, (int, float))]
            # ring = "able to trigger" (capacity): present when the version can still fire, bright
            # when it's also in its monitoring window this month, pale when able but off-season.
            in_window = CURRENT_MONTH in months
            able = able_to_trigger(fm, disp)
            ring = "now" if (able and in_window) else "able" if able else ""
            node["items"].append({
                "fwk": fm.get("framework", ""), "hazard": fm.get("hazard", ""),
                "hazard_label": pretty_hazard(fm.get("hazard", "")),
                "bucket": status_bucket(disp),
                "status": status_label(disp),
                "activated": bool(ent["acts"]),
                "acts": acts_objs(ent["acts"]),
                "ring": ring, "able": able,
                "doc": fm.get("framework_doc") if str(fm.get("framework_doc") or "").startswith("http") else None,
            })
    for node in mc.values():
        node["items"].sort(key=lambda it: it["hazard"])
    markers = sorted(mc.values(), key=lambda n: n["country"])

    # ---- tables ----
    def disp(fm: dict) -> str:
        acts = [a for a in as_list(fm.get("activations")) if isinstance(a, dict)]
        return display_status(fm.get("status", ""), acts, fm.get("version"), fm.get("valid_until"))

    active = sorted((rec for rec in current if disp(rec[1]) in ACTIVE_STATUSES),
                    key=lambda r: (r[1].get("hazard", ""), r[1].get("framework", "")))
    active_rows = [row_html(fm, w, e, full=False) for _, fm, w in active for e in entries(fm)]

    all_sorted = sorted(pages, key=lambda r: (r[1].get("framework", ""),
                        STATUS_RANK.get(disp(r[1]), 9), str(r[1].get("version", ""))))
    full_rows = [row_html(fm, w, e, full=True) for _, fm, w in all_sorted for e in entries(fm)]

    items = [it for m in markers for it in m["items"]]
    n_end = sum(1 for it in items if it["bucket"] == "endorsed")
    n_recent = sum(1 for it in items if it["bucket"] == "recently-triggered")
    n_expired = sum(1 for it in items if it["bucket"] == "expired")
    n_dev = sum(1 for it in items if it["bucket"] == "development")
    n_ret = sum(1 for it in items if it["bucket"] == "retired")
    n_activated = sum(1 for it in items if it["activated"])
    n_able_now = sum(1 for it in items if it["ring"] == "now")
    n_able_off = sum(1 for it in items if it["ring"] == "able")
    markers_json = json.dumps(markers).replace("<", "\\u003c")
    map_color_json = json.dumps(MAP_COLOR)
    hazard_svg_json = json.dumps(HAZARD_SVG).replace("<", "\\u003c")
    fw_iso_json = json.dumps({iso3: 1 for iso3 in mc})
    today = datetime.date.today().isoformat()

    doc = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>OCHA Anticipatory Action Frameworks</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
<style>
  :root {{ --ocha:#1a6bb5; --ink:#222; --muted:#777; --line:#e3e6ea; }}
  * {{ box-sizing:border-box; }}
  body {{ font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
         color:var(--ink); margin:0; background:#fafbfc; line-height:1.4; }}
  header {{ background:var(--ocha); color:#fff; padding:28px 24px; }}
  header h1 {{ margin:0 0 6px; font-size:24px; }}
  header p {{ margin:0; opacity:.9; font-size:14px; }}
  main {{ max-width:1560px; margin:0 auto; padding:24px; }}
  h2 {{ font-size:19px; border-bottom:2px solid var(--ocha); padding-bottom:6px; margin:32px 0 4px; }}
  .sub {{ color:var(--muted); font-size:13px; margin:0 0 12px; }}
  #mapwrap {{ position:relative; width:1360px; max-width:100%; margin:4px auto 0; }}
  #map {{ position:absolute; top:0; left:0; width:1360px; height:521px; transform-origin:top left;
         border-radius:8px; box-shadow:0 1px 3px rgba(0,0,0,.08); z-index:0; background:#ffffff; cursor:default; }}
  .leaflet-container {{ cursor:default !important; }}
  .leaflet-container {{ background:#ffffff; }}
  .maplegend {{ font-size:13px; line-height:1.5; background:#fff; padding:7px 9px; border-radius:6px; box-shadow:0 1px 4px rgba(0,0,0,.2); }}
  .dot {{ display:inline-block; width:12px; height:12px; border-radius:50%; margin-right:5px; vertical-align:-1px; }}
  .infopop {{ position:absolute; z-index:720; max-width:300px; background:#fff; border:1px solid #d4d8de;
         border-radius:8px; box-shadow:0 4px 16px rgba(0,0,0,.22); padding:10px 26px 10px 12px;
         font-size:12px; line-height:1.45; color:#222; pointer-events:auto; }}
  .infopop b {{ font-size:13px; }}
  .infopop a {{ color:var(--ocha); }}
  .infox {{ position:absolute; top:3px; right:7px; border:none; background:none; font-size:17px;
         line-height:1; cursor:pointer; color:#9aa3ad; }}
  .infox:hover {{ color:#555; }}
  .labelpane {{ position:absolute; inset:0; pointer-events:none; z-index:620; }}
  .leadersvg {{ position:absolute; inset:0; width:100%; height:100%; overflow:visible; }}
  .leader {{ stroke:#8a99a8; stroke-width:1; }}
  .callout {{ position:absolute; display:flex; flex-direction:column; align-items:flex-start; }}
  .cname {{ font-weight:700; font-size:11px; color:#16324f; white-space:nowrap; line-height:1.15; margin-bottom:1px;
         text-shadow:0 0 2px #fff,0 0 2px #fff,0 0 3px #fff,0 0 3px #fff; }}
  .hrow {{ display:flex; align-items:center; gap:4px; margin-top:2px; }}
  .hlab {{ font-size:10px; font-weight:400; color:#1c3550; white-space:nowrap;
         text-shadow:0 0 2px #fff,0 0 2px #fff,0 0 3px #fff,0 0 3px #fff; }}
  .iconbox {{ position:relative; width:19px; height:19px; border-radius:5px; flex:0 0 auto;
         display:flex; align-items:center; justify-content:center; border:1.5px solid #fff;
         box-shadow:0 1px 3px rgba(0,0,0,.4); }}
  .iconbox + .iconbox {{ margin-left:-3px; }}
  /* ring = "able to trigger": solid green = able now (in its monitoring season this month);
     pale green = able but off-season. No ring = cannot trigger (activated & exhausted / expired /
     in development). Legacy comment below kept for context.
     green ring = a live framework whose monitoring window includes this month;
     pale green = same, but the framework is still in development */
  /* able to trigger = orange ring; in-season (able-now) pulses, off-season (able-off) is a static pale orange. */
  @keyframes ablepulse {{
    0%   {{ box-shadow: 0 0 0 2px #f5a300, 0 0 0 0 rgba(245,163,0,.85), 0 1px 3px rgba(0,0,0,.4); }}
    65%  {{ box-shadow: 0 0 0 2px #f5a300, 0 0 0 11px rgba(245,163,0,0), 0 1px 3px rgba(0,0,0,.4); }}
    100% {{ box-shadow: 0 0 0 2px #f5a300, 0 0 0 11px rgba(245,163,0,0), 0 1px 3px rgba(0,0,0,.4); }}
  }}
  /* keep the icon's fine white border between the fill and the ring (don't tint it) so the
     red/blue pin reads clearly apart from the orange ring */
  .iconbox.able-now {{ border-color:#fff; box-shadow:0 0 0 2px #f5a300, 0 1px 3px rgba(0,0,0,.4); animation:ablepulse 1.1s ease-out infinite; }}
  .iconbox.able-off {{ border-color:#fff; box-shadow:0 0 0 2px #f6c95f, 0 1px 3px rgba(0,0,0,.4); }}
  @media (prefers-reduced-motion: reduce) {{ .iconbox.able-now {{ animation:none; }} }}
  .iconbox .hz {{ width:13px; height:13px; display:block; }}
  .actdots {{ position:absolute; top:-3px; right:-3px; display:flex; flex-direction:row-reverse; gap:1px; }}
  .actdot {{ width:6px; height:6px; border-radius:50%; background:{ACT_COLOR};
         border:1px solid #fff; box-shadow:0 0 1px rgba(0,0,0,.5); }}
  /* callout text styles now live in .cname / .hlab (vertical layout) */
  .leaflet-tooltip.maplabel {{ background:transparent; border:none; box-shadow:none; padding:0;
         color:#16324f; font-size:10.5px; font-weight:600; white-space:nowrap; line-height:1.15;
         text-shadow:0 0 2px #fff,0 0 2px #fff,0 0 3px #fff,0 0 3px #fff; }}
  .leaflet-tooltip.maplabel::before {{ display:none; }}
  input#q {{ width:100%; max-width:420px; padding:9px 12px; border:1px solid var(--line); border-radius:6px; font-size:14px; margin:8px 0 16px; }}
  .tw {{ overflow-x:auto; border-radius:8px; box-shadow:0 1px 3px rgba(0,0,0,.06); }}
  table {{ border-collapse:collapse; width:100%; background:#fff; font-size:12px; }}
  /* Cells size to content by default (no squished slivers); only the two long
     text columns (Trigger, AOI) wrap. The .tw wrapper scrolls on overflow. */
  th, td {{ text-align:left; padding:6px 10px; border-bottom:1px solid var(--line); vertical-align:top; white-space:nowrap; }}
  th {{ background:#f1f4f7; font-weight:600; position:sticky; top:0; }}
  .thsub {{ font-weight:400; font-size:9.5px; color:var(--muted); }}
  td.ctry {{ font-weight:600; }}
  td.num {{ text-align:right; }}
  td.trig {{ white-space:normal; min-width:240px; max-width:360px; font-size:11.5px; }}
  td.aoi {{ white-space:normal; min-width:130px; max-width:200px; font-size:11.5px; color:#444; word-break:break-word; }}
  td.actcol {{ white-space:normal; min-width:96px; max-width:150px; }}
  td.mon {{ font-size:11.5px; color:#444; cursor:help; }}
  td.repo {{ font-size:11.5px; }}
  tr.frow td {{ position:static; background:#f8fafc; padding:4px 6px; }}
  tr.frow input, tr.frow select {{ width:100%; box-sizing:border-box; font-size:11px; padding:3px 4px; border:1px solid var(--line); border-radius:4px; background:#fff; }}
  details.mfilter {{ position:relative; }}
  details.mfilter > summary {{ list-style:none; cursor:pointer; padding:3px 6px; border:1px solid var(--line); border-radius:4px; background:#fff; font-size:11px; white-space:nowrap; }}
  details.mfilter > summary::-webkit-details-marker {{ display:none; }}
  details.mfilter[open] > summary {{ border-color:var(--ocha); color:var(--ocha); }}
  .mpanel {{ position:absolute; z-index:40; margin-top:3px; background:#fff; border:1px solid var(--line);
         border-radius:6px; padding:7px 9px; box-shadow:0 3px 10px rgba(0,0,0,.16); display:grid;
         grid-template-columns:repeat(2,auto); gap:3px 14px; }}
  .mpanel label {{ display:flex; align-items:center; gap:5px; font-size:11px; font-weight:400; white-space:nowrap; cursor:pointer; }}
  .mpanel input {{ width:auto; margin:0; padding:0; border:0; }}
  .act {{ color:#b3261e; font-weight:600; font-size:12px; }}
  .win {{ padding:2px 0; border-bottom:1px dotted #eee; }}
  .win:last-child {{ border-bottom:none; }}
  .wlabel {{ display:inline-block; font-weight:600; color:var(--ocha); margin-right:4px; }}
  .muted {{ color:var(--muted); font-style:italic; }}
  a {{ color:var(--ocha); }}
  .badge {{ display:inline-block; padding:2px 8px; border-radius:10px; font-size:11px; font-weight:600; white-space:nowrap; }}
  .b-triggered {{ background:#fde2e1; color:#b3261e; }}
  .b-recently-triggered {{ background:#fce4cd; color:#b5650a; }}
  .b-expired {{ background:#f1ead0; color:#7d6b1a; }}
  .b-endorsed {{ background:#e2f3e6; color:#1e7a37; }}
  .b-development {{ background:#fdf0d5; color:#9a6d0a; }}
  .b-pre-development {{ background:#e5eefb; color:#15c; }}
  .b-superseded {{ background:#f3f0e2; color:#8a6d1e; }}
  .b-retired {{ background:#e8e8e8; color:#666; }}
  details {{ margin-top:4px; }}
  summary {{ cursor:pointer; font-weight:600; color:var(--ocha); }}
  footer {{ color:var(--muted); font-size:12px; padding:24px; text-align:center; }}
  .disclaimer {{ background:#fff4d6; border-bottom:1px solid #e6cf8f; color:#6b5310;
         font-size:13px; line-height:1.4; padding:9px 18px; text-align:center; }}
  .disclaimer b {{ color:#5a4408; }}
</style>
</head>
<body>
<div class="disclaimer" role="note">⚠️ <b>Work in progress.</b> This site is in active development and is auto-generated from an internal knowledge base. Details may be incomplete, out of date, or inaccurate — treat figures and statuses as indicative, not authoritative.</div>
<header>
  <h1>OCHA Anticipatory Action Frameworks</h1>
  <p>Published triggers, windows, and pre-arranged financing across the Centre for Humanitarian Data's AA portfolio. Red markers flag frameworks that have activated.</p>
</header>
<main>
  <h2>Map</h2>
  <p class="sub">Current version of each framework. Pin colour = status; each red dot = one past activation. Shaded countries have at least one framework. Click a pin for detail (activation dates link to the announcement where one exists).</p>
  <div id="mapwrap"><div id="map"></div></div>


  <h2>Active frameworks</h2>
  <p class="sub">Current version of each operational framework; multi-country frameworks are split to one row per country. Click a column header to sort; type in the per-column boxes to filter.</p>
  {table(active_rows, full=False, tid="t-active")}

  <h2>All versions</h2>
  <p class="sub">Every ingested version, including superseded and retired.</p>
  <details open>
    <summary>Show full version history</summary>
    <div style="margin-top:12px">{table(full_rows, full=True, tid="t-full")}</div>
  </details>
</main>
<footer>
  Auto-generated from the DS team knowledge base on {today}. Trigger details summarized; the linked framework document is authoritative.
</footer>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script src="https://unpkg.com/polygon-clipping@0.15.7/dist/polygon-clipping.umd.js"></script>
<script>
  var MARKERS = {markers_json};
  var COLOR = {map_color_json};
  var FW_ISO = {fw_iso_json};
  var HAZ = {hazard_svg_json};
  var MONTHS_ABBR = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
  var map = L.map('map', {{scrollWheelZoom:false, doubleClickZoom:false, touchZoom:false,
    boxZoom:false, zoomControl:false, dragging:false, keyboard:false, attributionControl:false,
    trackResize:false, zoomSnap:0}});   // fractional zoom fills width; fixed render size, CSS-scaled
  // Render the map at a fixed 1200x460 and CSS-scale the whole thing to fit the
  // window — keeps the tuned layout + aspect ratio, no cutoff. (Static map.)
  var mapwrap = document.getElementById('mapwrap'), mapEl = document.getElementById('map');
  function scaleMap() {{
    var s = Math.min(1, mapwrap.clientWidth / 1360);
    mapEl.style.transform = s < 1 ? 'scale(' + s + ')' : 'none';
    mapwrap.style.height = Math.round(521 * s) + 'px';
  }}
  window.addEventListener('resize', scaleMap); scaleMap();
  map.createPane('boundaries'); map.getPane('boundaries').style.zIndex = 250;
  // White "sea"; framework countries shaded blue, others light grey.
  var FWBBOX = {{}};   // iso3 -> lng/lat bounding box of the framework country (for avoidance)
  // Natural Earth splits Somaliland out of Somalia as a separate id="-99" feature; fold it back
  // into SOM so the whole country shades as one (otherwise the north of Somalia is left unshaded).
  function fwIso(f) {{
    if (f.id === '-99' && f.properties && f.properties.name === 'Somaliland') return 'SOM';
    return f.id;
  }}
  fetch('https://cdn.jsdelivr.net/gh/johan/world.geo.json@master/countries.geo.json')
    .then(function(r) {{ return r.json(); }})
    .then(function(geo) {{
      // Dissolve Somaliland (a separate Natural Earth feature, id "-99") into Somalia so the
      // country renders as ONE shape with no internal border line. Falls back to the fwIso fold
      // (shaded, but with the line) if polygon-clipping didn't load.
      try {{
        var _som = null, _sl = null;
        geo.features.forEach(function(f) {{
          if (f.id === 'SOM') _som = f;
          else if (f.id === '-99' && f.properties && f.properties.name === 'Somaliland') _sl = f;
        }});
        if (_som && _sl && window.polygonClipping) {{
          var _u = polygonClipping.union(_som.geometry.coordinates, _sl.geometry.coordinates);
          _som.geometry = {{type: 'MultiPolygon', coordinates: _u}};
          geo.features = geo.features.filter(function(f) {{ return f !== _sl; }});
        }}
      }} catch (e) {{}}
      L.geoJSON(geo, {{ pane: 'boundaries', interactive: false,
        style: function(f) {{
          return FW_ISO[fwIso(f)]
            ? {{color: '#9cc0e3', weight: 0.8, fillColor: '#cfe0f2', fillOpacity: 1}}
            : {{color: '#d3d7dc', weight: 0.5, fillColor: '#ebedf0', fillOpacity: 1}};
        }}
      }}).addTo(map);
      geo.features.forEach(function(f) {{
        if (!FW_ISO[fwIso(f)] || !f.geometry) return;
        var polys = f.geometry.type === 'Polygon' ? [f.geometry.coordinates] : f.geometry.coordinates;
        var b = {{minx: 1e9, miny: 1e9, maxx: -1e9, maxy: -1e9}};
        polys.forEach(function(poly) {{ poly[0].forEach(function(p) {{
          if (p[0] < b.minx) b.minx = p[0]; if (p[0] > b.maxx) b.maxx = p[0];
          if (p[1] < b.miny) b.miny = p[1]; if (p[1] > b.maxy) b.maxy = p[1];
        }}); }});
        // ignore degenerate boxes from antimeridian-crossing geometry (e.g. Fiji),
        // which would otherwise span the whole map and shove the callout off-screen.
        if (b.maxx - b.minx <= 170 && b.maxy - b.miny <= 130) {{
          var _k = fwIso(f), _pb = FWBBOX[_k];   // union across folded features (SOM + Somaliland)
          FWBBOX[_k] = _pb ? {{minx: Math.min(_pb.minx, b.minx), miny: Math.min(_pb.miny, b.miny),
                               maxx: Math.max(_pb.maxx, b.maxx), maxy: Math.max(_pb.maxy, b.maxy)}} : b;
        }}
      }});
      runLayout();
    }}).catch(function() {{}});
  function uniq(a) {{ var s = {{}}, o = []; a.forEach(function(x) {{ if (!s[x]) {{ s[x] = 1; o.push(x); }} }}); return o; }}
  // Each country = a callout (rounded-square hazard icon(s) + label text) placed in
  // open space, with a leader line to a small dot on the country.
  function calloutHTML(m) {{
    // fixed layout: country name on top, then one row per hazard — icon on the
    // left, label on the right (icons stacked vertically, left-aligned).
    var rows = m.items.map(function(it) {{
      var svg = '<svg viewBox="0 0 24 24" class="hz">' + (HAZ[it.hazard] || HAZ.other) + '</svg>';
      var nd = it.acts.length || (it.activated ? 1 : 0), dots = '';
      if (nd) {{ var s = ''; for (var i = 0; i < Math.min(nd, 6); i++) s += '<span class="actdot"></span>'; dots = '<span class="actdots">' + s + '</span>'; }}
      var ring = it.ring === 'now' ? ' able-now' : (it.ring === 'able' ? ' able-off' : '');
      return '<span class="hrow"><span class="iconbox' + ring + '" style="background:' + COLOR[it.bucket] + '">' + svg + dots + '</span>'
        + '<span class="hlab">' + it.hazard_label + '</span></span>';
    }}).join('');
    return '<span class="cname">' + m.country + '</span>' + rows;
  }}
  var NS = 'http://www.w3.org/2000/svg';
  var dots = L.layerGroup().addTo(map);
  var lpane = L.DomUtil.create('div', 'labelpane', map.getContainer());
  var lsvg = document.createElementNS(NS, 'svg'); lsvg.setAttribute('class', 'leadersvg'); lpane.appendChild(lsvg);
  // custom info popup — always on top (z 720), opened by either the callout or the dot
  var info = L.DomUtil.create('div', 'infopop', map.getContainer()); info.style.display = 'none';
  L.DomEvent.disableClickPropagation(info);
  map.on('click', function() {{ info.style.display = 'none'; }});
  function actsHTML(acts) {{
    return acts.map(function(a) {{
      var lbl = a.d + (a.full ? '' : ' (window)');
      return a.url
        ? '<a href="' + a.url + '" target="_blank" rel="noopener" style="color:{ACT_COLOR};text-decoration:underline">' + lbl + '↗</a>'
        : '<span style="color:{ACT_COLOR}">' + lbl + '</span>';
    }}).join(', ');
  }}
  function infoHTML(m, it) {{
    return '<button class="infox" aria-label="close">&times;</button>'
      + '<b>' + m.country + '</b> &mdash; ' + it.hazard_label + '<br>' + it.status
      + (it.able ? ' <span style="color:#c8860a">&bull; able to trigger</span>'
                 : (it.activated ? ' <span style="color:#999">&bull; not able to trigger now (spent)</span>' : ''))
      + (it.acts.length ? ' <span style="color:{ACT_COLOR}">&bull; triggered</span> ' + actsHTML(it.acts) : (it.activated ? ' <span style="color:{ACT_COLOR}">&bull; activated</span>' : ''))
      + (it.doc ? '<br><a href="' + it.doc + '" target="_blank" rel="noopener">framework doc ↗</a>' : '')
      + (it.fwk ? (it.doc ? ' &middot; ' : '<br>') + '<a href="frameworks/' + it.fwk + '.html" target="_top">framework page →</a>' : '');
  }}
  function showInfo(m, it, pt) {{
    info.innerHTML = infoHTML(m, it);
    info.style.display = 'block';
    var sz = map.getSize(), w = info.offsetWidth, h = info.offsetHeight;
    var x = pt.x + 12, y = pt.y + 10;
    if (x + w > sz.x - 4) x = pt.x - w - 12;
    if (y + h > sz.y - 4) y = sz.y - h - 4;
    info.style.left = Math.max(4, x) + 'px'; info.style.top = Math.max(4, y) + 'px';
    info.querySelector('.infox').onclick = function() {{ info.style.display = 'none'; }};
  }}
  var bounds = [];
  var labels = MARKERS.map(function(m) {{
    var dot = L.circleMarker([m.lat, m.lon], {{radius: 3.5, color: '#fff', weight: 1.5, fillColor: '#39506b', fillOpacity: 1}}).addTo(dots);
    var el = document.createElement('div'); el.className = 'callout'; el.innerHTML = calloutHTML(m);
    el.style.pointerEvents = 'auto'; el.style.visibility = 'hidden';
    lpane.appendChild(el);
    L.DomEvent.disableClickPropagation(el);
    // per-hazard popover: only the ICON opens it
    var iconEls = el.querySelectorAll('.iconbox');
    m.items.forEach(function(it, i) {{
      var ib = iconEls[i]; if (!ib) return;
      ib.style.cursor = 'pointer';
      ib.onclick = function(e) {{
        e.stopPropagation();
        var r = ib.getBoundingClientRect(), mr = map.getContainer().getBoundingClientRect();
        showInfo(m, it, {{x: r.left - mr.left + r.width / 2, y: r.top - mr.top + r.height / 2}});
      }};
    }});
    var ln = document.createElementNS(NS, 'line'); ln.setAttribute('class', 'leader'); lsvg.appendChild(ln);
    bounds.push([m.lat, m.lon]);
    return {{lat: m.lat, lon: m.lon, dir: m.dir, iso3: m.iso3, el: el, ln: ln}};
  }});
  if (bounds.length) map.fitBounds(bounds, {{paddingTopLeft: [88, 5], paddingBottomRight: [9, 68], maxZoom: 7}});
  else map.setView([12, 30], 2);
  var LOCKZ = map.getZoom(); map.setMinZoom(LOCKZ); map.setMaxZoom(LOCKZ);   // lock zoom

  // LAYOUT: each callout sits OUTSIDE its own country's box (so icons/labels never
  // cover the country), clear of the other callouts. cx,cy = box CENTRE (px).
  var PAD = 8;     // gap between callout boxes
  var GAP = 4;     // gap between a callout and a framework-country box
  var ALLRECTS = [];   // screen rects of EVERY framework country (avoid them all)
  function ownRect(L) {{   // own country bbox -> screen rect (px), or null
    var b = FWBBOX[L.iso3]; if (!b) return null;
    var p1 = map.latLngToContainerPoint([b.maxy, b.minx]), p2 = map.latLngToContainerPoint([b.miny, b.maxx]);
    return {{x1: Math.min(p1.x, p2.x), y1: Math.min(p1.y, p2.y), x2: Math.max(p1.x, p2.x), y2: Math.max(p1.y, p2.y)}};
  }}
  function clampAll(W, H) {{
    labels.forEach(function(L) {{
      if (L.cx - L.w / 2 < 3) L.cx = 3 + L.w / 2; if (L.cx + L.w / 2 > W - 3) L.cx = W - 3 - L.w / 2;
      if (L.cy - L.h / 2 < 3) L.cy = 3 + L.h / 2; if (L.cy + L.h / 2 > H - 3) L.cy = H - 3 - L.h / 2;
    }});
  }}
  // push a callout out of the framework-country box it overlaps MOST (along the
  // shortest axis, biased to its preferred direction), so icons/labels never sit
  // on ANY AA country — its own or a neighbour's.
  function ejectCountries(L) {{
    var bx1 = L.cx - L.w / 2 - GAP, by1 = L.cy - L.h / 2 - GAP, bx2 = L.cx + L.w / 2 + GAP, by2 = L.cy + L.h / 2 + GAP;
    var best = null, bestA = 0;
    for (var i = 0; i < ALLRECTS.length; i++) {{
      var r = ALLRECTS[i];
      var ox = Math.min(bx2, r.x2) - Math.max(bx1, r.x1), oy = Math.min(by2, r.y2) - Math.max(by1, r.y1);
      if (ox > 0 && oy > 0) {{ var a = Math.min(ox, oy); if (a > bestA) {{ bestA = a; best = r; }} }}
    }}
    if (!best) return false;
    var pushL = best.x1 - bx2, pushR = best.x2 - bx1, pushU = best.y1 - by2, pushD = best.y2 - by1;
    var cands = [[Math.abs(pushL), pushL, 0], [Math.abs(pushR), pushR, 0], [Math.abs(pushU), 0, pushU], [Math.abs(pushD), 0, pushD]];
    cands.sort(function(a, b) {{ return a[0] - b[0]; }});
    var dirBias = cands.filter(function(c) {{ return (c[1] * L.dir[0] + c[2] * L.dir[1]) >= 0; }});
    var pick = (dirBias[0] && dirBias[0][0] <= cands[0][0] * 1.6) ? dirBias[0] : cands[0];
    L.cx += pick[1]; L.cy += pick[2];
    return true;
  }}
  // HARD pass: no callout overlaps another callout OR its own country box.
  function separate(iters, W, H) {{
    for (var s = 0; s < iters; s++) {{
      var clean = true;
      for (var i = 0; i < labels.length; i++) for (var j = i + 1; j < labels.length; j++) {{
        var a = labels[i], b = labels[j];
        var ax = a.cx - a.w / 2, ay = a.cy - a.h / 2, bx = b.cx - b.w / 2, by = b.cy - b.h / 2;
        if (ax < bx + b.w + PAD && ax + a.w + PAD > bx && ay < by + b.h + PAD && ay + a.h + PAD > by) {{
          clean = false;
          var ox = Math.min(ax + a.w, bx + b.w) - Math.max(ax, bx) + PAD;
          var oy = Math.min(ay + a.h, by + b.h) - Math.max(ay, by) + PAD;
          if (ox <= oy) {{ var hx = ox / 2 + 0.5; if (a.cx < b.cx) {{ a.cx -= hx; b.cx += hx; }} else {{ a.cx += hx; b.cx -= hx; }} }}
          else {{ var hy = oy / 2 + 0.5; if (a.cy < b.cy) {{ a.cy -= hy; b.cy += hy; }} else {{ a.cy += hy; b.cy -= hy; }} }}
        }}
      }}
      labels.forEach(function(L) {{ if (ejectCountries(L)) clean = false; }});
      clampAll(W, H);
      if (clean) return true;
    }}
    return false;
  }}
  function runLayout() {{
    var sz = map.getSize(), W = sz.x, H = sz.y;
    ALLRECTS = [];
    for (var iso in FWBBOX) {{
      var bb = FWBBOX[iso], q1 = map.latLngToContainerPoint([bb.maxy, bb.minx]), q2 = map.latLngToContainerPoint([bb.miny, bb.maxx]);
      ALLRECTS.push({{x1: Math.min(q1.x, q2.x), y1: Math.min(q1.y, q2.y), x2: Math.max(q1.x, q2.x), y2: Math.max(q1.y, q2.y)}});
    }}
    if (legendEl) {{   // keep callouts off the legend
      var lr = legendEl.getBoundingClientRect(), mr = map.getContainer().getBoundingClientRect();
      if (lr.width) ALLRECTS.push({{x1: lr.left - mr.left - 6, y1: lr.top - mr.top - 6, x2: lr.right - mr.left + 6, y2: lr.bottom - mr.top + 6}});
    }}
    labels.forEach(function(L) {{
      var p = map.latLngToContainerPoint([L.lat, L.lon]); L.px = p.x; L.py = p.y;
      L.w = L.el.offsetWidth; L.h = L.el.offsetHeight;
      var ib = L.el.querySelector('.iconbox');                 // anchor the leader at the icon
      L.iox = ib ? ib.offsetLeft + ib.offsetWidth / 2 : 12;
      L.ioy = ib ? ib.offsetTop + ib.offsetHeight / 2 : L.h / 2;
      L.rect = ownRect(L);
      // seed: just outside the own-country box in the preferred direction
      var dl = Math.sqrt(L.dir[0] * L.dir[0] + L.dir[1] * L.dir[1]) || 1, ux = L.dir[0] / dl, uy = L.dir[1] / dl;
      var r = L.rect, cx0 = r ? (r.x1 + r.x2) / 2 : L.px, cy0 = r ? (r.y1 + r.y2) / 2 : L.py;
      var hx = r ? (r.x2 - r.x1) / 2 : 0, hy = r ? (r.y2 - r.y1) / 2 : 0;
      var reach = Math.abs(ux) * hx + Math.abs(uy) * hy + GAP + Math.abs(ux) * L.w / 2 + Math.abs(uy) * L.h / 2 + 2;
      L.cx = cx0 + ux * reach; L.cy = cy0 + uy * reach;
    }});
    for (var step = 0; step < 55; step++) {{
      labels.forEach(function(L) {{
        L.cx += (L.px - L.cx) * 0.06; L.cy += (L.py - L.cy) * 0.06;   // gentle pull toward the country
        ejectCountries(L);                                           // …but stay off every AA country box
      }});
      separate(10, W, H);
    }}
    separate(700, W, H);   // FINAL: no callout overlaps another callout or any AA country
    labels.forEach(function(L) {{ L.ll = map.containerPointToLatLng([L.cx, L.cy]); }});
    render();
  }}
  function render() {{
    labels.forEach(function(L) {{
      if (!L.ll) {{ L.el.style.visibility = 'hidden'; return; }}
      var c = map.latLngToContainerPoint(L.ll), p = map.latLngToContainerPoint([L.lat, L.lon]);
      L.cx = c.x; L.cy = c.y; L.px = p.x; L.py = p.y;
      L.el.style.visibility = 'visible'; L.el.style.left = (L.cx - L.w / 2) + 'px'; L.el.style.top = (L.cy - L.h / 2) + 'px';
      // leader originates at the icon (offset measured in runLayout)
      L.ln.setAttribute('x1', L.px); L.ln.setAttribute('y1', L.py);
      L.ln.setAttribute('x2', L.cx - L.w / 2 + (L.iox || 12)); L.ln.setAttribute('y2', L.cy - L.h / 2 + (L.ioy || L.h / 2));
    }});
  }}
  map.on('move zoom viewreset resize', render);
  map.on('zoomend', runLayout);
  setTimeout(function() {{ if (!labels[0] || !labels[0].ll) runLayout(); }}, 1500);  // fallback if geojson is slow

  var legendEl = null;
  var legend = L.control({{position:'bottomleft'}});
  legend.onAdd = function() {{
    var d = L.DomUtil.create('div', 'maplegend'); legendEl = d;
    d.innerHTML = '<b>Framework</b><br>' +
      '<span class="dot" style="background:' + COLOR.endorsed + '"></span>Active ({n_end})<br>' +
      '<span class="dot" style="background:' + COLOR['recently-triggered'] + '"></span>Recently triggered ({n_recent})<br>' +
      '<span class="dot" style="background:' + COLOR.expired + '"></span>Expired ({n_expired})<br>' +
      '<span class="dot" style="background:' + COLOR.development + '"></span>In development ({n_dev})<br>' +
      '<span class="dot" style="background:' + COLOR.retired + '"></span>Retired ({n_ret})<br>' +
      '<span class="dot" style="background:{ACT_COLOR};width:11px;height:11px;border:2px solid #fff"></span>Activated &mdash; a dot per activation ({n_activated})<br>' +
      '<span class="dot" style="background:#fff;width:12px;height:12px;border:2.5px solid #f5a300"></span>Able to trigger now &mdash; in season ({CURRENT_MONTH_LABEL}), pulsing ({n_able_now})<br>' +
      '<span class="dot" style="background:#fff;width:12px;height:12px;border:2.5px solid #f6c95f"></span>Able to trigger &mdash; off-season ({n_able_off})<br>' +
      '<span class="dot" style="background:#fff;width:12px;height:12px;border:2.5px solid #e3e6ea"></span>No ring = cannot trigger (activated &amp; spent, expired, or in development)';
    return d;
  }};
  legend.addTo(map);

  // ---- sortable + per-column filterable tables ----
  function numval(s) {{
    s = s.replace(/[,\\s]/g, '');
    var m = s.match(/-?\\d+\\.?\\d*/);
    if (!m) return null;
    var n = parseFloat(m[0]);
    if (/m/i.test(s)) n *= 1e6; else if (/k/i.test(s)) n *= 1e3;
    return n;
  }}
  function refilter() {{
    var qel = document.getElementById('q'), g = (qel ? qel.value : '').trim().toLowerCase();
    document.querySelectorAll('table.ftable').forEach(function(table) {{
      var fs = [];
      table.querySelectorAll('.colf').forEach(function(c) {{
        var v = (c.value || '').trim().toLowerCase();
        if (v) fs.push({{col: +c.dataset.col, v: v, eq: c.dataset.type === 'eq'}});
      }});
      var mfs = [];  // month multi-select filters (OR within: row's window must hit ≥1 selected month)
      table.querySelectorAll('details.mfilter').forEach(function(d) {{
        var sel = [];
        d.querySelectorAll('input.mbox:checked').forEach(function(b) {{ sel.push(b.value); }});
        if (sel.length) mfs.push({{col: +d.dataset.col, sel: sel}});
      }});
      Array.prototype.forEach.call(table.tBodies[0].rows, function(tr) {{
        var show = !g || tr.textContent.toLowerCase().indexOf(g) >= 0;
        if (show) {{
          for (var k = 0; k < fs.length; k++) {{
            var cell = tr.cells[fs[k].col].textContent.trim().toLowerCase();
            if (fs[k].eq ? cell !== fs[k].v : cell.indexOf(fs[k].v) < 0) {{ show = false; break; }}
          }}
        }}
        if (show) {{
          for (var j = 0; j < mfs.length; j++) {{
            var dm = (tr.cells[mfs[j].col].getAttribute('data-months') || '').split(',');
            if (!mfs[j].sel.some(function(s) {{ return dm.indexOf(s) >= 0; }})) {{ show = false; break; }}
          }}
        }}
        tr.style.display = show ? '' : 'none';
      }});
    }});
  }}
  function distinctCol(table, idx) {{
    var set = {{}};
    Array.prototype.forEach.call(table.tBodies[0].rows, function(tr) {{
      var t = tr.cells[idx].textContent.trim();
      if (t && t !== '—') set[t] = 1;
    }});
    return Object.keys(set).sort();
  }}
  function sortTable(table, col, th) {{
    var tb = table.tBodies[0], rows = Array.prototype.slice.call(tb.rows);
    var dir = (table.getAttribute('data-sc') == col && table.getAttribute('data-sd') == '1') ? -1 : 1;
    var allnum = rows.every(function(r) {{ var t = r.cells[col].textContent.trim(); return t === '' || t === '—' || numval(t) !== null; }});
    rows.sort(function(a, b) {{
      var x = a.cells[col].textContent.trim(), y = b.cells[col].textContent.trim();
      if (allnum) {{ var nx = numval(x), ny = numval(y); nx = nx === null ? -Infinity : nx; ny = ny === null ? -Infinity : ny; return (nx - ny) * dir; }}
      return x.localeCompare(y) * dir;
    }});
    rows.forEach(function(r) {{ tb.appendChild(r); }});
    table.setAttribute('data-sc', col); table.setAttribute('data-sd', dir == 1 ? '1' : '0');
    table.querySelectorAll('thead tr:first-child th').forEach(function(h, i) {{
      var a = h.querySelector('.tharrow');
      if (a) a.textContent = (i == col ? (dir == 1 ? ' ▲' : ' ▼') : '');
    }});
  }}
  document.querySelectorAll('table.ftable').forEach(function(table) {{
    var hrow = table.tHead.rows[0], n = hrow.cells.length;
    var frow = table.tHead.insertRow(); frow.className = 'frow';
    for (var i = 0; i < n; i++) {{
      (function(idx) {{
        var label = hrow.cells[idx].textContent.trim();
        hrow.cells[idx].style.cursor = 'pointer';
        hrow.cells[idx].addEventListener('click', function() {{ sortTable(table, idx, this); }});
        var fc = frow.insertCell(), ctrl;
        if (label === 'Hazard' || label === 'Status') {{
          ctrl = document.createElement('select');
          ctrl.innerHTML = '<option value="">all</option>';
          distinctCol(table, idx).forEach(function(v) {{
            var o = document.createElement('option'); o.value = v.toLowerCase(); o.textContent = v; ctrl.appendChild(o);
          }});
          ctrl.dataset.type = 'eq';
          ctrl.addEventListener('change', refilter);
        }} else if (label === 'Country') {{
          var dl = document.createElement('datalist'); dl.id = 'dl-' + table.id + '-' + idx;
          distinctCol(table, idx).forEach(function(v) {{ var o = document.createElement('option'); o.value = v; dl.appendChild(o); }});
          fc.appendChild(dl);
          ctrl = document.createElement('input');
          ctrl.setAttribute('list', dl.id); ctrl.placeholder = 'country…'; ctrl.dataset.type = 'contains';
          ctrl.addEventListener('input', refilter);
        }} else if (label === 'AOI') {{
          ctrl = document.createElement('input');
          ctrl.placeholder = 'filter…'; ctrl.dataset.type = 'contains';
          ctrl.addEventListener('input', refilter);
        }} else if (label === 'Monitoring') {{
          var det = document.createElement('details'); det.className = 'mfilter'; det.dataset.col = idx;
          var sum = document.createElement('summary'); sum.textContent = 'months'; det.appendChild(sum);
          var panel = document.createElement('div'); panel.className = 'mpanel';
          MONTHS_ABBR.forEach(function(name, k) {{
            var lab = document.createElement('label');
            var cb = document.createElement('input'); cb.type = 'checkbox'; cb.className = 'mbox'; cb.value = String(k + 1);
            cb.addEventListener('change', function() {{
              var nsel = det.querySelectorAll('input.mbox:checked').length;
              sum.textContent = nsel ? 'months (' + nsel + ')' : 'months';
              refilter();
            }});
            lab.appendChild(cb); lab.appendChild(document.createTextNode(' ' + name));
            panel.appendChild(lab);
          }});
          det.appendChild(panel); fc.appendChild(det);
          return;  // appended our own control
        }} else {{
          return;  // no filter control for other columns
        }}
        ctrl.className = 'colf'; ctrl.dataset.col = idx;
        fc.appendChild(ctrl);
      }})(i);
    }}
  }});
  function filterRows() {{ refilter(); }}
</script>
</body>
</html>
"""
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(doc, encoding="utf-8")
    print(f"Wrote {OUT.relative_to(ROOT)} — {len(active_rows)} active rows, {len(full_rows)} total rows, "
          f"{len(markers)} map markers ({n_activated} activated / {n_end} endorsed / "
          f"{n_recent} recently-triggered / {n_expired} expired / {n_dev} dev / {n_ret} retired).")


if __name__ == "__main__":
    main()
