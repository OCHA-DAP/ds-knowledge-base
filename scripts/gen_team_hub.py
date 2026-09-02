#!/usr/bin/env python3
"""Generate the TEAM HUB — one visual landing page for every dashboard, app, and published
analysis the DS team runs, served at the KB's GitHub Pages root.

Each spoke repo has its own landing page (the one-repo-one-Pages-site convention in
methods/static-data-apps.md); this is the page above them all. It is generated, never edited:
the point is that it stays current without anyone maintaining a list.

Inputs (all committed — no network, no secrets; safe to run at Pages deploy time):
  infrastructure/.pages-registry.json   every Pages site + product + declared surface, probed
                                        (gen_pages_registry.py, daily)            → the cards
  infrastructure/.infra-baseline.json   the Azure web-app estate (check_infra_drift.py, daily)
                                        → Azure apps no KB page declares + Running/Stopped state
  infrastructure/deployments.md         the hand table's app→repo column (Azure enrichment only)
  frameworks/ pipelines/ apps/ analysis/  frontmatter of the page that DECLARES each surface →
                                        blurb (purpose/summary), hazard, country, group, access
  hub/shots/*.jpg                       thumbnails (hub_screenshots.py, weekly) — optional

Outputs:
  hub/hub.json   the card inventory (what hub_screenshots.py captures; also a public JSON feed)
  hub.html       the page — site.yml copies it to the Pages root (site/index.html)

Usage:  python scripts/gen_team_hub.py [--check]
        --check   exit 2 if hub.html/hub.json on disk differ from what would be generated
Exit:   0 ok · 1 an input is missing/unparseable (nothing written — a good hub is never replaced
        by an empty one) · 2 (--check) stale
Needs:  pyyaml.
"""
from __future__ import annotations
import argparse
import datetime as dt
import hashlib
import html
import json
import re
import sys
import urllib.parse
from collections import defaultdict
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("Needs pyyaml:  uv pip install pyyaml")

ROOT = Path(__file__).resolve().parent.parent
REGISTRY = ROOT / "infrastructure" / ".pages-registry.json"
INFRA = ROOT / "infrastructure" / ".infra-baseline.json"
DEPLOYMENTS = ROOT / "infrastructure" / "deployments.md"
SHOTS = ROOT / "hub" / "shots"
OUT_JSON = ROOT / "hub" / "hub.json"
OUT_HTML = ROOT / "hub.html"
SCAN = ["frameworks", "pipelines", "apps", "analysis"]
GH = "https://github.com/OCHA-DAP"
KB_URL = f"{GH}/ds-knowledge-base"
SITE_ROOT = "https://ocha-dap.github.io/ds-knowledge-base/"

# Azure apps that are plumbing, not products — never cards. Reason recorded so the list is reviewable.
AZURE_EXCLUDE = {
    "chd-ds-kb-mcp": "KB MCP server (connector, not a page)",
    "chd-ds-kb-mcp-internal": "KB MCP server, token-gated tier",
    "chd-github-runner": "self-hosted GHA runner",
    "listmonk-demo": "mailing-list service trial",
    "dev-testaccess": "access test app",
    "chd-demo": "scratch demo app",
    "DataScienceFTP": "SFTP file drop (FIMS plan), not a web surface",
    "chd-ds-ait-report-status": "Entra Easy-Auth trial page (owner unidentified — deployments.md)",
}
# Surfaces on the KB's own site: gen_pages_registry.py IGNOREs ds-knowledge-base (it documents itself),
# so the AA site is declared here instead.
CURATED = [
    {"url": SITE_ROOT + "anticipatory-action/", "title": "Anticipatory Action frameworks — status map",
     "blurb": "Every OCHA/CERF AA framework on one map: active, recently triggered, expired, in development — "
              "with activations, trigger windows, funding and the published framework document.",
     "kind": "dashboard", "group": "framework", "repo": "ds-knowledge-base",
     "kb_page": "infrastructure/automation.md", "hazards": [], "countries": []},
    {"url": SITE_ROOT + "anticipatory-action/triggers.html", "title": "AA trigger statistics",
     "blurb": "How the portfolio's triggers have performed: activation rates, return periods and "
              "framework-by-framework detail, refreshed daily from the tracking database.",
     "kind": "dashboard", "group": "framework", "repo": "ds-knowledge-base",
     "kb_page": "infrastructure/automation.md", "hazards": [], "countries": []},
    {"url": SITE_ROOT + "anticipatory-action/global.html", "title": "All organisations' AA frameworks",
     "blurb": "The cross-organisation view — OCHA, IFRC, WFP, FAO, Start Network and others — one row "
              "per framework, from the KB's external-frameworks catalog.",
     "kind": "dashboard", "group": "framework", "repo": "ds-knowledge-base",
     "kb_page": "catalog-global.md", "hazards": [], "countries": []},
]

GROUPS = {   # content_type of the declaring KB page → section (order matters)
    "framework": ("Anticipatory action frameworks", "Trigger monitoring, forecast checks and design notes for the frameworks in the OCHA/CERF portfolio."),
    "pipeline": ("Monitoring, alerts & data", "Living systems: near-real-time monitoring, alert pages, and the data mirrors they publish."),
    "app": ("Apps & explorers", "Interactive tools — hosted on Azure or as static sites — for exploring exposure, forecasts and allocations."),
    "analysis": ("Analyses & reports", "Rendered analyses, reports and slide decks: regional overviews, ad-hoc activations, method studies."),
}
GROUP_ORDER = list(GROUPS)
KIND_LABEL = {"landing": "site", "app": "app", "report": "report", "book": "book", "dashboard": "dashboard",
              "form": "form", "download": "downloads", "docs": "docs", "status": "status", "other": ""}
HAZARD_LABEL = {"drought": "Drought", "flood": "Flood", "flooding": "Flood", "tropical-cyclone": "Tropical cyclone",
                "storm": "Tropical cyclone", "cyclone": "Tropical cyclone", "hurricane": "Tropical cyclone",
                "cholera": "Cholera", "disease": "Infectious disease", "infectious-disease": "Infectious disease",
                "earthquake": "Earthquake", "conflict": "Conflict", "food-insecurity": "Food insecurity",
                "heatwave": "Heatwave", "dry-spell": "Drought", "multi": "Multi-hazard"}
