#!/usr/bin/env python3
"""Build the cross-content-type dependency graph from `depends_on` edges.

Reads `depends_on` (direct upstream node ids) from every framework/pipeline/app
page, computes the reverse edges (dependents) and the transitive blast radius,
and writes `infrastructure/dependency-graph.md`: a single-point-of-failure /
"if X breaks, what's affected" table, a Mermaid diagram, an adjacency table, and
flags for unresolved (external / not-yet-ingested) dependencies.

Run after each ingest batch (post-batch routine). Edges are declared once, as
direct upstream `depends_on`; reverse edges + blast radius are derived here, so
the graph is always bidirectionally consistent.

Usage:  python scripts/gen_dependency_graph.py   (from repo root)
"""
from __future__ import annotations
import re
from collections import defaultdict
from pathlib import Path

try:
    import yaml
except ImportError:
    import sys
    sys.exit("Needs pyyaml")

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "infrastructure" / "dependency-graph.md"

# Known shared-infra / external nodes referenced by depends_on but not their own page.
INFRA = {
    "listmonk": ("Listmonk (comms)", "infra", "comms-listmonk.md"),
    "aws-smtp": ("AWS SMTP (comms)", "infra", None),
    "floodscan-ingest": ("ds-floodscan-ingest (upstream pipeline, not yet ingested)", "external", None),
    "dbx-job-compute": ("Databricks Job Compute policy 000C79D951EAF0D6 (injects dsci secrets)", "infra", "databricks.md"),
}
TYPE_ORDER = {"infra": 0, "external": 1, "table": 2, "pipeline": 3, "app": 4, "analysis": 5, "framework": 6}


def parse(path: Path) -> dict:
    t = path.read_text(encoding="utf-8")
    e = t.find("\n---", 3)
    try:
        return yaml.safe_load(t[3:e]) or {}
    except yaml.YAMLError:
        return {}


def mid(s: str) -> str:
    return "n_" + re.sub(r"[^a-z0-9]", "_", s.lower())


# depends_on values should be canonical ids (bare page stem | infra id | schema.table).
# Normalize the common drift — a stray folder prefix or the comms-listmonk page name — so
# a slightly-off ref still resolves instead of spawning a junk "external" node.
_PREFIXES = ("pipelines/", "apps/", "analysis/", "frameworks/", "infrastructure/")
_ALIASES = {"comms-listmonk": "listmonk"}


def norm(x) -> str:
    r = str(x).strip()
    for pre in _PREFIXES:
        if r.startswith(pre):
            r = r[len(pre):]
            break
    return _ALIASES.get(r, r)


