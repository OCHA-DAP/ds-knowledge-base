---
content_type: library
name: ocha-relay
status: active
purpose: "Thin Listmonk campaign client for the DS team's automated email alerts (SMTP+Jinja planned but not yet implemented)"
language: python
source_repo: ocha-dap/ocha-relay
source_branch: main
source_sha: "4e18078"
version: v0.3.0
install: "uv add \"ocha-relay @ git+https://github.com/OCHA-DAP/ocha-relay.git@v0.3.0\""
auth_env:
  - DSCI_LISTMONK_BASE_URL
  - DSCI_LISTMONK_API_USERNAME
  - DSCI_LISTMONK_API_KEY
key_api:
  - ListmonkClient
  - ListmonkClient.from_env
  - ListmonkClient.create_campaign
  - ListmonkClient.send_campaign
  - ListmonkClient.build_send_manifest
  - ListmonkClient.upload_media
  - ListmonkClient.upload_attachment
  - ListmonkClient.list_subscribers
  - ListmonkClient.campaign_recipients
  - ListmonkClient.fetch_all_lists
  - Subscriber
  - SendManifest
  - SendAborted
depends_on: []
used_by:
  - pipelines/storms-alerts
  - pipelines/moz-cholera-monitoring
  - pipelines/storm-impact-harmonisation
visibility: public
last_synced: "2026-06-22"
---

## Summary

