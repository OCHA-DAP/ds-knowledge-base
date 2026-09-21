---
content_type: analysis
name: external-aa-frameworks-review
analysis_type: regional-overview   # exploratory | ad-hoc-activation | pre-framework | regional-overview
status: active
country_iso3: [MOZ, ZWE, MWI, MDG, LSO]
hazard: drought
summary: "Independent review of the WFP/FAO Southern Africa drought AA triggers proposed for the CERF El Niño 2026/27 harmonisation: recovers the activation records behind the agencies' stated return periods from public endpoints (PRISM operational trigger CSVs, IRI fbfmaproom2 hindcast API), computes Weibull RPs and trend-split RPs, cross-checks triggers and 2026/27 forecasts against ERA5/SEAS5 (detrended, from the team rasterstats DB), and publishes a password-protected review site."
data_sources: [ECMWF, PyCPT]
feeds: []   # supports the CERF El Niño 2026/27 trigger-harmonisation discussion; no OCHA framework page exists yet for it
surfaces:
  - {url: "https://ocha-dap.github.io/ds-external-aa-frameworks/", kind: dashboard, title: "External AA frameworks review site (staticrypt; password shared internally, same as ds-aa-tracking)", access: password}
# --- source repo ---
source_repo: ocha-dap/ds-external-aa-frameworks
source_branch: main
source_sha: 1460d33
code_ref:
  - scripts/fetch.py
  - scripts/analyze.py
  - scripts/fetch_met.py
  - scripts/analyze_met.py
  - scripts/plots.py
  - scripts/build_site.py
depends_on: [raster-stats]   # met check reads public.era5/public.seas5 zonal stats (prod rasterstats DB)
discrepancies:
  - "[external-frameworks/wfp/mdg-drought.md] attributes the ~55% composite trigger score to WFP; the July 2026 FAO-WFP overview file puts the composite under FAO and gives WFP a PyCPT probability-of-non-exceedance trigger (25%/35% tiers) — the joint WFP-FAO national mechanism appears conflated on the KB page. Not yet corrected."
  - "[gap] No external-frameworks/wfp/mwi-drought.md page exists; the July 2026 file plus the PRISM Malawi trigger CSV recovered here now provide enough material to write it. Any such page must note: WFP Malawi runs operationally on PRISM/ECMWF (TSP WFP HQ APP-GRS); the public `malawi` fbfmaproom is the LEGACY IRI/WFP FbF-phase design tool (NMME-based pnep, DJF target season, hindcast ends ~2022) — not the operational system and not FAO/DCCMS's composite."
extra:
  source_file: "'FAO-WFP AA Overview for Southern Africa' xlsx, July 2026 (internal, not committed anywhere): WFP + FAO trigger sheets and a proposed CERF alignment matrix of harmonised SPI-3 triggers."
  trigger_logic_verified: "PRISM Ready/Set logic verified against WFP-VAM/prism-app source (strict >, one CSV row = a consecutive-month Ready/Set pair); fbfmaproom 'worst' flag verified against iridl/python-maprooms source (rank-based — full-record trigger frequency equals the tier label by construction, and it is a single-issue-month quantity)."
visibility: internal
last_synced: "2026-08-28"
---

# External AA frameworks review — Southern Africa drought (analysis)

> **Analysis, not a framework.** Reviews *other orgs'* (WFP, FAO) drought AA triggers
> across five Southern Africa countries ahead of the CERF El Niño 2026/27
> harmonisation exercise. The per-org/country baseline pages live under
> `external-frameworks/`; this page holds the comparative/verification layer.

## What it is

`ds-external-aa-frameworks` recovers the trigger and activation records that back the
return periods WFP and FAO state for their Southern Africa drought AA frameworks
(Mozambique, Zimbabwe, Malawi, Madagascar, Lesotho), as compiled in the internal
July 2026 "FAO-WFP AA Overview for Southern Africa" file proposing harmonised
SPI-3-based triggers for CERF adoption. Findings are published on a
**staticrypt-protected review site** (landing page + one page per framework): see
`extra.review_site`.

Data sources, all public or team-internal:

- **PRISM operational trigger CSVs** (public S3; URLs found in the open-source
  `WFP-VAM/prism-app` frontend config): per district × index × severity × window
  trigger thresholds *and* issued forecast probabilities, seasons 2023-24 onward
  (MOZ, ZWE, MWI). The Ready/Set double-confirmation logic was verified against the
  frontend source (strict `>`; each row pairs consecutive monthly issues), giving
  the realized activation record.
- **IRI fbfmaproom2 export API** (backend of the WFP "AA Design Dashboard"
  maprooms): full hindcasts of forecast probability vs design threshold and
  "bad years", with skill counts — Lesotho 1983–2026 and Madagascar 1992–2025
  (both current WFP PyCPT-era design tools), plus the **legacy** Malawi maproom
  (see below). National and district/region-level pulls.
- **ERA5 / SEAS5 zonal stats** from the team rasterstats DB (`public.era5`,
  `public.seas5`), over each framework's target adm1 regions, for the independent
  meteorological cross-check.

