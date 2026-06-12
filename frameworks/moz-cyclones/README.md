# Mozambique cyclones (moz-cyclones)

Tropical-cyclone AA across the coastal provinces. Two repos: `ocha-dap/ds-aa-moz-cyclones` (analysis, stale) + `ocha-dap/ds-aa-moz-cyclones-monitoring` (live pipeline). The **Action** trigger runs externally in INAM's PRISM.

**Current version: [2026-01-09](2026-01-09.md)** (status: active, two seasons 2025/26–2026/27).

## Version lineage

| version | doc | threshold design | scope |
|---|---|---|---|
| 2025-01-17 | [unocha](https://www.unocha.org/publications/report/mozambique/mozambique-anticipatory-action-and-early-response-framework-cyclones-9-january-2025) | two-threshold (89/118 km/h) | fewer provinces |
| 2025-05-23 (pamphlet) | [unocha](https://www.unocha.org/attachments/88349725-4b56-4372-acab-fdabae76a6a2/OCHA_Pamphlet-AA-Mozambique_final.pdf) | — | — |
| **2026-01-09** | [reliefweb](https://reliefweb.int/report/mozambique/mozambique-anticipatory-action-framework-cyclones-2026) | **single 119 km/h** | **all 8 coastal provinces** |

⚠️ Both repos still implement the pre-2026 two-threshold design — see [version page discrepancies](2026-01-09.md).

Live pipeline: [pipelines/moz-cyclones-monitoring](../../pipelines/moz-cyclones-monitoring.md).
