---
content_type: framework
framework: mmr-cyclones
version: development
status: development
valid_until: null
country_iso3: MMR
hazard: tropical-cyclone
admin_level: 1
geographic_scope: ["Rakhine"]
data_sources: [ECMWF, CMA, CHIRPS-GEFS, IBTrACS, IMERG, CODAB]
trigger_facets:
  basis: forecast
  calibration: absolute
  indicators: [ECMWF-wind-speed, CMA-wind-speed, CHIRPS-GEFS-3day-rainfall]
  n_windows: 2
  window_axes: []
monitoring_period:
  months: [4, 5, 6, 10, 11, 12]
  source: inferred
  note: "Bay of Bengal TC season — pre-monsoon (Apr–Jun) and post-monsoon (Oct–Dec) peaks; inferred from basin seasonality (Mocha was May 2023). Page does not state a season window."
supersedes: null
# --- funding & scope ---
prearranged_funding_usd: null
funding_by_source: {}
cofinancing_usd: null
cofinancing_sources: []
implementing_agencies: []
target_people: null
# --- documents, authority-ranked ---
framework_doc: null
framework_doc_date: null
framework_doc_annexes: []
languages: [en]
model_report: null
raw_extract: []
# --- live system ---
operated_by: null
apps: []
depends_on: [listmonk]
# --- source repo & reconciliation ---
source_repo: ocha-dap/ds-aa-mmr-cyclones
source_branch: main
source_sha: 284cf02
code_ref:
  - src/monitoring/wind_speed_monitoring_ecmwf.py
  - src/monitoring/wind_speed_monitoring_cma.py
  - src/monitoring/update_chirps_gefs.py
  - src/datasources/chirps_gefs.py
  - src/utils/constants.py
trigger_source: repo
repo_completeness: partial
discrepancies:
  - "[conflict] docs/index.qmd describes the wind trigger as a point-in-polygon check (storm predicted to pass through Rakhine ADM1), but the deployed monitoring code (wind_speed_monitoring_ecmwf.py, wind_speed_monitoring_cma.py) applies a distance-based wind reduction formula (0.9807 * exp(-0.003 * dist_km)) to tracks within a 500 km buffer, then checks if reduced wind >= 47 kt. These are substantially different trigger geometries."
  - "[conflict] docs/index.qmd and docs/cma-trigger-analysis.qmd describe two severity levels (L1 = 47 kt, L2 = 63 kt), but the deployed monitoring code only implements L1 (constants.wind_speed_alert_level = 47). The L2 = 63 kt threshold exists in analysis notebooks (notebooks/cma_forecasts.py, docs/cma-trigger-analysis.qmd) but is not present in the operational monitoring path."
  - "[stale] docs/cma-trigger-analysis.qmd uses simple point-in-polygon (gdf['within_rakhine'] = gdf.within(rakhine_geom)) without wind reduction, whereas the newer analysis notebook notebooks/cma_forecasts.py and the deployed monitoring both apply the distance-based wind reduction formula. The point-in-polygon Quarto chapter is the older/superseded analysis approach left in the repo; it is NOT the live trigger definition (which is distance-reduction) — read it as legacy retrospective analysis."
  - "[conflict] send_email.py checks for blobs with prefix 'wind' but the monitoring scripts produce files named wind_exceedance_{date}_{hour}_ecmwf.csv and wind_exceedance_{date}_{hour}_cma.csv — the email logic loads only the last blob matching 'wind', which may mix ECMWF and CMA exceedance events unpredictably."
  - "[gap] No published framework PDF found on ReliefWeb or unocha.org. The monitoring email disclaimer ('This email is purely informational and does not serve as an official notice for the anticipatory action framework. Official activation notices are sent in another email.') confirms an endorsed framework exists with separate official comms, but the document is not public."
  - "[gap] The CHIRPS-GEFS rainfall trigger threshold (175 mm 3-day rolling sum) appears only in constants.py; no return-period calibration or historical validation is documented in the repo. The rainfall_alert_level_observational = 250 mm is defined in constants but not used in any deployed monitoring script."
  - "[stale] historical_analysis/load_imerge_data.py references src/data/cerf_data.csv (loaded as df_cerf with CERF allocation amounts per storm_id), but this file is absent from the tracked repo (likely gitignored). The CERF allocation lookup is therefore unavailable."
  - "[stale] src/monitoring/__pycache__/rainfall_monitoring.cpython-311.pyc is committed to the repo, but no rainfall_monitoring.py source exists anywhere in the tree and nothing imports it. The deployed rainfall path is src/datasources/chirps_gefs.check_chirps_gefs_trigger driven by src/monitoring/update_chirps_gefs.py. The bytecode is an orphaned artifact of a removed/renamed module that should be gitignored; do not treat rainfall_monitoring as a live component."
  - "[stale] All monitoring scripts (wind_speed_monitoring_ecmwf.py, wind_speed_monitoring_cma.py, utils_windpseed.plot_storm_track) upload outputs with stage=\"dev\" to projects/ds-aa-mmr-cyclones/processed. The live monitoring pipeline therefore writes to and reads from the DEV blob slot, not prod — consistent with status: development, but means no prod-stage artifacts exist and a future promotion to prod is an outstanding change."
  - "[conflict] The deployed rainfall trigger (chirps_gefs.check_chirps_gefs_trigger) computes a 3-day rolling SUM of the Rakhine daily-mean precipitation (groupby(\"issue_date\")[\"mean\"].rolling(3).sum()) and compares it to rainfall_alert_level_forecast = 175 mm. Repo prose/README and the rainfall datasource naming (mmr_chirps_gefs_mean_daily) describe the indicator loosely as a rolling 'mean'/'average'; the operational statistic is a SUM of daily means, not a rolling mean. The mm value and the statistic must be read together (175 mm over 3 days, not a 175 mm daily average)."
