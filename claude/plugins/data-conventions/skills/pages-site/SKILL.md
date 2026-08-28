---
name: pages-site
description: Use when creating or publishing a GitHub Pages site for a team repo ("make me a GitHub page", "publish this as a site"), adding a product — app, book, slides, analysis — to a repo that already serves one, or writing/restructuring a Pages deploy workflow. Advisory — the repo's own setup wins.
---

# GitHub Pages sites — the decisions, in order

The knowledge lives in the KB → `methods/static-data-apps.md` (hosting choice, data
modalities, the landing-page convention, deploy gotchas). This skill is the front door:
check the discoverable facts silently, then put only the genuine choices to the user
before scaffolding anything.

## Check facts first — never ask what you can look up

- **Does the repo already serve a Pages site?** `gh api repos/OCHA-DAP/<repo>/pages`
  (404 = none). A repo gets exactly **one** Pages site — if one exists, the new product
  *joins* it under the landing-page convention; never clobber the root (moving an
  existing product's URL breaks saved links).
- Existing `pages/` or `docs/` layout, deploy workflow, and site mode (branch-served vs
  workflow-built) — extend what's there rather than inventing a parallel structure.

## Then put the real decisions to the user (one round, not a lecture)

1. **Is GH Pages right at all?** Pages on a public repo is world-readable. Sensitive
   data or org-login gating → stop and route via the SWA / App Service sections of
   `methods/static-data-apps.md`.
2. **Site shape.** Default to a landing page at `/` with each product under its own path
   whenever a second product is even plausible — retrofitting later moves URLs.
   Multi-contributor growth → the **manifest-driven** variant (drop-in
   `pages/products/*/page.toml`, no shared-file edits; lift `pages/_build/` per
   `ds-storm-impact-harmonisation/pages/README.md` § "Reusing this in another repo").
   Small one-maintainer site → hand-edited cards (`ds-seas5-skill/pages/`) is fine.
   Either way, nested product pages aren't templated but each carries the small
   **back-to-home button** at the top — snippet + per-product-type application in
   `methods/static-data-apps.md` § "Nested pages link back home".
3. **How data reaches the browser** — pre-rendered, CI-export into the Pages artifact,
   committed, or runtime-from-blob: walk the decision tree in
   `methods/static-data-apps.md`; don't restate or improvise it.
4. **Styling** — team sites use the HDX v2 design system (see the reference repos
   above); the style knowledge itself is the `hdx` plugin in the `hdx-ai-hub`
   marketplace, not this one.

Before the first deploy, read `methods/static-data-apps.md` § "GitHub Pages gotchas"
(workflow-mode switch, environment branch policy, secrets shadowing) — each one has
burned a real deploy.