COUNTRY = {
    "AFG": "Afghanistan", "BFA": "Burkina Faso", "BGD": "Bangladesh", "CAF": "Central African Rep.",
    "CMR": "Cameroon", "COD": "DR Congo", "CUB": "Cuba", "ETH": "Ethiopia", "FJI": "Fiji", "GTM": "Guatemala",
    "HND": "Honduras", "HTI": "Haiti", "KEN": "Kenya", "LBN": "Lebanon", "MDG": "Madagascar", "MLI": "Mali",
    "MMR": "Myanmar", "MOZ": "Mozambique", "MRT": "Mauritania", "MWI": "Malawi", "NER": "Niger",
    "NGA": "Nigeria", "NIC": "Nicaragua", "NPL": "Nepal", "PAK": "Pakistan", "PHL": "Philippines",
    "PLW": "Palau", "SDN": "Sudan", "SLV": "El Salvador", "SOM": "Somalia", "SSD": "South Sudan",
    "SYR": "Syria", "TCD": "Chad", "UGA": "Uganda", "VEN": "Venezuela", "VUT": "Vanuatu", "YEM": "Yemen",
    "ZMB": "Zambia", "ZWE": "Zimbabwe",
}
# Repo-name fallbacks when the declaring page carries no hazard/country (pipelines, apps).
REPO_HAZARD = [(re.compile(p, re.I), h) for p, h in [
    (r"drought|dry-corridor|seas5|asap|biomasse", "drought"), (r"flood|gfm|floodexposure", "flood"),
    (r"storm|cyclone|hurricane|nhc|tropical", "tropical-cyclone"), (r"cholera", "cholera"),
    (r"earthquake", "earthquake"), (r"acled|conflict", "conflict"), (r"ipc|fewsnet|ch-|food", "food-insecurity"),
]]
ISO3_IN_NAME = re.compile(r"(?:^|-)(aa-|pa-aa-)?([a-z]{3})-(?:drought|flood|floods|flooding|cyclone|cyclones|storms|hurricanes|cholera|earthquake|monitoring|trigger)", re.I)


# ── inputs ──────────────────────────────────────────────────────────────────────────────────

def die(msg: str) -> None:
    print(f"::error::{msg}", file=sys.stderr)
    sys.exit(1)


def frontmatter(path: Path) -> dict | None:
    text = path.read_text(encoding="utf-8", errors="replace")
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    if end < 0:
        return None
    try:
        fm = yaml.safe_load(text[3:end])
    except yaml.YAMLError:
        return None
    return fm if isinstance(fm, dict) else None


def load_pages() -> dict[str, dict]:
    pages: dict[str, dict] = {}
    for d in SCAN:
        for p in sorted((ROOT / d).rglob("*.md")):
            if p.name.startswith(("_", "README")):
                continue
            fm = frontmatter(p)
            if fm:
                pages[p.relative_to(ROOT).as_posix()] = fm
    if not pages:
        die("no KB pages parsed")
    return pages


def load_json(path: Path, key: str) -> dict:
    if not path.exists():
        die(f"missing input {path.relative_to(ROOT)} — run its generator first")
    try:
        d = json.loads(path.read_text())
    except json.JSONDecodeError as e:
        die(f"{path.name}: {e}")
    if key not in d:
        die(f"{path.name}: no '{key}' key")
    return d


def deployments_repo_map() -> dict[str, str]:
    """Azure app name → spoke repo, from deployments.md's hand table (the only place it's typed)."""
    out: dict[str, str] = {}
    if not DEPLOYMENTS.exists():
        return out
    for line in DEPLOYMENTS.read_text().splitlines():
        m = re.match(r"^\|\s*([A-Za-z0-9._-]+)\s*\|[^|]*\|\s*`?([A-Za-z0-9._-]+)`?", line)
        if m and m.group(2) not in ("repo", "—", "-"):
            out[m.group(1)] = m.group(2)
    return out


# ── derivation ──────────────────────────────────────────────────────────────────────────────

def as_list(v) -> list:
    if v is None:
        return []
    return list(v) if isinstance(v, (list, tuple)) else [v]


def norm_hazards(vals, repo: str) -> list[str]:
    out: list[str] = []
    for v in vals:
        v = str(v).lower().strip()
        if v in ("n/a", "na", "none", "-", "—", ""):
            continue
        lab = HAZARD_LABEL.get(v)
        if lab is None:                       # unknown token: title-case it rather than drop it
            lab = v.replace("-", " ").capitalize() if v else None
        if lab and lab not in out:
            out.append(lab)
    if not out:
        for rx, h in REPO_HAZARD:
            if rx.search(repo or ""):
                out.append(HAZARD_LABEL[h])
                break
    return out


def norm_countries(fm: dict, page_path: str, repo: str) -> list[str]:
    isos: list[str] = []
    for k in ("country_iso3", "countries", "iso3"):
        for v in as_list(fm.get(k)):
            if isinstance(v, str) and len(v) == 3:
                isos.append(v.upper())
    if not isos and page_path.startswith("frameworks/"):
        m = re.match(r"frameworks/([a-z]{3})-", page_path)
        if m:
            isos.append(m.group(1).upper())
    if not isos and repo:
        m = ISO3_IN_NAME.search(repo)
        if m and m.group(2).upper() in COUNTRY:
            isos.append(m.group(2).upper())
    return [COUNTRY.get(i, i) for i in dict.fromkeys(isos)]


def repo_of_page(fm: dict) -> str:
    """Bare repo name from a page's `source_repo` ("ocha-dap/ds-x", "OCHA-DAP/ds-x", or a local path)."""
    for v in as_list(fm.get("source_repo")):
        m = SLUG_RE.search(str(v))
        if m:
            return m.group(1)
    return ""


SLUG_RE = re.compile(r"(?:ocha-dap|OCHA-DAP)/([A-Za-z0-9._-]+)")


