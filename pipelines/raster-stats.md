---
content_type: pipeline
name: raster-stats
type: dataset-ingest
status: live
deployment:
  platform: databricks-job
  resource_group: null
  jobs:
    - { name: "Raster Stats ERA5", ref: "958368449638566", schedule: "chained (triggered after ds-raster-pipelines' Run ERA5 job, monthly)", status: live }
    - { name: "Raster Stats SEAS5", ref: "184508905416553", schedule: "chained (triggered after ds-raster-pipelines' Run SEAS5 job, monthly)", status: live }
    - { name: "Raster Stats IMERG", ref: "809803033083959", schedule: "chained (triggered after ds-raster-pipelines' Run IMERG job, daily)", status: live }
    - { name: "Raster Stats FLOODSCAN", ref: "957783975148658", schedule: "chained (triggered after ds-raster-pipelines' Run FloodScan job, daily)", status: live }
    - { name: "Raster Stats CHIRPS", ref: "563923219561241", schedule: "manual/on-demand", status: live }
inputs:
  - "blob: imb0chd0{dev|prod} raster container — seas5/monthly/processed/precip_em_i* (per-issued/leadtime COG)"
  - "blob: imb0chd0{dev|prod} raster container — era5/monthly/processed/precip_reanalysis_v* (monthly COG)"
  - "blob: imb0chd0{dev|prod} raster container — imerg/daily/late/v7/processed/imerg-daily-late-* (daily COG)"
  - "blob: imb0chd0{dev|prod} raster container — floodscan/daily/v5/processed/aer_area_300s_* (daily COG, SFED+MFED bands)"
  - "blob: imb0chd0{dev|prod} polygon container — {iso3}_shp.zip (COD admin boundaries, cached from Fieldmaps by the manual helpers/load_polygons.py script)"
  - "DB table: public.iso3 (rasterstats DB — country list with max_adm_level, has_active_hrp, per-dataset coverage flags)"
  - "https://data.fieldmaps.io/cod.csv (COD metadata, only for --update-metadata)"
  - "local data/humanitarian-response-plans.csv + data/global-pcodes.csv (only for --update-metadata, downloaded manually from HDX + fieldmaps.io)"
outputs:
  - "DB table: public.seas5 (forecast zonal stats: mean/median/min/max/count/sum/std by iso3+pcode+valid_date+issued_date+leadtime+adm_level)"
  - "DB table: public.era5 (observational zonal stats by iso3+pcode+valid_date+adm_level)"
  - "DB table: public.imerg (observational zonal stats by iso3+pcode+valid_date+adm_level)"
  - "DB table: public.floodscan (observational zonal stats by iso3+pcode+valid_date+band[SFED|MFED]+adm_level)"
  - "DB table: public.qa (per-iso3/dataset/adm_level error log)"
  - "DB table: public.iso3 (country registry — rewritten only on --update-metadata)"
  - "DB table: public.polygon (per-pcode metadata: name, area, per-dataset pixel-coverage counts — written only on --update-metadata)"
dependencies:
  - "azure-storage-blob==12.20.0 (direct Azure SDK — NOT ocha-stratus; SAS tokens from env)"
  - "sqlalchemy==2.0.33 + psycopg2_binary==2.9.9 (direct DB connection; UID/PW from DSCI_AZ_DB_*_{UID,PW}_WRITE, host from DSCI_AZ_DB_*_HOST — see extra.dedicated_db)"
  - "rioxarray==0.16.0, xarray==2024.3.0, dask==2024.7.0 (raster I/O + lazy COG stacking)"
  - "rasterio==1.3.10 (admin-boundary rasterization, resampling); geopandas==1.0.1 (vector boundaries)"
  - "rasterstats==0.19.0 (fast_zonal_stats is adapted from it; also used as a comparison baseline in exploration/validate_outputs.md — not used in the production path itself)"
  - "requests, adlfs==2024.4.1, tqdm==4.66.4 (fieldmaps.io COD metadata for --update-metadata; tqdm progress bar in local-mode COG stacking)"
  - "secrets: DSCI_AZ_BLOB_{DEV|PROD}_SAS, DSCI_AZ_BLOB_{DEV|PROD}_SAS_WRITE, DSCI_AZ_DB_{DEV|PROD}_UID_WRITE, DSCI_AZ_DB_{DEV|PROD}_PW_WRITE, DSCI_AZ_DB_{DEV|PROD}_HOST"
