"""Knowledge-base tools: search and read the repo's markdown.

These need no credentials — they read the checked-out KB. The design intentionally
relies on grep + open-the-source rather than a semantic index (see docs/DESIGN.md),
so `search_kb` is a content grep and `read_kb_page` returns a page verbatim.

All functions take the KB repo root explicitly so they stay pure and testable;
the server wires in the configured root.
"""
from __future__ import annotations

import re
from pathlib import Path

from ._paths import safe_resolve

# search_kb intentionally walks ALL markdown (rglob), not a fixed content-dir list —
# it's a grep, and code-nav callers want hits anywhere. (No scoping constant: a prior
# one was dead + listed a dir twice, implying scoping the code didn't do.)
_SNIPPETS_PER_FILE = 3
_MAX_LINE = 200


# VCS internals + any bundled virtualenv. `antenv` is Azure Oryx's venv name; without
# it search_kb surfaces dependency READMEs from site-packages. Mirror code_tools._SKIP_DIRS.
_SKIP_DIRS = {".git", "__pycache__", ".venv", "antenv", "venv", "site-packages", "node_modules"}


def _iter_md(root: Path):
    """All KB markdown files, skipping VCS internals and bundled virtualenvs."""
    for path in sorted(root.rglob("*.md")):
        if _SKIP_DIRS.intersection(path.parts):
            continue
        yield path


# ---- OCHA-first labelling (D105) -------------------------------------------------
# The KB catalogs OTHER organisations' AA frameworks too (external-frameworks/, D77). A
# consumer that can't tell those from the OCHA/CERF portfolio (frameworks/) answers "what
# is our Nigeria flood trigger" from IFRC's EAP. So every surface that hands a page to a
# model labels it: search hits are tagged and externals grouped last; opening an external
# page prepends a banner naming the org and pointing at OCHA's own framework(s).
_EXTERNAL_DIR = "external-frameworks"
_OCHA_DIR = "frameworks"
_EXTERNAL_NOTE = ("Other organisations' frameworks (IFRC/WFP/FAO/START/government…), NOT OCHA/CERF. "
                  "Unless the question is explicitly about other organisations, answer from the "
                  "OCHA/CERF pages above; if you cite one of these, say whose framework it is.")


def _frontmatter(text: str) -> dict:
    """Best-effort YAML frontmatter → dict ({} when absent or unparsable)."""
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    try:
        import yaml
        fm = yaml.safe_load(text[3:end])
        return fm if isinstance(fm, dict) else {}
    except Exception:
        return {}


def is_external_framework_page(rel: str) -> bool:
    """True for a framework page under external-frameworks/<org>/ (not the section's own
    README / template / inventory report)."""
    parts = rel.split("/")
    return len(parts) == 3 and parts[0] == _EXTERNAL_DIR and not parts[2].startswith("_")


_ISO3_CACHE: dict = {}   # (root, frameworks-tree fingerprint) → {ISO3: [folder, …]}


def _ocha_country_map(root: Path) -> dict[str, list[str]]:
    """ISO3 → OCHA/CERF framework folders, from every version page's `country_iso3`
    frontmatter (scalar or list). Memoised on the frameworks tree's (path, mtime) set:
    parsing ~80 YAML headers per call is cheap once, not 174× per lint/regen run, and
    the served tree can be swapped under us (refresh.py) or edited locally."""
    fdir = root / _OCHA_DIR
    if not fdir.is_dir():
        return {}
    pages = sorted(p for p in fdir.glob("*/*.md")
                   if not p.name.startswith("_") and p.name != "README.md")
    key = (str(root), tuple((p.name, p.parent.name, p.stat().st_mtime_ns) for p in pages))
    if key in _ISO3_CACHE:
        return _ISO3_CACHE[key]
    found: dict[str, set[str]] = {}
    for page in pages:
        try:
            fm = _frontmatter(page.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError):
            continue
        iso = fm.get("country_iso3")
        for x in (iso if isinstance(iso, list) else [iso]):
            if x:
                found.setdefault(str(x).upper(), set()).add(page.parent.name)
    _ISO3_CACHE.clear()   # one live tree at a time
    _ISO3_CACHE[key] = {k: sorted(v) for k, v in found.items()}
    return _ISO3_CACHE[key]


def ocha_frameworks_for(root: Path, iso3: str | None) -> list[str]:
    """OCHA/CERF framework folders covering a country, matched on the version pages'
    `country_iso3` frontmatter — NOT the folder name, which hides region-named
    multi-country frameworks (lac-dry-corridor covers SLV/GTM/HND)."""
    if not iso3:
        return []
    return list(_ocha_country_map(root).get(str(iso3).upper(), []))


