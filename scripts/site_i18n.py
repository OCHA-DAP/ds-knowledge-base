"""EN/FR i18n for the public AA site (status map · trigger stats · framework pages).

One mechanism, used by gen_aa_site.py / gen_public_site.py / gen_trigger_site.py /
gen_framework_pages.py:

  * `T(en)` / `T(en, fr)` — a plain-text string as a toggle-aware <span class="tr">
    carrying both languages in data attributes; the client JS swaps textContent.
    Sorting/filtering (which read textContent) therefore always see ONE language.
  * `TB(en_html, fr_html)` — an HTML-bearing block as a dual <span class="lv">;
    CSS shows the active language. Use when the string contains links/markup.
  * `FR` — the single EN → FR table for every fixed UI string. `fr(en)` looks a
    string up, falls back to English, and records the miss (printed at exit) so
    an untranslated string is loud, not silent.
  * `LANG_CSS`, `LANG_JS`, `TOGGLE_HTML` — the shared toggle plumbing each page
    embeds. Language choice persists in localStorage (`aa-lang`, same-origin =
    shared across the whole AA site); pages fire an `aalang` event so
    page-specific JS (map callouts, legend, month cells) re-renders.

The FRENCH TERMINOLOGY follows the team's own published framework documents
(the francophone frameworks — Chad, Niger, Burkina Faso, DRC, Madagascar,
Haiti — have French bodies and bilingual executive summaries); see the PR that
introduced this file for the glossary derivation. Keep new strings consistent
with those docs (e.g. "déclencheur" for trigger, "activation" for activation,
"période de retour" for return period, "action anticipatoire" as CERF/OCHA use).

Data-derived free text (trigger indicator/threshold prose, activation notes,
AOI lists, window names quoted from documents) is NOT translated — it renders
in the source language. Only fixed UI strings and controlled vocabularies
(statuses, hazards, months, country names) are.
"""
from __future__ import annotations

import atexit
import html
import re

# ---------------------------------------------------------------------------
# controlled vocabularies
# ---------------------------------------------------------------------------

# iso3 -> French country name (exonyms as used in the French framework docs / UN French)
COUNTRY_FR = {
    "AFG": "Afghanistan", "BFA": "Burkina Faso", "BGD": "Bangladesh",
    "COD": "RD Congo", "CUB": "Cuba", "ETH": "Éthiopie", "FJI": "Fidji",
    "GTM": "Guatemala", "HND": "Honduras", "HTI": "Haïti", "KEN": "Kenya",
    "MDG": "Madagascar", "MMR": "Myanmar", "MOZ": "Mozambique",
    "MRT": "Mauritanie", "MWI": "Malawi", "NER": "Niger", "NGA": "Nigéria",
    "NIC": "Nicaragua", "NPL": "Népal", "PHL": "Philippines", "PLW": "Palaos",
    "SLV": "El Salvador", "SOM": "Somalie", "SSD": "Soudan du Sud",
    "TCD": "Tchad", "VUT": "Vanuatu", "YEM": "Yémen",
}

# hazard slug -> French label (per the framework docs: sécheresse, inondations,
# cyclone tropical, choléra)
HAZARD_FR = {
    "drought": "Sécheresse", "flood": "Inondations",
    "tropical-cyclone": "Cyclone tropical", "cholera": "Choléra",
    "infectious-disease": "Maladies infectieuses", "plague": "Peste",
}

# computed display status -> French label ("endorsed" is shown publicly as
# Active/Actif; keep in sync with gen_public_site.STATUS_LABEL)
STATUS_FR = {
    "endorsed": "Actif", "recently-triggered": "Récemment déclenché",
    "expired": "Expiré", "development": "En développement",
    "pre-development": "En pré-développement", "superseded": "Remplacé",
    "retired": "Retiré", "triggered": "Déclenché", "prior": "Version antérieure",
}

MONTH_ABBR_FR = ["", "janv", "févr", "mars", "avr", "mai", "juin",
                 "juil", "août", "sept", "oct", "nov", "déc"]
