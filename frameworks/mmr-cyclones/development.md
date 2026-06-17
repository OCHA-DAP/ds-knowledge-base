---
content_type: framework
framework: mmr-cyclones
version: cma-analysis   # development branch; no published framework PDF
status: development
country_iso3: MMR
hazard: tropical-cyclone
admin_level: 1
geographic_scope: [MMR012]   # Rakhine State ADM1
data_sources: [ECMWF-TC-forecast, CMA-BoB-forecast, CHIRPS-GEFS, IMERG, IBTrACS]
trigger_facets:
  basis: forecast
  calibration: absolute
  indicators: [ECMWF-TC-wind-speed-kt, CMA-wind-speed-kt, CHIRPS-GEFS-3day-rainfall-mm]
  n_windows: 2
  window_axes: [time]
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
source_branch: cma-analysis
source_sha: 446d675
code_ref:
  - src/utils/constants.py
  - src/monitoring/rainfall_monitoring.py
  - src/monitoring/update_chirps_gefs.py
  - src/datasources/chirps_gefs.py
  - src/monitoring/send_email.py
  - notebooks/cma_forecasts.py
  - docs/cma-trigger-analysis.qmd
trigger_source: repo
repo_completeness:
  analysis: partial
  deployed_code: partial
discrepancies:
  - "[conflict] The deployed wind monitor (src/monitoring/rainfall_monitoring.py, misleadingly named — it only does wind, not rainfall) applies no lead-time windowing: it flags any ensemble forecast position whose distance-reduced wind reaches constants.wind_speed_alert_level (47 kt) at any forecast hour. The analysis notebook (notebooks/cma_forecasts.py) instead defines two time-gated windows — Readiness (72–120 h) and Action (48–72 h). The deployed code is inconsistent with this intended multi-window design."
  - "[conflict] Two alert levels (L1=47 kt, L2=63 kt) exist only in the analysis layer (notebooks/cma_forecasts.py WIND_L1_KT/WIND_L2_KT, docs/cma-trigger-analysis.qmd, docs/index.qmd). The deployed monitor (rainfall_monitoring.py) has NO L2: constants.py defines only wind_speed_alert_level = 47 — there is no 63 kt constant. The live trigger is single-level (47 kt). The L1/L2 severity tiering is not yet implemented in deployed code."
  - "[conflict] The earlier Quarto analysis (docs/cma-trigger-analysis.qmd, line 69) uses a point-in-polygon check (gdf.within(rakhine_geom) — forecast position must fall inside the Rakhine ADM1 boundary) with the RAW wind speed (no distance reduction). The newer Marimo notebook (notebooks/cma_forecasts.py) and the deployed monitor instead apply a continuous distance-based wind reduction factor (0.9807 * exp(-0.003 * dist_km)) from each forecast point to the Rakhine boundary, not requiring the track to enter the polygon. These are two materially different spatial trigger designs; the qmd one is superseded by the distance-reduction approach."
  - "[conflict] The 3-day rolling forecast rainfall threshold of 175 mm (constants.rainfall_alert_level_forecast) lives in src/datasources/chirps_gefs.py (check_chirps_gefs_trigger, applied to rolling_sum_3), driven by src/monitoring/update_chirps_gefs.py — NOT in rainfall_monitoring.py (which is wind-only). send_email.py then ORs the wind-exceedance and rainfall blobs. So the live system is wind (47 kt) OR rainfall (175 mm); the page Method/Trigger-logic must attribute rainfall to chirps_gefs.py, not rainfall_monitoring.py."
  - "[stale] constants.rainfall_alert_level_observational = 250 (observational IMERG rainfall threshold) is defined but never referenced anywhere in the codebase (grep finds no usage). It is an aspirational/unused constant, not a live trigger — the deployed rainfall path uses only the 175 mm CHIRPS-GEFS forecast threshold. Do not present 250 mm as an active 'observed' threshold."
  - "[gap] No published framework PDF has been found. The framework has no endorsed document on ReliefWeb, OCHA publications, or CERF. All trigger parameters are repo-only. The framework is in development."
  - "[gap] The calibration basis for all thresholds (47 kt, 63 kt, 175 mm) is not documented in the repo. The IMD scale alignment (Severe Cyclonic Storm = 47 kt, Very Severe = 63 kt) is referenced in code comments but no formal calibration analysis against historical return periods or humanitarian outcomes is present."
  - "[gap] The wind reduction formula (0.9807 * exp(-0.003 * dist_km)), applied in notebooks/cma_forecasts.py and src/monitoring/rainfall_monitoring.py, is not referenced to any published source or calibration study in the repo."
  - "[stale] Monitoring outputs are written to the DEV blob slot (stage='dev') throughout: rainfall_monitoring.py uploads monitoring/wind_exceedance/storm_track_plot CSVs and PNGs with stage='dev', and send_email.py reads from the same dev container; the plot URL is hardcoded to ochatest.blob.core.windows.net. The pipeline is wired to the dev/test environment, not a production slot — consistent with development status, but flag before any go-live."
  - "[stale] src/datasources/zma.py defines ZMI polygon coordinates for Cuba (Caribbean) — legacy code from another project, unused anywhere in the Myanmar analysis."
  - "[stale] src/datasources/imerg.py contains load_imerg_recent() hardcoded with pcode='CU' (Cuba) — a leftover from a different project, unused in the Myanmar workflow."
  - "[stale] historical_analysis(ecmwf_hres path) src/datasources/ecmwf_hres.py uses a hardcoded bbox [92, 9, 101, 28] and MARS API calls with the ocha_stratus upload lines commented out. Not part of the live monitoring pipeline."
  - "[conflict] filter_myanmar_tracks() in rainfall_monitoring.py has a function default of buffer_km=200, but main() invokes it with buffer_km=2000, while constants.buffer_km=500 is separately used to filter close_storms by min_dist_km. Three different buffer distances (200 default / 2000 track-filter / 500 close-storm) coexist; the intended operational buffer is ambiguous."
