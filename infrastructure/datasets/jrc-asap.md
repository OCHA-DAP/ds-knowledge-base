---
content_type: dataset
name: JRC ASAP
aliases: [ASAP, "JRC ASAP", "Anomaly hot Spots of Agricultural Production", APH]
provider: "European Commission Joint Research Centre (JRC)"
data_type: agricultural-drought-warnings
access: public
api: "https://agricultural-production-hotspots.ec.europa.eu (warnings/hotspots downloads + docs; SF-warnings doc at /documentation-sf-warnings.php)"
auth: "none (open)"
formats: [csv, geotiff, shapefile]
resolution: "sub-national admin units × landcover (cropland/rangeland) 'units'; warnings every dekad (10 days), global; hotspots monthly, ~70 food-insecure countries"
update_cadence: "warnings every dekad; hotspot assessment monthly"
license: "EC/JRC open data, attribution"
code_ref:
  - "ds-asap-trends: src/asap.py (indicator-statistics export client)"
mirror: none
mirror_priority: med
used_by:
  - analysis/rosea-thresholds.md
  - pipelines/rosea-thresholds-monitoring.md
  - analysis/asap-indicator-trends.md
visibility: public
last_verified: 2026-07-31
---

# JRC ASAP

The EC/JRC **Anomaly hot Spots of Agricultural Production** system — automated
agricultural-drought **warnings** per admin unit, plus expert-reviewed monthly
**hotspots**. Feeds the **ROSEA slow-onset monitoring**
([analysis/rosea-thresholds.md](../../analysis/rosea-thresholds.md), operational pipeline
[rosea-thresholds-monitoring](../../pipelines/rosea-thresholds-monitoring.md)), where the
country alert level = MAX of the ASAP and IPC classifications.

> **Not the same thing as [FAO GIEWS ASI/VHI](fao-asi-vhi.md).** JRC ASAP (EC/JRC,
> `agricultural-production-hotspots.ec.europa.eu`) and FAO ASIS/ASI are different
> agricultural-drought products from different agencies. Name which one you mean.

Primary doc: `asap_warning_classification_v_8_0.pdf` on the ASAP site.

## The three products: warnings, hotspots, and the raw indicator statistics

