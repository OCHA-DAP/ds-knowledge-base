---
content_type: framework
framework: npl-flooding
version: draft-geoglows
status: development
valid_until: null
country_iso3: NPL
hazard: flood
admin_level: 3
geographic_scope:
  - "NPL/Koshi Province/Sunsari district — Chatara gauge, Koshi river (in scope of the endorsed 2025 framework)"
  - "NPL/Karnali — Chisapani gauge, Karnali river (out of endorsed 2025 scope; carried for cross-source evaluation only)"
data_sources:
  - GEOGloWS-v2
  - GloFAS
  - GRRR
  - DHM
trigger_facets:
  basis: forecast
  calibration: return-period
  indicators: [discharge-RP, GEOGloWS-streamflow, GRRR-streamflow, DHM-bulletin]
  n_windows: 2
  window_axes: [time]
monitoring_period:
  months: [6, 7, 8, 9]
  source: stated
  note: "Nepal monsoon flood season in the Koshi basin (Jun-Sep). Unchanged from the endorsed 2025 design; this dev work re-evaluates the forecast DATA SOURCE behind the existing readiness/action windows, not the season or the windows themselves. No live monitoring runs from this work."
supersedes: "2025-08-25"
# --- funding & scope ---
all_in: true
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
raw_extract: null
# --- live system ---
operated_by: null
apps: []
depends_on: []
# --- source repo & reconciliation ---
source_repo: ocha-dap/ds-aa-npl-flooding
source_branch: main
source_sha: cff4aee
code_ref:
  - book/
  - book/05-event-detection.qmd
  - book/06-forecast-vs-retro.qmd
  - book/07-where-does-geoglows-fit.qmd
  - analysis/02.0_google_review_historical.ipynb
  - analysis/07_forecast_zarr_direct.py
  - src/datasources/grrr.py
  - src/datasources/geoglows_data.py
  - src/constants.py
  - src/utils.py
trigger_source: repo
repo_completeness:
  analysis: full
  deployed_code: lost
