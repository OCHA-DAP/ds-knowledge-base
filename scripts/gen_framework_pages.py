"""Generate aa_frameworks/ — one public page per AA framework (country–hazard combo) + an index.

Each page assembles, in order:
  1. the basic facts shown on the AA map's Active-frameworks table (status, monitoring period,
     AOI, trigger windows, financing, target people, doc + repo links);
  2. the REAL activation history — every activation linking BOTH the public trigger announcement
     AND the CERF allocation behind it (cerf.un.org), with the allocation's amount approved and
     people targeted/reached from the OneGMS feed (via aa.cerf_allocation);
  3. the full per-window trigger statistics of the current version (return period, probability,
     backtested activation years — the aa schema);
  4. brief sections on previous framework versions (their stats + the real activations that
     fired under each).

Data: KB frontmatter (gen_public_site loaders — same current-version logic as the map),
scripts/aa_cerf_links.csv + aa.cerf_allocation (CERF), aa schema views (trigger stats via
gen_trigger_site.build_entries — includes gsheet-only PRIOR versions), and
load_aa_cerf.parse_activations (real activations, deduped + version-attributed).

Output is committed (like activations.html) and copied to site/anticipatory-action/frameworks/
by site.yml; refreshed by trigger-stats.yml (needs the dev DB).
Run: python scripts/gen_framework_pages.py   (DSCI_AZ_DB_DEV_* + PGSSLMODE=require)
"""
import csv, html, sys
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gen_public_site as gp          # frontmatter/windows loaders, current-version logic, fmt helpers
import gen_trigger_performance as tp  # kb_meta, usd/pct/rp_fmt, ISO_NAME, HAZARD_LABEL
import gen_trigger_site as ts         # build_entries() — per-version trigger stats (DB), winlabel
import load_aa_cerf as lac            # parse_activations() — real activations, version-attributed

ROOT = Path(__file__).resolve().parent.parent
OUTDIR = ROOT / "aa_frameworks"
LINKS_CSV = ROOT / "scripts" / "aa_cerf_links.csv"

E = lambda s: html.escape(str(s if s is not None else "—"))

WIP = ('⚠️ <b>Work in progress.</b> This site is in active development and is auto-generated from '
       'an internal knowledge base. Details may be incomplete, out of date, or inaccurate — treat '
       'figures and statuses as indicative, not authoritative.')

