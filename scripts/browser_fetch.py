#!/usr/bin/env python3
"""Fetch a PDF that's behind a JS/WAF bot-challenge, using a real (headless) browser.

reliefweb.int / unocha.org intermittently return an HTTP-202 challenge to `curl`
(see gen_framework_captions.py / gen_framework_extracts.py) — a real browser runs the
challenge JS and gets through. This is the **robust fetcher** that makes automated
framework-PDF ingestion reliable: launch headless Chromium, clear the challenge on the
origin (sets the clearance cookie), then download the PDF via the same browser context.

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


def fetch(url: str, out: str, timeout_ms: int = 60000) -> bool:
    from playwright.sync_api import sync_playwright
    origin = f"{urlparse(url).scheme}://{urlparse(url).netloc}"
    data = b""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(user_agent=UA, accept_downloads=True,
                                  extra_http_headers={"Accept-Language": "en-US,en;q=0.9"})
        page = ctx.new_page()
        # 1) clear the challenge on the origin (HTML) — sets the clearance cookie on the context
        try:
            page.goto(origin, wait_until="domcontentloaded", timeout=timeout_ms)
            page.wait_for_timeout(5000)
        except Exception:
            pass
        # 2) fetch via the context's request API (reuses cookies); retry once. If the doc
        #    is a publication PAGE (HTML), follow its attachment `.pdf` link.
        for _ in range(2):
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
            page.wait_for_timeout(5000)
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
