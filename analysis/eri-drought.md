---
content_type: analysis
name: eri-drought
analysis_type: exploratory
status: one-off
country_iso3: ERI
hazard: drought
summary: "Eritrea June–August (JJA, Kiremti) 2026 season vs past seasons by admin 1 — CHIRPS rainfall, MODIS NDVI and the ICPAC Combined Drought Indicator in one published report; descriptive monitoring, no trigger, so not a framework."
data_sources: [CHIRPS, MODIS-NDVI, WFP-HungerMap-subnational, ICPAC-CDI, FieldMaps-COD-AB]
feeds: []
surfaces:
  - {url: "https://ocha-dap.github.io/ds-eri-drought/", kind: landing, title: "Eritrea Drought Monitoring"}
  - {url: "https://ocha-dap.github.io/ds-eri-drought/season-2026/", kind: report, title: "Eritrea Kiremti 2026"}
source_repo: ocha-dap/ds-eri-drought
source_branch: main
source_sha: f747c4c
code_ref:
  - notebooks/01_jja_season_2026.py
  - src/eri_drought/data.py
  - src/eri_drought/cdi.py
  - scripts/build_pages.py
  - .github/workflows/pages.yml
depends_on: []
discrepancies:
  - "[gap] No trigger, threshold or framework doc — the notebook only ranks/visualises 2026 against history; nothing says whether the season 'is' a drought."
  - "[gap] Raw WFP tables and CDI inputs are frozen extracts on the dev blob; no schedule refreshes them (CDI rebuild is a manual `REFRESH` flag; WFP CSVs were dropped in by hand — their provenance/URL is not in the repo)."
  - "[gap] Everything lives on the **dev** blob (`stage=\"dev\"`), including the CDI COGs the report reads — no prod copy."
extra: {}
visibility: public
last_synced: 2026-10-05
---

# Eritrea JJA 2026 drought watch — analysis

> **Analysis, not a framework.** A framework page is *only* for something with its own published framework doc. This repo is analysis (regional overview, ad-hoc activation, or pre-framework exploration) — captured so the work is findable, and linked to the framework(s) it supports if any.

## What it is
A single-notebook, descriptive look at how Eritrea's June–August 2026 (Kiremti) season compares with past seasons, by the six admin 1 areas (ER1–ER6). It combines three independent drought signals — rainfall, vegetation and ICPAC's combined indicator — and publishes them as a static report on GitHub Pages. It is not a framework (no OCHA/CERF AA framework doc, no trigger, no pre-arranged funding) and not a pipeline (no schedule, no deployment beyond the Pages build); it is a one-off season situation report, written after the JJA window closed (all repo commits on 2026-09-24). Status `one-off`: one dated notebook, one season, frozen inputs.

## What was analyzed / findings
Season window = the 9 dekads 1 Jun–31 Aug; JJA 2026 rainfall dekads are `final`, only the Sept 2026 dekads are `prelim`. The notebook (`notebooks/01_jja_season_2026.py`, jupytext-paired with the `.ipynb`) has three sections plus an admin-1 locator map:

1. **Rainfall (CHIRPS via WFP subnational table, 1981–2026).** JJA total = WFP's 3-month rolling columns on the 21 August dekad (`r3h` mm, `r3h_avg` = 1989–2018 average, `r3q` = % of average). Outputs: bar chart per admin 1 with the 2026 value, % of average and **rank among driest** years; a year × admin-1 heatmap of % of average; a table of the five driest years per admin 1; and a dekad-by-dekad March–October plot of 2026 against the 1981–2025 min/max envelope and average, highlighting the two driest JJA seasons on record (**1984, 1990**) as reference years.
2. **NDVI (MODIS via WFP subnational table, 2003–2026).** JJA mean of `viq` (% of average) over 9 dekads per year, rank-lowest per admin 1, and a dekadal 2026-vs-2003–2025 envelope. Noted finding: JJA mean NDVI is **above 100 % of average in all six admin 1s in every year 2019–2026**; the source doesn't state `vim_avg`'s baseline period.
3. **ICPAC Combined Drought Indicator (EADW CDI, 2020–2026, HDX, CC BY 4.0).** Class values grouped per the EADW factsheet: 1–3 Watch, 4–6 Warning, 7–10 Alert, 11–12 Partial recovery, 13–14 Full recovery (0 = "no class"; 15 appears only in 2022/2023 files, undocumented, excluded from charts but kept in the area denominator). Outputs: share of admin 1 area by class per month, a stacked dekadal timeline Jan 2020 → latest dekad, Jun/Jul/Aug 2026 maps clipped to the border, and a mean-JJA-share table incl. a `watch_warning_alert` sum.