CSS = """
:root { --ocha:#1a6bb5; --ink:#222; --muted:#777; --line:#e3e6ea; --act:#e3322d; }
* { box-sizing:border-box; }
body { font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
       color:var(--ink); margin:0; background:#fafbfc; line-height:1.45; }
.disclaimer { background:#fff4d6; border-bottom:1px solid #e6cf8f; color:#6b5310; font-size:13px;
       line-height:1.4; padding:9px 18px; text-align:center; }
.disclaimer b { color:#5a4408; }
header.aahead { background:var(--ocha); color:#fff; padding:22px 24px 0; }
header.aahead .row { display:flex; align-items:center; justify-content:space-between; gap:16px; }
header.aahead h1 { margin:0; font-size:23px; }
header.aahead h1 a { color:#fff; text-decoration:none; }
header.aahead .kb { color:#fff; text-decoration:none; font-size:13px; font-weight:500; opacity:.9; white-space:nowrap; }
header.aahead .kb:hover { opacity:1; text-decoration:underline; }
header.aahead nav { display:flex; gap:3px; margin-top:16px; }
header.aahead nav a { color:#fff; text-decoration:none; font-size:14px; font-weight:600; padding:9px 17px; border-radius:8px 8px 0 0; }
header.aahead nav a:hover { background:rgba(255,255,255,.16); }
header.aahead nav a.active { background:#fafbfc; color:var(--ocha); }
main { max-width:1100px; margin:0 auto; padding:26px 24px 60px; }
a { color:var(--ocha); }
h2.pgtitle { margin:0 0 4px; font-size:26px; display:flex; align-items:center; gap:12px; flex-wrap:wrap; }
p.pgsub { color:var(--muted); font-size:14px; margin:0 0 22px; }
h3.sec { font-size:18px; margin:34px 0 4px; }
p.sub { color:var(--muted); font-size:13px; margin:0 0 12px; max-width:820px; }
.badge { display:inline-block; padding:3px 10px; border-radius:11px; font-size:12px; font-weight:600; vertical-align:middle; }
.b-endorsed { background:#e2f3e6; color:#1e7a37; }
.b-recently-triggered { background:#fde2e1; color:#b3261e; }
.b-development, .b-pre-development { background:#e4edf6; color:#1a6bb5; }
.b-expired, .b-retired, .b-superseded, .b-prior { background:#ececec; color:#666; }
/* facts grid */
table.facts { border-collapse:collapse; background:#fff; font-size:13.5px; width:100%;
       border-radius:8px; box-shadow:0 1px 3px rgba(0,0,0,.06); overflow:hidden; }
table.facts th { text-align:left; background:#f1f4f7; font-weight:600; width:190px;
       padding:8px 14px; border-bottom:1px solid var(--line); vertical-align:top; white-space:nowrap; }
table.facts td { padding:8px 14px; border-bottom:1px solid var(--line); vertical-align:top; }
table.facts tr:last-child th, table.facts tr:last-child td { border-bottom:0; }
.win { margin:2px 0; }
.win .wlabel { font-weight:600; }
/* generic data table (activation history, stats) */
.tw { overflow-x:auto; border-radius:8px; box-shadow:0 1px 3px rgba(0,0,0,.06); }
table.data { border-collapse:collapse; width:100%; background:#fff; font-size:13px; }
table.data th, table.data td { text-align:left; padding:7px 12px; border-bottom:1px solid var(--line); vertical-align:top; }
table.data th { background:#f1f4f7; font-weight:600; white-space:nowrap; }
table.data td.num { text-align:right; white-space:nowrap; }
table.data tr:hover td { background:#f6f9fc; }
table.data td.date { white-space:nowrap; font-weight:600; }
tr.noterow td { border-bottom:1px solid var(--line); background:#fbfcfe; color:#555; font-size:12px; padding-top:5px; }
tr.noterow + tr td { border-top:0; }
.chip { display:inline-block; background:#eef2f6; color:#456; border-radius:9px; padding:1px 8px; font-size:11px; font-weight:600; white-space:nowrap; }
.actdot { display:inline-block; width:8px; height:8px; border-radius:50%; background:var(--act); margin-right:6px; vertical-align:baseline; }
.fnote { color:var(--muted); font-size:12px; margin:8px 2px 0; max-width:900px; }
/* previous versions */
.pv { background:#fff; border-radius:8px; box-shadow:0 1px 3px rgba(0,0,0,.06); padding:14px 18px; margin:0 0 14px; }
.pv h4 { margin:0 0 6px; font-size:15px; display:flex; align-items:center; gap:10px; flex-wrap:wrap; }
.pv .meta { color:var(--muted); font-size:12.5px; margin:0 0 8px; }
.pv table.data { box-shadow:none; font-size:12.5px; }
.pv .tw { box-shadow:none; border:1px solid var(--line); }
footer { color:var(--muted); font-size:12px; padding:26px; text-align:center; }
"""


def head(title, *, depth=1, active="frameworks"):
    """Shared blue header. depth = how many levels below /anticipatory-action/ the page sits."""
    up = "../" * depth
    def cls(n): return ' class="active"' if n == active else ""
    return f"""<!DOCTYPE html><html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{E(title)} — OCHA Anticipatory Action</title><style>{CSS}</style></head><body>
<div class="disclaimer" role="note">{WIP}</div>
<header class="aahead">
  <div class="row">
    <h1><a href="{up}index.html">OCHA Anticipatory Action Frameworks</a></h1>
    <a class="kb" href="{up}../" title="The full Data Science knowledge base">Knowledge Base ↗</a>
  </div>
  <nav>
    <a href="{up}index.html"{cls('map')}>Status map</a>
    <a href="{up}triggers.html"{cls('triggers')}>Trigger statistics</a>
    <a href="{up}frameworks/index.html"{cls('frameworks')}>Frameworks</a>
  </nav>
</header>
<main>"""

FOOT = ('</main><footer>Generated from the OCHA CHD Data Science knowledge base and the CERF '
        'OneGMS allocation feed by <code>scripts/gen_framework_pages.py</code>.</footer></body></html>')


# ---------------- data ----------------

def load_links():
    """(framework, event_date) -> [(application_code, flag, note)]; plus the NO_CERF set."""
    links, no_cerf = defaultdict(list), set()
    for r in csv.DictReader(open(LINKS_CSV)):
        if not r["kb_framework"]:
            continue                                   # ADHOC_AA rows aren't framework activations
        key = (r["kb_framework"], r["event_date"])
        code = (r.get("application_code") or "").strip()
        if code:
            links[key].append((code, r.get("flag") or "", r.get("note") or ""))
        else:
            no_cerf.add(key)
    return links, no_cerf


