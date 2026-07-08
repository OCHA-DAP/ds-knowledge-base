---
content_type: pipeline
name: rosea-thresholds-monitoring
type: monitoring
status: live
deployment:
  platform: github-actions
  resource_group: null
  jobs:
    - { name: "Check slow onset", ref: ".github/workflows/check_slow_onset.yaml", schedule: "0 0 * * *", status: live }
    - { name: "Send email", ref: ".github/workflows/send_email.yaml", schedule: "event (on merge of a send-email-labeled PR)", status: live }
inputs:
  - "IPC/CH: HDX HAPI food-security-nutrition-poverty endpoint, admin_level:0 (national), 15 ROSEA countries (needs HAPI_APP_IDENTIFIER)"
  - "JRC ASAP: agricultural-production-hotspots.ec.europa.eu/files/hotspots_ts.zip (hotspot time series, pulled live)"
  - "repo state: data/current.csv (prior alert levels, to diff against)"
outputs:
  - "repo: data/current.csv (rotated -> previous.csv) committed on any change"
  - "GitHub PR labeled send-email (the alert proposal)"
  - "listmonk: ROSEA slow-onset alert digest (lists 13 ROSEA + 6 DS prod, list 12 test; template_id 8)"
  - "GitHub Pages dashboard: ocha-dap.github.io/ds-rosea-thresholds (index.html on main)"
dependencies:
  - "listmonk list 13 (ROSEA), list 6 (DS team), list 12 (test); template_id 8"
  - "secrets: HAPI_APP_IDENTIFIER, listmonk credentials"
  - great_tables
downstream:
  - "OCHA Regional Office for Southern & Eastern Africa (ROSEA) + DS team - Listmonk digest recipients; regional surge / flash-appeal / CERF-request triage"
depends_on: [ipc, listmonk]
source_repo: ocha-dap/ds-rosea-thresholds
source_branch: main
source_sha: 6af5396
code_ref:
  - check_slow_onset.py
  - send_email.py
  - src/datasources/ipc.py
  - src/datasources/asap.py
  - src/utils.py
  - src/plot.py
  - src/listmonk.py
  - .github/workflows/check_slow_onset.yaml
  - .github/workflows/send_email.yaml
extra:
  methodology_url: "The digest links an internal Google Doc methodology (METHODS_URL, hardcoded in src/listmonk.py) - not extracted into the repo or KB."
  human_in_the_loop: "The daily cron only PROPOSES an alert (as a send-email-labeled PR); merging the PR is the actual send trigger. The digest is not itself scheduled."
visibility: internal
last_synced: "2026-07-08"
---

# ROSEA Slow-Onset Thresholds — monitoring pipeline

> Runbook. Optimize for "what feeds it, what it emits, and what to do when it breaks at 2am."
>
> **Sibling page:** the alert-level *thresholds themselves* — how they were derived and calibrated — live in [`analysis/rosea-thresholds.md`](../analysis/rosea-thresholds.md). This page is the operational runbook only; it does not redefine the thresholds.

## One-liner

*Daily: re-pull IPC/CH + JRC-ASAP for 15 ROSEA countries -> classify & merge to a per-country alert level -> if any level changed, open a `send-email` PR -> merging that PR sends a Listmonk email digest.*

## Jobs & schedule

| job | ref | schedule | status |
|---|---|---|---|
| Check slow onset | `.github/workflows/check_slow_onset.yaml` | `0 0 * * *` (daily 00:00 UTC) | live |
| Send email | `.github/workflows/send_email.yaml` | event — fires when a `send-email`-labeled PR is **merged** | live |

**Two-workflow, human-in-the-loop flow.** The cron only *proposes* an alert (as a PR); a human merge is the actual send trigger — the email digest is not itself scheduled. `check_slow_onset.yaml` also exposes a `FORCE_TRIGGER` dispatch input for testing.

## Inputs

| source | detail |
|---|---|
| IPC/CH | HDX HAPI food-security-nutrition-poverty endpoint, `admin_level:0` (national), for the 15 ROSEA countries (`src/datasources/ipc.py`; needs `HAPI_APP_IDENTIFIER`). |
| JRC ASAP | Hotspot time series pulled live from `agricultural-production-hotspots.ec.europa.eu/files/hotspots_ts.zip` (`src/datasources/asap.py`). |
| Prior state | `data/current.csv` — the last committed alert levels, diffed against the fresh classification. |

Neither data source is refreshed/archived beyond the two rolling snapshots (`current.csv` / `previous.csv`) the pipeline maintains.

## Steps

