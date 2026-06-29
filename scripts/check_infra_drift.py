#!/usr/bin/env python3
"""Detect drift in our *deployed infrastructure*: Azure web apps + Databricks/GHA pipelines.

The third drift axis. `check_drift.py` watches spoke **code** (source_sha); `check_pdf_freshness.py`
watches framework **docs**; this watches the **runtime estate** — what is actually deployed and
roughly how it's configured. It answers: did a new app/job appear, did one disappear, did the rough
config change (runtime, schedule, paused, data-mode, compute, plan)?

It is a *change notifier*, not a health checker — health (last-run-vs-cadence) is
`gen_pipeline_registry.py`'s job. This compares a fresh fingerprint of the estate against a committed
baseline (`infrastructure/.infra-baseline.json`) and reports the delta. With --update-baseline it then
advances the baseline, so the baseline's git history becomes the infra changelog and each run reports
only what changed since the last.

Two domains, each degrades safely (a domain that can't be read is reported as SKIPPED, never as
"everything was removed"):
  - **Azure web apps**: `az webapp list -g <RG>` (RG via --resource-group / INFRA_RG env). Needs `az`
    authed to the OCHA-PROD subscription (locally: `az login`; CI: a service-principal secret).
  - **Pipelines (Databricks + GHA)**: read from `infrastructure/.pipeline-registry.json`, which
    `gen_pipeline_registry.py` produces. Run that FIRST so the registry is fresh; if it's stale/missing
    the pipeline half is SKIPPED (no false drift).

Usage:  python scripts/check_infra_drift.py [--resource-group RG] [--report f.md] [--update-baseline]
Exit:   0 = no drift (or first-run baseline init) · 2 = at least one ADD/REMOVE/CHANGE
"""
from __future__ import annotations
import argparse
import datetime as dt
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASELINE = ROOT / "infrastructure" / ".infra-baseline.json"
REGISTRY = ROOT / "infrastructure" / ".pipeline-registry.json"
DEFAULT_RG = os.environ.get("INFRA_RG", "IMB-CHD-DataScience-EastUS2")
# A registry snapshot older than this is treated as stale → pipeline half SKIPPED (avoids
# diffing against a frozen file and either missing real drift silently or, worse, flagging
# nothing while pretending the half was checked).
REGISTRY_MAX_AGE_H = 36

# Rough-config fields tracked per domain. Deliberately structural and low-churn — we want
# "a new app / a runtime bump / a schedule change", not noise from volatile health/timing.
AZURE_FIELDS = ["state", "kind", "runtime", "plan", "host"]
PIPE_FIELDS = ["name", "repo", "cron", "paused", "data_mode", "compute", "category"]


def sh(args: list[str]) -> str:
    try:
        return subprocess.run(args, capture_output=True, text=True, timeout=120).stdout
    except Exception:
        return ""


# ---- current state ------------------------------------------------------------
def azure_fingerprint(rg: str) -> dict | None:
    """{app_name: {field: value}} for every web app in the RG. None if `az` is unavailable
    / unauthed / the RG can't be read (→ domain SKIPPED, not reported as wiped out)."""
    out = sh(["az", "webapp", "list", "-g", rg, "-o", "json"])
    if not out.strip():
        return None
    try:
        apps = json.loads(out)
    except json.JSONDecodeError:
        return None
    if not isinstance(apps, list):
        return None
    fp = {}
    for a in apps:
        sc = a.get("siteConfig") or {}
        fp[a.get("name", "?")] = {
            "state": a.get("state"),
            "kind": a.get("kind"),
            "runtime": sc.get("linuxFxVersion") or None,
            "plan": (a.get("appServicePlanId") or "").split("/")[-1] or None,
            "host": a.get("defaultHostName"),
        }
    return fp


def pipeline_fingerprint() -> dict | None:
    """{handle: {field: value}} from the committed pipeline registry. None if the registry is
    missing or stale (→ domain SKIPPED). Structural fields only — no health/timing."""
    if not REGISTRY.exists():
        return None
    try:
        reg = json.loads(REGISTRY.read_text())
    except json.JSONDecodeError:
        return None
    gen = reg.get("generated", "")
    try:
        # registry stamps "YYYY-MM-DD HH:MM UTC"
        gts = dt.datetime.strptime(gen, "%Y-%m-%d %H:%M UTC").replace(tzinfo=dt.timezone.utc)
        if (dt.datetime.now(dt.timezone.utc) - gts).total_seconds() / 3600 > REGISTRY_MAX_AGE_H:
            return None
    except ValueError:
        return None
    fp = {}
    for e in reg.get("entries", []):
        h = e.get("handle")
        if not h:
            continue
        fp[h] = {k: e.get(k) for k in PIPE_FIELDS}
    return fp


