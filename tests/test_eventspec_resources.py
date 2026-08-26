from __future__ import annotations

import json
import math
import zipfile
from hashlib import sha256
from pathlib import Path
from typing import Any

import pytest
from mcap.writer import CompressionType, Writer

from tests.helpers import create_micro_case, prepare_scored_submission, run_civ

EARTH_MEAN_RADIUS_M = 6_371_008.8
RESOURCE_CONTRACT = "civ.point-resource/v1alpha1"


def _write_location_bag(
    path: Path, locations: list[tuple[float, float]], *, topic: str = "/location"
) -> None:
    with path.open("wb") as stream:
        writer = Writer(stream, compression=CompressionType.NONE)
        writer.start(profile="civ.resource-conformance", library="human-authored-resource-cases")
        schema_id = writer.register_schema(
            name="civ.conformance.Location",
            encoding="jsonschema",
            data=b'{"type":"object"}',
        )
        channel_id = writer.register_channel(
            schema_id=schema_id,
            topic=topic,
            message_encoding="json",
        )
        for second, (latitude, longitude) in enumerate(locations):
            timestamp = second * 1_000_000_000
            writer.add_message(
                channel_id=channel_id,
                log_time=timestamp,
                publish_time=timestamp,
                data=json.dumps({"latitude": latitude, "longitude": longitude}).encode(),
            )
        writer.finish()


def _resource_document(points: list[dict[str, object]]) -> dict[str, object]:
    return {
        "contract": RESOURCE_CONTRACT,
        "coordinate_reference": "EPSG:4326",
        "points": points,
    }


def _write_resource_spec(path: Path, *, resource_path: str = "caves.json") -> None:
    path.write_text(
        "spec: civ.eventspec/v1alpha1\n"
        "name: reims-cave-encounter\n"
        "signals:\n"
        "  latitude: {topic: /location, field: latitude}\n"
        "  longitude: {topic: /location, field: longitude}\n"
        "resources:\n"
        "  caves:\n"
        f"    path: {resource_path}\n"
        f"    contract: {RESOURCE_CONTRACT}\n"
        "derive:\n"
        "  cave_distance_m:\n"
        "    op: min_distance_to\n"
        "    resource: caves\n"
        "    from: [latitude, longitude]\n"
        "condition: cave_distance_m <= 40.0\n"
        "timing: {min_duration: 1s, merge_gap: 1.1s, max_duration: 10s}\n"
        "evidence: {before: 0s, after: 0s, topics: [/location]}\n",
        encoding="utf-8",
    )


def test_reims_resource_exemplar_detects_two_encounters_and_records_provenance(
    tmp_path: Path,
) -> None:
    case = tmp_path / "case"
    case.mkdir()
    bag = case / "reims.mcap"
    spec = case / "detector.yaml"
    resource = case / "caves.json"
    output = tmp_path / "working"
    cave_points = [
        {"id": "cave-b", "latitude": 49.001, "longitude": 4.001},
        {"id": "cave-a", "latitude": 49.0, "longitude": 4.0},
    ]
    resource.write_text(
        json.dumps(_resource_document(cave_points), sort_keys=True), encoding="utf-8"
    )
    _write_location_bag(
        bag,
        [
            (48.0, 3.0),
            (49.0, 4.0),
            (49.0, 4.0),
            (48.0, 3.0),
            (49.001, 4.001),
            (49.001, 4.001),
            (48.0, 3.0),
        ],
    )
    _write_resource_spec(spec)

    result = run_civ(case, ["detect", str(spec), str(bag), "--output", str(output)])

    assert result.returncode == 0, result.stderr
    events = [json.loads(line) for line in (output / "events.jsonl").read_text().splitlines()]
    assert [(event["start_ns"], event["end_ns"]) for event in events] == [
        (1_000_000_000, 2_000_000_000),
        (4_000_000_000, 5_000_000_000),
    ]
    assert [event["trigger_values"]["cave_distance_m"] for event in events] == [0.0, 0.0]
    manifest = json.loads((output / "run-manifest.json").read_text(encoding="utf-8"))
    assert manifest["resources"] == [
        {
            "contract": RESOURCE_CONTRACT,
            "name": "caves",
            "path": "caves.json",
            "sha256": sha256(resource.read_bytes()).hexdigest(),
        }
    ]
    assert not (output / "detector" / "caves.json").exists()


