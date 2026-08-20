"""LFN-CONFORMANCE-002 provenance binding primitives.

This module provides the explicit M-004 provenance mechanism without changing
canonical LFN-CONFORMANCE-001 evaluation semantics.
"""

from __future__ import annotations

from pathlib import Path
import re
import subprocess

PROVENANCE_MATCH = "PROVENANCE_MATCH"
PROVENANCE_MISMATCH = "PROVENANCE_MISMATCH"
PROVENANCE_MISSING = "PROVENANCE_MISSING"

_GIT_SHA_RE = re.compile(r"^[0-9a-fA-F]{40}$")


def get_actual_git_revision(root: Path) -> str:
    """Return the exact Git revision checked out at *root*."""
    completed = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    revision = completed.stdout.strip()
    if not _GIT_SHA_RE.fullmatch(revision):
        raise RuntimeError(f"git rev-parse HEAD returned an invalid revision: {revision!r}")
    return revision.lower()


def classify_provenance(declared_revision: str | None, actual_revision: str) -> str:
    """Classify declared provenance against the actual executed revision."""
    if not declared_revision or not _GIT_SHA_RE.fullmatch(declared_revision.strip()):
        return PROVENANCE_MISSING
    return (
        PROVENANCE_MATCH
        if declared_revision.strip().lower() == actual_revision.lower()
        else PROVENANCE_MISMATCH
    )
