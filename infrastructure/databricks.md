---
content_type: infrastructure
last_reviewed: "2026-06-23"   # bump when a human verifies the page is still accurate
---

# Databricks — compute platform & the dev/prod model

How the team's **scheduled data pipelines actually run**. Most non-GHA pipelines are Databricks **jobs** in one workspace; this page is the platform reference (workspace, compute policies, clusters, the dev/prod model, bundle conventions). The per-job runtime registry — the authoritative "what's deployed and is it on the rails" list — lives in [deployments.md → Databricks jobs](deployments.md#databricks-jobs); the per-pipeline design/runbook lives on each `pipelines/*.md` page.

> Refresh anything here with the `databricks` CLI, profile **`default`** (the token expires — re-auth with `databricks auth login --profile default`). Snapshot date in each section.

## Workspace

- **Workspace:** `adb-6009046713167663` (Azure Databricks, East US 2), CLI profile **`default`**, current principal `adm.tdowning@global.un.org`.
- **Secret scope `dsci`** — holds the 14 `DSCI_AZ_*` DB/blob credentials (DEV+PROD host/uid/pw/SAS, read + write) plus `AWS_*`, `CDSAPI_*`, `CONTAINER_*`. Referenced as `{{secrets/dsci/<NAME>}}`; surfaced to clusters as env vars, which `ocha-stratus` reads. **Never hard-code creds** — they come from this scope via a policy (below) or an explicit `spark_env_vars` block.

## The two dev/prod axes (this is the subtle part)

A Databricks pipeline's "dev vs prod" is **two orthogonal things** — both must be right for a job to be a real prod pipeline, and they routinely mismatch during a cutover:

1. **Deployment target — *where it runs & as whom.*** Set by the Databricks Asset Bundle (DAB) `targets: {dev, prod}` (`databricks.yml`). `dev` → runs on a **personal interactive cluster**, deploys under your user, `mode: development`. `prod` → runs on **ephemeral Job Compute** (a fresh cluster per run, under a policy), with an explicit `root_path` + `run_as`.
2. **Data-plane mode — *which data it touches.*** A runtime arg the pipeline code reads — `--mode {local|dev|prod}` (raster-pipelines) or `mode`/`STAGE` (storms, others). It selects the **DEV vs PROD DB + blob** via `ocha-stratus`. Independent of axis 1.

**They can mismatch, and right now several do** (cutover): the live `NHC Pipeline` and `GDACS/ADAM Pipeline` deploy to **prod compute** but run **`mode=dev`** (writing the DEV DB) per a deliberate "flip to prod once ready" step in `ds-storms-pipeline/databricks.yml`. So "is this job producing prod data?" = **(prod target) AND (mode=prod)** — check both. The registry records both columns for exactly this reason.

## Compute policies (3)

Cluster **policies** are the durable, shared compute infra (a policy change has blast radius across every job that uses it). _Snapshot 2026-06-22._

