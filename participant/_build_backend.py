"""Build the Git subdirectory target from the kit's participant allowlist.

The resulting sdist is a standalone uv-build project containing only participant
code. Reading the allowlist as syntax avoids importing organizer assembly code.
"""
from __future__ import annotations

import ast
import os
import shutil
import tempfile
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any

import uv_build


@contextmanager
def _participant_project() -> Iterator[None]:
    repository = Path(__file__).resolve().parents[1]
    tree = ast.parse((repository / "src/civ_workshop/kit_assembly.py").read_text("utf-8"))
    modules = next(
        ast.literal_eval(node.value)
        for node in tree.body
        if isinstance(node, ast.Assign)
        and any(
            isinstance(target, ast.Name) and target.id == "PARTICIPANT_RUNTIME_MODULES"
            for target in node.targets
        )
    )
    previous = Path.cwd()
    with tempfile.TemporaryDirectory(prefix="civ-participant-build-") as temporary:
        project = Path(temporary)
        metadata = (repository / "participant/pyproject.toml").read_text("utf-8")
        (project / "pyproject.toml").write_text(
            metadata.split("[build-system]", 1)[0]
            + '[build-system]\nrequires = ["uv-build>=0.8.15,<0.9"]\n'
            + 'build-backend = "uv_build"\n', "utf-8"
        )
        package = project / "src/civ_workshop"
        package.mkdir(parents=True)
        for name in modules:
            shutil.copyfile(repository / "src/civ_workshop" / name, package / name)
        shutil.copytree(repository / "src/civ_workshop/_templates", package / "_templates")
        (package / "__init__.py").write_text(
            '"""Offline participant tooling for the CIV 2026 data hackathon."""\n', "utf-8"
        )
        (package / "__main__.py").write_text(
            "from civ_workshop.participant_cli import main\n\nmain()\n", "utf-8"
        )
        try:
            os.chdir(project)
            yield
        finally:
            os.chdir(previous)


def build_wheel(
    wheel_directory: str,
    config_settings: dict[str, Any] | None = None,
    metadata_directory: str | None = None,
) -> str:
    destination = str(Path(wheel_directory).resolve())
    with _participant_project():
        return uv_build.build_wheel(destination, config_settings, metadata_directory)


def build_sdist(
    sdist_directory: str, config_settings: dict[str, Any] | None = None
) -> str:
    destination = str(Path(sdist_directory).resolve())
    with _participant_project():
        return uv_build.build_sdist(destination, config_settings)
