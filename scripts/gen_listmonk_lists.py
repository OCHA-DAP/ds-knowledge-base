#!/usr/bin/env python3
"""Snapshot Listmonk's mailing lists (id, name, tags, subscriber count) to
`infrastructure/.listmonk-lists.json`, so the database network map (gen_db_network.py) can say how
many recipients each pipeline's alert emails reach — "if this goes down, who stops hearing from us".

Auth (HTTP Basic, the sending tier is enough — lists:get):
  DSCI_LISTMONK_BASE_URL       full base URL including /api
  DSCI_LISTMONK_API_USERNAME   API user
  DSCI_LISTMONK_API_KEY        API token

Usage:  python scripts/gen_listmonk_lists.py
Exit:   0 written · 1 auth/network failure or an empty response (the existing snapshot is kept —
        a good snapshot is never replaced by an empty one) · 3 secrets not configured (skipped, not an error)
Needs:  stdlib only.
"""
from __future__ import annotations
import base64
import datetime as dt
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "infrastructure" / ".listmonk-lists.json"


def main() -> int:
    base = (os.environ.get("DSCI_LISTMONK_BASE_URL") or "").rstrip("/")
    user = os.environ.get("DSCI_LISTMONK_API_USERNAME") or ""
    key = os.environ.get("DSCI_LISTMONK_API_KEY") or ""
    if not (base and user and key):
        print("listmonk secrets not configured (DSCI_LISTMONK_BASE_URL / _API_USERNAME / _API_KEY) — skipping", file=sys.stderr)
        return 3
    token = base64.b64encode(f"{user}:{key}".encode()).decode()
    lists, page = [], 1
    while True:
        req = urllib.request.Request(f"{base}/lists?page={page}&per_page=100&order_by=id&order=asc",
                                     headers={"Authorization": f"Basic {token}", "Accept": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                data = json.loads(r.read().decode())["data"]
        except (urllib.error.URLError, KeyError, json.JSONDecodeError) as e:
            print(f"ERROR: Listmonk lists fetch failed on page {page}: {e}", file=sys.stderr)
            return 1
        for x in data.get("results") or []:
            lists.append({"id": x["id"], "name": x.get("name"), "type": x.get("type"), "tags": x.get("tags") or [],
                          "subscriber_count": x.get("subscriber_count", 0),
                          "subscriber_statuses": x.get("subscriber_statuses") or {}})
        if len(lists) >= (data.get("total") or 0) or not data.get("results"):
            break
        page += 1
    if not lists:
        print("ERROR: Listmonk returned no lists — refusing to overwrite the snapshot", file=sys.stderr)
        return 1
    OUT.write_text(json.dumps({"generated": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
                               "source": base.replace("/api", ""), "lists": lists}, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {OUT.relative_to(ROOT)} — {len(lists)} lists, {sum(l['subscriber_count'] for l in lists)} list memberships.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
