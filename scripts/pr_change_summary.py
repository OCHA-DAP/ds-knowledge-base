#!/usr/bin/env python3
"""Deterministic "What changed" summary for the bots' PR bodies — show ONLY what changed.

KB pages are one paragraph per line, so GitHub's line diff paints a whole paragraph red+green
when three words moved. The bot PRs (kb-ingest re-syncs, kb-autofix, docs-audit) also front-load
an LLM narrative ("Checked / Changed / Still verify") that describes the change rather than
showing it. This script derives the change list from git itself and renders it so a reviewer
sees, per file: the frontmatter FIELDS that changed (old → new), and per body SECTION the
changed lines reduced to the changed WORDS with a little context. Nothing that didn't change is
shown. The workflows put this at the top of the PR body; the LLM narrative is folded below it.

Usage:
  python scripts/pr_change_summary.py --cached [--out FILE]          # index vs HEAD (after `git add`)
  python scripts/pr_change_summary.py --base origin/main --head HEAD  # ref vs ref
Exit 0 always (a summary that fails must never block a PR); prints nothing if nothing changed.
"""
from __future__ import annotations

import argparse
import difflib
import json
import re
import subprocess
import sys

try:
    import yaml
except ImportError:  # pragma: no cover — CI installs pyyaml; degrade to text frontmatter diff
    yaml = None

CTX_WORDS = 7          # words of context on either side of a changed run
MERGE_GAP = 3          # changed runs closer than this (in words) are shown as ONE -/+ run
JOIN_GAP = 14          # two changed runs closer than this (in words) share one context line
LINE_CAP = 480         # chars shown of a wholly-added / wholly-removed line
SHORT_VAL = 70         # scalar values up to this length go in the frontmatter table
PAIR_MIN = 0.45        # min similarity to treat a removed+added line as an edit of one line
FILE_LINE_BUDGET = 260 # output lines per file before truncating
TOTAL_CHAR_BUDGET = 28000  # PR bodies cap at 64k; leave room for the narrative
_UNSET = object()


# ----------------------------------------------------------------------------- git plumbing
def git(*args: str) -> str:
    r = subprocess.run(["git", *args], capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)}: {r.stderr.strip()}")
    return r.stdout


def changed_files(cached: bool, base: str, head: str) -> list[tuple[str, str, str | None]]:
    """→ [(status, path, old_path)] with rename detection. status ∈ A M D R."""
    if cached:
        out = git("diff", "--cached", "-M", "--name-status", "HEAD")
    else:
        out = git("diff", "-M", "--name-status", base, head)
    files = []
    for line in out.splitlines():
        parts = line.split("\t")
        st = parts[0][0]
        if st == "R":
            files.append(("R", parts[2], parts[1]))
        else:
            files.append((st, parts[1], None))
    return files


def blob(ref: str, path: str) -> str | None:
    r = subprocess.run(["git", "show", f"{ref}:{path}"], capture_output=True)
    if r.returncode != 0:
        return None
    if b"\0" in r.stdout[:8000]:
        return None  # binary
    return r.stdout.decode("utf-8", errors="replace")


# ----------------------------------------------------------------------------- markdown split
FM_RE = re.compile(r"\A---\n(.*?)\n---\n?", re.S)


def split_page(text: str) -> tuple[str | None, str]:
    m = FM_RE.match(text)
    if not m:
        return None, text
    return m.group(1), text[m.end():]


def parse_fm(fm: str | None):
    if fm is None or yaml is None:
        return None
    try:
        d = yaml.safe_load(fm)
        return d if isinstance(d, dict) else None
    except Exception:
        return None


# ----------------------------------------------------------------------------- word-level diff
TOK_RE = re.compile(r"\s+|\w+|[^\w\s]")


def tokens(s: str) -> list[str]:
    return TOK_RE.findall(s)


def similarity(a: str, b: str) -> float:
    return difflib.SequenceMatcher(None, tokens(a), tokens(b), autojunk=False).ratio()


