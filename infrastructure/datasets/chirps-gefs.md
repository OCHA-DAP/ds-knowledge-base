---
content_type: dataset
name: CHIRPS-GEFS
aliases: [CHIRPS-GEFS, chirps_gefs, "CHIRPS GEFS"]
provider: "UCSB Climate Hazards Center (CHC)"
data_type: rainfall-forecast
access: public
api: "https://www.chc.ucsb.edu/data/chirps-gefs (docs + data links; rasters served from the CHC data server)"
auth: "none (open)"
formats: [geotiff]
resolution: "0.05°, global; daily updates; 16-day leadtime"
update_cadence: "daily"
license: "open (CHC; public data, attribution)"
code_ref: null
mirror: none            # unresolved data-volume design question — see below
mirror_priority: med
used_by:
  - pipelines/hti-hurricanes-monitoring.md
  - pipelines/hti-hurricanes-impactmodel.md
  - frameworks/hti-hurricanes/2026-06-09.md
  - frameworks/cub-hurricanes/2026-06-17.md
  - frameworks/mmr-cyclones/development.md
  - frameworks/yem-flooding/2023.md
  - apps/hti-hurricanes-app.md
visibility: public
last_verified: 2026-07-10
---

# CHIRPS-GEFS

UCSB CHC's **CHIRPS-calibrated GEFS rainfall forecast** — the NOAA GEFS ensemble forecast
bias-corrected/downscaled to match **CHIRPS**, and validated against it. Our short-term
(sub-seasonal) forecast-rainfall input where a framework needs *forecast* rain at CHIRPS-like
resolution.

- **Daily updates**, **16-day leadtime**, **global**, **0.05°**.
- Sits in the CHIRPS family: CHIRPS v2.0 (observational, published 3rd week of the month),
  CHIRPS Prelim (lower latency), CHIRPS-GEFS (forecast).

## How we use it

**Raster stats over the AOI** for forecast-rainfall monitoring in hurricane/flood framework
monitoring — the Haiti (and Cuba) hurricanes rainfall trigger legs, Myanmar cyclones work,
and Yemen flooding. Pulled per-run from the CHC source by the monitoring pipelines; there is
no shared ingest.

## Gotchas / open questions

- **Unresolved data-volume design question (as of 2026-02):** how to manage volume if we
  ingest CHIRPS-GEFS into our own infra. Options weighed — sparse storage (drop precip==0
  cells), limiting pcodes, keeping no COGs and reading directly from the UCSB source,
  an on-demand COG-stacking pipeline, or limiting leadtime — **none chosen yet**. Until then
  there is no blob mirror; analyses read from CHC directly.
- It's a **forecast calibrated to CHIRPS** — compare against CHIRPS (not raw GEFS or other
  observational products) when validating.

---

Source: digested from the retired DSCI Confluence space (full archive: `confluence/` in the
private companion repo `ds-knowledge-base-internal`). Original page: "CHIRPS-GEFS" (+ facts
from "Core Data Sets").
