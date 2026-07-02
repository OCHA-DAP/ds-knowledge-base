"""Best-effort usage telemetry for the KB MCP.

Records one row per tool call to Postgres (`kb_usage.events`) so we can see how people
actually use the KB and feed that back into improving it — both the MCP's behaviour and
how the KB is organised. The analysis loop is `scripts/analyze_usage.py` + the
`usage-review` workflow (the "Usage" axis in `infrastructure/automation.md`).

Design constraints (read these before changing anything here):

- **The write path is ISOLATED.** The internet-facing MCP holds READ-ONLY DB creds by
  design. Telemetry uses a SEPARATE, least-privilege connection (`KB_USAGE_DB_URL`) whose
  role can only INSERT into `kb_usage.events`. A full env leak therefore only lets an
  attacker append telemetry rows — it cannot read or write real tables. The broad
  `DSCI_AZ_*_WRITE` creds never go on this box. See `mcp_server/deploy/usage_schema.sql`.
- **Fail-open, off the request path.** Logging must NEVER break or slow a tool call. If
  `KB_USAGE_DB_URL` is unset, or the DB is unreachable, recording silently no-ops. Writes
  happen on a background daemon thread, batched; `record()` never raises.
- **Privacy.** We store a truncated arg summary (the query / path / SQL). The internal
  tier's text can be sensitive, so it lives ONLY in the DB (never the public repo). Don't
  widen what's captured without re-reading `docs/PRIVACY.md`.
"""
from __future__ import annotations

import json
import os
import queue
import threading
import time

_TIER = (os.environ.get("KB_USAGE_TIER", "").strip() or "unknown")
_URL = os.environ.get("KB_USAGE_DB_URL", "").strip()
_ENABLED = bool(_URL)
_MAXLEN = 2000  # truncate arg summaries / error strings

_q: "queue.Queue[dict]" = queue.Queue(maxsize=10000)
_engine = None
_started = False
_lock = threading.Lock()

# For each tool, the single most useful argument to summarise.
_ARG_KEY = {
    "search_kb": "query", "grep": "pattern", "run_sql": "query",
    "read_kb_page": "path", "read_file": "path", "read_blob": "blob_name",
    "list_blobs": "prefix", "glob": "pattern", "list_dir": "path",
    "get_index": "which", "fetch_repo_file": "path", "run_python": "code",
}

# Heuristics for "this call found nothing" — the highest-signal thing to detect.
_EMPTY_NEEDLES = (
    "no matches", "no results", "not found", "0 rows", "no rows",
    "nothing found", "(empty)", "no files", "returned no", "empty result",
)


def _summarize(tool: str, args) -> str:
    if not isinstance(args, dict):
        return ""
    key = _ARG_KEY.get(tool)
    val = args.get(key) if key else None
    if val is None:
        try:
            val = json.dumps(args, default=str)
        except Exception:
            val = str(args)
    return str(val).strip().replace("\n", " ")[:_MAXLEN]


def _looks_empty(result_text: str) -> bool:
    if not result_text:
        return True
    t = result_text.strip().lower()
    if len(t) < 3:
        return True
    return any(n in t for n in _EMPTY_NEEDLES)


def record(tool, args, ok, result_text, latency_ms, error=None, session=None) -> None:
    """Enqueue one usage event. Never raises; no-ops when telemetry is disabled."""
    if not _ENABLED:
        return
    try:
        _ensure_worker()
        _q.put_nowait({
            "tier": _TIER,
            "tool": tool,
            "arg_summary": _summarize(tool, args),
            "ok": bool(ok),
            "empty": (_looks_empty(result_text) if ok else None),
            "result_chars": (len(result_text) if result_text else 0),
            "latency_ms": int(latency_ms),
            "error": (str(error)[:_MAXLEN] if error else None),
            "session": session,
        })
    except Exception:
        pass  # fail-open: telemetry must never affect a tool call


def _ensure_worker() -> None:
    global _started
    if _started:
        return
    with _lock:
        if _started:
            return
        threading.Thread(target=_worker, name="kb-usage", daemon=True).start()
        _started = True


def _get_engine():
    global _engine
    if _engine is None:
        from sqlalchemy import create_engine
        _engine = create_engine(_URL, pool_pre_ping=True, pool_size=1, max_overflow=1)
    return _engine


def _worker() -> None:
    from sqlalchemy import text
    insert = text(
        "INSERT INTO kb_usage.events "
        "(tier, tool, arg_summary, ok, empty, result_chars, latency_ms, error, session) "
        "VALUES (:tier, :tool, :arg_summary, :ok, :empty, :result_chars, :latency_ms, :error, :session)"
    )
    while True:
        batch = [_q.get()]
        deadline = time.time() + 1.0
        while len(batch) < 50 and time.time() < deadline:
            try:
                batch.append(_q.get(timeout=0.2))
            except queue.Empty:
                break
        try:
            eng = _get_engine()
            with eng.begin() as conn:
                conn.execute(insert, batch)
        except Exception:
            pass  # drop the batch rather than crash the worker
