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
  note: "Bay of Bengal TC season — pre-monsoon (Apr–Jun) and post-monsoon (Oct–Dec) peaks; inferred from basin seasonality (Mocha was May 2023). Page does not state a season window. In practice the GHA schedules run every day of the year (no seasonal cron gating), so this is a hazard-season judgment, not an enforced monitoring window."
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
source_sha: "5253227"
code_ref:
  - src/monitoring/wind_speed_monitoring_ecmwf.py
  - src/monitoring/wind_speed_monitoring_cma.py
  - src/utils/utils_windpseed.py
  - src/monitoring/update_chirps_gefs.py
  - src/datasources/chirps_gefs.py
  - src/monitoring/send_email.py
  - src/utils/constants.py
trigger_source: repo
repo_completeness: partial
discrepancies:
  - "[gap] No published framework PDF found on ReliefWeb or unocha.org (no PDF text extract was available for this re-ingestion either — this page is drafted from the repo and the prior page only). The monitoring email disclaimer ('This email is purely informational and does not serve as an official notice for the anticipatory action framework. Official activation notices are sent in another email.') confirms an endorsed framework exists with separate official comms, but the document is not public."
  - "[gap] The CHIRPS-GEFS rainfall trigger threshold (175 mm 3-day rolling sum, constants.rainfall_alert_level_forecast) has no documented return-period or historical-validation basis in the repo. constants.rainfall_alert_level_observational = 250 mm is defined but not consumed by any script (deployed or historical) — dead configuration, not a live observational check."
  - "[gap] The previously-recorded L2 severity threshold (63 kt, 'Very Severe Cyclonic Storm') is GONE from the repo entirely as of source_sha 5253227 — not in constants.py, not in any deployed monitoring script, and not in any analysis file findable in git history. Only a single wind_speed_alert_level = 47 kt threshold exists now. Cannot tell from the repo alone whether L2 was deliberately dropped from the design or was only ever a stale analysis artifact — flag for the framework team."
  - "[stale] historical_analysis/load_imerge_data.py reads src/data/cerf_data.csv (a CERF-allocation-by-storm-id lookup) to build a cerf_allocation column (load_imerge_data.py:60), but this CSV is absent from the tracked repo (likely gitignored/local-only). load_ecmwf_data.py does NOT read cerf_data.csv directly — it consumes the derived cerf_allocation column via results/df_full_{suff}.csv (an intermediate that is also not in the repo). Either way the CERF allocation join in the historical hindcast comparison is unavailable to reproduce from the repo alone."
  - "[stale] All monitoring/plot scripts (wind_speed_monitoring_ecmwf.py, wind_speed_monitoring_cma.py, utils_windpseed.plot_storm_track, update_chirps_gefs) upload outputs with stage=\"dev\" to projects/ds-aa-mmr-cyclones/processed. The live pipeline writes to and reads from the DEV blob slot, not prod — consistent with status: development, but means no prod-stage artifacts exist; promotion to prod is an outstanding change."
  - "[conflict] The deployed rainfall trigger (chirps_gefs.check_chirps_gefs_trigger) computes a 3-day rolling SUM of the Rakhine daily-mean precipitation (groupby(\"issue_date\")[\"mean\"].rolling(3, min_periods=1).sum()) compared to 175 mm. Repo naming (mmr_chirps_gefs_mean_daily) and casual description read as a rolling 'mean'; the operational statistic is a SUM of 3 daily means, not a 3-day average — read the mm value and the statistic together."
  - "[conflict] send_email.check_wind_speed_trigger_data lists blobs with prefix 'wind' (matching both wind_exceedance_{date}_{hour}_ecmwf.csv and _cma.csv), sorts, and loads only the LAST one. A day with exceedances from both ECMWF and CMA has one silently dropped from the trigger email — confirmed still present at source_sha 5253227 (send_email.py:15-26, sort+load at 23-24), unchanged since the prior ingestion."
  - "[stale] tests/monitoring/test_wind_speed_monitoring.py imports `from src.monitoring.wind_speed_monitoring import plot_storm_track` — a module that does not exist (the repo has only wind_speed_monitoring_ecmwf.py and wind_speed_monitoring_cma.py; plot_storm_track itself now lives in src/utils/utils_windpseed.py). This test file appears to be an orphan left over from before the ECMWF/CMA split and is very likely broken/unrun; test_send_email.py and test_phase_emails.py both import correctly from wind_speed_monitoring_ecmwf and reflect the live layout."
  - "[gap] The prior ingestion of this page (source_sha 284cf02) recorded several discrepancies referencing docs/index.qmd, docs/cma-trigger-analysis.qmd, and notebooks/cma_forecasts.py (a point-in-polygon-vs-distance-reduction conflict, the L2 threshold, and lead-time windows). None of these paths appear anywhere in `git log --all` for this repo — they cannot be verified and have been dropped from this page. Either those files lived in a different repo/location, were purged from history, or the prior ingestion drew on content not actually committed here."
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
  invest_filter: "send_email.check_wind_speed_trigger_data now excludes storms whose sid matches ^\\d{2}B$ (e.g. '90B') — CMA's convention for unnamed tropical disturbances/invests — from counting as a wind-threshold exceedance for the trigger email, via a has_valid_sid check. New since the prior ingestion."
  aoi_state: "Rakhine (ADM1_PCODE MMR012)"
  historical_archive_cma: "2022-2025 Bay of Bengal TCs; Cyclone Mocha (May 2023) is only storm that would have triggered at the wind threshold within Rakhine ADM1 (first qualifying forecast 2023-05-13 08:00 UTC) — unchanged since the prior ingestion; this repo checkout gives no evidence the CMA historical archive was extended."
  window_axes_note: "n_windows = 2 (wind alert, rainfall alert), but the two windows are NOT differentiated by the time/space/severity vocab: both cover Rakhine ADM1, both are forecast-basis, and neither filters by lead-time in the threshold check itself (only the alert email's phase label uses lead time — see extra.trigger_phase_email_logic). They are independent triggers that differ by INDICATOR (wind vs rainfall), so window_axes is left []."
  schema_strain: "No published doc — framework_doc and framework_doc_date are null; trigger_source set to repo; no PDF text extract was available for this re-ingestion. The two-level (L1/L2) wind design recorded in the prior ingestion is no longer traceable in the repo at all (see discrepancies) — window_axes is [] despite 2 windows because the differentiator (indicator: wind vs rainfall) is not in the time/space/severity vocab."
