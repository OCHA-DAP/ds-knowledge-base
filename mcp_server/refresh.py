"""Runtime self-refresh of the served KB tree (D100).

The deployed apps serve a deploy-time zip and have no CI redeploy path (no ARM
credential; publish-profile and OIDC are both blocked by org policy), so the
served KB silently lagged main — D99 found the public box missing 236 of 429
pages. The repo is PUBLIC, so the server needs no credential at all to fix
this itself: poll GitHub for main's HEAD sha and, when it moves, download the
tarball and atomically swap the tree the tools serve from.

Enabled by default only on App Service (WEBSITE_HOSTNAME set) so a local
`python -m mcp_server.server` keeps serving the local checkout unchanged;
KB_SELF_REFRESH=1/0 overrides in either direction.

What a swap preserves: each new tree gets the paths in KB_REFRESH_CARRYOVER
(default `drive,style-reference` — the internal tier's private content, which
is deliberately NOT in the public repo) hardlinked/copied from the ORIGINAL
deploy root. What a swap does NOT do: reload server *code* — the running
process never re-imports itself, so mcp_server/ changes still need a redeploy
(mcp_server/deploy/redeploy_*.sh, which stamp `.kb-refresh-sha` so a
just-deployed box skips the boot-time download).

Environment:
    KB_SELF_REFRESH      '1'/'0' force on/off (default: on iff WEBSITE_HOSTNAME set)
    KB_REFRESH_INTERVAL  poll seconds (default 900; min 60)
    KB_REFRESH_REPO      owner/name (default OCHA-DAP/ds-knowledge-base)
    KB_REFRESH_BRANCH    branch to track (default main)
    KB_REFRESH_CARRYOVER comma-sep dirs copied from the deploy root into each
                         new tree (default 'drive,style-reference')
    KB_REFRESH_DIR       where new trees are built (default: system temp)
"""
from __future__ import annotations

import io
import os
import shutil
import sys
import tarfile
import tempfile
import threading
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

_SHA_FILE = ".kb-refresh-sha"
_UA = {"User-Agent": "ds-knowledge-base-mcp-self-refresh"}

_lock = threading.Lock()
_base_root: Path | None = None
_current_root: Path | None = None
_previous_tree: Path | None = None  # kept one generation so in-flight calls finish
_state: dict = {"enabled": False, "sha": None, "refreshed_at": None,
                "last_check": None, "last_error": None, "source": "deploy"}


def _log(msg: str) -> None:
    print(f"[ds-knowledge-base mcp] refresh: {msg}", file=sys.stderr, flush=True)


def current_root() -> Path:
    with _lock:
        if _current_root is not None:
            return _current_root
        if _base_root is not None:
            return _base_root
    # start() not called (e.g. tools driven directly in tests) — same default as server.py
    return Path(os.environ.get("KB_ROOT", Path(__file__).resolve().parent.parent))


def status() -> dict:
    with _lock:
        return dict(_state)


def _enabled() -> bool:
    flag = os.environ.get("KB_SELF_REFRESH", "").strip().lower()
    if flag in ("1", "true", "yes"):
        return True
    if flag in ("0", "false", "no"):
        return False
    return bool(os.environ.get("WEBSITE_HOSTNAME"))


def _repo() -> str:
    return os.environ.get("KB_REFRESH_REPO", "OCHA-DAP/ds-knowledge-base").strip()


def _branch() -> str:
    return os.environ.get("KB_REFRESH_BRANCH", "main").strip()


def _interval() -> int:
    try:
        return max(60, int(os.environ.get("KB_REFRESH_INTERVAL", "900")))
    except ValueError:
        return 900


def _fetch(url: str, accept: str | None = None, timeout: int = 30) -> bytes:
    headers = dict(_UA)
    if accept:
        headers["Accept"] = accept
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=timeout) as resp:  # noqa: S310 — https only
        return resp.read()


def remote_sha() -> str:
    """HEAD sha of the tracked branch (GitHub API, unauthenticated, ~4 calls/hr)."""
    sha = _fetch(f"https://api.github.com/repos/{_repo()}/commits/{_branch()}",
                 accept="application/vnd.github.sha").decode().strip()
    if not (len(sha) == 40 and all(c in "0123456789abcdef" for c in sha)):
        raise ValueError(f"unexpected sha response: {sha[:60]!r}")
    return sha


