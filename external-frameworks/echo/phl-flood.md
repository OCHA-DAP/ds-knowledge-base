---
content_type: framework-external
framework: echo-phl-flood
org: ECHO
country_iso3: PHL
hazard: flood
status: active
valid_until: null
trigger_summary: >-
  Barangay-level river-gauge/flood-warning trigger in Cotabato City: when the Tamontaka
  River warning level reaches "orange" (alert), pre-registered households receive cash
  assistance before the flood peak (one source states a 5-day lead time), ahead of the
  point where an evacuation would be warranted.
data_sources: []
prearranged_funding_usd: 26800
funding_by_source: {ECHO: 26800}
target_people: 2614
framework_doc: https://oxfam.org.ph/echo-funded-project-strengthens-cotabato-villages-pre-disaster-response/
framework_doc_date: 2022-07-19
sources:
- https://oxfam.org.ph/echo-funded-project-strengthens-cotabato-villages-pre-disaster-response/
- https://oxfam.org.ph/marginalized-bangsamoro-project-participants-go-high-tech-in-money-matters/
- https://oxfam.org.ph/flood-assistance-helps-poor-bangsamoro-families-avoid-debt/
- https://oxfam.org.ph/ex-ofw-starts-pastil-business-through-flooding-cash-grant/
- https://oxfam.org.ph/what-we-do/anticipatory-action/
- https://www.early-action-reap.org/reap-anticipatory-action-enabling-environment-case-studies-philippines
- https://events.anticipation-hub.org/global-dialogue-platform-2022/agenda/
- https://www.anticipation-hub.org/experience/global-map
activations: []
last_checked: '2026-07-31'
extra:
  hub_captions:
  - '2023: Flood (ECHO) [Community Organizers Multiversity] [Cotabato City local government
    unit] [Global Parametrics] [Maya] [Oxfam] [People’s Disaster Risk Reduction Network]'
  hub_years:
  - '2023'
  implementing:
  - Community Organizers Multiversity
  - Cotabato City local government unit
  - Global Parametrics
  - Maya
  - Oxfam
  - People’s Disaster Risk Reduction Network
  project_name: >-
    Strengthening Urban Preparedness through Pre-emptive Action (SUPPA / SUPPA-BARMM),
    ECHO/EU Civil Protection and Humanitarian Aid Operations-funded, led by Oxfam
    Pilipinas.
  scope_note: >-
    Best-documented phase (2019-2022) covers five barangays of Tamontaka, Cotabato City
    (~300 families per cohort reported across articles: Tamontaka 3, Tamontaka 4), with
    Oxfam Philippines, IDEALS Inc., People's Disaster Risk Reduction Network (PDRRN) and
    Humanity & Inclusion as partners, and PayMaya (rebranded "Maya" in 2021) as the cash
    disbursement channel. Search indexes of REAP's Philippines case study and the
    Anticipation Hub's 2022 Global Dialogue Platform agenda additionally describe an
    expanded "SUPPA-BARMM" phase covering both Cotabato City and Marawi.
  no_activation_dates_found: >-
    Sources describe recurring trigger-based cash releases (four disbursements reported
    by mid-2022: face-to-face, then Palawan Pawnshop remittance, then two via
    PayMaya/Maya accounts) tied to river-level alerts each rainy season, but no article
    gives dated, event-specific activations (cf. `activations: []`) — recorded as
    ongoing anticipatory disbursement rather than itemized activations.
  schema_strain: >-
    No standalone EAP/protocol document (unlike the IFRC PHL flood EAP) was found for
    this framework; `framework_doc` is the most detailed Oxfam Pilipinas news article
    found, not a formal plan. The Hub's 2023 partner list (Community Organizers
    Multiversity, Cotabato City LGU, Global Parametrics, Maya) only partially overlaps
    the well-documented 2019-2022 SUPPA partner list (Oxfam, IDEALS, PDRRN, Humanity &
    Inclusion) — likely a later/expanded phase (see `extra.scope_note`) that is not
    separately documented with its own public trigger design or funding breakdown; the
    role Global Parametrics plays here (e.g. whether it supplies a parametric
    index/threshold, as it does for Oxfam's typhoon-focused B-READY project elsewhere in
    the Philippines) could not be confirmed from public sources. `data_sources` left
    empty because the river-gauge/warning-level system is locally operated (Cotabato
    City LGU) and no named forecast product (e.g. PAGASA feed) was confirmed. Direct
    fetch of `early-action-reap.org` and `preventionweb.net` case-study pages failed
    (expired cert / 403); details from those sources are drawn from indexed excerpts.
    `prearranged_funding_usd`/`target_people` are carried over from the Hub inventory
    record and could not be independently verified against a primary document.
