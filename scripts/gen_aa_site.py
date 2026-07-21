"""Generate the standalone Anticipatory Action site shells (aa_index.html, aa_triggers.html).

The public-facing AA site lives at /anticipatory-action/ — the only thing the repo publishes
to GitHub Pages (the KB itself is browsed on GitHub, D87). Layout (shared across both views):

    [ WIP banner ]
    [ "OCHA Anticipatory Action Frameworks" header — with the view nav inside it ]
    [ full-screen content: the status map / the trigger statistics ]

Each shell is a thin frame: the banner + header + nav, then an <iframe> of the existing
self-contained page (the Leaflet map / the trigger page). The shell HIDES the framed page's own
banner + header (injecting CSS into the same-origin iframe on load) so there's a single header,
and leaves the heavy generators (gen_public_site.py, gen_trigger_site.py) untouched.

site.yml assembles /anticipatory-action/ as:
  index.html <- aa_index.html (map view) · triggers.html <- aa_triggers.html (stats view)
  global.html <- aa_global_view.html (all-orgs view, D79 — direct-link only, no nav tab yet)
  map.html   <- index.html (Leaflet map) · stats.html    <- activations.html (trigger page)
  global-map.html <- aa_global.html (the cross-org map+table content page)

Static — no DB. Run: python scripts/gen_aa_site.py
"""
from pathlib import Path

import site_i18n as i18n
from site_i18n import T, TB

ROOT = Path(__file__).resolve().parent.parent

WIP_EN = ('⚠️ <b>Work in progress.</b> This site is in active development and is auto-generated from '
          'an internal knowledge base. Details may be incomplete, out of date, or inaccurate — treat '
          'figures and statuses as indicative, not authoritative.')
WIP = TB(WIP_EN)

CSS = """
*{box-sizing:border-box} html,body{height:100%;margin:0;}
body{display:flex;flex-direction:column;background:#fafbfc;
  font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;color:#222;}
.disclaimer{background:#fff4d6;border-bottom:1px solid #e6cf8f;color:#6b5310;font-size:13px;
  line-height:1.4;padding:9px 18px;text-align:center;}
.disclaimer b{color:#5a4408;}
header.aahead{background:#1a6bb5;color:#fff;padding:22px 24px 0;}
header.aahead .row{display:flex;align-items:center;justify-content:space-between;gap:16px;}
header.aahead h1{margin:0;font-size:23px;}
header.aahead .kb{color:#fff;text-decoration:none;font-size:13px;font-weight:500;opacity:.9;white-space:nowrap;}
header.aahead .kb:hover{opacity:1;text-decoration:underline;}
header.aahead nav{display:flex;gap:3px;margin-top:16px;}
header.aahead nav a{color:#fff;text-decoration:none;font-size:14px;font-weight:600;padding:9px 17px;border-radius:8px 8px 0 0;}
header.aahead nav a:hover{background:rgba(255,255,255,.16);}
header.aahead nav a.active{background:#fafbfc;color:#1a6bb5;}
.aaframe{flex:1;border:0;width:100%;display:block;background:#fafbfc;}
"""

# CSS injected into the framed page (same-origin) to drop its own banner + header (we provide them).
INJECT_MAP = (".disclaimer{display:none!important}header{display:none!important}"
              "main{padding-top:18px!important}")
# global page: drop its own header (the shell provides one).
INJECT_GLOBAL = ("header{display:none!important}")
# stats page: drop banner + header, and relax the sub-tab bar to a light strip under our blue header.
INJECT_STATS = (".disclaimer{display:none!important}header{display:none!important}"
                ".tabbar{background:#eef2f6!important;padding-top:8px!important}"
                ".tabbar button{background:#dde6ee!important;color:#1a6bb5!important}"
                ".tabbar button.active{background:#fff!important;color:#1a6bb5!important}"
                "main{padding-top:16px!important}")

def shell(active, src, title, inject):
    def cls(name): return ' class="active"' if name == active else ""
    title_fr = i18n.fr(title)
    return f"""<!DOCTYPE html><html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>OCHA Anticipatory Action Frameworks — {title}</title><style>{CSS}{i18n.LANG_CSS}</style></head><body>
<div class="disclaimer" role="note">{WIP}</div>
<header class="aahead">
  <div class="row">
    <h1>{T('OCHA Anticipatory Action Frameworks')}</h1>
    <span style="display:inline-flex;align-items:center;gap:14px">
      {i18n.TOGGLE_HTML}
      <a class="kb" href="https://github.com/OCHA-DAP/ds-knowledge-base" title="The full Data Science knowledge base">{T('Knowledge Base')} ↗</a>
    </span>
  </div>
  <nav>
    <a href="index.html"{cls('map')}>{T('Status map')}</a>
    <a href="triggers.html"{cls('triggers')}>{T('Trigger statistics')}</a>
    <a href="frameworks/index.html"{cls('frameworks')}>{T('Frameworks')}</a>
    {f'<a href="global.html" class="active">{T("All organisations")}</a>' if active == 'global' else ''}
  </nav>
</header>
<iframe class="aaframe" id="f" src="{src}" title="{title}"></iframe>
<script>{i18n.LANG_JS}
window.AA_TITLES = {{en: 'OCHA Anticipatory Action Frameworks — ' + {title!r},
                    fr: 'Cadres d’action anticipatoire de l’OCHA — ' + {title_fr!r}}};
(function(){{
  var f=document.getElementById('f');
  function inject(){{ try{{
    var d=f.contentDocument; if(!d||!d.head) return;
    if(d.getElementById('aa-embed')) return;
    var s=d.createElement('style'); s.id='aa-embed'; s.textContent={inject!r}; d.head.appendChild(s);
  }}catch(e){{}} }}
  f.addEventListener('load', inject);
  inject();   // in case it already loaded
  // keep the framed page's language in step with the shell (same-origin)
  function push(l){{ try{{ if (f.contentWindow && f.contentWindow.aaSetLang) f.contentWindow.aaSetLang(l); }}catch(e){{}} }}
  document.addEventListener('aalang', function(e){{ push(e.detail); }});
  f.addEventListener('load', function(){{
    var l=null; try{{l=localStorage.getItem('aa-lang');}}catch(e){{}}
    if (l) push(l);
  }});
}})();
</script>
</body></html>
"""

def main():
    (ROOT / "aa_index.html").write_text(
        shell("map", "map.html", "Status map", INJECT_MAP), encoding="utf-8")
    (ROOT / "aa_triggers.html").write_text(
        shell("triggers", "stats.html", "Trigger statistics", INJECT_STATS), encoding="utf-8")
    (ROOT / "aa_global_view.html").write_text(
        shell("global", "global-map.html", "All organisations", INJECT_GLOBAL), encoding="utf-8")
    print("Wrote aa_index.html, aa_triggers.html, aa_global_view.html")

if __name__ == "__main__":
    main()
