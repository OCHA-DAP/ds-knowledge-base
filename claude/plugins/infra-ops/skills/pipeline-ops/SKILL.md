---
name: pipeline-ops
description: Deploy, debug, or modify the team's scheduled pipelines (Databricks jobs + GitHub Actions crons) — the two-axis dev/prod model, DAB conventions, secrets, and where to check what's deployed and healthy. Use BEFORE debugging a pipeline that "stopped working" or deploying/changing any scheduled job.
---

# Pipeline operations the team way

Platform reference: KB `infrastructure/databricks.md`. What's deployed and whether
it's healthy: KB `infrastructure/pipeline-registry.md` (generated; job-id-keyed,
covers Databricks AND GHA, health = last-success vs expected cadence). Per-pipeline
runbooks: KB `pipelines/*.md`.

## First move when something "stopped working"

Check **`infrastructure/pipeline-registry.md`** before reading any code — it already
knows every deployed job, its schedule, and whether it's on the rails. Many
"pipeline bugs" are a paused job, an expired token, or a job that was never the one
actually writing prod data.

## The two dev/prod axes (the subtle part — check BOTH)

A job is a real prod pipeline only if **both** are prod; they routinely mismatch
during cutovers:

1. **Deployment target** — where it runs & as whom. DAB `targets: {dev, prod}`:
   `dev` → personal interactive cluster under your user; `prod` → ephemeral Job
   Compute under a policy, explicit `root_path` + `run_as`.
2. **Data-plane mode** — which data it touches. A runtime arg (`--mode
   {local|dev|prod}` or `STAGE`) selecting DEV vs PROD DB/blob via `ocha-stratus`.

"Is this job producing prod data?" = (prod target) AND (mode=prod). The registry
records both columns for exactly this reason.

## Conventions

- **Secrets**: everything comes from the Databricks secret scope `dsci`
  (`{{secrets/dsci/<NAME>}}` → env vars that stratus reads) via the compute
  policies. **Never hard-code credentials**; prod jobs on the Job Compute policy
  start with all secrets present.
- **DAB**: one bundle (`databricks.yml`) can define several independent jobs; jobs
  pull code via GitHub `git_source` (branch, default `main`) — the drift anchor is
  (branch + bundle file), not a SHA.
  `databricks bundle validate|deploy|run {job} -t {dev|prod} -p DEFAULT`.
- **Not every repo has a bundle** — some jobs are configured directly in the
  workspace UI (e.g. the raster pipelines); there the **workspace is the source of
  truth**, re-read it via the CLI (profile `default`; token expires —
  `databricks auth login --profile default`).
- **Never pin a scheduled prod job to a personal interactive cluster** — it breaks
  when the owner's cluster goes away. Prod jobs target the Job Compute policy.
- **GHA cron pipelines exist too** (~10: flood exposure, country monitoring,
  cholera scrapers…) — same registry, same health rules; a workflow on a repo's
  default branch is the deployed thing.
- **Git**: changes land on `main` via PR (KB `infrastructure/conventions.md`);
  scheduled mechanical regeneration jobs are the exception.