def fetch_cerf(codes):
    """application_code -> allocation facts, from aa.cerf_allocation (loaded by load_aa_cerf.py)."""
    if not codes:
        return {}
    import os
    os.environ.setdefault("PGSSLMODE", "require")
    if not os.environ.get("DSCI_AZ_DB_DEV_HOST") and os.environ.get("DS_AZ_DB_DEV_HOST"):
        os.environ["DSCI_AZ_DB_DEV_HOST"] = os.environ["DS_AZ_DB_DEV_HOST"]
    import ocha_stratus as stratus
    from sqlalchemy import text
    eng = stratus.get_engine(stage="dev")
    with eng.connect() as c:
        rows = c.execute(text(
            """select application_code, year, country_iso3, title, amount_approved,
                      individuals_planned, individuals_reached, allocation_status,
                      erc_endorsement_date
               from aa.cerf_allocation where application_code = any(:codes)"""),
            {"codes": list(codes)})
        return {r.application_code: r for r in rows}


def cerf_url(row):
    return f"https://cerf.un.org/what-we-do/allocation/{row.year}/summary/{row.application_code}"


def people(v, status):
    """Planned/reached display: OneGMS shows 0 until the country office reports (~9 months)."""
    if v is None or (v == 0 and status in ("Under Implementation", "Under Review")):
        return '<span style="color:var(--muted)">not yet reported</span>'
    return f"{v:,}"


# ---------------- sections ----------------

def facts_html(fm, windows, acts):
    disp = gp.display_status(str(fm.get("status", "")), acts, fm.get("version"), fm.get("valid_until"))
    rows = []
    def row(label, value_html):
        rows.append(f"<tr><th>{E(label)}</th><td>{value_html}</td></tr>")
    ents = gp.entries(fm)
    multi = len(ents) > 1
    row("Country", E(", ".join(gp.cname(e["iso3"]) for e in ents)))
    row("Hazard", E(tp.HAZARD_LABEL.get(fm.get("hazard", ""), str(fm.get("hazard", "")).title())))
    mp = fm.get("monitoring_period") or {}
    note = f' <span style="color:var(--muted)">({E(mp.get("note"))})</span>' if mp.get("note") else ""
    row("Monitoring period", E(gp.fmt_months(mp.get("months"))) + note)
    if multi:
        row("Area of interest", "<br>".join(f"<b>{E(gp.cname(e['iso3']))}:</b> {E(e['aoi'])}" for e in ents))
    else:
        row("Area of interest", E(ents[0]["aoi"]))
    row("Current version", f'{E(fm.get("version"))}'
        + (f' · valid until {E(fm.get("valid_until"))}' if fm.get("valid_until") else ""))
    if windows:
        row("Trigger windows", "".join(
            f'<div class="win"><span class="wlabel">{E(w["window"])}</span> '
            f'{E(": ".join(p for p in (w["indicator"], w["threshold"]) if p))}</div>' for w in windows))
    fund = fm.get("funding_by_source") or {}
    by = " (" + ", ".join(f"{E(k)} {tp.usd(v)}" for k, v in fund.items()) + ")" if fund else ""
    row("Pre-arranged financing", E(tp.usd(fm.get("prearranged_funding_usd"))) + by)
    if fm.get("target_people"):
        row("Target people", f'{int(fm["target_people"]):,}')
    if str(fm.get("framework_doc") or "").startswith("http"):
        row("Framework document", f'<a href="{E(fm["framework_doc"])}" target="_blank" rel="noopener">'
            f'{E(fm.get("framework_doc_date") or "document")} ↗</a>')
    repo = gp.repo_cell(fm)
    if repo != "—":
        row("Code repository", repo)
    dev_caveat = ""
    if fm.get("status") in gp.DEV_STATUSES:
        dev_caveat = ('<p class="sub" style="margin:0 0 12px">🛠 The current version of this framework '
                      'is an in-development redesign — not yet endorsed. Details below describe the '
                      'design being built; the last endorsed design is under <a href="#prev">previous '
                      'versions</a>.</p>')
    return (f'<h2 class="pgtitle">{E(", ".join(gp.cname(e["iso3"]) for e in ents))} — '
            f'{E(tp.HAZARD_LABEL.get(fm.get("hazard",""), str(fm.get("hazard","")).title()))} '
            f'<span class="badge b-{E(disp)}">{E(gp.status_label(disp))}</span></h2>'
            f'<p class="pgsub">Anticipatory action framework <code>{E(fm.get("framework"))}</code></p>'
            f'{dev_caveat}'
            f'<table class="facts"><tbody>{"".join(rows)}</tbody></table>')


