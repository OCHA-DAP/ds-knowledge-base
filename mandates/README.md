---
content_type: mandate
last_reviewed: "2026-10-08"   # bump when a human verifies the page is still accurate
---

# mandates/

The institutional footing of the work in this KB: **what OCHA and CERF were set up to do, by whom, and in which document** — read from the primary texts (General Assembly resolutions, Secretary-General's reports and bulletins), not from web summaries or memory. One page per mandate holder; every claim on a page points to a numbered paragraph in an extract under [`raw/mandates/`](../raw/mandates/), so the wording can always be checked.

- [ocha.md](ocha.md) — **OCHA** and the **Emergency Relief Coordinator**: GA resolution 46/182 (1991) — the guiding principles, early warning, the ERC's nine responsibilities, the IASC, consolidated appeals; the 1997 reform (A/51/950) that turned DHA into OCHA and fixed the ERC's three core functions; the 1999 organisation bulletin (ST/SGB/1999/8); the fourth principle (58/114, 2003); the annual "Strengthening of the coordination" resolutions that renew the mandate every December — and where anticipatory action entered them.
- [cerf.md](cerf.md) — **CERF**: the Central Emergency *Revolving* Fund of 46/182 (a $50M loan facility) → the Central Emergency *Response* Fund of 60/124 (2005, grant element, three objectives) → the $1 billion target (71/127, 2016; 79/140, 2024); the operating rules in the current Secretary-General's bulletin (ST/SGB/2020/5): eligibility, the loan and grant elements, the Rapid Response / Underfunded Emergencies split, timelines, reporting, the Advisory Group — and what the GA/bulletin layer does *not* say about anticipatory action.

## How to read these pages

**Authority levels, highest first.** (1) A **General Assembly resolution** (`A/RES/…`) is the Member States' decision — the mandate itself. (2) A **Secretary-General's bulletin** (`ST/SGB/…`) is the Secretariat's implementing regulation under those resolutions — it says *how* the mandate is run, and a later bulletin abolishes the earlier one. (3) **Secretary-General's reports** (`A/…`) propose or account for; they are authoritative on facts and intent but decide nothing until the Assembly acts on them. (4) Everything else — OCHA/CERF web pages, guidance notes, the life-saving criteria, our own framework documents — is secretariat practice *under* the above. Pages here label which level each statement comes from and stay at levels 1–3; practice belongs on the framework, pipeline and dataset pages that implement it.

**Paragraph citations.** `46/182 ¶35(e)` means annex paragraph 35, sub-paragraph (e), of `raw/mandates/A_RES_46_182.txt`; `SGB 2020/5 §4.2` means section 4.2 of `raw/mandates/ST_SGB_2020_5.txt`. The annual coordination resolutions renumber their operative paragraphs each year, so a citation always names the year's symbol.

**Scope (to start).** OCHA and CERF. The bodies 46/182 created alongside them — the ERC, the IASC, the consolidated appeal — are covered inline on the OCHA page rather than given pages of their own. Country-based pooled funds (CBPFs), the ECOSOC humanitarian affairs segment and the IASC's own terms of reference are candidates for later pages. <!-- TODO: cbpf.md (CBPF Global Guidelines are OCHA policy, not GA text — decide whether they belong here or under infrastructure/datasets/cbpf-odata.md) -->

## Sources and refresh

Extracts under `raw/mandates/` are `pdftotext -layout` of the official English PDFs, fetched from the UN Official Document System's symbol endpoint (`https://documents.un.org/api/symbol/access?s=<symbol>&l=E&t=pdf`) or from CERF's own document pages (<https://cerf.un.org/about-us/who-we-are/general-assembly-resolutions>, <https://cerf.un.org/about-us/who-we-are/secretary-general-reports-and-bulletins>). The one exception is **46/182**: ODS holds only an image scan of the 1991 resolution (no text layer), so its extract is the plain text of the former `un.org/documents/ga/res/46/a46r182.htm` page as mirrored by the Humanitarian Library — checked paragraph-by-paragraph against the scan's structure (42 annex paragraphs, sections I–VII). There is no generator: these documents change only when the Assembly adopts a new one (every December) or the Secretary-General issues a new bulletin. When that happens, fetch the new symbol the same way, add the extract, and update the page and its `last_reviewed` stamp.
