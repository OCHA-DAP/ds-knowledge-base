---
content_type: infrastructure
last_reviewed: "2026-06-23"   # bump when a human verifies the page is still accurate
---

# Databricks — compute platform & the dev/prod model

How the team's **scheduled data pipelines actually run**. Most non-GHA pipelines are Databricks **jobs** in one workspace; this page is the platform reference (workspace, compute policies, clusters, the dev/prod model, bundle conventions). The per-job runtime registry — the authoritative "what's deployed and is it on the rails" list — lives in [deployments.md → Databricks jobs](deployments.md#databricks-jobs); the per-pipeline design/runbook lives on each `pipelines/*.md` page.

> Refresh anything here with the `databricks` CLI, profile **`DEFAULT`** (the token expires — re-auth with `databricks auth login --host https://adb-6009046713167663.3.azuredatabricks.net --profile DEFAULT`). Snapshot date in each section.

## Workspace

- **Workspace:** `adb-6009046713167663` (Azure Databricks, East US 2), CLI profile **`DEFAULT`**, current principal `adm.tdowning@global.un.org`.
- **Secret scope `dsci`** — holds the 14 `DSCI_AZ_*` DB/blob credentials (DEV+PROD host/uid/pw/SAS, read + write) plus `AWS_*`, `CDSAPI_*`, `CONTAINER_*`. Referenced as `{{secrets/dsci/<NAME>}}`; surfaced to clusters as env vars, which `ocha-stratus` reads. **Never hard-code creds** — they come from this scope via a policy (below) or an explicit `spark_env_vars` block. **Host secrets:** `DSCI_AZ_DB_{PROD,DEV}_HOST` decide which server every job talks to; do not repoint them without the team lead's say-so (see [database.md](database.md#network-access)). What they currently hold and why is in the [internal KB → `infrastructure/db-network-access.md`](https://github.com/OCHA-DAP/ds-knowledge-base-internal/blob/main/infrastructure/db-network-access.md).

## The two dev/prod axes (this is the subtle part)

A Databricks pipeline's "dev vs prod" is **two orthogonal things** — both must be right for a job to be a real prod pipeline, and they routinely mismatch during a cutover:

1. **Deployment target — *where it runs & as whom.*** Set by the Databricks Asset Bundle (DAB) `targets: {dev, prod}` (`databricks.yml`). `dev` → runs on a **personal interactive cluster**, deploys under your user, `mode: development`. `prod` → runs on **ephemeral Job Compute** (a fresh cluster per run, under a policy), with an explicit `root_path` + `run_as`.
2. **Data-plane mode — *which data it touches.*** A runtime arg the pipeline code reads — `--mode {local|dev|prod}` (raster-pipelines) or `mode`/`STAGE` (storms, others). It selects the **DEV vs PROD DB + blob** via `ocha-stratus`. Independent of axis 1.

**They can mismatch, and right now several do** (cutover): the live `NHC Pipeline` and `GDACS/ADAM Pipeline` deploy to **prod compute** but run **`mode=dev`** (writing the DEV DB) per a deliberate "flip to prod once ready" step in `ds-storms-pipeline/databricks.yml`. So "is this job producing prod data?" = **(prod target) AND (mode=prod)** — check both. The registry records both columns for exactly this reason.

## Compute policies

Cluster **policies** are the durable, shared compute infra (a policy change has blast radius across every job that uses it). _Snapshot 2026-06-22; single-node row added 2026-10-01._

**Which policy:** jobs run on **Job Compute (single node)** (`0017962FF5D1E3B9`). Jobs still on Job Compute (`000C79D951EAF0D6`) are mid-migration; don't add new ones there. **Scheduled jobs never run on Personal Compute or another interactive cluster.** Dev-target runs may use your personal cluster for development; keep their schedules paused.

**Definitions:** [`databricks-policies/`](databricks-policies/), mirrored daily from the workspace (D114). Change policies in Databricks, not the files. Environment variables are left out; see the policy in Databricks. The table covers the team's policies; the workspace also has the Databricks defaults Shared, Legacy Shared and Power User Compute.

