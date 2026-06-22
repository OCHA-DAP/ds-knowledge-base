export const meta = {
  name: 'kb-ingest-libs',
  description: 'Ingest shared Python libraries → infrastructure/libs/<name>.md: Sonnet drafts from code, Opus reviews',
  phases: [
    { title: 'Ingest', detail: 'per lib: read repo (README, pyproject, public API) + find KB consumers → write page (Sonnet)' },
    { title: 'Review+Fix', detail: 'QA vs the lib template, in place (Opus)' },
  ],
}

// args = { outDir, kbDir, model, reviewModel, targets: [{ name, repo, status?, model? }] }
const A = (typeof args === 'string' ? JSON.parse(args) : args) || {}
const KB = A.kbDir || '/Users/tdowning/OCHA/repos/ds-knowledge-base'
const OUT = A.outDir || '/tmp/libs-ingest'
const TARGETS = A.targets || []
const MODEL = A.model || 'sonnet'
const REVIEW_MODEL = A.reviewModel || 'opus'

function ingestPrompt(t) {
  return `You ingest one shared OCHA Data Science **Python library** into a knowledge-base reference page. The AUTHORITATIVE source is the library's CODE + packaging — there is NO framework PDF and no deployment. Be an API/usage reference: what it's for, how to install + authenticate, the key public API, who uses it, and the gotchas.

LIBRARY: ${t.name}
REPO (read it): ${t.repo}
KNOWN STATUS HINT (verify; active unless superseded): ${t.status || 'active'}

STEP 0 — LEARN THE SHAPE. Read:
  - ${KB}/infrastructure/conventions.md  (how the team already describes ${t.name} in one line — your page is the deep version; do NOT contradict it)
  - ${KB}/INGESTION.md  (hub-vs-spoke: push deep detail DOWN to the repo; this page is the summary + pointers + the few canonical usage snippets)
  Look at a couple of existing infrastructure pages for tone (e.g. ${KB}/infrastructure/comms-listmonk.md). Do NOT copy an existing libs/ page; produce your own from the repo.

STEP 1 — BRANCH + VERSION. git -C ${t.repo} for-each-ref --sort=-committerdate --format='%(committerdate:short) %(refname:short)' refs/heads refs/remotes | grep -v HEAD | head -6 — check out the active/most-recent branch (strip 'origin/'). Record source_branch + source_sha (git -C ${t.repo} rev-parse --short HEAD). Get the version from pyproject.toml / setup.py / __version__ / latest git tag (git -C ${t.repo} tag --sort=-creatordate | head -3). source_repo MUST be ocha-dap/${t.name}.

STEP 2 — READ THE CODE. README + pyproject (deps, entry points) + the public API surface (src/${t.name}/ or ${t.name}/ — the functions/classes exported in __init__.py; load/save helpers, engines, clients). Capture: the PURPOSE (one line), INSTALL line (pip/uv, incl. the git+https form if not on PyPI), AUTH/ENV (which env vars / secrets it needs — e.g. DSCI_AZ_*, PGSSLMODE, Listmonk creds), the KEY public functions/classes (the 6-12 most-used, with one-line each), and any other OCHA libs it depends on.

STEP 3 — FIND CONSUMERS in the KB. grep the KB for who depends on this lib: grep -rl "${t.name}" ${KB}/frameworks ${KB}/pipelines ${KB}/apps ${KB}/analysis — list the page ids that have it in depends_on or reference it. Set used_by to those canonical ids (framework folder / pipeline|app filename).

STEP 4 — WRITE THE PAGE to ${OUT}/infrastructure/libs/${t.name}.md (mkdir -p first). Frontmatter (exact keys):
  content_type: library
  name: ${t.name}
  status:            # active | superseded  (ocha-anticipy is superseded; verify the rest)
  purpose:           # one line
  language: python
  source_repo: ocha-dap/${t.name}
  source_branch:
  source_sha:
  version:           # latest release/tag or pyproject version
  install:           # the canonical install line
  auth_env: []       # env vars / secrets it needs ([] if none)
  key_api: []        # the main public functions/classes (names)
  depends_on: []     # other ocha-* libs it needs
  used_by: []        # KB page ids that use it (discoverability)
  visibility: public
  last_synced:       # today's date YYYY-MM-DD
Body headings (all present): ## Summary, ## Install & auth, ## Key API (a small table: name | what it does), ## Used by, ## Gotchas & conventions, ## Source.
  YAML PARSE GATE (line-anchored, NOT t.split('---')): python3 -c "import yaml; t=open('${OUT}/infrastructure/libs/${t.name}.md').read(); e=t.find(chr(10)+'---',3); yaml.safe_load(t[3:e]); print('YAML OK')" — quote any ': '/brace/quote scalars until it passes. Write ONLY under ${OUT}.

Then RETURN this digest (structured): name, status, version, purpose, install, n_auth_env, n_key_api (count), depends_on (list), used_by (list), page_path, schema_strain.`
}

