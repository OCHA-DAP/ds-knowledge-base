#!/usr/bin/env python3
"""Generate the PUBLIC manifest of the Data Science team Google Drive.

Per docs/PRIVACY.md (Phase 7b): the Drive **manifest is public metadata** — a
catalog of what exists and where (folder path, title, type, dates, link), NOT the
content. Content extraction is a separate, INTERNAL step (Phase 7c, gitignored
`drive/`). Drive share-links are access-gated, so publishing them exposes nothing.

Writes:
  infrastructure/drive-index.md      human catalog (grouped by folder path)
  infrastructure/.drive-index.json    machine-readable manifest

Scope (hard rules from PRIVACY.md):
  • ONLY the DS team shared drive (DRIVE_ID below) — never the data-storage drive.
  • EXCLUDE the `General - All AA projects / Data` subtree (too much; data not knowledge).
  • Metadata only. Strip PII (no owner emails).

Two modes:
  • crawl  (default) — walk the Drive via the Drive API → rewrite both files.
    Needs Google Drive **read-only** credentials (the interactive Claude connector
    can't be called from a script): a service account with the shared drive shared
    to it, or an OAuth token. Set GOOGLE_APPLICATION_CREDENTIALS to the SA JSON.
    `pip install google-api-python-client google-auth`.
  • --render-only — re-render the .md from an existing .drive-index.json (no API).
    Used to seed/preview the format without credentials.

Usage:
  python3 scripts/gen_drive_index.py                # full crawl (needs creds)
  python3 scripts/gen_drive_index.py --render-only  # re-render md from the json
"""
from __future__ import annotations
import datetime, json, os, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT_MD = ROOT / "infrastructure" / "drive-index.md"
OUT_JSON = ROOT / "infrastructure" / ".drive-index.json"

DRIVE_ID = os.environ.get("DS_DRIVE_ID", "0AGYkOFcloQuyUk9PVA")   # DS team shared drive
DRIVE_NAME = "Data Science (team shared drive)"
# Folder *titles* whose subtree is excluded from the crawl (PRIVACY.md scope rule).
EXCLUDE_TITLES = {"General - All AA projects"}   # skip its `Data` subtree (and itself)
EXCLUDE_PATH_SUBSTR = ["General - All AA projects/Data"]

FOLDER = "application/vnd.google-apps.folder"
TYPE = {  # friendly type label from mimeType
    FOLDER: "folder", "application/vnd.google-apps.document": "doc",
    "application/vnd.google-apps.spreadsheet": "sheet",
    "application/vnd.google-apps.presentation": "slides",
    "application/pdf": "pdf", "text/csv": "csv",
}


def tlabel(m): return TYPE.get(m, (m or "").split(".")[-1].split("/")[-1] or "file")


def human_size(b):
    try:
        b = int(b)
    except (TypeError, ValueError):
        return ""
    for u in ("B", "KB", "MB", "GB"):
        if b < 1024:
            return f"{b:.0f}{u}"
        b /= 1024
    return f"{b:.0f}TB"


# ---- crawl (Drive API) --------------------------------------------------------
def crawl() -> list[dict]:
    try:
        from googleapiclient.discovery import build
        from google.oauth2 import service_account
    except ImportError:
        sys.exit("crawl needs `pip install google-api-python-client google-auth` "
                 "(or use --render-only).")
    cred_file = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if not cred_file:
        sys.exit("Set GOOGLE_APPLICATION_CREDENTIALS to a Drive read-only service-account JSON "
                 "(the shared drive must be shared to that service account).")
    creds = service_account.Credentials.from_service_account_file(
        cred_file, scopes=["https://www.googleapis.com/auth/drive.readonly"])
    svc = build("drive", "v3", credentials=creds, cache_discovery=False)

    nodes, stack = [], [(DRIVE_ID, "")]          # (folder_id, parent_path)
    fields = ("nextPageToken, files(id,name,mimeType,parents,createdTime,"
              "modifiedTime,size,webViewLink)")
    while stack:
        fid, ppath = stack.pop()
        token = None
        while True:
            resp = svc.files().list(
                q=f"'{fid}' in parents and trashed=false", corpora="drive",
                driveId=DRIVE_ID, includeItemsFromAllDrives=True, supportsAllDrives=True,
                pageSize=1000, fields=fields, pageToken=token).execute()
            for f in resp.get("files", []):
                is_folder = f["mimeType"] == FOLDER
                path = f"{ppath}/{f['name']}".lstrip("/") if ppath else f["name"]
                full = f"{ppath}/{f['name']}" if ppath else f["name"]
                if any(s in full for s in EXCLUDE_PATH_SUBSTR) or (
                        is_folder and f["name"] in EXCLUDE_TITLES):
                    nodes.append({"id": f["id"], "title": f["name"], "type": "folder",
                                  "path": ppath, "excluded": True})
                    continue                      # don't recurse, metadata only
                nodes.append({
                    "id": f["id"], "title": f["name"], "type": tlabel(f["mimeType"]),
                    "path": ppath, "created": (f.get("createdTime") or "")[:10],
                    "modified": (f.get("modifiedTime") or "")[:10],
                    "size": human_size(f.get("size")), "link": f.get("webViewLink"),
                })
                if is_folder:
                    stack.append((f["id"], full))
            token = resp.get("nextPageToken")
            if not token:
                break
    return nodes


