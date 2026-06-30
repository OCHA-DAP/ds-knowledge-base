---
content_type: framework
framework: mdg-plague
version: "draft-2021"   # no published framework PDF; pilot selected ~2021. Using a draft label per _TEMPLATE (development, no doc date).
status: development     # selected as an OCHA/CERF AA pilot ~2021; CERF "in development" through at least Nov 2024; never endorsed/activated. Default-to-development per _TEMPLATE.
valid_until: null       # no published validity period — framework never endorsed
country_iso3: MDG
hazard: plague
admin_level: null
geographic_scope:
  - "Central highlands (plague-endemic regions)"   # inferred from plague epidemiology, NOT from a framework doc
data_sources: []        # not publicly stated; IPM (Institut Pasteur de Madagascar) national plague reference lab is the obvious surveillance source — see body
trigger_facets:
  basis: null           # trigger design not publicly available
  calibration: null
  indicators: []        # not sourced; epidemiological case surveillance ± seasonal/climate signal implied but unpublished
  n_windows: null
  window_axes: []
monitoring_period:
  months: [10, 11, 12, 1, 2, 3, 4]   # Madagascar plague season ~Oct–Apr (central highlands), peaking Dec–Jan
  source: inferred
  note: "Inferred from plague seasonality (endemic season ~Sept/Oct–Apr in the central highlands), NOT from a framework doc — no monitoring window is publicly stated for the AA pilot."
supersedes: null
# --- funding & scope ---
all_in: true
prearranged_funding_usd: null   # development-stage, no endorsed envelope. A ~$3.0M figure appears in CERF tracking (see extra) but is planned/earmarked, not pre-arranged & committed.
funding_by_source: {}
cofinancing_usd: null
cofinancing_sources: []
implementing_agencies: []        # not stated for the AA pilot (WHO/UNICEF led the 2017 outbreak response, but that is not confirmed for this framework)
target_people: null
# --- documents, authority-ranked ---
framework_doc: null              # no standalone, public AA framework PDF found; only CERF portfolio/tracking references (see body & extra)
framework_doc_date: null
framework_doc_annexes: []
languages: [en]
model_report: null
raw_extract: []
# --- live system ---
operated_by: null
apps: []
depends_on: []
# --- source repo & reconciliation ---
source_repo: null
source_branch: null
source_sha: null
code_ref: []
trigger_source: null             # neither a public framework doc nor a DS repo found
repo_completeness: null          # no DS repo identified for this framework
discrepancies:
  - "[gap] No public AA framework document and no DS code repo were found for the Madagascar plague AA pilot. The trigger design (indicators, thresholds, lead time), implementing agencies, and target population are NOT publicly sourceable. Status, geography and seasonality below are reconstructed from CERF/OCHA portfolio references and plague epidemiology, not an endorsed framework text."
  - "[stale] A 2018 CERF rapid-response allocation of US$1,000,000 for plague early action in Madagascar predates the AA pilot and was NOT a triggered activation of this framework (rapid-response window, not pre-arranged AA finance). Recorded in body for context only."
# --- activation history ---
activations: []   # never activated as an AA framework (remained in development). The 2018 $1M rapid-response allocation is NOT an AA-framework activation.
# --- escape hatch ---
extra:
  pilot_selection: "Madagascar was selected ~2021 as one of OCHA's new collective anticipatory-action pilot cases, with plague as the hazard — alongside AA design work facilitated by OCHA in Chad, DRC, Madagascar, Mozambique and South Sudan. Listed in 'CERF Anticipatory Action' (11 Nov 2021)."
  pilot_goal: "Anticipate and contain plague outbreaks before they spread across regional or international borders; shift from a reactive (post-outbreak) posture to an early-warning-driven anticipatory one."
  planned_envelope_note: "CERF AA tracking (e.g. the Nov 2024 CERF climate/AA infographic) lists a Madagascar 'Plague/Cyclones' entry as 'In development' with US$3.0M. The label appears to bundle plague with the (separate, endorsed) Madagascar cyclone AA framework, so the $3.0M cannot be attributed cleanly to plague alone — left out of prearranged_funding_usd."
  ipm_note: "Institut Pasteur de Madagascar (IPM) hosts the WHO-collaborating national plague reference laboratory; clinically suspected plague cases are notified to the national surveillance system and confirmed by IPM. Any trigger would most plausibly key off this surveillance, but this is inference, not a sourced design."
  related_frameworks: "Distinct from the endorsed Madagascar tropical-cyclone AA framework (2024–2026, see mdg-storms) and from FAO/WFP forecast-based-action work on drought/dry-spells in southern Madagascar."
  schema_strain: "Framework with NO repo and NO public framework doc — most trigger/funding/scope fields are null by necessity. Page is a portfolio-completeness stub drawing on CERF/OCHA references and epidemiology; verify against an internal OCHA/CERF source if one exists."
visibility: public
last_synced: "2026-06-29"
---

# Madagascar Plague — draft-2021

> Fill the headings below. Keep the **questions** even when the answer is "n/a".
> The canonical trigger is the code at `code_ref`; this page explains it, it does not redefine it.
> **No public framework document or DS repo was found for this pilot** — this page is a sourced portfolio stub, not a reconciliation of an endorsed trigger. Facts not sourced are left `null`/`[]`.

## Summary

