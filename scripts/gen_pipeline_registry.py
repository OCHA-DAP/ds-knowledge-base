#!/usr/bin/env python3
"""Generate the authoritative prod-pipeline registry + health dashboard.

The unit of a "pipeline" is a DEPLOYED SCHEDULED JOB keyed by its runtime handle
(Databricks job_id OR GitHub Actions workflow) — see docs/DESIGN.md D43. This is
what supersedes `pipelines-status`: it spans BOTH Databricks and GHA, records the
two dev/prod axes (deployment compute + data-plane mode), and health-checks each
entry's last run against its expected cadence — "keeping the trains on the tracks".

Reads LIVE state:
  - Databricks: `databricks jobs list|get` + `jobs list-runs` (profile `default`;
    token expires → `databricks auth login --profile default`).
  - GHA: `gh run list -R <repo> --workflow <file>` for the seeded prod workflows.

Writes:
  - infrastructure/pipeline-registry.md   (human dashboard, health-sorted)
  - infrastructure/.pipeline-registry.json (structured, for the dep graph / future)

Health is a heuristic (cadence inferred from cron); it flags, it doesn't page.
"""
from __future__ import annotations
import datetime, json, os, re, subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT_MD = ROOT / "infrastructure" / "pipeline-registry.md"
OUT_JSON = ROOT / "infrastructure" / ".pipeline-registry.json"
# Local: a configured CLI profile (`default`). CI: set DATABRICKS_PROFILE="" to
# fall back to DATABRICKS_HOST/TOKEN env auth (no `-p` flag passed).
PROFILE = os.environ.get("DATABRICKS_PROFILE", "default")
NOW = datetime.datetime.now(datetime.timezone.utc)
NOW_MS = NOW.timestamp() * 1000
GRACE = 2.0  # an entry is OVERDUE only past expected_interval * GRACE since last success

# The Job Compute policy that injects the dsci secrets into every prod job.
JOB_COMPUTE_POLICY = "000C79D951EAF0D6"

# GHA prod pipelines (the half pipelines-status is blind to). Seeded from
# infrastructure/deployments.md; cron drives the cadence heuristic, the live
# check uses `gh run list`. Keep in sync as GHA pipelines are ingested.
GHA_SEED = [
    # workflow path verified live 2026-06-22 unless noted "unverified".
    {"repo": "ds-nhc-forecast", "workflow": "run-python-script.yaml", "cron": "0 */3 * * *",
     "writes": "storms.nhc_* (intended prod NHC writer)", "note": "verify: last run 2026-06-08 (failing) — may be defunct"},
    {"repo": "ds-floodexposure-monitoring", "workflow": "run_update_exposure.yml", "cron": "15 23 * * *",
     "writes": "app.floodscan_exposure", "note": "head of the daily exposure → quantiles → raster-stats chain"},
    {"repo": "ds-aa-eth-drought-monitoring", "workflow": "run_monitoring.yml", "cron": "0 6 6 2,4,5 *",
     "writes": "ETH drought monitoring", "seasonal": True, "note": "fires 6th of Feb/Apr/May only — idle otherwise"},
    {"repo": "ds-storm-impact-harmonisation", "workflow": "daily-gdacs-monitor-email.yml", "cron": "20 3,9,15,21 * * *",
     "writes": "GDACS monitor email", "note": ""},
    {"repo": "ds-pipelines-status", "workflow": "update.yml", "cron": "15 */6 * * *",
     "writes": "data/pipelines.json (the meta-pipeline being superseded)", "note": ""},
    {"repo": "ds-aa-mdg-monitoring", "workflow": "run_monitor_imerg.yml", "cron": "0 16 * * *",
     "writes": "MDG IMERG monitoring emails", "note": ""},
    {"repo": "ds-afro-cholera", "workflow": "daily_alerts.yml", "cron": "0 6 * * *",
     "writes": "global cholera alerts (Listmonk)", "note": ""},
    {"repo": "ds-acled-fetcher", "workflow": "main.yml", "cron": "0 8 * * *",
     "writes": "ACLED conflict data", "note": ""},
    {"repo": "ds-nga-flood-monitoring", "workflow": "nga-gauge-monitor.yaml", "cron": "0 14 * * *",
     "writes": "NGA flood gauge monitoring", "note": "workflow not on default branch — verify path/branch"},
    # ds-cholera-pdf-scraper omitted: the scheduled download triggers a workflow_run
    # chain (extract/rule-based/post-process) — not a single cron pipeline, so the
    # cadence heuristic doesn't fit. Revisit with per-chain modelling.
]

