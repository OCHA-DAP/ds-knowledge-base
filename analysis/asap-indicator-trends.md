---
content_type: analysis
name: asap-indicator-trends
analysis_type: exploratory
status: active
country_iso3: SSD             # South Sudan first; the ASAP export is per-country, so extending is one config entry
hazard: drought
summary: "Tests whether long-term trends in the JRC ASAP indicators have made ASAP's fixed −1 z-score warning threshold harder to reach. For South Sudan: zFPARc on rangeland rose ~0.5 z/decade and its threshold-breach rate fell from 15.5% to 1.1% of in-season dekads, while SPI-3 and WSI show no significant trend — so the drift is on the biomass side of the warning classification, not the rainfall side."
data_sources: [ASAP]
feeds: []
surfaces:
  - {url: "https://ocha-dap.github.io/ds-asap-trends/", kind: report, title: "ASAP indicator trends results site (refreshed monthly by GHA)"}
# --- source repo ---
source_repo: ocha-dap/ds-asap-trends
source_branch: main
code_ref:
  - "src/asap.py — client for ASAP's undocumented per-admin indicator-statistics export"
  - "src/trends.py — Theil-Sen + Mann-Kendall on seasonally aggregated series; derived z-scores"
  - "scripts/download.py, scripts/analyze.py — fetch and analysis entry points"
  - "docs/index.html — GitHub Pages results site"
depends_on: []                # reads ASAP directly; no team blob/DB dependency
discrepancies:
  - "[conflict] The ASAP download page's tooltip describes variable_id 160/170 as 'zWSI — [Anomaly] Z-score of the Water Satisfaction Index', but the export returns raw WSI on a 0–100% scale (the CSV's own variable_name comes back as 'Water Satisfaction Index (WSI)'). The z-scored WSI the warning classification thresholds is not downloadable. This repo derives its own z-score for WSI; the docs are wrong, the data is what it is."
  - "[gap] The breach share reported here is a proxy, not a warning count. ASAP requires the threshold over ≥25% of a unit's active *area* — a within-unit spatial criterion the published unit means cannot reproduce. Direction is reliable; absolute warning counts are not derivable from these statistics."
  - "[gap] Soil moisture is excluded from interpretation: ASAP gapfills it only to dekad 2023-12-21 and continues un-gapfilled after, and the series steps down at exactly that cutover (mean z −0.58 after vs +0.06 before). Its apparent decline mixes a methodology change with any real signal."
  - "[gap] Trend attribution is open. zFPARc rising while SPI-3 is flat rules out rainfall as the driver, but does not distinguish cropland expansion, intensification, and MODIS sensor history. Not resolvable from ASAP statistics alone."
  - "[gap] The national figures quoted here are an UNWEIGHTED mean across the 10 GAUL1 units, not area-weighted (ds-asap-trends issue #1). Defensible for the breach-rate framing — ASAP warns per unit, so 'the average unit' is the right frame — but not for national-conditions statements. The trend finding is robust to it (all 10 units +0.23 to +0.65 z/decade, 10/10 significant, so no non-negative weighting changes it); current-season national values are NOT (WSI cropland spans −2.79 to +0.64 across units at the same dekad). Correct weight would be cropland/rangeland area per unit, never admin polygon area; no ASAP tabular product carries it, so it needs zonal stats over the area-fraction mask rasters."
extra: {}
visibility: public
last_synced: "2026-07-31"
---

# ASAP indicator trends — is the warning threshold drifting?

## The question

