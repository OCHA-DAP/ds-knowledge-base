---
content_type: framework
framework: uga-flooding
version: development   # no published or endorsed framework document; this page reflects the spoke repo at handover (branch handover/pauline, 30 Sep 2026)
status: development   # four zone triggers drafted and backtested; Teso adopted, Elgon/Karamoja/Adjumani to finalise; nothing monitored, no endorsement, no CERF envelope yet
valid_until: null   # no framework doc, so no validity period. The design targets the 1 Oct - 31 Dec 2026 activation window (funding not past March 2027): a season, not a validity period
country_iso3: UGA
hazard: flood
admin_level: 2   # zones are lists of districts (CODAB ADM2). Teso's IFRC-form trigger also judges counties and sub-counties (ADM3/4); a triggered sub-area triggers its district
geographic_scope:
  # CODAB ADM2 pcodes (FieldMaps 135-district vintage, via ocha_stratus.codab), resolved from the
  # district-name lists in src/constants.py (ZONES): core + tier 2 per zone. Tier 2 = same driver,
  # different flood regime (and so a different indicator).
  # Teso / Lake Kyoga: core (Akokoro river)
  - UG2047   # Katakwi
  - UG2027   # Amuria
  - UG2046   # Kapelebyong
  # Teso / Lake Kyoga: tier 2 (downstream Awoja / Lake Bisina wetlands)
  - UG2062   # Soroti
  - UG2058   # Ngora
  - UG2060   # Serere
  # Mount Elgon: core (slopes, flash floods and landslides)
  - UG2029   # Bududa
  - UG2034   # Bulambuli
  - UG2061   # Sironko
  - UG2052   # Manafwa
  - UG2056   # Namisindwa
  - UG2054   # Mbale
  - UG2045   # Kapchorwa
  - UG2050   # Kween
  - UG2033   # Bukwo
  # Mount Elgon: tier 2 (Manafwa / Mpologoma / Awoja lowlands)
  - UG2036   # Butaleja
  - UG2028   # Budaka
  - UG2048   # Kibuku
  - UG2059   # Pallisa
  - UG2032   # Bukedea
  - UG2049   # Kumi
  # Karamoja: core (flash floods)
  - UG3075   # Kaabong
  - UG3076   # Karenga
  - UG3080   # Kotido
  - UG3064   # Abim
  - UG3086   # Moroto
  - UG3090   # Napak
  - UG3088   # Nabilatuk
  - UG3089   # Nakapiripirit
  - UG3069   # Amudat
  # Adjumani / Albert Nile: core
  - UG3065   # Adjumani
  - UG3087   # Moyo
  - UG3093   # Obongi
  # Adjumani / Albert Nile: tier 2 (Lake Albert shore and upper Albert Nile)
  - UG3098   # Pakwach
  - UG3091   # Nebbi
  - UG3084   # Madi Okollo
data_sources:
  - GloFAS         # v4: reanalysis (Uganda box), reforecast at G5196, official 5-yr return-level map
  - CHIRPS-GEFS    # 5-day forecast per district; v2 (calibration base) discontinued 1 Jul 2026 -> CHIRPS3-GEFS
  - IMERG
  - FloodScan
  - NASA-GWM       # Global Water Monitor lake altimetry (Victoria, Kyoga, Albert)
  - EM-DAT         # impact record, with DesInventar, curated press and IOM DTM
  - DesInventar
  - IOM-DTM
trigger_facets:
  basis: mixed   # forecast (GloFAS ensemble, CHIRPS-GEFS) + observed (lake-level leg; proposed FloodScan fallback in Teso)
  calibration: return-period   # Teso: the EAP's fixed GloFAS 5-yr level (not calibrated here). Others: Gumbel return levels at the zone's major-season frequency, floored at 1-in-3
  indicators:
    - GloFAS-discharge-probability
    - CHIRPS-GEFS-5day-rainfall-forecast
    - lake-level-rise-altimetry
    - FloodScan-SFED
  n_windows: 4   # one per zone; Adjumani's two legs and Teso's proposed fallback are OR-legs of their zone's window
  window_axes: [space]
