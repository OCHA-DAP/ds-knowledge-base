#!/usr/bin/env python3
"""Fetch a PDF that's behind a JS/WAF bot-challenge, using a real (headless) browser.

reliefweb.int / unocha.org intermittently return an HTTP-202 challenge to `curl`
(see gen_framework_captions.py / gen_framework_extracts.py) — a real browser runs the
challenge JS and gets through. This is the **robust fetcher** that makes automated
framework-PDF ingestion reliable: launch headless Chrome/Chromium, clear the challenge
on the document page (sets the clearance cookie), then download the PDF via the same
browser context. Cloudflare challenges datacenter IPs (GH runners) harder than
residential ones, so the challenge wait is generous and the request step retries.

Run with the venv that has playwright (`~/.config/ds-kb/venv`):
  python scripts/browser_fetch.py <url> <out.pdf>
Exit 0 + writes the file on a real PDF; non-zero otherwise.
"""
from __future__ import annotations
import re, sys
from pathlib import Path
from urllib.parse import urlparse

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")
CHALLENGE_TITLES = ("just a moment", "attention required", "checking your browser")


def _launch(p):
    # system Chrome passes the WAF more often than bundled Chromium (and GH runners
    # ship it); fall back to whatever playwright has installed
    for kw in ({"channel": "chrome"}, {}):
        try:
            return p.chromium.launch(headless=True,
                                     args=["--disable-blink-features=AutomationControlled"], **kw)
        except Exception:
            continue
    return None


def _challenged(page) -> bool:
    try:
        return any(t in (page.title() or "").lower() for t in CHALLENGE_TITLES)
    except Exception:
        return False


def fetch(url: str, out: str, timeout_ms: int = 60000) -> bool:
    from playwright.sync_api import sync_playwright
    origin = f"{urlparse(url).scheme}://{urlparse(url).netloc}"
    data = b""
    with sync_playwright() as p:
        browser = _launch(p)
        if browser is None:
            return False
        ctx = browser.new_context(user_agent=UA, accept_downloads=True,
                                  extra_http_headers={"Accept-Language": "en-US,en;q=0.9"})
        page = ctx.new_page()
        # 1) load the document page itself and let the challenge run to clearance
        #    (the cookie lands on the context); challenges can take 10-20s on
        #    datacenter IPs, so poll the title rather than one fixed short sleep
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=timeout_ms)
            for _ in range(12):
                if not _challenged(page):
                    break
                page.wait_for_timeout(2500)
        except Exception:
            pass
        # 2) fetch via the context's request API (reuses cookies); retry with waits.
        #    If the doc is a publication PAGE (HTML), follow its attachment `.pdf` link.
        for _ in range(3):
            try:
                resp = ctx.request.get(url, timeout=timeout_ms)
                body = resp.body()
                if resp.ok and body[:4] == b"%PDF":
                    data = body; break
                if resp.ok and b"<" in body[:200]:                 # an HTML page → find the PDF
                    links = re.findall(r'href="([^"]*\.pdf[^"]*)"', body.decode("utf-8", "ignore"), re.I)
                    cand = [u for u in links if "attachment" in u.lower()] or links
                    if cand:
                        purl = cand[0] if cand[0].startswith("http") else origin + cand[0]
                        r2 = ctx.request.get(purl, timeout=timeout_ms); b2 = r2.body()
                        if r2.ok and b2[:4] == b"%PDF":
                            data = b2; break
            except Exception:
                pass
            page.wait_for_timeout(7000)
        # 3) last resort: navigate to the URL and capture a triggered download
        if data[:4] != b"%PDF":
            try:
                with page.expect_download(timeout=timeout_ms) as dl:
                    page.goto(url, timeout=timeout_ms)
                tmp = Path(out).with_suffix(".dl.tmp")
                dl.value.save_as(str(tmp))
                if tmp.read_bytes()[:4] == b"%PDF":
                    data = tmp.read_bytes()
                tmp.unlink(missing_ok=True)
            except Exception:
                pass
        browser.close()
    if data[:4] == b"%PDF":
        Path(out).parent.mkdir(parents=True, exist_ok=True)
        Path(out).write_bytes(data)
        return True
    return False


def main():
    if len(sys.argv) != 3:
        sys.exit("usage: browser_fetch.py <url> <out.pdf>")
    ok = fetch(sys.argv[1], sys.argv[2])
    print(f"{'OK' if ok else 'FAIL'}: {sys.argv[2]}")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
