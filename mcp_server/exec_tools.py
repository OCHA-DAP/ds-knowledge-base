"""Sandboxed Python execution for analysis. Gated by KB_MCP_ENABLE_PYTHON.

`run_python` runs caller-supplied code in a hardened subprocess so the model can do real
data analysis (pandas/numpy/… are importable) without being able to reach this server's
secrets or anything personal:

  * **Scrubbed environment** — the child gets an allowlisted env only (PATH/LANG/HOME/…).
    None of `DSCI_AZ_*` (DB/blob creds), `KB_MCP_STATIC_TOKEN`, or any other server var is
    passed, so `os.environ` in the sandbox is credential-free. (With creds gone, importing
    ocha-stratus can't actually connect anywhere — get the DB data via `run_sql` first, then
    analyze it here.)
  * **Privilege drop** — best-effort setuid/setgid to an unprivileged id, so when the server
    runs as root (the App Service container) the child can't read the parent's
    `/proc/<pid>/environ` to recover the scrubbed creds. Skipped silently if not permitted.
  * **Resource limits** — CPU seconds, address space, max file size, fd count, process count
    (RLIMIT_NPROC, so a fork bomb can't exhaust the container), no core dump.
  * **Wall-clock timeout** and **output cap**.
  * **`python -I`** isolated mode (ignores PYTHON* env, user site, cwd on path).
  * **Isolated temp cwd**, removed after each call. Stateless: nothing persists between calls.

**Network:** the sandbox HAS outbound internet access (intentional — the assistant may pull
public reference data / online sources to supplement the KB). It has NO credentials, so it
cannot reach the team DB/blob/Drive or authenticate to any internal service; cloud-metadata
endpoints (IMDS 169.254.169.254, wireserver 168.63.129.16) are not reachable from App Service.
It is therefore not credential-isolated by network but by the scrubbed, credential-free env.

The model's Max-plan token is never on this server, so the sandbox cannot touch it regardless.
"""
from __future__ import annotations

import os
import resource
import shutil
import subprocess
import sys
import tempfile

_DEFAULT_TIMEOUT_S = 30
_MAX_TIMEOUT_S = 60
_MAX_OUTPUT = 20_000
_AS_BYTES = 2 * 1024**3      # 2 GiB address space
_FSIZE_BYTES = 50 * 1024**2  # 50 MiB max file written
_MAX_PROCS = 256             # RLIMIT_NPROC — caps fork bombs; ample for single-threaded analysis
_NOBODY_UID = 65534
_NOBODY_GID = 65534

# Allowlist — the ONLY env the child sees. No DSCI_*/KB_*/tokens by construction.
_SAFE_ENV_BASE = {
    "PATH": "/usr/local/bin:/usr/bin:/bin",
    "LANG": "C.UTF-8",
    "LC_ALL": "C.UTF-8",
    "PYTHONDONTWRITEBYTECODE": "1",
    "PYTHONUNBUFFERED": "1",
    "MPLBACKEND": "Agg",  # headless matplotlib
    "OMP_NUM_THREADS": "1",
    "OPENBLAS_NUM_THREADS": "1",
    "NUMEXPR_NUM_THREADS": "1",
    "MKL_NUM_THREADS": "1",
}


def _preexec(timeout_s: int):
    def _apply():
        # Resource ceilings (child only). Each is best-effort: a limit unsupported on the
        # current platform (e.g. RLIMIT_AS on macOS) is skipped rather than failing the run.
        # On the Linux App Service container they all apply.
        limits = [
            (resource.RLIMIT_CPU, timeout_s, timeout_s + 2),
            (resource.RLIMIT_AS, _AS_BYTES, _AS_BYTES),
            (resource.RLIMIT_FSIZE, _FSIZE_BYTES, _FSIZE_BYTES),
            (resource.RLIMIT_NOFILE, 256, 256),
            (resource.RLIMIT_CORE, 0, 0),
        ]
        if hasattr(resource, "RLIMIT_NPROC"):  # cap total procs/threads → fork-bomb guard
            limits.append((resource.RLIMIT_NPROC, _MAX_PROCS, _MAX_PROCS))
        for what, soft, hard in limits:
            try:
                resource.setrlimit(what, (soft, hard))
            except (ValueError, OSError):
                pass
        # Best-effort privilege drop — only succeeds if the server runs as root. Closes the
        # /proc/<ppid>/environ path to the scrubbed creds. Harmless no-op otherwise.
        try:
            os.setgroups([])
            os.setgid(_NOBODY_GID)
            os.setuid(_NOBODY_UID)
        except (PermissionError, OSError):
            pass

    return _apply


def run_python(code: str, timeout_s: int = _DEFAULT_TIMEOUT_S) -> str:
    """Run `code` in the sandbox and return its stdout (+ stderr). See module docstring."""
    if not code or not code.strip():
        return "No code provided."
    timeout_s = max(1, min(int(timeout_s), _MAX_TIMEOUT_S))
    workdir = tempfile.mkdtemp(prefix="kbpy-")
    os.chmod(workdir, 0o777)  # usable by the dropped-privilege child
    env = {**_SAFE_ENV_BASE, "HOME": workdir, "TMPDIR": workdir}
    try:
        proc = subprocess.run(
            [sys.executable, "-I", "-c", code],
            cwd=workdir, env=env, capture_output=True, text=True,
            timeout=timeout_s, preexec_fn=_preexec(timeout_s),
        )
    except subprocess.TimeoutExpired:
        return f"Timed out after {timeout_s}s (the sandbox CPU/time limit)."
    except Exception as e:  # noqa: BLE001 — surface to the model, don't crash the tool
        return f"Execution error ({type(e).__name__}: {e})."
    finally:
        shutil.rmtree(workdir, ignore_errors=True)

    out = (proc.stdout or "").rstrip()
    if proc.stderr and proc.stderr.strip():
        out += "\n--- stderr ---\n" + proc.stderr.rstrip()
    out = out.strip()
    if len(out) > _MAX_OUTPUT:
        out = out[:_MAX_OUTPUT] + f"\n… [output truncated at {_MAX_OUTPUT} chars]"
    if proc.returncode and proc.returncode < 0:  # killed by a signal
        sig = -proc.returncode
        limit_hint = " — exceeded the sandbox CPU/time or memory limit" if sig in (9, 24, 25) else ""
        msg = f"[sandbox terminated the process (signal {sig}){limit_hint}]"
        return (out + "\n" + msg).strip() if out else msg
    if proc.returncode != 0 and not out:
        return f"Exited with code {proc.returncode} and no output."
    return out or "(ran successfully; no output — use print() to see results)"