visibility: public
---

# ECHO — Philippines flood (Cotabato City)

## Summary
Oxfam Pilipinas leads an ECHO/EU-funded anticipatory cash-transfer project — Strengthening
Urban Preparedness through Pre-emptive Action (SUPPA, later expanded as SUPPA-BARMM) — for
flood-prone urban barangays of Cotabato City, in the Bangsamoro Autonomous Region in Muslim
Mindanao (BARMM). Registered households receive pre-agreed cash assistance, disbursed via
the Maya (formerly PayMaya) digital-wallet platform, when the Tamontaka River reaches an
"orange" alert warning level — ahead of the point where evacuation would be needed. It is
a separate, Oxfam/ECHO-run instrument; the Philippines has no OCHA/CERF collective
framework for flood (OCHA/CERF's only PHL framework, [`frameworks/phl-storms`](../../frameworks/phl-storms),
covers tropical cyclones), so this does not sit alongside an OCHA-coordinated piece.

## Trigger
A local river-gauge/warning-level trigger for the Tamontaka River in Cotabato City:
residents also feed in ground reports (photos of rising water) to the barangay government,
which assesses next steps. When the river warning reaches "orange" (alert) status,
pre-registered households receive cash — one source states assistance lands about 5 days
before the flood, "before the flood warning condition warrants an evacuation." The Hub's
2023 framework record additionally names Global Parametrics as an implementing partner,
which could suggest a parametric/forecast-index layer was added in a later phase, but no
public source confirms the specifics (see `extra.schema_strain`).

## Funding & scope
ECHO (EU Civil Protection and Humanitarian Aid Operations) is the sole funder identified
in all sources. The Anticipation Hub inventory records US$26,800 pre-arranged funding and
~2,614 people targeted (unverified against a primary document). Public case studies
describe smaller named cohorts within that total: ~300 families in Barangay Tamontaka 3,
236 families in Barangay Tamontaka 4 (out of 752 families/571 households village-wide) —
consistent with a project working barangay-by-barangay across Cotabato City. An expanded
phase ("SUPPA-BARMM") is described in secondary sources as also covering Marawi.

## Activations
No dated, event-specific activations found. Sources describe recurring, trigger-linked
cash disbursements — four rounds reported by mid-2022 (first face-to-face, then via
Palawan Pawnshop remittance, then two via PayMaya/Maya digital accounts) — tied to
river-warning alerts each rainy season, rather than one-off named events. See
`extra.no_activation_dates_found`.

## Sources
- **Authoritative:** [Oxfam Pilipinas — ECHO-funded project strengthens Cotabato village's pre-disaster response](https://oxfam.org.ph/echo-funded-project-strengthens-cotabato-villages-pre-disaster-response/) (19 Jul 2022)
- [Oxfam Pilipinas — Marginalized Bangsamoro project participants go high-tech in money matters](https://oxfam.org.ph/marginalized-bangsamoro-project-participants-go-high-tech-in-money-matters/)
- [Oxfam Pilipinas — Flood assistance helps poor Bangsamoro families avoid debt](https://oxfam.org.ph/flood-assistance-helps-poor-bangsamoro-families-avoid-debt/) (13 Jul 2022)
- [Oxfam Pilipinas — Ex-OFW starts 'pastil' business through flooding cash grant](https://oxfam.org.ph/ex-ofw-starts-pastil-business-through-flooding-cash-grant/)
- [Oxfam Pilipinas — Anticipatory Action overview](https://oxfam.org.ph/what-we-do/anticipatory-action/)
- [REAP — Philippines enabling-environment case study](https://www.early-action-reap.org/reap-anticipatory-action-enabling-environment-case-studies-philippines) (fetch failed; drawn from indexed excerpts, describes SUPPA-BARMM covering Cotabato City and Marawi)
- [Anticipation Hub Global Dialogue Platform 2022 agenda](https://events.anticipation-hub.org/global-dialogue-platform-2022/agenda/) (panel with Oxfam Pilipinas, Global Parametrics, Cotabato City LGU, PDRRN speakers)
- [Anticipation Hub global map](https://www.anticipation-hub.org/experience/global-map) (inventory record)
