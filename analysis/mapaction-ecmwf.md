---
content_type: analysis
name: mapaction-ecmwf
analysis_type: exploratory
status: dormant
country_iso3: ETH
hazard: drought
summary: "MapAction/OCHA forecast-verification study of ECMWF SEAS5 seasonal-forecast skill (bias-corrected, ERA5-calibrated) vs. ERA5 reanalysis for Ethiopia precipitation — a methods exercise, not a framework: no trigger, no schedule, dormant at v0.1.0."
data_sources: [SEAS5, ERA5]
feeds: []
source_repo: ocha-dap/ds-mapaction-ecmwf
source_branch: main
source_sha: 2c87052
code_ref:
  - notebooks/ecmwf_pipeline.ipynb
  - notebooks/ecmwf_analysis.ipynb
  - src/data_processing/custom_python_package.py
  - src/data_analysis/ecmwf_data_analysis.py
  - src/data_retrieval/__main__.py
  - src/data_retrieval/cds/ecmwf.py
  - src/data_retrieval/cds/era5.py
  - src/data_retrieval/cds/mars.py
  - src/data_retrieval/azure_blob_utils.py
depends_on: []
discrepancies:
  - "[stale] README 'Directory Tree' lists files not present at this sha (notebooks/ecmwf_sandbox.ipynb, notebooks/bounding-box-chad.ipynb, .ipynb_checkpoints/, __pycache__/) — aspirational/outdated, not current on main."
  - "[gap] notebooks/bounding-box-tool.ipynb states it builds on a prior 'bounding-box-chad' notebook, which does not exist in the repo — its origin can't be traced."
  - "[gap] No findings, thresholds, or figures are committed anywhere in the repo — the notebooks are the analysis; results only exist if someone re-runs them against manually-fetched CDS/MARS data and a Google-Drive input_data/ copy."
extra: {}
visibility: internal
last_synced: "2026-07-08"
---

# ECMWF seasonal-forecast skill (MapAction) — analysis

> **Analysis, not a framework.** A framework page is *only* for something with its own published framework doc. This repo is analysis (regional overview, ad-hoc activation, or pre-framework exploration) — captured so the work is findable, and linked to the framework(s) it supports if any.

## What it is

A collaboration between OCHA Centre for Humanitarian Data and **MapAction** (an external NGO partner — 3 of the 4 listed authors are MapAction staff) to evaluate how much skill the **ECMWF SEAS5 seasonal forecast** has for precipitation, once bias-corrected against its own leadtime climatology and separately calibrated against **ERA5** reanalysis. The repo ships two things: (1) generic, country-agnostic retrieval tooling for pulling SEAS5/ERA5 from Copernicus CDS or ECMWF MARS into local files or Azure Blob, and (2) a specific processing+analysis pipeline that is hardcoded to **Ethiopia** (ADM1 boundaries, Ethiopia-named output files). It is not a framework — it recommends no trigger, threshold, or activation mechanism, only forecast-verification metrics (bias, MAE, accuracy, F1, ROC/AUC) for below-normal-precipitation quantiles, which are drought-relevant but not a drought trigger. It is not a living pipeline — there is no schedule, no deployment, and no automated data refresh: running it means manually downloading a decade-plus of GRIB files from CDS/MARS and copying a `input_data/` folder (admin boundaries, etc.) from Google Drive into a local `~/ma-chd-data/data/` directory, then executing two Jupyter notebooks by hand in sequence.

## What was analyzed / findings

**Data acquisition** (`src/data_retrieval`): SEAS5 seasonal-forecast total precipitation (CDS dataset `seasonal-monthly-single-levels`, `originating_centre=ecmwf`, `system=51`, leadtime months 1–6, years 1981–2023) and ERA5 monthly-averaged-reanalysis total precipitation (CDS `reanalysis-era5-single-levels-monthly-means`), retrieved either via the Copernicus CDS API (global, cropped to a country bounding box at load time) or the ECMWF MARS API directly (country-specific `fcmean` request on a 0.4°×0.4° grid, `fcmonth` 1–7, 25 ensemble members for years ≤2016 / 51 for years >2016). Country bounding boxes for the MARS path come from a static CSV built once in `notebooks/bounding-box-tool.ipynb` by intersecting MapAction's `geocint-mapaction` world-boundaries repo.