Beyond the warnings and hotspots, ASAP also publishes the **per-admin-unit indicator
statistics** the warnings are computed *from* — the dekadal unit mean of every indicator.
This is usually what you want if you're analysing *why* a warning fired (or didn't), and
it avoids touching the rasters. See
[Indicator statistics](#indicator-statistics-the-raw-numbers-behind-the-warnings) below.

## Warnings vs hotspots

| | **Warnings** | **Hotspots** |
|---|---|---|
| how | fully automated, objective agricultural-indicator thresholds | declared as a second step after higher warnings persist; analysis by agricultural specialists |
| cadence | every 10 days (dekadal) | monthly |
| coverage | global, sub-national admin units | ~70 selected food-insecure countries |
| grain | levels 1–4 per unit, only during the growing season | coarse: no hotspot / hotspot / major hotspot (+ not-assessed) |

## Warning levels (croplands and rangelands)

1. **Level 1** — water-balance deficit possibly evolving to poor growth
2. **Level 2** — biomass evidence of poor growth
3. **Level 3** — water balance + biomass (poor growth AND negative prospects)
4. **Level 4** — end-of-season biomass: poor season growth; only triggered toward the end
   of the season

## Season definitions (what gates the warnings)

The seasonality is **stationary** (does not change year-on-year) and determines when each
warning type can "switch on".

- **Pixel level** (from phenology, per dekad): **SOS** (start of season — enters expansion,
  then maturation after the phenological MAX), **SEN** (start of senescence), **EOS** (end of
  season). A pixel is **active** between its SOS and EOS.
- **Unit level** (a "unit" = landcover [cropland/rangeland] × admin), aggregated from pixels:
  - **SOS** reached when **≥15%** of unit pixels reach their SOS → warning levels **1–3**
    become possible.
  - **Start of senescence** reached when **≥50%** of *active* unit pixels have reached SEN
    → level **4** becomes possible.
  - **EOS** reached when **<15%** of unit pixels are active → "Off season", no warnings.

### The "reference dekad" caveat (not in the public docs)

Communicated to us directly by ASAP: each unit has a **reference dekad** = the last dekad at
which a large proportion of unit pixels are still active. **After the reference dekad,
level-4 warnings should effectively be ignored** — they are based on too small a fraction of
the actual growing area.

## Alert thresholds

- A warning is issued when an indicator meets its threshold for **≥25% of the active area**
  of the unit.
- All observational indicators are **Z-score normalized** with a threshold of **−1** (one
  standard deviation below the historical mean).

### Seasonal-forecast (SF) warnings

- Can only be issued for valid months in the **"precipitation sensitive period"** = the unit
  season, but starting **one month earlier** and ending **MAX(one month, one quarter of the
  season length) earlier** (whichever shortens it more).
- Require **≥1 month overlap** between the forecast valid time (max 6-month leadtime) and the
  precipitation-sensitive period.
- Issued when **≥25% of the active area** has a **≥40% probability of the lower tercile**,
  AND the forecast skill is better than random (**RPSS > 0**).
- Docs: `agricultural-production-hotspots.ec.europa.eu/documentation-sf-warnings.php`.

### Breakpoints

Some units carry a **breakpoint** splitting the season in two — used when a unit effectively
contains two seasons (e.g. western pixels switch off just as eastern pixels switch on,
keeping the active fraction above 15%). Breakpoints only affect **SF warnings** (which of the
two seasons a warning is attributed to); the exact definition is under-documented by JRC.

## Indicator statistics — the raw numbers behind the warnings

ASAP computes, for every ASAP GAUL unit, the **dekadal mean of each indicator**, and
publishes it as a downloadable time series. These are the exact values the warning
classification is thresholded on, so they answer "why did/didn't this unit warn" without
downloading a single raster.

The download page exposes this only as a **form** ("Indicator Statistics"), with no
documented REST API. The form posts to an endpoint you can drive directly:

```
GET https://agricultural-production-hotspots.ec.europa.eu/export/rum/export.php
    ?gaul_level=1&country_id=88&variable_id=240&class_id=1&classesset_id=1&sensor_id=3
```

Returns a tidy CSV, one row per unit × dekad, for the indicator's full record. Valid id
combinations — and the country lookup — come from `/getDataDownload.php` (JSON).
Client: `src/asap.py` in [`ds-asap-trends`](https://github.com/OCHA-DAP/ds-asap-trends).

**Gotchas, all of which cost time the first go:**

- **`country_id` is ASAP's own `asap0_id`** — not ISO, not GAUL `adm0_code`. South Sudan is
  `88` (its `adm0_code` is 74). Always resolve from `/getDataDownload.php`.
- **`classesset_id` picks the mask**: `1` = "during growing cycle" (in-season pixels only),
  `2` = the whole landcover mask year-round. **The warning classification uses `1`.**
- **Only certain (variable, class, classesset, sensor) combinations exist.** WSI uses a
  *different `variable_id` per landcover* (160 crop, 170 rangeland). Invalid combinations
  return an HTML error page rather than an error status, so validate that the body starts
  with the CSV header.
- **⚠ There is no downloadable zWSI.** The download page's tooltip describes variable
  160/170 as *"zWSI — [Anomaly] Z-score of the Water Satisfaction Index"*, but the export
  returns the **raw WSI on a 0–100% scale** (the CSV's own `variable_name` comes back as
  "Water Satisfaction Index (WSI)"). The z-scored WSI the classification actually
  thresholds is not exposed — derive it yourself from the raw series if you need to compare
  against −1. zFPARc, zFPAR and SPI-3 *are* published pre-normalized.
- **Records start at different dates**: meteo (rainfall, temperature, SPI-3) from 1989, WSI
  1991, MODIS FPAR only 2001. Don't compare trends across indicators without a common window.
- **⚠ Soil moisture has a methodology break.** ASAP gapfills it only to dekad **2023-12-21**
  and continues with un-gapfilled soil moisture after. The series steps down at exactly that
  cutover, so it should not be used for trend analysis.

Also downloadable in bulk: `warnings_ts.zip` / `warnings_l2_ts.zip` (full warning history
since 2001-05), `hotspots_ts.zip` (since 2016-10, what the ROSEA pipeline pulls), the
`gaul{0,1,2}_asap` boundary shapefiles, crop calendars, phenology, and the indicator
rasters. Warnings are also served as WFS/WMS from `/public/ows?`.

### The z-score drift problem

Because every observational threshold is a z-score against the **full historical record**,
an indicator with a real long-term trend drifts away from its own fixed −1 threshold — the
same physical conditions stop triggering a warning as the record lengthens. This is
measured for South Sudan in
[analysis/asap-indicator-trends.md](../../analysis/asap-indicator-trends.md): zFPARc on
rangeland rose ~0.5 z/decade and its threshold-breach rate fell from 15.5% of in-season
dekads (2001–2005) to 1.1% (2022–2026), while SPI-3 and WSI showed no significant trend.
Worth checking before treating an ASAP warning level as a stationary indicator of severity.

---

Source: digested from the retired DSCI Confluence space (full archive: `confluence/` in the
private companion repo `ds-knowledge-base-internal`). Original pages: "ASAP", "ROSEA Slow
Onset Monitoring".
