---
content_type: infrastructure
last_reviewed: "2026-11-04"   # bump when a human verifies the page is still accurate
---

# Databricks bundle template

The starting point for a new `databricks.yml` in a `ds-` pipeline repo, and the reference to check an existing one against. It encodes the decisions every bundle shares so a repo only has to write what is specific to its pipeline: job names, schedules, tasks, libraries, parameters.

Platform background (workspace, the two dev/prod axes, compute policies) is in [databricks.md](databricks.md). This page is the copyable form of those rules, including [which policy to use](databricks.md#compute-policies).

## What the template fixes, and why

| Decision | Template value | Why |
|---|---|---|
| Compute | `policy_id` = Job Compute (single node) (`0017962FF5D1E3B9`) with `apply_policy_default_values: true`; no `num_workers` in the bundle | The policy injects the `dsci` secrets and owns the cluster shape: one VM, single-node profile, Jobs DBU rate. A bundle that restates `num_workers` fights the policy on every change. |
| Node type | `Standard_DS3_v2` unless a comment records why not | None of the team's pipelines use Spark, so all work runs on the one node. Size it for the job, and write down the evidence (an OOM date) when going bigger. Jobs that need more than 14 GB: `Standard_E4ads_v5` (32 GB) or `Standard_E8ads_v5` (64 GB), which cost less per hour than the DS4/DS5 they replace. |
| Availability | `SPOT_WITH_FALLBACK_AZURE` (policy default) | Applies to workers only: job clusters get `first_on_demand: 1`, so the single driver node runs on-demand. The saving over the original policy is the dropped worker VM and its DBUs, not spot. Left at the default so any future multi-node job gets spot workers. |
| Tags | The block in [databricks.md → Job tags](databricks.md#job-tags--required-on-every-scheduled-job) | The pipeline registry and `pipelines-status` discover jobs by tag. A job without them is invisible to health monitoring. |
| Targets | `dev` paused and `mode: development`; `prod` with explicit `root_path` and `run_as` | Production mode requires `root_path` (`bundle validate -t prod` errors without it, CLI 1.18.0). `run_as` is not enforced, but it pins the job's identity so it does not follow whoever deploys. |
| Data plane | `mode` / `DATA_STAGE` is a job parameter, not hard-coded | Which DB and blob a job touches is the second dev/prod axis and must be switchable without a redeploy. |
| Permissions | `dsci` group `CAN_MANAGE` on every job | Without it a job can only be edited or re-run by whoever deployed it and by workspace admins, and ownership moves with each deploy. |
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
        <One line of at most 15 words, with the external source linked in Markdown.>

      # Discovery tags. The registry and pipelines-status read these. Values
      # and rules: databricks.md -> Job tags. Omit hazard for hazard-agnostic
      # jobs; never write none.
      tags:
        databricks: job
        type: <dataset-ingest | monitoring | exposure | alert | publish | annotation | schema-owner>
        kb: <kb page slug, e.g. storms-pipeline>
        hazard: <drought | flood | tropical-cyclone | cholera | plague>
        output_schema: <schema.table,schema.table>    # and/or output_blob: <container/path/prefix>

      permissions:
        - group_name: dsci
          level: CAN_MANAGE

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
            # Job Compute (single node) policy: one VM, cluster_type=job, spot
            # with fallback, every dsci DB/blob secret injected as env vars.
            # Do not add num_workers, spark_env_vars for secrets, or pools.
            policy_id: "0017962FF5D1E3B9"
            apply_policy_default_values: true
            spark_version: "18.x-scala2.13"
            # DS3_v2 (4 vCPU, 14 GB) is the default. Going larger needs a
            # reason here, e.g. "E4ads_v5: adm1 exposure pass OOM-killed on
            # DS3 on 2026-08-28".
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
    # Optional: iterate on a personal cluster. Do not override
    # existing_cluster_id here on top of job_cluster_key (the task ends up with
    # both compute settings); instead leave compute off the base task and set
    # job_cluster_key in prod and existing_cluster_id in dev, as
    # ds-storms-pipeline does. Never leave a personal cluster in a scheduled
    # target.

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

## Tag vocabulary

The tag keys, their vocabularies and the rules (one `type` per job, `hazard` omitted rather than `none`, descriptions of at most 15 words) are defined once, in [databricks.md → Job tags](databricks.md#job-tags--required-on-every-scheduled-job), which matches what `fetch_pipelines.py` reads. This page does not repeat them.

## What not to put in a bundle

- `num_workers`. The policy fixes it at 0. `bundle validate` does not check it (a restated `1` passes locally and is only refused by the workspace), and restating it at all means every policy change breaks every repo.
- `existing_cluster_id` in a scheduled target. A prod job pinned to a person's interactive cluster dies when that cluster does, and bills All-purpose DBUs at nearly double the job rate. Storm Alert was moved off one on 2026-09-15.
- `spark_env_vars` for `DSCI_*` secrets. The policy injects them. Only add `spark_env_vars` for a secret the policy does not carry, and prefer `run_task.py --secret NAME`.
- A hard-coded data stage. `mode` is a variable so the same bundle can run against dev data from a prod deployment during a cutover.
- Photon or a non-STANDARD runtime engine. The policy fixes STANDARD; nothing here is Spark.

## Review checklist for a bundle PR

- Every job has the tag block from [databricks.md → Job tags](databricks.md#job-tags--required-on-every-scheduled-job) and a description of at most 15 words.
- Every job grants the `dsci` group `CAN_MANAGE`.
- No `num_workers` (a redundant `num_workers: 0`, as in the storms IBTrACS job, is harmless but unnecessary), no `existing_cluster_id` outside the `dev` target, no secrets in `spark_env_vars`.
- A node type larger than DS3_v2 has a dated reason in a comment.
- Every task has `timeout_seconds` and `max_retries: 0`.
- `prod` has `root_path` and `run_as`; `dev` has `mode: development`.
- The schedule is in UTC and the KB `pipelines/` page for the job names the same cadence.

## Reference bundles

- [`ds-storms-pipeline/databricks.yml`](https://github.com/OCHA-DAP/ds-storms-pipeline/blob/main/databricks.yml) — several jobs in one bundle, a documented DS4 exception, chained jobs via `trigger_job.py`.
- [`ds-aa-nga-flooding/databricks.yml`](https://github.com/OCHA-DAP/ds-aa-nga-flooding/blob/main/databricks.yml) — the `STAGE` vs `DATA_STAGE` split for a repo that emails from prod but reads dev data.
- The four mirrors (`ds-hnrp-mirror`, `ds-ipc-mirror`, `ds-fewsnet-mirror`, `ds-population-mirror`) — the plain `run_task.py` shape this template is drawn from.

## Migration from the original Job Compute policy

The status of the move, and what is still on `000C79D951EAF0D6`, has one home: [databricks.md → Moving jobs to the single-node policy](databricks.md#moving-jobs-to-the-single-node-policy). For a bundle the change is to swap `policy_id` and delete `num_workers`, then `bundle deploy -t prod`; the UI-created raster jobs are moved with `databricks jobs update`.
