---
content_type: library
name: ocha-mailchimp
status: active
purpose: "Thin wrapper around the Mailchimp REST API v3 for reading subscribers and managing interest groups and tags"
language: python
source_repo: ocha-dap/ocha-mailchimp
source_branch: main
source_sha: 57475c3
version: "unreleased (no git tag or PyPI release; version derived from VCS via hatch-vcs)"
install: "pip install git+https://github.com/OCHA-DAP/ocha-mailchimp.git"
auth_env:
  - MAILCHIMP_API_KEY
  - SERVER_PREFIX
key_api:
  - get_subscribers
  - get_subscriber_emails
  - get_interest_categories
  - get_interests
  - get_subscribers_with_interest
  - add_subscriber_to_group
  - get_subscriber_hash
  - add_tag_to_subscriber
  - remove_tag_from_subscriber
  - add_tag_to_interest_subscribers
depends_on: []
used_by: []
visibility: public
last_synced: "2026-06-22"
---

## Summary

`ocha-mailchimp` is a small, project-agnostic Python library that wraps the [Mailchimp Marketing API v3](https://mailchimp.com/developer/marketing/api/) for use across OCHA DS projects. It covers the subscriber/member read path (paginated listing, email extraction, interest-group filtering) and the write path (adding/removing subscriber interest groups and tags). Auth is Bearer token; credentials are loaded from env vars or a `.env` file via `python-dotenv`.

The library is early-stage (Alpha, four commits, no published PyPI release or git tag at time of ingestion — so there is no real version number; `hatch-vcs` derives one from VCS). It declares no runtime dependencies in `pyproject.toml` (`dependencies = []`), though the code imports `requests`, `loguru`, and `python-dotenv` (pinned only in `requirements.txt`), and has no `ocha-*` library dependencies — it talks directly to the Mailchimp REST API via `requests`.

> Note: the installation docs mention `DSCI_AZ_BLOB_DEV_SAS` in the `.env` example, but the actual code does not use Azure Blob at all. That env var is leftover boilerplate from the repo template and can be ignored.

## Install & auth

```bash
# install from git (no PyPI release yet)
pip install git+https://github.com/OCHA-DAP/ocha-mailchimp.git

# or with uv
uv add git+https://github.com/OCHA-DAP/ocha-mailchimp.git
```

Create a `.env` file or set these env vars before importing:

```bash
MAILCHIMP_API_KEY=<your Mailchimp API key>
SERVER_PREFIX=<your server prefix, e.g. us1>
```

The module reads both at import time (`mailchimp_api.py` top level) and constructs `BASE_URL = https://{SERVER_PREFIX}.api.mailchimp.com/3.0`. There is no `from_env()` helper — if either var is missing the API calls will silently fail with 401s, so validate the env before use.

```python
from ocha_mailchimp.mailchimp_api import get_subscribers, add_subscriber_to_group
```

## Key API

| Name | What it does |
|---|---|
| `get_subscribers(list_id)` | Paginated fetch of all `subscribed` members for a list; returns raw Mailchimp member dicts (1000/page). |
| `get_subscriber_emails(list_id)` | Convenience wrapper: returns just the `email_address` strings from `get_subscribers`. |
| `get_interest_categories(list_id)` | Lists all interest categories (groups) for a list. |
| `get_interests(list_id, category_id)` | Lists individual interests within a category. |
| `get_subscribers_with_interest(list_id, interest_id)` | Returns email addresses of subscribed members who have a specific interest set to `True`. |
| `add_subscriber_to_group(email, new_group_id, list_id)` | PATCH a subscriber to add them to an interest group (`interests: {group_id: True}`). |
| `get_subscriber_hash(email)` | MD5-hex of lowercased email — the Mailchimp member identifier required for member-level API calls. |
| `add_tag_to_subscriber(email, tag_name, list_id)` | POST a tag with `status: active` to a subscriber. |
| `remove_tag_from_subscriber(email, tag_name, list_id)` | POST a tag with `status: inactive` to remove it. |
| `add_tag_to_interest_subscribers(list_id, interest_id, tag_name)` | Batch: fetch all subscribers with an interest, then tag each one. |

## Used by

No KB pages currently list `ocha-mailchimp` in their `depends_on`. The library is available for any DS project using Mailchimp for subscriber management; no active pipeline consumer is recorded in this KB.

## Gotchas & conventions

- **Credentials loaded at import time.** `MAILCHIMP_API_KEY` and `SERVER_PREFIX` are read and the `BASE_URL` and `HEADERS` module-level constants are set when `mailchimp_api` is first imported. Missing env vars produce `None`-valued constants and silent 401 failures — validate the env before importing in any pipeline context.
- **No published release.** There are no git tags and no PyPI release; pin by SHA when using in production (`git+https://...@57475c3`).
- **No `ocha-stratus` dependency.** This library bypasses the team's standard blob/DB layer entirely — it talks directly to the Mailchimp REST API. Don't load subscribers from blob via stratus; use this library's `get_subscribers` instead.
- **Pagination cap is 1000/page.** The `get_subscribers` function hardcodes `count=1000` (Mailchimp's per-page max). For very large lists verify pagination is working correctly.
- **`DSCI_AZ_BLOB_DEV_SAS` in the install docs is a red herring.** The `.env` example in `docs/installation.md` lists this Azure SAS token, but the actual code never uses it. It's boilerplate from the repo template.
- **Interest groups vs tags.** Mailchimp distinguishes interest groups (segmentation within a list, identified by category/interest IDs) from tags (freeform labels). Both are supported; use the right call for each.
- **Alpha status.** Four commits, a dummy test, no CI configuration beyond pre-commit linting. Treat as experimental for production use.

## Source

- Repo: <https://github.com/OCHA-DAP/ocha-mailchimp>
- Branch: `main` (SHA `57475c3`)
- Docs: <https://ocha-mailchimp.readthedocs.io/en/latest/>
- Mailchimp API reference: <https://mailchimp.com/developer/marketing/api/>
