---
content_type: framework
framework: mmr-cyclones
version: development
status: development
valid_until: null
country_iso3: MMR
hazard: tropical-cyclone
admin_level: 3
geographic_scope: ["Rakhine State — AA Target area: 10 townships (ADM3: Buthidaung, Kyauktaw, Maungdaw, Mrauk-U, Pauktaw, Ponnagyun, Rathedaung, Sittwe, Minbya, Myebon); rest of Rakhine monitored for wind only"]
data_sources: [ECMWF, CMA, CHIRPS-GEFS, IBTrACS, IMERG, CODAB]
trigger_facets:
  basis: forecast
  calibration: absolute
  indicators: [ECMWF-wind-speed, CMA-wind-speed, CHIRPS-GEFS-3day-rainfall]
  n_windows: 2
  window_axes: []
monitoring_period:
  months: [4, 5, 6, 7, 8, 9, 10, 11, 12]
  source: inferred
  note: "Bay of Bengal TC season, Apr–Dec, with pre-monsoon (Apr–Jun) and post-monsoon (Oct–Dec) intensity peaks; no doc exists to state a season, so inferred. Jul–Sep is INCLUDED deliberately: the framework's own would-have-triggered set contains Komen (July 2015, via the rainfall condition), so a monsoon-season month can fire. In practice the GHA schedules run every day of the year with no seasonal cron gating and no MONITORING_START_DATE check (see extra.monitoring_start_note), so this is a hazard-season judgment, not an enforced monitoring window. The only code-level seasonal bounds are in the CHIRPS-GEFS step: the download range starts at the fixed date CHIRPS_GEFS_START_DATE = 2026-03-15 (never restarts per year), while the processing range starts each year on ~25 March (process_recent_chirps_gefs, start=f\"{date.year}-03-25\") — see discrepancies."
supersedes: null
# --- funding & scope ---
all_in: true   # development-stage: no pre-arranged envelope, so no split-budget case; default true
prearranged_funding_usd: null
funding_by_source: {}
funding_by_sector: {}
funding_by_agency: {}
funding_rows: []
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
surfaces: []
depends_on: [listmonk]
# --- source repo & reconciliation ---
source_repo: ocha-dap/ds-aa-mmr-cyclones
source_branch: main
source_sha: "8c09720"
code_ref:
  - src/monitoring/wind_speed_monitoring_ecmwf.py
  - src/monitoring/wind_speed_monitoring_cma.py
  - src/utils/utils_cma.py
  - src/utils/utils_windpseed.py
  - src/monitoring/update_chirps_gefs.py
  - src/datasources/chirps_gefs.py
  - src/datasources/codab.py
  - src/monitoring/send_email.py
  - src/utils/storm_names.py
  - src/utils/constants.py
