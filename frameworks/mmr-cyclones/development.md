---
content_type: framework
framework: mmr-cyclones
version: development
status: development
valid_until: null
country_iso3: MMR
hazard: tropical-cyclone
admin_level: 3
geographic_scope: ["Rakhine (MMR012)", Buthidaung, Kyauktaw, Maungdaw, Mrauk-U, Pauktaw, Ponnagyun, Rathedaung, Sittwe, Minbya, Myebon]   # ADM1 Rakhine = wider area (wind + rainfall); the ten ADM3 townships = restricted wind area (constants.ADM1_LIST / ADM3_LIST)
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
  note: "Bay of Bengal TC season, Apr–Dec, with pre-monsoon (Apr–Jun) and post-monsoon (Oct–Dec) intensity peaks; no doc exists to state a season, so inferred. Jul–Sep is INCLUDED deliberately: the would-have-triggered set contains Komen (July 2015, via the rainfall condition), so a monsoon-season month can fire. In practice the GHA schedules run every day of the year with no seasonal cron gating and no MONITORING_START_DATE check (see extra.monitoring_start_note), so this is a hazard-season judgment, not an enforced window; the only code-level seasonal bound is the CHIRPS-GEFS processing range, which starts each year on ~25 March (process_recent_chirps_gefs) and has no end — while the paired download step uses a HARD-CODED 2026-03-15 (see discrepancies)."
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
source_branch: chore/remove-stale-wind-test
source_sha: "fbbc5fd"
code_ref:
  - src/monitoring/wind_speed_monitoring_ecmwf.py
  - src/monitoring/wind_speed_monitoring_cma.py
  - src/utils/utils_cma.py
  - src/utils/utils_windpseed.py
  - src/utils/storm_names.py
  - src/monitoring/update_chirps_gefs.py
  - src/datasources/chirps_gefs.py
  - src/monitoring/send_email.py
  - src/utils/constants.py
