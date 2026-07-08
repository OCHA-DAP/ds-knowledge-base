---
content_type: analysis
name: rosea-thresholds
analysis_type: regional-overview   # exploratory | ad-hoc-activation | pre-framework | regional-overview
status: active                     # runs daily via GHA cron; live GH Pages dashboard + Listmonk alerts
country_iso3: [AGO, BDI, COM, DJI, SWZ, KEN, LSO, MDG, MWI, NAM, RWA, TZA, UGA, ZMB, ZWE]
hazard: food-insecurity             # slow-onset; driven by drought/agricultural-anomaly signals (ASAP) + IPC/CH phase classification
summary: "Daily IPC + JRC-ASAP alert-level screening across 15 countries in the OCHA ROSEA (Southern & Eastern Africa) region; feeds a Listmonk email digest and a GH Pages dashboard — a regional triage layer, not a country-hazard AA framework."
data_sources: [IPC, ASAP]
feeds: []          # standalone: no OCHA/CERF AA framework consumes this; it's a regional screening layer, not a per-country trigger
# --- source repo ---
source_repo: ocha-dap/ds-rosea-thresholds
source_branch: main
source_sha: 6af5396
code_ref:
  - check_slow_onset.py
  - send_email.py
  - src/datasources/ipc.py
  - src/datasources/asap.py
  - src/constants.py
  - src/utils.py
  - src/plot.py
  - src/listmonk.py
  - examples/historical_ipc.py
  - examples/explore_asap.py
depends_on: [ipc]   # this page = the threshold-derivation analysis (reads IPC/CH + ASAP); the operational listmonk dependency lives on the sibling pipeline page
discrepancies:
  - "[gap] The authoritative methodology writeup is an internal Google Doc (linked from README and hardcoded in src/listmonk.py as METHODS_URL) — not extracted into the repo or this KB. Thresholds here are reconstructed from src/constants.py plus the exploration notebooks, not the doc itself."
  # deployment/registry gaps (GH Pages, Azure chd-ds-rosea-ipc, README slow/sudden-onset) live on the operational runbook: pipelines/rosea-thresholds-monitoring.md
extra: {}
visibility: internal
last_synced: "2026-07-08"
---

# ROSEA Slow-Onset Thresholds — analysis

> **Analysis, not a framework.** A framework page is *only* for something with its own published framework doc. This repo is analysis (regional overview, ad-hoc activation, or pre-framework exploration) — captured so the work is findable, and linked to the framework(s) it supports if any.

## What it is

`ds-rosea-thresholds` is a daily operational screening tool that assigns each of 15 Southern/Eastern Africa countries (Angola, Burundi, Comoros, Djibouti, Eswatini, Kenya, Lesotho, Madagascar, Malawi, Namibia, Rwanda, Tanzania, Uganda, Zambia, Zimbabwe — a subset of the ~25 countries the OCHA ROSEA regional office covers) one of four alert levels (low/medium/high/very high) for slow-onset food-insecurity risk, combining JRC ASAP agricultural-anomaly hotspots and IPC/CH acute-food-insecurity phase data. It exists to help the OCHA Regional Office for Southern and Eastern Africa (ROSEA) — which covers a region with few permanent OCHA country offices, deploying from the regional hub in emergencies — decide when to send remote/physical surge support, flag flash appeals, or flag a possible CERF request. (The exact criterion for the 15-country selection lives in the internal methodology Google Doc, not the repo; note that OCHA does maintain country presences in some of these, e.g. Burundi and Kenya, so the list is not strictly "non-presence" countries.) It is **not** an AA framework: there is no framework PDF, no CERF-pre-arranged trigger, no endorsed activation protocol, and the thresholds themselves are still described as a work-in-progress internal methodology (Google Doc) rather than a published document — which is why it's captured as a `regional-overview` analysis (cf. `analysis/sahel-drought.md`, though that page rolls up *real* per-country frameworks — this one has none).

The repo has **two aspects, captured on two pages** (one home per fact):
- **This page (analysis)** — how the alert-level thresholds were *derived and calibrated* (the exploration notebooks, the threshold values, the framework relation).
- **[`pipelines/rosea-thresholds-monitoring.md`](../pipelines/rosea-thresholds-monitoring.md) (pipeline)** — the *operational runbook*: the daily GHA cron, the two-workflow detect→PR→email flow, Listmonk delivery, deployment, and failure modes.

## What was analyzed / findings

The live thresholds (`src/constants.py`) were derived in two companion marimo notebooks under `examples/` — both self-labeled "still a work in progress, meant for internal use":

