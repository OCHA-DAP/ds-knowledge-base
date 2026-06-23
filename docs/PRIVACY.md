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
| **internal** | Source is the team's private working material | **All Google Drive content**, non-public framework docs (e.g. mmr/vut/yem — see `extra.doc_status`), internal notes/decks | **metadata** → public repo; **content** (full text / substantive summary) → the **private store** | metadata ✅ / content ❌ |
| **restricted** | Personal / security / commercially sensitive | HR/personnel, security plans, personal data (PII), unreleased budgets, credentials | omit, or an access-controlled store; **redact even from internal extracts** | ❌ |

## Two layers: metadata vs. the data itself

A second axis cuts across the source classes — separate the **catalog** from the **content**:

- **Metadata / manifest** — title, folder path, type, dates, link, tags, a short non-sensitive descriptor ("what it is"). This says a document **exists** and where — *not what it says*. It is **public, even for internal sources.** (Drive share-links are access-gated, so publishing a link exposes nothing: a public viewer sees "a doc titled X exists" and a link they still can't open without Drive permission.)
- **Content / data** — the full text, and any substantive content-revealing summary. Classified by **source**: public source → public; internal source → **private**.

So for Google Drive: the **manifest is public (committed to this repo); the extracted content is private.** Caveats: strip PII from metadata (no personal emails — coarse/owner-optional); and for **restricted** items where the *existence or title is itself* sensitive, omit even the metadata.

| Layer | Public source | Internal source (e.g. Drive) | Restricted source |
|---|---|---|---|
| **Metadata / manifest** | public (repo) | **public (repo)** | omit |
| **Summary** | public (repo) | short descriptor on the public manifest ok; a substantive summary → private | omit |
| **Full-text / content** | public (repo, `raw/`) | **private store** | omit / redact |

## Where the files live

```
ds-knowledge-base/                       ← PUBLIC repo (git, GitHub Pages)
  frameworks/ pipelines/ apps/ …         curated summaries from PUBLIC sources
  raw/frameworks/<fw>/<version>.txt      full-text of public framework PDFs (greppable)     ← public
  infrastructure/drive-index.md          Drive MANIFEST — metadata only (titles/folders/links/dates)  ← public
  infrastructure/.drive-index.json       machine-readable manifest                          ← public
  docs/PRIVACY.md                        this doc
  .gitignore                             blocks `drive/` so internal CONTENT can't land here

  drive/   ← GITIGNORED — internal CONTENT only, never committed to this public repo
    raw/<…>.txt                          Drive full-text extracts (greppable)               ← internal
    summaries/<…>.md                     substantive internal summaries
```

The **manifest** is the one Drive-derived thing that *is* committed to the public repo — it's metadata (a catalog), not content. The **content store** (`drive/`) = a gitignored local cache (instant grep) **+** a durable copy on blob (`{PROJECT_PREFIX}/processed/drive/…`) and/or a **private** repo for team sharing; it is **never** committed to this public repo (`.gitignore` enforces it). The public repo only gains an actual *content* item when a human **explicitly promotes** a vetted, non-sensitive piece — a deliberate step, never the default.

## Google Drive — the rules

1. **Google Drive _content_ is `internal`; its _metadata_ is public.** The **manifest** (titles/folders/links/dates) is committed to the public repo — it's a catalog of what exists, not the content. The **extracted text and substantive summaries are private** (the internal store), never the public repo. Promoting actual content to public is an explicit, per-item human decision.
2. **Scope — only the Data Science team shared drive.** Do **not** crawl the **data-storage** drive (it's bulk data, not knowledge), and do **not** crawl any other Centre-wide drive your account happens to see.
3. **Exclude `General - All AA projects / Data`** within the DS team shared drive — far too much volume, and it's data not knowledge. Skip it entirely.
4. **Access is via your live Google authorization** (the Drive MCP connector), so it's **interactive / session-bound** — extraction runs in a live session, not a headless cron. The committed/synced extracts are what make querying fast afterwards; refreshes are re-run in a session.
5. **Restricted content stays out** even of the internal store — redact PII/HR/security/budget material rather than extract it.

## Framework docs (the public-source case)

The published framework PDFs are public, so their full-text extracts are **public and belong in-repo** under `raw/frameworks/<fw>/<version>.txt`, with each page's `raw_extract` pointing there. (This refines the earlier "persist to blob" note in DESIGN — blob was chosen when the public/private gate was open; for a *public* source, in-repo greppable text is better and honours "raw is always reachable".) The exception: frameworks whose doc is **non-public** (mmr/vut/yem, flagged `extra.doc_status`) are **internal** — their extracts go to the private store, same as Drive.

## Page-level marker

Every framework/pipeline/app page already carries `visibility: internal | public`. Set it honestly at creation (retrofitting a redaction pass across 100+ pages is exactly what we're avoiding). `public` = safe to publish; default `internal` when unsure. The public site generator (`gen_public_site.py`) is public-safe by construction and never emits `internal`-only fields.