**Processing** (`notebooks/ecmwf_pipeline.ipynb` → `src/data_processing/custom_python_package.py`): converts each GRIB file to a dataframe **one ensemble member at a time** (looping 0–50) to bound memory use; converts units to mm/day; derives `lead_time` in months from the forecast step; corrects ECMWF's valid-time month-end convention (shifts month/year back by one); builds a reference lat/lon grid buffered 0.5° and spatially joined to the Ethiopia ADM1 boundary file (`eth_admbnda_adm1_csa_bofedb_2021.shp`); regrids ERA5 onto the coarser ECMWF grid by nearest-neighbour lat/lon snap; aggregates to both **pixel** and **admin1** level. Applies two bias corrections, both computed as an additive climatological mean-shift (negative results clipped to 0): a **leadtime bias correction** (shifts each location/month/leadtime's mean onto the all-leadtime reference mean) and an **ERA5 calibration** (shifts ECMWF's climatology onto ERA5's).

**Analysis** (`notebooks/ecmwf_analysis.ipynb` → `src/data_analysis/ecmwf_data_analysis.py`): computes below-normal-precipitation probabilities against a **1993–2016 climatology baseline**, at four quantile thresholds — median (1/2), tercile (1/3), quartile (1/4), quintile (1/5) — per pixel/admin1 × year × month × leadtime. ERA5 gives a binary "was it below the quantile" observation; ECMWF gives an ensemble-share "probability" of being below it. From that pairing it plots: climatology bias (raw vs. leadtime-corrected vs. ERA5-calibrated) per month/leadtime; bias and MAE dependency on leadtime; accuracy and F1-score vs. probability-threshold, per leadtime; ROC/AUC skill per leadtime; and a spatial accuracy map (choice of leadtime + threshold) at both admin1 and pixel resolution, plus the same set of plots repeated per individual admin1 subdivision.

No conclusions, recommended thresholds, or exported figures are checked into the repo — the notebooks *are* the analysis, and nothing about their output (skill numbers, which leadtimes/quantiles performed best) is written down anywhere else. Reproducing the finding requires re-running both notebooks against freshly (and manually) fetched data.

## Relation to frameworks

Standalone (`feeds: []`) — nothing in this repo, nor in the Ethiopia drought framework/pipeline repos, references the other; it predates and was never wired into them. Closest KB neighbours by subject matter, asking a similar "how much can we trust SEAS5, and how does its skill decay with leadtime" question:
- [frameworks/eth-drought/2026-06-09](../frameworks/eth-drought/2026-06-09.md) — the in-development OCHA Ethiopia drought trigger, also built on SEAS5 + ERA5.
- [pipelines/eth-drought-monitoring](../pipelines/eth-drought-monitoring.md) — the live scheduled monitoring pipeline for that trigger.
- [apps/seas5-skill](../apps/seas5-skill.md) — a later, far more complete SEAS5-vs-ERA5 Pearson-r skill explorer covering every monitored country/trimester, not just Ethiopia.

None of these cite or reuse this repo's code; the overlap is in the question being asked, not a code dependency.

## Sources & status

Repo `ocha-dap/ds-mapaction-ecmwf`, branch `main` @ `2c87052`. GPL-3.0-licensed; authored jointly by MapAction (3 of 4 listed authors) and OCHA. `pyproject.toml` still self-classifies as `Development Status :: 1 - Planning`, version `0.1.0` — the project was never marked finished. CI (`ci-test.yml`) lints and tests only the CDS/MARS request-building code under `tests/data_retrieval/cds/`; the actual processing and analysis logic (`custom_python_package.py`, `ecmwf_data_analysis.py`) has no test coverage. There is no schedule, no deployment, and no committed output — status is **dormant**: the tooling still runs in principle, but nothing has picked it up or kept it current since v0.1.0.
