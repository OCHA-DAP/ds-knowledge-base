# Catalog — all framework-versions

Generated from `frameworks/**/*.md` frontmatter by `scripts/gen_catalog.py`. 27 version(s). Filter by hazard / data source / basis / #windows / window axes / status / completeness / activation.

| framework | version | country | hazard | status | $ pre-arr. | basis | #win | axes | data sources | repo | activated? |
|---|---|---|---|---|--:|---|--:|---|---|---|---|
| [afg-drought](frameworks/afg-drought/2026-04-04.md) | 2026-04-04 | AFG | drought | endorsed | $22.0M | mixed | 2 | time | SEAS5, ERA5, ERA5-Land, FAO-ASI, FAO-VHI | analysis:partial/deployed_code:full | ✅ 2025-04-01 |
| [bfa-drought](frameworks/bfa-drought/2026-04-17.md) | 2026-04-17 | BFA | drought | endorsed | $8.0M | mixed | 2 | time | SEAS5, ASAP | analysis:full/deployed_code:stale | — |
| [bfa-flooding](frameworks/bfa-flooding/2025-08.md) | 2025-08 | BFA | flood | triggered | $1.0M | mixed | 3 | time | SEAS5, IMERG, CONASUR-alerts, river-gauge-DGRE | analysis:partial/deployed_code:none | ✅ 2025-09-08 |
| [bgd-cyclone](frameworks/bgd-cyclone/2025-04-25.md) | 2025-04-25 | BGD | tropical-cyclone | endorsed | $4.0M | mixed | 3 | time | BMD, IMD, ECMWF, GFS, JTWC | partial | — |
| [bgd-flooding](frameworks/bgd-flooding/2025-04-25.md) | 2025-04-25 | BGD | flood | triggered | $6.0M | mixed | 4 | space, time | GloFAS, FFWC, RIMES | analysis:partial/deployed_code:lost | ✅ 2020, 2024-07 |
| [cod-flooding](frameworks/cod-flooding/development.md) | dec-seasonal | COD | flood | development | — | mixed | 3 | space | SEAS5, ERA5, Floodscan | partial | — |
| [cod-infectious-disease](frameworks/cod-infectious-disease/2025-03-11.md) | 2025-03-11 | COD | cholera | triggered | $3.0M | observational | 2 | space | PNECHOL-MD, IDSR | analysis:full/deployed_code:partial | ✅ 2023-01-01, 2023-06-01, 2025-03-13, 2025-01-01, 2025-05-01 |
| [cub-hurricanes](frameworks/cub-hurricanes/2025-08-26.md) | 2025-08-26 | CUB | tropical-cyclone | endorsed | $4.0M | mixed | 3 | time | NHC, IMERG | analysis:full/deployed_code:partial | — |
| [eth-flooding](frameworks/eth-flooding/development.md) | development | ETH | flood | development | — | forecast | 1 | — | SEAS5 | partial | — |
| [fji-storms](frameworks/fji-storms/2025-12-17.md) | 2025-12-17 | FJI | tropical-cyclone | endorsed | $3.9M | mixed | 3 | time | FMS-forecast, WorldPop, IMERG | analysis:full/deployed_code:partial | — |
| [hti-hurricanes](frameworks/hti-hurricanes/2024-08-23.md) | 2024-08-23 | HTI | tropical-cyclone | endorsed | — | mixed | 3 | time | NHC, CHIRPS-GEFS, IMERG, IBTrACS, EMDAT | full | — |
| [lac-dry-corridor](frameworks/lac-dry-corridor/2025-02.md) | 2025-02 | SLV/GTM/HND | drought | superseded | $10.5M | forecast | 2 | time | SEAS5, INSIVUMEH | analysis:full/deployed_code:full | — |
| [lac-dry-corridor](frameworks/lac-dry-corridor/2026-03-13.md) | 2026-03-13 | SLV/GTM/HND | drought | triggered | $10.5M | forecast | 2 | time | SEAS5, ERA5, INSIVUMEH, EM-DAT | analysis:partial/deployed_code:partial | ✅ 2025-07-01, 2026-03-05 |
| [mdg-storms](frameworks/mdg-storms/2024-12-13.md) | 2024-12-13 | MDG | tropical-cyclone | triggered | $3.0M | forecast | 2 | time | IBTrACS, Météo-Madagascar, RSMC-La-Réunion, IMERG, BNGRC-cyclone-database | analysis:full/deployed_code:partial | ✅ 2026-02-09 |
| [moz-cholera](frameworks/moz-cholera/2026-05-22.md) | 2026-05-22 | MOZ | cholera | endorsed | $1.5M | observational | 2 | space | WHO-AWD-surveillance, WorldPop-2025 | analysis:partial/deployed_code:full | — |
| [moz-cyclones](frameworks/moz-cyclones/2026-01-09.md) | 2026-01-09 | MOZ | tropical-cyclone | endorsed | $4.5M | mixed | 4 | time | RSMC-La-Reunion, IMERG, FloodScan | partial | — |
| [mrt-drought](frameworks/mrt-drought/2026-04-17.md) | 2026-04-17 | MRT | drought | endorsed | $2.5M | mixed | 2 | time | IRI-NCDP-Maproom, CHIRPS | analysis:partial/deployed_code:lost | — |
| [ner-drought](frameworks/ner-drought/2024-10-24.md) | 2024-10-24 | NER | drought | triggered | — | mixed | 3 | time | IRI-seasonal-forecast, ENACTS-SPI | partial | ✅ 2022-08 |
| [ner-flooding](frameworks/ner-flooding/2025-11-04.md) | 2025-11-04 | NER | flood | triggered | $5.0M | observational | 2 | severity | ABN-gauge, GloFAS, GRDC, Floodscan, ANADIA | analysis:full/deployed_code:partial | ✅ 2024-11-28 |
| [nga-cholera](frameworks/nga-cholera/development.md) | april24-new-data-python | NGA | cholera | development | — | observational | 1 | — | cholera-linelist | analysis:partial/deployed_code:lost | — |
| [nga-flooding](frameworks/nga-flooding/2025-08-11.md) | 2025-08-11 | NGA | flood | endorsed | — | mixed | 3 | space | GloFAS, Google-Flood-Hub, FloodScan, WorldPop | partial | — |
| [npl-flooding](frameworks/npl-flooding/2025-08-25.md) | 2025-08-25 | NPL | flood | endorsed | $2.7M | forecast | 2 | time | GloFAS, DHM | analysis:partial/deployed_code:lost | ✅ 2024-10, 2022-10 |
| [phl-storms](frameworks/phl-storms/2025-10-03.md) | 2025-10-03 | PHL | tropical-cyclone | endorsed | $6.0M | mixed | 3 | time | ECMWF, IBTrACS, IMERG, PAGASA, 510-model | partial | — |
| [sahel-drought](frameworks/sahel-drought/2022-09-29.md) | 2022-09-29 | BFA/NER/TCD | drought | triggered | $45.0M | mixed | 8 | time, space | IRI, CHIRPS, ECMWF-SEAS5, ERA5, ASAP, SPI | analysis:partial/deployed_code:lost | ✅ 2022-08 |
| [ssd-flooding](frameworks/ssd-flooding/development.md) | development | SSD | flood | development | — | forecast | 1 | — | SEAS5, ERA5, Floodscan, IRI, EM-DAT | partial | — |
| [tcd-drought](frameworks/tcd-drought/2025-03-03.md) | 2025-03-03 | TCD | drought | endorsed | $8.0M | mixed | 3 | time | SEAS5, Biomasse-ACF | full | — |
| [tcd-flooding](frameworks/tcd-flooding/2025-07-31.md) | 2025-07-31 | TCD | flood | triggered | $4.0M | forecast | 2 | time | GloFAS-v4, GloFAS-reanalysis, GloFAS-reforecast, FloodScan, DRE | analysis:full/deployed_code:full — pipeline is present and scheduled, but with caveats (threshold-test bug + dev-only slot); see discrepancies | ✅ 2024-09-28 |
