---
content_type: app
name: google-flood-hub
purpose: "Maps Google's Flood Forecasting API v1 and shows what its event products (significant events, flash floods, gauge flood status) currently report"
status: live
tech: other
related: standalone
deployment:
  platform: gh-pages
  ref: "ocha-dap/ds-google-flood-hub@main"
  url: "https://ocha-dap.github.io/ds-google-flood-hub/"
  resource_group: null
surfaces:
  - {url: "https://ocha-dap.github.io/ds-google-flood-hub/events/", kind: app, title: "Current flood events map"}
  - {url: "https://ocha-dap.github.io/ds-google-flood-hub/api/", kind: docs, title: "Flood Forecasting API v1 surface map"}
  - {url: "https://sites.research.google/floods/", kind: app, title: "Google Flood Hub", origin: external}
  - {url: "https://developers.google.com/flood-forecasting", kind: docs, title: "Google Flood Forecasting API docs", origin: external}
inputs:
  - "Google Flood Forecasting API v1 (external, live at deploy time): significantEvents:search, flashFloods:search, floodStatus:searchLatestFloodStatusByArea, floodStatus:queryLatestFloodStatusByGaugeIds, serializedPolygons.get, $discovery/rest"
depends_on: []
source_repo: ocha-dap/ds-google-flood-hub
source_branch: main
source_sha: 6c04490
code_ref:
  - "scripts/fetch_snapshot.py"
  - "scripts/build_api_page.py"
  - "pages/index.html"
  - "pages/events/index.html"
  - ".github/workflows/deploy-pages.yml"
extra: {}
visibility: public
last_synced: "2026-09-24"
---

# google-flood-hub

> An interactive deployed surface. Optimize for "what it shows, who it's for, and how to keep it running."

## What it shows

A public map of Google's Flood Forecasting API — the API behind Google's own [Flood Hub](https://sites.research.google/floods/) — focused on the parts of the API the team does **not** already consume operationally. Two team monitoring pipelines (`ds-aa-som-floods` → [som-floods-monitoring](../pipelines/som-floods-monitoring.md), `ds-aa-nga-flooding` → [nga-flooding-monitoring](../pipelines/nga-flooding-monitoring.md)) already use the API's gauge-forecast endpoints day to day; this repo instead documents and snapshots the **event products** — significant events, flash floods, gauge flood status, and their polygons — which have no history of their own and are only observable by checking them regularly. The landing page (`/`) links to two products: a current-events map (`/events/`) and a generated API surface-map reference (`/api/`).

## Key features

- **`/events/`** — a Leaflet world map built from a daily snapshot (`pages/events/data/snapshot.json`, written at deploy time by `scripts/fetch_snapshot.py`): significant-event polygons with the people/area Google predicts in their path and the gauges behind each event (coloured by severity), flash-flood forecast polygons (likely vs highly-likely), and every quality-verified gauge worldwide whose latest status is not `NO_FLOODING`. Toggleable layers, a per-country flash-flood table, a per-severity gauge count table, and a click-to-zoom event list in the sidebar.
- **`/api/`** — every method, field and enum of API v1, rendered by `scripts/build_api_page.py` from Google's own discovery document (`$discovery/rest?version=v1`) plus hand-written observed-behaviour notes (`api/observations.json`) — filters that don't exist (rejected with `400 Unknown name`), pagination quirks, the `cutoffTime` 2025-08-01 floor, the KML polygon format, and a running "since the team's March 2026 feedback to Google" answered/still-open list. Also shows API **drift**: the committed baseline `api/discovery.json` is diffed against the live discovery document fetched at build time, flagging any new/removed method, schema or field.
- `/` — hand-edited landing page linking both products plus Google's own Flood Hub map and API docs.

Not a framework or pipeline companion: it serves no single AA framework, it is a standalone reference/monitoring surface over a third-party API.

## Data

Everything is read directly from the live Flood Forecasting API at **deploy time** with the team's `GOOGLE_API_KEY` (a Google Cloud API key on the same project the two flood monitors use, quota 200 req/min) and published as a static JSON/HTML snapshot — the key never reaches the browser, nothing generated is committed. `scripts/fetch_snapshot.py` pulls, in order: (1) `significantEvents:search` with each event's polygon and the flood status of every gauge it lists, (2) `flashFloods:search` with likely/highly-likely polygons, (3) a worldwide sweep of `floodStatus:searchLatestFloodStatusByArea` over four 90°-wide longitude quadrants (a single world-spanning loop is ambiguous on the sphere and returns nothing or a partial set — observed 2026-09-24), and (4) the live discovery document. Transient 5xx/429 responses are retried with backoff (up to 4 attempts — a 503 on `serializedPolygons.get` was seen in CI on 2026-09-24). No database or blob store of ours is involved — this is a pure external-API read. The API itself is "latest-only" for events (no history endpoint), so the map only ever shows current state; a longer record would require accumulating these daily snapshots. Freshness: refreshed daily (09:15 UTC) plus on every push to `main` and on manual dispatch — timely enough that flash floods (issued ~06:30 UTC) and same-day flood-status updates are captured.

## Deployment & access

GitHub Pages, deployed via `.github/workflows/deploy-pages.yml` (Pages-artifact modality, not a `gh-pages` branch) on push to `main` (paths `pages/**`, `scripts/**`, `api/**`, the workflow itself), daily at 09:15 UTC, and `workflow_dispatch`. Public, no auth: <https://ocha-dap.github.io/ds-google-flood-hub/>. No dev/prod slot distinction — one site, one branch. The only secret is the repo secret `GOOGLE_API_KEY`. Not in `infrastructure/deployments.md`'s Azure table (it's a GH Pages site, not an App Service app); confirmed there is no existing row for it there.

## Maintenance / known issues

- Redeploy = re-run the workflow (push, schedule, or manual dispatch); both scripts run fresh each time and nothing generated is committed, so a broken deploy leaves the previously-published Pages artifact live rather than a half-built site.
- **API drift**: `api/discovery.json` is the committed baseline; the build compares it to the live discovery document and the `/api/` page states what changed (new/removed methods, schemas, or field sets). After reviewing a drift, refresh the baseline by copying `pages/api/discovery.json` over `api/discovery.json` and committing.
- **Known API limitations baked into the design** (see `api/observations.json` / the `/api/` "Since March 2026" section): significant events and flash floods are latest-only with no time filter or country/region filter (`significantEvents:search` takes no filters at all — filter client-side); `floodStatus` area search matches on gauge location, not the event polygon; a single world-spanning `loop` query is ambiguous and returns incomplete results — the quadrant workaround in `fetch_snapshot.py` is required, not optional; `eventTrackingIds` is a best-effort join key across days, not a stable id (an event that drops below Google's score threshold and returns gets a new id; merged events carry several).
- Rate limit is shared with the team's operational monitors (200 req/min per project) — a full snapshot run is ~170 requests / ~1 minute, well under quota, but a quota change on the shared project would affect this site too.
- Quirk carried in code comments: CARTO basemaps started requiring an API key in 2026, so the events map uses the key-free Esri "Light Gray Canvas" tile layer instead.
- No CI test suite; correctness is checked by reading the deployed pages after a change (`python -m http.server -d pages 8000` locally, per the README).
