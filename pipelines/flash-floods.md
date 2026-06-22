---
content_type: pipeline
name: flash-floods
type: dataset-ingest
status: in-development
deployment:
  platform: manual
  resource_group: null
  jobs: []
inputs: []
outputs: []
dependencies: []
downstream: []
depends_on: []
source_repo: ocha-dap/ds-flash-floods
source_branch: main
source_sha: null
code_ref: []
discrepancies:
  - "[gap] Repository is entirely empty — GitHub reports size 0, zero branches, and the commits API returns HTTP 409 'Git Repository is empty' (verified 2026-06-22). No code, README, or workflows exist, so inputs/outputs/jobs/dependencies are all unknown."
  - "[gap] No deployment exists. `deployment.platform` set to `manual` as a placeholder (not actually run anywhere); flash-floods does NOT appear in infrastructure/deployments.md (no Azure app, no Databricks job, no GHA workflow). Revisit once the first commit lands."
extra:
  repo_state: empty
  collaboration: "Luxembourg Institute for Science and Technology (LIST)"
  github_description: "Collaboration between the Centre for Humanitarian Data and Luxembourg Institute for Science and Technology on flash floods"
  created_at: "2026-03-25"
  schema_strain: "Empty repo: all operational fields (jobs, inputs, outputs, dependencies, downstream) left empty pending first commit. status=in-development, deployment.platform=manual are placeholders, not observed facts."
visibility: internal
last_synced: 2026-06-22
---

# Flash Floods

> Runbook. Optimize for "what feeds it, what it emits, and what to do when it breaks at 2am."

## One-liner

**No code yet — placeholder page.** Planned collaboration between the OCHA Centre for Humanitarian Data and the Luxembourg Institute for Science and Technology (LIST) on flash floods (per the GitHub repo description). Repository `ocha-dap/ds-flash-floods` was created 2026-03-25 and is still empty as of 2026-06-22 (GitHub API: size 0, no branches, commits API returns 409 "Git Repository is empty"). `status: in-development`.

## Jobs & schedule

No jobs exist — the repository has zero commits. Not deployed anywhere: flash-floods is absent from [infrastructure/deployments.md](../infrastructure/deployments.md) (no Azure web app, no Databricks job, no scheduled GitHub Actions workflow). `deployment.platform: manual` is a placeholder, not an observed runtime.

| job | ref | schedule | status |
|---|---|---|---|
| — | — | — | — |

## Inputs

Unknown — no code has been committed. The repo description suggests flash flood data processing in collaboration with LIST.

## Steps

No code to document. Return here once the first commit lands.

## Outputs

Unknown — no code or schema definitions exist.

## Dependencies

Unknown.

## Failure modes & debugging

Not applicable — pipeline has not launched.

<!-- TODO: populate once code exists. Check for GHA workflows, databricks.yml, and src/ entrypoints. -->

## Downstream consumers

None. Not referenced by any existing framework, pipeline, or app page in the KB (no `depends_on` edges point here). Revisit once outputs exist.
