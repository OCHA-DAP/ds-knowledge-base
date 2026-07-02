#!/usr/bin/env python3
"""One-command enablement of the usage-telemetry axis (run BY A HUMAN, once).

Does the three steps from infrastructure/usage.md "Enabling it":
  1. DB (as the server admin, AZURE_DB_UID/AZURE_DB_PW_DEV): apply usage_schema.sql to the
     DEV database — creates the kb_usage schema + events table + the INSERT-only
     kb_usage_writer role (password generated here) — and grants the standard read role SELECT.
  2. Apps: sets KB_USAGE_TIER + KB_USAGE_DB_URL on both MCP web apps
     (chd-ds-kb-mcp → public, chd-ds-kb-mcp-internal → internal) via `az`.
  3. Prints how to verify.

Idempotent: re-running refreshes the role password and app settings.

Usage:  PGSSLMODE=require uv run --with psycopg2-binary python mcp_server/deploy/enable_usage.py
Needs:  AZURE_DB_UID, AZURE_DB_PW_DEV, DSCI_AZ_DB_DEV_HOST, DSCI_AZ_DB_DEV_UID env vars;
        `az` CLI logged in to the OCHA-PROD subscription.
"""
from __future__ import annotations

import os
import secrets
import subprocess
import sys
from pathlib import Path

import psycopg2

RG = "IMB-CHD-DataScience-EastUS2"
APPS = {"chd-ds-kb-mcp": "public", "chd-ds-kb-mcp-internal": "internal"}
DBNAME = "postgres"


def main() -> None:
    host = os.environ["DSCI_AZ_DB_DEV_HOST"]
    read_role = os.environ["DSCI_AZ_DB_DEV_UID"]
    pw = secrets.token_urlsafe(24)

    sql_path = Path(__file__).parent / "usage_schema.sql"
    sql = sql_path.read_text().replace("CHANGE_ME", pw)

    print(f"1/3 applying {sql_path.name} to {host}/{DBNAME} as {os.environ['AZURE_DB_UID']} …")
    conn = psycopg2.connect(
        host=host, user=os.environ["AZURE_DB_UID"], password=os.environ["AZURE_DB_PW_DEV"],
        dbname=DBNAME, sslmode="require", connect_timeout=15,
    )
    cur = conn.cursor()
    cur.execute(sql)
    # role may already exist (idempotent re-run) — always align its password with this run's
    cur.execute("ALTER ROLE kb_usage_writer WITH PASSWORD %s", (pw,))
    cur.execute(f'GRANT USAGE ON SCHEMA kb_usage TO "{read_role}"')
    cur.execute(f'GRANT SELECT ON kb_usage.events TO "{read_role}"')
    conn.commit()
    cur.execute("SELECT count(*) FROM kb_usage.events")
    print(f"    ok — kb_usage.events exists ({cur.fetchone()[0]} rows); SELECT granted to {read_role}")
    conn.close()

    url = f"postgresql+psycopg2://kb_usage_writer:{pw}@{host}:5432/{DBNAME}?sslmode=require"
    for app, tier in APPS.items():
        print(f"2/3 setting KB_USAGE_TIER={tier} + KB_USAGE_DB_URL on {app} …")
        r = subprocess.run(
            ["az", "webapp", "config", "appsettings", "set", "-g", RG, "-n", app,
             "--settings", f"KB_USAGE_TIER={tier}", f"KB_USAGE_DB_URL={url}", "-o", "none"],
            capture_output=True, text=True,
        )
        if r.returncode != 0:
            sys.exit(f"::error:: az failed for {app}: {r.stderr[-400:]}")
        print(f"    ok — {app} restarts with telemetry on")

    print("""3/3 verify (after the apps recycle, ~1 min):
    python mcp_server/deploy/check_remote.py https://chd-ds-kb-mcp.azurewebsites.net/mcp
    # then rows should appear:
    #   SELECT ts, tier, tool, arg_summary, ok, empty FROM kb_usage.events ORDER BY ts DESC LIMIT 5;""")


if __name__ == "__main__":
    main()
