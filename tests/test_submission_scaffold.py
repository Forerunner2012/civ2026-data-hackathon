from __future__ import annotations

import json
from pathlib import Path
from typing import cast

import pytest

from civ_workshop.errors import CivError
from civ_workshop.reporting import REPORT_HEADINGS, build_report_bundle
from civ_workshop.submission import Shell, scaffold_submission
from tests.helpers import run_civ


def _files(root: Path) -> dict[str, bytes]:
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in root.rglob("*")
        if path.is_file()
    }


@pytest.mark.parametrize(
    ("shell", "reproduction"),
    [("powershell", "reproduce.ps1"), ("posix", "reproduce.sh")],
)
def test_submission_scaffold_is_deterministic_incomplete_and_platform_specific(
    tmp_path: Path, shell: str, reproduction: str
) -> None:
    first = tmp_path / f"first-{shell}"
    second = tmp_path / f"second-{shell}"

    first_result = scaffold_submission(first, cast(Shell, shell))
    second_result = scaffold_submission(second, cast(Shell, shell))

    assert _files(first) == _files(second)
    assert first_result["files"] == second_result["files"]
    assert sorted(_files(first)) == [
        "README.md",
        "detector/detector.yaml",
        "figure.svg",
        "report.md",
        reproduction,
    ]
    assert "CIV_TEMPLATE_REPLACE_ME" in (first / "detector/detector.yaml").read_text()
    report = (first / "report.md").read_text(encoding="utf-8")
    assert all(f"# {heading}" in report for heading in REPORT_HEADINGS)
    assert report.count("![") == 1
    assert "civ detect" in (first / reproduction).read_text(encoding="utf-8")
    assert not (first / ({"reproduce.ps1", "reproduce.sh"} - {reproduction}).pop()).exists()


def test_submission_scaffold_cli_refuses_to_overwrite(tmp_path: Path) -> None:
    workspace = tmp_path / "working"
    created = run_civ(
        tmp_path,
        ["submission-init", str(workspace), "--shell", "powershell"],
    )

    assert created.returncode == 0, created.stderr
    payload = json.loads(created.stdout)
    assert payload["shell"] == "powershell"
    original = _files(workspace)

    repeated = run_civ(
        tmp_path,
        ["submission-init", str(workspace), "--shell", "powershell"],
    )
    assert repeated.returncode == 2
    assert "submission workspace already exists" in repeated.stderr
    assert _files(workspace) == original


def test_report_rejects_untouched_template_prompts(tmp_path: Path) -> None:
    workspace = tmp_path / "working"
    scaffold_submission(workspace, "powershell")

    with pytest.raises(CivError, match="report still contains CIV_TEMPLATE_REPLACE_ME"):
        build_report_bundle(workspace)


def test_scaffold_contains_no_data_or_organizer_payload(tmp_path: Path) -> None:
    workspace = tmp_path / "working"
    scaffold_submission(workspace, "posix")
    joined = b"\n".join(_files(workspace).values()).lower()

    for forbidden in (
        b".mcap",
        b"answer key",
        b"ground truth",
        b"hidden label",
        b"organizer path",
        b"sealed interval",
    ):
        assert forbidden not in joined
