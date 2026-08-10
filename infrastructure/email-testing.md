---
content_type: infrastructure
last_reviewed: "2026-08-10"   # bump when a human verifies the page is still accurate
---

# Email pipeline run modes — `TEST_EMAIL` · `SIMULATE_TRIGGER` · `DRY_RUN`

How an email/alerting pipeline should distinguish a production send from a test. Agreed by the team **2026-08-10**. **Advisory and forward-looking**: use it when building a *new* email pipeline (or overhauling one anyway); existing pipelines keep their current idioms — don't retrofit them just for consistency. See [comms-listmonk.md](comms-listmonk.md) for the sending infrastructure itself; new pipelines should send through [ocha-relay](libs/ocha-relay.md), whose library-level safety layer (draft-first campaigns, send confirmation, finished-campaign refusal) complements these flags.

## The three env vars

All email systems going forward use these three boolean env vars:

| var | when `True` |
|---|---|
| `TEST_EMAIL` | Send to a **test distribution list** instead of the real one. Content and volume are otherwise identical to a real run. |
| `SIMULATE_TRIGGER` | **Simulate a trigger firing** — either with dummy data or by replaying a real historical forecast that would have triggered — so the full alert path can be exercised on demand. |
| `DRY_RUN` | **Suppress all email sends**, and if the pipeline logs monitoring records (state files, sent-email records, DB rows — e.g. like Signals), **do not update any records** either. |

In production monitoring, **all three are explicitly set to `False`** in the scheduler config (GHA workflow env / repo `vars.`, or the `databricks.yml` prod target) — see [databricks.md](databricks.md) for the two-axis dev/prod model those configs sit in.

## Recommended implementation practice

The convention is three names and their semantics; the points below are what the 2026-08 survey of our existing pipelines (bottom of page) showed actually goes wrong, and how to avoid it. Take what fits.

**1. Fail safe when unset.** A bare run — no env vars, e.g. someone's laptop or a misconfigured workflow — must not be able to email a real list. Default `TEST_EMAIL=True` and `DRY_RUN=True` when unset; only an explicit `False` in the prod config flips them. (`SIMULATE_TRIGGER` defaults `False` — simulation is always opt-in.) At survey time, half our email pipelines sent to the real list on a bare run (the ⚠️ rows in the table below); the six that fail safe — the env-var pipelines (ds-storms-alerts, ds-rosea-thresholds, hdx-signals) and the SMTP `TEST_LIST` family (hurricanes, HTI, MDG) — have never had an accidental prod send.

**2. Parse strictly, fail loud.** Accept `true/1/yes` and `false/0/no` case-insensitively; anything else should raise, not silently pick a side. Several older pipelines only recognise the exact string `"False"`, so `false`/`FALSE` silently stays in test mode — safe, but confusing to debug. Copyable helper:

```python
import os

def env_flag(name: str, default: bool) -> bool:
    val = os.getenv(name)
    if val is None or not val.strip():
        return default
    v = val.strip().lower()
    if v in ("true", "1", "yes"):
        return True
    if v in ("false", "0", "no"):
        return False
    raise ValueError(f"{name}={val!r} is not a boolean")

TEST_EMAIL = env_flag("TEST_EMAIL", default=True)
SIMULATE_TRIGGER = env_flag("SIMULATE_TRIGGER", default=False)
DRY_RUN = env_flag("DRY_RUN", default=True)
```

(R equivalent: wrap `Sys.getenv` the same way — note bare `as.logical("0")` is `NA`, which errors inside `if()`.)

**3. Log a mode banner.** First thing every run: log the three resolved values (`mode: TEST_EMAIL=True SIMULATE_TRIGGER=False DRY_RUN=True`). When a send does go wrong, the run log should answer "what mode was this?" without archaeology.

**4. Test runs must not touch production state.** `DRY_RUN=True` already means "no record writes" by definition. But a `TEST_EMAIL=True` or `SIMULATE_TRIGGER=True` run that still advances production trigger state — cooldown windows, `last_alert` markers, sent-email records — can silently suppress the *next real alert*, which is worse than a stray test email. Route test-run records to a test location (hdx-signals writes to a `test/` path) or skip them. Two of our pipelines had exactly this leak at survey time.

**5. Tag what actually happened.** Prefix the subject *and* campaign name with `[TEST]` when `TEST_EMAIL=True` and `[SIM]` when `SIMULATE_TRIGGER=True` — keyed to those flags, not to some other switch. (One pipeline keys its `TEST:` tag to the simulation flag rather than the recipient-list flag, so a real-list send can be tagged as test and vice versa.) A test email that is indistinguishable in an inbox from a real one defeats the point of a test list.