monitoring_period:
  months: [10, 11, 12]
  source: stated
  note: >-
    Activation window 1 Oct - 31 Dec, stated in the spoke repo (trigger_draft.py SEASON_MONTHS;
    HANDOVER.md), not in a framework doc. Chosen because planning runs into September and funding
    does not run past March (decision of 23 Sep 2026). It is not the flood peak: Oct-Dec holds only
    16-29% of each zone's recorded impact, and August is the peak month in three zones. Nothing is
    monitored yet (see Monitoring).
supersedes: null
# --- funding & scope ---
all_in: false   # zones trigger independently, each releasing its own share all-in (decision of 22 Sep 2026). No envelope exists yet; the split across zones is open
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
framework_doc: null   # no published or endorsed framework document; the public GH Pages site is declared under surfaces
framework_doc_date: null
framework_doc_annexes: []
languages: [en]
model_report: null
raw_extract: []   # the earlier extract of the landing page was dropped along with framework_doc (there is no framework document to extract)
# --- live system ---
operated_by: null   # nothing runs yet. Once monitored, Teso's trigger state is the 510/URCS IBF portal's (see Monitoring)
surfaces:
  - {url: "https://ocha-dap.github.io/ds-aa-uga-flooding/", kind: landing, title: "Uganda flood anticipatory action — OCHA Centre for Humanitarian Data"}
  - {url: "https://ocha-dap.github.io/ds-aa-uga-flooding/coverage/", kind: report, title: "Trigger zones and existing coverage — Uganda flood AA (zones and tiers, district lists, other organisations' flood AA by area)"}
  - {url: "https://ocha-dap.github.io/ds-aa-uga-flooding/results/", kind: report, title: "Results so far — Uganda flood AA (GloFAS coverage, FloodScan and exposure vs impact, rainfall chain, backstop options, impact maps)"}
  - {url: "https://ocha-dap.github.io/ds-aa-uga-flooding/triggers/", kind: report, title: "Uganda flood AA — draft triggers (restricted: one per zone, year-by-year backtests; team review password)", access: password}
  - {url: "https://ocha-dap.github.io/ds-aa-uga-flooding/partner/", kind: report, title: "Uganda flood AA — partner drafts (restricted: unpublished partner material)", access: password}
depends_on:
  - floodscan-ingest   # team FloodScan rasters: the backtests and Teso's proposed observed-flood fallback
  - imerg              # team IMERG rasters: antecedent-rain analyses; observed rain if the Elgon partner trigger needs it
# --- source repo & reconciliation ---
source_repo: ocha-dap/ds-aa-uga-flooding   # exploratory precursor: ocha-dap/ds-seas5-skill (uganda-flood-trigger page)
source_branch: handover/pauline   # PR #1 (https://github.com/OCHA-DAP/ds-aa-uga-flooding/pull/1), not yet merged. Switch to main once #1 merges (regular merge, so this SHA stays reachable)
source_sha: "49a838d"
code_ref:
  - analysis/trigger_draft.py       # the four zone triggers: calibration, event matching, backtest
  - analysis/ifrc_reproduction.py   # Teso: the IFRC/URCS EAP trigger as the IBF portal computes it
  - analysis/existing_triggers.py   # other organisations' triggers backtested beside ours
  - analysis/floodscan_fallback.py  # observed-flood fallback; Karamoja rain vs FloodScan per district
  - analysis/adjumani_options.py    # Adjumani design options (lake leg alone, compound, spatial)
  - src/constants.py                # zones and tiers (district-name lists)
