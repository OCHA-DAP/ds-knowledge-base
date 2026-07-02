---
content_type: dataset
name: FAO ASI/VHI
aliases: [FAO-ASI, FAO-VHI, ASI, VHI, ASIS, GIEWS, "FAO ASIS", "Agricultural Stress Index", "Vegetation Health Index"]
provider: "FAO GIEWS — Global Information and Early Warning System (ASIS)"
data_type: agricultural-drought-index
access: public
api: "https://www.fao.org/giews/earthobservation/  ·  FAO Hand-in-Hand geospatial portal + WMS + Google Earth Engine; country data via FAO FTP"
auth: "none (open)"
formats: [geotiff, wms]
resolution: "1 km (METOP-AVHRR); dekadal (10-day), updated ~2–3 days after each dekad"
update_cadence: "every dekad (~36×/year)"
license: "FAO open data, attribution"
code_ref: null
mirror: none
mirror_priority: med
used_by:
  - frameworks/eth-drought/2020-12-07.md
  - frameworks/eth-drought/2026-06-09.md
  - frameworks/afg-drought/2026-04-04.md
  - analysis/syr-drought.md
last_verified: 2026-07-01
---

# FAO ASI / VHI (ASIS)

FAO GIEWS's **Agricultural Stress Index System** — satellite agricultural-drought
monitoring from METOP-AVHRR. The two indicators we tag:

- **ASI (Agricultural Stress Index)** — a *seasonal* index: the % of a cropland/rangeland
  area under drought stress during the growing season. Answers "how much of the ag area is
  stressed this season".
- **VHI (Vegetation Health Index)** — combines vegetation condition (NDVI) and thermal
  stress into a general vegetation-health signal; computed dekadal and monthly, non-seasonal.
- (Related ASIS layers: Drought Intensity, Mean VHI, NDVI anomaly, VCI.)

## How we access it

- **FAO GIEWS Earth Observation** site (`fao.org/giews/earthobservation/`) — browse/download.
- Rasters via the **FAO Hand-in-Hand geospatial portal**, **WMS**, and **Google Earth
  Engine**; **country-level ASIS** downloadable from **FAO FTP**. See the FAO data catalog
  entries for [ASI](https://data.apps.fao.org/catalog/iso/66b7d407-edd4-490e-8b71-a9b7db6527f3)
  and [VHI](https://data.apps.fao.org/catalog/iso/d2a848f2-8ce2-47d7-9e99-b6f175464255).
- **No dedicated loader** — usage has been exploratory (drought monitoring in ETH/AFG/SYR).
  If it becomes a live indicator, GEE or the FTP + a `rioxarray` read is the likely path;
  record it here.

## How we use it

Complementary agricultural-drought signal alongside precipitation forecasts (SEAS5/CHIRPS)
and other vegetation indices — cross-checking whether a rainfall deficit is translating into
crop/rangeland stress.

## Gotchas

- **ASI is seasonal** — only meaningful within the crop calendar; off-season values aren't
  comparable. VHI is year-round but blends moisture and thermal signals.
- **1 km METOP-AVHRR** — coarser and noisier than higher-res EO; treat as a regional signal.
- One of several vegetation-stress products (cf. LEAP-WRSI, USGS NDVI); they don't always
  agree — name the indicator, don't say "vegetation stress" generically.
