---
content_type: dataset
name: CERF OneGMS allocations
aliases: [OneGMS, "CERF API", "cerfgms-webapi", "CERF allocations", "CERF projects"]
provider: "UN OCHA — CERF secretariat (OneGMS grant-management system)"
data_type: humanitarian-financing
access: public
api: "https://cerfgms-webapi.unocha.org/v1/application/All.xml  (full feed, ~1.6k applications, ~6 MB XML; also .json) + /v1/project/All.json (~8.6k agency projects, ~18 MB, ~8 min server-side generation)"
auth: none
formats: [xml, json]
resolution: "application-level (one row per CERF application) + project-level (one row per agency project under each application), 2006–present; country + emergency type + window (RR/UF), USD amounts, individuals planned/reached (projects: incl. women/men/girls/boys breakdowns), narrative summaries, per-project sector/country splits + HRP cap-codes"
update_cadence: "live feed from OneGMS; reached/planned figures fill in as reports come through (RR reports due ~9 months after allocation)"
license: open (public UN data)
code_ref: "ds-cerf-supplement scripts/refresh_mirror.py (daily allocation upsert) + scripts/refresh_projects.py (daily project upsert) + src/cerf_api.py (fetch); ds-aa-tracking src/ds_aa_tracking/schema.py (the AA layer: activations and their allocation links, D115)"
mirror: automated       # aa.cerf_allocation = pure mirror, upserted DAILY by ds-cerf-supplement refresh-mirror; the AA layer (aa.window_activation + aa.activation_funding; the KB-era aa.actual_activation + aa.activation_allocation are frozen) is owned by ds-aa-tracking
mirror_priority: med
used_by:
  - pipelines/cerf-supplement.md
  - apps/cerf-global-trigger-allocations-app.md
last_verified: 2026-11-20
---

# CERF OneGMS allocations

The authoritative public feed of **every CERF application** (Rapid Response +
Underfunded Emergencies) from the OneGMS grant-management system: amounts requested
and approved, emergency type, **individuals planned and reached**, key dates, and the
narrative chief-of-note summaries. Our reference for CERF allocation facts —
including the **anticipatory-action allocations** that fund CERF AA framework
activations.

## Access

- `GET https://cerfgms-webapi.unocha.org/v1/application/All.xml` — no auth, ~6 MB,
  one `<application>` element per application, 43 fields. `All.json` also works.
- `GET https://cerfgms-webapi.unocha.org/v1/project/All.json` — the **project-level**
  feed: ~8.6k agency projects (the "Projects included in this allocation" table on
  cerf.un.org), each carrying `applicationCode` (join to applications), agency,
  amount, dates, status, planned/reached people **with women/men/girls/boys
  breakdowns** (post-~2014), project summaries, nested sector/country splits and HRP
  cap-codes. **~8 min server-side generation** — wrong paths 404 instantly, the real
  one just hangs while building; use a generous read timeout (`fetch_project_feed()`
  in `src/cerf_api.py` uses 20 min).
- No pagination; fetch the whole feed (applications ~1 min). `ds-cerf-supplement`'s
  `src/cerf_api.py` has the minimal fetch/parse pattern.

## Key gotchas

- **`ApplicationID` is NOT unique** (~431 collisions, e.g. ID 1019 = both Madagascar
  2007 and Afghanistan 2023). **Always key on `ApplicationCode`**
  (e.g. `23-RR-AFG-61441`, newer style `CERF-GTM-26-RR-1521`) — unique and non-null.
  (Found the hard way in `ds-cerf-supplement`.)