# ---- render -------------------------------------------------------------------
def render(manifest: dict):
    nodes = manifest["nodes"]
    folders = [n for n in nodes if n["type"] == "folder"]
    files = [n for n in nodes if n["type"] != "folder"]
    by_path: dict[str, list] = {}
    for n in nodes:
        by_path.setdefault(n.get("path", ""), []).append(n)

    L = [
        "# Drive index — Data Science team shared drive",
        "",
        "_Generated by `scripts/gen_drive_index.py` — DO NOT EDIT BY HAND._  ",
        f"_Snapshot: {manifest.get('generated')} · coverage: **{manifest.get('coverage')}**._",
        "",
        "**Public metadata only** — a catalog of what exists in the team Drive (folder "
        "path, title, type, dates, link), per [docs/PRIVACY.md](../docs/PRIVACY.md). The "
        "**content is internal** (not here; Phase 7c → gitignored `drive/` + private store). "
        "Drive links are access-gated, so they expose nothing on their own.",
        "",
        f"- **Drive:** {DRIVE_NAME} (`{manifest.get('drive_id')}`)",
        f"- **Excluded** (scope rules): the data-storage drive (separate, not crawled) and "
        f"`General - All AA projects / Data` (too large; data not knowledge).",
        f"- **Counts:** {len(folders)} folders · {len(files)} files.",
        "",
    ]
    # one section per folder path (root first, then alphabetical)
    for path in sorted(by_path, key=lambda p: (p != "", p.lower())):
        items = sorted(by_path[path], key=lambda n: (n["type"] != "folder", n["title"].lower()))
        head = "`/` (drive root)" if path == "" else f"`{path}/`"
        L += [f"## {head}", "",
              "| title | type | modified | size | link |", "|---|---|---|--:|---|"]
        for n in items:
            if n.get("excluded"):
                L.append(f"| {n['title']} | folder | | | _excluded (scope rule)_ |")
                continue
            link = f"[open]({n['link']})" if n.get("link") else ""
            L.append(f"| {n['title']} | {n['type']} | {n.get('modified','')} | "
                     f"{n.get('size','')} | {link} |")
        L.append("")
    L += ["## Refresh", "",
          "`python3 scripts/gen_drive_index.py` (needs Drive read-only credentials — see the "
          "script header). The Claude Drive connector is interactive-only and can't do the "
          "full crawl from a script; this seed was captured via the connector, and the "
          "generator does the exhaustive tree when run with a service account.", ""]
    OUT_MD.write_text("\n".join(L))
    OUT_JSON.write_text(json.dumps(manifest, indent=2, ensure_ascii=False))
    print(f"Wrote {OUT_MD.relative_to(ROOT)} — {len(folders)} folders / {len(files)} files "
          f"({manifest.get('coverage')}).")


def main():
    if "--render-only" in sys.argv:
        if not OUT_JSON.exists():
            sys.exit(f"{OUT_JSON} not found — run a crawl first, or seed it.")
        render(json.loads(OUT_JSON.read_text()))
        return
    nodes = crawl()
    render({
        "drive_id": DRIVE_ID, "drive_name": DRIVE_NAME,
        "generated": datetime.date.today().isoformat(),
        "coverage": "full crawl",
        "nodes": nodes,
    })


if __name__ == "__main__":
    main()
