---
content_type: dataset
name: CBPF OData API (PFBI)
aliases: ["CBPF API", "cbpfapi", "pooled fund data hub", "PFBI", "CBPF allocations", "OneGMS public API", "GlobalGenericDataExtract", "Beneficiary Data Tool", "BDT"]
provider: "UN OCHA — Country-Based Pooled Funds section (OneGMS; the API behind pfdata.unocha.org / cbpfgms.github.io)"
data_type: humanitarian-financing
access: public
api: "https://cbpfapi.unocha.org/vo3/odata/ (28 OData entity sets, $metadata-typed; vo1 still answers for 9 older sets) + https://cbpfapi.unocha.org/vo3/odata/GlobalGenericDataExtract?SPCode=<code>&PoolfundCodeAbbrv=<PFAbbrv>&$format=csv (127 catalogued stored queries at /vo3/, 33 public) + Beneficiary Data Tool https://pfbi-eastus2-api-site.azurewebsites.net/bdt2/api/public/v1/ (deduplicated people)"
auth: none (94 stored queries are secured — HTTP Basic on cbpfapib.unocha.org — and NOT mirrored)
formats: [json, xml, csv]
resolution: "fund (46) → allocation envelope (904 incl. CERF rows) → project (16.3k grants to one implementing partner each) → cluster / admin-location / sub-IP / indicator / narrative-report splits; all figures are CURRENT STATE (cumulative, overwritten in place — no history endpoint)"
update_cadence: "live feed from OneGMS's reporting DB (LastModified entity set gives the last refresh timestamp; partner progress lands ~monthly)"
license: open (public UN data)
code_ref: "ds-cerf-supplement src/cbpf_api.py + src/bdt_api.py (clients), src/cbpf_registry.py (what is mirrored + how), scripts/refresh_cbpf_full.py (schema cbpf, daily), scripts/refresh_cbpf.py + refresh_cbpf_projects.py (normalized aa.cbpf_*, daily)"
mirror: automated       # schema cbpf (complete raw mirror, ~70 tables, refresh-cbpf-full.yml 03:00 UTC) + aa.cbpf_* (normalized AA-facing subset, refresh-mirror.yml)
mirror_priority: med
used_by:
  - pipelines/cerf-supplement.md
  - pipelines/aa-tracking.md
last_verified: 2026-09-18
---

# CBPF OData API (PFBI)

The public API behind the CBPF Data Hub visuals — the pooled-fund counterpart of the
[CERF OneGMS feed](cerf-onegms.md). We mirror **all of it** daily into the dev DB
(`ds-cerf-supplement`, the home of all OneGMS mirrors): the complete raw mirror in
schema **`cbpf`** (one table per public surface) and a normalized AA-facing subset in
schema `aa`. The ERD of the whole mirror, with live row counts and column lists:
<https://ocha-dap.github.io/ds-cerf-supplement/mirror/>.

## The three public surfaces

| Surface | Where | What |
| --- | --- | --- |
| **OData entity sets** | `/vo3/odata/<Set>` (28; `$metadata` types every column) and `/vo1/odata/<Set>` (50 listed, **9 still answer**) | fund/allocation/project masters, aggregates, contributions; vo1 is the only public home of the vo1-shape project row (org name on the row, direct/support cost split, planned dates, **proposal narrative text** with `ShowFullProjectInfo=1`), per-project cluster budgets, logframe indicators, narrative-report beneficiaries, contribution-level donor records |
| **Stored queries** | `/vo3/odata/GlobalGenericDataExtract?SPCode=<code>&PoolfundCodeAbbrv=<PFAbbrv>&…&$format=csv` — catalogue (127) scraped from `/vo3/` | the project record (`PF_PROJ_SUMMARY_V4`, 68 cols: targeted/reached M/W/B/G, disability, marker budgets, CVA, risk), `PF_PROJ_DETAIL` (title, dates), `PF_ORG_SUMMARY` (org master), `PF_GLB_INDIC` (indicator progress), `PF_RPT_CLST_BENEF`, `APIDAT_CVA`, `PROJ_LOC_MAP`, the masters (clusters, indicators, emergencies, markers, statuses) |
| **Beneficiary Data Tool (BDT2)** | `https://pfbi-eastus2-api-site.azurewebsites.net/bdt2/api/public/v1/{beneficiary,beneficiaryByDisabilities,templates}/` | **deduplicated** people targeted/reached per fund × allocation (× location) and per stored template (incl. the 2026 US tranches). Never reconciles with OneGMS project counts — stored separately, never summed across templates |

