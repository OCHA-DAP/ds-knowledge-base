---
content_type: infrastructure
last_reviewed: "2026-06-29"   # bump when a human verifies the page is still accurate
---

# Deployments — runtime registry

Where things actually **run**. Generated/refreshable from the platforms; cross-linked to repos. App pages and pipeline pages should link here (and carry their own `deployment` block).

## Azure web apps

Resource group **`IMB-CHD-DataScience-EastUS2`** (OCHA-PROD). ~26 apps (this hand table lags — `az` is the source of truth; **`scripts/check_infra_drift.py`** now diffs the live estate against a committed baseline and flags new/removed/reconfigured apps). App `chd-<x>` generally maps to repo `<x>` (or `<x>` minus/plus `-app`).

| app | state | repo | url |
|---|:--:|---|---|
| CERF-3RM | Running | `ds-cerf-3rm-app` | https://cerf-3rm.azurewebsites.net |
| DataScienceFTP | Running | `ds-cma-datasharing` | https://datascienceftp-dvf6gdfbcggaf7b5.eastus2-01.azurewebsites.net |
| chd-demo | Running | — | https://chd-demo-dxh9adanachxfegp.eastus2-01.azurewebsites.net |
| chd-ds-aa-hti-hurricanes-app | Running | `ds-aa-hti-hurricanes-app` | https://chd-ds-aa-hti-hurricanes-app.azurewebsites.net |
| chd-ds-data-validation | Running | `ds-app-data-validation` | https://chd-ds-data-validation-fhfyfahyb7gaa6a7.eastus2-01.azurewebsites.net |
| chd-ds-demos | Running | `ds-seasonal-bulletin` | https://chd-ds-demos-h7feecemach7cchk.eastus2-01.azurewebsites.net |
| chd-ds-floodexposure-monitoring | Running | `ds-floodexposure-monitoring` | https://chd-ds-floodexposure-monitoring.azurewebsites.net |
| chd-ds-geospatial-impact-viewer | Running | `ds-geospatial-impact-estimates` | https://chd-ds-geospatial-impact-viewer.azurewebsites.net |
| chd-ds-glb-tropicalcyclones-app | Running | `ds-glb-tropicalcyclones-app` | https://chd-ds-glb-tropicalcyclones-app.azurewebsites.net |
| chd-ds-ipc-cerf | Running | — | https://chd-ds-ipc-cerf-bsadf9atbhhdcdcq.eastus2-01.azurewebsites.net |
| chd-ds-rosea-ipc | Running | — | https://chd-ds-rosea-ipc-h4h3bgdvd6ekaqcp.eastus2-01.azurewebsites.net |
| chd-ds-seas5-skill | Running | `ds-seas5-skill` | https://chd-ds-seas5-skill.azurewebsites.net |
| chd-ds-seas5-viz | Running | `ds-seas5-viz` | https://chd-ds-seas5-viz-cycyb5daanfvcrcm.eastus2-01.azurewebsites.net |
| chd-ds-storms-alerts | Running | `ds-storms-alerts` | https://chd-ds-storms-alerts.azurewebsites.net |
| chd-ds-storms-explore | Running | — | https://chd-ds-storms-explore-dzgnb8crc8fsfgee.eastus2-01.azurewebsites.net |
| chd-github-runner | Running | — | https://chd-github-runner-daascrgxgmatgdhr.eastus2-01.azurewebsites.net |
| chd-pa-aa-fji-storms-app | Running | `pa-aa-fji-storms-app` | https://chd-pa-aa-fji-storms-app.azurewebsites.net |
| dev-testaccess | Running | — | https://dev-testaccess-c3cbfhcwa0h4crbb.eastus2-01.azurewebsites.net |
| ds-aa-bgd-cyclone-monitoring | Running | — | https://ds-aa-bgd-cyclone-monitoring-axc8gdejhwfrd6hy.eastus2-01.azurewebsites.net |
| ds-aa-cerf-allocations | Running | — | https://ds-aa-cerf-allocations-ajebgpgwaebte2bw.eastus2-01.azurewebsites.net |
| listmonk-demo | Running | — | https://listmonk-demo-afhcg8e2hde0fxca.eastus2-01.azurewebsites.net |
| nga-flood-trigger-monitor | Running | `ds-aa-nga-flooding` (inferred) | https://nga-flood-trigger-monitor.azurewebsites.net |
| chd-ds-kb-mcp | Running | `ds-knowledge-base` (`mcp_server/`) | https://chd-ds-kb-mcp.azurewebsites.net/mcp |
| chd-ds-kb-mcp-internal | Running | `ds-knowledge-base` (`mcp_server/`) + internal Drive corpus | https://chd-ds-kb-mcp-internal.azurewebsites.net/mcp |
| chd-ds-kb-chat | Running | `ds-kb-chatbot` (separate repo) | https://chd-ds-kb-chat.azurewebsites.net |

