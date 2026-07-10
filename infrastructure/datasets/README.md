# Datasets — external trusted sources

Reference pages for **third-party data sources the team consumes regularly but does
not produce**: where the data lives, how we access it (API / download / loader),
what shape it is, and which KB pages depend on it. One page per source.

## What belongs here (and what doesn't)

A `dataset` page is the **one home** for facts about an external source that would
otherwise be copy-pasted across framework/pipeline pages — the access pattern, auth,
resolution, licensing, and the loader we use.

- **Consumed ad-hoc, no pipeline of ours → page here.** IPC/CH, HDX, HRP/HNRP,
  FEWS NET, EM-DAT, WorldPop, FAO ASI/VHI, GHSL, [GloFAS](glofas.md),
  [JRC ASAP](jrc-asap.md), [CHIRPS-GEFS](chirps-gefs.md). These are the gap this
  folder fills.
- **We run a pipeline that ingests it → the pipeline page is the reference** for the
  ingest mechanics. Don't duplicate. IMERG (`pipelines/imerg.md`), FloodScan
  (`floodscan-ingest.md`), ACLED (`acled-fetcher.md`), NHC (`nhc-forecast.md`),
  GDACS/Google-Flood (flood pipelines). A dataset page here is still warranted when the
  **source itself** carries shared knowledge with no pipeline home — upstream conventions,
  licence nuance, data quirks — as for [ECMWF SEAS5/ERA5](ecmwf.md) and
  [IBTrACS](ibtracs.md); those pages link down to the pipeline for the ingest.
- **Country/partner one-off (1–2 pages) → stays a tag.** INSIVUMEH, RSMC La Réunion,
  FMS, BNGRC, DGPC, etc. Promote to a page only if a second page duplicates its facts.

Datasets remain **tags** (`data_sources: [...]`) on the pages that use them; this
folder holds the pages for the ones worth a shared home. See
[docs/INGESTION.md](../../docs/INGESTION.md) → *dataset* content type.

## Can we share derived products?

Quick redistribution matrix — can we **freely share derived products** (with attribution)?
The per-source nuance lives on the linked page (or the pipeline page for pipeline-ingested
sources); this is the at-a-glance answer. From the team's licence review (retired Confluence
"Licenses and Permissions", 2026-01).

| source | share derived products? | key condition |
|---|---|---|
| SEAS5 ([ecmwf](ecmwf.md)) | **sometimes** | CC-BY-4.0, but ECMWF clarified our free access is tied to **Official Duties** — not competitive/market-distorting use |
| FloodScan ([pipeline](../../pipelines/floodscan-ingest.md)) | **NO** | AER Use-of-Services/Data agreement; derived-product sharing **requires AER approval** |
| ERA5 ([ecmwf](ecmwf.md)) | yes | CC-BY-4.0 + cite the CDS catalogue DOI [10.24381/cds.f17050d7](https://doi.org/10.24381/cds.f17050d7) + visible Copernicus attribution |
| IMERG ([pipeline](../../pipelines/imerg.md)) | yes | NASA — freely available at all processed levels; cite Huffman et al. |
| IBTrACS ([ibtracs](ibtracs.md)) | yes | full & open (WDC); WMO Resolution 40 guides commercial use |
| NHC ([pipeline](../../pipelines/nhc-forecast.md)) | yes | US public domain; don't claim copyright or imply NOAA/NWS endorsement |
| ECMWF/TIGGE storm forecasts ([pipeline](../../pipelines/storms-pipeline.md)) | yes | CC-BY-4.0; cite the TIGGE TC Track Data DOI [10.5065/D6GH9GSZ](https://doi.org/10.5065/D6GH9GSZ) |

## Page frontmatter

```yaml
content_type: dataset
name: <canonical>
aliases: [<other spellings/tags used in the KB>]
provider: "<org>"
data_type: <food-security-phase | population-raster | disaster-impacts | ...>
access: public | registered | restricted
api: "<endpoint or portal URL, or null>"
auth: "<none | free API key | registration | ...>"
formats: [geojson, geotiff, xlsx, ...]
resolution: "<spatial/temporal grain>"
update_cadence: "<how often it refreshes>"
license: "<terms>"
code_ref: <loader we use, e.g. ocha-stratus emdat.load_emdat_from_blob, or null>
mirror: none | manual | automated | n/a   # is a copy in OUR blob/DB? (drives the wishlist below)
mirror_priority: high | med | low         # how much a stale/absent copy hurts
used_by: [<kb page paths>]
last_verified: <YYYY-MM-DD>
```

`how_we_use` prose follows the frontmatter. Keep the operational depth in the source
repo / loader; this page is the map, not the manual.

## Mirror candidates (which sources to pull into our infra)

The chatbot/MCP reads **our** blob + DB, not the live internet — so it can only *see the
data* for a source once a copy lives in our infra. `mirror:` records that state per page:
`automated` (a pipeline keeps it fresh — done), `manual` (in our blob but hand-refreshed →
stale risk), `none` (not in our infra at all), `n/a` (a platform/API we query per-need, not
a mirrorable dataset). The table below is the **derived wishlist** — every page that isn't
`automated`/`n/a`, ranked by priority then demand (`used_by` count). It's generated from the
pages, never hand-edited: when a mirror lands, flip that page's `mirror:` and it drops off.

Regenerate with `python scripts/gen_dataset_mirrors.py` (CI guards it with `--check`).

<!-- MIRRORS:START -->
**8 mirror candidate(s)** — ranked by priority, then demand (pages that reference the source):

| dataset | current state | priority | demand | note |
|---|---|---|---|---|
| [EM-DAT](emdat.md) | ⚠️ manual refresh (stale risk) | high | 10 pages | already in blob, no fresh loop |
| [IPC](ipc.md) | ❌ not in our infra | high | 7 pages | no copy, no loader |
| [CHIRPS-GEFS](chirps-gefs.md) | ❌ not in our infra | med | 7 pages | no copy, no loader |
| [FAO ASI/VHI](fao-asi-vhi.md) | ❌ not in our infra | med | 4 pages | no copy, no loader |
| [FEWS NET](fews-net.md) | ❌ not in our infra | med | 3 pages | no copy, no loader |
| [JRC ASAP](jrc-asap.md) | ❌ not in our infra | med | 2 pages | no copy, no loader |
| [WorldPop](worldpop.md) | ⚠️ manual refresh (stale risk) | low | 10 pages | already in blob, no fresh loop |
| [GHSL](ghsl.md) | ⚠️ manual refresh (stale risk) | low | 3 pages | already in blob, no fresh loop |

<!-- MIRRORS:END -->
