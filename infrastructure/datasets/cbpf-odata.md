---
content_type: dataset
name: CBPF OData API (PFBI)
aliases: ["CBPF API", "cbpfapi", "pooled fund data hub", "PFBI", "CBPF allocations"]
provider: "UN OCHA — Country-Based Pooled Funds section (OneGMS; the API behind pfdata.unocha.org / cbpfgms.github.io)"
data_type: humanitarian-financing
access: public
api: "https://cbpfapi.unocha.org/vo2/odata/  (OData; key collections: AllocationTypes — all allocation envelopes incl. CERF rows; MstPooledFund — the 46-fund registry; ProjectSummary?poolfundAbbrv=<abbrv> — project × cluster × admin-location rows per fund)"
auth: none
formats: [json, xml, csv]
resolution: "allocation-level (one row per Standard/Reserve allocation envelope per pooled fund, 2014-ish–present) + project-level (one row per grant to ONE implementing partner — CBPF funds NGOs incl. NNGOs directly, unlike CERF — with cluster splits, admin locations, and ##-delimited sub-implementing partners)"
update_cadence: live feed from OneGMS
license: open (public UN data)
code_ref: "ds-cerf-supplement scripts/refresh_cbpf.py (daily allocation/fund upsert + aa.v_allocation view) + scripts/refresh_cbpf_projects.py (daily project full-replace)"
mirror: automated       # aa.cbpf_allocation + aa.cbpf_fund + aa.cbpf_project(_cluster/_subip), daily via refresh-mirror
mirror_priority: med
used_by:
  - pipelines/cerf-supplement.md
  - pipelines/aa-tracking.md
last_verified: 2026-08-25
---

# CBPF OData API (PFBI)

The public OData API behind the CBPF Data Hub visuals — the pooled-fund counterpart of
the [CERF OneGMS feed](cerf-onegms.md). We mirror it daily into the dev `aa` schema
(`ds-cerf-supplement`, the home of all OneGMS mirrors).

## What it holds

- **`AllocationTypes`** — every *allocation* (a titled Standard/Reserve envelope
  containing a set of approved projects) across all pooled funds: title, summary,
  year, planned/approved budgets, project counts. **Also lists CERF allocations**
  (`FundTypeId = 2`) — exclude them; the CERF feed stays authoritative for CERF.
  `FundTypeId = 1` = CBPF + regional funds (RhPF).
- **`MstPooledFund`** — the fund registry: 46 pooled funds incl. the regional
  envelopes (RhPF-WCA/LAC/AP) and their per-country children (`ParentPFId`).
- **`ProjectSummary?poolfundAbbrv=<abbrv>`** — project-level rows **per fund** (the
  unfiltered endpoint times out): org name/type, budget, dates, status, targets,
  cluster splits, admin locations, sub-implementing partners.

## Gotchas

- **`AllocationTypeId` is NOT unique** — reused across funds (~50 collisions), the
  CBPF cousin of the CERF feed's `ApplicationID` gotcha. Key on
  **`(PooledFundId, AllocationTypeId)`**.
- **Sub-IP fields are `##`-delimited parallel lists** (`SubIPName` / `SubIPTypeId` /
  `SubIPAmt` cram several sub-partners into one cell) — explode before loading.
- `ProjectSummary` returns one row per project × cluster × admin-location (Afghanistan
  alone is ~14k rows / 29 MB) — normalize, don't mirror raw.
- Regional-envelope children share the envelope's `PFAbbrv` (e.g. Bangladesh (AP-RHPF)
  = `AP501`) — fetch per **distinct** abbrev; rows carry the child `PooledFundId`.
- No structured AA flag — AA allocations are identified by title/summary keyword
  (`anticipat`, `early action`, + French variants), same convention as the CERF
  mirror's `aa_keyword`.

## Where it lands

`aa.cbpf_allocation` (737 envelopes, 37 AA-keyword) · `aa.cbpf_fund` ·
`aa.cbpf_project` (16.3k) · `aa.cbpf_project_cluster` · `aa.cbpf_project_subip` —
plus **`aa.v_allocation`**, the fund-agnostic UNION view over the CERF and CBPF
allocation mirrors that downstream linking reads. Admin-location splits are
deliberately not mirrored (no consumer yet).

Why it matters for AA: CBPF pays NGOs directly, so this is where AA **localization**
is visible — under AA-keyword CBPF allocations, national NGOs hold ~252 projects /
~$129M directly (CERF shows NNGO money only as subgrants).
