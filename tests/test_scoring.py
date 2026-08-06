from __future__ import annotations

import json
from hashlib import sha256
from pathlib import Path
from typing import Any, cast

import pytest

from tests.helpers import run_civ

FIXTURES = Path(__file__).parent / "fixtures" / "scoring"


def _load_fixture(name: str) -> dict[str, Any]:
    return cast(
        dict[str, Any], json.loads((FIXTURES / name).read_text(encoding="utf-8"))
    )


def _write_scoring_inputs(
    root: Path, case: dict[str, Any], source_sha256: str
) -> tuple[Path, Path]:
    working = root / "submission"
    working.mkdir()
    events = [
        {
            "bag_sha256": source_sha256,
            "end_ns": prediction["end_ns"],
            "event_id": prediction["event_id"],
            "spec_sha256": "2" * 64,
            "start_ns": prediction["start_ns"],
            "trigger_values": {},
        }
        for prediction in case["predictions"]
    ]
    serialized_events = "".join(
        f"{json.dumps(event, sort_keys=True, separators=(',', ':'))}\n" for event in events
    )
    (working / "events.jsonl").write_text(
        serialized_events,
        encoding="utf-8",
        newline="\n",
    )
    (working / "run-manifest.json").write_text(
        json.dumps(
            {
                "contract": "civ.run-manifest/v1alpha1",
                "source": {"name": f"{case['dataset']}.mcap", "sha256": source_sha256},
            },
            sort_keys=True,
            separators=(",", ":"),
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )
    labels = root / "labels.json"
    labels.write_text(
        json.dumps(
            {
                "contract": "civ.label-pack/v1alpha1",
                "dataset": case["dataset"],
                "data_gaps": case.get("data_gaps", []),
                "labels": case["labels"],
                "source_sha256": source_sha256,
            },
            sort_keys=True,
            separators=(",", ":"),
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return working, labels


@pytest.mark.parametrize("case_index", [0, 1, 2])
def test_score_matches_temporal_iou_threshold_golden_cases(
    tmp_path: Path, case_index: int
) -> None:
    fixture = _load_fixture("threshold_boundaries.json")
    case = fixture["cases"][case_index]
    working, labels = _write_scoring_inputs(tmp_path, case, fixture["source_sha256"])

    result = run_civ(tmp_path, ["score", str(working), "--labels", str(labels)])

    assert result.returncode == 0, result.stderr
    metrics = json.loads((working / "metrics.json").read_text(encoding="utf-8"))
    assert metrics == {
        "aggregate": {
            "counts": case["expected"]["counts"],
            "f1": case["expected"]["f1"],
            "match_quality": {
                "mean_temporal_iou": case["expected"]["mean_temporal_iou"]
            },
            "precision": case["expected"]["precision"],
            "recall": case["expected"]["recall"],
        },
        "contract": "civ.metrics/v1alpha1",
        "datasets": [
            {
                "counts": case["expected"]["counts"],
                "dataset": case["dataset"],
                "excluded": {"data_gaps": 0, "labels": 0, "predictions": 0},
                "f1": case["expected"]["f1"],
                "match_quality": {
                    "mean_temporal_iou": case["expected"]["mean_temporal_iou"]
                },
                "precision": case["expected"]["precision"],
                "recall": case["expected"]["recall"],
                "source_sha256": fixture["source_sha256"],
            }
        ],
        "label_pack_sha256": sha256(labels.read_bytes()).hexdigest(),
        "matching": {"assignment": "one_to_one_best", "temporal_iou_threshold": 0.5},
    }


@pytest.mark.parametrize("case_index", [0, 1])
def test_score_uses_one_to_one_best_matching_and_penalizes_duplicates(
    tmp_path: Path, case_index: int
) -> None:
    fixture = _load_fixture("matching_and_duplicates.json")
    case = fixture["cases"][case_index]
    working, labels = _write_scoring_inputs(tmp_path, case, fixture["source_sha256"])

    result = run_civ(tmp_path, ["score", str(working), "--labels", str(labels)])

    assert result.returncode == 0, result.stderr
    dataset_metrics = json.loads(result.stdout)["datasets"][0]
    assert dataset_metrics["counts"] == case["expected"]["counts"]
    assert dataset_metrics["precision"] == case["expected"]["precision"]
    assert dataset_metrics["recall"] == case["expected"]["recall"]
    assert dataset_metrics["f1"] == case["expected"]["f1"]
    assert dataset_metrics["match_quality"] == {
        "mean_temporal_iou": case["expected"]["mean_temporal_iou"]
    }


def test_score_excludes_labels_and_predictions_overlapping_known_data_gaps(
    tmp_path: Path,
) -> None:
    case = _load_fixture("data_gap_exclusion.json")
    working, labels = _write_scoring_inputs(tmp_path, case, case["source_sha256"])

    result = run_civ(tmp_path, ["score", str(working), "--labels", str(labels)])

    assert result.returncode == 0, result.stderr
    dataset_metrics = json.loads(result.stdout)["datasets"][0]
    assert dataset_metrics["counts"] == case["expected"]["counts"]
    assert dataset_metrics["excluded"] == case["expected"]["excluded"]
    assert dataset_metrics["precision"] == case["expected"]["precision"]
    assert dataset_metrics["recall"] == case["expected"]["recall"]
    assert dataset_metrics["f1"] == case["expected"]["f1"]
    assert dataset_metrics["match_quality"] == {
        "mean_temporal_iou": case["expected"]["mean_temporal_iou"]
    }


def test_score_isolates_incompatible_dataset_identity_failure(tmp_path: Path) -> None:
    fixture = _load_fixture("threshold_boundaries.json")
    case = fixture["cases"][1]
    invalid_root = tmp_path / "invalid"
    valid_root = tmp_path / "valid"
    invalid_root.mkdir()
    valid_root.mkdir()
    invalid_working, invalid_labels = _write_scoring_inputs(
        invalid_root, case, fixture["source_sha256"]
    )
    label_pack = json.loads(invalid_labels.read_text(encoding="utf-8"))
    label_pack["source_sha256"] = "3" * 64
    invalid_labels.write_text(
        json.dumps(label_pack, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    prior_metrics = b"prior metrics remain intact\n"
    (invalid_working / "metrics.json").write_bytes(prior_metrics)

    invalid_result = run_civ(
        invalid_root,
        ["score", str(invalid_working), "--labels", str(invalid_labels)],
    )

    assert invalid_result.returncode == 2
    assert "label pack source_sha256 does not match submission source sha256" in (
        invalid_result.stderr
    )
    assert "Traceback" not in invalid_result.stderr
    assert (invalid_working / "metrics.json").read_bytes() == prior_metrics

    valid_working, valid_labels = _write_scoring_inputs(
        valid_root, case, fixture["source_sha256"]
    )
    valid_result = run_civ(
        valid_root,
        ["score", str(valid_working), "--labels", str(valid_labels)],
    )

    assert valid_result.returncode == 0, valid_result.stderr
    assert (valid_working / "metrics.json").is_file()


def test_score_ranks_deliberately_different_detectors_in_expected_order(
    tmp_path: Path,
) -> None:
    fixture = _load_fixture("rank_calibration.json")
    observed: list[tuple[float, str]] = []
    for detector in fixture["detectors"]:
        root = tmp_path / detector["name"]
        root.mkdir()
        case = {
            "dataset": fixture["dataset"],
            "labels": fixture["labels"],
            "predictions": detector["predictions"],
        }
        working, labels = _write_scoring_inputs(root, case, fixture["source_sha256"])

        result = run_civ(root, ["score", str(working), "--labels", str(labels)])

        assert result.returncode == 0, result.stderr
        f1 = json.loads(result.stdout)["datasets"][0]["f1"]
        assert f1 == detector["expected_f1"]
        observed.append((f1, detector["name"]))

    assert [name for _, name in sorted(observed, reverse=True)] == fixture["expected_order"]


def test_score_matching_is_orthogonal_to_clip_validity(tmp_path: Path) -> None:
    fixture = _load_fixture("threshold_boundaries.json")
    case = fixture["cases"][1]
    working, labels = _write_scoring_inputs(tmp_path, case, fixture["source_sha256"])
    manifest_path = working / "run-manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["clips"] = [{"event_id": "prediction-1", "valid": True}]
    manifest_path.write_text(
        json.dumps(manifest, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
        newline="\n",
    )

    valid_clip = run_civ(tmp_path, ["score", str(working), "--labels", str(labels)])
    assert valid_clip.returncode == 0, valid_clip.stderr
    valid_metrics = json.loads(valid_clip.stdout)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["clips"][0]["valid"] = False
    manifest_path.write_text(
        json.dumps(manifest, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
        newline="\n",
    )

    invalid_clip = run_civ(tmp_path, ["score", str(working), "--labels", str(labels)])

    assert invalid_clip.returncode == 0, invalid_clip.stderr
    assert json.loads(invalid_clip.stdout) == valid_metrics


@pytest.mark.parametrize(
    ("failure", "expected_error"),
    [
        ("invalid-label", "label 0 end_ns must be non-negative"),
        ("invalid-prediction", "event on line 1 end_ns must be non-negative"),
        (
            "zero-length-prediction",
            "event on line 1 end_ns must be greater than start_ns",
        ),
        ("boolean-prediction", "event on line 1 start_ns must be an integer"),
        ("missing-labels", "label pack does not exist"),
    ],
)
def test_score_rejects_invalid_or_missing_inputs_without_overwriting_metrics(
    tmp_path: Path, failure: str, expected_error: str
) -> None:
    fixture = _load_fixture("threshold_boundaries.json")
    case = fixture["cases"][1]
    working, labels = _write_scoring_inputs(tmp_path, case, fixture["source_sha256"])
    if failure == "invalid-label":
        label_pack = json.loads(labels.read_text(encoding="utf-8"))
        label_pack["labels"][0]["end_ns"] = -1
        labels.write_text(
            json.dumps(label_pack, sort_keys=True, separators=(",", ":")) + "\n",
            encoding="utf-8",
            newline="\n",
        )
    elif failure in {
        "boolean-prediction",
        "invalid-prediction",
        "zero-length-prediction",
    }:
        event = json.loads((working / "events.jsonl").read_text(encoding="utf-8"))
        if failure == "invalid-prediction":
            event["end_ns"] = -1
        elif failure == "zero-length-prediction":
            event["end_ns"] = event["start_ns"]
        else:
            event["start_ns"] = False
        (working / "events.jsonl").write_text(
            json.dumps(event, sort_keys=True, separators=(",", ":")) + "\n",
            encoding="utf-8",
            newline="\n",
        )
    else:
        labels = tmp_path / "missing-labels.json"
    prior_metrics = b"prior metrics remain intact\n"
    (working / "metrics.json").write_bytes(prior_metrics)

    result = run_civ(tmp_path, ["score", str(working), "--labels", str(labels)])

    assert result.returncode == 2
    assert expected_error in result.stderr
    assert "Traceback" not in result.stderr
    assert (working / "metrics.json").read_bytes() == prior_metrics
