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
- `gen_drive_extracts.py` — **Phase 7c content extraction**, also **headless** (the
  Drive API exports Google Docs/Slides text and downloads Office/PDF — the interactive
  connector is *not* needed for content either; refines D45). Reads the manifest, pulls
  **text** from content-bearing files under a subtree → `<private-repo>/drive/extracts/`
  with a provenance header, mirroring the folder tree. **Internal**, same as the manifest.
  Idempotent/resumable via `drive/.extract-index.jsonl` — JSON-Lines so a local run and
  the daily CI sync merge via git's `union` driver (private repo `.gitattributes`)
  instead of conflicting; the reader de-dupes. Re-runs only touch new/changed
  files; per-file failures are logged, not fatal; scanned PDFs (no text layer) are
  recorded empty so they aren't retried. Needs `python-docx python-pptx` in the venv +
  `pdftotext` on PATH.
  ```bash
  # narrative pass (Docs/Slides/Word/PPT/text) over a subtree — fast, light:
  GOOGLE_APPLICATION_CREDENTIALS= ~/.config/ds-kb/venv/bin/python scripts/gen_drive_extracts.py \
      --prefix "CERF Anticipatory Action"
  # heavy PDF pass (downloads; skips files > --max-pdf-mb; scanned PDFs yield no text):
  … scripts/gen_drive_extracts.py --types pdf --max-pdf-mb 40
  ```
  Then commit the new extracts in the private repo (or use `drive_refresh.sh`'s repo).
- `gen_slide_captions.py` — **slide-visual captions (Phase 7c+)**: text extraction misses
  the info in *plots/charts/maps/tables*, which for many decks is the key content. This
  renders each slide (Google Slides → Drive-export PDF; `.pptx` → LibreOffice → PDF; then
  `pdftoppm` → PNG) and runs **headless Claude Code** (`claude -p`) to write a
  `*.captions.txt` sidecar describing each slide's data → greppable alongside the extract.
  **Bills to the user's subscription/Max plan, NOT the per-token API** (no `ANTHROPIC_API_KEY`;
  CI uses `CLAUDE_CODE_OAUTH_TOKEN` from `claude setup-token`). Idempotent via
  `.caption-index.jsonl` (`merge=union`). `--all` captions every deck, `--sparse-below` only
  text-poor (visual-heavy) ones, `--ids-file` restricts to given decks (daily = only changed),
  `--model sonnet` for cheap breadth. Needs `libreoffice` (for `.pptx`) + `pdftoppm` + the
  `claude` CLI. The captions are a *searchable index* — for depth on a specific plot, re-render
  that one slide and examine it with Opus on demand (the Drive link is in each sidecar header).
- `drive_changes.py` — diffs two manifests (by file id + `modified`) → an added/removed/modified
  summary grouped by folder; feeds the daily sync's commit message + `drive/CHANGES.md`.

