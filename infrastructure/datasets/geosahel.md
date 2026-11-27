---
content_type: dataset
name: GeoSahel
aliases: [GeoSahel, Biomasse-ACF, "ACF/GeoSahel", "GeoSahel DMP", "Biomasse"]
provider: "Action contre la Faim (Action Against Hunger, Spain), from Copernicus Global Land Service DMP"
data_type: biomass-and-surface-water
access: public
api: "https://geosahel.info/geoserver/ows (OGC WFS; also per workspace, e.g. /geoserver/Biomass/wfs). Moved from http://213.206.230.89:8080/geoserver, unreachable since 2026-11-20"
auth: "none (open)"
formats: [csv, geojson]
resolution: "zonal statistics per admin unit (ADM0–ADM3, West Africa and Sahel); biomass dekadal, surface water monthly from October 2020"
update_cadence: "biomass every dekad but published irregularly (dekads 28–32 of 2026 all appeared between 20 and 23 November); surface water monthly"
license: "not stated on the WFS; attribute ACF/GeoSahel and the Copernicus Global Land Service"
code_ref:
  - "ds-aa-tcd-drought: src/datasources/biomasse.py (Window 3 loader; still on the old host and the stale ef_v1 layer)"
  - "ds-aa-mrt-drought: scripts/season_2026/fetch.sh (new host; biomass and surface water, ADM1 + ADM2)"
mirror: none
mirror_priority: high
used_by:
  - frameworks/tcd-drought/2025-03-03.md
  - frameworks/mrt-drought/2026-04-17.md
  - external-frameworks/wfp/tcd-drought.md
  - analysis/aa-drought-indicators.md
visibility: public
last_verified: 2026-11-23
---

# GeoSahel

Action contre la Faim's GeoSahel platform publishes biomass and surface-water statistics per
admin unit for West Africa and the Sahel through a GeoServer WFS. The biomass is cumulative
dry matter productivity (DMP) from the Copernicus Global Land Service. Chad's Window 3 trigger
([tcd-drought](../../frameworks/tcd-drought/2025-03-03.md)) keys on it, so it is a live CERF
trigger input with no copy in our infrastructure. That is why `mirror_priority` is high.

> **The GeoServer moved (found 2026-11-20).** It is now at `https://geosahel.info/geoserver`.
> The old `http://213.206.230.89:8080/geoserver` is unreachable (checked 2026-11-20 and
> 2026-11-23). The new host serves the same layer names. Code that still requests the old
> host, as of 2026-11-23:
> - `ds-aa-tcd-drought` `src/datasources/biomasse.py` (`_BASE_URL`, on `main`): the Window 3 loader
> - `ds-aa-tcd-drought` `analysis/hnrp_2027_secheresse/fetch_data.sh` (branch `ipc-ch-evolution`)
> - `ds-aa-bfa-drought` `scripts/hnrp_2027/prepare_inputs.py`
> - `pa-anticipatory-action` `src/indicators/drought/biomasse.py` (legacy)
> - `ds-aa-cmr-drought` `src/datasources/biomasse.py` (branch `initial-analysis`; repo archived)

## Layers

| layer | content | state (2026-11-23) |
|---|---|---|
| `Biomass:WA_BIO_ADM{0-3}_v4` | dekadal DMP, columns `DMP_YYYYDD` (dekads 01–36) | **current**: 2026 has real values through dekad 32; later dekads hold the no-data sentinel `-9998.8` |
| `Biomass:WA_DMP_ADM{0-2}_ef_v1` | older dekadal DMP | **stale**: no `DMP_2026*` columns. This is the layer Chad's `biomasse.py` requests; details on the [tcd-drought](../../frameworks/tcd-drought/2025-03-03.md) page |
| `Water:WA_WB_ADM{0-3}_v3` | monthly surface-water area, columns `WB_YYYYMM` | from October 2020 only, so too short for return periods |

The `v4` and `WB` layers carry `adm0_pcode`/`adm1_pcode`/`adm2_pcode`; `ef_v1` uses
`admin0Pcod`/`admin1Pcod` instead. So moving Chad's loader to `v4` means renaming columns as
well as changing the host. A request for one country (`adm0_pcode` is the two-letter code:
`MR`, `TD`, `BF`):

```
https://geosahel.info/geoserver/Biomass/wfs?service=WFS&version=1.0.0&request=GetFeature&typeName=Biomass:WA_BIO_ADM1_v4&outputFormat=csv&CQL_FILTER=adm0_pcode='MR'
```

For Mauritania the `adm1_pcode` and `adm2_pcode` values join to COD-AB v03 (15 wilayas,
63 moughataas). For Chad, `v4` spells TD19 "Barh El Gazel" and `ef_v1` "Barh-El-Gazel".

## How we use it

- **Chad Window 3:** cumulative DMP to dekad 24 over the seven-province area, as a ratio to the
  1999–2024 linear trend; it fires below 84.5%. The 2026 determination used `WA_BIO_ADM1_v4`
  because `ef_v1` had no 2026 data.
- **Chad and Burkina Faso HNRP 2027 drought-risk indices:** `WA_BIO_ADM2_v4`, detrended.
- **Mauritania 2026 season review:** biomass for dekads 10–27 by wilaya and moughataa, and
  October surface water (excluding Trarza and Gorgol, where open water is mostly the Senegal
  River and its lakes). See [mrt-drought](../../frameworks/mrt-drought/2026-04-17.md).

Method documentation: ACF's BioHydroGenerator user guide, linked from the docstring of
`ds-aa-tcd-drought` `src/datasources/biomasse.py`.
