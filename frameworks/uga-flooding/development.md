---
content_type: framework
framework: uga-flooding
version: development   # no published/endorsed CERF framework doc exists yet; drafted from the public GH Pages site, not a dated PDF
status: development   # exploratory trigger design across four zones, publicly documented as design/results pages, no CERF envelope or endorsement found
valid_until: null   # doc: no validity period stated anywhere public — there is no endorsed framework document yet
country_iso3: UGA
hazard: flood
admin_level: 2   # inferred: zone/district-level framing (Teso/Kyoga, Mt Elgon, Karamoja, Adjumani/Albert Nile all described at district granularity in secondary sources) — not confirmed against the site itself, see discrepancies
geographic_scope:
  - "Teso/Kyoga riverine zone"
  - "Mt Elgon"
  - "Karamoja"
  - "Adjumani/Albert Nile"
  # pcodes NOT resolved — this page could not verify the exact district list per zone against the source site (see discrepancies). IFRC's overlapping national flood exposure work (external-frameworks/ifrc/uga-flood.md) names Ntoroko, Buyende, Namayingo, Kikuube, Pallisa, Kagadi, Butaleja, Kyenjojo, Kaliro, Bugiri, Kibuku, Namutumba, Busia, Tororo, Budaka, Butebo as its 16 exposed districts, which may or may not match this framework's own zoning.
data_sources:
  - GloFAS
  - FloodScan
  - CHIRPS-GEFS
  - IMERG
trigger_facets:
  basis: mixed
  calibration: bespoke   # design options still being compared per zone; no single published calibration method (return-period vs percentile) could be confirmed for all four zones
  indicators:
    - GloFAS-discharge
    - FloodScan-flood-extent
    - CHIRPS-GEFS-rainfall-forecast
    - IMERG
  n_windows: 4
  window_axes:
    - space
monitoring_period:
  months: [9, 10, 11, 12]
  source: inferred
  note: >-
    No stated season found. Inferred from secondary reporting that the current design/testing
    cycle is framed as "OND 2026 flood trigger: revised analysis and design options"
    (surface declared on apps/seas5-skill.md, a sibling ds-seas5-skill repo product) — i.e.
    Oct-Dec is the season the live design work is being validated against. Uganda floods are
    not confined to OND (Mt Elgon/Karamoja flash flooding and landslides also occur in the
    Mar-May rains), and this framework is not yet operational on any fixed monitoring
    calendar, so treat this range as provisional, not a stated monitoring season.
supersedes: null
# --- funding & scope ---
all_in: true   # not stated; no envelope exists yet to be split or pooled — default per schema
prearranged_funding_usd: null
funding_by_source: {}
funding_by_sector: {}
funding_by_agency: {}
funding_rows: []
cofinancing_usd: null
cofinancing_sources: []
implementing_agencies: []
target_people: null
# --- documents, authority-ranked ---
framework_doc: https://ocha-dap.github.io/ds-aa-uga-flooding/
framework_doc_date: null   # a live/evolving GH Pages site, not a dated PDF — no publication date found
framework_doc_annexes: []
languages: [en]
model_report: null
raw_extract: ["raw/frameworks/uga-flooding/development.txt"]
# --- live system ---
operated_by: null
surfaces:
  - {url: "https://ocha-dap.github.io/ds-aa-uga-flooding/", kind: landing, title: "Uganda flood anticipatory action — OCHA Centre for Humanitarian Data"}
  - {url: "https://ocha-dap.github.io/ds-aa-uga-flooding/coverage/", kind: report, title: "Trigger zones and existing coverage — Uganda flood AA (zones + other organisations' flood AA, their triggers and status)"}
  - {url: "https://ocha-dap.github.io/ds-aa-uga-flooding/results/", kind: report, title: "Results so far — Uganda flood AA"}
