---
content_type: infrastructure
last_reviewed: "2026-07-02"   # bump when a human verifies the page is still accurate
---

# Usage telemetry — closing the feedback loop

The KB's three self-maintenance axes (generators, drift, discovery — see
[automation.md](automation.md)) all watch *the KB and the outside world*. **None of them
watch how people actually use it.** This is the fourth axis: **Usage** — instrument access,
analyse it, and route what we learn back into improving the KB and the MCP.

The goal: keep the whole thing continually streamlined, so people can get answers as easily
as possible.

## How it works

```
every MCP tool call ──▶ kb_usage.events ──▶ analyze_usage.py ──▶ kb-usage issue ──▶ (human ▸ kb-ingest) ──▶ PR
 (chatbot · claude.ai      (Postgres)         (weekly digest)        (review)
  connectors · direct)
```

1. **One hook catches every access path.** A FastMCP middleware (`mcp_server/usage.py`,
   wired in `server.py`) records one row per tool call. Because the chatbot, the claude.ai
   connectors, and any direct client all go through the same MCP tools, this single hook
   sees everything. Per call: timestamp, tier (`public`/`internal`), tool, a truncated
   **arg summary** (the query / path / SQL), result size, an **empty-result flag**,
   latency, and ok/error.
2. **It lands in Postgres** (`kb_usage.events`), so the analysis is just SQL — and you can
   even introspect it through the chatbot itself (`run_sql` against the same table).
3. **Weekly digest** (`scripts/analyze_usage.py` + `usage-review.yml`) surfaces the signals
   that drive improvement and maintains a single **`kb-usage`** tracking issue.

## What it surfaces (and what each signal means)

| Signal | What it tells you | The fix |
|---|---|---|
| **🔍 Searches that found nothing** | what people look for and *don't* find — the single highest-value signal | a missing/expanded page, a clearer **title**, or a **search synonym/alias** so the existing page is findable |
| **Most-read pages** | what's working / load-bearing | deepen, keep fresh, promote |
| **Top SQL shapes** (internal) | recurring analyses people hand-write | a pre-built **recipes** page, or a higher-level MCP tool |
| **Tool error % / errors** | MCP usability bugs | fix the tool, its description, or a tripping default |
| **p95 latency per tool** | slow paths | optimise or cache |

Findings route to **both** targets: KB-organisation fixes (pages, cross-links, synonyms,
titles) and MCP-behaviour fixes (tool descriptions, a convenience tool, better defaults).

## Digest-first, then automate

Today the loop is **digest-first**: the workflow opens/updates the `kb-usage` issue and a
human decides what to ingest. Once the signal is trusted, flip on auto-drafting by
dispatching `kb-ingest.yml` from the actionable items (the same detect→fix→PR loop the
[drift](automation.md) and discovery axes already use) — Claude never writes to `main`.

## Privacy

The internal tier's query text can be sensitive, so it lives **only in the DB** — never in
this public repo. Only the *aggregated* digest (themes, counts) is public-safe. The public
tier sees public-KB queries only. See [docs/PRIVACY.md](../docs/PRIVACY.md).

## Enabling it (one-time)

Telemetry **no-ops gracefully** until switched on — shipping the instrumentation is
harmless on its own.

1. **DB:** apply [`mcp_server/deploy/usage_schema.sql`](../mcp_server/deploy/usage_schema.sql)
   to the **dev** DB (a DB admin — it creates the `kb_usage` schema, the table, and a
   least-privilege **INSERT-only** role `kb_usage_writer`). Grant the standard read role
   `SELECT` so the workflow can aggregate it.
2. **MCP apps:** set `KB_USAGE_TIER` (`internal` on `chd-ds-kb-mcp-internal`, `public` on
   `chd-ds-kb-mcp`) and `KB_USAGE_DB_URL` (the `kb_usage_writer` connection string).
3. The `usage-review` workflow already has the DSCI read secrets; it starts producing the
   digest on the next Monday run (or `workflow_dispatch`).

### Why a separate write credential

The internet-facing MCP holds **read-only** DB creds by design (so the agent/sandbox can't
write). Telemetry needs to write — so it uses a **dedicated, least-privilege** role that can
*only* `INSERT` into `kb_usage.events`. Even a full env leak on the MCP box can therefore
only append telemetry rows; the broad `DSCI_AZ_*_WRITE` creds never touch that box. This
keeps the read-only posture intact while still capturing usage.

> ⚠️ **Interim state (2026-07-02):** `KB_USAGE_DB_URL` on both apps currently carries the
> standard **`dbwriter`** login, *not* the INSERT-only role — creating `kb_usage_writer`
> needs `CREATEROLE`, which no available login has (dbwriter lacks it; the flexible-server
> `chdadmin` password isn't held by the team). Telemetry is live, but the least-privilege
> claim above does **not** hold yet. **To fix:** whoever recovers/resets the admin
> credential runs `mcp_server/deploy/enable_usage.py` — it creates the role and swaps both
> apps' URL in one pass (idempotent).
