---
content_type: dataset
name: FEWS NET
aliases: [FEWSNET, "FEWS NET", "Famine Early Warning Systems Network", FDW]
provider: "USAID Famine Early Warning Systems Network"
data_type: food-security-phase
access: public
api: "https://fdw.fews.net/api/  (FEWS NET Data Warehouse REST API); explorer: https://fews.net/data"
auth: "none for public/owned data; permissions gate some series"
formats: [shapefile, geojson, csv, png]
resolution: "IPC-compatible acute food insecurity phases (1–5); regional shapefiles from Jun 2009, country-level from Oct 2020"
update_cadence: "outlooks ~3×/year (current + near/medium-term projection); FDW updated continuously"
license: "public — USAID/FEWS NET, attribution"
code_ref: OCHA-DAP/ds-fewsnet-mirror
mirror: automated       # mirrored since 2026-08 — see pipelines/fewsnet-mirror.md
mirror_priority: med
used_by:
  - frameworks/som-drought/2019.md
  - frameworks/eth-drought/2020-12-07.md
  - frameworks/eth-drought/2026-06-09.md
last_verified: 2026-07-01
---

# FEWS NET

USAID's **Famine Early Warning Systems Network** — food-security outlooks and
**IPC-compatible** acute food insecurity classifications, with strong coverage in the
Horn of Africa, Sahel, and other USAID priority regions. Pairs with [IPC](ipc.md).

## How we access it

- **FEWS NET Data Warehouse (FDW)** REST API at **`fdw.fews.net/api/`** — the flexible
  path (e.g. `/api/ipcpackage/` for classification packages). The **Data Explorer**
  (`fews.net/data`) is the interactive front end; both let you export shapefiles/CSV.
- Classification data as **GIS shapefiles + images**: regional from **Jun 2009**,
  country-level from **Oct 2020**.
- **Mirrored daily** since 2026-08 by
  [`ds-fewsnet-mirror`](../../pipelines/fewsnet-mirror.md) into the dev DB,
  schema `fewsnet`: the full classification record (`fewsnet.classification`,
  one row per FNID unit × scenario × collection round, 2009+), the latest
  round's unit registry (`fewsnet.units`), and unit geometry in the dev blob
  (`projects/ds-fewsnet-mirror/processed/units/{ISO3}.geojson`). Read it from
  there rather than hitting FDW ad hoc; explorer at
  <https://ocha-dap.github.io/ds-fewsnet-mirror/>. The pipeline page carries
  the keying and absent-data gotchas.

## How we use it

Food-security context and, in some drought frameworks, an activation reference — the
projected phase for the relevant livelihood zones/admin units.

## Gotchas

- **FEWS NET ≠ [IPC](ipc.md).** IPC-*compatible* but FEWS NET's own analysis; the two
  **can disagree**. State which one a trigger uses.
- Outlooks carry **current / near-term / medium-term** projections — pick the period the
  trigger means; don't conflate current with projected.
- Coverage is **region-weighted** (USAID priorities) — not every country is covered.
