---
content_type: analysis
name: external-aa-frameworks-review
analysis_type: regional-overview   # exploratory | ad-hoc-activation | pre-framework | regional-overview
status: active
country_iso3: [MOZ, ZWE, MWI, MDG, LSO]
hazard: drought
summary: "Independent review of the WFP/FAO Southern Africa drought AA triggers proposed for the CERF El Niño 2026/27 harmonisation: recovers the activation records behind the agencies' stated return periods from public endpoints (PRISM operational trigger CSVs, IRI fbfmaproom2 hindcast API), computes Weibull RPs, and publishes a password-protected review site."
data_sources: [ECMWF, PyCPT]
feeds: []   # supports the CERF El Niño 2026/27 trigger-harmonisation discussion; no OCHA framework page exists yet for it
# --- source repo ---
source_repo: ocha-dap/ds-external-aa-frameworks
source_branch: main
source_sha: 756b37a
code_ref:
  - scripts/fetch.py
  - scripts/analyze.py
  - scripts/build_site.py
depends_on: []
discrepancies:
  - "[external-frameworks/wfp/mdg-drought.md] attributes the ~55% composite trigger score to WFP; the July 2026 FAO-WFP overview file puts the composite under FAO and gives WFP a PyCPT probability-of-non-exceedance trigger (25%/35% tiers) — the joint WFP-FAO national mechanism appears conflated on the KB page. Not yet corrected."
  - "[gap] No external-frameworks/wfp/mwi-drought.md page exists; the July 2026 file plus the PRISM Malawi trigger CSV recovered here now provide enough material to write it."
extra:
  review_site: "https://ocha-dap.github.io/ds-external-aa-frameworks/ (staticrypt; password shared internally — same as the ds-aa-tracking review site)"
  source_file: "'FAO-WFP AA Overview for Southern Africa' xlsx, July 2026 (internal, not committed anywhere): WFP + FAO trigger sheets and a proposed CERF alignment matrix of harmonised SPI-3 triggers."
visibility: internal
last_synced: "2026-08-10"
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
SPI-3-based triggers for CERF adoption. Two public source families make this
independently checkable:

- **PRISM operational trigger CSVs** (public S3; URLs found in the open-source
  `WFP-VAM/prism-app` frontend config): per district × index × severity × window
  trigger thresholds *and* issued forecast probabilities, seasons 2023-24 onward
  (MOZ, ZWE, MWI). Applying the Ready/Set double-confirmation logic yields the
  realized activation record.
- **IRI fbfmaproom2 export API** (the backend of the WFP "AA Design Dashboard"
  maprooms): full hindcasts of forecast probability vs design threshold and
  "bad years", with skill counts — Lesotho 1983–2026, Madagascar 1992–2025.

Findings are published on a **staticrypt-protected review site** (one landing page +
one page per framework): see `extra.review_site`. Headlines: the stated RPs are
mostly honest as *event* frequencies (maproom hindcast Weibull RPs match their
labels) but Malawi's operational thresholds contradict its 1-in-4 label outright
(20 of 60 rows have trigger = 0.00; fired every recorded season); framework-level
(any-district) activation is far more frequent than any per-district label
(Mozambique's Moderate tier fired districts in all three complete seasons, including
La Niña 2024-25); measured forecast skill is weak where checkable (Madagascar 35%
tier: 3 worthy actions vs 8 acts-in-vain, 1992–2025); and the 2026/27 triggers had
**already fired** in Mozambique (21 districts Moderate / 24 Severe, W1), Zimbabwe
(all 18 districts) and Lesotho (highest forecast probability in the 44-year record,
all three tiers breached) by August 2026 — so climatological RPs understate expected
disbursement for this El Niño-conditioned appeal.

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

## Sources & status

**Repo**: `ocha-dap/ds-external-aa-frameworks` @ `main`. Fetched data and the built
site are regenerable (`data/`, `site_build/` not committed); the encrypted site is
committed under `docs/` and served by GitHub Pages. The internal July 2026 xlsx is
not committed anywhere. One-off analysis (no schedule); re-run the three scripts to
refresh after new forecast issues.
