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
  - "Azure Blob lake (dev account, container `projects`, prefix `ds-geospatial-impact-estimates/`) — GeoParquet, medallion bronze/silver/gold, partitioned `event=<event_id>` above `source=`/`model=` (ADR-0027)"
  - "gold/event=20260624-ve-earthquake/model=common/adm0=VE/facts.parquet (harmonized common-model damage facts)"
  - "gold/event=20260624-ve-earthquake/model=common/adm0=VE/building_flags.parquet (per-building source-agreement flags)"
  - "gold/event=20260624-ve-earthquake/source=<src>/adm0=VE/damage_facts.parquet (native per-source facts)"
  - "bronze/source=codab/adm0=VE/adm{0-3}.parquet (OCHA CODAB admin boundaries — shared reference tree, not event-partitioned)"
  - "silver source extents / CEMS analysed-extent + coverage-detail GeoParquet"
  - "platinum/events.json (event registry, published from repo `events.yaml` by `pipelines/publish_events.py`)"
depends_on: []
surfaces:
  - {url: "https://ocha-dap.github.io/ds-geospatial-impact-estimates/", title: "Geospatial Impact Estimates — OCHA Centre for Humanitarian Data", auto: true, first_seen: 2026-09-01}
  - {url: "https://ocha-dap.github.io/ds-geospatial-impact-estimates/langtang-sar-precursors/", title: "The Glacier That Stopped Refreezing", auto: true, first_seen: 2026-09-01}
  - {url: "https://ocha-dap.github.io/ds-geospatial-impact-estimates/manuscript/", title: "Damage evaluation, technical write-up — passphrase required", auto: true, first_seen: 2026-09-01}
  - {url: "https://ocha-dap.github.io/ds-geospatial-impact-estimates/vantor-activations/", title: "Vantor Open Data activations — Geospatial Impact Estimates", auto: true, first_seen: 2026-09-01}
source_repo: ocha-dap/ds-geospatial-impact-estimates
source_branch: v1
source_sha: 7ee8f10
code_ref:
  - asgi.py
  - api/main.py
  - src/gie/serving.py
  - web/src/main.ts
  - pipelines/publish_events.py
extra: {}
visibility: public
last_synced: 2026-08-14
---

# chd-ds-geospatial-impact-viewer

> An interactive deployed surface. Optimize for "what it shows, who it's for, and how to keep it running."

## What it shows

A map-first viewer for **multi-source, satellite-derived building-damage exposure**, built
first for the **Venezuela earthquake** (adm0=VE) response and, since 2026-08-14 (ADR-0027),
genuinely **multi-event** rather than just designed for it. It harmonizes heterogeneous AI/ML
damage data — **Microsoft AI** per-building damage labels, **Copernicus EMS** (EMSR884)
rapid-mapping damage, and the **IMPACT Initiatives Sentinel-1 SAR** damage proxy — onto a common
Overture building base and an H3 grid, aggregated to OCHA COD admin 0/1/2/3 units. The core
question it answers: **what does each source say about damage for the same unit, and where do
they agree or disagree?** Damage is aligned across sources to the Copernicus EMS grades (Possibly
/ Damaged / Destroyed); SAR z-score thresholds are mapped onto the same scale (ADR-0008 — SAR is a
preliminary hotspot/gap screen, *not* confirmed damage).

## Key features

- **Event landing page + per-event routing** (ADR-0027, since 2026-08-14): `/` lists registered
  events from `platinum/events.json`; each opens its own map view at `#/e/<event_id>`.
- **Full-bleed MapLibre GL basemap + deck.gl overlays** (custom Vite + TypeScript SPA, ADR-0004),
  with floating control/legend/comparison panels and rich `onHover` tooltips — chosen over
  Streamlit/Solara because the map is the product.
- Toggleable layers: **admin choropleth** (adm1/2/3), **H3 hexagon** grid, raw **building
  footprints**, **coverage/analysed extent**, and a **source-agreement** view (the spatial Venn:
  both-damaged / Microsoft-only / Copernicus-only / agree-undamaged).
- Metric selector: damaged buildings (detected), damaged buildings (estimated/extrapolated),
  coverage fraction, total buildings.
