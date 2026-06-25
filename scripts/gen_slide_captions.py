#!/usr/bin/env python3
"""Caption the VISUALS in slide decks (Phase 7c+): plots/charts/maps → searchable text.

Text extraction misses the information in slide *images* — and for many decks the key
info (trigger charts, return-period plots, maps, comparison tables) lives there, not in
text. This renders each slide to an image and asks **Claude Code headless** (`claude -p`)
to describe what it shows (variables, axes, thresholds, numbers, message), writing a
`*.captions.txt` sidecar next to the text extract so the plot content becomes greppable.

Uses headless Claude Code — bills to the user's **subscription/Max plan, NOT the
per-token API** (no ANTHROPIC_API_KEY). In CI, authenticate with a `CLAUDE_CODE_OAUTH_TOKEN`
(from `claude setup-token`). INTERNAL, like the extracts.

Cost-smart: by default only captions decks whose TEXT extract is *sparse* (`--sparse-below`
bytes) — the visual-heavy ones where we're actually losing info. Idempotent/resumable via
`drive/.caption-index.jsonl` (JSON-Lines + git-union, like the extract index), so a daily
run only captions newly-added/changed decks → near-zero steady-state cost; the big one-time
backfill is a deliberate, paced run.

Render: Google Slides → Drive export to PDF; PowerPoint → LibreOffice → PDF; then
`pdftoppm` → one PNG per slide. Needs: read-only Drive ADC, `pdftoppm` (poppler),
`libreoffice` (only for .pptx), and the `claude` CLI authenticated to a Max/Pro plan.

Usage:
  GOOGLE_APPLICATION_CREDENTIALS= ~/.config/ds-kb/venv/bin/python scripts/gen_slide_captions.py \
    --prefix "CERF Anticipatory Action/Nigeria" [--types slides,presentation] \
    [--sparse-below 800 | --all] [--limit N] [--model sonnet] [--workers 2]
"""
from __future__ import annotations
import json, os, re, subprocess, sys, tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INTERNAL = Path(os.environ.get("KB_INTERNAL_DIR", ROOT.parent / "ds-knowledge-base-internal"))
MANIFEST = INTERNAL / "drive" / "drive-index.json"
OUTDIR = INTERNAL / "drive" / "extracts"
EXTRACT_INDEX = INTERNAL / "drive" / ".extract-index.jsonl"
CAPTION_INDEX = INTERNAL / "drive" / ".caption-index.jsonl"

PROMPT_TMPL = (
    "You are building a searchable text archive of an internal humanitarian "
    "anticipatory-action slide deck. Read each slide image listed below and write its KEY "
    "INFORMATION to the file {capfile}, one section per slide headed exactly '--- slide N ---'. "
    "For any chart/plot/map/table: capture what it shows — variable, axes, units, key values, "
    "thresholds, trends, labels — and capture numbers/tables verbatim where you can. Give the "
    "slide's main point in one line. For a title/section/agenda slide with no data, write one "
    "short sentence. Be concise and factual; do NOT describe visual styling. Slides in order:\n{imgs}"
)


def arg(name, default=None):
    return sys.argv[sys.argv.index(name) + 1] if name in sys.argv else default


def load_jsonl(p):
    idx = {}
    if p.exists():
        for line in p.read_text().splitlines():
            line = line.strip()
            if line:
                try:
                    r = json.loads(line); idx[r["id"]] = {k: v for k, v in r.items() if k != "id"}
                except json.JSONDecodeError:
                    pass
    return idx


def write_jsonl(p, idx):
    p.write_text("\n".join(json.dumps({"id": i, **r}, ensure_ascii=False) for i, r in idx.items()) + "\n")


def drive():
    import google.auth
    from googleapiclient.discovery import build
    creds, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/drive.readonly"])
    return build("drive", "v3", credentials=creds, cache_discovery=False)


def deck_to_pngs(svc, node, workdir) -> list[Path]:
    t = node["type"]
    pdf = Path(workdir) / "deck.pdf"
    if t == "slides":
        pdf.write_bytes(svc.files().export_media(fileId=node["id"], mimeType="application/pdf").execute())
    elif t == "presentation":
        src = Path(workdir) / "deck.pptx"
        src.write_bytes(svc.files().get_media(fileId=node["id"]).execute())
        subprocess.run(["libreoffice", "--headless", "--convert-to", "pdf", "--outdir",
                        workdir, str(src)], capture_output=True, timeout=180, check=True)
    else:
        raise ValueError(f"not a deck type: {t}")
    subprocess.run(["pdftoppm", "-png", "-scale-to-x", "1100", "-scale-to-y", "-1",
                    str(pdf), str(Path(workdir) / "slide")], capture_output=True, timeout=120, check=True)
    return sorted(Path(workdir).glob("slide*.png"))


