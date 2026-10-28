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
def test_trusted_generated_entrypoint_rebuilds_a_fresh_submission(
    tmp_path: Path, evaluated: bool, with_resource: bool
) -> None:
    case = (
        _resource_case(tmp_path / "case")[0]
        if with_resource
        else create_micro_case(tmp_path / "case")
    )
    working = tmp_path / "completed"
    shell: Shell = "powershell" if os.name == "nt" else "posix"
    scaffold_submission(working, shell)
    shutil.copyfile(case.spec, working / "detector/detector.yaml")
    (working / "report.md").write_text(MICRO_REPORT, encoding="utf-8")
    (working / "figure.svg").write_text('<svg xmlns="http://www.w3.org/2000/svg"/>')
    if with_resource:
        detect_events(case.spec, case.bag, working)
        _add_extension_payloads(working)
    before = {p.relative_to(working): p.read_bytes() for p in working.rglob("*") if p.is_file()}
    output = tmp_path / "fresh output"
    if os.name == "nt":
        executable = shutil.which("pwsh") or shutil.which("powershell")
        assert executable is not None
        command = [executable, "-NoProfile", "-File", str(working / "reproduce.ps1")]
    else:
        command = ["sh", str(working / "reproduce.sh")]
    command += [str(case.bag), str(case.labels) if evaluated else "-", str(output)]
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
