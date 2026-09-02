#!/usr/bin/env python3
"""Generate the registry + live health of every PUBLISHED SITE (GitHub Pages first) — and
auto-declare the ones the KB doesn't know about yet.

Published sites are the team's fastest-growing deliverable: analyses, dashboards, explorers
and multi-product landing pages go straight to GitHub Pages. Documenting them by hand did not
keep up (2026-09-01: 38 DS repos served a Pages site, 11 were in the hand table). This is the
Pages counterpart of `gen_pipeline_registry.py`: mechanical facts are read from the platform
and the live site, not typed.

What it does
  1. SWEEP  — every `ocha-dap` repo with Pages enabled that is (a) DS-team-named or (b) a
     `source_repo` of some KB page (`gh api`; private repos need an org-read PAT).
  2. PROBE  — for each site and each declared surface: HTTP status + `<title>`; the landing
     page is crawled one level for same-site child products (`/<repo>/<x>/`, the landing-page
     convention in methods/static-data-apps.md).
  3. MATCH  — against the `surfaces:` frontmatter declared on framework / pipeline / app /
     analysis pages (+ `deployment.url` of app pages).
  4. WRITE  — infrastructure/pages-registry.md (+ .pages-registry.json).
  5. APPLY  — with --apply, every live surface no page declares is appended to the owning
     page's `surfaces:` (owner = the KB page whose `source_repo` is that repo; apps >
     pipelines > analysis > newest live framework version; ambiguity → reported, not guessed)
     as `{url, title, auto: true, first_seen}` — mechanical facts only. A human later replaces
     `auto: true` with `kind:` (+ a better title) when they review it.

Frontmatter contract (`surfaces:` on any content page; see docs/INGESTION.md):
  surfaces:
    - {url: "https://…/", kind: app, title: "…"}          # kind ∈ KINDS below (optional)
    - {url: "https://…/x/", title: "…", auto: true, first_seen: 2026-09-01}   # auto-added
  Optional per entry: access: public|password|private (private → not probed, never "dead");
                      status: live|retired (retired → kept for the record, not probed).

Usage:  python scripts/gen_pages_registry.py [--apply] [--report f.md] [--check] [--no-sweep]
        --check     offline lint only: surfaces shape + legacy URL shapes (CI, no gh needed)
        --no-sweep  probe declared surfaces only; registry files are NOT written
Exit:   0 = clean · 2 = attention items remain (undeclared / unreachable / no Pages / legacy)
        1 = the org sweep failed → nothing written (a good registry is never replaced by an empty one)
Needs:  gh (authed), pyyaml, network.
"""
from __future__ import annotations
import argparse
import datetime as dt
import html
import json
import re
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from collections import defaultdict
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("Needs pyyaml:  uv pip install pyyaml")

ROOT = Path(__file__).resolve().parent.parent
OUT_MD = ROOT / "infrastructure" / "pages-registry.md"
OUT_JSON = ROOT / "infrastructure" / ".pages-registry.json"
ORG = "OCHA-DAP"
SCAN = ["frameworks", "pipelines", "apps", "analysis",
        "infrastructure"]   # infrastructure/: only DECLARES (the KB's own site's products, D103) — never an owner
# Same DS-team naming rule as check_new_repos.py; plus any repo a KB page names as source_repo.
DS_RE = re.compile(r"^(ds-|pa-aa-|ds-aa-|hdx-signals$)", re.I)
# Pages sites in scope that are deliberately NOT KB content pages (reason recorded here).
IGNORE = {
    "ds-knowledge-base": "the KB's own public AA site — documented in infrastructure/automation.md (site.yml)",
    "pa-anticipatory-action": "legacy pre-2024 monorepo site; its per-country analyses are declared on the framework pages that use them",
}
KINDS = ("landing", "app", "report", "book", "dashboard", "form", "download", "docs", "status", "other")
SLUG_RE = re.compile(r"(?:ocha-dap|OCHA-DAP)/([A-Za-z0-9._-]+)")
ASSET_EXT = re.compile(r"\.(css|js|mjs|png|jpe?g|gif|svg|ico|webp|json|geojson|csv|parquet|xml|txt|md|"
                       r"woff2?|ttf|otf|pdf|zip|gz|nc|tif+)$", re.I)
