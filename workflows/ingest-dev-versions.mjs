export const meta = {
  name: 'kb-ingest-dev-versions',
  description: 'Ingest UNPUBLISHED in-development successor framework versions from a dev branch (framework_doc:null, trigger_source:repo) + hunt activations that fired under the endorsed version. Sonnet drafts, Opus reviews.',
  phases: [
    { title: 'Ingest', detail: 'per framework: read the dev branch → write in-development page + report endorsed-version activations (Sonnet)' },
    { title: 'Review+Fix', detail: 'QA against schema, fix conformance/discrepancy gaps in place (Opus)' },
  ],
}

// args = { outDir, kbDir, model, reviewModel, targets: [{ framework, repo, dev_branch, hazard, endorsed_version, endorsed_branch_should_be? }] }
const A = (typeof args === 'string' ? JSON.parse(args) : args) || {}
const KB = A.kbDir || '/Users/tdowning/OCHA/repos/ds-knowledge-base'
const OUT = A.outDir || '/tmp/kb-dev-versions'
const TARGETS = A.targets || []
const MODEL = A.model || 'sonnet'
const REVIEW_MODEL = A.reviewModel || 'opus'

const UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36'
const HAZARDS = 'drought | flood (NOT "flooding") | tropical-cyclone (cyclones/hurricanes/storms/typhoons all map here) | cholera | other'

