---
content_type: pipeline
name: hnrp-mirror
type: ingest
status: live
source_repo: OCHA-DAP/ds-hnrp-mirror
deployment:
  platform: github-actions
  resource_group: null
  jobs:
    - { name: "refresh-hnrp", ref: ".github/workflows/refresh-hnrp.yml", schedule: "daily 04:17 UTC (recent years) + Sun 02:47 UTC (full backfill)", status: live }
    - { name: "deploy-site", ref: ".github/workflows/deploy-site.yml", schedule: "on workflow_run(refresh-hnrp) + daily 08:00 UTC backstop", status: live }
inputs:
  - "HPC API: https://api.hpc.tools /v2/public/plan?year=Y + /v1/public/plan/id/{id}?content=measurements (plan metadata, plan/cluster caseloads, requirements; no auth)"
  - "FTS: https://api.hpc.tools/v1/public/fts/flow?planid={id}&groupby=plan (funding totals per plan)"
  - "HDX HAPI: https://hapi.humdata.org/api/v2/affected-people/humanitarian-needs (PiN to admin-2 by sector/category/status, Global HNO, 2024+; needs HAPI_APP_IDENTIFIER)"
  - "HDX global-hpc-hno CSVs (admin-3 PiN rows HAPI truncates: BFA/COD/MMR)"
  - "HDX per-country *-jiaf-humanitarian-needs-* workbooks (~20 country offices — JIAF intersectoral final severity 1-5 AND overall PiN (WS-3.1), 2025+; localized EN/FR/ES templates; newest resource per country-year wins)"
outputs:
  - "DB table: hpc.plans (dev — one row per plan: metadata, requirements, FTS funding, plan-level PiN/target/population; PK plan_id; all years 2004+)"
  - "DB table: hpc.plan_caseloads (dev — cluster-level PiN/target/reached/requirements; PK (plan_id, entity_id))"
  - "DB table: hpc.needs_admin (dev — HAPI + Global HNO adm3, admin 0–3 × sector × category × population_status; full replace each refresh, ~950k rows)"
  - "DB table: hpc.severity_admin (dev — JIAF final severity 1–5 per admin area × population group; admin-3 where published (BFA/COD/SYR); full replace, ~8k rows)"
  - "DB table: hpc.pin_admin (dev — JIAF overall PiN, preliminary + final, per admin area × population group; final_severity = WS-3.2 severity joined at refresh, severity = the PiN sheet's own (untrusted) column; PBS = final_pin by COALESCE(final_severity, severity); full replace, ~11k rows, 37 country-years)"
  - "GitHub Pages explorer: https://ocha-dap.github.io/ds-hnrp-mirror/ (Plans / Admin-level PiN / Severity / PiN × severity tabs, CSV download; site/data/*.json regenerated each deploy)"
dependencies:
  - "ocha-stratus (DB engine; STAGE env selects dev/prod, currently dev)"
  - "DSCI_AZ_DB_DEV_HOST / _UID / _PW (read — site export; OCHA-DAP org-level Actions secrets, no per-repo setup)"
  - "DSCI_AZ_DB_DEV_UID_WRITE / _PW_WRITE (write — refresh jobs; org-level secrets)"
  - "HAPI_APP_IDENTIFIER (repo secret; base64 of app-name:email, no registration)"
  - "PGSSLMODE=require (Azure Postgres SSL)"
last_verified: 2026-07-28
---

# HNRP / PiN mirror