trigger_source: repo
repo_completeness: partial
discrepancies:
  - "[gap] No published framework PDF found on ReliefWeb or unocha.org, and no PDF text extract was available for this re-ingestion — this page is drafted from the repo and the prior page only. CERF's AA update (November 2025) lists the Myanmar tropical-cyclone framework as 'Under development' (see extra.cerf_tracking_note), so there is no endorsed document yet; the monitoring email disclaimer ('purely informational ... Official activation notices are sent in another email') anticipates separate official comms once it is endorsed."
  - "[gap] The CHIRPS-GEFS rainfall threshold (175 mm 3-day rolling sum, constants.rainfall_alert_level_forecast) has no documented return-period or validation basis in the repo. Defined but consumed by no script: rainfall_alert_level_observational = 250 mm and MIN_EMAIL_DISTANCE = 1000 (constants.py). NUMERIC_NAME_REGEX and _parse_bool_env are likewise unreferenced outside constants.py."
  - "[gap] No 63 kt L2 severity TRIGGER threshold exists anywhere in the repo (constants.py defines only wind_speed_alert_level = 47). 63 survives only as an IMD intensity bin edge (src/datasources/ibtracs.py categorize_storms, duplicated in src/utils/utils_plot.py) — plausibly what an earlier ingestion recorded as 'L2'. Whether a two-level design was ever intended cannot be settled from the repo; flag for the framework team."
  - "[conflict] Spatial design changed vs the prior page and the rationale is undocumented: constants.py now sets adm_level = 3 and the wind trigger is evaluated against TWO areas — a restricted area (ADM3_LIST, ten Rakhine townships; wind_speed_at_land, files wind_exceedance_adm3_*) and a wider area (ADM1_LIST = Rakhine; wind_speed_at_land_adm1, files wind_exceedance_adm1_*). The ADM1 area contains the ADM3 area, so the ADM1 wind exceedance is a superset of the ADM3 one, and send_email concatenates both: either area exceeding 47 kt sends the trigger email. Rainfall remains ADM1-only (the threshold table reports 'Not assessed' for the restricted area). Nothing in the repo says which area is the 'official' trigger area, or whether the restricted area is meant to supersede the ADM1 check."
  - "[conflict] The deployed rainfall trigger (chirps_gefs.check_chirps_gefs_trigger) computes a 3-day rolling SUM (rolling(3, min_periods=1).sum()) of the Rakhine ADM1 daily-mean precipitation compared to 175 mm; the repo name mmr_chirps_gefs_mean_daily and casual wording read as a 'mean'. Read the mm value and the statistic together. min_periods=1 also lets the first one or two valid days of each issue date be compared as partial sums."
  - "[conflict] The two halves of the CHIRPS-GEFS step disagree about where the season starts, and one is frozen to a literal year: download_recent_chirps_gefs uses start=f\"2026-03-15\" (chirps_gefs.py:106) while process_recent_chirps_gefs uses the year-relative start=f\"{date.year}-03-25\" (chirps_gefs.py:258). From 2027 the download range will keep reaching back to March 2026 instead of restarting with the season. Unchanged at fbbc5fd."
  - "[gap] wind_speed_monitoring_cma.download_tracks_cma has no retry/backoff decorator, unlike download_tracks_ecmwf (tenacity, 3 attempts). Not documented as intentional (CMA reads blob storage rather than an external FTP). Unchanged at fbbc5fd."
  - "[gap] historical_analysis/load_ecmwf_data.py (line 70) AND load_cma_data.py (line 56) call run_trigger(..., windspeed_column=...) but src/utils/utils_fun.py:126 declares the parameter as wind_speed_column — a TypeError in both hindcast scripts as committed (previously only the ECMWF script was noted). The hindcast retrospective under Historical activations predates this and is not reproducible from the repo without a one-word fix."
  - "[stale] historical_analysis/load_imerge_data.py reads src/data/cerf_data.csv and src/data/emdat_mmr.csv, which are absent from the tracked repo (src/data holds only emdat_all.parquet and storms_date.pickle), so the CERF-allocation and impact joins in the hindcast comparison cannot be reproduced from the repo alone."
  - "[stale] All monitoring and plot outputs land in the DEV blob slot (projects/ds-aa-mmr-cyclones/processed): the wind monitoring scripts pass stage=\"dev\" explicitly, while the CHIRPS-GEFS writes and send_email reads pass no stage and rely on ocha_stratus defaulting to dev. Consistent with status: development; no prod-stage artifacts exist and promotion to prod is outstanding."
  - "[stale] src/datasources/zma.py (Cuba ZMI coordinates) and src/datasources/imerg.py:load_imerg_recent (queries public.imerg WHERE pcode = 'CU') are unused Cuba-specific leftovers, not referenced by any Myanmar script."
  - "[gap] The prior ingestion (source_sha 284cf02) referenced docs/index.qmd, docs/cma-trigger-analysis.qmd and notebooks/cma_forecasts.py; none appear in this repo's history, so those claims (point-in-polygon vs distance-reduction, L2 threshold, lead-time windows) cannot be verified and are not carried here."
