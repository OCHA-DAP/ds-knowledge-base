---
content_type: pipeline
name: teleconnections
type: dataset-ingest
status: live
deployment:
  platform: github-actions
  resource_group: null
  jobs:
    - { name: "Deploy to GitHub Pages", ref: ".github/workflows/pages.yml", schedule: "push to feature/era5-ghpages", status: live }
inputs:
  - "DB table: public.era5 (adm_level=0, monthly country-level precipitation mm/day) via ocha-stratus prod"
  - "NOAA PSL Niño3.4 index: https://psl.noaa.gov/data/correlation/nina34.anom.data (HTTP, cached)"
  - "NOAA PSL IOD/DMI index: https://psl.noaa.gov/gcos_wgsp/Timeseries/Data/dmi.had.long.data (HTTP, cached)"
  - "NOAA PSL TNA index: https://psl.noaa.gov/data/correlation/tna.data (HTTP, cached)"
  - "NOAA PSL TSA index: https://psl.noaa.gov/data/correlation/tsa.data (HTTP, cached)"
  - "NOAA PSL AMM index: https://psl.noaa.gov/data/correlation/amm.data (HTTP, cached)"
  - "NOAA PSL PDO index: https://psl.noaa.gov/data/correlation/pdo.data (HTTP, cached)"
  - "Natural Earth 110m admin-0 GeoJSON (GitHub raw, cached locally as cache/naturalearth_admin0.geojson)"
  - "ERA5 monthly COGs on the prod raster blob (era5/monthly/processed/precip_reanalysis_v*.tif) — the survey's 0.25° pixel cache plus, for the deep dives, an appended extension of any months newer than the cache (cache/era5_pixel/monthly_ext.npy)"
  - "NOAA CPC ERSST v5 Niño3.4 (ersst5.nino.mth.91-20.ascii) — the PINNED analysis series for the deep dives (identical to the PSL series the survey was built on); PSL's live series (ERSST v6 since 2026, ~+0.2 °C) is fetched weekly for the current-ENSO-state line only"
  - "DB table: public.era5 (adm_level=1, monthly admin-1 means) via ocha-stratus prod — the deep dives' by-province section"
  - "CODAB admin-1 polygons via ocha_stratus.codab (FieldMaps) — deep dives"
  - "seas5-skill detrended per-pixel skill cube on the DEV blob (ds-seas5-skill/processed/raster/skill_stats_grid_detrended.nc, 1.2 GB; pearson_r, forecast_rp, flood_rp, forecast_percentile) — deep dives' skill and return-period panels, never recomputed"
  - "FEWS NET: ds-fewsnet-mirror public site JSON (classification/<ISO3>.json, units/<ISO3>.json) + unit geometry on the dev blob (ds-fewsnet-mirror/processed/units/<ISO3>.geojson) — deep dives' food-security section"
  - "DB tables: aa.cerf_allocation + aa.cerf_supplement (dev) — CERF drought allocations and their dated drought periods, deep dives' season table"
outputs:
  - "docs/index.html — self-contained HTML report (committed to repo, served via GH Pages)"
  - "docs/maps/map_{l3,l6}_{total,partial}_{index}.png — per-index choropleth maps (12 PNGs)"
  - "docs/maps/map_dominant_{l3,l6}.png — dominant climate mode maps"
  - "docs/maps/ts_{index}.png — index historical time-series panels (6 PNGs)"
  - "docs/maps/enso_elnino.png / enso_lanina.png — ENSO composite anomaly maps"
  - "docs/maps/index_corr_matrix.png — index collinearity heatmap"
  - "out/corr_{total,partial}_{l3,l6}.parquet — intermediate correlation tables (git-ignored, local only)"
  - "out/corr_display_{total,partial}_{l3,l6}.parquet — display-ready filtered correlation tables (git-ignored, local only)"
  - "GH Pages site: https://ocha-dap.github.io/ds-teleconnections/"
  - "docs/enso/index.html — ENSO country deep dives index (cards, one per country)"
  - "docs/enso/<slug>/index.html + PNGs — one deep dive per country (seasonal_cycle, zones_map, corr_maps, phase_history, composite_maps, adm1_maps, skill_issued, fews_maps, seasons, zone_history)"
  - "cache/ (git-ignored): era5_pixel/monthly_ext.npy + meta_ext.json, nino34.data (pinned v5) + nino34_latest.data, skill_stats_grid_detrended.nc, fews_*.json/.geojson, cerf_drought_<ISO3>.parquet, era5_adm1_<ISO3>.parquet, adm1_<ISO3>.parquet"