# --- activation history ---
activations: []
# --- escape hatch ---
extra:
  doc_status: non-public
  monitoring_start: "2026-03-01"
  wind_reduction_formula: "wind_at_land = 0.9807 * exp(-0.003 * min_dist_km) * wind_knots"
  l2_threshold_kt: 63
  rainfall_threshold_forecast_mm3d: 175
  rainfall_threshold_observational_mm3d: 250
  action_window_hours: "48-72"
  readiness_window_hours: "72-120"
  aoi_state: "Rakhine (ADM1_PCODE MMR012)"
  historical_archive_cma: "2022-2025 Bay of Bengal TCs; Cyclone Mocha (May 2023) is only storm that would have triggered at L1 and L2 (first qualifying forecast 2023-05-13 08:00 UTC)"
  window_axes_note: "n_windows = 2 (wind alert, rainfall alert), but the two windows are NOT differentiated by the time/space/severity vocab: both cover Rakhine ADM1, both are forecast-basis, and neither filters by lead-time in deployment. They are independent triggers that differ by INDICATOR (wind vs rainfall), so window_axes is left []."
  schema_strain: "No published doc — framework_doc and framework_doc_date are null; trigger_source set to repo. Two-level (L1/L2) design partially implemented: only L1 is in deployed monitoring; L2 exists in analysis notebooks only. window_axes is [] despite 2 windows because the differentiator (indicator: wind vs rainfall) is not in the time/space/severity vocab."
visibility: internal
last_synced: "2026-06-18"
---

# Myanmar Tropical Cyclone — development

> The canonical trigger is the code at `code_ref`; this page explains it, it does not redefine it.

## Summary

Myanmar's cyclone anticipatory action framework targets Rakhine State (ADM1), the historically most-exposed part of the country to high-intensity Bay of Bengal tropical cyclones. The trigger combines a wind-speed forecast from ECMWF and/or CMA (checked against Rakhine after applying a distance-based reduction for overland tracks) with a CHIRPS-GEFS 16-day cumulative rainfall forecast. When either threshold is crossed, an alerting email is dispatched via Listmonk; official AA activation notices are sent through a separate channel. The monitoring pipeline has been live since 2026-03-01, running twice-daily GHA workflows. No public framework document has been located; the repo is the authoritative source for the current trigger design.

## Method

**Data flow:**

