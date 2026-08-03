---
content_type: framework-external
framework: netherlands-red-cross-zmb-drought
org: Netherlands Red Cross
country_iso3: ZMB
hazard: drought
status: active
valid_until: '2030-03-31'
trigger_summary: null
data_sources: []
prearranged_funding_usd: 541853
funding_by_source: {DREF-anticipatory: 541853}
target_people: 22530
framework_doc: https://reliefweb.int/report/zambia/zambia-drought-early-action-protocol-summary-march-2025-eap2024zm02
framework_doc_date: '2025-03'
sources:
- https://reliefweb.int/report/zambia/zambia-drought-early-action-protocol-summary-march-2025-eap2024zm02
- https://reliefweb.int/report/zambia/zambia-drought-early-action-protocol-summary-eap-no-eap2023cr02-operation-no-mdrzm025
- https://reliefweb.int/report/zambia/zambia-drought-early-action-protocol-annual-report-2025-eap-no-eap2023cr02-operation-no-mdrzm025
- https://goadmin.ifrc.org/api/v2/appeal/?code=MDRZM025
- https://510.global/2024/04/zambias-early-action-protocols-a-collaborative-journey/
- https://www.anticipation-hub.org/global-overview/countries/zambia/forecast-based-financing-fbf-in-the-zambia
- https://www.anticipation-hub.org/experience/global-map
activations: []
last_checked: '2026-07-28'
extra:
  hub_captions:
  - '2018: Drought (Netherlands Red Cross) [acted] [Action Against Hunger] [Action Socio Sanitaire
    Organisation Secours] [Action Aid Somaliland] [Caritas Bulawayo]'
  hub_years:
  - '2018'
  implementing:
  - Zambia Red Cross Society
  eap_no: EAP2024ZM02
  eap_no_prior: EAP2023CR02
  operation_no: MDRZM025
  hub_record_data_quality: >-
    The Hub global-map record that seeded this stub (raw layer "under-development",
    year 2018) looks corrupted rather than a real framework record: its
    prearranged_funding_usd and target_people fields were identical placeholder-like
    values (234234/234234), its framework_link was just the generic global-map URL
    (not a specific record page), and its "implementing" list mixed organisations tied
    to unrelated countries/hazards (Action Aid Somaliland, Caritas Bulawayo/Zimbabwe)
    alongside the literal token "acted" as if it were an org name. No independent
    public source corroborates a Netherlands-Red-Cross-owned Zambia drought framework
    dated 2018. The raw caption is preserved in hub_captions/hub_years above for
    audit only; the `implementing` list has been corrected to what research actually
    found (Zambia Red Cross Society).
  actual_framework: >-
    No 2018 NLRC-owned Zambia drought framework could be found, but a real, current
    Zambia Red Cross Society (ZRCS) drought Early Action Protocol does exist —
    EAP2024ZM02, operation MDRZM025 (an earlier internal reference, EAP2023CR02,
    appears on related ReliefWeb documents for the same operation number). Per the
    IFRC GO API, MDRZM025 ("Zambia - Drought EAP2024ZM02") is a DREF appeal that
    started 2025-03-27, runs to 2030-03-31, is fully funded at US$541,853, targets
    22,530 people, and lists Zambia Red Cross Society as the implementing
    organisation. This page documents that real, verifiable framework rather than
    the corrupted 2018 stub record, since it is the only Zambia-drought Red Cross
    framework found in public sources.
  coordination: >-
    Not a component of an OCHA/CERF collective framework — this KB holds no
    frameworks/ page for Zambia drought. The drought EAP is Zambia Red Cross
    Society's own IFRC-family Early Action Protocol (DREF-financed), developed with
    IFRC, the Netherlands Red Cross's 510 data initiative, the RCRC Climate Centre,
    and Zambia's National Technical Working Group for Anticipatory Action (chaired
    by DMMU), funded via the IFRC-EU Programmatic Partnership and the Dutch Ministry
    of Foreign Affairs. It grew out of the same Response Preparedness
    II / forecast-based-financing programme as Zambia's flood EAP, catalogued
    separately at external-frameworks/ifrc/zmb-flood.md under org IFRC. Per this
    KB's org-attribution convention (org = the org that owns/operates the
    framework), the drought EAP's operating org is properly IFRC/Zambia Red Cross
    Society, not Netherlands Red Cross — NLRC is a technical-development and
    co-funding partner, as it also is for the flood EAP. `org` is left as
    `Netherlands Red Cross` here only because this page's identity was inherited
    from the corrupted Hub stub and this enrichment pass is scoped to this one
    file; a future pass should consider re-homing this content under
    external-frameworks/ifrc/zmb-drought.md.
  development: >-
    Grew out of Zambia's Response Preparedness II programme and a subsequent
    Forecast-based Financing project (ZRCS + IFRC + Netherlands Red Cross/510 +
    RCRC Climate Centre). An October 2023 workshop in Monze, Southern Province,
    finalized the drought EAP's impact sectors and prioritized early actions
    (validated with drought-vulnerable communities) alongside a revision of the
    existing flood EAP; the DREF appeal (MDRZM025) itself started 2025-03-27.
  schema_strain: >-
    No numeric trigger indicator, threshold, or lead time could be sourced: the
    ReliefWeb EAP summary/annual-report pages (framework_doc and two of the sources
    above) return HTTP 403 to automated fetch, and no Anticipation-Hub-hosted PDF
    mirror for EAP2024ZM02 was found in this pass — so `trigger_summary` and
    `data_sources` are left null/[] rather than guessed. No activation of this
    drought EAP was found in public sources; Zambia's major 2024-2025 drought
    response (the OCHA-coordinated Drought Flash Appeal, and separately the IFRC
    emergency appeal MDRZM022) was ordinary humanitarian response, not a confirmed
    trigger of this EAP, and is not counted as an activation here. The IFRC GO
    appeal amount (US$541,853) is taken as reported by the API; DREF budgets are
    usually CHF-denominated and the underlying currency was not independently
    confirmed.
