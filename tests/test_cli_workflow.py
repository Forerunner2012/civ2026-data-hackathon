from __future__ import annotations

import json
import zipfile
from hashlib import sha256
from pathlib import Path

import pytest
from mcap.reader import make_reader

from tests.helpers import (
    MICRO_SPEC,
    MicroCase,
    create_micro_case,
    detect_micro_case,
    prepare_scored_submission,
    run_civ,
    run_complete_workflow,
    write_raw_ros2_bag,
    write_ros2_bool_bag,
    write_ros2_nested_bag,
    write_ros2_steering_bag,
)


@pytest.fixture
def micro_case(tmp_path: Path) -> MicroCase:
    return create_micro_case(tmp_path)


def test_inspect_reports_deterministic_bag_inventory(micro_case: MicroCase) -> None:
    result = run_civ(micro_case.root, ["inspect", str(micro_case.bag), "--json"])

    assert result.returncode == 0, result.stderr
    inventory = json.loads(result.stdout)
    assert inventory["start_time_ns"] == 0
    assert inventory["end_time_ns"] == 4_000_000_000
    assert inventory["duration_ns"] == 4_000_000_000
    assert inventory["warnings"] == []
    assert inventory["topics"] == [
        {
            "fields": ["label"],
            "message_count": 5,
            "message_encoding": "json",
            "message_rate_hz": 1.25,
            "schema_encoding": "jsonschema",
            "schema_id": 2,
            "schema_name": "civ.micro.Evidence",
            "schema_sha256": "07b8f2a0d121377e913a4c8f90dd4f8806ccc10976ed77034beea4c872d11090",
            "topic": "/micro/evidence",
        },
        {
            "fields": ["value"],
            "message_count": 5,
            "message_encoding": "json",
            "message_rate_hz": 1.25,
            "schema_encoding": "jsonschema",
            "schema_id": 1,
            "schema_name": "civ.micro.Signal",
            "schema_sha256": "873826050fecba535a60b72dc40a5b30b4f03bec47947e4121938a519a4f896e",
            "topic": "/micro/signal",
        },
    ]


def test_inspect_renders_concise_human_inventory(micro_case: MicroCase) -> None:
    result = run_civ(micro_case.root, ["inspect", str(micro_case.bag)])

    assert result.returncode == 0, result.stderr
    assert result.stdout == (
        "Bag: micro.mcap\n"
        "Duration: 4.000s (0..4000000000 ns)\n"
        "Topics:\n"
        "  /micro/evidence  5 messages  1.25 Hz  civ.micro.Evidence  fields: label\n"
        "  /micro/signal  5 messages  1.25 Hz  civ.micro.Signal  fields: value\n"
    )


def test_inspect_discovers_fields_in_embedded_ros2_cdr_schema(tmp_path: Path) -> None:
    bag = tmp_path / "ros2.mcap"
    write_ros2_bool_bag(bag)

    result = run_civ(tmp_path, ["inspect", str(bag), "--json"])

    assert result.returncode == 0, result.stderr
    inventory = json.loads(result.stdout)
    assert inventory["topics"] == [
        {
            "fields": ["data"],
            "message_count": 1,
            "message_encoding": "cdr",
            "message_rate_hz": 0.0,
            "schema_encoding": "ros2msg",
            "schema_id": 1,
            "schema_name": "std_msgs/msg/Bool",
            "schema_sha256": sha256(b"bool data\n").hexdigest(),
            "topic": "/ros2/enabled",
        }
    ]
    assert inventory["warnings"] == []


def test_inspect_discovers_nested_ros2_field_paths(tmp_path: Path) -> None:
    bag = tmp_path / "ros2-nested.mcap"
    write_ros2_nested_bag(bag)

    result = run_civ(tmp_path, ["inspect", str(bag), "--json"])

    assert result.returncode == 0, result.stderr
    topic = json.loads(result.stdout)["topics"][0]
    assert topic["fields"] == [
        "turn.angular.x",
        "turn.angular.y",
        "turn.angular.z",
    ]


