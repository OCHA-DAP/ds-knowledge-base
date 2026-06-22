---
content_type: pipeline
name: unified-disaster-database
type: dataset-ingest
status: retired
deployment:
  platform: manual
  resource_group: null
  jobs: []
inputs: []
outputs: []
dependencies: []
downstream: []
depends_on: []
source_repo: ocha-dap/ds-unified-disaster-database
source_branch: null   # no branch exists — repo has no default branch / zero commits
source_sha: null
code_ref: []
discrepancies:
  - "[gap] Repo is entirely empty (created 2024-09-26, 0 commits, no default branch, PRIVATE, diskUsage 0). No code, README, or workflows to ingest — page is a placeholder stub until code lands."
  - "[gap] Not present in any runtime registry (infrastructure/deployments.md): no Databricks job, no chd-* Azure web app, no GitHub Actions workflow maps to this repo."
extra:
  repo_state: "empty — created 2024-09-26, zero commits, no default branch, no code ever pushed (verified via gh: isEmpty=true, diskUsage=0)"
  github_size: 0
  intent: "unknown — no README, no issues, no code to infer purpose from"
visibility: internal
last_synced: 2026-06-22
---

# Unified Disaster Database

> Runbook. Optimize for "what feeds it, what it emits, and what to do when it breaks at 2am."

## One-liner

**No runbook possible — this repo has never had code pushed to it.** The GitHub repository `ocha-dap/ds-unified-disaster-database` was created on 2024-09-26 and remains entirely empty (zero commits, zero branches, no files). There is nothing to document yet.

## Jobs & schedule

| job | ref | schedule | status |
|---|---|---|---|
| (none) | — | — | — |

No jobs exist. Cross-checked against [infrastructure/deployments.md](../infrastructure/deployments.md): this repo appears in **none** of the three registries — no Databricks job (13 jobs, none map here), no `chd-*` Azure web app (20 apps, none map here), and no GitHub Actions workflow has ever been pushed.

## Inputs

None known. No code exists to inspect.

## Steps

No code to document.

## Outputs

None known.

## Dependencies

None known.

## Failure modes & debugging

Not applicable — no pipeline is running.

If this pipeline is ever implemented, key things to capture here:
- Where the upstream disaster data comes from (GDACS? EM-DAT? ADAM?)
- Where the unified output is written (blob path convention, DB table)
- Authentication / secret scopes required
- Log location (Databricks job runs or GHA workflow logs)

## Downstream consumers

Unknown. No pipeline documentation exists to identify who would consume the output.

<!-- TODO [gap]: Repo empty as of 2026-06-22 (0 commits, no default branch). Re-ingest from the actual implementation once code is pushed. The name suggests a cross-hazard unified disaster event database — plausible consumers include AA framework monitoring pipelines (e.g. GDACS/ADAM-fed) and apps needing a harmonised event feed. Until then this page stays a placeholder; the empty-repo state is the only fact. -->