# --- activation history ---
activations: []
# --- escape hatch ---
extra:
  schema_strain: "No published framework PDF exists; trigger_source=repo, status=development, version=cma-analysis (the active branch). All authority derives from the active branch. The framework defines two lead-time windows in analysis notebooks but the deployed monitoring code does not enforce lead-time windowing — this is the primary unresolved design question."
  imd_scale_reference: "L1 threshold (47 kt) = Severe Cyclonic Storm on the India Meteorological Department scale. L2 threshold (63 kt) = Very Severe Cyclonic Storm."
  cma_data_source: "CMA Bay of Bengal TC historical forecast archive 2022-2025 (blob: ds-cma-datasharing/processed/2022-2025_BoB_TC.parquet) is used for retrospective analysis. ECMWF ensemble tracks (storms.ecmwf_tracks_geo DB table) are also compared."
  monitoring_cadence: "Three GHA workflows run daily: run_update_ecmwf.yml (08:00 and 20:00 UTC), run_update_chirps_gefs.yml (08:50 UTC), run_monitoring.yml / send_email (09:00 and 20:15 UTC). Monitoring season starts 2026-03-01."
  mocha_backtest: "In the 2022-2025 CMA archive, only Cyclone Mocha (May 2023) would have triggered at both L1 and L2 within Rakhine — first qualifying CMA forecast issued 2023-05-13 08:00 UTC. Framework was not operational at that time."
visibility: internal
last_synced: "2026-06-17"
---

# Myanmar Tropical Cyclone — development

> The canonical trigger is the code at `code_ref`; this page explains it, it does not redefine it.
> No published framework PDF has been found. All trigger parameters derive from the active repo branch.

## Summary

