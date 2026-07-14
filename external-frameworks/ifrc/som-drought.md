---
content_type: framework-external
framework: ifrc-som-drought
org: IFRC
country_iso3: SOM
hazard: drought
status: active
valid_until: 2029-08-31
trigger_summary: >-
  District-level SPI-12 forecast below -1, combined with a FEWS NET population-weighted
  food-insecurity projection of ≥0.7 and an ICPAC/GHACOF seasonal outlook for below-normal
  rainfall; triggered the first time 31 Jan 2025 for Bari, Mudug, Sool and Togdheer ahead
  of the 2025 Gu (Mar-May) season, ~1-2 months lead time before projected impact.
data_sources: [SPI, FEWSNET, ICPAC]
prearranged_funding_usd: 945056
funding_by_source: {DREF-anticipatory: 945056}
target_people: 30000
framework_doc: https://www.anticipation-hub.org/download/file-4739
framework_doc_date: 2024-08-28
sources:
  - https://www.anticipation-hub.org/download/file-4739
  - https://reliefweb.int/report/somalia/somalia-drought-early-action-protocol-no-2024so01-summary-august-2024
  - https://www.anticipation-hub.org/news/somali-red-crescent-society-activates-its-early-action-protocol-for-drought
  - https://www.climatecentre.org/15087/somali-red-crescent-activates-early-action-protocol-for-spreading-drought/
  - https://reliefweb.int/report/somalia/somalia-drought-early-action-protocol-notification-operation-no-mdrso019-january-2025
  - https://reliefweb.int/report/somalia/somalia-drought-early-action-protocol-notification-operation-update-no-mdrso019-12-may-2025
  - https://goadmin.ifrc.org/api/v2/appeal/?code=MDRSO019
  - https://www.anticipation-hub.org/experience/global-map
activations:
  - date: 2025-01-31
    url: https://www.climatecentre.org/15087/somali-red-crescent-activates-early-action-protocol-for-spreading-drought/
    note: >-
      First trigger of EAP2024SO01 — SPI/FEWS NET/ICPAC thresholds met for Bari, Mudug,
      Sool and Togdheer ahead of poor Gu rains. CHF 373,102 (~US$410,000) released from
      the DREF anticipatory pillar for early-warning messaging, multi-purpose cash
      transfers and water-point rehabilitation, targeting ~30,000 people (a later
      operational breakdown split this as 9,000 for drought-driven food insecurity and
      7,200 for water scarcity). The 12 May 2025 operation update reports water-point
      rehabilitation could not be completed (spare parts unavailable) and SRCS requested
      a two-month no-cost extension; a post-distribution monitoring / lessons-learned
      workshop was pending completion.
last_checked: '2026-07-14'
extra:
  hub_captions:
  - '2024: Drought (IFRC) [Somali Red Crescent Society]'
  hub_years:
  - '2024'
  implementing:
  - Somali Red Crescent Society
  eap_no: 2024SO01
  operation_no: MDRSO019
  funding_note: >-
    IFRC GO lists a single fully-funded DREF budget of US$945,056 (CHF-denominated
    originally) running 2024-08-16 to 2029-08-31, 30,000 people targeted — the figures
    used above. Two other CHF figures appear in related documents and are not fully
    reconciled: CHF 530,533 as the DREF allocation dated 16 Aug 2024 (per the 12 May 2025
    operation update) and CHF 327,319.92 as an "early actions" budget line for 34,194
    people (per the EAP2024SO01 summary doc) — likely different accounting cuts (total
    operation vs. trigger-specific tranche) of the same overall envelope rather than
    contradictory figures.
  partners: >-
    EAP developed with support from the German Red Cross, funded by the German Federal
    Foreign Office (per Anticipation Hub activation news); DREF anticipatory pillar funds
    the operational/trigger budget.
  coordination: >-
    Not a component of a collective OCHA/CERF framework. A separate, unrelated OCHA/CERF
    Somalia drought/famine AA pilot exists in this KB (frameworks/som-drought/2019.md,
    status retired, last activated Feb 2021) — it used IPC food-security projections as
    a proxy trigger and CERF finance, and has no documented link to this SRCS/IFRC EAP
    (different trigger indicators, funding source and timeline). Mentioned here only to
    avoid conflating the two.
  schema_strain: >-
    Hub inventory listed prearranged_funding_usd 602194 (stub value, source unclear);
    superseded above by the IFRC GO API figure (945056, fully funded) as the more
    authoritative live source. Precise SPI-12/FEWS NET numeric thresholds for the
    trigger were readable only via a secondary reliefweb summary, not the primary PDF
    (PDF text extraction was not possible in this pass — see framework_doc).
