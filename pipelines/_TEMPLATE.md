---
content_type: pipeline
name:              # stable id, e.g. storms-alerts
type:              # dataset-ingest | monitoring | exposure | alert  (open vocab; apps are their own content type)
status:            # live | retired  (overall)
deployment:        # where it ACTUALLY runs — inventory in infrastructure/deployments.md
  platform:        # databricks-job | github-actions | azure-webapp | manual  (dominant platform)
  resource_group:  # azure only, e.g. IMB-CHD-DataScience-EastUS2
  jobs:            # ONE ENTRY PER deployed job/workflow — a pipeline repo is OFTEN several
    - { name: , ref: , schedule: , status: }   # name; databricks job_id | GHA workflow path | azure app; cron|event|on-demand; live|paused|retired
inputs: []         # data sources, blob paths, DB tables it reads  (open vocab)
outputs: []        # blob paths, DB tables, email lists, dashboards it writes
dependencies: []   # ocha-stratus, ocha-relay, Listmonk list ids, ...
downstream: []     # frameworks / apps that consume this output
source_repo:       # local path and/or ocha-dap/<repo>
source_branch:     # which branch this page reflects — work is OFTEN NOT on main
source_sha:
code_ref: []
extra: {}          # free-form escape hatch — anything the schema doesn't capture YET. NOT for things that already have a field.
visibility:        # internal | public
last_synced:
---

# {Pipeline name}

> Runbook. Optimize for "what feeds it, what it emits, and what to do when it breaks at 2am."

## One-liner
e.g. *daily: pull NHC cyclone forecast → compute ADM0 exposure → email via Listmonk*

## Jobs & schedule
A pipeline repo is often several jobs/workflows with different schedules. List them (one row even if single):

| job | ref | schedule | status |
|---|---|---|---|
| … | … | … | … |

## Inputs
Which `data_sources`, blobs, DB tables it reads.

## Steps
The flow, briefly. Link `code_ref` for detail.

## Outputs
Blob paths, DB tables, email lists, dashboards it writes.

## Dependencies
Libraries, services, list IDs, secrets/env it needs.

## Failure modes & debugging
What breaks, how to tell, where the logs are. The tribal knowledge.

## Downstream consumers
Which framework's monitoring or which app depends on this. Link them.
