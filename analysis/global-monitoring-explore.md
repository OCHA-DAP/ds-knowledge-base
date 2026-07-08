---
content_type: analysis
name: global-monitoring-explore
analysis_type: exploratory   # exploratory | ad-hoc-activation | pre-framework | regional-overview | other
status: dormant               # frozen local data extracts, stub second notebook, no CI/schedule/deployment; work not carried forward in this repo
country_iso3: global          # JRC ASAP hotspot data is worldwide, country/admin0-level, not scoped to one country
hazard: drought                # JRC ASAP tracks agricultural/vegetation-biomass anomaly, used elsewhere in the KB (sahel-drought) as a drought indicator
summary: "R/Quarto exploration of JRC ASAP agricultural-hotspot transitions (no→minor→major) as a candidate alert trigger and chart/map format for the pa-global-monitoring email pipeline, plus an unrelated generic map point/bubble-sizing technique stub. Not a framework or a pipeline — a frozen, undeployed exploration."
data_sources: [ASAP]
feeds: []   # standalone — see "Relation to frameworks" for the (unconfirmed) hdx-signals lineage
# --- source repo ---
source_repo: ocha-dap/ds-global-monitoring-explore
source_branch: map-pt-testing
source_sha: f8d3775
code_ref:
  - "exploration/asap_hotspot_exploration.qmd — ASAP hotspot classification + alert-frequency + map/timeseries exploration"
  - "exploration/map_pts_testing.qmd — unedited Quarto default template; synthetic point/bubble-sizing map technique test, not tied to ASAP or any real country data"
  - "README.Rmd / README.md — states the repo's purpose relative to pa-global-monitoring"
depends_on: []   # reads only frozen local CSV/shapefile extracts, no live DB table or pipeline dependency
discrepancies:
  - "[gap] map_pts_testing.qmd (the file the active branch map-pt-testing is named for) is the literal unedited Quarto starter template — synthetic random points on a Natural Earth Tanzania polygon, testing ellipse/bubble sizing + legend construction for point-magnitude maps. It never applies the technique to real monitoring data; treat it as a rendering-technique scratchpad, not a finding."
  - "[gap] asap_hotspot_exploration.qmd reads local paths under AA_DATA_DIR/AA_DATA_DIR_NEW (legacy local-filesystem env vars, same pattern as glb-tropicalcyclones) — the hotspots_ts.csv extract date is not recorded in the notebook and nothing in this repo refreshes it; findings reflect whatever snapshot was on disk when last run, not current ASAP data."
  - "[conflict] A top-of-notebook NOTE says the 'Number of Countries per Alert' section is 'not working - eval set to FALSE. Don't try to run that yet.' — but in the committed code those chunks are NOT flagged eval=F (global execute is eval: true); the only eval=F chunks are the 'Single Map Per Country' map and the 'Appendix Scrap' block. The author's note and the code disagree. The actually-broken chunk is the Timeseries one, which references `last10_alert_months`, defined only inside an eval=F Appendix chunk, so it would error on a clean render."
  - "[conflict] The stated trigger intent (intro NOTE: alerts on no→minor or minor→major) does not match the code: `flag_minor_to_major` is defined as `hs_major_lgl & lag(hs_major_lgl)` (major this month AND major last month = major persisting), not `major & lag(minor)`. So the flag labelled 'gradual major' actually fires on persistent-major, and a genuine minor→major transition is never flagged. Looks like a bug in this scratch code; no doc exists to arbitrate, so the code is not authoritative for any live trigger."
  - "[conflict] hdx-signals (pipelines/hdx-signals.md) already runs a live 'Monitor JRC agricultural hotspots' GitHub Actions workflow using the same ASAP/GAUL data — but this repo's README frames itself as exploration for the sibling pa-global-monitoring repo, not hdx-signals, and pa-global-monitoring is not itself in the KB. No code or commit in this repo confirms the ASAP hotspot logic explored here was carried into hdx-signals; the lineage is plausible but unevidenced, so feeds is left empty rather than asserted."
extra: {}
visibility: internal
last_synced: "2026-07-08"
---

# Global monitoring exploration — analysis

> **Analysis, not a framework.** A framework page is *only* for something with its own published framework doc. This repo is analysis (exploratory work) — captured so the work is findable, and linked to the framework(s)/pipeline(s) it may support.

## What it is

`ds-global-monitoring-explore` is a small R/Quarto scratch repo whose stated purpose (per `README.Rmd`) is to explore ideas for the **pa-global-monitoring** repo — a sibling repo already wired with `{renv}` and cron-scheduled GitHub Actions that sends "Global Monitoring" alert emails — without adding dependencies to that live repo. It holds exactly two `.qmd` exploration documents and no pipeline code, no tests, and no deployment. It is not a framework (no country/hazard trigger, no published doc) and not a pipeline (nothing scheduled or deployed; correctly absent from `infrastructure/pipeline-registry.md`).

## What was analyzed / findings