const DIGEST_SCHEMA = {
  type: 'object', additionalProperties: true,
  properties: {
    name: { type: 'string' }, status: { type: 'string' }, version: { type: 'string' },
    purpose: { type: 'string' }, install: { type: 'string' }, n_auth_env: { type: 'integer' },
    n_key_api: { type: 'integer' }, depends_on: { type: 'array', items: { type: 'string' } },
    used_by: { type: 'array', items: { type: 'string' } }, page_path: { type: 'string' },
    schema_strain: { type: 'string' },
  },
  required: ['name', 'status', 'purpose', 'page_path'],
}

function reviewFixPrompt(d, t) {
  return `You are the corrective QA reviewer for an ingested LIBRARY KB page. READ the page at ${d && d.page_path}, the source repo ${t.repo}, ${KB}/infrastructure/conventions.md, and ${KB}/INGESTION.md.

FIND AND FIX (edit in place):
1. CONFORMANCE: every frontmatter key + every body heading present; YAML parses (line-anchored gate, NOT t.split('---')). Fix missing/unquoted scalars.
2. ACCURACY: version + install line are real (cross-check pyproject/tags). auth_env lists the ACTUAL env vars/secrets (read the code — don't guess). key_api names exist in the public surface. status correct (ocha-anticipy = superseded).
3. used_by: only KB pages that genuinely use it; ids resolve to real pages.
4. Hub-vs-spoke: summary + pointers + a few canonical snippets, not a full API dump — trim restated detail to a pointer if over-long.
5. Don't contradict conventions.md's one-liner; this page is its deep version.

After fixing, RETURN: name, valid (bool — true only if conformant + accurate), fixes_applied (list), remaining_issues (list).`
}

const VERDICT_SCHEMA = {
  type: 'object', additionalProperties: true,
  properties: {
    name: { type: 'string' }, valid: { type: 'boolean' },
    fixes_applied: { type: 'array', items: { type: 'string' } },
    remaining_issues: { type: 'array', items: { type: 'string' } },
  },
  required: ['name', 'valid'],
}

log(`Ingesting ${TARGETS.length} library(ies) → ${OUT}  (draft=${MODEL}, review=${REVIEW_MODEL})`)

const results = await pipeline(
  TARGETS,
  (t) => agent(ingestPrompt(t), { label: `ingest:lib:${t.name}`, phase: 'Ingest', schema: DIGEST_SCHEMA, model: t.model || MODEL }),
  (digest, t) => agent(reviewFixPrompt(digest, t), { label: `review:${t.name}`, phase: 'Review+Fix', schema: VERDICT_SCHEMA, model: REVIEW_MODEL })
    .then((v) => ({ ...digest, _verdict: v })),
)

const clean = results.filter(Boolean)
return {
  ingested: clean.length, of: TARGETS.length,
  valid: clean.filter((r) => r._verdict && r._verdict.valid).length,
  pages: clean.map((r) => ({
    name: r.name, status: r.status, version: r.version, used_by: (r.used_by || []).length,
    valid: r._verdict && r._verdict.valid, remaining: (r._verdict && r._verdict.remaining_issues) || [],
    path: r.page_path,
  })),
}
