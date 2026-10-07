---
content_type: analysis
name: cerf-food-security-tiers
analysis_type: other
status: active
country_iso3: global
hazard: food-insecurity
summary: Review of the CERF Secretariat's food security tiering notes and a first automated run of the tier rules on IPC/CH data from the IPC mirror; private repo, password-protected Pages site; not agreed with CERF yet
data_sources: [ipc, cadre-harmonise]
feeds: []
surfaces:
  - {url: "https://ocha-dap.github.io/ds-cerf-food-security/", kind: landing, title: "Food security tiers for CERF", access: password}
  - {url: "https://ocha-dap.github.io/ds-cerf-food-security/tier-review/", kind: report, title: "CERF food security tiers: review and automated test", access: password}
# --- source repo ---
source_repo: ocha-dap/ds-cerf-food-security
source_branch: main
source_sha:
code_ref: [src/tiering.py, src/ipc.py, src/notes.py, scripts/run_tiering.py, scripts/build_site.py]
depends_on: [ipc-mirror, ipc.population, ipc.analyses]
discrepancies: []
extra: {}
visibility: public
last_synced: "2026-10-07"
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
