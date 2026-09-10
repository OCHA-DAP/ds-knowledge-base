"""Load the AA trigger-performance tables into the dev `aa` schema (via ocha-stratus).

Reads the curated crosswalk CSV (scripts/aa_crosswalk.csv, built by build_aa_crosswalk.py) and
writes four tables + computed views. RP / probability / overall / effective-RP are NEVER stored —
they are computed in views from the raw activations + budgets, so there is one source of truth and
the published `rp`/`prob` from the gsheet are kept only as a validation cross-check.

KEYS (2026-09 cutover): every table is keyed DIRECTLY on the version registry's natural key
(country_iso3, hazard, version) — aa.framework_version (ds-aa-tracking) is THE version registry and
aa.window etc. join it with no intermediary. The old aa.trigger_source_crosswalk table is GONE:
the kb_framework -> (country, hazard) relation is resolved in code from framework-page frontmatter,
and the reported gsheet headlines live in aa.version_performance_reported. kb_framework and a
kb_version alias are retained as ATTRIBUTE columns (and in aa.framework_version_map, now a compat
view over version_performance_reported) so existing readers keep working.

Tables (schema `aa`):
  aa.window                    dimension: one row per canonical window, PK
                               (country_iso3, hazard, version, window_name); per-window budget, all_in
  aa.simulated_activation      fact: one row per (window, backtest year) — the historical activations
  aa.funding_breakdown         fact: finest-grain budget cells (window/source/agency/sector, nullable
                               axes) from framework-page `funding_rows` frontmatter. `provenance` =
                               'stated' (doc cell) or 'imputed-5-95' (the readiness convention: docs
                               with a Readiness+Action window pair that don't price the readiness
                               window get each stated row REPLACED by a 5% readiness / 95% action
                               pair — totals and sector/agency marginals unchanged).
                               Window amounts are AUTHORIZATION TO SPEND, not disbursement: CERF
                               typically wires 100% at the readiness trigger, but agencies may spend
                               only the readiness share until action confirms (rest reimbursed if it
                               doesn't). Doc statements like "fully disbursed at readiness" are cash
                               flow and do NOT override the 5/95 spend split.
  aa.version_performance_reported  the published gsheet headline RP/prob/spend per framework version
                               + the source provenance (gsheet tab / excel file) those numbers came
                               from. NOT a relation — windows join framework_version directly.
Views:
  aa.framework_version_map     COMPAT view (old crosswalk shape) over version_performance_reported
  aa.v_window_performance      per-window n_activations, return_period, activation_prob (Weibull)
  aa.v_framework_performance   per (framework,version,country) overall RP/prob + effective RP
  aa.v_funding_by_sector /     marginals of aa.funding_breakdown (sum over the other axes; rows with
  aa.v_funding_by_agency /     a null axis simply don't contribute to that marginal, so partial
  aa.v_funding_by_window       coverage matches the page dicts)

Auth: ocha-stratus get_engine(stage='dev', write=True); needs DSCI_AZ_DB_DEV_* env (+ _WRITE) and
PGSSLMODE=require. Run:  python scripts/load_aa_performance.py [--csv PATH] [--dry-run]
"""
import argparse, csv, glob, os, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CSV = ROOT / "scripts" / "aa_crosswalk.csv"

