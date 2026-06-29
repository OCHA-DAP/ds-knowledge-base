"""Check framework validity periods — flag frameworks whose doc-stated validity has lapsed.

Every framework page carries `valid_until` (the END of the validity period stated in the framework
doc: YYYY | YYYY-MM | YYYY-MM-DD). This script reads them all and reports:

  EXPIRED        — an ENDORSED version whose validity has ended (still live but past its period →
                   needs review: renew, supersede, or retire). FAILS the check (exit 1).
  MISSING        — an ENDORSED version with no `valid_until` (the period should be in the doc;
                   extract it, or set null with a reason if the doc genuinely states none). Warning.
  EXPIRING_SOON  — ends within 120 days. Heads-up.
  MALFORMED      — `valid_until` isn't a YYYY / YYYY-MM / YYYY-MM-DD value. FAILS the check.

Superseded / retired / development versions are not failed (an expired superseded version is normal).

Stdlib only — no DB, no secrets. Writes a summary to $GITHUB_STEP_SUMMARY when set.
Usage:  python scripts/check_validity.py
"""
import glob, re, sys, os, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TODAY = datetime.date.today()
SOON_DAYS = 120

def frontmatter(p):
    t = Path(p).read_text(encoding="utf-8"); m = re.match(r'^---\n(.*?)\n---', t, re.S)
    b = m.group(1) if m else ""
    g = lambda k: (re.search(rf'^{k}:\s*(.+)$', b, re.M) or [None, ""])[1].strip().strip('"').split('"')[0].split('#')[0].strip()
    return g

def end_of(vu):
    """Parse valid_until -> (end_date, malformed?). Empty/null -> (None, False)."""
    if not vu or vu.lower() in ("null", "none", ""):
        return None, False
    s = vu.strip().strip('"')
    if re.match(r'^\d{4}$', s):
        return datetime.date(int(s), 12, 31), False
    if re.match(r'^\d{4}-\d{2}$', s):
        y, mo = map(int, s.split("-"))
        nxt = datetime.date(y + (mo == 12), (mo % 12) + 1, 1)
        return nxt - datetime.timedelta(days=1), False
    if re.match(r'^\d{4}-\d{2}-\d{2}$', s):
        try: return datetime.datetime.strptime(s, "%Y-%m-%d").date(), False
        except ValueError: return None, True
    return None, True

def main():
    expired, missing, soon, malformed, ok = [], [], [], [], []
    for f in sorted(glob.glob(str(ROOT / "frameworks/*/*.md"))):
        if f.endswith(("README.md", "_TEMPLATE.md")): continue
        g = frontmatter(f)
        fw, ver, st, vu = g("framework"), g("version"), g("status"), g("valid_until")
        if not fw or st != "endorsed":            # only live/endorsed versions are actionable
            continue
        end, bad = end_of(vu)
        tag = f"{fw} {ver}"
        if bad:
            malformed.append(f"{tag}: valid_until={vu!r} (not YYYY / YYYY-MM / YYYY-MM-DD)")
        elif end is None:
            missing.append(f"{tag}: no valid_until (validity should be stated in the framework doc)")
        elif end < TODAY:
            expired.append(f"{tag}: validity ended {end} — review (renew / supersede / retire)")
        elif (end - TODAY).days <= SOON_DAYS:
            soon.append(f"{tag}: validity ends {end} (in {(end - TODAY).days} days)")
        else:
            ok.append(f"{tag}: valid until {end}")

    lines = [f"# Framework validity check — {TODAY}", ""]
    def section(title, items):
        lines.append(f"## {title} ({len(items)})")
        lines.extend([f"- {x}" for x in items] if items else ["- none"])
        lines.append("")
    section("❌ EXPIRED (endorsed but past validity)", expired)
    section("⚠️ MISSING valid_until", missing)
    section("🛠 MALFORMED valid_until", malformed)
    section("⏳ Expiring soon (≤120 days)", soon)
    lines.append(f"*{len(ok)} endorsed frameworks valid.*")
    report = "\n".join(lines)
    print(report)
    summ = os.environ.get("GITHUB_STEP_SUMMARY")
    if summ:
        with open(summ, "a") as fh: fh.write(report + "\n")

    fail = len(expired) + len(malformed)
    if fail:
        print(f"\nFAIL: {len(expired)} expired, {len(malformed)} malformed.", file=sys.stderr)
        sys.exit(1)
    print(f"\nOK: {len(ok)} valid, {len(missing)} missing, {len(soon)} expiring soon.")

if __name__ == "__main__":
    main()
