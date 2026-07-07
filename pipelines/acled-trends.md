---
content_type: pipeline
name: acled-trends
type: dataset-ingest
status: live
deployment:
  platform: github-actions
  jobs:
    - { name: "Weekly ACLED Trends scrape & publish", ref: ".github/workflows/main.yml", schedule: "0 10 * * *", status: live }
inputs: ["ACLED Trends (\"trendfinder\") public JSON API — https://trendfinder-api.acledapps.com/api/v1/overview, no auth required"]
outputs:
  - "blob dev: ds-acled-trends/processed/acled/trends_organized_violence_<period_end>.csv (one per measured period)"
  - "blob dev: ds-acled-trends/processed/acled/trends_organized_violence_latest.csv"
  - "blob dev: ds-acled-trends/processed/acled/trends_organized_violence_all.csv (cumulative, rebuilt from all per-date files each run)"
  - "GitHub Pages: password-protected download site at https://ocha-dap.github.io/ds-acled-trends/ (docs/), CSVs client-side-encrypted at build time"
dependencies: ["ocha-stratus", "cryptography", "pandas", "requests", "GitHub Pages (actions/deploy-pages)", "secret: DSCI_AZ_BLOB_DEV_SAS_WRITE", "secret: SITE_PASSWORD"]
downstream: []   # no KB page currently reads these blobs/CSVs; distribution today is the password-gated GH Pages site only
depends_on: []   # reads directly from ACLED's public Trends API (third party, no KB dataset page yet); no upstream KB pipeline
source_repo: ocha-dap/ds-acled-trends
source_branch: main
source_sha: ce37c72
code_ref:
  - "pipelines/run_scrape.py"
  - "pipelines/build_site.py"
  - "src/scraper.py"
  - "src/constants.py"
  - ".github/workflows/main.yml"
extra: {}
visibility: internal
last_synced: "2026-07-07"
---

# ds-acled-trends

> Runbook. Optimize for "what feeds it, what it emits, and what to do when it breaks at 2am."

## One-liner
*daily: scrape the ACLED Trends ("trendfinder") public API for the latest measured 4-week organized-violence period → tidy per-country CSV → blob (dated + latest + self-healing cumulative "all") → rebuild a password-protected GitHub Pages download site.*

## Jobs & schedule

| job | ref | schedule | status |
|---|---|---|---|
| Weekly ACLED Trends scrape & publish (single job despite the workflow's name — it's actually daily) | `.github/workflows/main.yml` | `0 10 * * *` (daily 10:00 UTC) + `workflow_dispatch` | live |

Not present in `infrastructure/pipeline-registry.md` at time of ingestion — only the separate `ds-acled-fetcher` GHA is tracked there (registry shows that one `🔴 DOWN`/`OVERDUE(>48h)` as of the last snapshot). This job should be added to the registry. Also not listed in the GitHub Pages & Netlify table in `infrastructure/deployments.md`, and `ds-acled-trends` doesn't appear in `infrastructure/spoke-repos.md` — none of the three generated registries currently know about this repo.

