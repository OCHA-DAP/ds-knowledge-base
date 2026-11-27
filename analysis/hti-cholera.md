---
content_type: analysis
name: hti-cholera
analysis_type: pre-framework
status: active
country_iso3: HTI
hazard: cholera
summary: Preliminary look (October 2026) at whether PAHO/OMS commune-by-week cholera surveillance could support a Haiti AA trigger built like the DRC cholera framework's 2026 revision, with a CERF cholera-allocation comparison. Not a framework in development; findings kept private for now
data_sources: [PAHO-cholera-surveillance, CERF-allocations, CODAB, HDX]
feeds: []
surfaces:
  - {url: "https://literate-adventure-1glq4vr.pages.github.io/", kind: landing, title: "Haiti cholera (private-repo Pages landing page)", access: private}
  - {url: "https://literate-adventure-1glq4vr.pages.github.io/analysis/", kind: book, title: "Haiti cholera: a first look at an anticipatory action trigger (Quarto book; private-repo Pages)", access: private}
# --- source repo ---
source_repo: ocha-dap/ds-aa-hti-cholera
source_branch: main
source_sha: 8c8db0c
code_ref:
  - src/hti_cholera/trigger.py
  - src/hti_cholera/load.py
  - src/hti_cholera/analysis.py
  - tests/test_drc_reference.py
  - book/
depends_on: []
discrepancies: []
extra:
  method_source: "Trigger re-implemented in Python from OCHA-DAP/pa-aa-cod-infectious-disease main@a44d9a3 (the 2026 revision's L3 configuration: p98.8 pooled non-zero weekly suspected cases, >4x week-on-week rate rule, 3 consecutive alert weeks, 6-month same-unit and per-province spatial mutes). tests/test_drc_reference.py checks the port against saved outputs of the DRC code run on the Haitian data."
  data_access: "PAHO/OMS surveillance workbook shared with CHD in October 2026 (aggregated, anonymised); committed in the private repo. Not public."
visibility: internal
last_synced: 2026-10-16
---

# Haiti cholera — analysis

> **Analysis, not a framework.** A preliminary look at Haiti's cholera surveillance
> data for a possible anticipatory action trigger. It is not a framework in
> development, and there is no framework document. The write-up is on the private
> repository's Pages site (readers of `OCHA-DAP/ds-aa-hti-cholera` only).

## What it is

The DRC cholera framework's 2026 revision ([`cod-infectious-disease`](../frameworks/cod-infectious-disease/README.md))
applied to PAHO/OMS cholera surveillance data for Haiti: suspected and confirmed
cases and deaths by commune and epi week, September 2022 to September 2026. It asks
whether the data are complete and long enough to support a trigger of that kind. It
also compares the trigger's would-have-activated history with CERF's cholera
allocations to Haiti, and sketches what an alert for cholera re-emerging after a
quiet period would need.

## What was analyzed / findings

Covered in the private book: data completeness and consistency, thresholds under
different baseline windows, would-have-activated onsets, a percentile sweep, the
CERF comparison, and re-emergence. The findings are not summarised here while the
content stays private; read the book or ask the team.

Method notes that hold regardless of the findings:

- Unit = commune (COD-AB admin 2, 140), department in place of DRC's province for
  the spatial mute (department adjacency from the COD-AB). Epi weeks start on Sunday
  (MMWR), so 2025 has 53 weeks.
- The DRC's rolling five-year baseline cannot be applied as written to a four-year
  record. The book uses all years pooled (what a January recompute would give), plus
  expanding and two-year rolling alternatives.
- The same-week order in the L3 spatial mute can change the activation count. The DRC
  code orders same-week onsets by health-zone code, inherited from
  `constrain_same_unit()`. The port reproduces that and offers a larger-outbreak-first
  alternative (`TriggerConfig.tie_break`).

## Relation to frameworks

Standalone. Uses the method of [`cod-infectious-disease`](../frameworks/cod-infectious-disease/README.md)
(2026-06-24 version) but does not feed it.

## Sources & status

- Repo: `ocha-dap/ds-aa-hti-cholera` (private). Python only; the book renders and
  deploys from `main` via `.github/workflows/pages.yml`, which refuses to deploy unless
  the Pages site is private.
- Data: PAHO/OMS workbook as received (`data/raw/`); CERF OneGMS snapshot; OCHA Haiti's
  national monthly series 2010–2016 from HDX; COD-AB boundaries via FieldMaps.
- Status: preliminary, October 2026. Next steps depend on further data from PAHO/OMS
  and MSPP (listed in the book).
