---
content_type: method
last_reviewed: "2026-08-07"   # bump when a human verifies the page is still accurate
---

# P-code matching — joining admin-level datasets without losing people

Any analysis that joins two admin-level datasets on p-codes (forecast × PiN, exposure ×
severity, IPC × anything) inherits every difference between their boundary vintages. The
failure modes are mostly **silent**: populations drop out of the join, or — worse — land on
the wrong polygon. This page catalogues the mismatch classes we have actually hit, the audit
that finds them, and the fix ladder. Reference implementation:
[`ds-seas5-skill/pipeline/export_hnrp_drought.py`](https://github.com/OCHA-DAP/ds-seas5-skill/blob/main/pipeline/export_hnrp_drought.py)
(`normalize_pcodes` + `REFORM_XWALK`), built for the July 2026 forecast × HNRP overlay.

## Our canonical reference

The team's admin-boundary spine is the **COD shapefiles in the `polygon` blob container**
(`{iso3}_shp.zip`, prod) and the derived **`public.polygon`** table in the rasterstats DB —
these are the polygons all our zonal statistics (`public.seas5/era5/imerg/floodscan`) were
computed on, so their p-codes match our data **by construction**. Anything external (HPC,
HAPI, IPC, partner data) must be reconciled *to* that vintage, not the other way round.

Caveat: the blob CODs are a **frozen vintage**. Countries reorganise; the CODs on HDX move
on; ours don't until someone re-runs the raster-stats `--update-metadata` bootstrap and the
zonal stats. Check `public.polygon` before assuming a new admin unit exists for us.

## The mismatch classes (all seen in real data, July–August 2026)

1. **Code style** — same units, different rendering. HPC/HAPI often prefix with ISO3 where
   the COD uses ISO2 (`TCD01` vs `TD01` — all 23 of Chad; `NER001` vs `NE001` — all of
   Niger), and zero-padding varies (`CO5` vs `CO05`). *Fix mechanically and generically:*
   derive each country's reference style (alpha prefix + digit width) from your reference
   codes and re-render the incoming code — don't hardcode country lists. A unique
   accent-folded name match catches renumberings (`GT23` "Quiché" → `GT14`).

2. **Admin reforms newer than the reference vintage** — new units split from old ones, and
   sometimes **codes are reused with different meanings**. Known instances:

   | Country | Reform | Hazard |
   |---|---|---|
   | Mali | 2023: 10 regions → 19 + Bamako. `ML11–ML19` are splits (Nioro⊂Kayes, Kita⊂Kayes, Dioïla/Nara⊂Koulikoro, Bougouni/Koutiala⊂Sikasso, San⊂Ségou, Douentza/Bandiagara⊂Mopti) | **`ML09` reused**: old vintage = Bamako, new = Taoudenni; `ML20` = new Bamako. A naive code join books Taoudenni's caseload to Bamako. |
   | Burkina Faso | 2024: 13 → 17 regions. `BF46/BF52/BF56` dissolved into splits (`BF61/62`⊂Boucle du Mouhoun, `BF58/60/63`⊂Est, `BF59/64`⊂Sahel) | Surviving codes were **renamed** (BF13 Centre→Kadiogo etc.) with approximately-old boundaries — code-for-code join is right, name join is wrong. |
   | CAR | 2020: Ouham-Fafa (`CF33`) split from Ouham (`CF32`), Lim-Pendé (`CF34`) from Ouham-Pendé (`CF31`) | — |

   *Fix:* an explicit crosswalk mapping each new/reused code to the old unit that
   **contains** it, with a name guard wherever a code is reused across vintages. Mapping
   splits to parents keeps population attributed (the "rump" old-code rows undercount
   otherwise) at the cost of resolution — acceptable until the boundary vintage is updated.

3. **Placeholders — but there are TWO kinds, and they need opposite treatment.**

   *(a) Non-geographic buckets* — plan-wide caseloads not attributed to any admin unit:
   `*-XXX` codes named "UNSPECIFIED", Mali's `ML21` "PDI land" IDP bucket. Drop them,
   **loudly** (log the code, name, and population size) — silently keeping them creates
   ghost rows; silently dropping them hides caseload.

   *(b) A whole country shipped under ONE placeholder* — HAPI does this wherever it could
   not p-code a source: every area of Madagascar, Tanzania, Lesotho, Djibouti, Burundi and
   Eswatini arrives as `MDG-XXX`, `TZA-XXX`… **with its real admin name in the name
   column**. These are genuine units, and dropping them loses the country outright — ~9.4M
   people in IPC phase 3+ were invisible in the seas5-skill overlay for exactly this.

   **The dangerous part is not the drop, it is the aggregation.** Any `groupby`/`pivot`
   keyed on the p-code silently **sums the entire country into one row** and labels it with
   whichever area name sorts first. Madagascar arrived as a single row holding all 32.7M
   analysed and 2.57M in phase 3+, named "MENABE". Name-match that row onto a polygon and
   you have painted a country's caseload onto one region — the same shape as the Venezuela
   mis-attribution, and equally invisible to national-total checks, because the national
   total is exactly right.

   *Fix:* when the code cannot separate areas, **key the aggregation on the name instead**,
   then name-match each area to a p-code. Detect it rather than hardcoding: all rows in the
   group carry a `*-XXX` code AND the group holds more than one distinct name.

4. **Population-group semantics** (HPC severity / needs data specifically) — groups do not
   mean the same thing across plans: some publish one overall group (blank or
   `Global_Population`), some publish **overlapping unions** (Cameroon: "IDPs, Returnees,
   Host communities" vs "…, Refugees, …" — summing double-counts; take the most inclusive),
   and some publish **disjoint displacement categories** (Mali: PDI / Rapatriés / Communauté
   Hôte — these partition the analysed population and must be summed; Mali's blank group
   contains *only* the placeholder, so "prefer the overall group" returns an empty country).
   *Fix:* choose per country by coverage: overall group only if it actually covers the
   country's units; else the most inclusive union if group names contain commas; else sum.

5. **The analysis unit is not an admin unit at all.** Some IPC/CH analyses are run on
   **livelihood or agro-ecological zones**, not administrative areas: Burundi publishes
   `Imbo`, `Crête Congo-Nil`, `Plateaux humides`, `Buragane`; Eswatini's current analysis is
   `Lubombo plateau` and `Timber highlands`. No amount of p-code or name work will map
   these — there is no admin polygon for them. Distinguish this from a matching *failure*
   before spending effort on it, and say so in the output: "not matched" and "not an admin
   unit" are different facts. Beware the mixed case — Eswatini's table also contains its
   four real regions (`Hhohho`, `Lubombo`, `Manzini`, `Shiselweni`), just not at the level
   the current analysis publishes.

## Name matching: four traps, all hit in one afternoon

Name matching is the fallback when codes cannot be reconciled. It works, but every one of
these cost a debugging round:

- **Match against the table the matcher actually uses.** The same unit is spelled
  differently across our own tables: `pop.population_admin` has `Ali Sabeh` / `Dilkhil`,
  `public.polygon` has `Ali Sabieh` / `Dikhil`. Aliases written against the wrong one are
  silent no-ops.
- **Write aliases in the fold's own form.** Our `_fold` strips accents and casefolds but
  **keeps spaces** — `"Djibouti Ville"` folds to `djibouti ville`, not `djiboutiville`. An
  alias keyed without the space never fires, and only the single-word entries appear to
  work, which reads like a partial data problem rather than a typo.
- **Scope the collision guard to the row's identity, not the unit.** The guard that stops
  two rows landing on one polygon must key on whatever makes rows distinct. IPC ships one
  row per unit **per (type, validity window)**, so a unit matched in one period blocked
  itself in every later one — 148 legitimate matches lost, most of Madagascar's.
- **A split is not a rename.** Madagascar's `VATOVAVY` and `FITOVINANY` are the two halves
  of the old `Vatovavy Fitovinany`. Aliasing both onto the old unit silently drops one (the
  collision guard blocks the second); it needs the crosswalk-plus-sum of class 2, or
  honest exclusion. Renames *are* safe as aliases: `MATSIATRA AMBONY` = `Haute Matsiatra`.

## Verify with the source's own totals, per period

Match counts do not tell you whether the values landed correctly — the Madagascar collapse
had a perfect national total while every unit was wrong. **Sum your matched units for one
analysis period and compare against the source's published national figure for that same
period.** Ratio 1.000 is the pass; anything else is a coverage gap you can now name:

| | units | ours | source | ratio |
|---|---:|---:|---:|---:|
| Lesotho | 10 | 234,468 | 234,468 | 1.000 |
| Djibouti | 6 | 229,659 | 229,660 | 1.000 |
| Madagascar | 20 | 1,955,687 | 2,124,101 | 0.921 — the split + 2 post-vintage regions |

## Three gates stand between a source row and the map

A row can clear p-code matching and still show nothing. Check all three before concluding
the data is missing:

1. **A p-code that normalises** to the reference vintage (this page).
2. **A polygon in the published geometry.** In seas5-skill the geojson is a *cached
   artifact* rebuilt only with `--rebuild-geometry`, so a country that newly enters scope
   produces rows with **no geometry** until someone rebuilds — invisible on the map while
   looking perfectly healthy in the payload. Assert `rows − polygons == 0` in the export.
3. **Zonal statistics for the hazard.** Lesotho and Burundi have COD polygons and IPC data
   but **no admin-1 SEAS5 skill**, so they cannot appear on a forecast overlay whatever the
   p-codes do. Check the skill parquet, not just the boundary table — and check the right
   one: `skill_stats_detrended.parquet` is keyed by ISO2 **country**, the admin-level data
   is in `..._adm1/adm2.parquet`.

## The audit (run it before trusting any p-code join)

Per country and per source: compare the distinct p-code sets, print match counts and the
unmatched codes **with their names from both sides**. Names are what turn "65 unmatched"
into "oh, Chad is ISO3-prefixed and Mali had a reform". Then make the pipeline itself print
a **coverage report on every run** — any humanitarian unit lacking forecast data or a
polygon — so vintage drift surfaces the month it happens instead of silently shrinking the
analysis.

## Related

- [absent-data.md](absent-data.md) — the sibling failure: once matched, missing data must
  not render as a benign value. Unmatched units and unassessed units look identical on a
  map unless you make them look different.
- [infrastructure/datasets/](../infrastructure/datasets/) — the HRP/HNRP and HDX source pages.
- [`ds-hnrp-mirror`](https://github.com/OCHA-DAP/ds-hnrp-mirror) — HPC/HAPI mirror this was
  built against (`hpc.needs_admin`, `hpc.severity_admin`).
- [pipelines/raster-stats.md](../pipelines/raster-stats.md) — where `public.polygon` and the
  zonal-stats p-codes come from.
