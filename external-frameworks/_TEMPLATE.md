---
content_type: framework-external
framework:         # stable id: <org>-<iso3>-<hazard>, e.g. ifrc-bgd-cyclone
org:               # IFRC | WFP | FAO | START | ... (open vocab; the org that OWNS/operates the framework)
country_iso3:      # e.g. BGD — may be a list for multi-country programmes
hazard:            # drought | flood | tropical-cyclone | ... (same open vocab as OCHA pages)
status:            # active | in-development | expired | inactive | unknown  (DELIBERATELY looser
                   # than the OCHA enum — external lifecycle info is often vague; use `unknown`
                   # honestly rather than guessing)
valid_until:       # end of validity period if stated (YYYY | YYYY-MM | YYYY-MM-DD), else null
trigger_summary:   # 1-2 sentences: indicator, threshold, lead time. THE plain-language trigger.
                   # (No trigger_facets / windows machinery — that rigor is for OCHA pages.)
data_sources: []   # tags when known, e.g. [GloFAS, ECMWF] — same vocab as OCHA pages
# --- funding & scope (same field names as OCHA pages) ---
prearranged_funding_usd:   # USD int if stated (convert CHF etc., note rate in extra); null unknown
funding_by_source: {}      # e.g. {DREF: 250000} / {SFERA: ...} / {WFP: ...}. {} if unknown
target_people:             # int or null
# --- documents ---
framework_doc:     # URL of the most authoritative public document (EAP/AA plan/protocol)
framework_doc_date:  # its date
sources: []        # further source URLs (Anticipation Hub page, evaluations, news)
# --- activation history (same shape as OCHA pages) ---
activations: []    # [{date, url, note}] — real activations only; [] = none known
# --- bookkeeping ---
last_checked:      # YYYY-MM-DD — when a human/agent last verified this page against sources.
                   # External pages have NO drift-bot or PDF-freshness watcher (deliberate, D77);
                   # this date is the only staleness signal.
extra: {}          # anything that doesn't fit; keep the schema loose rather than growing it
visibility: public
---

# {Org} — {Country} {Hazard}

## Summary
One paragraph: who runs it, what it triggers on, what it activates, at what scale.

## Trigger
Plain language: data → indicator → threshold → lead time → what's released. As much detail
as the public docs support — a one-liner is acceptable when that's all there is.

## Funding & scope
Amounts, source (DREF / SFERA / WFP AA facility / …), target people/households, coverage area.

## Activations
Real activations with dates and one-line outcomes; "none known" is itself worth stating.

## Sources
Bullet list of every URL used, with dates. Note which is authoritative.
