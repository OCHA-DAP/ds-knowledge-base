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
  months: [4, 5, 6, 7, 8, 9, 10, 11, 12]
  source: inferred
  note: "Bay of Bengal TC season, Apr–Dec, with pre-monsoon (Apr–Jun) and post-monsoon (Oct–Dec) intensity peaks; no doc exists to state a season, so inferred. Jul–Sep is INCLUDED deliberately: the framework's own would-have-triggered set contains Komen (July 2015, via the rainfall condition), so a monsoon-season month can fire. In practice the GHA schedules run every day of the year with no seasonal cron gating and no MONITORING_START_DATE check (see extra.monitoring_start_note), so this is a hazard-season judgment, not an enforced monitoring window; the only code-level seasonal bound is the CHIRPS-GEFS processing range, which starts each year on ~25 March (chirps_gefs.process_recent_chirps_gefs, start=f\"{date.year}-03-25\") and has no end — and the paired download step bounds its range with a HARD-CODED 2026-03-15 rather than a year-relative date (see discrepancies)."
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
apps: []
depends_on: [listmonk]
# --- source repo & reconciliation ---
source_repo: ocha-dap/ds-aa-mmr-cyclones
source_branch: main
source_sha: "b8d84e2"
code_ref:
  - src/monitoring/wind_speed_monitoring_ecmwf.py
  - src/monitoring/wind_speed_monitoring_cma.py
  - src/utils/utils_cma.py
  - src/utils/utils_windpseed.py
  - src/monitoring/update_chirps_gefs.py
  - src/datasources/chirps_gefs.py
  - src/monitoring/send_email.py
  - src/utils/constants.py
