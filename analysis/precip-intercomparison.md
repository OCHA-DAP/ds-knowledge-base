---
content_type: analysis
name: precip-intercomparison
analysis_type: exploratory
status: active
country_iso3: global
hazard: drought
summary: "Global, land-only, monthly comparison of CHIRPS v2/v3 (with and without stations), IMERG Final and Late, ERA5, the JRC ASAP blend and six gauge analyses on a common 0.5° grid: relative bias, anomaly agreement, triple collocation, dry-tercile agreement and trends, all split by GPCC gauge coverage. Headlines: two-thirds of 50°S–50°N land never had a GPCC gauge in 2001–2020; mean biases are small and the wet end is consistent with gauge undercatch; in gauge-free cells products agree on only ~two-thirds of each other's dry 3-month terciles; ERA5 dries in Africa and arid climates (−5%/decade vs GPCC, −3% vs gauge-free CHIRP v3); CHIRP/CHIRPS v3 have a meridional seam near 72°E in Central/South Asia; IMERG Late has drifted ~6% wetter than Final since 2022 and the team archive holds NASA's corrupted 17 Oct–2 Nov 2024 values."
data_sources: [CHIRPS, CHIRP, IMERG, ERA5, GPCC, CRU-TS, CPC-Unified, PREC-L, UDel, ASAP]
feeds: []
surfaces:
  - {url: "https://ocha-dap.github.io/ds-precip-intercomparison/", kind: landing, title: "Precipitation intercomparison — landing page"}
  - {url: "https://ocha-dap.github.io/ds-precip-intercomparison/report/", kind: report, title: "How much do observed rainfall products disagree? (report + country explorer)"}
# --- source repo ---
source_repo: ocha-dap/ds-precip-intercomparison
source_branch: main
code_ref:
  - "src/products.py — one builder per product: native source -> monthly mm on the common 0.5° grid"
  - "src/grid.py — exact block means for nesting grids; ERA5 (0.25, 0.5, 0.25) kernel for its point-centred grid"
  - "scripts/ingest.py + databricks.yml — Databricks job `Precip Intercomparison Ingest` (1089199811732097, unscheduled) -> dev blob projects/ds-precip-intercomparison/processed/{grid05,aux05}/"
  - "scripts/pack.py, scripts/analyze.py, scripts/figures.py — local analysis; src/metrics.py holds every statistic"
  - "scripts/site_blob.py — generated site outputs parked on dev blob (sha256 manifest), pulled by the Pages workflow"
depends_on: [raster-pipelines, dbx-job-compute]
discrepancies:
  - "[gap] The team's IMERG Late archive (raster/imerg/daily/late/v7) holds NASA's corrupted Early/Late values for 17 Oct – 2 Nov 2024 (daily maxima 1,000–4,000 mm). Masked here (KNOWN_BAD in src/adata.py); see pipelines/raster-pipelines.md."
  - "[gap] ASAP's current CHIRPS version is undocumented; the 'ASAP blend' here follows the published setup (CHIRPS v2 ±50°, ERA5 beyond) and cannot reproduce ASAP's use of ECMWF HRES for the latest days."
  - "[gap] CPC Unified as served by NOAA PSL is missing single days globally in several months (1981–1992 outside the Americas, Feb 2007); months with ≤2 missing days are scaled, 1983 and 1985 still have whole months missing outside the Americas."
  - "[gap] Triple-collocation partners are never perfectly independent (CHIRPS and IMERG Late share infrared inputs; CHIRP climatology uses GPCC station normals) — treat TC differences of a few hundredths as ties."
extra:
  reference: "GPCC Full Data Monthly v2022 (ends 2020-12), stratified by share of months 2001–2020 with >=1 gauge in the cell; no ensemble-median reference (most products share GPCC/GHCN stations)"
  windows: "bias/agreement 2001–2020 (UDel 2001–2017); trends 1983–2020 and 2001–2025"
  common_domain: "37,529 0.5° land cells, 50°S–50°N (76% of non-Antarctic land)"
  blob: "dev projects/ds-precip-intercomparison/processed/grid05/<product>.nc (0.5°, mm/month, global, 1981-) — reusable by other analyses; CRU TS is ODbL, do not redistribute"
visibility: public
last_synced: "2026-10-02"
---

# Observed precipitation products compared — analysis

> **Analysis, not a framework.** A global reference comparison of the rainfall products our triggers
> read, so product choices in frameworks can cite evidence rather than habit.

## What it is

