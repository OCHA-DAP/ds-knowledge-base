---
content_type: pipeline
name: ken-drought-monitoring
type: monitoring
status: live
deployment:
  platform: github-actions
  resource_group: null
  jobs:
    - name: Kenya Drought Monitoring
      ref: .github/workflows/run_monitoring.yml
      schedule: on-demand (workflow_dispatch)
      status: live
inputs:
  - "blob: projects/ds-aa-ken-drought-monitoring/monitoring/{Month}_forecast_{year}.txt (KMD CPT seasonal forecast, uploaded manually before each run)"
  - "fieldmaps: KEN ADM1 boundaries via stratus.codab.load_codab_from_fieldmaps"
  - "user input: IOD state (negative | non-negative) — entered at run time based on BoM outlook"
outputs:
  - "listmonk: Kenya OND drought trigger alert email (list 105 prod, list 103 test)"
dependencies:
  - ocha-stratus
  - "ocha-relay @ git+https://github.com/OCHA-DAP/ocha-relay.git@v0.2.0"
  - geopandas
  - pandas
  - shapely
  - "listmonk list 105 (Kenya production)"
  - "listmonk list 103 (Kenya test)"
  - "secrets: DSCI_AZ_BLOB_DEV_SAS, DSCI_LISTMONK_BASE_URL, DSCI_LISTMONK_API_USERNAME, DSCI_LISTMONK_API_KEY"
downstream:
  - "frameworks/ken-drought — this pipeline IS the operational OND monitoring for the Kenya drought AA framework; the trigger thresholds here implement that framework's RP3/RP5 pathways"
  - "Kenya AA response teams / partners subscribed to Listmonk list 105 (prod)"
depends_on:
  - listmonk
source_repo: ocha-dap/ds-aa-ken-drought-monitoring
source_branch: main
source_sha: ce54c9f
code_ref:
  - run_monitoring.py
  - src/constants.py
  - src/datasources/kmd.py
  - src/datasources/iod.py
  - src/utils/parser.py
  - src/analysis/ond.py
  - src/alert/email.py
  - .github/workflows/run_monitoring.yml
extra:
  stage: dev
  blob_stage_note: "constants.py hardcodes STAGE='dev' — reads from the dev blob container, not prod"
  iod_source: "user-entered at run time (manual check of BoM IOD outlook at https://www.bom.gov.au/climate/enso/); the pipeline does NOT auto-detect IOD"
  exit_codes: "0 = no trigger or non-monitoring month | 1 = error | 2 = trigger reached"
  august_mode: "August is informational only — probabilities are shown but no trigger decision is made"
  trigger_design_repo: "ocha-dap/ds-aa-ken-drought"
visibility: internal
last_synced: "2026-06-22"
---

# Kenya Drought Monitoring

> Runbook. Optimize for "what feeds it, what it emits, and what to do when it breaks at 2am."

## One-liner

On-demand (July, August, September): load KMD seasonal forecast from blob, evaluate RP3/RP5 OND trigger conditions for 9 arid counties (IOD-adjusted thresholds), and send alert email via Listmonk.

## Jobs & schedule

| job | ref | schedule | status |
|---|---|---|---|
| Kenya Drought Monitoring | `.github/workflows/run_monitoring.yml` | on-demand (`workflow_dispatch`) | live |

No Databricks jobs. Not in the deployments.md registry. The workflow is manually dispatched via **Actions → Kenya Drought Monitoring → Run workflow** for each of the three monitoring months (July, August, September). Before running, the operator must: (1) upload the KMD forecast file to blob, and (2) check the BoM IOD outlook to determine the IOD state input.

## Inputs

| source | detail |
|---|---|
| KMD CPT seasonal forecast | blob `projects/ds-aa-ken-drought-monitoring/monitoring/{Month}_forecast_{year}.txt` (stage: dev). Uploaded manually before each run. One file per monitoring month. |
| Kenya ADM1 boundaries | Loaded from FieldMaps via `stratus.codab.load_codab_from_fieldmaps("KEN", admin_level=1)` |
| IOD state | User-supplied at run time (`iod_state` workflow input: `non-negative` or `negative`). Based on operator checking BoM IOD outlook. Not auto-detected. |

The KMD file is a CPT-format probabilistic forecast. Field `C=1` = RP5 (1-in-5yr), `C=2` = RP3 (1-in-3yr). Values are gridded probability of non-exceedance of the RP SPI threshold, covering 9 arid counties: Baringo, Garissa, Isiolo, Mandera, Marsabit, Samburu, Tana River, Turkana, Wajir.

## Steps

`run_monitoring.py` → `compute_ond_indicators` (`src/analysis/ond.py`) → `send_ond_alert` (`src/alert/email.py`). Briefly:

1. Load + parse the KMD CPT forecast from blob (`src/datasources/kmd.py`, `src/utils/parser.py`).
2. Resolve IOD state from `--iod-state` (or interactive prompt) → `"Negative"` / `"Non-Negative"` (`src/datasources/iod.py`).
3. Load KEN ADM1 from FieldMaps, filter to the 9 arid counties; buffer each KMD grid point to a 0.5° cell and spatial-join to the counties; take the median probability of non-exceedance across intersecting pixels for RP5 (`C=1`) and RP3 (`C=2`).
4. Apply the IOD-adjusted threshold (table below) — trigger fires if RP5 or RP3 median ≥ threshold. **July & September only**; August is informational (`dry_run=True` when `issue_month` not in `TRIGGER_MONTHS`).
5. Build HTML email and create + immediately send a Listmonk campaign (list 105 prod / 103 test).

