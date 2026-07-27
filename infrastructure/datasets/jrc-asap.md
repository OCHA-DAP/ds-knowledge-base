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
code_ref: null
mirror: none
mirror_priority: med
used_by:
  - analysis/rosea-thresholds.md
  - pipelines/rosea-thresholds-monitoring.md
visibility: public
last_verified: 2026-07-10
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

---

Source: digested from the retired DSCI Confluence space (full archive: `confluence/` in the
private companion repo `ds-knowledge-base-internal`). Original pages: "ASAP", "ROSEA Slow
Onset Monitoring".
