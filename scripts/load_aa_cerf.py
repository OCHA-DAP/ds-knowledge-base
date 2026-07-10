"""Load CERF allocations (OneGMS API) + REAL AA activations + their links into the dev `aa` schema.

Companion to load_aa_performance.py (which covers the SIMULATED/backtest side). This covers the
ACTUAL side: every CERF allocation from the OneGMS feed, the real activations recorded in the KB
framework pages' `activations:` frontmatter, and a curated many-to-many link between the two — so
per-activation CERF outcomes (amount approved, individuals planned/REACHED) are queryable.

Tables (schema `aa`):
  aa.cerf_allocation        ALL OneGMS applications (not just AA), keyed on application_code.
                            ApplicationID is NOT unique in the feed (~431 collisions) — never key
                            on it (see ds-cerf-supplement). `aa_keyword` flags anticipatory-action
                            titles ("anticipat*" / "early action"); the authoritative AA set is
                            whatever the link table references PLUS the curated `aa_adhoc` rows —
                            AA/early-action allocations with NO OCHA framework behind them
                            (e.g. Somalia 2023-25 early actions, Ethiopia OND-2024 drought AA).
  aa.actual_activation      one row per real activation EVENT (kb_framework, event_date), deduped
                            across the version pages that list it; kb_version = the version whose
                            reign it fired under (null if it predates all dated KB versions).
  aa.activation_allocation  curated link (scripts/aa_cerf_links.csv). MANY-TO-MANY:
                            LAC Mar-2026 = 1 activation -> 3 country applications;
                            TCD-drought 2026 W1+W2 / ETH 2020+2021 phases = N activations -> 1 app.
Views:
  aa.v_activation_funding   per-activation rollup: application codes, CERF USD approved,
                            individuals planned/reached. NOTE: an application SHARED by several
                            activations (flag SHARED_APP) repeats its totals on each — don't sum
                            this view across activations; sum aa.cerf_allocation instead.
  aa.v_aa_allocation        every CERF AA allocation (framework-linked or ad-hoc), one row per
                            (allocation, linked activation), with planned/reached.

The link CSV is the curation surface. Rows with an empty application_code (flag NO_CERF) mark
activations funded outside CERF (e.g. bfa-flooding via FHRAOC); rows with an empty kb_framework
(flag ADHOC_AA) mark ad-hoc AA allocations without a framework. After new activations land in the
KB (or new CERF AA allocations appear), run with --propose to see what needs curating.

Auth: ocha-stratus get_engine(stage='dev', write=True); needs DSCI_AZ_DB_DEV_* env (+ _WRITE) and
PGSSLMODE=require. Run:  python scripts/load_aa_cerf.py [--xml PATH] [--dry-run] [--propose]
"""
import argparse, csv, os, re, sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LINKS_CSV = ROOT / "scripts" / "aa_cerf_links.csv"
CERF_API_URL = "https://cerfgms-webapi.unocha.org/v1/application/All.xml"