Thirteen observed products plus the JRC ASAP blend, regridded to one 0.5° monthly grid and compared over
land: CHIRPS v2.0 and v3.0 and their station-free CHIRP versions, IMERG V07 Final (monthly) and Late (the
team's operational daily archive, summed), ERA5, GPCC Full Data and Monitoring, CRU TS 4.10, CPC Unified,
PREC/L and UDel. Every statistic is also split by how often the cell had a GPCC gauge in 2001–2020 (never /
<50% / ≥50% of months), because in gauge-free cells the gauge "reference" is itself an interpolation.

Methods were reviewed before and after the run (Fable): ratio-of-sums bias with dry cells excluded,
Spearman on standardised anomalies, extended triple collocation, dry-tercile Peirce skill (own and
reference climatology), Sen + autocorrelation-corrected Mann–Kendall with Benjamini–Hochberg FDR, and
trends of *difference* series (A − B) to isolate product artefacts from shared climate signal.

## Findings (2001–2020 over the common domain unless stated)

- **Gauges:** 66% of the common domain never had a GPCC gauge in 2001–2020. GPCC Full Data v2022 counts
  ~52k gauges/month in 1986 and ~12k in 2020 — partly real decline, partly delivery latency that later
  GPCC versions will fill.
- **Bias vs GPCC:** CHIRPS v2 +2%, IMERG Late +4%, IMERG Final +5%, CHIRPS v3 +8%, ERA5 +8%; gauge analyses
  within ±2% except **CPC −14% (Africa −23%)**. With gauge products lifted by Legates–Willmott, CHIRPS v3 /
  ERA5 / IMERG Final sit at 1.01 / 1.02 / 0.99 (CHIRPS v2 0.96) — the wet end is *consistent with* gauge
  undercatch; CHIRPS v3/v2 rises with the factor (1.02 → 1.28; cell-level r only 0.28).
- **Regional:** ERA5 +15% Asia, +20% cold climates, +27% poleward of 50°N, −16% Sahel (10–18°N), ~⅓ of GPCC
  on the Sahara's southern margin.
- **Anomalies:** agreement collapses in Africa (Spearman vs GPCC 0.42–0.56 for CHIRPS, ERA5, IMERG Late, CRU,
  PREC/L; 0.77–0.89 in Europe). Triple collocation ranks CHIRPS v3/v2, IMERG Final and ERA5 (ρ² 0.59–0.73)
  above gauge-only analyses (GPCC 0.34, CRU 0.24) in Africa, the reverse in Europe. CHIRP is weak everywhere
  (ρ² ≈ 0.35).
- **Dry terciles (3-month, the AA view), vs GPCC:** hit rate / false-alarm *ratio* (share of the product's dry
  calls GPCC doesn't call dry): IMERG Final 79% / 19%, CHIRPS v2 69% / 29%, ERA5 66% / 32%, IMERG Late
  62% / 36%; in Africa hits 51–56% and false-alarm ratios 35–41% for CHIRPS v2, ERA5, IMERG Late. Two
  gauge-independent products in never-gauged cells (CHIRPS v2 vs ERA5, PSS 0.46) agree on ~2 of 3 dry seasons.
- **Trends 1983–2020:** −1.7 (CHIRP v3) to +1.8%/decade (CHIRP v2) — the two station-free satellite products
  disagree by 3.5 points; ≥80% of the 11 independent products agree on the sign over 46% of the area.
  **ERA5 dries in Africa and arid climates** (−5.3%/decade vs GPCC, −3.3% vs gauge-free CHIRP v3 — an ERA5
  drift there); globally ERA5 − GPCC and CHIRP v3 − GPCC are both −2.3%, ambiguous (could be GPCC wetting).
  **CHIRPS v2 wets vs GPCC** (+1.2%/decade) from its satellite part. **CHIRPS v3's stations add +1.8%/decade
  to CHIRP v3**, matching GPCC. **CHIRP/CHIRPS v3 have a meridional seam near 72°E** in Central/South Asia
  (drying band 64–72°E, wetting either side, absent from ERA5/CRU — from CHIRP v3's satellite inputs, cause
  unknown). **CPC is unstable** (vs GPCC +5.6% Asia, −5.2% South America). The 7% of the area gauged every year
  shows a GPCC trend similar to all cells.
- **IMERG Late (operational):** triple-collocation ρ² 0.61 vs Final 0.85; dry-tercile PSS 0.42 vs 0.68;
  Late/Final 1.00 for 2001–2021, 1.05 for 2022–2025.

## Relation to frameworks

Standalone reference. Directly relevant to every framework that triggers on CHIRPS, IMERG Late or ERA5
rainfall (drought SPI/tercile triggers, IMERG flood/cyclone observational triggers) and to the ROSEA
pipeline via ASAP (whose rainfall is CHIRPS v2 within ±50°). The 0.5° cubes on the dev blob are reusable
for country backtests.

## Sources & status

Repo `OCHA-DAP/ds-precip-intercomparison` (public). Ingest ran 2026-10-02 on Databricks (job
1089199811732097, unscheduled; re-run with `databricks bundle run precip_ingest -t prod -p default`).
Analysis is a point-in-time run; refresh = re-run the job, `scripts/pack.py`, `analyze.py`, `figures.py`,
`site_blob.py upload`, then dispatch the Pages workflow.
