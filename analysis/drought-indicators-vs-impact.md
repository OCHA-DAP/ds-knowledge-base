---
content_type: analysis
name: drought-indicators-vs-impact
analysis_type: exploratory
status: active
country_iso3: [AFG, BFA, ETH, KEN, GTM, HND, SLV, MRT, NER, TCD]
hazard: drought
summary: "Cross-country backtest of the indicators behind our drought triggers (ASAP temperature, rainfall, SPI-3, WSI, zFPARc; ERA5 rainfall; FAO ASI/VHI) against real impact — FAOSTAT staple production anomalies, CERF drought seasons dated via the CERF supplement, EM-DAT — for the ten drought AA framework countries. Pooled: detrended growing-season temperature and FAO ASI/VHI predict production shortfalls best (LOO R² 0.13–0.14), rainfall measures 0.09, ASAP zFPARc 0.02; temperature + ASI 0.19. No framework uses temperature."
data_sources: [ASAP, ERA5, FAO-ASI, FAO-VHI, FAOSTAT, FEWS-NET-FDW, GDHY, CERF, EM-DAT]
feeds: [afg-drought, bfa-drought, eth-drought, ken-drought, lac-dry-corridor, mrt-drought, ner-drought, tcd-drought]
surfaces:
  - {url: "https://ocha-dap.github.io/ds-aa-drought-indicators/", kind: landing, title: "Drought AA indicators — landing page"}
  - {url: "https://ocha-dap.github.io/ds-aa-drought-indicators/indicators-vs-impact/", kind: report, title: "Do temperature, rainfall and vegetation indicators predict drought impact? Cross-country summary with one page per country"}
  - {url: "https://ocha-dap.github.io/ds-aa-drought-indicators/robustness/", kind: report, title: "How robust is the temperature finding? Literature, FEWS NET subnational official yields (8 countries), GDHY cross-check"}
# --- source repo ---
source_repo: ocha-dap/ds-aa-drought-indicators
source_branch: main
source_sha: 594d366
code_ref:
  - scripts/build_tables.py   # per-country season tables (predictors + targets), impact-season dating
  - scripts/analyse.py        # per-country + pooled OLS/LOO/AUC/quadrants
  - scripts/make_site.py      # Pages site (main report)
  - scripts/panel.py          # subnational panel on FEWS NET Data Warehouse official production statistics
  - scripts/gdhy.py           # GDHY gridded-yield cross-check (needs CODAB from blob)
  - scripts/make_robustness.py   # /robustness/ page
  - data/config/countries.json   # seasons, AOI names, staples, framework bad years per country
  - data/config/asap_ids.json    # ASAP export country_id map (see discrepancies)
depends_on: [public.era5, aa.cerf_allocation, aa.cerf_supplement]
discrepancies:
  - "[gap] ASAP's export/rum/export.php country_id is NOT asap0_id (as ds-asap-trends and infrastructure/datasets/jrc-asap.md assume) and not adm0_code: it is the rank of the ISO3 code in ASAP's full GAUL0 list (AFG 1, BFA 17, ETH 61, GTM 79, HND 85, KEN 102, MRT 129, NER 137, SLV 172, TCD 184). A wrong id silently returns a different country. Level 2 is available for BFA, ETH, MRT, NER, TCD, NGA; other countries return a header-only file at level 2. Established by probing ids 1–240; jrc-asap.md and ds-asap-trends should be updated."
  - "[gap] public.era5_temp (prod DB) exists only for ETH and holds precipitation-like values (3–5 in Jun–Sep, r = −0.60 with ASAP temperature); not a temperature table as named. Not used."
  - "[gap] Scale mismatch: targets are national (FAOSTAT) while framework areas are subnational; the test is uninformative where the framework area is a small share of production (ETH, KEN, GTM/HND/SLV). Partly closed by the FEWS NET Data Warehouse subnational panel (robustness page); TCD has no FDW series and HND only a national one to 2009."
  - "[gap] FEWS NET Data Warehouse cropproductionfacts: `Area Harvested` is mostly missing (status 'Missing Historic Data'), so production/area yields are empty — use the reported `Yield` indicator or `Area Planted`; only some unit-years carry an 'All (PS)' production-system row, so filter per unit-year rather than globally (NER otherwise collapses to one year per unit). Guatemala reports production without area; El Salvador changed reporting in 2013; Kenya districts to 2012 then counties."
  - "[gap] GDHY (Iizumi & Sakai 2020) agrees weakly with FAOSTAT in these countries (r ≤ 0.6, several ≈ 0), has no millet/sorghum, and blends NDVI — not usable as an independent yield target here."