dependencies:
  - "ocha-stratus (prod DB engine for public.era5)"
  - "numpy, pandas, geopandas, scipy, matplotlib"
  - "requests (NOAA PSL index download)"
  - "uv (Python env management)"
  - "GitHub Pages (static hosting)"
downstream:
  - "Framework teams referencing ENSO/IOD/PDO teleconnections for trigger justification (manual consultation via the live GH Pages site; no automated data feed)"
  - "apps/seas5-skill (shares the brown/blue drought-flood colour palette + global map viewport convention; visual-consistency only, no automated data dependency)"
depends_on:
  - "public.era5"
  - "aa.cerf_allocation"
  - "aa.cerf_supplement"
  - "pipelines/fewsnet-mirror"
  - "apps/seas5-skill"
surfaces:
  - {url: "https://ocha-dap.github.io/ds-teleconnections/", kind: docs, title: "Teleconnections (ENSO/IOD/PDO) docs & maps (served from feature/era5-ghpages docs/)"}
  - {url: "https://ocha-dap.github.io/ds-teleconnections/survey/", kind: docs, title: "Global teleconnection survey (ERA5 × ENSO/IOD/TNA/TSA/AMM/PDO, country + pixel)"}
  - {url: "https://ocha-dap.github.io/ds-teleconnections/enso/", kind: docs, title: "ENSO country deep dives — index"}
  - {url: "https://ocha-dap.github.io/ds-teleconnections/enso/eri/", kind: analysis, title: "Eritrea ENSO deep dive (kiremti; regrade robust → moderate)"}
  - {url: "https://ocha-dap.github.io/ds-teleconnections/enso/mwi/", kind: analysis, title: "Malawi ENSO deep dive (late-season, southern-half signal; national DJF cancels)"}
  - {url: "https://ocha-dap.github.io/ds-teleconnections/enso/zwe/", kind: analysis, title: "Zimbabwe ENSO deep dive — how bad is 2026/27, how confident, how much El Niño (with CERF + FEWS NET season table)"}
source_repo: ocha-dap/ds-teleconnections
source_branch: feature/era5-ghpages
source_sha: 223fa7e
code_ref:
  - "teleconnection_survey.py — single-file analysis + report generation"
  - ".github/workflows/pages.yml — GH Pages deployment on push"
  - "enso_deep_dive.py — ENSO country deep-dive generator (figures/tables from the survey's ERA5 cache + the products above; HTML assembled from named blocks)"
  - "deep_dives/<slug>.toml — one per country: curated narrative, zones, section order, titles, which products to include"
