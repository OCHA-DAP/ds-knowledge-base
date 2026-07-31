---
content_type: dataset
name: ACMAD seasonal forecasts
aliases: [ACMAD, "RCC-Africa", "African Centre of Meteorological Applications for Development"]
provider: "ACMAD, Niamey — WMO Regional Climate Centre for Africa (continental, RA I)"
data_type: seasonal-forecasts
access: open
api: "THREDDS: http://sgbd.acmad.org:8080/thredds (catalog.xml per folder; fileServer for downloads)"
auth: none
formats: [pdf, jpeg, png, shp, geojson, nc]
resolution: "continental Africa; tercile-probability polygons + map images; 2 overlapping 3-month seasons per monthly issue"
update_cadence: "Long-Range Forecast issued ~monthly (ACCOF process); RCOF products per forum (PRESASS ~Apr, PRESAGG ~Feb, PRESAC, MEDCOF, SWIOCOF)"
license: "none stated — public server, no terms published"
code_ref: "ocha-dap/ds-regional-forecasts src/datasources/acmad_thredds.py (catalog.xml crawler + skip rules)"
mirror: automated
mirror_priority: high
used_by:
  - apps/regional-forecasts.md
last_verified: 2026-07-26
---

# ACMAD seasonal forecasts

ACMAD (Niamey) is the **WMO Regional Climate Centre for the whole of Africa** and the
continental seasonal-forecast producer. Its flagship product is the monthly
**continental Long-Range Forecast (LRF)**: precipitation + temperature tercile
probabilities for two overlapping 3-month seasons, produced through the monthly
**ACCOF** (African Continental Climate Outlook Forum) process. ACMAD also co-organizes
the regional RCOFs and **hosts their outputs** (PRESASS, PRESAGG, PRESAC, MEDCOF,
SWIOCOF) — making it effectively the data server for AGRHYMET's forums too
(see [agrhymet.md](agrhymet.md)).

## The headline: an open THREDDS server with actual data

Nearly everything — current and archive, PDF/JPEG **and forecast polygons as
shapefiles** — lives on an open THREDDS server:

- **Base:** `http://sgbd.acmad.org:8080/thredds` — the HTTPS endpoint (`sgbd.acmad.org`)
  has an **expired TLS cert**; use port-8080 HTTP (or `verify=False`). Old pages also
  reference the raw IP `154.66.220.45:8080` (same host).
- **Enumeration:** every folder serves a machine-readable `catalog.xml`
  (`/thredds/catalog/<path>/catalog.xml`); files download via
  `/thredds/fileServer/<path>`. **Never construct filenames** — they are hand-authored
  (spaces, `%` chars, typos like "Breif"/"Verifcation", month codes that vary
  `Sep`/`September`). Crawl the catalog instead.
- **Key trees** (see the scraper's `ACMAD_SEASONAL_TREES` for exact paths):
  - `ACMAD/CDD/longrangeforecastingservice/<YYYY>/<Month>/` — LRF issues 2018–19 and
    2025–26, **including tercile polygons as shapefiles** (e.g. `Precip-fcst-jas-2026.shp`)
  - `ACMAD/PROJECTS/CLIMSA/CDD/ACTIVITIES/SERVICES/Long_Range_Forecast/` — LRF 2021–23
    (PDF bulletins, technical notes, policy briefs)
  - `.../SERVICES/Climate_outlook_forum/{PRESASS,PRESAGG,PRESAC,MEDCOF,SWIOCOF,RCOF_WEB}/`
    — per-forum archives ~2022+ (statements, forecast-map JPEGs)
  - `ACMAD/CDD/multihazard_shapefiles/seasonal/<YYYYMM>/` — 2022 only: forecast polygons
    as **GeoJSON** (`ACMAD_Precip_Outlook_NDJ_2022_23.geojson`), discontinued Nov 2022
- **"Latest issue" stable URLs** exist under `.../SERVICES/Doc_Web/` (e.g.
  `Long_Range_Forecast_Bulletin.pdf`) but are **overwritten in place** each cycle —
  poll `Last-Modified`.
- The issue folders are working directories: published products sit beside model-run
  debris (CPT runs, predictor data, per-city trend plots, analog-year GrADS files,
  obs monitoring). The scraper's skip-pattern list is the distilled knowledge of what
  is product vs debris — reuse it.

## Other access points

- `acmad.org` (WordPress) — ACCOF session pages `index.php/accof-<NN>/`; **all uploads
  land in `/wp-content/uploads/2019/03/` regardless of real date**. `new.acmad.org`
  (Climweb/Wagtail) has a working sitemap.xml. `rcc.acmad.org` (old PHP portal) is the
  richest link hub but its DB-driven archive pages are dead (`mysql_connect()` fatals).
- Interactive viewers with undocumented-but-open APIs: `multi-hazard.acmad.org`
  (`/api/catalog/...`, titiler tiles), `ada.acmad.org` (drought; GeoServer WMS at
  `/geoserver/wms`). No seasonal-forecast layers in either as of 2026-07.
- Sub-seasonal bonus with the estate's only fully predictable URL pattern:
  `.../FIT/BRIEFING/ARCHIVE/Hazard_Outlook/Continental_Hazard_Outlook_<YYYYMMDD>.pdf`
  (2021-10 → present, ~2/week).

## Gotchas

- Several products **silently stopped** (drought bulletin Jan 2024, multihazard seasonal
  GeoJSONs Nov 2022, RCOF_WEB "current" maps stuck at 2024) — check `Last-Modified`
  before presenting anything as current.
- The LRF archive is split across the two trees above with a 2020 gap and inconsistent
  layouts per era.
- Continental products are EN; West/Central Africa RCOF material is FR or bilingual.

## Our mirror

`ocha-dap/ds-regional-forecasts` crawls the trees above (resumable; junk-pattern skip
list) into blob `ds-regional-forecasts/raw/acmad/...` and serves a gallery + year-viewer
on GitHub Pages. See the repo CLAUDE.md for pipeline details.