trigger_source: repo
repo_completeness: {analysis: full, monitoring: none}   # every trigger and backtest rebuilds from the repo (README "Rebuilding everything"); output tables are gitignored, partner parameters live in gitignored config mirrored on the dev blob
discrepancies:
  - "[gap] Teso's trigger is a stand-in until checked against the IBF portal. analysis/ifrc_reproduction.py has the portal's mechanics (zonal max, all_touched, nodata=0, child-to-parent propagation) but runs on the GloFAS reanalysis as a perfect forecast, dated 5 days early. It over-triggers at marginal exceedances (at G5196, when the reanalysis is 0-2% over the 5-yr level, 60% of reforecast members agree only about a third of the time) and in Nov 2023 has ~23 districts over the level that the portal's notification did not list. Only the portal's own trigger log (2021-25), boundary file and per-area thresholds from URCS/510 settle it."
  - "[gap] Every rain threshold (Elgon, Karamoja, Adjumani's rain leg) was calibrated on CHIRPS-GEFS v2, which CHC discontinued on 1 Jul 2026. The live feed is CHIRPS3-GEFS; recalibrate on its hindcast (2001-2019, 2021-) or at least compare v2 and v3 district distributions before monitoring."
  - "[gap] Whether URCS's EAP2021UG01 is live for Oct-Dec 2026 is unconfirmed: the 2023 activation document gives its timeframe as 27 May 2021 - 27 May 2026, while IFRC GO lists operation MDRUG048 open to 30 Nov 2026. Teso's trigger follows whatever URCS runs."
  - "[stale] The module docstring of analysis/trigger_draft.py gives the event-matching lead windows as 14 / 30 / 120 days (rain / GloFAS / lake); the code's LEAD_DAYS (30 / 45 / 150) is what runs and what this page reports."
  - "[stale] The spoke README's 'The zones' table and the Teso zone label in src/constants.py still name GloFAS G5196 as Teso's indicator. Since 29 Sep 2026 Teso uses the IFRC/URCS trigger as the portal computes it (TESO_SOURCE = \"ifrc\" in trigger_draft.py), which does not read G5196 alone."
  - "[stale] The older results-page analyses (exposure_vs_impact, backstop_options, flash_flood_*) predate the 22 Sep 2026 DesInventar date fix (an unknown day is month precision, not the 1st) and should be rerun. The trigger backtests use the fixed loader."
