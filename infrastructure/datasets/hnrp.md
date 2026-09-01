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
mirror: "dev DB schema hpc (plans / plan_caseloads / needs_admin / severity_admin / pin_admin, plus monitoring_admin / monitoring_national / monitoring_periods from the GHO response-monitoring dashboard) — see pipelines/hnrp-mirror.md"
mirror_priority: done
used_by:
  - frameworks/hti-hurricanes/2024-08-23.md
  - frameworks/cub-hurricanes/2026-06-17.md
  - frameworks/lac-dry-corridor/2025-02.md
  - frameworks/nga-flooding/2025-08-11.md
  - analysis/nga-cholera.md
  - analysis/fts-us-award-funding.md
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
(see [pipelines/hnrp-mirror.md](../../pipelines/hnrp-mirror.md)): `hpc.plans` +
`hpc.plan_caseloads` (plan/cluster PiN, targets, requirements, FTS funding — all
years), `hpc.needs_admin` (HDX HAPI admin-2 PiN by sector/category/status,
2024+), and from the per-country JIAF workbooks `hpc.severity_admin`
(intersectoral final severity 1–5) + `hpc.pin_admin` (overall PiN per admin
area × population group; 2026 rows carry own severity → PiN-by-severity
distribution). **Read from the DB first**; explorer at
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
- Subnational plan figures do **not** always reach the plan's published national PiN —
  the workbook is an allocation over its own analysis scope. Checked 2026-08 against HPC:
  ten countries reconcile at 1.00 (Sudan to the person) but Mali reaches 0.67 of its
  headline, Mozambique 0.70, Chad 0.76, CAR 0.79, Somalia 0.84. Never present a
  subnational sum as the plan total.
- A released plan can publish **no subnational figures at all** — for 2026, Burkina Faso,
  Myanmar, Ukraine and Venezuela. Absent ≠ zero need; see
  [methods/absent-data.md](../../methods/absent-data.md).
- **2026 has no subnational targeted anywhere** (checked four ways: `needs_admin` TGT,
  HAPI, HPC v2 API, humanitarianaction.info). Targeting exists only as a national total,
  because the 2026 subnational figures come from the JIAF needs analysis, which publishes
  PiN by severity and no targets. Do not carry 2025 targets forward: 2025 subnational sums
  match 2025 national totals exactly, not 2026's.