extra:
  run_mode: manual
  analysis_period: "1981-2025 (survey); 1981-latest ERA5 month on blob (deep dives, via the cache extension)"
  deep_dives: ["eri (2026-09-03)", "mwi (2026-09-14)", "zwe (2026-09-16)"]
  deep_dive_method: "methods/enso-country-deep-dive.md"
  countries_covered: 153
  climate_indices: ["nino34 (ENSO)", "dmi (IOD)", "tna", "tsa", "amm", "pdo"]
  lag_caps: ["l3 (3-month, default)", "l6 (6-month)"]
  correlation_methods: ["total (pairwise Pearson r)", "partial (residuals, holding other modes constant)"]
  rainy_season_filter: "trimester climatological mean >= 25% of annual mean (non-overlapping canonical trimesters)"
  significance_threshold: "p < 0.05 (two-tailed); |r| < 0.30 shown as grey (no signal); |r| >= 0.5 = strong"
  correlation_bins: "House bins for r-vs-rainfall products: 0.30 moderate (~ the p<0.05 floor at 45 yrs; Cohen medium), 0.50 strong (Cohen large) - aligned Sep 2026 with the seas5-skill app's r_mod/r_high skill thresholds (previously 0.45 here)"
  not_in_deployments_registry: true
  discrepancies:
    - "[gap] The GH Pages deployment is not tracked in infrastructure/deployments.md — the 'GH Pages apps' section there lists only ds-aa-ner-drought and ds-storms-alerts and carries a TODO to inventory org Pages settings. teleconnections (served at ocha-dap.github.io/ds-teleconnections, from feature/era5-ghpages docs/) should be added when that inventory is built."
    - "[conflict] Deployed branch is NOT main. Production GH Pages serves the long-lived feature branch feature/era5-ghpages (the workflow only triggers on push to that branch); main is stale and does not publish. Anyone editing main will see no site change."
    - "[gap] Manual analysis vs scheduled publish: there is no scheduled run. The GH Pages workflow only re-publishes whatever is already committed under docs/. The correlation analysis is run by hand (uv run python teleconnection_survey.py) and the regenerated PNGs + index.html must be committed to feature/era5-ghpages before the site updates. A stale site means the artifacts in docs/ were never regenerated, not a workflow failure."
    - "[stale] Upstream dependency was mis-recorded as pipelines/imerg; this pipeline actually reads ERA5 (public.era5) produced by the Databricks Run ERA5 job. Corrected in depends_on to `public.era5` (the canonical DB-table node, produced by `raster-stats` from the `raster-pipelines` ERA5 COGs)."
  SCHEMA_STRAIN: "This is more of an analysis/app hybrid than a classic pipeline — it runs manually (not on a schedule), commits generated artifacts to the repo, and publishes a static site. The 'pipeline' type fits because it ingests ERA5 from DB and transforms it, but it has no recurring automated run."
visibility: internal
last_synced: "2026-06-22"
---

# Teleconnections

> Runbook. Optimize for "what feeds it, what it emits, and what to do when it breaks at 2am."

## One-liner

Manual run: query ERA5 country precip from DB + download six NOAA PSL climate indices → compute Pearson / partial correlation for every country × index × trimester × lag → render choropleth PNGs + self-contained HTML report → commit to repo → GH Pages publishes the live site.

## Jobs & schedule

| job | ref | schedule | status |
|---|---|---|---|
| Deploy to GitHub Pages | `.github/workflows/pages.yml` | push to `feature/era5-ghpages` | live |
| Run analysis (generate artifacts) | `teleconnection_survey.py` (manual) | on-demand | live |

The GH Pages workflow is purely a publisher — it deploys whatever is already in `docs/`. The actual correlation analysis is run manually with `uv run python teleconnection_survey.py`, and the generated PNGs + `index.html` are committed to the branch before pushing.

## Inputs

| Source | What | Path / access |
|---|---|---|
| ERA5 precipitation | Monthly country-level mean (mm/day), adm_level=0 | DB `public.era5` via `stratus.get_engine("prod")` |
| Niño3.4 | ENSO SST anomaly (5°N–5°S, 120–170°W) | NOAA PSL HTTP, cached at `cache/nino34.data` |
| IOD (DMI) | Indian Ocean Dipole Mode Index (HadISST) | NOAA PSL HTTP, cached at `cache/dmi.data` |
| TNA | Tropical North Atlantic SST anomaly | NOAA PSL HTTP, cached at `cache/tna.data` |
| TSA | Tropical South Atlantic SST anomaly | NOAA PSL HTTP, cached at `cache/tsa.data` |
| AMM | Atlantic Meridional Mode | NOAA PSL HTTP, cached at `cache/amm.data` |
| PDO | Pacific Decadal Oscillation | NOAA PSL HTTP, cached at `cache/pdo.data` |
| Boundaries | Natural Earth 110m admin-0 | GitHub raw → `cache/naturalearth_admin0.geojson` |

ERA5 data covers 153 countries at adm_level=0 for the period 1981–2025. Somaliland is merged into Somalia; Western Sahara is shown as its own entity.

## Steps

All logic is in `teleconnection_survey.py` (single file) driven by `main()`. The flow:

**load** six NOAA PSL indices (`load_indices`, cached) + ERA5 country precip from `public.era5` (`country_trimester_rainfall_era5`) → **filter** to rainy country-trimesters (`rainy_trimesters`, climatological-mean ≥ 25% of annual) → **correlate**: total Pearson lag-sweep (`sweep`) then partial-correlation pass holding other modes constant (`partial_pass`), each run at l3 and l6 lag caps, writing the `out/corr_*.parquet` tables → **filter for display** (`reduce_for_display`, p<0.05 & |r|≥0.30) → **render** choropleths, dominant-mode maps, ENSO composites, collinearity matrix, literature maps, and time-series panels into `docs/maps/` → **assemble** the self-contained `docs/index.html` (`generate_html_report`).

For the per-function detail (significance handling, PDO-excluded control set, suppressor exclusion, trimester wrapping) see the repo README "Methodology" section and the function docstrings in `teleconnection_survey.py` (`code_ref`).

## Outputs

Static site committed to the `feature/era5-ghpages` branch under `docs/`, served at **https://ocha-dap.github.io/ds-teleconnections/**.

```
docs/
  index.html                                   — self-contained HTML report (no external deps)
  maps/
    map_{l3,l6}_{total,partial}_{index}.png    — 24 per-index choropleth maps
    map_dominant_{l3,l6}.png                   — dominant mode maps (2)
    ts_{index}.png                             — index time-series panels (6)
    enso_elnino.png / enso_lanina.png          — ENSO composites
    index_corr_matrix.png                      — collinearity heatmap
    lit_enso_{elnino,lanina}.png               — literature ENSO impact maps

out/  (git-ignored; local only)
  corr_{total,partial}_{l3,l6}.parquet         — full sweep results
  corr_display_{total,partial}_{l3,l6}.parquet — filtered display tables
```

## Dependencies

| Dependency | Purpose |
|---|---|
| `ocha-stratus` | DB access (`stratus.get_engine("prod")`) for `public.era5` |
| `numpy`, `scipy` | Pearson + partial correlation computations |
| `pandas` | Data manipulation |
| `geopandas` | Vector geometry for choropleth rendering |
| `matplotlib` | Map and plot rendering |
| `requests` | NOAA PSL index HTTP download |
| `uv` | Python env management (Python 3.11+) |
| NOAA PSL | External data provider for all six climate indices (no auth required) |
| GitHub Pages | Static site hosting; deployment on push to `feature/era5-ghpages` |
| Azure / team DB credentials | Required in environment for `stratus.get_engine("prod")` |

Secrets needed: standard team Azure/DB credentials (same as any stratus-using project). No Databricks. No Listmonk.

## Failure modes & debugging

**NOAA PSL download fails** — the script will error at `load_indices`. Check connectivity to `psl.noaa.gov`. Cached files under `cache/` survive between runs; if the remote is down, the script can be patched to load from cache only. Files are plain text with a fixed NOAA format parsed by `_parse_psl`.

**DB query fails / auth error** — `stratus.get_engine("prod")` will throw. Ensure `PGSSLMODE=require` is set (Azure PostgreSQL requirement; see `infrastructure/database.md`) and that the team's Azure credentials are active. Check with `stratus` directly.

**Empty ERA5 results** — the query filters `adm_level = 0`; if the DB table has changed schema or the `public.era5` table is empty, `country_trimester_rainfall_era5` will return an empty DataFrame and all subsequent steps will silently produce maps with zero countries colored.

**GH Pages not updating** — the Pages workflow only deploys `docs/`; it does not rerun the analysis. If the site is stale, the PNGs and `index.html` in `docs/` are what's committed. Rerun the script, `git add docs/`, commit, and push to `feature/era5-ghpages`.

**Suppressor signal count inflated** — logged to stdout (`[l3] max_lag=3; suppressor-only partial signals excluded: N`). Suppressor-only signals (significant partial but not total) are excluded from the display. This is by design.

