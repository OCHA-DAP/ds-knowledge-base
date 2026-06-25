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

Network: fetches each PDF with a browser UA (unocha 403s default fetchers); if the
`framework_doc` is a publication page, it scrapes the attachment `.pdf` link. Needs
`pdftotext` (poppler) + `curl`. Does NOT edit pages — it (re)writes the `.txt` cache
only; `raw_extract` pointers are stable once set.

Usage:  python3 scripts/gen_framework_extracts.py [--check]
        --check : report which extracts are missing/stale, write nothing.
"""
from __future__ import annotations
import glob, os, re, shutil, subprocess, sys
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("Needs pyyaml")

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "raw" / "frameworks"
PDF_CACHE = ROOT / "raw" / ".pdf-cache"          # gitignored; shared with gen_framework_captions.py
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")
CHECK = "--check" in sys.argv
FORCE = "--force" in sys.argv                     # re-extract versions whose .txt already exists


def sh(args):
    return subprocess.run(args, capture_output=True, text=True, timeout=90)


def curl(url, out):
    sh(["curl", "-sL", "--max-time", "80", "-A", UA, url, "-o", out])


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


def fetch_pdf(doc: str, pdf: str, html: str, fw=None, ver=None) -> bool:
    """Resolve the framework_doc PDF: shared cache → curl (follow publication-page
    attachment) → headless browser (WAF fallback). Caches a successful fetch."""
    cache = PDF_CACHE / fw / f"{ver}.pdf" if (fw and ver) else None
    if cache and cache.exists() and is_pdf(cache):
        shutil.copy(cache, pdf); return True
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
    if _browser_fetch(doc, pdf):                  # curl/WAF failed → real browser
        _cache(fw, ver, pdf); return True
    return False


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


if __name__ == "__main__":
    main()