downstream:
  - "raster-stats-app (ds-raster-stats-app) — Dash explorer reads public.era5/seas5/imerg + public.iso3/polygon from the prod rasterstats DB"
  - "Any framework monitoring app that reads ERA5/SEAS5/IMERG/FloodScan zonal stats from the rasterstats DB"
depends_on:
  - "raster-pipelines"
  - "dbx-job-compute"
surfaces:
  - {url: "https://ocha-dap.github.io/ds-raster-stats/", kind: landing, title: "Raster-stats site landing page"}
  - {url: "https://ocha-dap.github.io/ds-raster-stats/benchmarks/", kind: report, title: "Zonal-stats speed benchmarks (incl. 2024-methodology reproduction)"}
  - {url: "https://ocha-dap.github.io/ds-raster-stats/method-change/", kind: report, title: "Method-change value comparison (exactextract vs legacy, all 4 datasets)"}
source_repo: ocha-dap/ds-raster-stats
source_branch: main
source_sha: "b8d7f47"
code_ref:
  - "run_raster_stats.py — entrypoint (CLI dispatch, --update-metadata branch, multiprocessing.Pool over date chunks)"
  - "src/utils/inputs.py — CLI args (dataset, --mode, --test, --update-stats, --backfill, --update-metadata, --chunksize)"
  - "src/config/{seas5,era5,imerg,floodscan}.yml — per-dataset blob prefix, start_date, frequency, forecast flag, extra_dims, coverage"
  - "src/config/settings.py — DATABASES dict (local sqlite / dev / prod), config_pipeline(), date-chunk generation"
  - "src/utils/cloud_utils.py — get_container_client / get_cog_url (raw azure-storage-blob)"
  - "src/utils/cog_utils.py — stack_cogs: list blob, stream COGs via rioxarray, combine into xarray Dataset"
  - "src/utils/raster_utils.py — fast_zonal_stats(_runner), prep_raster (clip+upsample), rasterize_admin, validate_stats"
  - "src/utils/database_utils.py — table DDL + check constraints, postgres_upsert, qa logging"
  - "src/utils/iso3_utils.py — load public.iso3, load_shp_from_azure, create_iso3_df bootstrap"
  - "src/utils/metadata_utils.py — process_polygon_metadata (public.polygon build)"
  - "src/utils/general_utils.py — parse_date, get_missing_dates (backfill), get_most_recent_date (update-stats)"
  - "helpers/load_polygons.py — one-off/manual script that caches Fieldmaps CODs into the polygon blob container (incl. the NGA/TCD/BDI dissolve workaround)"
  - "exploration/test_grid_alignment.md — clip-then-upsample vs upsample-then-clip investigation (why prep_raster clips first)"
  - "exploration/validate_outputs.md — DB stats vs exactextract vs rasterstats comparison (ERA5 + SEAS5) — in-repo reproduction of part of the methodology rationale below (the Philippines ADM2 figures come from the Confluence archive, not this notebook)"
  - "exploration/admin_lookup.md — builds a pcode↔place-name lookup parquet across admin levels, uploaded to the projects blob container"