1. **ECMWF tracks** — fetched every 12 hours from ECMWF FTP as BUFR files via CLIMADA `TCForecast`. Tracks within a 2000 km buffer of Myanmar are retained. For each track point, minimum distance to Rakhine ADM1 is computed (projected to EPSG:32647). Wind speed is reduced by the formula `wind_at_land = 0.9807 × exp(−0.003 × dist_km) × wind_knots`. Ensemble members and deterministic track are both included.

2. **CMA tracks** — fetched from blob storage (`ds-cma-datasharing/cma_ftp/data_out/typhoon/`). Files are WMO WTPQ .TXT bulletins parsed into per-forecast-hour rows with position and wind speed in m/s (converted to knots: × 1.9438). Same distance-reduction and spatial filter pipeline as ECMWF.

3. **CHIRPS-GEFS rainfall** — daily 16-day forecast GeoTIFFs clipped to Rakhine ADM1; the spatial mean precipitation per valid day is taken, then a **3-day rolling sum** of those daily means is computed (`chirps_gefs.check_chirps_gefs_trigger`: `groupby("issue_date")["mean"].rolling(3).sum()`). Compared against the 175 mm threshold.

4. **Alerting** — `send_email.py` checks three blob prefixes (wind exceedance, rainfall exceedance, storm-in-area-of-interest monitoring) and dispatches an email via Listmonk. Separate official AA activation notices are sent through a different channel.

## Trigger logic

- **Keys off:** ECMWF and CMA tropical cyclone forecast tracks (wind speed); CHIRPS-GEFS precipitation forecasts.
- **Decision rule (plain language):** A cyclone alert fires if any forecast ensemble member or deterministic track from ECMWF or CMA predicts wind speeds at Rakhine (after reducing for storm distance from land) reaching at least 47 knots. A rainfall alert fires if the CHIRPS-GEFS 3-day rolling sum of the Rakhine ADM1 daily-mean precipitation reaches or exceeds 175 mm. Either condition independently triggers an alert email.
- **Activation structure:** Two independent alert conditions (wind OR rainfall), each producing a separate signal. The Listmonk email sends if any cyclone is in the monitoring area or if either threshold is exceeded.
- **Calibration:** Wind threshold of 47 kt maps to "Severe Cyclonic Storm" on the IMD scale (bins: > 47 kt). The 63 kt secondary threshold (L2) maps to "Very Severe Cyclonic Storm". Threshold selection basis is not documented in the repo. The CHIRPS-GEFS rainfall threshold of 175 mm (3-day) has no documented return-period calibration.
- **Authoritative source:** No published framework PDF; `trigger_source: repo`. The `docs/index.qmd` and `notebooks/cma_forecasts.py` document the analytical basis.
- **Operated by:** OCHA Centre for Humanitarian Data (pipeline runs via GHA in `ocha-dap/ds-aa-mmr-cyclones`).

## Trigger windows

The notebooks (`notebooks/cma_forecasts.py`) define an action window (48–72 h lead time) and readiness window (72–120 h lead time), but the deployed operational monitoring (`wind_speed_monitoring_ecmwf.py`, `wind_speed_monitoring_cma.py`) does **not** filter by lead time — it checks peak wind across all forecast hours. See discrepancies.

| window | basis | indicator | threshold | lead time | return period | releases |
|---|---|---|---|---|---|---|
| wind alert | forecast | "ECMWF-wind-speed, CMA-wind-speed (distance-reduced at Rakhine)" | >= 47 kt at Rakhine ADM1 | any (full forecast horizon) | not calibrated | monitoring email; official activation notice via separate channel |
| rainfall alert | forecast | "CHIRPS-GEFS-3day-rainfall (3-day rolling SUM of Rakhine ADM1 daily-mean precip)" | >= 175 mm 3-day rolling sum | 0–16 days | not calibrated | monitoring email |

## Sources & repo completeness

- **Trigger taken from:** `repo` — no published framework PDF was found on ReliefWeb or unocha.org. A non-public framework document likely exists (confirmed by email disclaimer language).
- **Repo completeness:** partial — the operational monitoring scripts implement L1 only; L2 (63 kt) and the action/readiness lead-time windows exist only in analysis notebooks; the rainfall threshold has no documented calibration; the historical CERF allocation data (cerf_data.csv) is absent.
- **Discrepancies:** see frontmatter. Key issues: (a) point-in-polygon vs distance-reduction mismatch between docs and deployed code; (b) L2 threshold not deployed; (c) lead-time windows not enforced in production monitoring.