# Anchor tags only — the raw body includes inline <script>, whose `href="${x}"` template literals are not links.
HREF_RE = re.compile(r"""<a\b[^>]*?\bhref\s*=\s*["']([^"'#]+)["']""", re.I | re.S)
TEMPLATE_RE = re.compile(r"\$\{|\{\{|\$\d|<%")
TITLE_RE = re.compile(r"<title[^>]*>(.*?)</title>", re.I | re.S)
TIMEOUT = 25
TODAY = dt.date.today().isoformat()
NOW = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
CAT_ORDER = {"apps": 0, "pipelines": 1, "analysis": 2, "frameworks": 3}


# ---- helpers ---------------------------------------------------------------------
def ok(code) -> bool:
    """Live = any 2xx (shinyapps answers 202 while a sleeping app spins up; redirects are followed)."""
    return code is not None and 200 <= code < 300


def sh(args: list[str], timeout: int = 120) -> str | None:
    """stdout on success; None on a non-zero exit or timeout. Callers must treat None as
    'unknown', never as 'empty' — a half-paginated `gh api` must not read as a complete listing."""
    try:
        p = subprocess.run(args, capture_output=True, text=True, timeout=timeout)
    except Exception:
        return None
    return p.stdout if p.returncode == 0 else None


def frontmatter_span(text: str) -> tuple[int, int] | None:
    """(start, end) char offsets of the YAML body between the --- fences, or None."""
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    return (3, end) if end != -1 else None


def frontmatter(path: Path) -> dict | None:
    t = path.read_text(encoding="utf-8")
    span = frontmatter_span(t)
    if not span:
        return None
    try:
        fm = yaml.safe_load(t[span[0]:span[1]])
    except yaml.YAMLError:
        return None
    return fm if isinstance(fm, dict) else None


def norm_url(u: str) -> str:
    """Canonical form for MATCHING only (probes use the URL as written): https, lowercase host,
    no query/fragment, no index.html, trailing slash on directory-like paths."""
    u = (u or "").strip().strip("<>")
    if not u:
        return ""
    if "://" not in u:
        u = "https://" + u
    p = urllib.parse.urlsplit(u)
    path = re.sub(r"/index\.html?$", "/", p.path or "/")
    if not path.endswith("/") and not re.search(r"\.[A-Za-z0-9]{1,5}$", path):
        path += "/"
    return urllib.parse.urlunsplit(("https", p.netloc.lower(), path, "", ""))


def repo_of_url(u: str) -> str | None:
    """`ocha-dap.github.io/<repo>/…` → repo name (lowercase), else None."""
    p = urllib.parse.urlsplit(u)
    if p.netloc.lower() == "ocha-dap.github.io":
        seg = p.path.strip("/").split("/")
        return seg[0].lower() if seg and seg[0] else None
    return None


def fetch(url: str) -> tuple[int | None, str, str, str]:
    """(status, final_url, title, body). status None = network error / timeout."""
    req = urllib.request.Request(url, headers={"User-Agent": "ds-kb pages-registry (+github.com/OCHA-DAP/ds-knowledge-base)"})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            body = r.read(4_000_000).decode("utf-8", "replace")   # 4 MB: landing pages are small, but never truncate one silently
            m = TITLE_RE.search(body)
            title = html.unescape(re.sub(r"\s+", " ", m.group(1))).strip() if m else ""
            return r.status, r.geturl(), title, body
    except urllib.error.HTTPError as e:
        return e.code, url, "", ""
    except Exception:
        return None, url, "", ""


def child_products(site_url: str, body: str) -> list[str]:
    """Same-site links exactly one directory below the site root — the landing-page
    convention's 'products'. Chapters/files (`x.html`) and assets are not products."""
    root = norm_url(site_url)
    root_path = urllib.parse.urlsplit(root).path
    out: list[str] = []
    for href in HREF_RE.findall(body or ""):
        if href.startswith(("mailto:", "javascript:", "data:")) or TEMPLATE_RE.search(href):
            continue
        u = norm_url(urllib.parse.urljoin(root, href))
        if not u.startswith(root) or u == root or ASSET_EXT.search(u):
            continue
        rel = urllib.parse.urlsplit(u).path[len(root_path):].strip("/")
        if rel and "/" not in rel and u.endswith("/") and u not in out:
            out.append(u)
    return out[:40]


