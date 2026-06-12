---
content_type: app
name:              # stable id, e.g. hti-hurricanes-app
purpose:           # one line — what it shows / lets you do
status:            # live | retired
tech:              # marimo | dash | streamlit | quarto | other
related:           # framework/pipeline id this serves, or "standalone"
deployment:        # canonical inventory in infrastructure/deployments.md
  platform:        # azure-webapp | gh-pages
  ref:             # azure app name (e.g. chd-ds-...) | gh-pages repo/branch
  url:             # deployed URL
  resource_group:  # azure only, e.g. IMB-CHD-DataScience-EastUS2
inputs: []         # data sources / DB tables / blobs it reads
source_repo:       # local path and/or ocha-dap/<repo>
source_branch:     # work is OFTEN NOT on main
source_sha:
code_ref: []       # entrypoint(s)
visibility:        # internal | public
last_synced:
---

# {App name}

> An interactive deployed surface. Optimize for "what it shows, who it's for, and how to keep it running."

## What it shows
One paragraph: the question this app answers / what a user does with it.

## Key features
The main views / controls. Link to a framework or pipeline page if it serves one.

## Data
What it reads (DB tables, blobs, data sources) and how fresh it is.

## Deployment & access
Where it runs (Azure web app / GH Pages), the URL, prod vs dev slot, who can reach it. Cross-ref `infrastructure/deployments.md`.

## Maintenance / known issues
How it's redeployed, what breaks, dev-vs-prod gotchas.
