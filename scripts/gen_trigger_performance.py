"""Generate triggers.md — the public trigger-statistics page — from the dev `aa` schema.

Joins the authoritative trigger data (per-window return period / probability / activation years /
budgets, computed in the `aa` views) with framework CONTEXT from the KB frontmatter (country name,
hazard, pre-arranged financing, real-activation flag). Output is a static MkDocs page (like
catalog.md / db-schema.md) — committed and served by GitHub Pages; no DB access at build time.

Auth: ocha-stratus get_engine(stage='dev') + DSCI_AZ_DB_DEV_* (+ PGSSLMODE=require).
Run:  python scripts/gen_trigger_performance.py
"""
import os, re, glob, sys
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "triggers.md"

ISO_NAME = {
 "AFG":"Afghanistan","BFA":"Burkina Faso","BGD":"Bangladesh","COD":"DR Congo","CUB":"Cuba",
 "ETH":"Ethiopia","FJI":"Fiji","GTM":"Guatemala","HND":"Honduras","HTI":"Haiti","KEN":"Kenya",
 "MDG":"Madagascar","MOZ":"Mozambique","MRT":"Mauritania","NER":"Niger","NGA":"Nigeria",
 "NPL":"Nepal","PHL":"Philippines","SLV":"El Salvador","TCD":"Chad","MMR":"Myanmar","VUT":"Vanuatu"}
HAZARD_LABEL = {"drought":"Drought","flood":"Flood","tropical-cyclone":"Tropical cyclone",
 "cholera":"Cholera","infectious-disease":"Infectious disease"}

# ---------------- KB frontmatter (context) ----------------
def parse_fm(path):
    t = path.read_text(encoding="utf-8"); m = re.match(r'^---\n(.*?)\n---', t, re.S)
    if not m: return None
    b = m.group(1)
    g = lambda k: (re.search(rf'^{k}:\s*(.+)$', b, re.M) or [None,""])[1].strip()
    fund = {}
    fm = re.search(r'^funding_by_source:\s*\{(.+?)\}', b, re.M)
    if fm:
        for k,v in re.findall(r'(\w+):\s*(\d+)', fm.group(1)): fund[k]=int(v)
    n_act = len(re.findall(r'^\s*-\s*\{', re.search(r'^activations:(.*?)(?=^\w)', b+"\nX:", re.M|re.S).group(1))) \
            if re.search(r'^activations:\s*\[.+\]|^activations:\s*\n\s*-', b, re.M) else 0
    pf = g("prearranged_funding_usd")
    return dict(framework=g("framework"), version=g("version").strip('"'), status=g("status"),
                hazard=g("hazard"), doc=g("framework_doc").strip('"'),
                prearranged=int(pf) if pf.isdigit() else None,
                funding=fund, n_activations=n_act)

def kb_meta():
    meta = {}   # (framework, version) -> fm
    for f in glob.glob(str(ROOT/"frameworks/*/*.md")):
        if f.endswith(("README.md","_TEMPLATE.md")): continue
        fm = parse_fm(Path(f))
        if fm and fm["framework"]: meta[(fm["framework"], fm["version"])] = fm
    return meta

def usd(n):
    if n is None: return "—"
    return f"${n/1e6:.1f}M" if n >= 1e5 else f"${n:,.0f}"

def pct(p):
    return f"{round(float(p)*100)}%" if p not in (None,"") else "—"

def rp_fmt(years):
    return f"{float(years):.1f} years" if years not in (None,"") else "—"

# ---------------- DB (trigger stats) ----------------
def fetch():
    os.environ.setdefault("PGSSLMODE", "require")
    if not os.environ.get("DSCI_AZ_DB_DEV_HOST") and os.environ.get("DS_AZ_DB_DEV_HOST"):
        os.environ["DSCI_AZ_DB_DEV_HOST"] = os.environ["DS_AZ_DB_DEV_HOST"]
    import ocha_stratus as stratus
    from sqlalchemy import text
    eng = stratus.get_engine(stage="dev")
    with eng.connect() as c:
        wins = list(c.execute(text("""
            select p.kb_framework, p.kb_version, p.country_iso3, p.window_name, p.all_in,
                   p.allocation_usd, p.analysis_start, p.analysis_end, p.n_activations,
                   coalesce(p.rp_reported, p.return_period)   as rp,
                   coalesce(p.prob_reported, p.activation_prob) as prob,
                   m.kb_status
            from aa.v_window_performance p
            join aa.framework_version_map m using (kb_framework, kb_version, country_iso3)
            order by p.kb_framework, p.kb_version, p.country_iso3, p.window_name""")))
        acts = defaultdict(list)
        for r in c.execute(text("""select kb_framework, kb_version, country_iso3, window_name, event_year
                                    from aa.simulated_activation order by event_year""")):
            acts[(r[0],r[1],r[2],r[3])].append(r[4])
        overall = {}
        for r in c.execute(text("""select f.kb_framework, f.kb_version, f.country_iso3,
                   coalesce(m.overall_rp_reported, f.overall_return_period)     as rp,
                   coalesce(m.overall_prob_reported, f.overall_activation_prob) as prob,
                   f.all_in, f.analysis_years
                   from aa.v_framework_performance f
                   join aa.framework_version_map m using (kb_framework, kb_version, country_iso3)""")):
            overall[(r[0],r[1],r[2])] = dict(rp=r[3], prob=r[4], all_in=r[5], years=r[6])
    return wins, acts, overall