# ---- KB side -----------------------------------------------------------------------
def scan_pages() -> tuple[list[dict], dict[str, list[dict]]]:
    """All content pages with frontmatter, plus repo → [page] (exact source_repo slug match)."""
    pages: list[dict] = []
    by_repo: dict[str, list[dict]] = defaultdict(list)
    for d in SCAN:
        for path in sorted((ROOT / d).rglob("*.md")):
            if path.name in ("_TEMPLATE.md", "README.md"):
                continue
            fm = frontmatter(path)
            if fm is None:
                continue
            rel = path.relative_to(ROOT).as_posix()
            repos = sorted({m.lower() for m in SLUG_RE.findall(str(fm.get("source_repo") or ""))})
            page = {"path": rel, "cat": d, "fm": fm, "repos": repos}
            pages.append(page)
            for r in repos:
                by_repo[r].append(page)
    return pages, by_repo


def declared_surfaces(pages: list[dict]) -> tuple[dict[str, dict], list[str]]:
    """url → {page, kind, title, auto, access}; plus lint problems (bad shapes)."""
    decl: dict[str, dict] = {}
    problems: list[str] = []
    for pg in pages:
        fm, rel = pg["fm"], pg["path"]
        surfs = fm.get("surfaces")
        if surfs is None:
            surfs = []
        if not isinstance(surfs, list):
            problems.append(f"`{rel}`: `surfaces:` must be a list")
            surfs = []
        for i, s in enumerate(surfs):
            if not isinstance(s, dict) or not s.get("url"):
                problems.append(f"`{rel}`: surfaces[{i}] must be a mapping with `url`")
                continue
            k = s.get("kind")
            if k is not None and k not in KINDS:
                problems.append(f"`{rel}`: surfaces[{i}] kind `{k}` not in {list(KINDS)}")
            if k is None and not s.get("auto"):
                problems.append(f"`{rel}`: surfaces[{i}] ({s['url']}) has neither `kind` nor `auto: true`")
            acc = s.get("access")
            if acc is not None and acc not in ("public", "password", "private"):
                problems.append(f"`{rel}`: surfaces[{i}] access `{acc}` not in public|password|private")
            st = s.get("status")
            if st is not None and st not in ("live", "retired"):
                problems.append(f"`{rel}`: surfaces[{i}] status `{st}` not in live|retired")
            u = norm_url(str(s["url"]))
            if u in decl and decl[u]["page"] != rel:
                problems.append(f"`{u}` declared on both `{decl[u]['page']}` and `{rel}` (one home per fact)")
                continue
            decl[u] = {"page": rel, "kind": k, "title": s.get("title") or "", "auto": bool(s.get("auto")),
                       "access": acc or "public", "status": st or "live", "raw": str(s["url"]).strip()}
        # app pages: the deployment URL IS a surface — don't make them declare it twice.
        dep = fm.get("deployment") if pg["cat"] == "apps" else None
        if isinstance(dep, dict) and dep.get("url"):
            u = norm_url(str(dep["url"]))
            decl.setdefault(u, {"page": rel, "kind": "app", "title": fm.get("purpose") or fm.get("name") or "",
                                "auto": False, "access": "public", "via": "deployment.url", "raw": str(dep["url"]).strip()})
    return decl, problems


