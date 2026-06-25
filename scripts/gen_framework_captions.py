#!/usr/bin/env python3
"""Caption the VISUALS in framework PDFs (maps/charts/return-period plots/tables) → text.

The published framework PDFs (ReliefWeb/unocha) are dense with AOI maps, trigger and
return-period charts, and indicator tables — exactly the visual content the text extract
(`raw/frameworks/<fw>/<ver>.txt`) misses. This renders each PDF page and captions it via
**headless Claude Code** (`claude -p`, billed to the subscription/**Max plan, not the API**)
→ a sidecar `raw/frameworks/<fw>/<ver>.captions.txt`.

PUBLIC by construction: the source PDFs are already published, so per docs/PRIVACY.md the
captions are **public and belong in-repo** (unlike the internal Drive captions). Only
PUBLIC-doc framework versions are done — a page with `framework_doc: null` (repo-only/dev)
or a non-public doc (mmr/vut/yem, `extra.doc_status`) is skipped; its captions would be
internal, not here.

Reuses `gen_framework_extracts.py`'s PDF fetch (browser UA; follows publication-page
attachment `.pdf` links). Needs: `curl`, `pdftoppm` (poppler), the `claude` CLI
authenticated to a Max/Pro plan (CI: `CLAUDE_CODE_OAUTH_TOKEN`), and `pyyaml`.

Idempotent: skips a version whose `.captions.txt` already exists (framework PDFs are
immutable per version) unless `--force`. Usage logged to `raw/.caption-usage.jsonl`.

Usage:
  python3 scripts/gen_framework_captions.py [--framework tcd-drought] [--version 2024]
      [--limit N] [--model sonnet] [--workers 2] [--force] [--render-only]
"""
from __future__ import annotations
import glob, json, os, re, shutil, subprocess, sys, tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("Needs pyyaml")

ROOT = Path(__file__).resolve().parent.parent
PAGES = ROOT / "frameworks"
RAW = ROOT / "raw" / "frameworks"
USAGE = ROOT / "raw" / ".caption-usage.jsonl"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")
MODEL_DEFAULT = None

PROMPT_TMPL = (
    "These are pages from a published humanitarian **Anticipatory Action framework** PDF. "
    "Read each page image and write its KEY INFORMATION to the file {capfile}, one section per "
    "page headed exactly '--- page N ---'. Focus on the VISUALS that plain text misses: for a "
    "**map**, the area/admin units shown and what's highlighted (AOI, trigger zones, exposure); "
    "for a **chart/plot**, the variable, axes, units, thresholds, return periods, and key values; "
    "for a **table/figure**, the data. Capture numbers verbatim where you can and give each page's "
    "main point in one line. For a pure body-text page with no distinct figure, write one short "
    "line ('narrative text, no figure'). Be concise and factual; do NOT describe visual styling. "
    "Pages in order:\n{imgs}"
)


def arg(name, default=None):
    return sys.argv[sys.argv.index(name) + 1] if name in sys.argv else default


def sh(args):
    return subprocess.run(args, capture_output=True, text=True, timeout=120)


def curl(url, out):
    sh(["curl", "-sL", "--max-time", "90", "-A", UA, url, "-o", out])


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


def fetch_pdf(doc: str, pdf: str, html: str) -> bool:
    """Fetch framework_doc; if it's a publication page, follow the attachment .pdf."""
    curl(doc, pdf)
    if is_pdf(pdf):
        return True
    if os.path.exists(pdf):
        os.replace(pdf, html)
    h = open(html, encoding="utf-8", errors="ignore").read() if os.path.exists(html) else ""
    links = re.findall(r'href="([^"]*\.pdf[^"]*)"', h, re.I)
    cand = [u for u in links if "attachment" in u.lower()] or links
    if not cand:
        return False
    u = cand[0]
    if u.startswith("/"):
        base = "https://www.unocha.org" if "unocha" in doc else "https://reliefweb.int"
        u = base + u
    curl(u, pdf)
    return is_pdf(pdf)


def pdf_to_pngs(pdf: str, workdir: str) -> list[Path]:
    subprocess.run(["pdftoppm", "-png", "-scale-to-x", "1240", "-scale-to-y", "-1",
                    pdf, str(Path(workdir) / "page")], capture_output=True, timeout=240, check=True)
    return sorted(Path(workdir).glob("page*.png"))


def caption_pages(pngs, capfile, model):
    imgs = "\n".join(f"  page {i}: {p}" for i, p in enumerate(pngs, 1))
    prompt = PROMPT_TMPL.format(capfile=capfile, imgs=imgs)
    cmd = ["claude", "-p", prompt, "--allowedTools", "Read Write",
           "--permission-mode", "acceptEdits", "--output-format", "json"]
    if model:
        cmd += ["--model", model]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)
    usage = {"cost_usd": 0.0, "in_tok": 0, "out_tok": 0}
    try:
        j = json.loads(r.stdout); u = j.get("usage", {})
        usage = {"cost_usd": j.get("total_cost_usd", 0.0) or 0.0,
                 "in_tok": (u.get("input_tokens", 0) + u.get("cache_read_input_tokens", 0)
                            + u.get("cache_creation_input_tokens", 0)),
                 "out_tok": u.get("output_tokens", 0)}
    except (json.JSONDecodeError, AttributeError):
        pass
    return Path(capfile).exists(), usage


PDF_CACHE = ROOT / "raw" / ".pdf-cache"        # gitignored; first successful fetch is cached here