def _clip(s: str, n: int = LINE_CAP) -> str:
    s = s.rstrip("\n")
    return s if len(s) <= n else s[:n].rstrip() + f" …[+{len(s) - n} chars]"


def _ctx_words(toks: list[str], start: int, end: int) -> str:
    """Join toks[start:end], collapsing whitespace."""
    return re.sub(r"\s+", " ", "".join(toks[start:end])).strip()


def word_fragments(old: str, new: str) -> list[str]:
    """Render an edited line as diff-block fragments: grey context, '-' removed run, '+' added run.
    Only the changed words (plus CTX_WORDS words either side) are shown; the rest is '…'."""
    a, b = tokens(old), tokens(new)
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    ops = [list(op) for op in sm.get_opcodes() if op[0] != "equal"]
    if not ops:
        return []
    # token-level matching happily keeps a lone comma or "a" as "equal" inside an otherwise
    # rewritten phrase — merge runs separated by only a few words into one -/+ run
    merged: list[list] = []
    for op in ops:
        if merged and sum(1 for t in a[merged[-1][2]:op[1]] if not t.isspace()) <= MERGE_GAP:
            merged[-1][2], merged[-1][4] = op[2], op[4]
        else:
            merged.append(op)
    ops = merged

    def wc(seq, i, j):  # words in seq[i:j]
        return sum(1 for t in seq[i:j] if not t.isspace())

    def ctx_before(i1):
        k, n = i1, 0
        while k > 0 and n < CTX_WORDS:
            k -= 1
            if not a[k].isspace(): n += 1
        return k

    def ctx_after(i2):
        k, n = i2, 0
        while k < len(a) and n < CTX_WORDS:
            if not a[k].isspace(): n += 1
            k += 1
        return k

    out: list[str] = []
    prev_end = None  # old-side index where the previous run's context ended
    for idx, (_tag, i1, i2, j1, j2) in enumerate(ops):
        if prev_end is None:
            k = ctx_before(i1)
            pre = _ctx_words(a, k, i1)
            if pre:
                out.append("  " + ("…" if k > 0 else "") + pre)
        elif wc(a, prev_end, i1) <= JOIN_GAP:
            gap = _ctx_words(a, prev_end, i1)   # short gap: print it once, no ellipses
            if gap:
                out.append("  " + gap)
        else:
            post = _ctx_words(a, prev_end, ctx_after(prev_end))
            out.append("  " + post + "…")
            k = ctx_before(i1)
            out.append("  …" + _ctx_words(a, k, i1))
        rem = _ctx_words(a, i1, i2)
        add = _ctx_words(b, j1, j2)
        if rem:
            out.append("- " + _clip(rem))
        if add:
            out.append("+ " + _clip(add))
        prev_end = i2
    k2 = ctx_after(prev_end)
    post = _ctx_words(a, prev_end, k2)
    if post:
        out.append("  " + post + ("…" if k2 < len(a) else ""))
    return out


# ----------------------------------------------------------------------------- line alignment
def align(old_lines: list[str], new_lines: list[str]):
    """→ list of ('add', new_line) | ('del', old_line) | ('edit', old, new) | ('moved', line),
    each tagged with the (old_idx, new_idx) it applies to, in new-file order."""
    sm = difflib.SequenceMatcher(None, old_lines, new_lines, autojunk=False)
    events: list[tuple] = []  # (tag, oi, ni, old, new)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            continue
        dels = [(i, old_lines[i]) for i in range(i1, i2)]
        adds = [(j, new_lines[j]) for j in range(j1, j2)]
        # pair removed↔added lines by similarity (greedy, best first)
        cands = []
        for oi, ol in dels:
            if not ol.strip():
                continue
            for ni, nl in adds:
                if not nl.strip():
                    continue
                r = similarity(ol, nl)
                if r >= PAIR_MIN:
                    cands.append((r, oi, ni))
        cands.sort(reverse=True)
        used_o, used_n = set(), set()
        for r, oi, ni in cands:
            if oi in used_o or ni in used_n:
                continue
            used_o.add(oi); used_n.add(ni)
            events.append(("edit", oi, ni, old_lines[oi], new_lines[ni]))
        for oi, ol in dels:
            if oi not in used_o:
                events.append(("del", oi, None, ol, None))
        for ni, nl in adds:
            if ni not in used_n:
                events.append(("add", None, ni, None, nl))
    # a line removed here and added verbatim elsewhere = moved, not changed
    del_text = {e[3].strip(): e for e in events if e[0] == "del" and e[3].strip()}
    add_text = {e[4].strip(): e for e in events if e[0] == "add" and e[4].strip()}
    moved = set(del_text) & set(add_text)
    final = []
    for e in events:
        if e[0] == "del" and e[3].strip() in moved:
            continue
        if e[0] == "add" and e[4].strip() in moved:
            final.append(("moved", None, e[2], None, e[4]))
        else:
            final.append(e)
    return final