activations: []
# --- escape hatch ---
extra:
  handover: >-
    Handed over from Tristan to Pauline (GitHub @PaulineNimo) on 30 Sep 2026. Entry point:
    HANDOVER.md in the spoke repo (added by PR #1): where each zone stands, four next steps
    (confirm the IFRC trigger; put in the partner's processing for Elgon; finalise Karamoja and
    Adjumani; set up monitoring), outstanding points with owners, an independent review of the
    judgement calls, and where everything lives. Then CLAUDE.md (working notes and decisions with
    dates) and the restricted /triggers/ page (every backtest table).
  dev_status: >-
    Country-team request of 2 Sep 2026: a trigger system split by zone, with an observed-flood
    backstop and a coverage map beside other organisations' flood AA. By 30 Sep 2026 all four zones
    have a backtested draft; Teso's is adopted (the IFRC/URCS trigger), the other three are drafts.
    Builds on exploratory work in ds-seas5-skill (analysis/uga-drought-flood-2026.md,
    apps/seas5-skill.md), which keeps the country-team readouts. No CERF envelope, endorsement,
    monitoring or activation exists.
  operational_ifrc_eap: >-
    Uganda's operational flood trigger is the Uganda Red Cross Society's IFRC-DREF-financed Early
    Action Protocol EAP2021UG01, a URCS framework, not OCHA's. Approved wording (EAP summary, 27 May
    2021): GloFAS forecast of at least 70% probability of a 5-yr return-period flood in high-priority
    flood-prone districts and a 10-yr flood in lower-priority ones, expected to affect more than
    1,000 households, 5-day lead, where the false-alarm ratio is at most 0.5; the EAP names 14
    high-risk districts (Kasese, Katakwi, Amuria, Kampala, Butaleja, Sironko, Bududa, Manafwa, Kumi,
    Ntoroko, Bulambuli, Moyo, Nabilatuk, Ngora). The Nov 2023 activation document states at least
    60% probability of a 5-yr flood in flood-prone districts (no 10-yr tier), which is what the 510
    IBF portal's Uganda configuration computes (admin 2-4, zonal max of each of 51 members' flow vs
    zonal max of the official GloFAS v4 5-yr map, lead up to 5 days). Activated once: 15 Nov 2023,
    operation MDRUG048, CHF 348,761 for ~11,201 people in Butaleja, Kikuube and Ntoroko. The 16
    districts listed that day were the portal's "potentially exposed districts" for that forecast,
    not the EAP's district list. Timeframe per the 2023 activation document: 27 May 2021 - 27 May
    2026; IFRC GO lists MDRUG048 open to 30 Nov 2026; renewal for Oct-Dec 2026 is unconfirmed.
    Since 29 Sep 2026 it is also this framework's Teso trigger (alignment with URCS); it remains
    URCS's framework, and per D53 its activation is not recorded in `activations`. Full detail:
    external-frameworks/ifrc/uga-flood.md.
  related_fao_flood_side: >-
    FAO's Uganda flood work is separate from this framework: a closed OND-2023 El Nino flood AA
    project (OSRO/UGA/070/BEL) and the Japan-funded OPM/FAO flood early-warning project in the
    Rwenzori and Mount Elgon sub-regions (Mar 2025 - Mar 2026). A draft FAO flood AAP for the Mount
    Elgon sub-region exists (Sep 2026); it is unpublished and is not described here. Public detail:
    external-frameworks/fao/uga-drought.md (`extra.fao_uganda_flood_side`).
  national_context: >-
    Uganda launched a National Roadmap on Anticipatory Action 2026-2031 and the U-MHIEWS
    multi-hazard early-warning system in July 2026 (OPM with WFP, FAO, IGAD), with sub-national
    early-warning centres in Karamoja, Teso, Mount Elgon and Rwenzori. The roadmap commits to
    "establish clear disaster triggers"; none are published. Three of this framework's zones
    (Teso, Mount Elgon, Karamoja) match those centres; the fourth is Adjumani / Albert Nile, not
    Rwenzori. The /coverage/ page maps other organisations' flood AA against the zones.
  cerf_flood_allocations: >-
    CERF has made two rapid-response flood allocations to Uganda, shown per zone in the backtest
    timelines: 07-RR-UGA-11920 (4 Oct 2007, USD 6.0M, Aug-Oct 2007 floods; Teso and Karamoja
    primary) and 20-RR-UGA-40553 (17 Jan 2020, USD 3.95M, Sep-Dec 2019 floods and landslides; Elgon
    primary). Response allocations, not AA activations of this framework.
  schema_strain: >-
    n_windows = 4, one per zone, each an independent all-in trigger for its share. Within a zone,
    Adjumani's draft has two OR-legs (lake level, district rain) that split the zone's rate equally,
    and Teso's proposed FloodScan fallback is an OR-leg of Teso's window; neither adds a window.
    Karamoja and Adjumani's rain leg are per-district thresholds at a common rarity. No zone has
    readiness/action staging (a later design round).
visibility: public
last_synced: "2026-09-30"
---

# Uganda Flood — development

