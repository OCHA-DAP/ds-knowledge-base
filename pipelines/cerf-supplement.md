---
content_type: pipeline
name: cerf-supplement
type: annotation
status: live
deployment:
  platform: databricks
  resource_group: null
  # One Databricks job (databricks.yml, Job Compute policy), four chained tasks running the
  # unchanged scripts via databricks/run_task.py. Replaced four workflow_run-chained GitHub
  # Actions workflows on 2026-09-25 (runners lost DB access). Only deploy-site stays on GHA.
  jobs:
    - { name: "CERF Supplement Daily", ref: "databricks.yml (job id 326008260177607; tasks refresh → match_storms → match_droughts → publish_site)", schedule: "daily 05:30 UTC", status: live }
    - { name: "deploy-site", ref: ".github/workflows/deploy-site.yml", schedule: "dispatched by publish_site + push + daily 08:00 UTC backstop; reads site/data.json from the dev blob, no DB", status: live }
inputs:
  - "OneGMS API: https://cerfgms-webapi.unocha.org/v1/application/All.xml (all CERF applications, XML) — refreshed into aa.cerf_allocation each run"
  - "CBPF OData API: https://cbpfapi.unocha.org/vo2/odata (AllocationTypes + MstPooledFund + per-fund ProjectSummary) — refreshed into aa.cbpf_* each run (see datasets/cbpf-odata.md)"
  - "OneGMS API: https://cerfgms-webapi.unocha.org/v1/project/All.json (all agency projects, ~18 MB, ~8 min server-side generation) — refreshed into aa.cerf_project (+ _sector/_country) each run"
  - "DB table: storms.ibtracs_storms (sid, name, season — the matchable storm universe)"
  - "DB tables: aa.cerf_allocation_storm + aa.cerf_supplement (existing matches/periods, read each run)"
outputs:
  - "DB table: aa.cerf_allocation (the pure OneGMS mirror — refresh_mirror.py is its sole writer)"
  - "DB tables: aa.cerf_project + aa.cerf_project_sector + aa.cerf_project_country (project-level OneGMS mirror, keyed project_code — refresh_projects.py is their sole writer; matchers don't read them)"
  - "DB tables: aa.cbpf_allocation (737 Standard/Reserve envelopes, key (pooled_fund_id, allocation_type_id) — AllocationTypeId alone collides across funds) + aa.cbpf_fund (46 pooled funds incl. RhPF) — refresh_cbpf.py sole writer; also (re)creates aa.v_allocation, the fund-agnostic UNION view over the CERF + CBPF allocation mirrors"
  - "DB tables: aa.cbpf_project (16.3k; one row per grant to ONE implementing partner, key chf_project_code) + aa.cbpf_project_cluster + aa.cbpf_project_subip (##-delimited sub-IP cells exploded) — refresh_cbpf_projects.py sole writer"
  - "DB table: aa.cerf_allocation_storm (application_code, sid) — one row per matched storm"
  - "DB table: aa.cerf_supplement (application_code, not_tc, not_drought, valid_month/year_start/end, confidence, notes, updated_at)"
  - "GitHub Pages site: https://ocha-dap.github.io/ds-cerf-supplement/ (site/data.json, regenerated each deploy; Storms + Droughts tabs)"
  - "GitHub issues (labels cerf-sid, cerf-drought) for allocations needing human input"
dependencies:
  - "ocha-stratus (DB read/write engine)"
  - "DSCI_AZ_DB_DEV_HOST / _UID / _PW (read)"
  - "DSCI_AZ_DB_DEV_UID_WRITE / _PW_WRITE (write — daily writers)"
  - "PGSSLMODE=require (Azure Postgres SSL)"
  - "CLAUDE_CODE_OAUTH_TOKEN (Claude Code, for the match-storms Claude job)"
  - "GITHUB_TOKEN (issues: write — provided by Actions)"