extra:
  precedent: "Grew from the Burkina Faso heat-and-impact analysis (frameworks/bfa-drought, Sep 2026)."
  results_pooled_loo_r2: {temperature: 0.13, asi: 0.14, mean_vhi: 0.13, rain_era5: 0.09, spi3: 0.09, wsi: 0.09, rain_chirps: 0.06, zfparc: 0.02, temp_plus_asi: 0.19}
  where_it_works: "MRT (LOO 0.54), AFG (0.38), BFA (0.23), NER (0.11); temperature AUC 0.72–0.80 for impact seasons in BFA/NER/TCD/AFG. Nothing in ETH or the Dry Corridor; rainfall best in KEN."
  robustness: "Literature (Schlenker & Lobell 2010, Lobell et al. 2011, Sultan et al. 2013, Vogel et al. 2019, Lesk et al. 2016) supports temperature ≥ rainfall for African/Sahel crops; VHI contains a temperature condition index, which explains ASI/VHI ≈ temperature. FEWS NET subnational panel (8 countries, ~4,800 unit-years): year-aggregated official statistics reproduce the national ranking in AFG, NER, MRT and (weaker) BFA and agree with FAOSTAT r 0.83–0.90 there; within provinces every indicator is weak (pooled LOYO R² ≤ 0.04, VHI best, temperature 0.02, all signs correct and significant). Inside framework AOIs unit-level skill appears (BFA 4 provinces: WSI 0.25; AFG 5 provinces: ASI 0.33, temperature 0.19). No indicator predicts which province has a bad year."
visibility: public
last_synced: "2026-09-18"
---

# Drought indicators vs impact — analysis

> **Analysis, not a framework.** A cross-country evidence base for trigger design across the drought portfolio.

## What it is
For each of the ten drought AA framework countries: the indicators our triggers use (rainfall, SPI-3, water balance, ASAP cumulative-FPAR biomass) plus growing-season temperature, ERA5 rainfall and FAO ASI/VHI, tested against real outcomes — national staple production (FAOSTAT, % from 2001–2024 trend), CERF drought allocations dated to their deficit season by the CERF supplement, and EM-DAT drought events. Per-country and pooled (within-country standardised) regressions with leave-one-out R², AUC on impact seasons, and hot/low-biomass quadrants. One consistent predictor route: ASAP's per-admin export for all ten countries.

## Findings
- Pooled over 240 country-seasons, detrended temperature (LOO R² 0.13), FAO ASI (0.14) and mean VHI (0.13) predict production shortfalls best; ERA5 rainfall, SPI-3 and WSI 0.09; CHIRPS rainfall 0.06; ASAP zFPARc 0.02 (negative in 8 of 10 countries). Temperature + ASI reaches 0.19 with both coefficients significant.
- Strong in Mauritania, Afghanistan, Burkina Faso and Niger; moderate in Chad and Kenya (rainfall best there); absent in Ethiopia and the Central American Dry Corridor, where national production does not follow the framework area's weather.
- Impact seasons are saturated in ETH/KEN/HND (CERF most years); where sparse, temperature ranks them best (AUC 0.72–0.80 in BFA, NER, TCD, AFG).
- No framework currently uses temperature; a detrended growing-season temperature anomaly belongs in every observational-window candidate set, alongside ASI/VHI.
- Robustness (`/robustness/`): consistent with the peer-reviewed crop-climate literature for Africa and the Sahel. Official subnational statistics (FEWS NET Data Warehouse, 8 countries) reproduce the national ranking once aggregated to the year (AFG, NER, MRT, weaker BFA), but within individual provinces no indicator explains much of official yield variation (pooled leave-one-year-out R² ≤ 0.04); skill reappears inside the small, exposed framework AOIs (BFA, AFG). GDHY gridded yields are too weakly related to FAOSTAT here to serve as an independent check. Evidence for indicator skill is at the scale of a region or country, not a province.

## Relation to frameworks
Feeds all drought frameworks; the Burkina Faso case is worked in full on the `bfa-drought` site (heat-and-drought and heat-and-impact pages). Suggested follow-ups: temperature + ASI backtests for the 2027 revisions of BFA and TCD (both trigger on ASAP zFPARc); subnational production data requests for ETH, KEN and the Dry Corridor.

## Sources & status
Repo `ocha-dap/ds-aa-drought-indicators` (Sep 2026, complete for the ten countries; raw pulls in a scratch dir, processed tables committed under `data/processed/`). Active.