Mirrors OCHA **HNRP/HRP plan data and People in Need** figures into the dev DB
(schema `hpc`) and publishes a
[GitHub Pages explorer](https://ocha-dap.github.io/ds-hnrp-mirror/).

Two granularity tiers, deliberately split by source:

- **HPC API + FTS** — plan- and cluster-level (PiN, targeted, reached,
  requirements, funding) for **all plan years** (plans 2004+, caseloads ~2017+).
  Daily refresh covers current/previous/next plan years (funding moves
  continuously); the Sunday run re-walks all years.
- **HDX HAPI** (`affected-people/humanitarian-needs`, the Global HNO dataset) —
  the most granular *standardized* public PiN: **admin-2** × sector × age/gender
  category × population status, 2024+ for ~24 HNRP countries. Full-replace
  mirror with a row-count guard (refuses to wipe on a partial pull). Supplemented
  with **admin-3** rows from the `global-hpc-hno` CSVs (BFA/COD/MMR) that HAPI
  truncates — the CSVs lag HAPI within the current cycle, so HAPI stays primary.
- **JIAF severity + overall PiN** (`hpc.severity_admin`, `hpc.pin_admin`) —
  from per-country `*-jiaf-humanitarian-needs-*` workbooks, 2025+:
  intersectoral **final severity (1–5)** (WS-3.2 / "Severity" sheet) and
  intersectoral **overall PiN, preliminary + final** (WS-3.1 / "PiN" sheet),
  both per admin area × population group. Country offices localize the JIAF
  2.0 template (EN/FR/ES, renamed sheets), so parsing is anchor-based
  (`src/jiaf.py`); unparseable workbooks are logged in the Actions run, never
  silently dropped (currently: UKR ×2, SYR 2026, YEM 2025 publish no severity
  sheet; only UKR 2026 publishes no admin-level PiN — macro-zones only). Per
  country-year the **newest HDX resource wins**, so revised re-uploads
  ("[Revised] DRC ... 2026") supersede the original for both tables.
  **Admin depth**: admin-2 for most countries; admin-3 for COD (zones de
  santé), SYR (sub-districts) and BFA 2025 (communes; BFA 2026 dropped back
  to admin-2). No workbook publishes admin-4.

## Gotchas

- Join key is **`plan_id`** (HPC); plan codes/names change between versions.
- HAPI category rows **overlap** (Total / Adult / by-gender…) — filter, never
  sum across categories: `category='total'` exactly (231 other values are
  sex/age/group breakdowns of the same people).
- **JIAF classifies AREAS, it does not count people per class.** Every finest
  unit (× population group) in `hpc.severity_admin` carries exactly ONE
  `final_severity` and that unit's population (verified across all 8,108 units,
  2026-07). Any "population in severity N" figure derived from this table is
  really *the population of areas classified N* — label it that way. Per-class
  headcounts do not exist in this table; for **PiN by severity class** use
  `hpc.pin_admin` (final PiN grouped by the unit's severity — still
  area-classified, but PiN headcounts rather than area populations). PiN
  (`needs_admin`, `INN`) remains the plan's authoritative people-level caseload
  and is NOT derivable from severity.
- **How PiN is calculated (JIAF 2.0 "Mosaic Method")**: each sector estimates
  its own PiN per finest analysis unit; intersectoral PiN takes the *highest*
  sectoral PiN per unit (**core sectors only** — the template formula ranges
  over CCCM…WASH, so Protection AoRs CP/GBV/Mine Action/HLP never drive the
  overall PiN or the intersectoral severity) and sums those maxima upward,
  then validation workshops
  resolve flags by consensus. Consequences: (a) intersectoral < sum(sectors)
  always — never sum sector PiNs; (b) sectoral arithmetic won't reproduce the
  intersectoral exactly (TCD 2025: 73% of admin-2 units equal max(sector); SDN 0%
  equal but 98% ≥ — the mosaic ran at a finer unit); (c) from HPC 2026 overall
  PiN counts only areas in intersectoral severity 3+ (2025-cycle PiN can include
  class-1/2 areas).
- **PiN-by-severity (PBS) is now mirrored** (`hpc.pin_admin`, added
  2026-07-28) — definition, tool mechanics and sources in the dedicated
  section below. NOTE the sector × severity "PiN par gravité" sheet the CAR
  analysis used (analysis/jiaf-pbs-analysis) is **not in any HDX-published
  workbook** — that was an internal workbook hand-uploaded to blob; per-sector
  distributions (and the six-method collapse question) only return if such
  sheets ever get published.
- **`pin_admin` quirks** (mirrored as-is from the sheets): the `severity`
  column is untrusted — see the PBS section for the failure modes (SSD 2026
  pasted constant; LBN 2026 blank-pcode ID collapse) and use `final_severity`
  (the WS-3.2 join the refresh now performs); NGA 2025 publishes preliminary
  PiN only (final column empty); national sums can differ from
  `hpc.plans.in_need` (workbook vs HPC-reconciled figures; some workbooks
  track refugees in a separate column).
