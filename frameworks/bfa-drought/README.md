# Burkina Faso drought (bfa-drought)

Seasonal (Jun–Oct) drought AA framework. Repo: `ocha-dap/pa-aa-bfa-drought` (pilot-generation `pa-aa-` naming). The repo currently holds **three generations** of trigger code — treat `analysis/monitoring_2026.md` as current.

**Current version: [2026-04-17](2026-04-17.md)** (status: endorsed, valid 2026–2027).

## Version lineage

| version | doc | data source | forecast threshold | triggers | scope | ASAP |
|---|---|---|---|---|---|---|
| pilot 2024-02 | [unocha](https://www.unocha.org/publications/report/burkina-faso/cadre-de-laction-anticipatoire-pilote-de-la-secheresse-au-burkina-faso-version-2024) | IRI NMME tercile | ≥10% area, 40%+5pt | 2 fcast windows | 4 ADM1 regions | — |
| 2025-02-28 | [unocha](https://www.unocha.org/publications/report/burkina-faso/cadre-de-laction-anticipatoire-secheresse-au-burkina-faso-fevrier-2025) | SEAS5 tercile | ≥10% of AOI | 2 fcast + ASAP L4 | 4 ADM1 regions | Level-4, ≥1 region |
| **2026-04-17** | [reliefweb](https://reliefweb.int/report/burkina-faso/cadre-de-laction-anticipatoire-secheresse-en-burkina-faso-17-avril-2026) | SEAS5 tercile | **≥50% of AOI** | 1 fcast (Apr) + ASAP | **2 regions / 4 ADM2** | Level-3, ≥2 provinces |

The IRI→SEAS5 switch and the 10%→50% area-threshold change are the substantive evolution. Legacy HDX [model report](https://data.humdata.org/dataset/2048a947-5714-4220-905b-e662cbcd14c8) documents only the original IRI pilot.
