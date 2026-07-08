---
content_type: pipeline
name: ven-earthquake-support
type: exposure
status: live
deployment:
  platform: github-actions
  resource_group: null
  jobs:
    - { name: "Refresh official sources", ref: ".github/workflows/refresh.yml", schedule: "cron: 23 * * * * (hourly, :23)", status: live }
    - { name: "Zonal exposure (ShakeMap × population)", ref: ".github/workflows/zonal.yml", schedule: "cron: 41 */3 * * * (every 3h, :41)", status: live }
    - { name: "Deploy dashboard to GitHub Pages", ref: ".github/workflows/pages.yml", schedule: "push to web/** on main | workflow_dispatch", status: live }
    - { name: "SharePoint extraction & harmonization (manual)", ref: "run by hand: pipeline/ensure_synced.py -> scan.py -> normalize.py -> relevance_gate.py -> extract_worklist.py (interactive Claude Code) -> build_harmonized.py -> export_web.py -> sync_blob.py", schedule: "on-demand, when new files land in the synced SharePoint folder", status: live }
inputs:
  - "SharePoint-synced OneDrive folder '2026 A&A Earthquakes' (products/, Secondary Data/) — read-only, referenced by local path on the operator's machine, never copied into the repo"
  - "USGS ComCat/PAGER + ShakeMap API (earthquake.usgs.gov) — events us6000t7zp (M7.5 mainshock), us6000t7zc (M7.2 foreshock); source-of-record for magnitude, depth, ShakeMap MMI grid, PAGER exposure/fatality/economic model"
  - "GDACS API + report page (gdacs.org) — episode impact data + scraped 'Exposed Population MMI>=VII' figure"
  - "PDC Hazards API (hazards-api.pdc.org) — requires PDC_API_KEY; rolling ~30-day window, no archive endpoint"
  - "WFP ADAM API (api.adam.geospatial.wfp.org, collection adam.adam_eq_events) — per-admin per-MMI population CSV + distance-buffer populations"
  - "Wikipedia MediaWiki API (2026_Venezuela_earthquakes infobox) + Asamblea Nacional news index + GDACS report-page news headline — REPORTED (confirmed) casualty toll, kept separate from modelled estimates"
  - "Venezuela CODAB adm0-3 via FieldMaps (ocha-stratus codab.load_codab_from_fieldmaps)"
  - "WorldPop 2018/2026 + GHSL 2020/2025 population COGs on the dev blob raster container (infrastructure/datasets/worldpop.md, ghsl.md)"
  - "GEM combo.xlsx (probabilistic national loss estimates, p5/p95) — SharePoint, local path"
  - "DFS Pop estimations CSV (parish-level exposure model) — SharePoint, local path"
  - "OCHA consolidated USGS-ShakeMap-x-WorldPop exposure workbook + WFP ADAM sheet — SharePoint, data/external/, gitignored"
outputs:
  - "extractions/*.json — committed, per-source/per-document observation records (audit trail); frozen static baselines under extractions/static/ so CI can rebuild without SharePoint/CODAB inputs"
  - "harmonized/*.parquet (observations, adm1_map, adm3_map, admin_exp_adm1/2) — gitignored, rebuildable"
  - "web/data/*.json + *.geojson (observations, meta, sources, adm1/adm3, admin_exp_adm1/2) — committed, exactly what the dashboard renders"
  - "GitHub Pages static dashboard (web/index.html) — access-controlled (private Enterprise-org repo)"
  - "dev blob lake projects/ds-ven-earthquake-support/: raw/{usgs,gdacs,pdc,adam}/*.json, processed/extractions/**, processed/observations/observations_latest.parquet + history/run_ts=<ISO>/, processed/zonal_exposure/timeseries.parquet + version=<N>/ snapshots, raw/shakemap/<eid>/version=<N>/grid.xml, published/*"
  - "text/**/*.md — committed markdown mirror of the SharePoint corpus (verification + discovery, additive per ADR-0005)"
  - "ledger.jsonl — per-file processing state (hash, class, source_org, stage versions, status)"
