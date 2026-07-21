"""LEGACY BACKFILL: load the AA trigger-performance crosswalk into the dev `aa` schema.

FROZEN since D86 (2026-07-21): the DB is now the authoritative home for simulated
activations, written per-version from spoke repos by the aa-methods plugin's exporter
(claude/plugins/aa-methods/scripts/export_simulated_activations.py — the
`record-simulated-activations` skill). This loader remains only to (re)load the legacy
gsheet/excel-era record from scripts/aa_crosswalk.csv — never add new versions to the CSV.
It therefore requires --backfill to write, and deletes ONLY the (framework, version,
country) keys present in the CSV — repo-exported versions are never touched.

Reads the curated crosswalk CSV and writes three tables + two computed views. RP /
probability / overall / effective-RP are NEVER stored — they are computed in views from
the raw activations + budgets, so there is one source of truth and the published
`rp`/`prob` from the gsheet are kept only as a validation cross-check.

Tables (schema `aa`):
  aa.framework_version_map   provenance: canonical (kb_framework, kb_version, country) <- source codes
  aa.window                  dimension: one row per canonical window (+ per-window budget, all_in)
  aa.simulated_activation    fact: one row per (window, backtest year) — the historical activations
Views:
  aa.v_window_performance    per-window n_activations, return_period, activation_prob (Weibull)
  aa.v_framework_performance per (framework,version,country) overall RP/prob + effective RP
Table + view DDL is duplicated in the plugin exporter — keep the two in sync.

Auth: ocha-stratus get_engine(stage='dev', write=True); needs DSCI_AZ_DB_DEV_* env (+ _WRITE) and
PGSSLMODE=require. Run:  python scripts/load_aa_performance.py --backfill [--csv PATH] [--dry-run]
"""
import argparse, csv, os, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CSV = ROOT / "scripts" / "aa_crosswalk.csv"

DDL = """
create schema if not exists aa;

create table if not exists aa.framework_version_map (
    kb_framework            text not null,
    kb_version              text not null,
    country_iso3            text not null,
    kb_status               text,
    gsheet_tab              text,
    excel_fv                text,
    overall_rp_reported     numeric,   -- published overall return period (gsheet headline)
    overall_prob_reported   numeric,
    flag                    text,
    primary key (kb_framework, kb_version, country_iso3)
);
alter table aa.framework_version_map add column if not exists overall_rp_reported numeric;
alter table aa.framework_version_map add column if not exists overall_prob_reported numeric;
alter table aa.framework_version_map add column if not exists overall_spend_reported bigint;
alter table aa.framework_version_map add column if not exists source_repo text;
alter table aa.framework_version_map add column if not exists exported_at timestamptz;

create table if not exists aa.window (
    kb_framework    text   not null,
    kb_version      text   not null,
    country_iso3    text   not null,
    window_name     text   not null,
    all_in          boolean not null default false,
    basis           text,
    allocation_usd  bigint,
    analysis_start  int,
    analysis_end    int,
    rp_reported     numeric,
    prob_reported   numeric,
    source          text,            -- gsheet | excel (exporter adds: repo | report)
    primary key (kb_framework, kb_version, country_iso3, window_name)
);
alter table aa.window add column if not exists note text;

create table if not exists aa.simulated_activation (
    kb_framework  text not null,
    kb_version    text not null,
    country_iso3  text not null,
    window_name   text not null,
    event_year    int  not null,
    event_label   text,
    primary key (kb_framework, kb_version, country_iso3, window_name, event_year)
);
alter table aa.simulated_activation add column if not exists event_date date;

create or replace view aa.v_window_performance as
select w.kb_framework, w.kb_version, w.country_iso3, w.window_name, w.all_in,
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
  on (a.kb_framework, a.kb_version, a.country_iso3, a.window_name)
   = (w.kb_framework, w.kb_version, w.country_iso3, w.window_name)
group by w.kb_framework, w.kb_version, w.country_iso3, w.window_name, w.all_in,
         w.allocation_usd, w.analysis_start, w.analysis_end, w.rp_reported, w.prob_reported;

-- overall = ANY window firing in a year; effective RP = total budget / avg annual spend.
create or replace view aa.v_framework_performance as
with act as (
    select kb_framework, kb_version, country_iso3, event_year
    from aa.simulated_activation group by 1,2,3,4          -- distinct activation years (any window)
),
dims as (
    select kb_framework, kb_version, country_iso3,
           min(analysis_start) as a0, max(analysis_end) as a1,
           bool_or(all_in) as all_in, sum(allocation_usd) as total_budget
    from aa.window group by 1,2,3
)
select d.kb_framework, d.kb_version, d.country_iso3,
       d.a1 - d.a0 + 1                                    as analysis_years,
       count(a.event_year)                                as n_activation_years,
       round((d.a1 - d.a0 + 1 + 1.0)
             / nullif(count(a.event_year), 0), 2)         as overall_return_period,
       round(count(a.event_year)::numeric
             / nullif(d.a1 - d.a0 + 1, 0), 3)             as overall_activation_prob,
       d.all_in, d.total_budget
from dims d
left join act a
  on (a.kb_framework, a.kb_version, a.country_iso3)
   = (d.kb_framework, d.kb_version, d.country_iso3)
group by d.kb_framework, d.kb_version, d.country_iso3, d.a0, d.a1, d.all_in, d.total_budget;
"""

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

