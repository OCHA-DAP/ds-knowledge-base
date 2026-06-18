# scripts/

Generators and checks. The three generators are **idempotent** and rebuild
indexes from page frontmatter — run them after every ingest batch (the
"post-batch routine"); never hand-edit their output.

## Post-batch routine (run all three from repo root)

```bash
python scripts/gen_catalog.py            # → catalog.md (all framework-versions, filterable)
python scripts/gen_framework_readmes.py  # → frameworks/<id>/README.md (per-framework index + lineage)
python scripts/gen_issue_form.py         # → .github/ISSUE_TEMPLATE/kb-feedback.yml (Specific-item dropdown)
python scripts/gen_dependency_graph.py   # → infrastructure/dependency-graph.md (depends_on edges → blast radius + Mermaid)
```

Each also doubles as a light validator: `gen_catalog.py` parses every page's
YAML (a frontmatter break fails loudly).

## Checks (run by GitHub Actions, also runnable locally)

- `check_drift.py` — compares each page's `source_sha`/`code_ref` against the
  spoke's branch HEAD; flags pages whose source code moved. Daily action →
  `kb-drift` issue.
- `check_pdf_freshness.py` — flags endorsed framework pages whose published PDF
  is aging / may have a newer version. Weekly action → `kb-pdf-freshness` issue.

Needs `pyyaml`; the checks need `gh` (authenticated).

## Visibility snapshot (run locally)

- `gen_spoke_repos.py` — audits every page's `source_repo` GitHub visibility →
  `infrastructure/spoke-repos.md`, **marking the private/internal spokes**. These
  are the spokes the drift bot can't read with the default CI token (it reports
  them `NO-ACCESS`). Run **locally** with a `gh` PAT that has org `repo:read` —
  in CI the default token resolves private repos as `unknown`. Not wired into a
  scheduled action yet (pending the private-repo handling decision).

## Public site (published to GitHub Pages)

- `gen_public_site.py` — renders the **public-facing** frameworks page →
  `public-site/index.html`: a Leaflet **status map** (active / development /
  retired, with ⚡ activations flagged), an *Active frameworks* table, and a
  *full version history* table. Each row: country (full name), hazard, **AOI**
  (admin areas), status, **activations**, trigger windows, pre-arranged funding,
  target people, the published framework doc, and a link to the **source repo**.
  Multi-country frameworks (e.g. lac-dry-corridor) are **split to one row /
  marker per country**, with per-country AOI, funding, and activations.
  **Public-safe by construction** — emits only fields already in the published
  PDF / public CERF-AHF announcements, strips internal asides (discrepancy notes,
  repo-impl values), and NEVER emits discrepancies, dev-slot notes, or
  `visibility`. A **private** source repo (per `spoke-repos.md`) shows as
  "🔒 private", name withheld, not linked. Published from the `gh-pages` branch,
  which holds only the rendered `index.html` (+ `.nojekyll`), never the internal
  markdown. Re-run after a framework batch, then refresh `gh-pages`.

## DB snapshot (scheduled)

- `gen_db_schema.py` — read-only introspection of the Postgres schema via
  `ocha-stratus` → `infrastructure/db-schema.md` (schemas → tables → columns +
  PK, with row-count estimate + size) and `infrastructure/.db-tables.json` (the
  table list `gen_dependency_graph.py` uses to wire DB tables into the graph).
  Daily via `.github/workflows/db-schema.yml`; needs the DSCI_AZ_DB_PROD_* env /
  secrets, `PGSSLMODE=require`, Python 3.10+, and DB network access. Run order:
  `gen_db_schema.py` then `gen_dependency_graph.py`.