HEAD_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")


def section_index(lines: list[str]) -> list[str]:
    """For each line, the nearest preceding heading (or '' before the first)."""
    cur, out = "", []
    for ln in lines:
        m = HEAD_RE.match(ln)
        if m:
            cur = m.group(2).strip()
        out.append(cur)
    return out


# ----------------------------------------------------------------------------- frontmatter diff
def _repr(v) -> str:
    if isinstance(v, str):
        return v
    if v is None:
        return "null"
    if isinstance(v, (dict, list)):
        return json.dumps(v, ensure_ascii=False, sort_keys=True, default=str)
    return str(v)


def _short(v, n: int = SHORT_VAL) -> str:
    s = _repr(v).replace("\n", " ")
    return s if len(s) <= n else s[: n - 1].rstrip() + "…"


def _item_label(v) -> str:
    """One-line label for a list item (a dict shows its most identifying field)."""
    if isinstance(v, dict):
        for k in ("id", "url", "name", "title", "date", "version", "label"):
            if k in v:
                return f"{k}={_short(v[k], 90)}"
        return _short(v, 110)
    return _short(v, 110)


def diff_fm(path: str, old, new, changes: list) -> None:
    """Append (kind, path, old, new) tuples. kind ∈ set, add, del, item+, item-, edit."""
    if isinstance(old, dict) and isinstance(new, dict):
        for k in sorted(set(old) | set(new), key=str):
            p = f"{path}.{k}" if path else str(k)
            if k not in old:
                changes.append(("add", p, _UNSET, new[k]))
            elif k not in new:
                changes.append(("del", p, old[k], _UNSET))
            else:
                diff_fm(p, old[k], new[k], changes)
        return
    if isinstance(old, list) and isinstance(new, list):
        oa, na = [_repr(x) for x in old], [_repr(x) for x in new]
        sm = difflib.SequenceMatcher(None, oa, na, autojunk=False)
        for tag, i1, i2, j1, j2 in sm.get_opcodes():
            if tag == "equal":
                continue
            rem = list(range(i1, i2)); ins = list(range(j1, j2))
            # pair by similarity so an edited item shows as an edit, not remove+add
            cands = sorted(((similarity(oa[i], na[j]), i, j) for i in rem for j in ins), reverse=True)
            uo, un = set(), set()
            for r, i, j in cands:
                if r < PAIR_MIN or i in uo or j in un:
                    continue
                uo.add(i); un.add(j)
                diff_fm(f"{path}[{j}]", old[i], new[j], changes)
            for i in rem:
                if i not in uo:
                    changes.append(("item-", path, old[i], _UNSET))
            for j in ins:
                if j not in un:
                    changes.append(("item+", path, _UNSET, new[j]))
        return
    if old != new:
        changes.append(("set", path, old, new))


