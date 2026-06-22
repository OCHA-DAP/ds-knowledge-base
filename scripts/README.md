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
  `./index.html` (repo root): a Leaflet **status map** (Active / recently
  triggered / expired / in development / retired, with a **red dot per
  activation**), an *Active frameworks* table, and a *full version history*
  table. Each row: country (full name), hazard, **AOI** (admin areas), status,
  **activations**, trigger windows, pre-arranged funding, target people, the
  published framework doc, and a link to the **source repo**.
  Multi-country frameworks (e.g. lac-dry-corridor) are **split to one row /
  marker per country**, with per-country AOI, funding, and activations.
- **Two invariants that hide real activations if broken** (see
  `docs/INGESTION.md` → activations):
  - **"Current version" prefers the endorsed-lineage version**, NOT the latest
    version string. A newer-dated `status: development` successor page has
    `activations: []`; if it became "current" it would hide the endorsed
    version's activation + status. The script falls back to a dev version only
    when a framework has no endorsed version. After adding any in-development
    successor page, regenerate and confirm the endorsed version still drives the
    map (check the `MARKERS` JSON status per framework).
  - **Per-country activation attribution is by name match** in the note — every
    activating country of a multi-country framework must be named (ISO3 + full
    name) in the activation `note`, or it won't show as recently triggered.
- **Status labels:** stored `status: endorsed` is shown publicly as **"Active"**
  (`STATUS_LABEL`); a partial window trigger (`full_activation: false`) is
  captured but does **not** flip status (stays Active). Activation dates in the
  popover link to the announcement when one exists.
  **Public-safe by construction** — emits only fields already in the published
  PDF / public CERF-AHF announcements, strips internal asides (discrepancy notes,
  repo-impl values), and NEVER emits discrepancies, dev-slot notes, or
  `visibility`. A **private** source repo (per `spoke-repos.md`) shows as
  "🔒 private", name withheld, not linked. **GitHub Pages serves it from the main
  branch root** (`./index.html`, with `./.nojekyll` so files are served as-is) —
  just re-run after a framework batch and commit `index.html` to main.

## DB snapshot (scheduled)

- `gen_db_schema.py` — read-only introspection of the Postgres schema via
  `ocha-stratus` → `infrastructure/db-schema.md` (schemas → tables → columns +
  PK, with row-count estimate + size) and `infrastructure/.db-tables.json` (the
  table list `gen_dependency_graph.py` uses to wire DB tables into the graph).
  Daily via `.github/workflows/db-schema.yml`; needs the DSCI_AZ_DB_PROD_* env /
  secrets, `PGSSLMODE=require`, Python 3.10+, and DB network access. Run order:
  `gen_db_schema.py` then `gen_dependency_graph.py`.
