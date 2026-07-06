#!/usr/bin/env python3
"""One-command enablement of the usage-telemetry axis (run BY A HUMAN, once).

Does the steps from infrastructure/usage.md "Enabling it", connecting as the standard
write login (`DSCI_AZ_DB_DEV_UID_WRITE` / `_PW_WRITE`, i.e. dbwriter):
  1. DB: create the kb_usage schema + events table + indexes (dbwriter can do this),
     grant the standard read role SELECT.
  2. Role: create/refresh the INSERT-only `kb_usage_writer` role (password generated here).
     dbwriter lacks CREATEROLE, so this step falls back to the admin creds
     (AZURE_DB_UID / AZURE_DB_PW_DEV) if present, and otherwise prints the exact SQL
     for a DB admin to run — then re-run this script.
  3. Apps: set KB_USAGE_TIER + KB_USAGE_DB_URL on both MCP web apps
     (chd-ds-kb-mcp → public, chd-ds-kb-mcp-internal → internal) via `az`.

Idempotent: re-running refreshes the role password and app settings.

Usage:  PGSSLMODE=require uv run --with psycopg2-binary python mcp_server/deploy/enable_usage.py
Needs:  DSCI_AZ_DB_DEV_{HOST,UID,UID_WRITE,PW_WRITE} env vars; `az` CLI logged in.
"""
from __future__ import annotations

import os
import secrets
import subprocess
import sys

import psycopg2

RG = "IMB-CHD-DataScience-EastUS2"
APPS = {"chd-ds-kb-mcp": "public", "chd-ds-kb-mcp-internal": "internal"}
DBNAME = "postgres"

DDL = """
CREATE SCHEMA IF NOT EXISTS kb_usage;
CREATE TABLE IF NOT EXISTS kb_usage.events (
  id           bigserial PRIMARY KEY,
  ts           timestamptz NOT NULL DEFAULT now(),
  tier         text,
  tool         text NOT NULL,
  arg_summary  text,
  ok           boolean NOT NULL,
  empty        boolean,
  result_chars integer,
  latency_ms   integer,
  error        text,
  session      text
);
CREATE INDEX IF NOT EXISTS events_ts_idx   ON kb_usage.events (ts);
CREATE INDEX IF NOT EXISTS events_tool_idx ON kb_usage.events (tool);
"""


def connect(user: str, pw: str):
    return psycopg2.connect(
        host=os.environ["DSCI_AZ_DB_DEV_HOST"], user=user, password=pw,
        dbname=DBNAME, sslmode="require", connect_timeout=15,
    )


def ensure_role(pw: str) -> bool:
    """Create/refresh kb_usage_writer via whichever login has CREATEROLE. True on success."""
    candidates = [("dbwriter (DSCI_AZ_DB_DEV_UID_WRITE)",
                   os.environ["DSCI_AZ_DB_DEV_UID_WRITE"], os.environ["DSCI_AZ_DB_DEV_PW_WRITE"])]
    if os.environ.get("AZURE_DB_UID") and os.environ.get("AZURE_DB_PW_DEV"):
        candidates.append(("admin (AZURE_DB_UID)", os.environ["AZURE_DB_UID"], os.environ["AZURE_DB_PW_DEV"]))
    for label, user, cred in candidates:
        try:
            conn = connect(user, cred)
            cur = conn.cursor()
            cur.execute("SELECT 1 FROM pg_roles WHERE rolname = 'kb_usage_writer'")
            if cur.fetchone() is None:
                cur.execute("CREATE ROLE kb_usage_writer LOGIN PASSWORD %s", (pw,))
            else:
                cur.execute("ALTER ROLE kb_usage_writer WITH PASSWORD %s", (pw,))
            conn.commit()
            conn.close()
            print(f"    role kb_usage_writer ready (via {label})")
            return True
        except psycopg2.errors.InsufficientPrivilege:
            print(f"    {label}: no CREATEROLE — trying next")
        except psycopg2.OperationalError as e:
            print(f"    {label}: connection failed ({str(e).strip()[:80]}) — trying next")
    return False


def main() -> None:
    pw = secrets.token_urlsafe(24)
    host = os.environ["DSCI_AZ_DB_DEV_HOST"]

    print(f"1/3 schema+table on {host}/{DBNAME} as {os.environ['DSCI_AZ_DB_DEV_UID_WRITE']} …")
    conn = connect(os.environ["DSCI_AZ_DB_DEV_UID_WRITE"], os.environ["DSCI_AZ_DB_DEV_PW_WRITE"])
    cur = conn.cursor()
    cur.execute(DDL)
    read_role = os.environ["DSCI_AZ_DB_DEV_UID"]
    cur.execute(f'GRANT USAGE ON SCHEMA kb_usage TO "{read_role}"')
    cur.execute(f'GRANT SELECT ON kb_usage.events TO "{read_role}"')
    conn.commit()
    cur.execute("SELECT count(*) FROM kb_usage.events")
    print(f"    ok — kb_usage.events exists ({cur.fetchone()[0]} rows); SELECT granted to {read_role}")

    print("2/3 INSERT-only role …")
    if not ensure_role(pw):
        conn.close()
        sys.exit(
            "::error:: no available login can CREATE ROLE. Have a DB admin run this on "
            f"{host}/{DBNAME}, then re-run this script (it will reset the password and "
            "finish the grants/app settings):\n"
            "  CREATE ROLE kb_usage_writer LOGIN PASSWORD '<anything>';"
        )
    cur.execute("GRANT USAGE ON SCHEMA kb_usage TO kb_usage_writer")
    cur.execute("GRANT INSERT ON kb_usage.events TO kb_usage_writer")
    cur.execute("GRANT USAGE, SELECT ON SEQUENCE kb_usage.events_id_seq TO kb_usage_writer")
    conn.commit()
    conn.close()

    url = f"postgresql+psycopg2://kb_usage_writer:{pw}@{host}:5432/{DBNAME}?sslmode=require"
    for app, tier in APPS.items():
        print(f"3/3 setting KB_USAGE_TIER={tier} + KB_USAGE_DB_URL on {app} …")
        r = subprocess.run(
            ["az", "webapp", "config", "appsettings", "set", "-g", RG, "-n", app,
             "--settings", f"KB_USAGE_TIER={tier}", f"KB_USAGE_DB_URL={url}", "-o", "none"],
            capture_output=True, text=True,
        )
        if r.returncode != 0:
            sys.exit(f"::error:: az failed for {app}: {r.stderr[-400:]}")
        print(f"    ok — {app} restarts with telemetry on")

    print("""done. verify (after the apps recycle, ~1 min):
    python mcp_server/deploy/check_remote.py https://chd-ds-kb-mcp.azurewebsites.net/mcp
    # then rows should appear:
    #   SELECT ts, tier, tool, arg_summary, ok, empty FROM kb_usage.events ORDER BY ts DESC LIMIT 5;""")


if __name__ == "__main__":
    main()
