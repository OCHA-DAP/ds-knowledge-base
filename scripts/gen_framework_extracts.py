#!/usr/bin/env python3
"""Persist the full-text of each framework's PUBLIC PDF to a greppable in-repo cache.

Per docs/PRIVACY.md: framework PDFs are already published (ReliefWeb/unocha), so
their full-text extract is **public** and lives in-repo at
`raw/frameworks/<fw>/<version>.txt`. Each page's `raw_extract` points there. The
canonical source is still the `framework_doc` URL — this is a greppable cache
("raw is always reachable"), re-runnable to refresh.

Only PUBLIC-doc framework versions are extracted: a page with `framework_doc: null`
(repo-only/dev versions) or a non-public doc (mmr/vut/yem — `extra.doc_status`)
is skipped, and its extract — if any — belongs in the private store, not here.

Network: the fetch chain per version is committed cache (`raw/.pdf-cache/`) →
ReliefWeb API (no WAF; needs $RELIEFWEB_APPNAME) → curl with a browser UA (following
a publication page's attachment `.pdf` link) → headless Chromium (scripts/
browser_fetch.py, runs the WAF JS challenge). reliefweb/unocha's WAF 202-challenges
GH-runner IPs *intermittently*, so the whole chain retries with backoff; every
success is cached in `raw/.pdf-cache/` (COMMITTED — a PDF only ever has to be
fetched once, anywhere). A `framework_doc` that is an HTML page with no PDF at all
(e.g. som-drought) falls back to extracting the page text itself. Needs `pdftotext`
(poppler) + `curl`. Does NOT edit pages — it (re)writes the `.txt` cache only;
`raw_extract` pointers are stable once set.

Usage:  python3 scripts/gen_framework_extracts.py [--check] [--wire]
        --check : report which extracts are missing/stale, write nothing.
        --wire  : after extracting, point each page's empty `raw_extract` at its
                  existing .txt (targeted line edit; set pointers are never touched).
"""
from __future__ import annotations
import glob, json, os, re, shutil, subprocess, sys, time, urllib.parse, urllib.request
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("Needs pyyaml")

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "raw" / "frameworks"
PDF_CACHE = ROOT / "raw" / ".pdf-cache"          # COMMITTED; shared with gen_framework_captions.py
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")
RW_APPNAME = os.environ.get("RELIEFWEB_APPNAME", "")   # pre-approved API appname; rung skipped if unset
FETCH_ATTEMPTS = int(os.environ.get("PDF_FETCH_ATTEMPTS", "3"))
# first line of an extract built from an HTML framework_doc (no published PDF) —
# gen_framework_captions.py keys off this to skip captioning (nothing to render)
HTML_DOC_MARKER = "# extracted from HTML framework_doc (no published PDF)"
CHECK = "--check" in sys.argv
FORCE = "--force" in sys.argv                     # re-extract versions whose .txt already exists
WIRE = "--wire" in sys.argv                       # fill empty raw_extract pointers to existing .txt


def sh(args):
    return subprocess.run(args, capture_output=True, text=True, timeout=90)


def curl(url, out):
    sh(["curl", "-sL", "--max-time", "80", "--retry", "2", "--retry-delay", "5", "-A", UA,
        "-H", "Accept: text/html,application/xhtml+xml,application/pdf;q=0.9,*/*;q=0.8",
        "-H", "Accept-Language: en-US,en;q=0.9", url, "-o", out])


def is_pdf(p):
    try:
        return open(p, "rb").read(5).startswith(b"%PDF")
    except OSError:
        return False


def frontmatter(p: Path) -> dict:
    t = p.read_text(encoding="utf-8")
    e = t.find("\n---", 3)
    try:
        return yaml.safe_load(t[3:e]) or {}
    except yaml.YAMLError:
        return {}


def _cache(fw, ver, pdf):
    if fw and ver and is_pdf(pdf):
        dst = PDF_CACHE / fw / f"{ver}.pdf"
        dst.parent.mkdir(parents=True, exist_ok=True); shutil.copy(pdf, dst)


def _browser_fetch(doc, pdf) -> bool:
    """WAF 202? → headless Chromium (scripts/browser_fetch.py) runs the JS challenge."""
    venv_py = os.environ.get("DS_KB_VENV_PY", str(Path.home() / ".config/ds-kb/venv/bin/python"))
    bf = ROOT / "scripts" / "browser_fetch.py"
    if Path(venv_py).exists() and bf.exists():
        subprocess.run([venv_py, str(bf), doc, pdf], capture_output=True, text=True, timeout=240)
    return is_pdf(pdf)


