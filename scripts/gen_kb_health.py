#!/usr/bin/env python3
"""KB self-health — the KB's OWN GitHub Actions workflows, health-checked the way the
pipeline registry health-checks the team's pipelines (D106).

Why: the KB watches every spoke (pipeline registry, pages registry, infra drift) but until
Sept 2026 nothing watched the machine that does the watching. Three of its own workflows
sat red on `main` for one to two weeks (#631) — a `TypeError` on every nightly, visible only
in the Actions tab, noticed by accident when a PR merge fanned the failures out.

What it does — a pure function of this repo + `gh run list` (no secrets beyond `GITHUB_TOKEN`):
  1. Reads every `.github/workflows/*.yml`: name, `schedule:` crons, other triggers.
  2. Pulls the last runs ON `main` for each (`gh run list --branch main`).
  3. Judges each with the pipeline registry's rule (same GRACE, same cadence parser):
       scheduled  → DOWN if the latest completed run FAILED or no success within cadence×2
                    (seasonal crons exempt from OVERDUE); WARN on a lone cancellation /
                    NO-RUNS; OK otherwise.
       event/dispatch (push, PR, issues, workflow_dispatch…) → last-run-only: DOWN when the
                    last TWO non-cancelled runs failed, WARN on one failure (a dispatch-only
                    workflow like kb-ingest can fail on one bad input — that's the input's
                    problem; two in a row is the workflow's), OK on success, idle when no runs.
     Cancelled / skipped runs are neutral (concurrency-cancelled runs are not failures).
  4. Writes infrastructure/kb-health.md (+ .kb-health.json) and, with --report, the
     attention section for the `kb-self-health` issue.

Exit codes (kb-health.yml): 0 clean · 2 something is DOWN (issue opened/refreshed) ·
1 could not assess (gh failed for every workflow — nothing is written, same rule as the
pipeline registry: never overwrite a good board with an empty one).

Health is judged on `main` only. A failing PR check is the PR's problem, not the KB's.
"""
from __future__ import annotations

import argparse
import datetime
import json
import subprocess
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gen_pipeline_registry import GRACE, cron5_interval_h, is_seasonal  # noqa: E402 — one cadence rule for both boards

ROOT = Path(__file__).resolve().parent.parent
WF_DIR = ROOT / ".github" / "workflows"
OUT_MD = ROOT / "infrastructure" / "kb-health.md"
OUT_JSON = ROOT / "infrastructure" / ".kb-health.json"
REPO = "OCHA-DAP/ds-knowledge-base"
NOW = datetime.datetime.now(datetime.timezone.utc)
RUNS = 15                                   # enough to see a streak on a daily job
FAILED = {"failure", "timed_out", "startup_failure", "action_required"}
NEUTRAL = {"cancelled", "skipped", "neutral", "stale", None, ""}
EVENT_TRIGGERS = {"push", "pull_request", "pull_request_target", "issues", "issue_comment",
                  "pull_request_review", "pull_request_review_comment", "repository_dispatch", "release"}
DOT = {"OK": "🟢", "WARN": "🟡", "DOWN": "🔴", "UNKNOWN": "⚪", "—": "·"}
ORDER = {"DOWN": 0, "UNKNOWN": 1, "WARN": 2, "OK": 3, "—": 4}


# ---- workflows ---------------------------------------------------------------------
def triggers_of(path: Path) -> dict:
    doc = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    on = doc.get("on", doc.get(True, {}))   # PyYAML reads a bare `on:` key as boolean True
    if isinstance(on, str):
        on = {on: {}}
    if isinstance(on, list):
        on = {k: {} for k in on}
    crons = [str(s["cron"]) for s in (on.get("schedule") or []) if isinstance(s, dict) and s.get("cron")]
    return {"file": path.name, "name": doc.get("name") or path.name, "crons": crons,
            "events": sorted(k for k in on if k != "schedule")}


def role_of(t: dict) -> str:
    if t["crons"]:
        return "scheduled"
    return "event" if set(t["events"]) & EVENT_TRIGGERS else "dispatch"


def cadence_of(t: dict) -> tuple[float | None, str]:
    """Shortest interval across the workflow's crons (a workflow with two crons fires at both)."""
    best = None
    for c in t["crons"]:
        iv, label = cron5_interval_h(c)
        if iv and (best is None or iv < best[0]):
            best = (iv, label)
    if best:
        return best
    return None, {"event": "on event", "dispatch": "dispatch only"}[role_of(t)]


