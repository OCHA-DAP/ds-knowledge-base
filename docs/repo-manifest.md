# Repo manifest — ingestion work-list

Source of truth for what gets ingested into the KB. Generated from the `ocha-dap` org (repos starting `ds-`/`pa-`/`ocha-`).

- **cloned**: present in `/Users/tdowning/OCHA/repos/` (readable directly).
- **include**: default ingestion scope. Archived repos and pre-2024 `pa-*` (COVID-era) are excluded by default — flip to ✅ to opt in.
- Update this file as repos are ingested (add an `ingested:` date column when you start).

**136 in scope** · 78 cloned · **109 in default ingestion scope** (44 frameworks, 59 pipelines, 6 libs)

## frameworks (44 in scope / 47 total)

| repo | cloned | include | ingested | last push | notes |
|---|:---:|:---:|:---:|---|---|
| ds-aa-afg-drought | ✅ | ✅ | 2026-06-15 | 2026-04-02 |  |
| ds-aa-bfa-flooding | ✅ | ✅ | 2026-06-17 | 2025-08-06 |  |
| ds-aa-caf-flooding | ✅ | ✅ |  | 2026-01-22 |  |
| ds-aa-cerf-global-trigger-allocations | ✅ | ✅ |  | 2024-11-22 |  |
| ds-aa-cmr-drought | ✅ | — |  | 2024-06-27 | ARCHIVED |
| ds-aa-cod-flooding | ✅ | ✅ | 2026-06-15 | 2024-12-11 |  |
| ds-aa-cub-hurricanes | ✅ | ✅ | 2026-06-15 | 2026-06-08 |  |
| ds-aa-hti-hurricanes | ✅ | ✅ | 2026-06-13 | 2026-06-09 |  |
| ds-aa-hti-hurricanes-app | ✅ | ✅ | 2026-06-13 | 2024-07-23 | Web application for Haiti hurricanes AA framework |
| ds-aa-hti-hurricanes-impactmodel | ✅ | ✅ | 2026-06-13 | 2024-10-01 | Global Tropical Cyclone Model implementation for H |
| ds-aa-lac-dry-corridor | ✅ | ✅ | 2026-06-13 | 2026-03-05 |  |
| ds-aa-mdg-monitoring | ✅ | ✅ |  | 2026-02-09 |  |
| ds-aa-mmr-cyclones | ✅ | ✅ |  | 2026-06-08 |  |
| ds-aa-moz-cyclones | ✅ | ✅ | 2026-06-13 | 2026-02-03 |  |
| ds-aa-moz-cyclones-monitoring | ✅ | ✅ | 2026-06-13 | 2026-05-28 |  |
| ds-aa-mrt-drought | ✅ | ✅ | 2026-06-15 | 2026-03-03 |  |
| ds-aa-ner-drought | ✅ | ✅ | 2026-06-13 | 2026-06-04 |  |
| ds-aa-nga-flooding | ✅ | ✅ | 2026-06-13 | 2026-05-28 |  |
| ds-aa-plw-storms | ✅ | ✅ |  | 2025-10-03 |  |
| ds-aa-sahel-drought | ✅ | ✅ | 2026-06-17 | 2024-07-16 | Regional anticipatory action framework for drought |
| ds-aa-ssd-flooding | ✅ | ✅ | 2026-06-17 | 2025-05-06 |  |
| ds-aa-tcd-drought | ✅ | ✅ | 2026-06-15 | 2025-05-05 | Anticipatory action framework for drought in Chad |
| ds-aa-vut-cyclones | ✅ | ✅ |  | 2026-06-10 |  |
| pa-aa-bfa-drought | ✅ | ✅ | 2026-06-13 | 2026-04-14 | Analysis and monitoring of the anticipatory action |
| pa-aa-bgd-flooding | ✅ | ✅ | 2026-06-17 | 2024-07-04 |  |
| pa-aa-bgd-storms | ✅ | ✅ |  | 2024-09-18 |  |
| pa-aa-fji-storms | ✅ | ✅ | 2026-06-15 | 2026-06-08 | Anticipatory Action framework for Tropical Cyclone |
| pa-aa-fji-storms-app | ✅ | ✅ | 2026-06-15 | 2024-05-17 | Historical forecasts interactive plot for Fiji AA |
| pa-aa-ner-flooding | ✅ | ✅ | 2026-06-17 | 2026-01-16 |  |
| pa-aa-nga-cholera | ✅ | ✅ | 2026-06-17 | 2024-10-22 |  |
| pa-aa-phl-storms | ✅ | ✅ | 2026-06-15 | 2025-11-11 |  |
| pa-aa-tcd-flooding | ✅ | ✅ | 2026-06-17 | 2026-06-08 | Exploration of flooding in Chad |
| ds-aa-bgd-cyclone-monitoring | ✅ | ✅ | 2026-06-15 | 2026-03-05 |  |
| ds-aa-eth-drought | — | ✅ |  | 2026-06-09 | Analytical work to support trigger development for |
| ds-aa-eth-drought-monitoring | — | ✅ |  | 2026-06-09 |  |
| ds-aa-eth-flooding | ✅ | ✅ | 2026-06-17 | 2025-07-08 |  |
| ds-aa-ken-drought | — | ✅ |  | 2026-06-09 |  |
| ds-aa-ken-drought-monitoring | — | ✅ |  | 2026-06-09 |  |
| ds-aa-mdg-storms | ✅ | ✅ | 2026-06-17 | 2025-06-10 |  |
| ds-aa-moz-cholera | ✅ | ✅ | 2026-06-15 | 2026-05-07 |  |
| ds-aa-moz-cholera-monitoring | ✅ | ✅ | 2026-06-15 | 2026-06-09 |  |
| ds-aa-npl-flooding | ✅ | ✅ | 2026-06-15 | 2026-05-07 |  |
| ds-aa-syr-drought | — | ✅ |  | 2025-09-11 |  |
| pa-aa-cod-infectious-disease | ✅ | ✅ | 2026-06-17 | 2026-05-14 |  |
| pa-aa-cookiecutter | — | — |  | 2022-03-18 | COVID-era |
| pa-aa-food-insecurity | — | — |  | 2021-01-21 | ARCHIVED |
| pa-aa-yem-flooding | — | ✅ |  | 2024-12-12 |  |

