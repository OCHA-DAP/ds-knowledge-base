"""AA tracker tools: OCHA's anticipatory-action portfolio, read live from the tracker (D125).

ds-aa-tracking is the authoritative AA record (D115, D124). Its site publishes open files for
programs and AI assistants (https://ocha-dap.github.io/ds-aa-tracking/llms.txt): the map's
figures in text, the counting rules, and the data behind the open map as JSON/CSV. These tools
read those files, so the KB keeps no copy of the AA record: the `frameworks/` pages are frozen
(2026-09-28) and are not a source for current figures.

The same four tools are served two ways (server.py):
  - inside the KB server (both tiers), next to the KB tools;
  - on their own at <public KB app>/aa-tracker/mcp, with AA-only instructions, for anyone
    who wants the tracker without the team's KB.

No credentials: everything read here is already public. Fetches are cached in-process
(KB_AA_TRACKER_TTL seconds, default 3600; the tracker rebuilds nightly). If a refresh fails,
the last good copy this process fetched is served with a note saying how old it is, and that
file is not retried for 5 minutes. After a restart there is no copy until the first fetch
succeeds.

Environment:
    KB_AA_TRACKER_BASE   base URL of the tracker's open files
                         (default https://ocha-dap.github.io/ds-aa-tracking/)
    KB_AA_TRACKER_TTL    cache lifetime in seconds (default 3600)
"""
from __future__ import annotations

import csv
import functools
import io
import json
import os
import re
import threading
import time
import urllib.error
import urllib.request

BASE = os.environ.get("KB_AA_TRACKER_BASE", "https://ocha-dap.github.io/ds-aa-tracking/").rstrip("/") + "/"
TTL = int(os.environ.get("KB_AA_TRACKER_TTL", "3600"))
_MAX_BYTES = 8 * 1024 * 1024  # aa-map-data.json is ~0.9 MB; refuse anything absurd
_TIMEOUT = 15
# After a failed fetch, don't try that file again for this long: a hanging site would
# otherwise make every call wait the full timeout (and hold a worker thread) once TTL is up.
_RETRY_AFTER = 300
_UA = "ds-knowledge-base-mcp (+https://github.com/OCHA-DAP/ds-knowledge-base)"

# aa_data(file=…) → the tracker's JSON data file. Each carries description, columns, rows and
# the snapshot/caveat stamps (llms.txt § Data files).
DATA_FILES = {
    "frameworks": "aa-frameworks.json",
    "versions": "aa-versions.json",
    "activations": "aa-activations.json",
    "prearranged-funding": "aa-prearranged-funding.json",
    "cofinancing": "aa-cofinancing.json",
    "funds": "aa-funds.json",
}

INSTRUCTIONS = (
    "OCHA's anticipatory action (AA) portfolio, read live from the AA tracker "
    "(https://ocha-dap.github.io/ds-aa-tracking/), the authoritative record of OCHA's AA "
    "frameworks: which exist, their versions and triggers, pre-arranged funding, "
    "co-financing, activations, the money released and the people reached or targeted. "
    "Start with aa_overview(): the map's headline figures and the counting rules. Never add "
    "up rows yourself without those rules: pre-arranged funding is a stock (never summed "
    "across years, never added to released money), some envelopes are already counted twice, "
    "co-financing is separate, and figures depend on the map layer. For one framework use "
    "aa_framework(country_iso3, hazard); for tables use aa_data(file, filters); for field "
    "meanings and vocabulary use aa_guide(section). Every answer carries the data snapshot "
    "time; cite it. The tracker describes itself as under development: its figures may be "
    "incorrect, so say so when you report them."
)


# ---- fetching + cache ---------------------------------------------------------

class _Entry:
    __slots__ = ("failed_until", "fetched_at", "last_error", "lock", "parsed", "text")

    def __init__(self) -> None:
        self.text: str | None = None
        self.fetched_at = 0.0
        self.parsed = None
        self.failed_until = 0.0
        self.last_error = ""
        self.lock = threading.Lock()


_cache: dict[str, _Entry] = {}
_cache_lock = threading.Lock()


def _entry(name: str) -> _Entry:
    with _cache_lock:
        return _cache.setdefault(name, _Entry())


def _download(name: str) -> str:
    req = urllib.request.Request(BASE + name, headers={"User-Agent": _UA})
    with urllib.request.urlopen(req, timeout=_TIMEOUT) as resp:
        data = resp.read(_MAX_BYTES + 1)
    if len(data) > _MAX_BYTES:
        raise ValueError(f"{name} is larger than {_MAX_BYTES} bytes")
    return data.decode("utf-8")