# ---- runs ----------------------------------------------------------------------------
def gh_runs(wf_file: str) -> tuple[list[dict] | None, str]:
    try:
        r = subprocess.run(["gh", "run", "list", "-R", REPO, "--workflow", wf_file, "--branch", "main",
                            "-L", str(RUNS), "--json", "conclusion,status,createdAt,event,url,databaseId"],
                           capture_output=True, text=True, timeout=90)
        if r.returncode != 0:
            return None, (r.stderr or "").strip()[:200] or f"exit {r.returncode}"
        return json.loads(r.stdout or "[]"), ""
    except Exception as ex:                    # noqa: BLE001 — missing gh, timeout…
        return None, f"{type(ex).__name__}: {ex}"


def age_h(run: dict | None) -> float | None:
    if not run:
        return None
    dt = datetime.datetime.fromisoformat(run["createdAt"].replace("Z", "+00:00"))
    return round((NOW - dt).total_seconds() / 3600, 1)


# ---- health --------------------------------------------------------------------------
def assess(t: dict, runs: list[dict] | None, err: str) -> dict:
    role = role_of(t)
    interval, cadence = cadence_of(t)
    e = {"file": t["file"], "name": t["name"], "role": role, "cadence": cadence, "interval_h": interval,
         "crons": t["crons"], "events": t["events"], "seasonal": any(is_seasonal(c) for c in t["crons"]),
         "last_result": None, "last_age_h": None, "last_url": None, "success_age_h": None,
         "fail_streak": 0, "health": "—", "flags": []}
    if runs is None:
        e["health"], e["flags"] = "UNKNOWN", [f"RUNS-UNRETRIEVABLE({err})"]
        return e

    judged = [r for r in runs if r.get("status") == "completed" and r.get("conclusion") not in NEUTRAL]
    last = judged[0] if judged else None
    succ = next((r for r in judged if r.get("conclusion") == "success"), None)
    streak = 0
    for r in judged:
        if r.get("conclusion") in FAILED:
            streak += 1
        else:
            break
    e.update({"last_result": (last or {}).get("conclusion"), "last_age_h": age_h(last), "last_url": (last or {}).get("url"),
              "success_age_h": age_h(succ), "fail_streak": streak})

    flags: list[str] = []
    if role == "scheduled":
        if not judged:
            e["health"], e["flags"] = ("OK", ["SEASONAL-IDLE"]) if e["seasonal"] else ("WARN", ["NO-RUNS"])
            return e
        if last.get("conclusion") in FAILED:
            flags.append(f"FAILING(×{streak})" if streak > 1 else "FAILING")
        if interval and not e["seasonal"]:
            sa = e["success_age_h"]
            if sa is None:
                flags.append("NO-SUCCESS")
            elif sa > interval * GRACE:
                flags.append(f"OVERDUE(>{round(interval * GRACE)}h)")
        down = any(f.startswith(("FAILING", "OVERDUE", "NO-SUCCESS")) for f in flags)
        e["health"] = "DOWN" if down else ("WARN" if flags else "OK")
    else:
        if not judged:
            e["health"] = "—"                  # never ran on main (or only cancelled runs) — nothing to judge
        elif streak >= 2:
            e["health"], flags = "DOWN", [f"FAILING(×{streak})"]
        elif streak == 1:
            e["health"], flags = "WARN", ["LAST-RUN-FAILED"]
        else:
            e["health"] = "OK"
    e["flags"] = flags
    return e


# ---- render --------------------------------------------------------------------------
def fmt_age(h: float | None) -> str:
    if h is None:
        return "—"
    return f"{h}h ago" if h < 48 else f"{round(h / 24, 1)}d ago"


def row(e: dict) -> str:
    last = f"[{e['last_result']}]({e['last_url']})" if e["last_url"] else (e["last_result"] or "—")
    when = f" · {fmt_age(e['last_age_h'])}" if e["last_age_h"] is not None else ""
    role = {"scheduled": e["cadence"], "event": "on " + "/".join(e["events"]), "dispatch": "dispatch only"}[e["role"]]
    return (f"| {DOT[e['health']]} {e['health']} | `{e['file']}` | {role} | {last}{when} | "
            f"{fmt_age(e['success_age_h'])} | {e['fail_streak'] or '—'} | {', '.join(e['flags']) or '—'} |")


HEADER = "| health | workflow | when | last run (main) | last success | fail streak | flags |\n|:--:|---|---|---|---|:--:|---|"


