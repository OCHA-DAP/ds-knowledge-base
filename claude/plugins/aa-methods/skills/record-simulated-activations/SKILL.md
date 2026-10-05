---
name: record-simulated-activations
description: Write a framework version's backtest (trigger windows, analysed years, simulated activation years) to the AA tracking database, applied immediately from any repo — through ds-aa-tracking's proxy, checked against the live database first. Sealed (endorsed, document-checked) backtests take an erratum PR instead. Use when the user asks to record, update or correct simulated/backtested activations; never record a real activation as a simulated one.
---

# Record simulated activations — straight into the tracking database

The backtest record lives in OCHA-DAP/ds-aa-tracking (dev DB `aa`): per framework version,
`window` (each trigger window with its **analysed years** — the return-period denominator),
`simulated_activation` (the years the trigger *would have* fired) and
`version_performance_reported` (published headline RP / probability / spend).

This skill writes it **now**, from whatever repo you're in, with the bundled client
`${CLAUDE_PLUGIN_ROOT}/scripts/aa_entries.py` → the tracking proxy's `POST /entries`. The
database enforces the rules for every writer, so a bad file fails whole and nothing is
written: a **sealed** backtest refuses all changes, and every simulated year must lie inside
its window's analysis span. Never connect to the database yourself or write SQL.

**Explicit ask only, one version per go-ahead.** A finished backtest is a reason to *offer*
("the backtest changed — update the draft record?"), not to write.

## 1. Identify the version and its state

Identity is `(country_iso3, hazard, version)` as in `aa.framework_version` (the tracking site's
admin page, or ask). `version` is the registry label — the endorsement date, or a placeholder
like `2026` while in development.

| State | Path |
|---|---|
| development, or endorsed and unsealed | write it (steps 2–3) — iterate freely |
| endorsed, record now matches the endorsed document in full | write if needed, then propose a **seal** (step 4) |
| sealed (`backtest_sealed_at` set — the dry run says so) | **erratum PR** (step 5) |

A placeholder-labelled version that has been endorsed is relabelled to its endorsement date
first (`databricks/nightly.py --relabel` in ds-aa-tracking) — before any seal.

## 2. Extract, with provenance

Source ladder, recorded per window in `window.source`: `repo` (the spoke repo's backtest code
or output — *derived*) › `excel` / `gsheet` (a workbook the user hands you) › `report` (the
endorsed document's table — *reported*). When they disagree, record the derived years, put the
conflict in `window.note`, and tell the user — never pick silently (`return-periods`).

Per window: name, `all_in`, `basis`, **`analysis_start` / `analysis_end`**, reported RP/prob
when stated, and the years. A year after the analysed span, or a real activation of the version
itself, is not a backtest year — it belongs in `window_activation`. Seasons straddling two
years are labelled the way the source labels them; say which in `source_note`.

## 3. Write: dry run, show, apply

Build the entries file — `op: replace` makes the given rows the version's rows, so years that
dropped out of a re-run disappear too (one `country_iso3` per scope; multi-country frameworks
get one replace per country):

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

Keep it in a temp file (it's a payload, not a repo artifact). Then:

```
python ${CLAUDE_PLUGIN_ROOT}/scripts/aa_entries.py FILE           # dry run against the live DB
python ${CLAUDE_PLUGIN_ROOT}/scripts/aa_entries.py FILE --write   # apply
```

The dry run applies the file in a transaction, runs every check, rolls back and prints what
would change (rows out / in, field old → new). Show it to the user with the recomputed RPs
(Weibull, `return-periods`); `--write` only on their yes. Writes are audited under
`entered_by`. The tracking **site** shows the change after its next nightly publish; the
database has it at once.

Token: the tracking site's editor token (the one its admin page asks for), in
`AA_TRACKING_EDITOR_TOKEN` or `~/.config/ds-aa-tracking/editor-token`. If the user has none,
ask them to add it — never print it. If the proxy is unreachable, the fallback is the same
file uploaded to the private blob (`uv run python scripts/apply_entries.py --upload FILE` from
a ds-aa-tracking clone), applied by the nightly job (03:30 UTC).

## 4. Seal

When an endorsed version's record matches its endorsed document's table in full (every window,
span, years), propose a PR in ds-aa-tracking adding it to a `backtests/seals/*.json` file with
`against` = the document link + page. After that, only step 5 can change it.

## 5. Sealed: an erratum PR

`backtests/errata/<YYYY-MM-DD>-<iso3>-<hazard>-<version>.json` in ds-aa-tracking, reviewed in a
pull request, applied by the nightly job — format in its `backtests/README.md`:

- **transcription** — the database doesn't match the endorsed document: `changes` (delete /
  update / insert by primary key), `reason`, `evidence` (document + page).
- **analysis-note** — the endorsed backtest itself is wrong: no changes; it is recorded and
  shown. The fix is a **new version** — endorsed numbers are what was approved and budgeted on.

Errata are immutable once applied; a later fix is a new file. A version whose document is not
public: the erratum goes on the private blob (`projects/ds-aa-tracking/errata/`), not the public
repo. Never work around the seal.
