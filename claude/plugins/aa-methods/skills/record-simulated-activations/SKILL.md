---
name: record-simulated-activations
description: Write a framework version's backtest (trigger windows, analysed years, simulated activation years) to the AA tracking database, applied immediately from any repo. Resolves the exact registered version first and treats it by state — a version in development is rewritten freely; an endorsed one only from its endorsed document, named explicitly, then sealed; a sealed one only by an erratum PR. Use when the user asks to record, update or correct simulated/backtested activations; never record a real activation as a simulated one.
---

# Record simulated activations — into the right version

The backtest record lives in OCHA-DAP/ds-aa-tracking (dev DB `aa`), per **framework version**:
`window` (each trigger window with its **analysed years** — the return-period denominator),
`simulated_activation` (the years the trigger *would have* fired) and
`version_performance_reported` (published headline RP / probability / spend).

This skill writes it **now**, from whatever repo you are in, with the bundled client
`${CLAUDE_PLUGIN_ROOT}/scripts/aa_entries.py` → the tracking proxy. Never connect to the
database yourself or write SQL.

**Explicit ask only, one version per go-ahead.** A finished backtest is a reason to *offer*
("the backtest changed — update the draft record?"), not to write.

## 1. Which version? Ask the registry — never the repo you are in

A framework is a `(country_iso3, hazard)` pair; it has one row per version in
`aa.framework_version`, and the target of every write is one exact key
`ISO3/hazard/version`. The folder, repo or branch you happen to be in says nothing reliable
about which one. Look it up, every time:

```
python ${CLAUDE_PLUGIN_ROOT}/scripts/aa_entries.py --versions HTI          # every framework of a country
python ${CLAUDE_PLUGIN_ROOT}/scripts/aa_entries.py --versions HTI/storm    # one framework
```

It lists each registered version with its **role** — *development (a revision of X)*,
*endorsed — the latest endorsed version*, *endorsed — superseded by Y* — its validity, document, whether its
backtest is **sealed**, and the backtest recorded now. Then:

- **Copy the key from that list; never compose one.** A label does not tell you the status:
  an endorsed version is labelled by its endorsement date, a development one may be `2026` or
  a date (`HTI/storm/2026-06-09` is in development; `HTI/storm/2024-08-23` is endorsed). The
  hazard word is the registry's (`storm`, `flood`, `drought`, `cholera` …), and a regional
  framework is one framework per country (`GTM/drought`, `HND/drought`, `SLV/drought`): each
  country's backtest goes to its own key.
- **Say the target back to the user and get a yes to that exact key** — "the *development*
  revision of the Haiti storm framework, `HTI/storm/2026-06-09` — not the endorsed
  `2024-08-23`". When a framework has both an endorsed version and one in development, a
  backtest that is still being iterated belongs to the **development** one.
- **Not in the list → stop.** This skill never creates a version and never picks "the closest".
  A new revision is registered on the tracking site (entry / admin page) with status
  `development` first; then come back.

The server holds you to it: a key that is not registered is refused, with the real ones listed.

## 2. What happens, by the state of that version

| The target is… | What you do | The user confirms | Command |
|---|---|---|---|
| **in development** (or pre-development) | Write freely. Each write replaces the version's windows and years as a set; re-run as often as the analysis changes. | the key, and the dry-run diff | `FILE`, then `FILE --write` |
| **endorsed, not sealed** | A *backfill of the endorsed record*, not iteration: the years are the ones in the endorsed document's table (or the analysis behind it, checked against that table). Name the version explicitly. When the record then matches the document in full, **seal it in the same write**. | "this is the ENDORSED version — yes", the diff, and what it was checked against | `FILE --write --endorsed KEY` + `--seal "document link + page"` |
| **endorsed and sealed** | No write. If the database doesn't match the endorsed document: an erratum PR (§5). If the *analysis* changed: that is a new version, not an edit. | — | — |
| not registered, or status not set | Stop; it is fixed on the tracking site. | — | — |

These are enforced by the proxy and the database, not by this text: an endorsed version is
refused unless `--endorsed` names it; `--endorsed` naming a version that is in development is
refused too (your belief about the target was wrong — look again); a sealed backtest is
refused from every writer; a simulated year outside its window's analysis span is refused; a
window can't be dropped from under its years. A refusal writes nothing.

At endorsement: the version's status (and its label, from the placeholder to the endorsement
date) is changed on the tracking side first. Then write the final backtest from the endorsed
document with `--endorsed KEY --seal …` — from then on it is the sealed record.

## 3. Extract, with provenance

Source ladder, recorded per window in `window.source`: `repo` (the spoke repo's backtest code
or output — *derived*) › `excel` / `gsheet` (a workbook the user hands you) › `report` (the
endorsed document's table — *reported*). When they disagree, record the derived years, put the
conflict in `window.note`, and tell the user — never pick silently (`return-periods`). For an
endorsed version the document's table is the reference.

Per window: name, `all_in`, `basis`, **`analysis_start` / `analysis_end`**, reported RP/prob
when stated, and the years. A year after the analysed span, or a real activation of the version
itself, is not a backtest year — it belongs in `window_activation`. Seasons straddling two
years are labelled the way the source labels them; say which in `source_note`.

## 4. Write: dry run, show, apply

One file per version. `op: replace` makes the given rows the version's rows, so years that
dropped out of a re-run disappear too; replace `window` and `simulated_activation` together:

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

Keep it in a temp file (a payload, not a repo artifact). Then:

```
python ${CLAUDE_PLUGIN_ROOT}/scripts/aa_entries.py FILE            # dry run on the live DB
python ${CLAUDE_PLUGIN_ROOT}/scripts/aa_entries.py FILE --write    # apply (see §2 for flags)
```

The dry run applies the file in a transaction, runs every check, rolls back, and prints —
first — the **TARGET** line: the version the file touches, its role, document, seal, and its
other versions; then the changes (years out / in per window) and the recomputed return
periods. **Show the user the TARGET line and the changes as printed**, and write only on their
yes to that target. If the TARGET is not the version you agreed in §1, stop — the file is
wrong, not the registry.

Writes are audited under `entered_by`. The database has the change at once; the tracking
*site* shows it after its next nightly publish.

Token: the tracking site's editor token (the one its admin page asks for), in
`AA_TRACKING_EDITOR_TOKEN` or `~/.config/ds-aa-tracking/editor-token`. If the user has none,
ask them to add it — never print it. If the proxy is unreachable, say so and stop; don't
look for another route.

## 5. Sealed: an erratum PR

`backtests/errata/<YYYY-MM-DD>-<iso3>-<hazard>-<version>.json` in ds-aa-tracking, reviewed in a
pull request, applied by its nightly job — format in its `backtests/README.md`:

- **transcription** — the database doesn't match the endorsed document: `changes` (delete /
  update / insert by primary key), `reason`, `evidence` (document + page).
- **analysis-note** — the endorsed backtest itself is wrong: no changes; it is recorded and
  shown. The fix is a **new version** — endorsed numbers are what was approved and budgeted on.

Errata are immutable once applied; a later fix is a new file. A version whose document is not
public: the erratum goes on the private blob (`projects/ds-aa-tracking/errata/`), not the public
repo. Never work around a seal.
