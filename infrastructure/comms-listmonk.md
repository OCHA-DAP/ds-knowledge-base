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

## ocha-relay

Internal DS comms library (`ocha-dap/ocha-relay`, latest release **v0.3.0**) — full reference: [libs/ocha-relay](libs/ocha-relay.md). Only the Listmonk module is implemented (SMTP+Jinja planned). Install from git, **pin by tag/SHA** (consumers currently pin older tags, e.g. `@v0.2.0`; storms-alerts pins it in `databricks.yml`).

- **`ocha_relay.listmonk.ListmonkClient`** (frozen dataclass: base_url, username, password, timeout=30). `from_env()` reads the three `DSCI_LISTMONK_*` vars and raises if missing (no silent 401s).
- **Key functions:** `create_campaign(*, name, subject, body, list_ids, template_id=8, media_ids)` → draft id; `upload_media(bytes, filename)` → hosted URL (inline `<img>`); `upload_attachment(bytes, filename)` → media id; `send_campaign(id, *, skip_confirmation=False)` (PUTs status→running = the actual send; default requires retyping the campaign name; hard-refuses "finished"); plus `create_list`, `fetch_all_lists(tag=...)`, `list_subscribers`, `campaign_recipients`, `get_rendered_html`, `preview_in_browser`. Types: `Subscriber`, `SendManifest`; exception `SendAborted`.
- Talks to Listmonk over the REST API with `requests` + basic auth (pagination 100/page).
- **Who uses it:** general DS comms package; `ds-storms-alerts` is the concrete consumer today.