trigger_source: repo
repo_completeness: partial
discrepancies:
  - "[gap] No published framework PDF found on ReliefWeb or unocha.org (no PDF text extract was available for this re-ingestion either — this page is drafted from the repo and the prior page only). The monitoring email disclaimer ('This email is purely informational and does not serve as an official notice for the anticipatory action framework. Official activation notices are sent in another email.') confirms an endorsed framework exists with separate official comms, but the document is not public."
  - "[gap] The CHIRPS-GEFS rainfall trigger threshold (175 mm 3-day rolling sum, constants.rainfall_alert_level_forecast) has no documented return-period or historical-validation basis in the repo. Two further constants are defined but consumed by no script (deployed or historical) — dead configuration, not live checks: rainfall_alert_level_observational = 250 mm and MIN_EMAIL_DISTANCE = 1000 (constants.py:18,55). NUMERIC_NAME_REGEX (constants.py:57) and the _parse_bool_env helper (constants.py:29) are likewise unreferenced outside constants.py."
  - "[gap] No 63 kt L2 severity TRIGGER threshold exists anywhere in the repo — confirmed at source_sha b8d84e2 (already absent at 5253227 and 3b6ed15): constants.py defines only wind_speed_alert_level = 47, and no deployed monitoring script or historical_analysis file applies a second wind level. The value 63 survives ONLY as a classification bin edge in the IMD intensity table (src/datasources/ibtracs.py:54 categorize_storms, duplicated at src/utils/utils_plot.py:242), where 47 and 63 are the Severe / Very Severe Cyclonic Storm boundaries — which is plausibly what the prior ingestion recorded as 'L2'. Whether a two-level design was ever intended, or the prior page mistook the IMD bin edge for a threshold, cannot be settled from the repo — flag for the framework team."
  - "[stale] historical_analysis/load_imerge_data.py reads two CSVs that are absent from the tracked repo (src/data holds only emdat_all.parquet and storms_date.pickle): src/data/cerf_data.csv, a CERF-allocation-by-storm-id lookup used to build the cerf_allocation column (load_imerge_data.py:60), and src/data/emdat_mmr.csv, used for Total Deaths / Total Affected (load_imerge_data.py:65). Both are likely gitignored/local-only. load_ecmwf_data.py does NOT read them directly — it consumes the derived columns via results/df_full_{suff}.csv (an intermediate that is also not in the repo). Either way the CERF-allocation and impact joins in the historical hindcast comparison cannot be reproduced from the repo alone."
  - "[stale] All monitoring and plot outputs land in the DEV blob slot of the projects container (projects/ds-aa-mmr-cyclones/processed). wind_speed_monitoring_ecmwf.py, wind_speed_monitoring_cma.py, utils_windpseed.plot_storm_track and utils_plot.plot_chirps_gefs_forecast pass stage=\"dev\" explicitly; the CHIRPS-GEFS writes (chirps_gefs.py:192,314,352 — raw tifs, the mean-daily parquet, and the rainfall_exceedance CSV) pass no stage at all and reach dev only because ocha_stratus defaults to stage=\"dev\" (ocha-stratus 0.1.8 azure_blob.py). send_email likewise lists/loads with the default stage. Consistent with status: development, but means no prod-stage artifacts exist and the dev default is load-bearing; promotion to prod is an outstanding change."
  - "[conflict] The deployed rainfall trigger (chirps_gefs.check_chirps_gefs_trigger) computes a 3-day rolling SUM of the Rakhine daily-mean precipitation (groupby(\"issue_date\")[\"mean\"].rolling(3, min_periods=1).sum()) compared to 175 mm. Repo naming (mmr_chirps_gefs_mean_daily) and casual description read as a rolling 'mean'; the operational statistic is a SUM of 3 daily means, not a 3-day average — read the mm value and the statistic together."
  - "[conflict] send_email.check_wind_speed_trigger_data lists blobs with prefix 'wind' (matching both wind_exceedance_{date}_{hour}_ecmwf.csv and _cma.csv), sorts, and loads only the LAST one. A day with exceedances from both ECMWF and CMA has one silently dropped from the trigger email — confirmed still present at source_sha b8d84e2 (send_email.py `_todays_blobs`/`check_wind_speed_trigger_data`), unchanged since the prior three ingestions (284cf02 → 5253227 → 3b6ed15 → b8d84e2)."
  - "[conflict] The two halves of the CHIRPS-GEFS step disagree about where the season starts, and one is frozen to a literal year: chirps_gefs.download_recent_chirps_gefs builds its issue-date range from a hard-coded start=f\"2026-03-15\" (chirps_gefs.py:106), while chirps_gefs.process_recent_chirps_gefs uses the year-relative start=f\"{date.year}-03-25\" (chirps_gefs.py:258). From 2027 the download range will keep reaching back to March 2026 (re-listing/retrying every never-published issue date since) instead of restarting with the season. Verified at source_sha b8d84e2; predates this re-ingestion."
  - "[gap] wind_speed_monitoring_cma.download_tracks_cma has no retry/backoff decorator, unlike wind_speed_monitoring_ecmwf.download_tracks_ecmwf (tenacity, 3 attempts, exponential backoff) — noticed on this re-ingestion pass (source_sha b8d84e2). Not documented anywhere as an intentional asymmetry (CMA fetches from blob storage rather than an external FTP, which may make retries less necessary, but nothing in the repo says so)."
  - "[stale] tests/monitoring/test_wind_speed_monitoring.py imports `from src.monitoring.wind_speed_monitoring import plot_storm_track` — a module that does not exist (the repo has only wind_speed_monitoring_ecmwf.py and wind_speed_monitoring_cma.py; plot_storm_track itself now lives in src/utils/utils_windpseed.py). This test file appears to be an orphan left over from before the ECMWF/CMA split and is very likely broken/unrun; test_send_email.py and test_phase_emails.py both import correctly from wind_speed_monitoring_ecmwf and reflect the live layout."
  - "[gap] The prior ingestion of this page (source_sha 284cf02) recorded several discrepancies referencing docs/index.qmd, docs/cma-trigger-analysis.qmd, and notebooks/cma_forecasts.py (a point-in-polygon-vs-distance-reduction conflict, the L2 threshold, and lead-time windows). None of these paths appear anywhere in `git log --all` for this repo — they cannot be verified and have been dropped from this page. Either those files lived in a different repo/location, were purged from history, or the prior ingestion drew on content not actually committed here."
  - "[stale] src/datasources/zma.py (`load_zma`, Cuba ZMI coordinates) and src/datasources/imerg.py:load_imerg_recent (queries `public.imerg WHERE pcode = 'CU'`) are unused Cuba-specific leftovers — not referenced by any Myanmar monitoring/trigger/historical-analysis script found in the repo. Likely copy-paste from another country's cyclone-framework repo; harmless but dead code."
  - "[conflict] The 'invest filter' is an all-or-nothing gate, not a per-storm exclusion. send_email.check_wind_speed_trigger_data computes has_valid_sid = (~sid.str.match(r'^\\d{2}B$')).any() and, if ANY row has a non-invest sid, returns the WHOLE exceedance table — invest rows included — to the email; only when EVERY exceeding row is an unnamed CMA disturbance is the wind alert suppressed. The headline storm name is then taken as df_wind_speed.sid.unique()[0], which can still be the invest id. Describing it as 'excludes invest systems from the wind check' overstates what the code does."
  - "[gap] historical_analysis/load_ecmwf_data.py cannot execute as committed at source_sha b8d84e2 (unchanged since 3b6ed15): line 68 calls run_trigger(..., windspeed_column=\"wind_speed_at_land_forecasted\") but src/utils/utils_fun.py:126 declares the parameter as wind_speed_column (single definition, single call site) — a TypeError before the script reaches its results/hist_forecast_trigger_True_{suff}.csv write. The ECMWF hindcast retrospective quoted under Historical activations therefore predates this regression and is NOT reproducible from the repo at this sha without a one-word fix."