ASAP issues an automatic agricultural-drought warning when an indicator's z-score falls
below **−1** over ≥25% of a unit's active area. Those z-scores are normalized against the
**full historical record** (see
[infrastructure/datasets/jrc-asap.md](../infrastructure/datasets/jrc-asap.md#alert-thresholds)).

So if an indicator carries a genuine long-term trend, the z-score drifts along with it, and
a year that would have breached −1 early in the record sits comfortably above −1 today on
identical physical conditions. The threshold silently becomes harder to reach. That is a
**stationarity assumption inside an operational trigger**, and this analysis tests whether
it holds.

Relevant because ASAP warning level feeds the ROSEA slow-onset alert level
([pipelines/rosea-thresholds-monitoring.md](../pipelines/rosea-thresholds-monitoring.md),
where country level = MAX of ASAP and IPC), so drift in ASAP propagates.

## What was analysed

South Sudan, ASAP GAUL level 1 (10 units), dekadal statistics 1989/2001 → present, pulled
straight from ASAP's indicator-statistics export. Eleven indicators: the warning drivers
(zFPARc, WSI, SPI-3 for both cropland and rangeland) plus context (FPAR, zFPAR, rainfall,
temperature, soil moisture).

Method: collapse each dekadal series to one value per unit-year (in-season dekads only,
keeping seasonal mean, seasonal minimum, and the share of dekads under −1), then
**Theil-Sen** slope + **Mann-Kendall** significance on the annual series. Trends are
reported over a common 2001+ window, since the records start at different dates. WSI and
the other raw variables are z-scored here against each unit's own per-dekad climatology,
mirroring ASAP's own normalization — necessary because ASAP does not publish zWSI.

## Findings

| Indicator | z / decade | p | Breach 2001–05 | Breach 2022–26 |
|---|---|---|---|---|
| **zFPARc rangeland** | **+0.50** | <0.001 | **15.5%** | **1.1%** |
| zFPARc cropland | +0.20 | 0.008 | 8.5% | 6.9% |
| SPI-3 rangeland | +0.12 | 0.36 (n.s.) | 19.5% | 8.4% |
| SPI-3 cropland | +0.08 | 0.60 (n.s.) | 20.3% | 9.9% |
| WSI rangeland | +0.07 | 0.51 (n.s.) | 21.2% | 19.8% |
| WSI cropland | +0.05 | 0.76 (n.s.) | 20.2% | 17.2% |
| *(context)* temperature | +0.37 | <0.001 | — | — |

(National figures are an **unweighted** mean across the 10 GAUL1 units — see the last
`discrepancies` entry for when that matters and when it doesn't.)

- **The biomass indicator has drifted a lot.** zFPARc on rangeland rose **+0.50 z per
  decade** (p < 1e-6), a total shift of **+1.24 z** across 2001–2026. Its threshold-breach
  rate fell from 15.5% of in-season dekads to **1.1%** — a ~93% relative fall. Every one of
  the 10 units shows a positive slope (+0.23 to +0.65).
- **The water-balance and rainfall drivers have not.** SPI-3 and WSI show no significant
  trend in either landcover. Rainfall itself is flat (+0.02 z/decade, p = 0.73).
- **So the drift is specific to the biomass side of the classification.** Warning levels
  that depend on cumulative-FPAR evidence (levels 2, 3 and 4) are getting substantially
  harder to trigger; the water-balance level-1 warnings are not. That asymmetry matters
  more than either number alone — it means the *mix* of warning levels ASAP issues has
  shifted, not just their frequency.
- Temperature is warming as expected (+0.37 z/decade) but is not a warning driver.

## Current-season view

A second question the same data answers: **how is the current season tracking**. A seasonal
aggregate cannot answer it, because the current year's covers only the dekads elapsed so far
and is therefore not comparable to a complete year. So the site also compares the current
year against every prior year **at the same dekad** — a season-progression chart against the
prior-year 10th–90th percentile envelope, a dekad selector that pins the year-over-year
chart to one dekad, and a per-admin-unit view at that dekad.

Illustrative of why the drift matters operationally (2026, dekad 20 = Jul 11–20): zFPARc
rangeland was the **2nd highest of 26 years** nationally, while SPI-3 cropland in Jonglei was
the **7th lowest of 38** with **2 of 10 units already at or below −1** (El Buheyrat −1.47,
C. Equatoria −1.46). The rainfall deficit was real and the biomass indicator masked it —
which is exactly the failure mode the drift creates.

## Caveats

Read the `discrepancies` frontmatter — five of them matter for interpretation. Briefly: the
breach share is a proxy rather than a warning count; soil moisture is unusable because of
ASAP's 2023-12-21 gapfill cutover; a rising FPAR trend does not distinguish greening from
land-use change from sensor history (only that it isn't rainfall, since SPI-3 is flat); and
the national figures are an unweighted mean of units, which the trend conclusion survives but
current-season national values do not.

Also note p-values are mildly optimistic — annual aggregation removes within-season
autocorrelation but not year-to-year persistence.

## Where it lives

- Code + method detail: [`OCHA-DAP/ds-asap-trends`](https://github.com/OCHA-DAP/ds-asap-trends)
- Results site: <https://ocha-dap.github.io/ds-asap-trends/> (GitHub Pages, refreshed monthly by GHA)
- Endpoint documentation and its gotchas:
  [infrastructure/datasets/jrc-asap.md](../infrastructure/datasets/jrc-asap.md#indicator-statistics--the-raw-numbers-behind-the-warnings)
