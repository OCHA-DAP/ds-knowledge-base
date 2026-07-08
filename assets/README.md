# assets/

**Data asset catalog** — what data we actually have in blob storage, and whether it is fit for purpose.

This is distinct from:
- `infrastructure/blob-inventory.md` (structural map: which prefixes exist, file counts, sizes) — the file-system listing
- `infrastructure/datasets/<name>.md` (source metadata: what a dataset *is*, its resolution/CRS/licensing) — the dataset reference
- `pipelines/` (how data gets there) — the operational layer

An `assets/` page answers: *"what do we have stored for this project and dataset, and is the coverage sufficient?"* — gauge stations, year ranges, leadtime windows, gaps.

## Structure

One subfolder per project prefix (matching the blob `PROJECT_PREFIX`), one page per datasource within it.

```
assets/
  <project-prefix>/
    <datasource>.md     ← generated coverage report
```

## How pages are generated

Run `scripts/gen_blob_inventory.py` with `--write` for the relevant project and datasource. Pages are regenerated on demand (not on a fixed schedule — run when you need a fresh snapshot or after a large ingest).

## Cross-links

Asset pages are linked from:
- The framework or analysis page for the same project (`frameworks/<fw>/` or `analysis/<fw>.md`)
- The pipeline page that ingests or produces the data (`pipelines/<pipeline>.md`)