discrepancies:
  - "[gap] NO PROPOSED REPLACEMENT TRIGGER — This dev work is an EVALUATION of candidate streamflow sources (GEOGloWS v2, with GloFAS and Google GRRR cross-compared), not a revised trigger spec. Its conclusion (book/07-where-does-geoglows-fit.qmd) is to NOT adopt GEOGloWS. There is no new threshold, return period, or probability proposed to replace the endorsed 2025 GloFAS readiness trigger; the endorsed 50%/RP5-at-Chatara design stands as the baseline this development work builds from."
  - "[conflict] GEOGloWS PUBLISHED RPs ARE FORECAST-UNUSABLE — book/06 shows the GEOGloWS v2 operational forecast runs at ~half the retrospective magnitude at EVERY lead day (forecast ≈ retro/2; Q-Q log-correlation 0.91-0.97). The published RP2 at Chatara (14,459 m³/s, retrospective-only LP3 fit) is never reached by the ensemble mean across the ~22-month archive (max fc_avg = 9,016 m³/s; only 23 of 10,005 (date,lead) cells have ANY member exceed RP2). An ensemble-mean GEOGloWS trigger on the published RPs would never fire. This is the binding constraint against GEOGloWS."
  - "[gap] NO GEOGloWS REFORECAST ARCHIVE — GEOGloWS v2 publishes a 1940-present retrospective but NO multi-year reforecast archive (only ~22 months of live forecasts, ~670 dates). Lead-time-dependent skill (the exceedance-probability-at-fixed-leadtime calibration the AA trigger needs) cannot be fit. This is a structural gap, not a tuning issue (book/01, book/06)."
  - "[stale] GEOGloWS RP2 (14,459 m³/s at Chatara) vs GloFAS dashboard RP2 (8,113 m³/s) — large cross-source magnitude divergence (+78%) driven by LP3 vs Gumbel, 86-yr vs 44-yr record, and RAPID-routing vs LISFLOOD model differences. RP-based triggers normalize frequency by construction (book/03), so this changes the threshold VALUE, not the trigger count — but it makes GEOGloWS's published thresholds non-interchangeable with the framework's GloFAS thresholds."
  - "[conflict] GEOGloWS FAILS DHM EVENT-DETECTION — Against observed DHM danger-level crossings (book/05), GEOGloWS RP2 detects 1/9 Chatara and 0/7 Chisapani events; SFDC bias-correction does not change either count. GloFAS detects 2/9 and 5/7. GEOGloWS does not improve on the incumbent GloFAS at any cell. At Chisapani the 2013/2014 record floods register as ordinary monsoon flow in the GEOGloWS retrospective (peaks below its own RP2) — a structural mass-deficiency, not a threshold problem."
  - "[gap] GRRR IS THE STRONGEST CANDIDATE BUT UN-VALIDATED — The cross-comparison surfaces (tangentially) that Google GRRR matches 6/7 DHM crossings at Chisapani (RP2) — better than GloFAS (5/7) and far better than GEOGloWS (0/7); 12/16 matches across both stations and both RPs vs GloFAS 9/16. BUT this used the empirical-quantile RP convention borrowed from notebook 02.0, not GRRR's own published RPs, and only over the DHM record (ends 2012 Chatara / 2015 Chisapani). A purpose-built GRRR validation is named as the next concrete work item but has NOT been done. No GRRR trigger is specified."
  - "[stale] CHISAPANI / KARNALI IS OUT OF ENDORSED SCOPE — The endorsed 2025 framework covers Koshi (Chatara) only; constants.py and the whole evaluation also carry Chisapani (Karnali). Here Chisapani is retained DELIBERATELY for cross-source evaluation (it is where GRRR most outperforms GloFAS), and is relevant only IF a Karnali trigger is ever reintroduced. It is not part of the live framework."
  - "[stale] CHISAPANI REACH GEOGRAPHICALLY UNVERIFIED — The GEOGloWS Chisapani reach (441112306) was matched on upstream area + stream order, NOT a verified coordinate lookup (book/02, book/05). A coordinate getriverid at the gauge returns small tributaries. The 0/7 Chisapani failure could be partly reach-misalignment rather than pure product deficiency — book/05 cannot fully separate the two. Documented as 'not ruled out'."
  - "[stale] CHATARA glofas_rp5 = 10,306 m³/s in constants.py vs 10,300 m³/s in the 2025 PDF — same 6 m³/s rounding discrepancy carried from the endorsed page; the dashboard value is authoritative. Informational only; not touched by this evaluation."
  - "[gap] NO DEPLOYMENT / NO LIVE MONITORING — There is no deployed app or monitoring pipeline in this repo; the live 2025 trigger is monitored MANUALLY by CHD/RCO on GloFAS + DHM bulletins. This evaluation is analysis-only. The endorsed GloFAS trigger remains the operational design while this R&D continues."
  - "[stale] DEV-SLOT PERSISTENCE — constants.py pins BLOB_STAGE=\"dev\" and BLOB_PREFIX=\"ds-aa-npl-flooding/processed/geoglows\". All GEOGloWS retrospective/return-period/forecast-leadtime parquets are read from and written to the DEV blob stage (src/utils.py load_geoglows_retro / load_geoglows_retro_corrected); nothing is promoted to prod. Confirms exploratory-only status; the book renders against dev-slot cached data."
  - "[stale] SAME REPO SNAPSHOT AS THE ENDORSED PAGE — main HEAD here is cff4aee, the SAME SHA the endorsed 2025-08-25 page reflects (the geoglows-evaluation work merged via PR #2 IS on main at cff4aee). This dev version is not a separate branch ahead of the endorsed snapshot; it is a different READING of the same repo — treating the GEOGloWS/GRRR evaluation as the forward-looking R&D subject rather than as discrepancies against the endorsed GloFAS trigger."
