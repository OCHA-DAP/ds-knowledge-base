"""Generate the Anticipatory Action site shell (aa_global_view.html).

What the KB publishes under /anticipatory-action/ is now ONLY the cross-organisation page
(D79). The OCHA portfolio views this shell used to frame — the status map, the trigger
statistics and the per-framework pages — were retired in favour of the ds-aa-tracking site
(D110), and site.yml serves redirects at their old URLs. Layout:

    [ WIP banner ]
    [ "Anticipatory Action Frameworks — all organisations" header, with a link to the
      OCHA portfolio tracking site ]
    [ full-screen content: the cross-org map + table ]

The shell is a thin frame: banner + header, then an <iframe> of the self-contained
aa_global.html (gen_global_site.py). It HIDES the framed page's own header (injecting CSS
into the same-origin iframe on load) so there's a single header.

site.yml assembles /anticipatory-action/ as:
  global.html     <- aa_global_view.html (this shell)
  global-map.html <- aa_global.html (the cross-org map+table content page)
  index.html / map.html / triggers.html / stats.html / frameworks/ <- redirects to ds-aa-tracking

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

# CSS injected into the framed page (same-origin) to drop its own header (the shell provides one).
INJECT_GLOBAL = ("header{display:none!important}")

TRACKING_URL = "https://ocha-dap.github.io/ds-aa-tracking/"

def shell(src, title, inject):
    title_fr = i18n.fr(title)
    return f"""<!DOCTYPE html><html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Anticipatory Action Frameworks — {title}</title><style>{CSS}{i18n.LANG_CSS}</style></head><body>
<div class="disclaimer" role="note">{WIP}</div>
<header class="aahead">
  <div class="row">
    <h1>{T('Anticipatory Action Frameworks')}</h1>
    <span style="display:inline-flex;align-items:center;gap:14px">
      {i18n.TOGGLE_HTML}
      <a class="kb" href="{TRACKING_URL}" title="The OCHA portfolio: status map, framework pages, activations and trigger statistics (password-protected)">{T('OCHA portfolio tracking')} ↗</a>
      <a class="kb" href="../" title="Every Data Science dashboard, app and analysis — the team hub (D103)">{T('All team dashboards')}</a>
      <a class="kb" href="https://github.com/OCHA-DAP/ds-knowledge-base" title="The full Data Science knowledge base">{T('Knowledge Base')} ↗</a>
    </span>
  </div>
  <nav>
    <a href="global.html" class="active">{T("All organisations")}</a>
  </nav>
</header>
<iframe class="aaframe" id="f" src="{src}" title="{title}"></iframe>
<script>{i18n.LANG_JS}
window.AA_TITLES = {{en: 'Anticipatory Action Frameworks — ' + {title!r},
                    fr: 'Cadres d’action anticipatoire — ' + {title_fr!r}}};
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
    (ROOT / "aa_global_view.html").write_text(
        shell("global-map.html", "All organisations", INJECT_GLOBAL), encoding="utf-8")
    print("Wrote aa_global_view.html")

if __name__ == "__main__":
    main()
