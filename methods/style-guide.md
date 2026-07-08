---
content_type: method
last_reviewed: "2026-07-08"   # bump when a human verifies the page is still accurate
---

# Style guide — the HDX v2 design system

**Default style reference for pretty much everything the team builds** (maintainer decision,
2026-07-08): apps, dashboards, public sites, dataviz. When styling anything, start from the
HDX v2 design system rather than inventing colors/type/spacing.

## What it is

HDX's v2 component library and design foundation: token-based **color ramps** (`--hdx-brand-*`,
primary, neutral, success/warning/error — 0→10 scales), **typography** (Merriweather display,
Roboto heading/body/links, named type-style mixins), **spacing scale, elevation (shadows),
radius**, and ~22 specced components (buttons, cards — KPI/activity/dataset/resource/signal,
inputs, tables, drawers, accordions, navigation, …) with a stable BEM class vocabulary
(`c-button--primary`, `c-kpi-card`, …).

## Where it lives (access)

- **The source** is a *gated staging site* (HTTP basic auth) — not public, so the KB carries
  the greppable mirror in the **private companion repo**:
  **`ds-knowledge-base-internal/style-reference/`** — `tokens.md` (all 482 tokens by family),
  `components.md` (component inventory + class vocabulary), `raw/` (the page + v2 CSS bundles
  verbatim). The URL and credentials are in that folder's README (team GitHub access = access).
- **Refresh:** `scripts/gen_style_reference.py` (this repo) re-mirrors on demand — see the
  mirror README. Re-run when HDX ships design-system changes.
- Through the **internal MCP / chatbot** the mirror is bundled and searchable directly.

## How to use it (humans and agents)

1. **Grep `tokens.md` first** — use token *names* (CSS custom properties) over hex values, so
   outputs track the design system when it changes.
2. **Check `components.md`** for an existing component + its classes before hand-rolling one;
   `raw/*.css` has the implementation when you need exact styles outside an HDX page.
3. For plots/dataviz: pull palette ramps from the color tokens (brand ramp for sequential,
   success/warning/error for status), Roboto for chart text.
4. Marimo/Dash apps can't import the HDX CSS wholesale — lift the *tokens* (colors, type,
   spacing) into the app's stylesheet and note the source.

_Provenance: HDX v2 staging `/components` (Foundation + component demos). This page is the
public-safe pointer; the substance lives in the internal mirror._
