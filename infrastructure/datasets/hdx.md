---
content_type: dataset
name: HDX
aliases: ["Humanitarian Data Exchange", humdata]
provider: "UN OCHA Centre for Humanitarian Data (our own Centre)"
data_type: data-platform
access: public
api: "https://data.humdata.org  (CKAN REST API: /api/3/action/…)"
auth: "none for reads; API key only for writes"
formats: [csv, xlsx, geojson, shapefile, geotiff, parquet, "…per-dataset"]
resolution: "n/a — a catalog; grain is per-dataset"
update_cadence: "per-dataset; many series update daily/weekly via HDX's own pipelines"
license: "per-dataset (mostly CC-BY / CC-BY-IGO / open); check each dataset"
code_ref: "hdx-python-api (read-only)"
mirror: n/a             # platform/API queried per-need, not a single mirrorable dataset
mirror_priority: low
used_by:
  - pipelines/raster-pipelines.md
  - pipelines/raster-stats.md
  - pipelines/floodscan-ingest.md
  - pipelines/afro-cholera.md
  - pipelines/nga-flood-monitoring.md
  - apps/cerf-3rm-app.md
  - frameworks/bfa-drought/2026-04-17.md
  - frameworks/eth-drought/2026-06-09.md
  - frameworks/mrt-drought/2026-04-17.md
last_verified: 2026-07-01
---

# HDX — Humanitarian Data Exchange

Not a single dataset but the **platform** (`data.humdata.org`) many of our inputs come
through — COD administrative boundaries, HRP/HNO documents, CERF allocation exports,
partner rasters, and more. It's **OCHA's own** open data portal, built on **CKAN**.

## How we access it

- **Reads need no key.** For a known dataset, hit the **CKAN REST API**
  (`/api/3/action/package_show?id=<slug>`, `datastore_search`, `resource_show`) or just
  download the resource URL.
- **`hdx-python-api`** ([`OCHA-DAP/hdx-python-api`](https://github.com/OCHA-DAP/hdx-python-api))
  is the maintained wrapper — `Dataset.read_from_hdx(...)`, resource iteration, etc.
  Configure it in **read-only mode** (`Configuration.create(hdx_read_only=True)`) and no
  key is required for reads.
- Writing to HDX needs a registered account + API key — we rarely do this from DS repos.

## How we use it

Mostly a **fetch layer**: resolve a dataset slug → download the resource. COD admin
boundaries (via `hdx-python-api` read-only), CERF allocations (the `ocha-stratus` `cerf`
loader reads HDX-sourced Parquet), and one-off partner datasets.

## Gotchas

- **Slugs and resource IDs change**; datasets get archived. Pin the dataset id and
  handle 404s — don't assume a resource URL is permanent.
- Licenses are **per-dataset** — confirm reuse terms on the dataset page, not globally.
- HDX is a **catalog**, not a normalizer: two datasets of "the same" thing can differ in
  admin coding, CRS, and vintage. Reconcile on ingest.