def host_of(url: str) -> str:
    net = urllib.parse.urlparse(url).netloc.lower()
    if net.endswith("github.io"):
        return "github-pages"
    if "azurewebsites.net" in net:
        return "azure"
    if "netlify.app" in net:
        return "netlify"
    if "quarto.pub" in net:
        return "quarto-pub"
    if "shinyapps.io" in net:
        return "shinyapps"
    return "web"


HOST_LABEL = {"github-pages": "GitHub Pages", "azure": "Azure", "netlify": "Netlify", "quarto-pub": "Quarto Pub",
              "shinyapps": "shinyapps.io", "web": "Web"}


def slug_for(url: str) -> str:
    """Stable, readable file stem for a URL: host-less path, sanitised; hash suffix guards collisions."""
    u = urllib.parse.urlparse(url)
    base = re.sub(r"[^A-Za-z0-9]+", "-", (u.netloc.split(".")[0] if not u.netloc.endswith("github.io") else "") + u.path).strip("-")
    base = re.sub(r"^ocha-dap-", "", base) or "root"
    return f"{base[:60]}-{hashlib.sha1(url.encode()).hexdigest()[:6]}"


def clean(s) -> str:
    return re.sub(r"\s+", " ", html.unescape(str(s or ""))).strip()


def best_blurb(fm: dict, title: str) -> str:
    for k in ("purpose", "summary", "description"):
        v = fm.get(k)
        if isinstance(v, str) and clean(v) and clean(v).lower() != title.lower():
            return clean(v)
    return ""


# Live <title>s that name the hosting or a scaffold, not the product — never promoted to a card title.
GENERIC_TITLE = re.compile(r"azure app service|welcome|^index$|untitled|^ds-[a-z0-9-]+$|^[a-z0-9 ]{1,24}$|"
                           r"^(aa design|ds review — restricted)$", re.I)
SITE_SUFFIX = re.compile(r"\s*[—|·-]\s*(OCHA Centre for Humanitarian Data|OCHA Centre for Humanitarian Da[a-z]*|pa-anticipatory-action)\s*$", re.I)
ASIDE = re.compile(r"\s*\((?:[^()]|\([^()]*\))*\)\s*$")   # one trailing parenthetical, may nest once


def pick_title(kb_title: str, live_title: str, fm: dict) -> tuple[str, str]:
    """(title, blurb). The KB's `surfaces[].title` is often a descriptive note ("Interactive map and
    chart showing…", "… (Quarto, Netlify; site id …)") while the live <title> is the product's own
    name — but live titles can be scaffolding ("cerf predictor", "Microsoft Azure App Service").
    Rule: a short KB title (trailing KB-internal aside stripped) wins; a long one yields to a
    non-generic live title, else to the page's `name`; whatever long text lost becomes the blurb
    when the page has no purpose/summary of its own. The blurb never repeats the title."""
    kb = clean(kb_title)
    kb_short = ASIDE.sub("", kb).strip() or kb
    live = SITE_SUFFIX.sub("", clean(live_title)).strip()
    live_ok = bool(live) and not GENERIC_TITLE.search(live) and len(live) <= 90
    name = clean(fm.get("name"))
    if len(kb_short) <= 60:
        title, spare = kb_short, ""
    elif live_ok:
        title, spare = live, kb_short
    elif name:
        title, spare = humanize_app(name), kb_short
    else:
        title, spare = kb_short[:87].rsplit(" ", 1)[0] + "…", kb_short
    blurb = best_blurb(fm, title) or spare
    if blurb.lower().rstrip(".") == title.lower().rstrip(".") or ASIDE.sub("", blurb).strip().lower() == title.lower():
        blurb = ""
    return title, blurb


ACRONYMS = {"kb": "KB", "ipc": "IPC", "cerf": "CERF", "rosea": "ROSEA", "aa": "AA", "seas5": "SEAS5", "ds": "",
            "chd": "", "pa": "", "glb": "Global", "hti": "Haiti", "fji": "Fiji", "nga": "Nigeria", "bgd": "Bangladesh",
            "cub": "Cuba", "app": ""}


def humanize_app(app: str) -> str:
    words = [ACRONYMS.get(w.lower(), w) for w in app.split("-")]
    return " ".join(w for w in words if w).strip().capitalize() if not any(w.isupper() for w in words if w) \
        else " ".join(w for w in words if w).strip()


def page_group(page_path: str, fm: dict) -> str:
    ct = str(fm.get("content_type") or page_path.split("/")[0].rstrip("s"))
    return ct if ct in GROUPS else "analysis"


def status_of(http, access: str, declared_status: str | None, probed: bool) -> str:
    if declared_status == "retired":
        return "retired"
    if access in ("private", "password") and not probed:
        return "live"
    if http is None:
        return "live" if not probed else "dead"
    if http == 403:
        return "stopped"
    return "live" if http < 400 else "dead"


