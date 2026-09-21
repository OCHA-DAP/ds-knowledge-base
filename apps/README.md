# apps/

Deployed interactive surfaces — marimo / Dash / Quarto apps on **Azure web apps** or **GitHub Pages**. One page per app.

An app is a **deliverable/deployment**, distinct from a `pipeline` (which transforms data on a schedule). Some apps serve a framework (trigger explorers, monitoring dashboards); others are standalone (viz/explore/validation tools). The canonical *inventory* of what's deployed where lives in [`infrastructure/deployments.md`](../infrastructure/deployments.md) (Azure) and the generated [`infrastructure/pages-registry.md`](../infrastructure/pages-registry.md) (published sites); these pages add the per-app prose (what it shows, data, maintenance). Every live app is a card on the public **team hub** at <https://ocha-dap.github.io/ds-knowledge-base/> — the card's title/blurb come from this page's `purpose` and `surfaces:` entries, so fixing the page fixes the card.

Copy `_TEMPLATE.md` for each. Cross-link the framework/pipeline an app serves (and vice-versa). See [../docs/INGESTION.md](../docs/INGESTION.md).