def test_min_distance_to_includes_the_exact_40_metre_boundary(tmp_path: Path) -> None:
    case = tmp_path / "case"
    case.mkdir()
    bag = case / "boundary.mcap"
    spec = case / "detector.yaml"
    resource = case / "caves.json"
    resource.write_text(
        json.dumps(
            _resource_document([{"id": "origin", "latitude": 49.0, "longitude": 4.0}]),
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    forty_metres_latitude = 49.0 + math.degrees(40.0 / EARTH_MEAN_RADIUS_M)
    outside_latitude = 49.0 + math.degrees(40.001 / EARTH_MEAN_RADIUS_M)
    _write_location_bag(
        bag,
        [
            (outside_latitude, 4.0),
            (forty_metres_latitude, 4.0),
            (49.0, 4.0),
            (outside_latitude, 4.0),
        ],
    )
    _write_resource_spec(spec)

    result = run_civ(case, ["detect", str(spec), str(bag)])

    assert result.returncode == 0, result.stderr
    event = json.loads((case / "events.jsonl").read_text(encoding="utf-8"))
    assert (event["start_ns"], event["end_ns"]) == (1_000_000_000, 2_000_000_000)
    assert event["trigger_values"]["cave_distance_m"] == 40.0


def test_checked_in_reims_example_traverses_the_public_detect_command(tmp_path: Path) -> None:
    bag = tmp_path / "reims-example.mcap"
    output = tmp_path / "working"
    spec = Path(__file__).parents[1] / "examples" / "reims" / "cave-encounter.yaml"
    _write_location_bag(
        bag,
        [
            (48.0, 3.0),
            (49.2583, 4.0317),
            (48.0, 3.0),
            (48.0, 3.0),
            (48.0, 3.0),
            (49.257, 4.033),
            (48.0, 3.0),
        ],
        topic="/fix",
    )

    result = run_civ(tmp_path, ["detect", str(spec), str(bag), "--output", str(output)])

    assert result.returncode == 0, result.stderr
    events = [json.loads(line) for line in (output / "events.jsonl").read_text().splitlines()]
    assert [(event["start_ns"], event["end_ns"]) for event in events] == [
        (1_000_000_000, 1_000_000_000),
        (5_000_000_000, 5_000_000_000),
    ]


def test_min_distance_to_rejects_invalid_live_coordinates(tmp_path: Path) -> None:
    case = tmp_path / "case"
    case.mkdir()
    bag = case / "invalid-location.mcap"
    spec = case / "detector.yaml"
    (case / "caves.json").write_text(
        json.dumps(
            _resource_document([{"id": "cave", "latitude": 49.0, "longitude": 4.0}])
        ),
        encoding="utf-8",
    )
    _write_location_bag(bag, [(91.0, 4.0)])
    _write_resource_spec(spec)

    result = run_civ(case, ["detect", str(spec), str(bag)])

    assert result.returncode == 2
    assert result.stderr == (
        "civ: derive.cave_distance_m latitude must be between -90 and 90\n"
    )


@pytest.mark.parametrize(
    ("document", "diagnostic"),
    [
        (
            {
                "contract": "civ.point-resource/v2",
                "coordinate_reference": "EPSG:4326",
                "points": [],
            },
            "resource 'caves' has unsupported contract 'civ.point-resource/v2'",
        ),
        (
            _resource_document([]),
            "resource 'caves' points must contain at least one point",
        ),
        (
            {
                **_resource_document([]),
                "coordinate_reference": "EPSG:3857",
            },
            "resource 'caves' coordinate_reference must be EPSG:4326",
        ),
        (
            _resource_document([{"id": "bad", "latitude": 91.0, "longitude": 4.0}]),
            "resource 'caves' point 'bad' latitude must be between -90 and 90",
        ),
        (
            _resource_document(
                [
                    {"id": "same", "latitude": 49.0, "longitude": 4.0},
                    {"id": "same", "latitude": 49.1, "longitude": 4.1},
                ]
            ),
            "resource 'caves' point id 'same' is duplicated",
        ),
    ],
)
def test_point_resources_reject_invalid_contracts_actionably(
    document: dict[str, Any], diagnostic: str, tmp_path: Path
) -> None:
    case = tmp_path / "case"
    case.mkdir()
    bag = case / "locations.mcap"
    spec = case / "detector.yaml"
    (case / "caves.json").write_text(json.dumps(document), encoding="utf-8")
    _write_location_bag(bag, [(49.0, 4.0)])
    _write_resource_spec(spec)

    result = run_civ(case, ["detect", str(spec), str(bag)])

    assert result.returncode == 2
    assert result.stderr == f"civ: {diagnostic}\n"


@pytest.mark.parametrize(
    ("resource_path", "diagnostic"),
    [
        ("missing.json", "resource 'caves' does not exist: missing.json"),
        (
            "https://example.test/caves.json",
            "resources.caves.path must be a relative POSIX path inside the EventSpec directory",
        ),
        (
            "../caves.json",
            "resources.caves.path must be a relative POSIX path inside the EventSpec directory",
        ),
    ],
)
def test_resource_bindings_reject_nonlocal_paths_actionably(
    resource_path: str, diagnostic: str, tmp_path: Path
) -> None:
    case = tmp_path / "case"
    case.mkdir()
    bag = case / "locations.mcap"
    spec = case / "detector.yaml"
    _write_location_bag(bag, [(49.0, 4.0)])
    _write_resource_spec(spec, resource_path=resource_path)

    result = run_civ(case, ["detect", str(spec), str(bag)])

    assert result.returncode == 2
    assert result.stderr == f"civ: {diagnostic}\n"


def test_detector_field_is_reserved_with_a_correction(tmp_path: Path) -> None:
    case = create_micro_case(tmp_path / "case")
    case.spec.write_text(
        case.spec.read_text(encoding="utf-8") + "detector: custom.py\n", encoding="utf-8"
    )

    result = run_civ(case.root, ["detect", str(case.spec), str(case.bag)])

    assert result.returncode == 2
    assert result.stderr == (
        "civ: EventSpec detector is reserved; remove detector and use signals, derive, "
        "and resources\n"
    )


def test_resource_bytes_stay_out_of_the_metadata_bundle(tmp_path: Path) -> None:
    case = create_micro_case(tmp_path / "case")
    resource = case.root / "caves.json"
    resource.write_text(
        json.dumps(
            _resource_document([{"id": "target", "latitude": 2.0, "longitude": 2.0}]),
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    case.spec.write_text(
        case.spec.read_text(encoding="utf-8")
        .replace(
            "  signal:\n    topic: /micro/signal\n    field: value\n",
            "  latitude: {topic: /micro/signal, field: value}\n"
            "  longitude: {topic: /micro/signal, field: value}\n"
            "resources:\n"
            "  caves: {path: caves.json, contract: civ.point-resource/v1alpha1}\n"
            "derive:\n"
            "  cave_distance_m: {op: min_distance_to, resource: caves, "
            "from: [latitude, longitude]}\n",
        )
        .replace("condition: signal > 1.0", "condition: cave_distance_m <= 0.1"),
        encoding="utf-8",
    )
    working = tmp_path / "working"
    prepare_scored_submission(case, working)

    result = run_civ(case.root, ["report", str(working)])

    assert result.returncode == 0, result.stderr
    with zipfile.ZipFile(working / "submission.zip") as archive:
        assert "detector/caves.json" not in archive.namelist()
        assert all(not name.endswith("caves.json") for name in archive.namelist())


def test_report_rejects_invalid_resource_provenance_hash(tmp_path: Path) -> None:
    case = create_micro_case(tmp_path / "case")
    (case.root / "caves.json").write_text(
        json.dumps(
            _resource_document([{"id": "target", "latitude": 2.0, "longitude": 2.0}])
        ),
        encoding="utf-8",
    )
    case.spec.write_text(
        case.spec.read_text(encoding="utf-8")
        .replace(
            "  signal:\n    topic: /micro/signal\n    field: value\n",
            "  latitude: {topic: /micro/signal, field: value}\n"
            "  longitude: {topic: /micro/signal, field: value}\n"
            "resources:\n"
            "  caves: {path: caves.json, contract: civ.point-resource/v1alpha1}\n"
            "derive:\n"
            "  cave_distance_m: {op: min_distance_to, resource: caves, "
            "from: [latitude, longitude]}\n",
        )
        .replace("condition: signal > 1.0", "condition: cave_distance_m <= 0.1"),
        encoding="utf-8",
    )
    working = tmp_path / "working"
    prepare_scored_submission(case, working)
    manifest_path = working / "run-manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["resources"][0]["sha256"] = "not-a-hash"
    manifest_path.write_text(json.dumps(manifest, sort_keys=True), encoding="utf-8")

    result = run_civ(case.root, ["report", str(working)])

    assert result.returncode == 2
    assert result.stderr == "civ: run manifest resource 'caves' sha256 is invalid\n"


def test_resource_outputs_are_byte_stable_across_fresh_directories(tmp_path: Path) -> None:
    outputs: list[Path] = []
    for name in ("first", "second"):
        case = tmp_path / name
        case.mkdir()
        bag = case / "locations.mcap"
        spec = case / "detector.yaml"
        (case / "caves.json").write_text(
            json.dumps(
                _resource_document([{"id": "cave", "latitude": 49.0, "longitude": 4.0}]),
                sort_keys=True,
            ),
            encoding="utf-8",
        )
        _write_location_bag(bag, [(48.0, 3.0), (49.0, 4.0), (49.0, 4.0)])
        _write_resource_spec(spec)
        output = case / "working"
        result = run_civ(case, ["detect", str(spec), str(bag), "--output", str(output)])
        assert result.returncode == 0, result.stderr
        outputs.append(output)

    assert (outputs[0] / "events.jsonl").read_bytes() == (
        outputs[1] / "events.jsonl"
    ).read_bytes()
    assert (outputs[0] / "run-manifest.json").read_bytes() == (
        outputs[1] / "run-manifest.json"
    ).read_bytes()

    changed_case = tmp_path / "second"
    changed_resource = changed_case / "caves.json"
    resource_document = json.loads(changed_resource.read_text(encoding="utf-8"))
    changed_resource.write_text(
        json.dumps(resource_document, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    changed_output = changed_case / "changed-working"
    changed = run_civ(
        changed_case,
        [
            "detect",
            str(changed_case / "detector.yaml"),
            str(changed_case / "locations.mcap"),
            "--output",
            str(changed_output),
        ],
    )
    assert changed.returncode == 0, changed.stderr
    original_event = json.loads((outputs[1] / "events.jsonl").read_text(encoding="utf-8"))
    changed_event = json.loads((changed_output / "events.jsonl").read_text(encoding="utf-8"))
    assert changed_event["event_id"] != original_event["event_id"]
    original_manifest = json.loads(
        (outputs[1] / "run-manifest.json").read_text(encoding="utf-8")
    )
    changed_manifest = json.loads(
        (changed_output / "run-manifest.json").read_text(encoding="utf-8")
    )
    assert changed_manifest["resources"][0]["sha256"] != (
        original_manifest["resources"][0]["sha256"]
    )
