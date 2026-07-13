# Framework-PDF cache (committed)

One PDF per public framework version: `<framework>/<version>.pdf` — the file behind
each page's `framework_doc` URL. All of these are **already-published public
documents** (ReliefWeb / unocha.org), so per `docs/PRIVACY.md` they can live in this
public repo; non-public frameworks (`framework_doc: null`) never appear here.

**Why commit binaries?** reliefweb/unocha sit behind a Cloudflare WAF that
intermittently challenges GitHub-runner IPs, which made CI's PDF fetch flaky
(issue #250). This cache means each PDF only ever has to be fetched **once,
anywhere** — every later CI run (text extraction in `gen_framework_extracts.py`,
visual captioning in `gen_framework_captions.py`) reads the committed copy and never
re-faces the WAF. It doubles as insurance against the source being taken down
(nic-drought's ReliefWeb page already 404s).

Populated automatically: any successful fetch by `scripts/gen_framework_extracts.py`
or `scripts/gen_framework_captions.py` lands here and is committed by the
framework-sync / kb-ingest workflows. To unstick a version by hand, drop the PDF at
`<framework>/<version>.pdf` and push.