def main():
    try:
        wins, acts, overall = fetch()
    except Exception as e:
        sys.exit(f"DB fetch failed ({type(e).__name__}: {e}). Need DSCI_AZ_DB_DEV_* + PGSSLMODE=require.")
    meta = kb_meta()

    # group windows by (framework, version, country) — only endorsed versions on the page
    groups = defaultdict(list)
    for w in wins:
        if w.kb_status != "endorsed": continue
        groups[(w.kb_framework, w.kb_version, w.country_iso3)].append(w)

    # one display entry per group, sorted by country name
    entries = []
    for key, ws in groups.items():
        fw, ver, ctry = key
        fm = meta.get((fw, ver), {})
        # financing: KB pre-arranged total, else sum of per-window allocations
        fin = fm.get("prearranged") or (sum(w.allocation_usd for w in ws if w.allocation_usd) or None)
        entries.append((ISO_NAME.get(ctry, ctry), fw, ver, ctry, ws, fm, fin))
    entries.sort(key=lambda e: (e[0], e[1]))

    L = ["---", "title: Trigger statistics", "hide:\n  - navigation", "---", "",
         "# Trigger statistics", "",
         "Published triggers, windows, and pre-arranged financing across the Centre for Humanitarian "
         "Data's Anticipatory Action portfolio. **🔴 flags frameworks that have activated.** "
         "Return periods and activation probabilities are the trigger statistics published in each "
         "framework document; activation years are the historical (backtested) years each trigger "
         "would have fired.", "",
         "!!! note inline end \"How to read\"",
         "    *Return period* = the average interval between activations. *Activation probability* "
         "= the chance the trigger fires in a given year. *Overall* = the chance **any** trigger in "
         "the framework fires.", ""]

    # ---- portfolio summary table ----
    L += ["## Portfolio summary", "",
          "| Framework | Hazard | Windows | Overall return period | Pre-arranged | |",
          "|---|---|---|---|---|:--:|"]
    for cname, fw, ver, ctry, ws, fm, fin in entries:
        ov = overall.get((fw, ver, ctry), {})
        haz = HAZARD_LABEL.get(fm.get("hazard",""), (fm.get("hazard","") or "").title())
        flag = "🔴" if fm.get("n_activations",0) else ""
        anchor = f"{fw}-{ctry}".lower()
        L.append(f"| [{cname} — {haz}](#{anchor}) | {haz} | {len(ws)} | "
                 f"{rp_fmt(ov.get('rp'))} ({pct(ov.get('prob'))}) | {usd(fin)} | {flag} |")
    L.append("")

    # ---- per-framework detail ----
    L += ["## Frameworks", ""]
    for cname, fw, ver, ctry, ws, fm, fin in entries:
        ov = overall.get((fw, ver, ctry), {})
        haz = HAZARD_LABEL.get(fm.get("hazard",""), (fm.get("hazard","") or "").title())
        flag = " 🔴" if fm.get("n_activations",0) else ""
        anchor = f"{fw}-{ctry}".lower()
        a0 = ws[0].analysis_start; a1 = ws[0].analysis_end
        period = f" · analysis {a0}–{a1}" if a0 and a1 else ""
        L += [f'<h3 id="{anchor}">{cname} — {haz}{flag}</h3>', "",
              f"*Endorsed {ver}{period}.*", ""]
        # financing
        fund = fm.get("funding") or {}
        by = " (" + ", ".join(f"{k} {usd(v)}" for k,v in fund.items()) + ")" if fund else ""
        allin = " · all-in (whole envelope releases on any trigger)" if ws[0].all_in else ""
        L += [f"**Pre-arranged financing:** {usd(fin)}{by}{allin}", ""]
        # trigger table
        split = not ws[0].all_in and any(w.allocation_usd for w in ws)
        head = "| Window | Return period | Activation probability | Years activated |"
        sep =  "|---|---|---|---|"
        if split:
            head = "| Window | Allocation | Return period | Activation probability | Years activated |"
            sep =  "|---|---|---|---|---|"
        L += [head, sep]
        for w in ws:
            yrs = ", ".join(str(y) for y in acts.get((fw,ver,ctry,w.window_name), [])) or "—"
            cells = [w.window_name, rp_fmt(w.rp), pct(w.prob), yrs]
            if split:
                cells = [w.window_name, usd(w.allocation_usd), rp_fmt(w.rp), pct(w.prob), yrs]
            L.append("| " + " | ".join(cells) + " |")
        # overall + link
        if ov.get("rp"):
            L += ["", f"**Overall:** activates about 1-in-{float(ov['rp']):.1f} years "
                      f"(~{pct(ov.get('prob'))} chance per year)."]
        if fm.get("doc"):
            L += [f"  ·  [Framework document]({fm['doc']}) · [KB page](frameworks/{fw}/{ver}.md)"]
        L.append("")

    L += ["---",
          f"*Generated from the `aa` trigger-performance schema by `scripts/gen_trigger_performance.py`. "
          f"{len(entries)} endorsed framework-versions.*", ""]
    OUT.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"Wrote {OUT.relative_to(ROOT)} — {len(entries)} endorsed framework-versions.")

if __name__ == "__main__":
    main()