def render_fm(changes: list) -> list[str]:
    out: list[str] = []
    rows, block = [], []
    for kind, p, o, n in changes:
        if kind == "set" and len(_repr(o)) <= SHORT_VAL and len(_repr(n)) <= SHORT_VAL:
            rows.append(f"| `{p}` | {_cell(o)} | {_cell(n)} |")
        elif kind == "set" and isinstance(o, str) and isinstance(n, str):
            block.append(f"@@ {p}")
            frags = word_fragments(o, n) or ["- " + _clip(o), "+ " + _clip(n)]
            block.extend(frags)
        elif kind == "set":
            block.append(f"@@ {p}"); block.append("- " + _clip(_repr(o))); block.append("+ " + _clip(_repr(n)))
        elif kind == "add":
            block.append(f"@@ {p}  (new field)"); block.append("+ " + _clip(_repr(n)))
        elif kind == "del":
            block.append(f"@@ {p}  (field removed)"); block.append("- " + _clip(_repr(o)))
        elif kind == "item+":
            block.append(f"@@ {p}  (+1 item)"); block.append("+ " + _clip(_item_label(n)))
        elif kind == "item-":
            block.append(f"@@ {p}  (−1 item)"); block.append("- " + _clip(_item_label(o)))
    if rows:
        out += ["| field | before | after |", "|---|---|---|", *rows, ""]
    if block:
        out += ["```diff", *block, "```", ""]
    return out


def _cell(v) -> str:
    if v is None:
        return "*(none)*"
    s = _short(v).replace("|", "\\|")
    return f"`` {s} ``" if "`" in s else f"`{s}`"


# ----------------------------------------------------------------------------- per-file render
def render_body(old_body: str, new_body: str, md: bool = True) -> list[str]:
    ol, nl = old_body.splitlines(), new_body.splitlines()
    events = align(ol, nl)
    if not events:
        return []
    osec, nsec = (section_index(ol), section_index(nl)) if md else ([""] * len(ol), [""] * len(nl))

    def sec(e):
        return nsec[e[2]] if e[2] is not None else osec[e[1]]

    def key(e):  # order by position in the new file (deletions by their old position)
        return (e[2] if e[2] is not None else e[1], 0 if e[0] != "del" else 1)

    events.sort(key=key)
    out: list[str] = []
    cur = None
    block: list[str] = []

    def flush():
        nonlocal block
        if block:
            out.extend(["```diff", *block, "```", ""])
            block = []

    for e in events:
        s = sec(e)
        if s != cur:
            flush()
            cur = s
            if md:
                out.append(f"**§ {s}**" if s else "**§ (top of page)**")
                out.append("")
        tag, _oi, _ni, o, n = e
        if tag == "edit" and (n or "").lstrip().startswith("|"):
            cells = [c.strip() for c in n.strip().strip("|").split("|")]
            first = next((c for c in cells if c), "")
            if first and not set(first) <= set("-: "):
                block.append("@@ row " + _clip(first, 80))
        if tag == "edit":
            if HEAD_RE.match(n or "") or HEAD_RE.match(o or ""):
                block += ["- " + _clip(o), "+ " + _clip(n)]
            else:
                block += word_fragments(o, n) or ["- " + _clip(o), "+ " + _clip(n)]
        elif tag == "add":
            if n.strip():
                block.append("+ " + _clip(n))
        elif tag == "del":
            if o.strip():
                block.append("- " + _clip(o))
        elif tag == "moved":
            block.append("  (moved, text unchanged) " + _clip(n, 100))
    flush()
    return out


def line_counts(old: str, new: str) -> tuple[int, int]:
    ins = dele = 0
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, old.splitlines(), new.splitlines(), autojunk=False).get_opcodes():
        if tag in ("replace", "delete"):
            dele += i2 - i1
        if tag in ("replace", "insert"):
            ins += j2 - j1
    return ins, dele


def render_new_page(text: str) -> list[str]:
    fm, body = split_page(text)
    d = parse_fm(fm) or {}
    out = []
    bits = [f"`{k}: {_short(d[k], 60)}`" for k in ("title", "type", "status", "source_repo", "hazard", "country_iso3") if k in d]
    if bits:
        out.append("New page. " + " · ".join(bits))
    heads = [m.group(2) for ln in body.splitlines() if (m := HEAD_RE.match(ln)) and len(m.group(1)) <= 2]
    if heads:
        out.append("Sections: " + " · ".join(f"*{h}*" for h in heads))
    out.append(f"{len(text.splitlines())} lines — read it in the Files tab; nothing here existed before.")
    return out + [""]