visibility: internal
last_synced: "2026-07-24"
---

# Myanmar Tropical Cyclone — development

> The canonical trigger is the code at `code_ref`; this page explains it, it does not redefine it.

## Summary

Myanmar's cyclone anticipatory action framework targets Rakhine State (ADM1), the historically most-exposed part of the country to high-intensity Bay of Bengal tropical cyclones. The trigger combines a wind-speed forecast from ECMWF and/or CMA (checked against Rakhine after applying a distance-based reduction for overland tracks) with a CHIRPS-GEFS 3-day cumulative rainfall forecast. When either threshold is crossed, an alerting email is dispatched via Listmonk, now labelled by trigger phase (readiness/action/observational) based on forecast lead time; official AA activation notices are sent through a separate channel. The monitoring pipeline has been live since approximately 2026-03-01, running twice-daily GHA workflows, writing to the DEV blob slot. No public framework document has been located; the repo is the authoritative source for the current trigger design. **No PDF extract was available for this re-ingestion** — this page was re-drafted from the repo at `source_sha` 5253227 and the prior page, not from a framework document.

## Method

**Data flow:**

1. **ECMWF tracks** — fetched every 12 hours from ECMWF FTP as BUFR files via CLIMADA `TCForecast` (now retried up to 3x with exponential backoff on transient timeout/OSError, added since the prior ingestion — `tenacity`, `wind_speed_monitoring_ecmwf.download_tracks_ecmwf`). Tracks within a 2000 km buffer of Myanmar are retained. For each track point, minimum distance to Rakhine ADM1 is computed (projected to EPSG:3857 for the distance calc, EPSG:32647/`MMR_UTM` for the buffer). Ensemble members and the deterministic track are both included.

2. **CMA tracks** — fetched from blob storage (`ds-cma-datasharing/cma_ftp/data_out/typhoon/`), WMO WTPQ `.TXT` bulletins parsed by `src/utils/utils_cma.py` into per-forecast-hour rows (position, wind in m/s). Same distance-reduction and spatial-filter pipeline as ECMWF, sharing `src/utils/utils_windpseed.py`.

3. **Wind reduction (shared)** — `utils_windpseed.compute_wind_speed_at_land`: raw wind (m/s) is converted to knots, rescaled from a 10-minute- to a 3-minute-sustained convention (×1.05), then reduced by `wind_at_land = 0.9807 × exp(−0.003 × dist_km) × wind_knots`.

4. **CHIRPS-GEFS rainfall** — daily 16-day forecast GeoTIFFs clipped to Rakhine ADM1; the spatial mean precipitation per valid day is taken, then a **3-day rolling sum** of those daily means (`chirps_gefs.check_chirps_gefs_trigger`). Compared against the 175 mm threshold.