def activations_html(fw, acts, links, no_cerf, cerf):
    """Real-activation history: announcement link + CERF allocation link(s) + people reached."""
    mine = sorted((a for a in acts if a["kb_framework"] == fw),
                  key=lambda a: a["event_date"], reverse=True)
    if not mine:
        return ('<h3 class="sec">Activation history</h3>'
                '<p class="sub">This framework has not activated.</p>')
    shared = False
    body = []
    for a in mine:
        key = (fw, a["event_date"])
        codes = links.get(key, [])
        ann = (f'<a href="{E(a["url"])}" target="_blank" rel="noopener">announcement ↗</a>'
               if str(a.get("url") or "").startswith("http") else "—")
        win = E(a.get("window_name"))
        if not a.get("full_activation", True):
            win += ' <span class="chip">partial</span>'
        date_cell = f'<span class="actdot"></span>{E(a["event_date"])}'
        n = max(len(codes), 1)
        first_cells = (f'<td class="date" rowspan="{n}">{date_cell}</td>'
                       f'<td rowspan="{n}">{win}</td><td rowspan="{n}">{ann}</td>')
        if not codes:
            src = "non-CERF" if key in no_cerf else "—"
            body.append(f"<tr>{first_cells}<td>{E(src)}</td>"
                        f'<td class="num">—</td><td class="num">—</td><td class="num">—</td></tr>')
        for i, (code, flag, lnote) in enumerate(codes):
            r = cerf.get(code)
            mark = ""
            if flag == "SHARED_APP":
                shared, mark = True, " †"
            alloc = (f'<a href="{E(cerf_url(r))}" target="_blank" rel="noopener" '
                     f'title="{E(lnote or (r.title if r else code))}">{E(code)} ↗</a>{mark}') if r else E(code)
            cells = (f"<td>{alloc}</td>"
                     f'<td class="num">{E(tp.usd(float(r.amount_approved)) if r and r.amount_approved else "—")}</td>'
                     f'<td class="num">{people(r.individuals_planned, r.allocation_status) if r else "—"}</td>'
                     f'<td class="num">{people(r.individuals_reached, r.allocation_status) if r else "—"}</td>')
            body.append(f"<tr>{first_cells if i == 0 else ''}{cells}</tr>")
        if a.get("note"):
            body.append(f'<tr class="noterow"><td colspan="7">{E(a["note"])}</td></tr>')
    foot = ('<p class="fnote">† one CERF application funded more than one activation (phases or '
            'windows) — its totals appear on each linked row; don\'t sum them.</p>') if shared else ""
    return ('<h3 class="sec">Activation history</h3>'
            '<p class="sub">Real activations of this framework: the public trigger announcement and '
            'the CERF allocation that funded the response, with the people targeted and reached that '
            'CERF reports for the allocation (reported ~9 months after disbursement).</p>'
            '<div class="tw"><table class="data"><thead><tr><th>Date</th><th>Window</th>'
            '<th>Announcement</th><th>CERF allocation</th><th class="num">CERF approved</th>'
            '<th class="num">People targeted</th><th class="num">People reached</th></tr></thead>'
            f'<tbody>{"".join(body)}</tbody></table></div>{foot}')


