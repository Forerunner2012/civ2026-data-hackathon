from __future__ import annotations

import os
import shutil
import tempfile
from importlib.resources import files
from pathlib import Path
from typing import Literal

from civ_workshop.errors import CivError

Shell = Literal["powershell", "posix"]

COMMON_TEMPLATES = (
    ("README.md", "README.md"),
    ("detector.yaml", "detector/detector.yaml"),
    ("figure.svg", "figure.svg"),
    ("report.md", "report.md"),
)
REPRODUCTION_TEMPLATES: dict[Shell, tuple[str, str]] = {
    "powershell": ("reproduce.ps1", "reproduce.ps1"),
    "posix": ("reproduce.sh", "reproduce.sh"),
}


def scaffold_submission(destination: Path, shell: Shell) -> dict[str, object]:
    """Create one deterministic, deliberately incomplete participant workspace."""

    destination = destination.resolve()
    if destination.exists():
        raise CivError(f"submission workspace already exists: {destination}")
    if shell not in REPRODUCTION_TEMPLATES:
        raise CivError(f"unsupported submission shell: {shell}")

    try:
        destination.parent.mkdir(parents=True, exist_ok=True)
        temporary = Path(
            tempfile.mkdtemp(prefix=".civ-submission-", dir=destination.parent)
        )
    except OSError as error:
        raise CivError(f"cannot prepare submission workspace: {error}") from error

    selected = (*COMMON_TEMPLATES, REPRODUCTION_TEMPLATES[shell])
    resource_root = files("civ_workshop").joinpath("_templates").joinpath("submission")
    try:
        for source_name, relative_name in selected:
            target = temporary / relative_name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(resource_root.joinpath(source_name).read_bytes())
        if shell == "posix":
            (temporary / "reproduce.sh").chmod(0o755)
        os.replace(temporary, destination)
    except (OSError, TypeError) as error:
        raise CivError(f"cannot create submission workspace: {error}") from error
    finally:
        if temporary.exists():
            shutil.rmtree(temporary, ignore_errors=True)

    return {
        "directory": str(destination),
        "files": sorted(relative for _, relative in selected),
        "shell": shell,
    }