def test_inspect_reports_nested_message_arrays_as_consumable_fields(tmp_path: Path) -> None:
    bag = tmp_path / "ros2-array.mcap"
    write_raw_ros2_bag(
        bag,
        b"""geometry_msgs/Point[] points
================================================================================
MSG: geometry_msgs/Point
float64 x
float64 y
float64 z
""",
    )

    result = run_civ(tmp_path, ["inspect", str(bag), "--json"])

    assert result.returncode == 0, result.stderr
    topic = json.loads(result.stdout)["topics"][0]
    assert topic["fields"] == ["points"]


def test_detect_emits_one_normalized_interval_and_manifest(
    micro_case: MicroCase, tmp_path: Path
) -> None:
    output = tmp_path / "working"

    result = detect_micro_case(micro_case, output)

    assert result.returncode == 0, result.stderr
    event = json.loads((output / "events.jsonl").read_text(encoding="utf-8"))
    assert event == {
        "bag_sha256": sha256(micro_case.bag.read_bytes()).hexdigest(),
        "end_ns": 2_000_000_000,
        "event_id": event["event_id"],
        "spec_sha256": sha256(micro_case.spec.read_bytes()).hexdigest(),
        "start_ns": 1_000_000_000,
        "trigger_values": {"signal": 2.0},
    }
    assert len(event["event_id"]) == 64

    manifest = json.loads((output / "run-manifest.json").read_text(encoding="utf-8"))
    assert manifest["contract"] == "civ.run-manifest/v1alpha1"
    assert manifest["source"] == {
        "name": "micro.mcap",
        "sha256": sha256(micro_case.bag.read_bytes()).hexdigest(),
    }
    assert manifest["spec"] == {
        "contract": "civ.eventspec/v1alpha1",
        "name": "micro-high-signal",
        "sha256": sha256(micro_case.spec.read_bytes()).hexdigest(),
    }
    assert manifest["events"]["count"] == 1
    assert manifest["evidence"] == {
        "after_ns": 500_000_000,
        "before_ns": 500_000_000,
        "topics": ["/micro/evidence", "/micro/signal"],
    }


def test_detect_evaluates_embedded_ros2_cdr_messages(tmp_path: Path) -> None:
    bag = tmp_path / "ros2.mcap"
    spec = tmp_path / "detector.yaml"
    output = tmp_path / "working"
    write_ros2_bool_bag(bag, (False, True, True, False))
    spec.write_text(
        """\
spec: civ.eventspec/v1alpha1
name: ros2-enabled
signals:
  enabled:
    topic: /ros2/enabled
    field: data
condition: enabled == true
timing:
  min_duration: 1s
  merge_gap: 1.1s
  max_duration: 5s
evidence:
  before: 0s
  after: 0s
  topics:
    - /ros2/enabled
""",
        encoding="utf-8",
    )

    result = run_civ(
        tmp_path,
        ["detect", str(spec), str(bag), "--output", str(output)],
    )

    assert result.returncode == 0, result.stderr
    event = json.loads((output / "events.jsonl").read_text(encoding="utf-8"))
    assert event["start_ns"] == 1_000_000_000
    assert event["end_ns"] == 2_000_000_000
    assert event["trigger_values"] == {"enabled": True}


def test_kashiwa_example_detects_long_and_context_free_turns(tmp_path: Path) -> None:
    bag = tmp_path / "kashiwa-steering.mcap"
    output = tmp_path / "working"
    spec = Path(__file__).parents[1] / "examples" / "kashiwa" / "right_turn.yaml"
    write_ros2_steering_bag(bag)

    result = run_civ(tmp_path, ["detect", str(spec), str(bag), "--output", str(output)])

    assert result.returncode == 0, result.stderr
    events = [
        json.loads(line)
        for line in (output / "events.jsonl").read_text(encoding="utf-8").splitlines()
    ]
    assert [(event["start_ns"], event["end_ns"]) for event in events] == [
        (1_000_000_000, 21_000_000_000),
        (30_000_000_000, 35_000_000_000),
    ]
    assert all(event["trigger_values"] == {"steering_angle": 15} for event in events)