> **In development, handed over 30 Sep 2026.** No published or endorsed OCHA/CERF framework
> document exists. The trigger is the code at `code_ref` in `ocha-dap/ds-aa-uga-flooding`
> (branch `handover/pauline`, PR #1), and the entry point there is `HANDOVER.md`. This page
> summarises it; it does not redefine it.

## Summary

An OCHA/CERF flood anticipatory action trigger for Uganda, designed as **four zones that trigger
independently**, each releasing its own share all-in: **Teso / Lake Kyoga** (riverine), **Mount
Elgon** (flash floods and landslides on the slopes, riverine lowlands below), **Karamoja** (flash
floods) and **Adjumani / Albert Nile** (Nile high stand and tributary flash floods). The window is
**1 October to 31 December 2026**. Teso has adopted the IFRC/URCS EAP trigger as the 510 IBF
portal computes it (GloFAS ensemble, 5-yr return level, at least 60% of members, lead up to 5
days), for alignment with URCS rather than for skill. Elgon, Karamoja and Adjumani have
CHIRPS-GEFS rainfall-forecast drafts (Adjumani also a Lake Kyoga level leg) still to be
finalised. Backtested on the Oct-Dec seasons of 2000-2024 against dated floods, each zone
activates about 1 season in 4 to 1 in 20 and catches one major flood; October-December holds only
16-29% of each zone's recorded impact. Nothing is monitored yet, and the rain thresholds need
recalibrating on CHIRPS3-GEFS. The work passed from Tristan to Pauline on 30 Sep 2026.

## Method

**Zones.** District-name lists in `src/constants.py`, resolved to CODAB districts by
`src/zones.py`. Each zone has a core (what it is for) and, for three zones, a tier 2 with the same
driver but a different flood regime: the downstream Awoja / Bisina wetlands in Teso, the lowlands
below Elgon, the Lake Albert shore for Adjumani. Teso's six districts were settled by
`analysis/teso_glofas_coverage.py` (13 neighbours ruled out). District lists and the rationale
are on `/coverage/`.

**Data.** GloFAS v4 (the reanalysis over a Uganda box, the reforecast at the Akokoro reporting
point G5196, and the official 5-yr return-level map), the CHIRPS-GEFS 5-day forecast per
district (2000-2026), IMERG and FloodScan per district (team rasters), and NASA Global Water
Monitor lake altimetry (Victoria, Kyoga, Albert). The impact record combines EM-DAT, DesInventar
(an unknown day is month precision), curated press and IOM DTM events, with multi-district
events split across districts and only the zone's share counted.

**Calibration (the zone rule).** Each zone activates about as often as it has a major-impact
Oct-Dec season (a single event with at least 5 deaths or 5,000 people affected, zone share),
never more often than 1-in-3. The threshold is then raised while every caught event of 5,000 or
more people is still caught; with no such catch it stays at the frequency-matched level.
Thresholds are each series' Gumbel return level on its own Oct-Dec maxima, so wet and dry
districts are held to the same rarity; never tuned per district. Return periods are not chosen by
backtest score, since 25 seasons is noise. Teso is the exception: its threshold is the EAP's,
fixed, and its rate is whatever it is.

**Backtest.** Oct-Dec seasons 2000-2024 (25). The first activation of a season releases the
zone's envelope. It **catches** a major event if the event starts within the leg's lead window
after it (30 days for rain forecasts, 45 for GloFAS, 150 for the lake leg; an observed-flood
activation during the flood or up to 10 days after it) or is already under way; otherwise it is a
false alarm. A major season with no catch is a miss. Never scored by calendar year.

## Trigger logic

- **Keys off:** Teso: GloFAS ensemble exceedance of the official 5-yr return level, per
  district, county and sub-county (plus a proposed FloodScan extent fallback). Elgon: the
  CHIRPS-GEFS 5-day forecast averaged over the zone's 15 districts. Karamoja: the CHIRPS-GEFS
  5-day forecast in each of 9 districts. Adjumani: Lake Kyoga's 180-day level rise (a proxy for
  Lake Albert) or any district's CHIRPS-GEFS 5-day forecast.
- **Decision rule (plain language):** each zone is checked on its own every day from 1 October to
  31 December. Teso activates when the IBF portal would: at least 60% of the 51 GloFAS members put
  the largest river flow anywhere in a Teso district, or in one of its counties or sub-counties,
  above the largest official 5-yr level in that area, within 5 days. The rain zones activate when
  the 5-day forecast rainfall (zone mean for Elgon, any single district for Karamoja) passes a
  level set so that the zone activates about once in 5 Oct-Dec seasons; in Karamoja each
  district's level is rarer (about 1-in-12) so that any of nine comes to 1-in-5. Adjumani
  activates when the lake has risen unusually over 180 days or a district's forecast is
  exceptional.
- **Activation structure:** four independent zone windows, each all-in for its share; no
  readiness/action staging. Adjumani's legs are OR; Teso's fallback would be OR.