# The banner every external-frameworks page carries in its BODY, directly under the H1
# (D105). One producer — gen_hub_stubs.py emits it, gen_external_banners.py (re)writes it,
# check_docs.py recomputes it (lint NO-EXTERNAL-BANNER) — so it can't drift between them
# and goes stale visibly when a new frameworks/ folder lands for one of the countries.
PAGE_BANNER_MARK = "**Not an OCHA/CERF framework.**"


def external_page_banner(root: Path, org: str, iso3: str) -> str:
    """The markdown blockquote for an external page's body (relative links from
    external-frameworks/<org>/<page>.md)."""
    own = ocha_frameworks_for(root, iso3)
    tail = (f"OCHA's own {iso3} framework(s): "
            + ", ".join(f"[{n}](../../{_OCHA_DIR}/{n}/README.md)" for n in own) + "."
            if own else f"OCHA/CERF has no framework in {iso3}.")
    return (f"> {PAGE_BANNER_MARK} This is {org}'s anticipatory-action framework, "
            f"catalogued here for cross-organisation comparison ([why](../README.md)). {tail}")


def external_banner(root: Path, rel: str, text: str) -> str:
    """The banner prepended when an external-frameworks page is opened."""
    fm = _frontmatter(text)
    org = fm.get("org") or rel.split("/")[1]
    iso3 = fm.get("country_iso3")
    ocha = ocha_frameworks_for(root, iso3)
    own = (", ".join(f"{_OCHA_DIR}/{f}/README.md" for f in ocha)
           if ocha else f"none — OCHA/CERF has no framework in {iso3 or 'this country'}")
    return "\n".join([
        f"> ⚠️ EXTERNAL FRAMEWORK — this is {org}'s anticipatory-action framework, NOT an "
        f"OCHA/CERF one (KB section `{_EXTERNAL_DIR}/`, catalogued for cross-organisation comparison).",
        f"> OCHA's own framework(s) for {iso3 or 'this country'}: {own}.",
        "> Unless the user asked about other organisations' frameworks, answer from the OCHA "
        f"page(s); if you do cite this page, say explicitly that it is {org}'s framework, not OCHA's.",
    ])


def _hit_tag(rel: str, fm: dict) -> str:
    """Short provenance tag shown next to a search hit."""
    if is_external_framework_page(rel):
        return f"[EXTERNAL — {fm.get('org') or rel.split('/')[1]}; not OCHA/CERF]"
    if rel.startswith(_EXTERNAL_DIR + "/"):
        return "[external-frameworks section — other orgs]"
    if rel.startswith(_OCHA_DIR + "/"):
        return "[OCHA/CERF framework]"
    if rel == "catalog-global.md":
        return "[cross-org index: OCHA + other orgs]"
    return ""