def render(entries: list[dict], unknown_all: bool) -> tuple[str, str]:
    entries = sorted(entries, key=lambda e: (ORDER[e["health"]], e["file"]))
    n = {k: len([e for e in entries if e["health"] == k]) for k in DOT}
    summary = (f"**🔴 {n['DOWN']} down · 🟡 {n['WARN']} warn · ⚪ {n['UNKNOWN']} unknown · 🟢 {n['OK']} ok · "
               f"{n['—']} idle** ({len(entries)} workflows)")
    md = [
        "# KB self-health",
        "",
        "_Generated by `scripts/gen_kb_health.py` — DO NOT EDIT BY HAND._  ",
        f"_Snapshot: {NOW:%Y-%m-%d %H:%M} UTC._",
        "",
        "The KB's **own** GitHub Actions workflows — the machine described in [automation.md](automation.md) — judged on `main` "
        "with the same last-success-vs-cadence rule the [pipeline registry](pipeline-registry.md) applies to the team's pipelines. "
        "The pipeline registry keeps the trains on the tracks; this page checks the signalman. Scheduled workflows: DOWN when the "
        f"latest run failed or no success within cadence × {GRACE:g}. Event/dispatch workflows: DOWN after two consecutive failures, "
        "WARN after one (a dispatch can fail on one bad input). Cancelled runs are neutral. Anything DOWN opens/refreshes the "
        "`kb-self-health` issue (`kb-health.yml`, daily); it closes itself when the board is clean.",
        "",
        summary,
        "",
        HEADER,
    ] + [row(e) for e in entries] + [
        "",
        "Flags: **FAILING** latest completed run on `main` failed (×n = consecutive) · **OVERDUE** no success within cadence × "
        f"{GRACE:g} · **NO-SUCCESS** ran, never succeeded in the last {RUNS} runs · **NO-RUNS** scheduled but nothing ran · "
        "**LAST-RUN-FAILED** one failure on an event/dispatch workflow · **SEASONAL-IDLE** cron restricted to some months · "
        "**RUNS-UNRETRIEVABLE** `gh run list` failed (token scope?).",
        "",
        "**Fixing a red row:** open the linked run, read the failed step; most causes are a signature/vocabulary change in a shared "
        "script (add the caller to `lint-docs.yml`'s offline smokes so it fails at PR time next time), a dead secret/token "
        "(`automation.md` → *Running it / secrets*), or a spoke that moved. After the fix, re-run the workflow "
        "(`gh workflow run <file>`) rather than waiting for the next cron, and check this board's next refresh.",
        "",
    ]
    bad = [e for e in entries if e["health"] in ("DOWN", "UNKNOWN")]
    warn = [e for e in entries if e["health"] == "WARN"]
    report = [
        "# KB self-health — workflows needing attention",
        "",
        f"_Generated by `scripts/gen_kb_health.py` — {NOW:%Y-%m-%d %H:%M} UTC. Full board: `infrastructure/kb-health.md`._",
        "",
    ]
    if unknown_all:
        report += ["> ⚠️ `gh run list` failed for every workflow — nothing was assessed this run (token scope? outage?).", ""]
    if bad:
        report += [f"## 🔴 Down ({len(bad)})", "", "The KB's own automation is not running. Open the linked run, fix, re-run.", "", HEADER]
        report += [row(e) for e in bad] + [""]
    if warn:
        report += [f"## 🟡 Warn ({len(warn)})", "", HEADER] + [row(e) for e in warn] + [""]
    report += ["_This issue refreshes daily and closes itself when every workflow is green on `main`._", ""]
    return "\n".join(md), "\n".join(report)


# ---- main ----------------------------------------------------------------------------
def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--report", help="write the attention section (issue body) here")
    ap.add_argument("--dry-run", action="store_true", help="print the board, write nothing")
    args = ap.parse_args()

    wfs = sorted(WF_DIR.glob("*.yml")) + sorted(WF_DIR.glob("*.yaml"))
    entries = []
    for wf in wfs:
        t = triggers_of(wf)
        runs, err = gh_runs(wf.name)
        entries.append(assess(t, runs, err))

    unknown_all = bool(entries) and all(e["health"] == "UNKNOWN" for e in entries)
    md, report = render(entries, unknown_all)
    down = [e for e in entries if e["health"] == "DOWN"]

    if args.dry_run:
        print(md)
        return 2 if down else 0
    if unknown_all:
        sys.exit("ERROR: could not retrieve runs for any workflow (`gh run list` failing — GH_TOKEN scope, rate limit, "
                 "outage?). Not writing the board.")
    OUT_MD.write_text(md, encoding="utf-8")
    OUT_JSON.write_text(json.dumps({"generated": NOW.isoformat(timespec="seconds"), "repo": REPO, "grace": GRACE,
                                    "workflows": entries}, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    if args.report:
        Path(args.report).write_text(report, encoding="utf-8")
    print(f"Wrote {OUT_MD.relative_to(ROOT)} — {len(entries)} workflows, "
          f"{len(down)} down, {len([e for e in entries if e['health'] == 'WARN'])} warn.")
    return 2 if down else 0


if __name__ == "__main__":
    sys.exit(main())