Everything is **current state**: cumulative figures overwritten in place, no history
endpoint. `cbpf.mirror_run` logs every load; monthly snapshotting is the planned next
layer.

## Gotchas (all verified live 2026-09-18)

- **`AllocationTypeId` is NOT unique** — reused across funds (~50 collisions), the
  CBPF cousin of the CERF feed's `ApplicationID` gotcha. Key on
  **`(PooledFundId, AllocationTypeId)`**.
- **Fetch stored queries as CSV, never JSON** — the JSON form silently drops columns
  (`PF_PROJ_SUMMARY_V4`: 30 in JSON vs **68** in CSV; `PF_GLB_INDIC` 11 vs 19).
- **`ShowAllPooledFunds=1` does nothing** — fund-scoped queries still return one fund.
  Per-fund fan-out over the **34 distinct `PFAbbrv`** is the only way to get the
  portfolio; regional children share the envelope's abbrev (`AP501` = BGD/PAK/FJI/
  VUT/SLB) and rows carry the child `PooledFundId`.
- **Errors don't look like errors**: a missing/invalid parameter is an **HTTP 500
  HTML page**; a secured SPCode on the public host is an **HTTP 200** body
  `{"Error": "This is secure procedure…"}`. Check the first row.
- **Blank `AllocationYear(s)` = all years** the query covers; the `*_OneGMS`
  queries, `APIDAT_CVA`, `PF_GLB_INDIC` and the `Agg_V4` warehouse extract only
  cover OneGMS-era projects (2023+).
- **`PF_GLB_STATUS`** needs `InstanceTypeId` (1–7) and ignores the fund parameter
  (returns all 44 funds) — it is a status-code vocabulary in the fund's language.
- **`CBPFSummary`** needs a `?year=` to answer but ignores its value (all-time
  totals); **`HRPCBPFFundingSummary`** 404s for every parameter form.
- **Sub-IP fields are `##`-delimited parallel lists** (`SubIPName` / `SubIPTypeId` /
  `SubIPAmt`) — explode before using; `ProjectSummary` (vo3) is exploded per
  project × cluster × admin-location (~80k rows portfolio-wide) — `aa.cbpf_project*`
  is the normalized form.
- **French-locale text can be double-encoded UTF-8** (`approuvÃ©`) — Latin-1 round
  trip repairs it; **status vocabularies are bilingual** — map on codes, not labels.
- **BDT**: groups/templates are separate deduplication queries, **not sums**
  (combined ≠ T1 + T2); `only_allocation=1` and `template_name=` are mutually
  exclusive; the `GT_*` global templates 404 on `/beneficiary/`; blank = not yet
  reported, not zero; the legacy v2 feed returned nothing for 2025.
- No structured AA flag — AA allocations are identified by title keyword
  (`anticipat`, `early action`, + French variants), same convention as the CERF
  mirror's `aa_keyword` (title only — summaries produce large false positives).

## Where it lands

- **Schema `cbpf`** (raw, ~70 tables, `refresh-cbpf-full.yml` daily 03:00 UTC):
  columns keep the API's names snake_cased, typed from `$metadata` or by inference;
  full-replace per table; `fetched_at` on every row; `cbpf.mirror_run` per load.
  The registry `src/cbpf_registry.py` is the single source of what/how, and its
  tail lists what was probed and left out: the 94 secured stored queries, the
  superseded `PF_PROJ_SUMMARY`/`_V2`/`_V3` and `Agg_V3`, the 41 dead vo1 sets.
- **Schema `aa`** (normalized, `refresh-mirror.yml`): `aa.cbpf_allocation` (CBPF-only
  envelopes + `aa_keyword`) · `aa.cbpf_fund` · `aa.cbpf_project` (16.3k) ·
  `aa.cbpf_project_cluster` · `aa.cbpf_project_subip` — plus **`aa.v_allocation`**,
  the fund-agnostic UNION view over the CERF and CBPF allocation mirrors that
  downstream linking reads.

Why it matters for AA: CBPF pays NGOs directly, so this is where AA **localization**
is visible — under AA-keyword CBPF allocations, national NGOs hold ~252 projects /
~$129M directly (CERF shows NNGO money only as subgrants).