def stats_table(e):
    """Per-window trigger statistics table for one ts entry (framework-version-country)."""
    rows = []
    split = not e["all_in"] and any(w.allocation_usd for w in e["windows"])
    for w in e["windows"]:
        yrs = ", ".join(str(y) for y in e["acts"].get((e["fw"], e["ver"], e["ctry"], w.window_name), [])) or "—"
        cells = [f"<td>{E(ts.winlabel(w.window_name))}</td>"]
        if split:
            cells.append(f'<td class="num">{E(tp.usd(w.allocation_usd))}</td>')
        cells += [f'<td class="num">{E(tp.rp_fmt(w.rp))}</td>',
                  f'<td class="num">{E(tp.pct(w.prob))}</td>', f"<td>{E(yrs)}</td>"]
        rows.append("<tr>" + "".join(cells) + "</tr>")
    ov = e["overall"]
    span = 5 if split else 4
    if ov.get("rp"):
        rows.append(f'<tr><td colspan="{span - 3}"><b>Overall</b> (any window)</td>'
                    f'<td class="num"><b>{E(tp.rp_fmt(ov["rp"]))}</b></td>'
                    f'<td class="num"><b>{E(tp.pct(ov.get("prob")))}</b></td>'
                    f'<td></td></tr>')
    head = ["Window"] + (["Allocation"] if split else []) + ["Return period", "Probability", "Backtested activation years"]
    ths = "".join(f"<th{' class=num' if h != 'Window' and 'years' not in h else ''}>{E(h)}</th>" for h in head)
    ana = f'Analysis period {e["a0"]}–{e["a1"]}. ' if e["a0"] and e["a1"] else ""
    allin = "All-in: the whole envelope releases on any trigger. " if e["all_in"] else \
            "Split funding: each window has its own budget and fires independently. " if split else ""
    return (f'<p class="sub">{E(ana + allin)}Backtested years are when each trigger '
            f'<i>would have</i> fired in the historical record — not real activations.</p>'
            f'<div class="tw"><table class="data"><thead><tr>{ths}</tr></thead>'
            f'<tbody>{"".join(rows)}</tbody></table></div>')


def current_stats_html(fw, ts_by_fw):
    cur = [e for e in ts_by_fw.get(fw, []) if e["current"]]
    out = ['<h3 class="sec">Trigger statistics (current version)</h3>']
    if not cur:
        out.append('<p class="sub">No published trigger statistics for this framework yet.</p>')
    for e in cur:
        if len(cur) > 1:
            out.append(f'<h4 style="margin:14px 0 4px">{E(e["name"])}</h4>')
        out.append(stats_table(e))
    return "".join(out)


def previous_html(fw, versions, cur_ver, ts_by_fw, acts):
    """Brief blocks for non-current versions: KB pages + DB-only prior versions, newest first."""
    meta = {}
    for _, fm, _w in versions:                        # KB pages for this framework
        v = str(fm.get("version"))
        if v != cur_ver:
            meta[v] = fm
    ts_prev = defaultdict(list)
    for e in ts_by_fw.get(fw, []):
        if not e["current"] and e["ver"] != cur_ver:
            ts_prev[e["ver"]].append(e)
    all_vers = sorted(set(meta) | set(ts_prev), reverse=True)
    all_vers = [v for v in all_vers if (meta.get(v, {}).get("status") not in gp.DEV_STATUSES)]
    if not all_vers:
        return ""
    blocks = []
    for v in all_vers:
        fm = meta.get(v, {})
        status = fm.get("status") or (ts_prev[v][0]["status"] if ts_prev.get(v) else "prior")
        bits = []
        if str(fm.get("framework_doc") or "").startswith("http"):
            bits.append(f'<a href="{E(fm["framework_doc"])}" target="_blank" rel="noopener">framework document ↗</a>')
        if fm.get("prearranged_funding_usd"):
            bits.append(f'pre-arranged {tp.usd(fm["prearranged_funding_usd"])}')
        vacts = [a for a in acts if a["kb_framework"] == fw and str(a.get("kb_version")) == str(v)]
        if vacts:
            bits.append("activated " + ", ".join(a["event_date"] for a in sorted(vacts, key=lambda a: a["event_date"])))
        meta_line = f'<p class="meta">{" · ".join(bits)}</p>' if bits else ""
        vents = ts_prev.get(v, [])
        tables = "".join(
            (f'<h5 style="margin:12px 0 4px">{E(e["name"])}</h5>' if len(vents) > 1 else "") + stats_table(e)
            for e in vents)
        blocks.append(f'<div class="pv"><h4>{E(v)} <span class="badge b-{E(status)}">'
                      f'{E(gp.status_label(status))}</span></h4>{meta_line}{tables}</div>')
    return ('<h3 class="sec" id="prev">Previous versions</h3>'
            '<p class="sub">Earlier versions of this framework. Real activations listed here fired '
            'under that version\'s trigger design (details in the activation history above).</p>'
            + "".join(blocks))


def dev_note(versions, cur_ver):
    devs = [str(fm.get("version")) for _, fm, _w in versions
            if fm.get("status") in gp.DEV_STATUSES and str(fm.get("version")) != cur_ver]
    if not devs:
        return ""
    return (f'<p class="sub" style="margin-top:10px">🛠 A revised version of this framework is in '
            f'development ({E(", ".join(sorted(devs)))}).</p>')


# ---------------- index page ----------------