# --- activation history ---
activations: []
# --- escape hatch ---
extra:
  dev_status: "In-development R&D successor to the 2025-08-25 endorsed version. NOT a revised trigger: it is a candidate-source evaluation (GEOGloWS v2, cross-compared with GloFAS and Google GRRR) toward a possible future trigger revision. No published framework PDF; no proposed thresholds. Current verdict: do not adopt GEOGloWS; GRRR at Chisapani is the most promising lead and needs purpose-built validation. The endorsed GloFAS/DHM 2025 trigger remains operational."
  what_was_evaluated: "GEOGloWS v2 (1940-present retrospective + 52-member 15-day ensemble forecast, ~22-month live archive) as a trigger source. GloFAS (incumbent) and Google GRRR carried as reference signals. DHM observed water-level danger-level crossings (Chatara to 2012, Chisapani to 2015) as ground truth."
  grrr_finding: "Google GRRR matched 6/7 DHM crossings at Chisapani RP2 (best of any source), 12/16 across both stations and RPs vs GloFAS 9/16, GEOGloWS 2/16. Tangential to the GEOGloWS question; flagged as the next thing to evaluate properly, especially if a Karnali trigger is reintroduced."
  next_work_items: "Per book/07: (1) do not adopt GEOGloWS; (2) acquire a rating curve for Chatara & Chisapani to unlock geoglows.bias.correct_historical() and make DHM water level comparable to model discharge; (3) if GEOGloWS is ever used in a confirmation role, calibrate from the forecast archive, not the published retrospective RPs; (4) purpose-built GRRR validation using GRRR's own published RPs over the full DHM record; (5) re-run the evaluation if GEOGloWS adds reforecasts (v3)."
  schema_strain: "framework_doc null and trigger_source repo (no PDF for this dev work). prearranged_funding_usd null (no envelope endorsed for this version). The schema's per-window trigger spec is a weak fit: this is an evaluation of a data SOURCE for the existing windows, not a new window design — so n_windows/window_axes/monitoring_period carry over the endorsed 2025 readiness/action structure unchanged, and the substance lives in discrepancies + extra. Flagged rather than forced."
  relationship_to_endorsed: "supersedes 2025-08-25 in the version-lineage sense (this is the active forward work), but it does NOT propose new trigger parameters. The endorsed 2025 GloFAS readiness (50% @ RP5, Chatara) + DHM action trigger remains authoritative and operational until/unless a revision is endorsed."
visibility: public
last_synced: "2026-06-30"
---

# Nepal Flood — draft-geoglows (development)

> The **in-development successor** to the 2025-08-25 endorsed version (no published framework doc yet — `trigger_source: repo`). Its current substance is a data-source evaluation (GEOGloWS v2, cross-compared with GloFAS and Google GRRR) toward a future trigger revision — **no new trigger parameters are proposed yet**, so the endorsed GloFAS/DHM trigger remains the operational baseline this work builds from.
> The canonical content is the code/analysis at `code_ref` (chiefly the Quarto book); this page explains it, it does not redefine a trigger.

## Summary

This is the framework's **current in-development version** — the forward-looking work on the repo's `main` branch (SHA `cff4aee`, the same snapshot the endorsed [2025-08-25 page](2025-08-25.md) reflects). It supersedes 2025-08-25 in the version lineage but **has not yet proposed new trigger parameters**: so far it is a systematic evaluation of whether **GEOGloWS v2** streamflow could serve as (or strengthen) the framework's forecast trigger source, with **GloFAS** (the incumbent) and **Google GRRR** carried as reference signals and **DHM** observed danger-level crossings as ground truth. The evaluation lives in a Quarto book (`book/`) and supporting notebooks. Its bottom line is **do not adopt GEOGloWS as a trigger source**: GEOGloWS has no multi-year reforecast archive (so lead-time skill cannot be calibrated), its operational forecast runs at ~half retrospective magnitude so its published return-period thresholds can never fire on the forecast, and it underperforms GloFAS against observed DHM events (1/9 Chatara, 0/7 Chisapani). The most useful by-product is a **tangential GRRR finding** — Google GRRR matches 6/7 DHM crossings at Chisapani (Karnali), the best of any source — flagged as the next concrete thing to validate, especially if a Karnali trigger is ever reintroduced. No new framework PDF exists; no replacement thresholds are proposed; the endorsed 2025 GloFAS readiness + DHM action trigger remains authoritative and operational.

## Method

The evaluation chains four streamflow representations of the same two gauges and tests them against observations:

1. **Candidate (GEOGloWS v2):** 1940-present ERA5-forced RAPID retrospective on the TDX-Hydro network, plus the 52-member 15-day ensemble forecast (only ~22 months / ~670 dates of live archive retained — no reforecasts). Reaches: Chatara/Koshi `441135650` (found by coordinate lookup), Chisapani/Karnali `441112306` (found by upstream-area query; coordinate lookups returned tributaries). Return periods both as published (Log-Pearson III) and recomputed empirically, with and without the built-in SFDC bias correction.
2. **Incumbent (GloFAS):** Copernicus-dashboard Gumbel RPs (Chatara RP2 8,113 / RP5 10,306; Chisapani RP2 5,664 / RP5 6,797 m³/s) and the reanalysis time series.
3. **Reference (Google GRRR):** reanalysis + reforecast pulled from `gs://flood-forecasting/...` via `src/datasources/grrr.py`; empirical-quantile RPs (notebook 02.0 convention).
4. **Ground truth (DHM):** observed water-level danger-level crossings (Chatara danger 7.0 m, record to 2012; Chisapani 10.5 m, record to 2015).