depends_on: []
# --- source repo & reconciliation ---
source_repo: ocha-dap/ds-aa-uga-flooding   # trigger analysis + the Pages site; exploratory precursor in ocha-dap/ds-seas5-skill (uganda-flood-trigger page)
source_branch: null
source_sha: null
code_ref: []
trigger_source: framework_doc   # the GH Pages site is the only public artifact reviewed; the underlying ocha-dap/ds-aa-uga-flooding repo code was NOT consulted for this page (see discrepancies) — WebFetch on the live site was also unavailable in this drafting session, so even the site's own text is second-hand via search-engine indexing, not a direct read
repo_completeness: null   # not assessed — this page was drafted with no direct repo or page access, purely from search-engine-indexed summaries of the public site and secondary reporting; see discrepancies
discrepancies:
  - "[gap] This page was drafted without a direct fetch of https://ocha-dap.github.io/ds-aa-uga-flooding/ or its /coverage/ and /results/ subpages (fetch tooling was unavailable this session) — all zone/indicator detail below comes from search-engine-indexed summaries of the public repo/site (ocha-dap/ds-aa-uga-flooding on GitHub, plus its coverage/results pages) and secondary reporting, not a direct read. Re-verify every trigger-window cell against the live site before treating this page as authoritative."
  - "[gap] No specific numeric thresholds, lead times, or return periods could be sourced for any of the four zones — the site is described as presenting 'design options' still being compared, not a finalized/endorsed trigger. All Trigger-windows cells for these fields are null pending a direct read of the site."
  - "[gap] Exact district/pcode membership of each zone could not be confirmed — geographic_scope lists zone names only."
  - "[gap] No published CERF/OCHA framework document, funding envelope, implementing agency, or target-population figure was found anywhere public for this framework — consistent with a pre-endorsement, in-development status."
  - "[gap] infrastructure/pages-registry.md (generated 2026-09) flags this exact site as live (HTTP 200, all three pages) but with no owning KB page (\"no KB page\" / \"UNDECLARED\") prior to this page. This page resolves that gap; re-run the pages-registry generator to confirm the auto-detected entries now match `surfaces` above."
activations: []
# --- escape hatch ---
extra:
  dev_status: >-
    Repo ocha-dap/ds-aa-uga-flooding is public and live (GH Pages 200 as of the 2026-09
    pages-registry sweep) but this page's drafting session could not fetch it directly.
    Search-engine indexing of the repo/site describes a multi-zone trigger-design effort
    (Teso/Kyoga riverine, Mt Elgon, Karamoja, Adjumani/Albert Nile) building on exploratory
    work in the sibling ds-seas5-skill repo (Uganda drought/flood analysis, OND 2026
    flood-trigger design options, FloodScan recurrence layers, GloFAS skill verification —
    see analysis/uga-drought-flood-2026.md and apps/seas5-skill.md). No CERF envelope,
    endorsement, or activation exists for this framework.
  operational_ifrc_eap: >-
    Uganda already has an OPERATIONAL flood trigger, but it is NOT this OCHA/CERF framework:
    the Uganda Red Cross Society's IFRC-financed Early Action Protocol (EAP2021UG01,
    published Aug 2021, GloFAS >=60% probability of a 5-yr-RP flood at 5-day lead time,
    16 nationally-identified exposed districts) has activated once, 15 Nov 2023 (operation
    MDRUG048, CHF 348,761, ~11,201 people in Butaleja/Kikuube/Ntoroko). Full detail:
    external-frameworks/ifrc/uga-flood.md. Per docs/INGESTION.md's Kenya-EAP precedent, that
    activation is NOT recorded in this page's `activations` (it belongs to a different,
    non-OCHA framework) even though it is the only real flood AA activation Uganda has had
    to date.
  related_fao_flood_side: >-
    FAO also has non-CERF flood-side AA work in Uganda, separate from both this framework and
    the IFRC EAP: a closed OND-2023 El Nino flood AA project (OSRO/UGA/070/BEL, USD 1M, ten
    districts incl. Mbale/Butaleja/Sironko/Kasese) and a Japan-funded OPM/FAO early-warning
    infrastructure project in Rwenzori and Mount Elgon (USD 1.13M, Mar 2025-Mar 2026, 10
    hydro-climatic stations, 2 EW centres) with a draft, unpublished Mt Elgon flood AAP
    circulated internally Sep 2026. Full detail: external-frameworks/fao/uga-drought.md
    (`extra.fao_uganda_flood_side`), which itself names ocha-dap/ds-aa-uga-flooding as the
    source of an "independent backtest" of that draft AAP's triggers — i.e. this OCHA
    repo's analysis may feed FAO's Mt Elgon design as well as (or instead of) an eventual
    OCHA/CERF trigger. Not enough public detail to say which.
  national_context: >-
    Uganda launched a National Roadmap on Anticipatory Action 2026-2031 and the U-MHIEWS
    multi-hazard early-warning system in July 2026 (OPM with WFP, FAO, IGAD), including
    sub-national early-warning centres in Karamoja, Teso, Mount Elgon and Rwenzori. The
    roadmap commits to "establish clear disaster triggers"; none are published yet. This
    OCHA framework's four zones overlap three of those four U-MHIEWS centres (Karamoja,
    Teso, Mount Elgon) but substitute Adjumani/Albert Nile for Rwenzori — not yet reconciled
    in any public source.
  schema_strain: >-
    n_windows=4 taken as one per named zone (Teso/Kyoga, Mt Elgon, Karamoja,
    Adjumani/Albert Nile); could not confirm whether any zone itself splits into
    readiness+action sub-windows, which would raise this count. trigger_facets.calibration
    set to bespoke rather than return-period because return-period language could only be
    confirmed for the (separate, IFRC-owned) national EAP, not for this framework's own
    zone-specific designs.
