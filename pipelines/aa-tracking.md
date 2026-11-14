---
content_type: pipeline
name: aa-tracking
type: schema-owner
status: live
deployment:
  platform: databricks
  resource_group: null
  # The dev DB sits behind a private endpoint (2026-09), so nothing on GitHub or a laptop touches it.
  # One Databricks job applies the pending entries files, then snapshots
  # the whole aa schema to the dev blob; the GitHub publish workflow restores that snapshot into a
  # throwaway Postgres and builds the site from it. Interactive edits go through the entry / admin
  # pages, whose proxy (an Azure web app, proxy/) writes the DB. Since the KB flip (2026-09-28) the
  # tracking DB is authoritative; since 2026-10-05 (KB D115) it also owns the backtest tables and
  # the KB-era activation/funding record the KB's loaders used to write.
  jobs:
    - { name: "AA Tracking Nightly (aa snapshot)", ref: "databricks.yml (task nightly → databricks/nightly.py: apply_entries.py → export_snapshot.py; parquet + DDL to projects/ds-aa-tracking/snapshot, latest/ + dated copies)", schedule: "daily 03:30 UTC", status: live }
    - { name: "Publish site", ref: ".github/workflows/publish.yml", schedule: "daily 04:17 UTC + push to main + workflow_dispatch + repository_dispatch data-updated; restores the blob snapshot, no DB", status: live }
inputs:
  - "Entries files: JSON on the private dev blob (projects/ds-aa-tracking/entries/, never in the public repo), applied once each by the nightly job (scripts/apply_entries.py — upsert, op: delete, op: replace of a version's rows); every row audited (entry_audit)"
  - "Entry / admin pages (entry.html, admin.html) → the proxy (proxy/server.js) → direct writes to dev schema aa, every field change audited"
  - "DB tables (read for activation linking, dev): aa.cerf_allocation, aa.cbpf_allocation, aa.cbpf_fund + aa.v_allocation (ds-cerf-supplement mirrors)"
outputs:
  - "DB (dev schema aa): sole writer of every table and view outside the OneGMS/CBPF mirrors — DDL + views in src/ds_aa_tracking/schema.py, additive migrations only (never a full refresh). Core: aa.country_hazard (framework identity + pipeline, retired flag), framework_version (THE version registry incl. historical versions, doc_url/endorsed_by), window_activation + adhoc_activation + activation_funding (one activation, N fund allocations), window_funding, people_covered, framework_status/focal_point/calendar, report_channel_inclusion, plan_inclusion, cirv, start_network, cerf_subgrant, cerf_application_people/report, cerf_allocation_extra, cerf_project_supplement, cerf_cva_history, emergency_type_override, version_page, learning_document, framework_partner, entry_audit, applied_entries"
  - "Backtests (dev schema aa, moved from the KB 2026-10-05): aa.window, aa.simulated_activation, aa.version_performance_reported + views aa.v_window_performance, aa.v_framework_performance and the compatibility view aa.framework_version_map; edited freely and corrected as errors are found (aa.v_trk_backtest_check lists the rows that break a rule); sealing a checked backtest is a planned follow-up (ds-aa-tracking #7)"
  - "KB-era record, frozen (dev schema aa, moved 2026-10-05, no writer): aa.funding_breakdown, aa.actual_activation, aa.activation_allocation + views aa.v_funding_by_sector / _by_agency / _by_window, aa.v_aa_allocation, aa.v_activation_funding — superseded by window_funding, window_activation, activation_funding"
  - "Blob snapshot (dev blob projects/ds-aa-tracking/snapshot/{latest,YYYY-MM-DD}/): every aa table as parquet + schema.json (exact DDL) + manifest.json; dated copies kept 30 days, 31-December copies forever"
  - "Review site (staticrypt-encrypted GH Pages): https://ocha-dap.github.io/ds-aa-tracking/ — landing map, per-framework pages, dashboards, full table contents, crow's-foot ERDs, reconciliation queues, the admin page, target-schema roadmap; built from the blob snapshot"
  - "Donor shares page (dash-donors.html, scripts/donors.py, 2026-09-25): each donor's share of a pooled fund's income per fiscal year (aa.v_contribution, the ds-cerf-supplement contribution mirrors; cash basis) × the AA that fund released / pre-arranged that year (the Funding page's own series via dashboards.funding_series), plus hand-entered build earmarks (aa.build_contribution, dev); AA on fund-years with no contribution rows is reported as unattributable — replaces the hand-built 'Donor shares of OCHA AA' workbook"