extra:
  not_ocha_stratus: "Predates ocha-stratus adoption: uses raw azure-storage-blob (ContainerClient) for blob I/O and raw SQLAlchemy engine URLs for the DB. Does NOT use ocha-stratus. A future update should migrate."
  dedicated_db: "Runs against chd-rasterstats-{dev|prod} (the team Postgres servers — see infrastructure/database.md). settings.py reads the host from DSCI_AZ_DB_{DEV,PROD}_HOST (what the Job Compute policy injects and ocha-stratus reads) with the FQDN hard-coded only as a fallback for old local .env files predating that variable — the ds-raster-stats#51 migration flagged in the prior sync of this page is merged. local mode uses a sqlite file (chd-rasterstats-local.db)."
  run_modes: "Flag-driven, not date-config-driven: default = archival rebuild from config start_date to yesterday; --update-stats = stats against the single most-recent COG; --backfill = diff expected dates vs DB and fill gaps; --update-metadata = rebuild public.iso3 + public.polygon then exit; --test = 3-country subset (BDI/NGA/TCD)."
  metadata_bootstrap: "--update-metadata rebuilds public.iso3 (from fieldmaps.io cod.csv) and public.polygon. create_iso3_df ALSO requires local data/humanitarian-response-plans.csv (HDX) + data/global-pcodes.csv (fieldmaps.io) — so this is effectively a manual/local step, not a clean scheduled job."
  multiprocessing: "Dates are split into chunks of 100 (src/config/settings.py generate_date_series) and processed by a multiprocessing.Pool of NUM_PROCESSES=2 workers; each worker opens its own engine + stacks its own COGs."
  floodscan_bands: "FloodScan carries a 4th dim `band` mapped to SFED/MFED long-names in upsample_raster; written as the `band` column in public.floodscan."
  no_deploy_manifest: "This repo ships NO deployment config — no databricks.yml/DAB bundle and no scheduled GHA (the only workflow, .github/workflows/run_tests.yml, is push/PR CI on main). The five scheduled/on-demand jobs are registered directly in workspace adb-6009046713167663."
  job_naming: "The Databricks job NAMES are 'Raster Stats {ERA5,SEAS5,IMERG,FLOODSCAN,CHIRPS}' (this repo) vs 'Run {ERA5,SEAS5,IMERG,FloodScan}' (ds-raster-pipelines, the COG producer) — easy to conflate since both sets cover the same 4 datasets. README confirms the Raster Stats jobs are chained downstream of the matching Run job."
  SCHEMA_STRAIN: "No frontmatter field for dedicated-DB (vs shared stratus DB), for manual bootstrap steps, or for a job's own name vs its handle. All captured in extra/discrepancies."
discrepancies:
  - "[resolved] The previous version of this page (sha 5fe23b4) carried an unresolved 'attribution conflict': it listed the ds-raster-pipelines 'Run {ERA5,SEAS5,IMERG,FloodScan}' job_ids as if they were THIS pipeline's own scheduled jobs. infrastructure/pipeline-registry.md now correctly attributes 4 separate 'Raster Stats {ERA5,SEAS5,IMERG,FLOODSCAN}' job_ids to OCHA-DAP/ds-raster-stats, chained downstream of the Run * jobs — see Jobs & schedule."
  - "[conflict] pipeline-registry.md's `writes` column attributes public.era5/floodscan/imerg/seas5 to the ds-raster-pipelines 'Run *' jobs (this repo's output tables), while the 'Raster Stats *' jobs it attributes to this repo show `writes: —`. That's almost certainly a registry-generator heuristic (matching by dataset-name pattern on the upstream job in the chain) rather than reality — per the code, this repo's jobs are what actually upsert those tables. Flagged for the registry generator, not actioned here."
  - "[gap] A fifth job, 'Raster Stats CHIRPS' (dbx:563923219561241), is attributed to this repo in pipeline-registry.md and is currently FAILING. Current main has no chirps.yml config and no CHIRPS reference anywhere in the codebase (inputs.py's CLI choices are seas5/era5/imerg/floodscan only) — this job cannot succeed against this checkout. Needs human confirmation of what ref/branch it actually runs, or whether it should be retired."
  - "[resolved] The previous page flagged ds-raster-stats#51 (host from DSCI_AZ_DB_*_HOST instead of a hard-coded FQDN) as pending. Current main/settings.py already reads the host from the env var with FQDN only as a fallback default — the PR is merged."
  - "[resolved] The prior page flagged the README as documenting pre-rename env vars. README's Development Setup .env example now uses the correct current names (DSCI_AZ_BLOB_*_SAS, DSCI_AZ_DB_*_{UID,PW}_WRITE, DSCI_AZ_DB_*_HOST) — the OLD names (DSCI_AZ_SAS_DEV/PROD, AZURE_DB_PW_DEV/PROD) only survive inside the exploration/*.md notebooks (admin_lookup.md, validate_outputs.md), which are demonstrative/one-off and not part of the production path."
  - "[gap] Per-iso3 errors are caught and logged to public.qa; the run still exits 0, so missing-country stats are invisible unless you query public.qa. SEAS5/FloodScan all-NaN leadtime/band+date combos are silently skipped with NO qa entry."
visibility: internal
last_synced: "2026-09-26"
---

