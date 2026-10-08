#!/usr/bin/env python3
"""Move the KB's database-derived snapshot between a checkout and the dev blob.

The database is reachable only through its private endpoint (2026-09-30), so the
generators that read it run in the `KB DB Snapshot` Databricks job
(`databricks/kb_snapshot.py`, `databricks.yml`) and park their output here:

    dev `projects` container, prefix ds-knowledge-base/db-snapshot/latest/

        db-schema.md · db-schema-dev.md · .db-tables.json · .db-tables-dev.json
        usage-digest.md · manifest.json  (generated_at, usage_exit, usage_days)

`db-schema.yml` and `usage-review.yml` download from there (curl + the org read
SAS; no Python dependency), this script is the same thing for a laptop or the job:

    python scripts/db_snapshot_blob.py upload   [--from DIR]   # Databricks job
    python scripts/db_snapshot_blob.py download [--to DIR] [--max-age-hours 36]

Credentials: ocha-stratus — `DSCI_AZ_BLOB_DEV_SAS_WRITE` to upload (the Job Compute
policy injects it), `DSCI_AZ_BLOB_DEV_SAS` to download.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTAINER = "projects"
PREFIX = "ds-knowledge-base/db-snapshot/latest"
SCHEMA_FILES = ["db-schema.md", "db-schema-dev.md", ".db-tables.json", ".db-tables-dev.json"]
FILES = SCHEMA_FILES + ["usage-digest.md", "manifest.json"]


def upload(src: Path) -> None:
    import ocha_stratus as stratus

    missing = [f for f in FILES if not (src / f).is_file()]
    if missing:
        sys.exit(f"refusing to upload a partial snapshot — missing {missing} in {src}")
    client = stratus.get_container_client(CONTAINER, stage="dev", write=True)
    for f in FILES:
        client.upload_blob(f"{PREFIX}/{f}", (src / f).read_bytes(), overwrite=True)
    print(f"uploaded {len(FILES)} files to {CONTAINER}/{PREFIX}/")


def download(dst: Path, max_age_hours: float) -> None:
    import ocha_stratus as stratus

    client = stratus.get_container_client(CONTAINER, stage="dev")
    dst.mkdir(parents=True, exist_ok=True)
    for f in FILES:
        (dst / f).write_bytes(client.download_blob(f"{PREFIX}/{f}").readall())
    check_manifest(dst / "manifest.json", max_age_hours)
    print(f"downloaded {len(FILES)} files into {dst}")


def check_manifest(path: Path, max_age_hours: float) -> dict:
    """Fail loudly when the snapshot is stale: a stopped Databricks job must show up
    as a red row on kb-health, not as a silently frozen schema page."""
    m = json.loads(path.read_text())
    generated = datetime.fromisoformat(m["generated_at"])
    age_h = (datetime.now(timezone.utc) - generated).total_seconds() / 3600
    if age_h > max_age_hours:
        sys.exit(f"snapshot is {age_h:.0f}h old (generated {m['generated_at']}) — "
                 f"is the `KB DB Snapshot` Databricks job running?")
    print(f"snapshot generated {m['generated_at']} ({age_h:.1f}h ago), usage_exit={m.get('usage_exit')}")
    return m


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("action", choices=["upload", "download", "check"])
    ap.add_argument("--from", dest="src", default=None, help="upload: directory holding the files")
    ap.add_argument("--to", dest="dst", default=None, help="download: target directory")
    ap.add_argument("--max-age-hours", type=float, default=36)
    a = ap.parse_args()
    if a.action == "upload":
        upload(Path(a.src) if a.src else ROOT / "infrastructure")
    elif a.action == "download":
        download(Path(a.dst) if a.dst else ROOT / "infrastructure", a.max_age_hours)
    else:
        check_manifest(Path(a.dst or ".") / "manifest.json", a.max_age_hours)


if __name__ == "__main__":
    main()
