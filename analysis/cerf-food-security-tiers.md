---
content_type: analysis
name: cerf-food-security-tiers
analysis_type: other
status: active
country_iso3: global
hazard: food-insecurity
summary: Review of the CERF Secretariat's food security tiering notes, a first automated run of the tier rules on IPC/CH data from the IPC mirror, a month-by-month tier table with adjustable rules, and a per-country chart of every IPC/CH analysis since 2017; private repo, password-protected Pages site; not agreed with CERF yet
data_sources: [ipc, cadre-harmonise]
feeds: []
surfaces:
  - {url: "https://ocha-dap.github.io/ds-cerf-food-security/", kind: landing, title: "Food security tiers for CERF", access: password}
  - {url: "https://ocha-dap.github.io/ds-cerf-food-security/tier-review/", kind: report, title: "CERF food security tiers: review and automated test", access: password}
  - {url: "https://ocha-dap.github.io/ds-cerf-food-security/ipc-history/", kind: dashboard, title: "IPC figures over time, by country", access: password}
# --- source repo ---
source_repo: ocha-dap/ds-cerf-food-security
source_branch: main
source_sha:
code_ref: [src/tiering.py, src/ipc.py, src/notes.py, scripts/run_tiering.py, scripts/build_site.py, site/tier-review/rules.js, scripts/check_rules_js.py, scripts/history_page.py, site/ipc-history/history.js, scripts/archive_ipc.py]
depends_on: [ipc-mirror, ipc.population, ipc.analyses]
discrepancies: []
extra: {}
visibility: public
last_synced: "2026-10-09"
---

# CERF food security tiers — analysis

> **Analysis, not a framework.** Support to the CERF Secretariat on how countries are
> sorted into tiers of food insecurity for Underfunded Emergencies and Rapid Response
> allocations. No trigger, no pre-arranged financing.

## What it is

The CERF Secretariat places countries in tiers of food insecurity and has done so
by hand, in a note written for each allocation round. The team was asked whether the
tiering can be kept up to date automatically. This repo is the first look: it reviews the
notes shared with us (how the criteria and the tier lists changed from one note to the
next, and where the notes depart from their own rules) and tests how much of the current
rules can be applied to IPC and Cadre Harmonisé data without a person in the loop.

**The notes are internal CERF documents.** Their criteria, tier lists and figures are not
reproduced here; they are in the private repo and on the password-protected site. Ask the
team for access.

## What was analyzed / findings

- **Document review**: each note's criteria, tier lists, declared exceptions and annex
  figures, parsed from the Word tables and transcribed from the text.
- **Automated test**: each note's criteria coded as rules and run on the IPC/CH figures
  that were visible when the note was written, compared with the published tiers. The
  most recent note's rules reproduce its tiers for nearly every country that has IPC
  data; the mismatches in earlier notes are mostly exceptions the notes themselves
  declare.
- **Month-by-month tier table**: every country with IPC/CH figures, every month since
  2021, tiered under any note's rules, under the rules in force at the time, or under
  cutoffs the reader sets, with two rule sets comparable in one table. The rules are
  applied in the browser so they can be changed without a rebuild.
- **IPC history by country**: a chart and a table of every national IPC/CH analysis
  since January 2017. Each period is drawn across the months it covers, projections
  behind current periods and newer analyses in front of older ones, so a projection
  stays visible beside the figure that later replaced it. A strip under the chart shows
  how much of the country each analysis covered.
- **What cannot be automated from IPC alone**: countries without a current IPC analysis,
  conditions that are not in the population figures, and judgement about the outlook.
- **Design points worth knowing before reusing the approach** (these are about IPC data,
  not about the notes):
  - A run "as of" a past date must use only analyses that were visible then.
    `ipc.population` carries the analysis month, not a publication date; the IPC API
    registry (`ipc.analyses.created`) is the usable proxy, typically one to three months
    after the analysis month. Cadre Harmonisé rounds are entered country by country over
    several weeks, so the round is dated by its first entry.
  - Which validity period counts (the one covering the date, a projection, a period that
    has just ended) changes tiers near a threshold. It has to be an explicit parameter.
  - Prevalence is over the *analysed* population, and coverage varies a lot (a third of
    Kenya, a fifth of Pakistan, a few percent for refugee-only analyses in Uganda). A
    minimum coverage is needed before a prevalence threshold means anything nationally.
  - A partial projection can carry the previous period's analysed total in the `all` row
    (seen once, Sudan 2026): check the phase sum against `all` before computing
    prevalence.
  - A monthly series of "as of" runs should be run on the **last** day of each month, not
    the first. Documents written mid-month are then covered by their own month, and here
    that made each note's month agree exactly with the run on the note's own date.
  - **IPC history before 2021 is no longer published.** The IPC datasets on HDX stopped
    carrying analyses made before 2021 some time between July and October 2026, and the
    [IPC mirror](../pipelines/ipc-mirror.md), a full replace of those datasets, lost them
    too. This repo keeps the national rows of the 111 missing rounds (37 countries,
    2017 to mid-2021) in `data/ipc_national_archive.csv`, copied from a July 2026 export
    of the mirror's site data. They have no country totals, and their registry dates
    (`ipc.analyses.created`) are often years after the analysis, so they cannot be used
    as "visible from" dates.
  - National IPC rounds overlap: a new round's current period covers months an older
    round projected, and partial analyses of different areas share the same months. A
    time series either picks one figure per month or draws every period; the history
    page draws every period and layers them (projections behind, newer in front).
  - Rules that are also implemented in the browser (so a reader can edit them) need a
    guard against drift. The run ships the rule-independent part (which periods count on
    each date, with their figures) and the build compares the two implementations on
    every country and month and on made-up values either side of every threshold
    (`scripts/check_rules_js.py`), stopping if they differ.

## Relation to frameworks

Standalone. It is CERF allocation support, not anticipatory action.

## Sources & status

Repo `ocha-dap/ds-cerf-food-security` (**private**). Data: the [IPC mirror](../pipelines/ipc-mirror.md)
(`ipc.population` national rows and `ipc.analyses`), read as a snapshot through the DB
tunnel. Site built locally by `scripts/build_site.py` and published encrypted (staticrypt)
by `scripts/publish.sh`; there is no scheduled job yet.

Status (October 2026): first look, not yet discussed with the CERF Secretariat. The choices
in the run (which periods count, minimum coverage, how exceptions are recorded, which
countries are in scope) are open questions for CERF, listed on the site.

An earlier tool for the same audience, `hdx-foodsecurity-CERF` (2025, IPC figures for
CERF's peak hunger period, Azure app `chd-ds-ipc-cerf`, stopped since August 2026), is
unrelated code; this work starts the method from scratch.
