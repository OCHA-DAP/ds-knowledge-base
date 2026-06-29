"""Generate the standalone Anticipatory Action site shells (aa_index.html, aa_triggers.html).

The public-facing AA site lives at /anticipatory-action/ and is SEPARATE from the comprehensive
MkDocs repo mirror. It is two full-screen views — the status map and the trigger statistics — with
a shared top nav to move between them (and a link back to the Knowledge Base). Each shell is a thin
frame: a nav bar + an <iframe> of the existing self-contained page (the Leaflet map / the trigger
page), so the heavy generators are untouched.

site.yml assembles /anticipatory-action/ as:
  index.html    <- aa_index.html      (Status map view)
  triggers.html <- aa_triggers.html   (Trigger statistics view)
  map.html      <- index.html         (the Leaflet map page)
  stats.html    <- activations.html   (the trigger statistics page)

Static — no DB. Run: python scripts/gen_aa_site.py
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

CSS = """
*{box-sizing:border-box} html,body{margin:0;height:100%;background:#fafbfc;
  font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;}
.aanav{height:54px;background:#1a6bb5;display:flex;align-items:center;padding:0 18px;color:#fff;
  box-shadow:0 1px 4px rgba(0,0,0,.18);position:relative;z-index:5;}
.aanav .brand{font-weight:700;font-size:15px;margin-right:22px;white-space:nowrap;display:flex;align-items:center;gap:8px;}
.aanav .brand .dot{width:11px;height:11px;border-radius:50%;background:#fff;display:inline-block;}
.aanav a{color:#fff;text-decoration:none;font-size:14px;font-weight:600;padding:8px 15px;border-radius:8px;}
.aanav a:hover{background:rgba(255,255,255,.16);}
.aanav a.active{background:#fafbfc;color:#1a6bb5;}
.aanav .spacer{flex:1;}
.aanav a.ext{font-weight:500;opacity:.92;font-size:13px;}
.aaframe{border:0;width:100%;height:calc(100vh - 54px);display:block;}
"""

def shell(active, src, title):
    def cls(name): return ' class="active"' if name == active else ""
    return f"""<!DOCTYPE html><html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>OCHA Anticipatory Action — {title}</title><style>{CSS}</style></head><body>
<div class="aanav">
  <span class="brand"><span class="dot"></span>OCHA · Anticipatory Action</span>
  <a href="index.html"{cls('map')}>Status map</a>
  <a href="triggers.html"{cls('triggers')}>Trigger statistics</a>
  <span class="spacer"></span>
  <a class="ext" href="../" title="The full Data Science knowledge base">Knowledge Base ↗</a>
</div>
<iframe class="aaframe" src="{src}" title="{title}"></iframe>
</body></html>
"""

def main():
    (ROOT / "aa_index.html").write_text(shell("map", "map.html", "Status map"), encoding="utf-8")
    (ROOT / "aa_triggers.html").write_text(shell("triggers", "stats.html", "Trigger statistics"), encoding="utf-8")
    print("Wrote aa_index.html, aa_triggers.html")

if __name__ == "__main__":
    main()
