---
content_type: infrastructure
last_reviewed: "2026-08-10"   # bump when a human verifies the page is still accurate
---

# Comms — Listmonk & ocha-relay

How the team sends email alerts/campaigns. Used by [storms-alerts](../pipelines/storms-alerts.md) and other comms. For how a pipeline should distinguish test sends from production sends (`TEST_EMAIL` / `SIMULATE_TRIGGER` / `DRY_RUN`), see [email-testing.md](email-testing.md).

## Listmonk

> **Who receives what:** the [database network map](https://ocha-dap.github.io/ds-knowledge-base/db-network/) shows every alert pipeline that sends through Listmonk and, once `scripts/gen_listmonk_lists.py` has committed a lists snapshot (`infrastructure/.listmonk-lists.json`, weekly via `listmonk-lists.yml` when the `DSCI_LISTMONK_*` secrets exist), how many recipients each reaches. The production list ids per pipeline live in `infrastructure/db-network.yml`.

Self-hosted open-source newsletter/mailing-list manager (campaigns, subscribers, lists, media library, HTML templates). [API docs](https://listmonk.app/docs/apis/apis/).

- **Base URL:** env `DSCI_LISTMONK_BASE_URL` — full base URL **including `/api`**, trailing slash stripped. Current instance is hosted as an **Azure Web App (eastus2)**: `https://listmonk-demo-...eastus2-01.azurewebsites.net/api` (note: a `*-demo-*` URL, but it is the production target). Local testing: `listmonk-test/docker-compose.yml` (listmonk + postgres:17 on port 9000).
- **Lists referenced by TAG, not hardcoded IDs.** All project lists carry tag `ds-storms-alerts`; within that, per-country lists tagged `iso3:<ISO3>` (display "Storm Alerts - <Country>"), plus aggregates `aggregate:all`, `aggregate:lac`, `aggregate:monitoring`. IDs are discovered at runtime by tag. The only hardcoded ID is the test list (`5`); campaign template ID is hardcoded `8` (OCHA instance template).
- **Auth — two credential tiers (HTTP Basic):**
  - sending: `DSCI_LISTMONK_API_USERNAME` + `DSCI_LISTMONK_API_KEY` (needs campaigns:manage + campaigns:get)
  - admin/list-creation: `DSCI_LISTMONK_ADMIN_API_USERNAME` + `DSCI_LISTMONK_ADMIN_API_KEY` (used by `setup_country_lists.py`)
  - On Databricks these come from the `dsci` secret scope → env vars; on GHA from repo secrets.

### Template branching on the campaign name

The shared OCHA template (id `8`, `base_campaign`; `11` = `base_campaign_dev`, currently byte-identical) picks its chrome from the **campaign name**, case-insensitive contains-match:

- `[test]` → renders the **red TEST banner** in the email body — the visual marker recipients see on test sends (see [email-testing.md](email-testing.md));
- `[fr]` / `[es]` → French/Spanish translations of the template strings;
- `[manual]` → drops the "automated message" strip.

Two consequences: a test campaign whose *name* lacks `[test]` renders with production chrome even if the subject is tagged, and previewing under the wrong name shows the wrong variant. Also note `GET /api/campaigns?query=` is a Postgres `to_tsquery` — punctuation like `[test] x` **HTTP 500s**; search on a plain token and filter the exact name client-side.

### Media storage & persistence

Inline email images are **hosted, not embedded**: charts are uploaded via `upload_media` to Listmonk's media library and referenced by URL (`https://<host>/uploads/<file>`) in `<img>` tags — the bytes are not in the email. Images therefore render only as long as the media files survive on the instance.

- **Provider** is Listmonk's `filesystem` (admin → Settings → Media), served at `upload_uri = /uploads`.
- **Persistence gotcha (root-caused & fixed 2026-06-30):** `upload.filesystem.upload_path` was `/tmp`, which is **ephemeral** on Azure App Service — wiped on every container recycle, so already-sent emails lost their images after ~a day or two. Fixed by creating an Azure Files share **`listmonk-media`** (storage account `imb0chd0dev`, RG `IMB-CHD-DataScience-EastUS2`), mounting it at **`/media`** on the `listmonk-demo` App Service, and setting `upload_path = /media` via the admin API. `WEBSITES_ENABLE_APP_SERVICE_STORAGE = false`, so `/home` is **not** persistent — durability comes solely from the mount.
- **If images vanish again, check:** the `/media` mount still exists (`az webapp config storage-account list -g IMB-CHD-DataScience-EastUS2 -n listmonk-demo`) and Listmonk `upload_path` is still `/media` (admin → Settings → Media). Any **new** Listmonk instance must repeat this (durable mounted media) or images won't persist past a recycle.
- Already-delivered emails that predate the fix stay broken — their URLs point at the wiped `/tmp`; only new sends are durable.

### Deployments

There are **two Listmonk deployments sharing the same database** — subscribers/lists/campaigns are identical in both:

- **non-VNet** (`listmonk-dev-…`) — could send from the **@humdata.org** address; now **disabled** (that sender address is no longer used).
- **VNet** (`listmonk-demo-…`) — sends from the **@un.org** address; **the active instance** (this is the `*-demo-*` base URL above — VNet-integrated, not a demo).

### User roles

Simplified mapping (full per-permission detail is in the Listmonk UI under roles):

| role | used for |
|---|---|
| Super Admin | DS manager |
| Admin | DS team members |
| Sender | DS team API credentials (programmatic sends) |
| List manager | country/regional focal points who manage specific lists |
| Viewer | staff who only monitor Listmonk |

### Deployment & upgrades

- Azure Web App running the **official Listmonk Docker image**. **All configuration is via env vars** — no `config.toml` / docker-compose. DB password location: BitWarden.
- The image tag is **pinned to a specific version** (`listmonk:v6.0.0` at time of writing) — never `latest`: a new upstream release would break the app on any web-app restart.
- **Upgrade procedure**: (1) change the image tag to the new version; (2) back up the DB; (3) set the App Service Startup command to `./listmonk --upgrade --yes` and restart (upgrades the DB schema; `--yes` skips the back-up-first prompt); (4) clear the Startup command back to blank; (5) restart again.

### Design history

Listmonk replaced the ad-hoc per-framework email pipelines (Python/R or hand-built Mailchimp): heavy code duplication, a 50-recipient limit sending from `data.science@humdata.org`, and clunky hand-managed lists. The requirements that drove the choice: built-in mailing-list management, cc-style recipient visibility (all recipients can see each other — upgraded to must-have after CERF feedback), tiered permissions (admin / list-manager / self-serve), and an @un.org sender. The full requirement + platform comparison (MailChimp/SendGrid/MailGun/MailJet/Brevo/Mandrill) lives in the Confluence archive (pages `monitoring-setup.md` + `monitoring-setup/revised-requirements.md` under `confluence/` in `ds-knowledge-base-internal`).

Digested from the retired DSCI Confluence space (archive: `confluence/` in `ds-knowledge-base-internal`).

### Database — prod Postgres (migrated 2026-09-25)

The Listmonk database lives on **prod** `chd-rasterstats-prod` (database `listmonk`, app role `listmonk_service`, which owns the database and the `public` schema). The `listmonk-demo` App Service reaches it through its **private endpoint** (10.208.11.18): inside `ocha-eastus2-vnet` the prod hostname resolves to that address, so the app setting is simply the public hostname and traffic stays private. The URL, `dsci` secrets and GHA workflows did not change. The `listmonk_service` password was rotated on 2026-09-25 and lives in **BitWarden** (Listmonk entry) — it is only used by the App Service setting `LISTMONK_db__password`; no pipeline or person needs it.

**How to confirm the app is on the private path** (after any network change): inside the VNet the prod hostname must resolve to the endpoint IP (probe via the Kudu `api/command` endpoint with `getent hosts …`), and on the database `pg_stat_activity` shows the app's `client_addr` as an `fd40:…` Private Link address rather than the App Service's public IPv4.

**History.** Until 2026-09-25 the database was on the dev server. On 2026-09-22 OICT disabled public access on `chd-rasterstats-dev` (no private endpoint at first), which took Listmonk down for two days; a private endpoint plus a temporary public-IP stopgap brought it back, and the long-deferred move to prod was done with a full `pg_dump`/`pg_restore` (row counts and all hard-coded ids — template `8`, lists `5,6,10,11,14,15,21,110` — verified identical: 214 subscribers, 119 lists, 2007 campaigns, 1726 media rows). The dev copy is kept for about a week as rollback (repoint `LISTMONK_db__host` and `LISTMONK_db__password`, restart), then can be dropped. Runbook: `migrate_listmonk.sh` in the `listmonk-test` folder of the person who ran it; it needs only the dev **read** role for the dump and `listmonk_service` for the restore.

**Gotchas learned, for the next migration or a rebuild:**

- **Roles/databases need a real admin.** The Databricks Job Compute policy's prod write login is `dbwriter`, which owns the `storms` schema but has no CREATEDB/CREATEROLE. `CREATE ROLE listmonk_service` and `CREATE DATABASE listmonk OWNER listmonk_service` were run by an Entra admin of the server (`adm.hker1`, via `az account get-access-token --resource-type oss-rdbms` + psql).
- **Azure owns `public`.** On Azure Flexible Server the `public` schema of a new database belongs to `azure_pg_admin`, so even the database owner cannot create tables in it (the first restore attempt failed on every CREATE). Fix: the admin runs `ALTER SCHEMA public OWNER TO listmonk_service;` **connected to the `listmonk` database**. Dev has the same `azure_pg_admin`-owned `public`, with tables owned by `listmonk_service`.
- **pgcrypto** is in Listmonk's `schema.sql` (`CREATE EXTENSION`) but no query uses it. It must be on the server's `azure.extensions` allowlist (an Azure control-plane setting, IT/owner) for the restore to recreate it; it is a *trusted* extension, so once allow-listed the database owner can create it. Restores can also just skip the two pgcrypto TOC entries.
- **Private endpoints and NSGs.** `eastus2-nsg` is shared by the backend subnets; the `ocha-eastus2-prod-backend` subnet has private-endpoint network policies *disabled* (NSG not enforced on endpoints there, so the webapp subnet can reach 5432), while `ocha-eastus2-dev-backend` has them *enabled* and the NSG blocks the webapp subnet. That is why the first dev endpoint (10.208.11.164) is unreachable from App Services while the second one (`ch-rasterstast-dev2`, 10.208.11.20, in prod-backend) works. Probe from inside an App Service with the Kudu `api/command` endpoint, e.g. a Postgres SSL-request handshake to the endpoint IP.
- **A `pg_dump` 17 → PG 16 restore logs one harmless error** (`SET transaction_timeout`).

**Open follow-ups (as of 2026-09-25):** drop the dev `listmonk` database once the rollback window (~1 week) has passed (needs chdadmin or an Entra admin); six other App Services still point at the dev hostname (`chd-ds-kb-mcp`, `chd-ds-kb-mcp-internal`, `chd-ds-storms-explore`, `chd-ds-storms-alerts`, `chd-ds-aa-extract`, `chd-ds-cub-trigger`) and, if VNet-integrated, resolve it to the blocked dev endpoint — ask OICT to repoint the dev DNS record to the reachable endpoint (10.208.11.20) or fix the dev-backend NSG; and OICT should not disable public access on `chd-rasterstats-prod` while Databricks is not VNet-injected, or every prod pipeline loses the database.

## ocha-relay

Internal DS comms library (`ocha-dap/ocha-relay`, latest release **v0.3.0**) — full reference: [libs/ocha-relay](libs/ocha-relay.md). Only the Listmonk module is implemented (SMTP+Jinja planned). Install from git, **pin by tag/SHA** (consumers currently pin older tags, e.g. `@v0.2.0`; storms-alerts pins it in `databricks.yml`). <!-- timeless -->

- **`ocha_relay.listmonk.ListmonkClient`** (frozen dataclass: base_url, username, password, timeout=30). `from_env()` reads the three `DSCI_LISTMONK_*` vars and raises if missing (no silent 401s).
- **Key functions:** `create_campaign(*, name, subject, body, list_ids, template_id=8, media_ids)` → draft id; `upload_media(bytes, filename)` → hosted URL (inline `<img>`); `upload_attachment(bytes, filename)` → media id; `send_campaign(id, *, skip_confirmation=False)` (PUTs status→running = the actual send; default requires retyping the campaign name; hard-refuses "finished"); plus `create_list`, `fetch_all_lists(tag=...)`, `list_subscribers`, `campaign_recipients`, `get_rendered_html`, `preview_in_browser`. Types: `Subscriber`, `SendManifest`; exception `SendAborted`.
- Talks to Listmonk over the REST API with `requests` + basic auth (pagination 100/page).
- **Who uses it:** general DS comms package; `ds-storms-alerts` is the concrete consumer today.