# --- activation history ---
activations: []
# --- escape hatch ---
extra:
  doc_status: non-public
  monitoring_start: "2026-03-01"
  monitoring_start_note: "constants.MONITORING_START_DATE is defined (localised to Asia/Yangon) but grep shows no other file in src/ reads it — it is not visibly enforced as a gate on the live monitoring workflows, which run unconditionally on the GHA cron schedule. Likely vestigial or reserved for dummy-email date display per its own comment; treat 2026-03-01 as an approximate pipeline-live date, not a code-enforced start."
  wind_reduction_formula: "wind_at_land = 0.9807 * exp(-0.003 * min_dist_km) * wind_knots, where wind_knots = 1.05 * (raw_wind_ms * 1.9438444924) — i.e. m/s is converted to knots (from_ms_to_knots), then rescaled from a 10-minute-sustained to a 3-minute-sustained convention (convert_10m_wind_to_3m, x1.05) BEFORE the distance-based reduction is applied (src/utils/utils_windpseed.py, src/utils/utils_fun.py)."
  rainfall_threshold_forecast_mm3d: 175
  rainfall_threshold_observational_mm3d: 250
  action_window_hours: "48-72"
  readiness_window_hours: "72-120"
  trigger_phase_email_logic: "src/monitoring/send_email.py:determine_trigger_phase now computes an explicit phase (readiness 72-120h / action 48-72h / observational <48h / None if >120h) from the median, across ensemble members, of each member's closest-approach time to Myanmar (falling back to CHIRPS-GEFS valid-minus-issue lead time when no cyclone monitoring data exists). This phase only labels the ALERT EMAIL content and subject (via listmonk._PHASE_INTROS) — it does not gate or filter which forecasts count toward the wind/rainfall threshold checks themselves, which still scan the full forecast horizon. This is new since the prior ingestion (source_sha 284cf02) and partially answers that page's open question about whether lead-time windows would ever be enforced."
  invest_filter: "send_email.check_wind_speed_trigger_data suppresses the wind alert when EVERY exceeding storm has a sid matching ^\\d{2}B$ (e.g. '90B') — CMA's convention for unnamed tropical disturbances/invests. The has_valid_sid check is `.any()` over the non-matching rows, so a single named storm re-admits the whole table, invests included; it is a gate on the alert, not a row filter (see discrepancies). New since the prior ingestion."
  aoi_state: "Rakhine (ADM1_PCODE MMR012)"
  historical_archive_cma: "2022-2025 Bay of Bengal TCs; Cyclone Mocha (May 2023) is only storm that would have triggered at the wind threshold within Rakhine ADM1 (first qualifying forecast 2023-05-13 08:00 UTC) — unchanged since the prior ingestion; this repo checkout gives no evidence the CMA historical archive was extended."
  window_axes_note: "n_windows = 2 (wind alert, rainfall alert), but the two windows are NOT differentiated by the time/space/severity vocab: both cover Rakhine ADM1, both are forecast-basis, and neither filters by lead-time in the threshold check itself (only the alert email's phase label uses lead time — see extra.trigger_phase_email_logic). They are independent triggers that differ by INDICATOR (wind vs rainfall), so window_axes is left []."
  schema_strain: "No published doc — framework_doc and framework_doc_date are null; trigger_source set to repo; no PDF text extract was available for this re-ingestion. The two-level (L1/L2) wind design recorded in the prior ingestion has no counterpart in the repo: only one trigger level exists, and 63 kt is an IMD classification bin edge (see discrepancies). window_axes is [] despite 2 windows because the differentiator (indicator: wind vs rainfall) is not in the time/space/severity vocab."
visibility: internal
last_synced: "2026-08-12"
---

# Myanmar Tropical Cyclone — development

> The canonical trigger is the code at `code_ref`; this page explains it, it does not redefine it.

## Summary

Myanmar's cyclone anticipatory action framework targets Rakhine State (ADM1), the historically most-exposed part of the country to high-intensity Bay of Bengal tropical cyclones. The trigger combines a wind-speed forecast from ECMWF and/or CMA (checked against Rakhine after applying a distance-based reduction for overland tracks) with a CHIRPS-GEFS 3-day cumulative rainfall forecast. When either threshold is crossed, an alerting email is dispatched via Listmonk, now labelled by trigger phase (readiness/action/observational) based on forecast lead time; official AA activation notices are sent through a separate channel. The monitoring pipeline has been live since approximately 2026-03-01, running twice-daily GHA workflows, writing to the DEV blob slot. No public framework document has been located; the repo is the authoritative source for the current trigger design. **No PDF extract was available for this re-ingestion** — this page was re-verified against the repo at `source_sha` b8d84e2 and the prior page, not from a framework document.

## Method

**Data flow:**