DDL = """
create schema if not exists aa;

create table if not exists aa.window (
    country_iso3    text   not null,
    hazard          text   not null,   -- canonical vocab (storm, not tropical-cyclone)
    version         text   not null,   -- framework_version label the window belongs to
    window_name     text   not null,
    kb_framework    text,              -- attribute (folder slug), NOT part of the key
    all_in          boolean not null default false,
    basis           text,
    allocation_usd  bigint,
    analysis_start  int,
    analysis_end    int,
    rp_reported     numeric,
    prob_reported   numeric,
    source          text,            -- gsheet | excel
    primary key (country_iso3, hazard, version, window_name)
);

create table if not exists aa.simulated_activation (
    country_iso3  text not null,
    hazard        text not null,
    version       text not null,
    window_name   text not null,
    event_year    int  not null,
    event_label   text,
    kb_framework  text,
    primary key (country_iso3, hazard, version, window_name, event_year)
);

create table if not exists aa.funding_breakdown (
    country_iso3  text not null,
    hazard        text not null,
    version       text not null,
    window_name   text,               -- null = whole-framework envelope (all_in / doc doesn't split)
    fund_source   text,               -- CERF | AHF | NHF | ... ; null = single/unspecified source
    agency        text,               -- null = sector-only cell (e.g. partner-TBD envelopes)
    sector        text,               -- doc's own label; null = agency-only cell
    amount_usd    bigint not null,
    provenance    text not null default 'stated',   -- stated | imputed-5-95
    kb_framework  text
);

create table if not exists aa.version_performance_reported (
    country_iso3            text not null,
    hazard                  text not null,
    version                 text not null,
    kb_framework            text,
    kb_status               text,
    gsheet_tab              text,      -- provenance of the reported numbers
    excel_fv                text,
    overall_rp_reported     numeric,   -- published overall return period (gsheet headline)
    overall_prob_reported   numeric,
    overall_spend_reported  bigint,
    flag                    text,
    primary key (country_iso3, hazard, version)
);

-- COMPAT: the old crosswalk shape, for readers still keyed (kb_framework, kb_version, country_iso3)
create or replace view aa.framework_version_map as
select kb_framework, version as kb_version, country_iso3, kb_status, gsheet_tab, excel_fv,
       overall_rp_reported, overall_prob_reported, overall_spend_reported, flag
from aa.version_performance_reported;

create or replace view aa.v_funding_by_sector as
select country_iso3, hazard, version, kb_framework, version as kb_version,
       sector, sum(amount_usd) as amount_usd
from aa.funding_breakdown where sector is not null
group by 1, 2, 3, 4, 6;

create or replace view aa.v_funding_by_agency as
select country_iso3, hazard, version, kb_framework, version as kb_version,
       agency, sum(amount_usd) as amount_usd
from aa.funding_breakdown where agency is not null
group by 1, 2, 3, 4, 6;

create or replace view aa.v_funding_by_window as
select country_iso3, hazard, version, kb_framework, version as kb_version, window_name,
       bool_or(provenance <> 'stated') as any_imputed, sum(amount_usd) as amount_usd
from aa.funding_breakdown where window_name is not null
group by 1, 2, 3, 4, 6;

create or replace view aa.v_window_performance as
select w.country_iso3, w.hazard, w.version, w.window_name, w.kb_framework,
       w.version as kb_version, w.all_in,
       w.allocation_usd, w.analysis_start, w.analysis_end,
       (w.analysis_end - w.analysis_start + 1)              as analysis_years,
       count(a.event_year)                                  as n_activations,
       round((w.analysis_end - w.analysis_start + 1 + 1.0)
             / nullif(count(a.event_year), 0), 2)           as return_period,
       round(count(a.event_year)::numeric
             / nullif(w.analysis_end - w.analysis_start + 1, 0), 3) as activation_prob,
       w.rp_reported, w.prob_reported
from aa.window w
left join aa.simulated_activation a
  on (a.country_iso3, a.hazard, a.version, a.window_name)
   = (w.country_iso3, w.hazard, w.version, w.window_name)
group by w.country_iso3, w.hazard, w.version, w.window_name, w.kb_framework, w.all_in,
         w.allocation_usd, w.analysis_start, w.analysis_end, w.rp_reported, w.prob_reported;

-- overall = ANY window firing in a year; effective RP = total budget / avg annual spend.
create or replace view aa.v_framework_performance as
with act as (
    select country_iso3, hazard, version, event_year
    from aa.simulated_activation group by 1,2,3,4          -- distinct activation years (any window)
),
dims as (
    select country_iso3, hazard, version, max(kb_framework) as kb_framework,
           min(analysis_start) as a0, max(analysis_end) as a1,
           bool_or(all_in) as all_in, sum(allocation_usd) as total_budget
    from aa.window group by 1,2,3
)
select d.country_iso3, d.hazard, d.version, d.kb_framework, d.version as kb_version,
       d.a1 - d.a0 + 1                                    as analysis_years,
       count(a.event_year)                                as n_activation_years,
       round((d.a1 - d.a0 + 1 + 1.0)
             / nullif(count(a.event_year), 0), 2)         as overall_return_period,
       round(count(a.event_year)::numeric
             / nullif(d.a1 - d.a0 + 1, 0), 3)             as overall_activation_prob,
       d.all_in, d.total_budget
from dims d
left join act a
  on (a.country_iso3, a.hazard, a.version) = (d.country_iso3, d.hazard, d.version)
group by d.country_iso3, d.hazard, d.version, d.kb_framework, d.a0, d.a1, d.all_in, d.total_budget;
"""