def _get(name: str, parse=None):
    """(content, note) for one tracker file; content is parse(text) when parse is given.

    Cached for TTL seconds. A failed refresh serves the last good copy this process holds,
    with a note, and waits _RETRY_AFTER seconds before trying that file again; with no copy
    at all it raises RuntimeError (the tool turns that into a plain message)."""
    e = _entry(name)
    with e.lock:  # one fetch per file at a time; other files are not blocked
        now = time.time()
        fresh = e.text is not None and now - e.fetched_at < TTL
        if not fresh and now >= e.failed_until:
            try:
                text = _download(name)
                parsed = parse(text) if parse else None
            except Exception as exc:  # noqa: BLE001 — network, HTTP, decode or parse error
                e.failed_until, e.last_error = now + _RETRY_AFTER, str(exc)
            else:
                e.text, e.parsed, e.fetched_at = text, parsed, now
                e.failed_until, e.last_error = 0.0, ""
                return (parsed if parse else text), ""
        if e.text is None:
            raise RuntimeError(f"could not fetch {BASE + name}: {e.last_error}")
        if parse and e.parsed is None:
            e.parsed = parse(e.text)
        note = ""
        if now - e.fetched_at >= TTL:  # serving past its lifetime because a refresh failed
            note = (f"(Could not refresh {name} from the tracker: {e.last_error}. Serving the "
                    f"copy fetched {int((now - e.fetched_at) / 60)} min ago.)")
        return (e.parsed if parse else e.text), note


def _clear_cache() -> None:
    """Testing hook."""
    with _cache_lock:
        _cache.clear()


# ---- llms.txt helpers ----------------------------------------------------------

def _sections(md: str) -> dict[str, str]:
    """Split a markdown file on '## ' headings. Key '' is the text before the first one."""
    out: dict[str, str] = {}
    key, buf = "", []
    for line in md.splitlines():
        if line.startswith("## "):
            out[key] = "\n".join(buf).strip()
            key, buf = line[3:].strip(), []
        else:
            buf.append(line)
    out[key] = "\n".join(buf).strip()
    return out


def _intro_parts(llms: str) -> tuple[str, str, str]:
    """(snapshot line, caveat, counting rules) from llms.txt's intro."""
    intro = _sections(llms).get("", "")
    m = re.search(r"Data snapshot [^.;]*(?:UTC)?[^.]*\.", intro)
    snapshot = m.group(0).rstrip(".") if m else ""
    m = re.search(r"\*\*Caveat\.\*\*\s*(.+)", intro)
    caveat = m.group(1).strip() if m else ""
    i = intro.find("Counting rules")
    rules = intro[i:].strip() if i >= 0 else ""
    return snapshot, caveat, rules


def _header(snapshot: str, caveat: str, note: str = "") -> str:
    lines = [f"Source: OCHA AA tracker, {BASE} (the authoritative AA record)."]
    if snapshot:
        lines.append(snapshot + ".")
    if caveat:
        lines.append(f"Caveat (the tracker's own): {caveat}")
    if note:
        lines.append(note)
    return "\n".join(lines)


def _guard(fn):
    """Turn a fetch failure into a readable tool result instead of a stack trace."""
    @functools.wraps(fn)  # keeps the signature FastMCP builds the tool schema from
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except RuntimeError as exc:
            return (f"The AA tracker could not be reached: {exc}. Its files are at {BASE}llms.txt "
                    "— try again later, or read them directly.")
    return wrapper


# ---- tools ----------------------------------------------------------------------

@_guard
def aa_overview() -> str:
    """Start here for any question about OCHA's anticipatory action (AA) portfolio: how many
    frameworks, where, how much money is pre-arranged, what was activated and released, how
    many people were reached or targeted. Returns the AA tracker's headline figures exactly
    as its map shows them (with the map's own notes), followed by the counting rules that
    any total built from the data files must follow. Read from the live tracker, the
    authoritative AA record; the answer gives the data snapshot time."""
    llms, n1 = _get("llms.txt")
    amap, n2 = _get("aa-map.md")
    snapshot, caveat, rules = _intro_parts(llms)
    secs = _sections(amap)
    headline = next((v for k, v in secs.items() if k.lower().startswith("headline figures")), "")
    title = next((k for k in secs if k.lower().startswith("headline figures")), "Headline figures")
    parts = [
        _header(snapshot, caveat, " ".join(n for n in (n1, n2) if n)),
        "",
        f"## {title}",
        headline or f"(No headline section found in {BASE}aa-map.md.)",
        "",
        "## " + (rules.splitlines()[0] if rules else "Counting rules"),
        "\n".join(rules.splitlines()[1:]) if rules else f"(See {BASE}llms.txt.)",
        "",
        "## Next",
        ("- One framework (trigger, versions, windows, activations, funding): "
         "aa_framework(country_iso3, hazard)."),
        ("- Tables (frameworks, versions, activations, prearranged-funding, cofinancing, funds): "
         "aa_data(file, country_iso3=…, hazard=…, year=…)."),
        "- Field meanings and vocabulary (lifecycle, layers, return periods…): aa_guide(section).",
        f"- The map itself: {BASE}",
    ]
    return "\n".join(parts)