dependencies:
  - "ocha-stratus (DB engine + blob; PGSSLMODE=require set automatically)"
  - "DSCI_AZ_DB_DEV_* (+ _WRITE) creds — injected on Databricks by the Job Compute policy"
  - "GitHub Actions: the org blob secret + repo secrets EXTRACT_TOKEN (the proxy site token) and SITE_PASSWORD (staticrypt)"
  - "graphviz (`brew install graphviz`) for the site ERDs; staticrypt (npx) for publishing"
downstream:
  - "aa.framework_version is THE unified version registry; aa.framework_version_map is a compatibility view over aa.version_performance_reported, read with the performance views by the CERF trigger-allocations app"
  - "The KB reads this DB (registry, versions, statuses, funding) to find each framework's code, monitoring and documents; the KB's framework pages are frozen copies, no longer a source (D115)"
depends_on:
  - "cerf-supplement"     # allocation mirrors (CERF + CBPF) + v_allocation, read for activation linking
discrepancies:
  - "[pending] adjudication queues on the review site (per-person pages): activation amounts vs KB, people-covered conflicts across sheets, 17 sheet/sweep activations missing in KB, 19 KB-only activations, 22 historical versions missing KB pages, bgd-flooding 2020-06-26 framework_doc pointing at the 2021 doc"
  - "[pending] curation seeds: framework_version.endorsed_by (erc | cerf_secretariat) + valid_until_source; window trigger_statement/basis; activation windows currently 'unspecified' where the KB record lacks window_name"
  - "[pending] backtest curation: aa.v_trk_backtest_check is the queue (simulated years outside the analysed span, backtests under labels that are no registered version, endorsed versions with no backtest). The 2026-10-05 check against the endorsed documents produced the first corrections as an entries file (not yet applied); sealing checked backtests is deferred (user, 2026-10-26; ds-aa-tracking #7)"
  - "[resolved 2026-09] no ingest any more: the DB is the single source of truth (scripts/ingest.py is the retired migration-era loader and refuses to run); data is entered through the site or entries files, applied and snapshotted nightly by the Databricks job and published from the snapshot"
  - "[resolved 2026-10-05] the backtest tables and the KB-era activation/funding record moved here from the KB (KB D115). Ownership half in ds-aa-tracking #42 (2026-10-26, merges before this page's claims hold); the sealing half stays in #7"
surfaces:
  - {url: "https://ocha-dap.github.io/ds-aa-tracking/", kind: dashboard, title: "AA portfolio map (open, no password; llms.txt data files beside it; full site under dev/, password)"}
source_repo: ocha-dap/ds-aa-tracking
source_branch: aa-tables-owned   # PR #42; set to main once it merges
source_sha: bfb36d66
code_ref:
  - "src/ds_aa_tracking/schema.py — DDL + views for every owned aa table, incl. the backtest tables and the frozen KB-era tables (no guards yet: sealing is #7)"
  - "src/ds_aa_tracking/normalize.py — canonical country/hazard/status/fund vocabularies (framework identity = (country_iso3, hazard), KB D62)"
  - "src/ds_aa_tracking/snapshot.py — snapshot export + verbatim restore (both halves)"
  - "databricks.yml + databricks/nightly.py — the AA Tracking Nightly job (optional --ensure-schema / --relabel, then entries, snapshot)"
  - "scripts/apply_entries.py — entries files from the private blob (upsert / op: delete / op: replace), audited"
  - "scripts/export_snapshot.py / scripts/restore_snapshot.py — blob snapshot ↔ local Postgres"
  - "scripts/build_site.py + scripts/dashboards.py + scripts/admin_page.py — the encrypted review site, dashboards and the admin CRUD page"
  - "proxy/server.js — the one server: PDF extraction, framework entry, admin-page /schema /rows /save /delete; every change audited to aa.entry_audit"
  - "DESIGN.md — the agreed target schema + phased migration (unified version registry, window-first, multi-fund) and 'AA tables owned here (2026-10-05)' (sealing deferred)"
