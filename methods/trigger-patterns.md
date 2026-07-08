---
content_type: method
last_reviewed: "2026-07-02"   # bump when a human verifies the page is still accurate
---

# Trigger patterns — typology

Cross-cutting *how we actually build triggers*, derived bottom-up from `trigger_facets` across the **26 ingested frameworks** (current version each). Framework pages link here instead of re-explaining a pattern. Update when a new pattern appears in ≥2 frameworks; re-derive the counts from `../catalog.md`.

## At a glance

- **basis:** mixed 16 · forecast 6 · observational 4
- **calibration:** return-period 19 · percentile 6 · bespoke 1
- **windows:** 2–3 is the norm (20/26); differentiated mostly by **time** (16), sometimes **space** (≈6), rarely **severity** (1); a few single-window dev-stage
- **hazards:** flood 9 · drought 7 · tropical-cyclone 7 · cholera 3

Two things hold almost everywhere: **return-period calibration** (set the threshold to a target 1-in-X-year rarity, usually ~1-in-3 to 1-in-5) and **multi-window staging by lead time** (readiness → action, sometimes + observational).

## Hazard-family patterns

### 1. Cyclone wind(-exposure) + rainfall — *tropical-cyclone*
**Shape:** forecast of a storm reaching a wind-speed/category threshold within a proximity-or-exposure of land (a "wind buffer", or population inside the forecast wind field), usually paired with / OR'd against a 2–3-day rainfall trigger; staged readiness → action → (post-landfall) observational. **Calibration:** return-period. **Used by:** [bgd-cyclone](../frameworks/bgd-cyclone/), [cub-hurricanes](../frameworks/cub-hurricanes/), [fji-storms](../frameworks/fji-storms/), [hti-hurricanes](../frameworks/hti-hurricanes/), [mdg-storms](../frameworks/mdg-storms/), [moz-cyclones](../frameworks/moz-cyclones/), [phl-storms](../frameworks/phl-storms/) (phl via the Netherlands RC **510 impact model** — a model-based variant predicting damage rather than wind directly). The single most consistent family.

### 2. Seasonal-forecast drought (forecast ∨ observational) — *drought*
**Shape:** a seasonal precipitation forecast (SEAS5 / IRI tercile or percentile below-normal) over a cropping season, usually **OR'd with an observational backstop** (SPI, biomass — ASAP/NDVI) for late-season confirmation; two windows by issued month (readiness/action). **Calibration:** return-period or historical percentile. **Used by:** [afg-drought](../frameworks/afg-drought/), [bfa-drought](../frameworks/bfa-drought/), [lac-dry-corridor](../frameworks/lac-dry-corridor/), [mrt-drought](../frameworks/mrt-drought/), [ner-drought](../frameworks/ner-drought/), [sahel-drought](../analysis/sahel-drought.md), [tcd-drought](../frameworks/tcd-drought/). (sahel is the regional outlier — 8 windows across countries × seasons.)

### 3. Forecast discharge / return-period flood — *flood*
**Shape:** a river-discharge or seasonal-precip forecast (GloFAS, national hydrological services, SEAS5) exceeding a return-period threshold at a gauge/reach; readiness (longer lead) → action (shorter lead), sometimes split by basin (space). **Calibration:** return-period. **Used by:** [npl-flooding](../frameworks/npl-flooding/), [tcd-flooding](../frameworks/tcd-flooding/), [bgd-flooding](../frameworks/bgd-flooding/), [ssd-flooding](../analysis/ssd-flooding.md), [cod-flooding](../analysis/cod-flooding.md), [eth-flooding](../analysis/eth-flooding.md); [nga-flooding](../frameworks/nga-flooding/) adds population-exposure and is split by area.

### 4. Observational flood exceedance — *flood*
**Shape:** an observed water level or national flood-alert crossing a level (no forecast), as the action / early-response window — usually the observational leg of a mixed framework. **Used by:** [ner-flooding](../frameworks/ner-flooding/) (ABN Niamey water level; windows split by **severity**), [bfa-flooding](../frameworks/bfa-flooding/) (CONASUR alert + river-gauge fallback alongside a SEAS5 forecast window).

### 5. Cholera surveillance percentile (per-province) — *cholera*
**Shape:** weekly suspected-cases / case-rate (per population) crossing a **historical percentile band**, with a case-growth or consecutive-weeks condition, evaluated **per province** (space axis). Observational, percentile-calibrated — distinct from the hydromet families on every facet. **Used by:** [cod-infectious-disease](../frameworks/cod-infectious-disease/), [moz-cholera](../frameworks/moz-cholera/), [nga-cholera](../analysis/nga-cholera.md).

## Cross-cutting structures (orthogonal to hazard)

- **Readiness → Action (→ Observational) staging** — the dominant multi-window structure (`window_axes: [time]`, 16/26): the same indicator at decreasing lead times, releasing tranches of funding. Count windows by *activation component*, not by data source.
- **Forecast ∨ Observational (OR-logic)** — the "mixed" basis (16/26): a forecast trigger OR an observational backstop for the same activation, buying both lead time and a miss-catch. Recurs across drought and cyclone.
- **Per-area windows (space axis)** — flood-by-basin (cod, nga, bgd) and cholera-by-province: `n_windows` = areas, not stages.
- **Severity tiers (rare)** — only ner-flooding splits windows by severity (different magnitude → different response package).

## Calibration approaches

- **Return-period (19/26)** — threshold set to a target rarity (1-in-X years) against the historical / hindcast record. The default; chosen RP is usually a cost/sensitivity trade-off (~3–5 yr).
- **Percentile (6)** — historical percentile bands; all cholera + some drought.
- **Bespoke (1)** — ner-drought (custom combination).

## Where the live trigger runs

A recurring non-obvious fact: the **operational trigger often runs outside the framework repo** — IRI/NCDP Maproom (ner-drought, mrt-drought), INSIVUMEH (lac), INAM/PRISM (moz-cyclones). The repo is then the *derivation/analysis*, not the production system (`operated_by` on the page). Worth checking before assuming the repo code is what fires.