**Logs** — the script logs to stdout. No Databricks / Azure Monitor. If running locally, stdout is the only log. On GH Actions, the Pages deploy step logs are in the GitHub Actions UI under the `feature/era5-ghpages` branch.

**Not in deployments.md** — this pipeline is not in the Databricks or Azure registries; it runs entirely on GitHub Pages + manual local execution. The GH Pages deployment is not currently tracked in `infrastructure/deployments.md` (that section has a TODO stub for GH Pages).

## ENSO country deep dives (`/enso/`)

Since September 2026 the repo also publishes **per-country ENSO evidence reviews** under
`docs/enso/<slug>/`, one TOML of curated narrative per country
(`deep_dives/<slug>.toml`) plus figures and tables recomputed by `enso_deep_dive.py`. Build:
`PGSSLMODE=require PYTHONPATH=. uv run python enso_deep_dive.py [--only zwe]`; commit
`docs/enso/` and push `feature/era5-ghpages`. The method, the data each number comes from,
and the gotchas found on the way are on
**[methods/enso-country-deep-dive.md](../methods/enso-country-deep-dive.md)** — read that
before adding a country.

| Country | Question the page answers | Headline finding |
|---|---|---|
| [Eritrea](https://ocha-dap.github.io/ds-teleconnections/enso/eri/) | Is the catalogue's *robust* El Niño → drier JAS grade earned? | No — inherited from Ethiopia's kiremt row; ERA5 JAS r ≈ −0.41, strong only along the Tigray border, reversed on the coast in winter. Regrade to *moderate*, bidirectional. |
| [Malawi](https://ocha-dap.github.io/ds-teleconnections/enso/mwi/) | Right grade? Right season? | Grade holds, season is wrong: national DJF r ≈ 0 because the north (wetter under El Niño in NDJ) cancels the centre/south (drier in JFM–FMA). Southern Region: 7 of 10 El Niño JFM seasons in the driest third; 2023/24 hidden by a record-wet north. Sept SEAS5 skill low. |
| [Zimbabwe](https://ocha-dap.github.io/ds-teleconnections/enso/zwe/) | How bad is 2026/27, how confident are we, how much is El Niño? | Sept 2026 SEAS5: dry at 15–23-yr return periods, *moderate* skill for NDJ/DJF; 10 of 14 El Niño DJF seasons in the driest third, none wet; Niño3.4 +1.89 °C (Aug 2026); ENSO ≈ 46 % of DJF variance, uniform across provinces. Season-by-season table + figure with CERF drought allocations (timed vs the season) and FEWS NET pre-season / in-season / observed readings, 2006/07 onward. |

The deep dives read the team's precomputed products wherever one exists (SEAS5 skill and
return periods from the app's skill cube, ERA5 by province from `public.era5`, CERF from the
OneGMS mirror, FEWS NET from the mirror) and recompute only what no product holds (per-season
pixel correlations, ENSO-phase drought hit-rates) — see
[methods/reuse-published-stats.md](../methods/reuse-published-stats.md).

**Related products.** The [seas5-skill ENSO country slides](https://ocha-dap.github.io/ds-seas5-skill/enso/)
(two slides per country, all monitored countries) are the broad, automated view; the deep
dives are the narrow, curated one. The Niger HCT briefing deck
([ds-aa-ner-drought/hct-brief](https://ocha-dap.github.io/ds-aa-ner-drought/hct-brief/),
see [frameworks/ner-drought/2026-06-03](../frameworks/ner-drought/2026-06-03.md)) is the
same question asked for the Sahel season, built in the framework repo and reusing the
seas5-skill Niger slides.

## Downstream consumers

- **Framework teams** — use the live site (`https://ocha-dap.github.io/ds-teleconnections/`) to identify relevant climate modes and seasons for AA trigger design (ENSO, IOD signal by country), and the `/enso/` deep dives for the per-country evidence review. Manual reference products, not automated data feeds.
- **`ds-seas5-skill`** ([apps/seas5-skill](../apps/seas5-skill.md)) — shares the brown/blue drought-flood colour palette and global map viewport (visual consistency convention, not a data dependency).
- The `out/` parquet files are local/git-ignored; no downstream pipeline reads them automatically.
