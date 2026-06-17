export const meta = {
  name: 'kb-ingest-systems',
  description: 'Ingest pipelines & apps (repo + deployment authoritative, no PDF): Sonnet drafts from code + deployments.md, Opus reviews → runbook/app page',
  phases: [
    { title: 'Ingest', detail: 'per system: branch survey → read code + deployments.md → write page (Sonnet)' },
    { title: 'Review+Fix', detail: 'QA vs the pipeline/app template, deployment accuracy, in place (Opus)' },
  ],
}

// args = { outDir, kbDir, model, reviewModel, targets: [{ type: 'pipeline'|'app', name, repo, repos?:[], model? }] }
const A = (typeof args === 'string' ? JSON.parse(args) : args) || {}
const KB = A.kbDir || '/Users/tdowning/OCHA/repos/ds-knowledge-base'
const OUT = A.outDir || '/tmp/systems-ingest'
const TARGETS = A.targets || []
const MODEL = A.model || 'sonnet'
const REVIEW_MODEL = A.reviewModel || 'opus'

function ingestPrompt(t) {
  const repos = t.repos && t.repos.length ? t.repos : [t.repo]
  const isApp = t.type === 'app'
  const dir = isApp ? 'apps' : 'pipelines'
  return `You ingest one OCHA ${t.type} into a knowledge-base page. For ${t.type}s, the AUTHORITATIVE source is the CODE + where it actually runs — there is NO framework PDF. Be a runbook author: capture what feeds it, what it emits, where it runs, and what breaks.

${t.type.toUpperCase()}: ${t.name}
REPO(S) (read ALL): ${JSON.stringify(repos)}

STEP 0 — LEARN THE SCHEMA. Read in full and follow exactly:
  - ${KB}/${dir}/_TEMPLATE.md   (the EXACT frontmatter fields + body headings for a ${t.type})
  - ${KB}/INGESTION.md   (conventions, branch rule, hub-vs-spoke depth: push deep operational detail DOWN to the repo, this page is the comparative summary + pointers)
  - ${KB}/infrastructure/deployments.md   (the deployment registry — Azure web apps + Databricks jobs; FIND this ${t.type}'s deployment row here, it is the authority for where/how it runs)
  - ${KB}/infrastructure/conventions.md   (stratus/lens/relay, dev-vs-prod slots, PGSSLMODE)
  Do NOT read or copy any existing page under ${KB}/${dir}/ — produce your own from sources.

STEP 1 — BRANCH SURVEY (work is usually NOT on main), for EACH repo:
  git -C <repo> for-each-ref --sort=-committerdate --format='%(committerdate:short) %(refname:short)' refs/heads refs/remotes | grep -v HEAD | head -8
  Check out the ACTIVE/most-recent branch (strip any 'origin/' prefix): git -C <repo> checkout <branch> 2>/dev/null || git -C <repo> checkout -b <branch> origin/<branch> 2>/dev/null
  Record source_branch + source_sha (git -C <repo> rev-parse --short HEAD). source_repo MUST be the slug ocha-dap/<repo-name>, NOT the local path.

STEP 2 — READ THE CODE (authoritative). README + entrypoints + config:
${isApp
  ? `  - WHAT IT SHOWS: read the app code (marimo/Dash/Streamlit/Quarto) — the pages, plots, controls, and the question it answers for a user. Set tech (marimo|dash|streamlit|quarto). Set related = the framework/pipeline id it serves (or 'standalone').
  - DATA (inputs): which DB tables / blobs / data sources it loads, and how fresh.
  - DEPLOYMENT: find this app in deployments.md → platform (azure-webapp|gh-pages), ref (the chd-... Azure app name | gh-pages repo/branch), url, resource_group. Note prod-vs-dev slot. code_ref = the entrypoint(s).`
  : `  - JOBS & SCHEDULE: a pipeline repo is OFTEN several jobs. Find them in databricks.yml / databricks.yaml (Databricks Asset Bundle — job names, crons, tasks), .github/workflows/*.yml (GHA schedules/crons), and the entrypoint (run_pipeline.py / main.py / a CLI). deployment.jobs[] = ONE ENTRY PER job/workflow {name, ref (databricks job_id | GHA workflow path | azure app), schedule (cron|event|on-demand), status (live|paused|retired)}. Cross-check deployments.md for the actual job_id(s), schedule, and paused state.
  - INPUTS: data sources, blob paths, DB tables it reads. OUTPUTS: DB tables (look in src/schemas/sql or upsert calls), blob writes, email lists (Listmonk), dashboards. DEPENDENCIES: ocha-stratus/ocha-lens/ocha-relay, key libs, Listmonk list ids, secret scopes. DOWNSTREAM: which frameworks' monitoring or which apps consume this output.
  - deployment.platform = the dominant one (databricks-job|github-actions|azure-webapp|manual); resource_group for Azure.`}

STEP 3 — RECONCILE WITH DEPLOYMENT REALITY. Note (in extra or the body's failure-modes): dev-slot deployment, paused/UNPAUSED jobs, manual-vs-scheduled, and especially whether the DEPLOYED job's git_source branch differs from what's checked out (the storms-pipeline lesson). status: live unless clearly retired.

STEP 4 — WRITE THE PAGE to ${OUT}/${dir}/${t.name}.md (mkdir -p first). CONFORMANCE — diff against _TEMPLATE.md:
  - EVERY frontmatter field present (incl. deployment block with jobs[]/ref, inputs, ${isApp ? 'tech, related, ' : 'outputs, dependencies, downstream, '}depends_on, source_repo/branch/sha, code_ref, extra: {}, visibility: internal).
  - depends_on: canonical KB node ids this DIRECTLY needs (upstream) — ${isApp ? "the pipeline/framework whose data it reads (the thing it's a companion of)" : "upstream pipelines/datasets it reads, and comms it sends through ('listmonk')"}; use page ids (framework folder / pipeline|app filename) or a shared-infra id. Powers infrastructure/dependency-graph.md.
  - EVERY body heading present.
  - YAML PARSE GATE (line-anchored, NOT t.split('---')): python3 -c "import yaml; t=open('${OUT}/${dir}/${t.name}.md').read(); e=t.find(chr(10)+'---',3); yaml.safe_load(t[3:e]); print('YAML OK')" — quote any ': '/brace/quote scalars until it passes.
  Write ONLY under ${OUT}; never into the KB tree.

Then RETURN this digest (structured): name, type, status, platform, n_jobs (pipelines; 0 for apps), deployed (bool — is it in deployments.md?), deploy_ref, source_branch, inputs_count, outputs_or_data_count, downstream (list), discrepancies (list — dev-slot, paused, branch-mismatch, etc.), page_path, schema_strain.`
}

const DIGEST_SCHEMA = {
  type: 'object', additionalProperties: true,
  properties: {
    name: { type: 'string' }, type: { type: 'string' }, status: { type: 'string' },
    platform: { type: 'string' }, n_jobs: { type: 'integer' }, deployed: { type: 'boolean' },
    deploy_ref: { type: 'string' }, source_branch: { type: 'string' },
    inputs_count: { type: 'integer' }, outputs_or_data_count: { type: 'integer' },
    downstream: { type: 'array', items: { type: 'string' } },
    discrepancies: { type: 'array', items: { type: 'string' } },
    page_path: { type: 'string' }, schema_strain: { type: 'string' },
  },
  required: ['name', 'type', 'status', 'page_path'],
}

function reviewFixPrompt(d, t) {
  const dir = t.type === 'app' ? 'apps' : 'pipelines'
  return `You are the corrective QA reviewer for an ingested ${t.type} KB page. READ the page at ${d && d.page_path}, the schema (${KB}/${dir}/_TEMPLATE.md, ${KB}/INGESTION.md), ${KB}/infrastructure/deployments.md, and the source repo(s) ${JSON.stringify(t.repos && t.repos.length ? t.repos : [t.repo])} as needed.

FIND AND FIX (edit the file in place):
1. CONFORMANCE: every required frontmatter field + every body heading present. YAML parses (line-anchored gate, NOT t.split('---')). Fix any missing.
2. DEPLOYMENT ACCURACY (most important): the deployment block must match deployments.md — correct platform, the real ref (Databricks job_id / chd-... Azure app / GHA path), schedule, and paused/dev-slot state. ${t.type === 'pipeline' ? 'deployment.jobs[] must list EVERY job (a repo is often several); cross-check job_ids + crons + UNPAUSED state against deployments.md.' : 'deployment.ref/url must match the chd-... app row; note prod-vs-dev slot.'}
3. INPUTS/${t.type === 'pipeline' ? 'OUTPUTS/DOWNSTREAM' : 'DATA/RELATED'}: honest and specific (real DB tables/blobs, not vague). downstream/related links to actual framework/pipeline/app pages where they exist.
4. Hub-vs-spoke: this is a SUMMARY + pointers; deep step-by-step/CLI detail belongs in the repo — trim restated detail to a pointer if over-long.
5. DISCREPANCIES: capture the operational gotchas — dev-slot deployment, paused jobs, manual-vs-scheduled, deployed-branch ≠ checked-out branch. Tag each [stale]/[conflict]/[gap] as for frameworks.

After fixing, RETURN: name, valid (bool — true only if conformant + deployment matches the registry), fixes_applied (list), remaining_issues (list).`
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

log(`Ingesting ${TARGETS.length} system(s) → ${OUT}  (draft=${MODEL}, review=${REVIEW_MODEL})`)

const results = await pipeline(
  TARGETS,
  (t) => agent(ingestPrompt(t), { label: `ingest:${t.type}:${t.name}`, phase: 'Ingest', schema: DIGEST_SCHEMA, model: t.model || MODEL }),
  (digest, t) => agent(reviewFixPrompt(digest, t), { label: `review:${t.name}`, phase: 'Review+Fix', schema: VERDICT_SCHEMA, model: REVIEW_MODEL })
    .then((v) => ({ ...digest, _verdict: v })),
)

const clean = results.filter(Boolean)
return {
  ingested: clean.length, of: TARGETS.length,
  valid: clean.filter((r) => r._verdict && r._verdict.valid).length,
  pages: clean.map((r) => ({
    name: r.name, type: r.type, status: r.status, platform: r.platform,
    jobs: r.n_jobs, deployed: r.deployed, deploy_ref: r.deploy_ref, branch: r.source_branch,
    downstream: (r.downstream || []).length, discrepancies: (r.discrepancies || []).length,
    valid: r._verdict && r._verdict.valid,
    remaining: (r._verdict && r._verdict.remaining_issues) || [],
    path: r.page_path,
  })),
}
