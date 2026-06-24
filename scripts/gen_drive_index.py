#!/usr/bin/env python3
"""Generate the INTERNAL manifest of the Data Science team Google Drive.

Per docs/PRIVACY.md (Phase 7b, D44b/D45/D46): a catalog of what exists and where
(folder path, title, type, dates, link), NOT the content. The full crawl is ~9k
entries incl. partner/collab filenames — too much volume and exposure for the
public repo — so the manifest's home is the PRIVATE companion repo
`ds-knowledge-base-internal` (versioned + access-controlled; `git diff` is the
drift record). The public repo holds only a pointer. Document content is a
separate INTERNAL step (Phase 7c). Drive share-links are access-gated, so the
links expose nothing on their own.

Writes (into the private repo — clone it next to this one, or set KB_INTERNAL_DIR):
  ../ds-knowledge-base-internal/drive/drive-index.md      human catalog (by folder)
  ../ds-knowledge-base-internal/drive/drive-index.json    machine-readable manifest

Scope (hard rules from PRIVACY.md — keep the catalog to knowledge, drop bulk data):
  • ONLY the DS team shared drive (DRIVE_ID below) — never the data-storage drive.
  • EXCLUDE the bulk-data root folders (EXCLUDE_ROOT_TITLES: HDX Signals / Climate
    Data / Collaborations) and the `General - All AA projects / Data` subtree.
  • Metadata only. Strip PII (no owner emails).

Two modes:
  • crawl  (default) — walk the Drive via the Drive API → rewrite both files.
    Needs Google Drive **read-only** credentials (the interactive Claude connector
    can't be called from a script). Two ways, in priority order:
      1. Service account — set GOOGLE_APPLICATION_CREDENTIALS to the SA JSON. The
         shared drive must be shared to that SA's email as Viewer. Needs you to be
         a Manager of the drive AND the org to allow non-domain members — often
         locked down, so this can be a dead end.
      2. Your own Google login (no sharing, no admin) — acts AS you, who already
         has Drive access. One-time:
           gcloud auth application-default login \
             --scopes=https://www.googleapis.com/auth/drive.readonly,https://www.googleapis.com/auth/cloud-platform
         Then run the crawl with GOOGLE_APPLICATION_CREDENTIALS unset; it picks up
         Application Default Credentials automatically.
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
# The manifest is INTERNAL (D44b/D45/D46): ~9k partner/project filenames — too much
# volume + exposure for the public repo. Its home is the PRIVATE companion repo
# `ds-knowledge-base-internal` (versioned + access-controlled; `git diff` is the drift
# record — no blob, no custom drift job). Default = sibling clone; override with
# KB_INTERNAL_DIR. The public repo carries only a pointer (infrastructure/drive-index.md).
INTERNAL = Path(os.environ.get("KB_INTERNAL_DIR", ROOT.parent / "ds-knowledge-base-internal"))
OUT_MD = INTERNAL / "drive" / "drive-index.md"
OUT_JSON = INTERNAL / "drive" / "drive-index.json"

DRIVE_ID = os.environ.get("DS_DRIVE_ID", "0AGYkOFcloQuyUk9PVA")   # DS team shared drive
DRIVE_NAME = "Data Science (team shared drive)"
# Scope rules (PRIVACY.md): keep the catalog to *knowledge*, drop bulk *data*.
# Root-level folder titles whose entire subtree is skipped (data, not knowledge).
EXCLUDE_ROOT_TITLES = {"HDX Signals", "Climate Data", "Collaborations"}
# Exact folder paths excluded (the folder and its subtree) — boundary-aware, so
# `…/Data` does NOT also catch siblings like `…/DataGrids`. Only the `Data` child
# of the big AA-projects folder; the rest of that folder IS catalogued.
EXCLUDE_PATHS = ["General - All AA projects/Data"]


def path_excluded(full: str) -> bool:
    # Segment-boundary match anywhere in the path: `…/General - All AA projects/Data`
    # (a partial path) matches even when prefixed by parent folders, but does NOT
    # catch siblings like `…/DataGrids`. Wrap both sides in "/" so segments align.
    hay = f"/{full}/"
    return any(f"/{p}/" in hay for p in EXCLUDE_PATHS)

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
    except ImportError:
        sys.exit("crawl needs `pip install google-api-python-client google-auth` "
                 "(or use --render-only).")
    scopes = ["https://www.googleapis.com/auth/drive.readonly"]
    cred_file = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if cred_file:                                    # (1) service account
        from google.oauth2 import service_account
        creds = service_account.Credentials.from_service_account_file(cred_file, scopes=scopes)
    else:                                            # (2) your own login (ADC)
        import google.auth
        try:
            creds, _ = google.auth.default(scopes=scopes)
        except google.auth.exceptions.DefaultCredentialsError:
            sys.exit("No credentials. Either set GOOGLE_APPLICATION_CREDENTIALS to a Drive "
                     "read-only service-account JSON, or run:\n  gcloud auth application-default "
                     "login --scopes=https://www.googleapis.com/auth/drive.readonly,"
                     "https://www.googleapis.com/auth/cloud-platform")
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
                if path_excluded(full) or (
                        is_folder and ppath == "" and f["name"] in EXCLUDE_ROOT_TITLES):
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
        "**INTERNAL** — this is a catalog of what exists in the team Drive (folder path, "
        "title, type, dates, link), per the public KB's `docs/PRIVACY.md`. It lives in this "
        "**private repo** (`ds-knowledge-base-internal`), **not** the public repo: at ~9k "
        "entries it includes partner/collab filenames — more volume and exposure than a public "
        "catalog should carry. Document **content** is internal too (Phase 7c). The public repo "
        "holds only a pointer (`infrastructure/drive-index.md`), not this catalog.",
        "",
        f"- **Drive:** {DRIVE_NAME} (`{manifest.get('drive_id')}`)",
        f"- **Excluded** (scope = knowledge, not data): the separate data-storage drive, the "
        f"bulk-data root folders ({', '.join(sorted(EXCLUDE_ROOT_TITLES))}), and "
        f"`General - All AA projects / Data`.",
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
    L += ["## Refresh & drift", "",
          "Headless — the full crawl runs from a script in the public KB (the Claude Drive "
          "connector is interactive-only and is reserved for *content* spot-checks). This file "
          "is committed in this private repo, so **`git diff` after a re-crawl IS the drift "
          "record** — no separate drift job, no blob.",
          "",
          "```sh",
          "# from the public ds-knowledge-base checkout:",
          "# one-time auth (read-only Drive, our own internal OAuth client — see script header)",
          "gcloud auth application-default login \\",
          "  --client-id-file=~/.config/ds-kb/oauth-client.json \\",
          "  --scopes=https://www.googleapis.com/auth/drive.readonly,https://www.googleapis.com/auth/cloud-platform",
          "",
          "GOOGLE_APPLICATION_CREDENTIALS= ~/.config/ds-kb/venv/bin/python scripts/gen_drive_index.py   # rewrites this file",
          "scripts/drive_refresh.sh                                                                    # crawl + commit here",
          "```", ""]
    if not INTERNAL.exists():
        sys.exit(f"Private repo not found at {INTERNAL} — clone `ds-knowledge-base-internal` "
                 f"next to the public repo, or set KB_INTERNAL_DIR. (Refusing to write the "
                 f"internal manifest to an unexpected location.)")
    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.write_text("\n".join(L))
    OUT_JSON.write_text(json.dumps(manifest, indent=2, ensure_ascii=False))
    print(f"Wrote {OUT_MD} — {len(folders)} folders / {len(files)} files "
          f"({manifest.get('coverage')}).")


def diff(old_nodes, new_nodes):
    """Folder-level drift between two crawls, keyed by Drive id (stable across renames)."""
    o = {n["id"]: n for n in old_nodes if n["type"] == "folder"}
    n = {x["id"]: x for x in new_nodes if x["type"] == "folder"}
    added = sorted((f"{n[i].get('path','')}/{n[i]['title']}".lstrip("/") for i in n if i not in o))
    removed = sorted((f"{o[i].get('path','')}/{o[i]['title']}".lstrip("/") for i in o if i not in n))
    renamed = sorted((f"{o[i].get('path','')}/: {o[i]['title']} -> {n[i]['title']}"
                      for i in n if i in o and n[i]["title"] != o[i]["title"]))
    return added, removed, renamed


def main():
    if "--render-only" in sys.argv:
        if not OUT_JSON.exists():
            sys.exit(f"{OUT_JSON} not found — run a crawl first, or seed it.")
        render(json.loads(OUT_JSON.read_text()))
        return
    nodes = crawl()
    if "--check" in sys.argv:                         # drift detector: write nothing, exit 1 on change
        if not OUT_JSON.exists():
            sys.exit(f"{OUT_JSON} not found — nothing to diff against.")
        old = json.loads(OUT_JSON.read_text()).get("nodes", [])
        added, removed, renamed = diff(old, nodes)
        for label, rows in (("ADDED", added), ("REMOVED", removed), ("RENAMED", renamed)):
            for r in rows:
                print(f"  {label}: {r}")
        total = len(added) + len(removed) + len(renamed)
        print(f"drive drift: {len(added)} added / {len(removed)} removed / {len(renamed)} renamed folders")
        sys.exit(1 if total else 0)
    render({
        "drive_id": DRIVE_ID, "drive_name": DRIVE_NAME,
        "generated": datetime.date.today().isoformat(),
        "coverage": "full crawl",
        "nodes": nodes,
    })


if __name__ == "__main__":
    main()
