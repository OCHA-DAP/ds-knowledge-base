---
content_type: infrastructure
last_reviewed: "2026-09-30"   # bump when a human verifies the page is still accurate
---

# Databricks bundle template

The starting point for a new `databricks.yml` in a `ds-` pipeline repo, and the reference to check an existing one against. It encodes the decisions every bundle shares so a repo only has to write what is specific to its pipeline: job names, schedules, tasks, libraries, parameters.

Platform background (workspace, the two dev/prod axes, compute policies) is in [databricks.md](databricks.md). This page is the copyable form of those rules.

## What the template fixes, and why

| Decision | Template value | Why |
|---|---|---|
| Compute | `policy_id` = Job Compute (`000C79D951EAF0D6`) with `apply_policy_default_values: true`; no `num_workers` in the bundle | The policy injects the `dsci` secrets and owns the cluster shape. A bundle that restates `num_workers` fights the policy on every change. |
| Node type | `Standard_DS3_v2` unless a comment records why not | None of the team's pipelines use Spark, so all work runs on the driver. Size the driver for the job, and write down the evidence (an OOM date) when going bigger. |
| Availability | `SPOT_WITH_FALLBACK_AZURE` (policy default) | Spot VMs at roughly a third of list price; DBUs are the same either way. |
| Tags | `databricks`, `type`, `kb`, `hazard`, and `output_schema` or `output_blob` | The pipeline registry and `pipelines-status` discover jobs by tag. A job without them is invisible to health monitoring. |
| Targets | `dev` paused and `mode: development`; `prod` with explicit `root_path` and `run_as` | Production mode requires both, and `run_as` pins the SINGLE_USER cluster identity. |
| Data plane | `mode` / `DATA_STAGE` is a job parameter, not hard-coded | Which DB and blob a job touches is the second dev/prod axis and must be switchable without a redeploy. |
| Failure handling | `email_notifications.on_failure`, a `timeout_seconds`, `max_retries: 0` | A hung upstream request (CDS has burned six-hour runs) should fail loudly, not retry silently and double the bill. |

## The template

Replace every `<...>` placeholder. Keep the comments that record decisions; delete the ones that only explain the template.

```yaml
bundle:
  name: <ds-repo-name>

variables:
  mode:
    description: "Data plane (ocha-stratus stage): dev or prod. Set per target below."
    default: dev
  git_branch:
    description: "Branch the job clones each run. Override for a feature test."
    default: main

resources:
  jobs:
    <job_key>:
      name: <Human Readable Job Name>
      description: >-
        <One sentence: what it produces and who consumes it.>

      # Discovery tags. The registry and pipelines-status read these; keep
      # every key present. Vocabularies are open but reuse existing values
      # (see the tag table on this page).
      tags:
        databricks: job
        type: <dataset-ingest | monitoring | raster-stats | publish | alert | exposure>
        kb: <kb page slug, e.g. storms-pipeline>
        hazard: <flood | tropical-cyclone | drought | none>
        output_schema: <schema.table,schema.table>    # or output_blob: <container/path/prefix>

      git_source:
        git_provider: gitHub
        git_url: https://github.com/OCHA-DAP/<ds-repo-name>.git
        git_branch: ${var.git_branch}

      parameters:
        - name: mode
          default: ${var.mode}

      job_clusters:
        - job_cluster_key: main
          new_cluster:
            # Job Compute policy: cluster_type=job, spot with fallback, and
            # every dsci DB/blob secret injected as env vars. Do not add
            # num_workers, spark_env_vars for secrets, or instance pools.
            policy_id: "000C79D951EAF0D6"
            apply_policy_default_values: true
            spark_version: "18.x-scala2.13"
            # DS3_v2 (4 vCPU, 14 GB) is the default. Going larger needs a
            # reason here, e.g. "DS4_v2: adm1 exposure pass OOM-killed on DS3
            # on 2026-08-28".
            node_type_id: "Standard_DS3_v2"
            data_security_mode: SINGLE_USER

      tasks:
        - task_key: <task_key>
          job_cluster_key: main
          spark_python_task:
            python_file: databricks/run_task.py
            source: GIT
            parameters:
              - <pipelines/script.py>
              - --stage
              - "{{job.parameters.mode}}"
          libraries:
            - pypi: {package: ocha-stratus}
            # pin anything whose API has bitten you, e.g. ocha-lens==0.6.1
          timeout_seconds: 3600          # fail loudly instead of burning hours
          max_retries: 0                 # a retry re-spends compute and re-sends emails

      schedule:
        quartz_cron_expression: "0 0 20 * * ?"   # UTC
        timezone_id: UTC
        # No pause_status: prod runs it, dev (development mode) auto-pauses.

      email_notifications:
        on_failure:
          - <team-alias@un.org>
        no_alert_for_skipped_runs: true

targets:
  dev:
    mode: development       # pauses schedules, prefixes job names with "[dev <user>]"
    default: true
    workspace:
      profile: DEFAULT
    variables:
      mode: dev
    # Optional: point tasks at a personal cluster for iteration. Never leave
    # this in a scheduled target.
    # resources:
    #   jobs:
    #     <job_key>:
    #       tasks:
    #         - task_key: <task_key>
    #           existing_cluster_id: <personal cluster id>

  prod:
    mode: production
    workspace:
      profile: DEFAULT
      root_path: /Workspace/Users/<deployer>@global.un.org/.bundle/${bundle.name}/${bundle.target}
    run_as:
      user_name: <deployer>@global.un.org
    variables:
      mode: prod              # or dev while a repo is still on the dev data plane; say so in a comment
```

