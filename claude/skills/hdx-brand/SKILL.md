---
name: hdx-brand
description: Apply the team's HDX v2 design system when styling ANYTHING visual — charts, dashboards, marimo/Dash apps, reports, HTML artifacts, slides. Use BEFORE choosing colors, fonts, spacing, or components so outputs follow OCHA/HDX branding instead of invented styles.
---

# HDX v2 branding

The team style reference is the HDX v2 design system. The greppable mirror lives in the
INTERNAL repo (classification follows the gated source):

- `ds-knowledge-base-internal/style-reference/tokens.md` — every `--hdx-*` CSS custom
  property (colors, type, spacing, elevation, radius), grouped by family. THE source
  for values.
- `ds-knowledge-base-internal/style-reference/components.md` — component inventory +
  BEM class vocabulary (the design system's public contract).
- `ds-knowledge-base-internal/style-reference/raw/` — the demo page + CSS bundles verbatim.

## Rules

1. **Tokens over invented values.** Pull colors/spacing/type from `tokens.md`; never make
   up hexes. If a needed value has no token, say so and pick the nearest token.
2. **Check `components.md` before hand-rolling** a UI element — if HDX has the component,
   use its classes/markup rather than reinventing it.
3. **Dataviz:** build categorical/sequential ramps from the HDX color families; usage
   guidance lives in the public pointer page `ds-knowledge-base/methods/style-guide.md`.
4. **Fallback** when the internal repo isn't on this machine: follow
   `methods/style-guide.md` (public) and tell the user how to get the mirror
   (OCHA-DAP access → re-run the team setup script, `docs/USING.md`).
5. The live source is a gated staging site — access details are in the mirror's README
   (internal repo only). Never copy its credentials into any output.