- **Calibration:** Teso not calibrated (the EAP's fixed threshold); the other zones by the zone
  rule above.
- **Authoritative source:** the repo (`code_ref`); there is no framework document. The backtest
  tables are on the restricted `/triggers/` page and in the gitignored `outputs/triggers/`
  (`summary.csv`, `thresholds.csv`, one CSV per zone).
- **Operated by:** nothing runs yet. When it does, Teso's trigger state is the IBF portal's
  (URCS / 510), so that zone's live trigger will be computed outside this repo.

## Trigger windows

Backtest over the 25 Oct-Dec seasons 2000-2024. Rain thresholds are in
`outputs/triggers/thresholds.csv` (CHIRPS-GEFS v2 basis, to be recalibrated).

| window | basis | indicator | threshold | lead time | return period | releases |
|---|---|---|---|---|---|---|
| **Teso / Lake Kyoga** (6 districts). **Adopted** 29 Sep 2026; to confirm with URCS / 510 | forecast (+ proposed observed fallback) | GloFAS-discharge-probability (IFRC/URCS EAP2021UG01 as the IBF portal computes it); proposed FloodScan-SFED fallback | ≥60% of 51 members above the zonal max of the official GloFAS v4 5-yr map, each district / county / sub-county judged at its largest river cell; a triggered sub-area triggers its district. Fallback: FloodScan extent at a common rarity in 5 districts | ≤5 days (forecast); in Oct-Dec activations come with the river already high (median 0 days) | not calibrated; backtest **1-in-4.3** (stand-in: 6 activations). Not "1-in-5": some Teso district passes the 5-yr level in about 15 of 26 years | the zone's share, all-in (no envelope yet) |
| **Mount Elgon** (15 districts). **Draft**; likely replaced by a partner's trigger once the partner confirms its processing | forecast | CHIRPS-GEFS-5day-rainfall-forecast, zone mean | zone-mean 5-day total at the calibrated rarity | 5-day forecast | **1-in-5.4** (frequency-matched 1-in-5.2, raised while the Nov 2024 catch survives) | the zone's share, all-in |
| **Karamoja** (9 districts). **Draft**, to finalise | forecast | CHIRPS-GEFS-5day-rainfall-forecast, per district | any district above its own level at a common rarity (1-in-12.4 per district) | 5-day forecast | **1-in-5.2** (frequency-matched) | the zone's share, all-in |
| **Adjumani / Albert Nile** (6 districts). **Draft**, to finalise; recommended: lake leg alone | mixed (observed lake level OR rain forecast) | lake-level-rise-altimetry (Lake Kyoga 180-day rise, 3-pass median filter); CHIRPS-GEFS-5day-rainfall-forecast per district | current draft: lake rise at 1-in-43 on its own record OR any district at 1-in-29 (each leg half the zone's rate) | lake: none in this window (the Nile is already high); rain: 5-day forecast | **1-in-20** (frequency-matched 1-in-6.5, raised) | the zone's share, all-in |

**Simulated (backtest) record, per zone** (the draft designs above; not real activations):

| zone | activations | catches | misses (major seasons not caught) |
|---|---|---|---|
| Teso | 6 (2000, 2007, 2011, 2019, 2020, 2023) | Oct 2007, already under way for five weeks and only through one Katakwi sub-county at 1.045× the level | 2010, 2014, 2021 |
| Teso + FloodScan fallback | 8 (adds 2003, 2021) | Oct 2007, Oct 2021 | 2010, 2014 |
| Elgon | 5 (2004, 2006, 2014, 2019, 2024) | Nov 2024 (Bulambuli landslides, 5 days ahead) | 2007, 2011, 2018, 2019 |
| Karamoja | 5 (2006, 2009, 2014, 2019, 2024) | Dec 2006 (13 days ahead) | 2007, 2008, 2010, 2012 |
| Adjumani (draft) | 2 (2001, 2020) | 2020 (lake leg, months into the flood) | 2004, 2008, 2023 |
| Adjumani, lake leg alone at 1-in-5 to 1-in-6.5 | 5-6 | 2020 and 2023, both on 1 October with the flood under way | 2004, 2008 |

## Sources & repo completeness

- **Trigger taken from:** `trigger_source: repo`. No framework document exists; the IFRC/URCS
  trigger used for Teso is taken from the IBF pipeline's own code
  (`rodekruis/IBF-river-flood-pipeline`, Uganda settings), not from the EAP's wording.
- **Repo completeness:** analysis full (every trigger and backtest rebuilds from the repo; the
  rebuild order is in the README), monitoring none. Partner parameters live only in gitignored
  config, mirrored on the dev blob (`HANDOVER.md`, "Private material"); output tables are
  gitignored.
- **Discrepancies:** see frontmatter. The open ones that matter: Teso's reproduction is a
  stand-in until checked against the portal's trigger log; the rain thresholds sit on a
  discontinued product (CHIRPS-GEFS v2); and whether the EAP is live for Oct-Dec 2026 is
  unconfirmed.

## Monitoring

**Not set up.** Nothing runs operationally. What each trigger would need (detail in
`HANDOVER.md`, step 4):

| zone | live source | gap to close |
|---|---|---|
| Teso | the IBF portal's trigger state (URCS / 510), daily | an account or API feed; the portal's state *is* the trigger. Own check: adapt `ifrc_reproduction.py` to the GloFAS v4 per-member forecast (EWDS) |
| Teso fallback | team FloodScan rasters (~2 days behind) | a daily district extraction |
| Elgon, Karamoja, Adjumani rain | CHIRPS3-GEFS 5-day forecast, daily | recalibrate first: every rain threshold is on CHIRPS-GEFS v2, discontinued 1 Jul 2026 |
| Elgon (partner trigger) | depends on the partner's processing | waits on the partner |
| Adjumani lake leg | NASA Global Water Monitor lake levels (10-day passes, weeks of lag) | a scheduled refresh, keeping the 3-pass median filter |

The templates are the team's other flood monitors: Databricks jobs from a bundle, writing through
`ocha-stratus` and emailing through Listmonk, as in
[nga-flooding-monitoring](../../pipelines/nga-flooding-monitoring.md) and
[tcd-flooding-monitoring](../../pipelines/tcd-flooding-monitoring.md), with the run-mode
conventions in [email-testing](../../infrastructure/email-testing.md). Until then, the handover
proposes a manual weekly check through October: the IBF portal for Teso, and the CHIRPS3-GEFS
district values against the thresholds (after the v2/v3 check).

## Historical activations

**Never activated** (`activations: []`): there is no envelope to release. Uganda's only flood AA
activation so far is URCS's EAP2021UG01 on 15 Nov 2023 (operation MDRUG048), which belongs to a
different, non-OCHA framework even though Teso now uses the same trigger. See
`extra.operational_ifrc_eap` and
[external-frameworks/ifrc/uga-flood.md](../../external-frameworks/ifrc/uga-flood.md). CERF's two
Uganda flood allocations (2007, 2020) were rapid-response, not AA (`extra.cerf_flood_allocations`).
The per-zone record above is simulated, not real.

## Key decisions & rationale

**Zones trigger independently, each all-in (22 Sep 2026).** An earlier design shared one overall
1-in-3 budget across the four zones, tilted by recorded people affected, and scored by calendar
year. It was replaced by a per-zone rate equal to the zone's own major-season frequency and by
event matching. Allocation options across zones are on `/triggers/`.

**The window is 1 October to 31 December (23 Sep 2026)**, because planning runs into September
and the funding does not run past March. The cost: the window misses the flood peak (August in
three zones), and the indicators peak earlier still (April rain, August GloFAS). These triggers
catch few major floods, and the handover says so as its headline.

**Teso takes the IFRC/URCS trigger for alignment, not skill (29 Sep 2026).** No GloFAS reading has
anticipatory skill for Teso in this window: Teso's October floods are the tail of a wet
August-September, and the landscape state on 1 October predicts them better than any rain signal.
Aligning with URCS means OCHA/CERF money would move on the same signal as URCS's own early
action. The
trigger was rebuilt from the portal's code, not the EAP's prose: each area is judged at its
largest river cell, so Katakwi, Soroti and Ngora are read on the Lake Bisina-Awoja channel (fed
from Elgon), Amuria and Kapelebyong on the Akokoro, and Serere on Lake Kyoga, not at G5196 alone.
The level, probability and lead of the first draft were right (own 5-yr level at G5196: 59 m³/s;
official map: 61).

**Frequency-matched return periods, and a fix to the raising rule (30 Sep 2026).** Raising a
threshold "until a big catch would be lost" has no stopping point when there is no big catch; it
had parked Karamoja's bar 0.03 mm under a 140-affected card at 1-in-10. `raise_threshold` now
stays at the frequency-matched level in that case (Karamoja back to 1-in-5.2). Elgon and
Adjumani, which do protect big catches, are unchanged, with thin margins: that is the known cost
of the rule on 25 seasons.

**Adjumani: the lake leg alone, not the compound rule (30 Sep 2026).** A lake-AND-rain rule looked
better (4 activations, catching 2020 and 2023) but was chosen after seeing 2023, and the rain
condition does little work (some district reaches 1-in-3 in 17 of 25 seasons). The lake leg alone
at 1-in-5 to 1-in-6.5 catches the same two seasons, on 1 October, and should be stated plainly as
"activate when the Nile is already high". There is no anticipatory lead in this window.

**Observed-flood fallback in Teso only.** FloodScan usability is judged per district on
rank-based evidence, never on absolute extent. The fallback catches October 2021 in Teso for one
extra false alarm. It catches nothing in Elgon or Karamoja in this window, and no Adjumani district
passes the usability check. In Karamoja the rain forecast beats FloodScan in 6 of the 7 districts
with their own record.

**An independent review of the three judgement calls** (IFRC reproduction, Adjumani, Karamoja)
by a separate reasoning model on 30 Sep 2026, with its numbers re-checked, changed three things:
the IFRC numbers are labelled a stand-in, the Adjumani compound rule is no longer recommended,
and the raising rule was fixed. Detail: `HANDOVER.md` section 4.

**Unpublished partner material stays out of the public repo and site.** Partner parameters live
only in gitignored config and on the two restricted pages; this page says no more than that a
partner draft exists.

## Changes from previous version

`supersedes: null`: no earlier version of this framework exists. This page was rewritten at
handover (30 Sep 2026) from the spoke repo. The 18 Sep 2026 draft had been compiled from
search-engine summaries without access to the repo or the site. It left thresholds and districts
unresolved, and described an observed-flood backstop in every zone, Karamoja sub-zoned by basin
and Elgon moving to ECMWF. In the repo the backstop helps only in Teso, Karamoja is judged per
district, and nothing moves Elgon to ECMWF.

## Open questions / known issues

1. **Teso fidelity:** ask URCS / 510 for the IBF portal's trigger history since 2021, its
   boundary file and per-area thresholds, and whether its notifications list every triggered
   area. "Did Katakwi or Serere trigger in November 2023?" settles most of it. Compare with
   `outputs/triggers/ifrc_district_days.csv`.
2. **Is EAP2021UG01 live for Oct-Dec 2026?** If a renewed EAP changes districts, probability or
   return period, Teso's trigger follows it.
3. **Which Teso districts count:** the six zone districts (current) or the EAP's high-risk
   districts in Teso (Katakwi, Amuria, Ngora; Kumi is placed in the Elgon lowlands here). The
   backtest is the same either way.
4. **Elgon** waits on a partner confirming how it processes its trigger.
5. **Karamoja:** 1-in-5.2 by the rule, or 1-in-4 to also catch November 2008 (the zone's largest
   Oct-Dec flood, one rank short); district mean or wettest pixel (one run); all-in for the zone
   or per district (a funding question for the country team). The zone has one or two catchable
   Oct-Dec seasons in 25.
6. **Adjumani:** adopt the lake leg alone (recommended) or keep the two-leg draft; check the
   September 2023 onset, and whether the 2004 and 2008 "major" events are really this zone's (they
   look like national EM-DAT totals apportioned to districts).
7. **Recalibrate the rain thresholds on CHIRPS3-GEFS** before any monitoring.
8. **Monitoring** (see above), and whether a manual weekly check covers October in the meantime.
9. **Severity 3+ scope in Teso** is the working group's decision.
10. **GloFAS is not stationary in Teso:** its agreement with FloodScan swings by era (2020 is the
    model's record year in an ordinary satellite season). A third opinion (DWRM gauge) is low
    priority now that Teso follows IFRC; Google Flood Hub has no gauges in Uganda
    ([google-flood-hub](../../apps/google-flood-hub.md)).
11. **Later design round:** longer rainfall windows (2007 was a long wet season) and
    readiness/action staging.
12. **Optional:** wire in IOM DTM's day-precision events for 2022 onward, and rerun the older
    results-page analyses (see discrepancies).
13. **KB PR #624** (methods: choosing the area a threshold is calibrated on) is still open.