# Raster Statistics Pipeline

> Runbook. Optimize for "what feeds it, what it emits, and what to do when it breaks at 2am."

## One-liner

*On schedule: read COG rasters (SEAS5 / ERA5 / IMERG / FloodScan) from Azure blob → clip to country bounds → upsample → compute zonal stats per p-code per admin level → upsert into the dedicated Azure PostgreSQL "rasterstats" DB.*

## Jobs & schedule

Five Databricks jobs in workspace `adb-6009046713167663`, all attributed to **this repo** (`OCHA-DAP/ds-raster-stats`) by [`infrastructure/pipeline-registry.md`](../infrastructure/pipeline-registry.md) — this resolves the previous version of this page's "attribution conflict":

| job | ref | schedule | status |
|---|---|---|---|
| Raster Stats ERA5 | `958368449638566` | chained after `ds-raster-pipelines`' **Run ERA5** job (monthly) | live |
| Raster Stats SEAS5 | `184508905416553` | chained after `ds-raster-pipelines`' **Run SEAS5** job (monthly) | live |
| Raster Stats IMERG | `809803033083959` | chained after `ds-raster-pipelines`' **Run IMERG** job (daily) | live |
| Raster Stats FLOODSCAN | `957783975148658` | chained after `ds-raster-pipelines`' **Run FloodScan** job (daily) | live |
| Raster Stats CHIRPS | `563923219561241` | manual/on-demand | live (currently **FAILING**, see discrepancies) |

The registry shows these four ERA5/SEAS5/IMERG/FLOODSCAN jobs' own schedule as `manual` because they have no top-level cron — the README confirms they're **triggered as downstream tasks chained from the corresponding `Run *` COG-production job in [`ds-raster-pipelines`](raster-pipelines.md)**, not run independently. The separate `Run *` job_ids (`954457722530604`/`792911256578092`/`666239885322861`/`710204563973283`) belong to `ds-raster-pipelines` and produce the input COGs this pipeline consumes — they are **not** this pipeline's own jobs (the previous version of this page conflated the two).

This checkout is `main` @ `b8d7f47`. No deployment manifest ships in the repo (no `databricks.yml`/DAB bundle, no scheduled GHA — see `extra.no_deploy_manifest`); the five jobs above are registered directly in the workspace.

## Inputs

**Raster COGs** (Azure Blob `raster` container, `imb0chd0{dev|prod}`), prefix per `src/config/{dataset}.yml`:

- `seas5/monthly/processed/precip_em_i*` — SEAS5 monthly precip ensemble mean (forecast; per issued-date + leadtime)
- `era5/monthly/processed/precip_reanalysis_v*` — ERA5 monthly precip reanalysis
- `imerg/daily/late/v7/processed/imerg-daily-late-*` — IMERG daily late-run precip
- `floodscan/daily/v5/processed/aer_area_300s_*` — FloodScan daily flood fraction (SFED + MFED bands)

**Boundaries:** `{iso3}_shp.zip` per country in the `polygon` blob container (COD admin shapefiles), populated by the manual `helpers/load_polygons.py` script (see Admin boundary reference below).

**Database:** `public.iso3` in the rasterstats DB — `iso3`, `has_active_hrp`, `max_adm_level`, `stats_last_updated`, `shp_url`, and per-dataset coverage flags (e.g. `floodscan`).

The `--update-metadata` path additionally pulls `https://data.fieldmaps.io/cod.csv` and reads local `data/humanitarian-response-plans.csv` + `data/global-pcodes.csv`.

## Steps