visibility: public
---

# Netherlands Red Cross — Zambia drought

## Summary
The framework identity here (org: Netherlands Red Cross, ZMB, drought) traces to a
2018 Anticipation Hub inventory record that, on inspection, looks corrupted (see
`extra.hub_record_data_quality`) rather than a real, documented framework — no
independent public source describes a Netherlands-Red-Cross-owned Zambia drought
programme from 2018. Research instead found a real, current Zambia drought
framework: the Zambia Red Cross Society's (ZRCS) drought Early Action Protocol
(EAP2024ZM02, operation MDRZM025), developed 2023-2025 with IFRC, the Netherlands
Red Cross's 510 data initiative, and the RCRC Climate Centre, and financed through
a fully-funded DREF appeal (US$541,853, 22,530 people targeted, 2025-03-27 to
2030-03-31). It sits alongside Zambia's flood EAP (catalogued at
`external-frameworks/ifrc/zmb-flood.md`) as part of the same broader ZRCS/IFRC
forecast-based-financing programme. Per this KB's org-attribution convention the
drought EAP's actual operating organisation is IFRC/ZRCS, not Netherlands Red
Cross — see `extra.coordination`.

## Trigger
Not sourced. The authoritative ReliefWeb documents (EAP summary and annual report,
see `sources`) return HTTP 403 to automated fetch, and no Hub-hosted PDF mirror for
EAP2024ZM02 was located in this pass, so the specific indicator, threshold and lead
time are unknown from the sources reached — see `extra.schema_strain`.

## Funding & scope
Per the IFRC GO API (appeal MDRZM025, "Zambia - Drought EAP2024ZM02"): a DREF
appeal starting 2025-03-27 and running to 2030-03-31, fully funded at US$541,853,
targeting 22,530 people, implemented by the Zambia Red Cross Society. An earlier
internal reference, EAP2023CR02, appears on related ReliefWeb documents for the
same operation number and appears to be a prior/working code for the same
protocol. The EAP was developed with support from IFRC, the Netherlands Red
Cross's 510 initiative, and the RCRC Climate Centre, funded via the IFRC-EU
Programmatic Partnership and the Dutch Ministry of Foreign Affairs; an October
2023 workshop in Monze finalized its impact sectors and prioritized early actions.

## Activations
None known. No public source documents a trigger event for EAP2024ZM02 /
EAP2023CR02. Zambia's severe 2024-2025 drought (declared a national disaster in
February 2024) was met with separate, non-anticipatory humanitarian response
mechanisms — an OCHA-coordinated Drought Flash Appeal and the IFRC emergency
appeal MDRZM022 — which are not activations of this EAP and are not conflated
with it here.

## Sources
- **Most specific found:** [Zambia — Drought: Early Action Protocol Summary, March 2025 (EAP2024ZM02)](https://reliefweb.int/report/zambia/zambia-drought-early-action-protocol-summary-march-2025-eap2024zm02) (ReliefWeb; content 403s to automated fetch, cited by title/metadata only)
- [Zambia — Drought: Early Action Protocol Summary (EAP No. EAP2023CR02, Operation No. MDRZM025)](https://reliefweb.int/report/zambia/zambia-drought-early-action-protocol-summary-eap-no-eap2023cr02-operation-no-mdrzm025)
- [Zambia — Drought: Early Action Protocol Annual Report 2025 (EAP No. EAP2023CR02, Operation No. MDRZM025)](https://reliefweb.int/report/zambia/zambia-drought-early-action-protocol-annual-report-2025-eap-no-eap2023cr02-operation-no-mdrzm025)
- [IFRC GO — appeal MDRZM025](https://goadmin.ifrc.org/api/v2/appeal/?code=MDRZM025) (machine-readable dates/budget/beneficiaries/implementing org)
- [510 — "Zambia's Early Action Protocols: A Collaborative Journey" (April 2024)](https://510.global/2024/04/zambias-early-action-protocols-a-collaborative-journey/) (development history, October 2023 Monze workshop)
- [Anticipation Hub — Forecast-based financing (FbF) in Zambia](https://www.anticipation-hub.org/global-overview/countries/zambia/forecast-based-financing-fbf-in-the-zambia) (programme overview; flood-focused, confirms NLRC/IFRC/ZRCS/Climate Centre partnership)
- [Anticipation Hub global map](https://www.anticipation-hub.org/experience/global-map) (original 2018 inventory record — see `extra.hub_record_data_quality` for why it was not used as-is)