| policy_id | name | what it's for | injects (from `dsci`) |
|---|---|---|---|
| `000C79D951EAF0D6` | **Job Compute** | Ephemeral **prod job clusters**, being replaced by the single-node policy; no new jobs. Fixes `cluster_type=job`, single-worker STANDARD engine; `apply_policy_default_values: true` means a job just names the policy and inherits everything. | AWS_*, CDSAPI_*, CONTAINER_*, **DSCI_AZ_BLOB_PROD_SAS** + dev/blob SAS (DB creds via the same scope) — so prod jobs start with all secrets present, no `spark_env_vars` block needed. |
| `0017962FF5D1E3B9` | **Job Compute (single node)** | Job Compute without the idle worker VM (the pipelines don't use Spark). Built on the same `job-cluster` family, overriding its ban on single-node clusters. | Same as Job Compute, except `GH_FLOODSCAN_TOKEN`. |
| `000945F7985D4950` | **Personal Compute** | Interactive **per-user dev clusters** (e.g. Tristan's running cluster). Same secret injection as Job Compute (incl. AWS/CDSAPI/blob) so dev runs locally mirror prod. | AWS_*, CDSAPI_*, CONTAINER_*, DSCI blob SAS (dev). |
| `00039FDBACC1B739` | **SSH tunnel compute** | Personal single-node clusters (one per user) for **laptop access to the databases** through `databricks ssh` — the only laptop route since the databases went private-endpoint only on 2026-09-30 (how-to: [internal KB → `infrastructure/local-db-access.md`](https://github.com/OCHA-DAP/ds-knowledge-base-internal/blob/main/infrastructure/local-db-access.md)). Not a pipeline policy. About $0.72/h; stop it after use — the 60-min auto-stop did not fire while a tunnel was open (2026-09-29). | — |

**The Job Compute policy is a prod SPOF**: it's how every ephemeral prod job gets its credentials. A change to it (or to the `dsci` scope it references) ripples to all prod jobs. (Wiring it as a node in `dependency-graph.md` is a TODO — see Open questions.)

## Clusters

- **309 of 310 clusters are ephemeral JOB clusters** (all terminated — they exist only for the duration of a run). They are **not** durable infra; don't track them individually.
- **Interactive (UI) clusters are durable and per-user** — currently one running: `0515-161935-i2w5mxhc` "Tristan Downing's Personal Compute Cluster" (policy Personal Compute). The storms bundle also references a GDACS/ADAM dev cluster `0604-214501-kq22m39c` (zarno, isolated lib env).
- **⚠️ A scheduled prod job pinned to a durable interactive cluster is fragile.** If that cluster is deleted/renamed or its owner leaves, the job breaks — prod jobs should target Job Compute (single node), not a standing interactive cluster. **`Storm Alert` (job `500881901438881`) was moved off `0515-…` onto ephemeral Job Compute on 2026-09-15** ([#620](https://github.com/OCHA-DAP/ds-knowledge-base/issues/620); the registry reads `compute=job-compute`, which `gen_pipeline_registry.py` emits only when the job's `new_cluster.policy_id` is the Job Compute policy `000C79D951EAF0D6` — so this is a real redeploy, **not** the read-side flap described below, which can only swap `personal:` ↔ `existing:`). That leaves the `[dev adm_tdowning] NHC Pipeline` (job `583285176982712`) as the remaining job on the **`existing_cluster_id` `0515-…`** — a dev job, so lower stakes. _(infra-drift **flap — it is a read-side artifact, not a cluster change.** `personal:<id>` is assigned only when the id appears in `clusters list` with `cluster_source` `UI`/`API`; an identity that can't list clusters gets an **empty** personal set, and both jobs silently reclassify to `existing:<id>` (and the `PERSONAL-CLUSTER` warn can't fire). Confirmed for **2026-08-10 → 2026-08-11**: the 08-10 fingerprint was taken with the org-scoped `DSCI_DATABRICKS_TOKEN`, which **lacks the `clusters` scope** ([automation.md](automation.md)), and flipped straight back to `personal:` on the next locally-authenticated run. The earlier blips (2026-07-21, 2026-07-26 — each reverting the next run, 07-23 / 07-27) have the same signature; the cause of those empty reads is **unconfirmed**. **Longest run so far: 2026-08-12 → 2026-08-15** (two consecutive fingerprints read `existing:`), reverting to `personal:` on **2026-08-27** ([#573](https://github.com/OCHA-DAP/ds-knowledge-base/issues/573)) — so "it reverts on the very next run" is not a rule; don't read a multi-day `existing:` streak as a real re-pinning. Read an empty personal-cluster column as *not checked*, not *not personal*; to actually settle it, `databricks clusters get 0515-161935-i2w5mxhc`. The pinning fragility stands either way.)_

## Databricks Asset Bundles (DAB) — repo conventions

- **Start a new bundle from [databricks-bundle-template.md](databricks-bundle-template.md)** — the copyable `databricks.yml` that encodes the rules below (policy-owned compute, the five discovery tags, dev/prod targets, failure handling) plus a review checklist for bundle PRs.
- **One bundle can define several independent jobs** (e.g. `ds-storms-pipeline` → `nhc_pipeline` + `gdacs_adam_pipeline`, separate DAGs/schedules/compute). "One bundle" just means one `databricks.yml` deploys them together.
- Jobs pull code from **GitHub `git_source`** (a branch var, default `main`) — so a deploy pins the workspace job to a repo+branch; the cluster clones that branch each run. The drift anchor for a Databricks pipeline is therefore **(git_source branch) + (the bundle file)**, not a checked-out SHA.
- `databricks bundle validate|deploy|run {job} -t {dev|prod} -p DEFAULT`.
- **The generic wrapper `databricks/run_task.py`** (floodexposure / tcd / nga / the four mirrors / hdx-floodscan): every task is `run_task.py <script> --stage {dev|prod} [--env K=V] [--secret NAME] [--optional-secret NAME] [-- script args]`. It sets `STAGE`, copies `src/` + `scripts|pipelines/` off the wsfs checkout to `/local_disk0` (importing off the FUSE mount is flaky), resolves extra `dsci` secrets with `dbutils.secrets.get` at run time and shells out. **Extra secrets go through `--secret`, not `spark_env_vars: {{secrets/dsci/NAME}}`** — a missing or misnamed key in `spark_env_vars` stops the job cluster from launching with an opaque error, while `--secret` fails the task with a readable message (`--optional-secret` for keys the script can do without, e.g. `IPC_AUTH`).
- **Pages sites that used to query the DB from a GitHub runner** (the mirrors, since the private-endpoint cutover) use the *site-data-via-blob* pattern: the Databricks job runs the unchanged `export_site_data.py` then `scripts/site_data_blob.py upload` → dev blob `projects/<repo>/site-data/`; `deploy-site.yml` runs `download` with the org `DSCI_AZ_BLOB_DEV_SAS` on its old backstop cron and deploys the same `site/` dir. Output is identical by construction. Gotcha: the dev storage account has hierarchical namespace, so every folder is a zero-byte marker blob (`metadata.hdi_isfolder`) — list/download/stale-delete must skip them. Alternative when the build needs SQL: the ds-aa-tracking snapshot → throwaway Postgres model.
- **A job that must run on GitHub because of secrets only GitHub holds** (hdx-floodscan: the HDX bot token is an OCHA-DAP org secret) keeps the publish on Actions and moves only the DB half to Databricks (parquet intermediates + manifest on blob, job dispatches the workflow with `GH_FLOODSCAN_TOKEN`, workflow guards on manifest freshness) — see [pipelines/hdx-floodscan.md](../pipelines/hdx-floodscan.md).
- **Not every repo has a `databricks.yml`.** `ds-raster-pipelines` has none — its four jobs (Run ERA5/IMERG/SEAS5/FloodScan) are configured **directly in the workspace UI**, pointing `git_source` at `run_pipeline.py`. For those, the **workspace is the source of truth**, not the repo (re-read via the CLI).

## How a pipeline gets discovered today (and why we're superseding it)

[`pipelines-status`](../pipelines/pipelines-status.md) builds its dashboard by listing Databricks jobs **tagged `databricks=job`** and reading `output_schema` / `type` / `blob_container` tags. Blind spots this surfaces:

- **Tag-reliant:** the live `NHC Pipeline` (959161297191654) and `GDACS/ADAM Pipeline` (197203772269744) are **untagged**, so the dashboard doesn't show them — while the **tagged `Run NHC` it does show is PAUSED**. The dashboard is watching the wrong NHC.
- **Databricks-only:** it can't see the ~10 **GitHub Actions** cron pipelines (floodexposure, country monitoring, afro-cholera, cholera-pdf-scraper, …) — see [deployments.md → GitHub Actions pipelines](deployments.md#github-actions-pipelines).
- **Display-only:** no expected-cadence / freshness / data-plane-mode health; a paused or `mode=dev` job looks fine.

The KB's answer is **[pipeline-registry.md](pipeline-registry.md)** — a generated, job_id-keyed registry covering Databricks **and** GHA that **health-checks each entry's last-success vs its expected cadence**. Its first run flagged 6 down (incl. the two failing storm jobs, the dead NHC GHA workflow, and three stalled monitoring pipelines) — all invisible to `pipelines-status`. Built via `scripts/gen_pipeline_registry.py`; that's what "keeps the trains on the tracks" and supersedes the meta-pipeline.

## Moving jobs to the single-node policy

_Status 2026-10-19._ The rule (jobs go on **Job Compute (single node)** `0017962FF5D1E3B9`; nothing new on `000C79D951EAF0D6`) is in [#710](https://github.com/OCHA-DAP/ds-knowledge-base/pull/710).

**Done: every bundle with a scheduled job.** One PR per repo (branch `ops/single-node-policy`, opened 2026-10-13) swapped `policy_id` and deleted `num_workers` (`ds-storms-pipeline`: `num_workers: 0`, matching its IBTrACS block; cub and hti also gained `apply_policy_default_values: true`). Merged 2026-10-19 08:38–08:40 UTC on Hannah's go-ahead, then deployed 09:07–09:12 UTC with `databricks bundle deploy -t prod` from a fresh clone of `main`, by `adm.tdowning`. Before each deploy, `bundle plan -t prod` showed only `policy_id`, `num_workers` 1 → 0 and the owner. For moz and cub, still on the Terraform engine, the deployed job settings were diffed by hand instead, because their plan lists no field changes; their deploys also migrated them to the direct engine. No job had run on the new policy when this was written: the first scheduled run of each is the real test.

| PR | Jobs (25) |
|---|---|
| [ds-population-mirror#3](https://github.com/OCHA-DAP/ds-population-mirror/pull/3) | Population Mirror |
| [ds-fewsnet-mirror#3](https://github.com/OCHA-DAP/ds-fewsnet-mirror/pull/3) | FEWS NET Mirror |
| [ds-hnrp-mirror#8](https://github.com/OCHA-DAP/ds-hnrp-mirror/pull/8) | HNRP Mirror; HNRP Mirror — weekly full backfill |
| [ds-ipc-mirror#6](https://github.com/OCHA-DAP/ds-ipc-mirror/pull/6) | IPC Mirror |
| [ds-cerf-supplement#135](https://github.com/OCHA-DAP/ds-cerf-supplement/pull/135) | CERF Supplement Daily |
| [ds-floodexposure-monitoring#38](https://github.com/OCHA-DAP/ds-floodexposure-monitoring/pull/38) | Flood Exposure Monitoring; Flood Exposure — Init ISO3 |
| [ds-aa-mdg-monitoring#19](https://github.com/OCHA-DAP/ds-aa-mdg-monitoring/pull/19) | MDG IMERG Monitoring |
| [ds-aa-moz-cyclones-monitoring#26](https://github.com/OCHA-DAP/ds-aa-moz-cyclones-monitoring/pull/26) | MOZ Cyclone Monitoring |
| [ds-aa-nga-flooding#51](https://github.com/OCHA-DAP/ds-aa-nga-flooding/pull/51) | NGA Flash Flood Monitoring; NGA Riverine Flood Monitoring |
| [pa-aa-tcd-flooding#24](https://github.com/OCHA-DAP/pa-aa-tcd-flooding/pull/24) | TCD Flood Monitoring |
| [ds-aa-tracking#17](https://github.com/OCHA-DAP/ds-aa-tracking/pull/17) | AA Tracking Nightly (aa snapshot) |
| [ds-seas5-skill#123](https://github.com/OCHA-DAP/ds-seas5-skill/pull/123) | SEAS5 Skill Monthly Refresh |
| [hdx-floodscan#28](https://github.com/OCHA-DAP/hdx-floodscan/pull/28) | HDX FloodScan Prepare |
| [ds-aa-hti-hurricanes#30](https://github.com/OCHA-DAP/ds-aa-hti-hurricanes/pull/30) | HTI Hurricane Monitoring; HTI DGPC Rainfall Analysis |
| [ds-aa-cub-hurricanes#56](https://github.com/OCHA-DAP/ds-aa-cub-hurricanes/pull/56) | Cuba Hurricane Forecast Monitor; Cuba Hurricane Observational Monitor |
| [ds-storms-alerts#42](https://github.com/OCHA-DAP/ds-storms-alerts/pull/42) | Storm Alert |
| [ds-storms-pipeline#59](https://github.com/OCHA-DAP/ds-storms-pipeline/pull/59) | NHC Pipeline; GDACS/ADAM Pipeline; Run ECMWF Storms (Run IBTrACS was already on it) |
| [ds-pipelines-status#1](https://github.com/OCHA-DAP/ds-pipelines-status/pull/1) | Pipeline Status Refresh |

**Owners after the deploy.** A bundle deploy makes the deployer the job owner (`IS_OWNER`) but leaves `run_as` as the bundle sets it. 23 of the 25 jobs are now owned by `adm.tdowning`. The two Cuba monitors stayed with `adm.zarno1` (owner and `run_as`). Pipeline Status Refresh runs as `adm.hker1`, everything else as `adm.tdowning`. To stop ownership moving with each deploy, and prod jobs depending on personal accounts, see the service-principal proposal in [#790](https://github.com/OCHA-DAP/ds-knowledge-base/pull/790) (under review).

**HDX FloodScan Prepare and `GH_FLOODSCAN_TOKEN`.** The single-node policy does not inject the GitHub dispatch token. The job reads it from the `dsci` scope at run time (`run_task.py --secret GH_FLOODSCAN_TOKEN`), so it does not depend on the policy.

**Still on `000C79D951EAF0D6`** (workspace read 2026-10-19 after the deploys):

- **Scheduled: the four UI-managed raster jobs** in `ds-raster-pipelines` (no bundle): Run ERA5, Run IMERG, Run SEAS5, Run FloodScan. Their owners move them with `databricks jobs update`, together with the Raster Stats job each triggers through a `run_job` task (ERA5 `958368449638566`, FLOODSCAN `957783975148658`, IMERG `809803033083959`, SEAS5 `184508905416553`), which run on the same schedule. **Run FloodScan is blocked** until its `trigger_hdx_publish` notebook stops reading the policy-injected `GH_FLOODSCAN_TOKEN` (Hannah's note on #710).
- **Unscheduled** (they cost only when run): Precip Intercomparison Ingest (`ds-precip-intercomparison`), the SOM GloFAS reforecast downloader (`ds-aa-som-floods`, dev target), Raster Stats CHIRPS, FloodScan - extended testing, hdx-scraper-hno, Add New ISO3 Flood Exposure, an older UI copy of Flood Exposure Monitoring (`652823263317815`; the bundle job is `837650634477282`), `[ops] prod projects schema init (temporary, 2026-09-23)`, and the `[dev adm_zarno1] Flood Fusion` jobs (`ds-flood-gfm-fusion`; Daily is paused).
- **In code only:** the one-off `ds-storms-pipeline/databricks/backfill_nhc_from_archive_*.json` payloads, and [ds-aa-nga-flooding#35](https://github.com/OCHA-DAP/ds-aa-nga-flooding/pull/35) (GloFAS reforecast, open), which adds clusters on the old policy. Fix it when it is rebased.

**Registry label.** Until #710 merges, `gen_pipeline_registry.py` knows only the original policy id, so [pipeline-registry.md](pipeline-registry.md) shows single-node jobs as `job-cluster(custom)`. Nothing is wrong with them.

## Open questions / TODO

- **Job Compute policy is now a node in `dependency-graph.md`** (`dbx-job-compute`, blast radius 9 — raster-pipelines + storms-pipeline + 7 transitive). Still TODO: the `dsci` secret scope as its own node, and per-job (not per-repo) granularity in the graph.
- **DONE — a "pipeline" is a deployed job (job_id / GHA workflow)**, not a repo; multi-pipeline repos get one registry row per job in [pipeline-registry.md](pipeline-registry.md). (Decision: registry + repo pages, D43.)
- **Finish the NHC/GDACS cutover** (flip `mode: dev`→`prod` in the prod target) and **un-pause or retire `Run NHC`**. Prod `storms.nhc_*` is currently written by the **GHA `ds-nhc-forecast`** pipeline, not Databricks — three overlapping NHC jobs (paused prod / dev-cutover DAB / live GHA) are a concurrency + clarity hazard (see [nhc-forecast.md](../pipelines/nhc-forecast.md)).
- **Move `Storm Alert` (and `[dev adm_tdowning] NHC Pipeline`) off the standing interactive cluster `0515-…`** onto Job Compute.
- Auto-refresh: a generator (`gen_pipeline_registry.py`) that reads `databricks jobs list` + `gh workflow list` into the registry, like `gen_db_schema.py`.