# canonical hazard vocab used across the aa schema (matches ds-aa-tracking normalize.py)
HAZARD_CANON = {
    "tropical-cyclone": "storm", "cyclone": "storm", "typhoon": "storm",
    "hurricane": "storm", "storms": "storm",
    "dry-spell": "drought", "dryspell": "drought", "dry spells": "drought",
    "floods": "flood", "flooding": "flood",
}


def framework_hazards(frameworks_dir=None):
    """kb_framework (folder slug) -> canonical hazard, from framework-page frontmatter.
    THE hardcoded relation that replaced the trigger_source_crosswalk table: a window
    belongs to (country, hazard, version); the slug is display/provenance only."""
    import yaml
    out = {}
    for f in sorted(glob.glob(str((frameworks_dir or ROOT / "frameworks") / "*/*.md"))):
        if f.endswith(("_TEMPLATE.md", "README.md")):
            continue
        m = re.match(r"^---\n(.*?)\n---", Path(f).read_text(encoding="utf-8"), re.S)
        if not m:
            continue
        try:
            fm = yaml.safe_load(m.group(1))
        except yaml.YAMLError:
            continue
        if not isinstance(fm, dict) or not fm.get("framework"):
            continue
        hz = str(fm.get("hazard") or "").strip().lower()
        if hz:
            out[fm["framework"]] = HAZARD_CANON.get(hz, hz)
    return out

def basis_of(window: str) -> str:
    w = window.lower()
    if any(k in w for k in ("observ", "réanalyse", "asap", "alarme")): return "observational"
    if any(k in w for k in ("forecast", "seas5", "readiness", "action", "window a", "prév", "mobilis", "prédict")):
        return "forecast"
    return None

def years(s):
    return sorted({int(m.group()) for m in re.finditer(r'\b(?:19|20)\d{2}\b', s or "")})

def num(s):
    """First number in a string ('6.14 years' -> 6.14, '16%' -> 16, '0.256' -> 0.256)."""
    m = re.search(r'[\d]+\.?[\d]*', str(s or ""))
    return float(m.group()) if m else None

def load_rows(csv_path, hazards):
    """One canonical window per (country, hazard, version, window). Loads endorsed + superseded KB
    versions, PLUS gsheet-backed PRIOR versions (the gsheet's older -YYYY tabs that have no KB-dated
    page) — keyed by their gsheet year — so each framework's version history is available. Excel-only
    PRE_KB rows (legacy insurance vintages with no gsheet tab) are skipped."""
    win, acts, prov = {}, [], {}
    missing_hazard = set()
    for r in csv.DictReader(open(csv_path)):
        status = r["kb_status"]; ver = r["kb_version"]
        if r["flag"] == "PRE_KB":
            tab = r["gsheet_tab"]; m = re.search(r'-(\d{4})', tab) if tab else None
            if not m: continue                     # no gsheet source for this prior version → skip
            ver = m.group(1); status = "prior"     # version = the gsheet tab year
        elif status not in ("endorsed", "superseded") or not ver or ver.startswith("("):
            continue
        fw, ctry, w = r["kb_framework"], r["country"], r["window"]
        if not w: continue
        hz = hazards.get(fw)
        if not hz:
            missing_hazard.add(fw); continue
        key = (ctry, hz, ver, w)
        ay = years(r["analysis"])
        a0, a1 = (ay[0], ay[-1]) if len(ay) >= 2 else (None, None)
        yrs = years(r["years_gsheet"]) or years(r["years_excel"])   # gsheet authoritative
        src = "gsheet" if years(r["years_gsheet"]) else "excel"
        bud = None
        try: bud = int(float(r["budget_usd"])) if r["budget_usd"] else None
        except ValueError: pass
        win[key] = dict(country_iso3=ctry, hazard=hz, version=ver, window_name=w,
                        kb_framework=fw,
                        all_in=(r["all_in"] == "Y"), basis=basis_of(w), allocation_usd=bud,
                        analysis_start=a0, analysis_end=a1,
                        rp_reported=num(r["rp"]), prob_reported=num(r["prob"]), source=src)
        for y in yrs:
            acts.append(dict(country_iso3=ctry, hazard=hz, version=ver, window_name=w,
                             event_year=y, event_label=None, kb_framework=fw))
        prov[(ctry, hz, ver)] = dict(country_iso3=ctry, hazard=hz, version=ver,
                                     kb_framework=fw,
                                     kb_status=status, gsheet_tab=r["gsheet_tab"],
                                     excel_fv=r["excel_fv"],
                                     overall_rp_reported=num(r.get("overall_rp")),
                                     overall_prob_reported=num(r.get("overall_prob")),
                                     overall_spend_reported=(int(float(r["overall_spend"])) if r.get("overall_spend") else None),
                                     flag=r["flag"])
    if missing_hazard:
        print(f"  WARNING: no hazard found for framework(s) {sorted(missing_hazard)} — rows skipped")
    return list(win.values()), acts, list(prov.values())