dependencies:
  - ocha-stratus (blob I/O — upload_blob_data, upload_parquet_to_blob, load_parquet_from_blob, open_blob_cog, codab.load_codab_from_fieldmaps)
  - exactextract, rasterio, rioxarray (ShakeMap × population zonal-stats engine)
  - geopandas, pandas, pyarrow
  - marimo (local prototype dashboard, app.py — not the deployed web/ dashboard)
  - "markitdown[docx,pdf,pptx,xlsx] (document -> markdown normalization)"
  - playwright (headless render check for the web app, pipeline/check_web.py)
  - "PDC_API_KEY (GHA secret) — PDC Hazards API auth"
  - "DSCI_AZ_BLOB_DEV_SAS / DSCI_AZ_BLOB_DEV_SAS_WRITE (GHA secrets) — dev blob read/write"
  - GitHub Pages (actions/configure-pages, upload-pages-artifact, deploy-pages)
downstream:
  - "None formally in the KB — this is an ad-hoc event-response tool, not a framework/monitoring input. The GH Pages dashboard IS the deliverable: the humanitarian-facing comparison of multi-source Venezuela earthquake impact/exposure estimates for the 2026 A&A Earthquakes response."
depends_on: [worldpop, ghsl]
source_repo: ocha-dap/ds-ven-earthquake-support
source_branch: main
source_sha: f628720
code_ref:
  - pipeline/fetch_official.py
  - pipeline/fetch_usgs.py
  - pipeline/fetch_gdacs.py
  - pipeline/fetch_pdc.py
  - pipeline/fetch_adam.py
  - pipeline/fetch_reported.py
  - pipeline/scan.py
  - pipeline/normalize.py
  - pipeline/relevance_gate.py
  - pipeline/extract_worklist.py
  - pipeline/build_harmonized.py
  - pipeline/zonal_exposure.py
  - pipeline/zonal_cron.py
  - pipeline/export_web.py
  - pipeline/sync_blob.py
  - .github/workflows/refresh.yml
  - .github/workflows/zonal.yml
  - .github/workflows/pages.yml
  - docs/decisions/
  - schema/extraction_schema.md
extra:
  schema_strain: "type='exposure' is the closest open-vocab fit (own ShakeMap x population zonal exposure, per docs/decisions/0009) but the repo is really an ad-hoc multi-source disaster-response data hub (extraction + harmonization + comparison dashboard) built for a single event, not a recurring dataset/monitoring pipeline."
  doc_status: "README.md is stale relative to HEAD — it describes only the discovery/ledger/normalize stages ('extract and harmonize: planned'); the live-API fetchers, zonal-exposure pipeline, web dashboard, and 3 GHA workflows are built and running but undocumented there."
visibility: internal
last_synced: "2026-07-08"
---

# ven-earthquake-support

> Runbook. Optimize for "what feeds it, what it emits, and what to do when it breaks at 2am."

## One-liner
*Event-response data hub for the 2026 Venezuela earthquakes (M7.5 mainshock + M7.2 foreshock,
24 Jun 2026): reconciles ~15 partner/live-API sources of impact & exposure estimates into one
harmonized observation table, computes CHD's own ShakeMap × WorldPop admin-level exposure, and
publishes a static comparison dashboard — hourly for the live feeds, every 3h for the heavy
zonal-stats recompute.*

