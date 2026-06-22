---
content_type: app
name: c3s-viz
purpose: Compare C3S seasonal precipitation skill (1993–2016 hindcast correlation) with the current operational forecast for each contributing system; classify systems good/ok/bad and regroup forecasts by skill.
status: live
tech: other
related: standalone
deployment:
  platform: gh-pages
  ref: "OCHA-DAP/ds-c3s-viz @ add-c3s-viz path=/docs"
  url: https://ocha-dap.github.io/ds-c3s-viz/
  resource_group: null
inputs:
  - "C3S seasonal verification PNGs (ECMWF skill gallery: sites.ecmwf.int/cxep/c3s-seasonal-verification/)"
  - "OpenCharts seasonal forecast embeds (climate.copernicus.eu/charts/embed/c3s_seasonal/)"
  - "OpenCharts product availability API (charts.ecmwf.int/opencharts-api/v1/products/) — single fetch per selection to confirm forecast presence"
depends_on: []
source_repo: ocha-dap/ds-c3s-viz
source_branch: add-c3s-viz
source_sha: 4fd2dcc
code_ref:
  - docs/index.html
extra:
  deploy_note: "GH Pages is pointed at the add-c3s-viz branch /docs — NOT main (main is an empty initial commit). PR #2 is deliberately kept open for review; do not merge unless explicitly asked. Redeploy by pushing to add-c3s-viz."
  no_build: "Pure static — single HTML file with inline CSS and JS. No bundler, no Python, no ocha-stratus. The only network dependency beyond static image/iframe embeds is the one fetch() to the OpenCharts availability API; if that API drops CORS support this breaks."
  providers: "ECMWF SEAS5.1 (ecmwf_s51), UKMO GloSea6 (ukmo_s610), Météo-France S9 (meteo_france_s9), DWD GCFS2.2 (dwd_s22), CMCC SPS4 (cmcc_s4), NCEP CFSv2 (ncep_s2), JMA CPS4 (jma_s4), ECCC GEM5.2-NEMO (eccc_s5), BoM ACCESS-S2 (bom_s2), multi-system (year-versioned C3Smm_s{year})"
  skill_token_maintenance: "Skill tokens must match the latest C3S system in the verification gallery. Verify by probing token URLs (HTTP 200 = present). Bump MULTI_CANDS array when a new year's multi-system token appears."
  fcmonth_convention: "fcmonth = leadtime + 2 (lead to the LAST month of the 3-month window, not the first). Getting this wrong shifts skill maps by ~2 months."
  not_in_deployments_md: "c3s-viz is NOT listed in infrastructure/deployments.md (GH Pages inventory is incomplete per the TODO in that file)."
discrepancies:
  - "[gap] Not in infrastructure/deployments.md — the GH Pages section there is a stub (TODO: inventory via gh api / org Pages settings). This app belongs in that table (alongside ds-aa-ner-drought and ds-storms-alerts signup) but isn't yet listed. Verified live config via `gh api repos/OCHA-DAP/ds-c3s-viz/pages`: status=built, source.branch=add-c3s-viz, source.path=/docs, public=true."
  - "[stale] Default branch is `main` but `main` is an empty initial commit (sha a1b3b61 'Initial commit') — it is NOT the deployment. The entire live site runs from the feature branch `add-c3s-viz` (deployed sha 4fd2dcc). Deployed-branch ≠ default-branch."
  - "[conflict] PR #2 (add-c3s-viz → main) is deliberately kept OPEN and must NOT be merged; merging would lose the deployment source. (PR #1, an earlier version, was already merged.) Deploy is effectively manual-by-push to add-c3s-viz, not via any merge-to-main CI."
visibility: internal
last_synced: "2026-06-22"
---

# C3S seasonal precipitation — skill & forecast viewer

> An interactive deployed surface. Optimize for "what it shows, who it's for, and how to keep it running."

## What it shows

A single static HTML page for DS analysts comparing **C3S multi-model seasonal precipitation skill** with the **current operational forecast**. A user picks an issued month, valid trimester (only seasons starting 1–3 months after issue are selectable), forecast region, and optional product type (tercile summary, ensemble-mean anomaly, etc.). The app shows the C3S multi-system skill correlation map (1993–2016 hindcast) alongside the current multi-system forecast, then below it, one card per contributing system showing that system's skill map and its forecast embed. The user manually classifies each system as good/ok/bad using a dropdown; the bottom section regrouping the forecast maps live by that classification. This lets a forecaster quickly weight systems by their skill for the season and region of interest.

## Key features