- **One sector_code, several named series.** Within a single reference period a
  sector code can carry multiple `sector_name` series ("Protection (total)" AND
  "General Protection", both `PRO`, both `category='total'`) — summing across
  them double-counts (MMR PRO 2024 sums to 2.18× its published admin-1 total).
  Names also mutate BETWEEN cycles (COD: "Final HRP Caseload" 2024 vs "…caseload"
  2025) — pick one series per (country, sector, reference period), never
  globally.
- **Prefer the coarsest published admin level.** Where a country publishes the
  same series at admin-1 and finer, the admin-1 figures equal the finer sums
  (ratio 1.000) except where the finer level double-counts — aggregate the
  coarsest level at/below your target, never mix.
- **`*-XXX` placeholder sub-codes can carry a WRONG parent admin-1** upstream
  (MOZ 2024: Nampula districts filed under Sofala, Zambézia under Cidade de
  Maputo — a systematic shift). The names are good — re-attribute by unique COD
  name match before any rollup (see `export_hnrp_drought.py::sub_parent`).
- **Coverage boundaries**: the HPC mirror includes every plan type (HNRPs,
  **flash appeals**, RRPs, other) at plan/cluster level, all years. HAPI's
  admin-level PiN covers only Global-HNO countries (~24 HNRPs, 2024+) — flash
  appeals (e.g. OPT) and RRPs have no standardized admin-level PiN anywhere
  public. Historical (pre-2024) admin-level PiN exists only as heterogeneous
  per-country `*_hpc_needs_<year>.xlsx` on HDX (`ocha-hpc-tools` org, some back
  to 2015) or raw HPC disaggregation matrices (~8 MB/attachment) — bespoke
  parsing, not mirrored.
- **If HAPI is ever discontinued**: the same data ships as flat CSVs on HDX
  (`hdx-hapi-humanitarian-needs`, `global-hpc-hno`, per-country
  `*_hpc_needs_api_<year>.csv`) — swap `src/hapi.py` to those, schema unchanged.
  (Checked 2026-07: HAPI actively maintained, no public sunset plan.)
- **Pcode quality** (audited 2026-07 vs `public.polygon`): HAPI needs pcodes are
  COD-AB-aligned by design (~100%); known joins caveats — HAPI `*-XXX` placeholder
  codes (intentional "unattributed" rows), Chad `TCD##` vs COD-AB `TD##` prefix,
  SOM Banadir adm2 missing from the reference. Severity workbooks additionally:
  NER `NER###` vs `NE###`, COL zero-padding dropped (`CO5001` vs `CO05001`), and
  MLI `ML11+` / BFA `BF58+` are **real post-reform units newer than COD-AB** —
  polygon staleness, not data errors. adm3 parent pcodes are derived by longest-prefix match
  vs `public.polygon` (upstream CSV ships them blank). **BFA, COD, ETH, SYR are
  adm3-only in the Global HNO** — HAPI has no subnational rows for them at all, so
  the CSV adm3 supplement is their only subnational PiN.
- Runbook: failures are visible in the repo's Actions tab; both workflows are
  `workflow_dispatch`-able, and `refresh-hnrp` takes an `all_years` input for
  on-demand backfills.

## PiN-by-severity (PBS): definition, tool mechanics, sources

**Definition (2026 cycle):** PBS at severity *s* = **Σ Final PiN over all
analysis units whose final intersectoral severity = s**. A "unit" is admin
area × population group × pocket of need (the workbook's `ID` column — pockets
are separate rows, e.g. an IDP camp inside a commune). PBS partitions the
headline figure: Σ over all classes = the overall PiN. By construction
PBS(1)=PBS(2)≈0 (see below); anything nonzero there is a manual override
(e.g. CMR/NER refugee caseloads in low-severity areas). Interpretation caveat:
this is *PiN living in units classified s*, NOT people-in-phase-s — JIAF never
estimates a within-unit severity distribution (unlike IPC), so per-person
phase headcounts do not exist.

**How the 2026 tool computes it** (verified 2026-07-28 against the formulas in
the blank WS-3A/3B template; the 2026 country workbooks descend from it):

1. Sectors submit **sectoral severity** (WS-3.2) and **sectoral PiN**
   (WS-3.1) per unit, in parallel.
2. **Preliminary intersectoral severity** per unit = a hard-coded `IFS` over
   the **8 core sectors only** (CCCM…WASH; Protection AoRs excluded):
   ≥2 sectors at phase 5 AND ≥4 at ≥4 → 5; ≥4 sectors ≥4 → 4; ≥4 ≥3 → 3;
   ≥4 ≥2 → 2; else 1.