visibility: public
last_synced: "2026-09-18"
---

# Uganda Flood — development

> **Pre-endorsement / in development.** No published OCHA/CERF framework document exists yet
> for Uganda flooding (`framework_doc` points to the project's public GH Pages site, not a
> dated PDF). This page was drafted from public web sources only — `source_repo` and
> `code_ref` are deliberately empty; the underlying `ocha-dap/ds-aa-uga-flooding` repo (which
> does publicly exist, see discrepancies) was not consulted directly for this draft. The
> canonical trigger, once one exists, will be the framework document or the repo code — this
> page does not redefine it, and should be re-synced against a direct read of the site before
> being treated as authoritative.

## Summary

An OCHA/CERF anticipatory action trigger for flooding in Uganda is under development, designed
across **four geographically distinct zones**: **Teso/Kyoga** (riverine flooding around Lake
Kyoga), **Mt Elgon** (rainfall-triggered flash flooding and landslides), **Karamoja** (flash
flooding), and **Adjumani/Albert Nile** (riverine/lake-level flooding on the Albert Nile). The
work is published as a small documentation site (landing page, a "coverage" page describing
trigger zones and what other organisations already cover, and a "results" page) rather than a
CERF-endorsed framework document, and builds on exploratory analysis in the sibling
`ds-seas5-skill` repo (Uganda drought/flood country analysis, an "OND 2026 flood trigger:
revised analysis and design options" page, FloodScan recurrence layers, GloFAS skill
verification). No funding envelope, implementing agency, target population, or activation
exists for this framework. Uganda already has a separate, **operational** flood trigger run by
the Uganda Red Cross Society (IFRC EAP2021UG01, activated once, Nov 2023) — see
`extra.operational_ifrc_eap` — which this OCHA framework does not replace or supersede.

## Method

Public information indicates a per-zone design approach rather than one shared trigger:
riverine flooding around Lake Kyoga is approached via GloFAS discharge reforecasts mapped
against FloodScan-observed flood extent per district to assess likely impact; the Mt Elgon
massif uses rainfall forecasts (CHIRPS-GEFS, reportedly transitioning to ECMWF) with
antecedent-wetness qualifiers, validated against observed rainfall (IMERG) and reported
landslide/flood impacts; Karamoja is approached with similar flash-flood rainfall-forecast
logic, reportedly sub-zoned by basin; and Adjumani/Albert Nile is described as still choosing
between GloFAS Albert Nile reporting points, Lake Albert level via satellite altimetry, or
direct rainfall monitoring. An observational backstop using FloodScan flood extent (and
report-based observations where satellite data is unavailable) is described as present in
every zone, so a forecast miss does not necessarily mean the system fails to activate. **None
of this could be verified against a direct read of the site or repo in this drafting
session** — treat the above as a provisional summary pending re-verification (see
discrepancies).

## Trigger logic

- **Keys off:** GloFAS discharge reforecasts + FloodScan flood extent (Teso/Kyoga riverine);
  CHIRPS-GEFS rainfall forecasts + IMERG observed rainfall (Mt Elgon); rainfall forecasts,
  reportedly sub-zoned by basin (Karamoja); GloFAS Albert Nile points, Lake Albert altimetry,
  or rainfall monitoring — reportedly still being compared as design options (Adjumani/Albert
  Nile).
- **Decision rule (plain language):** Not publicly specified. The site is reported to present
  **design options being compared**, not a finalized, single decision rule per zone — none of
  the numeric thresholds, lead times, or return periods could be sourced.
- **Activation structure:** Four independent geographic windows/zones; no confirmed
  readiness/action staging within any zone.
