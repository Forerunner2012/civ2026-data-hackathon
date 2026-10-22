from __future__ import annotations

import hashlib
import json
import platform
import sys
from importlib.metadata import distributions
from pathlib import Path
from typing import Any


def _digest(value: Any) -> str:
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def measured_runtime_identity() -> dict[str, str]:
    """Hash the imported implementation and the active Python dependency environment."""
    package_root = Path(__file__).resolve().parent
    implementation_files = [
        {
            "path": path.relative_to(package_root).as_posix(),
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        }
        for path in sorted(package_root.rglob("*"))
        if path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc"
    ]
    implementation_sha256 = _digest(implementation_files)

    installed_distributions = sorted(
        (
            {
                "name": str(distribution.metadata["Name"]).lower().replace("_", "-"),
                "version": distribution.version,
            }
            for distribution in distributions()
            if "Name" in distribution.metadata
        ),
        key=lambda item: (item["name"], item["version"]),
    )
    project_lock = package_root.parent.parent / "uv.lock"
    lock_sha256 = (
        hashlib.sha256(project_lock.read_bytes()).hexdigest() if project_lock.is_file() else None
    )
    environment_sha256 = _digest(
        {
            "python_executable": str(Path(sys.executable).resolve()),
            "python_implementation": platform.python_implementation(),
            "python_version": platform.python_version(),
            "cache_tag": sys.implementation.cache_tag,
            "uv_lock_sha256": lock_sha256,
            "installed_distributions": installed_distributions,
        }
    )
    return {
        "implementation_sha256": implementation_sha256,
        "environment_sha256": environment_sha256,
    }


def verify_cohort_runtime_binding() -> None:
    """Enforce the parent scorer's measured identity inside each replay subprocess."""
    import os

    expected_implementation = os.environ.get("CIV_COHORT_IMPLEMENTATION_SHA256")
    expected_environment = os.environ.get("CIV_COHORT_ENVIRONMENT_SHA256")
    if expected_implementation is None and expected_environment is None:
        return
    measured = measured_runtime_identity()
    if (
        expected_implementation != measured["implementation_sha256"]
        or expected_environment != measured["environment_sha256"]
    ):
        from civ_workshop.errors import CivError

        raise CivError("trusted replay runtime does not match its measured plan identity")
