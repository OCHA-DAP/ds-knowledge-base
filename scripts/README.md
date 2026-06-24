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

## Drive manifest (internal catalog; internal source)

The manifest is **internal** and lives in the **private companion repo**
`ds-knowledge-base-internal` (D44b/D45/D46) — versioned + access-controlled, so
`git diff` there is its drift record (no blob, no custom drift job). The public repo
holds only a **pointer** at `infrastructure/drive-index.md`. Clone the private repo
**next to** the public one (or set `KB_INTERNAL_DIR`) before crawling.

- `gen_drive_index.py` — crawls the **DS team shared drive** (read-only) →
  `<private-repo>/drive/drive-index.md` + `drive-index.json`: an internal catalog of
  what exists (folder path, title, type, dates, size, link), PII-stripped. Scope rules
  (`docs/PRIVACY.md`): only `0AGYkOFcloQuyUk9PVA`; exclude the bulk-data roots `HDX
  Signals` / `Climate Data` / `Collaborations` and `General - All AA projects / Data`.
  Refuses to write if it can't find the private repo. Modes: bare = rewrite the
  manifest; `--render-only` = re-render md from the json (no API); `--check` =
  re-crawl + diff (writes nothing) — handy for a dry-run, though `git diff` after a
  real refresh is the canonical drift signal.
  - **Auth (the fiddly part — see DESIGN D45):** a read-only **service account** can't
    be added to the shared drive (org locks non-domain members), and gcloud's own
    OAuth client is **blocked by org policy** for Drive scopes. So we use a
    **dedicated internal OAuth client we own** (`ocha-ds-kb` GCP project, Internal
    consent) + the user's Drive ADC:
    ```bash
    gcloud auth application-default login \
      --client-id-file=~/.config/ds-kb/oauth-client.json \
      --scopes=https://www.googleapis.com/auth/drive.readonly,https://www.googleapis.com/auth/cloud-platform
    GOOGLE_APPLICATION_CREDENTIALS= ~/.config/ds-kb/venv/bin/python scripts/gen_drive_index.py
    ```
  - **Do NOT `pip install --user`** the Google libs — they shadow gcloud's bundled
    `protobuf` and break the CLI. Use the isolated venv `~/.config/ds-kb/venv`.
- `drive_refresh.sh` — the one-shot refresh: re-crawl → `git add/commit/push` in the
  private repo (durability + history + drift, all via git). No-op if nothing changed.
  ```bash
  scripts/drive_refresh.sh        # optionally wire to weekly launchd/cron (zero-secret, local ADC)
  ```
  The clean long-term is the dormant SA + domain-wide delegation (super-admin) so a CI
  refresh runs as a non-user identity.

## DB snapshot (scheduled)

- `gen_db_schema.py` — read-only introspection of the Postgres schema via
  `ocha-stratus` → `infrastructure/db-schema.md` (schemas → tables → columns +
  PK, with row-count estimate + size) and `infrastructure/.db-tables.json` (the
  table list `gen_dependency_graph.py` uses to wire DB tables into the graph).
  Daily via `.github/workflows/db-schema.yml`; needs the DSCI_AZ_DB_PROD_* env /
  secrets, `PGSSLMODE=require`, Python 3.10+, and DB network access. Run order:
  `gen_db_schema.py` then `gen_dependency_graph.py`.

## Pipeline registry & health (scheduled)

- `gen_pipeline_registry.py` — the authoritative **prod-pipeline registry + live
  health**, the supersede-target for `pipelines-status`. A pipeline = a **deployed
  scheduled job** keyed by runtime handle (`dbx:<job_id>` / `gha:<repo>/<workflow>`);
  the script reads LIVE state from `databricks jobs list|get|list-runs` **and**
  `gh run list`, then flags each prod entry against its expected cadence →
  `infrastructure/pipeline-registry.md` + `.pipeline-registry.json`.
  - **Conservative by design** (a false DOWN erodes trust): paused → WARN not DOWN;
    seasonal-idle (restricted-month cron) → not overdue; a GHA workflow whose runs
    can't be retrieved → **UNKNOWN**, never DOWN. Only confirmed FAILING / OVERDUE
    (cadence × 2) → DOWN.
  - **Two Databricks gotchas baked in:** `databricks jobs list` returns ABBREVIATED
    settings — you must `databricks jobs get <JOB_ID>` (positional, **not**
    `--job-id`) for `git_source`/`tasks`/data-mode/compute; `jobs list-runs` *does*
    take `--job-id`.
  - **GHA half is seeded** (`GHA_SEED`) since GHA has no org-wide job API — add a row
    as each GHA pipeline is ingested, and pin the workflow path/branch (a wrong path
    reads UNKNOWN). Some monitoring workflows live on non-default branches.
  - Auth: `databricks auth login --profile default` (token expires) + `gh` auth. The
    CI form (`.github/workflows/pipeline-registry.yml`) needs a Databricks **service
    principal / PAT** secret, not the interactive login.
