"""Read-only infrastructure tools: Postgres (SELECT-only) and blob reads.

All access goes through `ocha-stratus` with the read role — never the `_WRITE`
credentials, never raw psycopg2/Azure SDK. This mirrors scripts/gen_db_schema.py.

Defense in depth: the DB read role is the real protection, and on top of it
`validate_select` rejects anything but a single SELECT/WITH, a statement_timeout
bounds runtime, and results are row-capped so one call can't drain a table into a
transcript. These tools are only registered by the server when KB_MCP_ENABLE_INFRA
is set — keep them off until the endpoint is behind auth (see README).
"""
from __future__ import annotations

import os
import re

# Hard server-side ceilings — these bound result size + runtime regardless of what a
# caller passes, so the "can't drain a table" guarantee doesn't depend on the client.
_MAX_ROWS = 10_000
_MAX_TIMEOUT_S = 60

# Standalone write/DDL/transaction keywords. \b avoids matching inside identifiers
# like `update_time` (underscore is a word char). The read role is the real guard;
# this is belt-and-suspenders against an accidental data-modifying CTE.
_FORBIDDEN = re.compile(
    r"\b(insert|update|delete|drop|alter|create|truncate|grant|revoke|copy|merge|"
    r"call|do|vacuum|analyze|reindex|cluster|comment|lock|set|reset|begin|commit|"
    r"rollback|savepoint|prepare|execute|listen|notify)\b",
    re.IGNORECASE,
)


def _strip_sql_comments(q: str) -> str:
    q = re.sub(r"--[^\n]*", "", q)
    q = re.sub(r"/\*.*?\*/", "", q, flags=re.DOTALL)
    return q


def _mask_literals(q: str) -> str:
    """Blank out string-literal and quoted-identifier contents so the keyword scan
    can't false-positive on data, e.g. WHERE note = 'do not delete'."""
    q = re.sub(r"'(?:[^']|'')*'", "''", q)
    q = re.sub(r'"(?:[^"]|"")*"', '""', q)
    return q


def validate_select(query: str) -> str:
    """Return a cleaned single SELECT/WITH statement, or raise ValueError.

    Pure-Python and credential-free, so it's unit-testable on its own.
    """
    cleaned = _strip_sql_comments(query).strip()
    if not cleaned:
        raise ValueError("Empty query.")
    body = cleaned.rstrip(";").strip()
    if ";" in body:
        raise ValueError("Only a single statement is allowed (no ';').")
    first = body.split(None, 1)[0].lower() if body.split() else ""
    if first not in ("select", "with"):
        raise ValueError("Only read queries are allowed (must start with SELECT or WITH).")
    bad = _FORBIDDEN.search(_mask_literals(body))
    if bad:
        raise ValueError(f"Query contains a forbidden keyword: {bad.group(0).upper()}.")
    return body


def run_sql(query: str, stage: str = "prod", row_limit: int = 1000, timeout_s: int = 15) -> str:
    """Run a SELECT/WITH query against Postgres (read-only) and return the rows.

    `stage` is 'prod' or 'dev'. Results are capped at `row_limit` and the query is
    bounded by a statement timeout. See the 'db-schema' index for the schema.
    """
    if stage not in ("prod", "dev"):
        return "stage must be 'prod' or 'dev'."
    try:
        body = validate_select(query)
    except ValueError as e:
        return f"Rejected: {e}"

    try:
        import ocha_stratus as stratus
        from sqlalchemy import text
    except ImportError:
        return "Server missing ocha-stratus + sqlalchemy."

    # Hard ceilings, applied regardless of caller input (the cap can't be a no-op).
    row_limit = max(1, min(int(row_limit), _MAX_ROWS))
    timeout_s = max(1, min(int(timeout_s), _MAX_TIMEOUT_S))
    os.environ.setdefault("PGSSLMODE", "require")
    try:
        engine = stratus.get_engine(stage=stage)  # read role (write defaults False)
        with engine.connect() as conn:
            conn.execute(text(f"SET statement_timeout = {timeout_s * 1000}"))
            # Run the query as-is (no SELECT * FROM (...) wrapper — that breaks duplicate
            # output columns / some WITH…SELECT *). Stream + fetch one extra row so memory
            # is bounded to row_limit+1 even if the query has no LIMIT of its own.
            result = conn.execution_options(stream_results=True).execute(text(body))
            cols = list(result.keys())
            rows = result.fetchmany(row_limit + 1)
    except Exception as e:  # noqa: BLE001 — surface the cause to the model, don't crash the tool
        return (f"Query failed ({type(e).__name__}: {e}). "
                "Check the query against the 'db-schema' index.")

    if not rows:
        return "0 rows."
    capped = len(rows) > row_limit
    rows = rows[:row_limit]
    header = " | ".join(cols)
    sep = "-" * len(header)
    body_lines = [" | ".join("" if v is None else str(v) for v in r) for r in rows]
    note = f"\n\n({len(rows)} rows" + (f"; capped at {row_limit}" if capped else "") + ")"
    return "\n".join([header, sep, *body_lines]) + note


def list_blobs(prefix: str, stage: str = "prod", container: str = "projects",
               max_results: int = 200) -> str:
    """List blob names under `prefix` in a container ('projects'/'raster'/'polygon'/'global')."""
    try:
        import ocha_stratus as stratus
    except ImportError:
        return "Server missing ocha-stratus."
    try:
        names = list(stratus.list_container_blobs(
            name_starts_with=prefix, stage=stage, container_name=container))
    except Exception as e:  # noqa: BLE001
        return f"Listing failed ({type(e).__name__}: {e})."
    if not names:
        return f"No blobs under {prefix!r} in {container} ({stage})."
    shown = names[:max_results]
    out = "\n".join(shown)
    if len(names) > max_results:
        out += f"\n… +{len(names) - max_results} more"
    return out


def read_blob(blob_name: str, stage: str = "prod", container: str = "projects",
              n_rows: int = 20) -> str:
    """Return shape + a head preview of a tabular blob (.parquet or .csv)."""
    try:
        import ocha_stratus as stratus
    except ImportError:
        return "Server missing ocha-stratus."
    try:
        if blob_name.endswith(".parquet"):
            df = stratus.load_parquet_from_blob(blob_name, stage=stage, container_name=container)
        elif blob_name.endswith(".csv"):
            df = stratus.load_csv_from_blob(blob_name, stage=stage, container_name=container)
        else:
            return "Only .parquet and .csv blobs are previewable here."
    except Exception as e:  # noqa: BLE001
        return f"Read failed ({type(e).__name__}: {e})."
    head = df.head(n_rows)
    # Cap columns + cell width too (not just rows) so a wide blob can't balloon the
    # transcript or get unpredictably truncated by the transport.
    preview = head.to_string(max_rows=n_rows, max_cols=25, max_colwidth=40)
    return (f"shape: {df.shape[0]} rows x {df.shape[1]} cols\n"
            f"columns: {', '.join(map(str, df.columns))}\n\n"
            f"{preview}")