## Jobs & schedule
| job | ref | schedule | status |
|---|---|---|---|
| Refresh official sources | `.github/workflows/refresh.yml` | hourly, `23 * * * *` | live |
| Zonal exposure (ShakeMap × population) | `.github/workflows/zonal.yml` | every 3h, `41 */3 * * *` | live |
| Deploy dashboard to GitHub Pages | `.github/workflows/pages.yml` | on push to `web/**`/`main` or `workflow_dispatch` | live |
| SharePoint extraction & harmonization | run by hand (no GHA — needs the operator's synced OneDrive folder) | on-demand, when new partner files sync | live |

Note: a push made with the workflow's default `GITHUB_TOKEN` does **not** trigger other
workflows, so `refresh.yml` deploys Pages itself on every real change rather than relying on
`pages.yml`; `pages.yml` is effectively a backstop for direct pushes to `web/**`.

## Inputs
**Official live APIs** (deterministic, no LLM, `source_tier=official_api`): USGS ComCat/PAGER +
ShakeMap (the authoritative source almost everything else derives from), GDACS API + report
page, PDC Hazards API (`PDC_API_KEY`; rolling ~30-day window — raw payloads committed under
`pdc/raw/` as the durable record since there's no archive endpoint), WFP ADAM API.

**Reported (confirmed) toll** (`source_tier=live_reported`, kept structurally separate from
modelled estimates): Wikipedia's live event-article infobox, the Asamblea Nacional (Venezuelan
government) news index, a GDACS report-page news cross-check.

**SharePoint document corpus** (the "products"/"Secondary Data" sync, ~160+ heterogeneous files —
PDF maps, fact sheets, slides, Excel): iMMAP/UNOSAT/PAHO/OCHA/GDACS/WFP sitreps and situational
awareness products, extracted interactively via Claude Code (ADR-0001). Two structured Excel
exports ride the same sync: GEM's probabilistic national loss model (`GEM combo.xlsx`) and DFS's
parish-level population/casualty estimates (`DFS Pop estimations` CSV), plus an OCHA-consolidated
ShakeMap×WorldPop/ADAM exposure workbook — all parsed deterministically (no LLM) because they're
structured, not prose/imagery.

**Static reference data:** Venezuela CODAB adm0–3 (FieldMaps via `ocha-stratus`), WorldPop
2018/2026 + GHSL 2020/2025 population COGs on the dev blob raster container.

## Steps
1. **Discover & materialize** — `ensure_synced.py` force-downloads OneDrive cloud-stub files;
   `scan.py` content-hashes every file in the synced folders and reconciles against
   `ledger.jsonl` (new/changed/unchanged), the deterministic change-detector and cache key.
2. **Normalize** — `normalize.py` converts text-bearing docs to markdown under `text/` via
   `markitdown` (additive only — extraction always reads the original at full fidelity, ADR-0005).
3. **Relevance gate** — `relevance_gate.py` quarantines off-event decoys (a 1997 Cariaco
   earthquake, non-Venezuela ShakeMaps) that pollute the source folder; never deletes, just tags.
4. **Interactive extraction** — `extract_worklist.py` hands out one document at a time to a fresh
   Claude Code context (ADR-0001); each document emits schema-valid, cited observations
   (`schema/extraction_schema.md`, ADR-0006) to `extractions/*.json`.
5. **Official-source fetch** — `fetch_official.py` orchestrates `fetch_usgs/gdacs/pdc/adam/reported.py`
   in one command (each capped at 180s so one hanging feed can't block the rest); this is the only
   step the GHA `refresh.yml` runs live, hourly.
6. **Zonal exposure** (own estimate, ADR-0009) — `zonal_cron.py` compares each event's current
   USGS ShakeMap version against the max already in the blob time series; on a NEW version it
   ingests `grid.xml`, runs `zonal_exposure.py` (resample the MMI grid onto the population raster,
   `exactextract` coverage-weighted sum per MMI band per ADM3 parish, roll up to ADM2/1/0), and
   appends to the blob time series — the expensive step runs only on a real ShakeMap revision.
7. **Harmonize** — `build_harmonized.py` unions LLM extractions + GEM + the OCHA workbook, resolves
   place names via CODAB, canonicalizes MMI-band spellings across sources (`canon_basis`), derives
   cumulative `mmi_ge_N` rows from contiguous per-band reporters, marks SharePoint echoes of an
   org now pulled live as `superseded`, dedupes each source's report-series to its latest `as_of`,
   and writes `harmonized/*.parquet`. Admin-level maps only regenerate when the gitignored
   CODAB/DFS inputs are present (i.e. a local run, not CI).
8. **Export + publish** — `export_web.py` writes plain-English `web/data/*.json`/`*.geojson`;
   the GHA commits (if changed) and deploys `web/` to GitHub Pages.
9. **Sync to blob** — `sync_blob.py` lands raw payloads, parsed extractions, the harmonized
   observation table (latest pointer + timestamped history), and the published dashboard JSON
   into the dev blob lake — the canonical durable store (git holds code only).

## Outputs
- `extractions/*.json` — committed audit trail of every observation, with a `source_tier`
  (`official_api` / `sharepoint` / `superseded` / `live_reported` / `derived`) and citation.
- `harmonized/observations.parquet` + admin-map parquets (gitignored, rebuildable).
- `web/data/{observations,meta,sources}.json` + `{adm1,adm3,admin_exp_adm1,admin_exp_adm2}.geojson`
  — exactly what the GitHub Pages dashboard renders.
- Dev blob `projects/ds-ven-earthquake-support/`: `raw/{usgs,gdacs,pdc,adam}/`,
  `raw/shakemap/<eid>/version=<N>/grid.xml`, `processed/extractions/`,
  `processed/observations/observations_latest.parquet` + `history/run_ts=<ISO>/`,
  `processed/zonal_exposure/timeseries.parquet` + `version=<N>/` snapshots, `published/*`.
- `text/**/*.md` markdown mirror of the corpus; `ledger.jsonl` processing state.

## Dependencies
`ocha-stratus` for all blob I/O and CODAB loading; `exactextract`/`rasterio`/`rioxarray` for the
zonal-stats engine; `geopandas`/`pandas`/`pyarrow`; `markitdown` for doc normalization;
`playwright` for a headless dashboard render check (`pipeline/check_web.py`); `marimo` for a
separate local prototype dashboard (`app.py`, not the deployed one). Secrets: `PDC_API_KEY`
(PDC auth), `DSCI_AZ_BLOB_DEV_SAS` / `DSCI_AZ_BLOB_DEV_SAS_WRITE` (dev blob). GitHub Pages
(`actions/deploy-pages`) for the dashboard.

## Failure modes & debugging
- **The extraction/harmonization stage isn't automatable.** `scan.py`, `ensure_synced.py`, and
  `build_harmonized.py` hardcode the operator's local OneDrive path
  (`/Users/zackarno/Library/CloudStorage/...`) as `DEFAULT_ROOT`/`ROOT` — that whole stage only
  runs on the maintainer's machine, by hand, when new partner files sync. This is by design (no
  SharePoint access from CI) but means new-document ingestion silently stalls if the operator is
  unavailable; only the hourly/3h GHA jobs (which read committed frozen inputs) keep running.
- **Admin-level maps only refresh locally.** `build_harmonized.py`/`export_web.py` skip
  regenerating `adm1_map`/`adm3_map`/`admin_exp_adm*` in CI (CODAB + DFS CSV are gitignored/
  SharePoint-sourced) and keep the last-committed geojson — so the choropleth maps go stale
  between manual runs even though the observation comparison keeps updating hourly.
- **`fetch_official.py` swallows individual fetcher failures** (`|| true` in `refresh.yml`, plus
  a per-fetcher 180s timeout and try/except in the orchestrator) — a dead PDC key, a GDACS outage,
  or an ADAM schema change degrades silently to fewer sources rather than failing the workflow.
  Check the Action run log for `! <fetcher> failed` / `exceeded 180s`.
- **PDC's rolling ~30-day window has no archive endpoint** — `--refresh` will stop returning the
  Venezuela events entirely once ~30 days pass since they closed; the committed `pdc/raw/*.json`
  is the only durable record after that.
- **Asamblea Nacional (government primary) fetch is currently broken** — the site has a
  misconfigured TLS cert; `fetch_reported.py` deliberately does not disable verification, so it
  falls back to Wikipedia (which cites the same government figures). Fix is upstream (their cert),
  not ours.
- **GDACS's own API under-reports MMI≥VII** (`shakepop` reads 0 for the mainshock), so
  `fetch_gdacs.py` scrapes the rendered report page instead — a page-template change would break
  this regex silently (returns `None`, that source just drops the figure, no hard failure).
- **Secrets-gated steps degrade, not fail:** the blob-sync step in `refresh.yml` is
  `continue-on-error: true`, so a missing/rotated `DSCI_AZ_BLOB_DEV_SAS_WRITE` won't fail the run
  — the dashboard still deploys from committed data, but the blob lake silently stops receiving
  updates.
- **Pages deploy flakiness:** `actions/deploy-pages` intermittently rejects a new deployment while
  a prior one settles ("Deployment failed, try again later"); `refresh.yml` retries once after a
  60s sleep — a second failure needs a manual re-run.
- **`[stale]` ADR/code mismatch:** ADR-0004 chose "DuckDB + parquet" as the harmonized store, but
  `build_harmonized.py`/`sync_blob.py` write/read parquet directly — no DuckDB is in the current
  code path.
- **`[gap]` not yet in `infrastructure/pipeline-registry.md`** — this is a new ingestion; the
  registry's live-health tracking doesn't cover it yet.
- **README is stale relative to `HEAD`** — it documents only the discovery/ledger/normalize
  stages as built and calls extraction/harmonization "planned"; the live-API fetchers, the
  zonal-exposure pipeline, the web dashboard, and all 3 GHA workflows are live. Read the code, not
  the README, for current status.

## Downstream consumers
None formally tracked in the KB — this repo is itself the response-support deliverable for the
2026 Venezuela earthquake activation, not an input to another framework's monitoring or app. Its
GitHub Pages dashboard (private, access-controlled per the Enterprise-org repo setting) is the
consumer-facing surface for CHD and response partners comparing USGS/GDACS/PDC/WFP ADAM/CHD's own
exposure estimates against the reported toll.
