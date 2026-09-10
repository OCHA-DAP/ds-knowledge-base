"""Sync REAL AA activations (framework frontmatter) into the dev `aa` schema.

Companion to load_aa_performance.py (the SIMULATED/backtest side). This owns the ACTUAL side's
frontmatter-derived table and the views. The rest of the `aa` layer is owned elsewhere:

  aa.cerf_allocation        pure OneGMS mirror — feed columns upserted daily by
                            ds-cerf-supplement's refresh_mirror.py. Keyed on application_code
                            (ApplicationID is NOT unique in the feed, ~431 collisions).
                            This script never writes it.
  aa.actual_activation      one row per real activation EVENT *per window* — PK
                            (kb_framework, event_date, window_name) with window_name
                            'unspecified' when the page doesn't name one (2026-09 cutover:
                            two windows firing the same date are now two rows, not a merge).
                            Carries country_iso3 + hazard + version so it joins
                            aa.framework_version directly (no crosswalk). Parsed from the
                            framework pages' `activations:` frontmatter — UPSERTED here
                            (deletes stale rows only when nothing links to them).
  aa.activation_allocation  the CURATED activation ↔ allocation crosswalk — a DB-as-source table
                            (the old scripts/aa_cerf_links.csv is retired; migrated by
                            migrate_aa_links_to_db.py). Written by apply_aa_links.py (the
                            kb-aa-links confirm flow) — never truncated here. Keyed to the
                            activation EVENT (kb_framework, event_date) — deliberately NOT
                            per-window: allocations fund the event. Three row kinds:
                              link     (kb_framework, event_date, application_code [, SHARED_APP])
                              NO_CERF  (kb_framework, event_date, NULL)  activation funded outside CERF
                              ADHOC_AA (NULL, NULL, application_code)    AA allocation with no OCHA framework
Views:
  aa.v_activation_funding   per-activation-EVENT rollup (windows aggregated back to the event so
                            allocation totals are never repeated): application codes, CERF USD
                            approved, individuals planned/reached. NOTE: an application SHARED by
                            several activations (flag SHARED_APP) repeats its totals on each —
                            don't sum this view across activations; sum aa.cerf_allocation instead.
  aa.v_aa_allocation        every CERF AA allocation (framework-linked or ad-hoc), one row per
                            (allocation, linked activation), with planned/reached.

Gap detection/proposals live in propose_aa_links.py (the aa-links workflow), which posts
uncurated activations/allocations to the kb-aa-links issue with candidates from the mirror.

Auth: ocha-stratus get_engine(stage='dev', write=True); needs DSCI_AZ_DB_DEV_* env (+ _WRITE) and
PGSSLMODE=require. Run:  python scripts/load_aa_cerf.py [--dry-run]
"""
import argparse, os, re, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from load_aa_performance import framework_hazards  # slug -> canonical hazard (the hardcoded relation)

ROOT = Path(__file__).resolve().parent.parent