1. **ECMWF tracks** — fetched every 12 hours from ECMWF FTP as BUFR files via CLIMADA `TCForecast` (retried up to 3x with exponential backoff on transient `TimeoutError`/`OSError` — `tenacity`, `wind_speed_monitoring_ecmwf.download_tracks_ecmwf`; at `b8d84e2` a `climada_petals` bug that masks FTP connection failures as `UnboundLocalError` is re-raised as `OSError` so the retry actually engages). Tracks within a 2000 km buffer of Myanmar are retained. For each track point, minimum distance to Rakhine ADM1 is computed (projected to EPSG:3857 for the distance calc, EPSG:32647/`MMR_UTM` for the buffer). Ensemble members and the deterministic track are both included.

2. **CMA tracks** — fetched from blob storage (`ds-cma-datasharing/cma_ftp/data_out/typhoon/`), WMO WTPQ `.TXT` bulletins parsed by `src/utils/utils_cma.py` into per-forecast-hour rows (position, wind in m/s). Same distance-reduction and spatial-filter pipeline as ECMWF, sharing `src/utils/utils_windpseed.py`.

3. **Wind reduction (shared)** — `utils_windpseed.compute_wind_speed_at_land`: raw wind (m/s) is converted to knots, rescaled from a 10-minute- to a 3-minute-sustained convention (×1.05), then reduced by `wind_at_land = 0.9807 × exp(−0.003 × dist_km) × wind_knots`.

4. **CHIRPS-GEFS rainfall** — daily 16-day forecast GeoTIFFs clipped to Rakhine ADM1; the spatial mean precipitation per valid day is taken, then a **3-day rolling sum** of those daily means (`chirps_gefs.check_chirps_gefs_trigger`). Compared against the 175 mm threshold.

5. **Alerting** — `send_email.py` lists today's blobs under three prefixes — wind exceedance, rainfall exceedance, and storm-in-area-of-interest monitoring (a storm whose closest approach is within `constants.buffer_km` = 500 km of Rakhine) — suppresses the wind alert if *every* exceeding storm is an unnamed CMA "invest" (sid matching `^\d{2}B$`); computes a trigger **phase** (readiness/action/observational) from forecast lead time to land; and dispatches one of two campaign types via Listmonk: a **monitoring email** (`MMR_monitoring_email` — a storm is in the area of interest but no threshold is crossed) or a **trigger email** (`MMR_{phase}_email`, or `MMR_trigger_email` if no phase resolves — one or both thresholds crossed). Every email attaches **both** the storm-track and CHIRPS-GEFS rainfall-forecast plot images (`get_latest_monitoring_plot`, one blob each; a plot missing for today is silently skipped by `listmonk.generate_body_email`). Separate official AA activation notices are sent through a different channel.

## Trigger logic

- **Keys off:** ECMWF and CMA tropical cyclone forecast tracks (wind speed); CHIRPS-GEFS precipitation forecasts.
- **Decision rule (plain language):** A cyclone alert fires if any forecast ensemble member or deterministic track from ECMWF or CMA predicts wind speeds at Rakhine (after unit conversion and reducing for storm distance from land) reaching at least 47 knots. If *every* storm crossing that threshold is an unclassified CMA "invest", the alert is held back; one named storm is enough to release it. A rainfall alert fires if the CHIRPS-GEFS 3-day rolling sum of the Rakhine ADM1 daily-mean precipitation reaches or exceeds 175 mm. Either condition independently triggers an alert email, now labelled with a readiness/action/observational phase based on how close the storm's median forecast approach time is.
- **Activation structure:** Two independent alert conditions (wind OR rainfall), each producing a separate signal; a **trigger** email fires if either threshold is exceeded, and a **monitoring** email if no threshold is crossed but a storm is in the monitoring area (closest approach within 500 km of Rakhine, `constants.buffer_km`).
- **Calibration:** The 47 kt wind threshold is the Cyclonic Storm / Severe Cyclonic Storm boundary on the IMD scale (Severe Cyclonic Storm = 48–63 kt, 3-min sustained; the reduction pipeline converts to a 3-min convention, so the comparison is like-for-like). The repo *does* carry that IMD mapping — `src/datasources/ibtracs.py:45-67` (`categorize_storms`, duplicated at `utils_plot.py:242`) bins storms on the full IMD scale with 47 and 63 kt as bin edges — but only for classifying the historical record; the `constants.py` CAT_LIMITS table is *Saffir-Simpson* and is used for plot labels. What is missing is the **selection basis**: nothing in the repo records why 47 kt was chosen as the trigger, and the CHIRPS-GEFS 175 mm (3-day) threshold likewise has no documented return-period calibration. No second wind level (the "L2 = 63 kt" recorded in the prior ingestion of this page) exists as a trigger anywhere in the repo — 63 kt appears only as the Very Severe Cyclonic Storm bin edge, which may be what that earlier record actually referred to. See discrepancies.
- **Authoritative source:** No published framework PDF; `trigger_source: repo`. No `docs/` or `notebooks/` analysis directory exists in this repo's history — the deployed code in `src/` and the scripts in `historical_analysis/` are the only findable design record, and neither carries a written rationale for the thresholds.
- **Operated by:** OCHA Centre for Humanitarian Data (pipeline runs via GHA in `ocha-dap/ds-aa-mmr-cyclones`).