# Per-Databricks-job human overlay the API can't supply.
DBX_NOTES = {
    "527252598381643": "triggered by NHC Pipeline (fire-and-forget); runs main, no schedule",
}


def sh(args: list[str]) -> str:
    try:
        return subprocess.run(args, capture_output=True, text=True, timeout=90).stdout
    except Exception:
        return ""


def dbx(args: list[str]):
    prof = ["-p", PROFILE] if PROFILE else []   # empty PROFILE → env (DATABRICKS_HOST/TOKEN) auth
    out = sh(["databricks", *args, *prof, "-o", "json"])
    try:
        return json.loads(out) if out.strip() else None
    except Exception:
        return None


# ---- cadence heuristic --------------------------------------------------------
def quartz_interval_h(cron: str):
    """(interval_hours, label) from a Quartz 6/7-field cron (sec min hr dom mon dow)."""
    f = cron.split()
    if len(f) < 6:
        return cron5_interval_h(cron)
    hr, dom, mon, dow = f[2], f[3], f[4], f[5]
    return _from_fields(hr, dom, dow)


def cron5_interval_h(cron: str):
    """(interval_hours, label) from a standard 5-field cron (min hr dom mon dow)."""
    f = cron.split()
    if len(f) < 5:
        return (None, "?")
    return _from_fields(f[1], f[2], f[4])


def is_seasonal(cron: str) -> bool:
    """True if the cron's MONTH field is restricted (fires only some months)."""
    if not cron or cron in ("trigger", None):
        return False
    f = cron.split()
    mon = f[4] if len(f) >= 6 else (f[3] if len(f) >= 5 else "*")  # quartz field5 / cron field4
    return mon not in ("*", "?")


def _from_fields(hr, dom, dow):
    if "/" in hr:                                   # 0/3 or */3 → every N hours
        n = int(hr.split("/")[1]); return (n, f"every {n}h")
    if "," in hr:                                   # 3,9,15,21 → 24/count
        n = len(hr.split(",")); return (round(24 / n, 1), f"{n}×/day")
    # single fixed hour:
    if dom not in ("*", "?") and not dom.startswith("*"):
        if "," in dom:
            return (24 * 30 / len(dom.split(",")), "monthly (n days)")
        return (24 * 31, "monthly")                 # fixed day-of-month → monthly
    if dow not in ("*", "?"):
        return (24 * 7 / max(1, len(dow.split(","))), "weekly")
    return (24, "daily")                            # fixed hour, every day


# ---- databricks ---------------------------------------------------------------
def data_mode(settings: dict):
    """dev|prod|None from job params / task args."""
    vals = []
    for p in (settings.get("parameters") or []):
        if p.get("name") in ("mode", "stage", "STAGE") and p.get("default"):
            vals.append(str(p["default"]).lower())
    for t in (settings.get("tasks") or []):
        args = (t.get("spark_python_task") or {}).get("parameters") or []
        for i, a in enumerate(args):
            if a == "--mode" and i + 1 < len(args):
                vals.append(str(args[i + 1]).lower())
        for k, v in ((t.get("notebook_task") or {}).get("base_parameters") or {}).items():
            if k.lower() in ("mode", "stage"):
                vals.append(str(v).lower())
    for v in ("prod", "dev"):
        if v in vals:
            return v
    return None


def compute_of(settings: dict, personal_ids: set):
    jc = {c["job_cluster_key"]: (c.get("new_cluster") or {}) for c in (settings.get("job_clusters") or [])}
    kinds = set()
    for t in (settings.get("tasks") or []):
        ec = t.get("existing_cluster_id")
        if ec:
            kinds.add("personal:" + ec if ec in personal_ids else "existing:" + ec)
        elif t.get("job_cluster_key"):
            nc = jc.get(t["job_cluster_key"], {})
            kinds.add("job-compute" if nc.get("policy_id") == JOB_COMPUTE_POLICY else "job-cluster(custom)")
        elif t.get("new_cluster"):
            nc = t["new_cluster"]
            kinds.add("job-compute" if nc.get("policy_id") == JOB_COMPUTE_POLICY else "job-cluster(custom)")
        else:
            kinds.add("serverless/other")
    return ",".join(sorted(kinds)) or "?"


