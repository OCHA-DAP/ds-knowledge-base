# Glossary

Short definitions of recurring terms. Add as ingestion surfaces them; where a page owns the full story, delegate with a link rather than duplicating.

- **AA** — Anticipatory Action. Acting on a forecast/trigger *before* a shock hits.
- **Framework** — a country/hazard AA design: the trigger, the activation, the monitoring.
- **Trigger** — the rule that decides whether to activate. Canonical definition is the code, not prose. Full vocabulary (mechanism vs specific triggers, "activated") in [methods/trigger-design.md](../methods/trigger-design.md).
- **Readiness trigger / action trigger** — two distinct named triggers in a framework: an earlier *readiness* signal (mobilise, pre-position) and a later *action* trigger (release funds and act). FR: *déclencheur de mobilisation* / *déclencheur d'action*.
- **Trigger window** — the calendar period a specific trigger monitors (a framework's windows can differ by hazard season, region, or leadtime; `n_windows` in frontmatter).
- **Activation history — real vs simulated** — validated frameworks record both what *did* activate and what *would have* activated over history (the mandatory backtest against BOTH impact and indicator records; see [methods/trigger-design.md](../methods/trigger-design.md)).
- **Return period** — the average interval between events of a given severity (e.g. 1-in-5-year). Three levels — *individual*, *overall*, *effective* — with fixed ≤/≥ relations: [methods/return-periods.md](../methods/return-periods.md).
- **All-in vs split funding** — whether the full allocation releases on any activation (*all-in*, `all_in` in frontmatter) or is split across windows/triggers; changes the effective return period ([methods/return-periods.md](../methods/return-periods.md)).
- **Hub / spoke** — this KB is the *hub* (summaries, cross-links, comparison); the `ocha-dap` repos are the *spokes* (deep, code-adjacent detail). One home per fact.
- **Drift** — a KB page going stale against its source (spoke code moved, a newer PDF published, infra changed). Detected, never silently auto-fixed: [infrastructure/automation.md](../infrastructure/automation.md).
- **CODAB** — Common Operational Dataset, Administrative Boundaries.
- **valid_time / issued_time / leadtime** — see [infrastructure/conventions.md](../infrastructure/conventions.md).

_(extend during ingestion)_
