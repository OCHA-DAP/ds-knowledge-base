---
content_type: pipeline
name:              # stable id, e.g. storms-alerts
type:              # dataset-ingest | monitoring | exposure | app  (open vocab)
status:            # live | retired
schedule:          # cron expr | event | manual
deployment:        # where it ACTUALLY runs — see infrastructure/deployments.md
  platform:        # azure-webapp | databricks-job | github-actions | manual
  ref:             # azure app name | databricks job_id | GHA workflow path
  url:             # app url or databricks job url
  resource_group:  # azure only, e.g. IMB-CHD-DataScience-EastUS2
inputs: []         # data sources, blob paths, DB tables it reads  (open vocab)
outputs: []        # blob paths, DB tables, email lists, dashboards it writes
dependencies: []   # ocha-stratus, ocha-relay, Listmonk list ids, ...
downstream: []     # frameworks / apps that consume this output
source_repo:       # local path and/or ocha-dap/<repo>
source_sha:
code_ref: []
pdf: []
visibility:        # internal | public
last_synced:
---

# {Pipeline name}

> Runbook. Optimize for "what feeds it, what it emits, and what to do when it breaks at 2am."

## One-liner
e.g. *daily: pull NHC cyclone forecast → compute ADM0 exposure → email via Listmonk*

## Schedule / trigger
Cron, event, or manual? Which GHA workflow file?

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