def caption_deck(pngs, capfile, model=None):
    """Headless Claude Code reads the slide PNGs and writes the caption body to capfile."""
    imgs = "\n".join(f"  slide {i}: {p}" for i, p in enumerate(pngs, 1))
    prompt = PROMPT_TMPL.format(capfile=capfile, imgs=imgs)
    cmd = ["claude", "-p", prompt, "--allowedTools", "Read Write", "--permission-mode", "acceptEdits"]
    if model:
        cmd += ["--model", model]
    subprocess.run(cmd, capture_output=True, text=True, timeout=900)
    return Path(capfile).exists()


def caption_one(node, out, model):
    fid, modn = node["id"], node.get("modified", "")
    sidecar = out.with_suffix(".captions.txt")
    try:
        svc = drive()
        with tempfile.TemporaryDirectory() as wd:
            pngs = deck_to_pngs(svc, node, wd)
            capbody = Path(wd) / "caps.txt"
            if not caption_deck(pngs, str(capbody), model) or not capbody.stat().st_size:
                return {"fid": fid, "status": "fail", "msg": f"{node.get('path','')}/{node['title']}: no caption written"}
            header = (f"# VISION CAPTIONS — {node['title']}\n# drive-path: {node.get('path','')}\n"
                      f"# id: {fid} · modified: {modn} · slides: {len(pngs)} · via: claude headless\n"
                      f"# Auto-generated descriptions of slide visuals (plots/maps/figures).\n{'-'*60}\n")
            sidecar.write_text(header + capbody.read_text())
        return {"fid": fid, "status": "done",
                "record": {"modified": modn, "captions": str(sidecar.relative_to(OUTDIR)), "slides": len(pngs)}}
    except Exception as e:                            # noqa: BLE001
        return {"fid": fid, "status": "fail", "msg": f"{node.get('path','')}/{node['title']}: {type(e).__name__}: {str(e)[:80]}"}


def main():
    if not MANIFEST.exists():
        sys.exit(f"Manifest not found at {MANIFEST} — run gen_drive_index.py first.")
    prefix = arg("--prefix", "")
    types = [x.strip() for x in arg("--types", "slides,presentation").split(",")]
    sparse_below = int(arg("--sparse-below", "800"))
    cap_all = "--all" in sys.argv
    limit = int(arg("--limit", "0"))
    model = arg("--model", None)
    workers = int(arg("--workers", "2"))
    ids_file = arg("--ids-file", None)   # restrict to these deck ids (daily = only changed decks)
    only = None
    if ids_file:
        only = {x.strip() for x in Path(ids_file).read_text().split() if x.strip()}

    nodes = json.loads(MANIFEST.read_text())["nodes"]
    extract_idx = load_jsonl(EXTRACT_INDEX)
    cap_idx = load_jsonl(CAPTION_INDEX)

    todo, skip = [], 0
    for n in nodes:
        if n["type"] not in types or n.get("excluded") or not (n.get("path", "") + "/").startswith(prefix):
            continue
        if only is not None and n["id"] not in only:
            continue
        rec = extract_idx.get(n["id"])
        if not rec or not rec.get("out"):
            continue                                  # only caption decks we have a text extract for
        out = OUTDIR / rec["out"]
        if not (cap_all or (out.exists() and out.stat().st_size < sparse_below)):
            continue
        c = cap_idx.get(n["id"])
        if c and c.get("modified") == n.get("modified", "") and (out.with_suffix(".captions.txt")).exists():
            skip += 1; continue
        todo.append((n, out))
    if limit:
        todo = todo[:limit]

    print(f"{len(todo)} decks to caption under '{prefix}' "
          f"({'all' if cap_all else f'sparse<{sparse_below}B'}); {skip} already done; "
          f"model={model or 'default'}; workers={workers}")
    done = fail = 0
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = [ex.submit(caption_one, n, out, model) for n, out in todo]
        for i, fut in enumerate(as_completed(futs), 1):
            r = fut.result()
            if r["status"] == "done":
                cap_idx[r["fid"]] = r["record"]; done += 1
                print(f"  [{i}/{len(todo)}] {r['record']['slides']} slides → {Path(r['record']['captions']).name}")
            else:
                fail += 1; print(f"  FAIL {r['msg']}")
            write_jsonl(CAPTION_INDEX, cap_idx)
    write_jsonl(CAPTION_INDEX, cap_idx)
    print(f"done: {done} decks captioned / {fail} failed → {OUTDIR} (*.captions.txt)")


if __name__ == "__main__":
    main()