READINESS_SHARE = 0.05   # the 5%/95% readiness/action convention (docs that don't price readiness)

def load_funding_rows(hazards):
    """Finest-grain budget cells from framework-page `funding_rows` frontmatter (stated cells only —
    the pages never carry imputed values). Returns rows keyed like the other aa tables."""
    try:
        import yaml
    except ImportError:
        sys.exit("Needs pyyaml for funding_rows (use the aa-venv).")
    out = []
    for f in sorted(glob.glob(str(ROOT / "frameworks/*/*.md"))):
        if f.endswith(("_TEMPLATE.md", "README.md")): continue
        m = re.match(r"---\n(.*?)\n---\n", Path(f).read_text(encoding="utf-8"), re.S)
        if not m: continue
        try:
            fm = yaml.safe_load(m.group(1))
        except yaml.YAMLError:
            continue
        rows = fm.get("funding_rows") or []
        if not rows: continue
        fw, ver = fm.get("framework"), str(fm.get("version"))
        hz = hazards.get(fw)
        if not hz: continue
        iso = fm.get("country_iso3")
        default_iso = iso if isinstance(iso, str) else "ALL"   # multi-country: rows carry their own
        for r in rows:
            out.append(dict(country_iso3=r.get("country") or default_iso, hazard=hz,
                            version=ver, kb_framework=fw,
                            window_name=r.get("window"), fund_source=r.get("source"),
                            agency=r.get("agency"), sector=r.get("sector"),
                            amount_usd=int(r["amount_usd"]), provenance="stated"))
    return out

def impute_readiness(rows, windows):
    """The 5/95 convention: for a (country, hazard, version) whose aa.window set has a
    Readiness + Action(/Activation) pair but whose stated rows carry NO window attribution,
    replace each stated row with a readiness (5%) + action (95%) pair. Totals and the
    sector/agency marginals are unchanged; provenance marks the split as imputed."""
    by_key = {}
    for w in windows:   # (country_iso3, hazard, version) -> {window_name}
        by_key.setdefault(w[:3], set()).add(w[3])
    out, n_split = [], 0
    for key, group in _groupby(rows, lambda r: (r["country_iso3"], r["hazard"], r["version"])):
        names = by_key.get(key, set())
        ready = next((n for n in names if re.search(r"readiness", n, re.I)), None)
        action = next((n for n in names if re.search(r"action|activation", n, re.I)), None)
        if not (ready and action) or any(r["window_name"] for r in group):
            out.extend(group); continue
        for r in group:
            r_amt = round(r["amount_usd"] * READINESS_SHARE)
            out.append({**r, "window_name": ready, "amount_usd": r_amt, "provenance": "imputed-5-95"})
            out.append({**r, "window_name": action, "amount_usd": r["amount_usd"] - r_amt,
                        "provenance": "imputed-5-95"})
            n_split += 1
    return out, n_split