## pipelines (59 in scope / 83 total)

| repo | cloned | include | last push | notes |
|---|:---:|:---:|---|---|
| ds-acled-conflict-index | ✅ | ✅ | 2026-06-01 | Weekly ACLED conflict index Excel scraper |
| ds-ait-lngo-research | ✅ | ✅ | 2026-06-12 | LNGO annual operating budget research: subagent we |
| ds-app-data-validation | ✅ | ✅ | 2025-05-06 |  |
| ds-bdi-flooding-support | ✅ | — | 2024-12-12 | ARCHIVED |
| ds-bsgi-support | ✅ | ✅ | 2024-03-26 | Support for the Black Sea Grain Initiative |
| ds-c3s-viz | ✅ | ✅ | 2026-06-02 |  |
| ds-cerf-supplement | ✅ | ✅ | 2026-06-02 |  |
| ds-cma-datasharing | ✅ | ✅ | 2026-06-01 |  |
| ds-cmr-flooding-support | ✅ | ✅ | 2025-10-06 |  |
| ds-contingency-hurricanes | ✅ | ✅ | 2024-07-09 |  |
| ds-flood-gfm | ✅ | ✅ | 2026-01-27 |  |
| ds-floodexposure-monitoring | ✅ | ✅ | 2026-06-08 | Data pipelines to create estimates of daily flood  |
| ds-floodexposure-monitoring-app | ✅ | ✅ | 2026-02-05 | Dash app for flood exposure monitoring  |
| ds-fms-tc-outlook | ✅ | ✅ | 2026-06-08 |  |
| ds-glb-cyclones-impactmodel | ✅ | ✅ | 2025-03-03 |  |
| ds-glb-tropicalcyclones | ✅ | ✅ | 2026-01-02 |  |
| ds-glb-tropicalcyclones-app | ✅ | ✅ | 2024-05-17 |  |
| ds-global-monitoring-explore | ✅ | ✅ | 2024-05-09 |  |
| ds-hurricanes-monitoring | ✅ | ✅ | 2026-06-08 |  |
| ds-ibtracs-matching | ✅ | ✅ | 2026-03-16 |  |
| ds-imerg | ✅ | ✅ | 2024-08-01 |  |
| ds-imerg-check | ✅ | — | 2024-12-12 | ARCHIVED |
| ds-jiaf-pbs-analysis | ✅ | ✅ | 2025-01-10 | Analysis for JIAF 2 PiN-based severity |
| ds-mapaction-ecmwf | ✅ | ✅ | 2024-07-19 | Collaboration with MapAction for historical analys |
| ds-nhc-forecast | ✅ | ✅ | 2026-06-08 |  |
| ds-raster-pipelines | ✅ | ✅ | 2026-05-08 | Pipelines to store raster data as Cloud-Optimized  |
| ds-raster-stats | ✅ | ✅ | 2026-01-13 | Pipelines for computing raster statistics from COG |
| ds-sahel-flashflooding | ✅ | ✅ | 2024-11-23 |  |
| ds-seas5-skill | ✅ | ✅ | 2026-06-09 |  |
| ds-seas5-viz | ✅ | ✅ | 2025-09-29 |  |
| ds-seasonal-bulletin | ✅ | ✅ | 2025-12-30 |  |
| ds-storm-impact-harmonisation | ✅ | ✅ | 2026-05-11 |  |
| ds-storms-alerts | ✅ | ✅ | 2026-06-10 |  |
| ds-storms-pipeline | ✅ | ✅ | 2026-06-11 | Pipeline for processing storms data |
| ds-teleconnections | ✅ | ✅ | 2026-06-05 |  |
| ds-toolkit | ✅ | ✅ | 2025-01-28 | Reusable utility functions for the Data Science te |
| pa-anticipatory-action | ✅ | ✅ | 2024-09-20 | Code and documentation for analytical work on OCHA |
| pa-flood-pilot-validation | ✅ | — | 2023-08-23 | COVID-era |
| ds-acled-fetcher | — | ✅ | 2026-03-19 |  |
| ds-adhoc-aa-cuba | — | ✅ | 2024-05-30 |  |
| ds-afro-cholera | — | ✅ | 2026-03-03 |  |
| ds-cerf-3rm-app | — | ✅ | 2026-05-22 |  |
| ds-cholera-pdf-scraper | — | ✅ | 2026-04-13 |  |
| ds-claude-config | — | ✅ | 2026-04-27 | Global CLAUDE.md configuration file for Data Scien |
| ds-flash-floods | — | ✅ | 2026-03-25 | Collaboration between the Centre for Humanitarian  |
| ds-floodscan-ingest | — | ✅ | 2024-11-29 |  |
| ds-nga-flood-monitoring | — | ✅ | 2025-07-10 |  |
| ds-pak-flooding-contingency | — | ✅ | 2025-08-22 |  |
| ds-pipelines-status | — | ✅ | 2026-06-12 | Simple status checker for DSCI data pipelines |
| ds-raster-explore | — | ✅ | 2024-07-18 | Exploring appropriate formats for storing large ra |
| ds-raster-stats-app | — | ✅ | 2024-11-28 | Simple Dash application to explore raster stats |
| ds-rosea-thresholds | — | ✅ | 2026-06-12 | Country-based support for slow onset and sudden on |
| ds-sdn-displacement-analysis | — | ✅ | 2023-11-09 |  |
| ds-slack-bot | — | ✅ | 2025-11-28 | Slack notifications for the Data Science Team |
| ds-som-risk-analysis-support | — | ✅ | 2026-03-02 |  |
| ds-unified-disaster-database | — | ✅ | 2024-09-26 |  |
| pa-COVID-model-parameterization | — | — | 2021-08-17 | COVID-era |
| pa-COVID-model-reports | — | — | 2021-08-17 | COVID-era |
| pa-COVID-trend-analysis | — | — | 2023-07-06 | COVID-era |
| pa-bangladesh-aa | — | — | 2020-12-07 | ARCHIVED |
| pa-cholera-validation | — | ✅ | 2026-02-03 | Validation of the Global Cholera Risk Model |
| pa-compute-chirps-anomaly | — | — | 2022-11-10 | COVID-era |
| pa-covid-dataviz | — | ✅ | 2026-04-13 |  |
| pa-cross-crisis | — | — | 2023-06-01 | COVID-era |
| pa-dashboard-eth | — | — | 2021-09-15 | COVID-era |
| pa-drc-cholera-dashboard | — | — | 2023-01-15 | COVID-era |
| pa-eth-ndvi | — | ✅ | 2025-01-14 | Analyses for the country office on NDVI during dif |
| pa-global-monitoring-dashboard | — | — | 2022-11-11 | COVID-era |
| pa-global-typhoon-model | — | — | 2022-07-12 | ARCHIVED |
| pa-gm-cholera-explore | — | — | 2024-01-02 | ARCHIVED |
| pa-historical-agromet-analysis | — | — | 2023-06-28 | ARCHIVED |
| pa-infectious-disease-modeling | — | — | 2021-03-30 | COVID-era |
| pa-jiaf-analysis | — | — | 2023-01-26 | ARCHIVED |
| pa-ocha-bucky | — | — | 2020-12-15 | COVID-era |
| pa-plague-publication | — | — | 2022-08-08 | COVID-era |
| pa-pooled-funds-aa | — | — | 2023-05-12 | COVID-era |
| pa-rainfall-model-skills | — | — | 2023-05-31 | COVID-era |
| pa-rosea-support | — | ✅ | 2026-01-23 | This repo contains analyses as requested by the RO |
| pa-som-analysis-support | — | — | 2022-12-15 | COVID-era |
| pa-ssd-flooding-blog | — | ✅ | 2024-06-03 | Analysis for the SSD flooding blog |
| pa-swaps-support | — | ✅ | 2024-08-06 |  |
| pa-syr-earthquake-analysis-support | — | — | 2023-02-20 | COVID-era |
| pa-triple-crisis | — | — | 2022-06-17 | COVID-era |

## libs (6 in scope / 6 total)

| repo | cloned | include | last push | notes |
|---|:---:|:---:|---|---|
| ocha-anticipy | ✅ | ✅ | 2023-08-24 | Python package to support the development of antic |
| ocha-lens | ✅ | ✅ | 2026-06-09 | Utility functions for standard data processing by  |
| ocha-relay | ✅ | ✅ | 2026-06-03 |  |
| ocha-stratus | ✅ | ✅ | 2026-04-02 | Utility functions for Azure cloud data access  |
| ocha-dap.github.io | — | ✅ | 2017-06-20 | main github page |
| ocha-mailchimp | — | ✅ | 2025-03-28 |  |