def legacy_shapes(pages: list[dict], decl: dict[str, dict]) -> list[str]:
    """Published URLs still living in the pre-D102 ad-hoc keys and not (also) in surfaces."""
    out: list[str] = []
    site_re = re.compile(r"https?://[^\s\"'`<>)\]]+(?:github\.io|netlify\.app|quarto\.pub|shinyapps\.io|herokuapp\.com|azurewebsites\.net)[^\s\"'`<>)\]]*", re.I)
    for pg in pages:
        fm, rel = pg["fm"], pg["path"]
        mine = {d for d, v in decl.items() if v["page"] == rel}   # one home per fact: only THIS page's declarations exempt
        apps = fm.get("apps")
        if isinstance(apps, list) and apps:
            for a in apps:
                if not isinstance(a, str):
                    continue
                u = norm_url(a)
                where = f" (already declared on `{decl[u]['page']}` — just delete this line)" if u in decl and u not in mine else ""
                if u not in mine:
                    out.append(f"`{rel}`: `apps: [{a}]` — retired key, move to `surfaces:`{where}")
        for key in ("extra", "outputs"):
            blob = json.dumps(fm.get(key) or {}, ensure_ascii=False)
            for m in site_re.findall(blob):
                u = norm_url(m.rstrip(".,;"))
                if u not in decl and not any(u.startswith(d) or d.startswith(u) for d in mine):
                    out.append(f"`{rel}`: `{key}` carries {u} — declare it in `surfaces:` (the string may stay as prose)")
    return sorted(set(out))


def owner_for(repo: str, by_repo: dict[str, list[dict]]) -> tuple[dict | None, str]:
    """The one page that should declare this repo's surfaces, or (None, reason)."""
    cands = by_repo.get(repo, [])
    if not cands:
        return None, "no KB page has this source_repo"
    best_cat = min(CAT_ORDER[p["cat"]] for p in cands)
    top = [p for p in cands if CAT_ORDER[p["cat"]] == best_cat]
    if best_cat == CAT_ORDER["frameworks"]:
        live = [p for p in top if p["fm"].get("status") not in ("superseded", "retired")]
        top = live or top
        top = sorted(top, key=lambda p: p["path"])[-1:]  # newest version file name sorts last
    if len(top) == 1:
        return top[0], ""
    return None, "ambiguous owner: " + ", ".join(f"`{p['path']}`" for p in sorted(top, key=lambda p: p["path"]))


# ---- platform side ------------------------------------------------------------------
def sweep_org() -> dict[str, dict] | None:
    """{repo_lower: {name, visibility, archived}} for every org repo with Pages on. None if gh
    can't read the org (→ sweep SKIPPED, never 'everything vanished')."""
    out = sh(["gh", "api", "--paginate", f"orgs/{ORG}/repos?per_page=100&type=all",
              "--jq", ".[] | select(.has_pages==true) | [.name, .visibility, (.archived|tostring)] | @tsv"], timeout=300)
    if out is None or not out.strip():   # non-zero exit (incl. a pagination that died mid-way) or nothing readable
        return None
    res = {}
    for line in out.splitlines():
        parts = line.split("\t")
        if len(parts) >= 2:
            res[parts[0].lower()] = {"name": parts[0], "visibility": parts[1], "archived": parts[2] == "true" if len(parts) > 2 else False}
    return res


def pages_meta(repo: str) -> dict | None:
    out = sh(["gh", "api", f"repos/{ORG}/{repo}/pages",
              "--jq", '{html_url, build_type, status, branch: (.source.branch // ""), path: (.source.path // ""), public}'])
    try:
        return json.loads(out) if out and out.strip() else None
    except json.JSONDecodeError:
        return None


