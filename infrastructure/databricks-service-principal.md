---
content_type: infrastructure
last_reviewed: "2026-10-19"   # bump when a human verifies the page is still accurate
---

# Proposal: run and deploy prod Databricks jobs as a service principal

> **Status: proposal for team review, written 2026-10-19. Nothing on this page has been set up.** Discuss it on the pull request that adds this page. If the team agrees, this page becomes the how-to, and the `prod` target in the bundle template (`databricks-bundle-template.md`, added by [#710](https://github.com/OCHA-DAP/ds-knowledge-base/pull/710)) changes to match.

Platform background: [databricks.md](databricks.md). Workspace facts below were read on 2026-10-19.

## In 30 seconds

**Problem.** Prod jobs run as, and are owned by, individual people's admin accounts. Whoever deploys a bundle becomes the owner of its jobs, so ownership moves around every time a different person deploys. Worse, if one of those accounts is switched off, every job that runs as it stops.

**Proposal.** One service principal, `dsci-pipelines`, runs every prod job and is the only identity that deploys prod bundles. A GitHub Actions workflow in each repo deploys the bundle when a change to `databricks.yml` is merged to `main`. People keep full control of the jobs (run, pause, edit) through the `dsci` group.

**Cost.** One-off setup by a workspace admin and a GitHub org admin, then a small PR per repo. Pilot on one bundle first.

## The problem

**Ownership moves with every deploy.** A bundle deploy sets the deploying identity as the job's owner (`IS_OWNER`) and leaves `run_as` as the bundle says. On 2026-10-13 the prod plans showed many jobs owned by `adm.hker1`, the account that had deployed the tag changes. The single-node deploys on 2026-10-19 moved 23 jobs to `adm.tdowning` ([databricks.md → Moving jobs to the single-node policy](databricks.md)). 15 of the 18 prod bundles give the `dsci` group `CAN_MANAGE`, so for most jobs the owner label matters little day to day, but nobody can say who "owns" a pipeline. The other three (`ds-aa-cub-hurricanes`, `ds-aa-hti-hurricanes`, `ds-storms-alerts`) grant nothing, so only the owner and workspace admins can manage those jobs.

**Prod jobs depend on personal accounts.** Of the 29 scheduled (unpaused) jobs on 2026-10-19, 20 run as `adm.tdowning`, 6 as `adm.hker1`, 2 as `adm.itot6` and 1 as `adm.zarno1`. When an admin account is disabled (someone leaves, a contract ends, the admin account is replaced), every job that runs as it fails at its next run. [mdg-monitoring.md](../pipelines/mdg-monitoring.md) already lists this as a gap ("replace with a service principal once one is provisioned").

**Deployment state lives in personal folders.** Every prod target sets `root_path: /Workspace/Users/<person>/.bundle/...`. That folder holds the bundle's deployment state. If it is lost, the next deploy no longer knows the existing jobs and creates a second copy of each, and both copies run on schedule (Databricks allows duplicate job names).

**Deploys are a separate manual step.** Merging a bundle PR changes nothing in the workspace until someone runs `databricks bundle deploy -t prod` from a clean checkout of `main`. It is easy to forget, and different people deploy from different machines.

## Proposed setup

1. **One Databricks-managed service principal, `dsci-pipelines`.** The workspace has no Unity Catalog metastore, so this is a plain workspace service principal created by a workspace admin. No Entra ID app registration is needed (the team cannot create Azure resources). The workspace already has one built the same way: `fji-fms-relay`, which the Fiji FMS relay workflow uses to start a job.
2. **It is the `run_as` of every prod job**, and the only identity that deploys prod. Its jobs are owned by it, permanently.
3. **Deploy on merge from GitHub Actions.** Each repo with a bundle gets a workflow that runs `bundle validate`, `bundle plan` and `bundle deploy -t prod` as the service principal when `databricks.yml` changes on `main`, plus a manual trigger. Review of the bundle PR becomes the deploy gate, and repo rules such as "storms-pipeline merges need Hannah's review" carry over automatically.
4. **Shared deployment state.** `root_path` moves to `/Workspace/Shared/.bundle/${bundle.name}/${bundle.target}`.
5. **People keep control.** Every bundle grants `permissions: dsci CAN_MANAGE` (three need it added), so anyone in the team can run, pause, repair and edit jobs.
6. **Dev targets do not change.** `mode: development` still deploys `[dev <user>]` copies under each person, with schedules paused.

### Bundle `prod` target

```yaml
targets:
  prod:
    mode: production
    workspace:
      # host, not profile: CI has no ~/.databrickscfg. Locally pass -p DEFAULT on the command line.
      host: https://adb-6009046713167663.3.azuredatabricks.net
      root_path: /Workspace/Shared/.bundle/${bundle.name}/${bundle.target}
    run_as:
      service_principal_name: <dsci-pipelines application id>

permissions:
  - group_name: dsci
    level: CAN_MANAGE
```

Today every bundle sets `workspace: profile: DEFAULT` in its targets. The CLI then looks for that profile in `~/.databrickscfg` and fails on a GitHub runner, so the prod target names the host instead.

### Deploy workflow (`.github/workflows/deploy-databricks.yml`)

```yaml
name: Deploy Databricks bundle (prod)
on:
  push:
    branches: [main]
    paths: [databricks.yml, "resources/**"]
  workflow_dispatch:
concurrency: deploy-databricks-prod
jobs:
  deploy:
    runs-on: ubuntu-latest
    env:
      DATABRICKS_HOST: https://adb-6009046713167663.3.azuredatabricks.net
      DATABRICKS_CLIENT_ID: ${{ secrets.DSCI_DATABRICKS_CLIENT_ID }}
      DATABRICKS_CLIENT_SECRET: ${{ secrets.DSCI_DATABRICKS_CLIENT_SECRET }}
    steps:
      - uses: actions/checkout@v4
      - uses: databricks/setup-cli@v1.18.0
      - run: databricks bundle validate -t prod
      - run: databricks bundle plan -t prod
      - run: databricks bundle deploy -t prod
```

`DSCI_DATABRICKS_CLIENT_ID` / `_SECRET` are **OCHA-DAP org secrets**, like the `DSCI_AZ_*` ones, with visibility limited to the repos that deploy bundles. GitHub runners reach the Databricks API (the Fiji relay poller already does), even though they cannot reach the databases.

## One-off setup

| Step | Who | Notes |
|---|---|---|
| Create the service principal: `databricks service-principals create --display-name dsci-pipelines` | workspace admin | Five people are in `admins`, Tristan among them. |
| Grant it `CAN_USE` on the policy **Job Compute (single node)** `0017962FF5D1E3B9` | workspace admin | Today only `adm.hker1` and `admins` have it. |
| Check it can read the `dsci` secret scope | pilot | The scope gives the `users` group `MANAGE` and service principals join `users`, so this should already work, both for the policy's `{{secrets/dsci/...}}` values and for `dbutils.secrets.get` in tasks. Confirm on the pilot run. |
| Create an OAuth secret: `databricks service-principal-secrets-proxy create <id>` and store it as the two org secrets | workspace admin + GitHub org admin | Tristan is not an OCHA-DAP org admin. The secret has a fixed lifetime: record the expiry next to the other token expiries and rotate it. |
| Git access for **private** repos | to decide | Jobs clone their code through `git_source` as `run_as`. For public repos this should need no Git credential (confirm on the pilot). The private `ds-aa-moz-cyclones-monitoring` needs one, created as the service principal with `databricks git-credentials create`. Whose GitHub token goes in it is open: a personal token brings back the one-person dependency for that repo. |
| Leave `databricks-service-principal` alone | — | A second service principal already in the workspace, of unknown origin, in a group Databricks created on 2026-08-05. Find out who made it before reusing or deleting it. |

## Moving a bundle

1. **PR in the repo:** the `prod` target above, the `dsci` grant if missing, plus the deploy workflow.
2. **Bind the existing jobs before the first deploy.** Changing `root_path` starts an empty deployment state. Without a bind, the first deploy **creates a second copy of every job**. For each job, as the service principal: `databricks bundle deployment bind <resource_key> <job_id> -t prod`. Then `bundle plan -t prod` must show only updates, no creates.
3. **Merge.** The workflow deploys. Start one run by hand and check the cluster starts, the code is cloned, secrets resolve and the output lands.

**Pilot: ds-population-mirror.** A public repo with one Python task, writing the dev database idempotently, so a test run is harmless. Then the other bundles in the order of [databricks.md → Moving jobs to the single-node policy](databricks.md).

## Jobs that need extra care

- **Pipeline Status Refresh** (`ds-pipelines-status`) lists every job through the Jobs API as its `run_as`. A service principal sees only the jobs it has permission to view, so the UI-managed raster jobs and any job without a `dsci` grant would silently drop off the dashboard. Options: keep this one job running as a person (recommended for now, written down as the exception); grant the service principal `CAN_VIEW` on each job (drifts); or add it to `admins` (too broad for an identity that already holds every `dsci` secret).
- **ds-storms-pipeline starts other jobs** (Cuba Hurricane Forecast Monitor, HTI Hurricane Monitoring) through the Jobs API in `databricks/trigger_job.py`. The service principal needs `CAN_MANAGE_RUN` on them. That comes with owning them; grant it explicitly while either is still owned by a person.
- **The Cuba monitors** run as and are owned by `adm.zarno1`, and Zack deploys them. Move them with him.
- **UI-managed raster jobs** (`ds-raster-pipelines`: Run ERA5, IMERG, SEAS5, FloodScan and the Raster Stats jobs they trigger) have no bundle. Either set their `run_as` with `databricks jobs update`, or bring them into a bundle first.

## Decisions for the team

1. **One service principal for all prod jobs**, or one per repo? Recommended: one. Every prod job already gets the same `dsci` secrets through the policy, so separate identities would not narrow what a leaked credential can reach.
2. **Deploy from GitHub Actions on merge**, or share the service principal's credentials for local deploys? Recommended: Actions. Shared local credentials are harder to rotate and bring back "who deployed from where".
3. **Hand deploys to prod.** Workspace admins cannot be stopped technically. Proposed rule: never deploy prod by hand; use the workflow's manual trigger.
4. **Who sets and rotates the org secrets** (needs an OCHA-DAP org admin).
5. **Git credential for private repos** (see the setup table).
6. **The Pipeline Status Refresh exception.**

## Alternatives considered

- **Keep personal accounts, but one person always deploys.** Stops ownership moving, but all prod jobs still depend on that person's account.
- **Accept the moving owner label.** It is mostly cosmetic with `dsci CAN_MANAGE`, but leaves the `run_as` risk and the personal `root_path` folders as they are.
- **An Entra ID–managed service principal.** Needs an app registration in the UN tenant through OICT. Not needed for anything on this page.
- **GitHub OIDC federation instead of an OAuth secret.** No stored secret at all, but it needs a federation policy at the Databricks account level (account admin). A possible later improvement.