trigger_source: repo
repo_completeness: partial
discrepancies:
  - "[gap] No published framework PDF found on ReliefWeb or unocha.org, and no PDF text extract was available for this re-ingestion — this page is drafted from the repo and the prior page only. The monitoring email disclaimer ('This email is purely informational and does not serve as an official notice for the anticipatory action framework. Official activation notices are sent in another email.') implies an endorsed framework with separate official comms, but the document is not public."
  - "[gap] The 47 kt wind threshold and the CHIRPS-GEFS 175 mm 3-day rolling-sum threshold (constants.wind_speed_alert_level, constants.rainfall_alert_level_forecast) have no documented selection basis or return-period calibration in the repo. 47 kt is the IMD Cyclonic Storm / Severe Cyclonic Storm bin edge (src/datasources/ibtracs.py categorize_storms), but nothing says that is why it was chosen."
  - "[gap] No 63 kt 'L2' severity TRIGGER exists anywhere in the repo (re-confirmed at 8c09720): constants.py defines only wind_speed_alert_level = 47. 63 survives only as the Very Severe Cyclonic Storm bin edge in the IMD intensity table (src/datasources/ibtracs.py categorize_storms, duplicated in src/utils/utils_plot.py) — plausibly what an earlier ingestion recorded as 'L2'. Flag for the framework team."
  - "[gap] Dead configuration: constants.rainfall_alert_level_observational = 250, MIN_EMAIL_DISTANCE = 1000, MONITORING_START_DATE, NUMERIC_NAME_REGEX and _parse_bool_env are defined in constants.py but referenced by no other file (re-verified by grep at 8c09720). Not live checks."
  - "[conflict] The rainfall statistic is a 3-day rolling SUM of the AA-Target-area daily-mean precipitation (chirps_gefs.check_chirps_gefs_trigger: df['mean'].rolling(3, min_periods=1).sum() >= 175, applied to the latest issue date only), not a 3-day average, despite the 'mean_daily' blob name. Read the mm value and the statistic together. Note min_periods=1 means the first one or two valid days are partial sums (can only under-count, never spuriously fire)."
  - "[conflict] The two halves of the CHIRPS-GEFS step still disagree on season start: download_recent_chirps_gefs uses the fixed module constant CHIRPS_GEFS_START_DATE = date(2026, 3, 15) (no year-relative reset; incomplete issue dates since then are re-checked every run, newest first, capped by DEFAULT_MAX_ISSUE_DATES = 3 per run), while process_recent_chirps_gefs uses f\"{date.year}-03-25\". Improved since b8d84e2 (the literal is now a named constant and the download is capped/availability-checked via server directory listings) but the 15-vs-25 March mismatch and 2026-fixed start remain: from 2027 the download will keep reaching back to March 2026."
  - "[gap] wind_speed_monitoring_cma.download_tracks_cma has no retry/backoff decorator, unlike wind_speed_monitoring_ecmwf.download_tracks_ecmwf (tenacity; TimeoutError/OSError). Not documented as intentional (CMA data is read from blob storage, which may make retries less necessary)."
  - "[stale] historical_analysis/load_imerge_data.py reads src/data/cerf_data.csv and src/data/emdat_mmr.csv, which are absent from the tracked repo (src/data holds only emdat_all.parquet and storms_date.pickle). The CERF-allocation and impact joins in the historical comparison cannot be reproduced from the repo alone."
  - "[stale] All monitoring and plot outputs land in the DEV blob slot (projects/ds-aa-mmr-cyclones/processed): wind monitoring and plot uploads pass stage=\"dev\" explicitly; CHIRPS-GEFS writes pass no stage and rely on ocha_stratus defaulting to dev. Consistent with status: development; no prod-stage artifacts exist and promotion to prod is outstanding."
  - "[stale] src/datasources/zma.py (load_zma, Cuba ZMI coordinates) and src/datasources/imerg.py:load_imerg_recent (queries public.imerg WHERE pcode = 'CU') are unused Cuba-specific leftovers, referenced by no Myanmar trigger/monitoring script."
  - "[gap] Historical hindcast scripts historical_analysis/load_ecmwf_data.py (line 70) and load_cma_data.py (line 56) call run_trigger(..., windspeed_column=\"wind_speed_at_land_forecasted\") but src/utils/utils_fun.py:165 declares the parameter as wind_speed_column — a TypeError before either script writes its results. The ECMWF/CMA hindcast retrospective quoted under Historical activations predates this and is not reproducible at 8c09720 without a one-word fix."
  - "[conflict] AREA SCOPE CHANGED vs the prior page: the trigger area is no longer all of Rakhine ADM1. constants.adm_level is now 3 and the wind distance/reduction and the CHIRPS-GEFS spatial mean are computed over the AA Target area (constants.ADM3_LIST, 10 townships; codab.load_aa_target_and_rest_areas), with the remainder of Rakhine ('Rest of Rakhine') tracked separately for wind only. The prior page described Rakhine ADM1 (MMR012) and ADM1 daily-mean rainfall; those statements are superseded. Whether this was a deliberate framework design change or a repo-side refinement cannot be determined without the framework document."
  - "[gap] send_email.main concatenates ALL wind exceedance frames (AA Target area and Rest of Rakhine, ECMWF and CMA) into df_wind_speed, so an exceedance confined to the Rest-of-Rakhine area alone sends a trigger-labelled email (wind_speed_threshold_reached = REACHED) even though that area is outside the AA Target area. The threshold table shows the areas separately, but the campaign choice does not. Unclear whether rest-of-Rakhine exceedance is meant to count as a trigger or only as information."
