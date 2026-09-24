#!/usr/bin/env python3
"""Generate the DSCI DATABASE NETWORK map — one screen showing every scheduled job, app and manual
process that reads or writes the team's Azure PostgreSQL databases (prod / dev), the table groups
they touch, and the CERF frameworks whose live triggers sit downstream. Built for the question
"what breaks if a database loses its network path?": click any item and its whole chain lights up.

Inputs (all committed — no network, no secrets; safe to run at Pages deploy time):
  pipelines/*.md apps/*.md          frontmatter: `inputs` / `outputs` (DB table mentions → read/write
                                    edges), `deployment` (platform, job refs → runtime + links),
                                    `type`, `source_repo`, `surfaces`, `purpose`
  frameworks/<id>/*.md              `depends_on` (which monitor implements the framework),
                                    `prearranged_funding_usd`, `status` → the framework ledger
  infrastructure/.db-tables.json    prod table list (gen_db_schema.py, daily)
  infrastructure/.db-tables-dev.json  dev table list
  infrastructure/.pipeline-registry.json  job health + Databricks job URLs (gen_pipeline_registry.py, daily)
  infrastructure/db-network.yml     the CURATED overlay: table groups, impact statements, role /
                                    framework overrides, nodes without a KB page, notes text
  infrastructure/.listmonk-lists.json  OPTIONAL — Listmonk list sizes (gen_listmonk_lists.py, weekly); when
                                    present, each alert pipeline's card shows how many recipients it reaches

Output:
  db_network.html   the page — site.yml copies it to /db-network/index.html on the Pages site

A page that mentions a DB table but has no overlay `impact:` is still drawn (placeholder text) and
listed under "Unreviewed" in the page's Notes, so the gap is visible rather than hidden. Dev-side
table groups that have readers but no writer on the map are flagged the same way — after the
2026-09-22 dev cutover that usually means a page still declares a dev-stage read.

Usage:  python scripts/gen_db_network.py [--check]
        --check   exit 2 if db_network.html on disk differs from what would be generated
Exit:   0 ok · 1 an input is missing/unparseable (nothing written) · 2 (--check) stale
Needs:  pyyaml.
"""
from __future__ import annotations
import argparse
import fnmatch
import html as _html
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("Needs pyyaml:  uv pip install pyyaml")

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
try:
    from gen_catalog import display_status          # the catalog's computed lifecycle (endorsed / recently-triggered / expired / …)
except Exception:                                   # pragma: no cover — keep generating with the stored status
    def display_status(stored, activations, version=None, valid_until=None):
        return stored or "—"
ACTIVE_STATES = {"endorsed", "recently-triggered"}
OVERLAY = ROOT / "infrastructure" / "db-network.yml"
TABLES_PROD = ROOT / "infrastructure" / ".db-tables.json"
TABLES_DEV = ROOT / "infrastructure" / ".db-tables-dev.json"
REGISTRY = ROOT / "infrastructure" / ".pipeline-registry.json"
LISTMONK = ROOT / "infrastructure" / ".listmonk-lists.json"     # optional (gen_listmonk_lists.py)
OUT = ROOT / "db_network.html"
GH = "https://github.com/OCHA-DAP"
KB_BLOB = f"{GH}/ds-knowledge-base/blob/main"
DBX_JOB = "https://adb-6009046713167663.3.azuredatabricks.net/?o=6009046713167663#job/"

ISO3 = {"AFG": "Afghanistan", "BFA": "Burkina Faso", "BGD": "Bangladesh", "COD": "DR Congo", "CUB": "Cuba", "ETH": "Ethiopia",
        "FJI": "Fiji", "HTI": "Haiti", "KEN": "Kenya", "MDG": "Madagascar", "MMR": "Myanmar", "MOZ": "Mozambique", "MRT": "Mauritania",
        "MWI": "Malawi", "NER": "Niger", "NGA": "Nigeria", "NIC": "Nicaragua", "NPL": "Nepal", "PHL": "Philippines", "SOM": "Somalia",
        "SSD": "South Sudan", "TCD": "Chad", "UGA": "Uganda", "VUT": "Vanuatu", "YEM": "Yemen", "LAC": "Latin America & Caribbean"}
PLATFORM_RT = {"databricks-job": "dbx", "github-actions": "gha", "gh-pages": "gha", "azure-webapp": "web", "manual": "man"}
STATUS_RANK = {"DOWN": 3, "WARN": 2, "UNKNOWN": 1, "OK": 0}


# ----------------------------------------------------------------------------- inputs

def parse(path: Path) -> dict:
    txt = path.read_text(encoding="utf-8")
    if not txt.startswith("---"):
        return {}
    end = txt.find("\n---", 3)
    if end < 0:
        return {}
    try:
        return yaml.safe_load(txt[3:end]) or {}
    except yaml.YAMLError as e:
        sys.exit(f"ERROR: bad frontmatter in {path.relative_to(ROOT)}: {e}")