Each model's RP-exceedance days are collapsed to events (`src/utils.py collapse_to_events`, 7-day gap) and matched to DHM crossings within ±7 days (`match_events`). A separate forecast-vs-retrospective magnitude study (`book/06`, `analysis/07_forecast_zarr_direct.py`) pulls ~20,000 GEOGloWS forecast slices from per-date Zarr stores and compares ensemble-mean forecast to retrospective on the same valid date, by lead day.

## Trigger logic

- **Keys off:** nothing new — the **endorsed 2025 trigger is unchanged** (GloFAS 7-day ensemble at Chatara for readiness; DHM 3-day flood bulletin for action). This work asks only whether a *different forecast source* should feed those windows in a future revision.
- **Decision rule (plain language):** unchanged from the endorsed version. The R&D question is "could GEOGloWS (or GRRR) replace or back up GloFAS in the readiness window?" — and the answer reached for GEOGloWS is no.
- **Activation structure:** unchanged two-stage readiness→action design (carried over for facet completeness; not modified here).
- **Calibration:** the evaluation IS a calibration study. Key negative results: (a) GEOGloWS published RP2 at Chatara (14,459 m³/s) is never reached by the ensemble-mean forecast (max 9,016 m³/s over the archive); (b) forecast ≈ retro/2 at every lead day (so retrospective-derived thresholds are a category error on the forecast); (c) no reforecasts ⇒ no lead-time skill calibration; (d) GEOGloWS detects 1/9 (Chatara) and 0/7 (Chisapani) DHM events, vs GloFAS 2/9 and 5/7. No replacement threshold is proposed.
- **Authoritative source:** none for this dev work — no published PDF. The endorsed authority remains the [2025-08-25 framework PDF](2025-08-25.md). The repo book is the source for this evaluation.
- **Operated by:** the live 2025 trigger is monitored manually by CHD/RCO Nepal on GloFAS + DHM. This evaluation does not run anything live.

## Trigger windows

**Counting rule:** The endorsed two-window design (readiness, action) is carried over unchanged — this work evaluates the data source feeding the *readiness* window, it does not add or redesign windows. `n_windows = 2` reflects the inherited structure, not a new proposal.

| window | basis | indicator (endorsed) | candidate source under evaluation | evaluation verdict |
|---|---|---|---|---|
| readiness | forecast | GloFAS ensemble discharge at Chatara, ≥50% prob > RP5 (10,300 m³/s), 7-day lead | GEOGloWS v2 forecast (cross-compared with GRRR) | **Reject GEOGloWS** — no reforecasts; forecast≈retro/2 so published RPs never fire; 1/9 DHM events vs GloFAS 2/9. GRRR not yet validated for Chatara (1/9, comparable to GEOGloWS). Keep GloFAS. |
| action | forecast (bulletin) | DHM 3-day flood-forecast bulletin (3 qualitative conditions) | not under evaluation here | unchanged from endorsed 2025 design |

(No replacement thresholds, return periods, or probabilities are proposed by this work. The endorsed values are shown for context only.)

## Sources & repo completeness

- **Trigger taken from:** repo (`main` @ `cff4aee`) — but as an *evaluation*, not a trigger spec. The authoritative trigger is still the endorsed 2025 PDF.
- **Repo completeness:** `{analysis: full, deployed_code: lost}` — the GEOGloWS/GRRR/GloFAS-vs-DHM evaluation is **fully present and reproducible** in the Quarto book and notebooks (this is the layer this page documents). There is no deployed/operational monitoring code (the live trigger is run manually), and the evaluation's cached data sits in the dev blob slot.
- **Discrepancies:** the substance of this page lives in the frontmatter `discrepancies` (kind-tagged). The headline ones: (1) `[gap]` no replacement trigger is proposed — this is an evaluation with a "reject GEOGloWS" verdict; (2) `[conflict]` GEOGloWS published RPs are forecast-unusable (forecast≈retro/2, RP2 never reached); (3) `[gap]` no GEOGloWS reforecast archive; (4) `[conflict]` GEOGloWS fails DHM event-detection vs GloFAS; (5) `[gap]` GRRR is the strongest candidate (6/7 Chisapani) but un-validated; (6) `[stale]` Chisapani/Karnali is out of endorsed scope and its GEOGloWS reach is geographically unverified.