- **Issued-month / trimester selector** with year stepper; only valid lead windows are enabled (1–3 months after issue, year-wrap handled).
- **Skill maps**: static PNGs from the C3S verification gallery, shown as `<img>`, draggable + scroll-to-zoom. Pan/zoom is **shared across all skill maps simultaneously** (and separately for forecast maps).
- **Forecast embeds**: interactive OpenCharts player iframes per provider and for the multi-system ensemble. Rendered in a fixed 600 × 600 px wrapper scaled to fit each tile so internal layout is identical at every size.
- **Availability gate**: before rendering forecast iframes, a single `fetch()` to the OpenCharts product API confirms the selected issued month's forecast exists. If absent, tiles are blanked rather than silently showing a wrong date.
- **Skill classification and grouping**: per-system good/ok/bad dropdowns regroup the forecast tiles live.
- **Forecast region selector**: switches the continent embed area code (Africa = area11, Global = area08, etc.); skill maps are always global.
- **Advanced panel**: forecast product type selector (tercile summary / ensemble-mean anomaly / upper tercile probability / lower tercile probability / prob. exceeding median).
- **No build, no backend, no dependencies** (besides Google Fonts CDN). Runs entirely in the browser.

## Data

All data is fetched live from ECMWF / Copernicus public APIs — no OCHA blob or DB is touched:

| Source | What | Mechanism |
|---|---|---|
| C3S seasonal verification gallery (`sites.ecmwf.int/cxep/c3s-seasonal-verification/`) | Skill PNGs — 1993–2016 hindcast correlation, per provider + month + lead | `<img>` tag (no CORS needed) |
| OpenCharts seasonal forecast player (`climate.copernicus.eu/charts/embed/c3s_seasonal/`) | Interactive forecast iframes per provider and multi-system | `<iframe>` embed (no X-Frame-Options) |
| OpenCharts product API (`charts.ecmwf.int/opencharts-api/v1/products/`) | Forecast availability probe (single fetch per selection) | `fetch()` — requires CORS from this origin |

Freshness: the C3S monthly forecast is released around the 13th of each issued month. The app auto-selects the latest issued month on load via `latestIssued()` (steps back one month before RELEASE_DAY=13). No data is cached or stored locally.

Nine individual systems plus one multi-system aggregate are covered (see `extra.providers`). The multi-system skill token is year-versioned (`C3Smm_s{year}`); the app cascades from newest to oldest candidate on image error.

## Deployment & access

- **Platform**: GitHub Pages, served from branch `add-c3s-viz`, folder `/docs`.
- **URL**: https://ocha-dap.github.io/ds-c3s-viz/
- **Redeployment**: push to `add-c3s-viz` — Pages picks up changes automatically. No CI workflow needed.
- **Branch note**: `main` is an intentionally empty initial commit. The live site runs entirely from `add-c3s-viz`. PR #2 is open for review and is **deliberately not merged**.
- **Access**: public URL (GitHub Pages org site); no authentication.
- **Not in `infrastructure/deployments.md`**: the GH Pages inventory there is marked TODO; this app should be added when that inventory is completed.

Cross-ref: `infrastructure/deployments.md` (GH Pages section, currently incomplete).

## Maintenance / known issues

**Routine maintenance:**
- **Skill tokens**: when ECMWF releases a new C3S system version, the `PROVIDERS` token strings in the `<script>` config block must be updated. Verify by probing the gallery URL (`curl` returns 200 for valid tokens, 302 for absent). Higher system number = newer.
- **Multi-system token**: add the new `C3Smm_s{year}` to the front of `MULTI_CANDS` array each year.
- **Redeploy**: push `docs/index.html` change to `add-c3s-viz`.

**Known failure modes:**
- **OpenCharts CORS drops**: the single `fetch()` for availability checking will fail, blanking all forecast tiles. Mitigation: remove the availability check and accept OpenCharts' fallback behaviour (silently shows nearest available date).
- **Verification gallery URL changes**: skill `<img>` tags silently show broken images. The `onerror` handler replaces them with "no map for this month/lead" text, but an upstream URL restructure would break all skill maps.
- **Stale system tokens**: if a provider upgrades its C3S system, the old token returns 302 (missing) from the gallery — the `onerror` handler shows "no map for this month/lead" per card. Not catastrophic but misleading.
- **Dev-vs-prod**: there is no dev slot — the branch IS the deployment. Test locally by opening `docs/index.html` in a browser; no build step required.
- **JS parse errors**: since there's no bundler, a syntax error in the inline `<script>` silently breaks the whole page. Before committing, validate: `node --check <(sed -n '/<script>/,/<\/script>/p' docs/index.html)` or extract the script block and run `node --check`.
