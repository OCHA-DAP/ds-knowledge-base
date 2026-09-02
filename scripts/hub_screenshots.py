#!/usr/bin/env python3
"""Capture a thumbnail of every publicly reachable card in the team hub (hub/hub.json).

A picture of the dashboard is the fastest way for someone who has used it to recognise the one
they want — the reason the spoke landing pages screenshot their app (ds-seas5-skill). This does
it for the whole team, weekly, so the hub stays visual without anyone taking screenshots.

  hub/hub.json           the inventory (gen_team_hub.py — run it FIRST, then this, then it again
                         so hub.html picks up the new thumbnails)
  hub/shots/<slug>.jpg   640×400 JPEG per card (1280×800 viewport at half scale — no image lib)
  hub/shots/manifest.json  when each shot was taken + what the page returned

Skips cards that are not public (internal Azure, password/private), not live, or whose shot is
younger than --max-age days (default 6, so a weekly run refreshes everything but a re-run the same
day is a no-op). Pages that hang or error keep their previous shot; a card that gets no usable
frame (blank / error page) gets none rather than a picture of an error.

Usage:  python scripts/hub_screenshots.py [--max-age DAYS] [--only SUBSTR] [--force] [--prune] [--parallel N]
        --prune   delete shots for URLs no longer in hub.json
Needs:  pip install playwright && playwright install --with-deps chromium
"""
from __future__ import annotations
import argparse
import datetime as dt
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HUB = ROOT / "hub" / "hub.json"
SHOTS = ROOT / "hub" / "shots"
MANIFEST = SHOTS / "manifest.json"
VIEWPORT = {"width": 1280, "height": 800}
SCALE = 0.5            # → 640×400 output
SETTLE_MS = 2500       # maps and charts draw after load; give them a moment
NAV_TIMEOUT_MS = 40000

# <title>s / body text that mean "this is not the product" — no thumbnail is better than one of these
BAD_TITLE = ("404", "not found", "azure app service", "application error", "sign in", "login", "unauthorized",
             "site not found", "there isn't a github pages site here")


def load_manifest() -> dict:
    if MANIFEST.exists():
        try:
            return json.loads(MANIFEST.read_text())
        except json.JSONDecodeError:
            pass
    return {}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--max-age", type=float, default=6, help="re-shoot only if the existing shot is older (days)")
    ap.add_argument("--only", default="", help="only URLs containing this substring")
    ap.add_argument("--force", action="store_true", help="ignore --max-age")
    ap.add_argument("--prune", action="store_true", help="remove shots whose URL left hub.json")
    ap.add_argument("--parallel", type=int, default=4, help="pages captured concurrently (one browser)")
    args = ap.parse_args()

    try:
        import playwright  # noqa: F401
    except ImportError:
        sys.exit("Needs playwright:  pip install playwright && playwright install --with-deps chromium")

    if not HUB.exists():
        sys.exit("hub/hub.json missing — run scripts/gen_team_hub.py first")
    cards = json.loads(HUB.read_text())["cards"]
    SHOTS.mkdir(parents=True, exist_ok=True)
    manifest = load_manifest()
    now = dt.datetime.now(dt.timezone.utc)

    todo = []
    for c in cards:
        if c["access"] != "public" or c["status"] != "live":
            continue
        if args.only and args.only not in c["url"]:
            continue
        out = SHOTS / f"{c['slug']}.jpg"
        prev = manifest.get(c["slug"], {})
        if out.exists() and not args.force and prev.get("taken"):
            age = now - dt.datetime.fromisoformat(prev["taken"])
            if age.total_seconds() < args.max_age * 86400:
                continue
        todo.append((c, out))
    print(f"{len(todo)} to capture (of {len(cards)} cards)")

    import asyncio
    from playwright.async_api import async_playwright, TimeoutError as PWTimeout

    async def capture(ctx, c, out, sem, results):
        async with sem:
            page = await ctx.new_page()
            t0 = time.time()
            entry = {"url": c["url"], "taken": now.isoformat(timespec="seconds")}
            try:
                resp = await page.goto(c["url"], wait_until="load", timeout=NAV_TIMEOUT_MS)
                status = resp.status if resp else None
                try:
                    await page.wait_for_load_state("networkidle", timeout=10000)
                except PWTimeout:
                    pass                       # live maps keep tiles streaming; the frame is fine
                await page.wait_for_timeout(SETTLE_MS)
                title = ((await page.title()) or "").strip()
                body = (await page.inner_text("body"))[:400].lower() if await page.locator("body").count() else ""
                bad = (status is not None and status >= 400) or any(b in title.lower() for b in BAD_TITLE) \
                    or (len(body.strip()) < 20 and not await page.locator("canvas, svg, img, iframe").count())
                if bad:
                    entry.update(status=status, title=title, result="skipped-not-a-product")
                    if out.exists():
                        out.unlink()
                    results["fail"] += 1
                    print(f"  ✗ {c['url']}  (HTTP {status}, title={title!r})", flush=True)
                else:
                    await page.screenshot(path=str(out), type="jpeg", quality=78, clip={"x": 0, "y": 0, **VIEWPORT})
                    entry.update(status=status, title=title, result="ok", bytes=out.stat().st_size)
                    results["ok"] += 1
                    print(f"  ✓ {c['url']}  {out.stat().st_size // 1024} KB  {time.time() - t0:.1f}s", flush=True)
            except Exception as ex:                      # noqa: BLE001 — one bad page must not stop the run
                entry.update(result=f"error: {type(ex).__name__}: {str(ex)[:120]}")
                results["fail"] += 1
                print(f"  ✗ {c['url']}  {type(ex).__name__}", flush=True)
            finally:
                await page.close()
            manifest[c["slug"]] = entry

    async def run_all():
        results = {"ok": 0, "fail": 0}
        sem = asyncio.Semaphore(args.parallel)
        async with async_playwright() as pw:
            browser = await pw.chromium.launch()
            ctx = await browser.new_context(viewport=VIEWPORT, device_scale_factor=SCALE, locale="en-GB",
                                            user_agent="Mozilla/5.0 (X11; Linux x86_64) ds-knowledge-base hub thumbnails")
            await asyncio.gather(*(capture(ctx, c, out, sem, results) for c, out in todo))
            await browser.close()
        return results

    res = asyncio.run(run_all())
    ok, fail = res["ok"], res["fail"]

    if args.prune:
        keep = {c["slug"] for c in cards}
        for f in SHOTS.glob("*.jpg"):
            if f.stem not in keep:
                f.unlink()
                manifest.pop(f.stem, None)
                print(f"  pruned {f.name}")
    MANIFEST.write_text(json.dumps(manifest, indent=1, sort_keys=True) + "\n")
    print(f"done: {ok} captured, {fail} skipped/failed, {sum(1 for _ in SHOTS.glob('*.jpg'))} shots on disk")
    return 0


if __name__ == "__main__":
    sys.exit(main())