def repo_of(settings: dict):
    gs = settings.get("git_source") or {}
    if gs.get("git_url"):
        return gs["git_url"].replace("https://github.com/", "").replace(".git", "").rstrip("/")
    return None


def schedule_of(settings: dict):
    sc = settings.get("schedule") or {}
    if sc.get("quartz_cron_expression"):
        return sc["quartz_cron_expression"], sc.get("pause_status", "?")
    if settings.get("trigger"):
        return "trigger", "—"
    return None, "—"


def last_run_dbx(job_id) -> dict:
    runs = dbx(["jobs", "list-runs", "--job-id", str(job_id), "--limit", "10"]) or []
    runs = runs if isinstance(runs, list) else runs.get("runs", [])
    last = runs[0] if runs else None
    last_success = next((r for r in runs if (r.get("state") or {}).get("result_state") == "SUCCESS"), None)
    def age_h(r):
        t = r.get("start_time")
        return round((NOW_MS - t) / 3.6e6, 1) if t else None
    return {
        "last_result": (last.get("state") or {}).get("result_state") if last else None,
        "last_life": (last.get("state") or {}).get("life_cycle_state") if last else None,
        "last_age_h": age_h(last) if last else None,
        "success_age_h": age_h(last_success) if last_success else None,
        "url": last.get("run_page_url") if last else None,
    }


def collect_databricks(personal_ids: set) -> list[dict]:
    jobs = dbx(["jobs", "list"]) or []
    out = []
    for j in jobs:
        # `jobs list` returns ABBREVIATED settings (name/tags/schedule but no
        # git_source/tasks) — fetch full settings so repo, data-mode and compute
        # (the dev/prod axes) populate.
        full = dbx(["jobs", "get", str(j["job_id"])]) or {}  # positional JOB_ID (not --job-id)
        s = full.get("settings") or j.get("settings", {})
        name = s.get("name", "?")
        cron, pause = schedule_of(s)
        tags = s.get("tags") or {}
        if cron is None or cron == "trigger":
            category = "trigger/manual"
        elif name.startswith("[dev "):
            category = "dev"
        else:
            category = "prod"
        interval, cad = quartz_interval_h(cron) if cron and cron != "trigger" else (None, "manual")
        e = {
            "handle": f"dbx:{j['job_id']}", "kind": "databricks", "job_id": str(j["job_id"]),
            "name": name, "repo": repo_of(s), "cron": cron, "cadence": cad, "interval_h": interval,
            "seasonal": is_seasonal(cron), "paused": pause == "PAUSED", "category": category,
            "data_mode": data_mode(s), "compute": compute_of(s, personal_ids),
            "writes": tags.get("output_schema") or tags.get("blob_container"),
            "in_status_dashboard": tags.get("databricks") == "job",
            "note": DBX_NOTES.get(str(j["job_id"]), ""),
        }
        e.update(last_run_dbx(j["job_id"]) if category == "prod" else
                 {"last_result": None, "last_age_h": None, "success_age_h": None, "url": None})
        out.append(e)
    return out


def personal_cluster_ids() -> set:
    cs = dbx(["clusters", "list"]) or []
    return {c["cluster_id"] for c in cs if c.get("cluster_source") in ("UI", "API")}


# ---- gha ----------------------------------------------------------------------
def collect_gha() -> list[dict]:
    out = []
    for g in GHA_SEED:
        interval, cad = cron5_interval_h(g["cron"])
        runs = sh(["gh", "run", "list", "-R", f"OCHA-DAP/{g['repo']}", "--workflow", g["workflow"],
                   "-L", "5", "--json", "conclusion,status,createdAt,url"])
        last_result = last_age = url = None
        try:
            rl = json.loads(runs) if runs.strip() else []
            if rl:
                last = rl[0]
                url = last.get("url")
                last_result = (last.get("conclusion") or last.get("status") or "").upper() or None
                ts = last.get("createdAt")
                if ts:
                    dt = datetime.datetime.fromisoformat(ts.replace("Z", "+00:00"))
                    last_age = round((NOW - dt).total_seconds() / 3600, 1)
                succ = next((r for r in rl if r.get("conclusion") == "success"), None)
                succ_age = None
                if succ:
                    dt = datetime.datetime.fromisoformat(succ["createdAt"].replace("Z", "+00:00"))
                    succ_age = round((NOW - dt).total_seconds() / 3600, 1)
            else:
                succ_age = None
        except Exception:
            succ_age = None
        out.append({
            "handle": f"gha:{g['repo']}/{g['workflow']}", "kind": "gha", "job_id": None,
            "name": g["workflow"], "repo": f"OCHA-DAP/{g['repo']}", "cron": g["cron"],
            "cadence": cad, "interval_h": interval, "seasonal": g.get("seasonal", False) or is_seasonal(g["cron"]),
            "paused": False, "category": "prod",
            "data_mode": None, "compute": "github-actions", "writes": g["writes"],
            "in_status_dashboard": False, "note": g["note"],
            "last_result": last_result, "last_age_h": last_age, "success_age_h": succ_age, "url": url,
        })
    return out