extra:
  db_schema: aa
  identity: "(country_iso3, hazard) = framework; (+ version) = the approved unit (a version IS an endorsed document; endorsed by ERC = major/new validity, or CERF secretariat = minor/inherited validity)"
  conflicts_policy: "sources loaded side by side (source in the key); reconciliation in views, never silent merges; colleagues' sheets win over KB on historical activations"
  backtest_policy: "edited freely (entries file op: replace / op: delete, admin page) and corrected as errors are found; sealing a checked backtest (trigger-enforced, changed only by a reviewed erratum) is a planned follow-up — ds-aa-tracking #7"
visibility: internal
last_synced: "2026-10-26"
---

# AA tracking (portfolio schema)

> The single authoritative tracking system for OCHA's AA portfolio — superseding the
> team-member spreadsheets it was seeded from, the KB's framework pages (the KB flip,
> 2026-09-28) and, since 2026-10-05, the KB's own trigger-performance loaders (D115).

## One-liner

Owns every dev-DB `aa`-schema table outside the OneGMS/CBPF mirrors: the framework
**registry** (identity + pipeline countries) and **version registry** (every endorsed
document 2019→, incl. the 2026-08 historical sweep of the OCHA AA page +
`pa-anticipatory-action`), lifecycle status snapshots, pre-arranged funding per window and
fund, people covered, the full **activation record** (framework + ad-hoc + early-action,
one activation × N fund allocations, linked to the OneGMS/CBPF mirrors), external-report
inclusion (A-Hub, UK BCs, SG/CERF/OCHA reports), CERF depth the mirrors don't carry
(subgrants with localization, application demographics, CVA, emergency-type retags, CIRV)
and, since 2026-10-05, each version's **backtest** (trigger windows with their analysed
years, simulated activation years, published headline figures).

Since 2026-11-01 (tracking D169) the site's address opens the **map with no password**,
with its Definitions page and accessibility statement; every other page (per-framework
pages, dashboards, tables, crow's-foot ERDs, reconciliation queues, per-person review
pages for the sheet owners, the target-schema roadmap) is on the development site under
`dev/`, behind the password. **Since 2026-09-24 it is
also the team's only AA portfolio site**: the KB's own `/anticipatory-action/` status map,
trigger-statistics page and per-framework pages were retired (D110) and their URLs
redirect here; the KB keeps only the cross-organisation page. Conflicts between sources are **kept, keyed by source, and
surfaced** — never silently merged.

## Answering portfolio questions

Use two sources, in this order.

**1. Headline figures: the tracker's open files, not SQL.** Beside the open map the build
writes plain files for programs and AI assistants, no password (tracking D181):
[`llms.txt`](https://ocha-dap.github.io/ds-aa-tracking/llms.txt) (what each file holds,
the counting rules, a dictionary of every field),
[`aa-map.md`](https://ocha-dap.github.io/ds-aa-tracking/aa-map.md) (the map's headline
figures as it opens), and `aa-frameworks`, `aa-versions`, `aa-activations`,
`aa-prearranged-funding`, `aa-cofinancing`, `aa-funds` (`.json` and `.csv`, same
directory). Each build checks every figure in them against the map. **Read `llms.txt`
before adding anything up.** The map's figures are computed in the site build
(`scripts/dashboards.py`), not by one view, so totals summed straight from the tables do
not match them. The rules most often broken:

- pre-arranged money is a stock per year: never add years together, never add it to
  money released by activations;
- where a framework allows two activations a year, its CERF envelope is already counted
  twice: never multiply again;
- money and activations belong to a layer (current frameworks, retired frameworks,
  non-framework allocations): add up the layers the question needs and say which;