@pytest.mark.parametrize(
    "schema_data",
    [
        pytest.param(b"\xff", id="invalid-utf8"),
        pytest.param(b"not valid", id="invalid-field"),
    ],
)
def test_detect_reports_topic_for_invalid_embedded_ros2_schema(
    tmp_path: Path, schema_data: bytes
) -> None:
    bag = tmp_path / "ros2-invalid-schema.mcap"
    spec = tmp_path / "detector.yaml"
    write_raw_ros2_bag(bag, schema_data)
    spec.write_text(
        """\
spec: civ.eventspec/v1alpha1
name: invalid-schema
signals:
  signal:
    topic: /ros2/broken
    field: data
condition: signal == true
timing:
  min_duration: 1s
  merge_gap: 1s
  max_duration: 2s
evidence:
  before: 0s
  after: 0s
  topics:
    - /ros2/broken
""",
        encoding="utf-8",
    )

    result = run_civ(tmp_path, ["detect", str(spec), str(bag)])

    assert result.returncode == 2
    assert "topic /ros2/broken has invalid ROS 2 schema" in result.stderr
    assert "valid embedded ros2msg definition" in result.stderr
    assert "Traceback" not in result.stderr


def test_detect_dry_run_validates_without_writing(micro_case: MicroCase, tmp_path: Path) -> None:
    output = tmp_path / "working"
    output.mkdir()
    sentinel = output / "keep.txt"
    sentinel.write_text("unchanged", encoding="utf-8")

    before = {path.name: path.read_bytes() for path in output.iterdir()}
    result = run_civ(
        micro_case.root,
        [
            "detect",
            str(micro_case.spec),
            str(micro_case.bag),
            "--output",
            str(output),
            "--dry-run",
        ],
    )
    after = {path.name: path.read_bytes() for path in output.iterdir()}

    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout) == {"dry_run": True, "event_count": 1}
    assert after == before


def test_clip_writes_reopenable_evidence_and_updates_manifest(
    micro_case: MicroCase, tmp_path: Path
) -> None:
    working = tmp_path / "working"
    detected = detect_micro_case(micro_case, working)
    assert detected.returncode == 0, detected.stderr
    event = json.loads((working / "events.jsonl").read_text(encoding="utf-8"))

    result = run_civ(
        micro_case.root,
        ["clip", str(working / "events.jsonl"), str(micro_case.bag)],
    )

    assert result.returncode == 0, result.stderr
    clip = working / "evidence" / f"{event['event_id']}.mcap"
    assert clip.is_file()
    with clip.open("rb") as stream:
        messages = list(make_reader(stream, validate_crcs=True).iter_messages())
    assert sorted({channel.topic for _, channel, _ in messages}) == [
        "/micro/evidence",
        "/micro/signal",
    ]
    assert [message.log_time for _, _, message in messages] == [
        1_000_000_000,
        1_000_000_000,
        2_000_000_000,
        2_000_000_000,
    ]

    manifest = json.loads((working / "run-manifest.json").read_text(encoding="utf-8"))
    assert manifest["clips"] == [
        {
            "actual_end_ns": 2_000_000_000,
            "actual_start_ns": 1_000_000_000,
            "event_id": event["event_id"],
            "input_bytes": micro_case.bag.stat().st_size,
            "name": f"evidence/{event['event_id']}.mcap",
            "output_bytes": clip.stat().st_size,
            "requested_end_ns": 2_500_000_000,
            "requested_start_ns": 500_000_000,
            "sha256": sha256(clip.read_bytes()).hexdigest(),
            "topics": ["/micro/evidence", "/micro/signal"],
            "valid": True,
        }
    ]


