---
content_type: app
name: chd-ds-geospatial-impact-viewer
purpose: Map-first viewer comparing multi-source satellite damage-exposure estimates for the same admin/H3 unit
status: live
tech: other
related: standalone
deployment:
  platform: azure-webapp
  ref: chd-ds-geospatial-impact-viewer
  url: https://chd-ds-geospatial-impact-viewer.azurewebsites.net
  resource_group: IMB-CHD-DataScience-EastUS2
inputs:
  - "Azure Blob lake (dev account, container `projects`, prefix `ds-geospatial-impact-estimates/`) — GeoParquet, medallion bronze/silver/gold"
  - "gold/model=common/adm0=VE/facts.parquet (harmonized common-model damage facts)"
  - "gold/model=common/adm0=VE/building_flags.parquet (per-building source-agreement flags)"
  - "gold/source=<src>/adm0=VE/damage_facts.parquet (native per-source facts)"
  - "bronze/source=codab/adm0=VE/adm{0-3}.parquet (OCHA CODAB admin boundaries)"
  - "silver source extents / CEMS analysed-extent + coverage-detail GeoParquet"
depends_on: []
source_repo: ocha-dap/ds-geospatial-impact-estimates
source_branch: v1
source_sha: 82d785e
code_ref:
  - asgi.py
  - api/main.py
  - src/gie/serving.py
  - web/src/main.ts
extra: {}
visibility: public
last_synced: 2026-06-29
---

# chd-ds-geospatial-impact-viewer

> An interactive deployed surface. Optimize for "what it shows, who it's for, and how to keep it running."

## What it shows

A map-first viewer for **multi-source, satellite-derived building-damage exposure**, built
first for the **Venezuela earthquake** (adm0=VE) response and designed to generalize to other
events. It harmonizes heterogeneous AI/ML damage data — **Microsoft AI** per-building damage
labels, **Copernicus EMS** (EMSR884) rapid-mapping damage, and the **IMPACT Initiatives
Sentinel-1 SAR** damage proxy — onto a common Overture building base and an H3 grid, aggregated
to OCHA COD admin 0/1/2/3 units. The core question it answers: **what does each source say about
damage for the same unit, and where do they agree or disagree?** Damage is aligned across sources
to the Copernicus EMS grades (Possibly / Damaged / Destroyed); SAR z-score thresholds are mapped
onto the same scale (ADR-0008 — SAR is a preliminary hotspot/gap screen, *not* confirmed damage).

## Key features

- **Full-bleed MapLibre GL basemap + deck.gl overlays** (custom Vite + TypeScript SPA, ADR-0004),
  with floating control/legend/comparison panels and rich `onHover` tooltips — chosen over
  Streamlit/Solara because the map is the product.
- Toggleable layers: **admin choropleth** (adm1/2/3), **H3 hexagon** grid, raw **building
  footprints**, **coverage/analysed extent**, and a **source-agreement** view (the spatial Venn:
  both-damaged / Microsoft-only / Copernicus-only / agree-undamaged).
- Metric selector: damaged buildings (detected), damaged buildings (estimated/extrapolated),
  coverage fraction, total buildings.
- Per-source and `view=overture` vs `view=native` toggles.
- **XLSX export** (`/api/export.xlsx`) — per-admin-unit, per-source damage table, one sheet per
  admin level.
- Standalone: serves its own in-repo harmonization pipelines, not a published AA framework.

## Data

Read-only via **DuckDB-over-blob** (`spatial`+`azure`+`h3` extensions) — no Postgres. The FastAPI
layer (`api/main.py`) wraps `gie.serving` queries and returns GeoJSON/JSON, in-memory `lru_cache`d
per process and browser-cached (`max-age=300, stale-while-revalidate=3600`). Data is the **dev**
blob account (`GIE_STAGE=dev` / `STAGE=dev` slot setting); container `projects`, prefix
`ds-geospatial-impact-estimates/` in a medallion `bronze/silver/gold` GeoParquet layout. The
served layer is the coverage-aware **gold common-model** (`gold/model=common/adm0=VE/`). Freshness
is whatever the in-repo ingestion/harmonization pipelines (`pipelines/`, run via `run_all.py`)
last wrote — there is no scheduled refresh; the ledger (`data_ledger.md`) is the provenance view
(VE common-model last written 2026-06-28). After a data refresh, **restart the app** to re-read
the new gold (clients pick it up within `max-age`).

## Deployment & access