def _rw_api(params: list[tuple[str, str]]) -> list[dict]:
    q = urllib.parse.urlencode([("appname", RW_APPNAME), ("fields[include][]", "file"),
                                ("fields[include][]", "url_alias")] + params)
    try:
        with urllib.request.urlopen(f"https://api.reliefweb.int/v2/reports?{q}", timeout=30) as r:
            return json.load(r).get("data", [])
    except Exception:
        return []


def _reliefweb_api_pdf_urls(doc: str) -> list[str]:
    """Resolve a reliefweb.int report URL to its attachment .pdf URLs via the official
    API (api.reliefweb.int v2) — built for programmatic access, so runner IPs are not
    WAF-challenged. Needs a pre-approved appname (free form:
    apidoc.reliefweb.int/parameters#appname) in $RELIEFWEB_APPNAME; skipped if unset.

    Two lookups: exact url_alias filter first; if the report was renamed since the KB
    stored the URL (aliases drift with title edits — afg-drought's '…-drought-2026'
    became '…-drought-march-2026'), fall back to an AND full-text query on the slug
    tokens, accepting only a candidate whose current alias still contains EVERY
    requested token (never returns a merely-similar document)."""
    if not RW_APPNAME or "reliefweb.int/report/" not in doc:
        return []
    url = doc.split("?")[0].rstrip("/")
    files = [f["url"] for item in _rw_api([("filter[field]", "url_alias"), ("filter[value]", url)])
             for f in item.get("fields", {}).get("file", []) if f.get("url")]
    if files:
        return files
    tokens = [t for t in re.split(r"[-_]", url.rsplit("/", 1)[-1]) if t]
    for item in _rw_api([("query[value]", " ".join(tokens)), ("query[operator]", "AND"),
                         ("limit", "5")]):
        alias = str(item.get("fields", {}).get("url_alias", ""))
        if all(t in re.split(r"[-_/.]", alias) for t in tokens):
            return [f["url"] for f in item.get("fields", {}).get("file", []) if f.get("url")]
    return []


def fetch_pdf(doc: str, pdf: str, html: str, fw=None, ver=None) -> bool:
    """Resolve the framework_doc PDF: committed cache → ReliefWeb API → curl (follow
    publication-page attachment) → headless browser (WAF fallback). The WAF challenge
    is intermittent on datacenter IPs, so the whole chain retries with backoff; a
    success is cached in the committed raw/.pdf-cache (fetched once, kept forever)."""
    cache = PDF_CACHE / fw / f"{ver}.pdf" if (fw and ver) else None
    if cache and cache.exists() and is_pdf(cache):
        shutil.copy(cache, pdf); return True
    api_urls = _reliefweb_api_pdf_urls(doc)
    for attempt in range(FETCH_ATTEMPTS):
        if attempt:
            time.sleep(15 * attempt)
        for u in api_urls:
            curl(u, pdf)
            if is_pdf(pdf):
                _cache(fw, ver, pdf); return True
        curl(doc, pdf)
        if is_pdf(pdf):
            _cache(fw, ver, pdf); return True
        os.replace(pdf, html) if os.path.exists(pdf) else None
        h = open(html, encoding="utf-8", errors="ignore").read() if os.path.exists(html) else ""
        links = re.findall(r'href="([^"]*\.pdf[^"]*)"', h, re.I)
        cand = [u for u in links if "attachment" in u.lower()] or links
        if cand:
            u = cand[0]
            if u.startswith("/"):
                base = "https://www.unocha.org" if "unocha" in doc else "https://reliefweb.int"
                u = base + u
            curl(u, pdf)
            if is_pdf(pdf):
                _cache(fw, ver, pdf); return True
        if _browser_fetch(doc, pdf):              # curl/WAF failed → real browser
            _cache(fw, ver, pdf); return True
    return False


def _html_to_text(h: str) -> str:
    from html.parser import HTMLParser

    class P(HTMLParser):
        def __init__(self):
            super().__init__(); self.skip = 0; self.out = []

        def handle_starttag(self, tag, attrs):
            if tag in ("script", "style", "noscript", "svg"):
                self.skip += 1

        def handle_endtag(self, tag):
            if tag in ("script", "style", "noscript", "svg"):
                self.skip = max(0, self.skip - 1)

        def handle_data(self, d):
            if not self.skip and d.strip():
                self.out.append(d.strip())

    p = P(); p.feed(h)
    return "\n".join(p.out)