Madagascar was selected around 2021 as one of OCHA's new collective **anticipatory-action (AA) pilot** countries, with **plague** as its hazard (an unusual disease-specific hazard for the AA portfolio). The intent was to **anticipate and contain plague outbreaks before they spread** across regional or international borders, moving from a reactive (act-once-an-outbreak-is-reported) posture to an early-warning-driven one, with pre-arranged CERF finance ready to release on a pre-agreed trigger. As of the most recent public CERF tracking (through at least November 2024) the framework was still listed **"in development"**; **no AA framework document was ever published, the trigger was never finalised publicly, and it has never activated.** It should not be confused with Madagascar's separate, endorsed **tropical-cyclone** AA framework (2024–2026), nor with the 2018 CERF rapid-response allocation for plague early action (see *Historical activations*).

## Method

Not publicly documented. The pilot's stated direction was to build an **early-warning system** for plague that could trigger pre-agreed actions during the window between rising risk/early signals and a full-blown outbreak. Madagascar accounts for the large majority of the world's reported plague cases; the disease is **endemic and seasonal in the central highlands**, with a season running roughly **September/October to April** (bubonic form dominant, with the feared escalation being **pneumonic** plague, which is human-to-human transmissible and drove the large 2017 epidemic). The national surveillance system, anchored by the WHO-collaborating reference laboratory at **Institut Pasteur de Madagascar (IPM)**, is the natural data backbone for any trigger — but the actual indicator/threshold/lead-time design is **not in the public record**.

## Trigger logic

- **Keys off:** *Not publicly stated.* Most plausibly epidemiological case surveillance (IPM / national system), potentially combined with seasonal/climatic risk signals — **unconfirmed**.
- **Decision rule (plain language):** *Not available.* No published threshold or activation rule exists for this pilot.
- **Activation structure:** *Unknown* — no windows documented (`n_windows: null`).
- **Calibration:** *Unknown.* No public calibration against historical plague seasons/outbreaks was found.
- **Authoritative source:** **None found.** There is no `framework_doc` (the field is `null`); the only public references are CERF/OCHA AA portfolio materials that *list* the pilot, not define its trigger.
- **Operated by:** n/a — no live trigger system identified.

## Trigger windows

No trigger windows are publicly documented. `n_windows: null`.

| window | basis | indicator | threshold | lead time | return period | releases |
|---|---|---|---|---|---|---|
| *(none documented)* | — | — | — | — | — | — |

## Per-country variants

n/a — single-country framework.

## Sources & repo completeness

- **Trigger taken from:** nothing — neither a public framework doc nor a DS repo was located (`trigger_source: null`).
- **Repo completeness:** no DS repo identified for this framework (`repo_completeness: null`).
- **Discrepancies:** `[gap]` the trigger/funding/agency/target-population design is not publicly sourceable; `[stale]` the 2018 $1M rapid-response allocation is unrelated context, not an activation. See frontmatter.

## Monitoring

No live monitoring pipeline identified. The relevant epidemiological monitoring is Madagascar's national plague surveillance with IPM laboratory confirmation; the plague season runs ~Oct–Apr in the central highlands. Whether any AA-specific monitoring was ever stood up is unknown.

## Historical activations

**Never activated as an AA framework.** The pilot remained in development and no pre-arranged AA trigger fired.

For context (and **not** an AA-framework activation): in **2018**, after the catastrophic 2017 pneumonic-plague epidemic (which killed 200+ people), CERF allocated **US$1,000,000 from its rapid-response window** for early action to prevent a large-scale plague outbreak; it reportedly benefited ~1,520,799 people (~1,460,000 via health activities, the remainder via WASH) and was associated with a sharp reduction in 2018 plague deaths (~50, vs. 220+ in 2017). This was a **rapid-response** allocation, predating and distinct from the anticipatory-action pilot — it is recorded here only to prevent it being mistaken for a trigger-based activation.

## Key decisions & rationale

The rationale for choosing plague as Madagascar's AA hazard is the disease's **annual seasonality and explosive escalation potential** (bubonic → pneumonic), which makes a pre-agreed early-action window genuinely actionable, and Madagascar's outsized share of global plague burden. Why the framework did not progress to endorsement is not documented publicly (disease-outbreak triggers are intrinsically hard to pre-define and calibrate — cf. the difficulty noted across OCHA's epidemic AA work).

## Changes from previous version

n/a — first (and only) record; no prior version.

## Open questions / known issues

- **Trigger design unknown** — indicator(s), threshold(s), lead time, number of windows: all unsourced. Verify against any internal OCHA/CERF/CHD design note.
- **Funding** — is the ~$3.0M "Plague/Cyclones" CERF entry partly or wholly the cyclone framework? The plague-specific pre-arranged amount (if any) is unconfirmed.
- **Implementing agencies & target people** — not stated for the AA pilot.
- **Current status** — is the pilot still "in development", quietly **discontinued/superseded**, or absorbed into other epidemic-preparedness work? Last public signal is the Nov 2024 CERF tracking; confirm whether it should be retired.
- **IPM / surveillance integration** — confirm whether IPM data was ever wired into a candidate trigger.

<!-- TODO: If an internal OCHA/CERF design document or CHD analysis for the Madagascar plague AA pilot exists, ingest it and replace the null trigger/funding fields. -->