def _groupby(rows, key):
    groups = {}
    for r in rows: groups.setdefault(key(r), []).append(r)
    return groups.items()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", default=str(DEFAULT_CSV))
    ap.add_argument("--dry-run", action="store_true", help="parse + report; no DB connection/writes")
    args = ap.parse_args()

    hazards = framework_hazards()
    windows, acts, prov = load_rows(args.csv, hazards)
    funding = load_funding_rows(hazards)
    print(f"parsed: {len(windows)} windows · {len(acts)} activations · {len(prov)} framework-versions"
          f" · {len(funding)} funding cells")
    win_keys = [(w["country_iso3"], w["hazard"], w["version"], w["window_name"]) for w in windows]
    funding, n_split = impute_readiness(funding, win_keys)
    print(f"readiness 5/95 imputation: {n_split} stated rows split "
          f"-> {len(funding)} funding_breakdown rows")
    if args.dry_run:
        for w in windows[:8]:
            print("  ", w["country_iso3"], w["hazard"], w["version"], w["window_name"],
                  "all_in" if w["all_in"] else "", f"${w['allocation_usd']}", w["analysis_start"], w["analysis_end"])
        for r in funding[:8]:
            print("  fb:", r["country_iso3"], r["hazard"], r["version"], r["window_name"],
                  r["fund_source"], r["agency"], r["sector"], r["amount_usd"], r["provenance"])
        return

    os.environ.setdefault("PGSSLMODE", "require")
    # accommodate the older DS_AZ_DB_DEV_HOST env name if the DSCI_ form isn't set
    if not os.environ.get("DSCI_AZ_DB_DEV_HOST") and os.environ.get("DS_AZ_DB_DEV_HOST"):
        os.environ["DSCI_AZ_DB_DEV_HOST"] = os.environ["DS_AZ_DB_DEV_HOST"]
    try:
        import ocha_stratus as stratus
        from sqlalchemy import text
    except ImportError:
        sys.exit("Needs ocha-stratus + sqlalchemy (use the aa-venv).")
    eng = stratus.get_engine(stage="dev", write=True)
    with eng.begin() as c:                         # one transaction; commits on exit
        # cutover migration (2026-09): the crosswalk table is gone and the fact tables
        # are re-keyed on (country_iso3, hazard, version). All four are full-refresh,
        # so old shapes are simply dropped; framework_version_map survives as a compat
        # VIEW over version_performance_reported (recreated by the DDL below).
        c.execute(text("drop view if exists aa.framework_version_map cascade"))
        c.execute(text("drop table if exists aa.trigger_source_crosswalk cascade"))
        for t in ("window", "simulated_activation", "funding_breakdown"):
            has_new_key = c.execute(text(
                "select 1 from information_schema.columns where table_schema='aa' "
                f"and table_name='{t}' and column_name='hazard'")).scalar()
            if not has_new_key:
                c.execute(text(f"drop table if exists aa.{t} cascade"))
        for stmt in [s for s in DDL.split(";\n") if s.strip()]:
            c.execute(text(stmt))
        # idempotent reload of the four tables
        for t in ("simulated_activation", "window", "version_performance_reported", "funding_breakdown"):
            c.execute(text(f"truncate aa.{t}"))
        def ins(table, recs):
            if not recs: return
            cols = list(recs[0].keys())
            q = text(f"insert into aa.{table} ({','.join(cols)}) values ({','.join(':'+x for x in cols)})")
            c.execute(q, recs)
        ins("version_performance_reported", prov)
        ins("window", windows)
        ins("simulated_activation", acts)
        ins("funding_breakdown", funding)
    # validation: computed vs reported
    with eng.connect() as c:
        print("\n-- aa.v_framework_performance (overall) --")
        for row in c.execute(text("""select country_iso3, hazard, version,
                 overall_return_period, overall_activation_prob, all_in, total_budget
                 from aa.v_framework_performance order by 1,2,3""")):
            print("  ", *row)
        print("\n-- computed vs reported RP (per window, flag >10% drift) --")
        for row in c.execute(text("""select kb_framework, window_name, return_period, rp_reported
                 from aa.v_window_performance where rp_reported is not null
                 and abs(return_period - rp_reported) > 0.1*rp_reported order by 1""")):
            print("   DRIFT:", *row)
        # funding cells vs window envelopes: independent sources (framework PDF vs insurance Excel/
        # gsheet), so drift is informative, not fatal — flag >2% where the window names align
        print("\n-- funding_breakdown window sums vs aa.window envelopes (flag >2% drift) --")
        for row in c.execute(text("""
                 select f.country_iso3, f.hazard, f.version, f.window_name,
                        f.amount_usd as cells_sum, w.allocation_usd as envelope, f.any_imputed
                 from aa.v_funding_by_window f
                 join aa.window w
                   on (w.country_iso3, w.hazard, w.version) =
                      (f.country_iso3, f.hazard, f.version)
                  and lower(w.window_name) = lower(f.window_name)
                 where w.allocation_usd is not null
                   and abs(f.amount_usd - w.allocation_usd) > 0.02 * w.allocation_usd
                 order by 1, 2, 4""")):
            print("   FUND-DRIFT:", *row)
    print("\nloaded ✓")

if __name__ == "__main__":
    main()