# --- activation history ---
activations: []
# --- escape hatch ---
extra:
  doc_status: non-public
  monitoring_start: "2026-03-01"
  monitoring_start_note: "constants.MONITORING_START_DATE (Asia/Yangon-localised) is defined but read by no other file in src/ — not an enforced gate on the live workflows, which run unconditionally on the GHA cron schedule. Treat 2026-03-01 as an approximate pipeline-live date; the CHIRPS-GEFS download actually starts 2026-03-15."
  wind_reduction_formula: "wind_at_land = 0.9807 * exp(-0.003 * min_dist_km) * wind_knots, where wind_knots = 1.05 * (raw_wind_ms * 1.9438444924) — m/s to knots, then 10-min → 3-min sustained convention (x1.05), BEFORE the distance reduction (src/utils/utils_windpseed.py compute_wind_speed_at_land). min_dist_km is the distance from the track point to the nearest AA Target-area township polygon (compute_wind_speed_at_adm_list), not to the whole country."
  rainfall_threshold_forecast_mm3d: 175
  rainfall_threshold_observational_mm3d: 250   # defined in constants.py, never used
  chirps_gefs_versions: "CHIRPS-GEFS v12 (CHC EWX daily_16day) for issue dates before 2026-07-01, v3 (CHIRPS-GEFS/v3/daily/global) from 2026-07-01 (chirps_gefs._source_for); 16 lead-time days (constants.chirps_gefs_lead_time)."
  action_window_hours: "48-72"
  readiness_window_hours: "72-120"
  trigger_phase_email_logic: "send_email.determine_trigger_phase labels the alert email readiness (72-120 h) / action (48-72 h) / observational (<48 h) / None (>120 h) from the median, across ensemble members, of each member's closest-approach time (falling back to CHIRPS-GEFS valid-minus-issue lead time if no cyclone monitoring data; 'observational' if neither). It labels the email only — it does not gate which forecasts count toward the wind/rainfall threshold checks, which scan the full forecast horizon."
  unnamed_storm_filter: "storm_names.drop_unnamed_storms drops rows whose sid/storm_name matches ^\\d{2}[A-Za-z]$ (e.g. 70B, 71W). Applied PER ROW when loading wind exceedance blobs (check_wind_speed_trigger_data) and monitoring blobs (check_cyclone_presence) — a per-row filter now, no longer the all-or-nothing gate of earlier versions."
  aoi_area: "AA Target area = union of the 10 ADM3_LIST townships; 'Rest of Rakhine' = ADM1_LIST (Rakhine) minus that area. Storm-in-area-of-interest monitoring = a track member whose min_dist_km to the AA Target area is <= constants.buffer_km (500)."
  historical_archive_cma: "2022-2025 Bay of Bengal TCs; Cyclone Mocha (May 2023) is the only storm that would have triggered at the wind threshold (first qualifying forecast 2023-05-13 08:00 UTC; evaluated against Rakhine ADM1 in the prior analysis, not re-derived for the ADM3 target area)."
  window_axes_note: "n_windows = 2 (wind alert, rainfall alert), but the windows are not differentiated by the time/space/severity vocab: both forecast-basis, same AA Target area, neither filters by lead time in the threshold itself. They differ by INDICATOR, so window_axes is []."
  schema_strain: "No published doc — framework_doc and framework_doc_date are null; trigger_source set to repo; no PDF text extract available. window_axes is [] despite 2 windows because the differentiator (indicator: wind vs rainfall) is not in the time/space/severity vocab. Old `apps: []` key replaced by `surfaces: []` (D102)."
visibility: internal
last_synced: "2026-10-20"
---

# Myanmar Tropical Cyclone — development

> The canonical trigger is the code at `code_ref`; this page explains it, it does not redefine it.

## Summary