5. **Alerting** — `send_email.py` checks blob prefixes for wind exceedance, rainfall exceedance, and storm-in-area-of-interest monitoring; excludes unnamed CMA "invest" systems (sid matching `^\d{2}B$`) from the wind check; computes a trigger **phase** (readiness/action/observational) from forecast lead time to land; and dispatches a phase-labelled email via Listmonk. Separate official AA activation notices are sent through a different channel.

## Trigger logic

- **Keys off:** ECMWF and CMA tropical cyclone forecast tracks (wind speed); CHIRPS-GEFS precipitation forecasts.
- **Decision rule (plain language):** A cyclone alert fires if any forecast ensemble member or deterministic track from ECMWF or CMA predicts wind speeds at Rakhine (after unit conversion and reducing for storm distance from land) reaching at least 47 knots, excluding unclassified "invest" systems. A rainfall alert fires if the CHIRPS-GEFS 3-day rolling sum of the Rakhine ADM1 daily-mean precipitation reaches or exceeds 175 mm. Either condition independently triggers an alert email, now labelled with a readiness/action/observational phase based on how close the storm's median forecast approach time is.
- **Activation structure:** Two independent alert conditions (wind OR rainfall), each producing a separate signal; the alert email fires if a storm is in the monitoring area or either threshold is exceeded.
- **Calibration:** The 47 kt wind threshold sits at the Cyclonic Storm / Severe Cyclonic Storm boundary on the IMD scale (IMD Severe Cyclonic Storm = 48–63 kt, 3-min sustained; the reduction pipeline converts to a 3-min convention, so the comparison is like-for-like). Note the repo does not document this IMD mapping — `constants.py` carries a *Saffir-Simpson* CAT_LIMITS table (TS 34, Cat 1 64, …), not IMD categories, and the threshold-selection basis is not documented in the repo. The CHIRPS-GEFS rainfall threshold of 175 mm (3-day) has no documented return-period calibration. The second severity level (63 kt, "L2") recorded in the prior ingestion of this page is no longer findable anywhere in the repo — see discrepancies.
- **Authoritative source:** No published framework PDF; `trigger_source: repo`. No `docs/` or `notebooks/` analysis directory exists in this repo's history — the deployed code in `src/` is the only findable design record.
- **Operated by:** OCHA Centre for Humanitarian Data (pipeline runs via GHA in `ocha-dap/ds-aa-mmr-cyclones`).

## Trigger windows

The email-phase logic (`send_email.determine_trigger_phase`) now computes readiness (72–120 h lead time to closest approach) / action (48–72 h) / observational (<48 h) phases from the median ensemble approach time, and labels the alert email accordingly. This does **not** gate the underlying threshold checks — `wind_speed_monitoring_ecmwf.py`/`_cma.py` still scan peak wind across the full forecast horizon regardless of lead time; only the email's phrasing/subject changes. See discrepancies and `extra.trigger_phase_email_logic`.

| window | basis | indicator | threshold | lead time | return period | releases |
|---|---|---|---|---|---|---|
| wind alert | forecast | ECMWF-wind-speed, CMA-wind-speed (distance-reduced at Rakhine) | >= 47 kt at Rakhine ADM1 | any (full forecast horizon) for detection; readiness/action/observational label only on the alert email | not calibrated | monitoring email (phase-labelled); official activation notice via separate channel |
| rainfall alert | forecast | CHIRPS-GEFS-3day-rainfall (3-day rolling SUM of Rakhine ADM1 daily-mean precip) | >= 175 mm 3-day rolling sum | 0–16 days | not calibrated | monitoring email |

## Sources & repo completeness

- **Trigger taken from:** `repo` — no published framework PDF was found on ReliefWeb or unocha.org, and no PDF text extract was supplied for this re-ingestion either. A non-public framework document likely exists (confirmed by the email disclaimer language).
- **Repo completeness:** partial — the operational monitoring implements a single wind threshold (47 kt) only; the previously-recorded L2 (63 kt) threshold is untraceable in the current repo; the rainfall threshold has no documented calibration; the historical CERF allocation data (`cerf_data.csv`) is absent; one test module (`test_wind_speed_monitoring.py`) imports a module that no longer exists.
- **Discrepancies:** see frontmatter. Key open items: (a) the L2 threshold's disappearance from the repo entirely; (b) the wind-exceedance blob-prefix match in `send_email.py` can silently drop an ECMWF-vs-CMA exceedance; (c) lead-time windows now label the email phase but still don't filter the underlying threshold detection.

## Monitoring

Monitoring runs via five GitHub Actions workflows in `ocha-dap/ds-aa-mmr-cyclones`:

- `run_update_ecmwf.yml` — twice daily (08:00, 20:00 UTC): downloads ECMWF BUFR tracks (retried on transient timeouts), filters to Myanmar region, applies wind reduction, uploads to blob.
- `run_update_cma.yml` — twice daily (08:00, 20:00 UTC): downloads CMA WTPQ bulletins from blob, applies the same wind-reduction pipeline, uploads to blob.
- `run_update_chirps_gefs.yml` — daily (08:50 UTC): downloads 16-day CHIRPS-GEFS GeoTIFFs, clips to Rakhine ADM1, computes the 3-day rolling sum, checks the threshold.
- `run_monitoring.yml` (`send_email.py`) — twice daily (09:00, 20:15 UTC): checks all threshold/monitoring blobs, determines trigger phase, and sends a phase-labelled Listmonk email if any alert condition is active or a storm is in the area of interest.
- `slack_bot.yml` — twice daily (09:15, 20:30 UTC): posts status summaries to a Slack channel.

The storm-track plot (`utils_windpseed.plot_storm_track`, used by both ECMWF and CMA monitoring) now also draws Myanmar's neighbouring countries as a background layer and highlights the highest-wind-speed track in red (others green), with Rakhine shaded blue — new since the prior ingestion, purely a visualization change with no effect on the trigger. Processed outputs are written to Azure Blob under `projects/ds-aa-mmr-cyclones/processed/` (dev stage).

## Historical activations

Never activated (framework has been live since approximately 2026-03-01; no CERF/AA activations recorded post-endorsement).

