---
content_type: pipeline
name: slack-bot
type: alert
status: in-development   # code + workflows live only on the manual-update-notifications branch; nothing deployed from main yet
deployment:
  platform: github-actions
  resource_group: null
  jobs:
    - name: "Manual Dataset Update Notification"
      ref: ".github/workflows/dataset-updates.yaml"
      schedule: "0 9 1 * *"
      status: not-deployed   # workflow file only on manual-update-notifications branch, NOT on main; GHA crons fire from default branch only -> never runs in prod
    - name: "CI"
      ref: ".github/workflows/ci.yaml"
      schedule: "push/PR to main"
      status: not-deployed   # ci.yaml also only on manual-update-notifications branch, not main; triggers on push/PR to main but the file isn't there yet
inputs: []
outputs:
  - "Slack message to #dsci-pipelines-stats"
dependencies:
  - "slack-sdk>=3.39.0"
  - "python-dotenv"
  - "SLACK_BOT_TOKEN (GitHub Actions secret)"
downstream:
  - "Team ops: manual dataset update tracking (EM-DAT, CERF Allocations)"
depends_on: []
source_repo: ocha-dap/ds-slack-bot
source_branch: manual-update-notifications
source_sha: 55659fd
code_ref:
  - "src/dataset_updates.py"
  - ".github/workflows/dataset-updates.yaml"
discrepancies:
  - "[conflict] Nothing is deployed. The default branch `main` contains ONLY `.gitignore` and `README.md` — no `src/`, no `.github/workflows/`. Both `dataset-updates.yaml` (scheduled cron) and `ci.yaml` (push/PR) exist ONLY on the `manual-update-notifications` branch. GHA scheduled crons fire from the default branch only, and `ci.yaml` triggers on push/PR to `main` but the file isn't on `main` — so NEITHER workflow currently runs in production. The monthly reminder will not fire automatically until the branch is merged to `main`."
  - "[gap] `ds-slack-bot` is NOT listed in infrastructure/deployments.md (not in the GHA pipelines table). Once `manual-update-notifications` merges to `main` and the monthly cron goes live, add a row to the GitHub Actions pipelines section of deployments.md."
extra:
  slack_channel: "#dsci-pipelines-stats"
  wiki_instructions: "https://knowledge.base.unocha.org/wiki/spaces/DSCI/pages/4829413383/Instructions+for+manual+updates"
  author: "Hannah Ker (hannah.ker@un.org)"
  python_version: "==3.10.*"
visibility: internal
last_synced: "2026-06-22"
---

# DSCI Slack Bot

> Runbook. Optimize for "what feeds it, what it emits, and what to do when it breaks at 2am."

## One-liner

Monthly (1st of month, 09:00 UTC): post a Slack `@channel` reminder to `#dsci-pipelines-stats` listing the datasets that require manual updates (EM-DAT, CERF Allocations), with links to the wiki instructions.

## Jobs & schedule

| job | ref | schedule | status |
|---|---|---|---|
| Manual Dataset Update Notification | `.github/workflows/dataset-updates.yaml` | `0 9 1 * *` (09:00 UTC on the 1st of every month) | **not deployed** — workflow only exists on `manual-update-notifications` branch, not `main`; GHA crons only fire from the default branch |
| CI | `.github/workflows/ci.yaml` | push/PR to `main` (ruff check + format) | **not deployed** — `ci.yaml` is also only on `manual-update-notifications`, not `main`; it triggers on push/PR to `main` but the file isn't there yet |

> The default branch `main` is effectively empty (`.gitignore` + `README.md` only). All code and both workflows live on `manual-update-notifications`. **Nothing runs in production until that branch is merged.** `ds-slack-bot` is not yet in [infrastructure/deployments.md](../infrastructure/deployments.md) — add it when it goes live.

## Inputs

None. The pipeline takes no data inputs — it sends a static, pre-authored message.

## Steps

GHA runner → `uv sync` → `uv run src/dataset_updates.py` → `slack_sdk.WebClient.chat_postMessage` posts the `@channel` reminder. The message body (EM-DAT + CERF Allocations + wiki links + ✅-when-done instruction) is hardcoded in the script — see [`src/dataset_updates.py`](https://github.com/ocha-dap/ds-slack-bot/blob/manual-update-notifications/src/dataset_updates.py).

## Outputs

- **Slack message** posted to `#dsci-pipelines-stats` — a `@channel` notification listing two datasets for manual update:
  - EM-DAT
  - CERF Allocations
- Instructions link: `https://knowledge.base.unocha.org/wiki/spaces/DSCI/pages/4829413383/Instructions+for+manual+updates`

## Dependencies

| dependency | purpose |
|---|---|
| `slack-sdk>=3.39.0` | Slack Web API client |
| `python-dotenv` | load `.env` for local dev |
| `SLACK_BOT_TOKEN` | GHA secret; Slack bot OAuth token with `chat:write` permission |

No `ocha-stratus`, `ocha-lens`, `ocha-relay`, or database access. No blob storage. Entirely self-contained.

## Failure modes & debugging

**Nothing is deployed (primary risk):** `main` holds only `.gitignore` + `README.md`; all code and both workflows live on `manual-update-notifications`. GitHub Actions scheduled crons only run from the default branch, and `ci.yaml`'s push/PR-to-`main` trigger can't fire because the file isn't on `main` either. Until `manual-update-notifications` is merged to `main`, the monthly reminder never fires automatically and CI never runs.

**`SlackApiError` on send:** The script catches `SlackApiError` and `print()`s the error code. In GHA, this surfaces in the workflow run log. Common causes:
- `SLACK_BOT_TOKEN` secret missing or expired → error `invalid_auth`
- Bot not invited to `#dsci-pipelines-stats` → error `not_in_channel`
- Rate limiting → retry manually or re-run the workflow

**Finding logs:** GitHub Actions → `ds-slack-bot` repo → Actions tab → "Manual Dataset Update Notification" workflow. The `print()` in the except block is the only error signal.

**Local testing:** Set `SLACK_BOT_TOKEN` in a `.env` file and run `uv run src/dataset_updates.py`. The bot must be in the target channel.

## Downstream consumers

No automated downstream consumers. The output is a human-facing Slack reminder that triggers manual operator action (updating EM-DAT and CERF Allocations on Azure blob). The ✅ reactions serve as an informal acknowledgement mechanism.

<!-- TODO: confirm whether EM-DAT and CERF Allocations have their own pipeline pages; if so, link them here as downstream-adjacent context. -->