# --- activation history ---
activations: []
# --- escape hatch ---
extra:
  doc_status: non-public
  cerf_tracking_note: "CERF Anticipatory Action Update, November 2025 (https://cerf.un.org/sites/default/files/resources/Overview%20of%20CERF%20support%20to%20Anticipatory%20Action%20November%202025_0.pdf), table of frameworks: 'Myanmar — Tropical Cyclones — Under development — CERF overall commitment $5,000,000 — remaining pre-arranged $5,000,000 (as of 15 Nov 2025)'; the table covers frameworks under development 'for which pre-approval from the ERC has been obtained'. The same update says a collaborative CERF + OCHA Country Fund (co-funding) approach 'is now being explored in Myanmar for the tropical cyclones AA framework'. Kept OUT of prearranged_funding_usd/funding_by_source because no framework has been endorsed (development-stage convention, cf. mdg-plague planned_envelope_note) — set them once the doc is endorsed."
  monitoring_start: "2026-03-01"
  monitoring_start_note: "constants.MONITORING_START_DATE (Asia/Yangon-localised) is defined but no other file in src/ reads it; the workflows run unconditionally on the GHA cron. Treat 2026-03-01 as an approximate pipeline-live date, not a code-enforced start."
  wind_reduction_formula: "wind_at_land = 0.9807 * exp(-0.003 * min_dist_km) * wind_knots, where wind_knots = 1.05 * (raw_wind_ms * 1.9438444924) — m/s to knots (from_ms_to_knots), then 10-min to 3-min sustained convention (convert_10m_wind_to_3m, x1.05), BEFORE the distance reduction (src/utils/utils_windpseed.compute_wind_speed_at_land, src/utils/utils_fun.py). min_dist_km is now the distance to the AREA OF INTEREST (ADM3_LIST townships or Rakhine ADM1) rather than to all Myanmar land (compute_wind_speed_at_adm_list)."
  rainfall_threshold_forecast_mm3d: 175
  rainfall_threshold_observational_mm3d: 250
  action_window_hours: "48-72"
  readiness_window_hours: "72-120"
  trigger_phase_email_logic: "send_email.determine_trigger_phase computes readiness (72-120 h) / action (48-72 h) / observational (<48 h) / None (>120 h) from the median across ensemble members of each member's closest-approach time (falling back to CHIRPS-GEFS valid-minus-issue lead time if no cyclone monitoring data; 'observational' if neither). It only labels the ALERT EMAIL (subject campaign name MMR_{phase}_email and listmonk._PHASE_INTROS copy); it does not gate the wind/rainfall threshold checks, which scan the full forecast horizon."
  unnamed_storm_filter: "src/utils/storm_names.py: unnamed disturbances are identifiers matching ^\\d{2}[A-Za-z]$ (e.g. 70B, 71W). send_email drops these rows per-row (drop_unnamed_storms) from the wind-exceedance and monitoring data, and plot_storm_track(filter_name='all') leaves them out of plots. This replaces the earlier all-or-nothing has_valid_sid gate (^\\d{2}B$)."
  email_threshold_table: "send_email.build_threshold_table renders a status grid in the email: rows = Wind speed (ECMWF), Wind speed (CMA), Rainfall; columns = Restricted area / Wider area (Rakhine); cells REACHED / NOT REACHED / Not assessed (rainfall for the restricted area)."
  aoi_state: "Rakhine (ADM1_PCODE MMR012)"
  historical_archive_cma: "2022-2025 Bay of Bengal TCs; Cyclone Mocha (May 2023) is the only storm that would have triggered at the wind threshold within Rakhine ADM1 (first qualifying forecast 2023-05-13 08:00 UTC) — from the prior ingestion; not re-run."
  window_axes_note: "n_windows = 2 (wind alert, rainfall alert), differing by INDICATOR (not time/space/severity), so window_axes is []. The wind window is evaluated in two nested areas (ADM3 restricted, ADM1 wider) but they feed one alert and are counted as one window."
  schema_strain: "No published doc — framework_doc/framework_doc_date null, trigger_source repo, no PDF extract. The earlier two-level (L1/L2) wind design has no counterpart in the repo. admin_level is 3 (the restricted trigger area) although rainfall and the wider wind check are ADM1."
visibility: internal
last_synced: "2026-10-13"
---

# Myanmar Tropical Cyclone — development

> The canonical trigger is the code at `code_ref`; this page explains it, it does not redefine it.

## Summary

Myanmar's cyclone anticipatory action framework targets Rakhine State, the part of the country most exposed to intense Bay of Bengal cyclones. The monitoring combines a wind-speed forecast from ECMWF and/or CMA (distance-reduced to the area of interest, threshold 47 kt) with a CHIRPS-GEFS 3-day cumulative rainfall forecast (175 mm over Rakhine ADM1). Wind is now checked against two nested areas — a restricted area of ten Rakhine townships (ADM3) and the wider Rakhine ADM1. When either wind or rainfall threshold is crossed, an alert email goes out via Listmonk, labelled by phase (readiness / action / observational) from forecast lead time and carrying a threshold-status table; official AA activation notices are sent through a separate channel. The pipeline has been live since about 2026-03-01 on twice-daily GHA workflows writing to the DEV blob slot. No public framework document has been located and **no PDF extract was available**: this page was re-verified against the repo at `fbbc5fd` and the prior page only.

## Method