1. **Parse CLI** (`src/utils/inputs.py`) — positional dataset (`seas5|era5|imerg|floodscan` — note: **not** `chirps`, see discrepancies), `--mode {local,dev,prod}`, `--test`, `--update-stats`, `--backfill`, `--update-metadata`, `--chunksize`.
2. **`--update-metadata` short-circuit** — rebuild `public.iso3` (`create_iso3_df`) and `public.polygon` (`process_polygon_metadata`), then `sys.exit(0)`. (Needs local CSVs — effectively manual.)
3. **Create tables** — `create_qa_table` + `create_dataset_table` (idempotent `MetaData.create_all`; forecast datasets get `issued_date`/`leadtime`, extra_dims add columns; check constraints enforce min≤max, mean/median∈[min,max], leadtime∈0..6, etc.).
4. **Resolve dates** (`config_pipeline`) — default = config `start_date` → yesterday; `--update-stats` = single most-recent COG date; `--backfill` = expected-vs-existing date diff (`get_missing_dates`). Dates are chunked (100/chunk).
5. **Load country list** — `get_iso3_data` queries `public.iso3` (or the `--test` 3-country subset).
6. **Process chunks in parallel** (`multiprocessing.Pool`, 2 workers; `process_chunk`):
   a. `stack_cogs` — list blob by prefix, stream matching COGs via `rioxarray`, combine into one `xarray.Dataset` (`date` dim, plus `leadtime`/`band` where applicable).
   b. Per country: download boundary zip, read ADM0, `prep_raster` (**clip to bounds first, then upsample** — see Methodology rationale for why this order matters).
   c. Per admin level `0..max_adm_level`: `fast_zonal_stats_runner` (rasterize boundaries, compute mean/median/min/max/sum/std/count per p-code per date; `validate_stats` each row).
   d. **Upsert** all rows for the country via `postgres_upsert` (on-conflict update on the `(valid_date, pcode[, leadtime/band])` unique key).
   e. Any per-iso3 exception → `insert_qa_table` and continue.

See `run_raster_stats.py` + `src/utils/` for detail.

## Methodology rationale

Why the pipeline computes stats the way it does (2024 design work — digested from the retired Confluence archive, partly reproduced by in-repo `exploration/` notebooks):

- **Boundary pixels: whole-pixel vs pixel-weighting.** Two standard ways to treat pixels straddling polygon boundaries: *whole-pixel* methods (à la `rasterstats` — include a pixel by centroid-in-polygon or any-touch, optionally upsampling first to shrink the weight of boundary pixels) vs *pixel-weighting* methods (à la `exactextract` — weight each boundary pixel by its area fraction inside the polygon). Discrepancy is largest for small, coastline-heavy geographies.
- **Choice: whole-pixel with upsampling.** All input rasters are upscaled to **0.05°** with `nearest` resampling — `nearest` preserves original cell values, and the upsampling acts as a simplified area-weighting proxy. Per-dataset upscales: SEAS5 0.4°→0.05°, ERA5 0.25°→0.05°, IMERG 0.1°→0.05°.
- **Clip-then-upsample, not upsample-then-clip.** `exploration/test_grid_alignment.md` demonstrates that the order of clip vs upsample changes the output grid alignment and therefore the stats — `prep_raster` clips to the ADM0 bounding box *first*, then upsamples, matching production. The notebook links a comment on `ds-raster-stats#13` for the proposed alignment fix.
- **exactextract was evaluated and rejected** for this general pipeline — much slower for repeated calculations across many dates, and output very similar — though it *is* used in the storms exposure path. `exploration/validate_outputs.md` reproduces this for ERA5 + SEAS5: it pulls a live DB row, `exactextract`, and `rasterstats.zonal_stats` for the same country/date/admin level and diffs them (>5% absolute difference flagged). Validation on the Philippines ADM2 stress case (small country, lots of coastline): the majority of ADM2 means agree within ±5% between the two methods; only a minority exceed ±10%. A higher upsample resolution shrinks the gap further but costs memory/performance.
- **Simplify then rasterize once.** Input polygons are simplified with a conservative 0.001° tolerance before rasterizing (big speedup, no material boundary change). Boundaries are rasterized **once per admin level** (pixels whose centroid falls inside the polygon) and cached across all dates — the major speedup vs baseline `rasterstats`, which re-rasterizes per date; valid because admin polygons don't overlap. Smaller geometries get less accurate stats at the reference resolution.
- **Scoping choices** (2024): stats are min/max/mean/median/sum; any quantiles would be in tens only (10/20/30…) — no team framework uses a non-multiple-of-10 threshold (quantiles are not in the current output schema). Output format was scoped as one big parquet internally + CSVs for HDX/ad-hoc country sends; the implementation landed on the Postgres tables below.

Digested from the retired DSCI Confluence space (archive: `confluence/` in `ds-knowledge-base-internal`).

## Admin boundary reference & quirks

