---
content_type: dataset
name: IBTrACS
aliases: [IBTrACS, ibtracs, "International Best Track Archive for Climate Stewardship"]
provider: "NOAA NCEI"
data_type: tropical-cyclone-tracks
access: public
api: "raw v04r01: https://www.ncei.noaa.gov/data/international-best-track-archive-for-climate-stewardship-ibtracs/v04r01/access/netcdf/  ·  landing: https://www.ncei.noaa.gov/products/international-best-track-archive  ·  browser: https://ncics.org/ibtracs/"
auth: "none (open)"
formats: [netcdf, csv]
resolution: "0.1° track points, global; temporal extent varies by basin (Atlantic since the 1850s, others ~1970, more complete since 1980)"
update_cadence: "3× weekly (usually Sun/Tue/Thu); near-real-time lags a few days; official WMO best-track values lag ~1 year"
license: "full and open access (WDC for Meteorology); WMO Resolution 40 guides commercial use"
code_ref: "ocha-lens ibtracs module (get_tracks etc.) → storms.ibtracs_* tables via ds-storms-pipeline"
mirror: automated       # storms-pipeline 'Run IBTrACS' job writes storms.ibtracs_* (check pipeline health)
mirror_priority: high
used_by:
  - pipelines/storms-pipeline.md
  - pipelines/glb-tropicalcyclones.md
  - pipelines/glb-cyclones-impactmodel.md
  - pipelines/hti-hurricanes-impactmodel.md
  - frameworks/cub-hurricanes/2026-06-17.md
  - frameworks/hti-hurricanes/2026-06-09.md
  - frameworks/phl-storms/2025-10-03.md
  - analysis/ibtracs-matching.md
  - apps/glb-tropicalcyclones-app.md
visibility: public
last_verified: 2026-07-10
---

# IBTrACS

NOAA NCEI's **International Best Track Archive for Climate Stewardship** — the merged
global historical record of tropical-cyclone tracks (position, wind, pressure, wind radii)
from all reporting agencies. Our reference set for **historical cyclone analysis** and the
historical half of the storms data backbone. **Operational homes:**
[pipelines/storms-pipeline.md](../../pipelines/storms-pipeline.md) (ingest → the Postgres
`storms.ibtracs_*` tables) and [ocha-lens](../libs/ocha-lens.md) (the loader). This page is
the source reference and quirks.

## How we access it

- **Loader = [`ocha-lens`](../libs/ocha-lens.md)** (`lens.ibtracs`), which
  [ds-storms-pipeline](../../pipelines/storms-pipeline.md) runs to keep
  `storms.ibtracs_storms` / `storms.ibtracs_tracks_geo` (+ wind buffers/exposure) current.
- Upstream: **v04r01** raw data at the NCEI access dir (`.nc` preferred, `.csv` also
  available); quick single-storm lookup via the NCICS browser at `ncics.org/ibtracs`.
- Legacy pre-pipeline product: DEV blob `ibtracs/ibtracs_with_usa_wind.parquet`, built by
  `OCHA-DAP/ds-glb-tropicalcyclones/src/datasources/ibtracs.py` (download + pivot).

## Gotchas

- **PROVISIONAL vs BEST ("main") tracks.** Near-real-time data is flagged `PROVISIONAL`:
  lower quality, subject to change until the agency reanalysis ("best tracking"), usually the
  following year. In practice a **complete** provisional track is rarely adjusted before
  reanalysis; an **incomplete** one (missing time slots) may be updated as data is filled.
  **Recommended update logic** (what the pipeline spec settled on): on each run, re-pull
  **all** provisional tracks in case they changed, add new best-track data, and check whether
  any provisional storm has switched to best track.
- **`US-PROVISIONAL` track_type (new in v04r01).** Lets US (JTWC) provisional data coexist
  with other agencies' best tracks — in v04r00 a best-track update from one agency (e.g. JMA
  in February) would supplant and *remove* all provisional data. For `US-PROVISIONAL`, the
  USA variables **and** the merged position/dependent variables (landfall, storm speed and
  direction, nature) remain subject to change under the same caveats as `PROVISIONAL`.
- **1-min vs 10-min wind averaging.** US agencies (NOAA, JTWC) report 1-minute sustained
  winds; most of the rest of the world uses 10-minute. Rough rule: **peak 1-min ≈ 12% higher
  than peak 10-min** — but procedures vary by agency, so **interbasin comparison of
  intensities is problematic**. Know which agency's wind you're reading. (Cross-agency wind
  comparison is an open question — ocha-lens issue #16.)
- **No direct 1-to-1 SID ↔ ATCF-ID mapping.** ATCF IDs are what NOAA uses operationally
  *before* a SID is assigned; keep a lookup table — NOAA publishes
  `IBTrACS_SerialNumber_NameMapping_v04r01_*.txt` in the same access dir. (Matching work:
  [analysis/ibtracs-matching.md](../../analysis/ibtracs-matching.md).)
- **RSMC La Réunion data is missing for recent years** — points in the SW Indian Ocean can
  lack `wmo_wind` and silently get filtered out by wind-based filters.

## Monitoring the source

- Announcements: `groups.google.com/g/ibtracs-news` · QA forum: `groups.google.com/g/ibtracs-qa`
- Column documentation + change log PDFs/txt on the NCEI v04r01 doc path
  (`.../v04r01/doc/`, e.g. `IBTrACS_v04r01_change_log.txt`).

## Licence & sharing

**Derived products: yes.** Full and open access under the World Data Center for Meteorology
policy, with RSMC agreements permitting open distribution for research; **WMO Resolution 40**
guides commercial use. Cite: "NOAA's International Best Track Archive for Climate Stewardship
(IBTrACS) data, accessed on [date]". See the
[shareability matrix](README.md#can-we-share-derived-products).

---

Source: digested from the retired DSCI Confluence space (full archive: `confluence/` in the
private companion repo `ds-knowledge-base-internal`). Original pages: "IBTrACS Pipeline Spec"
(+ nuggets from "IBTrACS").
