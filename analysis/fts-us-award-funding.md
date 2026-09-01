---
content_type: analysis
name: fts-us-award-funding
analysis_type: ad-hoc
status: active
country_iso3: [HTI, BGD, TCD, COL, COD, SLV, ETH, GTM, HND, KEN, MOZ, MMR, NGA, SSD, SDN, SYR, UGA, UKR]
hazard: n/a
summary: FTS incoming funding to the 18 US Award countries 2025–2026, split GHO vs non-GHO plus pooled-fund (CERF+CBPF) shares; single CSV + Excel + GH Pages table, rerunnable stdlib pull
data_sources: [fts, hnrp, cerf, cbpf]
feeds: []
surfaces:
  - {url: "https://ocha-dap.github.io/ds-fts/", kind: download, title: "FTS GHO-vs-non-GHO funding download page"}
# --- source repo ---
source_repo: ocha-dap/ds-fts
source_branch: main
source_sha:
code_ref: [fts_gho_pull.py]
depends_on: [hnrp]
discrepancies: []
extra: {}
visibility: public
last_synced: "2026-07-24"
---

# FTS US Award funding (GHO vs non-GHO) — analysis

> **Analysis, not a framework.** Ad-hoc funding breakdown; no trigger or plan doc involved.

## What it is

A single-deliverable pull of **FTS incoming humanitarian funding to the 18 US Award
countries** (HTI BGD TCD COL COD SLV ETH GTM HND KEN MOZ MMR NGA SSD SDN SYR UGA UKR),
2025 vs 2026, split by whether the money went to a **GHO plan** or outside the GHO.
Output is one CSV (country × year × GHO/non-GHO/total), published with a table +
download page on GH Pages: <https://ocha-dap.github.io/ds-fts/>.

## What was analyzed / findings

- Source is the **public HPC/FTS API** (`api.hpc.tools`, no auth):
  `/v1/public/fts/flow?countryISO3=X&year=Y&groupby=plan` using **`report3`**
  (destination-plan grouping incl. boundary flows — this exactly reproduces FTS's own
  HDX export `fts_requirements_funding_global.csv`, validated to the dollar), plus
  `/v2/public/plan/year/Y` → `planVersion.isPartOfGHO` for GHO membership.
- 2025 totals ≈ $12.15B (81% GHO) across the 18 countries; 2026 (partial, self-reported
  and still rising) ≈ $8.8B (86% GHO).
- Gotchas worth remembering: **Ethiopia HRP 2025 funding is not public on FTS** (plan
  1272 → "data not publicly available"), so ETH GHO is understated; **Uganda 2026
  non-GHO is negative** in FTS's own attribution (cross-boundary RRP flows);
  SLV/GTM/HND have **no GHO plan in 2026** (Central America HNRPs ended with 2025);
  the Syria As-Sweida addendum (plan 1432) is absent from the plan APIs and is
  GHO-classified via a manual override in the script.

## Relation to frameworks

Standalone.

## Sources & status

Repo `ocha-dap/ds-fts` — `fts_gho_pull.py` (stdlib-only, rerunnable; refreshes the CSV
incl. pooled columns), `gen_excel.py` (wide Excel), site with year filter +
all-country totals (any-branch push redeploys). A reproduction of the internal
quarterly US Award dashboard is parked in `dashboard/NOTES.md` (panel→API mapping,
what has no public source, why the ProjectSummary pulls stalled). Full
methodology + reconciliation in the repo README. Active; figures update whenever
re-run. See
[hnrp dataset page](../infrastructure/datasets/hnrp.md) for the broader FTS/HPC access
pattern.