# ---- health -------------------------------------------------------------------
FAIL_STATES = ("FAILED", "FAILURE", "ERROR", "TIMEDOUT", "CANCELED", "CANCELLED", "INTERNAL_ERROR")


def health(e: dict) -> tuple[str, list[str]]:
    """(status OK|WARN|DOWN|UNKNOWN, flags) for a prod entry.

    Conservative by design — never a false DOWN: a paused job is WARN not DOWN (the
    pause explains it); a seasonal job idle out of season is OK; a GHA workflow whose
    runs we can't retrieve (wrong path / non-default branch / no access) is UNKNOWN,
    not a health claim. Only confirmed FAILING / OVERDUE-with-history → DOWN."""
    if e["category"] != "prod":
        return "—", []
    last, iv, sa = e.get("last_result"), e.get("interval_h"), e.get("success_age_h")
    flags = []

    if e["paused"]:                                   # paused dominates: it's a state, not an outage
        flags.append("PAUSED")
    if e["kind"] == "gha" and last is None and not e.get("seasonal"):
        return "UNKNOWN", ["UNVERIFIED(path/branch?)"]  # can't retrieve runs → no claim
    if e.get("seasonal") and last is None:
        flags.append("SEASONAL-IDLE")

    if not e["paused"]:
        if last is None and e["kind"] == "databricks":
            flags.append("NO-RUNS")                  # deployed, never ran → WARN (could be new)
        elif last is not None:                       # ran at least once → can judge success/cadence
            if str(last) in FAIL_STATES:
                flags.append("FAILING")
            if iv and not e.get("seasonal") and (sa is None or sa > iv * GRACE):
                flags.append(f"OVERDUE(>{round(iv * GRACE)}h)" if sa is not None else "NO-SUCCESS")
    if e["kind"] == "databricks" and e.get("data_mode") and e["data_mode"] != "prod":
        flags.append(f"MODE={e['data_mode']}")
    if "personal:" in (e.get("compute") or ""):
        flags.append("PERSONAL-CLUSTER")

    down = (not e["paused"]) and any(f.startswith(("FAILING", "OVERDUE", "NO-SUCCESS")) for f in flags)
    if down:
        return "DOWN", flags
    return ("WARN" if flags else "OK"), flags


DOT = {"OK": "🟢", "WARN": "🟡", "DOWN": "🔴", "UNKNOWN": "⚪", "—": "·"}


def md_table(entries: list[dict]) -> str:
    rows = []
    for e in entries:
        st, flags = e["_status"], e["_flags"]
        sa = e.get("success_age_h")
        last = f"{sa}h ago" if sa is not None else (f"{e['last_age_h']}h (last)" if e.get("last_age_h") is not None else "—")
        link = f"[{e['name']}]({e['url']})" if e.get("url") else e["name"]
        mode = e.get("data_mode") or ("—" if e["kind"] == "gha" else "?")
        rows.append(f"| {DOT[st]} {st} | `{e['handle']}` | {link} | {e.get('repo') or '—'} | "
                    f"{e.get('cadence','?')} | {last} | {mode} | {e.get('writes') or '—'} | "
                    f"{', '.join(flags) or '—'} |")
    head = ("| health | handle | name | repo | cadence | last success | data-mode | writes | flags |\n"
            "|:--:|---|---|---|---|---|:--:|---|---|\n")
    return head + "\n".join(rows)


