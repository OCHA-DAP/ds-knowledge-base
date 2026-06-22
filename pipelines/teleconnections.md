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
  - "ERA5 precipitation (DB table public.era5, adm_level=0) — produced by the Databricks `Run ERA5` job (job_id 954457722530604); no dedicated ERA5 pipeline page exists in the KB yet"
source_repo: ocha-dap/ds-teleconnections
source_branch: feature/era5-ghpages
source_sha: 1d514d5
code_ref:
  - "teleconnection_survey.py — single-file analysis + report generation"
  - ".github/workflows/pages.yml — GH Pages deployment on push"
extra:
  run_mode: manual
  analysis_period: "1981-2025"
  countries_covered: 153
  climate_indices: ["nino34 (ENSO)", "dmi (IOD)", "tna", "tsa", "amm", "pdo"]
  lag_caps: ["l3 (3-month, default)", "l6 (6-month)"]
  correlation_methods: ["total (pairwise Pearson r)", "partial (residuals, holding other modes constant)"]
  rainy_season_filter: "trimester climatological mean >= 25% of annual mean (non-overlapping canonical trimesters)"
  significance_threshold: "p < 0.05 (two-tailed); |r| < 0.30 shown as grey (no signal)"
  not_in_deployments_registry: true
  discrepancies:
    - "[gap] The GH Pages deployment is not tracked in infrastructure/deployments.md — the 'GH Pages apps' section there lists only ds-aa-ner-drought and ds-storms-alerts and carries a TODO to inventory org Pages settings. teleconnections (served at ocha-dap.github.io/ds-teleconnections, from feature/era5-ghpages docs/) should be added when that inventory is built."
    - "[conflict] Deployed branch is NOT main. Production GH Pages serves the long-lived feature branch feature/era5-ghpages (the workflow only triggers on push to that branch); main is stale and does not publish. Anyone editing main will see no site change."
    - "[gap] Manual analysis vs scheduled publish: there is no scheduled run. The GH Pages workflow only re-publishes whatever is already committed under docs/. The correlation analysis is run by hand (uv run python teleconnection_survey.py) and the regenerated PNGs + index.html must be committed to feature/era5-ghpages before the site updates. A stale site means the artifacts in docs/ were never regenerated, not a workflow failure."
    - "[stale] Upstream dependency was mis-recorded as pipelines/imerg; this pipeline actually reads ERA5 (public.era5) produced by the Databricks Run ERA5 job. Corrected in depends_on. No ERA5 pipeline page exists in the KB yet."
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

## Downstream consumers

- **Framework teams** — use the live site (`https://ocha-dap.github.io/ds-teleconnections/`) to identify relevant climate modes and seasons for AA trigger design (ENSO, IOD signal by country). This is a manual reference product, not an automated data feed.
- **`ds-seas5-skill`** ([apps/seas5-skill](../apps/seas5-skill.md)) — shares the brown/blue drought-flood colour palette and global map viewport (visual consistency convention, not a data dependency).
- The `out/` parquet files are local/git-ignored; no downstream pipeline reads them automatically.
