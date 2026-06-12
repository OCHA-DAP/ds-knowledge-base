export const meta = {
  name: 'kb-ingest-frameworks',
  description: 'Branch-aware AA-framework ingestion: Sonnet drafts (read active branch + reconcile latest PDF), Opus reviews-and-fixes → schema-conformant KB page',
  phases: [
    { title: 'Ingest', detail: 'per framework: branch survey → PDF resolve+extract → reconcile → write page (Sonnet)' },
    { title: 'Review+Fix', detail: 'QA against schema, correct discrepancy/axis/lineage/conformance gaps in place (Opus)' },
  ],
}

// args = { outDir, kbDir, model, reviewModel, targets: [{ framework, repo, repos?:[], hazard, doc_pages:[url], model? }] }
// args may arrive as a JSON string — parse defensively.
const A = (typeof args === 'string' ? JSON.parse(args) : args) || {}
const KB = A.kbDir || '/Users/tdowning/OCHA/repos/ds-knowledge-base'
const OUT = A.outDir || '/tmp/phase2-validation'
const TARGETS = A.targets || []
const MODEL = A.model || 'sonnet'
const REVIEW_MODEL = A.reviewModel || 'opus'

const UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36'
// Fixed hazard vocabulary — normalize to these exact tags.
const HAZARDS = 'drought | flood (NOT "flooding") | tropical-cyclone (cyclones/hurricanes/storms/typhoons all map here) | cholera | other'

function ingestPrompt(t) {
  const repos = t.repos && t.repos.length ? t.repos : [t.repo]
  return `You ingest one OCHA anticipatory-action framework into a knowledge-base page. The page must be schema-conformant AND faithful — capture the subtle reconciliation findings, not just the headline trigger.

FRAMEWORK: ${t.framework}   HAZARD (normalize to: ${HAZARDS}): ${t.hazard}
REPO(S) (read ALL — a framework may pair with a -monitoring/-app companion): ${JSON.stringify(repos)}
CANDIDATE DOC PAGES (newest first; the most recent published version is authoritative): ${JSON.stringify(t.doc_pages)}

STEP 0 — LEARN THE SCHEMA. Read in full and follow exactly:
  - ${KB}/INGESTION.md   (authority rules, branch rule, reconciliation, PDF handling)
  - ${KB}/frameworks/_TEMPLATE.md   (the EXACT frontmatter fields and body headings)
  Do NOT read or copy any existing page under ${KB}/frameworks/<this-framework>/ — produce your own from sources.

STEP 1 — BRANCH SURVEY (work is usually NOT on main), for EACH repo:
  git -C <repo> for-each-ref --sort=-committerdate --format='%(committerdate:short) %(refname:short)' refs/heads refs/remotes | head -6
  Read the ACTIVE/most-recent branch's working tree. Record source_branch + source_sha. Never assume main.

STEP 2 — LATEST PDF (authoritative for the trigger). Browser-UA fetch each candidate page, extract the attachment PDF, pdftotext:
  UA='${UA}'
  curl -sL -A "$UA" '<page>' -o /tmp/${t.framework}_page.html
  grep -oiE 'href="[^"]*\\.pdf"' /tmp/${t.framework}_page.html   # unocha.org/attachments/...pdf OR reliefweb.int/attachments/...pdf
  curl -sL -A "$UA" '<pdf-url>' -o /tmp/${t.framework}_doc.pdf && pdftotext /tmp/${t.framework}_doc.pdf ${OUT}/raw/${t.framework}_doc.txt
  Read FR/ES/PT natively. Use the most recent dated version. **Find the PRIOR published version too** (older dated doc on the portfolio) → set 'supersedes' to its date; only null if genuinely the first. Save the full-text extraction path under raw_extract.

STEP 3 — READ THE REPO(S): README + exploration/*.md + analysis/ + pipelines/ + src/ + constants. README is often incomplete — read code. Find canonical trigger code (code_ref), deployed apps (apps), and any companion-repo (-monitoring) state.

STEP 4 — RECONCILE (the hard part — be thorough). Trigger from the latest PDF; cross-check the repo. Set repo_completeness (full|partial|lost, or a layered map {analysis,deployed_code}). HUNT for discrepancies and record EACH — do not smooth over:
  (a) PDF-internal inconsistencies (a value that differs between an exec-summary table and the model-section table — flag the likely typo);
  (b) repo logic NOT in the PDF (WARNING/early-alert tiers, extra thresholds);
  (c) stale/legacy constants in code (old thresholds, "visual guess" values) that aren't the live trigger;
  (d) deployment maturity (apps on -development- Azure slots despite endorsed status);
  (e) companion-repo drift (a -monitoring repo encoding an OLDER design than the endorsed PDF);
  (f) the live trigger running OUTSIDE the repo (IRI Maproom, INAM/PRISM, INSIVUMEH) → set operated_by.

STEP 5 — WRITE THE PAGE to ${OUT}/frameworks/${t.framework}/<version>.md (mkdir -p first). CONFORMANCE — before finishing, diff your file against _TEMPLATE.md:
  - EVERY frontmatter field present (incl. framework_doc_annexes, raw_extract, operated_by, activations, extra: {});
  - EVERY body heading present (Summary, Method, Trigger logic, Trigger windows, Per-country variants [delete only if single-country], Sources & repo completeness, Monitoring, Historical activations, Key decisions & rationale, Changes from previous version, Open questions);
  - status ∈ {pre-development,development,endorsed,triggered,superseded,retired}; quote dated version values; visibility: internal.
  TRIGGER WINDOWS table: n_windows MUST equal its row count.
  window_axes: assert an axis (time|space|severity) ONLY with hard evidence; prefer the SINGLE dominant differentiator. Do NOT add 'severity' merely because intensity thresholds differ — only when a window exists specifically for a different severity tier. Most frameworks are [time]; flooding-by-area is [space].
  basis: derive from the windows — forecast-only=forecast, obs-only=observational, both=mixed.
  Put anything that doesn't fit a field into extra: {}.

Then RETURN this digest (structured): framework, version, status, hazard, country_iso3, source_branch, framework_doc, framework_doc_date, trigger_source, repo_completeness_summary, n_windows, window_axes, data_sources, operated_by, discrepancies (list — be complete), activations_count, page_path, schema_strain.`
}