`ocha-relay` is the DS team's internal Python library for sending automated email campaigns through the team's self-hosted [Listmonk](https://listmonk.app) instance. It wraps Listmonk's REST API with a typed, safety-first `ListmonkClient`: draft → inspect → preview → confirm → send, with hard refusals against re-sending finished campaigns. SMTP + Jinja templating is planned but not yet implemented. The only runtime dependency is `requests`.

Not on PyPI — install from git, pinned to a release tag.

## Install & auth

**Install (pin to a tag, never `@main` in production):**

```bash
uv add "ocha-relay @ git+https://github.com/OCHA-DAP/ocha-relay.git@v0.3.0"
```

In `pyproject.toml` / `uv.lock`, uv writes this as a `[tool.uv.sources]` stanza:

```toml
[tool.uv.sources]
ocha-relay = { git = "https://github.com/OCHA-DAP/ocha-relay.git", rev = "v0.3.0" }
```

**Auth — three env vars (all required):**

| Variable | What it is |
|---|---|
| `DSCI_LISTMONK_BASE_URL` | Full base URL including `/api`, no trailing slash (e.g. `https://<host>/api`) |
| `DSCI_LISTMONK_API_USERNAME` | API user from Listmonk admin → Settings → Users |
| `DSCI_LISTMONK_API_KEY` | API key paired with the username above |

`ListmonkClient.from_env()` raises `RuntimeError` immediately if any variable is missing — no silent 401s. On Databricks these come from the `dsci` secret scope; on GHA from repo secrets.

> For list-creation / admin operations (e.g. `setup_country_lists.py`), a second credential pair (`DSCI_LISTMONK_ADMIN_API_USERNAME` + `DSCI_LISTMONK_ADMIN_API_KEY`) is used directly — not via this library.

**Quick start:**

```python
from ocha_relay.listmonk import ListmonkClient

client = ListmonkClient.from_env()

# 1. Create a draft (does NOT send)
cid = client.create_campaign(
    name="Storm alert 2026-W25",
    subject="Tropical Cyclone Update",
    body="<h1>Alert</h1><p>Body copy.</p>",
    list_ids=[5, 7],
)

# 2. Inspect recipients before sending
recipients = client.campaign_recipients(cid)

# 3. Preview rendered HTML in a browser
client.preview_in_browser(cid)

# 4. Send — prompts for campaign name; use skip_confirmation=True in automation
client.send_campaign(cid, skip_confirmation=True)
```

## Key API

The full, canonical API reference is the repo's [`README.md` § API reference](https://github.com/OCHA-DAP/ocha-relay/blob/main/README.md) and the code at `src/ocha_relay/listmonk.py` — they live next to the code and can't drift. The few load-bearing entry points:

| Name | What it does |
|---|---|
| `ListmonkClient.from_env()` | Build a client from the three `DSCI_LISTMONK_*` env vars (raises if any missing). The normal entry point. |
| `create_campaign(*, name, subject, body, list_ids, template_id=8, media_ids)` | POSTs a **draft** campaign; returns its id. Does NOT send. |
| `send_campaign(campaign_id, *, skip_confirmation=False)` | The actual send (PUT status→`running`). Default retypes-the-name confirmation; `skip_confirmation=True` for automation; hard-refuses `status="finished"`. |
| `fetch_all_lists(*, tag=None)` / `list_subscribers` / `campaign_recipients` | Resolve list ids by tag and inspect recipients before sending. |

Other public surface (see the repo for signatures): `upload_media` / `upload_attachment`, `build_send_manifest`, `create_list`, `get_rendered_html`, `preview_in_browser`; data types `Subscriber`, `SendManifest`; exception `SendAborted`.

## Used by

- **`pipelines/storms-alerts`** — primary consumer; sends storm alert campaigns per-country and aggregate. Constructs `ListmonkClient.from_env()`, resolves lists by tag (`ds-storms-alerts`, `iso3:<ISO3>`), calls `create_campaign` + `send_campaign(skip_confirmation=True)` from a GHA-scheduled job. Pins the library by git SHA.
- **`pipelines/moz-cholera-monitoring`** — Mozambique cholera monitoring; pins `ocha-relay @v0.2.0`, creates and immediately sends a weekly campaign to list 102 (prod) / 103 (test).
- **`pipelines/storm-impact-harmonisation`** — daily GDACS monitor digest; pins `ocha-relay` (v0.2.0), renders an HTML exposure email and sends a Listmonk campaign.

> `pipelines/fms-tc-outlook` also emails via Listmonk but does **not** use this library — it has its own `src/email/listmonk.py` client. It depends on the Listmonk *instance* (see `infrastructure/comms-listmonk.md`), not `ocha-relay`.

## Gotchas & conventions

- **Not on PyPI — always pin by tag.** `@main` moves; `@v0.3.0` is immutable. Pin in `pyproject.toml`/`databricks.yml`.
- **`template_id=8` is OCHA-instance-specific.** If you point the client at a different Listmonk, find the correct template id in that instance's admin UI.
- **List IDs are discovered at runtime by tag, never hardcoded** (except the test list, id `5`). Use `fetch_all_lists(tag="ds-storms-alerts")` then filter by `iso3:<ISO3>` tags.
- **`send_campaign` hard-refuses `status="finished"`** even with `skip_confirmation=True`. Re-sending a finished campaign would duplicate emails and is intentionally blocked.
- **Headless environments with `skip_confirmation=False`** will raise `EOFError` on the `input()` call — the library surfaces this rather than silently skipping confirmation. Always set `skip_confirmation=True` in scheduled jobs.
- **Subscriber status vs subscription status are different.** `Subscriber.status` is the subscriber-level state (`enabled`/`disabled`/`blocklisted`). Per-list state (`confirmed`/`unconfirmed`/`unsubscribed`) lives in `.raw["lists"]` and is accessed via `.subscription_status_for(list_id)`.
- **Admin credentials (list creation)** are a second pair — `DSCI_LISTMONK_ADMIN_API_*` — used directly, not via `ListmonkClient`.
- **Tests are network-safe:** `tests/conftest.py` patches `requests.Session.send` to refuse real HTTP — a forgotten mock fails loudly rather than firing against prod.
- **Early-stage (v0.3.0); SMTP+Jinja planned.** Only the Listmonk module is implemented. Check the repo for new modules before adding custom email helpers.

## Source

- Repo: [ocha-dap/ocha-relay](https://github.com/OCHA-DAP/ocha-relay)
- Branch: `main` (sha `4451729`)
- Latest release: `v0.3.0`
- Listmonk API reference: https://listmonk.app/docs/apis/apis/
- Infrastructure context: [infrastructure/comms-listmonk.md](../comms-listmonk.md)
