---
content_type: app
name: storm-exposure-compare
purpose: "Interactive comparison of CHD (forecast-only + observed) vs GDACS vs ADAM per-country tropical-cyclone population exposure, with configurable trigger thresholds and a Weibull return-period readout."
status: live
tech: other                    # static JS (hand-rolled SVG + Leaflet), pre-baked JSON — not marimo/dash/streamlit
related: storm-impact-harmonisation
deployment:
  platform: gh-pages
  ref: "ocha-dap/ds-storm-impact-harmonisation (app/ + .github/workflows/deploy-app.yml); serving branch TBD — confirm from repo"
  url: https://ocha-dap.github.io/ds-storm-impact-harmonisation/compare/
  resource_group:              # n/a — GitHub Pages, not Azure
  trigger: "GH Pages workflow mode — schedule (daily ~06:00 UTC data refresh from dev DB) + workflow_dispatch + push touching app/**"
inputs:
  - "DB (dev): storms.nhc_tracks_fcastonly_exposure, storms.nhc_tracks_obsv_exposure (CHD forecast-only + observed exposure)"
  - "DB (dev): storms.gdacs_exposure, storms.adam_exposure (GDACS / ADAM per-country exposure)"
  - "Exported to pre-baked JSON under app/data/ at deploy time by export_app_data.py (data never enters git)"
depends_on: [storm-impact-harmonisation]
source_repo: ocha-dap/ds-storm-impact-harmonisation
source_branch:                 # TODO confirm serving branch (built via PR OCHA-DAP/ds-storm-impact-harmonisation#10)
source_sha:                    # TODO fill from repo HEAD once branch confirmed
code_ref:
  - "app/ (index.html + app.js + style.css — static client)"
  - "export_app_data.py (CI-only DB->JSON export)"
  - ".github/workflows/deploy-app.yml (GH Pages workflow-mode deploy)"
extra:
  stub: "Created from issue #225 as a stub; source_branch/source_sha and exact code_ref paths need confirming against the repo. Live app content verified 2026-07-09 against the deployed URL."
  pattern: "Reference implementation of the static-data-app pattern — see methods/static-data-apps.md."
  built: "2026-07-07/08, PR OCHA-DAP/ds-storm-impact-harmonisation#10."
  return_periods: "RP readout uses Weibull plotting position — see methods/return-periods.md."
  repo_note: "Same repo hosts the storm-impact-harmonisation pipeline (GDACS monitor email + CERF predictor + exposure workbook); this app is a separate deployment surface in that repo."
visibility: internal
last_synced: "2026-07-09"
---

# Storm exposure comparison

> Interactive deployed surface. Optimize for "what it shows, who it's for, and how to keep it running."

## What it shows

Answers: "For a given storm, which per-country exposure source (CHD forecast-only, CHD observed,
GDACS, ADAM) would have crossed a chosen trigger, and how does that compare across sources and
forecast issue-times?" It compares tropical-cyclone **population exposure by country** across
wind thresholds (34 kt / 50 kt / 64 kt) and across the three data sources, letting a user set
population-exposure and return-period thresholds and see which storms trigger.

## Key features

- **Track map** — storm tracks coloured by wind severity (amber 34 kt, orange 50 kt, red 64 kt;
  green for observed tracks). Triggering storms shown in full colour, non-triggering in pale grey.
- **Configurable thresholds** — population-exposure threshold, return-period settings (per GDACS
  and ADAM), and wind-exposure level, adjusted with live-update sliders.
- **Trigger table** — which storms trigger under the current settings, per source.
- **Forecast evolution** — examine a single storm and how its forecast exposure evolves by
  issued time (CHD forecast-only vs observed, per valid time).
- **Return-period readout** — Weibull plotting-position RP (see [methods/return-periods.md](../methods/return-periods.md)).

## Data

Pre-baked **static JSON exported from the dev DB at deploy time** (no runtime DB connection).
`export_app_data.py` queries the `storms.*` exposure tables via `ocha-stratus` and writes JSON
under `app/data/` (gitignored). The GH Pages deploy workflow refreshes the export on a daily
schedule (~06:00 UTC), on `workflow_dispatch`, and on pushes touching `app/**`. This is the
reference implementation of the static-data-app pattern — [methods/static-data-apps.md](../methods/static-data-apps.md).

## Deployment & access

**GitHub Pages** (workflow mode), served from `ds-storm-impact-harmonisation`, live at
<https://ocha-dap.github.io/ds-storm-impact-harmonisation/compare/>. No Azure web app, no
runtime server, no client-side credentials. Cross-ref the GitHub Pages table in
[infrastructure/deployments.md](../infrastructure/deployments.md).

## Maintenance / known issues

- **Data freshness = last deploy** — driven by the daily-scheduled deploy workflow plus manual
  `workflow_dispatch`; there is no live query path.
- **Stub page** — serving branch, `source_sha`, and exact `code_ref` paths still need confirming
  against the repo (built via PR #10 on `ds-storm-impact-harmonisation`).
- For the pattern, gotchas, and the (prospective, not-yet-set-up) SWA variant, see [methods/static-data-apps.md](../methods/static-data-apps.md).