- a framework is one (country, hazard) pair: there are no regional frameworks;
- co-financing (money from outside CERF and the pooled funds) is separate from
  pre-arranged money: never add the two.

The files carry only what the open pages show (today, the map's data). A people-covered
figure taken from an unpublished framework document is left out of them.

**2. Detail the open files don't carry: the dev `aa` schema.** Read-only through the
internal KB MCP server's `run_sql` (`stage="dev"`) or `ocha-stratus`. Say in the answer that
the tracker is an internal product under development.

| Question | Where |
|---|---|
| Where each framework stands now: lifecycle, current version, status, CERF pre-arranged, people covered | `aa.v_trk_framework_current` (one row per country–hazard pair) |
| Lifecycle (active, updating, development, pipeline, retired) | `aa.v_framework_lifecycle.lifecycle`: count frameworks by this, not by `status` |
| Every version: validity, who endorsed it, document, which version it supersedes | `aa.framework_version`; one row per version with its funding and activation count: `aa.v_trk_version_summary` |
| Status over time | `aa.framework_status` (snapshots by `as_of`, one row per source) |
| Activations, framework and non-framework | `aa.activation` (view over `window_activation` + `adhoc_activation`); money per fund: `aa.activation_funding`; refunds: `aa.activation_refund` |
| Pre-arranged funding per window, year and fund | `aa.prearranged_funding` (view over `window_funding`); by agency and sector: `aa.v_window_funding_split` |
| Backtest return periods | `aa.v_framework_performance` (per version), `aa.v_window_performance` (per window). The map shows the return period the document states where there is one, else the backtest's |
| Focal points, calendar, partners | `aa.framework_focal_point`, `aa.framework_calendar`, `aa.framework_partner` |
| CERF sub-grants to partners | `aa.cerf_subgrant` |

Don't use the frozen KB-era tables for current figures: `funding_breakdown`,
`actual_activation`, `activation_allocation` and the views `v_funding_by_*`,
`v_aa_allocation`, `v_activation_funding` stopped on 2026-10-05.

## Relationship to the rest of the `aa` schema

Strict single-writer-per-table, two writers:

- **ds-aa-tracking** (this page) — everything AA-interpretive, including what the KB used
  to load: the backtests (`window`, `simulated_activation`, `version_performance_reported`
  and their performance views) and the frozen KB-era record (`funding_breakdown`,
  `actual_activation`, `activation_allocation`, superseded by `window_funding`,
  `window_activation`, `activation_funding`). The KB writes nothing in `aa` any more (D115).
- **ds-cerf-supplement** (cerf_allocation/_project*, cbpf_allocation/_fund/_project*,
  cerf_supplement, cerf_allocation_storm, v_allocation) — the OneGMS mirrors.

**Backtests** are edited freely (an entries file with `op: replace`, or the admin page) and
corrected as errors are found; `aa.v_trk_backtest_check` lists the rows that break a rule.
Sealing a backtest once it is checked against the endorsed document — a database trigger
refusing every change except a reviewed erratum — is a planned follow-up (ds-aa-tracking #7,
user decision 2026-10-26).

The **unification plan** (repo `DESIGN.md`, mirrored on the site's Roadmap page):
`aa.framework_version` is THE version registry; `framework_version_map` survives as a
compatibility view over `version_performance_reported`; windows are universal (≥1 per
version, funding/coverage/activations attach to windows).

## Running

Laptops can't reach the dev DB (since 2026-09-30). Data goes in through the site's
entry/admin pages or an entries file. The nightly job applies them and snapshots the schema:

```sh
databricks bundle deploy -t prod -p DEFAULT
databricks bundle run aa_tracking_nightly -t prod -p DEFAULT        # entries → snapshot
uv run python scripts/apply_entries.py --upload FILE                # put an entries file on the blob
uv run python scripts/restore_snapshot.py && uv run python scripts/build_site.py   # local build from the snapshot (needs a local Postgres — repo README)
```

The site publishes from the blob snapshot via `.github/workflows/publish.yml` (staticrypt
to the `gh-pages` branch).