<!-- TODO: full re-sync needed — the serving architecture moved to v2 (client-side
PMTiles/hyparquet, ADR-0011-v2) in July 2026; the Data section above still describes the v1
server-side DuckDB/GeoJSON path. Below reflects the hosting/auth state as of 2026-07-15. -->

- **Two parallel hosts, one codebase/branch (`v1`)** since 2026-07-15 (ADR-0023): the new
  **Static Web App `chd-ds-satellite-impact-viewer`** (Free tier, same RG,
  https://ashy-sea-03134990f.7.azurestaticapps.net, deployed by `swa-deploy.yml` — push → prod,
  **PRs touching `web/` → SWA preview environments** on the staging data tier) **supersedes**
  the App Service; the App Service stays as the classic-URL / stale-client fallback until a
  retirement decision. A build-time config switch (`web/src/config.ts`: `VITE_TOKEN_URL` /
  `VITE_API_BASE`; unset ⇒ byte-identical classic build) keeps the two builds from forking.
- **Azure App Service** Linux Python 3.13 web app `chd-ds-geospatial-impact-viewer` on plan
  `DsciAppServicePlan`, resource group `IMB-CHD-DataScience-EastUS2`; state Running.
  URL: https://chd-ds-geospatial-impact-viewer.azurewebsites.net
- One app serves **both API and SPA**: `asgi.py` is the gunicorn entry point (adds `src/` to path,
  exposes `app`); FastAPI mounts the built Vite SPA (`web/dist`) at `/` *after* the `/api` routes.
  Startup: `gunicorn asgi:app -k uvicorn.workers.UvicornWorker -w 2 -b 0.0.0.0:8000`, `--always-on`.
- **Staging + production slots** (ADR-0007). `STAGE` sticky slot settings keep each slot on its
  own data tier across swaps; the staging/prod data split (`platinum` vs `platinum-prod`) now
  rides the token issuer's `?tier=` parameter. Publicly reachable (CORS `allow_origins=["*"]`).
- **Blob auth is now the shared [token issuer](../infrastructure/token-issuer.md)** (ADR-0022,
  live 2026-07-14): a keyless, read-only, directory-scoped, ~24h user-delegation SAS
  (`?app=satellite-viewer&tier=<staging|prod>`), used to read PMTiles/Parquet directly from
  blob. The two hosts consume it differently: the **SWA client calls the issuer directly**
  (`VITE_TOKEN_URL`); the **App Service client calls its own `/api/token`**, whose server
  proxies the issuer (cached, refreshed when <6h remain) and degrades gracefully — issuer →
  own-MI-minted SAS → legacy `GIE_PLATINUM_SAS` app setting → `mode: unavailable`
  (`api/main.py`). So the hand-rotation chore is gone, but `GIE_PLATINUM_SAS` survives as the
  last-resort fallback (the previously "planned managed-identity upgrade" landed as the
  standalone issuer's MI instead, so it outlives the App Service).
- Cross-ref [infrastructure/deployments.md](../infrastructure/deployments.md).

## Maintenance / known issues

- **No CI** — zip-deploy with Oryx build (matches sibling `chd-ds-*` apps): build the SPA
  (`cd web && npm run build`), generate `requirements.txt` from the lock
  (`uv export --no-dev --group api --no-emit-project --no-hashes`), zip exactly
  `api src web/dist requirements.txt asgi.py`, `az webapp deploy --type zip`, verify on `staging`,
  then promote by **slot swap**. `web/dist` is gitignored and built per deploy.
- **Azure-extension TLS gotcha** (ADR-0007): the DuckDB `azure` extension's default transport
  couldn't verify TLS to blob on the App Service image. Fix in `db.py`:
  `SET azure_transport_option_type = 'curl'` **and** point **`CURL_CA_INFO`** (not `CURL_CA_BUNDLE`)
  at `certifi.where()`. No-op locally.
- **Cold start ~15 s** on first `/api/common/admin/3` call (DuckDB + ~4 MB GeoJSON build), then
  lru-cached. (The old long-lived-SAS rotation chore is gone — tokens now come from the
  [token issuer](../infrastructure/token-issuer.md), with `GIE_PLATINUM_SAS` kept only as the
  last-resort fallback.)
- **Discrepancies:** app name (`...-viewer`) ≠ repo name (`ds-geospatial-impact-estimates`).
  Even the production slot reads **dev** blob data (`STAGE=dev`); this is a single-event (VE),
  early-stage exploratory tool, labelled as such in the UI.
