---
content_type: analysis
name: nga-niger-benue-multistate
analysis_type: pre-framework
status: active
country_iso3: NGA
hazard: flood
summary: DRAFT (unreviewed, unapproved) reproduction of the endorsed Adamawa multi-gauge flood-trigger method across all 14 Niger/Benue riverine states, feeding a national-level government (non-OCHA) AA framework in design
data_sources: [Google-GRRR, GloFAS, FloodScan-SFED, HydroRIVERS, NiHSA]
feeds: [government-of-nigeria-nga-flood]   # the national framework page in external-frameworks/
surfaces:
  - {url: "https://ocha-dap.github.io/ds-aa-nga-flooding/app/", kind: app, title: "Niger/Benue flood-trigger monitor (static data app, pre-baked JSON incl. live Google forecasts)"}
source_repo: ocha-dap/ds-aa-nga-flooding
source_branch: feat/niger-benue-multistate-monitoring
source_sha: 1134cd0
code_ref:
  - src/config/registry.py
  - src/config/presets.py
  - pipelines/build_config_registry.py
  - pipelines/build_floodscan_benchmark.py
  - pipelines/build_trigger_config.py
  - pipelines/tune_trigger_gridsearch.py
  - pipelines/check_reforecast_skill.py
  - pipelines/export_app_data.py
  - app/index.html
depends_on: []
discrepancies:
  - "[gap] GloFAS readiness triggers (Phase 3) not yet derived — per-state glofas_readiness_thresh/leadtime are null in the registry; deferred until the whole-country GloFAS reforecast processing fully lands (repo PR #35)."
  - "[stale] Monitoring/app data refresh runs off the feature branch via a cron shim on main (repo PR #36) until feat/niger-benue-multistate-monitoring merges."
extra:
  maturity: "draft — a first end-to-end pass, not reviewed or approved by anyone (as of 2026-08-03)"
  method_parent: frameworks/nga-flooding 2026-06-18 (endorsed Adamawa multi-gauge design)
visibility: internal
last_synced: "2026-08-03"
---

# Nigeria Niger/Benue multi-state flood triggers — analysis

> **Analysis, not a framework — and a DRAFT.** This is OCHA-CHD's trigger
> derivation feeding a national-level, government-owned AA framework in design
> ([external-frameworks/government-of-nigeria/nga-flood](../external-frameworks/government-of-nigeria/nga-flood.md))
> — not an OCHA/CERF framework, and there is no published framework document.
> The whole derivation is a **simple first-pass draft: nothing here has been
> reviewed or approved** by the government, a working group, or internally —
> per-state configurations and performance numbers are exploratory and expected
> to change. The canonical code is at `code_ref`; this page explains it, it does
> not redefine it.

## What it is

Reproduces the **endorsed 2026 Adamawa multi-gauge trigger method**
([frameworks/nga-flooding/2026-06-18](../frameworks/nga-flooding/2026-06-18.md))
across **all 14 states along the Niger and Benue rivers**: Adamawa, Anambra,
Bayelsa, Benue, Delta, Edo, Imo, Kebbi, Kogi, Kwara, Nasarawa, Niger, Rivers,
Taraba. Google-first by design decision: the GRRR action-trigger derivation
(workflow steps 1–6) is done; the GloFAS readiness component (step 7) is deferred
(see discrepancies).

## What was analyzed / findings

### Scope & configuration registry

- **Riverine LGAs derived automatically:** Niger + Benue main channels
  (HydroRIVERS `DIS_AV_CMS >= 500`) buffered 10 km ∩ LGA polygons → **89 LGAs /
  14 states**. Validated: recovers Adamawa's endorsed 7 LGAs (+ river-adjacent
  Song, dropped by pinning Adamawa to the endorsed set for continuity).
- **Data-driven registry replaces the old hardcoded `STATE_CONFIG`:**
  `pipelines/build_config_registry.py` → `{lga,gauge}_registry.parquet` on blob
  (dev stage), loaded via `src/config/registry.py` with named presets
  (`src/config/presets.py`).