MONTH_FULL_FR = ["", "janvier", "février", "mars", "avril", "mai", "juin",
                 "juillet", "août", "septembre", "octobre", "novembre", "décembre"]

# ---------------------------------------------------------------------------
# fixed UI strings — filled from the framework-doc glossary
# ---------------------------------------------------------------------------

FR: dict[str, str] = {
    # ---- shared chrome ----
    'OCHA Anticipatory Action Frameworks': 'Cadres d’action anticipatoire de l’OCHA',
    'Knowledge Base': 'Base de connaissances',
    'Status map': 'Carte des statuts',
    'Trigger statistics': 'Statistiques de déclenchement',
    'Frameworks': 'Cadres',
    'All organisations': 'Toutes les organisations',
    '⚠️ <b>Work in progress.</b> This site is in active development and is auto-generated from '
    'an internal knowledge base. Details may be incomplete, out of date, or inaccurate — treat '
    'figures and statuses as indicative, not authoritative.':
        '⚠️ <b>Travail en cours.</b> Ce site est en cours de développement et est généré '
        'automatiquement à partir d’une base de connaissances interne. Les détails peuvent être '
        'incomplets, obsolètes ou inexacts — considérez les chiffres et les statuts comme '
        'indicatifs, sans valeur officielle.',
    '⚠️ <b>Work in progress.</b> Auto-generated from an internal knowledge base; figures are '
    'indicative, not authoritative.':
        '⚠️ <b>Travail en cours.</b> Généré automatiquement à partir d’une base de connaissances '
        'interne ; les chiffres sont indicatifs, sans valeur officielle.',

    # ---- status map page ----
    "Published triggers, windows, and pre-arranged financing across the Centre for Humanitarian "
    "Data's AA portfolio. Red markers flag frameworks that have activated.":
        'Déclencheurs publiés, fenêtres de déclenchement et financements pré-arrangés du '
        'portefeuille d’action anticipatoire du Centre de données humanitaires. Les marqueurs '
        'rouges signalent les cadres qui se sont activés.',
    'Current version of each framework. Pin colour = status; each red dot = one past activation. '
    'Shaded countries have at least one framework. Click a pin for detail (activation dates link '
    'to the announcement where one exists).':
        'Version actuelle de chaque cadre. Couleur de l’épingle = statut ; chaque point rouge = '
        'une activation passée. Les pays ombrés comptent au moins un cadre. Cliquez sur une '
        'épingle pour le détail (les dates d’activation renvoient à l’annonce lorsqu’elle existe).',
    'Current version of each operational framework; multi-country frameworks are split to one row '
    'per country. Click a column header to sort; type in the per-column boxes to filter.':
        'Version actuelle de chaque cadre opérationnel ; les cadres multi-pays sont répartis en '
        'une ligne par pays. Cliquez sur un en-tête de colonne pour trier ; tapez dans les cases '
        'de chaque colonne pour filtrer.',
    'Every ingested version, including superseded and retired.':
        'Toutes les versions ingérées, y compris remplacées et retirées.',
    'Map': 'Carte',
    'Active frameworks': 'Cadres actifs',
    'All versions': 'Toutes les versions',
    'Show full version history': 'Afficher l’historique complet des versions',
    'Country': 'Pays',
    'Hazard': 'Aléa',
    'Monitoring': 'Suivi',
    'AOI': 'Zone d’intérêt',
    'Status': 'Statut',
    'Version': 'Version',
    'Activations': 'Activations',
    'Trigger (per window)': 'Déclencheur (par fenêtre)',
    'Pre-arranged': 'Pré-arrangé',
    'Target people': 'Personnes ciblées',
    'Framework doc': 'Document du cadre',
    '(endorsed date)': '(date d’approbation)',
    'Repo': 'Dépôt',
    'Supersedes': 'Remplace',
    'see framework doc': 'voir le document du cadre',
    'not public': 'non public',
    'doc': 'doc',
    'private': 'privé',
    'National': 'National',

    # ---- trigger-statistics page ----
    'AA Trigger Statistics': 'Statistiques de déclenchement AA',
    "Published triggers, windows, return periods, and historical activations across the Centre "
    "for Humanitarian Data's Anticipatory Action portfolio. Activations are the historical "
    "(backtested) years each trigger would have fired.":
        'Déclencheurs publiés, fenêtres de déclenchement, périodes de retour et activations '
        'historiques du portefeuille d’action anticipatoire du Centre de données humanitaires. '
        'Les activations sont les années historiques (backtest) où chaque déclencheur se serait '
        'déclenché.',
    'Historical activations': 'Activations historiques',
    'Summary statistics': 'Statistiques récapitulatives',
    'By framework': 'Par cadre',
    'No activation data.': 'Aucune donnée d’activation.',
    'Year': 'Année',
    "Each filled cell marks a year the framework's trigger would have fired in the historical "
    "(backtested) record. One row per year, one column per framework.":
        'Chaque cellule remplie marque une année où le déclencheur du cadre se serait déclenché '
        'dans l’historique (backtest). Une ligne par année, une colonne par cadre.',
    'Overall return period = the chance <b>any</b> trigger in the framework fires. Pre-arranged '
    '= committed financing released on activation.':
        'Période de retour globale = la probabilité que <b>n’importe quel</b> déclencheur du '
        'cadre se déclenche. Pré-arrangé = financement engagé, libéré lors de l’activation.',
    'Framework': 'Cadre',
    'Windows': 'Fenêtres',
    'Overall RP': 'PR globale',
    'Annual prob.': 'Prob. annuelle',
    'Funding': 'Financement',
    'all-in': 'enveloppe unique',
    'split': 'réparti par fenêtre',
    'all-in (whole envelope releases on any trigger)':
        'enveloppe unique (toute l’enveloppe est libérée à tout déclenchement)',
    'Source:': 'Source :',
    'framework document': 'document du cadre',
    'current': 'actuelle',
    'superseded': 'remplacée',
    'prior version': 'version antérieure',
    'prior': 'antérieure',
    'framework page': 'page du cadre',
    'Trigger Mechanism Statistics': 'Statistiques du mécanisme de déclenchement',
    'Stats by trigger': 'Statistiques par déclencheur',
    'Trigger': 'Déclencheur',
    'Return period': 'Période de retour',
    'Activation probability': 'Probabilité d’activation',
    'Years activated': 'Années d’activation',
    'Overall stats': 'Statistiques globales',
    'Overall return period': 'Période de retour globale',
    'Overall probability of activation': 'Probabilité globale d’activation',
    'Average total spending per year': 'Dépense totale moyenne par an',
    'Pre-arranged financing:': 'Financement pré-arrangé :',
    "Per-framework trigger statistics in the format used in the framework documents. Frameworks "
    "with more than one version show each — pick a year to see that version's trigger history.":
        'Statistiques de déclenchement par cadre, dans le format utilisé dans les documents des '
        'cadres. Les cadres ayant plusieurs versions les affichent toutes — choisissez une année '
        'pour voir l’historique de déclenchement de cette version.',

    # ---- framework pages ----
    'Generated from the OCHA CHD Data Science knowledge base and the CERF OneGMS allocation feed '
    'by <code>scripts/gen_framework_pages.py</code>.':
        'Généré à partir de la base de connaissances de l’équipe Science des données du Centre '
        'de données humanitaires (OCHA) et du flux d’allocations OneGMS du CERF par '
        '<code>scripts/gen_framework_pages.py</code>.',
    'Monitoring period': 'Période de suivi',
    'Area of interest': 'Zone d’intérêt',
    'Current version': 'Version actuelle',
    'valid until': 'valide jusqu’en',
    'Trigger windows': 'Fenêtres de déclenchement',
    'Pre-arranged financing': 'Financement pré-arrangé',
    'framework total': 'total du cadre',
    'country envelope': 'enveloppe pays',
    'Budget by sector': 'Budget par secteur',
    'Budget by agency': 'Budget par agence',
    'Framework document': 'Document du cadre',
    'document': 'document',
    'Code repository': 'Dépôt de code',
    'Anticipatory action framework': 'Cadre d’action anticipatoire',
    '🛠 The current version of this framework is an in-development redesign — not yet endorsed. '
    'Details below describe the design being built; the last endorsed design is under '
    '<a href="#prev">previous versions</a>.':
        '🛠 La version actuelle de ce cadre est une refonte en cours de développement — pas '
        'encore approuvée. Les détails ci-dessous décrivent la conception en cours ; la dernière '
        'conception approuvée figure sous <a href="#prev">versions précédentes</a>.',
    'not yet reported': 'pas encore rapporté',
    'Activation history': 'Historique des activations',
    'This framework has not activated.': 'Ce cadre ne s’est pas activé.',
    'Real activations of this framework: the public trigger announcement and the CERF allocation '
    'that funded the response, with the people targeted and reached that CERF reports for the '
    'allocation (reported ~9 months after disbursement).':
        'Activations réelles de ce cadre : l’annonce publique de déclenchement et l’allocation '
        'du CERF qui a financé la réponse, avec les personnes ciblées et atteintes rapportées par '
        'le CERF pour l’allocation (rapporté ~9 mois après le décaissement).',
    'Date': 'Date',
    'Window': 'Fenêtre',
    'Announcement': 'Annonce',
    'CERF allocation': 'Allocation CERF',
    'CERF approved': 'Approuvé par le CERF',
    'People targeted': 'Personnes ciblées',
    'People reached': 'Personnes atteintes',
    'announcement': 'annonce',
    'partial': 'partielle',
    'non-CERF': 'hors CERF',
    "† one CERF application funded more than one activation (phases or windows) — its totals "
    "appear on each linked row; don't sum them.":
        '† une même demande CERF a financé plus d’une activation (phases ou fenêtres) — ses '
        'totaux apparaissent sur chaque ligne liée ; ne les additionnez pas.',
    'Overall': 'Global',
    '(any window)': '(toutes fenêtres confondues)',
    'Allocation': 'Allocation',
    'Probability': 'Probabilité',
    'Backtested activation years': 'Années d’activation (backtest)',
    'All-in: the whole envelope releases on any trigger.':
        'Enveloppe unique : toute l’enveloppe est libérée dès qu’un déclencheur se déclenche.',
    'Split funding: each window has its own budget and fires independently.':
        'Financement réparti : chaque fenêtre a son propre budget et se déclenche indépendamment.',
    'Backtested years are when each trigger <i>would have</i> fired in the historical record — '
    'not real activations.':
        'Les années backtest sont celles où chaque déclencheur se <i>serait</i> déclenché dans '
        'l’historique — pas des activations réelles.',
    'Trigger statistics (current version)': 'Statistiques de déclenchement (version actuelle)',
    'No published trigger statistics for this framework yet.':
        'Pas encore de statistiques de déclenchement publiées pour ce cadre.',
    'pre-arranged': 'pré-arrangé',
    'activated': 'activé',
    'Previous versions': 'Versions précédentes',
    "Earlier versions of this framework. Real activations listed here fired under that version's "
    "trigger design (details in the activation history above).":
        'Versions antérieures de ce cadre. Les activations réelles listées ici se sont '
        'déclenchées sous la conception de déclencheur de cette version (détails dans '
        'l’historique des activations ci-dessus).',
    'One page per anticipatory action framework: status, triggers, real activations, and the '
    'CERF allocations behind them.':
        'Une page par cadre d’action anticipatoire : statut, déclencheurs, activations réelles '
        'et les allocations du CERF correspondantes.',
    'CERF allocated (activations)': 'CERF alloué (activations)',
    "CERF allocated / people reached sum the CERF allocations linked to this framework's real "
    "activations (shared applications counted once).":
        'CERF alloué / personnes atteintes additionnent les allocations du CERF liées aux '
        'activations réelles de ce cadre (les demandes partagées ne sont comptées qu’une fois).',
    'Source': 'Source',
    'Agency': 'Agence',
    'Sector': 'Secteur',
    'Amount': 'Montant',
}

