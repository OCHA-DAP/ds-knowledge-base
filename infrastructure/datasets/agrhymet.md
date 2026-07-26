---
content_type: dataset
name: AGRHYMET seasonal forecasts (PRESASS / PRESAGG)
aliases: [AGRHYMET, PRESASS, PRESAGG, "CCR-AOS", "RCC-WAS", "Centre Régional AGRHYMET"]
provider: "AGRHYMET Regional Centre (CILSS), Niamey — WMO Regional Climate Centre for West Africa & the Sahel"
data_type: seasonal-forecasts
access: open
api: "WordPress REST: https://agrhymet.cilss.int/wp-json/wp/v2/media?search=<term>&per_page=100 (open, paginated)"
auth: none
formats: [pdf, nc]
resolution: "West Africa / Sahel; consensus tercile maps (images embedded in PDFs) + season onset/cessation, dry spells, river-basin flows"
update_cadence: "PRESASS forum late April (JJAS season) + Bulletin Spécial ~May + occasional July update; PRESAGG forum late Feb (MAMJ Gulf of Guinea season) + bulletin Mar–Apr"
license: "none stated for PDFs; the digitized NetCDF record is CC-BY 4.0 (Zenodo)"
code_ref: "ocha-dap/ds-regional-forecasts src/datasources/{agrhymet_wp,wayback,zenodo}.py"
mirror: automated
mirror_priority: high
used_by:
  - apps/regional-forecasts.md
  - frameworks/ner-drought/2026-06-03.md
last_verified: 2026-07-26
---

# AGRHYMET seasonal forecasts (PRESASS / PRESAGG)

AGRHYMET (CILSS institution, Niamey; WMO RCC for West Africa & the Sahel) runs the
region's two consensus seasonal-forecast forums, co-organized with ACMAD and 17
national met services:

- **PRESASS** — Sudano-Sahelian zone, **JJAS** rainy season. Forum late April;
  outputs: communiqué final (tercile maps embedded as images) + technical
  **Bulletin Spécial** (~May, SST/ENSO analysis, sectoral advisories) + occasional
  mid-season updates. Also forecasts **season onset/cessation dates, dry-spell
  lengths, and river-basin flows** (Niger, Senegal, Volta, Lake Chad).
- **PRESAGG** — Gulf of Guinea countries, **MAMJ** ("grande saison"). Forum late
  February; same communiqué + bulletin pair. No second-season (SON) forum product.
- Predecessor: **PRESAO** (1998–2015, ACMAD-led), Wayback-only.

**Everything is PDF.** No data server, no geoportal, no API for the forecasts
themselves — the deliverable of a consensus forum is literally a map negotiated in a
workshop. FR is primary; EN versions since ~2018.

## Access & harvesting

- **The WordPress REST API is open** and is the only reliable enumeration route —
  filenames are hand-made each year (host cities embedded, double `.pdf.pdf`, stray
  `-1` suffixes): `https://agrhymet.cilss.int/wp-json/wp/v2/media?search=PRESASS`.
  Same API open on the parent `www.cilss.int` (which mirrors communiqués).
- **URL rot is severe**: the domain has been through 3+ site generations and each
  broke all prior PDF URLs. Live site holds ~2023+; **2016–2022 is Wayback-only**
  (resolve snapshots via the CDX API; a few issues have no usable capture).
  ACMAD's site/THREDDS also carries copies (see [acmad.md](acmad.md)) — the best
  non-Wayback source for 2022–2023.
- The old IRI-Data-Library "Map Room" (`cradata.agrhymet.ne`) is **dead**; guessed
  geoportal subdomains don't resolve. Live CILSS portals carry no forecast layers.

## Machine-readable data: the Zenodo deposit

The one usable digitized record — published by AGRHYMET's own Houngnibo et al.
(WAS-NextGen / AICCRA), **DOI 10.5281/zenodo.18936657, CC-BY 4.0**:

- `Consensual_Forecasts_2016_2024.nc` — the PRESASS consensus tercile probabilities
  (JAS), digitized from georeferenced forum maps
- `Objective_Forecasts_2017_2024.nc` — the parallel objective (WASS2S-style) forecasts
- (a 1.3 GB obs/forcing zip also exists in the record)

Longer digitized records (PRESAO/PRESASS **1998–2024**) exist but were never
deposited: Pirret et al. 2020 (UK Met Office, 1998–2017) and Rauch et al. 2025
(Univ. Augsburg, extended to 2024) — **author contact required**.

**Direction of travel:** the region's met directors have endorsed replacing the
consensus process with the objective **WASS2S** system, so future forecasts should
increasingly exist as reproducible NetCDF; the digitization problem is the
historical record.

## Our mirror

`ocha-dap/ds-regional-forecasts` harvests the WP API + Wayback rescues + the Zenodo
NetCDFs into blob `ds-regional-forecasts/raw/{agrhymet,zenodo}/...`, extracts the
forecast maps embedded in the PDFs, and serves a gallery + year-viewer on GitHub
Pages. For East Africa, ICPAC's geoportal (GeoNode) already serves GHACOF outlook
polygons as shapefiles back to 1998 — the model of what good looks like, and the
planned next addition.