## Monitoring

No live monitoring runs from this work. The endorsed 2025 trigger is monitored **manually** by CHD and RCO daily during the monsoon season on GloFAS forecasts and DHM bulletins (see the [2025-08-25 page](2025-08-25.md)). The evaluation book renders against dev-slot cached GEOGloWS parquets in Azure blob (`BLOB_STAGE="dev"`); nothing is promoted to prod and there is no deployed app for this framework.

## Historical activations

None under this development work. This is an analysis/evaluation, not an endorsed framework, and has never itself been activated.

The framework's real activations (October 2024 Koshi/Chatara, $3.4M CERF; October 2022 Karnali/Chisapani, $3.2M CERF) occurred under prior endorsed versions and are recorded on the [2025-08-25 endorsed page](2025-08-25.md). They are deliberately not duplicated here.

## Key decisions & rationale

**Why evaluate GEOGloWS at all?** It offers an 86-year retrospective (1940-present, vs GloFAS 1979) and a free, unauthenticated API — attractive for a longer extreme-value record and lower operational friction. The evaluation asked whether those advantages could strengthen the existing GloFAS-based trigger.

**Why the verdict is "do not adopt GEOGloWS."** Two structural gaps are decisive: (1) GEOGloWS publishes no multi-year reforecast archive, so the lead-time-dependent skill calibration the AA trigger depends on (exceedance probability at a fixed lead) cannot be fit — the ~22-month live archive contains zero-or-one RP2 events by construction. (2) The published RPs are fit to the retrospective, but the operational forecast runs at ~half retrospective magnitude at every lead day, so those thresholds can never fire correctly on the forecast (Chatara ensemble-mean max 9,016 m³/s vs published RP2 14,459). On top of that, GEOGloWS does not beat the incumbent GloFAS against observed DHM events at either station, and SFDC bias-correction does not rescue it.

**Why surface GRRR.** The cross-comparison incidentally found Google GRRR is the best performer against DHM at Chisapani (6/7 vs GloFAS 5/7, GEOGloWS 0/7) and best overall (12/16). This is tangential to the GEOGloWS question but operationally interesting, and is flagged as the next concrete validation — particularly relevant if the Karnali (western) basin is ever reintroduced into the framework (it was dropped in the 2025 revision).

**Why Chisapani is kept despite being out of scope.** The endorsed 2025 framework is Koshi-only. Chisapani/Karnali is retained in the evaluation precisely because it is where the sources most disagree and where GRRR most outperforms — making it the sharpest test of the candidate products and the place a future Karnali decision would draw on.

## Changes from previous version

Supersedes the 2025-08-25 endorsed version in the *lineage* sense (it is the active forward R&D), but proposes **no change to the trigger itself**. The endorsed GloFAS readiness (50% probability of exceeding RP5 ≈ 10,300 m³/s at Chatara, 7-day lead) plus the DHM 3-condition bulletin action trigger remain authoritative and operational. What is new vs the endorsed page is the *framing*: the endorsed page recorded the GEOGloWS work as discrepancies/context against the live GloFAS trigger; this page treats that same evaluation as the forward-looking subject — a documented investigation of candidate sources whose current conclusion is to keep GloFAS, reject GEOGloWS, and validate GRRR next.

## Open questions / known issues

- **No successor trigger yet.** This is an evaluation, not a revision. The concrete next-trigger question (which source, which thresholds) is unresolved; GloFAS remains the design.
- **GRRR needs a purpose-built validation** using GRRR's own published return periods (not the borrowed empirical-quantile convention) over the full DHM record before any trigger role is considered.
- **Chisapani GEOGloWS reach is geographically unverified** — the 0/7 detection failure could be partly reach-misalignment rather than pure product mass-deficiency; book/05 could not fully separate the two.
- **Rating curves for Chatara and Chisapani** would unlock `geoglows.bias.correct_historical()` and make DHM water level directly comparable to model discharge — the cleanest path to any future source comparison.
- **Re-evaluate GEOGloWS if/when v3 adds reforecasts** — the structural blocker (no reforecast archive) is the kind of thing a new release could remove.
- **Karnali reintroduction is a live possibility** but a policy/scope decision, not a data one; the GRRR Chisapani result is the technical lead if it happens.
- The evaluation persists cached data to the **dev blob slot**; if any of it is ever operationalized, the storage stage/path should be promoted out of dev per the `{PROJECT_PREFIX}/{raw|processed}/{datasource}/` convention.