DDL = """
create schema if not exists aa;

create table if not exists aa.cerf_allocation (
    application_code    text primary key,   -- e.g. 23-RR-AFG-61441 / CERF-GTM-26-RR-1521
    application_id      int,                -- NOT unique in the feed; informational only
    year                int,
    country_iso3        text,
    country_name        text,
    region_name         text,
    window_name         text,               -- Rapid Response | Underfunded Emergencies
    emergency_type      text,
    emergency_group     text,               -- EmergencyGroupForGlobalReporting
    title               text,
    allocation_status   text,               -- Under Review | Under Implementation | Completed | Report Available
    agencies            text,               -- ';'-separated agency short names
    amount_requested    numeric,
    amount_approved     numeric,
    individuals_affected bigint,
    individuals_planned  bigint,
    individuals_reached  bigint,
    erc_endorsement_date        date,
    first_project_approved_date date,
    last_project_approved_date  date,
    report_due_date             date,
    aa_keyword          boolean not null default false,
    aa_adhoc            boolean not null default false, -- curated: AA/early-action WITHOUT an OCHA framework
    aa_note             text,                           -- curation note for ad-hoc rows
    summary             text,               -- CN_Summary
    humanitarian_overview text,
    allocation_rationale  text
);
alter table aa.cerf_allocation add column if not exists aa_adhoc boolean not null default false;
alter table aa.cerf_allocation add column if not exists aa_note text;

create table if not exists aa.actual_activation (
    kb_framework    text not null,
    event_date      text not null,          -- as recorded: YYYY | YYYY-MM | YYYY-MM-DD
    kb_version      text,                   -- version in force when it fired; null = predates KB'd versions
    country_iso3    text,                   -- '+'-joined for multi-country frameworks
    window_name     text,
    full_activation boolean not null default true,
    released_usd    bigint,                 -- as recorded in KB frontmatter (may lag CERF's number)
    url             text,
    note            text,
    primary key (kb_framework, event_date)
);

create table if not exists aa.activation_allocation (
    kb_framework     text not null,
    event_date       text not null,
    application_code text not null references aa.cerf_allocation(application_code),
    flag             text,                  -- SHARED_APP = application spans several activations
    note             text,
    primary key (kb_framework, event_date, application_code),
    foreign key (kb_framework, event_date) references aa.actual_activation(kb_framework, event_date)
);

create or replace view aa.v_activation_funding as
select act.kb_framework, act.event_date, act.kb_version, act.country_iso3, act.window_name,
       act.full_activation, act.released_usd,
       count(ca.application_code)                                        as n_allocations,
       string_agg(ca.application_code, ' + ' order by ca.application_code) as application_codes,
       bool_or(l.flag = 'SHARED_APP')                                    as shared_app,
       sum(ca.amount_approved)                                           as cerf_amount_approved,
       sum(ca.individuals_planned)                                       as individuals_planned,
       sum(ca.individuals_reached)                                       as individuals_reached,
       min(ca.allocation_status)                                         as allocation_status,
       min(ca.erc_endorsement_date)                                      as erc_endorsement_date
from aa.actual_activation act
left join aa.activation_allocation l using (kb_framework, event_date)
left join aa.cerf_allocation ca using (application_code)
group by act.kb_framework, act.event_date, act.kb_version, act.country_iso3, act.window_name,
         act.full_activation, act.released_usd;

-- every CERF AA allocation, framework-linked or ad-hoc. One row per (allocation, linked activation):
-- LAC-style multi-country events give one row per country application; a SHARED_APP application
-- appears once per activation it funded (don't sum this view; sum aa.cerf_allocation instead).
create or replace view aa.v_aa_allocation as
select ca.application_code, ca.year, ca.country_iso3, ca.emergency_type, ca.title,
       ca.amount_approved, ca.individuals_planned, ca.individuals_reached, ca.allocation_status,
       l.kb_framework, l.event_date, ca.aa_adhoc, ca.aa_note
from aa.cerf_allocation ca
left join aa.activation_allocation l using (application_code)
where l.application_code is not null or ca.aa_adhoc;
"""

# ---------- OneGMS feed ----------

AA_KEYWORDS = ("anticipat", "early action")

def _txt(el, tag):
    c = el.find(tag)
    return c.text.strip() if c is not None and c.text and c.text.strip() else None

def _date(s):
    return s[:10] if s and re.match(r"\d{4}-\d{2}-\d{2}", s) else None

def _int(s):
    try: return int(float(s)) if s else None
    except ValueError: return None

def _num(s):
    try: return float(s) if s else None
    except ValueError: return None