def load_rows(csv_path):
    """One canonical window per (fw,ver,country,window). Loads endorsed + superseded KB versions,
    PLUS gsheet-backed PRIOR versions (the gsheet's older -YYYY tabs that have no KB-dated page) —
    keyed by their gsheet year — so each framework's version history is available. Excel-only PRE_KB
    rows (legacy insurance vintages with no gsheet tab) are skipped."""
    win, acts, prov = {}, [], {}
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
        key = (fw, ver, ctry, w)
        ay = years(r["analysis"])
        a0, a1 = (ay[0], ay[-1]) if len(ay) >= 2 else (None, None)
        yrs = years(r["years_gsheet"]) or years(r["years_excel"])   # gsheet authoritative
        src = "gsheet" if years(r["years_gsheet"]) else "excel"
        bud = None
        try: bud = int(float(r["budget_usd"])) if r["budget_usd"] else None
        except ValueError: pass
        win[key] = dict(kb_framework=fw, kb_version=ver, country_iso3=ctry, window_name=w,
                        all_in=(r["all_in"] == "Y"), basis=basis_of(w), allocation_usd=bud,
                        analysis_start=a0, analysis_end=a1,
                        rp_reported=num(r["rp"]), prob_reported=num(r["prob"]), source=src)
        for y in yrs:
            acts.append(dict(kb_framework=fw, kb_version=ver, country_iso3=ctry, window_name=w,
                             event_year=y, event_label=None))
        prov[(fw, ver, ctry)] = dict(kb_framework=fw, kb_version=ver, country_iso3=ctry,
                                     kb_status=status, gsheet_tab=r["gsheet_tab"],
                                     excel_fv=r["excel_fv"],
                                     overall_rp_reported=num(r.get("overall_rp")),
                                     overall_prob_reported=num(r.get("overall_prob")),
                                     overall_spend_reported=(int(float(r["overall_spend"])) if r.get("overall_spend") else None),
                                     flag=r["flag"])
    return list(win.values()), acts, list(prov.values())

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", default=str(DEFAULT_CSV))
    ap.add_argument("--dry-run", action="store_true", help="parse + report; no DB connection/writes")
    ap.add_argument("--backfill", action="store_true",
                    help="required to write: this loader only re-loads the frozen legacy "
                         "crosswalk; new versions go via the plugin exporter (D86)")
    args = ap.parse_args()

    windows, acts, prov = load_rows(args.csv)
    print(f"parsed: {len(windows)} windows · {len(acts)} activations · {len(prov)} framework-versions")
    if args.dry_run:
        for w in windows[:8]:
            print("  ", w["kb_framework"], w["kb_version"], w["country_iso3"], w["window_name"],
                  "all_in" if w["all_in"] else "", f"${w['allocation_usd']}", w["analysis_start"], w["analysis_end"])
        return
    if not args.backfill:
        sys.exit("refusing to write without --backfill: since D86 the DB is authoritative and "
                 "repo-exported versions live alongside the legacy record — this loader only "
                 "re-loads the frozen crosswalk. New versions: the aa-methods plugin's "
                 "record-simulated-activations skill / export_simulated_activations.py.")

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
        for stmt in [s for s in DDL.split(";\n") if s.strip()]:
            c.execute(text(stmt))
        # idempotent reload of the CSV's OWN keys only — repo-exported versions (D86,
        # exported_at is not null) and CSV rows since dropped are left untouched
        keys = {(p["kb_framework"], p["kb_version"], p["country_iso3"]) for p in prov}
        owned = {tuple(r) for r in c.execute(text(
            "select kb_framework, kb_version, country_iso3 from aa.framework_version_map "
            "where exported_at is not null"))}
        if keys & owned:
            for k in sorted(keys & owned):
                print(f"  SKIP {'/'.join(k)}: repo-exported (exported_at set) — the export "
                      "supersedes the crosswalk row")
            keys -= owned
        windows = [w for w in windows if (w["kb_framework"], w["kb_version"], w["country_iso3"]) in keys]
        acts = [a for a in acts if (a["kb_framework"], a["kb_version"], a["country_iso3"]) in keys]
        prov = [p for p in prov if (p["kb_framework"], p["kb_version"], p["country_iso3"]) in keys]
        for t in ("simulated_activation", "window", "framework_version_map"):
            for fw, ver, ctry in sorted(keys):
                c.execute(text(f"delete from aa.{t} where kb_framework = :fw "
                               "and kb_version = :ver and country_iso3 = :ctry"),
                          dict(fw=fw, ver=ver, ctry=ctry))
        def ins(table, recs):
            if not recs: return
            cols = list(recs[0].keys())
            q = text(f"insert into aa.{table} ({','.join(cols)}) values ({','.join(':'+x for x in cols)})")
            c.execute(q, recs)
        ins("framework_version_map", prov)
        ins("window", windows)
        ins("simulated_activation", acts)
    # validation: computed vs reported
    with eng.connect() as c:
        print("\n-- aa.v_framework_performance (overall) --")
        for row in c.execute(text("""select kb_framework, kb_version, country_iso3,
                 overall_return_period, overall_activation_prob, all_in, total_budget
                 from aa.v_framework_performance order by 1,2,3""")):
            print("  ", *row)
        print("\n-- computed vs reported RP (per window, flag >10% drift) --")
        for row in c.execute(text("""select kb_framework, window_name, return_period, rp_reported
                 from aa.v_window_performance where rp_reported is not null
                 and abs(return_period - rp_reported) > 0.1*rp_reported order by 1""")):
            print("   DRIFT:", *row)
    print("\nloaded ✓")

if __name__ == "__main__":
    main()
