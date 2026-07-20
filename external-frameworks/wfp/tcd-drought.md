---
content_type: framework-external
framework: wfp-tcd-drought
org: WFP
country_iso3: TCD
hazard: drought
status: active
valid_until: "2027-03"
trigger_summary: >-
  Collective OCHA/CERF framework trigger (not WFP-specific): fires if ECMWF SEAS5
  seasonal-forecast pixel-percentile rank shows ≥20% of the AOI in the lowest 15th
  historical percentile for JAS rainfall (Window 1, SEAS5 issued March/April; Window 2,
  SEAS5 issued May/June), OR ACF/GeoSahel cumulative biomass by early September is
  <84.5% of its long-term trend-adjusted prediction (Window 3). WFP implements Food
  Security activities under Windows 1 and 2 when the forecast trigger fires.
data_sources: [SEAS5, Biomasse-ACF]
prearranged_funding_usd: 1968000
funding_by_source: {CERF: 1968000}
target_people: null
framework_doc: https://www.unocha.org/publications/report/chad/cadre-de-laction-anticipatoire-secheresse-au-tchad-version-finale-du-3-mars-2025
framework_doc_date: "2025-03-03"
sources:
  - https://www.unocha.org/publications/report/chad/cadre-de-laction-anticipatoire-secheresse-au-tchad-version-finale-du-3-mars-2025
  - https://www.anticipation-hub.org/news/from-preparedness-to-activation-partners-act-to-anticipate-drought-in-chad
  - https://www.anticipation-hub.org/experience/anticipatory-action-in-the-world/chad
  - https://centre.humdata.org/model-report-anticipatory-action-trigger-for-drought-in-chad/
  - https://www.anticipation-hub.org/experience/global-map
activations:
  - date: "2026-04"
    url: https://www.anticipation-hub.org/news/from-preparedness-to-activation-partners-act-to-anticipate-drought-in-chad
    note: >-
      Window 1 (livelihoods, main harvest) fired 30 April 2026 on the SEAS5 April issue.
      WFP implements Food Security activities under this window (WFP share $1,112,000 of
      the $3.05M window envelope).
  - date: "2026-05"
    url: https://www.anticipation-hub.org/news/from-preparedness-to-activation-partners-act-to-anticipate-drought-in-chad
    note: >-
      Window 2 (livelihoods, market garden & livestock) fired 9 May 2026 on the SEAS5 May
      issue. WFP share $856,000 of the $1.33M window envelope.
last_checked: '2026-07-20'
extra:
  hub_captions:
  - '2023: Drought (WFP) [WFP]'
  hub_years:
  - '2023'
  implementing:
  - WFP
  coordination: >-
    This is WFP's component of the OCHA/CERF collective anticipatory action framework
    for Chad drought (see frameworks/tcd-drought/ — endorsed 2025-03-03, up to $8M CERF,
    7 Sahelian provinces, three trigger windows monitored by OCHA CHD). WFP is one of
    five implementing agencies (with FAO, UNICEF, UNFPA, WHO) and receives $1,968,000 of
    the $8M envelope for Food Security activities under Windows 1 and 2. No evidence was
    found that WFP publishes an independent Chad-drought AA framework document separate
    from this collective one — this page is WFP's slice of the OCHA page, not a
    standalone framework, per the component-of-collective rule in
    external-frameworks/README.md.
  schema_strain: >-
    The Anticipation Hub global-map inventory record for this stub gave $120,000
    pre-arranged funding and 62,200 target people, attributed to WFP alone. Neither
    figure reconciles with the 2025-03-03 collective framework doc, which gives WFP a
    $1,968,000 funding share (Window 1 $1,112,000 + Window 2 $856,000) and only an
    overall (not per-agency) target of 260,000 people. The Hub figures may be inherited
    from the superseded 2022 pilot (total budget $10M vs $8M in 2025) rather than the
    current design; no WFP-specific target-people breakdown was found in any public
    source, so target_people is left null rather than guessed. prearranged_funding_usd
    and funding_by_source above use the reconciled 2025 collective-framework figures for
    WFP's share, not the unreconciled Hub numbers.