def index_html(records):
    rows = []
    for r in sorted(records, key=lambda r: (r["country"], r["hazard"])):
        acts = (f'<span class="actdot"></span>{r["n_acts"]} ({E(r["latest_act"])})'
                if r["n_acts"] else "—")
        reached = f'{r["reached"]:,}' if r["reached"] else "—"
        rows.append(f'<tr><td><a href="{E(r["fw"])}.html">{E(r["country"])}</a></td>'
                    f'<td>{E(r["haz_label"])}</td>'
                    f'<td><span class="badge b-{E(r["disp"])}">{E(gp.status_label(r["disp"]))}</span></td>'
                    f'<td>{acts}</td><td class="num">{E(tp.usd(r["fin"]))}</td>'
                    f'<td class="num">{E(tp.usd(r["cerf_total"]) if r["cerf_total"] else "—")}</td>'
                    f'<td class="num">{reached}</td></tr>')
    return (head("Frameworks", depth=1, active="frameworks")
            + '<h2 class="pgtitle">Frameworks</h2>'
            '<p class="pgsub">One page per anticipatory action framework: status, triggers, real '
            'activations, and the CERF allocations behind them.</p>'
            '<div class="tw"><table class="data"><thead><tr><th>Country</th><th>Hazard</th>'
            '<th>Status</th><th>Activations</th><th class="num">Pre-arranged</th>'
            '<th class="num">CERF allocated (activations)</th><th class="num">People reached</th>'
            '</tr></thead><tbody>' + "".join(rows) + "</tbody></table></div>"
            '<p class="fnote">CERF allocated / people reached sum the CERF allocations linked to '
            'this framework\'s real activations (shared applications counted once).</p>' + FOOT)


# ---------------- main ----------------

def main():
    pages = gp.load_pages()
    current = gp.current_versions(pages)
    acts = lac.parse_activations(ROOT / "frameworks")
    links, no_cerf = load_links()
    cerf = fetch_cerf({c for v in links.values() for c, _f, _n in v})
    entries = ts.build_entries()
    ts_by_fw = defaultdict(list)
    for e in entries:
        ts_by_fw[e["fw"]].append(e)
    by_fwk = defaultdict(list)
    for rec in pages:
        by_fwk[rec[1].get("framework", rec[0].parent.name)].append(rec)

    OUTDIR.mkdir(exist_ok=True)
    index_records = []
    for path, fm, windows in sorted(current, key=lambda r: str(r[1].get("framework"))):
        fw = fm.get("framework") or path.parent.name
        fw_acts = [a for a in fm.get("activations") or [] if isinstance(a, dict)]
        page = (head(f"{', '.join(gp.cname(e['iso3']) for e in gp.entries(fm))} — "
                     f"{tp.HAZARD_LABEL.get(fm.get('hazard',''), str(fm.get('hazard','')).title())}")
                + facts_html(fm, windows, fw_acts)
                + dev_note(by_fwk[fw], str(fm.get("version")))
                + activations_html(fw, acts, links, no_cerf, cerf)
                + current_stats_html(fw, ts_by_fw)
                + previous_html(fw, by_fwk[fw], str(fm.get("version")), ts_by_fw, acts)
                + FOOT)
        (OUTDIR / f"{fw}.html").write_text(page, encoding="utf-8")

        my_codes = {c for (f, d), v in links.items() if f == fw for c, _f, _n in v}
        my_rows = [cerf[c] for c in my_codes if c in cerf]
        reached = sum(r.individuals_reached or 0 for r in my_rows)
        ents = gp.entries(fm)
        index_records.append(dict(
            fw=fw, country=", ".join(gp.cname(e["iso3"]) for e in ents),
            hazard=fm.get("hazard", ""),
            haz_label=tp.HAZARD_LABEL.get(fm.get("hazard", ""), str(fm.get("hazard", "")).title()),
            disp=gp.display_status(str(fm.get("status", "")), fw_acts, fm.get("version"), fm.get("valid_until")),
            n_acts=len({a["event_date"] for a in acts if a["kb_framework"] == fw}),
            latest_act=max((a["event_date"] for a in acts if a["kb_framework"] == fw), default=""),
            fin=fm.get("prearranged_funding_usd"),
            cerf_total=sum(float(r.amount_approved or 0) for r in my_rows) or None,
            reached=reached))
    (OUTDIR / "index.html").write_text(index_html(index_records), encoding="utf-8")
    print(f"Wrote {len(index_records)} framework pages + index to {OUTDIR.relative_to(ROOT)}/")


if __name__ == "__main__":
    main()
