---
content_type: app
name: hti-hurricanes-app
purpose: Explore the historical activation record of the Haiti hurricanes trigger
status: live
tech: dash
related: hti-hurricanes
deployment:
  platform: azure-webapp
  ref: chd-ds-aa-hti-hurricanes-app
  url: https://chd-ds-aa-hti-hurricanes-app.azurewebsites.net
  resource_group: IMB-CHD-DataScience-EastUS2
inputs:
  - hti monitoring parquets (blob) / historical NHC + CHIRPS-GEFS trigger evaluation
depends_on: [hurricanes-monitoring]
source_repo: ocha-dap/ds-aa-hti-hurricanes-app
source_branch: main   # TODO confirm active branch (repo last commit 2024-07-23)
source_sha: null
code_ref: []
visibility: internal
last_synced: 2026-06-12
---

# Haiti hurricanes — trigger app

## What it shows
Interactive view of the historical record of the [Haiti hurricanes framework](../frameworks/hti-hurricanes/2024-08-23.md) trigger — which storms would/did meet the three-stage wind+rain trigger, deployed for partners to inspect the activation history.

## Key features
Historical-storm trigger evaluation against the framework's thresholds (`THRESHS`, 230 km gate). Serves the `hti-hurricanes` framework.

## Data
Reads the historical NHC + CHIRPS-GEFS / IMERG trigger evaluation produced by the framework repo's monitoring. *(Detail TODO — verify against the app repo.)*

## Deployment & access
Azure App Service `chd-ds-aa-hti-hurricanes-app` (RG `IMB-CHD-DataScience-EastUS2`), deployed from `ds-aa-hti-hurricanes-app` via a GitHub Actions workflow. Currently a **development** slot.

## Maintenance / known issues
App repo last touched 2024-07-23 — confirm whether it's current vs. the framework's active `melissa-exposure` branch. _Stub — needs a proper ingestion pass on `ds-aa-hti-hurricanes-app`._