This anticipatory action framework targets Rakhine State (ADM1 PCODE MMR012), the coastal area of Myanmar historically most exposed to high-intensity Bay of Bengal tropical cyclones. It triggers on ECMWF or CMA ensemble track forecasts of sustained wind speed reaching predefined thresholds at Rakhine — with a secondary rainfall indicator from CHIRPS-GEFS. A live monitoring pipeline runs daily during the cyclone season (approximately March–November) and sends email alerts via Listmonk when either indicator exceeds its threshold. The framework defines two alert levels aligned with the IMD tropical cyclone intensity scale: L1 (≥ 47 kt, Severe Cyclonic Storm) and L2 (≥ 63 kt, Very Severe Cyclonic Storm). As of mid-2026, no framework PDF has been published and no formal endorsement has been confirmed; the framework is under active development.

## Method

Data flows:

1. **Wind (ECMWF tracks):** ECMWF ensemble TC track forecasts are fetched twice daily via CLIMADA-Petals `TCForecast`. For each ensemble member, the maximum sustained wind at each track point is converted from m/s to knots and adjusted to 3m height (×1.05, WMO convention). A distance-based wind reduction factor (`0.9807 × exp(−0.003 × dist_km)`) is applied, where `dist_km` is the shortest distance from the forecast track point to the Rakhine ADM1 boundary (projected to UTM zone 47N). Track members whose reduced wind at any forecast position reaches ≥ 47 kt are flagged as exceeding the L1 alert level; ≥ 63 kt is L2.

2. **Rainfall forecast (CHIRPS-GEFS):** `src/monitoring/update_chirps_gefs.py` downloads daily precipitation rasters for Rakhine from CHIRPS-GEFS (16-day lead time product, UCSB) and `src/datasources/chirps_gefs.py` computes the mean over the ADM1 boundary, a 3-day rolling sum (`rolling_sum_3`), and `check_chirps_gefs_trigger()` flags rows where the rolling sum ≥ 175 mm (`rainfall_alert_level_forecast`). This rainfall logic is entirely separate from the wind monitor (`rainfall_monitoring.py`, which despite its name only does wind).

3. **Decision / notification:** The `send_email.py` script checks blob storage for today's wind-exceedance and rainfall files (both written to the `dev` slot), then ORs them: if either is present it sends a trigger email via Listmonk; if a cyclone is merely present in the area of interest (within `constants.buffer_km` = 500 km) but no threshold is met, a monitoring (watch) email is sent instead.

The retrospective analysis (Marimo notebook `notebooks/cma_forecasts.py`) refines the trigger design by splitting forecasts into two time-gated windows — Readiness (72–120 h) and Action (48–72 h) — and comparing CMA and ECMWF forecast performance against IBTrACS observations for 2022–2025 Bay of Bengal storms. This two-window design has not yet been ported to the deployed monitoring code.

## Trigger logic

- **Keys off:** ECMWF ensemble TC track forecasts (wind speed, reduced at Rakhine) and CHIRPS-GEFS 16-day rainfall forecast (3-day rolling sum over Rakhine ADM1).
- **Decision rule (plain language):** As deployed: for each forecast cycle, if any ensemble member's distance-reduced wind speed at/near Rakhine ADM1 reaches the single 47 kt threshold (`constants.wind_speed_alert_level`), a wind exceedance is written. Separately, if the 3-day rolling sum of CHIRPS-GEFS forecast rainfall over Rakhine reaches 175 mm, a rainfall exceedance is written. `send_email.py` ORs the two: either alone triggers an alert email. If a cyclone is present in the area of interest (tracks filtered to within 2000 km, then close storms kept within `constants.buffer_km` = 500 km) but no threshold is met, a watch email is sent. The L2 (63 kt) level exists only in the analysis notebook, not in deployed code.
- **Activation structure:** Deployed: a single wind level (47 kt) OR a single rainfall level (175 mm), with no lead-time windowing. Intended (analysis notebook only): two alert levels (L1=47 kt, L2=63 kt) across two time windows — Readiness (72–120 h) and Action (48–72 h). The deployed code does not enforce the windows or the L2 tier.
- **Calibration:** The 47 kt and 63 kt thresholds align with the IMD tropical cyclone intensity classification (Severe Cyclonic Storm and Very Severe Cyclonic Storm respectively). No formal return-period calibration or quantitative humanitarian impact study has been found in the repo. The 175 mm forecast rainfall threshold is present in constants.py without documented derivation; the 250 mm observational threshold is defined but unused.
- **Authoritative source:** The active `cma-analysis` branch of the repo (`code_ref`), as no published framework PDF exists.
- **Operated by:** OCHA/CHD (monitoring pipeline runs via GitHub Actions on the `ocha-dap/ds-aa-mmr-cyclones` repo). Email delivery via Listmonk.