## Monitoring

Monitoring runs via four GitHub Actions workflows in `ocha-dap/ds-aa-mmr-cyclones`:

- `run_update_ecmwf.yml` — twice daily (08:00, 20:00 UTC): downloads ECMWF BUFR tracks, filters to Myanmar region, applies wind reduction, uploads to blob.
- `run_update_cma.yml` — twice daily (08:00, 20:00 UTC): downloads CMA WTPQ bulletins from blob, applies same wind reduction pipeline, uploads to blob.
- `run_update_chirps_gefs.yml` — daily (08:50 UTC): downloads 16-day CHIRPS-GEFS GeoTIFFs, clips to Rakhine ADM1, computes 3-day rolling mean, checks threshold.
- `run_monitoring.yml` — twice daily (09:00, 20:15 UTC): checks all three threshold blobs; sends Listmonk email if any alert condition is active or a storm is in the area of interest.

A Slack bot (`slack_bot.yml`) posts daily status summaries to a Slack channel at 09:15 and 20:30 UTC. Processed outputs are written to Azure Blob under `projects/ds-aa-mmr-cyclones/processed/` (dev stage).

## Historical activations

Never activated (framework has been live since 2026-03-01; no CERF/AA activations recorded post-endorsement).

**Retrospective analysis:** Of 11 Bay of Bengal storms in the 2022–2025 CMA archive, only Cyclone Mocha (May 2023) would have triggered the framework at either threshold within Rakhine ADM1 (first qualifying forecast issued 2023-05-13 08:00 UTC). Major historical storms — Nargis (2008), Giri (2010), Mora (2017) — predate the CMA archive and require separate data sourcing for a full return-period estimate.

The `historical_analysis/` scripts also merge CERF allocation amounts by storm ID, indicating the original trigger was partly calibrated against historical CERF responses, but the methodology is not fully documented.

## Key decisions & rationale

- **Geographic scope (Rakhine only):** Rakhine State has the highest historical exposure to intense Bay of Bengal cyclones making landfall in Myanmar; ADM1-level scope avoids false positives from storms tracking through neighboring states.
- **Two forecast sources (ECMWF + CMA):** Running parallel monitoring against both ECMWF and CMA reduces the risk of a source outage silencing the trigger. CMA provides Bay of Bengal-focused subjective forecasts not available in ECMWF ensemble products.
- **Distance-based wind reduction:** The formula `0.9807 × exp(−0.003 × dist)` captures the rapid decrease in wind speed as a storm approaches land; applying it at each forecast point rather than only at landfall provides a more conservative (earlier) trigger.
- **Dual indicator (wind + rainfall):** Cyclone Mocha demonstrated that extreme rainfall can be severe even if wind speeds at Rakhine ADM1 are below the threshold; the CHIRPS-GEFS rainfall window supplements the wind trigger for slow-moving or rain-heavy systems.
- **Monitoring-only email vs official activation:** The Listmonk email system provides near-real-time situational awareness; the decision to trigger official AA action is made via a separate, manual process — reflecting the operational context in Myanmar (conflict-affected setting).

## Changes from previous version

First documented version; no prior version to compare against.

## Open questions / known issues

- What is the return period of the 47 kt and 175 mm thresholds? No calibration is documented.
- Is the L2 (63 kt) threshold intended to trigger a different response tier, or only for informational monitoring? It is not in the deployed pipeline.
- Should the monitoring filter by lead-time window (action: 48–72 h; readiness: 72–120 h) as coded in the analysis notebooks, or check the full forecast horizon as currently deployed?
- The rainfall_alert_level_observational = 250 mm is defined in constants but not consumed by any deployed script. What was the intended use?
- The `send_email.py` blob prefix check `wind` will match both `wind_exceedance_*_ecmwf.csv` and `wind_exceedance_*_cma.csv`; the last-sorted blob may mix sources. Should exceedances be merged or reported separately?
- Is there a return period for Cyclone Mocha as a calibration event? The 2022–2025 archive is too short for robust return-period estimation.
- No framework activation has occurred since monitoring began; is the framework still considered endorsed or is it in active development?
