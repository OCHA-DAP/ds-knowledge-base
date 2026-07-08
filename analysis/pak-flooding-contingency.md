---
content_type: analysis
name: pak-flooding-contingency
analysis_type: exploratory   # historical return-period threshold analysis + a standing monitor; no AA framework and no activation ever fired
status: active
country_iso3: PAK
hazard: flood
summary: "Real-time IMERG rainfall monitoring + daily alert email for the Lower Indus basin (Sindh), built around historical return-period thresholds — no published AA framework or CERF trigger envelope behind it."
data_sources: [IMERG, HydroBASINS, FieldMaps, CERF-allocations, EM-DAT]
feeds: []
# --- source repo ---
source_repo: ocha-dap/ds-pak-flooding-contingency
source_branch: main
source_sha: a4e5b0c
code_ref:
  - "R/tar_thresholds.R"
  - "R/tar_load_basins.R"
  - "_targets_imerg_v7.R"
  - "src/monitor_imerg_2025a.R"
  - "src/monitor_imerg.R"
  - "exploration/01_map_aoi.qmd"
  - "exploration/02_adhoc_check_for_cerf_2025_floods.qmd"
  - ".github/workflows/pak-2025.yaml"
  - ".github/workflows/pak-email.yaml"
depends_on: []
discrepancies:
  - "[stale] .github/workflows/pak-email.yaml is a legacy duplicate of the 2024 monitor: it runs the old script (src/monitor_imerg.R), which reads an un-suffixed thresholds parquet (imerg_flooding_thresholds.parquet, no _2025 suffix) from dev-stage blob — a path R/tar_thresholds.R's select_final_thresholds() only writes under the v==2024 branch, and that nothing has refreshed since the 2025 rewrite. It carries the same daily cron ('30 15 * * *') as the live pak-2025.yaml, but its YAML is invalid (see next item) so GitHub Actions cannot schedule it — a dead artifact left alongside the current pipeline rather than removed."
  - "[stale] pak-email.yaml's final step ('Run monitor imerg R script') is indented one space deeper than its sibling steps, which makes the file invalid YAML — confirmed by parsing it with python yaml.safe_load, which raises a ParserError at line 52. GitHub Actions cannot load or schedule this workflow; it is effectively dead."
  - "[gap] Not listed in infrastructure/deployments.md's GitHub Actions pipelines table despite having a live daily cron (pak-2025.yaml, '30 15 * * *') that writes to Postgres services and sends email — flagged here since it blurs the analysis/pipeline line (see Sources & status)."
extra: {}
visibility: internal
last_synced: "2026-07-08"
---

# Pakistan — Lower Indus flooding contingency monitoring — analysis

> **Analysis, not a framework.** A framework page is *only* for something with its own published framework doc. This repo is analysis (regional overview, ad-hoc activation, or pre-framework exploration) — captured so the work is findable, and linked to the framework(s) it supports if any.

## What it is

`ds-pak-flooding-contingency` monitors 3-day cumulative IMERG rainfall over a subset of the lower Indus river basin around Sindh province, Pakistan, and emails a daily status ("Alert"/"No Alert") when rainfall crosses a historically-derived return-period threshold. It exists to shorten disbursement time for future flood response funding by giving early, real-time visibility into an event's severity relative to history — but it is **not** an AA framework: there is no published trigger document, no CERF pre-arranged financing envelope, and no endorsed activation mechanism behind the alert. It is best read as a standing early-warning utility built on top of a one-off historical-threshold analysis, not a framework-in-waiting — nothing in the repo (README, commits, or the empty 2025 follow-up notebook) suggests intent to formalize it into one.

## What was analyzed / findings

**Historical analysis (`exploration/01_map_aoi.qmd`, `_targets.R`/`_targets_imerg_v7.R`):**
- **AOI selection**: compared monitoring the full Indus basin (HydroBASINS level 3, id `4030033640`) vs. a smaller subset of level-4 sub-basins around Sindh province upstream of the flood-prone area (`BAS4_ID_AOI`, 6 sub-basin ids). Settled on the level-4 subset ("basin_4") as the primary AOI, with the level-3 basin kept as a secondary comparison.
- **Data source choice**: compared CHIRPS, IMERG, and ERA5 for near-real-time monitoring; picked **IMERG** because it publishes daily by 3pm UTC, versus significant lag for CHIRPS/ERA5.
- **Threshold derivation**: built a `targets` pipeline (`imerg_zonal()` → rolling 1/2/3-day sums → yearly max → return-period quantiles via `grouped_quantile_summary()`) from the IMERG time series back to ~2004. Selected the **3-day rolling rainfall, 5-year return-period value** for the basin-4 AOI as the operational alert threshold (`select_final_thresholds()` in `R/tar_thresholds.R`, description: "Select final thresholds based on 5 year RP of 3d rainfall values for the AOI (Basin 4 merged and subset)").
- **Validation against real allocations**: overlaid the 5-year-RP exceedance events (2004–2024) against a hand-built table of ten historical CERF flood allocations to Pakistan (2007×2, 2008, 2010×3, 2011, 2012, 2020, 2022) and EM-DAT flood impact records (deaths, injured, affected, damage). Finding: since 2004 the Indus basin-4 subset saw **seven 1-in-5-year rainfall events**; CERF responded with an allocation to **all but one** (the 2023 event went unfunded), plus one allocation tied to a 1-in-4-year event (2020) and three tied to sub-3-year events — i.e. the RP-based threshold aligns reasonably well with, but doesn't perfectly predict, historical CERF flood response.
- The **2025 rewrite** (`_targets_imerg_v7.R`, store `_targets_2025`) re-ran the same pipeline against IMERG **v7** (previous version used v6), against `prod`-stage blob via the `cumulus` R package instead of `dev`-stage via hand-rolled `AzureStor` calls, and re-wrote the threshold parquet to a `_2025`-suffixed path. Logic is otherwise unchanged (same AOI ids, same 5-year/3-day threshold rule).

