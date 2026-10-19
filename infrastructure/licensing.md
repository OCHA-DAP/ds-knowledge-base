---
content_type: infrastructure
last_reviewed: "2026-09-09"   # bump when a human verifies the page is still accurate
---

# Repo & content licensing — considered, not decided

> **Status: nothing here is decided or implemented.** This is a captured discussion (2026-09) so the reasoning isn't lost. Repos keep whatever license they have today; the only current team-wide rule about repos is the `ds-` prefix in [conventions.md](conventions.md). Treat this page as input to a decision, not as guidance to follow.

## Why it came up

The prompt was AI: everyone is coding with LLMs now, so *"is there something we should add to our licenses about people not stealing our work?"* — while keeping everything as open as possible on principle.

## Where we stand today

Inventory of the 95 team repos in `OCHA-DAP` (`ds-*`, `pa-aa-*`, `ocha-*`, `hdx-signals*`), taken 2026-09-09:

| License | All | Public only |
|---|---|---|
| **none** | 68 | 59 |
| GPL-3.0 | 17 | 16 |
| MIT | 6 | 6 |
| Apache-2.0 | 4 | 4 |

Reproduce with:

```bash
gh repo list OCHA-DAP --limit 300 --json name,licenseInfo,visibility \
  --jq '.[] | select(.name | test("^(ds-|pa-aa-|hdx-signals|ocha-)")) |
        [.name, .visibility, (.licenseInfo.key // "none")] | @tsv'
```

**The finding that matters: most public team repos have no license at all** — which legally means *all rights reserved*, so they are not actually open source and nobody can legitimately reuse them, while offering no practical protection whatsoever. That is the worst of both worlds, and it is a bigger problem than anything AI-specific. Where licenses do exist there's drift: GPL-3.0 on most analysis/framework repos, MIT on the shared `ocha-*` libraries, a few Apache-2.0.

## What a license can and can't do here

- **A license cannot keep our code out of AI training.** Training pipelines scrape public GitHub regardless of license (GPL code included); whether that infringes is unsettled law, and a LICENSE file doesn't change the outcome. GitHub's own terms grant broad rights over public-repo content with no training opt-out — the only real opt-out is going private, which contradicts the open-by-default principle.
- **An "no AI training" clause would cost us the open-source label.** It's a field-of-use restriction, so it fails the Open Source Definition. "Fully open source" and "no AI use" cannot both be true of one license.
- **A non-commercial clause has the same problem, plus worse ones.** "Non-commercial" is undefined at the edges (is a for-profit contractor delivering aid commercial?), it blocks the legitimate institutional adopters we *want* — government met services, NGO tech teams, IFI-funded work — and it stops nobody we're actually worried about. CC BY-NC is the license people half-remember for this; it's for content, not code, and Creative Commons itself advises against using CC licenses for software.
- **What a license *can* do** is govern derivatives: copyleft (GPL/AGPL) forces anyone who builds on our code and ships it — AGPL additionally covers hosted services — to open-source their derivative. That's real leverage against a closed SaaS clone, but it's leverage bought at the cost of scaring off exactly the institutional adopters above (some large organisations have blanket bans on AGPL code).
- **The harm we should actually be designing against isn't copyright at all.** For a UN team the realistic damage is (a) someone selling an *"OCHA-validated"* consultancy product, and (b) someone lifting a threshold out of context and causing operational harm. Copyright licenses touch neither. **Trademark** language addresses the first; a **revalidation disclaimer** addresses the second.

## The leading proposal (team discussion, 2026-09)

1. **Code → Apache-2.0.** Add it to every repo currently at `none`, and to whatever scaffolds new repos so the gap stops recurring. **Leave existing MIT and GPL-3.0 repos alone** — relicensing GPL needs every contributor's sign-off and isn't worth it. Apache-2.0 is OSI-approved, permissive (like MIT — commercial use allowed), and adds three things MIT lacks that this plan depends on: an express **patent grant**, an explicit statement that **no trademark rights** are granted, and the **NOTICE mechanism** (§4(d)) — redistributors of derivatives must carry our NOTICE text forward, which is what makes point 4 travel with the code instead of being aspirational.
2. **KB and its content → CC BY 4.0.** Attribution is the thing we actually want and the only part realistically enforceable.
3. **No non-commercial license** — for the reasons above.
4. **Put the protection in the NOTICE, not the license.** One paragraph: reuse the code and methods freely; do not use OCHA's name, logo, or framework names in a way that implies endorsement. **Trademark is the lever that stops "OCHA-validated" products. Copyright isn't.**
5. **Add a reuse disclaimer to the README:** thresholds are context-specific and validated against a named record — revalidate before reuse. This is the guard against the failure mode that actually causes harm.

## Open items before any of this could ship

- **Data-terms carve-out (blocking).** Blanket CC BY on KB pages derived from non-commercially-licensed sources would grant rights we don't hold. Confirmed NC sources already recorded in the KB: **EM-DAT** ("free for non-commercial use, attribution to CRED/UCLouvain", [datasets/emdat.md](datasets/emdat.md)) and **IPC** ("attribution required, non-commercial", [datasets/ipc.md](datasets/ipc.md)). The clean pattern is: our text and methods under CC BY, with a per-page data-terms note that the underlying data stays under the provider's license.
  <!-- TODO: ACLED terms are not recorded anywhere in the KB (nothing in pipelines/acled-*.md). ACLED restricts redistribution; confirm the exact terms and add them to a dataset/pipeline page before any blanket CC BY. Same sweep needed for Copernicus/ECMWF (SEAS5/ERA5) attribution terms. -->
- **Contributor consent applies to the unlicensed repos too**, not only to relicensing GPL ones. A repo with no license isn't unowned — each contributor holds copyright on their commits. In practice this is a handful of team colleagues and a Slack message, and UN staff work product likely vests in the organisation anyway, but run `git shortlog -sn` per repo before stamping, especially where there are external contributors.
- **UN/OCHA house guidance unchecked.** UN materials sometimes carry special copyright treatment; confirm with whoever owns that before stamping a license on ~60 repos.
- **Worth folding in: `CITATION.cff`** on the code and methods repos (trigger frameworks especially). GitHub renders a cite button from it; it's the cheap machinery that turns "we want attribution" into attribution actually happening. Attribution norms protect us more in practice than enforcement ever will.
- **Where the "scaffolds new repos" hook goes** — repo template, or a new-repo checklist in [conventions.md](conventions.md).

## What implementing would involve

LICENSE + NOTICE + `CITATION.cff` added as PRs across the unlicensed public repos (with the per-repo contributor check), a CC BY footer on the KB with the source carve-outs, and the template/checklist update so new repos don't recreate the gap.