function ingestPrompt(t) {
  return `You ingest the **unpublished, in-development successor version** of an OCHA anticipatory-action framework into a NEW knowledge-base page. This is NOT the endorsed version — it lives only on a dev branch, has NO published framework PDF yet, and is NOT authoritative. The endorsed version already has its own page (do NOT touch it from here; you only REPORT a patch for it). Your job: faithfully capture the NEW trigger design as it currently stands in the repo, clearly marked not-yet-endorsed.

FRAMEWORK: ${t.framework}   HAZARD (normalize to: ${HAZARDS}): ${t.hazard}
REPO (read it): ${t.repo}
DEV BRANCH (the in-development work lives here): ${t.dev_branch}
ENDORSED VERSION already on its own page (its date — set this as 'supersedes'): ${t.endorsed_version}

STEP 0 — LEARN THE SCHEMA. Read in full and follow exactly:
  - ${KB}/INGESTION.md   (esp. the branch rule, "a trigger version newer than the latest published PDF" = separate status:development page with trigger_source:repo + framework_doc:null; and the lifecycle/activations rules)
  - ${KB}/frameworks/_TEMPLATE.md   (the EXACT frontmatter fields + body headings)
  You MAY read the existing endorsed page ${KB}/frameworks/${t.framework}/${t.endorsed_version}.md ONCE — only to (a) avoid restating its content and (b) frame "Changes from previous version". Do NOT copy it.

STEP 1 — CHECK OUT THE DEV BRANCH and read its working tree:
  git -C ${t.repo} fetch -q origin
  git -C ${t.repo} checkout ${t.dev_branch} 2>/dev/null || git -C ${t.repo} checkout -b ${t.dev_branch} origin/${t.dev_branch}
  git -C ${t.repo} rev-parse --short HEAD    # → source_sha
  Record source_branch=${t.dev_branch}, source_sha. source_repo MUST be the GitHub slug ocha-dap/<repo-name> (from git -C ${t.repo} remote get-url origin) — NOT a filesystem path.

STEP 2 — READ THE NEW TRIGGER. README + exploration/*.md + analysis/ + notebooks/*.py (marimo) + src/ + constants. The dev work is usually in notebooks/exploration. Capture the NEW trigger logic: windows, indicators, thresholds, data sources, lead times, the canonical trigger code (code_ref on THIS branch). Note what is still unsettled (this is in-development — open questions are expected and valuable).

STEP 3 — VERSION + STATUS. There is NO new published PDF, so:
  framework_doc: null
  trigger_source: repo
  status: development   (or pre-development if the trigger is clearly not yet settled; never 'endorsed')
  supersedes: "${t.endorsed_version}"
  visibility: internal
  version: choose a dated version string for this dev snapshot — prefer a design date stated in the analysis; else use the dev-branch tip commit date (git -C ${t.repo} log -1 --format=%cd --date=short ${t.dev_branch}), as "YYYY-MM-DD". Write the page to ${OUT}/frameworks/${t.framework}/<version>.md (mkdir -p first). Make the page's filename == version.
  In the body and in extra.dev_status, state plainly: "In-development successor to the ${t.endorsed_version} endorsed version; not yet endorsed, no published framework doc; trigger from the ${t.dev_branch} branch and subject to change."

STEP 4 — ACTIVATIONS (report a patch for the ENDORSED page; do NOT put endorsed-era activations on THIS dev page). An activation that fired under the ENDORSED version belongs on the ENDORSED page, not here. HUNT them: read the repo (activation notebooks, 'activation summary' app cells, dated trigger-fired notes), and web-search ReliefWeb / CERF / unocha for "<country> anticipatory action <hazard> activated 2025/2026" and major recent events for this hazard+country (e.g. Hurricane Melissa Oct 2025 for Caribbean hurricanes). For EACH real activation return {date: "YYYY-MM" or "YYYY-MM-DD", url, window, note, prearranged_or_released_usd?} in endorsed_activations. If a major event clearly hit the country but you cannot confirm the AA framework actually fired (funds released / trigger met), return it in endorsed_activations with note prefixed "UNCONFIRMED:" and an honest caveat — do not assert an activation you can't source. This dev page's own activations: [] (a dev version that has never itself been the live framework).

STEP 5 — RECONCILE / DISCREPANCIES on the dev trigger (tag each [stale]/[conflict]/[gap]): legacy constants vs the new design, app deployed on a dev Azure slot, companion-monitoring encoding the OLD trigger, the live trigger running outside the repo (IRI Maproom etc. → operated_by). Funding is usually null for an unendorsed version (no envelope yet) — only fill if the dev docs state a planned envelope.

STEP 6 — WRITE THE PAGE. CONFORMANCE — diff against _TEMPLATE.md: EVERY frontmatter field present (framework_doc:null, trigger_source:repo, supersedes, activations:[], depends_on, prearranged_funding_usd:null unless stated, funding_by_source, cofinancing_usd, cofinancing_sources, implementing_agencies, target_people, operated_by, trigger_facets.indicators [NO primary_indicator], raw_extract:null [no PDF], extra:{}). EVERY body heading present (Summary, Method, Trigger logic, Trigger windows, Per-country variants [delete only if single-country], Sources & repo completeness, Monitoring, Historical activations [state "none under this dev version; see the endorsed page for prior activations"], Key decisions & rationale, Changes from previous version, Open questions). n_windows == Trigger-windows row count. window_axes only with hard evidence (most [time]; flooding-by-area [space]). basis from the windows (forecast/observational/mixed). Put schema-strain under extra.schema_strain. Write ONLY under ${OUT}.
  YAML PARSE GATE (line-anchored, NOT t.split('---')):
    python3 -c "import yaml; t=open('${OUT}/frameworks/${t.framework}/<version>.md').read(); e=t.find(chr(10)+'---',3); yaml.safe_load(t[3:e]); print('YAML OK')"
  Quote any colon-space/brace/bracket/'#' scalar until it prints YAML OK. Keep the template's '# --- section ---' dividers.

Then RETURN this digest (structured): framework, version, status, hazard, country_iso3, source_branch, source_sha, trigger_source, n_windows, window_axes, data_sources, operated_by, discrepancies (list), endorsed_activations (list of objects), endorsed_page_note (any correction the endorsed page needs, e.g. its source_branch points at this dev branch and should instead track the endorsed trigger — free text, or empty), page_path, schema_strain.`
}

const ACT_SCHEMA = {
  type: 'object', additionalProperties: true,
  properties: {
    date: { type: 'string' }, url: { type: 'string' }, window: { type: 'string' },
    note: { type: 'string' }, prearranged_or_released_usd: {},
  },
  required: ['date', 'note'],
}