def build_cards(reg: dict, infra: dict, pages: dict[str, dict]) -> list[dict]:
    cards: list[dict] = []
    seen_urls: set[str] = set()
    site_by_repo = {s["repo"]: s for s in reg.get("sites", [])}

    # 1. every declared/discovered surface in the registry
    for sf in reg.get("surfaces", []):
        url = sf["url"]
        if url in seen_urls:
            continue
        seen_urls.add(url)
        page_path = sf.get("declared_by") or ""
        fm = pages.get(page_path, {})
        repo = sf.get("repo") or repo_of_page(fm)
        title, blurb = pick_title(sf.get("title") or clean(site_by_repo.get(repo, {}).get("title")) or repo or url,
                                  sf.get("live_title") or "", fm)
        access = sf.get("access") or ("internal" if str(fm.get("visibility")) == "internal" and host_of(url) == "azure" else "public")
        cards.append({
            "url": url, "slug": slug_for(url), "title": title, "blurb": blurb,
            "kind": sf.get("kind") or "", "group": page_group(page_path, fm) if page_path else "analysis",
            "repo": repo, "repo_url": f"{GH}/{repo}" if repo else "", "kb_page": page_path,
            "kb_url": f"{KB_URL}/blob/main/{page_path}" if page_path else "",
            "host": host_of(url), "access": access,
            "status": status_of(sf.get("http"), access, sf.get("status"), bool(sf.get("probed"))),
            "http": sf.get("http"), "hazards": norm_hazards(as_list(fm.get("hazard")), repo),
            "countries": norm_countries(fm, page_path, repo), "auto": bool(sf.get("auto")),
            "is_landing": urllib.parse.urlparse(url).path.count("/") <= 2 and host_of(url) == "github-pages",
        })

    # 2. Pages sites the registry swept but nothing declares yet (undeclared → still show, flagged)
    for s in reg.get("sites", []):
        url = s.get("final_url") or s["url"]
        if s.get("ignored") or url in seen_urls or not s.get("probed"):
            continue
        seen_urls.add(url)
        repo = s["repo"]
        cards.append({
            "url": url, "slug": slug_for(url), "title": clean(s.get("title")) or repo, "blurb": "",
            "kind": "landing", "group": "analysis", "repo": repo, "repo_url": f"{GH}/{repo}", "kb_page": "",
            "kb_url": "", "host": "github-pages", "access": "public",
            "status": status_of(s.get("http"), "public", None, True), "http": s.get("http"),
            "hazards": norm_hazards([], repo), "countries": norm_countries({}, "", repo), "auto": True,
            "is_landing": True,
        })

    # 3. Azure web apps from the estate baseline that no surface covers
    repo_map = deployments_repo_map()
    azure_hosts = {urllib.parse.urlparse(c["url"]).netloc.lower() for c in cards if c["host"] == "azure"}
    for app, meta in sorted(infra.get("azure", {}).items()):
        if app in AZURE_EXCLUDE:
            continue
        host = (meta.get("host") or "").lower()
        if not host or host in azure_hosts:
            # already a card via a declared surface — the estate's state is the authority on whether
            # the app is up: Stopped → stopped; Running but the probe failed → still live, flagged
            # (the shared plan throws transient 503s under memory pressure — deployments.md)
            if host in azure_hosts:
                running = str(meta.get("state")).lower() == "running"
                for c in cards:
                    if urllib.parse.urlparse(c["url"]).netloc.lower() == host:
                        if not running:
                            c["status"] = "stopped"
                        elif c["status"] == "dead":
                            c["status"], c["probe_failed"] = "live", True
            continue
        url = f"https://{host}/"
        repo = repo_map.get(app, "")
        # match a KB app page by deployment.ref for enrichment
        page_path, fm = "", {}
        for pp, f in pages.items():
            dep = f.get("deployment") or {}
            if isinstance(dep, dict) and str(dep.get("ref") or "").strip() == app:
                page_path, fm = pp, f
                break
        title = humanize_app(app)
        cards.append({
            "url": url, "slug": slug_for(url), "title": title,
            "blurb": best_blurb(fm, title) or (f"Azure web app {app}" + (f" from {repo}" if repo else "")
                                              + " — not yet described in the knowledge base."),
            "kind": "app", "group": page_group(page_path, fm) if page_path else "app", "repo": repo,
            "repo_url": f"{GH}/{repo}" if repo else "", "kb_page": page_path,
            "kb_url": f"{KB_URL}/blob/main/{page_path}" if page_path else "", "host": "azure",
            "access": "internal", "status": "live" if str(meta.get("state")).lower() == "running" else "stopped",
            "http": None, "hazards": norm_hazards(as_list(fm.get("hazard")), repo or app),
            "countries": norm_countries(fm, page_path, repo or app), "auto": not page_path, "is_landing": False,
        })

    # 4. the KB's own curated surfaces
    for c in CURATED:
        if c["url"] in seen_urls:
            continue
        cards.append({**c, "slug": slug_for(c["url"]), "repo_url": f"{GH}/{c['repo']}",
                      "kb_url": f"{KB_URL}/blob/main/{c['kb_page']}", "host": "github-pages", "access": "public",
                      "status": "live", "http": 200, "auto": False, "is_landing": False})

    # thumbnails present?
    for c in cards:
        shot = SHOTS / f"{c['slug']}.jpg"
        c["shot"] = f"hub/shots/{shot.name}" if shot.exists() else ""
    return cards


# ── render ──────────────────────────────────────────────────────────────────────────────────

def e(s) -> str:
    return html.escape(str(s or ""), quote=True)


def chips(card: dict) -> str:
    out = []
    for h in card["hazards"]:
        out.append(f'<span class="tag tag-h">{e(h)}</span>')
    for c in card["countries"]:
        out.append(f'<span class="tag tag-c">{e(c)}</span>')
    return "".join(out)


def badge(card: dict) -> str:
    b = [f'<span class="badge">{e(HOST_LABEL.get(card["host"], "Web"))}</span>']
    if card["access"] in ("internal", "password", "private"):
        lab = {"internal": "internal", "password": "password", "private": "private repo"}[card["access"]]
        b.append(f'<span class="badge badge-lock" title="Not publicly accessible">🔒 {lab}</span>')
    if card.get("probe_failed"):
        b.append(f'<span class="badge badge-warn" title="Azure reports the app Running, but the last daily probe got HTTP {e(card["http"])} — usually the shared plan under memory pressure">probe failed</span>')
    if card["status"] == "dead":
        b.append('<span class="badge badge-bad" title="Last probe returned an error">unreachable</span>')
    elif card["status"] == "stopped":
        b.append('<span class="badge badge-bad" title="Azure app is stopped">stopped</span>')
    elif card["status"] == "retired":
        b.append('<span class="badge badge-mute">retired</span>')
    return "".join(b)


def thumb(card: dict, small=False) -> str:
    if card["shot"]:
        return (f'<span class="shot"><img src="{e(card["shot"])}" alt="" loading="lazy" '
                f'width="640" height="400"></span>')
    ini = "".join(w[0] for w in re.findall(r"[A-Za-z]+", card["title"])[:2]).upper() or "•"
    lock = "🔒" if card["access"] != "public" else ""
    return f'<span class="shot shot-ph" aria-hidden="true"><span>{lock or e(ini)}</span><small>{e(HOST_LABEL.get(card["host"], "Web"))}</small></span>'