Data-handling choices worth knowing: WFP admin 1 values are pixel-weighted aggregates of the admin 1/2 rows; **ER3 has two `adm_id`s** — 1211 (mainland, 1141 px) kept, 1206 (37 px, Red Sea islands) dropped, so ER3 is mainland only. Admin 1 boundaries are FieldMaps COD-AB via `ocha-stratus`. The repo records no written conclusion about 2026 severity beyond what the charts show (the rendered numbers are in the executed notebook/report, not the README).

## Relation to frameworks
Standalone (`feeds: []`). There is no Eritrea AA framework in the OCHA/CERF portfolio. Closest KB neighbours are the East-Africa drought-monitoring pipelines — [eth-drought-monitoring](../pipelines/eth-drought-monitoring.md) and [ken-drought-monitoring](../pipelines/ken-drought-monitoring.md) (living, scheduled; this one is a one-off); the [hdx](../infrastructure/datasets/hdx.md) dataset page covers the HDX access pattern used to pull the CDI.

## Sources & status
- **Repo:** `ocha-dap/ds-eri-drought`, branch `main` (single active branch), sha `f747c4c`. Python package `src/eri_drought` (`data.py` loads/aggregates WFP tables + admin 1; `cdi.py` reads ICPAC CDI GeoTIFFs from HDX by HTTP range request, clips to Eritrea admin 1 bbox + 0.1°, writes COGs, and counts pixels per admin 1 × class; `constants.py` = blob prefix `ds-eri-drought`). Deps via `uv`.
- **Data (dev blob, `projects` container, prefix `ds-eri-drought/`):** `raw/eri-rainfall-subnat-full.csv`, `raw/eri-ndvi-subnat-full.csv` (WFP, adm1+adm2); `processed/cdi_adm1_jja_counts.parquet`; `processed/cdi_adm1_dekadal_counts.parquet`; `processed/icpac_cdi/eri_cdi_monthly_YYYY-MM.tif` and `.../dekadal/eri_cdi_dekadal_YYYY-MM-DD.tif` (every month/dekad on HDX, 2020–2026). Access needs `DSCI_AZ_BLOB_DEV_SAS` (+ `_WRITE`). Reruns of `save_eritrea_cogs` skip months already on blob.
- **Where it runs:** nowhere scheduled. The notebook is run by hand (`REFRESH` / `REFRESH_DEKADAL` = False by default, reading cached parquet). The only automation is `.github/workflows/pages.yml` (GitHub Pages deploy on push to `main` touching `pages/`, `notebooks/`, `scripts/build_pages.py`, or manually): `scripts/build_pages.py` assembles `_site/`, extracting each notebook cell tagged `fig-<name>` from the **committed executed notebook** into `season-2026/figs/<name>.png` — so to update the report, re-execute the notebook locally and commit it. The CI build does not touch the blob or HDX.
- **Published:** <https://ocha-dap.github.io/ds-eri-drought/> (landing) and `/season-2026/` (report), declared in `surfaces:`.
- **What breaks:** a stale executed notebook (charts won't update on its own); HDX CDI file naming/URL changes (`cdi.py`); WFP table schema or ER3 `adm_id` changes; dev-blob SAS expiry; the 2026 dekads marked `prelim` get revised.
- **Status:** `one-off` — single season snapshot, frozen inputs, no stub notebooks; would become `active` only if re-run for the next Kiremti season.