Myanmar's cyclone anticipatory action framework targets a 10-township **AA Target area in Rakhine State** (ADM3: Buthidaung, Kyauktaw, Maungdaw, Mrauk-U, Pauktaw, Ponnagyun, Rathedaung, Sittwe, Minbya, Myebon), part of Myanmar historically most exposed to high-intensity Bay of Bengal cyclones. The trigger combines a wind-speed forecast from ECMWF and/or CMA (reduced for distance to the target-area townships) with a CHIRPS-GEFS 3-day cumulative rainfall forecast. When either threshold is crossed, an alert email is dispatched via Listmonk, labelled by trigger phase (readiness / action / observational) from forecast lead time; official AA activation notices go through a separate channel. Wind is also assessed for the "Rest of Rakhine" and reported separately. The monitoring pipeline has been live since about 2026-03-01 on daily/twice-daily GHA workflows, writing to the DEV blob slot. No public framework document has been located — **no PDF extract was available for this re-ingestion**, so the page is verified against the repo at `source_sha` 8c09720 and the prior page only.

## Method

1. **ECMWF tracks** — fetched every 12 h from ECMWF FTP as BUFR via CLIMADA `TCForecast` (tenacity retry, 3 attempts with exponential backoff on `TimeoutError`/`OSError`; a `climada_petals` `UnboundLocalError` on failed connection is re-raised as `OSError` so the retry engages). Tracks within a 2000 km buffer of Myanmar are kept; ensemble members and the deterministic track are included.
2. **CMA tracks** — WMO WTPQ `.TXT` bulletins read from blob storage (`ds-cma-datasharing/cma_ftp/data_out/typhoon/`), parsed by `src/utils/utils_cma.py` (single deterministic member, `ensemble_number = 0`), then run through the same shared pipeline (`utils_windpseed.py`).
3. **Area-specific wind reduction** — `compute_wind_speed_at_adm_list` computes, for every track point, the distance to the **AA Target-area townships** and `wind_at_land = 0.9807 × exp(−0.003 × dist_km) × wind_knots` (knots, 3-min convention). It also keeps a country-wide value and records the nearest ADM3 where the country-wide value reaches 47 kt. The same function is run a second time against the Rest-of-Rakhine townships (`codab.rest_of_rakhine_townships`) to give `wind_speed_at_land_rest`.
4. **Wind exceedance** — `get_wind_exceedance` keeps each `sid`/ensemble member whose maximum reduced wind is ≥ 47 kt, written to blob as `wind_exceedance_adm3_{date}_{hour}_{source}.csv` (target area) and `wind_exceedance_rest_…` (rest of Rakhine). Members within 500 km (`buffer_km`) of the target area are also written as `monitoring_{date}_{hour}_{source}.csv` and plotted.
5. **CHIRPS-GEFS rainfall** — 16-day daily forecast GeoTIFFs (v12 before 2026-07-01, v3 after) are downloaded newest-first (≤3 incomplete issue dates per run), clipped to the AA Target-area polygon, spatially averaged per valid day (`mmr_chirps_gefs_mean_daily_aa_target.parquet`), then the **latest issue date only** gets a 3-day rolling SUM compared with 175 mm (`check_chirps_gefs_trigger` → `rainfall_exceedance_{date}.csv`).
6. **Alerting** — `send_email.py` reads today's blobs, drops unnamed-storm ids per row, builds a per-area/per-source **threshold table** (wind ECMWF/CMA × AA Target/Rest of Rakhine; rainfall for the target area only, "Not assessed" for the rest), computes the trigger **phase**, and creates a Listmonk campaign: `MMR_monitoring_email` (a named storm in the area of interest, no threshold crossed) or `MMR_{phase}_email` / `MMR_trigger_email` (any wind or rainfall exceedance). Both the storm-track and rainfall-forecast plots are attached when present. Separate official AA activation notices are sent through a different channel.

## Trigger logic