- **Source & cache.** All admin boundaries are the **Fieldmaps.io original-shapefile CODs** (fieldmaps.io/data/cod), cached in the prod `polygon` blob container to pin versions and avoid hammering the Fieldmaps server. The cache is populated/refreshed by the **manual** `helpers/load_polygons.py` script (explicitly marked "temporary... not written to full production standards" in its own docstring) — no automation, no schedule; last prod refresh from Fieldmaps was **2024-10-07** (as of the Confluence source doc). <!-- TODO: check whether the polygon cache has been refreshed since 2024-10-07 -->
- **Coverage.** ADM0/1 for all COD countries; ADM2 only for HRP countries. Encoded in `public.iso3`: `max_adm_level = 2` where `has_active_hrp` (pulled from the HDX humanitarian-response-plans dataset, where the source CODs allow), else 1; `src_lvl`/`src_update`/`o_shp` are copied from the Fieldmaps COD metadata CSV (`data.fieldmaps.io/cod.csv`).
- **Quirk: tiny countries have no data** — their extent is smaller than the raw raster pixels, so clipping fails: DMA, LCA, SXM, MSR.
- **Quirk: multiple ADM0 entries** — BDI, NGA, TCD (also the `--test` 3-country subset). `helpers/load_polygons.py` explicitly dissolves these three at ADM0 before caching, working around a known Fieldmaps issue.
- **Quirk: extraneous / non-standard pcodes** in the CODs — CHN, LBN, MOZ, PAK, SDN, SSD (e.g. Lebanon has an ADM1 named "Conflict").
- **`public.polygon` semantics** (for interpreting the coverage columns): `area` is km² computed on the Mollweide equal-area projection; `{dataset}_frac_raw_pixels` = n_upsampled_pixels / upsample_factor² (polygon size relative to raw pixel size); `{dataset}_n_intersect_raw_pixels` excludes pixels with very small overlap.

Digested from the retired DSCI Confluence space (archive: `confluence/` in `ds-knowledge-base-internal`).

## Outputs

**Dedicated Azure PostgreSQL** `chd-rasterstats-{dev|prod}.postgres.database.azure.com` (local mode → `chd-rasterstats-local.db` sqlite):

- `public.seas5` — `iso3, pcode, valid_date, issued_date, leadtime, adm_level, mean, median, min, max, count, sum, std`. Unique on `(valid_date, pcode, leadtime)` (nulls-not-distinct).
- `public.era5` / `public.imerg` — observational schema (no `issued_date`/`leadtime`). Unique on `(valid_date, pcode)`.
- `public.floodscan` — observational schema + `band` (SFED/MFED). Unique on `(valid_date, pcode, band)`.
- `public.qa` — error log: `date, iso3, adm_level, dataset, error, stack_trace`.
- `public.iso3` — country registry (rewritten only on `--update-metadata`).
- `public.polygon` — per-pcode metadata: `name, area, standard`, per-dataset pixel-coverage counts (built only on `--update-metadata`).

No blob outputs. No email outputs.

## Dependencies

| Dependency | Notes |
|---|---|
| `azure-storage-blob==12.20.0` | Direct Azure SDK — **not** ocha-stratus; SAS from env |
| `sqlalchemy==2.0.33` + `psycopg2_binary==2.9.9` | Direct DB engine; creds from env |
| `rioxarray==0.16.0`, `xarray==2024.3.0`, `dask==2024.7.0` | Raster I/O + lazy COG stacking |
| `rasterio==1.3.10`, `geopandas==1.0.1` | Admin rasterization / vector boundaries |
| `rasterstats==0.19.0` | `fast_zonal_stats` is adapted from it; also the comparison baseline in `exploration/validate_outputs.md` (not imported in the production path) |
| `requests`, `adlfs==2024.4.1`, `tqdm==4.66.4` | fieldmaps.io COD metadata (`--update-metadata` only); local-mode progress bar |

