# Datasets — external trusted sources

Reference pages for **third-party data sources the team consumes regularly but does
not produce**: where the data lives, how we access it (API / download / loader),
what shape it is, and which KB pages depend on it. One page per source.

## What belongs here (and what doesn't)

A `dataset` page is the **one home** for facts about an external source that would
otherwise be copy-pasted across framework/pipeline pages — the access pattern, auth,
resolution, licensing, and the loader we use.

- **Consumed ad-hoc, no pipeline of ours → page here.** IPC/CH, HDX, HRP/HNRP,
  FEWS NET, EM-DAT, WorldPop, FAO ASI/VHI, GHSL. These are the gap this folder fills.
- **We run a pipeline that ingests it → the pipeline page is the reference.** Don't
  duplicate. IMERG (`pipelines/imerg.md`), FloodScan (`floodscan-ingest.md`), ACLED
  (`acled-fetcher.md`), NHC (`nhc-forecast.md`), IBTrACS/SEAS5/ERA5 (raster + storms
  pipelines), GDACS/GloFAS/Google-Flood (flood pipelines). At most add a one-line
  stub here pointing at the pipeline.
- **Country/partner one-off (1–2 pages) → stays a tag.** INSIVUMEH, RSMC La Réunion,
  FMS, BNGRC, DGPC, etc. Promote to a page only if a second page duplicates its facts.

Datasets remain **tags** (`data_sources: [...]`) on the pages that use them; this
folder holds the pages for the ones worth a shared home. See
[docs/INGESTION.md](../../docs/INGESTION.md) → *dataset* content type.

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
**6 mirror candidate(s)** — ranked by priority, then demand (pages that reference the source):

| dataset | current state | priority | demand | note |
|---|---|---|---|---|
| [EM-DAT](emdat.md) | ⚠️ manual refresh (stale risk) | high | 10 pages | already in blob, no fresh loop |
| [IPC](ipc.md) | ❌ not in our infra | high | 7 pages | no copy, no loader |
| [FAO ASI/VHI](fao-asi-vhi.md) | ❌ not in our infra | med | 4 pages | no copy, no loader |
| [FEWS NET](fews-net.md) | ❌ not in our infra | med | 3 pages | no copy, no loader |
| [WorldPop](worldpop.md) | ⚠️ manual refresh (stale risk) | low | 10 pages | already in blob, no fresh loop |
| [GHSL](ghsl.md) | ⚠️ manual refresh (stale risk) | low | 3 pages | already in blob, no fresh loop |

<!-- MIRRORS:END -->