- **Keys off:** ECMWF and CMA tropical cyclone forecast tracks (wind speed at the AA Target area after distance reduction); CHIRPS-GEFS precipitation forecast over the AA Target area.
- **Decision rule (plain language):** A wind alert fires if any ensemble member (ECMWF) or the deterministic CMA track forecasts a distance-reduced wind speed of at least 47 knots at the AA Target area at any point in the forecast. A rainfall alert fires if, in the latest CHIRPS-GEFS forecast, the sum of three consecutive days of area-average rainfall over the AA Target area reaches at least 175 mm. Either condition on its own sends an alert email, labelled readiness/action/observational by how soon the storm's median closest approach is. Unnamed disturbances (ids like `70B`) are dropped row by row.
- **Activation structure:** two independent alert conditions (wind OR rainfall). A trigger email if either is exceeded; a monitoring email if neither but a named storm is within 500 km of the target area. Lead time shapes only the email phase label.
- **Calibration:** no documented selection basis in the repo. 47 kt coincides with the IMD Cyclonic Storm / Severe Cyclonic Storm boundary (3-min sustained, consistent with the ×1.05 conversion), and the historical analysis (`src/datasources/ibtracs.py`, `historical_analysis/`) classifies storms on the IMD scale and joins CERF allocations/EM-DAT impact and IMERG rainfall — but no return period is computed for either threshold. See discrepancies.
- **Authoritative source:** none published; `trigger_source: repo`. The deployed code in `src/` is the only design record, and it carries no written rationale for the thresholds.
- **Operated by:** OCHA Centre for Humanitarian Data (GHA workflows in `ocha-dap/ds-aa-mmr-cyclones`).

## Trigger windows

The email phase (`send_email.determine_trigger_phase`) does **not** gate the threshold checks; `wind_speed_monitoring_*.py` scan peak wind across the full forecast horizon.

| window | basis | indicator | threshold | lead time | return period | releases |
|---|---|---|---|---|---|---|
| wind alert | forecast | ECMWF-wind-speed, CMA-wind-speed (distance-reduced to AA Target area, 10 Rakhine townships) | >= 47 kt | any (full forecast horizon) for detection; readiness 72–120 h / action 48–72 h / observational <48 h label on the email only | not calibrated | trigger email (`MMR_{phase}_email` / `MMR_trigger_email`); official activation notice via separate channel |
| rainfall alert | forecast | CHIRPS-GEFS-3day-rainfall (3-day rolling SUM of AA-Target-area daily-mean precip, latest issue date) | >= 175 mm | 0–16 days | not calibrated | trigger email (same campaign path) |

## Sources & repo completeness

- **Trigger taken from:** `repo` — no published framework PDF located and no extract supplied. A non-public framework document likely exists (email disclaimer).
- **Repo completeness:** partial — thresholds have no recorded rationale; no 63 kt level exists as a trigger; CERF-allocation and EM-DAT lookup CSVs are absent; the ECMWF and CMA hindcast scripts raise a `TypeError` as committed.
- **Discrepancies:** see frontmatter. Key items: (a) the trigger area is now 10 ADM3 townships, not Rakhine ADM1 (prior page superseded); (b) a Rest-of-Rakhine-only wind exceedance still sends a trigger-labelled email; (c) no 63 kt trigger exists; (d) the CHIRPS-GEFS download/process season-start mismatch; (e) hindcast scripts' keyword-argument bug; (f) CMA download has no retry.

## Monitoring

Seven GHA workflows exist in `ocha-dap/ds-aa-mmr-cyclones` (five operational; the other two are Claude code-review helpers):

- `run_update_ecmwf.yml` — 08:00 and 20:00 UTC: download ECMWF BUFR tracks, filter to Myanmar, reduce wind, upload exceedance/monitoring blobs and track plot (job timeout 10 min).
- `run_update_cma.yml` — 08:00 and 20:00 UTC: same for CMA bulletins (timeout 10 min).
- `run_update_chirps_gefs.yml` (`src/monitoring/update_chirps_gefs.py`) — 08:50 UTC daily: download (≤3 newest incomplete issue dates; optional `--max-issue-dates 0` for backfill), process to the AA-target mean parquet, check the 175 mm threshold, save the rainfall-forecast plot. Job timeout is now 180 min (was 25).
- `run_monitoring.yml` (`send_email.py`) — 09:00 and 20:15 UTC: decide and send the monitoring/trigger email via Listmonk.
- `slack_bot.yml` (`src/monitoring/slack_bot.py`) — 09:15 and 20:30 UTC: posts workflow run-status and today's blob signals (wind/rainfall threshold status) to Slack.

Outputs are written to Azure Blob under `projects/ds-aa-mmr-cyclones/processed/` (dev stage). Storm-track plots draw neighbouring countries and highlight the highest-wind track.

## Historical activations