1. **ECMWF tracks** — BUFR files fetched via CLIMADA `TCForecast` (retried up to 3x with exponential backoff; a `climada_petals` `UnboundLocalError` that masks FTP failures is re-raised as `OSError` so the retry engages). Points within a 2000 km buffer of Myanmar (ADM0, EPSG:32647) are kept; ensemble members and the deterministic track are both included.
2. **CMA tracks** — WMO WTPQ `.TXT` bulletins read from blob storage (`ds-cma-datasharing/cma_ftp/data_out/typhoon/`), parsed by `src/utils/utils_cma.py`; same filter and reduction pipeline via `src/utils/utils_windpseed.py`.
3. **Wind reduction at the area of interest** — `compute_wind_speed_at_adm_list` projects tracks (EPSG:3857), computes distance to the named ADM units, converts m/s → knots → 3-min convention (×1.05) and applies `0.9807 × exp(−0.003 × dist_km)`. It is run twice: against `ADM3_LIST` (restricted, → `wind_speed_at_land`) and against `ADM1_LIST` (wider, → `wind_speed_at_land_adm1`). `get_wind_exceedance` keeps each `sid`/`ensemble_number` whose maximum reduced wind is ≥ 47 kt; exceedances are uploaded as `wind_exceedance_adm3_{date}_{hour}_{source}.csv` and `wind_exceedance_adm1_…`. Storms whose closest approach is ≤ `buffer_km` = 500 km are uploaded as `monitoring_{date}_{hour}_{source}.csv` with a storm-track plot (ECMWF plot keeps points ≥ 30 kt where any exist).
4. **CHIRPS-GEFS rainfall** — daily 16-day forecast GeoTIFFs clipped to Rakhine ADM1; spatial mean per valid day, then a **3-day rolling sum** per issue date compared to 175 mm (`chirps_gefs.check_chirps_gefs_trigger` → `rainfall_exceedance_{date}.csv`).
5. **Alerting** — `send_email.py` loads today's latest wind-exceedance blob **per (area, source)**, drops unnamed disturbances row by row, loads rainfall exceedance and storm-in-area monitoring data, determines the phase, builds the threshold table, and sends via Listmonk either a **monitoring email** (`MMR_monitoring_email`: a named storm is in the 500 km area but no threshold crossed) or a **trigger email** (`MMR_{phase}_email`, or `MMR_trigger_email` when no phase resolves). Storm-track and rainfall-forecast plots are attached when present for today.

## Trigger logic