def fetch_cerf(xml_path=None):
    """All applications from the OneGMS feed -> aa.cerf_allocation rows, keyed on ApplicationCode."""
    if xml_path:
        root = ET.parse(xml_path).getroot()
    else:
        import requests
        resp = requests.get(CERF_API_URL, timeout=300)
        resp.raise_for_status()
        root = ET.fromstring(resp.content)
    rows = []
    for a in root.findall("application"):
        title, emerg = _txt(a, "ApplicationTitle"), _txt(a, "EmergencyTypeName")
        hay = f"{title or ''} {emerg or ''}".lower()
        rows.append(dict(
            application_code=_txt(a, "ApplicationCode"),
            application_id=_int(_txt(a, "ApplicationID")),
            year=_int(_txt(a, "Year")),
            country_iso3=_txt(a, "CountryCode"),
            country_name=_txt(a, "CountryName"),
            region_name=_txt(a, "RegionName"),
            window_name=_txt(a, "WindowFullName"),
            emergency_type=emerg,
            emergency_group=_txt(a, "EmergencyGroupForGlobalReporting"),
            title=title,
            allocation_status=_txt(a, "AllocationStatus"),
            agencies=_txt(a, "AgencyShortName"),
            amount_requested=_num(_txt(a, "CN_AmountRequested")),
            amount_approved=_num(_txt(a, "TotalAmountApproved")),
            individuals_affected=_int(_txt(a, "TotalIndividualsAffected")),
            individuals_planned=_int(_txt(a, "TotalIndividualPlanned")),
            individuals_reached=_int(_txt(a, "TotalIndividualReached")),
            erc_endorsement_date=_date(_txt(a, "CN_ERC_EndorsementDate")),
            first_project_approved_date=_date(_txt(a, "FirstProjectApprovedDate")),
            last_project_approved_date=_date(_txt(a, "LastProjectApprovedDate")),
            report_due_date=_date(_txt(a, "ReportDueDate")),
            aa_keyword=any(k in hay for k in AA_KEYWORDS),
            summary=_txt(a, "CN_Summary"),
            humanitarian_overview=_txt(a, "OverviewoftheHumanitarianSituation"),
            allocation_rationale=_txt(a, "RationaleforCERFAllocation"),
        ))
    dupes = len(rows) - len({r["application_code"] for r in rows})
    if dupes:
        sys.exit(f"ApplicationCode no longer unique in the feed ({dupes} dupes) — investigate before loading.")
    return rows

# ---------- KB activations ----------

def _ym(s):
    """Year-month tuple, same as gen_public_site._parse_ym: '2024-09-27' -> (2024,9); '2021' -> (2021,1)."""
    m = re.match(r"\s*(\d{4})(?:-(\d{1,2}))?", str(s or ""))
    return (int(m.group(1)), int(m.group(2) or 1)) if m else None

