---
content_type: framework-external
framework: ifrc-mmr-heatwave
org: IFRC
country_iso3: MMR
hazard: heatwave
status: active
valid_until: null
trigger_summary: >-
  Myanmar Red Cross Society's Simplified EAP releases pre-agreed early actions (cash
  assistance, cooling support, water distribution) for vulnerable urban populations in
  heatwave-prone townships ahead of forecast/observed severe heat; the public sEAP
  document does not state a specific temperature/heat-index threshold or lead-time figure
  (see `extra.schema_strain`).
data_sources: []
prearranged_funding_usd: 200000
funding_by_source: {DREF-anticipatory: 200000}
target_people: 10220
framework_doc: https://reliefweb.int/report/myanmar/myanmar-urban-heatwaves-simplified-early-action-protocol-seap-no-seap2024mm01-operation-no-mdrmm022
framework_doc_date: 2024-12-13
sources:
  - https://reliefweb.int/report/myanmar/myanmar-urban-heatwaves-simplified-early-action-protocol-seap-no-seap2024mm01-operation-no-mdrmm022
  - https://www.anticipation-hub.org/download/file-5058
  - https://go-api.ifrc.org/api/DownloadFile/89567/sEAP2024MM01_MDRMM022
  - https://reliefweb.int/report/myanmar/myanmar-urban-heatwaves-simplified-early-action-protocol-2025-annual-report-seap-no-seap2024mm01-operation-no-mdrmm022-31-march-2026
  - https://go-api.ifrc.org/api/DownloadFile/89569/MDRMM022eapar2025
  - https://goadmin.ifrc.org/api/v2/appeal/?code=MDRMM022
  - https://go.ifrc.org/emergencies/7603/details
  - https://www.ifrc.org/press-release/searing-temperatures-sweep-fire-across-asia-pacific-causing-distress-millions
  - https://www.anticipation-hub.org/experience/global-map
activations: []
last_checked: '2026-07-17'
extra:
  hub_captions:
  - '2024: Heat Wave (IFRC) [Myanmar Red Cross Society]'
  hub_years:
  - '2024'
  implementing:
  - Myanmar Red Cross Society
  eap_no: sEAP2024MM01
  operation_no: MDRMM022
  funding_detail: >-
    CHF 200,000 total DREF anticipatory-pillar allocation (reported as ~US$200,000 by
    IFRC GO, no separate conversion rate given), including CHF 45,722 earmarked for
    stock pre-positioning and branch readiness activities, with the remainder released
    on trigger. DREF appeal MDRMM022 approved 2024-12-11, status "Active" through
    2026-12-31 per IFRC GO.
  coverage: >-
    Urban heatwave risk in vulnerable/informal-settlement populations; document extracts
    reference Yangon (incl. Hlinethaya Township) and cite the 2010 Mandalay (47°C, ~230
    deaths), 2014 Mandalay (41.7°C, 9 deaths), and 2019 Yangon (42.2°C, 8 deaths)
    heatwaves as the risk rationale.
  related_reactive_response: >-
    A separate, earlier MRCS heatwave response (May 2024, pre-dating this sEAP's
    December 2024 approval) ran heat-prevention education across Ayeyarwady, Mandalay,
    Magway, Yangon, Bago, Tanintharyi, Kayin and Mon, plus cash assistance to 250+
    low-income families in Shwe Pyi Thar, Dala and Dagon Seikkan townships (Yangon),
    funded by German Red Cross — not DREF/EAP-funded and not counted as an EAP
    activation.
  schema_strain: >-
    Automated fetches of both the sEAP document (GO DownloadFile 89567) and the 2025
    annual report (GO DownloadFile 89569) could not reliably extract a specific
    trigger temperature/heat-index threshold or lead-time figure — the PDFs' text
    layers extracted inconsistently across repeated attempts. Could not confirm whether
    the trigger was actually met/activated during the severe Myanmar heatwave of
    April-May 2025 (widely reported, ~100 deaths per RFA); the CHF 45,722
    pre-positioning/readiness tranche is a standard EAP structural feature, not
    evidence of activation, so `activations` is left empty rather than guessed.
    GO appeal end_date of 2026-12-31 reflects the DREF operation's administrative
    window, not a stated framework validity end date, so `valid_until` is left null.
