# External AA frameworks — other organisations' anticipatory action

Catalog of anticipatory-action frameworks run by organisations **other than OCHA/CERF**:
IFRC Early Action Protocols, WFP anticipatory action plans, FAO anticipatory action
protocols, START Network, and others. One page per framework, grouped by org:
`external-frameworks/<org>/<iso3-hazard>.md`.

**This section is deliberately separate from [`frameworks/`](../frameworks/README.md)**
(the OCHA/CERF portfolio, D51/D53) and holds itself to a **looser standard** (D76):

- **Schema = the common core only** (see [`_TEMPLATE.md`](_TEMPLATE.md)): org, country,
  hazard, loose status, a plain-language `trigger_summary`, funding, docs, activations.
  Field names match the OCHA schema exactly where they overlap, so the OCHA schema is a
  superset — the [global catalog](../catalog-global.md) reads only the core from both.
- **Sources are public web documents** (org publications, ReliefWeb, the
  [Anticipation Hub](https://www.anticipation-hub.org)) — there is no repo, no
  PDF-authority reconciliation, no drift bot. Each page carries `last_checked` instead.
- **Identity is org + country + hazard** (vs country + hazard within OCHA, D62).
  No version folders — one page per framework, updated in place.

The OCHA AA map/page and all `frameworks/` tooling are untouched by this section.
The comparative view across ALL orgs (including OCHA) is the generated
[`catalog-global.md`](../catalog-global.md) (`scripts/gen_global_catalog.py`); the public
face is the **"All organisations" tab** of the AA site (/anticipatory-action/global.html;
`scripts/gen_global_site.py`, D78).

## The Hub pipeline (how this section grows — D77)

1. **`scripts/fetch_hub_inventory.py`** — pulls the Hub's global-map JSON API (both
   layers) → `.hub-inventory.json` (~330 raw records).
2. **`scripts/gen_hub_stubs.py`** — collapses records to framework identity
   (org+country+hazard), writes a core-fields **stub page** for every framework we
   don't hold (`extra.hub_stub: true`, `trigger_summary: null`), cross-checks
   OCHA-coordinated rows against `frameworks/` (missing combos = aa-watch signal), and
   regenerates [`hub-inventory.md`](hub-inventory.md) — coverage report + the
   **prioritized enrichment queue** of dispatch commands. Re-running only ADDS newly
   listed frameworks; existing pages (stub or enriched) are never overwritten.
3. **`scripts/enrich_external_framework.py`** — one stub → full page via headless
   Claude web research (`kb-ingest.yml -f page=external-frameworks/...`); Opus-reviewed,
   lands as a PR like every other ingest.

## Discovery sources (reference)

The [Anticipation Hub](https://www.anticipation-hub.org) is the authoritative global
inventory — ~155 active frameworks in 49 countries per the
[2024 overview report](https://www.anticipation-hub.org/global-overview/global-snapshot/overview-reports/overview-report-2024)
(IFRC EAPs ~40, FAO 27, OCHA/CERF 16, WFP 15, Start Network 13, rest NGO-funded).
Two machine-readable routes for batch ingestion (both public, no auth):

- **Global-map JSON API** — live, per-framework records (org, hazard, people targeted,
  investment USD, doc link): `…/experience/global-map/global-map/active-frameworks/areas/api.json`
  → per-country `area-detail-<id>/api.json`; same pattern for the `under-development`
  and `activations` layers. Org filter ids: IFRC 359, WFP 291, FAO 378, Start 311.
- **Annual XLSX data tables** — the 2024 report's Table A2 (active frameworks, 26 cols
  incl. funding/coordinating/implementing orgs, budgets, EAP codes, project-page URLs),
  A1 (activations), A3 (under development), under
  `…/Documents/Reports/Overview-report-2024/`.

Caveat when attributing `org`: the report tables cut by *funding* org, the map API by
*coordinating* org — they disagree for some IFRC EAPs (National Society vs IFRC). We use
the org that OWNS/operates the framework.

Org-specific machine-readable sources: **IFRC GO API**
(`https://goadmin.ifrc.org/api/v2/appeal/?code=MDR…` — live status, budget, beneficiaries
per EAP operation number). ReliefWeb/unocha.org 403 default fetchers — use a browser
User-Agent (same as the OCHA ingest path); Anticipation-Hub-hosted PDF mirrors are the
most fetch-friendly.

## Patterns learned from the sample (apply when adding pages)

- **Component-of-collective**: when an org runs a piece of an OCHA/CERF collective
  framework (FAO in PHL, WFP in NPL), the collective framework stays an OCHA page; the
  org's own component gets an external page ONLY if the org publishes it as its own
  framework — with an `extra.coordination` note cross-linking the OCHA page, so nothing
  reads as independent that isn't.
- **IFRC versioning**: EAP numbers persist confusingly across revisions — record both
  `extra.eap_no` and `extra.operation_no` (MDR…), and generation lineage in
  `extra.generations`.
- **Activation flavors**: full · partial/no-regret · expert-consensus below-threshold ·
  trigger-not-met (worth recording as a near-activation in `extra`, not `activations`).
- Currency: `prearranged_funding_usd` is USD — note original CHF/EUR amounts in `extra`.