| policy_id | name | what it's for | injects (from `dsci`) |
|---|---|---|---|
| `000C79D951EAF0D6` | **Job Compute** | Ephemeral **prod job clusters** — the standard prod pipeline compute. Fixes `cluster_type=job`, single-worker STANDARD engine; `apply_policy_default_values: true` means a job just names the policy and inherits everything. | AWS_*, CDSAPI_*, CONTAINER_*, **DSCI_AZ_BLOB_PROD_SAS** + dev/blob SAS (DB creds via the same scope) — so prod jobs start with all secrets present, no `spark_env_vars` block needed. |
| `000945F7985D4950` | **Personal Compute** | Interactive **per-user dev clusters** (e.g. Tristan's running cluster). Same secret injection as Job Compute (incl. AWS/CDSAPI/blob) so dev runs locally mirror prod. | AWS_*, CDSAPI_*, CONTAINER_*, DSCI blob SAS (dev). |
| `00039FDBACC1B739` | **SSH tunnel compute** | Instance-pool-backed compute for SSH-tunnelled access; not a pipeline policy. | — |

**The Job Compute policy is a prod SPOF**: it's how every ephemeral prod job gets its credentials. A change to it (or to the `dsci` scope it references) ripples to all prod jobs. (Wiring it as a node in `dependency-graph.md` is a TODO — see Open questions.)

## Clusters

- **309 of 310 clusters are ephemeral JOB clusters** (all terminated — they exist only for the duration of a run). They are **not** durable infra; don't track them individually.
- **Interactive (UI) clusters are durable and per-user** — currently one running: `0515-161935-i2w5mxhc` "Tristan Downing's Personal Compute Cluster" (policy Personal Compute). The storms bundle also references a GDACS/ADAM dev cluster `0604-214501-kq22m39c` (zarno, isolated lib env).
- **⚠️ A scheduled prod job pinned to a personal cluster is fragile.** `Storm Alert` (job `500881901438881`) runs on the **`existing_cluster_id` `0515-…`** (Tristan's personal compute) — if that cluster is deleted/renamed or its owner leaves, the job breaks. Prod jobs should target Job Compute, not a person's interactive cluster.

## Cluster how-tos

- **System deps (e.g. `libeccodes-dev` for cfgrib), two ways:** *transient* — run `%sh sudo apt-get install <pkg> --assume-yes` in a notebook cell (lost on cluster restart); *durable* — a **cluster-scoped init script** (`sudo apt-get update && sudo apt-get install <pkg> --assume-yes`) that installs on every cluster start — required for scheduled/long-running jobs.
- **Debugging init scripts:** enable cluster logging (cluster settings) to write logs to `dbfs:/`, then read the stderr log from a notebook: `open('/dbfs/cluster-logs/<cluster-id>/init_scripts/.../<ts>_init.sh.stderr.log').read()`.
- **Gotcha — init scripts run the WORKSPACE copy** of the script file, which is **not auto-synced with the git repo**. A fix committed to the repo doesn't take effect until the workspace copy is updated — a classic "my fix didn't take".
- **Secrets → env vars (one-offs):** the standard `DSCI_AZ_*`/`AWS_*`/`CDSAPI_*` creds already arrive via the compute policies (above). For a new secret: `databricks secrets create-scope --scope <name>` / `databricks secrets put --scope <name> --key <KEY>`, then set `ENV_NAME={{secrets/<scope>/<KEY>}}` in the cluster env-var config — so `os.getenv("ENV_NAME")` works identically locally and on Databricks.

**Operating conventions:**

- Default instance for day-to-day notebook work is **`Standard_DS3_v2`** (4 vCPU / 14 GB), on both Personal and Job compute; escalate only when a job needs it.
- **Job compute is cheaper than personal** (snapshot pricing: DS3_v2 $0.454/hr as a job vs $0.642/hr personal). Anything running **more than a few hours a day should be an automated job**, not an interactive cluster — admins monitor cost and will stop clusters that threaten the budget.
- Recurring env vars belong **in the compute policy** (raise a request to the admins), not per-cluster config.

Digested from the retired DSCI Confluence space (archive: `confluence/` in `ds-knowledge-base-internal`).

## Databricks Asset Bundles (DAB) — repo conventions

- **One bundle can define several independent jobs** (e.g. `ds-storms-pipeline` → `nhc_pipeline` + `gdacs_adam_pipeline`, separate DAGs/schedules/compute). "One bundle" just means one `databricks.yml` deploys them together.
- Jobs pull code from **GitHub `git_source`** (a branch var, default `main`) — so a deploy pins the workspace job to a repo+branch; the cluster clones that branch each run. The drift anchor for a Databricks pipeline is therefore **(git_source branch) + (the bundle file)**, not a checked-out SHA.
- `databricks bundle validate|deploy|run {job} -t {dev|prod} -p DEFAULT`.
- **Not every repo has a `databricks.yml`.** `ds-raster-pipelines` has none — its four jobs (Run ERA5/IMERG/SEAS5/FloodScan) are configured **directly in the workspace UI**, pointing `git_source` at `run_pipeline.py`. For those, the **workspace is the source of truth**, not the repo (re-read via the CLI).

## How a pipeline gets discovered today (and why we're superseding it)

[`pipelines-status`](../pipelines/pipelines-status.md) builds its dashboard by listing Databricks jobs **tagged `databricks=job`** and reading `output_schema` / `type` / `blob_container` tags. Blind spots this surfaces:

- **Tag-reliant:** the live `NHC Pipeline` (959161297191654) and `GDACS/ADAM Pipeline` (197203772269744) are **untagged**, so the dashboard doesn't show them — while the **tagged `Run NHC` it does show is PAUSED**. The dashboard is watching the wrong NHC.
- **Databricks-only:** it can't see the ~10 **GitHub Actions** cron pipelines (floodexposure, country monitoring, afro-cholera, cholera-pdf-scraper, …) — see [deployments.md → GitHub Actions pipelines](deployments.md#github-actions-pipelines).
- **Display-only:** no expected-cadence / freshness / data-plane-mode health; a paused or `mode=dev` job looks fine.

The KB's answer is **[pipeline-registry.md](pipeline-registry.md)** — a generated, job_id-keyed registry covering Databricks **and** GHA that **health-checks each entry's last-success vs its expected cadence**. Its first run flagged 6 down (incl. the two failing storm jobs, the dead NHC GHA workflow, and three stalled monitoring pipelines) — all invisible to `pipelines-status`. Built via `scripts/gen_pipeline_registry.py`; that's what "keeps the trains on the tracks" and supersedes the meta-pipeline.

## Open questions / TODO

- **Job Compute policy is now a node in `dependency-graph.md`** (`dbx-job-compute`, blast radius 9 — raster-pipelines + storms-pipeline + 7 transitive). Still TODO: the `dsci` secret scope as its own node, and per-job (not per-repo) granularity in the graph.
- **DONE — a "pipeline" is a deployed job (job_id / GHA workflow)**, not a repo; multi-pipeline repos get one registry row per job in [pipeline-registry.md](pipeline-registry.md). (Decision: registry + repo pages, D43.)
- **Finish the NHC/GDACS cutover** (flip `mode: dev`→`prod` in the prod target) and **un-pause or retire `Run NHC`**. Prod `storms.nhc_*` is currently written by the **GHA `ds-nhc-forecast`** pipeline, not Databricks — three overlapping NHC jobs (paused prod / dev-cutover DAB / live GHA) are a concurrency + clarity hazard (see [nhc-forecast.md](../pipelines/nhc-forecast.md)).
- **Move `Storm Alert` off the personal cluster** onto Job Compute.
- Auto-refresh: a generator (`gen_pipeline_registry.py`) that reads `databricks jobs list` + `gh workflow list` into the registry, like `gen_db_schema.py`.