<!-- TODO: this section is INCOMPLETE — a longer-record ECMWF-hindcast retrospective (historical_analysis/load_ecmwf_data.py; output CSV in Drive: CERF Anticipatory Action/Myanmar/Cyclones 2025/results/Trigger_ecmwf_forecast_vs_ibtracs_observed/Rakhine only/hist_forecast_trigger_True_1_94288602.csv — confirmed this output path is still produced by the same script at source_sha 5253227) WAS completed: over the 2006–2024 storm universe (22 storms), FOUR storms trigger at the wind threshold ≥47 kt — Nargis 2008 (52.4 kt), Giri 2010 (53.2), Mora 2017 (50.2), Mocha 2023 (78.9). Wind-only: rainfall input hard-set to 0 in that script. Each triggering storm in a distinct year. Fold into this page. Corroborating internal decks (Drive, extracts in ds-knowledge-base-internal): "Myanmar – trigger proposal.pptx" (2025-10-23, id 1V23b9E6R9CQCzSTM7B-kQ1KQt6-ozRBH — analysis from year 2000, 200 km buffer; CERF allocations for 5 cyclones: Komen, Mora, Nargis, Mocha, Giri; states all observed-wind-triggering storms also trigger in historical ECMWF forecasts; Komen 2015 triggers via the RAINFALL condition (confirmed by framework lead 2026-07-15), completing the would-have-triggered set as Nargis 2008, Giri 2010, Komen 2015, Mora 2017, Mocha 2023 — plus Mala 2006 on the OBSERVED-wind basis (in storms_date.pickle and the IBTrACS analysis, which starts at year ≥2006 per load_ibtracs_data.py:63; Mala is absent from the 4-row forecast-hindcast CSV because the ECMWF forecast archive doesn't reach April 2006, and got no CERF allocation as it predates CERF AA). Six storms, six distinct years — one storm per year, no multi-storm year; NOTE its rainfall condition is 3-day mean ≥200 mm, vs 175 mm forecast / 250 mm observational in deployed constants.py) and "Myanmar Cyclone Review - IBTrACS" (2025-06-27, id 16A0C5L-GNbfAagc0Z7CXHiSgEWyHA87vNjsDcF7LOlg — Rakhine SCS-or-higher frequency 1-in-1.6 yr, before wind-reduction-at-land filtering). Slide visuals not yet captioned in the internal repo. -->

**Retrospective analysis:** Of 11 Bay of Bengal storms in the 2022–2025 CMA archive, only Cyclone Mocha (May 2023) would have triggered the framework at the wind threshold within Rakhine ADM1 (first qualifying forecast issued 2023-05-13 08:00 UTC). Major historical storms — Nargis (2008), Giri (2010), Mora (2017) — predate the CMA archive and require separate data sourcing for a full return-period estimate.

The `historical_analysis/` scripts also merge CERF allocation amounts by storm ID (`src/data/cerf_data.csv`, absent from this checkout), indicating the original trigger was partly calibrated against historical CERF responses, but the methodology is not fully documented and cannot be reproduced from the repo alone.

## Key decisions & rationale

- **Geographic scope (Rakhine only):** Rakhine State has the highest historical exposure to intense Bay of Bengal cyclones making landfall in Myanmar; ADM1-level scope avoids false positives from storms tracking through neighboring states.
- **Two forecast sources (ECMWF + CMA):** Running parallel monitoring against both ECMWF and CMA reduces the risk of a source outage silencing the trigger. CMA provides Bay of Bengal-focused subjective forecasts not available in ECMWF ensemble products.
- **Distance-based wind reduction:** The formula `0.9807 × exp(−0.003 × dist)` captures the rapid decrease in wind speed as a storm approaches land; applying it at each forecast point rather than only at landfall provides a more conservative (earlier) trigger.
- **Dual indicator (wind + rainfall):** Cyclone Mocha demonstrated that extreme rainfall can be severe even if wind speeds at Rakhine ADM1 are below the threshold; the CHIRPS-GEFS rainfall window supplements the wind trigger for slow-moving or rain-heavy systems.
- **Invest exclusion:** Filtering out unnamed CMA "invest" systems (`^\d{2}B$` storm IDs) from the wind-alert trigger avoids sending exceedance emails for disturbances that haven't yet been classified as a named tropical cyclone — a refinement added since the prior ingestion.
- **Monitoring-only email vs official activation:** The Listmonk email system provides near-real-time situational awareness; the decision to trigger official AA action is made via a separate, manual process — reflecting the operational context in Myanmar (conflict-affected setting).

## Changes from previous version

First documented version; no prior *published* version to compare against. Changes **within this development version** since the last KB sync (`source_sha` 284cf02 → 5253227):

- **Trigger-phase-labelled alerting (new):** `send_email.determine_trigger_phase` now classifies each alert as readiness (72–120 h)/action (48–72 h)/observational (<48 h)/none, and `listmonk.generate_body_email` renders phase-specific email copy. This partially answers the prior page's open question about whether the analysis notebooks' lead-time windows would ever reach production — they now shape the *email*, though not the underlying threshold detection.
- **Invest-system filter (new):** wind-exceedance detection now excludes CMA storm IDs matching the unnamed-invest pattern `^\d{2}B$`.
- **Reliability fixes:** ECMWF BUFR download now retries on transient timeout/`OSError` (tenacity, 3 attempts, exponential backoff); a CMA date-parse crash and ECMWF/CMA blob-upload failures were fixed (`cbd27d0`).
- **Plot changes (cosmetic):** storm-track plots now show neighbouring countries and highlight the max-wind-speed track in red; test coverage added for phase-differentiated emails.
- **L2 (63 kt) threshold vanished:** untraceable anywhere in the repo at 5253227 (see discrepancies) — was recorded as analysis-only (not deployed) in the prior ingestion; now not findable at all.
- **Prior discrepancies dropped:** several discrepancies recorded at the last ingestion referenced `docs/index.qmd`, `docs/cma-trigger-analysis.qmd`, and `notebooks/cma_forecasts.py` — none of these paths exist anywhere in this repo's git history (`git log --all`), so they could not be re-verified and have been removed from this page. Flagged for the framework team in case that analysis exists in a different location.

## Open questions / known issues

- What is the return period of the 47 kt and 175 mm thresholds? No calibration is documented in the repo.
- What happened to the L2 (63 kt) severity threshold recorded in the prior KB ingestion? It is not findable anywhere in the current repo (deployed code, tests, or `historical_analysis/`). Was it deliberately dropped, or did it only ever live in analysis material outside this repo?
- Should the underlying wind/rainfall threshold *detection* filter by the same lead-time windows (readiness/action) now used to label the alert email, or is checking the full forecast horizon for detection (with lead-time only shaping the email) the intended design?
- `rainfall_alert_level_observational = 250` mm remains defined in `constants.py` but is not consumed by any script. What was the intended use?
- `send_email.check_wind_speed_trigger_data`'s blob prefix check `wind` still matches both `wind_exceedance_*_ecmwf.csv` and `_cma.csv`, loading only the alphabetically-last blob. Should ECMWF and CMA exceedances be merged or reported separately instead of one silently overriding the other?
- `tests/monitoring/test_wind_speed_monitoring.py` imports a module (`src.monitoring.wind_speed_monitoring`) that no longer exists — is this test still run anywhere, or is it dead and safe to delete?
- Is there a return period for Cyclone Mocha as a calibration event? The 2022–2025 CMA archive is too short for a robust return-period estimate.
- No framework activation has occurred since monitoring began; is the framework still considered in development, or has it been quietly endorsed pending a document?