3. **Outcome reference indicators** (mortality, malnutrition, epidemics =
   life-threatening; livelihood coping, HR/IHL violations = irreversible harm)
   only **flag** (±2-phase discrepancy vs preliminary) — they never change the
   class themselves. Other flags: ≥2 sectors in phase 5; manual.
4. **Final Severity = preliminary by formula default**; flag resolution in the
   multi-partner workshop *overwrites the cell*. (Hence SSD 2026's broken
   constant-4 column.) From HPC 2026, severity-5 classifications also get a
   rapid global review.
5. WS-3.1 looks the final severity up by unit `ID`
   (`Severity = INDEX/MATCH(WS-3.2 Final Severity)`), then
   **Preliminary PiN = IF(Severity > 2, max sectoral PiN of core sectors,
   blank)** — the mosaic max and the phase-3+ restriction in one formula.
6. **Final PiN = preliminary by default**, overwritten during PiN-flag
   resolution (flags: ≥2 sectors zero PiN; highest PiN ≥90% of population;
   1st-vs-2nd sector gap >30%; 1st-vs-3rd >50%; >100% change vs last year;
   manual).
7. Downstream targeting (also in the tool): targeted = 50% of Final PiN in
   sev-3 units, 100% in sev-4/5; prioritized = 100% of sev-4/5 PiN
   (country-adjustable maxima in the Thresholds tab).

In `hpc.pin_admin` (as of 2026-07-29): **PBS =
`SUM(final_pin) GROUP BY COALESCE(final_severity, severity)`**. The refresh
joins WS-3.2's final severity onto every PiN row as `final_severity` (deepest
admin code, name fallback, population group with area-level fallback) and
warns when it disagrees with `severity`, the PiN sheet's own column.
**Never group by `severity` alone** — it's a live `INDEX/MATCH` of WS-3.2
keyed on a pcode-built unit ID, and offices break it in wrong-but-plausible
ways: SSD 2026 pasted a constant 4 over it; a LBN 2026 preliminary workbook
left every P-Code blank, collapsing all IDs to `""` so `MATCH` broadcast the
*first* unit's severity (3) to all 76 rows — invisible in the sheet, ~17% of
the PiN misclassified. `final_severity` is NULL only where no severity sheet
exists at all (UKR, SYR 2026, YEM 2025 — there the sheet column, parsed from
the workbook's own intersectoral severity, is the only and correct source).
Published "final" columns are formula defaults wherever no workshop
intervened.

**Sources** (PDF page numbers):

- [JIAF 2 Technical Manual, July 2024 ("Final for 2025 HPC")](https://jiaf.info/wp-content/uploads/2024/07/JIAF-2-Technical-Manual_Final-for-2025-HPC.pdf)
  — Mosaic Method: Box 21, p. 50; severity rule + flags + consensus: Box 22,
  p. 50; outcome-indicator thresholds: Box 19 / Diagram 19, pp. 42–47; PBS
  explicitly NOT yet included: pp. 12, 35.
- ["Overview of changes in JIAF PIN and Severity tool" (OCHA, 2025-08-22)](https://knowledge.base.unocha.org/wiki/download/attachments/3993829401/Overview%20of%20changes%20in%20JIAF%20PIN%20and%20Severity%20tool.docx?api=v2)
  — the only official statement of the 2026 PBS implementation (severity
  column auto-filled from the Severity tab; PiN formula restricted to
  severity 3+; pockets of need; targeting thresholds). Listed under "HPC 2026
  Tools" on the [OCHA KB JIAF Manuals page](https://humanitarian.atlassian.net/wiki/spaces/hpc/pages/3993829401/JIAF+Manuals),
  alongside the [blank WS-3A/3B template (EN)](https://knowledge.base.unocha.org/wiki/download/attachments/3993829401/Worksheet_3A_3B_PiN%26Sev_Template.xlsx?api=v2)
  whose formulas are the ground truth for the mechanics above, and the "JIAF
  Severity 5 review process" PDF.
- [GHC "Decoding JIAF 2.0" brief (Aug 2025)](https://healthcluster.who.int/docs/librariesprovider16/meeting-reports/20250820-decoding-jiaf---en.pdf)
  — Humanitarian Reset framing (p. 2), HPC 2026 changes table + Mosaic
  glossary (p. 4).