- **Keys off:** ECMWF and CMA cyclone forecast tracks (reduced wind speed at Rakhine); CHIRPS-GEFS precipitation forecasts.
- **Decision rule (plain language):** A wind alert fires if any ensemble member or deterministic track from ECMWF or CMA gives a distance-reduced wind of at least 47 kt at the restricted area (ten Rakhine townships) or at Rakhine as a whole, for a named storm (unnamed `70B`-style disturbances are ignored). A rainfall alert fires if the CHIRPS-GEFS 3-day rolling sum of Rakhine's daily-mean rainfall reaches 175 mm. Either one independently sends a trigger email, phase-labelled by how soon the storm's median approach is.
- **Activation structure:** Two independent conditions (wind OR rainfall); wind is evaluated in two nested areas and by two sources, all merged into one alert. A monitoring email goes out if no threshold is crossed but a named storm is within 500 km.
- **Calibration:** 47 kt is the Cyclonic Storm / Severe Cyclonic Storm edge on the IMD scale (3-min sustained, matching the pipeline's convention); the repo carries the IMD mapping only for classifying the historical record. No document in the repo records why 47 kt, the 175 mm threshold, or the ADM3/ADM1 split were chosen. See discrepancies.
- **Authoritative source:** none published; `trigger_source: repo`.
- **Operated by:** OCHA Centre for Humanitarian Data (GHA in `ocha-dap/ds-aa-mmr-cyclones`).

## Trigger windows

The phase logic labels emails only; it does not gate threshold detection.

| window | basis | indicator | threshold | lead time | return period | releases |
|---|---|---|---|---|---|---|
| wind alert | forecast | ECMWF-wind-speed, CMA-wind-speed (distance-reduced; restricted area ADM3 ×10 townships and wider area Rakhine ADM1) | ≥ 47 kt | full forecast horizon for detection; readiness 72–120 h / action 48–72 h / observational <48 h label on the email | not calibrated | trigger email (`MMR_{phase}_email` / `MMR_trigger_email`); official notice via separate channel |
| rainfall alert | forecast | CHIRPS-GEFS-3day-rainfall (3-day rolling SUM of Rakhine ADM1 daily-mean precip) | ≥ 175 mm | 0–16 days | not calibrated | trigger email (same path) |

## Sources & repo completeness

- **Trigger taken from:** `repo` — no framework PDF found; none extracted.
- **Repo completeness:** partial — thresholds and area choices have no recorded rationale; no L2 trigger exists; hindcast scripts raise `TypeError`; CERF/EM-DAT lookup CSVs absent.
- **Discrepancies:** see frontmatter. Key items: (a) wind trigger now has restricted-ADM3 and wider-ADM1 areas with no stated authority between them; (b) no 63 kt trigger exists; (c) both hindcast scripts fail on a keyword mismatch; (d) hard-coded `2026-03-15` in the CHIRPS-GEFS download; (e) CMA download lacks retries; (f) rainfall threshold uncalibrated.

## Monitoring

Five GitHub Actions workflows in `ocha-dap/ds-aa-mmr-cyclones` (all UTC cron, unchanged):

- `run_update_ecmwf.yml` — 08:00, 20:00: ECMWF tracks → wind reduction → blob.
- `run_update_cma.yml` — 08:00, 20:00: CMA bulletins → wind reduction → blob.
- `run_update_chirps_gefs.yml` — 08:50: CHIRPS-GEFS 16-day forecasts → Rakhine mean → 3-day rolling sum → threshold check (timeout 25 min).
- `run_monitoring.yml` (`send_email.py`) — 09:00, 20:15: builds and sends the monitoring/trigger email via Listmonk.
- `slack_bot.yml` — 09:15, 20:30: posts workflow-run status and today's blob signals to Slack.

Outputs live under `projects/ds-aa-mmr-cyclones/processed/` (dev stage). Storm-track plots show neighbouring countries and highlight the max-wind track in red.

## Historical activations

Never activated. Monitoring has been live since approximately 2026-03-01; no activation is recorded in the repo, and no public CERF/ReliefWeb record of a Myanmar cyclone AA allocation was found. CERF's November 2025 AA update lists the framework as **under development** with a $5M CERF commitment still fully pre-arranged (unspent) as of 15 November 2025 (see `extra.cerf_tracking_note`).

<!-- TODO: this section is INCOMPLETE — a longer-record ECMWF-hindcast retrospective (historical_analysis/load_ecmwf_data.py; output CSV in Drive: CERF Anticipatory Action/Myanmar/Cyclones 2025/results/Trigger_ecmwf_forecast_vs_ibtracs_observed/Rakhine only/hist_forecast_trigger_True_1_94288602.csv; the script now raises a TypeError before writing, so the CSV predates that regression) WAS completed: over the 2006–2024 storm universe (22 storms), FOUR storms trigger at the wind threshold ≥47 kt — Nargis 2008 (52.4 kt), Giri 2010 (53.2), Mora 2017 (50.2), Mocha 2023 (78.9). Wind-only: rainfall input hard-set to 0. Fold into this page. Corroborating internal decks (Drive, extracts in ds-knowledge-base-internal): "Myanmar – trigger proposal.pptx" (2025-10-23, id 1V23b9E6R9CQCzSTM7B-kQ1KQt6-ozRBH — analysis from year 2000, 200 km buffer; CERF allocations for 5 cyclones: Komen, Mora, Nargis, Mocha, Giri; Komen 2015 triggers via the RAINFALL condition (confirmed by framework lead 2026-07-15), giving the would-have-triggered set Nargis 2008, Giri 2010, Komen 2015, Mora 2017, Mocha 2023 — plus Mala 2006 on the OBSERVED-wind basis; one storm per year; its rainfall condition is 3-day mean ≥200 mm vs 175 mm forecast / 250 mm observational in deployed constants.py) and "Myanmar Cyclone Review - IBTrACS" (2025-06-27, id 16A0C5L-GNbfAagc0Z7CXHiSgEWyHA87vNjsDcF7LOlg — Rakhine SCS-or-higher frequency 1-in-1.6 yr, before wind-reduction-at-land filtering). Slide visuals not yet captioned in the internal repo. Also: these analyses predate the ADM3 restricted-area design — re-run for the ten townships. -->

**Retrospective analysis (prior ingestion, not re-run):** of 11 Bay of Bengal storms in the 2022–2025 CMA archive, only Cyclone Mocha (May 2023) would have triggered at the wind threshold within Rakhine ADM1 (first qualifying forecast 2023-05-13 08:00 UTC). Nargis, Giri and Mora predate the CMA archive.

**Storm classification (IMD scale)** — `src/datasources/ibtracs.py:categorize_storms` bins historical storms; 47 kt is the trigger edge, 63 kt is only a bin edge:

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

**Rainfall join.** IMERG is joined to IBTrACS storms as the ADM daily-mean rainfall at the max-wind point summed over day −1, 0, +1 (`load_imerge_data.py`), column `3days_rain_mean` — a 3-day sum, the same statistic as the CHIRPS-GEFS check. The historical scripts now key on `ADM_LIST` (= ADM3 townships, `dates_cyclones.py`).

Digested from the retired DSCI Confluence space (archive: `confluence/` in `ds-knowledge-base-internal`).

## Key decisions & rationale

- **Rakhine scope, now nested:** Rakhine has the highest historical exposure; a restricted ten-township wind area was added inside the ADM1 check (rationale not recorded in the repo — likely to reduce false positives for tracks near but not threatening the core townships; unverified).
- **Two forecast sources (ECMWF + CMA):** parallel monitoring reduces the risk of a source outage silencing the trigger; CMA adds Bay of Bengal-focused forecasts not in the ECMWF ensemble.
- **Distance-based wind reduction** applied at every forecast point (not just landfall), relative to the area of interest, gives an earlier, more conservative trigger.
- **Dual indicator:** Cyclone Mocha showed extreme rainfall can be severe even if wind at Rakhine is below threshold; CHIRPS-GEFS supplements wind.
- **Unnamed-storm exclusion:** `70B`-style disturbances are dropped per row so alerts are about named cyclones.
- **Monitoring-only email vs official activation:** Listmonk gives situational awareness; the official AA decision is a separate manual process (conflict-affected setting).

## Changes from previous version

First documented version; no prior published version. Changes within this development version since the last KB sync (`source_sha` b8d84e2 → fbbc5fd, branch `chore/remove-stale-wind-test`; checked against `git diff b8d84e2 fbbc5fd`):

- **Two-area wind trigger (new):** `constants.adm_level = 3`, `ADM3_LIST` (ten Rakhine townships) and `ADM1_LIST`; `compute_wind_speed_at_adm_list` computes reduced wind relative to the areas of interest; separate `wind_exceedance_adm3_*` / `wind_exceedance_adm1_*` blobs.
- **Email rework:** wind blobs are loaded per (area, source), fixing the earlier bug where only the last-sorted `wind*` blob of the day was read (`xx[-1]`), so one source's exceedances could be silently dropped; a threshold-status table is added.
- **Unnamed-storm filter is now per-row** (`storm_names.py`, `^\d{2}[A-Za-z]$`) instead of the all-or-nothing `^\d{2}B$` gate.
- **Stale orphan test removed:** `tests/monitoring/test_wind_speed_monitoring.py` no longer exists; new tests `test_threshold_table.py`, `test_wind_speed_at_adm_list.py`, `test_slack_bot.py`.
- **Unchanged:** 47 kt / 175 mm thresholds, phase logic, cron schedules, CHIRPS-GEFS hard-coded `2026-03-15`, CMA no-retry, hindcast `TypeError` (now in both scripts).

## Open questions / known issues

- What is the return period of the 47 kt and 175 mm thresholds? No calibration is documented.
- Why were the ten-township ADM3 area and the ADM1 area both kept, which is the official trigger area, and why is rainfall only assessed for ADM1? Should the hindcast (return-period) analysis be re-run for the ADM3 area?
- Was there ever an L2 (63 kt) severity trigger, or was the earlier record a misreading of the IMD bin edge?
- Should wind/rainfall *detection* be filtered by the readiness/action lead-time windows now used only to label the email?
- `rainfall_alert_level_observational = 250` mm, `MIN_EMAIL_DISTANCE = 1000` and `MONITORING_START_DATE` are defined but unused — what was intended?
- `load_ecmwf_data.py` and `load_cma_data.py` pass `windspeed_column=` to a function expecting `wind_speed_column` — fix so the hindcast can be re-run.
- Is `download_tracks_cma` intentionally without retry/backoff?
- Should the `2026-03-15` hard-coded start in `download_recent_chirps_gefs` be year-relative, and should it match the `03-25` process start?
- Is there a return period for Cyclone Mocha as a calibration event? The 2022–2025 CMA archive is too short for a robust estimate.
- CERF listed the framework as under development ($5M pre-approved) in November 2025. Has it been endorsed since, with what final envelope (CERF + Myanmar Humanitarian Fund co-funding?), and when will the document be published?