def test_score_writes_deterministic_metrics_from_separate_labels(
    micro_case: MicroCase, tmp_path: Path
) -> None:
    working = tmp_path / "working"
    detected = detect_micro_case(micro_case, working)
    assert detected.returncode == 0, detected.stderr

    first = run_civ(
        micro_case.root,
        ["score", str(working), "--labels", str(micro_case.labels)],
    )
    assert first.returncode == 0, first.stderr
    first_metrics = (working / "metrics.json").read_bytes()
    second = run_civ(
        micro_case.root,
        ["score", str(working), "--labels", str(micro_case.labels)],
    )

    assert second.returncode == 0, second.stderr
    assert (working / "metrics.json").read_bytes() == first_metrics
    assert json.loads(first_metrics) == {
        "aggregate": {
            "counts": {"false_negative": 0, "false_positive": 0, "true_positive": 1},
            "f1": 1.0,
            "match_quality": {"mean_temporal_iou": 1.0},
            "precision": 1.0,
            "recall": 1.0,
        },
        "contract": "civ.metrics/v1alpha1",
        "datasets": [
            {
                "counts": {"false_negative": 0, "false_positive": 0, "true_positive": 1},
                "dataset": "micro",
                "excluded": {"data_gaps": 0, "labels": 0, "predictions": 0},
                "f1": 1.0,
                "match_quality": {"mean_temporal_iou": 1.0},
                "precision": 1.0,
                "recall": 1.0,
                "source_sha256": sha256(micro_case.bag.read_bytes()).hexdigest(),
            }
        ],
        "label_pack_sha256": sha256(micro_case.labels.read_bytes()).hexdigest(),
        "matching": {"assignment": "one_to_one_best", "temporal_iou_threshold": 0.5},
    }
    assert not (working / "labels.json").exists()


def test_report_assembles_stable_metadata_only_bundle(
    micro_case: MicroCase, tmp_path: Path
) -> None:
    working = tmp_path / "working"
    prepare_scored_submission(micro_case, working)

    first = run_civ(micro_case.root, ["report", str(working)])
    assert first.returncode == 0, first.stderr
    bundle = working / "submission.zip"
    first_bundle = bundle.read_bytes()
    second = run_civ(micro_case.root, ["report", str(working)])

    assert second.returncode == 0, second.stderr
    assert bundle.read_bytes() == first_bundle
    assert json.loads(first.stdout) == {
        "bundle": "submission.zip",
        "sha256": sha256(first_bundle).hexdigest(),
    }
    with zipfile.ZipFile(bundle) as archive:
        assert archive.namelist() == [
            "detector/detector.yaml",
            "events.jsonl",
            "figure.svg",
            "metrics.json",
            "report.md",
            "reproduce.ps1",
            "run-manifest.json",
        ]
        assert all(not name.startswith("evidence/") for name in archive.namelist())
        assert "labels.json" not in archive.namelist()


@pytest.mark.parametrize(
    ("arguments", "expected_error"),
    [
        (["inspect", "missing.mcap"], "bag does not exist"),
        (["detect", "bad-topic.yaml", "micro.mcap"], "EventSpec topics not found in bag"),
        (["detect", "bad-field.yaml", "micro.mcap"], "field not found in decoded message"),
        (["detect", "bad-cel.yaml", "micro.mcap"], "invalid CEL condition"),
        (["detect", "bad-timing.yaml", "micro.mcap"], "must not exceed"),
        (
            ["clip", "bad-events.jsonl", "micro.mcap"],
            "end_ns must be greater than start_ns",
        ),
        (["report", "incomplete"], "submission is missing report.md"),
    ],
)
def test_commands_return_actionable_errors_without_tracebacks(
    micro_case: MicroCase,
    tmp_path: Path,
    arguments: list[str],
    expected_error: str,
) -> None:
    substitutions = {
        "bad-topic.yaml": MICRO_SPEC.replace("/micro/signal", "/missing/topic", 1),
        "bad-field.yaml": MICRO_SPEC.replace("field: value", "field: missing"),
        "bad-cel.yaml": MICRO_SPEC.replace("signal > 1.0", "signal >"),
        "bad-timing.yaml": MICRO_SPEC.replace("min_duration: 1s", "min_duration: 20s"),
    }
    for name, contents in substitutions.items():
        (tmp_path / name).write_text(contents, encoding="utf-8")
    (tmp_path / "bad-events.jsonl").write_text(
        '{"event_id":"bad","start_ns":2,"end_ns":1}\n', encoding="utf-8"
    )
    (tmp_path / "incomplete").mkdir()

    result = run_civ(tmp_path, arguments)

    assert result.returncode == 2
    assert expected_error in result.stderr
    assert "Traceback" not in result.stderr


