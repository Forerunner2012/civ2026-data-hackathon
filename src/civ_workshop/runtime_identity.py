from __future__ import annotations

import hashlib
import json
import platform
import re
import sys
from importlib.metadata import distributions
from pathlib import Path, PurePosixPath
from typing import Any


def _digest(value: Any) -> str:
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _generated_or_cache_file(path: PurePosixPath) -> bool:
    cache_directories = {
        "__pycache__",
        ".cache",
        ".mypy_cache",
        ".pytest_cache",
        ".ruff_cache",
        "cache",
        "caches",
    }
    return path.suffix.casefold() in {".pyc", ".pyo"} or any(
        part.casefold() in cache_directories for part in path.parts
    )


def _distribution_identity(distribution: Any) -> dict[str, Any]:
    name = str(distribution.metadata["Name"]).lower().replace("_", "-")
    files = distribution.files
    if files is None:
        raise RuntimeError(f"installed distribution '{name}' has no file inventory")

    file_records: list[dict[str, object]] = []
    for item in files:
        relative_path = PurePosixPath(str(item).replace("\\", "/"))
        if _generated_or_cache_file(relative_path):
            continue
        installed_path = Path(distribution.locate_file(item))
        if installed_path.is_file():
            file_records.append(
                {"path": relative_path.as_posix(), "sha256": _file_sha256(installed_path)}
            )
        else:
            file_records.append({"path": relative_path.as_posix(), "missing": True})
    file_records.sort(key=lambda record: str(record["path"]))
    return {
        "name": name,
        "version": distribution.version,
        "files": file_records,
    }


def _runtime_dependency_distributions(installed: list[Any]) -> list[Any]:
    by_name = {
        str(distribution.metadata["Name"]).lower().replace("_", "-"): distribution
        for distribution in installed
        if "Name" in distribution.metadata
    }
    project = by_name.get("civ-workshop")
    if project is None:
        return installed

    selected: dict[str, Any] = {}
    pending = list(project.requires or [])
    while pending:
        requirement = pending.pop()
        match = re.match(r"\s*([A-Za-z0-9][A-Za-z0-9._-]*)", requirement)
        if match is None:
            continue
        name = match.group(1).lower().replace("_", "-")
        distribution = by_name.get(name)
        if distribution is None or name in selected:
            continue
        selected[name] = distribution
        pending.extend(distribution.requires or [])
    return [selected[name] for name in sorted(selected)]


def measured_runtime_identity() -> dict[str, str]:
    """Hash the imported implementation and the active Python dependency environment."""
    package_root = Path(__file__).resolve().parent
    implementation_files = []
    for path in package_root.rglob("*"):
        if not path.is_file():
            continue
        relative_path = PurePosixPath(path.relative_to(package_root).as_posix())
        if _generated_or_cache_file(relative_path):
            continue
        implementation_files.append(
            {"path": relative_path.as_posix(), "sha256": _file_sha256(path)}
        )
    implementation_files.sort(key=lambda record: str(record["path"]))
    implementation_sha256 = _digest(implementation_files)

    installed = [
        distribution for distribution in distributions() if "Name" in distribution.metadata
    ]
    installed_distributions = [
        {
            "name": str(distribution.metadata["Name"]).lower().replace("_", "-"),
            "version": distribution.version,
        }
        for distribution in installed
    ]
    installed_distributions.sort(key=lambda item: (item["name"], item["version"]))
    runtime_dependencies = [
        _distribution_identity(distribution)
        for distribution in _runtime_dependency_distributions(installed)
    ]
    runtime_dependencies.sort(key=lambda item: (item["name"], item["version"]))
    python_executable = Path(sys.executable).resolve()
    project_lock = package_root.parent.parent / "uv.lock"
    lock_sha256 = (
        hashlib.sha256(project_lock.read_bytes()).hexdigest() if project_lock.is_file() else None
    )
    environment_sha256 = _digest(
        {
            "python_executable": str(python_executable),
            "python_executable_sha256": _file_sha256(python_executable),
            "python_implementation": platform.python_implementation(),
            "python_version": platform.python_version(),
            "cache_tag": sys.implementation.cache_tag,
            "uv_lock_sha256": lock_sha256,
            "installed_distributions": installed_distributions,
            "runtime_dependency_files": runtime_dependencies,
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