def main() -> None:
    nodes: dict[str, dict] = {}
    deps: dict[str, set] = defaultdict(set)

    # framework nodes (one per folder; union depends_on across versions)
    for d in sorted(p for p in (ROOT / "frameworks").iterdir() if p.is_dir()):
        vps = [p for p in d.glob("*.md") if p.name not in ("README.md", "_TEMPLATE.md")]
        if not vps:
            continue
        nodes[d.name] = {"type": "framework", "link": f"../frameworks/{d.name}/"}
        for p in vps:
            for x in (parse(p).get("depends_on") or []):
                deps[d.name].add(norm(x))
    # pipeline + app + analysis nodes (flat files)
    for kind, folder in (("pipeline", "pipelines"), ("app", "apps"), ("analysis", "analysis")):
        for p in sorted((ROOT / folder).glob("*.md")):
            if p.name in ("README.md", "_TEMPLATE.md"):
                continue
            nodes[p.stem] = {"type": kind, "link": f"../{folder}/{p.name}"}
            for x in (parse(p).get("depends_on") or []):
                deps[p.stem].add(norm(x))

    # DB tables as nodes (from the introspected prod list — the canonical data layer):
    # pipeline writes table -> app/pipeline reads it. (dev tables live in db-schema-dev.md.)
    import json as _json
    dbjson = ROOT / "infrastructure" / ".db-tables.json"
    db_tables = list(_json.loads(dbjson.read_text())) if dbjson.exists() else []
    for tid in db_tables:
        nodes.setdefault(tid, {"type": "table", "link": f"db-schema.md#{tid.split('.')[0]}"})

    def _refs(fm, *fields):
        txt = " ".join(str(x) for f in fields for x in (fm.get(f) or []))
        return [t for t in db_tables if t in txt]

    for kind, folder in (("pipeline", "pipelines"), ("app", "apps")):
        for p in sorted((ROOT / folder).glob("*.md")):
            if p.name in ("README.md", "_TEMPLATE.md"):
                continue
            fm = parse(p)
            for t in _refs(fm, "outputs"):       # writers: pipeline -> table
                deps[t].add(p.stem)
            for t in _refs(fm, "inputs"):         # readers: table -> consumer
                deps[p.stem].add(t)

    # materialise referenced infra/external nodes
    for ups in list(deps.values()):
        for r in ups:
            if r not in nodes:
                if r in INFRA:
                    lbl, typ, link = INFRA[r]
                    nodes[r] = {"type": typ, "link": link, "label": lbl}
                else:
                    # third-party data sources get a reference page under infrastructure/datasets/
                    ds = ROOT / "infrastructure" / "datasets" / f"{r}.md"
                    nodes[r] = {"type": "external", "link": f"datasets/{r}.md" if ds.exists() else None}

    rev: dict[str, set] = defaultdict(set)
    for u, ups in deps.items():
        for v in ups:
            rev[v].add(u)

    def blast(x: str) -> set:
        seen, stack = set(), list(rev[x])
        while stack:
            n = stack.pop()
            if n in seen:
                continue
            seen.add(n)
            stack += list(rev[n])
        return seen

    edged = {n for n in nodes if deps.get(n) or rev.get(n)}

    def label(n):
        return nodes[n].get("label", n)

    def linked(n):
        lk = nodes[n].get("link")
        return f"[`{label(n)}`]({lk})" if lk else f"`{label(n)}`"

    L = ["<!-- generated by scripts/gen_dependency_graph.py — declare edges via `depends_on` on each page, not here -->",
         "", "# Dependency graph & blast radius", "",
         "Cross-content-type dependencies, built from the `depends_on` field on every framework / pipeline / app page. "
         "Edges are declared once (direct upstream); **reverse edges and blast radius are derived here**, so this is always consistent. "
         "Arrows below point in the direction failure propagates: **X → Y means \"if X breaks, Y is affected.\"**", ""]

    # blast radius table
    spof = sorted((n for n in nodes if rev.get(n)), key=lambda n: (-len(blast(n)), n))
    L += ["## Single points of failure (blast radius)", "",
          "If a node breaks, everything in its **transitive downstream** is affected. Sorted by reach.", "",
          "| node | type | direct dependents | total downstream | what breaks (transitive) |",
          "|---|---|--:|--:|---|"]
    for n in spof:
        direct = sorted(rev[n])
        trans = sorted(blast(n))
        L.append(f"| {linked(n)} | {nodes[n]['type']} | {len(direct)} | {len(trans)} | "
                 + ", ".join(f"`{t}`" for t in trans) + " |")
    L.append("")

    # mermaid
    L += ["## Graph", "", "```mermaid", "graph LR"]
    for n in sorted(edged, key=lambda n: (TYPE_ORDER.get(nodes[n]["type"], 9), n)):
        L.append(f'  {mid(n)}["{label(n)}"]')
    for u in sorted(deps):
        for v in sorted(deps[u]):
            L.append(f"  {mid(v)} --> {mid(u)}")
    L += ["  classDef framework fill:#dbeafe,stroke:#3b82f6;",
          "  classDef pipeline fill:#dcfce7,stroke:#22c55e;",
          "  classDef app fill:#ffedd5,stroke:#f97316;",
          "  classDef infra fill:#fee2e2,stroke:#ef4444;",
          "  classDef analysis fill:#ede9fe,stroke:#8b5cf6;",
          "  classDef table fill:#fef9c3,stroke:#eab308;",
          "  classDef external fill:#f3f4f6,stroke:#9ca3af,stroke-dasharray:4;"]
    for typ in ("framework", "pipeline", "app", "analysis", "table", "infra", "external"):
        ids = [mid(n) for n in edged if nodes[n]["type"] == typ]
        if ids:
            L.append(f"  class {','.join(ids)} {typ};")
    L += ["```", ""]

    # adjacency
    L += ["## Adjacency (nodes with edges)", "",
          "| node | type | depends on ↑ | depended on by ↓ |", "|---|---|---|---|"]
    for n in sorted(edged, key=lambda n: (TYPE_ORDER.get(nodes[n]["type"], 9), n)):
        up = ", ".join(f"`{x}`" for x in sorted(deps.get(n, []))) or "—"
        dn = ", ".join(f"`{x}`" for x in sorted(rev.get(n, []))) or "—"
        L.append(f"| {linked(n)} | {nodes[n]['type']} | {up} | {dn} |")
    L.append("")

    # flags
    ext = sorted(n for n in nodes if nodes[n]["type"] in ("external", "infra") and not nodes[n].get("link"))
    isolated = sorted(n for n in nodes if nodes[n]["type"] == "framework" and n not in edged)
    L += ["## Flags", "",
          f"- **Unresolved / not-yet-a-page dependencies ({len(ext)}):** "
          + (", ".join(f"`{n}`" for n in ext) or "none")
          + " — referenced as `depends_on` but no KB page yet (ingest or stub them to complete the chain).",
          f"- **Frameworks with no declared edges ({len(isolated)}):** their monitoring isn't yet ingested as a pipeline, "
          "or `depends_on` is unset — most run monitoring in-repo. Edges fill in as pipelines/apps are ingested.",
          ""]

    OUT.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"Wrote {OUT.relative_to(ROOT)} — {len(nodes)} nodes, {sum(len(v) for v in deps.values())} edges, "
          f"{len(spof)} nodes with dependents.")


if __name__ == "__main__":
    main()