# EN -> FR strings rendered CLIENT-SIDE (map legend, popovers, filter controls).
# Keys must match the tr8() lookups in gen_public_site's JS verbatim (including
# the HTML entities used there).
JS_UI: dict[str, str] = {
    'Framework': 'Cadre',
    'Active': 'Actif',
    'Recently triggered': 'Récemment déclenché',
    'Expired': 'Expiré',
    'In development': 'En développement',
    'Retired': 'Retiré',
    'Activated &mdash; a dot per activation': 'Activé &mdash; un point par activation',
    'Able to trigger now &mdash; in season': 'Peut se déclencher actuellement &mdash; en saison',
    'pulsing': 'clignotant',
    'Able to trigger &mdash; off-season': 'Peut se déclencher &mdash; hors saison',
    'No ring = cannot trigger (activated &amp; spent, expired, or in development)':
        'Sans anneau = ne peut pas se déclencher (activé &amp; épuisé, expiré ou en développement)',
    'able to trigger': 'peut se déclencher',
    'not able to trigger now (spent)': 'ne peut pas se déclencher actuellement (épuisé)',
    'triggered': 'déclenché',
    'activated': 'activé',
    'window': 'fenêtre',
    'framework doc': 'document du cadre',
    'framework page': 'page du cadre',
    'all': 'tous',
    'months': 'mois',
    'country…': 'pays…',
    'filter…': 'filtrer…',
}