The **public KB MCP connector** (`chd-ds-kb-mcp`) is the team's remote MCP server — authless,
KB + code-nav tools over this public repo, no creds. Add it in claude.ai (Team) as a custom
connector. **`chd-ds-kb-mcp-internal`** is the same server with **infra on** (read-only
`run_sql`/`list_blobs`/`read_blob`) + internal Drive extracts, locked by `KB_MCP_AUTH=token`
(401 without the bearer). **`chd-ds-kb-chat`** is the password-gated web chatbot (Max-plan billed
via headless `claude -p`): `/` = public KB; `/private` = KB + Drive + DB + sandboxed `run_python`
via the internal MCP, plus WebSearch/WebFetch. Model is set per tier via
`KB_CHAT_{PUBLIC,PRIVATE}_MODEL` (default `KB_CHAT_MODEL=sonnet`; the private tier runs `opus`
for stronger SQL/analysis reasoning — Max-plan billed, so the cost is quota, not dollars).
Details: [mcp-connectors.md](mcp-connectors.md); chatbot lives in the `ds-kb-chatbot` repo.

_Refresh:_ `az webapp list --resource-group IMB-CHD-DataScience-EastUS2 -o table`
_Drift check:_ `az login && python scripts/check_infra_drift.py --update-baseline` (also covers Databricks/GHA pipelines via the registry; daily via `infra-drift.yml`, dormant until secrets — see below).

## Azure Function Apps & Static Web Apps

