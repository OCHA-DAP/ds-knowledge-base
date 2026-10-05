---
name: record-simulated-activations
description: Record or correct a framework version's backtest (trigger windows, analysed years, simulated activation years) in the AA tracking database — an entries file while the version is unsealed, an erratum PR once it is sealed. Use when the user asks to record, update or correct simulated/backtested activations; never write the database directly, and never record a real activation as a simulated one.
---

# Record simulated activations — through ds-aa-tracking, never around it

The backtest record lives in OCHA-DAP/ds-aa-tracking (dev DB `aa`): per framework version,
`window` (each trigger window with its **analysed years** — the return-period denominator),
`simulated_activation` (the years the trigger *would have* fired) and
`version_performance_reported` (published headline RP / probability / spend). That repo owns
the tables and every write path; its `backtests/README.md` is the reference. This skill
prepares what goes through those paths.

**Explicit ask only, one version per go-ahead.** A finished backtest is a reason to *offer*
("the backtest changed — update the draft record?"), not to write.

## 1. Find the version and its state

Identity is `(country_iso3, hazard, version)` as in `aa.framework_version` (look it up on the
tracking site's admin page, or ask). Then its state:

| `kb_status` / `backtest_sealed_at` | Path |
|---|---|
| development, or endorsed and unsealed | **entries file** (step 3) — iterate freely |
| endorsed, record now matches the endorsed document in full | entries file if needed, then a **seal** (step 4) |
| sealed | **erratum** (step 5) — the database refuses anything else |

A version entered under a placeholder label (`2026`) that has since been endorsed gets
relabelled to its endorsement date first (`databricks/nightly.py --relabel`, in ds-aa-tracking)
— before any seal.

## 2. Extract, with provenance

Source ladder, recorded per window in `window.source`: `repo` (the spoke repo's backtest code
or output — *derived*) › `excel` / `gsheet` (a workbook the user hands you) › `report` (the
endorsed document's table — *reported*). When they disagree, record the derived years, put
the conflict in `window.note`, and tell the user — never pick silently (`return-periods`).

Per window: name, `all_in`, `basis`, **`analysis_start` / `analysis_end`**, reported RP/prob
when stated, and the years. Every simulated year must lie **inside** the span — the database
rejects anything else. A year after the analysed span, or a real activation of the version
itself, is not a backtest year: it belongs in `window_activation`. Seasons that straddle two
years are labelled the way the source labels them; say which in `source_note`.

## 3. Unsealed: an entries file

JSON for `scripts/apply_entries.py` (ds-aa-tracking) — `op: replace` makes the given rows the
version's rows, so years that dropped out of a re-run disappear too:

```json
{"entered_by": "who, from what (repo@commit / workbook / document page)",
 "rows": [
  {"op": "replace", "table": "window",
   "scope": {"country_iso3": "UGA", "hazard": "flood", "version": "2026"},
   "rows": [{"country_iso3": "UGA", "hazard": "flood", "version": "2026", "window_name": "…",
             "all_in": false, "basis": "forecast", "analysis_start": 2003, "analysis_end": 2025,
             "source": "repo"}]},
  {"op": "replace", "table": "simulated_activation",
   "scope": {"country_iso3": "UGA", "hazard": "flood", "version": "2026"},
   "rows": [{"country_iso3": "UGA", "hazard": "flood", "version": "2026", "window_name": "…",
             "event_year": 2007, "time_precision": "year", "source_note": "…"}]}]}
```

Before uploading, show the user the file, what it changes against the current record (the
tracking site, or a snapshot restored locally), and the recomputed RPs (Weibull, `return-periods`).
On their yes, from a ds-aa-tracking clone: `uv run python scripts/apply_entries.py --upload FILE`
(private dev blob — never commit it to the public repo). The nightly job applies it (03:30 UTC);
`--dry-run --dir` against a restored snapshot checks it first. One `country_iso3` per scope —
multi-country frameworks get one replace per country.

## 4. Seal

When an endorsed version's record matches its endorsed document's table in full (every window,
span, years), propose a PR in ds-aa-tracking adding it to a `backtests/seals/*.json` file with
`against` = the document link + page. After that, step 5 is the only way in.

## 5. Sealed: an erratum PR

`backtests/errata/<YYYY-MM-DD>-<iso3>-<hazard>-<version>.json` in ds-aa-tracking, reviewed in a
pull request, applied by the nightly job — format in `backtests/README.md`:

- **transcription** — the database doesn't match the endorsed document: `changes` (delete /
  update / insert by primary key), `reason`, `evidence` (document + page).
- **analysis-note** — the endorsed backtest itself is wrong: no changes; it is recorded and
  shown. The fix is a **new version** — endorsed numbers are what was approved and budgeted on.

Errata are immutable once applied; a later fix is a new file. For a version whose document is
not public, the erratum goes on the private blob (`projects/ds-aa-tracking/errata/`), not the
public repo. Never work around the seal (no hand-set `aa.erratum_id`, no direct SQL).
