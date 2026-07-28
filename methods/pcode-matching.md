---
content_type: method
last_reviewed: "2026-07-22"   # bump when a human verifies the page is still accurate
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

## The four mismatch classes (all seen in real data, July 2026)

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

3. **Non-geographic placeholders** — plan-wide caseloads not attributed to any admin unit:
   `*-XXX` codes ("UNSPECIFIED"), Mali's `ML21` "PDI land" IDP bucket. *Fix:* drop them,
   **loudly** (log the code, name, and population size) — silently keeping them creates
   ghost rows; silently dropping them hides caseload.

4. **Population-group semantics** (HPC severity / needs data specifically) — groups do not
   mean the same thing across plans: some publish one overall group (blank or
   `Global_Population`), some publish **overlapping unions** (Cameroon: "IDPs, Returnees,
   Host communities" vs "…, Refugees, …" — summing double-counts; take the most inclusive),
   and some publish **disjoint displacement categories** (Mali: PDI / Rapatriés / Communauté
   Hôte — these partition the analysed population and must be summed; Mali's blank group
   contains *only* the placeholder, so "prefer the overall group" returns an empty country).
   *Fix:* choose per country by coverage: overall group only if it actually covers the
   country's units; else the most inclusive union if group names contain commas; else sum.

## The audit (run it before trusting any p-code join)

Per country and per source: compare the distinct p-code sets, print match counts and the
unmatched codes **with their names from both sides**. Names are what turn "65 unmatched"
into "oh, Chad is ISO3-prefixed and Mali had a reform". Then make the pipeline itself print
a **coverage report on every run** — any humanitarian unit lacking forecast data or a
polygon — so vintage drift surfaces the month it happens instead of silently shrinking the
analysis.

## Related

- [infrastructure/datasets/](../infrastructure/datasets/) — the HRP/HNRP and HDX source pages.
- [`ds-hnrp-mirror`](https://github.com/OCHA-DAP/ds-hnrp-mirror) — HPC/HAPI mirror this was
  built against (`hpc.needs_admin`, `hpc.severity_admin`).
- [pipelines/raster-stats.md](../pipelines/raster-stats.md) — where `public.polygon` and the
  zonal-stats p-codes come from.
