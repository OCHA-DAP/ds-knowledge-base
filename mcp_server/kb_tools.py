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


def ocha_frameworks_for(root: Path, iso3: str | None) -> list[str]:
    """OCHA/CERF framework folders for a country (frameworks/<iso3>-<hazard>/)."""
    if not iso3:
        return []
    prefix = f"{str(iso3).lower()}-"
    fdir = root / _OCHA_DIR
    if not fdir.is_dir():
        return []
    return sorted(d.name for d in fdir.iterdir() if d.is_dir() and d.name.startswith(prefix))


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
    hits = hits[:max_results]

    # OCHA/team pages first; other organisations' framework pages grouped under a labelled
    # divider so a reader can't mistake IFRC's Nigeria EAP for OCHA's Nigeria framework.
    own = [h for h in hits if not h[1].startswith(_EXTERNAL_DIR + "/")]
    ext = [h for h in hits if h[1].startswith(_EXTERNAL_DIR + "/")]

    def _emit(group):
        for count, rel, snippets, tag in group:
            head = f"### {rel}  ({min(count, 9999)} match{'es' if count != 1 else ''})"
            out.append(f"{head}  {tag}" if tag else head)
            out.extend(snippets)
            out.append("")

    out = [f"{total} page(s) match {query!r}" + (f" (showing top {max_results})" if total > max_results else "") + ":", ""]
    _emit(own)
    if ext:
        out.append(f"--- {len(ext)} hit(s) in {_EXTERNAL_DIR}/ — {_EXTERNAL_NOTE} ---")
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