# ---- apply: append auto surfaces to a page's frontmatter (textual, comment-preserving) ----
def append_surfaces(path: Path, entries: list[dict]) -> None:
    text = path.read_text(encoding="utf-8")
    span = frontmatter_span(text)
    if not span:
        raise ValueError(f"{path}: no frontmatter")
    fm_text = text[span[0]:span[1]]
    lines = fm_text.split("\n")

    def flow(e: dict) -> str:
        parts = [f"url: {json.dumps(e['url'], ensure_ascii=False)}"]
        if e.get("title"):
            parts.append(f"title: {json.dumps(e['title'], ensure_ascii=False)}")
        parts.append("auto: true")
        parts.append(f"first_seen: {e.get('first_seen', TODAY)}")
        return "  - {" + ", ".join(parts) + "}"

    new = [flow(e) for e in entries]
    idx = next((i for i, l in enumerate(lines) if re.match(r"^surfaces\s*:", l)), None)
    if idx is None:
        # insert before `source_repo:` (the "source" block) if present, else at the end
        at = next((i for i, l in enumerate(lines) if re.match(r"^source_repo\s*:", l)), len(lines))
        # keep a preceding `# --- source repo` comment attached to source_repo
        while at > 0 and lines[at - 1].startswith("#"):
            at -= 1
        lines[at:at] = ["surfaces:"] + new
    else:
        head = lines[idx]
        if re.match(r"^surfaces\s*:\s*\[\s*\](\s*#.*)?$", head):
            comment = re.search(r"\s*#.*$", head)
            lines[idx] = "surfaces:" + (comment.group(0) if comment else "")
            lines[idx + 1:idx + 1] = new
        else:
            j = idx + 1
            while j < len(lines) and (lines[j].startswith((" ", "\t")) or lines[j].strip() == "" and j + 1 < len(lines) and lines[j + 1].startswith(" ")):
                j += 1
            # trim trailing blank lines inside the block so entries stay contiguous
            k = j
            while k > idx + 1 and lines[k - 1].strip() == "":
                k -= 1
            lines[k:k] = new
    path.write_text(text[:span[0]] + "\n".join(lines) + text[span[1]:], encoding="utf-8")