- **Cross-state gauge sharing:** the gauge registry is keyed **(gauge_id,
  state)** — a gauge informs every state whose riverine-LGA zone buffered 10 km
  contains it (138 of 289 GRRR gauges serve more than one state; the same gauge
  can carry a different threshold per state). **Adamawa's pool stays pinned to
  in-state Google gauges** to preserve the endorsed configuration.

### Method (the endorsed Adamawa workflow, parameterized per state)

1. **Floodscan benchmark per state** (`build_floodscan_benchmark.py`): daily mean
   SFED over the state's riverine buffer, 1998–2025. Validated exact against the
   endorsed Adamawa benchmark (identical 42 pixels, zero SFED difference).
2. **Flood-season convention:** seasons run **Apr 1 → Mar 31, labelled by start
   year** (`SEASON_START_MONTH = 4` in `build_trigger_config.py`) — Kebbi's
   February peaks and the Bayelsa/Rivers Jan–Feb upper-Niger "black flood" peaks
   are otherwise split into the wrong calendar year; the country-wide
   climatological trough is Mar–Apr.
3. **Correlation windows:** step-3 gauge–Floodscan Spearman ρ is computed on
   wet-season daily values only, with the per-state window anchored on the
   state's climatological Floodscan peak (**peak −1 .. peak +2 months**): Aug–Nov
   for the Sep-peak states (Adamawa, Kebbi, Taraba), Sep–Dec for the other 11.
   This reproduces the canonical Aug–Nov `WET_MONTHS` for Adamawa. **Validation:
   the derived Adamawa top-10 matches the endorsed gauge list exactly (10/10)** —
   year-round ρ had drifted the selection.
4. **Gauge selection:** top 10 gauges per state by wet-season ρ from the combined
   GRRR + GloFAS pool (GloFAS station daily proxy = reforecast ensemble-median at
   shortest lead). After the wet-season re-rank, **4 GloFAS stations survive
   selection**: onitsha (Anambra + Delta), baro + lokoja (Kogi), kende (Kebbi);
   127 selected gauge-state rows overall (Imo has only 2 viable gauges, Rivers 5).
5. **Trigger tuning** (`tune_trigger_gridsearch.py`): per-state grid search over
   per-gauge RP ∈ {2,3,4,5} × consensus fraction, same-day simultaneous
   exceedance, state-level grouping. **Uniform activation frequency by design:**
   every state is pinned to the endorsed Adamawa trigger's **6 fire-seasons in
   26** (~4.5-yr overall RP, ~22% annual probability) — the *individual-gauge* RP
   varies per state; F1 against 4-yr Floodscan flood events breaks ties. Adamawa
   itself is pinned to the endorsed configuration (RP 4, ≥6/10 gauges).
6. **GRRR reforecast skill check** (`check_reforecast_skill.py`): seasonal-peak
   rank agreement between reanalysis and reforecast (2016–2022, leads 0–7 d):
   median rank ρ ≈ 0.96–1.00 at leads 0–3 d everywhere, ≥0.95 at 7 d for most
   states — justifying reanalysis-based calibration. **Taraba is the outlier**
   (ρ decays to 0.59 at lead 7; use short leads there). GloFAS lead-decay:
   onitsha/lokoja/baro/kende hold ρ ≥ 0.82 at 16 d (promising for future
   readiness triggers); umaisha/makurdi/ibi decay hard past ~4 d.

### Per-state results — draft (app export 2026-07-15, sha 1134cd0)

All states fire 6 of 26 seasons by construction; F1/POD/FPR are scored against
each state's 4-yr Floodscan event seasons (~5–6 events — **small sample**).
Viability tiers as rendered in the app: **strong** F1 ≥ 0.70, **moderate**
F1 ≥ 0.50, **weak** F1 < 0.50 or FPR > 0.20.