_missing: set[str] = set()


def fr(en: str) -> str:
    """French for a fixed UI string; falls back to English and records the miss."""
    out = FR.get(en)
    if out is None:
        _missing.add(en)
        return en
    return out


@atexit.register
def _report_missing() -> None:
    if _missing:
        print(f"::warning::site_i18n: {len(_missing)} UI string(s) missing a French "
              "translation (rendered in English):")
        for s in sorted(_missing):
            print(f"  [i18n-missing] {s!r}")


def _attr(s: str) -> str:
    return html.escape(str(s), quote=True)


def T(en: str, fr_: str | None = None) -> str:
    """Toggle-aware plain-text span. textContent is swapped client-side, so table
    sorting/filtering always operate on the active language only."""
    f = fr(en) if fr_ is None else fr_
    return (f'<span class="tr" data-en="{_attr(en)}" data-fr="{_attr(f)}">'
            f'{html.escape(str(en))}</span>')


def TB(en_html: str, fr_html: str | None = None) -> str:
    """Dual-language block for strings that contain markup (links, <b>, …)."""
    if fr_html is None:
        fr_html = fr(en_html)
    return (f'<span class="lv lv-en">{en_html}</span>'
            f'<span class="lv lv-fr">{fr_html}</span>')


# ---------------------------------------------------------------------------
# date/label French helpers
# ---------------------------------------------------------------------------
# NOTE: numbers, currency ($4.0M), percentages, and counts render identically in
# both languages — only unit WORDS are translated (e.g. '12.3 years' -> '12.3
# ans'). This keeps the client-side sort/filter (which parse cell text) simple.