def test_complete_workflow_is_byte_stable_across_fresh_directories(
    micro_case: MicroCase, tmp_path: Path
) -> None:
    first_working = tmp_path / "first"
    second_working = tmp_path / "second"

    first = run_complete_workflow(micro_case, first_working)
    second = run_complete_workflow(micro_case, second_working)

    assert first.returncode == 0, first.stderr
    assert second.returncode == 0, second.stderr
    assert (first_working / "events.jsonl").read_bytes() == (
        second_working / "events.jsonl"
    ).read_bytes()
    assert (first_working / "metrics.json").read_bytes() == (
        second_working / "metrics.json"
    ).read_bytes()
    assert json.loads(first.stdout)["sha256"] == json.loads(second.stdout)["sha256"]
    assert (first_working / "submission.zip").read_bytes() == (
        second_working / "submission.zip"
    ).read_bytes()


def test_report_rejects_non_metadata_detector_artifacts(
    micro_case: MicroCase, tmp_path: Path
) -> None:
    working = tmp_path / "working"
    prepare_scored_submission(micro_case, working)
    (working / "detector" / "labels.json").write_text("{}", encoding="utf-8")

    result = run_civ(micro_case.root, ["report", str(working)])

    assert result.returncode == 2
    assert "detector directory contains non-EventSpec artifacts" in result.stderr
    assert "Traceback" not in result.stderr


def test_report_rejects_evidence_clip_used_as_figure(micro_case: MicroCase, tmp_path: Path) -> None:
    working = tmp_path / "working"
    prepare_scored_submission(micro_case, working)
    clip_name = json.loads((working / "run-manifest.json").read_text(encoding="utf-8"))["clips"][0][
        "name"
    ]
    report = (working / "report.md").read_text(encoding="utf-8")
    (working / "report.md").write_text(report.replace("figure.svg", clip_name), encoding="utf-8")

    result = run_civ(micro_case.root, ["report", str(working)])

    assert result.returncode == 2
    assert "top-level supported image file" in result.stderr
    assert "Traceback" not in result.stderr


def test_report_rejects_commented_out_reproduction_command(
    micro_case: MicroCase, tmp_path: Path
) -> None:
    working = tmp_path / "working"
    prepare_scored_submission(micro_case, working)
    (working / "reproduce.ps1").write_text("# civ detect detector.yaml bag.mcap\n")

    result = run_civ(micro_case.root, ["report", str(working)])

    assert result.returncode == 2
    assert "reproduction entry point must invoke civ detect" in result.stderr
    assert "Traceback" not in result.stderr


@pytest.mark.parametrize(
    ("artifact", "expected_error"),
    [
        ("events.jsonl", "events.jsonl hash does not match"),
        ("metrics.json", "metrics.json hash does not match"),
        ("detector/detector.yaml", "EventSpec hash does not match"),
    ],
)
def test_report_rejects_corrupt_bundle_artifacts(
    micro_case: MicroCase,
    tmp_path: Path,
    artifact: str,
    expected_error: str,
) -> None:
    working = tmp_path / "working"
    prepare_scored_submission(micro_case, working)
    artifact_path = working / artifact
    if artifact_path.suffix in {".yaml", ".yml"}:
        contents = artifact_path.read_text(encoding="utf-8")
        artifact_path.write_text(
            contents.replace("name: micro-high-signal", "name: changed"),
            encoding="utf-8",
        )
    else:
        with artifact_path.open("a", encoding="utf-8") as stream:
            stream.write("corrupt\n")

    result = run_civ(micro_case.root, ["report", str(working)])

    assert result.returncode == 2
    assert expected_error in result.stderr
    assert "Traceback" not in result.stderr