const DIGEST_SCHEMA = {
  type: 'object', additionalProperties: true,
  properties: {
    framework: { type: 'string' }, version: { type: 'string' }, status: { type: 'string' },
    hazard: { type: 'string' }, country_iso3: { type: 'string' }, source_branch: { type: 'string' },
    framework_doc: { type: 'string' }, framework_doc_date: { type: 'string' },
    trigger_source: { type: 'string' }, repo_completeness_summary: { type: 'string' },
    n_windows: { type: 'integer' }, window_axes: { type: 'array', items: { type: 'string' } },
    data_sources: { type: 'array', items: { type: 'string' } }, operated_by: { type: 'string' },
    discrepancies: { type: 'array', items: { type: 'string' } }, activations_count: { type: 'integer' },
    page_path: { type: 'string' }, schema_strain: { type: 'string' },
  },
  required: ['framework', 'version', 'status', 'trigger_source', 'n_windows', 'page_path'],
}

function reviewFixPrompt(d, t) {
  return `You are the corrective QA reviewer for an ingested KB page. READ the page at: ${d && d.page_path}, the schema (${KB}/frameworks/_TEMPLATE.md, ${KB}/INGESTION.md), and the source repo(s) ${JSON.stringify(t.repos && t.repos.length ? t.repos : [t.repo])} + the extracted PDF text under ${OUT}/raw/${t.framework}_doc.txt as needed.

FIND AND FIX (edit the file in place — don't just report):
1. CONFORMANCE: every required frontmatter field + every body heading present (esp. raw_extract, extra: {}, the "## Historical activations" section). Add any missing.
2. n_windows == rows in the Trigger windows table. Fix to match.
3. window_axes: remove any axis not strongly evidenced; prefer the single dominant differentiator (most are [time]; flooding-by-area [space]). Don't keep 'severity' unless a window exists for a distinct severity tier.
4. basis correct vs the windows (forecast/observational/mixed).
5. supersedes: if a prior published version exists and it's null, find it and set the date.
6. status/enum valid; hazard normalized (flood not flooding); quoted dated version.
7. DISCREPANCY COMPLETENESS — the most important: re-read the PDF + repo and ensure discrepancies captures the subtle ones the drafter may have missed: PDF-internal table inconsistencies (swapped values), repo-only WARNING/extra tiers, stale/legacy constants, dev-slot deployment, and companion-repo drift. ADD any real ones with evidence.

After fixing, RETURN: framework, valid (bool, true only if now fully conformant + faithful), fixes_applied (list), remaining_issues (list).`
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

log(`Ingesting ${TARGETS.length} framework(s) → ${OUT}  (draft=${MODEL}, review=${REVIEW_MODEL})`)

const results = await pipeline(
  TARGETS,
  (t) => agent(ingestPrompt(t), { label: `ingest:${t.framework}`, phase: 'Ingest', schema: DIGEST_SCHEMA, model: t.model || MODEL }),
  (digest, t) => agent(reviewFixPrompt(digest, t), { label: `review:${t.framework}`, phase: 'Review+Fix', schema: VERDICT_SCHEMA, model: REVIEW_MODEL })
    .then((v) => ({ ...digest, _verdict: v })),
)

const clean = results.filter(Boolean)
return {
  ingested: clean.length,
  of: TARGETS.length,
  valid: clean.filter((r) => r._verdict && r._verdict.valid).length,
  pages: clean.map((r) => ({
    framework: r.framework, version: r.version, status: r.status, branch: r.source_branch,
    n_windows: r.n_windows, axes: r.window_axes, trigger_source: r.trigger_source,
    completeness: r.repo_completeness_summary, discrepancies: (r.discrepancies || []).length,
    valid: r._verdict && r._verdict.valid,
    fixes: (r._verdict && r._verdict.fixes_applied) || [],
    remaining: (r._verdict && r._verdict.remaining_issues) || [],
    path: r.page_path,
  })),
}
