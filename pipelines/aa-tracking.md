---
content_type: pipeline
name: aa-tracking
type: schema-owner
status: live
deployment:
  platform: manual        # ingest is run by hand (scheduled GHA planned); the site
  resource_group: null    # publishes to GitHub Pages on each run
  jobs: []
inputs:
  - "Colleagues' tracking workbooks (Julia: 2026 planning / AA reporting / activations 2020-2026; Yakubu: CERF AA Jun-2026 / subgrants / displacement-GMS / Mar-2026 allocation analysis) — read from AA_TRACKING_DIR, never committed (public repo)"
  - "KB framework-page frontmatter (frameworks/*/[0-9]*.md — version registry seed incl. superseded/retired, framework_doc, valid_until, prearranged funding)"
  - "reference/historical_framework_versions.csv + historical_activations.csv — curated output of the 2026-08 historical sweep (OCHA AA page Wayback 2021-2026 + ReliefWeb + pa-anticipatory-action monorepo)"
  - "DB tables (read for crosswalking): aa.framework_version_map, aa.actual_activation, aa.activation_allocation (KB-owned); aa.cerf_allocation, aa.cbpf_allocation, aa.cbpf_fund (mirrors)"
outputs:
  - "DB: 22 tables + 7 v_trk_* views in dev schema aa — sole writer of all (full-refresh loads). Core: framework_registry (identity + pipeline), framework_version (THE version registry: 65+ versions incl. historical, doc_url/analysis_ref/endorsed_by), fund (OCHA pooled funds only), activation + activation_funding (one activation, N fund allocations), prearranged_funding, prearranged_sector_budget, people_covered, framework_status/focal_point/calendar, report_channel_inclusion, plan_inclusion, cirv, start_network, cerf_subgrant, cerf_application_people/report, cerf_allocation_extra, cerf_project_supplement, cerf_cva_history, emergency_type_override"
  - "Review site (staticrypt-encrypted GH Pages): https://ocha-dap.github.io/ds-aa-tracking/ — full table contents, crow's-foot ERDs, reconciliation queues (sheets vs KB vs mirrors), per-person review pages (Julia / Yakubu), target-schema roadmap"
dependencies:
  - "ocha-stratus (DB engine; PGSSLMODE=require)"
  - "DSCI_AZ_DB_DEV_* (+ _WRITE) env creds"
  - "graphviz (`brew install graphviz`) for the site ERDs; staticrypt (npx) for publishing"
downstream:
  - "future: KB loaders read aa.framework_version as the unified version registry (DESIGN.md phases 1-3: framework_version_map shrinks to a trigger_source_crosswalk + compat view)"
depends_on:
  - "cerf-supplement"     # allocation mirrors (CERF + CBPF) + v_allocation, read for activation linking
discrepancies:
  - "[pending] adjudication queues on the review site (per-person pages): activation amounts vs KB, people-covered conflicts across sheets, 17 sheet/sweep activations missing in KB, 19 KB-only activations, 22 historical versions missing KB pages, bgd-flooding 2020-06-26 framework_doc pointing at the 2021 doc"
  - "[pending] curation seeds: framework_version.endorsed_by (erc | cerf_secretariat) + valid_until_source; window trigger_statement/basis; activation windows currently 'unspecified' where the KB record lacks window_name"
  - "[gap] no scheduled ingest yet — tables refresh only when scripts/ingest.py is run manually"
surfaces:
  - {url: "https://ocha-dap.github.io/ds-aa-tracking/", kind: dashboard, title: "AA tracking review site (staticrypt; tables, ERDs, reconciliation queues)", access: password}
source_repo: ocha-dap/ds-aa-tracking
source_branch: main
source_sha: 9f27056
code_ref:
  - "src/ds_aa_tracking/normalize.py — canonical country/hazard/status/fund vocabularies (framework identity = (country_iso3, hazard), KB D62)"
  - "src/ds_aa_tracking/parsers.py — one parser per source workbook (primary sheets only; derived pivots skipped, decisions documented on the site)"
  - "src/ds_aa_tracking/versions.py — framework_version build (KB frontmatter + historical CSV + sheet revisions) and version attribution of facts"
  - "src/ds_aa_tracking/schema.py — DDL + views"
  - "scripts/ingest.py — parse → KB/mirror crosswalk → CBPF match → fund seed → activation split → version attribution → full-refresh load"
  - "scripts/build_site.py — DB → encrypted review site (tables, ERDs, reconciliation, roadmap)"
  - "DESIGN.md — the agreed target schema + phased migration (unified version registry, window-first, multi-fund)"
extra:
  db_schema: aa
  identity: "(country_iso3, hazard) = framework; (+ version) = the approved unit (a version IS an endorsed document; endorsed by ERC = major/new validity, or CERF secretariat = minor/inherited validity)"
  conflicts_policy: "sources loaded side by side (source in the key); reconciliation in views, never silent merges; colleagues' sheets win over KB on historical activations"
visibility: internal
last_synced: "2026-08-25"
---

# AA tracking (portfolio schema)

> The single authoritative tracking system for OCHA's AA portfolio — superseding the
> team-member spreadsheets it was seeded from, and (per its DESIGN.md) eventually
> unifying with the KB-owned trigger-performance tables.

## One-liner

Owns 22 dev-DB `aa`-schema tables covering everything the portfolio-tracking
spreadsheets tracked: the framework **registry** (identity + pipeline countries) and
**version registry** (every endorsed document 2019→, incl. the 2026-08 historical
sweep of the OCHA AA page + `pa-anticipatory-action`), lifecycle status snapshots,
pre-arranged funding per fund, people covered, the full **activation record**
(framework + ad-hoc + early-action, one activation × N fund allocations, crosswalked
to KB `actual_activation` and the OneGMS mirrors), external-report inclusion (A-Hub,
UK BCs, SG/CERF/OCHA reports), and CERF depth the mirrors don't carry (subgrants with
localization, application demographics, CVA, emergency-type retags, CIRV).

Everything is reviewable on the password-protected site (tables, crow's-foot ERDs,
reconciliation queues, per-person review pages for the sheet owners, and the
target-schema roadmap). Conflicts between sources are **kept, keyed by source, and
surfaced** — never silently merged.

## Relationship to the rest of the `aa` schema

Third writer in the schema, strict single-writer-per-table beside:

- **ds-knowledge-base** (framework_version_map, window, simulated_activation,
  funding_breakdown, actual_activation, activation_allocation) — trigger performance;
- **ds-cerf-supplement** (cerf_allocation/_project*, cbpf_allocation/_fund/_project*,
  cerf_supplement, cerf_allocation_storm, v_allocation) — the OneGMS mirrors.

The **unification plan** (repo `DESIGN.md`, mirrored on the site's Roadmap page):
`aa.framework_version` becomes THE version registry; `framework_version_map` shrinks
to a KB-owned `trigger_source_crosswalk` behind a compatibility view; windows become
universal (≥1 per version, funding/coverage/activations attach to windows); the KB's
`actual_activation` eventually merges into `aa.activation`. Phases 0 (this repo's
restructure) and 4 (CBPF mirror) are done; 1–3 and 5–6 are KB-side and pending.

## Running

```sh
uv run python scripts/ingest.py       # parse sheets → crosswalk → load dev DB
uv run python scripts/build_site.py   # regenerate the review site (needs graphviz)
```

Raw workbooks live outside the repo (`AA_TRACKING_DIR`); the site publishes via
staticrypt to the `gh-pages` branch.