def _safe_extract(tar: tarfile.TarFile, dest: Path) -> None:
    try:
        tar.extractall(dest, filter="data")  # py>=3.11.4: blocks traversal/links/devices
    except TypeError:  # older 3.11 — sanitize by hand
        for m in tar.getmembers():
            name = Path(m.name)
            if name.is_absolute() or ".." in name.parts or not (m.isfile() or m.isdir()):
                continue
            tar.extract(m, dest)


def _link_or_copy(src: str, dst: str) -> None:
    try:
        os.link(src, dst)  # free when same filesystem
    except OSError:
        shutil.copy2(src, dst)


def _build_tree(sha: str) -> Path:
    """Download the repo at `sha` and assemble a servable tree next to a
    `.kb-refresh-sha` stamp, with carryover dirs from the base root."""
    workdir = Path(os.environ.get("KB_REFRESH_DIR") or tempfile.gettempdir())
    workdir.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=f"kb-{sha[:8]}-", dir=workdir))
    tarball = _fetch(f"https://codeload.github.com/{_repo()}/tar.gz/{sha}", timeout=180)
    with tarfile.open(fileobj=io.BytesIO(tarball), mode="r:gz") as tar:
        _safe_extract(tar, staging)
    # tarball wraps everything in a single '<owner>-<name>-<sha7>/' dir
    inner = [p for p in staging.iterdir() if p.is_dir()]
    if len(inner) != 1:
        raise RuntimeError(f"unexpected tarball layout: {[p.name for p in staging.iterdir()]}")
    tree = inner[0]
    carryover = [d.strip() for d in
                 os.environ.get("KB_REFRESH_CARRYOVER", "drive,style-reference").split(",") if d.strip()]
    for name in carryover:
        src = _base_root / name
        if src.is_dir() and not (tree / name).exists():
            shutil.copytree(src, tree / name, copy_function=_link_or_copy)
    (tree / _SHA_FILE).write_text(sha + "\n")
    return tree


def refresh_once() -> bool:
    """One poll-and-maybe-swap. Returns True if the tree was swapped."""
    global _current_root, _previous_tree
    sha = remote_sha()
    with _lock:
        _state["last_check"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
        if sha == _state["sha"]:
            _state["last_error"] = None
            return False
    tree = _build_tree(sha)
    with _lock:
        retire, _previous_tree = _previous_tree, (
            _current_root if _current_root not in (None, _base_root) else None)
        _current_root = tree
        _state.update(sha=sha, refreshed_at=_state["last_check"], last_error=None,
                      source="self-refresh")
    _log(f"now serving {_repo()}@{sha[:8]}")
    if retire is not None:
        shutil.rmtree(retire.parent if retire.parent.name.startswith("kb-") else retire,
                      ignore_errors=True)
    return True


def _loop() -> None:
    while True:
        try:
            refresh_once()
        except Exception as e:  # keep serving the current tree; retry next tick
            with _lock:
                _state["last_error"] = f"{type(e).__name__}: {e}"
            _log(f"check failed (still serving {_state['sha'] or 'deploy tree'}): {e}")
        time.sleep(_interval())


def start(base_root: Path) -> None:
    """Record the deploy root and, if enabled, start the poll thread."""
    global _base_root, _current_root
    _base_root = base_root.resolve()
    _current_root = _base_root
    stamp = _base_root / _SHA_FILE
    if stamp.is_file():  # redeploy scripts stamp HEAD → no boot download when current
        _state["sha"] = stamp.read_text().strip() or None
    if not _enabled():
        _log("disabled (set KB_SELF_REFRESH=1 to enable off App Service)")
        return
    _state["enabled"] = True
    threading.Thread(target=_loop, daemon=True, name="kb-self-refresh").start()
    stamped = _state["sha"][:8] if _state["sha"] else "unstamped"
    _log(f"tracking {_repo()}@{_branch()} every {_interval()}s (deploy sha: {stamped})")