def card_html(card: dict, compact=False) -> str:
    data = " ".join([
        f'data-h="{e("|".join(card["hazards"]))}"', f'data-c="{e("|".join(card["countries"]))}"',
        f'data-host="{e(card["host"])}"', f'data-g="{e(card["group"])}"',
        f'data-q="{e((card["title"] + " " + card["blurb"] + " " + card["repo"] + " " + " ".join(card["hazards"] + card["countries"])).lower())}"',
    ])
    kind = KIND_LABEL.get(card["kind"], card["kind"])
    kb = f'<a class="meta-link" href="{e(card["kb_url"])}" title="KB page">KB page</a>' if card["kb_url"] else ""
    repo = f'<a class="meta-link" href="{e(card["repo_url"])}" title="Source repository">{e(card["repo"])}</a>' if card["repo"] else ""
    return f"""<article class="k{' k-compact' if compact else ''}" {data}>
  <a class="k-main" href="{e(card["url"])}">
    {thumb(card)}
    <span class="body">
      <h3>{e(card["title"])}{f' <span class="kind">{e(kind)}</span>' if kind else ''}</h3>
      {f'<p>{e(card["blurb"])}</p>' if card["blurb"] else ''}
      <span class="tags">{chips(card)}</span>
    </span>
  </a>
  <span class="foot"><span class="badges">{badge(card)}</span><span class="meta">{repo}{kb}</span></span>
</article>"""


def family_html(repo: str, cards: list[dict]) -> str:
    """A repo with several products: landing card first, its products as compact cards under it."""
    landing = next((c for c in cards if c["is_landing"]), None)
    products = [c for c in cards if c is not landing]
    head = ""
    if landing:
        head = f'<a class="fam-head" href="{e(landing["url"])}"><span>{e(landing["title"])}</span><em>{e(repo)} · {len(products)} pages ↗</em></a>'
    else:
        head = f'<a class="fam-head" href="{e(GH + "/" + repo)}"><span>{e(repo)}</span><em>{len(products)} pages</em></a>'
    inner = "\n".join(card_html(c, compact=True) for c in (products or cards))
    hz = "|".join(sorted({h for c in cards for h in c["hazards"]}))
    co = "|".join(sorted({x for c in cards for x in c["countries"]}))
    return f'<section class="fam" data-h="{e(hz)}" data-c="{e(co)}">{head}<div class="grid grid-fam">{inner}</div></section>'


def section_html(group: str, cards: list[dict]) -> str:
    title, sub = GROUPS[group]
    by_repo: dict[str, list[dict]] = defaultdict(list)
    for c in cards:
        by_repo[c["repo"] or c["url"]].append(c)
    # sort: families with most products first, then title
    blocks: list[str] = []
    singles: list[dict] = []
    for repo, cs in sorted(by_repo.items(), key=lambda kv: (-len(kv[1]), kv[0])):
        # a "family" = several GitHub Pages products of one repo (the landing-page convention);
        # the repo's other surfaces (an Azure twin, a Netlify book) stay as ordinary cards
        fam = [c for c in cs if c["host"] == "github-pages"]
        if len(fam) > 1:
            blocks.append(family_html(repo, sorted(fam, key=lambda c: (not c["is_landing"], c["title"].lower()))))
            singles.extend(c for c in cs if c not in fam)
        else:
            singles.extend(cs)
    singles.sort(key=lambda c: (c["countries"][:1] or ["~"], c["title"].lower()))
    grid = f'<div class="grid">{"".join(card_html(c) for c in singles)}</div>' if singles else ""
    return f"""<section class="sec" id="{e(group)}" data-g="{e(group)}">
  <h2>{e(title)} <span class="n">{len(cards)}</span></h2>
  <p class="sub">{e(sub)}</p>
  {"".join(blocks)}
  {grid}
</section>"""