def search_kb(root: Path, query: str, max_results: int = 20, regex: bool = False) -> str:
    """Search KB markdown for `query`; return matching pages with line snippets.

    Case-insensitive. A multi-word query matches pages containing ALL the words —
    anywhere in the page, not necessarily on one line or adjacent; exact-phrase
    matches rank first. Set `regex=True` to treat `query` as a regular expression.
    Use `read_kb_page` to open a full page.
    """
    root = root.resolve()
    if not query.strip():
        return "Empty query."
    # A multi-word query used to require the WHOLE query as a substring of a single line —
    # usage telemetry showed most real searches ("Nigeria trigger development Adamawa")
    # returning zero hits on pages containing every word. AND-across-the-page instead.
    terms = [query] if regex else query.split()
    try:
        term_pats = [re.compile(t if regex else re.escape(t), re.IGNORECASE) for t in terms]
        phrase_pat = re.compile(query if regex else re.escape(query), re.IGNORECASE)
    except re.error as e:
        return f"Invalid regex: {e}"

    hits = []  # (score, rel_path, [snippet lines], tag)
    for path in _iter_md(root):
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        if not all(p.search(text) for p in term_pats):
            continue
        # snippet lines: most distinct terms first, then earliest in the page
        scored = sorted((-sum(1 for p in term_pats if p.search(ln)), i + 1, ln)
                        for i, ln in enumerate(text.splitlines())
                        if any(p.search(ln) for p in term_pats))
        snippets = [f"  L{n}: {ln.strip()[:_MAX_LINE]}" for _, n, ln in scored[:_SNIPPETS_PER_FILE]]
        if len(scored) > _SNIPPETS_PER_FILE:
            snippets.append(f"  … +{len(scored) - _SNIPPETS_PER_FILE} more matching line(s)")
        # cap each term's contribution so huge generated indexes don't drown content pages
        score = sum(min(len(p.findall(text)), 25) for p in term_pats)
        if len(terms) > 1 and phrase_pat.search(text):
            score += 10_000   # exact phrase beats scattered-words matches
        rel = path.relative_to(root).as_posix()
        hits.append((score, rel, snippets, _hit_tag(rel, _frontmatter(text))))

    if not hits:
        return f"No matches for {query!r}."
    hits.sort(key=lambda h: (-h[0], h[1]))
    total = len(hits)

    # OCHA/team pages first; other organisations' framework pages grouped under a labelled
    # divider so a reader can't mistake IFRC's Nigeria EAP for OCHA's Nigeria framework.
    # The split happens BEFORE the max_results cut: 176 external pages share the OCHA
    # pages' vocabulary (country, hazard, "framework"), so a post-cut regroup could only
    # reorder survivors while "flood framework" pushed frameworks/nga-flooding below the
    # cut (review finding on #622). Externals keep a small reserved quota so cross-org
    # questions still see them; the rest of the slots go to OCHA/team pages.
    own_all = [h for h in hits if not h[1].startswith(_EXTERNAL_DIR + "/")]
    ext_all = [h for h in hits if h[1].startswith(_EXTERNAL_DIR + "/")]
    ext_slots = min(len(ext_all), max(3, max_results // 4)) if ext_all else 0
    own = own_all[:max(0, max_results - ext_slots)]
    ext = ext_all[:max_results - len(own)]

    def _emit(group):
        for count, rel, snippets, tag in group:
            head = f"### {rel}  ({min(count, 9999)} match{'es' if count != 1 else ''})"
            out.append(f"{head}  {tag}" if tag else head)
            out.extend(snippets)
            out.append("")

    shown = ""
    if total > len(own) + len(ext):
        shown = (f" (showing {len(own)} of {len(own_all)} OCHA/team pages"
                 + (f" + {len(ext)} of {len(ext_all)} {_EXTERNAL_DIR}/ pages" if ext_all else "")
                 + "; raise max_results for more)")
    out = [f"{total} page(s) match {query!r}{shown}:", ""]
    _emit(own)
    if ext:
        out.append(f"--- {len(ext)} of {len(ext_all)} hit(s) in {_EXTERNAL_DIR}/ — {_EXTERNAL_NOTE} ---")
        out.append("")
        _emit(ext)
    out.append("Open a page with read_kb_page(path).")
    return "\n".join(out)


def read_kb_page(root: Path, path: str) -> str:
    """Return the full markdown of a KB page (frontmatter + body).

    `path` is repo-relative, e.g. 'frameworks/lac-dry-corridor/2026-04-04.md'
    or a generated index like 'catalog.md' / 'infrastructure/db-schema.md'.
    """
    try:
        target = safe_resolve(root, path)
    except ValueError as e:
        return str(e)
    if not target.is_file():
        return f"No such page: {path}"
    try:
        text = target.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as e:
        return f"Could not read {path}: {e}"
    rel = target.relative_to(root.resolve()).as_posix()
    if is_external_framework_page(rel):
        return external_banner(root, rel, text) + "\n\n" + text
    return text


def get_index(root: Path, which: str) -> str:
    """Return a generated orientation index verbatim.

    `which` is one of: 'catalog' (the OCHA/CERF framework-versions — the team's own
    portfolio), 'catalog-global' (every AA framework incl. OTHER organisations' — only
    when the question is explicitly cross-org), 'dependency-graph'
    (cross-type deps + blast radius), 'db-schema' / 'db-schema-dev' (DB snapshots),
    'pipeline-registry' (deployed jobs + health). Read these first to orient.
    """
    index_paths = {
        "catalog": "catalog.md",
        "catalog-global": "catalog-global.md",
        "dependency-graph": "infrastructure/dependency-graph.md",
        "db-schema": "infrastructure/db-schema.md",
        "db-schema-dev": "infrastructure/db-schema-dev.md",
        "pipeline-registry": "infrastructure/pipeline-registry.md",
    }
    rel = index_paths.get(which)
    if rel is None:
        return f"Unknown index {which!r}. Options: {', '.join(index_paths)}."
    return read_kb_page(root, rel)
