-- One-time DB setup for KB usage telemetry (the "Usage" axis; see
-- infrastructure/usage.md and infrastructure/automation.md).
--
-- Run by a DB admin (needs DDL + CREATE ROLE). Put this in the DEV database by default
-- — it's operational telemetry, not core analytics data. The chatbot can still read it
-- via run_sql(stage='dev').
--
-- Two roles touch this table, by least privilege:
--   * kb_usage_writer  — used ONLY by the MCP's telemetry path (KB_USAGE_DB_URL). INSERT only.
--                        Even a full env leak on the internet-facing MCP can only append
--                        telemetry rows; it cannot read or write any real table.
--   * the standard DSCI read role (DSCI_AZ_DB_*_UID) — gets SELECT, so scripts/analyze_usage.py
--                        (run in the usage-review workflow, read creds only) can aggregate it.

CREATE SCHEMA IF NOT EXISTS kb_usage;

CREATE TABLE IF NOT EXISTS kb_usage.events (
  id           bigserial PRIMARY KEY,
  ts           timestamptz NOT NULL DEFAULT now(),
  tier         text,            -- 'public' | 'internal' | 'unknown' (KB_USAGE_TIER per deployment)
  tool         text NOT NULL,   -- search_kb / read_kb_page / run_sql / run_python / ...
  arg_summary  text,            -- truncated query / path / SQL (the intent signal)
  ok           boolean NOT NULL,
  empty        boolean,         -- result looked empty / zero-hit (NULL when the call errored)
  result_chars integer,
  latency_ms   integer,
  error        text,            -- truncated error string when ok = false
  session      text             -- coarse client/session id when available
);
CREATE INDEX IF NOT EXISTS events_ts_idx   ON kb_usage.events (ts);
CREATE INDEX IF NOT EXISTS events_tool_idx ON kb_usage.events (tool);

-- Least-privilege writer used ONLY by the MCP telemetry path. CHANGE THE PASSWORD.
DO $$ BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'kb_usage_writer') THEN
    CREATE ROLE kb_usage_writer LOGIN PASSWORD 'CHANGE_ME';
  END IF;
END $$;
GRANT USAGE ON SCHEMA kb_usage TO kb_usage_writer;
GRANT INSERT ON kb_usage.events TO kb_usage_writer;
GRANT USAGE, SELECT ON SEQUENCE kb_usage.events_id_seq TO kb_usage_writer;

-- Let the standard read role aggregate it. Replace <read_role> with the login behind
-- DSCI_AZ_DB_*_UID (the one gen_db_schema.py / analyze_usage.py use).
-- GRANT USAGE ON SCHEMA kb_usage TO <read_role>;
-- GRANT SELECT ON kb_usage.events TO <read_role>;

-- Then set on the MCP app(s):
--   KB_USAGE_TIER   = internal   (on chd-ds-kb-mcp-internal)  /  public (on chd-ds-kb-mcp)
--   KB_USAGE_DB_URL = postgresql+psycopg2://kb_usage_writer:<pw>@<host>:5432/<db>?sslmode=require