## Inputs
- **ACLED Trends overview API** — `GET https://trendfinder-api.acledapps.com/api/v1/overview?outcome=organized_violence&lead=0&lag=12`, public, no login/API key (only a `Referer: https://apps.acleddata.com/` header). This is a *different* ACLED surface than the authenticated Access/Export API used by `ds-acled-fetcher`/`ds-acled-conflict-index` — no code or data dependency between the three repos.
- `lead=0` selects the most recent **completed** ("measured") 4-week period; `lag=12` sets the comparison baseline to the prior-year average (the app's default).
- On rebuild of the `all` table: every existing per-date CSV already in blob (`ds-acled-trends/processed/acled/trends_organized_violence_*.csv`), read back via `ocha-stratus`.

## Steps
1. `pipelines/run_scrape.py` → `src/scraper.get_trends_table()`: fetch the overview JSON (`fetch_overview`), parse `displayData.countries` into one row per country for the measured period (`parse_measured_table`) — country, region, lat/lng, `event_count`, `change_pct`/`change_abs` vs. comparison, period/comparison date bounds, `latest_update`.
2. Upload this run's table twice: as the dated file (`trends_organized_violence_<period_end>.csv`) and overwriting `trends_organized_violence_latest.csv`.
3. `build_all_table()`: list every dated blob under the prefix, download and concatenate them, de-dup on `["outcome","period_start","period_end","country_id"]` (keep last), sort by `period_end`/`event_count`, re-upload as `trends_organized_violence_all.csv`. Rebuilt from scratch every run — blob is canonical, so the `all` file self-heals from whatever dated files exist.
4. `pipelines/build_site.py` (same workflow, next step): pull `all`/`latest`/every dated CSV back from blob, AES-256-GCM-encrypt each with a key derived from `SITE_PASSWORD` (PBKDF2-SHA256, fixed salt, 200k iterations), write ciphertext + a static `docs/index.html` that decrypts in-browser on password entry. Raw CSVs are never served; `docs/` is gitignored and only exists as the CI build artifact deployed to Pages.
5. GH Actions `actions/deploy-pages` publishes `docs/` to GitHub Pages.

## Outputs
- Blob (dev container, "projects"): `ds-acled-trends/processed/acled/trends_organized_violence_<period_end>.csv`, `..._latest.csv`, `..._all.csv` — columns `country`, `country_id` (UN M49), `region`, `lat`/`lng`, `event_count`, `change_pct`, `change_abs`, `outcome`, `period_start`/`period_end`, `comparison`, `comparison_start`/`comparison_end`, `latest_update` (see repo README for the full column table).
- GitHub Pages site (this repo, `docs/`) — password-gated download UI over the same CSVs, ciphertext-only (`*.csv.enc`); live at https://ocha-dap.github.io/ds-acled-trends/ (verified 200, title "ACLED Trends — Data Downloads"). Not yet recorded in `infrastructure/deployments.md`'s GitHub Pages & Netlify table — should be added there.
- No DB writes; no email/Listmonk.

## Dependencies
- **`ocha-stratus`** — blob read/write (dev stage only; a single write-SAS token doubles for read+list since a separate read token isn't provisioned in CI — see `_write_container_client()` in `src/scraper.py`).
- `cryptography` (PBKDF2HMAC, AESGCM), `pandas`, `requests`.
- Secrets: `DSCI_AZ_BLOB_DEV_SAS_WRITE` (blob), `SITE_PASSWORD` (site encryption key — rotating it requires re-running the workflow to re-encrypt everything).
- GitHub Pages (`actions/configure-pages`, `actions/upload-pages-artifact`, `actions/deploy-pages`), `astral-sh/setup-uv`.

## Failure modes & debugging
- **Dev-blob only.** Everything (per-date/latest/all CSVs, the site's source data) lives in the `dev` stratus stage — there is no `prod` slot for this pipeline. If another pipeline/app ever expects a prod copy, it won't exist.
- **`all` table depends on every dated blob being present and correctly named** — `_DATED_RE` in `src/scraper.py` matches `trends_organized_violence_<YYYY-MM-DD>.csv`; a renamed/moved blob silently drops out of the cumulative rebuild (no error, just missing rows).
- **API shape drift.** The scraper hard-parses ACLED's undocumented `trendfinder` JSON (`filters.filterTimeRanges`, `filters.filterComparisonTimeRanges`, `metadata`, `displayData.countries`); `parse_measured_table` raises `RuntimeError` if no `type: "measured"` range is found — the most likely break if ACLED changes the frontend API.
- **`SITE_PASSWORD` rotation** requires a full re-run (`workflow_dispatch`) to re-encrypt every file — old ciphertext in `docs/data/` won't decrypt with a new password until that happens.
- **`build_site.py` hard-fails without `SITE_PASSWORD`** (`SystemExit`) and also if blob has no CSVs yet (`SystemExit: No CSVs found`) — the latter would only happen on a from-scratch blob container.
- **Not in `pipeline-registry.md` / `deployments.md` / `spoke-repos.md`** — its live/failing state isn't currently surfaced by the health registry the way `ds-acled-fetcher`'s is; this pipeline's health has to be checked manually via `gh run list -R ocha-dap/ds-acled-trends`.
- Logs: GitHub Actions run logs for the `scrape-and-publish` job (`Scrape ACLED Trends → blob` and `Build encrypted download site` steps).

## Downstream consumers
None found in this KB yet — no framework/pipeline/app page references `ds-acled-trends` blobs or the `trends_organized_violence_*` CSVs. The only current distribution channel is the password-protected GitHub Pages site (password shared out-of-band); update this section if a consumer starts reading the blob directly.