### Daily sync (scheduled — runs in the PRIVATE repo)
`ds-knowledge-base-internal/.github/workflows/drive-sync.yml` (daily 06:17 UTC + manual) re-crawls
the drive, re-extracts covered subtrees, captions **new/changed** decks only (Sonnet), writes the
change summary, and auto-commits — so `git log` there is the change feed. Secrets (in the private
repo): `DRIVE_ADC_JSON` (the Drive ADC), `CLAUDE_CODE_OAUTH_TOKEN` (captioning; the caption step is
parked/skipped until it's set). The historical caption **backfill** is a deliberate on-demand
`workflow_dispatch` (input `backfill_prefix`), not the daily auto-run. See DESIGN D47.

### Framework-PDF captions (PUBLIC sibling)
- `gen_framework_captions.py` — same headless-Claude captioning, but for the **published
  framework PDFs** (AOI maps, return-period/trigger charts, indicator tables) → a **public**
  sidecar `raw/frameworks/<fw>/<ver>.captions.txt` (the PDFs are public, so the captions are
  too — *not* the private repo). Reuses `gen_framework_extracts.py`'s fetch; only public-doc
  versions (skips `framework_doc:null` and non-public mmr/vut/yem). Idempotent (skips an
  existing `.captions.txt`; `--force` to redo); usage → `raw/.caption-usage.jsonl`.
  ```bash
  python3 scripts/gen_framework_captions.py --model sonnet            # all public framework versions
  python3 scripts/gen_framework_captions.py --framework tcd-drought   # one framework
  ```
  **Fetch (auto, handles the WAF):** reliefweb/unocha intermittently return an HTTP-202
  bot-challenge to `curl` (it worked in Phase 7a when the WAF was quiet; it's flaky). The
  captioner now falls back to **`browser_fetch.py`** (headless Chromium via Playwright) which
  runs the challenge JS like a real browser and gets the PDF — proven on the exact URLs curl
  402s on. So fetching is automatic: cache/`--pdf-dir` → `curl` → **browser**. A fetched PDF is
  cached at `raw/.pdf-cache/<fw>/<ver>.pdf` (gitignored). `--render-only` tests fetch+render (no
  credits). Needs `playwright` + chromium in the crawl venv (`pip install playwright && playwright
  install chromium`); the captioner shells out to it via `DS_KB_VENV_PY` (default `~/.config/ds-kb/venv`).
- `browser_fetch.py` — standalone headless-browser PDF fetcher (the keystone for *automated*
  framework-PDF ingestion, since `curl` can't pass the WAF). `python browser_fetch.py <url> <out.pdf>`;
  handles direct-PDF URLs and follows a publication page's attachment `.pdf` link. Run with the
  Playwright venv.

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

## Infra drift — Azure + pipeline estate (scheduled)

- `check_infra_drift.py` — the **third drift axis** (code = `check_drift.py`, docs =
  `check_pdf_freshness.py`, **estate** = this). Fingerprints the deployed runtime estate
  and diffs it against a committed baseline (`infrastructure/.infra-baseline.json`),
  flagging **new / removed / rough-reconfigured** resources (runtime, schedule, paused,
  data-mode, compute, plan). A *change notifier*, not a health board.
  - **Two domains, each degrades safely** (SKIPPED when unreadable, never "all removed"):
    **Azure web apps** via `az webapp list -g IMB-CHD-DataScience-EastUS2`, and
    **Databricks + GHA pipelines** read from `.pipeline-registry.json` (run
    `gen_pipeline_registry.py` first so it's fresh; a >36h-stale registry → SKIPPED).
  - `--update-baseline` advances the baseline after diffing, so its **git history is the
    infra changelog** and each run reports only the delta since the last.
  - Auth: `az login` + a fresh registry (so its dbx/gh auth). The CI form
    (`.github/workflows/infra-drift.yml`) is **dormant** until an Azure SP secret
    (`AZURE_CREDENTIALS`) + the registry's Databricks secrets exist.

## Local updaters (scheduled on your machine — for the dormant CI workflows)

- `run_local_updaters.sh` — runs the two **secret-dependent** updaters above
  (`gen_pipeline_registry.py` + `check_infra_drift.py`) from your local checkout using your
  `az` / `databricks` auth, commits + pushes the artifacts, and maintains the
  `kb-infra-drift` issue via `gh` — i.e. does locally what `pipeline-registry.yml` +
  `infra-drift.yml` would do in CI. Preflights auth and bails (without clobbering committed
  artifacts) if `az`/`databricks` aren't live. The other updaters already run in CI and are
  intentionally not duplicated here.
  - **Schedule it** with the launchd agent `com.ocha.ds-kb.updaters.plist` (daily 07:45):
    edit the `REPLACE_ME` paths → `cp` it to `~/Library/LaunchAgents/` →
    `launchctl load`. Logs in `/tmp/kb-updaters.{out,err}.log`. (cron works too, but
    launchd re-fires a run missed while the laptop slept.)
  - **Caveat:** the Databricks OAuth token expires — when a run logs the `databricks auth
    login` hint, re-run it. A service-principal token avoids the expiry (and is what the CI
    workflows will use once their secrets land — at which point this local runner is
    retired).
