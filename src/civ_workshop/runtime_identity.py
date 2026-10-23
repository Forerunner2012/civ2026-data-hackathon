"""Record the checkout and pinned environment used for organizer replay."""

from __future__ import annotations

import platform
import subprocess
from pathlib import Path

from civ_workshop import __version__
from civ_workshop.artifacts import file_sha256


def runtime_metadata() -> dict[str, object]:
    root = Path(__file__).resolve().parents[2]
    revision: str | None = None
    dirty: bool | None = None
    try:
        revision = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=root,
            capture_output=True,
            text=True,
            check=True,
            timeout=10,
        ).stdout.strip()
        dirty = bool(
            subprocess.run(
                [
                    "git",
                    "status",
                    "--porcelain",
                    "--untracked-files=no",
                    "--",
                    "src",
                    "pyproject.toml",
                    "uv.lock",
                ],
                cwd=root,
                capture_output=True,
                text=True,
                check=True,
                timeout=10,
            ).stdout.strip()
        )
    except (OSError, subprocess.SubprocessError):
        pass
    lock = root / "uv.lock"
    return {
        "tool_version": __version__,
        "python_version": platform.python_version(),
        "code_revision": revision,
        "working_tree_dirty": dirty,
        "uv_lock_sha256": file_sha256(lock) if lock.is_file() else None,
    }