Per-pixel geometry, CRS reprojection and CPT parsing details live in the code (`code_ref`) — see `src/analysis/ond.py::_compute_rp_indicator`.

**Thresholds:**

| Return period | Non-Negative IOD | Negative IOD |
|---|---|---|
| RP5 (1-in-5yr) | ≥ 40% | ≥ 35% |
| RP3 (1-in-3yr) | ≥ 60% | ≥ 50% |

## Outputs

| output | detail |
|---|---|
| Listmonk email campaign | HTML alert to list 105 (prod) or 103 (test). Subject: `Kenya OND Drought Monitoring - {Month} {Year}`. Contains summary table, per-RP trigger status, county-level median probabilities. Campaign named `ken-drought-ond-{year}-{month}-{ts}`. |

No DB writes. No blob writes beyond the input file (which is uploaded externally).

## Dependencies

- **`ocha-stratus`** — blob reads (KMD forecast) and CODAB boundary loading
- **`ocha-relay` v0.2.0** — `ListmonkClient` for campaign creation and dispatch
- **Listmonk list 105** — Kenya production mailing list
- **Listmonk list 103** — Kenya test mailing list
- **geopandas / shapely** — spatial join of KMD grid to county polygons
- **FieldMaps** — ADM1 boundary source (via stratus.codab)
- **GitHub Actions secrets** — `DSCI_AZ_BLOB_DEV_SAS`, `DSCI_LISTMONK_BASE_URL`, `DSCI_LISTMONK_API_USERNAME`, `DSCI_LISTMONK_API_KEY`

The `STAGE` is hardcoded to `"dev"` in `src/constants.py`, meaning blob reads always go to the dev storage container even in production runs.

## Failure modes & debugging

| symptom | likely cause | fix |
|---|---|---|
| Blob read error on startup | KMD file not uploaded yet, wrong filename, or stale SAS token | Check blob path matches `{Month}_forecast_{year}.txt` exactly (capital first letter). Renew `DSCI_AZ_BLOB_DEV_SAS` if expired. |
| `No data parsed from blob` | CPT file format invalid or empty | Inspect the raw file manually; re-upload a corrected version. |
| Spatial join returns empty | KMD grid doesn't overlap the county polygons | Check CRS; `KEN_EPSG=EPSG:32736`, `KEN_GEO_EPSG=EPSG:4326`. Confirm the county names in `ARID_COUNTIES` match `adm1_name` values from FieldMaps. |
| Email not sent | Listmonk credentials invalid or relay down | Check `DSCI_LISTMONK_BASE_URL` / API key secrets. Run with `--no-email` to isolate analysis from email. |
| IOD prompt blocks CI | `iod_state` input not passed | Always pass `--iod-state` in GHA runs; it's a required workflow input. |
| Exit code 1 | Script error (analysis or email) | GHA step has `continue-on-error: true`; a subsequent "Fail on error" step catches this. Check job logs. |
| Exit code 2 | Trigger reached (expected outcome) | Not an error — script exits 2 when trigger fires. GHA marks the step as failed but the workflow handles it via the continue-on-error pattern. |

GHA logs: **Actions → Kenya Drought Monitoring → (run)** in the `ocha-dap/ds-aa-ken-drought-monitoring` repo.

For August runs, the trigger is never assessed regardless of probabilities — `dry_run=True` is set when `issue_month` is not in `TRIGGER_MONTHS = ["July", "September"]`.

## Downstream consumers

The email list (Listmonk list 105) drives the operational AA trigger notification for the Kenya drought framework — see [`frameworks/ken-drought`](../frameworks/ken-drought/2023-02-19.md). Trigger design and hindcast analysis live in the [ds-aa-ken-drought](https://github.com/OCHA-DAP/ds-aa-ken-drought) repo. No DB tables or blob outputs consumed by downstream pipelines or apps.

## Discrepancies & gotchas

- **[gap]** Not listed in [`infrastructure/deployments.md`](../infrastructure/deployments.md) GitHub Actions table. This is a scheduled-less (`workflow_dispatch`-only) GHA pipeline that the registry doesn't yet index — add a row when the registry is next refreshed.
- **[conflict]** `STAGE` is hardcoded to `"dev"` in `src/constants.py`, so even "production" runs read the KMD forecast from the **dev** blob container and authenticate with `DSCI_AZ_BLOB_DEV_SAS`. There is no prod-stage path; operators must upload the forecast to the dev container.
- **[gap]** No cron — the workflow is **manual only** (`workflow_dispatch`). Nothing fires it automatically; an operator must dispatch it each monitoring month (July/Aug/Sep) after uploading the forecast and checking the BoM IOD outlook. Easy to miss.
- **[gap]** IOD state is **not auto-detected** — it is operator-entered (`iod_state` input) from a manual read of the BoM outlook. `IOD_NEGATIVE_THRESHOLD = -0.4` exists in constants but nothing in the pipeline computes the DMI; the threshold is documentation only.
- Deployed branch `main` = the checked-out/ingested branch (`source_sha: ce54c9f`) — no branch mismatch.
