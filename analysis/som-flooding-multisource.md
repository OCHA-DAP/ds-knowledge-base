---
content_type: analysis
name: som-flooding-multisource
analysis_type: pre-framework
status: active
country_iso3: SOM
hazard: flood
summary: Multi-source (GloFAS / Google Flood Hub / GEOGloWS) riverine flood trigger design for the Juba and Shabelle, calibrated against SWALIM gauges — the proposed mechanism for a Somalia flooding AA framework
data_sources: [glofas, google-flood-hub, geoglows, swalim, floodscan]
feeds: []
# --- source repo ---
source_repo: ocha-dap/ds-aa-som-floods
source_branch: feat/multisource-trigger
source_sha: 6669adda3
code_ref:
  - analysis/11_multisource_trigger.ipynb
  - analysis/01_swalim_flood_threshold_exceedance.ipynb
  - src/constants.py
depends_on: []
discrepancies: []
extra: {}
apps: [https://sturdy-memory-v6voe4m.pages.github.io/]  # private Pages — OCHA-DAP members only
visibility: internal
last_synced: 2026-08-25
---

# Somalia riverine flooding, multi-source trigger — analysis

> **Analysis, not a framework.** Pre-framework trigger design for anticipatory
> action against riverine flooding on the Juba and Shabelle; no framework doc
> has been published yet. This page is the landing page for the analysis and
> its rendered report site.

## What it is

Trigger design combining the three global streamflow providers — **GloFAS**
(v5 reanalysis / v4 reforecast, EWDS), **Google Flood Hub** (GRRR) and
**GEOGloWS v2** — against **FAO SWALIM river-gauge observations** as ground
truth. Follows the Nigeria flooding playbook (pooled best-skill station
selection, per-station Weibull thresholds at a common return period, N-of-M
same-day consensus), adapted to Somalia's two rivers x two flood seasons
(Gu, Deyr) and to the presence of a real gauge network. Built in
`ds-aa-som-floods`: evidence notebooks 01–10 (Pauline Wairimu, Aug 2026 —
SWALIM thresholds/events, model-vs-gauge skill, lead-time skill, FloodScan
benchmarks, station selection, trigger grids, a staged-mechanism
exploration) and the mechanism itself in notebook 11 (Tristan Downing,
2026-08-25).

**The rendered trigger report**:
<https://sturdy-memory-v6voe4m.pages.github.io/> (private Pages — OCHA-DAP
members only): landing page at the site root, report under
[`/trigger/`](https://sturdy-memory-v6voe4m.pages.github.io/trigger/).

## What was analyzed / findings

The mechanism is **fully forecast-based** (SWALIM is calibration/validation
ground truth, not a trigger input), one specific trigger per basin x season,
each staged readiness -> action:

| window | action (leads <= 6 d) | leg RP | readiness (leads 7-12 d, GloFAS-only) |
|---|---|---|---|
| Juba Gu | Google GRRR: >= 6/8 stations over own RP6 threshold | 6.5 y | GloFAS RP2 >= 5/8 (RP 3.7) |
| Juba Deyr | GloFAS v5: >= 6/8 over RP6 | 13.0 y | GloFAS RP2 >= 6/8 (RP 4.4) |
| Shabelle Gu | Google GRRR: >= 6/8 over RP6 | 8.7 y | GloFAS RP3 >= 2/8 (RP 3.7) |
| Shabelle Deyr | GloFAS v5: >= 7/8 over RP6 | 8.7 y | GloFAS RP2 >= 5/8 (RP 3.1) |

- **Return periods** (Weibull, backtest 1999–2023): each basin 6/25 years =
  **1-in-4.3, equal by construction**; overall (either basin) 7/25 =
  **1-in-3.7**, meeting the >= 3-year spec. Activation years 2006, 2013,
  2016, 2018, 2019, 2020, 2023 — all documented major floods. Under all-in
  funding, effective RP = overall RP.
- **Provider outcome**: multi-source by competition, not quota — GRRR wins
  both Gu windows, GloFAS v5 both Deyr windows; GEOGloWS wins nowhere (ties
  GRRR on rho in Shabelle Gu but its signal trails the gauge by 4–10 days,
  it has no reforecast archive, and its forecasts run 0.6–0.7x its
  retrospective climatology). Selection rule: one source per station; among
  sources within 0.05 rho, the earliest signal wins.
- **Reforecast backtests**: Gu legs reproduce their calibration years
  cleanly (GRRR 2016–2023). Deyr legs run through the **v4 reforecast proxy**
  (no v5 reforecast exists) with thresholds refit on v4 climatology: Juba
  Deyr catches 2023 (late, −16 d vs the Luuq Moderate crossing), Shabelle
  Deyr catches 2019 but **misses Deyr 2023 at <= 6 d** — the key caveat;
  operational forecasts are v5, whose reanalysis flags 2023 clearly, but
  this is unprovable until EWDS publishes a v5 reforecast.
- **Readiness (7–12 d)**, using the leads-8-12 GloFAS reforecast downloaded
  for this purpose: full action-year coverage for three windows; Shabelle
  Deyr covers only 1/3 (v4 cannot see Deyr-2023-type events at that range).
  Readiness legs individually 1-in-3.1–4.4; union ~1-in-1.7.

**Open items before a trigger report**: independent impact-record
cross-check (the two-historical-records rule); v5 reforecast re-verification
when available; version pinning for operations (action thresholds are
v5-climatology, readiness v4-climatology); GEOGloWS re-assessment as its
archive grows; final RP adjustment + funding split with the working group.

## Relation to frameworks

Pre-figures a Somalia flooding CERF AA framework (none exists yet; the
evidence deck assumes a $7M all-in envelope). External Somalia flood AA
frameworks for context: `external-frameworks/wfp/som-flood.md`,
`external-frameworks/start-network/som-flood.md`. Somalia drought framework:
`frameworks/som-drought/`.

## Sources & status

- Repo: [`ds-aa-som-floods`](https://github.com/OCHA-DAP/ds-aa-som-floods)
  (private). Mechanism: `analysis/11_multisource_trigger.ipynb`; evidence
  chain: notebooks 01–10; station registry with per-provider ID mappings:
  `src/constants.py`. Adopted configuration tables in blob:
  `ds-aa-som-floods/processed/workflow/som_ms_*` (projects container, dev).
- Ground truth: SWALIM SNRFA river levels (16 gauges, thresholds table);
  benchmark = seasonal maxima at the reference gauges (Belet Weyne, Luuq),
  post-2000 record.
- Status: **active** — trigger structure agreed 2026-08-25, awaiting the
  open items above and working-group review. Evidence deck:
  `docs/som_flood_trigger_evidence.pptx` in the repo; Google Slides
  "Somalia Floods" (Aug 2026).