_MONTH_EN = {"Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6,
             "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12}


def months_fr(en_span: str) -> str:
    """French counterpart of gen_public_site.fmt_months() output
    ('Nov–Apr' -> 'nov–avr', 'year-round' -> 'toute l'année')."""
    if en_span == "year-round":
        return "toute l’année"
    return re.sub("|".join(_MONTH_EN),
                  lambda m: MONTH_ABBR_FR[_MONTH_EN[m.group(0)]], en_span)


def month_year_fr(en_label: str) -> str:
    """'June 2026' -> 'juin 2026' (the map legend's current-month label)."""
    full_en = ["January", "February", "March", "April", "May", "June", "July",
               "August", "September", "October", "November", "December"]
    for i, name in enumerate(full_en, start=1):
        if en_label.startswith(name):
            return en_label.replace(name, MONTH_FULL_FR[i])
    return en_label


def country_fr(iso3: str, en_name: str) -> str:
    return COUNTRY_FR.get(iso3, en_name)


def hazard_fr(slug: str, en_label: str) -> str:
    return HAZARD_FR.get(slug, en_label)


# common trigger-window names quoted from the docs (per the MDG bilingual glossing:
# readiness trigger = déclencheur de mobilisation, action trigger = déclencheur d'action)
WINDOW_NAME_FR = {
    "Readiness": "Mobilisation", "Action": "Action",
    "Readiness trigger": "Déclencheur de mobilisation",
    "Action trigger": "Déclencheur d’action",
}

# compact map-callout hazard labels (gen_public_site.pretty_hazard counterpart)
PRETTY_HAZARD_FR = {"tropical-cyclone": "Cyclones trop.", "flood": "Inondations",
                    "drought": "Sécheresse", "cholera": "Choléra", "plague": "Peste"}


def pretty_hazard_fr(slug: str, en_label: str) -> str:
    return PRETTY_HAZARD_FR.get(slug, HAZARD_FR.get(slug, en_label))


def status_fr(status: str) -> str:
    return STATUS_FR.get(status, status.replace("-", " "))


# ---------------------------------------------------------------------------
# client-side plumbing (embed in each page)
# ---------------------------------------------------------------------------

LANG_CSS = """
.lv-fr{display:none}
html[data-lang="fr"] .lv-fr{display:inline}
html[data-lang="fr"] .lv-en{display:none}
.aa-lang{display:inline-flex;align-items:center;gap:0;border:1px solid rgba(255,255,255,.55);
  border-radius:6px;overflow:hidden;flex:0 0 auto;vertical-align:middle}
.aa-lang button{border:none;background:transparent;color:#fff;font-size:12px;font-weight:700;
  padding:4px 9px;cursor:pointer;line-height:1;opacity:.75}
.aa-lang button:hover{opacity:1}
.aa-lang button.on{background:#fff;color:#1a6bb5;opacity:1}
"""

# The toggle button pair. Pages place it in their header (top-right).
TOGGLE_HTML = ('<span class="aa-lang" role="group" aria-label="Language">'
               '<button type="button" data-l="en" class="on" onclick="aaSetLang(\'en\')">EN</button>'
               '<button type="button" data-l="fr" onclick="aaSetLang(\'fr\')">FR</button></span>')

# Core toggle JS. Optional page hook: define window.AA_TITLES = {en:…, fr:…} for
# <title> swapping, and listen for the 'aalang' event to re-render dynamic bits.
LANG_JS = """
function aaSetLang(l){
  document.documentElement.setAttribute('data-lang', l);
  document.documentElement.setAttribute('lang', l);
  try{localStorage.setItem('aa-lang', l);}catch(e){}
  document.querySelectorAll('.tr').forEach(function(el){
    var v = el.getAttribute('data-' + l);
    if (v !== null) el.textContent = v;
  });
  document.querySelectorAll('.aa-lang button').forEach(function(b){
    b.classList.toggle('on', b.getAttribute('data-l') === l);
  });
  if (window.AA_TITLES && window.AA_TITLES[l]) document.title = window.AA_TITLES[l];
  try{document.dispatchEvent(new CustomEvent('aalang', {detail: l}));}catch(e){}
}
(function(){
  var l = null;
  try{l = localStorage.getItem('aa-lang');}catch(e){}
  if (l !== 'fr') return;
  if (document.readyState === 'loading')
    document.addEventListener('DOMContentLoaded', function(){ aaSetLang('fr'); });
  else
    aaSetLang('fr');
})();
"""