## Trigger windows

The email-phase logic (`send_email.determine_trigger_phase`) now computes readiness (72–120 h lead time to closest approach) / action (48–72 h) / observational (<48 h) phases from the median ensemble approach time, and labels the alert email accordingly. This does **not** gate the underlying threshold checks — `wind_speed_monitoring_ecmwf.py`/`_cma.py` still scan peak wind across the full forecast horizon regardless of lead time; only the email's phrasing/subject changes. See discrepancies and `extra.trigger_phase_email_logic`.

| window | basis | indicator | threshold | lead time | return period | releases |
|---|---|---|---|---|---|---|
| wind alert | forecast | ECMWF-wind-speed, CMA-wind-speed (distance-reduced at Rakhine) | >= 47 kt at Rakhine ADM1 | any (full forecast horizon) for detection; readiness/action/observational label only on the alert email | not calibrated | trigger email (`MMR_{phase}_email` / `MMR_trigger_email`); official activation notice via separate channel |
| rainfall alert | forecast | CHIRPS-GEFS-3day-rainfall (3-day rolling SUM of Rakhine ADM1 daily-mean precip) | >= 175 mm 3-day rolling sum | 0–16 days | not calibrated | trigger email (same campaign path as the wind alert) |

## Sources & repo completeness

- **Trigger taken from:** `repo` — no published framework PDF was found on ReliefWeb or unocha.org, and no PDF text extract was supplied for this re-ingestion either. A non-public framework document likely exists (confirmed by the email disclaimer language).
- **Repo completeness:** partial — the operational monitoring implements a single wind threshold (47 kt) only, with no recorded rationale for it; the previously-recorded L2 (63 kt) threshold exists only as an IMD classification bin edge, never as a trigger; the rainfall threshold has no documented calibration; the historical CERF-allocation and EM-DAT lookups (`src/data/cerf_data.csv`, `src/data/emdat_mmr.csv`) are absent; the ECMWF hindcast script does not run as committed (bad keyword argument); one test module (`test_wind_speed_monitoring.py`) imports a module that no longer exists.
- **Discrepancies:** see frontmatter. Key open items: (a) no 63 kt trigger threshold exists in the repo, only the IMD bin edge; (b) the wind-exceedance blob-prefix match in `send_email.py` can silently drop an ECMWF-vs-CMA exceedance; (c) the invest filter is an all-or-nothing gate rather than a per-storm exclusion; (d) lead-time windows now label the email phase but still don't filter the underlying threshold detection; (e) `historical_analysis/load_ecmwf_data.py` raises a `TypeError` before writing its results.

## Monitoring

Monitoring runs via five GitHub Actions workflows in `ocha-dap/ds-aa-mmr-cyclones`:

- `run_update_ecmwf.yml` — twice daily (08:00, 20:00 UTC): downloads ECMWF BUFR tracks (retried on transient timeouts), filters to Myanmar region, applies wind reduction, uploads to blob.
- `run_update_cma.yml` — twice daily (08:00, 20:00 UTC): downloads CMA WTPQ bulletins from blob, applies the same wind-reduction pipeline, uploads to blob.
- `run_update_chirps_gefs.yml` — daily (08:50 UTC): downloads 16-day CHIRPS-GEFS GeoTIFFs, clips to Rakhine ADM1, computes the 3-day rolling sum, checks the threshold. Job timeout raised 10 → 25 min at `b8d84e2` because a new issue date means 16 sequential file fetches and the daily run was being cancelled by the old timeout; the per-file HTTP GET also gained a 30 s timeout.
- `run_monitoring.yml` (`send_email.py`) — twice daily (09:00, 20:15 UTC): checks all threshold/monitoring blobs, determines trigger phase, and sends a monitoring or phase-labelled trigger email (with storm-track + rainfall-forecast plots attached) via Listmonk if any alert condition is active or a storm is in the area of interest.
- `slack_bot.yml` — twice daily (09:15, 20:30 UTC): posts GHA workflow run-status summaries plus today's blob-storage signals (cyclone presence, wind exceedance, rainfall exceedance) to a Slack channel via webhook.

The storm-track plot (`utils_windpseed.plot_storm_track`, used by both ECMWF and CMA monitoring) now also draws Myanmar's neighbouring countries as a background layer and highlights the highest-wind-speed track in red (others green), with Rakhine shaded blue — new since the prior ingestion, purely a visualization change with no effect on the trigger. Processed outputs are written to Azure Blob under `projects/ds-aa-mmr-cyclones/processed/` (dev stage).

