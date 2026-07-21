#!/usr/bin/env python3
"""Export ONE framework version's trigger structure + simulated (backtested) activations
to the authoritative record: the dev DB `aa` schema (D86 — DB-as-source; the crosswalk
CSV loader in ds-knowledge-base, `load_aa_performance.py`, is the frozen legacy backfill).

Run from a spoke repo via the aa-methods plugin's `record-simulated-activations` skill:

    python export_simulated_activations.py export.yml [--dry-run] [--replace] [--force]

export.yml — one file per (framework, version, country); commit it in the spoke repo,
it is the reviewable record of what was exported and its provenance:

    kb_framework: afg-drought        # KB page folder name — exactly
    kb_version: "2026-04-04"         # KB page version date — exactly
    country_iso3: AFG
    kb_status: endorsed              # endorsed | development (trigger-stats renders endorsed only)
    source_repo: OCHA-DAP/ds-aa-afg-drought   # optional; inferred from `git remote` if omitted
    overall:                         # optional — REPORTED numbers from the trigger report
      rp: 3.91
      prob: 0.256
      spend_usd: 3070000
    windows:
      - name: Window A
        all_in: false
        basis: forecast              # forecast | observational
        allocation_usd: 3400000
        analysis_start: 1984         # the RP denominator — wrong span = wrong RP
        analysis_end: 2024
        rp_reported: 6.14            # optional; validation cross-check, never substituted
        prob_reported: 0.162         # optional
        source: repo                 # repo | excel | gsheet | report — where the YEARS came from
        note:                        # optional; e.g. reported-vs-derived discrepancies
        activations: [1985, 2000, 2018]
        # discrete events may carry labels/dates: {year: 2018, label: "Cyclone X", date: 2018-06-14}
        # two events in one year = ONE entry (the PK is per year); label both in `label`.

Writes all three tables atomically — aa.framework_version_map, aa.window,
aa.simulated_activation; the trigger-stats page inner-joins them, so a partial write
renders nothing. Guards: existing development-status rows need --replace; existing
ENDORSED rows need --force (a changed backtest after endorsement is usually a NEW
framework version, not an edit). Validates identity against the local KB clone
($KB_REPOS_DIR -> ~/.claude/.kb-repos-dir) when one is present.

Auth: ocha_stratus.get_engine(stage="dev", write=True) — needs DSCI_AZ_DB_DEV_* (+ write
variant); PGSSLMODE=require is set automatically.
"""
from __future__ import annotations

import argparse
import datetime as dt
import os
import re
import subprocess
import sys
from pathlib import Path

