---
content_type: dataset
name: IPC
aliases: [CH, "Cadre Harmonisé", IPC-CH, IPC/CH]
provider: "IPC Global Partnership (FAO, FEWS NET, WFP, UNICEF, Save the Children, CILSS/CH for West Africa & the Sahel, and others)"
data_type: food-security-phase
access: registered
api: "https://api.ipcinfo.org/  (docs: https://docs.api.ipcinfo.org/)"
auth: "free API key — request via a form; key is per-user"
formats: [json, geojson, vector-tiles, xlsx]
resolution: "sub-national units (admin areas, urban areas, IDP camps, HFA zones); Acute Food Insecurity phases 1–5; 'current' + 'projection' periods"
update_cadence: "2–3 analyses per country per year (irregular; on assessment cycles); >45 countries covered"
license: "IPC Terms of Use — attribution required, non-commercial"
code_ref: null
mirror: none            # none | manual | automated | n/a  — is a copy in OUR blob/DB?
mirror_priority: high   # high | med | low — how much a stale/absent copy hurts
used_by:
  - frameworks/som-drought/2019.md
  - frameworks/eth-drought/2020-12-07.md
  - frameworks/eth-drought/2026-06-09.md
  - frameworks/ken-drought/2023-02-19.md
  - frameworks/mrt-drought/2026-04-17.md
  - frameworks/lac-dry-corridor/2025-02.md
  - analysis/eth-flooding.md
last_verified: 2026-07-01
---

# IPC / Cadre Harmonisé

The **Integrated Food Security Phase Classification** (and its West-Africa/Sahel
counterpart, the **Cadre Harmonisé**) is the consensus classification of acute food
insecurity — the **Phase 1–5** scale (Minimal → Famine) most of our drought/food-security
frameworks trigger against or reference for context. IPC and CH share a single API.

## How we access it

- **Public API** at `api.ipcinfo.org` — Acute Food Insecurity classifications for 45+
  countries, current + projection periods, as **population tables** and **maps** (GeoJSON
  or vector tiles). Requires a **free API key** (request form → per-user key). Full
  reference at `docs.api.ipcinfo.org` (Public API v2.0).
- Country analyses are also downloadable as **xlsx** from the IPC website, and mirrored
  on **HDX** ([`ipc`](https://data.humdata.org/organization/ipc) org) and the FAO catalog.

We have **no dedicated loader** yet — usage to date has been per-analysis pulls of the
phase for the relevant admin units. If IPC becomes a live trigger indicator, add a loader
(candidate home: `ocha-lens`) and record it as `code_ref` here.

## How we use it

Drought frameworks use the projected IPC/CH phase as a **situational anchor** or an
**activation condition** (e.g. a threshold share of population in Phase 3+ / a projected
move to Phase 4). Note the authority caveat below when reconciling against FEWS NET.

## Gotchas

- **IPC ≠ [FEWS NET](fews-net.md).** FEWS NET classifications are *IPC-compatible* but
  are FEWS NET's own analysis and **do not always match** the IPC technical consensus.
  Name which source a trigger uses; don't treat them as interchangeable.
- Analyses are **irregular** — coverage and recency vary by country; a "projection" can be
  months old. Check the analysis date, not just the phase.
- Phases are **areal** (a unit's dominant phase), not a continuous surface.