Beyond App Service web apps, the same resource group now carries **Function Apps** and
**Static Web Apps (SWAs)** — the emerging pattern for client-side data apps is *SWA (static
build) + the shared [token issuer](token-issuer.md) (ephemeral scoped SAS) + blob (data
bytes)*, replacing always-on Python servers. Note: each SWA is its own Azure resource, so
creating one is an **IT request** (unlike deployments inside the shared `DsciAppServicePlan`)
— see [token-issuer.md](token-issuer.md#hosting-context--swas-and-the-it-resource-constraint).

| resource | type | repo | url | notes |
|---|---|---|---|---|
| chd-ds-token-issuer | Function App (Consumption, Linux, Py 3.11) | `ds-geospatial-impact-estimates` (`token-issuer/`) | https://chd-ds-token-issuer.azurewebsites.net/api/token | **shared multi-app** keyless SAS minter — [token-issuer.md](token-issuer.md) |
| chd-ds-satellite-impact-viewer | SWA (Free) | `ds-geospatial-impact-estimates` (`swa-deploy.yml`, branch `v1`) | https://ashy-sea-03134990f.7.azurestaticapps.net | satellite impact viewer — supersedes the `chd-ds-geospatial-impact-viewer` App Service (kept as classic-URL fallback); PR previews on staging tier |
| dsci-monitor | SWA (Free) | `ds-pipelines-status` | https://thankful-ground-0e9f52a0f.7.azurestaticapps.net | pipelines-status dashboard (superseded by [pipeline-registry.md](pipeline-registry.md)) |
| CHD-HDXSignalsBlobTriggerApp | Function App (Linux) | — (HDX Signals) | — | blob-trigger function; not DS-team-owned day-to-day |

_Refresh:_ `az functionapp list -g IMB-CHD-DataScience-EastUS2 -o table` · `az staticwebapp list --query "[?resourceGroup=='IMB-CHD-DataScience-EastUS2']" -o table`

## Databricks jobs → see the live registry

The per-job inventory + **live health** for the Databricks **and** GitHub-Actions prod pipelines is the generated **[pipeline-registry.md](pipeline-registry.md)** (`scripts/gen_pipeline_registry.py`) — one row per deployed job keyed by runtime handle, with last-success-vs-cadence health, the data-plane mode, and compute. That's the single source of truth (this section used to carry a hand table; it drifted). The compute platform (policies, clusters, the dev/prod model) is [databricks.md](databricks.md).

Snapshot of what the registry flags (2026-06-22): **7 down** — `Run ECMWF Storms` + `Run IBTrACS` + the `Cuba Hurricane Observational Monitor` failing every run; the intended-prod NHC GHA workflow (`ds-nhc-forecast`) failing since 8 Jun; `ds-afro-cholera`, `ds-acled-fetcher`, `ds-aa-mdg-monitoring` monitoring all silently stalled for weeks–months — plus the NHC/GDACS DAB jobs running `mode=dev` (cutover) and `Storm Alert` on a personal cluster. None of these were visible to `pipelines-status`. (Dev jobs are now health-monitored too.)

## GitHub Actions pipelines

Many pipelines run on **scheduled GitHub Actions** (cron in `.github/workflows/`), not Databricks — this layer was previously untracked here. The registry indexes them; per-workflow schedules + the full `jobs[]` list live on each pipeline page (one home per fact). Surfaced during systems ingestion 2026-06-17; growing as more pipeline repos are ingested.

| pipeline | repo | GHA workflows (summary) | page |
|---|---|---|---|
| floodexposure-monitoring | `ds-floodexposure-monitoring` | daily `23:15 UTC` exposure → chained `repository_dispatch` (raster-stats → quantiles) + keep-awake | [pipelines/floodexposure-monitoring](../pipelines/floodexposure-monitoring.md) |
| nhc-forecast | `ds-nhc-forecast` | `Run script` every 3h (GHA, live) — note the named prod Databricks `Run NHC` job `266763033249426` is **PAUSED** | [pipelines/nhc-forecast](../pipelines/nhc-forecast.md) |
| imerg | `ds-imerg` | `run_download_imerg.yml` daily (+ Databricks `Run IMERG` `666239885322861`) | [pipelines/imerg](../pipelines/imerg.md) |
| hurricanes-monitoring | `ds-hurricanes-monitoring` | per-country monitoring workflows (GHA-only; not previously in any registry) | [pipelines/hurricanes-monitoring](../pipelines/hurricanes-monitoring.md) |
| mdg-monitoring | `ds-aa-mdg-monitoring` | `run_monitor_imerg.yml` daily `16:00 UTC` (`Monitor IMERG`, live; + `keep-alive` ping job) — GHA-only, scheduled workflow on `main` | [pipelines/mdg-monitoring](../pipelines/mdg-monitoring.md) |
| eth-drought-monitoring | `ds-aa-eth-drought-monitoring` | `run_monitoring.yml` (`Ethiopia Drought Monitoring`) cron `0 6 6 2,4,5 *` — 6th at 06:00 UTC in Feb/Apr/May only, live; single `monitor` job, scheduled workflow on `main` (+ `workflow_dispatch`). Reads SEAS5 from **prod** DB but zone CSVs from the **dev** blob (`STAGE='dev'`) | [pipelines/eth-drought-monitoring](../pipelines/eth-drought-monitoring.md) |
| ken-drought-monitoring | `ds-aa-ken-drought-monitoring` | `run_monitoring.yml` (`Kenya Drought Monitoring`) — `workflow_dispatch`-only (no cron), live; GHA-only on `main` | [pipelines/ken-drought-monitoring](../pipelines/ken-drought-monitoring.md) |
| afro-cholera | `ds-afro-cholera` | `daily_alerts.yml` (`Daily Cholera Alert`) `0 6 * * *` + dispatch, live — Global Cholera Monitoring, Listmonk alerts (GHA-only) | [pipelines/afro-cholera](../pipelines/afro-cholera.md) |
| nga-flood-monitoring | `ds-nga-flood-monitoring` | `nga-gauge-monitor.yaml` daily `14:00 UTC` + dispatch, live (GHA-only) — Nigeria flood gauge monitor | [pipelines/nga-flood-monitoring](../pipelines/nga-flood-monitoring.md) |
| acled-fetcher | `ds-acled-fetcher` | `main.yml` daily `08:00 UTC` + `workflow_dispatch`, live (GHA-only on `main`) | [pipelines/acled-fetcher](../pipelines/acled-fetcher.md) |
| acled-conflict-index | `ds-acled-conflict-index` | `main.yml` weekly `0 9 * * 1` — **not firing** (workflow lives only on `feat/initial-scraper`, not the default branch; effectively `workflow_dispatch`-only); dev | [pipelines/acled-conflict-index](../pipelines/acled-conflict-index.md) |
| cholera-pdf-scraper | `ds-cholera-pdf-scraper` | 5 workflows: `download-latest-who-pdf.yml` `47 13 * * 2,5` → chained `extract-from-pdf` / `rule-based-extract` (`workflow_run`) → `post-process-extractions` (`workflow_call`), live; all `STAGE=dev` (dev blob) | [pipelines/cholera-pdf-scraper](../pipelines/cholera-pdf-scraper.md) |
| pipelines-status | `ds-pipelines-status` | `update.yml` `15 */6 * * *` (scrapes Databricks job status) + `azure-static-web-apps-…0f.yml` deploys the status Static Web App on push, live | [pipelines/pipelines-status](../pipelines/pipelines-status.md) |
| hti-hurricanes-impactmodel | `ds-aa-hti-hurricanes-impactmodel` | `main.yml` (2STG-XGB affected-population predictions) on push to `fede-implementation` + dispatch (daily cron commented out); runs off the feature branch (`main` stale) | [pipelines/hti-hurricanes-impactmodel](../pipelines/hti-hurricanes-impactmodel.md) |
| storm-impact-harmonisation | `ds-storm-impact-harmonisation` | `daily-gdacs-monitor-email.yml` `20 3,9,15,21 * * *` (live) + 2 app-deploy workflows (cerf-rr slot of `chd-ds-seas5-viz`; global-cyclones slot of `chd-pa-aa-fji-storms-app`); work split across 3 branches | [pipelines/storm-impact-harmonisation](../pipelines/storm-impact-harmonisation.md) |
| slack-bot | `ds-slack-bot` | `dataset-updates.yaml` monthly `0 9 1 * *` (manual dataset-update Slack alerts) + `ci.yaml` — **not deployed** (lives on `manual-update-notifications`, unmerged) | [pipelines/slack-bot](../pipelines/slack-bot.md) |

_TODO: GitHub Actions has no single org-wide API like `az`/`databricks`; inventory grows as pipeline repos are ingested. Refresh per-repo via `gh workflow list -R ocha-dap/<repo>`._

## GitHub Pages & Netlify — rendered sites & WASM apps

Many repos publish a **rendered static site** rather than (or alongside) an Azure app: a Quarto/RMarkdown book of the analysis, a maps/docs site, or a marimo notebook exported to WASM. These are the "nice rendered version" to point people at — collected here so you don't have to dig through each repo. Cross-link from the relevant framework/pipeline/analysis page (use the `apps:` frontmatter list and link back here).

| site | repo | platform | kind | url | KB page |
|---|---|---|---|---|---|
| Afghanistan drought analysis book | `ds-aa-afg-drought` | Netlify (+ Quarto Pub mirror) | Quarto book | https://drought-aa-afghanistan.netlify.app | [frameworks/afg-drought/2026-04-04](../frameworks/afg-drought/2026-04-04.md) |
| Syria drought analysis book | `ds-aa-syr-drought` | Netlify | Quarto book | https://book-aa-syria-drought.netlify.app | [analysis/syr-drought](../analysis/syr-drought.md) |
| Cuba hurricanes analysis book | `ds-aa-cub-hurricanes` | Netlify | Quarto book | https://ds-aa-cuba-hurricanes-analysis.netlify.app | [frameworks/cub-hurricanes/2026-06-17](../frameworks/cub-hurricanes/2026-06-17.md) |
| Global Flood Monitoring (GFM) book | `ds-flood-gfm` | Netlify | Quarto book | https://ds-global-flood-monitoring.netlify.app | [pipelines/flood-gfm](../pipelines/flood-gfm.md) |
| Cholera PDF-scraper (LLM extraction) book | `ds-cholera-pdf-scraper` | Netlify | Quarto book | https://llm-data-sraping.netlify.app | [pipelines/cholera-pdf-scraper](../pipelines/cholera-pdf-scraper.md) |
| COD IDSR data-evaluation book | `pa-aa-cod-infectious-disease` | GH Pages | Quarto book | https://psychic-adventure-5l3yn6e.pages.github.io/ | [frameworks/cod-infectious-disease/2025-03-11](../frameworks/cod-infectious-disease/2025-03-11.md) |
| Teleconnections (ENSO/IOD) docs & maps | `ds-teleconnections` | GH Pages (`feature/era5-ghpages`) | rendered docs site | https://ocha-dap.github.io/ds-teleconnections/ | [pipelines/teleconnections](../pipelines/teleconnections.md) |
| C3S seasonal-skill viz | `ds-c3s-viz` | GH Pages | rendered viz | https://ocha-dap.github.io/ds-c3s-viz/ | [apps/c3s-viz](../apps/c3s-viz.md) |
| SEAS5 skill & alert explorer | `ds-seas5-skill` | GH Pages | marimo WASM | https://ocha-dap.github.io/ds-seas5-skill/ | [apps/seas5-skill](../apps/seas5-skill.md) |
| Niger drought trigger explorer | `ds-aa-ner-drought` | GH Pages (`iri-trend` branch, `docs/`) | marimo WASM | https://ocha-dap.github.io/ds-aa-ner-drought/ | [frameworks/ner-drought/2026-06-03](../frameworks/ner-drought/2026-06-03.md) |
| Vanuatu cyclone trigger explorer | `ds-aa-vut-cyclones` | GH Pages (`2026-workshop` branch) | marimo WASM | https://ocha-dap.github.io/ds-aa-vut-cyclones/ | [frameworks/vut-cyclones/development](../frameworks/vut-cyclones/development.md) |
| Storms-alerts signup form | `ds-storms-alerts` | GH Pages | static form | https://ocha-dap.github.io/ds-storms-alerts/ | [pipelines/storms-alerts](../pipelines/storms-alerts.md) |
| Storm exposure comparison | `ds-storm-impact-harmonisation` | GH Pages (workflow mode) | static data app (pre-baked JSON) | https://ocha-dap.github.io/ds-storm-impact-harmonisation/compare/ | [apps/storm-exposure-compare](../apps/storm-exposure-compare.md) |

Notes:
- **Branch matters.** Several are served off a feature branch's `docs/` folder, not `main` — recorded in the platform column. The published site can lag (or lead) `main`.
- **Default Netlify/Pages URLs** (e.g. `psychic-adventure-…pages.github.io`) are auto-generated and fragile; prefer the named URL if the repo later sets one.

_Refresh (no single org-wide endpoint — iterate over repos):_
- GH Pages: `gh api repos/ocha-dap/<repo>/pages --jq .html_url` (404 = Pages off). Sweep: `for r in $(gh repo list ocha-dap -L 300 --json name -q '.[].name'); do gh api repos/ocha-dap/$r/pages --jq .html_url 2>/dev/null && echo "  $r"; done`
- Netlify (best-effort; team uses personal Netlify accounts): `netlify sites:list` after `netlify login`, or grep repos for `netlify.toml`.
- **Best signal for Quarto books: `_publish.yml`** — `quarto publish` writes the exact target(s) + URL(s) into a `_publish.yml` next to `_quarto.yml`, even when there's no CI deploy workflow and no GH Pages. This is how the AFG book (Netlify + Quarto Pub, no deploy workflow) was found. Org-wide sweep: `gh search code --owner ocha-dap --filename _publish.yml --json repository,path`, then `gh api repos/ocha-dap/<repo>/contents/<path> --jq .content | base64 -d` for each. **Caveat:** `gh search code` only indexes **default branches of repos the token can read** — books published from a feature branch, or with `_publish.yml` gitignored, won't appear. This table is a floor, not a ceiling. (Last full sweep: 2026-06-25 → 5 books: afg, syr, cub, gfm, cholera-pdf-scraper.) These are often **personal** Netlify/Quarto-Pub accounts (AFG → `zackarno.quarto.pub`), so they won't show under any org inventory. Netlify auto-names can also carry typos (cholera → `llm-data-sraping`) — record the live address verbatim.
- Other per-repo hints: `_quarto.yml` / `_site/` / `docs/` output, a `.github/workflows/pages.yml`, or a README badge.
