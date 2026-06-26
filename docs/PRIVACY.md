# Privacy & data classification

How we decide what is **public** vs **internal**, and where each kind of content physically lives. Read this before ingesting any new source — especially Google Drive.

## The one principle

**Classification follows the _source_, not the content type.** A summary and a full-text extract of the *same* document get the *same* classification — what matters is whether the **source** is already public. So:

- A full-text extract of a **published framework PDF** is **public** (the PDF is already on ReliefWeb/unocha — extracting it adds no exposure).
- A one-line summary of an **internal Drive doc** is **internal** (the source is internal; summarising it doesn't make it shareable).

We are **public-by-default for curated knowledge drawn from public sources**, and **internal-by-default for anything drawn from internal sources**. When unsure, classify **internal**.

## Classification: source × layer

Two axes decide where anything goes.

**Source class** — how sensitive the *origin* is:
- **public** — already published / open: framework PDFs (ReliefWeb/unocha), published reports, open datasets, public `ocha-dap` code.
- **internal** — the team's private working material: **all Google Drive content**, non-public framework docs (mmr/vut/yem — see `extra.doc_status`), internal notes/decks.
- **restricted** — personal / security / commercially sensitive: HR, security plans, PII, unreleased budgets, credentials.

**Layer** — the *catalog* vs the *content*:
- **Metadata / manifest** — title, folder, type, dates, link, tags. Says a doc **exists** and where, *not what it says*. A single share-link exposes nothing (access-gated). **But aggregate matters:** the *whole* Drive manifest is ~9k entries of partner/collaboration/project filenames — at that scale the catalog itself is revealing, so the **bulk Drive manifest is internal** even though any *individual* metadata row is low-sensitivity and promotable.
- **Summary** — a curated description.
- **Full-text / content** — the actual text (and any substantive, content-revealing summary).

Where each combination goes:

| Layer ↓  /  Source → | **public** | **internal** (e.g. Drive) | **restricted** |
|---|---|---|---|
| **Metadata / manifest** | ✅ public repo | 🔒 **private repo** (`ds-knowledge-base-internal`); public repo holds a pointer. Per-item rows are promotable. | ⛔ omit |
| **Summary** | ✅ public repo page | 🔒 private repo — a short non-sensitive descriptor may be promoted per-item | ⛔ omit |
| **Full-text / content** | ✅ public repo (`raw/`) | 🔒 **private repo** (`ds-knowledge-base-internal/drive/extracts/`) | ⛔ omit / redact |

The headline: **a manifest is less sensitive than content, but "metadata" ≠ "automatically public" — the bulk Drive manifest is internal (volume + aggregated filenames); only deliberate, per-item promotions go public.** Strip PII from metadata (no personal emails); for *restricted* items where the existence or title is itself sensitive, omit even the metadata.

## Where the files live

```
ds-knowledge-base/                       ← PUBLIC repo (git, GitHub Pages)
  frameworks/ pipelines/ apps/ …         curated summaries from PUBLIC sources
  raw/frameworks/<fw>/<version>.txt      full-text of public framework PDFs (greppable)     ← public
  infrastructure/drive-index.md          POINTER to the private repo (no catalog here)       ← public
  docs/PRIVACY.md                        this doc
  .gitignore                             blocks `drive/` — a safety net; internal lives in the private repo

ds-knowledge-base-internal/              ← PRIVATE repo (access-gated; versioned)
  drive/drive-index.md / drive-index.json   Drive MANIFEST (metadata catalog, ~9k entries)  ← internal
  drive/extracts/<…>.txt                    Drive full-text extracts (greppable, Phase 7c)  ← internal
```

Both the **manifest** and the **content** live in the **private repo** `ds-knowledge-base-internal` — versioned, diffable, and access-controlled (a `git diff` there is the manifest's drift record). Neither is committed to this public repo. Blob is **not** used for this: it's the data-plane tool (rasters/parquet/pipeline outputs), a poor fit for small versioned text. The public repo carries only a **pointer** (`infrastructure/drive-index.md`) and gains an actual Drive item — a metadata row or a content extract — only when a human **explicitly promotes** a vetted, non-sensitive piece: a deliberate step, never the default.

## Google Drive — the rules

1. **Google Drive content _and_ the bulk manifest are `internal`.** The manifest (titles/folders/links/dates, ~9k entries) is a useful catalog but its aggregate of partner/project filenames is more exposure than a public repo should carry, so it lives in the **private repo** `ds-knowledge-base-internal` with the content; the public repo holds only a pointer. Promoting any individual row or extract to public is an explicit, per-item human decision.
2. **Scope — only the Data Science team shared drive.** Do **not** crawl the **data-storage** drive (it's bulk data, not knowledge), and do **not** crawl any other Centre-wide drive your account happens to see.
3. **Exclude `General - All AA projects / Data`** within the DS team shared drive — far too much volume, and it's data not knowledge. The crawler skips that subtree (`EXCLUDE_PATH_SUBSTR`); the rest of the drive is in scope.
4. **Two access paths, by layer.** The **manifest** (metadata) is crawled **headlessly** by `scripts/gen_drive_index.py` using a dedicated **read-only Drive OAuth client** we own (`ocha-ds-kb` project, Internal consent) + the user's Drive ADC — so it's scriptable and **schedulable** (weekly drift `--check`). The **content** layer (per-doc text extraction, Phase 7c) still uses the **interactive** Drive MCP connector (session-bound) — extraction runs in a live session, and the committed/synced extracts make querying fast afterwards.
5. **Restricted content stays out** even of the internal store — redact PII/HR/security/budget material rather than extract it.

## Framework docs (the public-source case)

The published framework PDFs are public, so their full-text extracts are **public and belong in-repo** under `raw/frameworks/<fw>/<version>.txt`, with each page's `raw_extract` pointing there. (This refines the earlier "persist to blob" note in DESIGN — blob was chosen when the public/private gate was open; for a *public* source, in-repo greppable text is better and honours "raw is always reachable".) The exception: frameworks whose doc is **non-public** (mmr/vut/yem, flagged `extra.doc_status`) are **internal** — their extracts go to the private store, same as Drive.

## Page-level marker

Every framework/pipeline/app page already carries `visibility: internal | public`. Set it honestly at creation (retrofitting a redaction pass across 100+ pages is exactly what we're avoiding). `public` = safe to publish; default `internal` when unsure. The public site generator (`gen_public_site.py`) is public-safe by construction and never emits `internal`-only fields.
