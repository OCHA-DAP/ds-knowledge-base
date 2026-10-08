"""Databricks entrypoint for the `KB DB Snapshot` job (databricks.yml).

Runs the KB's database-reading generators unchanged, then parks their output on
the dev blob for the GitHub workflows (which can't reach the database):

  1. scripts/gen_db_schema.py --stage prod   -> infrastructure/db-schema.md + .db-tables.json
  2. scripts/gen_db_schema.py --stage dev    -> infrastructure/db-schema-dev.md + .db-tables-dev.json
  3. scripts/analyze_usage.py --stage dev --days 30 --report usage-digest.md
     (exit 2 = actionable signals; recorded in the manifest, never a failure here)
  4. scripts/db_snapshot_blob.py upload      -> projects/ds-knowledge-base/db-snapshot/latest/

The scripts are copied off the workspace git checkout onto local disk first
(importing straight off the FUSE mount is unreliable) and run with the same
interpreter. Credentials come from the Job Compute policy (dsci secret scope).
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

USAGE_DAYS = 30


def _checkout_root() -> Path:
    """spark_python_task's exec context doesn't reliably define __file__."""
    hints = []
    try:
        hints.append(Path(__file__).resolve())  # noqa: F821
    except NameError:
        pass
    if sys.argv and sys.argv[0]:
        hints.append(Path(sys.argv[0]).resolve())
    hints.append(Path.cwd())
    for h in hints:
        for d in [h, *h.parents]:
            if (d / "scripts" / "gen_db_schema.py").is_file():
                return d
    raise SystemExit(f"cannot find the repo root from {[str(h) for h in hints]}")


def main() -> None:
    for v in ("DSCI_AZ_DB_PROD_HOST", "DSCI_AZ_DB_DEV_HOST", "DSCI_AZ_BLOB_DEV_SAS_WRITE"):
        if not os.environ.get(v):
            sys.exit(f"{v} is not set — the Job Compute policy should inject the dsci secrets")

    src = _checkout_root()
    base = Path("/local_disk0" if Path("/local_disk0").is_dir() else tempfile.gettempdir())
    root = base / "kb_snapshot_run"
    shutil.rmtree(root, ignore_errors=True)
    shutil.copytree(src / "scripts", root / "scripts", ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    out = root / "infrastructure"
    out.mkdir()

    def run(*args, ok=(0,)):
        cmd = [sys.executable, *args]
        print("+", " ".join(str(a) for a in cmd), flush=True)
        rc = subprocess.run(cmd, cwd=root).returncode
        if rc not in ok:
            sys.exit(f"{args[0]} exited {rc}")
        return rc

    run("scripts/gen_db_schema.py", "--stage", "prod")
    run("scripts/gen_db_schema.py", "--stage", "dev")
    usage_exit = run("scripts/analyze_usage.py", "--stage", "dev", "--days", str(USAGE_DAYS),
                     "--report", str(out / "usage-digest.md"), ok=(0, 2))
    if not (out / "usage-digest.md").is_file():  # analyze_usage exits 0 without a report on an empty window
        (out / "usage-digest.md").write_text(f"# KB usage digest — last {USAGE_DAYS} days\n\n_no events in the window_\n")

    (out / "manifest.json").write_text(json.dumps({
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "usage_exit": usage_exit,
        "usage_days": USAGE_DAYS,
        "files": sorted(p.name for p in out.iterdir()),
    }, indent=1))
    run("scripts/db_snapshot_blob.py", "upload", "--from", str(out))


if __name__ == "__main__":
    main()