visibility: public
---

# IFRC — Myanmar heatwave

## Summary
The Myanmar Red Cross Society's Simplified Early Action Protocol for urban heatwaves
(sEAP2024MM01, DREF operation MDRMM022), approved 11 December 2024 and financed through
the IFRC DREF anticipatory pillar. Targets ~10,220 people in heatwave-vulnerable urban
areas (including Yangon) with pre-agreed early actions such as cash assistance, cooling
support, and water distribution.

## Trigger
Public documents describe the sEAP as triggering pre-agreed early actions ahead of
forecast/observed severe urban heat, but neither the sEAP summary nor the 2025 annual
report yielded an extractable specific temperature or heat-index threshold, monitored
forecast source, or lead-time figure in automated fetches (see `extra.schema_strain`) —
a one-liner is recorded here rather than a guessed number.

## Funding & scope
CHF 200,000 (~US$200,000, no separate conversion stated) allocated via the DREF
anticipatory pillar, fully funded as of the 2024-12-11 appeal approval. Of this,
CHF 45,722 is earmarked for stock pre-positioning and branch readiness, with the
remainder for trigger-based early action. Targets ~10,220 people in heatwave-prone
urban/informal-settlement areas, including Yangon (Hlinethaya Township referenced in
the sEAP text); the document cites historical Mandalay (2010, 2014) and Yangon (2019)
heatwave mortality as its risk rationale. DREF operation status "Active" through
2026-12-31 per IFRC GO.

## Activations
None confirmed. A separate, earlier MRCS response to the May 2024 Myanmar heatwave
(education campaigns across eight regions/states, cash assistance to 250+ families in
three Yangon townships) pre-dated this sEAP's December 2024 approval, was funded by
German Red Cross rather than DREF, and is not counted as an EAP activation. Whether the
sEAP's own trigger was met during the severe April-May 2025 Myanmar heatwave could not
be confirmed from available public sources — the CHF 45,722 readiness tranche is a
standard structural feature of the protocol, not itself evidence of a trigger-based
activation.

## Sources
- **Authoritative:** [sEAP summary, sEAP2024MM01/MDRMM022, 13 Dec 2024](https://reliefweb.int/report/myanmar/myanmar-urban-heatwaves-simplified-early-action-protocol-seap-no-seap2024mm01-operation-no-mdrmm022) (mirrored at [Anticipation Hub](https://www.anticipation-hub.org/download/file-5058), direct file at [IFRC GO](https://go-api.ifrc.org/api/DownloadFile/89567/sEAP2024MM01_MDRMM022))
- [2025 annual report, MDRMM022, 31 Mar 2026](https://reliefweb.int/report/myanmar/myanmar-urban-heatwaves-simplified-early-action-protocol-2025-annual-report-seap-no-seap2024mm01-operation-no-mdrmm022-31-march-2026) (direct file at [IFRC GO](https://go-api.ifrc.org/api/DownloadFile/89569/MDRMM022eapar2025))
- [IFRC GO — appeal MDRMM022](https://goadmin.ifrc.org/api/v2/appeal/?code=MDRMM022) · [emergency 7603](https://go.ifrc.org/emergencies/7603/details) (machine-readable status/budget)
- [IFRC press release — May 2024 Asia Pacific heatwave response](https://www.ifrc.org/press-release/searing-temperatures-sweep-fire-across-asia-pacific-causing-distress-millions) (Myanmar section: pre-dates this sEAP)
- [Anticipation Hub global map](https://www.anticipation-hub.org/experience/global-map) (inventory record)
