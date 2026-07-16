---
content_type: infrastructure
last_reviewed: "2026-06-30"   # bump when a human verifies the page is still accurate
---

# Comms — Listmonk & ocha-relay

How the team sends email alerts/campaigns. Used by [storms-alerts](../pipelines/storms-alerts.md) and other comms.

## Listmonk

Self-hosted open-source newsletter/mailing-list manager (campaigns, subscribers, lists, media library, HTML templates). [API docs](https://listmonk.app/docs/apis/apis/).

- **Base URL:** env `DSCI_LISTMONK_BASE_URL` — full base URL **including `/api`**, trailing slash stripped. Current instance is hosted as an **Azure Web App (eastus2)**: `https://listmonk-demo-...eastus2-01.azurewebsites.net/api` (note: a `*-demo-*` URL, but it is the production target). Local testing: `listmonk-test/docker-compose.yml` (listmonk + postgres:17 on port 9000).
- **Lists referenced by TAG, not hardcoded IDs.** All project lists carry tag `ds-storms-alerts`; within that, per-country lists tagged `iso3:<ISO3>` (display "Storm Alerts - <Country>"), plus aggregates `aggregate:all`, `aggregate:lac`, `aggregate:monitoring`. IDs are discovered at runtime by tag. The only hardcoded ID is the test list (`5`); campaign template ID is hardcoded `8` (OCHA instance template).
- **Auth — two credential tiers (HTTP Basic):**
  - sending: `DSCI_LISTMONK_API_USERNAME` + `DSCI_LISTMONK_API_KEY` (needs campaigns:manage + campaigns:get)
  - admin/list-creation: `DSCI_LISTMONK_ADMIN_API_USERNAME` + `DSCI_LISTMONK_ADMIN_API_KEY` (used by `setup_country_lists.py`)
  - On Databricks these come from the `dsci` secret scope → env vars; on GHA from repo secrets.

### Media storage & persistence

Inline email images are **hosted, not embedded**: charts are uploaded via `upload_media` to Listmonk's media library and referenced by URL (`https://<host>/uploads/<file>`) in `<img>` tags — the bytes are not in the email. Images therefore render only as long as the media files survive on the instance.

- **Provider** is Listmonk's `filesystem` (admin → Settings → Media), served at `upload_uri = /uploads`.
- **Persistence gotcha (root-caused & fixed 2026-06-30):** `upload.filesystem.upload_path` was `/tmp`, which is **ephemeral** on Azure App Service — wiped on every container recycle, so already-sent emails lost their images after ~a day or two. Fixed by creating an Azure Files share **`listmonk-media`** (storage account `imb0chd0dev`, RG `IMB-CHD-DataScience-EastUS2`), mounting it at **`/media`** on the `listmonk-demo` App Service, and setting `upload_path = /media` via the admin API. `WEBSITES_ENABLE_APP_SERVICE_STORAGE = false`, so `/home` is **not** persistent — durability comes solely from the mount.
- **If images vanish again, check:** the `/media` mount still exists (`az webapp config storage-account list -g IMB-CHD-DataScience-EastUS2 -n listmonk-demo`) and Listmonk `upload_path` is still `/media` (admin → Settings → Media). Any **new** Listmonk instance must repeat this (durable mounted media) or images won't persist past a recycle.
- Already-delivered emails that predate the fix stay broken — their URLs point at the wiped `/tmp`; only new sends are durable.

### DB migration dev → prod Postgres — **deferred TODO**

<!-- TODO: migrate the Listmonk DB off the dev Postgres server to prod. Deferred 2026-07; not yet scheduled. -->

The Listmonk database currently lives on the **dev** server `chd-rasterstats-dev` (database `listmonk`, app role `listmonk_service`) — the `listmonk-demo` App Service points at it via its `LISTMONK_db__*` app settings. It should move to **prod** `chd-rasterstats-prod`. The app stays on `listmonk-demo` and the URL is unchanged, so **no repos, `dsci` secrets, or GHA workflows change** — only the app's three DB settings (`__host`, `__user`, `__password`) get repointed. Verified plan (June 2026), not yet executed:

- **Must be a full `pg_dump`/`pg_restore`, not list-recreation** — primary-key IDs are hardcoded downstream (template `8`, test list `5`; and `pa-aa-fji-storms` lists `5,6,10,11,14,15`, `ds-aa-mmr-cyclones` list `21`/template `100`). A binary-faithful copy preserves every id. DB is small (~72 MB; PG 16.13 both ends; extensions `pgcrypto` + `plpgsql`).
- **Run the copy from the Databricks personal cluster**, not locally: the `dsci` scope gives the cluster the *current* prod admin pw (`DSCI_AZ_DB_PROD_PW_WRITE` = `chdadmin`; local copies go stale), it's Linux with network reach to both servers, and needs no local Postgres tooling (`apt-get install postgresql-client-16`).
- **Azure control-plane bits stay in local `az`** (cluster isn't authed for App Service / server params): add `PGCRYPTO` to prod `azure.extensions` (currently `POSTGIS` only, else the restore's `CREATE EXTENSION` fails); stop/start `listmonk-demo`; set the three DB app settings.
- **Prod prep** (as `chdadmin`): `CREATE ROLE listmonk_service` + `CREATE DATABASE listmonk OWNER listmonk_service`, then `CREATE EXTENSION pgcrypto` in it. Prod firewall already has an `AllowAll` rule.
- **Downtime**: stop the app during the dump (a few minutes) so no writes are lost between dump and cutover. **Rollback**: repoint the three settings back to `chd-rasterstats-dev` — keep the dev DB untouched ~1 week.
- **Verify** post-restore counts match the dev baseline (June 2026): subscribers `111`, lists `100`, subscriber_lists `153`, campaigns `777`, templates `6`, media `749`, users `8`; and that template `8` / lists `5,6,10,11,14,15,21` exist by id.
- **Media is unaffected** — files sit on the durable `/media` Azure Files mount (see above), not in the DB; the DB carries only metadata and the mount stays put.

## ocha-relay

Internal DS comms library (`ocha-dap/ocha-relay`, latest release **v0.3.0**) — full reference: [libs/ocha-relay](libs/ocha-relay.md). Only the Listmonk module is implemented (SMTP+Jinja planned). Install from git, **pin by tag/SHA** (consumers currently pin older tags, e.g. `@v0.2.0`; storms-alerts pins it in `databricks.yml`).

- **`ocha_relay.listmonk.ListmonkClient`** (frozen dataclass: base_url, username, password, timeout=30). `from_env()` reads the three `DSCI_LISTMONK_*` vars and raises if missing (no silent 401s).
- **Key functions:** `create_campaign(*, name, subject, body, list_ids, template_id=8, media_ids)` → draft id; `upload_media(bytes, filename)` → hosted URL (inline `<img>`); `upload_attachment(bytes, filename)` → media id; `send_campaign(id, *, skip_confirmation=False)` (PUTs status→running = the actual send; default requires retyping the campaign name; hard-refuses "finished"); plus `create_list`, `fetch_all_lists(tag=...)`, `list_subscribers`, `campaign_recipients`, `get_rendered_html`, `preview_in_browser`. Types: `Subscriber`, `SendManifest`; exception `SendAborted`.
- Talks to Listmonk over the REST API with `requests` + basic auth (pagination 100/page).
- **Who uses it:** general DS comms package; `ds-storms-alerts` is the concrete consumer today.
