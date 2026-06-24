#!/usr/bin/env python3
"""Push the INTERNAL Drive manifest to Azure blob — a durable second copy.

The manifest (`drive/.drive-index.json` + `drive/drive-index.md`) is internal and
gitignored, so it only lives on the machine that crawled. This mirrors it to blob
at `ds-knowledge-base/processed/drive/` (the team `processed/` convention) so it
survives a laptop wipe. The blob container is internal — consistent with the
manifest's classification (docs/PRIVACY.md D44b).

Run with the KB repo venv (it has `ocha-stratus`; the crawl venv does not):
    .venv/bin/python scripts/drive_index_to_blob.py [--stage dev|prod]

Default stage is `dev` (the write SAS we have is `DSCI_AZ_BLOB_DEV_SAS_WRITE`).
The crawl writes locally; this uploads — refresh = run the crawl, then this.
"""
from __future__ import annotations
import sys
from pathlib import Path

import ocha_stratus as stratus

ROOT = Path(__file__).resolve().parent.parent
PREFIX = "ds-knowledge-base"          # no src.constants in this repo; KB's own prefix
DEST = f"{PREFIX}/processed/drive"
STAGE = "dev"
if "--stage" in sys.argv:
    STAGE = sys.argv[sys.argv.index("--stage") + 1]

# (local path, blob basename, content-type)
FILES = [
    (ROOT / "drive" / ".drive-index.json", "drive-index.json", "application/json"),
    (ROOT / "drive" / "drive-index.md", "drive-index.md", "text/markdown"),
]


def main():
    missing = [str(p) for p, _, _ in FILES if not p.exists()]
    if missing:
        sys.exit("Manifest not found (run scripts/gen_drive_index.py first): "
                 + ", ".join(missing))
    for path, name, ctype in FILES:
        blob_name = f"{DEST}/{name}"
        stratus.upload_blob_data(path.read_bytes(), blob_name, stage=STAGE,
                                 content_type=ctype)
        print(f"  ↑ {blob_name}  ({path.stat().st_size // 1024} KB, {STAGE})")
    print(f"uploaded to {STAGE} blob: {DEST}/")


if __name__ == "__main__":
    main()