visibility: public
---

# WFP — Chad drought

## Summary
WFP is one of five UN agencies (with FAO, UNICEF, UNFPA, WHO) implementing the OCHA/CERF
collective anticipatory action framework for drought in Chad (endorsed 2025-03-03, up to
$8M CERF across seven Sahelian provinces). This is **not an independently-published WFP
framework**: no separate WFP Chad-drought AA document was found in public sources — WFP's
role is a Food Security-sector implementation slice of the OCHA collective design,
funded at $1,968,000 across the framework's two forecast-based windows.

## Trigger
The trigger is the collective framework's, not WFP-specific. **Window 1** (livelihoods,
main harvest) fires if an ECMWF SEAS5 forecast issued in March or April shows at least
20% of the seven-province AOI with forecast JAS (Jul–Aug–Sep) rainfall in the lowest 15th
historical percentile. **Window 2** (livelihoods, market garden & livestock) applies the
same rule to the May/June SEAS5 issue. **Window 3** (early humanitarian impact,
observational) fires if cumulative ACF/GeoSahel biomass by early September is below
84.5% of a long-term trend-adjusted prediction. WFP implements Food Security activities
under Windows 1 and 2 only; it has no funding line under Window 3. Full derivation:
OCHA's [model report](https://centre.humdata.org/model-report-anticipatory-action-trigger-for-drought-in-chad/)
and the [2025-03-03 framework doc](https://www.unocha.org/publications/report/chad/cadre-de-laction-anticipatoire-secheresse-au-tchad-version-finale-du-3-mars-2025).

## Funding & scope
WFP receives $1,968,000 of the framework's $8M CERF envelope: $1,112,000 under Window 1
and $856,000 under Window 2, both for Food Security. The framework overall targets
260,000 people across all five agencies and sectors (Food Security, Nutrition, WASH,
Health, Child Protection, GBV, Education) — no WFP-specific target-people figure is
published; see `extra.schema_strain` for the unreconciled Hub-inventory figure
(62,200 people, $120,000) inherited from this stub's original creation. Geographic scope:
Lac, Kanem, Bahr-El-Gazal, Sila, Wadi Fira, Batha, Ouaddaï provinces. CERF funding is
subject to a two-year activation window from the 2025-03-03 endorsement (i.e. by
2027-03).

## Activations
The collective framework activated twice in the 2026 season, both within WFP's funded
windows:
- **30 April 2026 — Window 1.** SEAS5 April issue met the forecast threshold; ~$3.05M
  released for the window, of which WFP's Food Security share is $1,112,000.
- **9 May 2026 — Window 2.** SEAS5 May issue met the threshold; ~$1.33M released, of
  which WFP's share is $856,000.

Both are per-window (not all-in) activations — see the OCHA framework page
(`frameworks/tcd-drought/`) for the full activation record and Window 3 status. As of the
2025-03-03 endorsement the framework had never triggered before 2026.

## Sources
- **Authoritative:** [Cadre de l'action anticipatoire — Sécheresse au Tchad, version finale du 3 mars 2025](https://www.unocha.org/publications/report/chad/cadre-de-laction-anticipatoire-secheresse-au-tchad-version-finale-du-3-mars-2025) (OCHA/CERF collective framework doc; WFP funding table therein)
- [Anticipation Hub — 2026 activation news](https://www.anticipation-hub.org/news/from-preparedness-to-activation-partners-act-to-anticipate-drought-in-chad) (30 Apr / 9 May 2026 activations, $4.4M total)
- [Anticipation Hub — Chad country page](https://www.anticipation-hub.org/experience/anticipatory-action-in-the-world/chad) (active-frameworks table; source of the unreconciled WFP $120,000/62,200-people figures)
- [OCHA Centre for Humanitarian Data — model report on the Chad drought trigger](https://centre.humdata.org/model-report-anticipatory-action-trigger-for-drought-in-chad/)
- [Anticipation Hub global map](https://www.anticipation-hub.org/experience/global-map) (original inventory record)
- Internal cross-link: `frameworks/tcd-drought/` (the OCHA collective framework this page is a component of)