1. **Detect (daily cron)** — `check_slow_onset.py` re-pulls both data sources, classifies each per the alert-level rules (`src/datasources/ipc.py::_classify_row`, `src/datasources/asap.py::_classify_row`), and merges them per country by taking the **max** of the ASAP and IPC levels as `max_alert_level` (`src/utils.py::merge_ipc_hotspots`). It diffs the result against `data/current.csv`; on any diff it rotates `current.csv` -> `previous.csv`, commits the new `current.csv`, and **opens a PR labeled `send-email`**. (Threshold values are documented in the [analysis page](../analysis/rosea-thresholds.md#what-was-analyzed--findings).)
2. **Send email (on PR merge)** — merging the `send-email`-labeled PR fires `send_email.yaml` -> `send_email.py` -> `src/plot.py` (renders a `great_tables` HTML summary: per-country badges colored by alert level, arrows for level changes) -> **`src/listmonk.py::send_rosea_campaign`**, which posts a campaign to a self-hosted **Listmonk** instance.

## Outputs

| output | detail |
|---|---|
| `data/current.csv` / `previous.csv` | The two rolling per-country alert-level snapshots, committed to the repo on any change. |
| `send-email` PR | The alert proposal — merging it is the send trigger. |
| Listmonk campaign | HTML digest to list **13** (ROSEA) + list **6** (DS team) in prod; list **12** when `TEST_EMAIL=true`. `template_id 8`. Links the methodology Google Doc (`METHODS_URL`, hardcoded in `src/listmonk.py`). |
| GitHub Pages dashboard | Static `index.html` (vanilla JS + Leaflet) at `ocha-dap.github.io/ds-rosea-thresholds` — its in-app modal describes it as "an internal tool under development." |

## Dependencies

- **Listmonk** — lists `13` (ROSEA prod), `6` (DS prod), `12` (test); `template_id 8` (`src/listmonk.py`).
- **`great_tables`** — HTML summary table rendering (`src/plot.py`).
- **Secrets** — `HAPI_APP_IDENTIFIER` (HDX HAPI); Listmonk credentials.

## Failure modes & debugging

| symptom | likely cause | fix |
|---|---|---|
| No `send-email` PR opened | No alert-level change since last run (normal), or the HAPI/ASAP pull failed | Check `check_slow_onset.yaml` run logs; a fetch error aborts before the diff. Confirm `HAPI_APP_IDENTIFIER` is valid. |
| Empty / stale alert levels | IPC reporting-window gap — no new national IPC report for a country | Expected: alert levels only move when IPC/ASAP data moves. The notebook text notes gaps can mean "missing IPC data, rather than misconfigured thresholds." |
| Email not sent after merge | PR wasn't labeled `send-email`, or Listmonk credentials invalid | The send workflow only fires on merge of a **`send-email`-labeled** PR. Check the label and the `send_email.yaml` logs / Listmonk UI. |
| Accidental real-list send | `TEST_EMAIL` not set | Set `TEST_EMAIL=true` to route to test list `12` instead of prod lists `13` + `6`. |

GHA logs: **Actions -> Check slow onset / Send email** in `ocha-dap/ds-rosea-thresholds`.

## Downstream consumers

The Listmonk digest (lists `13` + `6`) is the terminal output — it drives the ROSEA regional office's triage of remote/physical surge support, flash-appeal flags, and possible CERF requests. No downstream pipeline or framework consumes it (`feeds: []` on the analysis page; none of the OCHA/CERF ROSEA-country frameworks read this tool). The GH Pages dashboard is a parallel human-facing view of the same `current.csv`.

## Discrepancies & gotchas

- **[gap]** The live GH Pages dashboard (`ocha-dap.github.io/ds-rosea-thresholds`, served from `index.html` on `main`) is **not** listed in [`infrastructure/deployments.md`](../infrastructure/deployments.md)'s GitHub Pages & Netlify table.
- **[gap]** `infrastructure/deployments.md` lists an Azure Web App `chd-ds-rosea-ipc` (repo column `—`) that is actually **this repo's** deploy target: `.github/workflows/add-ipc_chd-ds-rosea-ipc(dev).yml` pushes the `add-ipc` branch to Azure Web App `chd-ds-rosea-ipc` (`dev` slot) via pip/venv — a different deployment path (and toolchain) than the documented uv + GHA-cron + static-GH-Pages flow. Not clear whether this Azure path is still live or a superseded earlier attempt; the registry doesn't attribute the app to this repo. **Needs an Azure-portal check.**
- **[gap]** README states the repo supports "slow onset and sudden onset shocks," but every implemented data source and script (`check_slow_onset.py`, `src/datasources/ipc.py`, `src/datasources/asap.py`) covers only **slow-onset** (food security) monitoring. No sudden-onset (cyclone, flood) logic exists in the repo.
