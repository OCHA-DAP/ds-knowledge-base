# pipelines/

One page per living operational system — dataset ingests, monitoring, exposure jobs, apps. Runbook-shaped: optimize for understanding what feeds it, what it emits, and how to debug it.

Copy `_TEMPLATE.md` for each. Declare `inputs`/`outputs`/`downstream` honestly — that's what turns the KB into a dependency graph ("if SEAS5 changes format, what breaks?" → grep `inputs: SEAS5`). See [../docs/INGESTION.md](../docs/INGESTION.md).