Deploy with `databricks bundle validate -t prod -p DEFAULT` then `databricks bundle deploy -t prod -p DEFAULT`. The `databricks/run_task.py` wrapper is described under "Databricks Asset Bundles" in [databricks.md](databricks.md); copy it from any of the mirrors.

## Tag vocabulary in use

Open vocabularies: reuse a value below before inventing one. Snapshot of the workspace on 2026-09-30.

| Key | Values in use | Notes |
|---|---|---|
| `databricks` | `job` | Constant. It is the discovery filter. |
| `type` | `dataset-ingest` (14), `monitoring` (7), `raster-stats` (4), `publish`, `alert`, `exposure`, `annotation`, `schema-owner` | One value per job. |
| `kb` | the KB page slug, e.g. `storms-pipeline`, `nga-flooding-monitoring`, `hnrp-mirror` | Links the job to its `pipelines/` page. 23 of 29 active jobs carry it. |
| `hazard` | `tropical-cyclone`, `flood`, `drought` | Use `none` for cross-hazard mirrors rather than omitting the key. 16 of 29 carry it. |
| `output_schema` | `schema.table` list, comma-separated | For jobs that write the DB. |
| `output_blob` | `container/path/prefix` | For jobs that write blob. A job that does both carries both. |
| `input_schema` | `schema.table` | Optional; used once so far. |

## What not to put in a bundle

- `num_workers`. The policy sets it. Restating it means every policy change breaks `bundle validate` in every repo.
- `existing_cluster_id` in a scheduled target. A prod job pinned to a person's interactive cluster dies when that cluster does, and bills All-purpose DBUs at nearly double the job rate. Storm Alert was moved off one on 2026-09-15.
- `spark_env_vars` for `DSCI_*` secrets. The policy injects them. Only add `spark_env_vars` for a secret the policy does not carry, and prefer `run_task.py --secret NAME`.
- A hard-coded data stage. `mode` is a variable so the same bundle can run against dev data from a prod deployment during a cutover.
- Photon or a non-STANDARD runtime engine. The policy fixes STANDARD; nothing here is Spark.

## Review checklist for a bundle PR

- Every job has the five tag keys with values from the table above.
- No `num_workers`, no `existing_cluster_id` outside the `dev` target, no secrets in `spark_env_vars`.
- A node type larger than DS3_v2 has a dated reason in a comment.
- Every task has `timeout_seconds` and `max_retries: 0`.
- `prod` has `root_path` and `run_as`; `dev` has `mode: development`.
- The schedule is in UTC and the KB `pipelines/` page for the job names the same cadence.

## Reference bundles

- [`ds-storms-pipeline/databricks.yml`](https://github.com/OCHA-DAP/ds-storms-pipeline/blob/main/databricks.yml) — several jobs in one bundle, a documented DS4 exception, chained jobs via `trigger_job.py`.
- [`ds-aa-nga-flooding/databricks.yml`](https://github.com/OCHA-DAP/ds-aa-nga-flooding/blob/main/databricks.yml) — the `STAGE` vs `DATA_STAGE` split for a repo that emails from prod but reads dev data.
- The four mirrors (`ds-hnrp-mirror`, `ds-ipc-mirror`, `ds-fewsnet-mirror`, `ds-population-mirror`) — the plain `run_task.py` shape this template is drawn from.

## Pending change: single-node compute

The Job Compute policy currently fixes `num_workers` at 1 and forbids the single-node profile, so every job runs a driver plus an idle worker. A second policy, "Job Compute (single node)", is proposed (September 2026 cost audit): `num_workers` 0, the single-node Spark profile, and `Standard_E4ads_v5` / `Standard_E8ads_v5` added to the node allowlist for the jobs that need more than 14 GB. When it lands, the only bundle change is the `policy_id` value above; this page and the policy id in the template will be updated at the same time.