def load_json(path: Path):
    if not path.exists():
        sys.exit(f"ERROR: missing input {path.relative_to(ROOT)}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        sys.exit(f"ERROR: unparseable {path.relative_to(ROOT)}: {e}")


def as_items(v) -> list[str]:
    if v is None:
        return []
    if isinstance(v, str):
        return [v]
    return [x if isinstance(x, str) else json.dumps(x) for x in v]


# ----------------------------------------------------------------------------- table matching

def match_tables(text: str, tables: set[str]) -> set[str]:
    """Table ids named in a free-text list item: `schema.table`, or a bare table name when its schema
    is also named in the item ("storms.nhc_tracks_geo / nhc_tracks_obsv_exposure")."""
    hits = set()
    schemas_named = {s for s in {t.split(".")[0] for t in tables} if re.search(rf"\b{re.escape(s)}\.", text)}
    for t in tables:
        schema, name = t.split(".", 1)
        if re.search(rf"\b{re.escape(t)}\b", text):
            hits.add(t)
        elif schema in schemas_named and re.search(rf"\b{re.escape(name)}\b", text):
            hits.add(t)
    # explicit wildcards ("storms.nhc_*")
    for m in re.finditer(r"\b([a-z_]+)\.([a-z0-9_]*)\*", text):
        pat = f"{m.group(1)}.{m.group(2)}*"
        hits.update(fnmatch.filter(tables, pat))
    return hits


def stages_in(text: str) -> set[str]:
    out = set()
    if re.search(r"\b(dev|development)\b", text, re.I):
        out.add("dev")
    if re.search(r"\b(prod|production)\b", text, re.I):
        out.add("prod")
    return out


def expand_group_match(patterns, tables: set[str]) -> set[str]:
    out = set()
    for p in patterns or []:
        out.update(fnmatch.filter(tables, p) if any(ch in p for ch in "*?[") else ({p} & tables))
    return out


# ----------------------------------------------------------------------------- build

def build() -> dict:
    ov = yaml.safe_load(OVERLAY.read_text(encoding="utf-8")) or {}
    prod = set(load_json(TABLES_PROD))
    dev = set(load_json(TABLES_DEV))
    all_tables = prod | dev
    registry = load_json(REGISTRY)
    reg_entries = registry.get("entries") or []
    if not all_tables or not reg_entries:
        sys.exit("ERROR: empty table list or registry — refusing to generate an empty map")

    # --- table groups: (table, stage) -> group id
    groups: dict[str, dict] = {}
    for g in ov.get("groups") or []:
        groups[g["id"]] = {"id": g["id"], "db": g["db"], "label": g["label"], "tables": set(), "links": g.get("links") or [],
                           "_match": expand_group_match(g.get("match"), all_tables)}

    def add_group(g: dict) -> None:
        groups[g["id"]] = {"id": g["id"], "db": g["db"], "label": g["label"], "tables": set(g.get("tables") or []), "links": g.get("links") or [],
                           "_match": expand_group_match(g.get("match"), all_tables)}
    for svc in ov.get("services") or []:
        add_group(svc["group"])

    def group_for(table: str, stage: str) -> str:
        for g in groups.values():
            if g["db"] == stage and table in g["_match"]:
                g["tables"].add(table)
                return g["id"]
        schema = table.split(".")[0]
        gid = f"auto_{schema}_{stage}"
        groups.setdefault(gid, {"id": gid, "db": stage, "label": f"{schema}.* ({stage})", "tables": set(), "links": [], "_match": set()})
        groups[gid]["tables"].add(table)
        return gid

    # --- registry lookup by repo
    by_repo: dict[str, list] = defaultdict(list)
    for e in reg_entries:
        if e.get("repo"):
            by_repo[e["repo"].lower()].append(e)

    def writer_mode(repo: str, table: str) -> str | None:
        entries = [e for e in by_repo.get((repo or "").lower(), []) if e.get("category") == "prod"]
        for e in entries:
            if table in (e.get("writes") or "") and e.get("data_mode") in ("prod", "dev"):
                return e["data_mode"]
        modes = {e.get("data_mode") for e in entries if e.get("data_mode") in ("prod", "dev")}
        return modes.pop() if len(modes) == 1 else None

    # --- frameworks: folder -> monitor stems (from depends_on), envelope, versions
    fw_by_monitor: dict[str, str] = {}
    fw_meta: dict[str, dict] = {}
    for folder in sorted((ROOT / "frameworks").iterdir()):
        if not folder.is_dir():
            continue
        versions = sorted(p for p in folder.glob("*.md") if p.name != "README.md")
        if not versions:
            continue
        fms = [(p, parse(p)) for p in versions]
        for p, fm in fms:
            for d in as_items(fm.get("depends_on")):
                fw_by_monitor.setdefault(d, folder.name)
        latest_p, latest = fms[-1]
        usd, usd_from, usd_status, retired_note = None, None, None, None
        for p, fm in reversed(fms):
            v = fm.get("prearranged_funding_usd")
            if not (isinstance(v, (int, float)) and v > 0):
                continue
            if str(fm.get("status") or "").startswith("retired"):
                retired_note = retired_note or f"The retired {p.stem} version carried ${float(v)/1e6:.1f}M."
                continue
            usd, usd_from, usd_status = float(v), p.stem, fm.get("status")
            break
        title = None
        readme = folder / "README.md"
        if readme.exists():
            m = re.search(r"^#\s+(.+)$", readme.read_text(encoding="utf-8"), re.M)
            if m:
                title = re.sub(r"\s*[—–-]\s*`?[a-z0-9-]+`?\s*$", "", m.group(1).strip())
        if not title or title.lower().replace(" ", "-") == folder.name:
            iso, _, hz = folder.name.partition("-")
            title = f"{iso.upper()} {hz.replace('-', ' ')}"
        m = re.match(r"([A-Z]{3})\b(.*)", title)
        if m and m.group(1) in ISO3:
            title = ISO3[m.group(1)] + m.group(2)
        # a version's status can carry an inline comment; keep the first word, then apply the catalog's lifecycle rule
        stored = str(latest.get("status") or "").split()[0] if latest.get("status") else ""
        lstat = display_status(stored, latest.get("activations"), latest.get("version"), latest.get("valid_until")) or "—"
        note = []
        if usd is not None:
            note.append(f"${usd/1e6:.1f}M pre-arranged on version {usd_from} ({str(usd_status).split()[0] if usd_status else '—'}).")
            if usd_from != latest_p.stem:
                note.append(f"Latest version {latest_p.stem} ({lstat}) records no envelope.")
        else:
            note.append(f"No pre-arranged envelope recorded on a current version; latest is {latest_p.stem} ({lstat}).")
            if retired_note:
                note.append(retired_note)
        links = [{"label": f"KB · {latest_p.stem} ({lstat})", "url": f"{KB_BLOB}/frameworks/{folder.name}/{latest_p.name}"}]
        if usd_from and usd_from != latest_p.stem:
            links.insert(0, {"label": f"KB · {usd_from} (${usd/1e6:.1f}M)", "url": f"{KB_BLOB}/frameworks/{folder.name}/{usd_from}.md"})
        fw_meta[folder.name] = {"id": f"f_{folder.name}", "name": title, "usd": usd, "usdNote": " ".join(note), "links": links,
                                "latest": latest_p.stem, "status": lstat, "active": lstat in ACTIVE_STATES}

    # --- pages
    ov_nodes = ov.get("nodes") or {}
    ignore = ov.get("ignore") or {}
    merged_into = {m: k for k, v in ov_nodes.items() for m in (v.get("merge") or [])}
    pages: dict[str, dict] = {}
    for folder in ("pipelines", "apps"):
        for p in sorted((ROOT / folder).glob("*.md")):
            if p.name in ("README.md", "_TEMPLATE.md"):
                continue
            fm = parse(p)
            reads, writes = set(), set()     # (table, stage)
            for item in as_items(fm.get("inputs")):
                for t in match_tables(item, all_tables):
                    for st in (stages_in(item) or {None}):
                        reads.add((t, st))
            for item in as_items(fm.get("outputs")):
                for t in match_tables(item, all_tables):
                    for st in (stages_in(item) or {None}):
                        writes.add((t, st))
            pages[p.stem] = {"stem": p.stem, "folder": folder, "fm": fm, "reads": reads, "writes": writes}

    def resolve_stage(t: str, st, repo: str, writing: bool) -> str:
        if st in ("prod", "dev"):
            return st
        if writing:
            m = writer_mode(repo, t)
            if m:
                return m
        if t in prod and t not in dev:
            return "prod"
        if t in dev and t not in prod:
            return "dev"
        return "prod"

    def runtime_of(fm: dict, stem: str) -> list[str]:
        dep = fm.get("deployment") or {}
        rts = []
        plat = str(dep.get("platform") or "").strip()
        if plat in PLATFORM_RT:
            rts.append(PLATFORM_RT[plat])
        for j in dep.get("jobs") or []:
            j = j or {}
            if str(j.get("status") or "live") not in ("live",):
                continue
            ref = str(j.get("ref") or "")
            if ".github/workflows/" in ref and "gha" not in rts:
                rts.append("gha")
            if re.search(r"\b\d{12,16}\b", ref) or "databricks.yml" in ref:
                if "dbx" not in rts:
                    rts.append("dbx")
        return rts or ["man"]

    def links_of(fm: dict, stem: str, folder: str) -> list[dict]:
        L = []
        repo = fm.get("source_repo")
        if repo:
            L.append({"label": f"Repo · {repo.split('/')[-1]}", "url": f"https://github.com/{repo}"})
        dep = fm.get("deployment") or {}
        seen = set()
        for j in dep.get("jobs") or []:
            j = j or {}
            ref, name, status = str(j.get("ref") or ""), str(j.get("name") or ""), str(j.get("status") or "")
            if status and status not in ("live", "paused"):
                continue
            m = re.search(r"\.github/workflows/([\w.\-()]+\.ya?ml)", ref)
            if m and repo and m.group(1) not in seen and "keep_awake" not in m.group(1):
                seen.add(m.group(1))
                L.append({"label": f"Workflow · {m.group(1)}", "url": f"https://github.com/{repo}/actions/workflows/{m.group(1)}"})
            for jid in re.findall(r"\b(\d{12,16})\b", ref):
                if jid not in seen:
                    seen.add(jid)
                    L.append({"label": f"Databricks · {name or jid}", "url": DBX_JOB + jid})
        if dep.get("url"):
            L.append({"label": "Azure app", "url": str(dep["url"])})
        for s in (fm.get("surfaces") or [])[:4]:
            if isinstance(s, dict) and s.get("url") and not s.get("auto"):
                L.append({"label": str(s.get("title") or "Published page")[:60], "url": s["url"]})
        L.append({"label": "KB page", "url": f"{KB_BLOB}/{folder}/{stem}.md"})
        return L

    def health_of(repos: list[str]) -> tuple[str, list[dict]]:
        jobs = []
        for r in repos:
            for e in by_repo.get(r.lower(), []):
                if e.get("category") != "prod":
                    continue
                jobs.append({"name": e.get("name"), "status": e.get("_status") or "—", "flags": ", ".join(e.get("_flags") or []),
                             "cadence": e.get("cadence") or "", "age_h": e.get("success_age_h"),
                             "url": e.get("url") or (DBX_JOB + e["job_id"] if e.get("job_id") else None)})
        worst = max(jobs, key=lambda j: STATUS_RANK.get(j["status"], -1), default=None)
        return (worst["status"] if worst else "—"), jobs

    nodes: list[dict] = []
    gaps: list[str] = []
    for stem, pg in pages.items():
        if stem in ignore or stem in merged_into:
            continue
        o = ov_nodes.get(stem) or {}
        members = [pg] + [pages[m] for m in (o.get("merge") or []) if m in pages]
        touches = any(m["reads"] or m["writes"] for m in members)
        if not touches and not o:
            continue
        fm = pg["fm"]
        repo = fm.get("source_repo") or ""
        reads_g, writes_g, tables_txt = set(), set(), []
        for m in members:
            mrepo = m["fm"].get("source_repo") or repo
            for t, st in sorted(m["writes"]):
                stage = resolve_stage(t, st, mrepo, True)
                writes_g.add(group_for(t, stage)); tables_txt.append(f"writes {t} ({stage})")
            for t, st in sorted(m["reads"]):
                stage = resolve_stage(t, st, mrepo, False)
                reads_g.add(group_for(t, stage)); tables_txt.append(f"reads {t} ({stage})")
        reads_g.update(o.get("reads") or [])
        writes_g.update(o.get("writes") or [])
        role = o.get("role") or ("monitor" if str(fm.get("type") or "") == "monitoring" else "backend" if writes_g and not reads_g else "other")
        framework = o.get("framework") or fw_by_monitor.get(stem)
        if role != "monitor":
            framework = o.get("framework")
        rts = []
        for m in members:
            for r in runtime_of(m["fm"], m["stem"]):
                if r not in rts:
                    rts.append(r)
        rts = o.get("runtime") or rts
        links = []
        for m in members:
            links += links_of(m["fm"], m["stem"], m["folder"])
        links += o.get("links") or []
        if framework and framework in fw_meta:
            links += fw_meta[framework]["links"]
        repos = sorted({m["fm"].get("source_repo") for m in members if m["fm"].get("source_repo")})
        status, jobs = health_of(repos)
        impact = o.get("impact")
        if not impact:
            gaps.append(f"{stem} — no impact statement in db-network.yml")
            impact = "No impact statement recorded yet — see the KB page."
        nodes.append({
            "id": stem, "col": 1 if role == "backend" else 3, "name": o.get("label") or fm.get("name") or stem,
            "meta": o.get("meta") or str(fm.get("type") or fm.get("tech") or pg["folder"][:-1]),
            "rt": rts, "role": role, "fwRef": f"f_{framework}" if framework and framework in fw_meta else None,
            "reads": sorted(reads_g), "writes": sorted(writes_g), "unverified": o.get("unverified"),
            "status": status, "jobs": jobs, "repo": ", ".join(repos) or "—",
            "tables": "; ".join(tables_txt) or o.get("tables") or "—", "impact": impact, "links": links,
        })

    for x in ov.get("extra_nodes") or []:
        framework = x.get("framework")
        links = []
        if x.get("repo"):
            links.append({"label": f"Repo · {x['repo'].split('/')[-1]}", "url": f"https://github.com/{x['repo']}"})
        links += x.get("links") or []
        if framework and framework in fw_meta:
            links += fw_meta[framework]["links"]
        status, jobs = health_of([x["repo"]] if x.get("repo") else [])
        for gid in list(x.get("reads") or []) + list(x.get("writes") or []):
            if gid not in groups:
                sys.exit(f"ERROR: extra node {x['id']} references unknown table group {gid}")
        nodes.append({
            "id": x["id"], "col": 1 if x.get("role") == "backend" else 3, "name": x["label"], "meta": x.get("meta") or "",
            "rt": x.get("runtime") or ["man"], "role": x.get("role") or "other",
            "fwRef": f"f_{framework}" if framework and framework in fw_meta else None,
            "reads": x.get("reads") or [], "writes": x.get("writes") or [], "unverified": x.get("unverified"),
            "status": status, "jobs": jobs, "repo": x.get("repo") or "—", "tables": x.get("tables") or "—",
            "impact": x.get("impact") or "No impact statement recorded yet.", "links": links,
        })
        if not x.get("impact"):
            gaps.append(f"{x['id']} — extra node without an impact statement")

    # --- shared services: a backend node, its table group, and every page whose depends_on names it
    node_by_id = {n["id"]: n for n in nodes}
    fw_direct: list[tuple[str, str]] = []      # (group id, framework folder) for frameworks depending on a service directly
    for svc in ov.get("services") or []:
        gid = svc["group"]["id"]
        status, jobs = health_of([svc["repo"]] if svc.get("repo") else [])
        nodes.append({
            "id": svc["id"], "col": 1, "name": svc["label"], "meta": svc.get("meta") or "", "rt": svc.get("runtime") or ["web"],
            "role": "backend", "fwRef": None, "reads": [gid], "writes": [gid], "unverified": svc.get("unverified"),
            "status": status, "jobs": jobs, "repo": svc.get("repo") or "—", "tables": svc.get("tables") or "—",
            "impact": svc.get("impact") or "No impact statement recorded yet.", "links": svc.get("links") or [],
        })
        for stem, pg in pages.items():
            if svc["key"] not in as_items(pg["fm"].get("depends_on")) or stem in ignore:
                continue
            target = merged_into.get(stem, stem)
            if target in node_by_id:
                n = node_by_id[target]
                if gid not in n["reads"]:
                    n["reads"].append(gid)
                n.setdefault("via", []).append(svc["label"])
                continue
            fm = pg["fm"]
            o = ov_nodes.get(stem) or {}
            role = o.get("role") or ("monitor" if str(fm.get("type") or "") == "monitoring" else "other")
            framework = o.get("framework") or (fw_by_monitor.get(stem) if role == "monitor" else None)
            repo = fm.get("source_repo") or ""
            st, jb = health_of([repo] if repo else [])
            impact = o.get("impact")
            if not impact:
                gaps.append(f"{stem} — depends on {svc['label']} but has no impact statement in db-network.yml")
                impact = "No impact statement recorded yet — see the KB page."
            n = {"id": stem, "col": 3, "name": o.get("label") or fm.get("name") or stem,
                 "meta": o.get("meta") or str(fm.get("type") or pg["folder"][:-1]), "rt": o.get("runtime") or runtime_of(fm, stem),
                 "role": role, "fwRef": f"f_{framework}" if framework and framework in fw_meta else None,
                 "reads": [gid], "writes": [], "unverified": o.get("unverified"), "status": st, "jobs": jb, "repo": repo or "—",
                 "tables": f"no direct database access on its page; depends on {svc['label']}", "impact": impact,
                 "links": links_of(fm, stem, pg["folder"]) + (o.get("links") or []) + (fw_meta[framework]["links"] if framework in fw_meta else []),
                 "via": [svc["label"]]}
            nodes.append(n); node_by_id[stem] = n
        for folder, meta in fw_meta.items():
            for p in (ROOT / "frameworks" / folder).glob("*.md"):
                if p.name != "README.md" and svc["key"] in as_items(parse(p).get("depends_on")):
                    fw_direct.append((gid, folder)); break

    # frameworks that appear on the map
    used_fw = {n["fwRef"] for n in nodes if n["fwRef"]} | {fw_meta[f]["id"] for _, f in fw_direct}
    frameworks = [dict(fw_meta[k], unverified=any(n["unverified"] for n in nodes if n["fwRef"] == fw_meta[k]["id"] and n["role"] == "monitor"))
                  for k in sorted(fw_meta) if fw_meta[k]["id"] in used_fw]
    for f in frameworks:
        f["unverified"] = bool(f["unverified"]) and not any(n["fwRef"] == f["id"] and n["role"] == "monitor" and not n["unverified"] for n in nodes)

    # table groups actually used, in overlay order then auto groups
    used = {g for n in nodes for g in n["reads"] + n["writes"]} | {gid for gid, _ in fw_direct}
    tables = [{"id": g["id"], "db": g["db"], "label": g["label"], "tables": sorted(g["tables"]), "links": g["links"]}
              for g in groups.values() if g["id"] in used]

    # orphan dev reads: dev groups with readers but no writer on the map
    writers = {g for n in nodes for g in n["writes"]}
    for t in tables:
        if t["db"] == "dev" and t["id"] not in writers:
            readers = [n["name"] for n in nodes if t["id"] in n["reads"]]
            gaps.append(f"dev table group '{t['label']}' is read by {', '.join(readers)} but nothing on the map writes it — "
                        f"likely a page still declaring a dev-stage read after the 2026-09-22 dev cutover")

    # --- recipients: Listmonk list sizes per node (overlay `lists` / `list_tags`), when a snapshot exists
    lm = json.loads(LISTMONK.read_text(encoding="utf-8")) if LISTMONK.exists() else None
    lm_lists = {int(x["id"]): x for x in (lm or {}).get("lists") or []}
    for n in nodes:
        o = (ov_nodes.get(n["id"]) or {}) if n["id"] in ov_nodes else next((x for x in (ov.get("extra_nodes") or []) if x["id"] == n["id"]), {})
        ids = [int(i) for i in (o.get("lists") or [])]
        tags = list(o.get("list_tags") or [])
        if tags and lm_lists:
            ids += [i for i, x in lm_lists.items() if set(x.get("tags") or []) & set(tags) and i not in ids]
        if not ids and not tags:
            continue
        rows = [{"id": i, "name": (lm_lists.get(i) or {}).get("name"), "count": (lm_lists.get(i) or {}).get("subscriber_count")} for i in sorted(set(ids))]
        n["lists"] = rows
        n["list_tags"] = tags
        known = [r["count"] for r in rows if isinstance(r.get("count"), int)]
        n["recipients"] = sum(known) if known and len(known) == len(rows) else None
    listmonk_meta = {"snapshot": (lm or {}).get("generated"), "lists": len(lm_lists),
                     "memberships": sum(x.get("subscriber_count") or 0 for x in lm_lists.values())} if lm else None

    # --- recommendations, derived from the same data -----------------------------------------------
    readers = {g for n in nodes for g in n["reads"]} | {gid for gid, _ in fw_direct}
    service_ids = {sv["id"] for sv in ov.get("services") or []}
    fw_by_id = {f["id"]: f for f in frameworks}

    # the same edge set the page draws, so "downstream" here equals a click on the page
    edges: list[tuple[str, str]] = []
    for n in nodes:
        edges += [(n["id"], g) for g in n["writes"]] + [(g, n["id"]) for g in n["reads"]]
        if n["fwRef"] and n["fwRef"] in fw_by_id:
            edges.append((n["id"], n["fwRef"]))
    edges += [(gid, fw_meta[f]["id"]) for gid, f in fw_direct]
    succ: dict[str, set] = defaultdict(set)
    for a, b in edges:
        succ[a].add(b)

    def downstream(start: str) -> set:
        seen, q = set(), [start]
        while q:
            cur = q.pop()
            for nxt in succ.get(cur, ()):
                if nxt not in seen:
                    seen.add(nxt); q.append(nxt)
        return seen

    node_by_id = {n["id"]: n for n in nodes}
    DEAD_H = 24 * 30      # a month without a success is "long dead" for anything scheduled

    # ---- Pruning: long dead · zero connections · already stopped
    prune: list[dict] = []
    for n in nodes:
        for j in n.get("jobs") or []:
            fl = j.get("flags") or ""
            age = j.get("age_h")
            jl = ([{"label": "Job run · " + str(j["name"]), "url": j["url"]}] if j.get("url") else []) + [l for l in n["links"] if l["label"].startswith("Repo")]
            if "NO-SUCCESS" in fl:
                prune.append({"group": "Long dead", "item": f"{n['name']} · {j['name']}", "node": n["id"], "links": jl, "why": f"has never succeeded ({j['status']}, {fl}). Delete the job definition, or fix it and give it an on_failure recipient."})
            elif "PAUSED" in fl:
                prune.append({"group": "Long dead", "item": f"{n['name']} · {j['name']}", "node": n["id"], "links": jl, "why": "paused in the registry. A paused schedule still holds secrets and a cluster reference; retire it or un-pause deliberately."})
            elif isinstance(age, (int, float)) and age > DEAD_H and "SEASONAL" not in fl:
                prune.append({"group": "Long dead", "item": f"{n['name']} · {j['name']}", "node": n["id"], "links": jl, "why": f"last success {age/24:.0f} days ago ({j['status']}, {fl}); its cadence is {j.get('cadence') or 'unknown'}. Retire it explicitly or revive it."})
    for t in tables:
        if t["id"] in writers and t["id"] not in readers:
            w = [n["name"] for n in nodes if t["id"] in n["writes"]]
            prune.append({"group": "Zero connections", "item": t["label"], "node": t["id"], "links": t["links"], "why": f"{t['db']} tables written by {', '.join(w)} that nothing on the map reads. Confirm a consumer outside the KB, or stop writing them."})
    for n in nodes:
        if n["col"] == 1 and n["id"] not in service_ids and n["writes"] and not any(g in readers for g in n["writes"]):
            prune.append({"group": "Zero connections", "item": n["name"], "node": n["id"], "links": n["links"], "why": "backend whose tables no monitor, alert, app or analysis reads."})
        if n["col"] == 3 and n["reads"] and all(g not in writers for g in n["reads"]):
            prune.append({"group": "Zero connections", "item": n["name"], "node": n["id"], "links": n["links"], "why": "every table it reads has no writer on the map — since 2026-09-22 that means a dev-stage read of a server that is unreachable. Repoint or retire."})
    for k, v in ignore.items():
        if any(w in v.lower() for w in ("stopped", "retired", "superseded", "failing", "dead")):
            pg = pages.get(k)
            kl = links_of(pg["fm"], k, pg["folder"]) if pg else []
            prune.append({"group": "Already stopped or superseded", "item": k, "node": None, "links": kl, "why": v + ". Delete the app, job or repo so it stops appearing in registries."})
    for n in nodes:
        if n["role"] == "monitor" and n["fwRef"] in fw_by_id and not fw_by_id[n["fwRef"]]["active"]:
            prune.append({"group": "Review", "item": n["name"], "node": n["id"], "links": n["links"], "why": f"{fw_by_id[n['fwRef']]['name']}'s latest version is {fw_by_id[n['fwRef']]['status']}. Pause the monitor until the version is endorsed, or fix the framework page's status if it is in fact live."})
        if n.get("unverified"):
            prune.append({"group": "Review", "item": n["name"], "node": n["id"], "links": n["links"], "why": f"{n['unverified']}. Verify in the repo, then document the tables or drop it from the map."})
    for x in ov.get("prune_notes") or []:
        prune.append({"group": x.get("group") or "Review", "item": x["item"], "node": x.get("node"), "links": x.get("links") or [], "why": x["why"]})
    seen_keys: set = set(); dedup = []
    for x in prune:
        key = (x["group"], x["item"].split(" · ")[-1])
        if key not in seen_keys:
            seen_keys.add(key); dedup.append(x)
    order = ["Long dead", "Zero connections", "Already stopped or superseded", "Review"]
    prune = sorted(dedup, key=lambda x: (order.index(x["group"]) if x["group"] in order else 99, x["item"]))

    # ---- Migration priority: what is mission-critical, by how much hangs off it
    def score(n: dict) -> dict:
        d = downstream(n["id"])
        fws = [fw_by_id[x] for x in d if x in fw_by_id]
        mons = [node_by_id[x] for x in d if x in node_by_id and node_by_id[x]["role"] == "monitor"]
        others = [x for x in d if x in node_by_id and node_by_id[x]["role"] != "monitor"]
        usd = sum(f["usd"] or 0 for f in fws if f["active"])
        rec = sum(node_by_id[x].get("recipients") or 0 for x in d if x in node_by_id) + (n.get("recipients") or 0)
        own_fw = fw_by_id.get(n["fwRef"]) if n["fwRef"] else None
        if own_fw:
            fws = fws or [own_fw]
            usd = usd or (own_fw["usd"] or 0 if own_fw["active"] else 0)
        active_fws = [f for f in fws if f["active"]]
        val = 4 * len(active_fws) + 1 * (len(fws) - len(active_fws)) + 2 * len(mons) + 0.5 * len(others) + usd / 1e6 + (1 if n["role"] == "monitor" else 0)
        return {"score": round(val, 1), "frameworks": sorted(f["name"] for f in fws), "active_frameworks": len(active_fws), "monitors": len(mons),
                "others": len(others), "usd": usd, "recipients": rec}
    migrate_dbx, migrate_prod = [], []
    for n in nodes:
        if n["id"] in service_ids:
            sc = score(n)
        else:
            sc = score(n)
        # a node's own dev exposure excludes service groups: Listmonk's dev database is Listmonk's row to fix
        svc_groups = {sv["group"]["id"] for sv in ov.get("services") or []}
        own = [g for g in n["reads"] + n["writes"] if g in groups and (g not in svc_groups or n["id"] in service_ids)]
        dbs = sorted({groups[g]["db"] for g in own})
        inactive = len(sc["frameworks"]) - sc["active_frameworks"]
        why = (f"{sc['active_frameworks']} active framework{'s' if sc['active_frameworks'] != 1 else ''}"
               + (f" (${sc['usd']/1e6:.1f}M)" if sc["usd"] else "")
               + (f", {inactive} not active" if inactive else "")
               + (f", {sc['monitors']} monitor{'s' if sc['monitors'] != 1 else ''}" if sc["monitors"] else "")
               + (f", {sc['others']} other consumer{'s' if sc['others'] != 1 else ''}" if sc["others"] else "")
               + (f", {sc['recipients']} email recipients" if sc["recipients"] else "")
               + (f" · frameworks: {', '.join(sc['frameworks'])}" if sc["frameworks"] else ""))
        row = {"item": n["name"], "node": n["id"], "links": n["links"], "score": sc["score"], "why": why, "rt": n["rt"], "dbs": dbs, "role": n["role"]}
        if "gha" in n["rt"] or "man" in n["rt"]:
            migrate_dbx.append(dict(row, note=("runs on GitHub-hosted runners" if "gha" in n["rt"] else "runs by hand from a laptop") + " — no private route to the databases"))
        if "dev" in dbs:
            migrate_prod.append(dict(row, note=("still declares dev-stage " + ("writes" if any(groups[g]["db"] == "dev" for g in n["writes"]) else "reads")) + " — the dev server lost public access on 2026-09-22"))
    def split(rows):
        rows.sort(key=lambda r: (-r["score"], r["item"]))
        return {"ranked": [r for r in rows if r["score"] > 0], "rest": [r["item"] for r in rows if r["score"] <= 0]}
    migrate_dbx, migrate_prod = split(migrate_dbx), split(migrate_prod)

    notes = ov.get("notes") or {}
    direct = [{"from": gid, "to": fw_meta[f]["id"]} for gid, f in fw_direct]
    return {"tables": tables, "pipes": nodes, "frameworks": frameworks, "direct": direct, "prune": prune, "listmonk": listmonk_meta,
            "migrate": {"databricks": migrate_dbx, "prod": migrate_prod},
            "meta": {"registry_snapshot": registry.get("generated") or "?", "gaps": gaps, "notes": notes,
                     "ignored": [f"{k} — {v}" for k, v in ignore.items()]}}


# ----------------------------------------------------------------------------- page

def render(data: dict) -> str:
    notes = data["meta"]["notes"]
    def li(items):
        return "".join(f"<li>{_html.escape(str(x))}</li>" for x in items)
    gaps_html = f"<h3>Unreviewed</h3><ul>{li(data['meta']['gaps'])}</ul>" if data["meta"]["gaps"] else ""
    ignored_html = f"<h3>Left off the map on purpose</h3><ul>{li(data['meta']['ignored'])}</ul>" if data["meta"]["ignored"] else ""
    context_html = f"<h3>Context</h3><p>{_html.escape(notes.get('context',''))}</p>" if notes.get("context") else ""
    mitig = notes.get("mitigations") or []
    groups_p: dict[str, list] = {}
    for x in data.get("prune") or []:
        groups_p.setdefault(x["group"], []).append(x)
    def chips(links, node=None, limit=6):
        out = "".join(f"<a href=\"{_html.escape(l['url'])}\" target=\"_blank\" rel=\"noopener\">{_html.escape(l['label'])}</a>" for l in (links or [])[:limit] if l.get("url"))
        if node:
            out = f"<button type=\"button\" class=\"chip-btn\" data-select=\"{_html.escape(node)}\">Show on map</button>" + out
        return f"<div class=\"links\">{out}</div>" if out else ""
    prune_html = "".join(f"<h3>{_html.escape(g)}</h3><ul>" + "".join(f"<li><strong>{_html.escape(x['item'])}</strong> — {_html.escape(x['why'])}{chips(x.get('links'), x.get('node'))}</li>" for x in xs) + "</ul>"
                         for g, xs in groups_p.items()) or "<p>No pruning candidates found.</p>"
    def mig_table(block):
        rows, rest = (block or {}).get("ranked") or [], (block or {}).get("rest") or []
        tail = f"<p class=\"meta\">Nothing downstream on the map, so no priority from this view: {_html.escape(', '.join(rest))}.</p>" if rest else ""
        if not rows:
            return "<p>Nothing to migrate.</p>" + tail
        body = "".join(f"<tr><td class=\"rank\">{i+1}</td><td><strong>{_html.escape(r['item'])}</strong><br><span class=\"small\">{_html.escape(r['note'])}</span></td>"
                       f"<td class=\"num\">{r['score']:g}</td><td>{_html.escape(r['why'])}{chips(r.get('links'), r.get('node'), 5)}</td></tr>" for i, r in enumerate(rows))
        return f"<table class=\"mig\"><thead><tr><th>#</th><th>Pipeline / app</th><th>Score</th><th>What hangs off it</th></tr></thead><tbody>{body}</tbody></table>" + tail
    mig = data.get("migrate") or {}
    migrate_html = ("<h3>Move to Databricks (off GitHub-hosted runners and laptops)</h3>" + mig_table(mig.get("databricks"))
                    + "<h3>Move to the prod database (off dev)</h3>" + mig_table(mig.get("prod"))
                    + "<p class=\"meta\">Score = 4 per active CERF framework downstream + 1 per inactive one + 2 per framework monitor + 0.5 per other consumer + the active frameworks' pre-arranged envelope in $M, +1 if the item is itself a monitor. Downstream is the same chain a click on the map highlights. A high score means many systems, frameworks and dollars stop when this item loses its database path.</p>")
    lmm = data.get("listmonk")
    listmonk_html = (f"Recipient counts come from the Listmonk lists snapshot of {_html.escape(str(lmm['snapshot']))} "
                     f"({lmm['lists']} lists, {lmm['memberships']} list memberships); counts are memberships per list, not de-duplicated people."
                     if lmm else "Recipient counts are not shown yet: no Listmonk lists snapshot is committed. Run <code>scripts/gen_listmonk_lists.py</code> "
                                 "with the DSCI_LISTMONK_* secrets (or enable the weekly listmonk-lists.yml workflow) and the map will show how many people each alert pipeline reaches.")
    payload = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    return TEMPLATE.replace("__DATA__", payload) \
        .replace("__SNAPSHOT__", _html.escape(str(data["meta"]["registry_snapshot"]))) \
        .replace("__CONTEXT__", context_html) \
        .replace("__MONEY__", _html.escape(notes.get("money", ""))) \
        .replace("__NOT_AFFECTED__", _html.escape(notes.get("not_affected", ""))) \
        .replace("__MITIGATIONS__", li(mitig)) \
        .replace("__GAPS__", gaps_html) \
        .replace("__IGNORED__", ignored_html) \
        .replace("__PRUNE__", prune_html) \
        .replace("__MIGRATE__", migrate_html) \
        .replace("__LISTMONK__", listmonk_html)


TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="generator" content="ds-knowledge-base scripts/gen_db_network.py">
<title>DSCI Database Network</title>
<style>
  :root {
    color-scheme: light;
    --page:#ffffff; --surface:#ffffff; --tint:#f3f4f2; --ink:#0b0b0b; --ink2:#52514e; --muted:#898781; --grid:#e1e0d9; --axis:#c3c2b7; --ring:rgba(11,11,11,.10);
    --gha:#2a78d6; --dbx:#eb6834; --web:#1baf7a; --man:#eda100;
    --critical:#d03b3b; --focus:#2a78d6;
    --read:#cfcec8; --write:#0b0b0b;
  }
  * { box-sizing:border-box; }
  html, body { height:100%; }
  body { margin:0; background:var(--page); color:var(--ink); font:13px/1.4 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif; overflow:hidden; }
  .app { height:100%; display:grid; grid-template-rows:auto 1fr; gap:8px; padding:10px 14px 12px; }
  header { display:flex; flex-wrap:wrap; align-items:flex-end; justify-content:space-between; gap:8px 24px; }
  h1 { font-size:19px; margin:0; line-height:1.2; }
  .filters { display:flex; flex-wrap:wrap; gap:8px 16px; align-items:center; }
  .fgroup { display:flex; align-items:center; gap:6px; }
  .fgroup > span { font-size:11px; text-transform:uppercase; letter-spacing:.05em; color:var(--muted); }
  .seg { display:inline-flex; border:1px solid var(--axis); border-radius:6px; overflow:hidden; background:var(--surface); }
  .seg button { border:0; background:transparent; color:var(--ink2); font:12px system-ui,sans-serif; padding:4px 9px; cursor:pointer; border-right:1px solid var(--grid); display:flex; align-items:center; gap:5px; }
  .seg button:last-child { border-right:0; }
  .seg button[aria-pressed="true"] { background:var(--ink); color:var(--surface); }
  .seg button:focus-visible, .btn:focus-visible { outline:2px solid var(--focus); outline-offset:-2px; }
  .dot { width:9px; height:9px; border-radius:50%; display:inline-block; }
  .btn { border:1px solid var(--axis); background:var(--surface); color:var(--ink2); border-radius:6px; padding:4px 9px; font:12px system-ui,sans-serif; cursor:pointer; }

  .diag { position:relative; background:var(--surface); border:1px solid var(--ring); border-radius:8px; padding:10px 18px 10px; display:grid; grid-template-rows:auto 1fr; min-height:0; overflow:hidden; }
  .colheads, .cols { display:grid; grid-template-columns:1fr .9fr 1.05fr .95fr; gap:0 48px; }
  .colheads { margin-bottom:8px; }
  .colheads div { font-size:11px; text-transform:uppercase; letter-spacing:.05em; color:var(--muted); padding-left:2px; display:flex; justify-content:space-between; gap:8px; }
  .colheads .legend { text-transform:none; letter-spacing:0; color:var(--ink2); display:flex; gap:12px; align-items:center; }
  .colheads .legend[hidden] { display:none; }
  .legend span { display:inline-flex; align-items:center; gap:5px; }
  .legend svg { width:26px; height:6px; overflow:visible; }
  .legend line { stroke:var(--focus); stroke-width:1.5; }
  .legend line.r { stroke-dasharray:4 3; }
  .cols { min-height:0; position:relative; overflow:hidden; }
  .col { display:flex; flex-direction:column; justify-content:space-evenly; gap:3px; min-width:0; min-height:0; position:relative; z-index:2; }
  .node { position:relative; cursor:pointer; transition:opacity .18s; text-align:left; font:inherit; color:inherit; width:100%; border:0; background:transparent; padding:0; }
  .node:focus-visible { outline:2px solid var(--focus); outline-offset:2px; }
  .node.dim { opacity:.14; }
  .node.hov { box-shadow:0 0 0 1.5px var(--ink2); }
  .node.tbl.hov, .node.fw.hov { box-shadow:inset 0 0 0 1.5px var(--ink2); }
  .node.sel.hov { box-shadow:0 0 0 2px var(--ink); }

  .node.pipe { border:1px solid var(--ring); border-radius:5px; padding:4px 8px 4px 11px; background:var(--surface); }
  .node.pipe::before { content:""; position:absolute; left:0; top:0; bottom:0; width:4px; border-radius:6px 0 0 6px; background:var(--stripe, var(--axis)); }
  .node.pipe.two::before { background:linear-gradient(to bottom, var(--stripe) 50%, var(--stripe2) 50%); }
  .node.pipe:hover, .node.pipe.sel { border-color:var(--ink); }
  .node.pipe.sel { box-shadow:0 0 0 2px var(--ink); }
  .node .t { font-weight:600; font-size:12px; line-height:1.25; display:flex; align-items:center; gap:6px; flex-wrap:wrap; }
  .node .m { color:var(--muted); font-size:10.5px; margin-top:1px; line-height:1.3; display:flex; flex-wrap:wrap; gap:2px 5px; align-items:center; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
  .node .m > span:first-child { overflow:hidden; text-overflow:ellipsis; }
  .tag { font:10px/1.35 ui-monospace,Menlo,monospace; padding:0 4px; border-radius:3px; border:1px solid var(--axis); color:var(--ink2); white-space:nowrap; }
  .tag.prod { background:var(--ink); color:var(--surface); border-color:var(--ink); }
  .tag.rt { border:0; color:var(--surface); font-weight:600; }
  .tag.warn { border-style:dashed; }
  .tag.w { border-color:var(--ink); color:var(--ink); font-weight:600; }
  .health { font-size:10.5px; color:var(--critical); font-weight:600; }

  .dbgroup { border:1px solid var(--axis); background:var(--tint); border-radius:7px; padding:0 6px 5px; display:flex; flex-direction:column; gap:0; position:relative; }
  .dbgroup .gh { font:600 10.5px/1.3 ui-monospace,Menlo,monospace; letter-spacing:.04em; text-transform:uppercase; color:var(--ink2); padding:5px 0 4px; margin-bottom:2px; border-bottom:1px solid var(--axis); display:flex; align-items:center; gap:6px; }
  .dbgroup .gh .tag { font-size:10.5px; }
  .node.tbl { display:flex; align-items:center; gap:8px; padding:3px 6px; border-radius:4px; border-top:1px solid var(--grid); }
  .node.tbl:first-of-type { border-top:0; }
  .node.tbl:hover, .node.tbl.sel { background:var(--surface); }
  .node.tbl.sel { box-shadow:inset 0 0 0 1.5px var(--ink); }
  .node.tbl .t { font-family:ui-monospace,Menlo,monospace; font-weight:500; font-size:11px; line-height:1.3; }

  #c4 { justify-content:flex-start; gap:12px; }
  .fwlist { flex:0 0 auto; display:flex; flex-direction:column; gap:0; }
  .node.fw { display:grid; grid-template-columns:1fr auto; gap:0 10px; align-items:baseline; padding:3px 4px; border-bottom:1px solid var(--grid); border-radius:0; }
  .node.fw:hover, .node.fw.sel { background:var(--tint); }
  .node.fw.sel { box-shadow:inset 0 0 0 1.5px var(--ink); }
  .node.fw .n { font-weight:600; font-size:12.5px; }
  .node.fw .usd { font-variant-numeric:tabular-nums; font-size:12.5px; font-weight:600; text-align:right; }
  .node.fw.inactive { opacity:.45; }
  .node.fw.inactive .n, .node.fw.inactive .usd { font-weight:500; }
  .node.fw .st { font:10px/1.3 ui-monospace,Menlo,monospace; color:var(--muted); margin-left:4px; }
  .node.fw.inactive.sel, .node.fw.inactive.hov { opacity:.85; }

  .side { flex:1 1 auto; min-height:0; background:var(--tint); border:1px solid var(--ring); border-radius:8px; padding:12px 14px; overflow-y:auto; overflow-x:hidden; font-size:12px; line-height:1.4; overflow-wrap:anywhere; word-break:break-word; min-width:0; }
  .side * { max-width:100%; min-width:0; }
  .side h2 { font-size:13px; margin:0 0 6px; }
  .side .kv { display:grid; grid-template-columns:minmax(0,auto) minmax(0,1fr); gap:4px 10px; margin:8px 0; }
  .side .kv dt { color:var(--muted); }
  .side .kv dd { margin:0; }
  .side code { font-family:ui-monospace,Menlo,monospace; font-size:11px; }
  .side p { margin:6px 0 0; }
  .side .hint { color:var(--ink2); }
  .side ul { margin:4px 0 0; padding-left:16px; }
  .side li { margin:2px 0; }
  .side .tags { display:flex; flex-wrap:wrap; gap:4px; }
  .side .tag { white-space:normal; }
  .side .links { display:flex; flex-wrap:wrap; gap:4px 6px; margin-top:10px; padding-top:8px; border-top:1px solid var(--grid); }
  .side .links a { font-size:11.5px; color:var(--focus); text-decoration:none; border:1px solid var(--grid); border-radius:4px; padding:1px 6px; white-space:normal; }
  .side .links a:hover { border-color:var(--focus); }
  .side .clear { margin-top:10px; }

  svg.edges { position:absolute; inset:0; width:100%; height:100%; z-index:1; pointer-events:none; overflow:visible; }
  svg.edges path { fill:none; stroke-linejoin:round; stroke-linecap:round; transition:opacity .18s; }
  svg.edges path { stroke:var(--read); stroke-width:1; }
  svg.edges path.hov { stroke:var(--ink2); stroke-width:1.5; }
  svg.edges path.trig { stroke-dasharray:2 4; }
  svg.edges path.dim { opacity:.05; }
  svg.edges path.hi { stroke:var(--focus); stroke-width:1.5; }
  svg.edges path.hi.read { stroke-dasharray:4 3; }
  svg.edges path.hi.trig { stroke-dasharray:2 4; stroke-width:1.25; }

  dialog { border:1px solid var(--ring); border-radius:8px; background:var(--surface); color:var(--ink); max-width:720px; max-height:85vh; overflow:auto; padding:18px 22px; font-size:13px; }
  dialog::backdrop { background:rgba(0,0,0,.35); }
  dialog h3 { margin:12px 0 4px; font-size:13px; }
  dialog h3:first-child { margin-top:0; }
  dialog ul { margin:4px 0; padding-left:18px; }
  dialog li { margin:3px 0; }
  dialog .meta { color:var(--muted); font-size:12px; }
  #dlg-rec { max-width:860px; width:min(860px, 92vw); }
  .tabs { display:flex; gap:0; border-bottom:1px solid var(--axis); margin-bottom:10px; }
  .tab { border:0; background:transparent; color:var(--ink2); font:600 13px system-ui,sans-serif; padding:6px 12px; cursor:pointer; border-bottom:2px solid transparent; margin-bottom:-1px; }
  .tab[aria-selected="true"] { color:var(--ink); border-bottom-color:var(--ink); }
  .tab:focus-visible { outline:2px solid var(--focus); }
  table.mig { border-collapse:collapse; width:100%; font-size:12.5px; margin:4px 0 10px; }
  table.mig th { text-align:left; font-size:11px; text-transform:uppercase; letter-spacing:.04em; color:var(--muted); padding:4px 8px; border-bottom:1px solid var(--axis); }
  table.mig td { padding:6px 8px; border-bottom:1px solid var(--grid); vertical-align:top; }
  table.mig td.rank, table.mig td.num { font-variant-numeric:tabular-nums; white-space:nowrap; text-align:right; }
  table.mig .small { color:var(--muted); font-size:11.5px; }
  dialog .links { display:flex; flex-wrap:wrap; gap:4px 6px; margin-top:4px; }
  dialog .links a, dialog .chip-btn { font:11.5px system-ui,sans-serif; color:var(--focus); text-decoration:none; border:1px solid var(--grid); border-radius:4px; padding:1px 6px; background:transparent; cursor:pointer; }
  dialog .links a:hover, dialog .chip-btn:hover { border-color:var(--focus); }
  dialog .chip-btn { color:var(--ink); border-color:var(--axis); }

  @media (max-height: 720px) { #c3 .node .m { display:none; } #c3 .node.pipe { padding:3px 8px 3px 11px; } }
  body.dense #c3 .node .m { display:none; }
  body.dense #c3 .node.pipe { padding:3px 8px 3px 11px; }
  body.dense #c3.col { gap:2px; }
  @media (max-width: 980px) {
    body { overflow:auto; }
    .app { height:auto; }
    .diag { overflow:visible; }
    .colheads, .cols { gap:0 20px; }
  }
  @media (prefers-reduced-motion: reduce) { .node, svg.edges path { transition:none; } }
</style>
</head>
<body>
<div class="app">
<header>
  <h1>DSCI Database Network</h1>
  <div class="filters" id="filters">
    <div class="fgroup"><span>Runs on</span>
      <div class="seg" data-f="rt">
        <button aria-pressed="true" data-v="all">All</button>
        <button aria-pressed="false" data-v="gha"><i class="dot" style="background:var(--gha)"></i>GitHub Actions</button>
        <button aria-pressed="false" data-v="dbx"><i class="dot" style="background:var(--dbx)"></i>Databricks</button>
        <button aria-pressed="false" data-v="web"><i class="dot" style="background:var(--web)"></i>Azure web app</button>
        <button aria-pressed="false" data-v="man"><i class="dot" style="background:var(--man)"></i>Manual</button>
      </div>
    </div>
    <div class="fgroup"><span>Database</span>
      <div class="seg" data-f="db">
        <button aria-pressed="true" data-v="all">Both</button>
        <button aria-pressed="false" data-v="prod">prod</button>
        <button aria-pressed="false" data-v="dev">dev</button>
      </div>
    </div>
    <div class="fgroup"><span>Role</span>
      <div class="seg" data-f="role">
        <button aria-pressed="true" data-v="all">All</button>
        <button aria-pressed="false" data-v="monitor">Framework monitors</button>
        <button aria-pressed="false" data-v="backend">Backends</button>
        <button aria-pressed="false" data-v="other">Alerts, apps, analysis</button>
      </div>
    </div>
    <button class="btn" id="reset">Reset</button>
    <button class="btn" id="notes">Notes</button>
    <button class="btn" id="rec">Recommendations</button>
  </div>
</header>

<section class="diag" id="diag" aria-label="Dependency map">
  <div class="colheads">
    <div>Backend jobs (write)</div>
    <div>Database tables <span class="legend" id="legend" hidden><span><svg viewBox="0 0 26 6"><line x1="0" y1="3" x2="26" y2="3"/></svg>write</span><span><svg viewBox="0 0 26 6"><line class="r" x1="0" y1="3" x2="26" y2="3"/></svg>read</span></span></div>
    <div>Monitors, alerts, apps (read)</div>
    <div>CERF frameworks · last envelope</div>
  </div>
  <div class="cols" id="cols">
    <svg class="edges" id="edges" aria-hidden="true"></svg>
    <div class="col" id="c1"></div>
    <div class="col" id="c2">
      <div class="dbgroup prod" id="g_prod"><div class="gh"><span class="tag prod">prod</span> database</div></div>
      <div class="dbgroup dev" id="g_dev"><div class="gh"><span class="tag">dev</span> database</div></div>
    </div>
    <div class="col" id="c3"></div>
    <div class="col" id="c4">
      <div class="fwlist" id="fwlist"></div>
      <aside class="side" id="side" aria-live="polite"></aside>
    </div>
  </div>
</section>
</div>

<dialog id="dlg">
  <h3>How to read the map</h3>
  <p>Three kinds of thing are drawn. <strong>Cards</strong> are scheduled jobs, web apps or manual work; the stripe colour is where they run. <strong>Rows inside the two boxes</strong> are groups of database tables, in the prod or dev database. <strong>Ledger rows</strong> on the right are CERF frameworks with their last recorded pre-arranged envelope; a greyed row's latest version is not currently active (in development, superseded, retired or expired, using the catalog's lifecycle rule), though its monitor may still run. Data flows left to right: jobs on the left write the tables, consumers on the right read them, dotted lines link a monitor to the framework it triggers. When an item is selected its connections are highlighted in blue: solid for writes, dashed for reads. A consumer that also writes carries an "also writes" tag and a line back into the database. ▲ marks a job the pipeline registry showed failing or overdue at its last snapshot. Click the item again, an empty area, or the clear button to deselect.</p>
  <p class="meta">__LISTMONK__</p>
  <p class="meta">Generated by <code>scripts/gen_db_network.py</code> from page frontmatter, the DB table snapshots and the pipeline registry (snapshot __SNAPSHOT__); curated text lives in <code>infrastructure/db-network.yml</code>.</p>
  __CONTEXT__
  <h3>Read the money carefully</h3>
  <p>__MONEY__</p>
  <h3>Not affected</h3>
  <p>__NOT_AFFECTED__</p>
  <h3>Mitigations recorded in the knowledge base</h3>
  <ul>__MITIGATIONS__</ul>
  __GAPS__
  __IGNORED__
  <form method="dialog" style="text-align:right;margin-top:12px"><button class="btn">Close</button></form>
</dialog>

<dialog id="dlg-rec">
  <div class="tabs" role="tablist">
    <button class="tab" role="tab" aria-selected="true" data-tab="prune">Pruning</button>
    <button class="tab" role="tab" aria-selected="false" data-tab="migrate">Migration priority</button>
  </div>
  <section class="tabpane" data-pane="prune">
    <p class="meta">Evidence for a clean-up, never an automatic action: jobs long dead in the registry, things with zero connections on this map, and pages already stopped or superseded.</p>
    __PRUNE__
  </section>
  <section class="tabpane" data-pane="migrate" hidden>
    <p class="meta">What to move first, ranked by how much depends on it: CERF frameworks and their envelopes, framework monitors, other consumers and email recipients downstream. Two lists, because the two moves are independent: off GitHub-hosted runners onto Databricks, and off the dev database onto prod.</p>
    __MIGRATE__
  </section>
  <form method="dialog" style="text-align:right;margin-top:12px"><button class="btn">Close</button></form>
</dialog>

<script>
const DATA = __DATA__;
const RT = { gha:{name:"GitHub Actions",v:"var(--gha)"}, dbx:{name:"Databricks",v:"var(--dbx)"}, web:{name:"Azure web app",v:"var(--web)"}, man:{name:"Manual / laptop",v:"var(--man)"} };
const TABLES = DATA.tables, PIPES = DATA.pipes, FRAMEWORKS = DATA.frameworks;
const tblById = Object.fromEntries(TABLES.map(t=>[t.id,t]));
const pipeById = Object.fromEntries(PIPES.map(p=>[p.id,p]));
const fwById = Object.fromEntries(FRAMEWORKS.map(f=>[f.id,f]));
for (const p of PIPES) p.db = [...new Set([...p.writes,...p.reads].map(t=>tblById[t].db))].sort((a,b)=>a==="prod"?-1:1);

const EDGES = [];
for (const p of PIPES){
  for (const t of p.writes) EDGES.push({from:p.id, to:t, kind:"write"});
  for (const t of p.reads)  EDGES.push({from:t, to:p.id, kind:"read"});
  if (p.fwRef && fwById[p.fwRef]) EDGES.push({from:p.id, to:p.fwRef, kind:"trig"});
}
for (const d of (DATA.direct||[])) if (tblById[d.from] && fwById[d.to]) EDGES.push({from:d.from, to:d.to, kind:"trig"});
const colOf = id => pipeById[id] ? pipeById[id].col : tblById[id] ? 2 : 4;

const state = { rt:"all", db:"all", role:"all", sel:null, hover:null };
const esc = s => String(s==null?"":s).replace(/[&<>"]/g, c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
const usdFmt = v => v==null ? "n/a" : "$"+(v/1e6).toFixed(1)+"M";
const rtTags = p => p.rt.map(r=>`<span class="tag rt" style="background:${RT[r].v}">${RT[r].name}</span>`).join(" ");
const dbTag = d => `<span class="tag ${d}">${d}</span>`;
const isBad = s => s==="DOWN";

function mkNode(id, cls){ const el=document.createElement("button"); el.type="button"; el.id="n_"+id; el.className="node "+cls;
  el.addEventListener("click", e=>{ e.stopPropagation(); state.sel = state.sel===id ? null : id; update(); });
  el.addEventListener("mouseenter", ()=>{ state.hover=id; applyHover(); });
  el.addEventListener("mouseleave", ()=>{ state.hover=null; applyHover(); });
  return el; }

// Drop the card subtitles only when the columns really overflow the viewport (measured, not guessed).
function fitToViewport(){
  const cols = document.getElementById("cols");
  document.body.classList.remove("dense");
  if (cols.scrollHeight > cols.clientHeight + 1) document.body.classList.add("dense");
}
function render(){
  for (const p of PIPES){
    const el = mkNode(p.id, "pipe" + (p.rt.length>1?" two":""));
    el.style.setProperty("--stripe", RT[p.rt[0]].v); if (p.rt[1]) el.style.setProperty("--stripe2", RT[p.rt[1]].v);
    const rtLabel = p.rt.map(r=>RT[r].name.replace(" / laptop","")).join(" + ");
    const rw = [];
    if (p.col===3 && p.writes.length) rw.push(`<span class="tag w">also writes ${[...new Set(p.writes.map(t=>tblById[t].db))].join("+")}</span>`);
    if (p.via && p.via.length) rw.push(`<span class="tag">via ${esc(p.via.join(", "))}</span>`);
    if (p.recipients!=null) rw.push(`<span class="tag">${p.recipients} recipients</span>`);
    el.innerHTML = `<div class="t">${esc(p.name)}${p.unverified?' <span class="tag warn">unverified</span>':""}${isBad(p.status)?' <span class="health">▲ '+esc(p.status)+'</span>':""}</div>
      <div class="m"><span>${esc(rtLabel)} · ${esc(p.meta)}</span>${rw.length?" "+rw.join(" "):""}</div>`;
    document.getElementById("c"+p.col).appendChild(el);
  }
  for (const t of TABLES){
    const el = mkNode(t.id, "tbl");
    el.innerHTML = `<div class="t">${esc(t.label)}</div>`;
    document.getElementById("g_"+t.db).appendChild(el);
  }
  for (const f of FRAMEWORKS){
    const el = mkNode(f.id, "fw");
    const sub = f.unverified ? "database dependency unverified" : f.usd==null ? "no envelope on current version" : "";
    if (!f.active) el.classList.add("inactive");
    el.title = [f.active ? "" : `latest version is ${f.status}`, sub].filter(Boolean).join(" · ");
    el.innerHTML = `<span class="n">${esc(f.name)}${f.active?"":` <span class="st">${esc(f.status)}</span>`}</span><span class="usd">${usdFmt(f.usd)}${f.unverified?"?":""}</span>`;
    document.getElementById("fwlist").appendChild(el);
  }
  document.getElementById("g_dev").hidden = !TABLES.some(t=>t.db==="dev");
  fitToViewport();
  update();
}

function pipeMatches(p){
  if (state.rt!=="all" && !p.rt.includes(state.rt)) return false;
  if (state.db!=="all" && !p.db.includes(state.db)) return false;
  if (state.role!=="all" && p.role!==state.role) return false;
  return true;
}
function visibleSet(){
  const vis = new Set();
  for (const p of PIPES) if (pipeMatches(p)) vis.add(p.id);
  for (const t of TABLES){
    if (state.db!=="all" && t.db!==state.db) continue;
    if (EDGES.some(e=> e.kind!=="trig" && ((e.from===t.id&&vis.has(e.to)) || (e.to===t.id&&vis.has(e.from))))) vis.add(t.id);
  }
  for (const f of FRAMEWORKS) if (EDGES.some(e=> e.to===f.id && vis.has(e.from))) vis.add(f.id);
  return vis;
}

// Everything reachable from a node: downstream along data flow and upstream against it; consumers reached
// upstream (or the selection itself) also contribute what they write.
function reach(id){
  const out = new Set([id]);
  const walk = (start, fwd) => { const q=[start]; while(q.length){ const cur=q.pop(); for (const e of EDGES){ const nxt = fwd ? (e.from===cur ? e.to : null) : (e.to===cur ? e.from : null); if (nxt && !out.has(nxt)){ out.add(nxt); q.push(nxt); } } } };
  walk(id, true);
  const before = new Set(out);
  walk(id, false);
  for (const x of out) if (!before.has(x) || x===id){ const p = pipeById[x]; if (p && (p.col===3 || x===id)) for (const t of p.writes) out.add(t); }
  return out;
}
let effective = new Set();
let hoverSet = null;
function applyHover(){
  hoverSet = state.hover ? new Set([...reach(state.hover)].filter(x=>visibleSet().has(x))) : null;
  for (const id of [...PIPES,...TABLES,...FRAMEWORKS].map(x=>x.id)) document.getElementById("n_"+id).classList.toggle("hov", !!hoverSet && hoverSet.has(id));
  drawEdges();
}

function update(){
  const vis = visibleSet();
  effective = state.sel ? new Set([...vis].filter(x=>reach(state.sel).has(x))) : vis;
  for (const id of [...PIPES,...TABLES,...FRAMEWORKS].map(x=>x.id)){
    const el = document.getElementById("n_"+id);
    el.classList.toggle("dim", !effective.has(id));
    el.classList.toggle("sel", state.sel===id);
  }
  document.getElementById("legend").hidden = !state.sel;
  document.getElementById("g_prod").classList.toggle("dim", state.db==="dev");
  document.getElementById("g_dev").classList.toggle("dim", state.db==="prod");
  drawEdges();
  renderSide();
}

function drawEdges(){
  const svg = document.getElementById("edges");
  const box = document.getElementById("cols").getBoundingClientRect();
  svg.setAttribute("viewBox", `0 0 ${box.width} ${box.height}`);
  const rect = id => { const r = document.getElementById("n_"+id).getBoundingClientRect(); return {l:r.left-box.left, r:r.right-box.left, cy:r.top+r.height/2-box.top, h:r.height}; };
  const R = {}; for (const e of EDGES){ R[e.from] = R[e.from] || rect(e.from); R[e.to] = R[e.to] || rect(e.to); }
  const ends = EDGES.map(e => { const ltr = colOf(e.from) < colOf(e.to); return {e, ltr, sSide: ltr?"r":"l", tSide: ltr?"l":"r"}; });
  const slots = {};
  for (const x of ends){ (slots[x.e.from+"|"+x.sSide] = slots[x.e.from+"|"+x.sSide] || []).push({x, other:R[x.e.to].cy, key:"sy"}); (slots[x.e.to+"|"+x.tSide] = slots[x.e.to+"|"+x.tSide] || []).push({x, other:R[x.e.from].cy, key:"ty"}); }
  for (const k in slots){ const list = slots[k]; const id = k.split("|")[0]; const r = R[id]; list.sort((a,b)=>a.other-b.other); const n=list.length; const span = Math.min(r.h*0.6, (n-1)*7); list.forEach((it,i)=> it.x[it.key] = r.cy + (n>1 ? -span/2 + span*i/(n-1) : 0)); }
  let out = "";
  const rad = 8;
  for (const x of ends){
    const e = x.e, a = R[e.from], b = R[e.to];
    const x1 = x.ltr ? a.r : a.l, x2 = x.ltr ? b.l : b.r, y1 = x.sy, y2 = x.ty;
    const mx = (x1 + x2)/2, dy = y2 - y1, sg = Math.sign(dy) || 1, r = Math.min(rad, Math.abs(dy)/2, Math.abs(x2-x1)/2), dir = x.ltr ? 1 : -1;
    let d;
    if (Math.abs(dy) < 1) d = `M${x1},${y1} L${x2},${y2}`;
    else d = `M${x1},${y1} H${mx - r*dir} Q${mx},${y1} ${mx},${y1 + r*sg} V${y2 - r*sg} Q${mx},${y2} ${mx + r*dir},${y2} H${x2}`;
    const on = effective.has(e.from) && effective.has(e.to);
    const hi = state.sel && on;
    const hov = hoverSet && hoverSet.has(e.from) && hoverSet.has(e.to);
    out += `<path d="${d}" class="${e.kind}${on?"":" dim"}${hi?" hi":""}${hov?" hov":""}"/>`;
  }
  svg.innerHTML = out;
}

function jobsHtml(p){
  if (!p.jobs || !p.jobs.length) return "";
  return `<dt>Jobs</dt><dd><ul>${p.jobs.map(j=>`<li>${j.url?`<a href="${esc(j.url)}" target="_blank" rel="noopener">${esc(j.name)}</a>`:esc(j.name)} · ${esc(j.cadence)} · ${isBad(j.status)?`<span class="health">▲ ${esc(j.status)}${j.flags?" · "+esc(j.flags):""}</span>`:esc(j.status)+(j.flags?" · "+esc(j.flags):"")}</li>`).join("")}</ul></dd>`;
}

function renderSide(){
  const side = document.getElementById("side");
  const id = state.sel;
  if (!id){ side.innerHTML = `<p class="hint">Select a node to see more details</p>`; return; }
  let html = "";
  let links = [];
  if (tblById[id]){
    const t = tblById[id];
    const w = EDGES.filter(e=>e.kind==="write"&&e.to===id).map(e=>pipeById[e.from].name);
    const r = EDGES.filter(e=>e.kind==="read"&&e.from===id).map(e=>pipeById[e.to].name);
    html += `<h2><code>${esc(t.label)}</code></h2><div class="tags">${dbTag(t.db)} <span class="tag">table group</span></div>
      <dl class="kv"><dt>Tables</dt><dd><code>${esc(t.tables.join(", "))||"—"}</code></dd><dt>Written by</dt><dd>${esc(w.join(", "))||"—"}</dd><dt>Read by</dt><dd>${esc(r.join(", "))||"—"}</dd></dl>`;
    links = t.links || [];
  } else if (fwById[id]){
    const f = fwById[id];
    const m = PIPES.filter(p=>p.fwRef===id);
    const viaGroups = EDGES.filter(e=>e.to===id && tblById[e.from]).map(e=>tblById[e.from].label);
    html += `<h2>${esc(f.name)} · ${usdFmt(f.usd)}${f.unverified?"?":""}</h2><div class="tags"><span class="tag">CERF framework</span> <span class="tag">${esc(f.latest)} · ${esc(f.status)}</span></div>
      <dl class="kv"><dt>Envelope</dt><dd>${esc(f.usdNote)}</dd><dt>Live monitor</dt><dd>${esc(m.map(x=>x.name).join(", "))||"—"}</dd>${viaGroups.length?`<dt>Depends on</dt><dd>${esc(viaGroups.join(", "))}</dd>`:""}<dt>Runs on</dt><dd>${m.map(rtTags).join(" ")}</dd><dt>Database</dt><dd>${[...new Set(m.flatMap(x=>x.db))].map(dbTag).join(" ")}</dd></dl>
      ${m.some(x=>x.recipients!=null)?`<p><strong>Recipients:</strong> ${m.filter(x=>x.recipients!=null).map(x=>`${x.recipients} via ${esc(x.name)}`).join(", ")}</p>`:""}
      <p><strong>If cut:</strong> ${esc(m.map(x=>x.impact).join(" "))}</p>`;
    links = f.links || [];
  } else {
    const p = pipeById[id];
    const roleName = {monitor:"CERF framework monitor", backend:"Backend producer", other:"Alerts / app / analysis"}[p.role];
    html += `<h2>${esc(p.name)}</h2>
      <div class="tags">${rtTags(p)} ${p.db.map(dbTag).join(" ")} <span class="tag">${roleName}</span>${p.unverified?' <span class="tag warn">unverified</span>':""}</div>
      <dl class="kv">
        <dt>Repo</dt><dd>${esc(p.repo)}</dd>
        ${jobsHtml(p)}
        <dt>Tables</dt><dd><code>${esc(p.tables)}</code></dd>
        ${p.lists?`<dt>Email lists</dt><dd>${p.lists.map(l=>`${esc(l.name||("list "+l.id))}${l.count!=null?` (${l.count})`:""}`).join(", ")}${p.list_tags&&p.list_tags.length?` · tag ${esc(p.list_tags.join(", "))}`:""}${p.recipients!=null?`<br><strong>${p.recipients} recipients</strong> across ${p.lists.length} list${p.lists.length===1?"":"s"} (list memberships, not de-duplicated people)`:DATA.listmonk?"<br>list sizes unknown for these ids in the snapshot":"<br>list sizes unavailable: no Listmonk snapshot yet (gen_listmonk_lists.py)"}</dd>`:""}
        ${p.unverified?`<dt>Unverified</dt><dd>${esc(p.unverified)}</dd>`:""}
        ${p.fwRef&&fwById[p.fwRef]?`<dt>Framework</dt><dd>${esc(fwById[p.fwRef].name)} · ${usdFmt(fwById[p.fwRef].usd)}${fwById[p.fwRef].unverified?"?":""}</dd>`:""}
      </dl>
      <p><strong>If cut:</strong> ${esc(p.impact)}</p>`;
    const down = new Set(); const q=[p.id]; while(q.length){ const cur=q.pop(); for (const e of EDGES) if (e.from===cur && !down.has(e.to)){ down.add(e.to); q.push(e.to); } }
    const dPipes = PIPES.filter(x=>down.has(x.id)), dMons = dPipes.filter(x=>x.role==="monitor"), dUsd = dMons.filter(x=>!x.unverified).map(x=>fwById[x.fwRef]).filter(f=>f&&f.usd!=null).reduce((a,f)=>a+f.usd,0);
    const dRec = dPipes.filter(x=>x.recipients!=null).reduce((a,x)=>a+x.recipients,0), dRecN = dPipes.filter(x=>x.recipients!=null).length;
    if (dPipes.length) html += `<p><strong>Downstream:</strong> ${dPipes.length} jobs and apps, ${dMons.length} framework monitors${dUsd?`, ${usdFmt(dUsd)} pre-arranged CERF funding`:""}${dRecN?`, ${dRec} email recipients across ${dRecN} pipelines`:""}.</p>`;
    links = p.links || [];
  }
  if (links.length) html += `<div class="links">${links.map(l=>`<a href="${esc(l.url)}" target="_blank" rel="noopener">${esc(l.label)}</a>`).join("")}</div>`;
  html += `<div class="clear"><button class="btn" id="clearsel">Clear selection</button></div>`;
  side.innerHTML = html;
  document.getElementById("clearsel").addEventListener("click", ()=>{ state.sel=null; update(); });
}

document.getElementById("filters").addEventListener("click", e=>{
  const b = e.target.closest("button[data-v]"); if(!b) return;
  const g = b.closest(".seg");
  state[g.dataset.f] = b.dataset.v;
  g.querySelectorAll("button").forEach(x=>x.setAttribute("aria-pressed", x===b ? "true":"false"));
  update();
});
document.getElementById("reset").addEventListener("click", ()=>{
  state.rt=state.db=state.role="all"; state.sel=null;
  document.querySelectorAll(".seg button").forEach(x=>x.setAttribute("aria-pressed", x.dataset.v==="all"?"true":"false"));
  update();
});
document.getElementById("notes").addEventListener("click", ()=>document.getElementById("dlg").showModal());
document.getElementById("rec").addEventListener("click", ()=>document.getElementById("dlg-rec").showModal());
document.getElementById("dlg-rec").addEventListener("click", e=>{
  const b = e.target.closest("[data-select]"); if(!b) return;
  document.getElementById("dlg-rec").close();
  state.sel = b.dataset.select; update();
  const el = document.getElementById("n_"+state.sel); if (el) el.focus({preventScroll:true});
});
document.querySelector("#dlg-rec .tabs").addEventListener("click", e=>{
  const b = e.target.closest(".tab"); if(!b) return;
  document.querySelectorAll("#dlg-rec .tab").forEach(x=>x.setAttribute("aria-selected", x===b?"true":"false"));
  document.querySelectorAll("#dlg-rec .tabpane").forEach(x=>x.hidden = x.dataset.pane!==b.dataset.tab);
});
document.getElementById("diag").addEventListener("click", e=>{ if (!e.target.closest(".node")) { state.sel=null; update(); } });
document.addEventListener("keydown", e=>{ if (e.key==="Escape" && state.sel){ state.sel=null; update(); } });
window.addEventListener("resize", ()=>{ fitToViewport(); update(); });

render();
if (document.fonts) document.fonts.ready.then(update);
</script>
</body>
</html>
"""


# ----------------------------------------------------------------------------- main

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="exit 2 if db_network.html on disk is stale")
    ap.add_argument("--dump", action="store_true", help="print the node/edge data as JSON instead of writing the page")
    args = ap.parse_args()
    data = build()
    if args.dump:
        print(json.dumps(data, indent=1, ensure_ascii=False))
        return 0
    out = render(data)
    for g in data["meta"]["gaps"]:
        print(f"::warning title=db-network gap::{g}", file=sys.stderr)
    if args.check:
        if OUT.exists() and OUT.read_text(encoding="utf-8") == out:
            print("db_network.html is current")
            return 0
        print("db_network.html is STALE — run scripts/gen_db_network.py", file=sys.stderr)
        return 2
    OUT.write_text(out, encoding="utf-8")
    print(f"Wrote {OUT.relative_to(ROOT)} — {len(data['pipes'])} jobs/apps, {len(data['tables'])} table groups, "
          f"{len(data['frameworks'])} frameworks, {len(data['meta']['gaps'])} gaps.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