**Secrets / env** (NOTE: renamed vs README's Development Setup section, which is now correct — the old `DSCI_AZ_SAS_DEV/PROD` and `AZURE_DB_PW_DEV/PROD` names only survive in the `exploration/*.md` notebooks): blob = `DSCI_AZ_BLOB_{DEV|PROD}_SAS` and `DSCI_AZ_BLOB_{DEV|PROD}_SAS_WRITE`; DB = `DSCI_AZ_DB_{DEV|PROD}_UID_WRITE`, `DSCI_AZ_DB_{DEV|PROD}_PW_WRITE`, and `DSCI_AZ_DB_{DEV|PROD}_HOST` (the Job Compute policy injects all of these from the `dsci` secret scope). `PGSSLMODE=require` may be needed for Azure PostgreSQL — see [infrastructure/conventions.md](../infrastructure/conventions.md).

## Failure modes & debugging

**`No COGs found to process for dates: ...`** — blob listing returned nothing for the resolved date range. Check: (a) the `blob_prefix` in `src/config/{dataset}.yml` still matches blob layout; (b) the upstream [raster-pipelines](raster-pipelines.md) COG producer actually ran (a missed COG run starves this job, since the Raster Stats * job is chained after it); (c) the SAS token (`DSCI_AZ_BLOB_*_SAS*`) hasn't expired. `stack_cogs` also logs a warning when `len(cogs) != len(dates)` but proceeds.

**"Raster Stats CHIRPS" job is failing** — `infrastructure/pipeline-registry.md` shows `dbx:563923219561241` ("Raster Stats CHIRPS") attributed to this repo and currently `FAILING`. The current `main` checkout has **no `chirps.yml` config and no `chirps` reference anywhere in the repo** (`src/utils/inputs.py`'s CLI `choices` is `seas5|era5|imerg|floodscan` only) — this job cannot succeed against this checkout. Either the job targets a stale/different ref, or CHIRPS support was removed/never merged; needs human confirmation in the workspace before deciding whether to fix, repoint, or retire the job.

**Per-country errors silently swallowed** — `process_chunk` catches per-iso3 exceptions, logs to `public.qa`, and continues; the run still exits `0`. If a country's stats are missing, `SELECT * FROM public.qa WHERE iso3 = 'XYZ'`.

**All-NaN combos skipped with no trace** — in `fast_zonal_stats_runner`, a leadtime/band+date slice that is entirely NaN is `continue`-skipped with **no qa entry** (expected for invalid SEAS5 forecast combos / FloodScan band gaps).

**Admin boundary not in blob** — `load_shp_from_azure` raises if `{iso3}_shp.zip` is absent in the `polygon` container; caught → qa. Fix: run `helpers/load_polygons.py` for that iso3, or drop it from `public.iso3`.

**Constraint violations on upsert** — `create_dataset_table` adds check constraints (min≤max, mean/median∈[min,max], `leadtime BETWEEN 0 AND 6`, `valid_date >= issued_date`, etc.) and `validate_stats` re-checks in Python; a genuine bad stat row will raise and land in qa.

**DB / env issues** — verify `DSCI_AZ_DB_*_{UID|PW}_WRITE` and `DSCI_AZ_DB_*_HOST` are set on the cluster. Set `PGSSLMODE=require` if the connection is refused.

**`--update-metadata` fails locally** — `create_iso3_df` reads `data/humanitarian-response-plans.csv` and `data/global-pcodes.csv` from the working dir; without them it errors. This step is effectively manual/local.

**Databricks logs** — workspace `adb-6009046713167663`; check the `Raster Stats {ERA5,SEAS5,IMERG,FLOODSCAN,CHIRPS}` job run logs (this repo). If there is no fresh run, check the upstream `Run *` job in `ds-raster-pipelines` first, because the stats job only fires after it. Note that the registry's `writes` column still lists this pipeline's tables against the `Run *` jobs (see discrepancies).

## Downstream consumers

- **raster-stats-app** — the Dash explorer (`ds-raster-stats-app`) reads `public.era5/seas5/imerg` plus `public.iso3`/`public.polygon` (and `*_completeness`) from the prod rasterstats DB. See [apps/raster-stats-app](../apps/raster-stats-app.md).
- **Framework monitoring apps** — any AA framework monitor that reads ERA5/SEAS5/IMERG/FloodScan zonal stats from the rasterstats DB consumes this output.

> **Not a consumer:** `ds-floodexposure-monitoring` has its *own* internal raster-stats step (`pipelines/update_raster_stats.py` → `app.floodscan_exposure`) and a self-contained `repository_dispatch` chain. It does **not** read from this pipeline. See [pipelines/floodexposure-monitoring](floodexposure-monitoring.md).
