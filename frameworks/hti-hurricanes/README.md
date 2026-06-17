# Haiti hurricanes (hti-hurricanes)

National tropical-cyclone AA (wind AND rainfall). Repo: `ocha-dap/ds-aa-hti-hurricanes` — which is simultaneously the analysis repo, the trigger source-of-truth (`constants.py`), and the live monitoring pipeline. Satellite repos: `-app` (Dash trigger app), `-impactmodel` (EMDAT/impact analysis).

**Current version: [2024-08-23](2024-08-23.md)** (status: piloted, Version #1).

## Version lineage

| version | doc | notes |
|---|---|---|
| **2024-08-23** | [unocha](https://www.unocha.org/publications/report/haiti/cadre-daction-anticipatoire-pilote-en-haiti-tempetesouragans) | Pilote #1; 3-stage wind+rain trigger, ~3yr RP |

Active post-v1 trigger R&D (NHC watch/warning OR-trigger) is in `exploration/` but not yet a published v2.

Live pipeline: [pipelines/hti-hurricanes-monitoring](../../pipelines/hti-hurricanes-monitoring.md).