- Per-source and `view=overture` vs `view=native` toggles.
- **XLSX export** — client-side via `exceljs` (per-admin-unit, per-source damage table, one sheet
  per admin level); the old server-rendered `/api/export.xlsx` survives only as an App
  Service-side fallback, gated to the legacy `20260624-ve-earthquake` event (PR #50).
- Standalone: serves its own in-repo harmonization pipelines, not a published AA framework.

## Data

Serving is **client-side (v2)** since 2026-07-15 (ADR-0011): the browser reads **PMTiles** and
**GeoParquet** directly from blob — no DuckDB/FastAPI query layer in the request path for the SWA
host. Auth is a short-lived, read-only, directory-scoped SAS
(`?app=satellite-viewer&tier=<staging|prod>`) minted per-request by the shared
[token issuer](../infrastructure/token-issuer.md) (ADR-0022). Container `projects`, prefix
`ds-geospatial-impact-estimates/`, medallion `bronze/silver/gold` GeoParquet layout; since
2026-08-14 (ADR-0027) every tier is partitioned `event=<event_id>` above `source=`/`model=` (see
Multi-event, below) except the shared CODAB reference tree. Freshness is whatever the in-repo
ingestion/harmonization pipelines (`pipelines/`, run via `run_all.py`) last wrote — there is no
scheduled refresh; `data_ledger.md` is the provenance view. The old **server-side
DuckDB-over-blob / FastAPI GeoJSON** path (`api/main.py`, `gie.serving`) is obsolete for the SWA
host and now only backs the App Service's own (legacy, un-evented) serving.

## Multi-event (ADR-0027, since 2026-08-14)

PRs #51/#52 made the viewer multi-event: `/` is a landing page of registered events read from
`platinum/events.json`, published from the repo's `events.yaml` by `pipelines/publish_events.py`;
per-event map views live at `#/e/<event_id>`. Two events are registered: `20260624-ve-earthquake`
(full data — the original Venezuela buildout) and `20260810-co-earthquake` (registered, no
products yet — the UI states this explicitly rather than showing an empty map). Blob layout:
every tier gains an `event=<id>` partition above `source=`; CODAB stays a shared reference tree
(`bronze/source=codab/adm0=XX`), not event-partitioned; the original VE tree was server-side
copied under its event partition, and the pre-event legacy tree is still in place — its deletion
is gated on the App Service retirement decision.

## Deployment & access

- **Two parallel hosts, one codebase/branch (`v1`)** since 2026-07-15 (ADR-0023): the
  **Static Web App `chd-ds-satellite-impact-viewer`** (Free tier, same RG,
  https://ashy-sea-03134990f.7.azurestaticapps.net) is the live production host, deployed by
  `swa-deploy.yml` (push to `v1` → prod; **PRs touching `web/` → SWA preview environments** on
  the staging data tier). As of 2026-08 it has **zero App Service dependencies** — PR #50 severed
  the last one, a server-side export fallback, which is now gated to the legacy
  `20260624-ve-earthquake` event only.
- **Azure App Service** Linux Python 3.13 web app `chd-ds-geospatial-impact-viewer` on plan
  `DsciAppServicePlan`, resource group `IMB-CHD-DataScience-EastUS2`; state Running.
  URL: https://chd-ds-geospatial-impact-viewer.azurewebsites.net. It is now the **legacy
  fallback host**: pinned to the old, un-evented blob layout (no multi-event support), and its
  retirement is decidable now that the SWA has no dependency on it.
- CI is deployed via GitHub Actions: `swa-deploy.yml` (SWA, as above) and `azure-deploy.yml` (App
  Service). One app still serves **both API and SPA** on the App Service host: `asgi.py` is the
  gunicorn entry point (adds `src/` to path, exposes `app`); FastAPI mounts the built Vite SPA
  (`web/dist`) at `/` *after* the `/api` routes. Startup:
  `gunicorn asgi:app -k uvicorn.workers.UvicornWorker -w 2 -b 0.0.0.0:8000`, `--always-on`.
- **Staging + production slots** (ADR-0007). `STAGE` sticky slot settings keep each slot on its
  own data tier across swaps; the staging/prod data split (`platinum` vs `platinum-prod`) now
  rides the token issuer's `?tier=` parameter. Publicly reachable (CORS `allow_origins=["*"]`).
- **Blob auth is the shared [token issuer](../infrastructure/token-issuer.md)** (ADR-0022,
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

- **CI exists**: `swa-deploy.yml` (push to `v1` → SWA prod; PRs touching `web/` → SWA preview
  envs on the staging tier) and `azure-deploy.yml` (App Service). The App Service deploy is still
  zip-based under the hood (Oryx build, matches sibling `chd-ds-*` apps): build the SPA
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
  Even the production slot reads **dev** blob data (`STAGE=dev`); this is an early-stage
  exploratory tool, labelled as such in the UI.
