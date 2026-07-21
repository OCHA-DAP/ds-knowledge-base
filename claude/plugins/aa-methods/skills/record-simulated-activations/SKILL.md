---
name: record-simulated-activations
description: Set up and record a framework version's trigger structure and simulated (backtested) activations in the authoritative place — the team DB `aa` schema — from WHATEVER source exists — the repo's backtest code/output, an excel/gsheet analysis, or the trigger report PDF. Covers defining a brand-new version from scratch (windows, budgets, spans). Use when a trigger is finalized or endorsed, when asked to "export/register/record" backtest results, or when a version is missing from the trigger-stats page.
---

# Record simulated activations — any source, one destination

The authoritative home for a framework version's trigger-performance record —
its windows (budgets, all-in, analysis spans) and which years/events would
have activated — is the dev DB `aa` schema. The trigger-stats page and
downstream products read from it. This skill gets that record defined and
written correctly from whatever evidence exists. For a **brand-new framework
version this IS the setup**: nothing pre-exists in the DB; the extraction
stage below builds the full window definition, not just the year list.

Two stages, deliberately split:

- **Extraction (you, the model)**: read the source, fill `export.yml`.
- **Writing (the script)**: deterministic, transactional, source-agnostic.
  Never write SQL by hand; never INSERT into `aa.*` directly.

## Stage 1 — extract / define

**Prerequisite**: the KB framework page `frameworks/<kb_framework>/<kb_version>.md`
should exist — it anchors `kb_framework`/`kb_version` (folder name + page
version date, the join key to the KB and the public site). If it doesn't yet,
say so: either the page gets created first (KB worktree + PR) or the export
proceeds with an explicit warning and a KB issue to follow up.

Work down this source ladder; record the rung used (`source:` per window):

1. **`source: repo`** — the spoke repo's own backtest script or output
   (preferred). Run or read the analysis that produced the activation list;
   these are *derived* numbers.
2. **`source: excel` / `source: gsheet`** — a structured trigger-analysis
   workbook or sheet tab the user hands you.
3. **`source: report`** — the published trigger report / framework PDF;
   these are *reported* numbers.

If sources disagree, do NOT pick silently: record the derived years, put the
discrepancy in the window's `note:`, and tell the user (reported-vs-derived
discipline — see `return-periods`).

Fill `export.yml` — the full field reference with an example is in the
exporter's docstring (`--help` / top of the script). Per (framework, version,
country): identity + `kb_status` (`endorsed` or `development` — the
trigger-stats page renders endorsed only), reported overall RP/prob/spend if
stated, and per **window** (define ALL of them — for a new version this is
the trigger structure itself): name, `all_in`, basis, budget USD, **analysis
span** (the RP denominator — wrong span = wrong RP), reported RP/prob, and
the activation list — one entry per year; `label`/`date` for discrete events
like cyclones; two events in one year = one entry, label both.

## Stage 2 — write

```
python ${CLAUDE_PLUGIN_ROOT}/scripts/export_simulated_activations.py export.yml
```

(`--dry-run` first. Needs `pyyaml` + `ocha-stratus`, `DSCI_AZ_DB_DEV_*` write
creds; SSL is set automatically.)

Upserts one (framework, version, country) atomically across all three tables —
`framework_version_map`, `window`, `simulated_activation` (all three or the
version is invisible: the trigger-stats page inner-joins them). Touches no
other rows.

**The exporter validates before writing — fix, don't override:**

- **Identity vs the KB**: the framework page exists in the local KB clone
  (`$KB_REPOS_DIR` → `~/.claude/.kb-repos-dir`) and `country_iso3` matches
  its frontmatter. No clone → warns and skips; missing page → warns (see
  prerequisite); country mismatch → hard error.
- **Internal consistency**: ISO3 shape; dated version for endorsed; ≥1
  window; every activation year inside its window's span; positive budgets;
  recomputed Weibull RPs vs reported (>10% drift → warning) and the
  overall ≤ individual inequality.
- **Existing-data guard**: rows already present for this version → it STOPS
  and prints them (windows, years, source, exported_at). Overwriting a
  `development` export is normal iteration (`--replace`). Overwriting an
  **endorsed** export needs `--force` — first show the user old-vs-new and
  get an explicit yes; a changed backtest after endorsement usually means a
  NEW framework version, not an edit.

**Then check the printout**: it re-queries the views and shows computed
per-window and overall RP/prob next to the reported numbers — confirm they
match the trigger report before calling it done. Downstream is automatic:
`trigger-stats.yml` re-renders `activations.html` daily and on framework-page
edits.

## Gotchas

- Multi-country frameworks: a full export (own `export.yml` or one file per
  country) per `country_iso3`.
- Commit `export.yml` in the spoke repo alongside the trigger analysis — the
  reviewable record of what was exported and its provenance.
- The KB framework page stays the prose home (spec, rationale, narrative);
  its `activations:` frontmatter is REAL activations only — never simulated.
- The historical backfill (`ds-knowledge-base/scripts/aa_crosswalk.csv` +
  `load_aa_performance.py --backfill`) is the same operation run once in
  bulk over the legacy gsheet/excel record — frozen; never add new versions
  there.
- RP method (Weibull, three levels, all-in vs split): the `return-periods`
  skill + KB `methods/return-periods.md`.