def _norm_list(value: str) -> set[str]:
    return {v.strip().lower() for v in (value or "").split(",") if v.strip()}


# Common names → the tracker's hazard vocabulary (llms.txt § Vocabulary): a model asking
# for 'cyclone' must not conclude there are none because the file says 'storm'.
_HAZARD_ALIASES = {
    "cyclone": "storm", "cyclones": "storm", "tropical cyclone": "storm",
    "tropical-cyclone": "storm", "tropical_cyclone": "storm", "hurricane": "storm",
    "hurricanes": "storm", "typhoon": "storm", "typhoons": "storm", "storms": "storm",
    "flooding": "flood", "floods": "flood", "droughts": "drought", "dry spell": "drought",
}


def _hazards(value: str) -> set[str]:
    return {_HAZARD_ALIASES.get(h, h) for h in _norm_list(value)}


# aa-frameworks has no `layer` column; its `map_layers` lists the map layers a
# (country, hazard) pair is drawn on. Same names as the money files' `layer`, mapped.
_FRAMEWORK_LAYERS = {"current": "framework", "framework": "framework", "retired": "retired",
                     "non_framework": "adhoc", "non-framework": "adhoc", "adhoc": "adhoc",
                     "tech": "tech"}


def _map_layers(row: dict) -> set[str]:
    v = row.get("map_layers")
    items = v if isinstance(v, list) else str(v or "").replace(",", ";").split(";")
    return {str(x).strip().lower() for x in items if str(x).strip()}


def _row_year(file: str, row: dict) -> str:
    if file == "activations":
        return str(row.get("event_date") or "")[:4]
    if file in ("prearranged-funding", "cofinancing"):
        return str(row.get("year") or "")
    return ""


def _cell(v) -> str:
    if v is None:
        return ""
    if isinstance(v, (list, dict)):
        if isinstance(v, list) and all(not isinstance(x, (list, dict)) for x in v):
            return "; ".join("" if x is None else str(x) for x in v)
        return json.dumps(v, ensure_ascii=False)
    if isinstance(v, float) and v.is_integer():
        return str(int(v))
    return str(v)