Never activated. Monitoring live since about 2026-03-01; no activation is recorded in the repo, and no Myanmar cyclone AA framework activation or pre-arranged allocation appears in public CERF AA sources reachable at the last check (the 15 Nov 2024 portfolio update does not list Myanmar).

<!-- TODO: this section is INCOMPLETE — a longer-record ECMWF-hindcast retrospective (historical_analysis/load_ecmwf_data.py; output CSV in Drive: CERF Anticipatory Action/Myanmar/Cyclones 2025/results/Trigger_ecmwf_forecast_vs_ibtracs_observed/Rakhine only/hist_forecast_trigger_True_1_94288602.csv) WAS completed in an earlier run, but the script now raises a TypeError (see discrepancies) so the CSV cannot be regenerated, and it was computed for Rakhine ADM1, not the current 10-township target area. Over 2006–2024 (22 storms) FOUR storms trigger at wind >=47 kt — Nargis 2008 (52.4 kt), Giri 2010 (53.2), Mora 2017 (50.2), Mocha 2023 (78.9); wind-only (rainfall input hard-set to 0). Internal deck "Myanmar – trigger proposal.pptx" (2025-10-23, Drive id 1V23b9E6R9CQCzSTM7B-kQ1KQt6-ozRBH; extract in ds-knowledge-base-internal): analysis from 2000, 200 km buffer; CERF allocations for 5 cyclones (Komen, Mora, Nargis, Mocha, Giri); Komen 2015 triggers via the RAINFALL condition (framework lead, 2026-07-15), giving would-have-triggered Nargis 2008, Giri 2010, Komen 2015, Mora 2017, Mocha 2023 — plus Mala 2006 on the OBSERVED-wind basis only (forecast archive does not reach April 2006; no CERF AA allocation). Its rainfall condition is 3-day mean >=200 mm, vs 175 mm in deployed constants. "Myanmar Cyclone Review - IBTrACS" (2025-06-27, id 16A0C5L-GNbfAagc0Z7CXHiSgEWyHA87vNjsDcF7LOlg): Rakhine SCS-or-higher frequency 1-in-1.6 yr before wind-reduction-at-land filtering. Fold into this page once the framework doc or a re-run exists. -->

**Retrospective analysis (simulated, not real activations):** of 11 Bay of Bengal storms in the 2022–2025 CMA archive, only Cyclone Mocha (May 2023) would have crossed the wind threshold (first qualifying forecast issued 2023-05-13 08:00 UTC). Nargis (2008), Giri (2010) and Mora (2017) predate the CMA archive. The `historical_analysis/` scripts also merge CERF allocations and EM-DAT impact by storm id (CSV inputs absent — see discrepancies), so calibration against past responses is implied but not reproducible here.

**IMD storm classification** used by the historical analysis (`ibtracs.categorize_storms`, by wind at landfall or reduced wind at the closest track point). 47 kt is the trigger level; 63 kt is only the next bin edge:

| wind speed (knots) | IMD classification |
|---|---|
| < 16 | Below Depression |
| 16–27 | Depression |
| 27–33 | Deep Depression |
| 33–47 | Cyclonic Storm |
| 47–63 | Severe Cyclonic Storm |
| 63–89 | Very Severe Cyclonic Storm |
| 89–119 | Extremely Severe Cyclonic Storm |
| > 119 | Super Cyclonic Storm |

**IMERG rainfall join** (`load_imerge_data.py`): ADM1 daily-mean rainfall at the max-wind point summed over day −1, 0, +1 around the peak-wind date (`offsets = [-1, 0, 1]`) into `3days_rain_mean` — a 3-day sum despite the name, the same statistic as the deployed CHIRPS-GEFS check (but over ADM1, vs the AA Target area live).

Digested from the retired DSCI Confluence space (archive: `confluence/` in `ds-knowledge-base-internal`).

## Key decisions & rationale

