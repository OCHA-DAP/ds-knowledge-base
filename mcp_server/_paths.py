"""Shared path-traversal guard. Security-sensitive — kept in one home so a hardening
fix (e.g. symlink handling) can't be applied to one tool surface and missed in another."""
from __future__ import annotations

from pathlib import Path


def safe_resolve(root: Path, rel: str) -> Path:
    """Resolve `rel` against `root`, rejecting traversal / absolute escapes."""
    root = root.resolve()
    cand = (root / rel).resolve()
    if root != cand and root not in cand.parents:
        raise ValueError(f"Path '{rel}' is outside the repository.")
    return cand