DDL = """
create schema if not exists aa;

create table if not exists aa.actual_activation (
    kb_framework    text not null,           -- folder slug (display/provenance)
    event_date      text not null,           -- as recorded: YYYY | YYYY-MM | YYYY-MM-DD
    window_name     text not null default 'unspecified',
    country_iso3    text,                    -- '+'-joined for multi-country frameworks
    hazard          text,                    -- canonical vocab; joins aa.framework_version
    version         text,                    -- version in force when it fired; null = predates KB'd versions
    full_activation boolean not null default true,
    released_usd    bigint,                  -- as recorded in KB frontmatter (may lag CERF's number)
    url             text,
    note            text,
    primary key (kb_framework, event_date, window_name)
);

-- The curated crosswalk (DB-as-source; see module docstring for the three row kinds).
-- Keyed to the activation EVENT — no FK onto the per-window activation rows.
create table if not exists aa.activation_allocation (
    kb_framework     text,
    event_date       text,
    application_code text references aa.cerf_allocation(application_code),
    flag             text,                  -- SHARED_APP | NO_CERF | ADHOC_AA
    note             text,
    updated_at       timestamptz not null default now(),
    check (kb_framework is not null or application_code is not null),
    check ((kb_framework is null) = (event_date is null))
);
create unique index if not exists activation_allocation_uniq on aa.activation_allocation
    (coalesce(kb_framework,''), coalesce(event_date,''), coalesce(application_code,''));

-- per-EVENT rollup: window rows are aggregated back to the event before allocations join,
-- so a multi-window event never repeats its allocation totals.
create or replace view aa.v_activation_funding as
with ev as (
    select kb_framework, event_date,
           max(country_iso3) as country_iso3, max(hazard) as hazard, max(version) as version,
           string_agg(distinct window_name, ' + ' order by window_name) as window_name,
           bool_or(full_activation) as full_activation, sum(released_usd) as released_usd
    from aa.actual_activation
    group by kb_framework, event_date
)
select ev.kb_framework, ev.event_date, ev.version, ev.version as kb_version,
       ev.country_iso3, ev.hazard, ev.window_name,
       ev.full_activation, ev.released_usd,
       count(ca.application_code)                                        as n_allocations,
       string_agg(ca.application_code, ' + ' order by ca.application_code) as application_codes,
       bool_or(l.flag = 'SHARED_APP')                                    as shared_app,
       sum(ca.amount_approved)                                           as cerf_amount_approved,
       sum(ca.individuals_planned)                                       as individuals_planned,
       sum(ca.individuals_reached)                                       as individuals_reached,
       min(ca.allocation_status)                                         as allocation_status,
       min(ca.erc_endorsement_date)                                      as erc_endorsement_date
from ev
left join aa.activation_allocation l using (kb_framework, event_date)
left join aa.cerf_allocation ca using (application_code)
group by ev.kb_framework, ev.event_date, ev.version, ev.country_iso3, ev.hazard, ev.window_name,
         ev.full_activation, ev.released_usd;

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

def parse_activations(frameworks_dir, hazards):
    """Real activations from `activations:` frontmatter, one row per
    (framework, event_date, window). window defaults to 'unspecified' when the
    page doesn't name one — the curation queue, matching aa.activation's rule.

    Version pages carry the historical-activation UNION (see gen_public_site.py), so the same event
    appears on several pages — dedupe per window, and attribute the version in force when it fired:
    the latest dated version of the framework <= event date, at year-month precision (the site's own
    rule); null if the event predates every dated version (early pilots with no KB'd page). Field
    values prefer the attributed version's page, falling back to any page that has them.
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
    events = {}                              # (framework, date_str, window) -> [(version_ym, record), ...]
    for fw, ver, vym, acts, iso in pages:
        for a in acts:
            if not isinstance(a, dict) or not a.get("date"): continue
            d = str(a["date"]).strip()
            w = str(a.get("window") or "unspecified").strip() or "unspecified"
            rec = dict(kb_framework=fw, event_date=d, window_name=w, version=None,
                       country_iso3=iso, hazard=hazards.get(fw),
                       full_activation=a.get("full_activation", True) is not False,
                       released_usd=_int(a.get("prearranged_or_released_usd")),
                       url=a.get("url"), note=a.get("note"))
            events.setdefault((fw, d, w), []).append((vym or (0, 0), rec))
    out = []
    for (fw, d, w), recs in sorted(events.items()):
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
        merged["version"] = attributed
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

    hazards = framework_hazards(ROOT / "frameworks")
    acts = parse_activations(ROOT / "frameworks", hazards)
    print(f"parsed {len(acts)} real activation-window rows from framework frontmatter")
    if args.dry_run:
        for a in acts:
            print(f"  {a['kb_framework']} {a['event_date']} [{a['window_name']}] ({a['country_iso3']})")
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
        "on conflict (kb_framework, event_date, window_name) do update set "
        + ", ".join(f"{c} = excluded.{c}" for c in cols
                    if c not in ("kb_framework", "event_date", "window_name")))
    with eng.begin() as c:
        # cutover migration (2026-09): re-key per window. The old table (PK
        # kb_framework+event_date, kb_version column) is dropped and rebuilt from
        # frontmatter — content is fully regenerated here anyway. The FK from
        # activation_allocation is gone by design (allocations fund the EVENT;
        # windows subdivide it), so drop it before the table.
        legacy = c.execute(text(
            "select 1 from information_schema.columns where table_schema='aa' "
            "and table_name='actual_activation' and column_name='kb_version'")).scalar()
        if legacy:
            c.execute(text(
                "alter table aa.activation_allocation drop constraint if exists "
                "activation_allocation_kb_framework_event_date_fkey"))
            c.execute(text("drop table if exists aa.actual_activation cascade"))
        for stmt in [s for s in DDL.split(";\n") if s.strip()]:
            c.execute(text(stmt))
        c.execute(upsert, acts)
        # stale rows: in the DB but no longer in frontmatter. Delete only when nothing links
        # to them — a linked stale row means CSV-era curation vs frontmatter drift: surface it.
        keys = {(a["kb_framework"], a["event_date"], a["window_name"]) for a in acts}
        db_keys = c.execute(text(
            "select kb_framework, event_date, window_name from aa.actual_activation")).fetchall()
        for fw, ed, w in db_keys:
            if (fw, ed, w) in keys:
                continue
            n_links = c.execute(text(
                "select count(*) from aa.activation_allocation "
                "where kb_framework = :fw and event_date = :ed"), {"fw": fw, "ed": ed}).scalar()
            n_sibling = sum(1 for k in keys if k[0] == fw and k[1] == ed)
            if n_links and not n_sibling:
                print(f"  WARNING: stale activation {fw} {ed} [{w}] has {n_links} curated link(s) — "
                      "kept; reconcile frontmatter vs aa.activation_allocation")
            else:
                c.execute(text("delete from aa.actual_activation "
                               "where kb_framework = :fw and event_date = :ed and window_name = :w"),
                          {"fw": fw, "ed": ed, "w": w})
                print(f"  removed stale activation row {fw} {ed} [{w}]")
    with eng.connect() as c:
        print("\n-- aa.v_activation_funding --")
        for row in c.execute(text("""select kb_framework, event_date, window_name, application_codes,
                 cerf_amount_approved, individuals_planned, individuals_reached
                 from aa.v_activation_funding order by event_date""")):
            print("  ", *row)
    print("\nsynced ✓")

if __name__ == "__main__":
    main()