CSS = """
:root { --b5:#269777; --b6:#1e795f; --b7:#18614c; --b05:#e9f5f1; --b1:#d4eae4;
        --n9:#1f2324; --n8:#3f4748; --n7:#5e6a6b; --n3:#c9d1d1; --n05:#f5f7f7; --r:#c7342d; --a:#d97a12; }
* { box-sizing:border-box; }
html { scroll-behavior:smooth; }
body { margin:0; background:var(--n05); color:var(--n9); line-height:1.5;
       font-family:'Roboto',system-ui,-apple-system,'Segoe UI','Helvetica Neue',Arial,sans-serif; }
a { color:var(--b6); }
.wrap { max-width:1240px; margin:0 auto; background:#fff; min-height:100vh; box-shadow:0 0 40px rgba(31,35,36,.06); }
.hero { position:relative; overflow:hidden; background:var(--b6); padding:52px 44px 44px; }
.hero canvas { position:absolute; inset:0; width:100%; height:100%; z-index:0; }
.hero .inner { position:relative; z-index:1; display:flex; gap:32px; align-items:flex-end; flex-wrap:wrap; }
.hero .txt { flex:1 1 480px; }
.eyebrow { font-size:11px; letter-spacing:.15em; text-transform:uppercase; font-weight:700; color:rgba(255,255,255,.88); margin:0 0 12px; }
.hero h1 { font-family:'Merriweather',Georgia,serif; font-weight:700; font-size:34px; line-height:1.2; color:#fff; margin:0 0 12px; text-shadow:0 2px 16px rgba(0,0,0,.28); }
.hero p { margin:0; font-size:15px; line-height:1.6; color:#fff; max-width:66ch; text-shadow:0 1px 10px rgba(0,0,0,.25); }
.stats { display:flex; gap:22px; flex-wrap:wrap; color:#fff; }
.stats b { display:block; font-family:'Merriweather',Georgia,serif; font-size:28px; line-height:1; }
.stats span { font-size:11px; text-transform:uppercase; letter-spacing:.1em; opacity:.85; }
/* filter bar */
.bar { position:sticky; top:0; z-index:5; background:#fff; border-bottom:1px solid #e2e7e7; padding:12px 44px; display:flex; gap:10px; flex-wrap:wrap; align-items:center; }
.bar input { flex:1 1 260px; font:inherit; font-size:14px; padding:9px 12px; border:1px solid var(--n3); border-radius:5px; }
.bar input:focus { outline:none; border-color:var(--b5); box-shadow:0 0 0 3px var(--b1); }
.bar select { font:inherit; font-size:13px; padding:8px 10px; border:1px solid var(--n3); border-radius:5px; background:#fff; color:var(--n8); }
.bar .cnt { font-size:12px; color:var(--n7); margin-left:auto; white-space:nowrap; }
.bar button { font:inherit; font-size:12px; padding:7px 11px; border:1px solid var(--n3); background:#fff; border-radius:5px; color:var(--n8); cursor:pointer; }
.bar button:hover { border-color:var(--b5); color:var(--b7); }
.toc { display:flex; gap:6px; flex-wrap:wrap; padding:14px 44px 0; }
.toc a { font-size:12px; text-decoration:none; color:var(--b7); background:var(--b05); border:1px solid var(--b1); border-radius:14px; padding:4px 11px; }
.toc a:hover { background:var(--b1); }
/* sections */
main { padding:8px 44px 8px; }
.sec { padding-top:30px; }
.sec h2 { font-family:'Merriweather',Georgia,serif; font-size:22px; color:var(--n9); margin:0 0 4px; }
.sec h2 .n { font:500 12px 'Roboto',sans-serif; color:var(--n7); background:var(--n05); border-radius:12px; padding:2px 9px; vertical-align:middle; margin-left:6px; }
.sec .sub { margin:0 0 18px; color:var(--n7); font-size:13.5px; max-width:80ch; }
.grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(280px,1fr)); gap:16px; margin-bottom:18px; }
.fam { border:1px solid #e2e7e7; border-left:4px solid var(--b5); border-radius:6px; padding:14px 16px 2px; margin-bottom:16px; background:#fbfcfc; }
.fam-head { display:flex; justify-content:space-between; align-items:baseline; gap:12px; text-decoration:none; margin:0 0 12px; }
.fam-head span { font-family:'Merriweather',Georgia,serif; font-weight:700; font-size:16px; color:var(--b7); }
.fam-head em { font-style:normal; font-size:11px; color:var(--n7); text-transform:uppercase; letter-spacing:.06em; white-space:nowrap; }
.fam-head:hover span { text-decoration:underline; }
.grid-fam { grid-template-columns:repeat(auto-fill,minmax(230px,1fr)); gap:12px; }
/* cards */
.k { display:flex; flex-direction:column; background:#fff; border:1px solid #e2e7e7; border-radius:6px; overflow:hidden;
     transition:box-shadow .18s ease, transform .18s ease; }
.k:hover { box-shadow:0 6px 24px rgba(31,35,36,.12); transform:translateY(-2px); }
.k-main { display:flex; flex-direction:column; text-decoration:none; color:inherit; flex:1; }
.k-main:focus-visible { outline:3px solid var(--b1); }
.shot { display:block; aspect-ratio:16/10; background:var(--n05); border-bottom:1px solid #eef1f1; overflow:hidden; }
.shot img { display:block; width:100%; height:100%; object-fit:cover; object-position:top; }
.shot-ph { display:flex; flex-direction:column; align-items:center; justify-content:center; gap:4px; color:var(--b6);
           background:linear-gradient(135deg,var(--b05),#fff); }
.shot-ph span { font-family:'Merriweather',Georgia,serif; font-size:30px; font-weight:700; }
.shot-ph small { font-size:10px; text-transform:uppercase; letter-spacing:.1em; color:var(--n7); }
.body { display:flex; flex-direction:column; flex:1; padding:12px 14px 10px; }
.k h3 { font-family:'Merriweather',Georgia,serif; margin:0 0 6px; font-size:15px; font-weight:700; color:var(--b6); line-height:1.3; }
.k h3 .kind { font:600 9.5px 'Roboto',sans-serif; text-transform:uppercase; letter-spacing:.08em; color:var(--n7); margin-left:6px; vertical-align:middle; }
.k p { margin:0 0 10px; font-size:13px; color:var(--n8); line-height:1.5; flex:1; display:-webkit-box; -webkit-line-clamp:4; -webkit-box-orient:vertical; overflow:hidden; }
.k-compact p { -webkit-line-clamp:2; font-size:12.5px; }
.k-compact h3 { font-size:14px; }
.tags { display:flex; flex-wrap:wrap; gap:4px; }
.tag { font-size:10px; padding:2px 7px; border-radius:10px; letter-spacing:.03em; }
.tag-h { background:var(--b05); color:var(--b7); border:1px solid var(--b1); }
.tag-c { background:#f2f4f4; color:var(--n8); border:1px solid #e2e7e7; }
.foot { display:flex; justify-content:space-between; align-items:center; gap:8px; padding:8px 14px; border-top:1px solid #f0f3f3; font-size:10.5px; color:var(--n7); }
.badges { display:flex; gap:5px; flex-wrap:wrap; }
.badge { text-transform:uppercase; letter-spacing:.06em; font-weight:600; font-size:9.5px; padding:2px 6px; border-radius:3px; background:var(--n05); color:var(--n7); }
.badge-lock { background:#fff5e8; color:#8a4b00; }
.badge-bad { background:#fdeeed; color:var(--r); }
.badge-warn { background:#fff5e8; color:var(--a); }
.badge-mute { background:#eee; color:#777; }
.meta { display:flex; gap:8px; white-space:nowrap; overflow:hidden; }
.meta-link { color:var(--n7); text-decoration:none; overflow:hidden; text-overflow:ellipsis; max-width:160px; }
.meta-link:hover { color:var(--b6); text-decoration:underline; }
/* archive */
details.arch { margin:26px 44px 10px; border:1px solid #e2e7e7; border-radius:6px; background:#fafbfb; }
details.arch summary { cursor:pointer; padding:12px 16px; font-weight:500; color:var(--n8); font-size:14px; }
details.arch .grid { padding:6px 16px 4px; }
details.arch .k { opacity:.8; }
.empty { display:none; padding:40px 0; text-align:center; color:var(--n7); }
.wrap.none .empty { display:block; }
.note { margin:30px 44px 40px; padding:13px 17px; border-radius:4px; background:var(--b05); border-left:5px solid var(--b5); font-size:12.5px; color:var(--n8); line-height:1.6; }
.note code { background:#fff; border:1px solid var(--b1); padding:1.5px 6px; border-radius:3px; font-size:11.5px; color:var(--b7); }
.note p { margin:0 0 8px; } .note p:last-child { margin:0; }
.hide { display:none !important; }
@media (max-width:640px) {
  .hero { padding:36px 20px 30px; } .hero h1 { font-size:26px; }
  .bar, .toc, main { padding-left:18px; padding-right:18px; } details.arch, .note { margin-left:18px; margin-right:18px; }
}
@media (prefers-reduced-motion:reduce) { .k, .k:hover { transition:none; transform:none; } }
"""

