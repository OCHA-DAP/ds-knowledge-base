#!/usr/bin/env python3
"""Mirror the workspace's cluster policies into infrastructure/databricks-policies/ (D114).

Environment variables (`spark_env_vars.*`) are left out entirely, name and value, so
nothing they hold can reach this public repo; see the policy in Databricks for them.
CI uses DATABRICKS_PROFILE="" with env auth; `--from-json` reads a saved list for testing.
"""
from __future__ import annotations
import argparse, json, os, re, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "infrastructure" / "databricks-policies"
PROFILE = os.environ.get("DATABRICKS_PROFILE", "default")
# Backstop only: stop the run if anything credential-shaped survives elsewhere in a policy.
LEAK_PATTERN = re.compile(r"Signature=|[\w.+-]+@[\w-]+\.[\w.]+|ghp_|github_pat_|gho_|sv=\d{4}-\d{2}-\d{2}&|AKIA[0-9A-Z]{16}")


def fetch_policies(from_json: str | None) -> list[dict]:
    if from_json:
        raw = Path(from_json).read_text()
    else:
        prof = ["-p", PROFILE] if PROFILE else []
        r = subprocess.run(["databricks", "cluster-policies", "list", *prof, "-o", "json"],
                           capture_output=True, text=True, timeout=120)
        if r.returncode != 0:
            sys.exit(f"databricks cluster-policies list failed: {r.stderr.strip()[:600]}")
        raw = r.stdout
    data = json.loads(raw)
    return data.get("policies", []) if isinstance(data, dict) else data


def without_env_vars(definition_json: str | None) -> dict:
    """Parse a policy definition and drop every environment-variable rule."""
    definition = json.loads(definition_json or "{}")
    return {k: v for k, v in sorted(definition.items()) if not k.startswith("spark_env_vars.")}


def policy_record(p: dict) -> dict:
    record = {
        "policy_id": p["policy_id"],
        "name": p.get("name"),
        "description": p.get("description"),
        "policy_family_id": p.get("policy_family_id"),
        # Family-based policies repeat their settings here, so it gets the same treatment.
        "policy_family_definition_overrides": without_env_vars(p.get("policy_family_definition_overrides")) or None,
        "is_default": p.get("is_default", False),
        "definition": without_env_vars(p.get("definition")),
    }
    return {k: v for k, v in record.items() if v not in (None, "")}


def leaking_fields(value, path: str = "") -> list[str]:
    """Paths of string values in a record that match LEAK_PATTERN."""
    if isinstance(value, dict):
        return [p for k, v in value.items() for p in leaking_fields(v, f"{path}.{k}" if path else k)]
    if isinstance(value, list):
        return [p for v in value for p in leaking_fields(v, path)]
    return [path] if isinstance(value, str) and LEAK_PATTERN.search(value) else []


def index_md(records: list[dict]) -> str:
    lines = [
        "# Databricks cluster policies (generated)",
        "",
        "Generated daily from Databricks by `scripts/gen_databricks_policies.py` (D114). Do not edit.",
        "Environment variables are left out; see the policy in Databricks.",
        "What each policy is for: [databricks.md](../databricks.md#compute-policies).",
        "",
        "| policy_id | name | description |",
        "|---|---|---|",
    ]
    for rec in records:
        pid = rec["policy_id"]
        desc = (rec.get("description") or "").replace("|", "\\|").replace("\n", " ")
        lines.append(f"| [`{pid}`]({pid}.json) | {rec.get('name', '')} | {desc} |")
    return "\n".join(lines) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--from-json", help="read a saved `cluster-policies list -o json` instead of the CLI")
    args = ap.parse_args()

    policies = fetch_policies(args.from_json)
    if not policies:
        sys.exit("no policies returned; refusing to delete the mirror")
    records = sorted((policy_record(p) for p in policies), key=lambda r: r.get("name", ""))
    for rec in records:
        leaks = leaking_fields(rec)
        if leaks:
            # Never print the matched text: Actions logs on this public repo are public.
            sys.exit(f"{rec['policy_id']}: credential-like value in {', '.join(leaks)}; nothing written")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    keep = {f"{rec['policy_id']}.json" for rec in records} | {"README.md"}
    for f in OUT_DIR.iterdir():
        if f.name not in keep:
            f.unlink()
    for rec in records:
        (OUT_DIR / f"{rec['policy_id']}.json").write_text(json.dumps(rec, indent=2) + "\n")
    (OUT_DIR / "README.md").write_text(index_md(records))
    print(f"wrote {len(records)} policies to {OUT_DIR.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