## Trigger windows

| window | basis | indicator | threshold | lead time | return period | releases |
|---|---|---|---|---|---|---|
| Readiness | forecast | ECMWF/CMA wind speed (distance-reduced at Rakhine) | L1 ≥ 47 kt or L2 ≥ 63 kt (analysis only) | 72–120 h | not calibrated | Readiness/early actions (not yet defined) |
| Action | forecast | ECMWF/CMA wind speed (distance-reduced at Rakhine); CHIRPS-GEFS 3-day rolling rainfall | Wind: L1 ≥ 47 kt or L2 ≥ 63 kt (analysis); Rainfall: 3-day rolling sum ≥ 175 mm forecast | 48–72 h (wind); up to 16 days (rainfall) | not calibrated | Full activation actions (not yet defined) |

**Note on windows:** The two-window (Readiness / Action) structure exists only in the analysis notebook (`notebooks/cma_forecasts.py`); it has NOT been implemented in the deployed pipeline. Deployed monitoring fires on any forecast hour exceeding the single deployed wind threshold (47 kt, no L2) — `n_windows: 2` reflects the *intended analysis design*, which is what this development page documents.

**Note on rainfall:** The 175 mm CHIRPS-GEFS forecast threshold lives in `src/datasources/chirps_gefs.py` (not in the wind monitor). In the deployed system, `send_email.py` simply ORs the wind-exceedance and rainfall blobs across the whole season — rainfall is not actually gated to the Action window. The 250 mm observational (IMERG) threshold in `constants.py` is defined but unused; it is not a live trigger and is omitted here.

## Sources & repo completeness

- **Trigger taken from:** `repo` — no framework PDF exists. The `cma-analysis` branch is authoritative.
- **Repo completeness:** partial — The historical IBTrACS analysis and CMA/ECMWF retrospective analysis are present. A live monitoring pipeline (wind + rainfall, daily) is deployed. However: (a) the two-window design from the notebooks is not reflected in deployed code; (b) threshold calibration documentation is absent; (c) the repo contains substantial legacy code from other projects (Cuba/Caribbean references); (d) results/ directory is empty — outputs are not committed.
- **Discrepancies:** See frontmatter `discrepancies` list. Most critical: the deployed monitoring code is inconsistent with the intended multi-window design. The point-in-polygon vs distance-reduction spatial approach is unresolved between the two analysis documents.

## Monitoring

The monitoring pipeline runs via three GitHub Actions workflows:

- `run_update_ecmwf.yml`: downloads ECMWF TC forecast tracks twice daily (08:00 and 20:00 UTC), filters for storms within 2000 km of Myanmar, computes wind reduction, and uploads track and wind exceedance CSVs to blob storage.
- `run_update_chirps_gefs.yml`: downloads and processes CHIRPS-GEFS 16-day rainfall forecasts daily (08:50 UTC) for Rakhine ADM1.
- `run_monitoring.yml` / `send_email.py`: checks blob for threshold exceedances and sends alert or watch emails via Listmonk twice daily (09:00 and 20:15 UTC).
- `slack_bot.yml`: posts daily workflow status and active alerts to a Slack channel.