JS = r"""
(function () {
  // particle hero — same lineage as the spoke landing pages (ds-storm-impact-harmonisation → ds-seas5-skill)
  var c = document.getElementById("bg");
  if (c && c.getContext) {
    var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    var x = c.getContext("2d"), W, H, P;
    function reset() {
      var dpr = window.devicePixelRatio || 1, r = c.parentNode.getBoundingClientRect();
      W = r.width; H = r.height; if (!W || !H) return;
      c.width = Math.round(W * dpr); c.height = Math.round(H * dpr); x.setTransform(dpr, 0, 0, dpr, 0, 0);
      var n = Math.max(24, Math.min(90, Math.floor(W * H / 7000))); P = [];
      for (var i = 0; i < n; i++) P.push({ x: Math.random() * W, y: Math.random() * H, vx: (Math.random() - .5) * .6, vy: (Math.random() - .5) * .6 });
    }
    function paint(step) {
      x.fillStyle = "#1e795f"; x.fillRect(0, 0, W, H);
      for (var i = 0; i < P.length; i++) { var p = P[i]; if (step) { p.x += p.vx; p.y += p.vy; if (p.x < 0 || p.x > W) p.vx *= -1; if (p.y < 0 || p.y > H) p.vy *= -1; } }
      for (var i = 0; i < P.length; i++) for (var j = i + 1; j < P.length; j++) {
        var dx = P[i].x - P[j].x, dy = P[i].y - P[j].y, d = Math.sqrt(dx * dx + dy * dy);
        if (d < 120) { x.strokeStyle = "rgba(255,255,255," + (0.28 * (1 - d / 120)) + ")"; x.lineWidth = 1; x.beginPath(); x.moveTo(P[i].x, P[i].y); x.lineTo(P[j].x, P[j].y); x.stroke(); }
      }
      x.fillStyle = "rgba(255,255,255,.75)";
      for (var i = 0; i < P.length; i++) { x.beginPath(); x.arc(P[i].x, P[i].y, 1.8, 0, Math.PI * 2); x.fill(); }
    }
    function loop() { paint(true); requestAnimationFrame(loop); }
    reset(); if (reduce) paint(false); else loop();
    window.addEventListener("resize", function () { reset(); if (reduce) paint(false); });
  }

  // filters — pure client-side over data-* attributes; state kept in the URL hash so a filtered view is shareable
  var q = document.getElementById("q"), hz = document.getElementById("hz"), co = document.getElementById("co"), ho = document.getElementById("ho");
  var cnt = document.getElementById("cnt"), wrap = document.querySelector(".wrap");
  var cards = Array.prototype.slice.call(document.querySelectorAll("article.k"));
  function has(attr, v) { return !v || (attr || "").split("|").indexOf(v) >= 0; }
  function apply() {
    var s = q.value.trim().toLowerCase(), h = hz.value, cc = co.value, hh = ho.value, n = 0;
    cards.forEach(function (k) {
      var ok = has(k.dataset.h, h) && has(k.dataset.c, cc) && (!hh || k.dataset.host === hh) && (!s || k.dataset.q.indexOf(s) >= 0);
      k.classList.toggle("hide", !ok); if (ok) n++;
    });
    document.querySelectorAll(".fam").forEach(function (f) { f.classList.toggle("hide", !f.querySelector("article.k:not(.hide)")); });
    document.querySelectorAll(".sec").forEach(function (sec) { sec.classList.toggle("hide", !sec.querySelector("article.k:not(.hide)")); });
    cnt.textContent = n + " of " + cards.length;
    wrap.classList.toggle("none", n === 0);
    var parts = []; if (s) parts.push("q=" + encodeURIComponent(s)); if (h) parts.push("hazard=" + encodeURIComponent(h)); if (cc) parts.push("country=" + encodeURIComponent(cc)); if (hh) parts.push("host=" + encodeURIComponent(hh));
    history.replaceState(null, "", parts.length ? "#" + parts.join("&") : location.pathname);
  }
  function fromHash() {
    var p = new URLSearchParams(location.hash.replace(/^#/, ""));
    q.value = p.get("q") || ""; hz.value = p.get("hazard") || ""; co.value = p.get("country") || ""; ho.value = p.get("host") || "";
  }
  [q, hz, co, ho].forEach(function (el) { el.addEventListener("input", apply); el.addEventListener("change", apply); });
  document.getElementById("reset").addEventListener("click", function () { q.value = ""; hz.value = ""; co.value = ""; ho.value = ""; apply(); q.focus(); });
  document.querySelectorAll(".tag").forEach(function (t) {
    t.addEventListener("click", function (ev) {
      ev.preventDefault(); ev.stopPropagation();
      var sel = t.classList.contains("tag-h") ? hz : co; sel.value = sel.value === t.textContent ? "" : t.textContent; apply();
    });
  });
  if (location.hash.indexOf("=") >= 0) fromHash();
  apply();
})();
"""