- Same in the project feed: **`projectID` is NOT unique** (~3.1k collisions across
  the feed's two source tables, `tableName` M/P). **Key on `projectCode`**
  (e.g. `06-FAO-010-A`, newer style `CERF-TCD-25-UF-HCR-35482`) — unique and
  non-null. Project `totalAmountApproved` sums exactly to the application's
  amount, and the feed has a handful of real duplicate (project, sector) split
  rows — don't assume that pair is a key.
- **No structured AA flag.** Anticipatory-action allocations are only identifiable
  from title keywords — usually "(Anticipatory Action …)", but Somalia and SSD use
  "Early Action". The curated activation↔allocation mapping lives in
  ds-aa-tracking's **`aa.activation_funding`** (see below), not in keyword guesses.
- `TotalIndividualReached` is 0/empty until the country office reports (~9 months
  post-allocation) — 0 for a recent allocation means "not yet reported", not "none".
- An AA application is often **pre-arranged months before the trigger fires**
  (title month = arrangement; `FirstProjectApprovedDate` ≈ disbursement/trigger).
- `CountryCode` is ISO3.

## Where it lands in our DB (dev, schema `aa`)

> ER diagram of the whole `aa` schema (mirror + crosswalk + performance tables):
> [../db-erd.md](../db-erd.md).

The full feed lands in **`aa.cerf_allocation`** — a **pure OneGMS mirror** (feed columns
+ the deterministic `aa_keyword` title flag), upserted daily by `ds-cerf-supplement`'s
`scripts/refresh_mirror.py` (its `refresh-mirror` workflow), keyed on `application_code`.
Nothing else writes it. (The pure-mirror split proposed on this page was completed
2026-07 / D83: the curated `aa_adhoc`/`aa_note` columns moved off the table into the
crosswalk below.)

The project feed lands in three companion tables (same workflow, second step,
`scripts/refresh_projects.py` — sole writer, added 2026-08), joined to the
allocation mirror on `application_code`:

- **`aa.cerf_project`** — one row per agency project, keyed on `project_code`:
  agency, amount, dates, status, planned/reached people incl. demographic
  breakdowns, HRP cap-codes, project summaries.
- **`aa.cerf_project_sector`** — per-sector USD splits (1–5 rows per project; no
  PK — the feed has real duplicate sector rows with split amounts).
- **`aa.cerf_project_country`** — per-country budget splits (regional projects,
  e.g. the 2018 Venezuela-crisis projects, span up to 22 countries).

Everything AA-interpretive lives in **separate tables beside it**, owned by
[ds-aa-tracking](../../pipelines/aa-tracking.md) (D115):

- **`aa.window_activation`** — framework activations, per country and window; ad-hoc AA and
  early-action allocations with no OCHA framework behind them (Somalia 2023-25 early actions,
  Ethiopia OND-2024 drought) are **`aa.adhoc_activation`**.
- **`aa.activation_funding`** — the **curated link** from an activation to its fund
  allocations: one activation × N allocations, any pooled fund (`allocation_code` = the CERF
  `application_code`, or a CBPF code, via `aa.v_allocation`). Entered on the tracking site's
  entry/admin pages or through an entries file.
- **The KB-era record, frozen** — written by the KB's loaders and its `kb-aa-links` confirm
  flow until the framework pages stopped being a source (2026-09-28): `aa.actual_activation`
  (from framework-page `activations:` frontmatter) and `aa.activation_allocation`, the old
  curated crosswalk. Many-to-many (LAC Mar-2026 = 1 activation → 3 country applications;
  TCD-drought 2026 / ETH 2020-21 = several activations → 1 application, flag `SHARED_APP`),
  plus two special row kinds: `NO_CERF` (activation funded outside CERF, e.g. bfa-flooding
  via FHRAOC) and `ADHOC_AA`. **`aa.v_activation_funding`** (per-activation rollup: CERF USD
  approved, individuals planned/**reached**) and **`aa.v_aa_allocation`** (every AA
  allocation, framework-linked or ad-hoc) still read these two tables.

## Feed field → mirror column

The mirror changes every feed field name to snake_case, and some names change more than
that (`TotalIndividualPlanned` → `individuals_planned`, `totalPeoplePlanned` →
`people_planned`). To find a field's column, search this section for its feed name.
Values are copied as they are, with one exception: a field the feed leaves blank never
overwrites a value already stored. Both upserts use `coalesce` (ds-cerf-supplement
#141), because the feed sometimes blanks newer-style `CERF-…` figures for a day.
Checked against both feeds on 2026-11-20: all 919 `TotalIndividualPlanned` values in
the feed matched `individuals_planned` on dev.

### Applications → `aa.cerf_allocation` (`refresh_mirror.py`)

| Feed field (`v1/application/All.xml`) | Column | Note |
|---|---|---|
| `ApplicationCode` | `application_code` | primary key |
| `ApplicationID` | `application_id` | not unique |
| `Year` | `year` | |
| `CountryCode` | `country_iso3` | |
| `CountryName` | `country_name` | |
| `RegionName` | `region_name` | |
| `WindowFullName` | `window_name` | |
| `EmergencyTypeName` | `emergency_type` | |
| `EmergencyGroupForGlobalReporting` | `emergency_group` | |
| `ApplicationTitle` | `title` | |
| `AllocationStatus` | `allocation_status` | |
| `AgencyShortName` | `agencies` | |
| `CN_AmountRequested` | `amount_requested` | USD |
| `TotalAmountApproved` | `amount_approved` | USD |
| `TotalIndividualsAffected` | `individuals_affected` | |
| `TotalIndividualPlanned` | `individuals_planned` | blank for every 2006–2013 application |
| `TotalIndividualReached` | `individuals_reached` | 0 or blank until the report is in |
| `CN_ERC_EndorsementDate` | `erc_endorsement_date` | date part only |
| `FirstProjectApprovedDate` | `first_project_approved_date` | date part only |
| `LastProjectApprovedDate` | `last_project_approved_date` | date part only |
| `ReportDueDate` | `report_due_date` | date part only |
| `CN_Summary` | `summary` | |
| `OverviewoftheHumanitarianSituation` | `humanitarian_overview` | |
| `RationaleforCERFAllocation` | `allocation_rationale` | |
| — | `aa_keyword` | derived: title or emergency type contains "anticipat" or "early action" |

**Not mirrored** (19 of the feed's 43 fields): the numeric IDs (`CountryID`, `WindowID`,
`EmergencyTypeID`, `EmergencyGroupID`, `EmergencyCategoryID`, `RegionID`, `SubRegionID`,
`ContinentID`), `TableName`, `EmergencyGroupName`, `EmergencyCategoryName`,
`SubRegionName`, `ContinentName`, `applicationgrouping` (empty in every row),
`ApplicationSummary` (filled for 388 applications; `CN_Summary` is the summary we
mirror), `CERFSStrategicAddedValue` (593 filled), `BeneficiaryType` (664),
`CERFFeedbackDt` (655) and `InterimDueDate` (1,260).

### Projects → `aa.cerf_project` + sector and country tables (`refresh_projects.py`)

| Feed field (`v1/project/All.json`) | Column | Note |
|---|---|---|
| `projectCode` | `project_code` | primary key |
| `projectID` | `project_id` | not unique |
| `applicationCode` | `application_code` | joins to `aa.cerf_allocation` |
| `tableName` | `source_table` | `M` or `P` |
| `year` | `year` | |
| `countryCode` | `country_iso3` | |
| `countryName` | `country_name` | |
| `regionName` | `region_name` | |
| `subRegionName` | `subregion_name` | |
| `windowFullName` | `window_name` | |
| `agencyShortName` | `agency_short_name` | |
| `agencyName` | `agency_name` | |
| `implementingAgencyName` | `implementing_agency_name` | |
| `emergencyTypeName` | `emergency_type` | |
| `emergencyGroupForGlobalReporting` | `emergency_group` | |
| `projectTitle` | `title` | |
| `projectSummary` | `summary` | |
| `projectStatus` | `project_status` | |
| `allocationStatus` | `allocation_status` | |
| `projectTypeName` | `project_type` | |
| `projectSectorName` | `sector_name` | headline sector; the USD splits are in `aa.cerf_project_sector` |
| `totalAmountApproved` | `amount_approved` | USD |
| `beneficiaryType` | `beneficiary_type` | |
| `cerfGenderMarkerID` | `gender_marker_id` | |
| `genderMarkerType` | `gender_marker_type` | |
| `cerfGenderMarkerName` | `gender_marker_name` | |
| `projectStartDate` | `start_date` | date part only |
| `projectEndDate` | `end_date` | date part only |
| `letterSentToAgencyDate` | `letter_sent_date` | date part only |
| `dateUSGSignature` | `usg_signature_date` | date part only |
| `disbursementDate` | `disbursement_date` | date part only |
| `totalPeoplePlanned` | `people_planned` | |
| `plannedFemale`, `plannedMale` | `planned_female`, `planned_male` | |
| `plannedWomen`, `plannedMen`, `plannedGirls`, `plannedBoys` | `planned_women`, `planned_men`, `planned_girls`, `planned_boys` | |
| `totalPeopleReached` | `people_reached` | |
| `reachedFemale`, `reachedMale` | `reached_female`, `reached_male` | |
| `reachedWomen`, `reachedMen`, `reachedGirls`, `reachedBoys` | `reached_women`, `reached_men`, `reached_girls`, `reached_boys` | |
| `projectcapcode[].capCode` | `cap_codes` | distinct values joined with `;` |
| `projectgrouping[].groupingName` | `grouping_names` | distinct values joined with `;` |
| `projectsectors[].sectorID`, `.sectorName`, `.cERFSectorName`, `.clusterName`, `.iascSectorname`, `.sectorAmount` | `aa.cerf_project_sector`: `sector_id`, `sector_name`, `cerf_sector_name`, `cluster_name`, `iasc_sector_name`, `sector_amount` | one row per split, keyed by the parent's `project_code` |
| `ProjectCountry[].countryCode`, `.countryPercent`, `.totalBudget` | `aa.cerf_project_country`: `country_iso3`, `country_percent`, `total_budget` | one row per country; a country listed twice in a project keeps its first row |

**Not mirrored** (14 of the feed's 63 top-level fields): the numeric IDs (`applicationID`,
`windowID`, `countryID`, `agencyID`, `implementingAgencyID`, `emergencyTypeID`,
`projectTypeID`), `emergencyGroupName`, `emergencyCategoryName`, `continentName`, and
`plannedChildren`, `plannedAdults`, `reachedChildren`, `reachedAdults`. In over 99% of
rows those last four equal girls + boys and women + men. `projectgrouping[].groupingID`
is not kept either.

## Related tables (storm matches + drought periods)

Storm/drought enrichment of these allocations lives in a **separate** pair of tables
(same key, `application_code`), produced by [`cerf-supplement`](../../pipelines/cerf-supplement.md):
`aa.cerf_allocation_storm (application_code, sid)` → joins to `storms.ibtracs_storms`,
and `aa.cerf_supplement (application_code, not_tc, valid_month/year_*, confidence, notes)`
— the `valid_*` fields hold each drought allocation's meteorological (rainfall-deficit)
period, Claude-matched with stored confidence. So `aa.cerf_allocation` stays the clean
feed mirror; the storm/drought matching is layered on top.

## Used by

- **`ds-cerf-supplement`** — **refreshes the feed columns** of `aa.cerf_allocation` daily
  (`refresh_mirror.py`) and the project-level tables (`refresh_projects.py`), matches
  storm allocations to IBTrACS storm(s), and dates drought allocations' valid periods,
  writing `aa.cerf_allocation_storm` + `aa.cerf_supplement`
  (chained daily GHAs + static GH Pages site).
- **`ds-aa-tracking`** — links activations to their allocations (`aa.activation_funding`)
  and reads the mirror for its funding and activation pages, next to the backtest tables it
  also owns.
- The CERF global trigger allocations app (`ds-aa-cerf-global-trigger-allocations`)
  is a future consumer (currently reads its own blob extracts).