- **`examples/historical_ipc.py`** — pulls all historical IPC/CH reports for the 15 countries via the HDX HAPI food-security endpoint, restricts to *national*-level reports, and works in the *fraction* of population per phase rather than raw counts (to be comparable across countries). Overlapping IPC reports for the same period are de-duplicated by keeping the most recent, prioritized `current > first projection > second projection`. It gives users interactive sliders to tune four alert-level rules and validates them against three independent series pulled from blob storage (`ds-rosea-thresholds/rosea_surge_20202024.csv`, `flash_appeals.csv`, `cerf.csv`): historical ROSEA physical/remote surge missions, flash-appeal publications, and CERF drought disbursements for Eastern/Southern Africa (2017+).
- **`examples/explore_asap.py`** — the equivalent exploration for JRC ASAP hotspot/warning data (`hs_code`, plus `w_crop`/`w_range` warning levels remapped to a 0–4 ordinal with an "out of season" sentinel).

The thresholds that shipped into the live pipeline (`src/constants.py`, applied in `src/datasources/ipc.py::_classify_row` and `src/datasources/asap.py::_classify_row`):

**IPC alert level** — an "emergency" (absolute population) OR "deteriorating" (proportion + increase) condition per level:
- **Very high**: population in IPC 4+ ≥ 500,000 (emergency) OR proportion in 3+ ≥ 25% AND a ≥3 percentage-point increase in the 4+ population share since the prior comparable report (deteriorating)
- **High**: population in IPC 4+ ≥ 200,000 (emergency) OR proportion in 3+ ≥ 25% AND a ≥5pp increase in the 3+ share (deteriorating)
- **Medium**: proportion in 3+ ≥ 18% OR population in IPC 4+ ≥ 50,000
- **Low**: everything else

Percentage-point change is only computed when consecutive reports' "population analyzed" denominators are within 10% of each other (`POP_THRESH`, copied from the team's Signals tool) — otherwise the change is left null rather than compared across non-comparable populations.

**ASAP hotspot alert level** (`HIGH_CONSEC = 3`):
- `hs_code == 0` → low
- `hs_code == 1` and fewer than 3 consecutive days at that code → medium
- `hs_code == 1` and ≥3 consecutive days → high
- `hs_code == 2` → very high

The two are merged per country by `src/utils.py::merge_ipc_hotspots`, taking the **max** of the ASAP and IPC alert levels as `max_alert_level`. The notebook's validation step (overlaying surge/flash-appeal/CERF markers on a per-country timeline) is exploratory calibration, not a documented backtest with pass/fail criteria — the notebook's own text acknowledges IPC reporting-window gaps mean "some desired windows of past activation may be missing due to missing IPC data, rather than misconfigured thresholds."

## Relation to frameworks

Standalone (`feeds: []`). None of the existing OCHA/CERF frameworks for ROSEA countries — e.g. `frameworks/ken-drought/2023-02-19`, `frameworks/mdg-plague/draft-2021`, `frameworks/mdg-storms/2024-12-13`, `frameworks/mwi-drought/2021` — consume this tool's output; it operates at a different tier (regional triage across *all* no-presence countries) and a different authority level (no CERF pre-arrangement) than a country-hazard AA framework. The closest KB neighbor in shape is `analysis/sahel-drought.md` (also `analysis_type: regional-overview`), but that page is a rollup of real endorsed per-country frameworks, whereas this tool has never fed, and isn't a precursor to, any specific framework.

## The operational pipeline (daily screening → email alert)

Yes — the email-sending pipeline lives in this repo, and it has its **own runbook page**: [`pipelines/rosea-thresholds-monitoring.md`](../pipelines/rosea-thresholds-monitoring.md). In brief, it's a **two-workflow, human-in-the-loop** flow — `check_slow_onset.yaml` (daily cron `0 0 * * *`) re-classifies both data sources and, on any change, opens a `send-email`-labeled PR; merging that PR fires `send_email.yaml` → a **Listmonk** campaign to the ROSEA + DS lists. The digest is *not* itself scheduled: the cron only proposes the alert; the human merge is the send trigger. Jobs/schedules, inputs/outputs, Listmonk list IDs, dependencies, failure modes, and the deployment-registry gaps all live on that runbook page.

## Sources & status

**Repo**: `ocha-dap/ds-rosea-thresholds` @ `main` (`6af5396`). **Data**: IPC/CH via the HDX HAPI food-security-nutrition-poverty endpoint (`src/datasources/ipc.py`); JRC ASAP hotspot time series (`src/datasources/asap.py`) — details on the [pipeline page](../pipelines/rosea-thresholds-monitoring.md#inputs).

**Exploration notebooks** (`examples/*.py`, marimo) are explicitly marked works-in-progress and are not run on a schedule — they're the one-time threshold-derivation record captured here, not part of the live pipeline.

Net: the repo is captured on **two pages** — this `analysis` page for the threshold-derivation work, and the `pipeline` runbook for the live daily monitoring/alerting system. It never was, and isn't heading toward being, an endorsed OCHA/CERF AA framework, which is why neither page is under `frameworks/`.