const DIGEST_SCHEMA = {
  type: 'object', additionalProperties: true,
  properties: {
    framework: { type: 'string' }, version: { type: 'string' }, status: { type: 'string' },
    hazard: { type: 'string' }, country_iso3: { type: 'string' }, source_branch: { type: 'string' },
    source_sha: { type: 'string' }, trigger_source: { type: 'string' },
    n_windows: { type: 'integer' }, window_axes: { type: 'array', items: { type: 'string' } },
    data_sources: { type: 'array', items: { type: 'string' } }, operated_by: { type: 'string' },
    discrepancies: { type: 'array', items: { type: 'string' } },
    endorsed_activations: { type: 'array', items: ACT_SCHEMA },
    endorsed_page_note: { type: 'string' },
    page_path: { type: 'string' }, schema_strain: { type: 'string' },
  },
  required: ['framework', 'version', 'status', 'trigger_source', 'n_windows', 'page_path', 'endorsed_activations'],
}

function reviewFixPrompt(d, t) {
  return `You are the corrective QA reviewer for an ingested IN-DEVELOPMENT framework version page. READ the page at ${d && d.page_path}, the schema (${KB}/frameworks/_TEMPLATE.md, ${KB}/INGESTION.md), and the source repo ${t.repo} (branch ${t.dev_branch}).

FIND AND FIX (edit the file in place):
1. CONFORMANCE: every required frontmatter field + every body heading present. Run the YAML PARSE GATE (line-anchored, NOT t.split('---')): python3 -c "import yaml; t=open('${d && d.page_path}').read(); e=t.find(chr(10)+'---',3); yaml.safe_load(t[3:e]); print('YAML OK')" — fix unquoted colon-space/brace/quote scalars until it parses.
2. NOT-ENDORSED INVARIANTS: framework_doc MUST be null; trigger_source MUST be repo; status ∈ {pre-development, development} (NEVER endorsed/triggered/superseded); supersedes == "${t.endorsed_version}"; raw_extract null; visibility internal; activations: [] (endorsed-era activations do NOT belong on this dev page — they go on the endorsed page). The page must plainly say it is the unpublished successor and subject to change.
3. n_windows == rows in the Trigger windows table. window_axes only if strongly evidenced. basis correct vs the windows.
4. trigger_facets.indicators = union across windows, NO primary_indicator.
5. DISCREPANCIES tagged [stale]/[conflict]/[gap]; add any real ones (legacy constants vs the new design, dev-slot deployment, companion-monitoring on the OLD trigger, live trigger run outside the repo).
6. Hub-vs-spoke: summary + the new trigger + pointers, not a code dump.

After fixing, RETURN: framework, valid (bool — true only if conformant + correctly marked not-endorsed), fixes_applied (list), remaining_issues (list).`
}

const VERDICT_SCHEMA = {
  type: 'object', additionalProperties: true,
  properties: {
    framework: { type: 'string' }, valid: { type: 'boolean' },
    fixes_applied: { type: 'array', items: { type: 'string' } },
    remaining_issues: { type: 'array', items: { type: 'string' } },
  },
  required: ['framework', 'valid'],
}

log(`Ingesting ${TARGETS.length} in-development version(s) → ${OUT}  (draft=${MODEL}, review=${REVIEW_MODEL})`)

const results = await pipeline(
  TARGETS,
  (t) => agent(ingestPrompt(t), { label: `ingest:${t.framework}`, phase: 'Ingest', schema: DIGEST_SCHEMA, model: t.model || MODEL }),
  (digest, t) => agent(reviewFixPrompt(digest, t), { label: `review:${t.framework}`, phase: 'Review+Fix', schema: VERDICT_SCHEMA, model: REVIEW_MODEL })
    .then((v) => ({ ...digest, _verdict: v })),
)

const clean = results.filter(Boolean)
return {
  ingested: clean.length, of: TARGETS.length,
  valid: clean.filter((r) => r._verdict && r._verdict.valid).length,
  pages: clean.map((r) => ({
    framework: r.framework, version: r.version, status: r.status, branch: r.source_branch,
    n_windows: r.n_windows, trigger_source: r.trigger_source,
    discrepancies: (r.discrepancies || []).length,
    endorsed_activations: r.endorsed_activations || [],
    endorsed_page_note: r.endorsed_page_note || '',
    valid: r._verdict && r._verdict.valid,
    remaining: (r._verdict && r._verdict.remaining_issues) || [],
    path: r.page_path,
  })),
}