visibility: public
---

# IFRC — Somalia drought

## Summary
The Somali Red Crescent Society (SRCS) runs an Early Action Protocol (EAP2024SO01,
operation MDRSO019) for drought, approved by IFRC on 15 August 2024 and validated for
five years (to 31 August 2029). It is pre-financed by the DREF anticipatory pillar
(US$945,056, fully funded) and targets ~30,000 people in Somalia's northern/central
regions (Bari, Mudug, Sool, Togdheer) with early-warning messaging, multi-purpose cash
transfers and water-point rehabilitation. The EAP was developed with support from the
German Red Cross (funded by the German Federal Foreign Office) and triggered for the
first time on 31 January 2025.

## Trigger
District-level **SPI-12 forecast below -1**, combined with a **FEWS NET** population-
weighted food-insecurity projection of **≥0.7**, and an **ICPAC/GHACOF** seasonal outlook
for below-normal rainfall. At the January 2025 trigger, observed SPI-7 values were
already around -0.8 across most of Somalia ahead of the Gu (March-May) rains, giving
roughly 1-2 months of lead time before the projected drought impact window (from May
onward). Full numeric thresholds are stated in the EAP document itself (`framework_doc`);
this summary draws on a secondary description since the source PDF could not be
text-extracted in this pass.

## Funding & scope
US$945,056 pre-arranged from the DREF anticipatory pillar (fully funded), running
2024-08-16 to 2029-08-31, targeting 30,000 people. On the January 2025 trigger, CHF
373,102 (~US$410,000) was released for early actions in Bari, Mudug, Sool and Togdheer.
Related documents cite other CHF figures for the same operation (CHF 530,533 total DREF
allocation; CHF 327,319.92 for a 34,194-person "early actions" line) that are not fully
reconciled with the headline US$945,056 — see `extra.funding_note`.

## Activations
- **31 January 2025** — first (and to date only) trigger. Early-warning messaging,
  multi-purpose cash transfers, and water-point rehabilitation across Bari, Mudug, Sool
  and Togdheer, targeting ~30,000 people (later broken out as 9,000 for food insecurity,
  7,200 for water scarcity). As of the 12 May 2025 operation update, water-point
  rehabilitation was incomplete (spare parts unavailable) and SRCS had requested a
  two-month no-cost extension; no final/lessons-learned report was located as of this
  page's last check.

## Sources
- **Authoritative:** [EAP2024SO01 document (Anticipation Hub, 28 Aug 2024)](https://www.anticipation-hub.org/download/file-4739) · [EAP2024SO01 summary, Aug 2024 (ReliefWeb)](https://reliefweb.int/report/somalia/somalia-drought-early-action-protocol-no-2024so01-summary-august-2024)
- [Somali Red Crescent activates EAP for drought (Anticipation Hub news)](https://www.anticipation-hub.org/news/somali-red-crescent-society-activates-its-early-action-protocol-for-drought) · [Climate Centre coverage of the same activation](https://www.climatecentre.org/15087/somali-red-crescent-activates-early-action-protocol-for-spreading-drought/)
- [EAP notification, operation MDRSO019, Jan 2025 (ReliefWeb)](https://reliefweb.int/report/somalia/somalia-drought-early-action-protocol-notification-operation-no-mdrso019-january-2025) · [Operation update, 12 May 2025 (ReliefWeb)](https://reliefweb.int/report/somalia/somalia-drought-early-action-protocol-notification-operation-update-no-mdrso019-12-may-2025)
- [IFRC GO — appeal MDRSO019](https://goadmin.ifrc.org/api/v2/appeal/?code=MDRSO019) (machine-readable budget/status/beneficiaries)
- [Anticipation Hub global map](https://www.anticipation-hub.org/experience/global-map) (original inventory listing)
