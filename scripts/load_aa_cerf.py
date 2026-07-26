"""Sync REAL AA activations (framework frontmatter) into the dev `aa` schema.

Companion to load_aa_performance.py (the SIMULATED/backtest side). This owns the ACTUAL side's
frontmatter-derived table and the views. The rest of the `aa` layer is owned elsewhere:

  aa.cerf_allocation        pure OneGMS mirror — feed columns upserted daily by
                            ds-cerf-supplement's refresh_mirror.py. Keyed on application_code
                            (ApplicationID is NOT unique in the feed, ~431 collisions).
                            This script never writes it.
  aa.actual_activation      one row per real activation EVENT (kb_framework, event_date), parsed
                            from the framework pages' `activations:` frontmatter — UPSERTED here
                            (deletes stale rows only when nothing links to them).
  aa.activation_allocation  the CURATED activation ↔ allocation crosswalk — a DB-as-source table
                            (the old scripts/aa_cerf_links.csv is retired; migrated by
                            migrate_aa_links_to_db.py). Written by apply_aa_links.py (the
                            kb-aa-links confirm flow) — never truncated here. Three row kinds:
                              link     (kb_framework, event_date, application_code [, SHARED_APP])
                              NO_CERF  (kb_framework, event_date, NULL)  activation funded outside CERF
                              ADHOC_AA (NULL, NULL, application_code)    AA allocation with no OCHA framework
Views:
  aa.v_activation_funding   per-activation rollup: application codes, CERF USD approved,
                            individuals planned/reached. NOTE: an application SHARED by several
                            activations (flag SHARED_APP) repeats its totals on each — don't sum
                            this view across activations; sum aa.cerf_allocation instead.
  aa.v_aa_allocation        every CERF AA allocation (framework-linked or ad-hoc), one row per
                            (allocation, linked activation), with planned/reached.

Gap detection/proposals live in propose_aa_links.py (the aa-links workflow), which posts
uncurated activations/allocations to the kb-aa-links issue with candidates from the mirror.

Auth: ocha-stratus get_engine(stage='dev', write=True); needs DSCI_AZ_DB_DEV_* env (+ _WRITE) and
PGSSLMODE=require. Run:  python scripts/load_aa_cerf.py [--dry-run]
"""
import argparse, os, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

DDL = """
create schema if not exists aa;

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

-- The curated crosswalk (DB-as-source; see module docstring for the three row kinds).
-- Nullable columns encode the kind; the coalesce unique index stands in for a PK.
create table if not exists aa.activation_allocation (
    kb_framework     text,
    event_date       text,
    application_code text references aa.cerf_allocation(application_code),
    flag             text,                  -- SHARED_APP | NO_CERF | ADHOC_AA
    note             text,
    updated_at       timestamptz not null default now(),
    foreign key (kb_framework, event_date) references aa.actual_activation(kb_framework, event_date),
    check (kb_framework is not null or application_code is not null),
    check ((kb_framework is null) = (event_date is null))
);
create unique index if not exists activation_allocation_uniq on aa.activation_allocation
    (coalesce(kb_framework,''), coalesce(event_date,''), coalesce(application_code,''));

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
       l.kb_framework, l.event_date,
       (l.flag = 'ADHOC_AA') as aa_adhoc, l.note as aa_note
from aa.activation_allocation l
join aa.cerf_allocation ca using (application_code);
"""

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

def _int(s):
    try: return int(float(s)) if s else None
    except (ValueError, TypeError): return None

# ---------- load ----------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="parse + report; no DB writes")
    args = ap.parse_args()

    acts = parse_activations(ROOT / "frameworks")
    print(f"parsed {len(acts)} real activations from framework frontmatter")
    if args.dry_run:
        for a in acts:
            print(f"  {a['kb_framework']} {a['event_date']} ({a['country_iso3']})")
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
    cols = list(acts[0].keys())
    upsert = text(
        f"insert into aa.actual_activation ({','.join(cols)}) "
        f"values ({','.join(':' + c for c in cols)}) "
        "on conflict (kb_framework, event_date) do update set "
        + ", ".join(f"{c} = excluded.{c}" for c in cols if c not in ("kb_framework", "event_date")))
    with eng.begin() as c:
        for stmt in [s for s in DDL.split(";\n") if s.strip()]:
            c.execute(text(stmt))
        c.execute(upsert, acts)
        # stale rows: in the DB but no longer in frontmatter. Delete only when nothing links
        # to them — a linked stale row means CSV-era curation vs frontmatter drift: surface it.
        keys = {(a["kb_framework"], a["event_date"]) for a in acts}
        db_keys = c.execute(text("select kb_framework, event_date from aa.actual_activation")).fetchall()
        for fw, ed in db_keys:
            if (fw, ed) in keys:
                continue
            n_links = c.execute(text(
                "select count(*) from aa.activation_allocation "
                "where kb_framework = :fw and event_date = :ed"), {"fw": fw, "ed": ed}).scalar()
            if n_links:
                print(f"  WARNING: stale activation {fw} {ed} has {n_links} curated link(s) — "
                      "kept; reconcile frontmatter vs aa.activation_allocation")
            else:
                c.execute(text("delete from aa.actual_activation "
                               "where kb_framework = :fw and event_date = :ed"), {"fw": fw, "ed": ed})
                print(f"  removed stale activation {fw} {ed}")
    with eng.connect() as c:
        print("\n-- aa.v_activation_funding --")
        for row in c.execute(text("""select kb_framework, event_date, application_codes,
                 cerf_amount_approved, individuals_planned, individuals_reached
                 from aa.v_activation_funding order by event_date""")):
            print("  ", *row)
    print("\nsynced ✓")

if __name__ == "__main__":
    main()
