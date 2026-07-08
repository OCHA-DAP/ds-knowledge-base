#!/usr/bin/env python3
"""Mirror the HDX v2 design system (style reference) into the PRIVATE companion repo.

The team's style reference for "pretty much everything" we build lives on an HDX staging
site behind basic auth — NOT public — so, per docs/PRIVACY.md (classification follows the
source), the greppable mirror goes to `ds-knowledge-base-internal/style-reference/`, and
the public KB carries only a pointer page (`methods/style-guide.md`). This script (the
machinery) is public; the credentials and the mirrored content are not.

Extracts, from /components + the two v2 CSS bundles:
  tokens.md       every CSS custom property (--hdx-*), grouped by family — colors, type,
                  spacing, elevation, radius. THE thing agents grep when styling anything.
  components.md   the component inventory: every section/subsection + the demo markup's
                  class names per component (the public contract of the design system).
  raw/*.css       the two CSS bundles verbatim (implementation reference).
  README.md       provenance + access (URL + where the credentials live) + refresh how-to.

Usage:  STYLE_REF_USER=… STYLE_REF_PASS=… python scripts/gen_style_reference.py
        [--base https://feature.data-humdata-org.ahconu.org] [--internal-dir PATH]
Needs:  curl; KB_INTERNAL_DIR or ~/OCHA/repos/ds-knowledge-base-internal checked out.
"""
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from collections import defaultdict
from datetime import date
from html import unescape
from pathlib import Path

DEFAULT_BASE = "https://feature.data-humdata-org.ahconu.org"
CSS_HREF_RE = re.compile(r'href="(/webassets/ckanext-hdx_theme/[^"]+\.css)"')
TOKEN_RE = re.compile(r"(--[a-z][a-z0-9-]*)\s*:\s*([^;}]+)[;}]")


def fetch(url: str, user: str, pw: str, out: Path) -> None:
    r = subprocess.run(["curl", "-sf", "-u", f"{user}:{pw}", "-m", "60", url, "-o", str(out)])
    if r.returncode != 0 or not out.exists() or out.stat().st_size < 500:
        sys.exit(f"::error::fetch failed: {url}")


def token_family(name: str) -> str:
    m = re.match(r"--hdx-([a-z]+)", name)
    return m.group(1) if m else name.split("-")[2] if name.count("-") > 2 else "other"


def extract_tokens(css_texts: list[str]) -> str:
    fams: dict[str, dict[str, str]] = defaultdict(dict)
    for css in css_texts:
        for name, val in TOKEN_RE.findall(css):
            fams[token_family(name)].setdefault(name, val.strip())
    lines = ["# HDX v2 design tokens", "",
             "_Every CSS custom property in the v2 bundles, by family. Use these names/values",
             "when styling team outputs — see the public pointer `methods/style-guide.md`._", ""]
    for fam in sorted(fams):
        lines += [f"## {fam}", "", "| token | value |", "|---|---|"]
        lines += [f"| `{n}` | `{v}` |" for n, v in sorted(fams[fam].items())]
        lines.append("")
    total = sum(len(v) for v in fams.values())
    lines.insert(5, f"_{total} tokens across {len(fams)} families._")
    lines.insert(6, "")
    return "\n".join(lines)


def extract_components(html: str) -> str:
    # sections: <h1 class="demo-section__title">Name … subsections + demo markup class names
    lines = ["# HDX v2 component inventory", "",
             "_Sections/subsections of the /components demo page + each section's CSS class",
             "vocabulary (from the demo markup). For full markup, fetch the page (see README)._", ""]
    # split on h1 sections
    parts = re.split(r'<h1 class="demo-section__title">', html)
    for part in parts[1:]:
        title = unescape(re.match(r"([^<]{1,60})", part).group(1)).strip()
        lines += [f"## {title}", ""]
        subs = [unescape(s).strip() for s in
                re.findall(r'<h2 class="demo-subsection__heading">([^<]{1,80})', part)]
        if subs:
            lines += ["**Variants:** " + " · ".join(subs), ""]
        classes = sorted({c for chunk in re.findall(r'class="([^"]+)"', part)
                          for c in chunk.split()
                          if not c.startswith("demo-") and c not in ("", "container")})
        if classes:
            lines += ["**Classes:** " + " ".join(f"`{c}`" for c in classes[:60])
                      + (f" … +{len(classes) - 60} more" if len(classes) > 60 else ""), ""]
    return "\n".join(lines)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default=os.environ.get("STYLE_REF_BASE", DEFAULT_BASE))
    ap.add_argument("--internal-dir", default=os.environ.get(
        "KB_INTERNAL_DIR", str(Path.home() / "OCHA/repos/ds-knowledge-base-internal")))
    args = ap.parse_args()

    user, pw = os.environ.get("STYLE_REF_USER"), os.environ.get("STYLE_REF_PASS")
    if not (user and pw):
        sys.exit("::error::set STYLE_REF_USER / STYLE_REF_PASS (see the mirror README in the internal repo)")
    dest = Path(args.internal_dir) / "style-reference"
    (dest / "raw").mkdir(parents=True, exist_ok=True)

    page = dest / "raw" / "components.html"
    fetch(f"{args.base}/components", user, pw, page)
    html = page.read_text(encoding="utf-8", errors="ignore")

    css_texts = []
    for href in sorted(set(CSS_HREF_RE.findall(html))):
        out = dest / "raw" / Path(href).name
        fetch(f"{args.base}{href}", user, pw, out)
        css_texts.append(out.read_text(encoding="utf-8", errors="ignore"))

    (dest / "tokens.md").write_text(extract_tokens(css_texts), encoding="utf-8")
    (dest / "components.md").write_text(extract_components(html), encoding="utf-8")
    (dest / "README.md").write_text(f"""# Style reference mirror — HDX v2 design system

Greppable mirror of the team's style reference (INTERNAL — the source is a gated staging
site). Public pointer + usage guidance: `ds-knowledge-base/methods/style-guide.md`.

- **Source:** {args.base}/components  (HTTP basic auth — credentials: user `{user}` /
  pass `{pw}`; staging-grade shared creds, fine to hold here, never in the public repo)
- **Contents:** `tokens.md` (all CSS custom properties by family) · `components.md`
  (component inventory + class vocabulary) · `raw/` (page + CSS bundles verbatim)
- **Refresh:** `STYLE_REF_USER={user} STYLE_REF_PASS={pw} python scripts/gen_style_reference.py`
  (script lives in the public repo). Re-run when HDX ships design-system changes.
- **Last mirrored:** {date.today().isoformat()}
""", encoding="utf-8")
    print(f"mirrored → {dest}  (tokens.md, components.md, README.md, raw/×{1 + len(css_texts)})")


if __name__ == "__main__":
    main()
