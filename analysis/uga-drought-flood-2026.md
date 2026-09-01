---
content_type: analysis
name: uga-drought-flood-2026
analysis_type: ad-hoc-activation
status: active
country_iso3: UGA
hazard: [drought, flood]
summary: District-level SEAS5 drought readout + OND flood outlook for the Uganda country team (no HNRP, so JIAF 2.0 Light + reach workbooks replace the HPC mirror), published as a standalone page
data_sources: [SEAS5, ERA5, Floodscan, EM-DAT, ASAP-crop-calendars, JIAF-2.0-Light, CODAB, NOAA-DMI-ONI]
feeds: []
source_repo: ocha-dap/ds-seas5-skill
source_branch: main
source_sha: ed6b6df
code_ref:
  - analysis/uganda_hnrp.qmd
  - pipeline/compute_uga_district_stats.py
  - pipeline/compute_skill_uga_adm2.py
  - pipeline/compute_uga_flood_recurrence.py
  - pipeline/build_uga_crop_calendar.py
  - pipeline/fetch_climate_indices.py
  - src/datasources/uga_country_team.py
depends_on: [raster-pipelines, raster-stats, public.seas5, public.era5, public.floodscan]
discrepancies: []
extra:
  live_url: https://ocha-dap.github.io/ds-seas5-skill/uganda/
  review_pr: https://github.com/OCHA-DAP/ds-seas5-skill/pull/81
visibility: internal
last_synced: 2026-08-24
---

# Uganda drought & flood analysis (Aug 2026) — analysis

> **Analysis, not a framework.** Ad-hoc support to the Uganda country team's
> 2026 planning, published at
> <https://ocha-dap.github.io/ds-seas5-skill/uganda/> (rendered from
> `analysis/uganda_hnrp.qmd`; re-render + copy to `pages/uganda/` to update).

## What it is

Uganda has no HNRP (only the refugee RRP, which the SEAS5-skill app's plan
pipeline excludes), so the Forecast × HNRP methodology was adapted for it:
climate from the same SEAS5/ERA5 sources the app uses, humanitarian data from
country-team workbooks (JIAF 2.0 Light severity + PiN; Gender-MAX
targeted/achieved), plus ASAP crop calendars and a FloodScan-based OND flood
outlook. Structured as: season-to-date → forecast → crop/pasture relevance →
caseload/response → priorities, with flooding as a separate closing section.

## What was analyzed / findings

- **Aug 2026 issuance**: 134/135 districts at the capped 46-yr drought RP for
  their worst rainy-season slot; the discriminator is the deficit (forecast %
  of normal). Karamoja worst (3–17% of normal) in its single wet season;
  season-to-date Apr–Jul was its driest on record (41–54% of normal), a
  false-start shape (wet Feb–Mar, failed Jun–Jul).
- **West Nile** (refugee corridor): season-to-date 84–99% of normal; record-dry
  June hit at harvest, not grain-fill → reduced season, but unimodal: nothing
  replanted until Mar 2027.
- **Oct–Dec is forecast strongly wet** (91st–98th pctile; the Aug-issued OND
  forecast is SEAS5's wettest in its own history, 93rd pctile) with El Niño +
  positive IOD both active — the 2015/2023 configuration.
- **Flood statistics (n=28 OND seasons)**: drivers→rain firm (rain~DMI +0.63,
  rain~ONI +0.55); wettest-quintile ONDs flood more (Mann-Whitney p=0.018);
  direct index→flood links not supported; lag-1 persistence suggestive
  (+0.38, p=0.053) — 2025's record flood came with negative indices.
- **Extent ≠ impact**: FloodScan recurrence concentrates in Teso/Lake Kyoga
  wetlands; EM-DAT impacts concentrate in Kasese and the Mt Elgon landslide
  corridor, which a 9-km SFED product under-sees.

## Gotchas worth reusing

- Uganda is capped at `max_adm_level=1` in the rasterstats DB (`public.iso3`),
  so **district-level SEAS5/ERA5/FloodScan stats do not exist in the DB**;
  they were computed with exactextract from the same processed COGs (region
  means reproduce the DB within ~1%) and live at
  `ds-seas5-skill/processed/uga/` (dev blob).
- ASAP publishes **no crop calendar for Karamoja** (91% rangeland) — that is a
  finding (pastoral zone), not a data gap; West Nile is unimodal in ASAP.
- JIAF operational units vs CODAB: Terego (post-2020 district) sits inside
  CODAB Arua (UG3072); "Madi-Okollo & Terego" → UG3084. Aliases documented in
  `src/datasources/uga_country_team.py`.
- Reach workbooks' admin levels are **independent rollups** (district totals
  exceed region totals) — never sum across levels.
- OND-mean DMI/ONI (NOAA PSL) stored at
  `ds-seas5-skill/raw/climate_indices/ond_indices.parquet` for reproducible
  year classification.

## Relation to frameworks

Standalone country-team support; methodology shared with the SEAS5-skill app's
Forecast × HNRP tab (`pipeline/export_hnrp_drought.py` lineage).

## Sources & status

Repo `ocha-dap/ds-seas5-skill` (main, ed6b6df); live page above; whole-content
review PR: <https://github.com/OCHA-DAP/ds-seas5-skill/pull/81>. Active —
natural re-render points are the Sep/Oct 2026 SEAS5 issuances (bimodal
second-season establishment check; FloodScan watch once OND rains start).