def parse_activations(frameworks_dir):
    """Real activations from `activations:` frontmatter, one row per (framework, event_date).

    Version pages carry the historical-activation UNION (see gen_public_site.py), so the same event
    appears on several pages — dedupe, and attribute the version in force when it fired: the latest
    dated version of the framework <= event date, at year-month precision (the site's own rule);
    null if the event predates every dated version (early pilots with no KB'd page). Field values
    prefer the attributed version's page, falling back to any page that has them.
    """
    import yaml
    pages = []                               # (framework, version_str, version_ym, activation dicts, iso)
    versions = {}                            # framework -> {(ym, version_str), ...} — ALL dated versions
    for f in sorted(Path(frameworks_dir).glob("*/*.md")):
        m = re.match(r"^---\n(.*?)\n---", f.read_text(), re.S)
        if not m: continue
        try:
            fm = yaml.safe_load(m.group(1))
        except yaml.YAMLError:
            continue
        if not isinstance(fm, dict) or not fm.get("framework"): continue
        fw, ver = fm["framework"], str(fm.get("version"))
        vym = _ym(ver) if re.match(r"^\d{4}(-\d{1,2}){0,2}$", ver) else None
        if vym:
            versions.setdefault(fw, set()).add((vym, ver))
        if fm.get("activations"):
            iso = fm.get("country_iso3")
            pages.append((fw, ver, vym, fm["activations"],
                          "+".join(iso) if isinstance(iso, list) else iso))
    events = {}                              # (framework, date_str) -> [(version_ym, record), ...]
    for fw, ver, vym, acts, iso in pages:
        for a in acts:
            if not isinstance(a, dict) or not a.get("date"): continue
            d = str(a["date"]).strip()
            rec = dict(kb_framework=fw, event_date=d, kb_version=None, country_iso3=iso,
                       window_name=a.get("window"), full_activation=a.get("full_activation", True) is not False,
                       released_usd=_int(a.get("prearranged_or_released_usd")),
                       url=a.get("url"), note=a.get("note"))
            events.setdefault((fw, d), []).append((vym or (0, 0), rec))
    out = []
    for (fw, d), recs in sorted(events.items()):
        eym = _ym(d)
        eligible = [(vym, vs) for vym, vs in versions.get(fw, ()) if eym and vym <= eym]
        attributed = max(eligible)[1] if eligible else None
        # merge: attributed page's values first (if it lists the event), then newest-page fallback
        att_ym = next((vym for vym, vs in eligible if vs == attributed), None)
        recs.sort(key=lambda t: (t[0] != att_ym, tuple(-x for x in t[0])))
        merged = dict.fromkeys(recs[0][1])
        for _, rec in recs:
            for k, v in rec.items():
                if merged.get(k) is None and v is not None:
                    merged[k] = v
        merged["kb_version"] = attributed
        merged["full_activation"] = recs[0][1]["full_activation"]
        out.append(merged)
    return out

# ---------- curated links ----------

def load_links(path, activations, cerf_rows):
    """Validate the curated CSV against both sides; returns (link_rows, no_cerf_keys, adhoc).

    Three row kinds: normal links (framework + date + code); NO_CERF (framework + date, empty code)
    = activation funded outside CERF; ADHOC_AA (empty framework/date + code) = a CERF anticipatory/
    early-action allocation with NO OCHA framework behind it — flagged on aa.cerf_allocation.
    """
    act_keys = {(a["kb_framework"], a["event_date"]) for a in activations}
    cerf_by_code = {r["application_code"]: r for r in cerf_rows}
    links, no_cerf, adhoc, errs = [], set(), {}, []
    for r in csv.DictReader(open(path)):
        code = (r.get("application_code") or "").strip()
        if not r["kb_framework"]:                       # ad-hoc AA: allocation without a framework
            if r.get("flag") != "ADHOC_AA" or not code:
                errs.append(f"row without kb_framework must be flag=ADHOC_AA with an application_code: {r}")
            elif code not in cerf_by_code:
                errs.append(f"ADHOC_AA application_code {code!r} not in the OneGMS feed")
            else:
                adhoc[code] = r.get("note") or None
            continue
        key = (r["kb_framework"], r["event_date"])
        if key not in act_keys:
            errs.append(f"link row {key} has no matching KB activation")
            continue
        if not code:
            no_cerf.add(key)
            continue
        app = cerf_by_code.get(code)
        if app is None:
            errs.append(f"{key}: application_code {code!r} not in the OneGMS feed")
            continue
        iso_act = next(a["country_iso3"] for a in activations
                       if (a["kb_framework"], a["event_date"]) == key) or ""
        if app["country_iso3"] and app["country_iso3"] not in iso_act.split("+"):
            errs.append(f"{key}: country mismatch — activation {iso_act} vs application {app['country_iso3']} ({code})")
        links.append(dict(kb_framework=key[0], event_date=key[1], application_code=code,
                          flag=r.get("flag") or None, note=r.get("note") or None))
    if errs:
        sys.exit("link CSV validation failed:\n  " + "\n  ".join(errs))
    for r in cerf_rows:                                 # stamp the curated ad-hoc flag onto the feed rows
        r["aa_adhoc"] = r["application_code"] in adhoc
        r["aa_note"] = adhoc.get(r["application_code"])
    return links, no_cerf, adhoc