- **Geographic scope (Rakhine, now a 10-township AA Target area):** Rakhine has the highest historical exposure to intense Bay of Bengal landfalls; the live code narrows the trigger to the target townships and tracks the rest of the state for information. Rationale for the township list is not recorded in the repo.
- **Two forecast sources (ECMWF + CMA):** parallel monitoring reduces the risk of one source silencing the trigger; CMA adds Bay of Bengal-focused deterministic forecasts not in ECMWF ensemble products.
- **Distance-based wind reduction:** `0.9807 × exp(−0.003 × dist)` is applied at every forecast point (not only landfall), giving a more conservative (earlier) trigger.
- **Dual indicator (wind + rainfall):** Cyclone Mocha showed extreme rainfall can be severe even if reduced wind is below threshold; Komen (2015) is the rainfall-only case in the would-have-triggered set.
- **Unnamed-storm exclusion:** ids like `70B` are dropped per row so unclassified disturbances don't generate alerts.
- **Monitoring-only email vs official activation:** Listmonk gives near-real-time situational awareness; the decision to act is made through a separate manual process (conflict-affected setting).

## Changes from previous version

First documented version; no prior published version. Changes **within this development version** since the last KB sync (`source_sha` b8d84e2 → 8c09720; no PDF extract available):

- **Trigger area narrowed from Rakhine ADM1 to a 10-township ADM3 AA Target area** (`constants.ADM3_LIST`, `adm_level = 3`, `codab.load_aa_target_and_rest_areas`, `utils_windpseed.compute_wind_speed_at_adm_list`). Wind distances and the CHIRPS-GEFS spatial mean now use that area; "Rest of Rakhine" is monitored for wind in parallel (`wind_exceedance_rest_*` blobs, `wind_speed_at_land_rest`). Threshold values (47 kt, 175 mm) are unchanged.
- **Email now carries a per-area/per-source threshold table** (`build_threshold_table`) and loads the latest wind exceedance blob per (area, source) pair — this **fixes** the earlier bug where a `wind` prefix match let one source silently override the other.
- **Unnamed-storm filter is now per row** (`storm_names.drop_unnamed_storms`, pattern `^\d{2}[A-Za-z]$`), replacing the all-or-nothing `has_valid_sid` gate; blobs are also filtered to today's date.
- **CHIRPS-GEFS pipeline reworked:** v12 → v3 source switch on 2026-07-01, directory-listing availability check, newest-first capped download (3 issue dates/run), only the latest issue date is checked for the trigger, and the workflow timeout is 180 min. The hard-coded `"2026-03-15"` literal became `CHIRPS_GEFS_START_DATE` (still fixed to 2026).
- **Test layout cleaned up:** the orphan `tests/monitoring/test_wind_speed_monitoring.py` is gone; new tests cover the threshold table, ADM-list wind, Slack bot and CHIRPS-GEFS.
- **Unchanged:** no 63 kt trigger; dead constants; hindcast `TypeError` (now in both ECMWF and CMA scripts); CMA download without retry; DEV-only outputs; Cuba leftovers.

## Open questions / known issues

- Why was the trigger narrowed to 10 ADM3 townships, and is that the endorsed framework geography? The earlier hindcast and the Mocha result were computed on Rakhine ADM1 and have not been re-derived for the target area.
- Should a wind exceedance only in "Rest of Rakhine" trigger an email labelled as a trigger? Currently `send_email.main` pools all areas.
- Return period of the 47 kt and 175 mm thresholds? No calibration is documented; the proposal deck cites a 200 mm rainfall condition vs 175 mm deployed.
- Was there ever an L2 (63 kt) severity trigger? Only the IMD bin edge exists in the repo.
- Should threshold detection filter by the readiness/action lead-time windows now used to label the email?
- Intended use of `rainfall_alert_level_observational = 250`, `MIN_EMAIL_DISTANCE`, `MONITORING_START_DATE`?
- Fix `windspeed_column=` → `wind_speed_column=` in `load_ecmwf_data.py:70` and `load_cma_data.py:56` so the hindcasts can run again.
- Make the CHIRPS-GEFS `CHIRPS_GEFS_START_DATE` year-relative and reconcile 15 vs 25 March with `process_recent_chirps_gefs`.
- Is `download_tracks_cma` intentionally without retry/backoff?
- Missing inputs `src/data/cerf_data.csv` and `emdat_mmr.csv` for the historical joins.
- No activation since monitoring began; is the framework still in development or quietly endorsed pending a document? If a framework PDF appears, it likely warrants a dated version page.
