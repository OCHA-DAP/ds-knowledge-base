---
content_type: dataset
name: SADC CSC seasonal forecasts (SARCOF)
aliases: [SARCOF, "SADC Climate Services Centre", "SADC CSC", "Southern African Regional Climate Outlook Forum"]
provider: "SADC Climate Services Centre, Gaborone — WMO Regional Climate Centre for Southern Africa"
data_type: seasonal-forecasts
access: open
api: "none — two Drupal sites crawled (www.sadc.int document library; csc.sadc.int, whose /climate-prediction page embeds the full objective-forecast image space as drupalSettings JSON)"
auth: none
formats: [pdf, jpg]
resolution: "SADC region (16 member states); consensus tercile maps in statement PDFs + gridded objective-forecast map images (~1° pixels by eye)"
update_cadence: "two SARCOF forums per year since 2024 (Aug/Sep main for OND–JFM, Jan/Feb mid-season for FMA–AMJ; annual before that); objective forecast images ~monthly since 2023-06"
license: "none stated — public sites, no terms published"
code_ref: "ocha-dap/ds-regional-forecasts src/datasources/{sadc_web,sadc_wayback,sadc_osf}.py"
mirror: automated
mirror_priority: high
used_by:
  - apps/regional-forecasts.md
last_verified: 2026-08-24
---

# SADC CSC seasonal forecasts (SARCOF)

The SADC Climate Services Centre (Gaborone) is the WMO Regional Climate Centre for
Southern Africa and runs **SARCOF** — the Southern African Regional Climate Outlook
Forum, the region's PRESASS equivalent. SARCOF-1 was 1997; the forum was annual
(Aug/Sep, covering OND–JFM) through SARCOF-27 (2023), and since SARCOF-28 (Jan 2024)
runs **twice a year** (Jan/Feb mid-season update + Aug/Sep main) — so session number
no longer maps 1:1 to year (`session_year()` in the scraper encodes the mapping).

## Access

- **www.sadc.int** (Secretariat, Drupal): document library title-search
  (`/documents?title=SARCOF`) reaches statements back to SARCOF-16; more hide behind
  `latest-news` nodes and unlinked `/sites/default/files/` URLs.
- **csc.sadc.int**: **HTTP only** — HTTPS times out (same disease as ACMAD). The
  ~2025 Drupal relaunch killed every old Joomla `/images/...` URL; only SARCOF-30+
  lives there now.
- **Objective seasonal forecasts** (the CSC's WASS2S analogue): the
  `/climate-prediction` page embeds its complete valid product space (issued dates,
  systems MME01/SEAS51/CFSv2/GEOSS2S/CCSM4, products, predictors) as drupalSettings
  JSON, and image URLs are fully constructible:
  `/sites/default/files/climate-prediction/osf-seasonal/{var}_{product}_{system}[_{predictor}]_{YYYY-Mon}_{PER}.jpg`.
  Seasonal issues exist 2023-06 → present; a target season is published to ~4 months
  lead; single models require a predictor suffix, MME01 doesn't. Monthly and
  subseasonal variants exist too (not mirrored).
- **Wayback Machine** for everything older: three generations of dead hosting
  (dmc.co.zw = SADC Drought Monitoring Centre, Harare, ~2002–2006 → old sadc.int CMS
  `/files/<hash>/` → Joomla csc.sadc.int).

## Gotchas

- **Known-lost**: SARCOF-11/12/13 statements (2007–2009 — the DMC-era site was barely
  archived) and the SARCOF-22 / SARCOF-26 main statements (only their mid-season
  review/updates survive). A few Wayback captures are truncated/unreadable PDFs —
  check before trusting a rescued file.
- **No machine-readable record exists upstream**: no digitized SARCOF forecast
  dataset anywhere (checked Zenodo 2026-08), and the CSC's own OSF NetCDFs never
  leave their internal system (their pipeline is public at github.com/sadccsc/osf —
  only rendered maps are synced to the website). We therefore **digitized the OSF
  maps ourselves**: `src/digitize_osf.py` in ds-regional-forecasts inverts all 742
  images back to dominant tercile + probability class on the 0.25° grid (blob
  `ds-regional-forecasts/processed/osf-digitized/*.nc`). The SARCOF statements'
  consensus maps remain images only.
- `cscgeo.sadc.int` (a geo server referenced for weather alerts) was unreachable
  during the 2026-08 survey — worth re-probing for outlook polygons.

## Our mirror

`ocha-dap/ds-regional-forecasts` mirrors 63 SARCOF documents (2002–2026) and 742
objective-forecast tercile maps into blob `ds-regional-forecasts/raw/sadc/...` and
serves them in the [regional-forecasts gallery](../../apps/regional-forecasts.md).
See the repo CLAUDE.md for the full survey.
