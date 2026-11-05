from __future__ import annotations

import shutil
import subprocess
import tarfile
import zipfile
from pathlib import Path

import pytest

from civ_workshop.kit_assembly import (
    PARTICIPANT_RUNTIME_MODULES,
    PRIVATE_RUNTIME_MODULES,
    _copy_participant_runtime,
)

REPOSITORY = Path(__file__).parents[1]


def test_participant_metadata_matches_assembled_kit() -> None:
    git_target = (REPOSITORY / "participant/pyproject.toml").read_text("utf-8")
    kit_target = (REPOSITORY / "kit/participant-pyproject.toml").read_text("utf-8")
    assert git_target.split("[build-system]")[0] == kit_target.split("[build-system]")[0]


def test_git_target_builds_participant_only_wheel_and_standalone_sdist(tmp_path: Path) -> None:
    uv = shutil.which("uv")
    if uv is None:
        pytest.skip("uv is required for isolated build checks")
    result = subprocess.run(
        [uv, "build", str(REPOSITORY / "participant"), "--out-dir", str(tmp_path)],
        text=True, capture_output=True, check=False,
    )
    assert result.returncode == 0, result.stderr
    with zipfile.ZipFile(next(tmp_path.glob("*.whl"))) as archive:
        paths = set(archive.namelist())
        modules = {Path(name).name for name in paths
                   if name.startswith("civ_workshop/") and name.endswith(".py")}
        assert modules == set(PARTICIPANT_RUNTIME_MODULES) | {"__init__.py", "__main__.py"}
        assert modules.isdisjoint(PRIVATE_RUNTIME_MODULES)
        assert "civ_workshop/organizer/label_review.py" not in paths
        assert not any(Path(name).name == "label_review.html" for name in paths)
        assert "civ_workshop/_templates/submission/detector.yaml" in paths
        assert "civ_workshop/_templates/submission/reproduce.sh" in paths
        assert "participant_cli:main" in archive.read(
            "civ_workshop-0.1.0.dist-info/entry_points.txt"
        ).decode()
    with tarfile.open(next(tmp_path.glob("*.tar.gz"))) as archive:
        names = archive.getnames()
        assert not any(Path(name).name in PRIVATE_RUNTIME_MODULES for name in names)
        metadata = archive.extractfile("civ_workshop-0.1.0/pyproject.toml")
        assert metadata is not None
        assert 'build-backend = "uv_build"' in metadata.read().decode()


def test_participant_kit_runtime_omits_organizer_review(tmp_path: Path) -> None:
    runtime = tmp_path / "runtime"
    _copy_participant_runtime(REPOSITORY, runtime)
    package = runtime / "src" / "civ_workshop"
    assert not (package / "organizer" / "label_review.py").exists()
    assert not (package / "organizer" / "label_review.html").exists()
    assert not (package / "_templates" / "label_review.html").exists()