# ---- main ---------------------------------------------------------------------------
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="append undeclared live surfaces to their owning KB page")
    ap.add_argument("--report", help="write the attention section (issue body) here")
    ap.add_argument("--check", action="store_true", help="offline lint of surfaces/legacy shapes only")
    ap.add_argument("--no-sweep", action="store_true", help="skip the org sweep (probe declared surfaces only)")
    args = ap.parse_args()

    pages, by_repo = scan_pages()
    decl, problems = declared_surfaces(pages)
    legacy = legacy_shapes(pages, decl)

    if args.check:
        for p in problems + legacy:
            print("::warning::" if legacy and p in legacy else "::error::", p)
        sys.exit(1 if problems else 0)

    # ---- sweep + probe sites
    org = None if args.no_sweep else sweep_org()
    if org is None and not args.no_sweep:
        # Refuse to overwrite a good registry with an empty sites table (same rule as
        # gen_pipeline_registry.py). Exit 1 ≠ 2, so the workflow neither commits nor files drift.
        sys.exit("ERROR: org sweep failed (`gh api orgs/…/repos` non-zero or empty — auth? rate limit? "
                 "partial pagination?). Not writing the registry. Use --no-sweep for a probe-only dry run.")
    sites: list[dict] = []
    if org is not None:
        spoke_repos = set(by_repo)
        for key, meta in sorted(org.items()):
            if not (DS_RE.match(meta["name"]) or key in spoke_repos):
                continue
            pm = pages_meta(meta["name"]) or {}
            url = norm_url(pm.get("html_url") or f"https://ocha-dap.github.io/{meta['name']}/")
            # Is the SITE public? The Pages API says so directly (a private repo can serve a public site
            # on Enterprise); fall back to repo visibility only when the Pages settings were unreadable.
            site_public = pm["public"] if isinstance(pm.get("public"), bool) else meta["visibility"] == "public"
            if site_public:
                code, final, title, body = fetch(url)
                if title.startswith("Sign in to GitHub"):      # access-controlled Pages answer 200 with a login page
                    code, title, body = 401, "", ""
                probed = True
            else:                                              # private-repo Pages: anonymous probe is meaningless
                code, final, title, body, probed = None, url, "", "", False
            sites.append({"repo": key, "name": meta["name"], "visibility": meta["visibility"], "public": site_public, "archived": meta["archived"],
                          "url": url, "final_url": norm_url(final) if final else url, "http": code, "probed": probed, "title": title,
                          "build": pm.get("build_type") or "?", "branch": pm.get("branch") or "", "path": pm.get("path") or "",
                          "children": child_products(url, body) if ok(code) else [],
                          "ignored": IGNORE.get(key)})

    # ---- collect every surface: declared ∪ site roots ∪ discovered children
    surfaces: dict[str, dict] = {}
    for u, d in decl.items():
        surfaces[u] = {"url": u, "raw": d.get("raw") or u, "declared_by": d["page"], "kind": d.get("kind"), "title": d.get("title", ""),
                       "auto": d.get("auto", False), "access": d.get("access", "public"), "status": d.get("status", "live"),
                       "discovered": False, "repo": repo_of_url(u)}
    for s in sites:
        if s["ignored"]:
            continue
        for u in [s["url"]] + s["children"]:
            e = surfaces.setdefault(u, {"url": u, "declared_by": None, "kind": None, "title": "", "auto": False,
                                        "access": "public", "status": "live", "discovered": False, "repo": s["repo"]})
            e["discovered"] = True
            e["repo"] = e["repo"] or s["repo"]   # private sites live at <random>.pages.github.io — repo comes from the sweep
            e.setdefault("site", s["url"])
            if not s["public"] and e["declared_by"] is None:
                e["access"] = "private"          # inferred only for undeclared entries — a human's `access:` is never overridden
    # probe everything not yet probed (declared surfaces + children); private ones are not probed
    site_http = {s["url"]: (s["http"], s["title"], s["probed"]) for s in sites}
    for u, e in surfaces.items():
        if u in site_http:
            e["http"], e["live_title"], e["probed"] = site_http[u]
        elif e["access"] == "private" or e["status"] == "retired":   # can't be judged / kept for the record only
            e["http"], e["live_title"], e["probed"] = None, "", False
        else:
            code, _final, title, _ = fetch(e.get("raw") or u)   # probe the URL as written, match on the normalised form
            if title.startswith("Sign in to GitHub"):
                code, title = 401, ""
            e["http"], e["live_title"], e["probed"] = code, title, True
        if not e["title"]:
            e["title"] = e["live_title"]

    # ---- attention items
    undeclared: list[dict] = [e for e in surfaces.values() if e["declared_by"] is None and ok(e["http"])]
    # a landing page links to a product that doesn't resolve: not declarable (it isn't live), but not fine either
    broken = [e for e in surfaces.values() if e["declared_by"] is None and e["probed"] and not ok(e["http"])]
    dead = [e for e in surfaces.values() if e["declared_by"] and e["probed"] and not ok(e["http"])]
    declared_repos = {e["repo"] for e in surfaces.values() if e["declared_by"] and e["repo"]}
    swept = {s["repo"] for s in sites}
    # a declared github.io surface whose repo no longer has Pages enabled (only judged when the sweep ran)
    no_pages = sorted(r for r in declared_repos if org is not None and r not in org)

    # ---- apply: auto-declare undeclared live surfaces on their owner page
    applied: list[str] = []
    unowned: list[tuple[dict, str]] = []
    if undeclared:
        per_owner: dict[str, tuple[Path, list[dict]]] = {}
        for e in sorted(undeclared, key=lambda e: e["url"]):
            owner, why = owner_for(e["repo"] or "", by_repo)
            if owner is None:
                unowned.append((e, why))
                continue
            if args.apply:
                per_owner.setdefault(owner["path"], (ROOT / owner["path"], []))[1].append(
                    {"url": e["url"], "title": e["title"], "first_seen": TODAY})
                e["declared_by"], e["auto"] = owner["path"], True
            else:
                unowned.append((e, f"would auto-declare on `{owner['path']}` (run with --apply)"))
        for rel, (p, entries) in per_owner.items():
            append_surfaces(p, entries)
            applied.append(f"`{rel}` ← {len(entries)} surface(s): " + ", ".join(e["url"] for e in entries))

    # ---- write registry
    n_sites = len([s for s in sites if not s["ignored"]])
    n_live = len([e for e in surfaces.values() if ok(e["http"])])
    n_auto = len([e for e in surfaces.values() if e["auto"]])

    def dot(e: dict) -> str:
        if not e.get("probed"):
            return "⚪ n/a"
        return f"🟢 {e['http']}" if ok(e["http"]) else f"🔴 {e['http'] or 'ERR'}"
    kb = lambda rel: f"[{rel}](../{rel})" if rel else "—"

    def site_row(s: dict) -> str:
        mode = s["build"] + (f" `{s['branch']}{s['path']}`" if s["branch"] else "")
        owners = ", ".join(kb(p["path"]) for p in by_repo.get(s["repo"], [])) or "— **no KB page**"
        kids = [e for e in surfaces.values() if e.get("repo") == s["repo"] and e["url"] != s["url"]]
        nd = len([k for k in kids if k["declared_by"]])
        prod = f"{nd}/{len(kids)}" if kids else "—"
        st = "ignored" if s["ignored"] else ("private" if s["visibility"] != "public" else "")
        return (f"| {dot(s)} | [`{s['name']}`]({s['url']}) | {s['title'][:70] or '—'} | {mode} | "
                f"{prod} | {owners} | {st} |")

    def surf_row(e: dict) -> str:
        flag = []
        if e["declared_by"] is None:
            flag.append("**UNDECLARED**")
        if e["declared_by"] and e["probed"] and not ok(e["http"]):
            flag.append("**DEAD**")
        if e["auto"]:
            flag.append("auto")
        if e["declared_by"] and e["repo"] and not e["discovered"] and e["repo"] in swept:
            flag.append("not linked from landing")
        if e["access"] != "public":
            flag.append(e["access"])
        if e["status"] == "retired":
            flag.append("retired")
        return (f"| {dot(e)} | <{e['url']}> | {(e['title'] or '')[:70] or '—'} | {e['kind'] or '?'} | "
                f"{kb(e['declared_by'])} | {', '.join(flag) or '—'} |")

    attention: list[str] = []
    if org is None:
        attention += ["> ⏭️ **Org sweep SKIPPED** — `gh api orgs/…/repos` returned nothing (auth?). Declared surfaces were still probed; nothing is reported as undeclared.", ""]
    if unowned:
        attention += [f"## 🆕 Live but undeclared ({len(unowned)})", "",
                      "Sites/products that exist but no KB page declares. Fix by ingesting a page for the repo "
                      "(`gh workflow run kb-ingest.yml -f kind=<app|pipeline|analysis> -f target=<repo>`) or adding a `surfaces:` entry.", "",
                      "| url | title | why not auto-declared |", "|---|---|---|"]
        attention += [f"| <{e['url']}> | {(e['title'] or '')[:60]} | {why} |" for e, why in unowned]
        attention.append("")
    if applied:
        attention += [f"## ✍️ Auto-declared this run ({len(applied)} page(s))", ""] + [f"- {a}" for a in applied] + [
            "", "_Each entry carries `auto: true` — review it: set `kind:` (and a better `title:`), drop `auto`._", ""]
    if broken:
        attention += [f"## 🔗 Landing-page links that don't resolve ({len(broken)})", "",
                      "The site root links to these, but they aren't live — a broken link on the landing page (or a crawler false positive worth reporting).", "",
                      "| url | HTTP | site |", "|---|---|---|"]
        attention += [f"| <{e['url']}> | {e['http'] or 'ERR'} | <{e.get('site', '')}> |" for e in sorted(broken, key=lambda e: e["url"])]
        attention.append("")
    if dead:
        attention += [f"## 🔴 Declared but not reachable ({len(dead)})", "",
                      "| url | HTTP | declared by |", "|---|---|---|"]
        attention += [f"| <{e['url']}> | {e['http'] or 'ERR'} | {kb(e['declared_by'])} |" for e in sorted(dead, key=lambda e: e["url"])]
        attention += ["", "_Retired on purpose? Remove the entry (or set `access: private` if it's an access-controlled site)._", ""]
    if no_pages:
        attention += [f"## 🗑️ Declared repos with Pages now OFF ({len(no_pages)})", ""] + [f"- `{r}`" for r in no_pages] + [""]
    if legacy:
        attention += [f"## 🧹 Legacy URL shapes ({len(legacy)})", "", "Pre-D102 keys still carrying a published URL that `surfaces:` doesn't:", ""] + [f"- {l}" for l in legacy] + [""]
    if problems:
        attention += [f"## ⚠️ Frontmatter problems ({len(problems)})", ""] + [f"- {p}" for p in problems] + [""]
    n_undeclared = len([e for e in surfaces.values() if e["declared_by"] is None])   # every UNDECLARED row in the table below
    clean = not (unowned or broken or dead or no_pages or legacy or problems)
    assert clean or n_undeclared or dead or no_pages or legacy or problems   # summary and table can't disagree

    md = ["# Published sites registry & health", "",
          "_Generated by `scripts/gen_pages_registry.py` — DO NOT EDIT BY HAND._  ",
          f"_Snapshot: {NOW}._", "",
          "Every **GitHub Pages site** an `ocha-dap` DS repo serves, every **product** under it (the landing-page "
          "convention: `/<repo>/<product>/`), and every other published surface a KB page declares (Netlify, "
          "Quarto Pub, Azure app URLs…) — probed live. The `surfaces:` frontmatter on framework / pipeline / "
          "app / analysis pages is the declared layer; this registry is the mechanical layer that finds what "
          "the pages forgot and (with `--apply`, daily in CI) declares it for them as `auto: true` entries. "
          "Hosting/build guidance lives in [methods/static-data-apps.md](../methods/static-data-apps.md); "
          "Azure web apps stay in [deployments.md](deployments.md).", "",
          f"**{n_sites} Pages sites · {len(surfaces)} surfaces ({n_live} live, {n_auto} auto-declared awaiting review) · "
          f"{n_undeclared} undeclared · {len(dead)} dead.**", ""]
    if not clean:
        md += ["## Attention", ""] + attention
    else:
        md += ["✅ Every live site is declared and every declared surface is reachable.", ""]
    md += ["## GitHub Pages sites (one row per repo)", "",
           "| HTTP | repo → site | title | build `branch/path` | products declared/found | KB page(s) | |",
           "|:--:|---|---|---|:--:|---|---|"]
    md += [site_row(s) for s in sorted(sites, key=lambda s: (bool(s["ignored"]), s["probed"] and not ok(s["http"]), s["repo"]))]
    md += ["", "_`products` = same-site links one level below the root (`/<repo>/<x>/`) — chapters and files are not counted. "
           "**no KB page** = the repo is nobody's `source_repo` yet → ingest it._", "",
           "## Surfaces (one row per URL)", "",
           "| HTTP | url | title | kind | declared by | flags |", "|:--:|---|---|---|---|---|"]
    md += [surf_row(e) for e in sorted(surfaces.values(), key=lambda e: (e["declared_by"] is not None, ok(e["http"]), e["url"]))]
    md += ["", "Flags: **UNDECLARED** live but on no page · **DEAD** declared, not 200 · **auto** added by this script, "
           "`kind` pending human review · *not linked from landing* declared but the site root doesn't link to it "
           "(fine for deep status pages; a gap for products) · *password/private* access-controlled by design · *retired* kept for the "
           "record (`status: retired`), not probed.", "",
           "## Refresh",
           "`python scripts/gen_pages_registry.py --apply` (needs `gh` auth; private repos need an org-read PAT). "
           "Runs daily via `.github/workflows/pages-registry.yml`; `--check` is the offline lint used by `lint-docs.yml`.", ""]
    if args.no_sweep:
        print("--no-sweep: probe-only dry run — registry files NOT written (the sites table would be empty).")
    else:
        OUT_MD.write_text("\n".join(md), encoding="utf-8")
        OUT_JSON.write_text(json.dumps({"generated": NOW, "sites": sites, "surfaces": sorted(surfaces.values(), key=lambda e: e["url"])},
                                       indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if args.report:
        Path(args.report).write_text("\n".join(["# KB published-sites drift", "", f"_Generated by `scripts/gen_pages_registry.py` — {NOW}. "
                                                "Full board: `infrastructure/pages-registry.md`._", ""] + attention) + "\n", encoding="utf-8")
    print(f"{'Probed' if args.no_sweep else 'Wrote ' + OUT_MD.relative_to(ROOT).as_posix()} — {n_sites} sites, {len(surfaces)} surfaces, "
          f"{n_undeclared} undeclared ({len(broken)} broken landing links), {len(dead)} dead, {len(applied)} page(s) auto-updated.")
    for line in attention:
        if line.startswith(("## ", "- ", "| <")):
            print("  " + line[:160])
    sys.exit(0 if clean else 2)


if __name__ == "__main__":
    main()