@_guard
def aa_data(file: str, country_iso3: str = "", hazard: str = "", year: str = "",
            layer: str = "", columns: str = "", max_rows: int = 300) -> str:
    """Rows from one of the AA tracker's data files, filtered, as CSV, with the file's own
    description (which states how its figures may be added up). `file` is one of:
    'frameworks' (one row per country+hazard on the map: lifecycle, latest version,
    pre-arranged now, co-financing, people covered), 'versions' (every framework version:
    validity, trigger basis and indicators, document, return period, agencies),
    'activations' (every real activation since 2020 and the money it drew per fund),
    'prearranged-funding' (pre-arranged money per framework, year and fund: a STOCK),
    'cofinancing' (money from outside the OCHA-managed funds: a separate stock), 'funds'
    (fund codes). Filters (all optional, comma-separated values allowed): `country_iso3`
    (e.g. 'BGD,NPL'), `hazard` (drought, flood, storm, cholera…), `year` (activations: the
    event year; prearranged-funding/cofinancing: the year), `layer` (current, retired,
    non_framework; on 'frameworks' it matches the map layers a pair is drawn on, so
    layer='current' gives the frameworks the map's headline counts). `columns` keeps only
    the named columns. Read aa_overview()'s counting
    rules before totalling anything."""
    key = (file or "").strip().lower().replace("_", "-").removeprefix("aa-")
    key = key.removesuffix(".json").removesuffix(".csv")
    if key not in DATA_FILES:
        return f"Unknown file {file!r}. Options: {', '.join(DATA_FILES)}."
    doc, note = _get(DATA_FILES[key], parse=json.loads)
    cols: list[str] = list(doc.get("columns") or [])
    rows = doc.get("rows") or []
    if rows and isinstance(rows[0], list):  # tolerate a columnar layout
        rows = [dict(zip(cols, r)) for r in rows]
    if not cols and rows:
        cols = list(rows[0])

    isos, hazards, years, layers = (_norm_list(country_iso3), _hazards(hazard),
                                    _norm_list(year), _norm_list(layer))
    layer_col = "layer" if "layer" in cols else ("map_layers" if "map_layers" in cols else "")
    unsupported = []
    if years and key not in ("activations", "prearranged-funding", "cofinancing"):
        unsupported.append(f"year (no year column in {key})")
    if layers and not layer_col:
        unsupported.append(f"layer (no layer column in {key})")
    elif layers and layer_col == "map_layers":
        bad_layers = sorted(x for x in layers if x not in _FRAMEWORK_LAYERS)
        if bad_layers:
            unsupported.append(f"layer {', '.join(bad_layers)} (use current, retired, "
                               "non_framework or tech)")
        layers = {_FRAMEWORK_LAYERS[x] for x in layers if x in _FRAMEWORK_LAYERS}
    if hazards and "hazard" not in cols:
        unsupported.append(f"hazard (no hazard column in {key})")
    if unsupported:
        return f"Filter not available for {key!r}: {'; '.join(unsupported)}. Columns: {', '.join(cols)}."

    def keep(r: dict) -> bool:
        if isos and str(r.get("country_iso3") or "").lower() not in isos:
            return False
        if hazards and str(r.get("hazard") or "").lower() not in hazards:
            return False
        if years and _row_year(key, r) not in years:
            return False
        if not layers:
            return True
        if layer_col == "map_layers":
            return bool(_map_layers(r) & layers)
        return str(r.get("layer") or "").lower() in layers

    picked = [r for r in rows if keep(r)]
    hint = ""
    if not picked and rows:  # say what the file does hold, so "no rows" isn't read as "none"
        avail = []
        for col, on in (("country_iso3", isos), ("hazard", hazards), ("layer", layers and layer_col == "layer")):
            if on and col in cols:
                vals = sorted({str(r.get(col)) for r in rows if r.get(col) not in (None, "")})
                avail.append(f"{col}: {', '.join(vals)}")
        if years:
            avail.append("years: " + ", ".join(sorted({_row_year(key, r) for r in rows} - {""})))
        if avail:
            hint = "Values in this file — " + "; ".join(avail)
    want = [c.strip() for c in (columns or "").split(",") if c.strip()]
    bad = [c for c in want if c not in cols]
    if bad:
        return f"Unknown column(s) {', '.join(bad)} in {key!r}. Columns: {', '.join(cols)}."
    out_cols = want or cols
    max_rows = max(1, min(int(max_rows or 300), 2000))
    shown = picked[:max_rows]

    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(out_cols)
    for r in shown:
        w.writerow([_cell(r.get(c)) for c in out_cols])

    snapshot = doc.get("snapshot_at") or ""
    head = _header(f"Data snapshot {snapshot} UTC" if snapshot else "", doc.get("caveat") or "", note)
    filt = ", ".join(f"{k}={v}" for k, v in (("country_iso3", country_iso3), ("hazard", hazard),
                                               ("year", year), ("layer", layer)) if v)
    count = f"{len(picked)} of {len(rows)} row(s)" + (f" matching {filt}" if filt else "")
    if len(picked) > len(shown):
        count += f"; showing the first {len(shown)} (raise max_rows or filter more)"
    lines = [
        head,
        f"File: {BASE}{DATA_FILES[key]} (CSV: {BASE}{DATA_FILES[key][:-5]}.csv)",
        f"About this file: {doc.get('description') or ''}",
        "",
        count + ":",
        buf.getvalue().rstrip("\n"),
    ]
    if hint:
        lines += ["", hint]
    return "\n".join(lines)


_VERSION_BRIEF = ("v", "status", "valid_from", "valid_until", "doc_title", "doc_url")