ISO3_RE = re.compile(r"^[A-Z]{3}$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
BASES = {"forecast", "observational"}
SOURCES = {"repo", "excel", "gsheet", "report"}
STATUSES = {"endorsed", "development"}

# Table + view DDL — keep in sync with ds-knowledge-base/scripts/load_aa_performance.py
# (idempotent: safe against the live schema, and makes a fresh DB work).
DDL = """
create schema if not exists aa;

create table if not exists aa.framework_version_map (
    kb_framework            text not null,
    kb_version              text not null,
    country_iso3            text not null,
    kb_status               text,
    gsheet_tab              text,
    excel_fv                text,
    overall_rp_reported     numeric,
    overall_prob_reported   numeric,
    flag                    text,
    primary key (kb_framework, kb_version, country_iso3)
);
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
    source          text,
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

create or replace view aa.v_framework_performance as
with act as (
    select kb_framework, kb_version, country_iso3, event_year
    from aa.simulated_activation group by 1,2,3,4
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


def kb_clone_dir() -> Path | None:
    """Resolve the local ds-knowledge-base clone: $KB_REPOS_DIR -> ~/.claude/.kb-repos-dir."""
    root = os.environ.get("KB_REPOS_DIR")
    if not root:
        state = Path.home() / ".claude" / ".kb-repos-dir"
        if state.is_file():
            root = state.read_text().strip()
    if root:
        clone = Path(root).expanduser() / "ds-knowledge-base"
        if clone.is_dir():
            return clone
    return None


def page_frontmatter(page: Path) -> dict[str, str]:
    """Minimal flat frontmatter parse (key: value lines) — enough for country_iso3/status."""
    fm: dict[str, str] = {}
    lines = page.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].strip() != "---":
        return fm
    for line in lines[1:]:
        if line.strip() == "---":
            break
        if ":" in line and not line.startswith((" ", "\t", "#")):
            k, _, v = line.partition(":")
            fm[k.strip()] = v.split("#")[0].strip()
    return fm


def infer_source_repo() -> str | None:
    try:
        url = subprocess.run(["git", "remote", "get-url", "origin"],
                             capture_output=True, text=True, check=True).stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None
    m = re.search(r"github\.com[:/]([^/]+/[^/.]+)", url)
    return m.group(1) if m else None


def norm_activation(entry, win_name: str, errors: list[str]) -> dict | None:
    """int -> {year}; dict -> {year, label, date}."""
    if isinstance(entry, int):
        return {"year": entry, "label": None, "date": None}
    if isinstance(entry, dict) and "year" in entry:
        d = entry.get("date")
        if isinstance(d, dt.datetime):
            d = d.date()
        if d is not None and not isinstance(d, dt.date):
            if isinstance(d, str) and DATE_RE.match(d):
                d = dt.date.fromisoformat(d)
            else:
                errors.append(f"window {win_name!r}: activation date {d!r} is not YYYY-MM-DD")
                d = None
        if d is not None and d.year != entry["year"]:
            errors.append(f"window {win_name!r}: activation date {d} disagrees with year {entry['year']}")
        return {"year": int(entry["year"]), "label": entry.get("label"), "date": d}
    errors.append(f"window {win_name!r}: unparseable activation entry {entry!r}")
    return None


def weibull(n_years: int, n_acts: int) -> float | None:
    return round((n_years + 1) / n_acts, 2) if n_acts else None


def validate(cfg: dict) -> tuple[list[str], list[str], list[dict]]:
    """Returns (errors, warnings, normalized windows with activation dicts)."""
    errors: list[str] = []
    warnings: list[str] = []

    fw, ver = cfg.get("kb_framework"), str(cfg.get("kb_version") or "")
    iso3, status = cfg.get("country_iso3"), cfg.get("kb_status")
    for field in ("kb_framework", "kb_version", "country_iso3", "kb_status"):
        if not cfg.get(field):
            errors.append(f"missing required field {field!r}")
    if iso3 and not ISO3_RE.match(str(iso3)):
        errors.append(f"country_iso3 {iso3!r} is not an upper-case ISO3 code")
    if status and status not in STATUSES:
        errors.append(f"kb_status {status!r} must be one of {sorted(STATUSES)} "
                      "(legacy superseded versions belong to the crosswalk backfill)")
    if ver and not DATE_RE.match(ver):
        msg = (f"kb_version {ver!r} is not a YYYY-MM-DD framework-doc date "
               "(the KB page version is the join key)")
        (errors if status == "endorsed" else warnings).append(msg)
    if fw and iso3:
        prefix = str(fw)[:3].upper()
        if prefix.isalpha() and len(str(fw)) > 3 and str(fw)[3] == "-" and prefix != iso3:
            warnings.append(f"framework id {fw!r} starts with {prefix!r} but country_iso3 is "
                            f"{iso3!r} — fine for multi-country frameworks, otherwise check")

    wins = cfg.get("windows") or []
    if not wins:
        errors.append("no windows defined — the trigger structure (windows, budgets, spans) "
                      "is part of the export")
    names = [w.get("name") for w in wins]
    if len(names) != len(set(names)):
        errors.append("duplicate window names")

    norm: list[dict] = []
    for w in wins:
        name = w.get("name") or "?"
        a0, a1 = w.get("analysis_start"), w.get("analysis_end")
        if not name or name == "?":
            errors.append("a window is missing `name`")
        if not (isinstance(a0, int) and isinstance(a1, int) and a0 <= a1):
            errors.append(f"window {name!r}: analysis_start/analysis_end must be ints with "
                          f"start <= end (got {a0!r}..{a1!r}) — the span is the RP denominator")
            a0, a1 = None, None
        if w.get("basis") is not None and w["basis"] not in BASES:
            errors.append(f"window {name!r}: basis {w['basis']!r} not in {sorted(BASES)}")
        if w.get("source") not in SOURCES:
            errors.append(f"window {name!r}: source {w.get('source')!r} must be one of "
                          f"{sorted(SOURCES)} — record where the YEARS came from")
        if w.get("allocation_usd") is not None and w["allocation_usd"] <= 0:
            errors.append(f"window {name!r}: allocation_usd must be positive")
        if "all_in" not in w:
            errors.append(f"window {name!r}: `all_in` is required (true = one envelope, "
                          "any trigger releases everything)")

        acts = [a for a in (norm_activation(e, name, errors)
                            for e in (w.get("activations") or [])) if a]
        years = [a["year"] for a in acts]
        if len(years) != len(set(years)):
            errors.append(f"window {name!r}: duplicate activation years — the record is one row "
                          "per year; two events in one year = one entry, label both")
        if a0 and a1:
            outside = [y for y in years if not a0 <= y <= a1]
            if outside:
                errors.append(f"window {name!r}: activation years {outside} outside the "
                              f"analysis span {a0}-{a1}")
        if not years:
            warnings.append(f"window {name!r}: zero simulated activations — legitimate for a "
                            "never-triggering backtest, but double-check it isn't a missed list")
        norm.append({**w, "activations": acts})

    # RP coherence: recompute and compare (reported values are a cross-check, never substituted)
    all_years: set[int] = set()
    spans: list[tuple[int, int]] = []
    for w in norm:
        a0, a1 = w.get("analysis_start"), w.get("analysis_end")
        if not (isinstance(a0, int) and isinstance(a1, int)):
            continue
        spans.append((a0, a1))
        rp = weibull(a1 - a0 + 1, len(w["activations"]))
        rep = w.get("rp_reported")
        if rp and rep and abs(rp - rep) > 0.1 * rep:
            warnings.append(f"window {w['name']!r}: computed RP {rp} vs reported {rep} drifts "
                            ">10% — record the discrepancy in `note`, don't silently pick")
        all_years |= {a["year"] for a in w["activations"]}
    if spans:
        o0, o1 = min(s[0] for s in spans), max(s[1] for s in spans)
        overall_rp = weibull(o1 - o0 + 1, len(all_years))
        indiv = [weibull(a1 - a0 + 1, len(w["activations"]))
                 for w, (a0, a1) in zip([w for w in norm if isinstance(w.get("analysis_start"), int)], spans)]
        indiv = [r for r in indiv if r]
        if overall_rp and indiv and overall_rp > min(indiv) + 0.01:
            warnings.append(f"overall RP {overall_rp} > smallest individual RP {min(indiv)} — "
                            "violates overall <= individual; check spans/years (see the "
                            "return-periods skill)")
        rep_overall = (cfg.get("overall") or {}).get("rp")
        if overall_rp and rep_overall and abs(overall_rp - rep_overall) > 0.1 * rep_overall:
            warnings.append(f"computed overall RP {overall_rp} vs reported {rep_overall} drifts "
                            ">10% — check spans and the year union")

    # identity vs the local KB clone
    clone = kb_clone_dir()
    if clone is None:
        warnings.append("no local KB clone found ($KB_REPOS_DIR / ~/.claude/.kb-repos-dir) — "
                        "identity checks against the framework page were SKIPPED")
    elif fw and ver:
        page = clone / "frameworks" / str(fw) / f"{ver}.md"
        if not page.is_file():
            warnings.append(f"KB page frameworks/{fw}/{ver}.md not found — for a brand-new "
                            "version create the page first (worktree + PR), or proceed and "
                            "open a KB issue so the page follows")
        else:
            fm = page_frontmatter(page)
            page_iso = fm.get("country_iso3", "")
            if iso3 and page_iso and str(iso3) not in re.findall(r"[A-Z]{3}", page_iso):
                errors.append(f"country_iso3 {iso3!r} does not match the KB page's "
                              f"country_iso3 {page_iso!r}")
            if status and fm.get("status") and fm["status"] != status:
                warnings.append(f"kb_status {status!r} differs from the KB page's status "
                                f"{fm['status']!r} — align them (the trigger-stats page "
                                "renders endorsed only)")
    return errors, warnings, norm


def print_plan(cfg: dict, norm: list[dict]) -> None:
    print(f"\nplan: {cfg['kb_framework']} {cfg['kb_version']} {cfg['country_iso3']} "
          f"[{cfg['kb_status']}] · {len(norm)} window(s)")
    for w in norm:
        n = len(w["activations"])
        rp = weibull(w["analysis_end"] - w["analysis_start"] + 1, n) \
            if isinstance(w.get("analysis_start"), int) and isinstance(w.get("analysis_end"), int) else None
        years = ", ".join(str(a["year"]) + (f"({a['label']})" if a.get("label") else "")
                          for a in w["activations"]) or "—"
        print(f"  {w['name']}: {w.get('analysis_start')}-{w.get('analysis_end')} · "
              f"{n} activation(s) · computed RP {rp} (reported {w.get('rp_reported')}) · "
              f"source={w.get('source')} · budget={w.get('allocation_usd')}")
        print(f"    years: {years}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("yml", help="export.yml describing one (framework, version, country)")
    ap.add_argument("--dry-run", action="store_true", help="validate + show plan; no DB")
    ap.add_argument("--replace", action="store_true",
                    help="overwrite an existing NON-endorsed export for this version")
    ap.add_argument("--force", action="store_true",
                    help="overwrite an existing ENDORSED export (usually wrong: a changed "
                         "backtest after endorsement is a NEW framework version)")
    args = ap.parse_args()

    try:
        import yaml
    except ImportError:
        sys.exit("needs pyyaml (uv pip install pyyaml)")
    cfg = yaml.safe_load(Path(args.yml).read_text(encoding="utf-8"))
    if not isinstance(cfg, dict):
        sys.exit(f"{args.yml}: not a YAML mapping")

    errors, warnings, norm = validate(cfg)
    for w in warnings:
        print(f"WARNING: {w}")
    if errors:
        for e in errors:
            print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
    print_plan(cfg, norm)
    if args.dry_run:
        print("\ndry-run: no DB writes.")
        return

    os.environ.setdefault("PGSSLMODE", "require")
    try:
        import ocha_stratus as stratus
        from sqlalchemy import text
    except ImportError:
        sys.exit("needs ocha-stratus + sqlalchemy (uv pip install ocha-stratus)")

    fw, ver, iso3 = cfg["kb_framework"], str(cfg["kb_version"]), cfg["country_iso3"]
    key = {"fw": fw, "ver": ver, "iso3": iso3}
    where = ("kb_framework = :fw and kb_version = :ver and country_iso3 = :iso3")
    eng = stratus.get_engine(stage="dev", write=True)

    with eng.connect() as c:
        exists = c.execute(text(
            "select to_regclass('aa.framework_version_map')")).scalar()
        prior_status, prior = None, []
        if exists:
            row = c.execute(text(
                f"select kb_status, source_repo, exported_at from aa.framework_version_map "
                f"where {where}"), key).first()
            prior_status = row[0] if row else None
            prior = list(c.execute(text(
                """select w.window_name, count(a.event_year),
                          coalesce(string_agg(a.event_year::text, ',' order by a.event_year), '')
                   from aa.window w
                   left join aa.simulated_activation a
                     on (a.kb_framework, a.kb_version, a.country_iso3, a.window_name)
                      = (w.kb_framework, w.kb_version, w.country_iso3, w.window_name)
                   where w.kb_framework = :fw and w.kb_version = :ver
                     and w.country_iso3 = :iso3
                   group by w.window_name order by w.window_name"""), key))
            if row or prior:
                print(f"\nEXISTING export for {fw} {ver} {iso3} "
                      f"[status={prior_status}, source_repo={row[1] if row else None}, "
                      f"exported_at={row[2] if row else None}]:")
                for name, n, years in prior:
                    print(f"  {name}: {n} activation(s) — {years or '—'}")
                if prior_status == "endorsed" and not args.force:
                    sys.exit("\nBLOCKED: this version is already exported as ENDORSED. "
                             "A changed backtest after endorsement is usually a NEW framework "
                             "version. If this really is a correction, confirm with the user "
                             "and re-run with --force.")
                if prior_status != "endorsed" and not (args.replace or args.force):
                    sys.exit("\nBLOCKED: this version already has a (non-endorsed) export. "
                             "Re-run with --replace to overwrite it.")

    source_repo = cfg.get("source_repo") or infer_source_repo()
    overall = cfg.get("overall") or {}
    with eng.begin() as c:  # one transaction; commits on exit
        for stmt in [s for s in DDL.split(";\n") if s.strip()]:
            c.execute(text(stmt))
        for t in ("simulated_activation", "window", "framework_version_map"):
            c.execute(text(f"delete from aa.{t} where {where}"), key)
        c.execute(text(
            "insert into aa.framework_version_map (kb_framework, kb_version, country_iso3, "
            "kb_status, overall_rp_reported, overall_prob_reported, overall_spend_reported, "
            "source_repo, exported_at) values (:fw, :ver, :iso3, :status, :rp, :prob, :spend, "
            ":repo, now())"),
            {**key, "status": cfg["kb_status"], "rp": overall.get("rp"),
             "prob": overall.get("prob"), "spend": overall.get("spend_usd"),
             "repo": source_repo})
        for w in norm:
            c.execute(text(
                "insert into aa.window (kb_framework, kb_version, country_iso3, window_name, "
                "all_in, basis, allocation_usd, analysis_start, analysis_end, rp_reported, "
                "prob_reported, source, note) values (:fw, :ver, :iso3, :name, :all_in, :basis, "
                ":alloc, :a0, :a1, :rp, :prob, :source, :note)"),
                {**key, "name": w["name"], "all_in": bool(w["all_in"]), "basis": w.get("basis"),
                 "alloc": w.get("allocation_usd"), "a0": w["analysis_start"],
                 "a1": w["analysis_end"], "rp": w.get("rp_reported"),
                 "prob": w.get("prob_reported"), "source": w["source"], "note": w.get("note")})
            for a in w["activations"]:
                c.execute(text(
                    "insert into aa.simulated_activation (kb_framework, kb_version, "
                    "country_iso3, window_name, event_year, event_label, event_date) "
                    "values (:fw, :ver, :iso3, :name, :year, :label, :date)"),
                    {**key, "name": w["name"], **a})

    # verification: what the views (and therefore the trigger-stats page) now compute
    with eng.connect() as c:
        print("\n-- aa.v_window_performance (computed from what was just written) --")
        for row in c.execute(text(
                f"""select window_name, analysis_years, n_activations, return_period,
                           activation_prob, rp_reported, prob_reported
                    from aa.v_window_performance where {where} order by window_name"""), key):
            print(f"  {row[0]}: {row[1]}y · {row[2]} acts · RP {row[3]} (reported {row[5]}) · "
                  f"prob {row[4]} (reported {row[6]})")
        print("-- aa.v_framework_performance --")
        for row in c.execute(text(
                f"""select analysis_years, n_activation_years, overall_return_period,
                           overall_activation_prob, all_in, total_budget
                    from aa.v_framework_performance where {where}"""), key):
            print(f"  overall: {row[0]}y · {row[1]} activation-years · RP {row[2]} · "
                  f"prob {row[3]} · all_in={row[4]} · budget={row[5]}")
    print(f"\nexported ✓  ({fw} {ver} {iso3} [{cfg['kb_status']}] · source_repo={source_repo})"
          "\ntrigger-stats regenerates daily (endorsed versions only render there).")


if __name__ == "__main__":
    main()
