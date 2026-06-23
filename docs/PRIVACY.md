# Privacy & data classification

How we decide what is **public** vs **internal**, and where each kind of content physically lives. Read this before ingesting any new source — especially Google Drive.

## The one principle

**Classification follows the _source_, not the content type.** A summary and a full-text extract of the *same* document get the *same* classification — what matters is whether the **source** is already public. So:

- A full-text extract of a **published framework PDF** is **public** (the PDF is already on ReliefWeb/unocha — extracting it adds no exposure).
- A one-line summary of an **internal Drive doc** is **internal** (the source is internal; summarising it doesn't make it shareable).

We are **public-by-default for curated knowledge drawn from public sources**, and **internal-by-default for anything drawn from internal sources**. When unsure, classify **internal**.

## The three classes

| Class | What it is | Examples | Lives in | In the public repo? |
|---|---|---|---|---|
| **public** | Source is already published / open | Framework PDFs (ReliefWeb/unocha), published reports, open datasets, the code in public `ocha-dap` repos | the **public** `ds-knowledge-base` repo — summary page **and** full-text extract (`raw/…`) | ✅ |
| **internal** | Source is the team's private working material | **All Google Drive content**, non-public framework docs (e.g. mmr/vut/yem — see `extra.doc_status`), internal notes/decks | the **private store** (see below) — never the public repo | ❌ |
| **restricted** | Personal / security / commercially sensitive | HR/personnel, security plans, personal data (PII), unreleased budgets, credentials | omit, or an access-controlled store; **redact even from internal extracts** | ❌ |

## Where everything goes (placement)

```
ds-knowledge-base/                       ← PUBLIC repo (git, GitHub Pages)
  frameworks/ pipelines/ apps/ …         curated summaries from PUBLIC sources
  raw/frameworks/<fw>/<version>.txt      full-text of the public framework PDF (greppable)  ← public
  docs/PRIVACY.md                        this doc
  .gitignore                             blocks `drive/` so internal content can't be committed here

  drive/   ← GITIGNORED — INTERNAL, never committed to this public repo
    index.md | index.jsonl               the Drive manifest (titles/folders/links/dates)   ← internal
    raw/<…>.txt                          Drive full-text extracts (greppable)              ← internal
    summaries/<…>.md                     internal summaries
```

The **internal store** = a gitignored local `drive/` cache (instant local grep) **+** a durable copy on blob (`{PROJECT_PREFIX}/processed/drive/…`) and/or a **private** repo for team sharing. It is **never** the public `ds-knowledge-base` repo. `.gitignore` enforces this so an internal extract can't be committed to the public repo by accident.

Note: because **all** Drive-derived material is internal, the Drive **manifest is internal too** — it is *not* published. The public repo only gains Drive-derived content when a human **explicitly promotes** a vetted, non-sensitive summary (a deliberate step, never the default).

## Google Drive — the rules

1. **Everything from Google Drive is `internal`.** Manifest, extracts, and summaries all live in the private store, not the public repo. Promotion to public is an explicit, per-item human decision.
2. **Scope — only the Data Science team shared drive.** Do **not** crawl the **data-storage** drive (it's bulk data, not knowledge), and do **not** crawl any other Centre-wide drive your account happens to see.
3. **Exclude `General - All AA projects / Data`** within the DS team shared drive — far too much volume, and it's data not knowledge. Skip it entirely.
4. **Access is via your live Google authorization** (the Drive MCP connector), so it's **interactive / session-bound** — extraction runs in a live session, not a headless cron. The committed/synced extracts are what make querying fast afterwards; refreshes are re-run in a session.
5. **Restricted content stays out** even of the internal store — redact PII/HR/security/budget material rather than extract it.

## Framework docs (the public-source case)

The published framework PDFs are public, so their full-text extracts are **public and belong in-repo** under `raw/frameworks/<fw>/<version>.txt`, with each page's `raw_extract` pointing there. (This refines the earlier "persist to blob" note in DESIGN — blob was chosen when the public/private gate was open; for a *public* source, in-repo greppable text is better and honours "raw is always reachable".) The exception: frameworks whose doc is **non-public** (mmr/vut/yem, flagged `extra.doc_status`) are **internal** — their extracts go to the private store, same as Drive.

## Page-level marker

Every framework/pipeline/app page already carries `visibility: internal | public`. Set it honestly at creation (retrofitting a redaction pass across 100+ pages is exactly what we're avoiding). `public` = safe to publish; default `internal` when unsure. The public site generator (`gen_public_site.py`) is public-safe by construction and never emits `internal`-only fields.
