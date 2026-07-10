---
content_type: dataset
name: EM-DAT
aliases: [EMDAT, "EM-DAT", "Emergency Events Database"]
provider: "CRED — Centre for Research on the Epidemiology of Disasters, UCLouvain"
data_type: disaster-impacts
access: registered
api: "https://public.emdat.be  (portal; event links: https://public.emdat.be/data/<disaster-id>)"
auth: "free registration (non-commercial); download as .xlsx after login"
formats: [xlsx, parquet]
resolution: "event-level records, 1900–present, ~27k+ disasters; country + disaster-type, human & economic impacts"
update_cadence: "CRED curates continuously; OUR blob snapshot is refreshed MANUALLY and ad-hoc — no automation, so it may be stale"
license: "EM-DAT Terms of Use — free for non-commercial use, attribution to CRED/UCLouvain"
code_ref: "ocha-stratus emdat.load_emdat_from_blob(iso3, include_historic, stage)"
mirror: manual          # in our blob, but refreshed by hand → stale risk (see ⚠️ below)
mirror_priority: high
used_by:
  - pipelines/unified-disaster-database.md
  - pipelines/glb-tropicalcyclones.md
  - pipelines/glb-cyclones-impactmodel.md
  - pipelines/hti-hurricanes-impactmodel.md
  - pipelines/seasonal-bulletin.md
  - frameworks/hti-hurricanes/2026-06-09.md
  - frameworks/cub-hurricanes/2026-06-17.md
  - frameworks/phl-storms/2025-10-03.md
  - frameworks/tcd-drought/2025-03-03.md
  - apps/glb-tropicalcyclones-app.md
last_verified: 2026-07-01
---

# EM-DAT

CRED's **Emergency Events Database** — the standard historical record of disaster
**impacts** (deaths, people affected, economic damage) by event, country, and type,
1900–present. Our reference set for **historical impact / return-period** work and for
calibrating storm/flood impact models.

## How we access it

- **We don't hit EM-DAT live.** We keep a **blob snapshot** and read it with
  **`ocha-stratus`**: `emdat.load_emdat_from_blob(iso3, include_historic=..., stage=...)`
  → a DataFrame. That's the sanctioned path (`ds-storms-pipeline` and the impact models
  use it).
- Source of the snapshot: the **public EM-DAT portal** (`public.emdat.be`) — free
  **registration** for non-commercial use, then **.xlsx** export via the "Access Data" tab.
  Refreshing our blob copy means re-exporting and re-uploading (procedure below).
- **The snapshot lives on the DEV blob account only** (`imb0chd0dev`), at
  `global/emdat/processed/emdat_all.parquet` — like other manually-updated datasets, it was
  never promoted to prod. Point `stage` accordingly when loading.

> ⚠️ **The snapshot may be out of date.** Unlike our pipeline-ingested sources (IMERG,
> FloodScan, …), **nothing keeps the EM-DAT blob copy current** — it's a manual re-export
> whenever someone remembers. Check the blob's vintage before any claim that leans on recent
> events, and re-snapshot if it's stale.
>
> <!-- TODO: stand up automation to keep the EM-DAT snapshot fresh (a small scheduled
> ingest — its own repo or a job in an existing pipelines repo — that re-pulls the portal
> export and upserts to blob, then this becomes a normal pipeline page and the ⚠️ goes away).
> EM-DAT's ToS is non-commercial + no bulk redistribution, so keep it to our read-gated infra;
> a headless export needs a stored EM-DAT login. -->


## Manual refresh procedure

How to re-snapshot the blob copy (from the retired Confluence "Instructions for manual
updates" page):

1. Log in at `public.emdat.be/data` and export the data with **no filters** and
   **"Include Historical events (pre-2000)" toggled ON**.
2. Locally, with **`DSCI_AZ_BLOB_DEV_SAS_WRITE`** set, read the exported `.xlsx` into pandas
   and upload with [ocha-stratus](../libs/ocha-stratus.md):

   ```python
   stratus.upload_parquet_to_blob(
       df, "emdat/processed/emdat_all.parquet", container_name="global"
   )
   ```

   (Targets the **dev** account `imb0chd0dev` — the only home of the snapshot.)

## How we use it

Ground-truth for **historical impacts** — return-period severity, storm/flood impact-model
calibration, and the [unified disaster database](../../pipelines/unified-disaster-database.md).

## Gotchas

- **Registration-gated, non-commercial** — respect the Terms; don't republish raw records.
- **Reporting bias / thresholds**: EM-DAT only logs events meeting entry criteria
  (deaths / affected / declaration / appeal), so small events and older decades are
  under-recorded. Treat counts as a **floor**, not a census.
- **Our blob copy can lag** the live database — check `last_verified` and re-snapshot before
  claims that depend on very recent events.
