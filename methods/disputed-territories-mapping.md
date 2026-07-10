---
content_type: method
last_reviewed: "2026-07-10"   # bump when a human verifies the page is still accurate
---

# Disputed territories on maps

The team's cartographic convention for disputed territories. Worked out for the HDX Signals
India maps, but the approach applies to **any map the team produces** — treat this as the
default whenever a map touches a disputed area.

## The rule

Follow **OCHA's brand guideline on representing territories**
([brand.unocha.org/document/368498](https://brand.unocha.org/document/368498#/guidance/representing-territories)).
For India specifically, the guideline (p. 17) says:

- **Jammu & Kashmir** is shown as a **single undivided territory, separate from both India and
  Pakistan**.
- **Arunachal Pradesh** is shown.

When in doubt, cross-check against established examples — maps published by the UN or other
international organisations — rather than inventing a depiction. The goal is neutrality, not a
position.

## The implemented decision (India)

What we actually do, as built for the HDX Signals India maps:

1. **Arunachal Pradesh is displayed as part of India**, by merging the UN Geoportal
   geoboundaries for iso3 codes `IND` + `xAP`. Boundaries come from the
   [UN Geoportal](https://geoportal.un.org/arcgis/apps/sites/#/geohub/datasets/702b9ed60bde48ba8619d691077ce309/about).
2. **Jammu & Kashmir is not displayed at all** — neither the India-administered nor the
   Pakistan-administered region.
3. **Data points falling in Jammu & Kashmir are shown as floating points**, keeping the data
   provider's **original iso3 assignment**. This avoids taking any position on whether a point
   "belongs" to the Indian- or Pakistani-administered area.

The pattern generalises: render disputed polygons per the OCHA brand guideline (undivided /
omitted as it directs), and let point data float on its provider-assigned country code rather
than re-assigning it yourself.

Digested from the retired DSCI Confluence space (archive: `confluence/` in
`ds-knowledge-base-internal`).