Monitoring season is currently hardcoded to start 2026-03-01. There is no automatic end-of-season cutoff in the code. Alert emails are sent to a Listmonk list; the specific list ID is loaded from environment variables.

## Historical activations

Never activated. The framework has not reached endorsement and no real anticipatory action activation has occurred.

**Retrospective backtest finding:** In the 2022–2025 CMA Bay of Bengal forecast archive (11 storms), only Cyclone Mocha (May 2023) would have triggered at both L1 and L2. The first qualifying CMA forecast was issued 2023-05-13 08:00 UTC. Cyclone Mocha made landfall in Rakhine on 2023-05-14 and was the most destructive cyclone in Myanmar's recorded history. Several other intense storms (ASANI at 64 kt global peak, HAMOON at 68 kt) tracked toward Bangladesh or India and were never forecast to enter Rakhine.

## Key decisions & rationale

- **Focus on Rakhine ADM1 (MMR012):** Rakhine is the primary Bay of Bengal landfall risk zone for Myanmar, with historical major cyclone landfalls (Nargis 2008, Giri 2010, Mora 2017, Mocha 2023).
- **Distance-based wind reduction:** The factor `0.9807 × exp(−0.003 × dist_km)` reduces open-ocean track wind speeds to expected near-land values. This allows triggering based on forecast positions that are close to but not yet inside Rakhine, providing earlier lead time. The formula is not traced to a published source in the repo.
- **CMA as analysis data source:** CMA's Bay of Bengal TC forecast archive provides 2022–2025 historical data for retrospective analysis. ECMWF ensemble tracks are used operationally. The Marimo notebook compares both sources against IBTrACS observations.
- **Two alert levels (L1/L2) linked to IMD scale:** The 47 kt (Severe Cyclonic Storm) and 63 kt (Very Severe Cyclonic Storm) thresholds align with established IMD intensity categories, making the trigger interpretable to regional meteorological agencies.
- **Rainfall as secondary indicator:** Given that cyclone-related rainfall can cause significant damage even when wind intensity is below the highest threshold, the framework includes a forecast rainfall trigger from CHIRPS-GEFS (175 mm 3-day rolling sum, in `src/datasources/chirps_gefs.py`). An IMERG observational counterpart (250 mm constant) is sketched in `constants.py` but is not wired into any code path yet.

## Changes from previous version

No previous version. This is the first iteration of the Myanmar cyclone anticipatory action framework.

## Open questions / known issues

- **Two-window design vs deployed code:** The readiness/action time-gated windows are defined in the analysis notebook but not in the monitoring pipeline. When will the deployed code be updated to reflect the intended design?
- **Calibration:** What are the return periods for the 47 kt and 63 kt wind thresholds at Rakhine? The IBTrACS analysis script (`historical_analysis/load_ibtracs_data.py`) computes return periods but outputs are not in the repo.
- **Rainfall threshold derivation:** The 175 mm forecast threshold lacks documented calibration (the 250 mm observational constant is unused). What humanitarian impact study or return-period analysis underlies these values, and will the IMERG observational path be wired up?
- **Wind reduction formula source:** The `0.9807 × exp(−0.003 × dist_km)` formula appears in multiple files but is not referenced to any publication.
- **Endorsement path:** When is endorsement planned? No framework PDF or CERF pre-arrangement has been found.
- **Season definition:** Monitoring hardcodes a March 2026 start date. A systematic season definition (month range) and end-of-season logic is missing.
- **Legacy code:** `src/datasources/zma.py` (Cuba ZMI polygon) and Cuba-referencing `imerg.py` function should be cleaned up.
- **Results not committed:** The `results/` directory is empty (.gitkeep only). Analysis outputs are not reproducible from the repo alone.