## Historical activations

Never activated. Monitoring has been live since approximately 2026-03-01; no activation is recorded anywhere in the repo, and a public search (CERF anticipatory-action portfolio, unocha.org, ReliefWeb) turns up no Myanmar cyclone AA framework activation or pre-arranged allocation — the most recent reachable CERF AA portfolio update (as of 15 November 2024) does not list Myanmar at all.

<!-- TODO: this section is INCOMPLETE — a longer-record ECMWF-hindcast retrospective (historical_analysis/load_ecmwf_data.py; output CSV in Drive: CERF Anticipatory Action/Myanmar/Cyclones 2025/results/Trigger_ecmwf_forecast_vs_ibtracs_observed/Rakhine only/hist_forecast_trigger_True_1_94288602.csv — the same script still writes that path at source_sha b8d84e2, but NOTE it now raises a TypeError at line 68 before reaching the write, so the CSV predates that regression and cannot currently be regenerated: see discrepancies) WAS completed: over the 2006–2024 storm universe (22 storms), FOUR storms trigger at the wind threshold ≥47 kt — Nargis 2008 (52.4 kt), Giri 2010 (53.2), Mora 2017 (50.2), Mocha 2023 (78.9). Wind-only: rainfall input hard-set to 0 in that script. Each triggering storm in a distinct year. Fold into this page. Corroborating internal decks (Drive, extracts in ds-knowledge-base-internal): "Myanmar – trigger proposal.pptx" (2025-10-23, id 1V23b9E6R9CQCzSTM7B-kQ1KQt6-ozRBH — analysis from year 2000, 200 km buffer; CERF allocations for 5 cyclones: Komen, Mora, Nargis, Mocha, Giri; states all observed-wind-triggering storms also trigger in historical ECMWF forecasts; Komen 2015 triggers via the RAINFALL condition (confirmed by framework lead 2026-07-15), completing the would-have-triggered set as Nargis 2008, Giri 2010, Komen 2015, Mora 2017, Mocha 2023 — plus Mala 2006 on the OBSERVED-wind basis (in storms_date.pickle and the IBTrACS analysis — note the year ≥ 2006 filter at load_ibtracs_data.py:63 restricts only the plotted storm maps, not the categorised IBTrACS table itself, which is unfiltered; Mala is absent from the 4-row forecast-hindcast CSV because the ECMWF forecast archive doesn't reach April 2006, and got no CERF allocation as it predates CERF AA). Six storms, six distinct years — one storm per year, no multi-storm year; NOTE its rainfall condition is 3-day mean ≥200 mm, vs 175 mm forecast / 250 mm observational in deployed constants.py) and "Myanmar Cyclone Review - IBTrACS" (2025-06-27, id 16A0C5L-GNbfAagc0Z7CXHiSgEWyHA87vNjsDcF7LOlg — Rakhine SCS-or-higher frequency 1-in-1.6 yr, before wind-reduction-at-land filtering). Slide visuals not yet captioned in the internal repo. -->

**Retrospective analysis:** Of 11 Bay of Bengal storms in the 2022–2025 CMA archive, only Cyclone Mocha (May 2023) would have triggered the framework at the wind threshold within Rakhine ADM1 (first qualifying forecast issued 2023-05-13 08:00 UTC). Major historical storms — Nargis (2008), Giri (2010), Mora (2017) — predate the CMA archive and require separate data sourcing for a full return-period estimate.

The `historical_analysis/` scripts also merge CERF allocation amounts and EM-DAT impact figures by storm ID (`src/data/cerf_data.csv`, `src/data/emdat_mmr.csv` — both absent from this checkout), indicating the original trigger was partly calibrated against historical CERF responses and observed impact, but the methodology is not fully documented and cannot be reproduced from the repo alone.

**Storm classification (IMD scale).** The historical analysis (`src/datasources/ibtracs.py:45-67`, `categorize_storms`) categorizes each IBTrACS storm by wind speed at landfall — or, for storms that never make landfall in the area of interest, by the **reduced wind speed at the track point closest to the AOI geometries** — against the full IMD classification table. The 47 kt trigger threshold is the Cyclonic Storm / Severe Cyclonic Storm bin edge here; 63 kt is the next bin edge up but is **not** a trigger level anywhere in the code:

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

**Rainfall join.** IMERG rainfall is joined to the IBTrACS storm record as the **ADM1 daily-mean rainfall for the ADM1 at the max-wind point**, over a **3-day window** — the day before, the day of, and the day after the peak-wind/landfall date (`offsets = [-1, 0, 1]`, `load_imerge_data.py:13`) — **summed** per storm into the column `3days_rain_mean` (`load_imerge_data.py:55-57`). Despite the column name it is a 3-day sum of daily means, the same statistic the deployed CHIRPS-GEFS check uses.

Digested from the retired DSCI Confluence space (archive: `confluence/` in `ds-knowledge-base-internal`).

## Key decisions & rationale

- **Geographic scope (Rakhine only):** Rakhine State has the highest historical exposure to intense Bay of Bengal cyclones making landfall in Myanmar; ADM1-level scope avoids false positives from storms tracking through neighboring states.
- **Two forecast sources (ECMWF + CMA):** Running parallel monitoring against both ECMWF and CMA reduces the risk of a source outage silencing the trigger. CMA provides Bay of Bengal-focused subjective forecasts not available in ECMWF ensemble products.
- **Distance-based wind reduction:** The formula `0.9807 × exp(−0.003 × dist)` captures the rapid decrease in wind speed as a storm approaches land; applying it at each forecast point rather than only at landfall provides a more conservative (earlier) trigger.
- **Dual indicator (wind + rainfall):** Cyclone Mocha demonstrated that extreme rainfall can be severe even if wind speeds at Rakhine ADM1 are below the threshold; the CHIRPS-GEFS rainfall window supplements the wind trigger for slow-moving or rain-heavy systems.
- **Invest exclusion:** Holding back the wind alert when *all* exceeding systems are unnamed CMA "invests" (`^\d{2}B$` storm IDs) avoids sending exceedance emails for disturbances that haven't yet been classified as a named tropical cyclone — a refinement added since the prior ingestion. It is implemented as a gate on the whole alert rather than a per-storm filter, so a mixed batch still reports the invests alongside the named storm (see discrepancies).
- **Monitoring-only email vs official activation:** The Listmonk email system provides near-real-time situational awareness; the decision to trigger official AA action is made via a separate, manual process — reflecting the operational context in Myanmar (conflict-affected setting).

## Changes from previous version

First documented version; no prior *published* version to compare against. Changes **within this development version** since the last KB sync (`source_sha` 284cf02 → 5253227):

- **Trigger-phase-labelled alerting (new):** `send_email.determine_trigger_phase` now classifies each alert as readiness (72–120 h)/action (48–72 h)/observational (<48 h)/none, and `listmonk.generate_body_email` renders phase-specific email copy. This partially answers the prior page's open question about whether the analysis notebooks' lead-time windows would ever reach production — they now shape the *email*, though not the underlying threshold detection.
- **Invest-system filter (new):** wind-exceedance detection now excludes CMA storm IDs matching the unnamed-invest pattern `^\d{2}B$`.
- **Reliability fixes:** ECMWF BUFR download now retries on transient timeout/`OSError` (tenacity, 3 attempts, exponential backoff); a CMA date-parse crash and ECMWF/CMA blob-upload failures were fixed (`cbd27d0`).
- **Plot changes (cosmetic):** storm-track plots now show neighbouring countries and highlight the max-wind-speed track in red; test coverage added for phase-differentiated emails.
- **L2 (63 kt) threshold not traceable as a trigger:** no second wind level exists at 5253227 or 3b6ed15 — it was recorded as analysis-only (not deployed) in the prior ingestion, and the only 63 kt in the repo is the IMD Very Severe Cyclonic Storm bin edge (see discrepancies).
- **Prior discrepancies dropped:** several discrepancies recorded at the last ingestion referenced `docs/index.qmd`, `docs/cma-trigger-analysis.qmd`, and `notebooks/cma_forecasts.py` — none of these paths exist anywhere in this repo's git history (`git log --all`), so they could not be re-verified and have been removed from this page. Flagged for the framework team in case that analysis exists in a different location.

**This re-ingestion (`source_sha` 5253227 → 3b6ed15):** no functional change to the trigger, monitoring code, or workflow schedules — every threshold, formula, blob-prefix behaviour and GHA cron reviewed at 5253227 is unchanged at 3b6ed15 (all re-verified against the public repo at 3b6ed15 in this pass). Page corrections made at review rather than repo changes: the invest filter is an all-or-nothing gate, not a per-storm exclusion; the IMD scale *is* in the repo (`ibtracs.categorize_storms`) and 63 kt is a classification bin edge, not a lost trigger; the IMERG historical rainfall join is a 3-day sum, not a 4-day window; `historical_analysis/load_ecmwf_data.py` raises a `TypeError` as committed; `src/data/emdat_mmr.csv` is missing alongside `cerf_data.csv`; `MIN_EMAIL_DISTANCE` joins the dead-constant list; and `monitoring_period.months` was widened to Apr–Dec to cover monsoon-season rainfall triggers such as Komen (July 2015). `src/datasources/zma.py` and `src/datasources/imerg.py:load_imerg_recent` were confirmed to be unused Cuba-specific leftovers (see discrepancies), not part of the Myanmar trigger.

**This re-ingestion (`source_sha` 3b6ed15 → b8d84e2, no PDF extract available):** no trigger-design or threshold change — the wind/rainfall thresholds, reduction formula, invest filter, phase logic, wind-blob-prefix bug, dead constants, IMD bin table, `load_ecmwf_data.py` `TypeError`, and all five GHA cron schedules were independently re-verified line-by-line at b8d84e2 and are unchanged from 3b6ed15. The range contains exactly **two reliability fixes**, both operational rather than methodological (`git diff 3b6ed15 b8d84e2`: 4 files):

- **ECMWF FTP retry actually engages** (`ad26140`) — `climada_petals`' `fetch_bufr_ftp` raises `UnboundLocalError` (unassigned `con` in its `finally` block) when the initial FTP connection fails, which the tenacity `retry_if_exception_type((TimeoutError, OSError))` decorator did not match, so the download failed on the first attempt instead of retrying. `download_tracks_ecmwf` now translates it to `OSError`; a regression test in `tests/monitoring/test_wind_speed_monitoring_ecmwf.py` pins the retry count.
- **CHIRPS-GEFS workflow no longer times out** (`be69dfd`) — `run_update_chirps_gefs.yml` job timeout 10 → 25 min (a new issue date means 16 sequential lead-time fetches + reprojection + upload, which was reliably exceeding 10 min and being **cancelled every day**), plus a 30 s `requests.get` timeout per file in `chirps_gefs.download_chirps_gefs`.

Two pieces of email-alerting detail, present already but not previously called out on this page: `send_email.py` sends one of **two campaign types** — a monitoring email (`MMR_monitoring_email`, storm in the area of interest but no threshold crossed) vs. a trigger email (`MMR_{phase}_email`/`MMR_trigger_email`) — and every email attaches **both** the storm-track and rainfall-forecast plot images, not just one. Also newly noted at review: `download_tracks_cma` has no retry/backoff decorator, unlike ECMWF's tenacity-wrapped `download_tracks_ecmwf`, and the CHIRPS-GEFS download/process pair disagree on the season-start date with a hard-coded `2026-03-15` on the download side (both in discrepancies). `tests/monitoring/test_rainfall_monitoring.py` and `tests/test_images/generate_storm_track_test_image.py` were **not** added in this range — both predate 3b6ed15 (commits `f0102ec`, `bb6a74c`); the only test change here is the ECMWF retry regression test above.

## Open questions / known issues

- What is the return period of the 47 kt and 175 mm thresholds? No calibration is documented in the repo.
- Was there ever an L2 (63 kt) severity *trigger*, as the prior KB ingestion recorded? No such threshold exists in the current repo (deployed code, tests, or `historical_analysis/`); 63 kt appears only as the Very Severe Cyclonic Storm bin edge in the IMD classification table. Did a two-level design exist outside this repo, or was the earlier record a misreading of that bin edge?
- Should the underlying wind/rainfall threshold *detection* filter by the same lead-time windows (readiness/action) now used to label the alert email, or is checking the full forecast horizon for detection (with lead-time only shaping the email) the intended design?
- `rainfall_alert_level_observational = 250` mm and `MIN_EMAIL_DISTANCE = 1000` remain defined in `constants.py` but are consumed by no script. What was the intended use? (`MONITORING_START_DATE` is likewise defined and never read.)
- Should the invest filter drop invest rows individually rather than gate the whole wind alert? As written, one named storm re-admits every invest in the same batch, and the email's headline storm name can still be an invest id.
- `historical_analysis/load_ecmwf_data.py:68` passes `windspeed_column=` to a function whose parameter is `wind_speed_column` — a one-word fix, but until it lands the wind hindcast underpinning the retrospective can't be re-run.
- `send_email.check_wind_speed_trigger_data`'s blob prefix check `wind` still matches both `wind_exceedance_*_ecmwf.csv` and `_cma.csv`, loading only the alphabetically-last blob. Should ECMWF and CMA exceedances be merged or reported separately instead of one silently overriding the other?
- `tests/monitoring/test_wind_speed_monitoring.py` imports a module (`src.monitoring.wind_speed_monitoring`) that no longer exists — is this test still run anywhere, or is it dead and safe to delete?
- Is there a return period for Cyclone Mocha as a calibration event? The 2022–2025 CMA archive is too short for a robust return-period estimate.
- No framework activation has occurred since monitoring began; is the framework still considered in development, or has it been quietly endorsed pending a document?
- Is `download_tracks_cma` intentionally without the retry/backoff wrapper that `download_tracks_ecmwf` now has, or is this an oversight from when the retry logic was added only to the ECMWF path? (Noted at `source_sha` b8d84e2.)
- Should `chirps_gefs.download_recent_chirps_gefs`'s hard-coded `start="2026-03-15"` be year-relative like the matching `process_recent_chirps_gefs` (`{date.year}-03-25`)? As written, the 2027 season will still re-walk every issue date back to March 2026. Also: are those two dates (15 vs 25 March) meant to differ?
