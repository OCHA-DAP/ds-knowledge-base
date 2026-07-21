---
content_type: dataset
name: HNRP
aliases: [HRP, HNO, HNRP, "Humanitarian Needs and Response Plan", FTS, "Financial Tracking Service", "HPC / api.hpc.tools", "People in Need", PiN]
provider: "UN OCHA (Humanitarian Programme Cycle / FTS)"
data_type: humanitarian-needs-and-funding
access: public
api: "FTS funding: https://api.hpc.tools/v1/public/  ·  plans/needs: HPC API + https://humanitarianaction.info"
auth: "none (public read)"
formats: [json, csv, xlsx, pdf]
resolution: "country / plan / cluster / admin-1 (needs); flow-level (funding)"
update_cadence: "needs: annual plan cycle (+ revisions); funding: continuous"
license: "open — attribution to OCHA/FTS"
code_ref: "OCHA-DAP/ds-hnrp-mirror"
mirror: "dev DB schema hnrp (plans / plan_caseloads / needs_admin) — see pipelines/hnrp-mirror.md"
mirror_priority: done
used_by:
  - frameworks/hti-hurricanes/2024-08-23.md
  - frameworks/cub-hurricanes/2026-06-17.md
  - frameworks/lac-dry-corridor/2025-02.md
  - frameworks/nga-flooding/2025-08-11.md
  - analysis/nga-cholera.md
last_verified: 2026-07-21
---

# HNRP / HRP — humanitarian needs & response-plan funding

The **Humanitarian Needs and Response Plan** (formerly split into the **HNO** — needs —
and **HRP** — response) is OCHA's annual per-crisis planning document: **People in Need
(PiN)**, targets, severity, and financial requirements. Two data lenses we draw on:

1. **Needs / PiN** — from the **Humanitarian Programme Cycle (HPC)** and published on
   **[humanitarianaction.info](https://humanitarianaction.info)** (per-plan PiN, targets,
   severity, often to admin-1). Used as **denominators and context** (people in need /
   affected) when sizing an activation's caseload.
2. **Funding** — the **Financial Tracking Service (FTS)**: reported flows against each
   plan's requirements. Public API at **`api.hpc.tools/v1/public/`**
   (e.g. `/fts/flow?planid=<id>`, `/plan/year/<yyyy>`). Also mirrored on
   [HDX (`ocha-fts`)](https://data.humdata.org/organization/ocha-fts).

## How we access it

No key needed. FTS via `api.hpc.tools`; plan/needs metadata via the HPC API +
`humanitarianaction.info`; bulk exports via the FTS HDX org.

**Mirrored in the dev DB since 2026-07** by
[`OCHA-DAP/ds-hnrp-mirror`](https://github.com/OCHA-DAP/ds-hnrp-mirror)
(see [pipelines/hnrp-mirror.md](../../pipelines/hnrp-mirror.md)): `hnrp.plans` +
`hnrp.plan_caseloads` (plan/cluster PiN, targets, requirements, FTS funding — all
years) and `hnrp.needs_admin` (HDX HAPI admin-2 PiN by sector/category/status,
2024+). **Read from the DB first**; explorer at
<https://ocha-dap.github.io/ds-hnrp-mirror/>. Query the APIs directly only for
what the mirror doesn't carry (e.g. flow-level FTS, raw disaggregation matrices).

## How we use it

Framing and denominators, not triggers: PiN/targets to contextualise the population a
flood/storm/drought activation would cover, and FTS to characterise the funding gap a
CERF anticipatory allocation sits against.

## Gotchas

- **Plan IDs are the join key** across FTS and HPC — resolve country+year → `planId` first.
- **"HNRP" is the current name**; older years are **HNO + HRP** separately. Terminology and
  plan structure shift between cycles — don't assume field stability year-to-year.
- FTS funding is **as-reported** (donor/agency self-report) — undercounts and lags are
  normal; a low "% funded" is not necessarily a data error.