def html_doc_extract(doc: str, html: str, txt: Path) -> bool:
    """Fallback for a framework_doc that is an HTML page with no published PDF at all
    (e.g. som-drought/2019): extract the page's own text. Guards against writing a WAF
    challenge or a 404 page (short, or telltale titles) so a transient failure can't
    poison the extract."""
    h = open(html, encoding="utf-8", errors="ignore").read() if os.path.exists(html) else ""
    if not h or "<" not in h[:500]:
        return False
    low = h.lower()
    if "just a moment" in low or "page not found" in low[:5000] or "attention required" in low:
        return False
    text = _html_to_text(h)
    if len(text) < 2000:
        return False
    txt.write_text(f"{HTML_DOC_MARKER}\n# framework_doc: {doc}\n{'-' * 60}\n{text}\n",
                   encoding="utf-8")
    return True


def main():
    ok, skip, fail = [], [], []
    for f in sorted(glob.glob(str(ROOT / "frameworks/*/*.md"))):
        if f.endswith(("README.md", "_TEMPLATE.md")):
            continue
        fm = frontmatter(Path(f))
        if not isinstance(fm, dict):
            continue
        fw = fm.get("framework") or Path(f).parent.name
        ver = str(fm.get("version"))
        doc = fm.get("framework_doc")
        if not (doc and str(doc).startswith("http")):       # null doc → repo-only/dev or non-public
            skip.append((fw, ver))
            continue
        txt = RAW / fw / f"{ver}.txt"
        if CHECK:
            (ok if txt.exists() else fail).append((fw, ver, "present" if txt.exists() else "MISSING"))
            continue
        if txt.exists() and not FORCE:                # immutable per dated version → skip (–-force to redo)
            skip.append((fw, ver))
            continue
        txt.parent.mkdir(parents=True, exist_ok=True)
        pdf, html = f"/tmp/fwx_{fw}_{ver}.pdf", f"/tmp/fwx_{fw}_{ver}.html"
        if not fetch_pdf(str(doc), pdf, html, fw, ver):
            if html_doc_extract(str(doc), html, txt):     # doc is an HTML page, no PDF
                ok.append((fw, ver, f"{txt.stat().st_size // 1024}KB (html doc)"))
            else:
                fail.append((fw, ver, "could not resolve a PDF (WAF? browser fetch also failed)"))
            continue
        sh(["pdftotext", "-enc", "UTF-8", pdf, str(txt)])
        sz = txt.stat().st_size if txt.exists() else 0
        if sz < 500:
            fail.append((fw, ver, f"extract too small ({sz}b)"))
            continue
        ok.append((fw, ver, f"{sz // 1024}KB"))

    verb = "present" if CHECK else "extracted"
    print(f"{len(ok)} {verb} / {len(fail)} failed / {len(skip)} skipped (existing or no public doc)")
    for fw, ver, why in fail:
        print(f"  FAIL {fw}/{ver}: {why}")
        # surface fetch failures in the Actions UI — the job itself succeeds (partial
        # results still get committed), so without this a broken fetch looks green
        if os.environ.get("GITHUB_ACTIONS"):
            print(f"::warning title=framework extract failed::{fw}/{ver}: {why}")
    if WIRE and not CHECK:
        print(f"{wire_pointers()} raw_extract pointer(s) wired")


_EMPTY_RE = re.compile(r"^raw_extract:\s*(\[\s*\]|null|~|)\s*(#.*)?$")


def wire_pointers() -> int:
    """Point each version page's EMPTY raw_extract at its on-disk .txt (targeted line
    edit so the rest of the frontmatter is untouched); pages with a pointer set, or
    with no extract on disk, are left alone."""
    wired = 0
    for f in sorted(glob.glob(str(ROOT / "frameworks/*/*.md"))):
        if f.endswith(("README.md", "_TEMPLATE.md")):
            continue
        p = Path(f)
        fm = frontmatter(p)
        if not isinstance(fm, dict) or fm.get("raw_extract"):
            continue
        fw = fm.get("framework") or p.parent.name
        ver = str(fm.get("version"))
        rel = f"raw/frameworks/{fw}/{ver}.txt"
        if not (ROOT / rel).exists():
            continue
        lines = p.read_text(encoding="utf-8").splitlines(keepends=True)
        for i, line in enumerate(lines):
            if _EMPTY_RE.match(line.rstrip("\n")):
                lines[i] = f'raw_extract: ["{rel}"]\n'
                p.write_text("".join(lines), encoding="utf-8")
                print(f"  WIRED {fw}/{ver} -> {rel}")
                wired += 1
                break
        else:
            print(f"  WARN {fw}/{ver}: extract exists but no raw_extract line to wire")
    return wired


if __name__ == "__main__":
    main()