## Headline findings (as of Aug 2026)

- **Frequency labels are mostly honest as event frequencies, but framework-level
  activation is far more frequent.** Maproom hindcast Weibull RPs match their tier
  labels *by construction* (the flag is rank-based). Mozambique's Moderate tier
  fired districts in every recorded operational season, including La Niña 2024-25.
- **Malawi's PRISM operational config contradicts its 1-in-4 label**: 20 of 60 rows
  carry a trigger threshold of exactly 0.00, only 5 districts are covered (file
  says 12), and it fired nearly everywhere every season.
- **Non-stationarity**: the maproom forecast-probability series trend upward against
  fixed full-record percentile thresholds — Lesotho's action tier ran RP 11.5 over
  1983–2004 vs **2.2** since 2005; recent-decades activation frequency is roughly
  twice the advertised label for LSO/MWI.
- **2026/27 triggers had already fired by Aug 2026** (MOZ 21 districts Moderate /
  22 Severe double-confirmed W1; ZWE all 18; LSO all three tiers at the highest
  probability in its 44-year record), and the independent SEAS5 check corroborates:
  detrended Aug-2026 seasonal forecasts are ~1-in-6 (MOZ, ZWE) to ~1-in-15 (LSO)
  dry-forecast events, and **driest in the 46-year forecast record for both the
  Grand Sud and Southern Malawi** — rarer in every case than the trigger tiers.
- **Skill is the weak link.** All skill numbers detrended (ds-seas5-skill method:
  log1p + linear trend fitted on hist years, applied to all incl. 2026). SEAS5 vs
  ERA5 over target regions: Spearman r 0.26–0.37. Providers' own hindcast series:
  Lesotho PyCPT r 0.26 (its raw 0.38 was substantially trend inflation — below
  SEAS5), Madagascar 0.14–0.19 per Grand Sud region (national series is
  *negatively* correlated with Grand Sud outcomes — wet-north aggregation
  artifact), and historically MDG's triggered years sat at a **median 84th ERA5
  percentile** in the Grand Sud (wetter than average; the real droughts 2015/2019/
  2020 went untriggered). MOZ/ZWE publish no hindcast series to score.
- **Malawi maproom attribution (corrected 2026-08-26)**: the public `malawi`
  fbfmaproom is the legacy IRI/WFP FbF-phase design tool — NMME-based pnep, DJF
  target season (per the fbfmaproom config), hindcast ends ~2022; **not** WFP's
  operational system (PRISM/ECMWF) and **not** FAO/DCCMS's multi-indicator
  composite. On its own DJF design season its detrended skill is negative
  (r = −0.16). It is kept in the review as the only long public Malawi trigger
  hindcast.

## Relation to external-frameworks pages

Baseline (web-sourced) descriptions of the same frameworks:
[wfp/moz-drought](../external-frameworks/wfp/moz-drought.md) ·
[wfp/zwe-drought](../external-frameworks/wfp/zwe-drought.md) ·
[wfp/mdg-drought](../external-frameworks/wfp/mdg-drought.md) ·
[wfp/lso-drought](../external-frameworks/wfp/lso-drought.md) ·
[fao/moz-drought](../external-frameworks/fao/moz-drought.md) ·
[fao/zwe-drought](../external-frameworks/fao/zwe-drought.md) ·
[fao/mwi-drought](../external-frameworks/fao/mwi-drought.md) ·
[fao/mdg-drought](../external-frameworks/fao/mdg-drought.md).
This analysis adds numeric thresholds and activation records several of those pages
flag as publicly unavailable (`schema_strain`), and surfaces two KB fixes (see
`discrepancies`): the wfp/mdg-drought composite-trigger conflation, and the missing
wfp/mwi-drought page.

## Open items

- Request from WFP/IRI: per-district hindcast activation tables and the actual
  per-district/month probability cutoffs (the summary skill ranges in the July 2026
  file are per-metric envelopes and internally inconsistent — not jointly usable);
  confirmation of operational maproom issue months (our pulls are best guesses).
- CHIRPS empirical check of the SPI-percentile↔RP claims in the CERF matrix
  (semi-arid zero-inflation makes Φ-table arithmetic suspect in Gaza/Grand Sud).
- CERF-matrix design gaps that block any framework-level RP quote: spatial
  aggregation rule, observation-vs-forecast basis of the harmonised SPI-3 trigger,
  readiness tiers kept or dropped, all-in vs split funding structure. Lesotho is
  absent from the matrix entirely — in scope or not?

## Sources & status

**Repo**: `ocha-dap/ds-external-aa-frameworks` @ `main` (`1460d33`). Fetched data
and the built site are regenerable (`data/`, `site_build/` not committed; the met
scripts need prod rasterstats DB env vars); the encrypted site is committed under
`docs/` and served by GitHub Pages. The internal July 2026 xlsx is not committed
anywhere. One-off analysis (no schedule); re-run the six scripts to refresh after
new forecast issues.