@_guard
def aa_framework(country_iso3: str, hazard: str = "", version: str = "") -> str:
    """Everything the AA tracker's map shows for one country's OCHA anticipatory action
    framework(s), as JSON: lifecycle and status, pre-arranged money now and its split,
    co-financing, people covered, activations (date, window, money released per fund,
    people), learning documents, and the versions with their trigger tables (indicator,
    threshold, lead time, what each trigger releases), windows with budgets and backtests,
    funding, agencies and partners. `hazard` (drought, flood, storm, cholera…) narrows to
    one framework. By default the current version comes in full and earlier ones in brief;
    pass `version` ('2025-04-25') for one version in full, or 'all' for every version.
    Field meanings: aa_guide('map-data')."""
    iso = (country_iso3 or "").strip().upper()
    if not re.fullmatch(r"[A-Z]{3}", iso):
        return "country_iso3 must be an ISO 3166-1 alpha-3 code, e.g. 'BGD'."
    data, note = _get("aa-map-data.json", parse=json.loads)
    countries = data.get("countries") or {}
    c = countries.get(iso)
    if not c:
        return (f"{iso} is not on the AA tracker's map (no framework, activation or allocation "
                f"recorded). Countries on the map: {', '.join(sorted(countries))}.")
    fws = c.get("fws") or []
    hz = (hazard or "").strip().lower()
    hz = _HAZARD_ALIASES.get(hz, hz)
    if hz:
        fws = [f for f in fws if str(f.get("hazard") or "").lower() == hz]
        if not fws:
            have = sorted({str(f.get("hazard")) for f in c.get("fws") or []})
            return f"No {hz!r} framework for {iso} on the map. Hazards there: {', '.join(have)}."
    want = (version or "").strip()

    def shape(fw: dict) -> dict:
        fw = dict(fw)
        versions = fw.get("versions") or []
        cur = fw.get("current") or fw.get("latest")
        if want.lower() == "all":
            fw["versions"] = versions
        elif want:
            sel = [v for v in versions if str(v.get("v")) == want]
            fw["versions"] = sel
            if not sel:
                fw["versions_note"] = (f"no version {want!r}; versions: "
                                       + ", ".join(str(v.get("v")) for v in versions))
        else:
            fw["versions"] = [v if v.get("v") == cur else {k: v.get(k) for k in _VERSION_BRIEF}
                              for v in versions]
            if len(versions) > 1:
                fw["versions_note"] = (f"version {cur} in full, the others in brief; "
                                       "pass version='all' or a version id for more")
        return fw

    out = {"country_iso3": iso, "country": c.get("name"), "region": c.get("region"),
           "frameworks": [shape(f) for f in fws]}
    if not hz and c.get("subgrants"):
        out["subgrants"] = c.get("subgrants")
    snapshot = data.get("snapshot_at") or ""
    head = _header(f"Data snapshot {snapshot} UTC" if snapshot else "", data.get("caveat") or "", note)
    return "\n".join([
        head,
        (f"From {BASE}aa-map-data.json (the map's country panel for {iso}). Amounts in US "
         "dollars; pre-arranged figures follow the counting rules in aa_overview()."),
        "",
        json.dumps(out, ensure_ascii=False, separators=(",", ":"), default=str),
    ])


_GUIDE_ALIASES = {
    "counting-rules": "__rules__",
    "rules": "__rules__",
    "data-files": "Data files",
    "files": "Data files",
    "map-data": "The map's data",
    "fields": "The map's data",
    "vocabulary": "Vocabulary",
    "map": "The map",
    "related": "Related",
    "all": "__all__",
}


@_guard
def aa_guide(section: str = "counting-rules") -> str:
    """The AA tracker's own guide for programs and AI assistants (its llms.txt), by section:
    'counting-rules' (how figures may be added up — read before any total), 'vocabulary'
    (lifecycle, layers, return periods, fund codes, event types), 'data-files' (what each
    file holds, column by column), 'map-data' (every field of the per-framework data that
    aa_framework returns), 'related' (links), or 'all' (the whole guide, ~33 KB)."""
    llms, note = _get("llms.txt")
    key = _GUIDE_ALIASES.get((section or "").strip().lower(), (section or "").strip())
    snapshot, caveat, rules = _intro_parts(llms)
    head = _header(snapshot, caveat, note)
    if key == "__all__":
        return head + "\n\n" + llms
    if key == "__rules__":
        return head + "\n\n" + (rules or llms)
    secs = _sections(llms)
    match = next((k for k in secs if k and k.lower().startswith(key.lower())), None)
    if match is None:
        return (f"Unknown section {section!r}. Options: counting-rules, vocabulary, data-files, "
                "map-data, map, related, all.")
    return f"{head}\n\n## {match}\n{secs[match]}"


TOOLS = (aa_overview, aa_data, aa_framework, aa_guide)


def register(server) -> None:
    """Add the AA tracker tools to a FastMCP server (read-only, open-world: they fetch from
    the public tracker site)."""
    for fn in TOOLS:
        server.tool(fn, annotations={"readOnlyHint": True, "openWorldHint": True,
                                     "idempotentHint": True})