def render(cards: list[dict], generated: str, sources: dict) -> str:
    live = [c for c in cards if c["status"] == "live"]
    archive = [c for c in cards if c["status"] != "live"]
    hazards = sorted({h for c in live for h in c["hazards"]})
    countries = sorted({x for c in live for x in c["countries"]})
    hosts = sorted({c["host"] for c in live})
    by_group: dict[str, list[dict]] = defaultdict(list)
    for c in live:
        by_group[c["group"]].append(c)
    sections = "\n".join(section_html(g, by_group[g]) for g in GROUP_ORDER if by_group.get(g))
    toc = "".join(f'<a href="#{e(g)}">{e(GROUPS[g][0])} · {len(by_group[g])}</a>' for g in GROUP_ORDER if by_group.get(g))
    n_repos = len({c["repo"] for c in live if c["repo"]})
    n_shots = sum(1 for c in live if c["shot"])
    opt = lambda vals: "".join(f'<option value="{e(v)}">{e(v)}</option>' for v in vals)
    arch = ""
    if archive:
        arch = f"""<details class="arch"><summary>Archive — {len(archive)} stopped, unreachable or retired surfaces</summary>
  <div class="grid">{"".join(card_html(c, compact=True) for c in sorted(archive, key=lambda c: c["title"].lower()))}</div></details>"""
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>OCHA Centre for Humanitarian Data — Data Science: dashboards, apps & analyses</title>
<meta name="description" content="Every dashboard, monitoring page, app and published analysis from the OCHA Centre for Humanitarian Data's Data Science team, on one page. Generated daily from the team knowledge base.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Merriweather:wght@700&family=Roboto:wght@400;500;700&display=swap" rel="stylesheet">
<style>{CSS}</style>
</head>
<body>
<div class="wrap">
  <header class="hero">
    <canvas id="bg" aria-hidden="true"></canvas>
    <div class="inner">
      <div class="txt">
        <p class="eyebrow">OCHA Centre for Humanitarian Data · Data Science</p>
        <h1>Dashboards, apps &amp; analyses</h1>
        <p>Everything the team publishes — anticipatory-action trigger monitors, exposure dashboards,
           forecast explorers, data mirrors and rendered analyses — in one place. Generated from the
           <a href="{KB_URL}" style="color:#fff">team knowledge base</a>, so it tracks what is actually deployed.</p>
      </div>
      <div class="stats">
        <div><b>{len(live)}</b><span>live pages</span></div>
        <div><b>{n_repos}</b><span>repositories</span></div>
        <div><b>{len(countries)}</b><span>countries</span></div>
      </div>
    </div>
  </header>

  <div class="bar" role="search">
    <input id="q" type="search" placeholder="Search — e.g. Somalia, cyclone, exposure, SEAS5…" aria-label="Search pages">
    <select id="hz" aria-label="Hazard"><option value="">All hazards</option>{opt(hazards)}</select>
    <select id="co" aria-label="Country"><option value="">All countries</option>{opt(countries)}</select>
    <select id="ho" aria-label="Hosting"><option value="">All hosting</option>{"".join(f'<option value="{e(h)}">{e(HOST_LABEL.get(h, h))}</option>' for h in hosts)}</select>
    <button id="reset" type="button">Clear</button>
    <span class="cnt" id="cnt"></span>
  </div>
  <nav class="toc" aria-label="Sections">{toc}</nav>

  <main>
    {sections}
    <p class="empty">Nothing matches — clear the filters.</p>
  </main>

  {arch}

  <div class="note">
    <p><strong>How this page stays current.</strong> It is generated, not maintained. GitHub Pages sites are
       swept from the <code>ocha-dap</code> org and probed daily (<code>gen_pages_registry.py</code>);
       Azure web apps come from the daily infrastructure baseline; titles, blurbs, hazards and countries
       come from each surface's page in the knowledge base; thumbnails are captured weekly.
       Sources: registry {e(sources.get("registry", "?"))} · Azure estate {e(sources.get("infra", "?"))} ·
       {n_shots} of {len(live)} live pages have a thumbnail · page built {e(generated)}.</p>
    <p><strong>Something missing or mislabelled?</strong> Add or fix the <code>surfaces:</code> entry on the
       owning KB page (title, <code>kind</code>, <code>access</code>) — see
       <a href="{KB_URL}/blob/main/infrastructure/pages-registry.md">the published-sites registry</a> for what
       was found and where it landed. A new Pages site in a <code>ds-*</code> repo appears here by itself
       within a day.</p>
  </div>
</div>
<script>{JS}</script>
</body>
</html>
"""


# ── main ────────────────────────────────────────────────────────────────────────────────────

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="exit 2 if outputs on disk are stale")
    args = ap.parse_args()

    reg = load_json(REGISTRY, "surfaces")
    infra = load_json(INFRA, "azure")
    pages = load_pages()
    cards = build_cards(reg, infra, pages)
    if len(cards) < 10:
        die(f"only {len(cards)} cards derived — inputs look empty, refusing to write")

    generated = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    sources = {"registry": str(reg.get("generated", "?")), "infra": str(infra.get("generated", "?"))}
    out_json = json.dumps({"generated": generated, "sources": sources, "cards": cards}, indent=1, ensure_ascii=False) + "\n"
    out_html = render(cards, generated, sources)

    if args.check:
        stale = []
        strip = lambda s: re.sub(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2} UTC", "", s)
        if not OUT_JSON.exists() or strip(OUT_JSON.read_text()) != strip(out_json):
            stale.append(OUT_JSON.relative_to(ROOT).as_posix())
        if not OUT_HTML.exists() or strip(OUT_HTML.read_text()) != strip(out_html):
            stale.append(OUT_HTML.relative_to(ROOT).as_posix())
        if stale:
            print(f"STALE: {', '.join(stale)} — run scripts/gen_team_hub.py")
            return 2
        print("hub up to date")
        return 0

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(out_json)
    OUT_HTML.write_text(out_html)
    live = sum(1 for c in cards if c["status"] == "live")
    shots = sum(1 for c in cards if c["shot"])
    print(f"wrote {OUT_HTML.relative_to(ROOT)} + {OUT_JSON.relative_to(ROOT)}: {len(cards)} cards "
          f"({live} live, {len(cards) - live} archived), {shots} with thumbnails")
    return 0


if __name__ == "__main__":
    sys.exit(main())
