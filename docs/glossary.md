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
- **46/182** — General Assembly resolution 46/182 of 19 December 1991, the framework for UN humanitarian assistance: guiding principles, the ERC, the IASC, consolidated appeals and the (then revolving) CERF. Paragraph citations like `46/182 ¶35(e)` point into its annex: [mandates/ocha.md](../mandates/ocha.md).
- **Humanitarian principles** — humanity, neutrality, impartiality (46/182 ¶2) and independence (added by GA 58/114, 2003); reaffirmed in every annual coordination resolution. [mandates/ocha.md](../mandates/ocha.md) §4.
- **ERC** — the Under-Secretary-General for Humanitarian Affairs and Emergency Relief Coordinator: the official 46/182 ¶34–35 designates, head of OCHA, chair of the IASC, manager of CERF. [mandates/ocha.md](../mandates/ocha.md).
- **OCHA** — the UN Office for the Coordination of Humanitarian Affairs: the ERC's secretariat (46/182 ¶36), reorganised from the Department of Humanitarian Affairs by the 1997 reform and defined by ST/SGB/1999/8. Mandate page: [mandates/ocha.md](../mandates/ocha.md).
- **IASC** — Inter-Agency Standing Committee, established by 46/182 ¶38 under the ERC's chairmanship (UN operational agencies + standing invitation to ICRC, IFRC, IOM). [mandates/ocha.md](../mandates/ocha.md) §1.
- **CERF** — Central Emergency Response Fund: the Revolving Fund of 46/182 ¶22–26 ($50M loan facility), upgraded by GA 60/124 (2005) with a grant element; run by the ERC under Secretary-General's bulletin ST/SGB/2020/5 (eligibility: UN agencies + IOM; Rapid Response / Underfunded Emergencies; $1 billion annual target). [mandates/cerf.md](../mandates/cerf.md). Our allocation mirror: [infrastructure/datasets/cerf-onegms.md](../infrastructure/datasets/cerf-onegms.md).

_(extend during ingestion)_