def resolve_pdf(fw, ver, doc, wd, pdf_dir) -> str | None:
    """Prefer a local PDF (cache or --pdf-dir) — no WAF can block a file. Else fetch + cache."""
    for cand in ([Path(pdf_dir) / fw / f"{ver}.pdf", Path(pdf_dir) / f"{fw}__{ver}.pdf"] if pdf_dir else []) \
            + [PDF_CACHE / fw / f"{ver}.pdf"]:
        if cand.exists() and is_pdf(cand):
            return str(cand)
    pdf = f"{wd}/doc.pdf"
    if fetch_pdf(doc, pdf, f"{wd}/doc.html"):
        cache = PDF_CACHE / fw / f"{ver}.pdf"
        cache.parent.mkdir(parents=True, exist_ok=True); shutil.copy(pdf, cache)
        return pdf
    return None


def caption_one(fw, ver, doc, model, render_only, pdf_dir):
    out = RAW / fw / f"{ver}.captions.txt"
    try:
        with tempfile.TemporaryDirectory() as wd:
            pdf = resolve_pdf(fw, ver, doc, wd, pdf_dir)
            if not pdf:
                return {"key": f"{fw}/{ver}", "status": "fail",
                        "msg": "no PDF (host WAF 202?) — drop a copy in raw/.pdf-cache/<fw>/<ver>.pdf or use --pdf-dir"}
            pngs = pdf_to_pngs(pdf, wd)
            if not pngs:
                return {"key": f"{fw}/{ver}", "status": "fail", "msg": "no pages rendered"}
            if render_only:
                return {"key": f"{fw}/{ver}", "status": "render", "pages": len(pngs)}
            capbody = Path(wd) / "caps.txt"
            wrote, usage = caption_pages(pngs, str(capbody), model)
            if not wrote or not capbody.stat().st_size:
                return {"key": f"{fw}/{ver}", "status": "fail", "msg": "no caption written"}
            header = (f"# FRAMEWORK PDF CAPTIONS — {fw} {ver}\n# framework_doc: {doc}\n"
                      f"# pages: {len(pngs)} · model: {model or 'default'} · via: claude headless\n"
                      f"# Auto-generated descriptions of the PDF's visuals (maps/charts/tables). PUBLIC.\n"
                      f"{'-'*60}\n")
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(header + capbody.read_text())
        return {"key": f"{fw}/{ver}", "status": "done", "pages": len(pngs), "usage": usage}
    except Exception as e:                            # noqa: BLE001
        return {"key": f"{fw}/{ver}", "status": "fail", "msg": f"{type(e).__name__}: {str(e)[:80]}"}


def main():
    only_fw = arg("--framework")
    only_ver = arg("--version")
    model = arg("--model", MODEL_DEFAULT)
    workers = int(arg("--workers", "2"))
    limit = int(arg("--limit", "0"))
    force = "--force" in sys.argv
    render_only = "--render-only" in sys.argv
    pdf_dir = arg("--pdf-dir")            # dir of pre-downloaded PDFs (<fw>/<ver>.pdf or <fw>__<ver>.pdf)

    todo, skip = [], 0
    for f in sorted(glob.glob(str(PAGES / "*/*.md"))):
        if f.endswith(("README.md", "_TEMPLATE.md")):
            continue
        fm = frontmatter(Path(f))
        if not isinstance(fm, dict):
            continue
        fw = fm.get("framework") or Path(f).parent.name
        ver = str(fm.get("version"))
        doc = fm.get("framework_doc")
        if only_fw and fw != only_fw:
            continue
        if only_ver and ver != only_ver:
            continue
        if not (doc and str(doc).startswith("http")):       # repo-only/dev → skip
            continue
        if "non-public" in str(fm.get("extra", {}).get("doc_status", "")).lower():
            continue                                          # non-public doc → captions internal, not here
        if not force and (RAW / fw / f"{ver}.captions.txt").exists():
            skip += 1; continue
        todo.append((fw, ver, doc))
    if limit:
        todo = todo[:limit]

    print(f"{len(todo)} framework versions to caption; {skip} already done; "
          f"model={model or 'default'}; workers={workers}{' · RENDER-ONLY' if render_only else ''}")
    done = fail = pages = 0
    cost = in_tok = out_tok = 0
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = [ex.submit(caption_one, fw, ver, doc, model, render_only, pdf_dir) for fw, ver, doc in todo]
        for i, fut in enumerate(as_completed(futs), 1):
            r = fut.result()
            if r["status"] in ("done", "render"):
                done += 1; pages += r.get("pages", 0)
                u = r.get("usage", {})
                cost += u.get("cost_usd", 0); in_tok += u.get("in_tok", 0); out_tok += u.get("out_tok", 0)
                print(f"  [{i}/{len(todo)}] {r['key']}: {r.get('pages',0)} pages"
                      f"{' (render-only)' if r['status']=='render' else ''}")
            else:
                fail += 1; print(f"  FAIL {r['key']}: {r['msg']}")
    if done and not render_only:
        import datetime
        with open(USAGE, "a") as fh:
            fh.write(json.dumps({"date": datetime.date.today().isoformat(), "model": model or "default",
                                 "source": "framework-pdf", "versions": done, "pages": pages,
                                 "in_tok": in_tok, "out_tok": out_tok, "cost_usd": round(cost, 4)},
                                ensure_ascii=False) + "\n")
    verb = "rendered" if render_only else "captioned"
    print(f"done: {done} versions {verb} / {pages} pages / {fail} failed → raw/frameworks/<fw>/<ver>.captions.txt")
    if not render_only and done:
        print(f"usage this run: ~${cost:.2f} equiv · {in_tok:,} in / {out_tok:,} out tokens "
              f"(model {model or 'default'}) — logged to raw/.caption-usage.jsonl")


if __name__ == "__main__":
    main()