def main():
    personal = personal_cluster_ids()
    dbx_entries = collect_databricks(personal)
    if not dbx_entries:
        # No jobs came back → almost certainly a Databricks auth failure (expired token
        # / missing DATABRICKS_HOST+TOKEN). Refuse to overwrite a good registry with an
        # empty one (this is what would clobber the committed file in a CI run without
        # secrets). Exit non-zero so the caller notices.
        import sys
        sys.exit("ERROR: Databricks returned no jobs — auth not configured? "
                 "Run `databricks auth login --profile default` (local) or set "
                 "DATABRICKS_HOST/TOKEN (CI). Not overwriting the existing registry.")
    entries = dbx_entries + collect_gha()
    for e in entries:
        e["_status"], e["_flags"] = health(e)

    prod = [e for e in entries if e["category"] == "prod"]
    order = {"DOWN": 0, "WARN": 1, "UNKNOWN": 2, "OK": 3, "—": 4}
    prod.sort(key=lambda e: (order[e["_status"]], e["kind"], e["name"]))
    other = [e for e in entries if e["category"] != "prod"]

    n = {s: sum(1 for e in prod if e["_status"] == s) for s in ("DOWN", "WARN", "UNKNOWN", "OK")}
    ts = NOW.strftime("%Y-%m-%d %H:%M UTC")

    md = [
        "# Prod-pipeline registry & health",
        "",
        "_Generated by `scripts/gen_pipeline_registry.py` — DO NOT EDIT BY HAND._  ",
        f"_Snapshot: {ts}._",
        "",
        "The authoritative list of **deployed scheduled pipelines** — one row per job, "
        "keyed by runtime handle (`dbx:<job_id>` or `gha:<repo>/<workflow>`), spanning "
        "**Databricks + GitHub Actions**. This is the supersede-target for "
        "[pipelines-status](../pipelines/pipelines-status.md) (which is Databricks-only, "
        "`databricks=job`-tag-reliant, and display-only). A pipeline is a real prod writer "
        "only when it is **unpaused AND `data-mode=prod`** — see "
        "[databricks.md → the two dev/prod axes](databricks.md#the-two-devprod-axes-this-is-the-subtle-part).",
        "",
        f"**Health: {DOT['DOWN']} {n['DOWN']} down · {DOT['WARN']} {n['WARN']} warn · "
        f"{DOT['UNKNOWN']} {n['UNKNOWN']} unknown · {DOT['OK']} {n['OK']} ok** "
        f"(of {len(prod)} prod pipelines). Heuristic: OVERDUE = no success within cadence × {GRACE:g}; "
        f"UNKNOWN = GHA runs not retrievable (path/branch/access).",
        "",
        "## Prod pipelines",
        "",
        md_table(prod),
        "",
        "### Flag legend",
        "- 🔴 **FAILING** last run errored · **OVERDUE** no success within the expected cadence · "
        "**NO-RUNS/NO-SUCCESS** never (successfully) ran.",
        "- 🟡 **PAUSED** schedule disabled · **MODE=dev** prod-compute job writing the DEV data plane "
        "(cutover) · **PERSONAL-CLUSTER** scheduled job pinned to a personal interactive cluster (fragile) "
        "· **SEASONAL-IDLE** seasonal pipeline, out of season now.",
        "- ⚪ **UNVERIFIED** GHA workflow runs couldn't be retrieved (wrong path / non-default branch / "
        "access) — not a health claim. Pin the path/branch to promote it to a real check.",
        "",
        "## Dev / trigger / manual jobs (not health-monitored)",
        "",
        md_table(other),
        "",
        "## Refresh",
        "`python3 scripts/gen_pipeline_registry.py` (needs `databricks auth login --profile default` + `gh` auth). "
        "GHA pipelines are seeded in the script (`GHA_SEED`); add rows as GHA pipelines are ingested.",
        "",
    ]
    OUT_MD.write_text("\n".join(md))
    OUT_JSON.write_text(json.dumps(
        {"generated": ts, "entries": [{k: v for k, v in e.items()} for e in entries]}, indent=2))
    print(f"Wrote {OUT_MD.relative_to(ROOT)} — {len(prod)} prod ({n['DOWN']} down / {n['WARN']} warn / "
          f"{n['OK']} ok), {len(other)} dev/manual.")
    for e in prod:
        if e["_status"] in ("DOWN", "WARN", "UNKNOWN"):
            print(f"  {DOT[e['_status']]} {e['name']:34} {', '.join(e['_flags'])}")


if __name__ == "__main__":
    main()
