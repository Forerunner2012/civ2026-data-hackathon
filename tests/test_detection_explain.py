from __future__ import annotations

import json
from pathlib import Path

import pytest

from tests.helpers import create_micro_case, run_civ, write_micro_bag


@pytest.mark.parametrize(
    ("values", "maximum", "expected"),
    [
        ([0.0] * 5, "30s", (0, 0, 0, 0, 0)),
        ([2.0, 0.0, 0.0], "30s", (1, 1, 1, 0, 0)),
        ([2.0] * 31, "30s", (31, 1, 0, 0, 1)),
        ([2.0] * 32, "30s", (32, 1, 0, 1, 0)),
        ([2.0] * 32, "600s", (32, 1, 0, 0, 1)),
    ],
)
def test_explain_distinguishes_hits_and_duration_rejection_without_writing(
    tmp_path: Path, values: list[float], maximum: str, expected: tuple[int, ...]
) -> None:
    case = create_micro_case(tmp_path / "case")
    write_micro_bag(case.bag, values)
    case.spec.write_text(
        case.spec.read_text().replace("max_duration: 10s", f"max_duration: {maximum}")
    )
    output = tmp_path / "unwritten"
    result = run_civ(
        case.root,
        [
            "detect",
            str(case.spec),
            str(case.bag),
            "--output",
            str(output),
            "--dry-run",
            "--explain",
        ],
    )
    assert result.returncode == 0, result.stderr
    summary = json.loads(result.stdout)
    keys = (
        "matching_samples",
        "merged_candidates",
        "rejected_below_min_duration",
        "rejected_above_max_duration",
        "emitted_events",
    )
    assert tuple(summary["timing"][key] for key in keys) == expected
    assert summary["event_count"] == expected[-1]
    assert not output.exists()


def test_explain_changes_only_console_output(tmp_path: Path) -> None:
    case = create_micro_case(tmp_path / "case")
    outputs = [tmp_path / "plain", tmp_path / "explained"]
    for index, output in enumerate(outputs):
        arguments = ["detect", str(case.spec), str(case.bag), "--output", str(output)]
        if index:
            arguments.append("--explain")
        result = run_civ(case.root, arguments)
        assert result.returncode == 0, result.stderr
        assert ("timing" in json.loads(result.stdout)) == bool(index)

    def files(directory: Path) -> dict[str, bytes]:
        return {
            path.relative_to(directory).as_posix(): path.read_bytes()
            for path in directory.rglob("*")
            if path.is_file()
        }

    assert files(outputs[0]) == files(outputs[1])


def test_wider_geofence_can_reject_the_entire_merged_interval(tmp_path: Path) -> None:
    from tests.test_eventspec_resources import (
        _resource_document,
        _write_location_bag,
        _write_resource_spec,
    )

    bag = tmp_path / "locations.mcap"
    spec = tmp_path / "detector.yaml"
    (tmp_path / "caves.json").write_text(
        json.dumps(
            _resource_document(
                [
                    {"id": "origin", "latitude": 49.0, "longitude": 4.0},
                ]
            )
        )
    )
    # About 56 m away except for two central hits. All 33 samples are within 125 m.
    _write_location_bag(bag, [(49.0 if i in (15, 16) else 49.0005, 4.0) for i in range(33)])
    _write_resource_spec(spec)
    text = spec.read_text().replace("max_duration: 10s", "max_duration: 30s")
    summaries = []
    for radius in (40.0, 125.0):
        spec.write_text(text.replace("<= 40.0", f"<= {radius}"))
        result = run_civ(tmp_path, ["detect", str(spec), str(bag), "--dry-run", "--explain"])
        assert result.returncode == 0, result.stderr
        summaries.append(json.loads(result.stdout))
    assert [s["event_count"] for s in summaries] == [1, 0]
    assert summaries[1]["timing"]["matching_samples"] == 33
    assert summaries[1]["timing"]["merged_candidates"] == 1
    assert summaries[1]["timing"]["rejected_above_max_duration"] == 1