On Listmonk, tag the campaign **name**, not just the subject — the shared OCHA template branches on the name, giving test sends a red in-body TEST banner for free; an untagged test send renders exactly like production. Mechanism and the other name-triggered variants: [comms-listmonk.md](comms-listmonk.md#template-branching-on-the-campaign-name).

**6. A simulation to a real list must be deliberate.** `SIMULATE_TRIGGER=True` with `TEST_EMAIL=False` and `DRY_RUN=False` delivers a fabricated activation to real recipients. That combination *is* legitimate in very specific tests (e.g. a full end-to-end drill where the real audience is meant to receive it) — but it should never be reachable by accident. Don't let the two flags alone produce it: gate it behind an extra explicit step. In an *interactive* run, ocha-relay's typed-campaign-name confirmation is that step. In a *scheduled or dispatched* run it can't be — the prompt is `input()`-based and headless jobs set `skip_confirmation=True` (see [libs/ocha-relay](libs/ocha-relay.md)) — so use a dedicated second opt-in there (e.g. an `ALLOW_REAL_SIMULATION` env var or a separate `workflow_dispatch` input that is never set in any stored config). Either way, a stray flag combination alone must not be able to fabricate an activation for a live list.

**7. Precedence: `DRY_RUN` wins.** Whatever the other two say, `DRY_RUN=True` means nothing leaves the pipeline and nothing is recorded.

### Mode matrix

| `TEST_EMAIL` | `SIMULATE_TRIGGER` | `DRY_RUN` | meaning |
|---|---|---|---|
| `False` | `False` | `False` | **Production monitoring** — set explicitly in the scheduler config. |
| `True` | `False` | `False` | End-to-end rehearsal on real data; email goes to the test list. |
| `True` | `True` | `False` | Full trigger simulation delivered to the test list — the standard "does the alert email actually work" check. |
| — | `True` | `True` | Exercise the trigger path offline; nothing sent, nothing recorded. |
| — | — | `True` | Offline run; `DRY_RUN` overrides everything else. |
| `False` | `True` | `False` | Real-list drill — allowed only in very specific tests, behind an extra explicit confirmation (see point 6). |

### Where prod flips the switches

Keep the explicit `False`s in version-controlled or at least discoverable config, with any fallback chain ending on the *safe* value:

- **GHA:** `TEST_EMAIL: ${{ inputs.test_email || vars.TEST_EMAIL || 'True' }}` — manual dispatch input first, repo variable second, safe default last. Scheduled cron runs pick up the repo variable. **Declare the dispatch input `type: string`, not `boolean`**: in GHA expressions a boolean `false` is falsy, so the `||` chain silently discards an operator's explicit `false` and falls through to the repo var — exactly the "silently pick a side" behavior point 2 forbids. A string `"false"` is truthy and survives the chain.
- **Databricks (DAB):** flag variables with safe defaults at the top of `databricks.yml`, overridden to `"False"` only in `targets.prod.variables` (ds-storms-alerts does exactly this).

A prod/test switch that lives *only* in a GitHub repo variable with no in-code default is invisible when reading the source — always keep the in-code fail-safe default as the backstop.

## Current alignment (survey, 2026-08-10)

Snapshot of every email-sending pipeline at the time the convention was agreed. None of these are being retrofitted; this is the baseline the convention was designed against. "Bare run" = no env vars/flags set.

| repo | sends via | test-list switch | dry-run | simulate trigger | bare run is… |
|---|---|---|---|---|---|
| [ds-storms-alerts](../pipelines/storms-alerts.md) | Listmonk (ocha-relay) | `TEST_EMAIL` ✅ (default True) | `DRY_RUN` ✅ (default True) | `--issued-time` historical replay; `--send-test` | ✅ safe |
| [ds-rosea-thresholds](../pipelines/rosea-thresholds-monitoring.md) | Listmonk | `TEST_EMAIL` ✅ (default True) | — (test list is the fallback) | `FORCE_TRIGGER` env | ✅ safe |
| [hdx-signals](../pipelines/hdx-signals.md) | Mailchimp | archive-segment (fn arg) | `GMAS_TEST_RUN` (default TRUE; also gates record writes + OpenAI calls) | `first_run` fn arg | ✅ safe |
| [ds-hurricanes-monitoring](../pipelines/hurricanes-monitoring.md) | SMTP | `TEST_LIST` (default test; only exact `"False"` disables) | — | `TEST_STORM` (default True) injects historical storm | ✅ safe, but test rows land in prod `email_record.csv` |
| [ds-aa-hti-hurricanes](../pipelines/hti-hurricanes-monitoring.md) | SMTP | `TEST_LIST` (default test) | — | `TEST_STORM` forces full readiness+action activation | ✅ safe, same email-record leak |
| [ds-aa-mdg-monitoring](../pipelines/mdg-monitoring.md) | SMTP | `TEST_LIST` (default test) | — | `--date` replay | ✅ safe; no `[TEST]` subject tag; checked-in `.env` overrides shell locally |
| [ds-storm-impact-harmonisation](../pipelines/storm-impact-harmonisation.md) (GDACS monitor) | Listmonk (ocha-relay) | ❌ none — `--list-id` override only (default = real monitoring list 101); all sends currently hard-tagged `[test]` | `--dry-run` CLI (HTML to disk, no Listmonk call); `--inspect` (draft + manifest + preview, no send) | — | ⚠️ targets the real list, but ocha-relay's typed-name confirmation blocks a headless send unless `--auto-send` (which the cron passes) |
| [ds-aa-ken-drought-monitoring](../pipelines/ken-drought-monitoring.md) | Listmonk (ocha-relay) | `--test` CLI (default **real list**) | `--no-email` CLI | `--year`/`--month` replay | ⚠️ real send (dispatch-only workflow) |
| [ds-aa-eth-drought-monitoring](../pipelines/eth-drought-monitoring.md) | Listmonk (ocha-relay) | `--test` CLI (default **real list**) | `--no-email` CLI | `--year`/`--month` replay | ⚠️ real send, on cron |
| [ds-aa-moz-cholera-monitoring](../pipelines/moz-cholera-monitoring.md) | Listmonk (ocha-relay) | `--test` CLI (default **real list**) | `--no-email` CLI | `--force`, `--filename` | ⚠️ real send; state blob (cooldowns) written even on `--test`/`--no-email` runs |
| [ds-aa-moz-cyclones-monitoring](../pipelines/moz-cyclones-monitoring.md) | SMTP | ❌ hardcoded off (see pipeline page) | — | — | ⚠️ real send, hourly cron |
| [ds-afro-cholera](../pipelines/afro-cholera.md) | Listmonk (R) | ❌ none (list id hardcoded; test path is dead code) | — | — | ⚠️ real send, daily cron; `last_alerts.csv` always committed |
| [ds-fms-tc-outlook](../pipelines/fms-tc-outlook.md) | Listmonk | ❌ none (list id hardcoded) | — | — (emails every run, no trigger condition) | ⚠️ real send, daily cron |
| [ds-nga-flood-monitoring](../pipelines/nga-flood-monitoring.md) | SMTP (blastula) | ❌ none | — | — | ⚠️ real send if SMTP creds present |

Not email pipelines (checked, nothing to align): ds-aa-bgd-cyclone-monitoring (Shiny dashboard), ds-floodexposure-monitoring (DB writes only; `STAGE` env), ds-seasonal-bulletin (marimo app), ds-flash-floods (empty repo at survey time).

**[ocha-relay](libs/ocha-relay.md)** (the library) deliberately reads none of these vars — list routing is the calling repo's job. Five of the pipelines above send through it (ds-storms-alerts, the GDACS monitor, KEN, ETH, MOZ-cholera); the rest use raw Listmonk clients or SMTP. Its own safety layer is orthogonal and complementary: campaigns are created as drafts, `send_campaign` requires typing the campaign name back (or explicit `skip_confirmation=True` for scheduled runs), and re-sending a finished campaign is refused unconditionally. A shared `env_flag`-style helper would be a natural future addition to ocha-relay. <!-- TODO: if a third repo copies the env_flag helper, promote it into ocha-relay -->

### Hazards worth knowing even if you never touch this page's convention

- **ds-aa-moz-cyclones-monitoring** cannot be put in test mode without a code edit — the test switch is hardcoded off; details on [the pipeline page](../pipelines/moz-cyclones-monitoring.md).
- **ds-aa-moz-cholera-monitoring** and **ds-afro-cholera** advance real alert/cooldown state on *every* run, including test runs — a careless test can suppress the next genuine alert.
- **ds-storms-alerts**: the no-exposure "monitoring" email branch picks the real `aggregate:monitoring` lists *before* checking `TEST_EMAIL`, so `TEST_EMAIL=True, DRY_RUN=False` can still send a (tagged) email to real monitoring lists.
