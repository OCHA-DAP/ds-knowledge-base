---
content_type: infrastructure
last_reviewed: "2026-07-10"   # bump when a human verifies the page is still accurate
---

# Confluence archive — pointer (the content is in the private repo)

The team's old **DSCI Confluence space**
(`knowledge.base.unocha.org/wiki/spaces/DSCI`) has been archived in full and is
no longer used. Confluence is an **internal** source, so per
[docs/PRIVACY.md](../docs/PRIVACY.md) (classification follows the source) the
archive lives in the **private companion repo**:

**→ [`OCHA-DAP/ds-knowledge-base-internal`](https://github.com/OCHA-DAP/ds-knowledge-base-internal)** · `confluence/confluence-index.md` (+ `confluence-index.json`)

What's there: a one-shot snapshot (fetched 2026-07-10) of all **132 pages**
(127 current + 5 archived) as markdown mirroring the page tree, with
frontmatter (id, url, dates, author, labels), page **comments**, all **120
attachments** (image links rewritten to local copies), and the canonical
storage-format XML bodies as a fidelity backup. Fetched by
`scripts/fetch_confluence_archive.py` (in the private repo) — a one-shot
script, deliberately **not** wired into sync/drift automation.

Much of the archived content is superseded by pages in this KB (Databricks,
Postgres schema, pipelines, COG standards…). The archive exists for
completeness: if a fact turns out to live only there, promote/ingest it into
the right KB page per-item — don't link Confluence.
