from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from civ_workshop.detection import detect_events
from civ_workshop.errors import CivError
from civ_workshop.reporting import build_report_bundle
from civ_workshop.submission import Shell, scaffold_submission
from tests.helpers import MICRO_REPORT, create_micro_case, prepare_scored_submission, run_civ
from tests.test_submission_v2 import _add_extension_payloads, _resource_case


@pytest.mark.parametrize("evaluated", [True, False])
@pytest.mark.parametrize("with_resource", [True, False])
@pytest.mark.parametrize("shell", ["powershell", "posix"])
@pytest.mark.parametrize("relative_output", [True, False])
def test_trusted_generated_entrypoint_rebuilds_a_fresh_submission(
    tmp_path: Path, evaluated: bool, with_resource: bool, shell: Shell, relative_output: bool
) -> None:
    executable = shutil.which("pwsh") or shutil.which("powershell")
    if shell == "posix":
        executable = shutil.which("sh")
        if executable is None and os.name == "nt":
            git = shutil.which("git")
            git_sh = Path(git).parent.parent / "bin/sh.exe" if git else None
            if git_sh is not None and git_sh.is_file():
                executable = str(git_sh)
    if executable is None:
        pytest.skip(f"{shell} shell is not installed")
    case = (
        _resource_case(tmp_path / "case")[0]
        if with_resource
        else create_micro_case(tmp_path / "case")
    )
    working = tmp_path / "completed"
    scaffold_submission(working, shell)
    shutil.copyfile(case.spec, working / "detector/detector.yaml")
    figure_name = "figure.svg"
    if shell == "posix":
        figure_name = "figure.SVG" if evaluated else "figure.sVg"
    (working / "report.md").write_text(
        MICRO_REPORT.replace("figure.svg", figure_name), encoding="utf-8"
    )
    (working / "figure.svg").unlink()
    (working / figure_name).write_text('<svg xmlns="http://www.w3.org/2000/svg"/>')
    if with_resource:
        detect_events(case.spec, case.bag, working)
        _add_extension_payloads(working)
    before = {p.relative_to(working): p.read_bytes() for p in working.rglob("*") if p.is_file()}
    location = tmp_path / "shell location"
    location.mkdir()
    output = (location if relative_output else tmp_path) / "fresh output"
    arguments = [str(case.bag), str(case.labels) if evaluated else "-", str(output)]
    if shell == "powershell":
        if relative_output:
            arguments[-1] = output.name
            invocation = " ".join(
                "'" + value.replace("'", "''") + "'"
                for value in [str(working / "reproduce.ps1"), *arguments]
            )
            quoted_location = str(location).replace("'", "''")
            command = [
                executable,
                "-NoProfile",
                "-Command",
                f"Set-Location -LiteralPath '{quoted_location}'; & {invocation}",
            ]
        else:
            command = [
                executable, "-NoProfile", "-File", str(working / "reproduce.ps1"), *arguments
            ]
    else:
        arguments = [
            case.bag.as_posix(),
            case.labels.as_posix() if evaluated else "-",
            output.relative_to(tmp_path).as_posix() if relative_output else output.as_posix(),
        ]
        command = [executable, (working / "reproduce.sh").as_posix(), *arguments]
    environment = {
        **os.environ,
        "PATH": str(Path(sys.executable).parent) + os.pathsep + os.environ.get("PATH", ""),
    }
    result = subprocess.run(
        command, cwd=tmp_path, env=environment, text=True, capture_output=True, check=False
    )
    assert result.returncode == 0, result.stdout + result.stderr
    metrics = json.loads((output / "metrics.json").read_text())
    assert metrics["contract"] == ("civ.metrics/v1" if evaluated else "civ.metrics/v2")
    assert (output / "submission.zip").is_file()
    assert (output / figure_name).read_bytes() == (working / figure_name).read_bytes()
    if relative_output:
        assert not (tmp_path / output.name).exists()
    if with_resource:
        assert (output / "extension/manifest.json").read_bytes() == (
            working / "extension/manifest.json"
        ).read_bytes()
    assert list((output / "evidence").glob("*.mcap"))
    assert before == {
        p.relative_to(working): p.read_bytes() for p in working.rglob("*") if p.is_file()
    }
    baseline = tmp_path / "baseline"
    prepare_scored_submission(case, baseline)
    if not evaluated:
        result = run_civ(tmp_path, ["score", str(baseline)])
        assert result.returncode == 0, result.stderr
    for name in ("events.jsonl", "metrics.json"):
        assert (baseline / name).read_bytes() == (output / name).read_bytes()
    repeated = subprocess.run(
        command, cwd=tmp_path, env=environment, text=True, capture_output=True, check=False
    )
    assert repeated.returncode != 0


def test_wrapper_rejection_explains_supported_direct_invocations(tmp_path: Path) -> None:
    case = create_micro_case(tmp_path / "case")
    working = tmp_path / "working"
    prepare_scored_submission(case, working)
    (working / "reproduce.ps1").write_text('Invoke-Detector "civ detect"')
    with pytest.raises(CivError, match="direct command line.*wrappers"):
        build_report_bundle(working)