- **Calibration:** Not confirmed for any zone. (For contrast, the separate, IFRC-owned
  national EAP calibrates to a 5-year return period — see `extra.operational_ifrc_eap` — but
  this OCHA framework's own calibration approach per zone is not public.)
- **Authoritative source:** No CERF framework document exists. `framework_doc` points to the
  project's public GH Pages site (<https://ocha-dap.github.io/ds-aa-uga-flooding/>) as the
  closest thing to a public authoritative reference at this stage.
- **Operated by:** null — analytical work attributed to OCHA-DAP; not yet an operating live
  system (no monitoring pipeline, distribution list, or CERF allocation found).

## Trigger windows

| window | basis | indicator | threshold | lead time | return period | releases |
|---|---|---|---|---|---|---|
| Teso/Kyoga riverine (Lake Kyoga basin) | mixed (forecast + observational backstop) | GloFAS-discharge; FloodScan-flood-extent | not published | not published | not published | not yet defined (no CERF envelope) |
| Mt Elgon | forecast, with observational validation | CHIRPS-GEFS-rainfall-forecast (transitioning to ECMWF); IMERG (validation) | not published | not published | not published | not yet defined |
| Karamoja | forecast | rainfall forecast, reportedly sub-zoned by basin | not published | not published | not published | not yet defined |
| Adjumani/Albert Nile | mixed — design options under comparison | GloFAS-discharge (Albert Nile points) OR lake-level altimetry OR rainfall monitoring | not published | not published | not published | not yet defined |

## Per-country variants

*(Single-country framework — section not applicable.)*

## Sources & repo completeness

- **Trigger taken from:** `trigger_source: framework_doc` — no CERF-endorsed document exists;
  the GH Pages site is the nearest public artifact, and even that was not fetched directly
  this session (see discrepancies).
- **Repo completeness:** not assessed (`repo_completeness: null`). The `ocha-dap/ds-aa-uga-flooding`
  GitHub repository is public and its GH Pages site is live per `infrastructure/pages-registry.md`,
  but per this task's scope `source_repo`/`code_ref` were deliberately left empty and the repo
  was not read directly.
- **Discrepancies:** see frontmatter `discrepancies` — headline gap is that this entire page is
  drafted from search-engine-indexed secondary summaries of the public site, not a direct
  fetch; every zone-level design claim needs re-verification against
  <https://ocha-dap.github.io/ds-aa-uga-flooding/coverage/> and `/results/` directly.

## Monitoring

No live monitoring pipeline was found for this framework (no GHA workflow, Databricks job, or
distribution list identified). `infrastructure/pipeline-registry.md` was not checked for a
possible match; if a monitoring job for this repo exists it should be linked here. The related
`ds-seas5-skill` app (`apps/seas5-skill.md`) publishes an "OND 2026 flood trigger: revised
analysis and design options" page for Uganda as a design artifact, not an operational
monitor.

## Historical activations

**Never activated** (`activations: []`) — there is no CERF envelope for this framework to
release. This is distinct from Uganda's only real flood AA activation to date, the IFRC/URCS
EAP2021UG01 trigger of 15 November 2023 (operation MDRUG048), which belongs to a different,
non-OCHA framework — see `extra.operational_ifrc_eap` and
[external-frameworks/ifrc/uga-flood.md](../../external-frameworks/ifrc/uga-flood.md). Do not
read that activation as evidence of how this framework's (still undefined) trigger would
behave.

## Key decisions & rationale

**Four zones instead of one national trigger.** Uganda's flood risk is geographically and
hydrologically distinct — Lake Kyoga-basin riverine flooding, Mt Elgon rainfall-driven
landslides/flash floods, Karamoja flash flooding, and Albert Nile/Lake Albert dynamics in the
west Nile — which public sources describe as the reason for a per-zone rather than single
national design, mirroring the zone structure IFRC's own EAP and FAO's Karamoja/Mt Elgon work
independently converge on (see `extra.operational_ifrc_eap`, `extra.related_fao_flood_side`).
Why each zone's specific indicator/threshold choices were made could not be sourced.

**Relationship to other Uganda flood AA work is unresolved in public sources.** At least three
efforts now touch overlapping geography — this OCHA framework, the IFRC national EAP, and
FAO's Mt Elgon/Karamoja work (one FAO source names this very repo as providing an "independent
backtest" of FAO's own draft Mt Elgon AAP triggers) — with no public document yet reconciling
scope, indicators, or governance between them.

## Changes from previous version

`supersedes: null` — this is the only version of this framework recorded in the KB, and no
prior OCHA/CERF Uganda flood framework was found in any source reviewed.

## Open questions / known issues

1. **This page needs a direct fetch of the live site.** Web-fetch tooling was unavailable
   during drafting; every zone/indicator claim above is a search-engine-indexed secondary
   summary of <https://ocha-dap.github.io/ds-aa-uga-flooding/> (plus `/coverage/` and
   `/results/`), not a first-hand read. Re-verify before relying on this page.
2. **No numeric trigger detail is public** — thresholds, lead times, return periods, and even
   which design option was chosen per zone (e.g. for Adjumani/Albert Nile) are all unknown.
3. **Zone-to-district mapping unresolved** — `geographic_scope` lists zone names only, not
   pcodes.
4. **Relationship to the IFRC national EAP and FAO's Mt Elgon/Karamoja work is undocumented** —
   whether this framework is meant to complement, backtest, or eventually supersede either is
   not stated anywhere public found.
5. **Status could shift once the repo/site is read directly** — this page defaults to
   `status: development` per the schema's guidance to default there when pre-development vs.
   development is hard to tell from public sources alone; a direct repo read may show it is
   further along (or earlier) than this draft assumes.