downstream:
  - "aa schema joins: aa.cerf_allocation_storm × aa.cerf_allocation × storms.ibtracs_storms (allocation × storm × track)"
depends_on:
  - "storms-pipeline"      # storms.ibtracs_storms (Databricks 'Run IBTrACS' job) — a storm must be ingested before it can be matched
  - "cerf-onegms"          # the OneGMS feed dataset; this pipeline now upserts its feed columns into aa.cerf_allocation (refresh_mirror.py), while the KB loader owns the AA layer
discrepancies:
  - "[gap] storms.ibtracs_storms is only current to ~Feb 2026 (provisional storms); allocations whose storm isn't ingested yet (e.g. Maila/Sinlaku Apr 2026) stay open until storms-pipeline catches up, then auto-match."
  - "[gap] 22 of 193 RR drought allocations remain unresolved after the two-pass 2026-07-14 backfill (155 dated ≥ 0.8, 16 flagged not_drought ≥ 0.9) — each has an open cerf-drought issue with the sub-threshold suggestion (mixed-driver crises: Zimbabwe 2008-10 economic collapse, Lesotho/Nepal food-price entanglement, bimodal-season ambiguity)."
  - "[resolved 2026-07-13/D83] aa.cerf_allocation is now a PURE OneGMS mirror with refresh_mirror.py as its sole writer — the curated aa_adhoc/aa_note columns moved into aa.activation_allocation (the KB's DB-as-source crosswalk, curated via the kb-aa-links confirm flow). See cerf-onegms.md."
surfaces:
  - {url: "https://ocha-dap.github.io/ds-cerf-supplement/", kind: dashboard, title: "CERF supplement review — Storms + Droughts tabs"}
  - {url: "https://ocha-dap.github.io/ds-cerf-supplement/mirror/", title: "CBPF mirror — ERD", auto: true, first_seen: 2026-09-18}
  - {url: "https://ocha-dap.github.io/ds-cerf-supplement/review/", title: "CERF Allocations × Storms & Droughts", auto: true, first_seen: 2026-09-18}
source_repo: ocha-dap/ds-cerf-supplement
source_branch: main
source_sha: 9888263
code_ref:
  - "src/cerf_api.py — OneGMS API fetch + XML parse (RR/UF, keyed ApplicationCode; classify_type Storm/Drought)"
  - "src/db.py — storms.ibtracs_storms query"
  - "src/storage.py — DB read/write for aa.cerf_supplement + aa.cerf_allocation_storm"
  - "scripts/refresh_mirror.py — daily OneGMS-feed upsert into aa.cerf_allocation (sole writer of the pure mirror)"
  - "scripts/refresh_projects.py — daily OneGMS project-feed upsert into aa.cerf_project + _sector/_country splits (sole writer; key projectCode — projectID has ~3.1k collisions)"
  - "scripts/refresh_cbpf.py — daily CBPF/RhPF allocation + fund mirror from the CBPF OData API, + aa.v_allocation view (sole writer; CERF rows in that feed excluded)"
  - "scripts/refresh_cbpf_projects.py — daily CBPF project-level mirror (per-fund ProjectSummary fetch; cluster + sub-IP splits; admin locations deliberately not mirrored)"
  - "scripts/check_storm_sids.py — daily deterministic backfill + issue management (match-storms job 1; issue helpers shared via label= param)"
  - "scripts/prepare_claude_input.py + prompts/match_storms.md + scripts/apply_claude_matches.py — Claude storm matcher (match-storms job 2)"
  - "scripts/prepare_drought_input.py + prompts/match_droughts.md + scripts/apply_drought_matches.py — Claude drought matcher (match-drought)"
  - "scripts/export_site_data.py + site/index.html — static GH Pages site (Storms/Droughts tabs)"
extra:
  db_schema: aa
  key_column: ApplicationCode
  scope: "Rapid Response storm + drought allocations (WindowFullName='Rapid Response'); Underfunded excluded by definition"
  python_version: "3.12 (psycopg2-binary fails on 3.14+); CI installs with uv --no-sources (ocha-stratus from PyPI)"