**`exploration/asap_hotspot_exploration.qmd`** — the substantive piece. It explores whether the JRC **ASAP** ("Anomaly hotSpots of Agricultural Production") country-level hotspot classification (no hotspot / minor hotspot / major hotspot, from a frozen local extract at `AA_DATA_DIR_NEW/public/raw/glb/asap/hotspots_ts/hotspots_ts.csv`, joined to GAUL0 admin-0 boundaries at `AA_DATA_DIR/public/raw/glb/asap/reference_data/gaul0_asap_v04`) could drive a global monitoring email alert:

- **Trigger mechanism explored**: reuse JRC's own hotspot categories as-is — the stated intent (intro NOTE) is to flag a country when it transitions **no → minor** or **minor → major** hotspot month-over-month. No new threshold is derived; the candidate trigger is simply "watch for a category upgrade." The code defines three flags (`flag_to_minor`, `flag_minor_to_major`, `flag_no_to_major`), but note that `flag_minor_to_major` is coded as major-and-still-major (persistent major), not an actual minor→major transition — an apparent bug in the scratch code (see `discrepancies`).
- **Alert-frequency check**: histograms of how many countries would be flagged in the same monthly email, both overall and split by transition type (minor / gradual major / abrupt major) — sizing the problem of "how many countries per email."
- **Chart format candidates**: a per-alert tile/point/line timeseries (hotspot category over the trailing 6 months) faceted by country, prototyped as the "easiest to automate for emails" visualization; the author notes a foreseeable issue if more than ~7 countries flag simultaneously (colored-line crowding).
- **Map format candidates**: (a) one map per alert-month with all flagged countries shaded by transition class, bounding-boxed to the flagged set; (b) one small map per flagged country, patchworked together — explicitly noted by the author as too slow to render ("~5 min... looks insane") and not worth pursuing further.
- A top-of-notebook author note flags the **"Number of Countries per Alert"** section as "not working — eval set to FALSE. Don't try to run that yet." — but the committed chunks in that section are *not* actually marked `eval=F` (see `discrepancies`); the chunk that would genuinely fail on a clean render is the Timeseries one, which depends on `last10_alert_months` defined only inside an `eval=F` Appendix chunk.
- Ends with an "Appendix Scrap" of abandoned alternative groupings (`eval: false`), kept only as a record of discarded ideas.

**`exploration/map_pts_testing.qmd`** — an empty stub in substance: it is the **unedited Quarto default "Untitled" starter template**, repurposed only to test a generic cartographic technique — sizing/legending point markers as ellipses so bubble area scales with a `value` field — using synthetic random points scattered over a Natural Earth Tanzania polygon (`rnaturalearth`/`sf`). It does not touch ASAP, hotspots, or any real monitoring indicator; it is a rendering-technique scratchpad for point-magnitude maps (relevant if a future alert map needs to size markers by e.g. population or magnitude), not an analytical finding. This is the file the active branch (`map-pt-testing`) is named after.

No conclusion or recommendation is written up anywhere in the repo; both documents end mid-exploration.

## Relation to frameworks

Standalone (`feeds: []`). The repo names its intended consumer as **`pa-global-monitoring`**, which is not itself a page in this KB (not a framework, and `docs/repo-manifest.md` only lists the unrelated, COVID-era `pa-global-monitoring-dashboard`). The closest *live* KB neighbour is [`pipelines/hdx-signals`](../pipelines/hdx-signals.md) — a GitHub-Actions-scheduled monitoring/alert-email pipeline that already runs a live "Monitor JRC agricultural hotspots" workflow against the same ASAP/GAUL reference data, plus monitors for six other indicator sources (ACLED, ACAPS INFORM, IDMC, IPC, WFP Market Monitor, WHO cholera) feeding Mailchimp campaigns and an HDX dataset. Nothing in either repo cross-references the other, so whether this exploration's ASAP-transition logic informed `hdx-signals`'s JRC hotspot monitor, or the two are independent, unevidenced (see `discrepancies`). Also loosely adjacent: [`pipelines/glb-tropicalcyclones`](../pipelines/glb-tropicalcyclones.md), which uses the same GAUL0/ASAP admin-0 reference shapefile and the same legacy `AA_DATA_DIR`/`AA_DATA_DIR_NEW` local-filesystem convention, for an unrelated (tropical cyclone) purpose.

## Sources & status

Repo `ocha-dap/ds-global-monitoring-explore`, branch `map-pt-testing` @ `f8d3775` (see `code_ref`). No `renv.lock`, no CI, no `.github/workflows/`, no Azure app, no Databricks job — purely local, interactively-rendered Quarto documents reading local-filesystem env vars (`AA_DATA_DIR`, `AA_DATA_DIR_NEW`), the same legacy pattern documented in `glb-tropicalcyclones`. Both exploration documents stop mid-thought with no write-up of conclusions, and the second is a copy-pasted default template never adapted to real data.

**Dormant**: frozen local data snapshot (extract date unrecorded), one file a genuine but unfinished exploration, the other an unedited template stub, no evidence the work was picked up in `pa-global-monitoring` or elsewhere. Re-running requires a local `AA_DATA_DIR`/`AA_DATA_DIR_NEW` tree with the ASAP hotspot CSV and GAUL0 shapefile already present — nothing in the repo fetches or refreshes them.
