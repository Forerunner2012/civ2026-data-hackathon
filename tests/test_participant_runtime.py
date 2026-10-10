from __future__ import annotations

import shutil
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path

import pytest

from civ_workshop.cli import build_parser as organizer_parser
from civ_workshop.participant_cli import build_parser as participant_parser
from tests.helpers import MICRO_REPORT, MicroCase, create_micro_case

REPOSITORY = Path(__file__).parents[1]
PUBLIC_COMMANDS = (
    "doctor", "inspect", "sample", "detect", "clip", "score", "report", "submission-init"
)


def participant_workflow(
    case: MicroCase, working: Path, invoke: Callable[[list[str]], subprocess.CompletedProcess[str]]
) -> dict[str, bytes]:
    """Exercise every public command, including resources and deterministic artifacts."""
    def run(arguments: list[str]) -> subprocess.CompletedProcess[str]:
        result = invoke(arguments)
        assert result.returncode == 0, result.stderr + result.stdout
        return result

    run(["doctor", "--workspace", str(case.root), "--bag", str(case.bag),
         "--offline-kit", str(REPOSITORY), "--json"])
    run(["inspect", str(case.bag), "--json"])
    sample = run(["sample", str(case.bag), "--topic", "/micro/signal",
                  "--field", "value", "--json"])
    scaffold = run(["submission-init", str(working), "--shell", "posix"])
    assert (working / "detector/detector.yaml").is_file()
    assert "civ" in (working / "reproduce.sh").read_text("utf-8")
    run(["detect", str(case.spec), str(case.bag), "--output", str(working), "--dry-run"])
    run(["detect", str(case.spec), str(case.bag), "--output", str(working)])
    run(["clip", str(working / "events.jsonl"), str(case.bag)])
    run(["score", str(working), "--labels", str(case.labels)])
    (working / "report.md").write_text(MICRO_REPORT, "utf-8")
    (working / "figure.svg").write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="10"></svg>\n', "utf-8"
    )
    (working / "reproduce.sh").write_text(
        "civ detect detector/detector.yaml micro.mcap\n", "utf-8"
    )
    run(["report", str(working)])
    invalid = invoke(["sample", str(case.bag), "--topic", "/absent", "--field", "value"])
    assert invalid.returncode == 2
    assert "topic not found" in invalid.stderr
    artifacts = {str(path.relative_to(working)): path.read_bytes()
                 for path in working.rglob("*") if path.is_file()}
    artifacts["sample.stdout"] = sample.stdout.encode()
    artifacts["scaffold.stdout"] = scaffold.stdout.encode()
    artifacts["invalid.stderr"] = invalid.stderr.encode()
    return artifacts


@pytest.mark.parametrize("command", PUBLIC_COMMANDS)
def test_public_subcommand_arguments_match(
    command: str, capsys: pytest.CaptureFixture[str]
) -> None:
    help_output = []
    for parser in (organizer_parser(), participant_parser()):
        # Help uses SystemExit before any dispatch, preserving argparse semantics.
        with pytest.raises(SystemExit) as result:
            parser.parse_args([command, "--help"])
        assert result.value.code == 0
        help_output.append(capsys.readouterr().out)
    assert help_output[0] == help_output[1]


def test_both_entry_points_reproduce_complete_workflow(tmp_path: Path) -> None:
    case = create_micro_case(tmp_path / "case")
    working = case.root / "submission"
    results = []
    for module in ("civ_workshop.cli", "civ_workshop.participant_cli"):
        def invoke(arguments: list[str], module: str = module) -> subprocess.CompletedProcess[str]:
            return subprocess.run([sys.executable, "-m", module, *arguments],
                                  cwd=case.root, text=True, capture_output=True, check=False)
        results.append(participant_workflow(case, working, invoke))
        shutil.rmtree(working)
    assert results[0] == results[1]


@pytest.mark.parametrize("command", ["intake-form", "intake-local", "intake-tally", "score-batch"])
def test_participant_rejects_organizer_commands(command: str) -> None:
    with pytest.raises(SystemExit) as result:
        participant_parser().parse_args([command])
    assert result.value.code == 2
