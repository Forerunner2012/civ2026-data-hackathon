from __future__ import annotations

import json
import subprocess
import sys
from hashlib import sha256
from pathlib import Path

from tests.helpers import MicroCase, create_micro_case

PROJECT_ROOT = Path(__file__).resolve().parents[1]
ONBOARDING_SCRIPT = PROJECT_ROOT / "scripts" / "onboarding_check.py"


def run_onboarding_check(
    source: Path,
    spec: Path,
    labels: Path,
    output: Path,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(ONBOARDING_SCRIPT),
            "--source",
            str(source),
            "--eventspec",
            str(spec),
            "--labels",
            str(labels),
            "--output",
            str(output),
        ],
        cwd=PROJECT_ROOT,
        capture_output=True,
        check=False,
        text=True,
    )


def summary(result: subprocess.CompletedProcess[str]) -> dict[str, object]:
    return json.loads(result.stdout)


def input_hashes(case: MicroCase) -> tuple[str, str, str]:
    return tuple(
        sha256(path.read_bytes()).hexdigest() for path in (case.bag, case.spec, case.labels)
    )


def test_onboarding_check_runs_consumers_for_one_mcap_in_chunk_folder(tmp_path: Path) -> None:
    case = create_micro_case(tmp_path / "chunk")
    before = input_hashes(case)
    output = tmp_path / "onboarding-output"

    result = run_onboarding_check(case.root, case.spec, case.labels, output)

    report = summary(result)
    assert result.returncode == 0, result.stderr
    assert report["source_binding"] == "match"
    assert report["detect"] == {"accepted": True}
    assert report["score"] == {"accepted": True}
    assert (output / "events.jsonl").is_file()
    assert (output / "metrics.json").is_file()
    assert input_hashes(case) == before


def test_onboarding_check_accepts_zero_detected_events(tmp_path: Path) -> None:
    case = create_micro_case(tmp_path / "quiet-chunk", values=[0.0] * 5)
    output = tmp_path / "onboarding-output"

    result = run_onboarding_check(case.bag, case.spec, case.labels, output)

    report = summary(result)
    assert result.returncode == 0, result.stderr
    assert report["source_binding"] == "match"
    assert report["detect"] == {"accepted": True}
    assert report["score"] == {"accepted": True}
    assert (output / "events.jsonl").read_text(encoding="utf-8") == ""


def test_onboarding_check_uses_score_consumer_to_reject_mismatched_pack(
    tmp_path: Path,
) -> None:
    case = create_micro_case(tmp_path / "chunk")
    pack = json.loads(case.labels.read_text(encoding="utf-8"))
    pack["source_sha256"] = "0" * 64
    pack_directory = tmp_path / "mismatched-pack"
    pack_directory.mkdir()
    mismatched_labels = pack_directory / "labels.json"
    mismatched_labels.write_text(json.dumps(pack), encoding="utf-8")
    output = tmp_path / "onboarding-output"

    result = run_onboarding_check(case.bag, case.spec, mismatched_labels, output)

    report = summary(result)
    assert result.returncode != 0
    assert report["source_binding"] == "mismatch"
    assert report["detect"] == {"accepted": True}
    assert report["score"]["accepted"] is False
    assert report["score"]["diagnostic"] == (
        "label pack source_sha256 does not match submission source sha256"
    )


def test_onboarding_check_rejects_ambiguous_chunk_folder_without_writing(
    tmp_path: Path,
) -> None:
    case = create_micro_case(tmp_path / "chunk")
    (case.root / "second.mcap").write_bytes(case.bag.read_bytes())
    output = tmp_path / "onboarding-output"

    result = run_onboarding_check(case.root, case.spec, case.labels, output)

    report = summary(result)
    assert result.returncode != 0
    assert report["error"] == {
        "category": "source",
        "message": "source folder contains multiple MCAP files; pass the intended MCAP file",
    }
    assert not output.exists()
    assert str(case.root) not in result.stdout
    assert str(case.root) not in result.stderr


def test_onboarding_check_rejects_missing_source_with_path_safe_diagnostic(
    tmp_path: Path,
) -> None:
    case = create_micro_case(tmp_path / "chunk")
    missing_source = tmp_path / "private" / "missing.mcap"
    output = tmp_path / "onboarding-output"

    result = run_onboarding_check(missing_source, case.spec, case.labels, output)

    report = summary(result)
    assert result.returncode != 0
    assert report["error"] == {
        "category": "source",
        "message": "source input does not exist",
    }
    assert str(tmp_path) not in result.stdout
    assert str(tmp_path) not in result.stderr
    assert not output.exists()


def test_onboarding_check_rejects_malformed_pack_before_creating_output(
    tmp_path: Path,
) -> None:
    case = create_micro_case(tmp_path / "chunk")
    pack_directory = tmp_path / "malformed-pack"
    pack_directory.mkdir()
    malformed_labels = pack_directory / "labels.json"
    malformed_labels.write_text('{"contract":"wrong"}', encoding="utf-8")
    output = tmp_path / "onboarding-output"

    result = run_onboarding_check(case.bag, case.spec, malformed_labels, output)

    report = summary(result)
    assert result.returncode != 0
    assert report["error"] == {
        "category": "label_pack",
        "message": "label pack does not satisfy the scoring contract",
    }
    assert not output.exists()
    assert str(tmp_path) not in result.stdout


def test_onboarding_check_redacts_invalid_event_spec_resource_path(tmp_path: Path) -> None:
    case = create_micro_case(tmp_path / "chunk")
    spec_directory = tmp_path / "spec"
    spec_directory.mkdir()
    spec = spec_directory / "detector.yaml"
    spec_text = case.spec.read_text(encoding="utf-8")
    spec_text = spec_text.replace(
        "condition:",
        "resources:\n"
        "  points:\n"
        "    path: /private/points.json\n"
        "    contract: civ.point-resource/v1\n"
        "condition:",
    )
    spec.write_text(spec_text, encoding="utf-8")
    output = tmp_path / "onboarding-output"

    result = run_onboarding_check(case.bag, spec, case.labels, output)

    report = summary(result)
    assert result.returncode != 0
    assert report["detect"] == {
        "accepted": False,
        "diagnostic": "detect consumer rejected an EventSpec resource path",
    }
    assert "/private/points.json" not in result.stdout
    assert str(tmp_path) not in result.stdout