def report_gaps(activations, cerf_rows, links, no_cerf):
    """What still needs curating: unlinked activations, and AA-keyword allocations that are neither
    linked to an activation nor curated as ad-hoc."""
    linked = {(l["kb_framework"], l["event_date"]) for l in links}
    gaps = False
    for a in activations:
        key = (a["kb_framework"], a["event_date"])
        if key not in linked and key not in no_cerf:
            gaps = True
            print(f"  UNLINKED activation: {key[0]} {key[1]} ({a['country_iso3']}) — add to aa_cerf_links.csv")
            for r in cerf_rows:
                if r["aa_keyword"] and r["country_iso3"] in (a["country_iso3"] or "").split("+"):
                    print(f"      candidate: {r['application_code']} | {r['year']} | {r['title'][:70]}")
    used = {l["application_code"] for l in links}
    for r in sorted(cerf_rows, key=lambda x: x["application_code"]):
        if r["aa_keyword"] and r["application_code"] not in used and not r["aa_adhoc"]:
            gaps = True
            print(f"  ORPHAN AA allocation (no KB activation, not curated ad-hoc): {r['application_code']} | "
                  f"{r['year']} | {r['country_iso3']} | reached={r['individuals_reached']} | {r['title'][:70]}")
    if not gaps:
        print("  none — links fully curated ✓")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--xml", help="parse a saved All.xml instead of hitting the API")
    ap.add_argument("--links", default=str(LINKS_CSV))
    ap.add_argument("--dry-run", action="store_true", help="parse + validate + gap report; no DB writes")
    ap.add_argument("--propose", action="store_true", help="only print the curation gap report")
    args = ap.parse_args()

    cerf = fetch_cerf(args.xml)
    acts = parse_activations(ROOT / "frameworks")
    links, no_cerf, adhoc = load_links(args.links, acts, cerf)
    n_aa = sum(r["aa_keyword"] for r in cerf)
    print(f"parsed: {len(cerf)} CERF applications ({n_aa} AA-keyword) · {len(acts)} real activations · "
          f"{len(links)} links · {len(no_cerf)} non-CERF activations · {len(adhoc)} ad-hoc AA allocations")
    print("\n-- curation gaps --")
    report_gaps(acts, cerf, links, no_cerf)
    if args.dry_run or args.propose:
        return

    os.environ.setdefault("PGSSLMODE", "require")
    if not os.environ.get("DSCI_AZ_DB_DEV_HOST") and os.environ.get("DS_AZ_DB_DEV_HOST"):
        os.environ["DSCI_AZ_DB_DEV_HOST"] = os.environ["DS_AZ_DB_DEV_HOST"]
    try:
        import ocha_stratus as stratus
        from sqlalchemy import text
    except ImportError:
        sys.exit("Needs ocha-stratus + sqlalchemy (use the aa-venv).")
    eng = stratus.get_engine(stage="dev", write=True)
    with eng.begin() as c:
        for stmt in [s for s in DDL.split(";\n") if s.strip()]:
            c.execute(text(stmt))
        for t in ("activation_allocation", "actual_activation", "cerf_allocation"):  # FK order
            c.execute(text(f"truncate aa.{t} cascade"))
        def ins(table, recs):
            if not recs: return
            cols = list(recs[0].keys())
            q = text(f"insert into aa.{table} ({','.join(cols)}) values ({','.join(':'+x for x in cols)})")
            c.execute(q, recs)
        ins("cerf_allocation", cerf)
        ins("actual_activation", acts)
        ins("activation_allocation", links)
    with eng.connect() as c:
        print("\n-- aa.v_activation_funding --")
        for row in c.execute(text("""select kb_framework, event_date, application_codes,
                 cerf_amount_approved, individuals_planned, individuals_reached
                 from aa.v_activation_funding order by event_date""")):
            print("  ", *row)
    print("\nloaded ✓")

if __name__ == "__main__":
    main()