def render_file(status: str, path: str, old_path: str | None, old: str | None, new: str | None) -> tuple[str, list[str]]:
    """→ (one-line stat cell, detail lines)."""
    if old is None and new is None:
        return "binary", []
    if status == "A" or old is None:
        n = len((new or "").splitlines())
        det = render_new_page(new) if path.endswith(".md") else [f"New file, {n} lines.", ""]
        return f"**new** +{n}", det
    if status == "D" or new is None:
        return f"**deleted** −{len(old.splitlines())}", ["Page deleted.", ""]
    ins, dele = line_counts(old, new)
    stat = f"+{ins} −{dele}"
    if status == "R":
        stat = f"renamed from `{old_path}` · " + stat
    det: list[str] = []
    if path.endswith(".md"):
        ofm, obody = split_page(old)
        nfm, nbody = split_page(new)
        od, nd = parse_fm(ofm), parse_fm(nfm)
        if od is not None and nd is not None:
            ch: list = []
            diff_fm("", od, nd, ch)
            if ch:
                det.append("**Frontmatter**"); det.append("")
                det += render_fm(ch)
        elif (ofm or "") != (nfm or ""):
            det.append("**Frontmatter**"); det.append("")
            det += render_body(ofm or "", nfm or "")
        bd = render_body(obody, nbody)
        if bd:
            det.append("**Body**"); det.append("")
            det += bd
    else:
        det += render_body(old, new, md=False)
    if len(det) > FILE_LINE_BUDGET:
        cut = det[:FILE_LINE_BUDGET]
        if cut and cut[-1] != "```" and any(l == "```diff" for l in cut) and cut.count("```diff") > cut.count("```") - cut.count("```diff"):
            cut.append("```")
        det = cut + [f"*… truncated ({len(det) - FILE_LINE_BUDGET} more lines) — see the Files tab for the rest.*", ""]
    return stat, det


# ----------------------------------------------------------------------------- main
def build(cached: bool, base: str, head: str) -> str:
    files = changed_files(cached, base, head)
    if not files:
        return ""
    old_ref = "HEAD" if cached else base
    new_ref = "" if cached else head  # '' → index ("git show :path")
    rows, details = [], []
    for st, path, old_path in files:
        old = None if st == "A" else blob(old_ref, old_path or path)
        new = None if st == "D" else blob(new_ref, path)
        stat, det = render_file(st, path, old_path, old, new)
        rows.append(f"| `{path}` | {stat} |")
        if det:
            details.append(f"### `{path}`")
            details.append("")
            details.extend(det)
    n = len(files)
    out = [
        "## What changed",
        "",
        f"{n} file{'s' if n != 1 else ''}. Only changed fields, sections and words are shown below — "
        "everything not listed is untouched.",
        "",
        "| file | lines |",
        "|---|---|",
        *rows,
        "",
        *details,
    ]
    text = "\n".join(out).rstrip() + "\n"
    if len(text) > TOTAL_CHAR_BUDGET:
        text = text[:TOTAL_CHAR_BUDGET]
        if text.count("```") % 2:
            text += "\n```"
        text += "\n\n*… summary truncated — see the Files tab.*\n"
    return text


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--cached", action="store_true", help="index vs HEAD (run after `git add`)")
    ap.add_argument("--base", default="origin/main")
    ap.add_argument("--head", default="HEAD")
    ap.add_argument("--out", help="write here instead of stdout (file is empty when nothing changed)")
    a = ap.parse_args()
    try:
        text = build(a.cached, a.base, a.head)
    except Exception as e:  # never block a PR on the summary
        print(f"pr_change_summary: {e}", file=sys.stderr)
        text = ""
    if a.out:
        with open(a.out, "w", encoding="utf-8") as f:
            f.write(text)
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
