---
content_type: infrastructure
last_reviewed: "2026-09-09"   # bump when re-verified against live pg_constraint / pg_indexes
---

# Database ER diagrams

Relational maps of the two schemas in the DB that actually *are* relational — **`aa`**
and **`storms`** — including the join edges the DB doesn't declare. The generated
[db-schema-dev.md](db-schema-dev.md) / [db-schema.md](db-schema.md) snapshots have the
complete column lists; this page adds the **relationships, provenance, and the
constraint story**. Hand-curated (the interesting edges are join-by-convention, so no
generator can introspect them); verified against live dev-DB `pg_constraint` /
`pg_indexes` introspection on 2026-08-03.

**Legend:** solid line = **declared foreign key** (DB-enforced); dashed line =
**join-by-convention** (same key, no constraint). The other schemas (`public`, `app`,
`hpc`, `ipc`, `pop`, `projects`) are flat fact/stats tables keyed by
`(iso3, pcode, valid_date, …)` with no inter-table structure — nothing to diagram
(see [the note at the end](#the-other-schemas-deliberately-not-relational)).

## `aa` — the AA portfolio & CERF funding schema (dev only)

Two writers meet in this schema (strict single-writer-per-table): the **OneGMS
mirrors** (CERF feed + CBPF OData API, `ds-cerf-supplement`) and the **AA
portfolio-tracking system** (`ds-aa-tracking`, see
[pipelines/aa-tracking.md](../pipelines/aa-tracking.md)), which owns every other table —
the framework and version registry, activations and funding, and since 2026-10-05 (D115)
the backtest tables and the KB-era record the KB's loaders used to write. Nothing in this
repo writes the schema any more. The KB-era curated crosswalk `activation_allocation`
(frozen) joined activations to the CERF mirror; its successor is `activation_funding`.

### Provenance — how OneGMS gets in and what joins it

```mermaid
flowchart LR
    onegms["OneGMS<br/>(CERF grant-management system)<br/>cerfgms-webapi public feed"]
    onegms -->|"daily upsert · ds-cerf-supplement<br/>refresh_mirror.py · key application_code"| mirror["aa.cerf_allocation<br/>(pure OneGMS mirror)"]
    onegms -->|"daily upsert · ds-cerf-supplement<br/>refresh_projects.py · key project_code"| projmirror["aa.cerf_project<br/>+ _sector / _country splits<br/>(pure OneGMS project mirror)"]
    mirror -->|"Claude-matched drought periods /<br/>IBTrACS storm links (ds-cerf-supplement)"| supp["aa.cerf_supplement<br/>aa.cerf_allocation_storm"]
    cbpfapi["CBPF OData API<br/>cbpfapi.unocha.org (public)"]
    cbpfapi -->|"daily · ds-cerf-supplement<br/>refresh_cbpf.py + refresh_cbpf_projects.py"| cbpf["aa.cbpf_allocation + aa.cbpf_fund<br/>aa.cbpf_project + _cluster/_subip<br/>(pure CBPF mirrors)"]
    mirror --> valloc["aa.v_allocation<br/>(fund-agnostic UNION view)"]
    cbpf --> valloc
    entry["ds-aa-tracking write paths<br/>entry / admin pages (proxy) ·<br/>entries files + backtest errata<br/>(nightly Databricks job)"]
    entry --> trk["aa.country_hazard / framework_version /<br/>window_activation / activation_funding /<br/>window_funding + more"]
    entry -->|"free while unsealed ·<br/>sealed: errata only"| perf["aa.window · aa.simulated_activation<br/>aa.version_performance_reported<br/>(framework_version_map = compat view)"]
    trk <-->|"activation_funding.allocation_code"| valloc
    frozen["KB-era record, frozen (D115)<br/>aa.actual_activation · aa.funding_breakdown<br/>aa.activation_allocation (old curated crosswalk)"]
    frozen <-->|"activation_allocation<br/>declared FK"| mirror
```

`aa.cerf_allocation` is a **pure mirror** of the OneGMS feed (D83): `ds-cerf-supplement`
is its sole writer, and everything AA-interpretive lives in the tables beside it. See
[datasets/cerf-onegms.md](datasets/cerf-onegms.md) for the feed itself and its gotchas
(key on `application_code`, never `application_id`).

### Entity-relationship diagram

```mermaid
erDiagram
    %% ---- OneGMS side ----
    cerf_allocation {
        text application_code PK "OneGMS key, e.g. 23-RR-AFG-61441"
        int year
        text country_iso3
        text window_name "RR / UF"
        text emergency_type
        numeric amount_approved
        bigint individuals_planned
        bigint individuals_reached
        boolean aa_keyword "deterministic title flag"
    }
    cerf_supplement {
        text application_code PK
        boolean not_tc
        int valid_month_start "drought met. period"
        int valid_year_start
        double confidence
    }
    cerf_allocation_storm {
        text application_code PK
        text sid PK "IBTrACS storm id"
    }
    cerf_project {
        text project_code PK "OneGMS key, e.g. 06-FAO-010-A"
        text application_code "indexed join to cerf_allocation"
        text agency_short_name
        numeric amount_approved "sums to allocation amount"
        bigint people_planned "+ w/m/g/b breakdowns"
        bigint people_reached
        text cap_codes "HRP project codes, ;-joined"
    }
    cerf_project_sector {
        text project_code "no PK - real dup sector split rows"
        int sector_id
        numeric sector_amount
    }
    cerf_project_country {
        text project_code PK
        text country_iso3 PK "regional projects span up to 22"
        numeric country_percent
    }
    ibtracs_storms {
        text sid PK "lives in schema storms"
    }

    %% ---- KB-era crosswalk (frozen; owned by ds-aa-tracking) ----
    activation_allocation {
        text kb_framework FK "nullable — ADHOC_AA rows"
        text event_date FK
        text application_code FK "nullable — NO_CERF rows"
        text flag "SHARED_APP / NO_CERF / ADHOC_AA"
    }

    %% ---- backtests + KB-era record (ds-aa-tracking) ----
    actual_activation {
        text kb_framework PK
        text event_date PK "text, not date"
        text window_name PK "'unspecified' when the page names none"
        text country_iso3
        text hazard "canonical vocab"
        text version "version in force; joins framework_version"
        boolean full_activation
        bigint released_usd
    }
    version_performance_reported {
        text country_iso3 PK
        text hazard PK
        text version PK
        text kb_framework "attribute, not key"
        text kb_status
        numeric overall_rp_reported "gsheet headline + its source tabs"
    }
    window {
        text country_iso3 PK
        text hazard PK
        text version PK
        text window_name PK
        text kb_framework "attribute, not key"
        boolean all_in
        bigint allocation_usd
        int analysis_start "backtest year range"
        int analysis_end
    }
    simulated_activation {
        text country_iso3 PK
        text hazard PK
        text version PK
        text window_name PK
        int event_year PK
    }
    funding_breakdown {
        text kb_framework "no PK on this table"
        text hazard
        text version
        text country_iso3
        text window_name "nullable axis"
        text fund_source "nullable axis"
        text agency "nullable axis"
        text sector "nullable axis"
        bigint amount_usd
        text provenance "stated / imputed-5-95"
    }

    %% declared FKs (solid)
    cerf_allocation |o--o{ activation_allocation : "application_code"
    actual_activation |o--o{ activation_allocation : "kb_framework + event_date"
    %% join-by-convention (dashed)
    cerf_allocation ||..o| cerf_supplement : "application_code"
    cerf_allocation ||..o{ cerf_allocation_storm : "application_code"
    cerf_allocation ||..|{ cerf_project : "application_code"
    cerf_project ||..|{ cerf_project_sector : "project_code"
    cerf_project ||..o{ cerf_project_country : "project_code"
    ibtracs_storms ||..o{ cerf_allocation_storm : "sid (cross-schema)"
    window ||..o{ simulated_activation : "iso3 + hazard + version + window_name"
    window |o..o{ funding_breakdown : "+ window_name (nullable)"
```

`activation_allocation` is deliberately keyless: its three row kinds carry NULLs a PK
can't hold — *link* rows (both sides set, many-to-many: `SHARED_APP` = several
activations on one application, and e.g. LAC Mar-2026 = one activation on three
applications), `NO_CERF` rows (activation funded outside CERF → `application_code`
NULL), and `ADHOC_AA` rows (AA allocation with no OCHA framework → framework side
NULL). Uniqueness is enforced by a **coalesce expression index** plus two CHECK
constraints on the NULL pattern, and the two declared FKs still guard whichever side
is non-null (D83). Frozen since 2026-10-05 together with `actual_activation` and
`funding_breakdown` — superseded by `activation_funding`, `window_activation` and
`window_funding` in ds-aa-tracking (D115).

### Views (computed, never stored)

RP / activation probability are **never stored** — computed in views from the raw
facts so there is one source of truth; the gsheet-published figures are kept only as
`*_reported` cross-checks.

| view | computes | from |
|---|---|---|
| `v_window_performance` | per-window n_activations, Weibull return period, activation prob | `window` ⟕ `simulated_activation` |
| `v_framework_performance` | overall RP/prob per (framework, version, country), total budget | `window` + `simulated_activation` |
| `v_funding_by_sector` / `_agency` / `_window` | marginals of the budget cells | `funding_breakdown` |
| `v_activation_funding` | per real activation: linked CERF USD, individuals planned/reached | `actual_activation` ⟕ `activation_allocation` ⟕ `cerf_allocation` |
| `v_aa_allocation` | every AA allocation, framework-linked or ad-hoc | `activation_allocation` ⨝ `cerf_allocation` |
| `v_allocation` | fund-agnostic allocation union (fund_type, allocation_code, amount, is_aa) | `cerf_allocation` ∪ `cbpf_allocation` (owned by ds-cerf-supplement) |
| `v_trk_*` | tracking-system reconciliation: framework-current rollup, version attribution/summary, activation reconciliation vs the KB-era record, AA-flag + localization checks, the backtest curation queue (`v_trk_backtest_check`) | ds-aa-tracking tables ⟕ KB-era/mirror tables |

### The 2026-08 expansion (ds-aa-tracking + CBPF mirrors)

The schema grew from 9 to ~34 tables in Aug 2026: 22 **portfolio-tracking** tables
(`ds-aa-tracking` — registry/version/window-era model: `framework_registry` →
`framework_version` (the unified version registry, one row per **endorsed document**)
→ version-attributed facts (status, funding, coverage, calendar, focal points, report
inclusion) + `fund` / `activation` / `activation_funding` (one activation, N fund
allocations — multi-fund events like Nigeria Sep-2025 CERF+NHF reconcile as one
event)) and 5 **CBPF mirror** tables + `v_allocation`. Diagramming all of them here
would drown the page — the tracking system publishes its own always-current
**crow's-foot ERDs and column-level schema** (the unification landed 2026-09: `aa.framework_version` is THE version registry; the crosswalk table is GONE — `aa.window` and `aa.actual_activation` key directly on (country_iso3, hazard, version), gsheet headline numbers live in `aa.version_performance_reported`, and `framework_version_map` survives only as a compatibility view) on its review site
(ocha-dap.github.io/ds-aa-tracking, internal password) and in its repo `DESIGN.md`.
The diagram above keeps the CERF-mirror core plus the backtest tables and the frozen
KB-era record (all ds-aa-tracking's since 2026-10-05, D115).

### Is `aa` set up properly as a relational database?

Mostly, yes — it's the best-constrained schema we have, and the soft spots are
deliberate trade-offs rather than neglect (audit below covers the original 9-table
core; the ds-aa-tracking tables follow the same conventions — natural keys, UNIQUE
NULLS NOT DISTINCT composites, single writer — with their constraint story in the
repo's DESIGN.md):

- **Uniqueness: 8 of 9 tables enforced.** Seven composite/natural PKs, plus the
  crosswalk's expression index. **`funding_breakdown` is the one gap** — no PK or
  unique index. It is frozen (no writer since the KB flip, 2026-09-28) and superseded
  by `window_funding`, which has a `UNIQUE NULLS NOT DISTINCT` key, so the gap can no
  longer grow.
- **FKs: 2 declared, ~7 by convention.** Only the (frozen) crosswalk edges are
  DB-enforced. Elsewhere FKs would impose write ordering across *separate repos*
  (e.g. `ds-cerf-supplement`'s mirror refresh vs `ds-aa-tracking`'s entries) for
  little gain. The backtest tables are guarded by triggers instead (ds-aa-tracking,
  2026-10-05): a deferred constraint trigger keeps every simulated year inside its
  window's analysed span (and the window must exist), and once a version's backtest
  is **sealed** every change from any writer is refused except a reviewed erratum
  (its `backtests/README.md`). The cheap win, if wanted: `cerf_supplement` and
  `cerf_allocation_storm` → `cerf_allocation` (same writer owns all three, so no
  ordering risk).
- **Natural text keys, not surrogates — deliberate.** A framework version is
  `(country_iso3, hazard, version)`, the key of `aa.framework_version`; `kb_framework`
  (the KB folder slug) survives as an attribute on the backtest and KB-era tables;
  `application_code` is OneGMS's own stable key.
- **Type warts:** `actual_activation.event_date` is `text` and is half the PK — it
  holds frontmatter date strings; fine for joining, but don't date-arithmetic on it
  without casting. `cerf_supplement`'s drought periods are split int month/year
  columns rather than dates.
- **Dev-only, deliberately** — the schema is analysis/curation infrastructure, not a
  prod app dependency (nothing in [pipeline-registry.md](pipeline-registry.md) reads
  it from prod).

## `storms` — storm identity, tracks, and exposure

Hub-and-spoke around three per-provider **identity tables** — `ibtracs_storms`
(`sid`), `nhc_storms` (`atcf_id`), `ecmwf_storms` — sharing a synthetic cross-provider
`storm_id`, with `storm_id_lookup` crosswalking GDACS/ADAM event ids onto them. Track
tables have real FKs (`ON DELETE CASCADE`); the buffer/exposure families dedupe via
composite `UNIQUE` constraints (22 of them) instead of PKs.

```mermaid
erDiagram
    ibtracs_storms {
        text sid PK
        text atcf_id
        text storm_id "cross-provider key"
    }
    nhc_storms {
        text atcf_id PK
        text storm_id
    }
    ecmwf_storms {
        text storm_id PK
    }
    storm_id_lookup {
        int gdacs_eventid PK
        text atcf_id
        text sid
        int adam_eventid
    }
    ibtracs_tracks_geo {
        text sid FK "ON DELETE CASCADE"
        timestamp valid_time
        geometry geometry
    }
    nhc_tracks_geo {
        text atcf_id FK "ON DELETE CASCADE"
        timestamp issued_time
        geometry geometry
    }
    ecmwf_tracks_geo {
        text storm_id FK
        timestamp issued_time
        geometry geometry
    }
    buffers_and_exposure {
        text family "ibtracs_wind_* · nhc_tracks_x3 · nhc_wsp_x5 · adam · gdacs"
        text key "storm key + wind_speed_kt (+ time, admin)"
        int pop_exposed "exposure tables"
    }
    admin_population {
        int admin_level UK
        text iso3 UK
        text pcode UK
        bigint total_pop
    }

    ibtracs_storms ||--o{ ibtracs_tracks_geo : "sid (FK)"
    nhc_storms ||--o{ nhc_tracks_geo : "atcf_id (FK)"
    ecmwf_storms ||--o{ ecmwf_tracks_geo : "storm_id (FK)"
    ibtracs_storms ||..o| storm_id_lookup : "sid"
    nhc_storms ||..o| storm_id_lookup : "atcf_id"
    ibtracs_storms ||..o{ buffers_and_exposure : "sid"
    nhc_storms ||..o{ buffers_and_exposure : "atcf_id"
    admin_population ||..o{ buffers_and_exposure : "iso3 + pcode (exposure)"
```

`buffers_and_exposure` above is a stand-in for the ~15 derived tables (see
[db-schema-dev.md](db-schema-dev.md) for the full list): the `ibtracs_wind_*` pair,
the three `nhc_tracks_{obsv,fcast,fcastonly}_{buffers,exposure}` sets, the five
`nhc_wsp_*` wind-speed-probability tables, and the ADAM/GDACS exposure +
`*_fm_lookup` admin-matching tables. All key back to their provider's identity table
by convention and dedupe with composite `UNIQUE` (mostly `NULLS NOT DISTINCT`)
constraints.

## The other schemas — deliberately not relational

`public`, `app`, `hpc`, `ipc`, `pop`, and `projects` are **flat fact/stats tables**:
raster zonal stats, HAPI/HPC extracts, and per-project monitoring series, each keyed
by some subset of `(iso3, pcode, adm_level, valid_date, issued_date)` and written by
append/replace pipelines. There are no inter-table joins to draw — the only shared
dimension is the admin geometry in `public.polygon` / `public.iso3`, which everything
joins on `(iso3, pcode)` by convention. Constraint coverage is thin (e.g. `app` and
`projects` have no PKs at all, `public.floodscan`/`era5`/`seas5` dedupe only by
pipeline discipline) — a known pattern, acceptable while each table has exactly one
pipeline writer; see [dependency-graph.md](dependency-graph.md) for who writes what.