visibility: internal
last_synced: "2026-08-25"
---

# CERF Supplement

> Runbook. Optimize for "what feeds it, what it emits, and what to do when it breaks at 2am."

## One-liner

Enriches CERF **storm** allocations with the IBTrACS storm(s) they responded to (and
flags the ones that aren't tropical cyclones), and CERF **drought** allocations with
their **valid period** — the months of the actual meteorological drought (rainfall
deficit), often up to a year before the allocation. Fully automated as a **chained
daily pipeline**: refresh the OneGMS mirror → match storms → match droughts → deploy.
The annotations live in the dev DB (`aa` schema) and publish to a static GitHub Pages
site. Since 2026-08 this repo is also **the home of all OneGMS mirrors**: the CERF
allocation + project mirrors and the **CBPF/regional-fund mirrors**
(`aa.cbpf_allocation`/`_fund`/`_project*`, from the public
[CBPF OData API](../infrastructure/datasets/cbpf-odata.md)) plus `aa.v_allocation`,
the fund-agnostic union view — future OneGMS-sourced mirrors belong here too. Humans are looped in only for uncertain cases, via GitHub issues (Claude-proposed
periods below the 0.8 confidence bar are suggested on the issue, not written).

Keyed on **`ApplicationCode`** — `ApplicationID` is NOT unique in the OneGMS feed
(~431 collisions). Scope is **Rapid Response** storm allocations only (Underfunded
Emergencies aren't triggered by a specific storm, so they're out of scope).

## Jobs & schedule

One Databricks job, **CERF Supplement Daily** (`databricks.yml`, job 326008260177607,
05:30 UTC, pulls `main` at run time — code ships on merge, `databricks bundle deploy -t prod
-p DEFAULT` only when the job config changes). Four chained tasks on one ephemeral Job
Compute cluster, each running the unchanged scripts in order through
`databricks/run_task.py` (sets `STAGE`, copies `src/`+`scripts/`+`prompts/` off wsfs,
resolves the two extra `dsci` secrets, stops at the first failure). Since 2026-09-25;
before that the same chain was four `workflow_run`-linked GitHub Actions workflows.

```
refresh ─▶ match_storms ─▶ match_droughts ─▶ publish_site ─▶ (GitHub Actions) deploy-site
```

| task | what it does |
|---|---|
| `refresh` | `refresh_mirror` → `refresh_projects` → `refresh_cbpf` → `refresh_cbpf_projects`: upsert the OneGMS feed into `aa.cerf_allocation` (feed columns + deterministic `aa_keyword`; sole writer of the pure mirror) and the project / CBPF mirrors; makes new allocations matchable. (`refresh_contributions` joins the list once [ds-cerf-supplement#129](https://github.com/OCHA-DAP/ds-cerf-supplement/pull/129) lands.) |
| `match_storms` | **deterministic** (`check_storm_sids --write`): parse storm name(s) from the title → resolve against `storms.ibtracs_storms`; auto-backfill unambiguous matches; open a `cerf-sid` issue for the rest; auto-close resolved/out-of-scope. **Claude** (`prepare_claude_input` → `run_claude prompts/match_storms.md` → `apply_claude_matches`): Claude Code researches the still-unresolved ones (summary + web), reads human replies on open issues (authoritative), applies only confidence ≥ 0.8 validated matches |
| `match_droughts` | no deterministic stage: Claude Code dates each undated RR drought allocation's valid (rainfall-deficit) period from the OneGMS narratives + the cerf.un.org project titles + web (climatological rainy-season fallback when no source names the season); apply validates (months 1–12, span ≤ 24 mo, within 2 yrs of the allocation) and writes only confidence ≥ 0.8 (confidence + reasoning stored on the row), or `not_drought` at ≥ 0.9; the rest get a `cerf-drought` issue with the suggestion. Prepare skips undated allocations whose issue is open with no reply — daily workload = new allocations + replies, not the backlog |
| `publish_site` | `export_site_data` rebuilds `site/data.json` from the DB; `publish_site_data` uploads it to the dev blob (`projects/ds-cerf-supplement/site/data.json`) and dispatches `deploy-site.yml`, which downloads it (`fetch_site_data.py`) and deploys `site/` to GitHub Pages |

**The Claude steps run the Claude Code CLI headlessly on the cluster** (`scripts/run_claude.py`:
installs the CLI with the native installer at run time, `--allowedTools Read,Write,Edit,WebSearch,WebFetch`,
model `claude-sonnet-5`, every `DSCI_*` variable stripped from Claude's environment — as
on GitHub, Claude never holds DB credentials; the apply scripts do all validated writes).
Two `dsci` secrets beyond the policy-injected `DSCI_AZ_*`, resolved by the wrapper with
`--secret` (a missing key fails the task with a readable message rather than the cluster
launch): `CERF_SUPPLEMENT_GH_TOKEN` (exposed as `GITHUB_TOKEN`; a `repo`+`workflow`-scoped
PAT — issues + deploy dispatch) and `CLAUDE_CODE_OAUTH_TOKEN`. Automation comments are
recognised by their `🤖`/`✅` prefixes, so a user-owned token does not turn the job's own
comments into "human guidance".

**Matchers chain rather than fan out** — both write `aa.cerf_supplement` via a
transactional full-replace, so they must not run concurrently. Add another matcher as
a new task `depends_on` the last one, and move `publish_site`'s dependency to it.

## Inputs

1. **OneGMS CERF API** (`.../application/All.xml`) — all CERF applications; `refresh_mirror.py` upserts the whole feed into `aa.cerf_allocation`, and `src/cerf_api.py` parses it for matching (filtered to `EmergencyTypeName=="Storm"` & `WindowFullName=="Rapid Response"`).
2. **`storms.ibtracs_storms`** (`sid`, `name`, `season`) — the matchable storm universe; a storm must be ingested here before it can be matched.
3. **`aa.cerf_supplement` + `aa.cerf_allocation_storm`** — the existing matches, read at the start of each run.

## Outputs (source of truth = the DB, schema `aa`)

- **`aa.cerf_allocation`** — the **pure OneGMS mirror**, refreshed daily by `refresh_mirror.py` (idempotent upsert keyed on `application_code`; sole writer). The KB's AA layer (`aa.actual_activation` + the curated `aa.activation_allocation` crosswalk, incl. ad-hoc flags) lives in separate tables, curated via the KB's `kb-aa-links` confirm flow.
- **`aa.cerf_allocation_storm (application_code, sid, updated_at)`** — one row per matched storm (multi-storm friendly, e.g. Haiti 2008 = Fay/Gustav/Hanna/Ike). Joins to `aa.cerf_allocation` on `application_code` and `storms.ibtracs_storms` on `sid`.
- **`aa.cerf_supplement (application_code, not_tc, not_drought, valid_month_start, valid_year_start, valid_month_end, valid_year_end, confidence, notes, updated_at)`** — per-allocation annotations. `not_tc=true` marks a storm allocation that is definitely not a tropical cyclone (tornado, winter storm, inland flooding outside any TC basin) — it will never be in IBTrACS. `not_drought=true` is its drought analogue: a "Drought"-typed allocation with no meteorological drought behind it (the 2008 food-price-crisis allocations, conflict/displacement responses) — auto-applied only at confidence ≥ 0.9 (vs 0.8 for periods), and a real period supersedes it. `valid_*` capture the drought valid period (start/end month+year — the rainfall-deficit months, which can span a year boundary and usually precede the allocation; for anticipatory allocations it's the forecast failed season). `confidence` is the Claude matcher's stated confidence for auto-applied picks (NULL = human-set); `notes` carries the reasoning (which season(s) failed, or the real driver).
- **GitHub Pages site** `https://ocha-dap.github.io/ds-cerf-supplement/` — Storms tab (matched / not-a-TC / needs-storm) + Droughts tab (dated with confidence % / needs-period); `site/data.json` is regenerated each deploy, not committed.
- **GitHub issues** (labels `cerf-sid`, `cerf-drought`) — one per allocation needing human input; `review`-labelled issues double-check existing matches.

```sql
-- allocation × storm × track
SELECT a.country_name, a.year, i.name, i.season
FROM aa.cerf_allocation_storm s
JOIN aa.cerf_allocation   a USING (application_code)
JOIN storms.ibtracs_storms i USING (sid);
```

Upstream OneGMS feed: [`cerf-onegms`](../infrastructure/datasets/cerf-onegms.md) (`aa.cerf_allocation`). Live table snapshots: `infrastructure/db-schema-dev.md`.

## Human-in-the-loop (issues)

- Anything the automation can't resolve gets an issue (assigned + @-mentioning the maintainer): `cerf-sid` with candidate IBTrACS storms and research links; `cerf-drought` with the allocation narrative excerpt and Claude's sub-threshold suggestion + reasoning.
- **Reply on the issue** in plain language — "it's Beryl", "not a TC", "suggestion is correct", "Oct 2020 – Mar 2021", "not a drought". The next matcher run treats your comment as authoritative, applies it, and closes the issue.
- `review`-labelled issues (`scripts/raise_review_issues.py`) flag existing matches for a double-check; the checker never auto-closes them — they wait for your reply.

## Storage & code internals

`src/storage.py` reads/writes the two `aa` tables but keeps the legacy DataFrame API
(`load_supplemental`/`save_supplemental`/`upsert_annotation`/`remove_annotation`;
`sids` column is a JSON list string) so all callers are unchanged. `save_supplemental`
does a transactional full-replace of both tables (small, single-writer). Writers use
`get_engine(write=True)`; readers the read engine. History: the store was a blob
parquet (`global/dev/cerf/cerf_supplemental_data.parquet`) until 2026-07 — migrated to
the DB by `scripts/migrate_blob_to_db.py`; the blob is retired.

## Failure modes & debugging

| Symptom | Likely cause | Check |
|---|---|---|
| Storm not matchable / issue stays open | storm not yet in `storms.ibtracs_storms` | check `storms-pipeline` freshness (`infrastructure/pipeline-registry.md`); recent-season storms lag |
| `match_storms` fails in `run_claude` | bad/absent model, `CLAUDE_CODE_OAUTH_TOKEN` missing from the `dsci` scope, or the CLI installer unreachable from the cluster | model input must be a *current* id (currently `claude-sonnet-5`; Claude API ids drift, check the models overview); token secret set on the repo |
| `run_claude` reports "timed out after N minutes" | research backlog too big for the budget | `--timeout-minutes` on the `run_claude` entry in `databricks.yml` (droughts 45, storms 20); prepare should be excluding open-issue/no-reply backlog |
| Writer step fails to save | job not on the Job Compute policy (no `DSCI_AZ_DB_DEV_*_WRITE` injected) | `policy_id` in `databricks.yml`; a `relation does not exist` across many jobs = wrong host secret, see [database.md](../infrastructure/database.md) |
| `deploy-site` install fails on `ocha-stratus` path | `[tool.uv.sources]` local path not in CI | install with `uv pip install --no-sources -e .` (pulls from PyPI) |
| `deploy-site` fails in `fetch_site_data` | `publish_site` hasn't uploaded yet / org `DSCI_AZ_BLOB_DEV_SAS` not visible | check the Databricks run; the workflow's 08:00 UTC backstop re-deploys whatever is on the blob |
| Site not updating | deploy cancelled by concurrency, or CDN cache | check `deploy-site` runs (concurrency group `pages`); cache-bust `data.json?x=…` |
| Duplicate CERF codes / scrambled matches | keying on `ApplicationID` (not unique) | always key on `ApplicationCode` |
