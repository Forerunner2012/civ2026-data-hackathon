from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from civ_workshop.runtime_identity import measured_runtime_identity


class _SyntheticDistribution:
    metadata = {"Name": "synthetic-probe"}
    version = "1.0"

    def __init__(self, root: Path, files: tuple[Path, ...]) -> None:
        self.root = root
        self.files = files

    def locate_file(self, path: Any) -> Path:
        return self.root / Path(str(path))


def test_environment_identity_changes_when_dependency_bytes_change(
    tmp_path: Path, monkeypatch: Any
) -> None:
    package_root = tmp_path / "site-packages"
    dependency = package_root / "synthetic_probe.py"
    dependency.parent.mkdir()
    dependency.write_bytes(b"VALUE = 1\n")
    cache = package_root / ".cache" / "generated.bin"
    cache.parent.mkdir()
    cache.write_bytes(b"first cache value")
    bytecode = package_root / "__pycache__" / "synthetic_probe.pyc"
    bytecode.parent.mkdir()
    bytecode.write_bytes(b"first bytecode value")
    distribution = _SyntheticDistribution(
        package_root,
        (
            Path("synthetic_probe.py"),
            Path(".cache/generated.bin"),
            Path("__pycache__/synthetic_probe.pyc"),
        ),
    )
    monkeypatch.setattr(
        "civ_workshop.runtime_identity.distributions", lambda: [distribution]
    )

    first = measured_runtime_identity()["environment_sha256"]
    cache.write_bytes(b"changed cache value")
    bytecode.write_bytes(b"changed bytecode value")
    assert measured_runtime_identity()["environment_sha256"] == first

    dependency.write_bytes(b"VALUE = 2\n")
    assert measured_runtime_identity()["environment_sha256"] != first


def test_environment_identity_hashes_python_executable_bytes(
    tmp_path: Path, monkeypatch: Any
) -> None:
    executable = tmp_path / "python.exe"
    executable.write_bytes(b"synthetic interpreter one")
    monkeypatch.setattr(sys, "executable", str(executable))
    monkeypatch.setattr("civ_workshop.runtime_identity.distributions", lambda: [])

    first = measured_runtime_identity()["environment_sha256"]
    executable.write_bytes(b"synthetic interpreter two")

    assert measured_runtime_identity()["environment_sha256"] != first
