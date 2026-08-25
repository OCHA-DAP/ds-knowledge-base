---
content_type: analysis
name: som-flooding-multisource
analysis_type: pre-framework
status: active
country_iso3: SOM
hazard: flood
summary: Multi-model (GloFAS / Google Flood Hub / GEOGloWS) riverine flood trigger design for the Juba and Shabelle, calibrated against SWALIM gauges — the proposed mechanism for a Somalia flooding AA framework
data_sources: [glofas, google-flood-hub, geoglows, swalim, floodscan]
feeds: []
# --- source repo ---
source_repo: ocha-dap/ds-aa-som-floods
source_branch: feat/multisource-trigger
source_sha: 6571c9f
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
[`/trigger/`](https://sturdy-memory-v6voe4m.pages.github.io/trigger/), and an
[indicator explorer](https://sturdy-memory-v6voe4m.pages.github.io/explorer/)
(basin x year daily timeseries: SWALIM level, per-source station-consensus
counts and reference-station signal, each source against its own 1-in-6
thresholds — GEOGloWS shown via its retrospective).

## What was analyzed / findings

The mechanism is **fully forecast-based** (SWALIM is calibration/validation
ground truth, not a trigger input), one specific trigger per basin x season,
each staged readiness -> action. Action legs are consensuses of
**(station, model) pairs** — pairs compete freely (a station may carry two
models) under two model-blind rules: a -3 d timing guard and a **relative
quality floor** (the voting pool is every pair within 0.10 rho of the
window's best — no fixed count, no diversity quota; an earlier explicit
diversity rule proved unnecessary and was dropped, decision 2026-08-25 v3).
Pool sizes 8-12 pairs per window:

| window | action (leads <= 6 d) | leg RP | readiness (leads 7-12 d, GloFAS-only) |
|---|---|---|---|
| Juba Gu | Google GRRR x8 + GloFAS v5 x3 + GEOGloWS: >= 9/12 pairs over own RP5 | 6.5 y | GloFAS RP2 >= 5/8 (RP 3.7) |
| Juba Deyr | GloFAS v5 x6 + GEOGloWS x2: >= 5/8 over RP4 | 13.0 y | GloFAS RP2 >= 5/6 (RP 4.4) |
| Shabelle Gu | Google GRRR x8 + GloFAS v5: all 9 pairs over RP5 | 13.0 y | GloFAS RP3 >= 2/8 (RP 3.7) |
| Shabelle Deyr | GloFAS v5 x8 + GEOGloWS x2: >= 8/10 over RP4 | 6.5 y | GloFAS RP2 >= 5/8 (RP 3.1) |

- **Return periods** (Weibull, backtest 1999-2023): each basin 6/25 years =
  **1-in-4.3, equal by construction**; overall (either basin) 8/25 =
  **1-in-3.2**, meeting the >= 3-year spec. Activation years 2006, 2013,
  2014, 2016, 2018, 2019, 2020, 2023 — all documented major floods. Under
  all-in funding, effective RP = overall RP.
- **GEOGloWS placement — earned, not injected**: it clears the model-blind
  floor in Juba Deyr (top-8 outright once the guard removes the trailing
  GloFAS pairs), Juba Gu and Shabelle Deyr; excluded from Shabelle Gu (its
  signal trails the gauge by 4-10 d). Operational debias plan: SFDC
  flow-duration-curve mapping of its live forecast onto the retrospective
  climatology (the method from the team's Nepal technical note, June 2026,
  Drive doc 1iORZn8POkhJCNTVdCWicOdP1zfRgjHBkPNseOhuotFw) fitted on the
  2024+ overlap, or forecast-climatology refit as the archive grows. Its votes are calibrated/backtested through its retrospective
  (lead-0 stand-in — it has no reforecast archive), so they carry hindsight;
  its live forecasts run 0.85-0.91x its own retrospective even at lead 1, so
  operational thresholds need a forecast-climatology refit once its archive
  spans a few Deyr seasons.
- **Forecast-vs-own-reanalysis skill** (new report section): GloFAS v4 and
  GRRR are self-consistent at action leads (rank rho >= 0.99, ratio ~1.00 —
  the licence for reanalysis-fitted thresholds); GloFAS drifts to ~0.90x by
  lead 12; no GloFAS **v5** reforecast exists — the single most important
  gap (the v4 proxy misses Shabelle Deyr 2023 at <= 6 d; v5's reanalysis
  flags it clearly).
- **Reforecast backtests**: Juba Gu clean (3/3). Two operational tuning
  items surfaced: Juba Deyr over-fires on the v4 proxy (~1-in-4.4 vs
  calibration 1-in-13), and Shabelle Gu's all-9-pairs consensus is fragile
  on forecasts (misses 2018/2020 operationally).
- **Readiness (7-12 d)** on the leads-8-12 GloFAS reforecast: full
  action-year coverage for three windows; Shabelle Deyr covers 2/4;
  readiness union ~1-in-1.7 (individually 3.1-4.4).

**Open items before a trigger report**: v5 reforecast re-verification;
operational tuning of Juba Deyr and Shabelle Gu (trade N against RP within
the 1-in-4.3 basin budget); GEOGloWS operational debias (SFDC or refit);
version pinning for operations; formal impact cross-check (the report's
year-by-year activation x EM-DAT/CERF table — basin-attributed — is descriptive — an impact
threshold is a working-group decision); final RP adjustment + funding split.

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