# ---- diff ---------------------------------------------------------------------
def diff_domain(old: dict, new: dict, fields: list[str]):
    """(added, removed, changed) where changed = [(key, [(field, old, new), ...]), ...]."""
    added = sorted(k for k in new if k not in old)
    removed = sorted(k for k in old if k not in new)
    changed = []
    for k in sorted(set(old) & set(new)):
        deltas = [(f, old[k].get(f), new[k].get(f)) for f in fields if old[k].get(f) != new[k].get(f)]
        if deltas:
            changed.append((k, deltas))
    return added, removed, changed


def render_domain(title: str, fp: dict | None, base: dict | None, fields: list[str], lines: list[str]):
    """Append one domain's section to `lines`. Returns the drift count for that domain (0 if SKIPPED)."""
    if fp is None:
        lines += [f"### {title}", "", f"> ⏭️ **SKIPPED** — source unreadable (auth / staleness). "
                  "Not checked this run; treat as a blind spot, not a clean bill.", ""]
        return 0
    base = base or {}
    added, removed, changed = diff_domain(base, fp, fields)
    n = len(added) + len(removed) + len(changed)
    lines.append(f"### {title}")
    lines.append("")
    if not base:
        lines += [f"_Baseline initialised with {len(fp)} entries (no prior baseline to diff)._", ""]
        return 0
    if n == 0:
        lines += [f"✅ No change ({len(fp)} entries).", ""]
        return 0
    if added:
        lines.append(f"**🆕 New ({len(added)}):**")
        lines += [f"- `{k}` — " + ", ".join(f"{f}={fp[k].get(f)}" for f in fields if fp[k].get(f)) for k in added]
        lines.append("")
    if removed:
        lines.append(f"**🗑️ Removed ({len(removed)}):**")
        lines += [f"- `{k}` — was " + ", ".join(f"{f}={base[k].get(f)}" for f in fields if base[k].get(f)) for k in removed]
        lines.append("")
    if changed:
        lines.append(f"**✏️ Config changed ({len(changed)}):**")
        for k, deltas in changed:
            lines.append(f"- `{k}`: " + "; ".join(f"**{f}** `{o}` → `{nw}`" for f, o, nw in deltas))
        lines.append("")
    return n


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--resource-group", default=DEFAULT_RG, help="Azure RG to inventory")
    ap.add_argument("--report", help="write the markdown report to this file")
    ap.add_argument("--update-baseline", action="store_true",
                    help="advance the committed baseline to the current fingerprint after diffing")
    ap.add_argument("--emit-new-apps", metavar="PATH",
                    help="write newline-separated names of NEW Azure apps (for chaining the app-ingest)")
    args = ap.parse_args()

    now = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    azure = azure_fingerprint(args.resource_group)
    pipes = pipeline_fingerprint()

    base = {}
    if BASELINE.exists():
        try:
            base = json.loads(BASELINE.read_text())
        except json.JSONDecodeError:
            base = {}
    first_run = not base

    lines = ["# KB infra drift", "",
             f"_Generated by `scripts/check_infra_drift.py` — {now}._  ",
             "_Estate fingerprint vs. committed baseline (`infrastructure/.infra-baseline.json`). "
             "Change notifier, not a health board — see [pipeline-registry.md](pipeline-registry.md) for health._",
             ""]
    n = 0
    n += render_domain(f"Azure web apps (`{args.resource_group}`)", azure, base.get("azure"), AZURE_FIELDS, lines)
    n += render_domain("Pipelines (Databricks + GHA)", pipes, base.get("pipelines"), PIPE_FIELDS, lines)

    if first_run:
        lines.insert(4, "> First run — baseline initialised. Future runs report the delta against it.\n")
    elif n == 0:
        lines.append("✅ **No infra drift** across all checked domains.")
    else:
        lines.append("_To accept this as the new normal, the baseline has been advanced "
                     "(its git history is the infra changelog). Reconcile the human docs: "
                     "`infrastructure/deployments.md` (Azure table) and the affected pipeline/app pages._")

    report = "\n".join(lines) + "\n"
    print(report)
    if args.report:
        Path(args.report).write_text(report, encoding="utf-8")

    # Emit NEW Azure app names so a caller can chain the app-ingest (ingest-app.yml).
    # Empty unless we have a real baseline AND could read Azure this run (no first-run /
    # SKIPPED false positives).
    if args.emit_new_apps:
        new_apps = []
        if azure is not None and not first_run:
            new_apps, _, _ = diff_domain(base.get("azure") or {}, azure, AZURE_FIELDS)
        Path(args.emit_new_apps).write_text("\n".join(new_apps), encoding="utf-8")

    # Advance the baseline only for domains we could actually read (don't wipe a domain's
    # baseline just because it was SKIPPED this run).
    if args.update_baseline and (azure is not None or pipes is not None):
        new_base = dict(base)
        new_base["generated"] = now
        if azure is not None:
            new_base["azure"] = azure
        if pipes is not None:
            new_base["pipelines"] = pipes
        BASELINE.write_text(json.dumps(new_base, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    sys.exit(2 if (n and not first_run) else 0)


if __name__ == "__main__":
    main()