| state | per-gauge RP | consensus | gauges | F1 | POD | FPR | tier |
|---|---|---|---|---|---|---|---|
| Bayelsa | 4 | 0.2 | 10 | 0.909 | 1.00 | 0.05 | strong |
| Rivers | 4 | 0.1 | 5 | 0.909 | 1.00 | 0.05 | strong |
| Delta | 3 | 1.0 | 10 | 0.833 | 0.83 | 0.05 | strong |
| Imo | 4 | 0.1 | 2 | 0.727 | 0.80 | 0.10 | strong |
| Kogi | 2 | 1.0 | 10 | 0.727 | 0.80 | 0.10 | strong |
| Anambra | 3 | 1.0 | 10 | 0.667 | 0.67 | 0.10 | moderate |
| Adamawa (pinned) | 4 | 0.6 | 10 | 0.545 | 0.60 | 0.14 | moderate |
| Kebbi | 4 | 0.2 | 10 | 0.545 | 0.60 | 0.14 | moderate |
| Nasarawa | 4 | 0.5 | 10 | 0.545 | 0.60 | 0.14 | moderate |
| Niger | 4 | 0.1 | 10 | 0.545 | 0.60 | 0.14 | moderate |
| Taraba | 4 | 0.3 | 10 | 0.545 | 0.60 | 0.14 | moderate |
| Benue | 5 | 0.2 | 10 | 0.500 | 0.50 | 0.15 | moderate |
| Edo | 4 | 0.3 | 10 | 0.500 | 0.50 | 0.15 | moderate |
| Kwara | 4 | 0.1 | 10 | 0.500 | 0.50 | 0.15 | moderate |

### Monitoring app

Static **GitHub Pages** app (per [methods/static-data-apps](../methods/static-data-apps.md)):
`pipelines/export_app_data.py` exports blob → JSON (~0.8 MB) including **live
Google GRRR reforecasts** and the **operational GloFAS 5-day ensemble-mean** (CDS
`cems-glofas-forecast`) per selected station; `app/` is Leaflet + hand-rolled SVG
charts — national map of gauges/stations and riverine LGAs, per-state
year-by-year trigger table (gauges met / needed / Floodscan RP /
hit-miss-false-alarm), season-peak comparison scatters, reforecast-skill
expanders. Refreshed 6-hourly (cron shim on main, repo PR #36, until the branch
merges). Replaced a torn-down Azure App Service Streamlit deployment
(2026-07-15).

## Relation to frameworks

- **Feeds** the national-level Government of Nigeria flood framework
  ([external-frameworks/government-of-nigeria/nga-flood](../external-frameworks/government-of-nigeria/nga-flood.md))
  — in design, no document yet.
- **Method parent:** OCHA's endorsed
  [nga-flooding 2026-06-18](../frameworks/nga-flooding/2026-06-18.md) Adamawa
  multi-gauge design. Adamawa is pinned to the endorsed configuration throughout
  (LGAs, in-state gauge pool, RP 4 / ≥6-of-10, 6 fire-seasons), so the OCHA
  framework remains an exact subset of the national analysis.

## Sources & status

- **Repo:** `ocha-dap/ds-aa-nga-flooding`, branch
  `feat/niger-benue-multistate-monitoring` (off `govt-2026-prep`), sha `1134cd0`.
  Derived data on blob under `ds-aa-nga-flooding/processed/config/`
  (`{lga,gauge}_registry.parquet`, `trigger_performance.parquet`,
  `trigger_year_detail.parquet`, `reforecast_skill.parquet`) — dev stage.
- **Status:** active, **draft**. A first end-to-end pass of the action-trigger
  derivation and monitoring app exists on the branch — none of it reviewed or
  approved; GloFAS readiness (Phase 3) deferred.
- **Open issues:**
  - **The entire derivation is unreviewed** — gauge selections, per-state
    RP/consensus configurations, and the uniform-frequency design choice all
    need technical review and working-group sign-off before being treated as
    candidate triggers.
  - All F1s rest on ~5–6 events per state; tuned consensus fractions range
    0.1–1.0 — real overfit risk at this sample size.
  - Edo and Niger are dam-regulated (Kainji/Jebba/Shiroro) with weak Google
    signal in the nationwide coverage screening (Niger median best-gauge r 0.15)
    — their tuned triggers hit the moderate tier but should be treated
    cautiously.
  - The 2015 and 2023 Floodscan flood years are missed by the endorsed Adamawa
    method and remain unexplained here (possible Lagdo-dam release timing /
    tributary pathways) — inherited, not resolved.
  - Nothing merged to `main` yet; monitoring is pre-operational (dev-stage blobs,
    feature-branch deploys).