**2025 ad hoc check (`exploration/02_adhoc_check_for_cerf_2025_floods.qmd`):** an **empty stub** — a "one-off" comment block outlining what a Khyber Pakhtunkhwa admin-1 rainfall/threshold check against the DB `imerg` table *would* look like, entirely commented out. Never executed or filled in.

**Live monitoring (`src/monitor_imerg_2025a.R`, run by `.github/workflows/pak-2025.yaml`):** each day, pulls the last 10 days of processed IMERG v7 COGs from the `prod` raster container, computes basin-4 zonal-mean rainfall, rolls to a 3-day sum, flags `alert_flag = 3d >= threshold`, renders a plot + `email_pak_monitor.Rmd` templated email (subject "Alert"/"No Alert"), and sends via `blastula`/SMTP to a recipient list read from blob (`pak_monitoring_email_receps.csv`, filtered to `keep_2025`, split into `test`/`daily`/`alerts` frequency groups).

## Relation to frameworks

Standalone (`feeds: []`). There is no OCHA/CERF-endorsed Pakistan flood AA framework in the KB catalog to feed. The repo's own historical-CERF-allocation comparison (above) is itself informal groundwork that *could* inform a future PAK flood framework, but nothing in the repo indicates that's underway. Closest KB neighbours by shape (real-time IMERG rainfall monitoring feeding a daily alert email, no framework behind it) are [pipelines/mdg-monitoring](../pipelines/mdg-monitoring.md) and [pipelines/nga-flood-monitoring](../pipelines/nga-flood-monitoring.md) — both of those, however, are registered in `infrastructure/deployments.md`'s GHA pipeline table, which this repo currently is not (see discrepancies).

## Sources & status

- **Repo**: `ocha-dap/ds-pak-flooding-contingency`, single branch `main` (sha `a4e5b0c`). No feature branches — all work, including the 2025 rewrite, happened directly on `main`.
- **Data**: IMERG v7 daily precipitation COGs (`prod` raster container, `imerg/daily/late/v7/processed`), HydroBASINS Asia levels 3/4 (uploaded once via `data-raw/01_upload_hydrobasins_asia.R`, subset via `02_subset_basins.R`, staged at `projects/ds-contingency-pak-floods/hybas_asia_basins_03_04.parquet` — frozen extract, not refreshed on a schedule), Pakistan admin-1 boundaries via FieldMaps (`R/utils.R::download_fieldmaps_sf`), a hand-typed CERF allocation table (through 2022) and an EM-DAT export (`public_emdat_custom_request_2024-06-25...xlsx`, read from a local path in the exploration notebook — not staged on blob) used only for the one-off historical validation, not the live monitor.
- **Completeness**: the historical threshold analysis (`exploration/01_map_aoi.qmd`) is complete and substantive — full AOI comparison, threshold derivation, and validation against real allocations/impacts. The 2025 follow-up notebook (`02_adhoc_check_for_cerf_2025_floods.qmd`) is an empty stub.
- **Live surface**: despite living in `analysis/`, this repo runs two **scheduled** GitHub Actions workflows (`pak-2025.yaml`, `pak-email.yaml`, both cron `30 15 * * *`) that read live data and send email — operationally it behaves like a small monitoring pipeline, just one with no framework/trigger envelope behind it and no entry in `infrastructure/deployments.md` yet (flagged as a gap above). `pak-2025.yaml` running `src/monitor_imerg_2025a.R` against prod/2025 thresholds appears to be the current, intended system; `pak-email.yaml` (older `src/monitor_imerg.R`, dev-stage blob, un-suffixed 2024 thresholds) is an un-retired duplicate whose YAML no longer parses — confirmed dead, GitHub Actions cannot schedule it (see discrepancies).
- **Status**: `active` — the 2025 monitoring workflow and email pipeline are live and current; the underlying historical analysis is a one-off (not re-run on a schedule) but its output (the threshold parquet) is what the live monitor depends on.
