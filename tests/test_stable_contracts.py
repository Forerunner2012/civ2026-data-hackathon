from __future__ import annotations

import json
from hashlib import sha256
from pathlib import Path
from typing import Any

import pytest
import yaml

from civ_workshop.contracts import STABLE_FIELDS
from tests.helpers import (
    MicroCase,
    create_micro_case,
    prepare_scored_submission,
    run_civ,
    run_complete_workflow,
)

REPOSITORY = Path(__file__).parents[1]
SCHEMA_DIRECTORY = REPOSITORY / "schemas"


def _schema(contract: str) -> dict[str, Any]:
    kind, version = contract.split("/")
    path = SCHEMA_DIRECTORY / f"{kind}.{version}.schema.json"
    schema: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    return schema


def _identifier_field(contract: str) -> str:
    return "spec" if contract == "civ.eventspec/v1" else "contract"


def _assert_matches_schema(document: dict[str, Any], contract: str) -> None:
    schema = _schema(contract)
    assert document[_identifier_field(contract)] == contract
    assert set(schema["required"]) <= set(document) <= set(schema["properties"])


def _write_json(path: Path, value: object) -> None:
    path.write_text(
        json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def _detected_working(tmp_path: Path) -> tuple[MicroCase, Path]:
    case = create_micro_case(tmp_path / "case")
    working = tmp_path / "working"
    detected = run_civ(
        tmp_path,
        ["detect", str(case.spec), str(case.bag), "--output", str(working)],
    )
    assert detected.returncode == 0, detected.stderr
    return case, working


def _set_event_contract(working: Path, contract: str | None) -> None:
    events_path = working / "events.jsonl"
    event = json.loads(events_path.read_text(encoding="utf-8"))
    if contract is None:
        event.pop("contract")
    else:
        event["contract"] = contract
    _write_json(events_path, event)


def test_detect_dry_run_accepts_stable_eventspec(tmp_path: Path) -> None:
    case = create_micro_case(tmp_path)

    result = run_civ(
        tmp_path,
        ["detect", str(case.spec), str(case.bag), "--dry-run"],
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout == '{"dry_run":true,"event_count":1}\n'


@pytest.mark.parametrize(
    ("contract", "diagnostic"),
    [
        (
            "civ.eventspec/v1alpha1",
            "unsupported EventSpec contract 'civ.eventspec/v1alpha1'; expected "
            "'civ.eventspec/v1'; regenerate with the stable civ workflow",
        ),
        (
            "civ.eventspec/v1.0",
            "invalid EventSpec contract 'civ.eventspec/v1.0'; expected 'civ.eventspec/v1'",
        ),
        (
            "civ.eventspec/v1beta1",
            "unsupported EventSpec contract 'civ.eventspec/v1beta1'; expected 'civ.eventspec/v1'",
        ),
        (
            "civ.eventspec/v2",
            "unsupported EventSpec contract 'civ.eventspec/v2'; this civ-workshop supports "
            "'civ.eventspec/v1'",
        ),
        (
            "civ.metrics/v1",
            "invalid EventSpec contract 'civ.metrics/v1'; expected 'civ.eventspec/v1'",
        ),
    ],
)
def test_detect_dry_run_rejects_unsupported_eventspec_contracts(
    tmp_path: Path, contract: str, diagnostic: str
) -> None:
    case = create_micro_case(tmp_path)
    case.spec.write_text(
        case.spec.read_text(encoding="utf-8").replace(
            "civ.eventspec/v1", contract
        ),
        encoding="utf-8",
    )

    result = run_civ(
        tmp_path,
        ["detect", str(case.spec), str(case.bag), "--dry-run"],
    )

    assert result.returncode == 2
    assert result.stderr == f"civ: {diagnostic}\n"


def test_clip_rejects_mixed_event_and_manifest_versions_before_mutation(
    tmp_path: Path,
) -> None:
    case, working = _detected_working(tmp_path)
    manifest_path = working / "run-manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["contract"] = "civ.run-manifest/v1alpha1"
    _write_json(manifest_path, manifest)
    before = manifest_path.read_bytes()

    result = run_civ(
        tmp_path, ["clip", str(working / "events.jsonl"), str(case.bag)]
    )

    assert result.returncode == 2
    assert "mixed participant contract versions:" in result.stderr
    assert "civ.event/v1, civ.run-manifest/v1alpha1" in result.stderr
    assert manifest_path.read_bytes() == before
    assert not (working / "evidence").exists()


@pytest.mark.parametrize(
    ("contract", "diagnostic"),
    [
        (
            "civ.run-manifest/v1.0",
            "invalid run manifest contract 'civ.run-manifest/v1.0'; expected "
            "'civ.run-manifest/v1'",
        ),
        (
            "civ.metrics/v1",
            "invalid run manifest contract 'civ.metrics/v1'; expected 'civ.run-manifest/v1'",
        ),
        (
            "civ.run-manifest/v2",
            "unsupported run manifest contract 'civ.run-manifest/v2'; this civ-workshop "
            "supports 'civ.run-manifest/v1'",
        ),
    ],
)
def test_clip_rejects_invalid_manifest_contract_before_mutation(
    tmp_path: Path, contract: str, diagnostic: str
) -> None:
    case, working = _detected_working(tmp_path)
    manifest_path = working / "run-manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["contract"] = contract
    _write_json(manifest_path, manifest)
    before = manifest_path.read_bytes()

    result = run_civ(
        tmp_path, ["clip", str(working / "events.jsonl"), str(case.bag)]
    )

    assert result.returncode == 2
    assert result.stderr == f"civ: {diagnostic}\n"
    assert manifest_path.read_bytes() == before
    assert not (working / "evidence").exists()


@pytest.mark.parametrize(
    ("contract", "diagnostic"),
    [
        (
            "civ.event/v2",
            "unsupported event contract 'civ.event/v2'; this civ-workshop supports "
            "'civ.event/v1'",
        ),
        (
            "civ.event/v1beta1",
            "unsupported event contract 'civ.event/v1beta1'; expected 'civ.event/v1'",
        ),
        (
            "civ.run-manifest/v1",
            "invalid event contract 'civ.run-manifest/v1'; expected 'civ.event/v1'",
        ),
        (None, "event contract is required; expected 'civ.event/v1'"),
    ],
)
def test_clip_rejects_events_outside_the_stable_contract_before_mutation(
    tmp_path: Path, contract: str | None, diagnostic: str
) -> None:
    case, working = _detected_working(tmp_path)
    _set_event_contract(working, contract)

    result = run_civ(
        tmp_path, ["clip", str(working / "events.jsonl"), str(case.bag)]
    )

    assert result.returncode == 2
    assert result.stderr == f"civ: {diagnostic}\n"
    assert not (working / "evidence").exists()


@pytest.mark.parametrize("event_contract", ["civ.event/v1alpha1", None])
def test_score_rejects_a_candidate_working_directory_without_writing_metrics(
    tmp_path: Path, event_contract: str | None
) -> None:
    case, working = _detected_working(tmp_path)
    manifest_path = working / "run-manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["contract"] = "civ.run-manifest/v1alpha1"
    _write_json(manifest_path, manifest)
    _set_event_contract(working, event_contract)

    result = run_civ(
        tmp_path, ["score", str(working), "--labels", str(case.labels)]
    )

    assert result.returncode == 2
    assert (
        "unsupported run manifest contract 'civ.run-manifest/v1alpha1'" in result.stderr
    )
    assert "regenerate with the stable civ workflow" in result.stderr
    assert not (working / "metrics.json").exists()


def test_report_rejects_events_outside_the_stable_contract_before_creating_bundle(
    tmp_path: Path,
) -> None:
    case = create_micro_case(tmp_path / "case")
    working = tmp_path / "working"
    prepare_scored_submission(case, working)
    _set_event_contract(working, "civ.event/v2")
    manifest_path = working / "run-manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["events"]["sha256"] = sha256((working / "events.jsonl").read_bytes()).hexdigest()
    _write_json(manifest_path, manifest)

    result = run_civ(tmp_path, ["report", str(working)])

    assert result.returncode == 2
    assert "unsupported event contract 'civ.event/v2'" in result.stderr
    assert not (working / "submission.zip").exists()


def test_detect_rejects_candidate_point_resource_and_requires_regeneration(
    tmp_path: Path,
) -> None:
    case = create_micro_case(tmp_path)
    resource = tmp_path / "points.json"
    _write_json(
        resource,
        {
            "contract": "civ.point-resource/v1alpha1",
            "coordinate_reference": "EPSG:4326",
            "points": [{"id": "one", "latitude": 49.0, "longitude": 4.0}],
        },
    )
    case.spec.write_text(
        case.spec.read_text(encoding="utf-8").replace(
            "condition: signal > 1.0",
            "resources:\n"
            "  points: {path: points.json, contract: civ.point-resource/v1alpha1}\n"
            "condition: signal > 1.0",
        ),
        encoding="utf-8",
    )

    result = run_civ(
        tmp_path, ["detect", str(case.spec), str(case.bag), "--dry-run"]
    )

    assert result.returncode == 2
    assert "unsupported point resource contract 'civ.point-resource/v1alpha1'" in result.stderr
    assert "regenerate with the stable civ workflow" in result.stderr


def test_report_rejects_candidate_metrics_before_creating_bundle(tmp_path: Path) -> None:
    case = create_micro_case(tmp_path / "case")
    working = tmp_path / "working"
    prepare_scored_submission(case, working)
    metrics_path = working / "metrics.json"
    metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
    metrics["contract"] = "civ.metrics/v1alpha1"
    _write_json(metrics_path, metrics)
    manifest_path = working / "run-manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["metrics"]["sha256"] = sha256(metrics_path.read_bytes()).hexdigest()
    _write_json(manifest_path, manifest)

    result = run_civ(tmp_path, ["report", str(working)])

    assert result.returncode == 2
    assert "unsupported metrics contract 'civ.metrics/v1alpha1'" in result.stderr
    assert not (working / "submission.zip").exists()


@pytest.mark.parametrize(
    ("member", "candidate", "diagnostic"),
    [
        (
            "bundle",
            "civ.submission-bundle/v1alpha1",
            "unsupported submission bundle contract 'civ.submission-bundle/v1alpha1'",
        ),
        (
            "reproduction",
            "civ.reproduction/v1alpha1",
            "unsupported reproduction contract 'civ.reproduction/v1alpha1'",
        ),
    ],
)
def test_report_rejects_candidate_submission_declarations_without_overwriting_bundle(
    tmp_path: Path, member: str, candidate: str, diagnostic: str
) -> None:
    case = create_micro_case(tmp_path / "case")
    working = tmp_path / "working"
    prepare_scored_submission(case, working)
    first = run_civ(tmp_path, ["report", str(working)])
    assert first.returncode == 0, first.stderr
    bundle_path = working / "submission.zip"
    bundle_before = bundle_path.read_bytes()
    manifest_path = working / "run-manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if member == "bundle":
        manifest["submission"]["contract"] = candidate
    else:
        manifest["submission"]["reproduction"]["contract"] = candidate
    _write_json(manifest_path, manifest)
    manifest_before = manifest_path.read_bytes()

    result = run_civ(tmp_path, ["report", str(working)])

    assert result.returncode == 2
    assert diagnostic in result.stderr
    assert bundle_path.read_bytes() == bundle_before
    assert manifest_path.read_bytes() == manifest_before


def test_published_schemas_pin_the_closed_stable_field_sets() -> None:
    assert sorted(path.name for path in SCHEMA_DIRECTORY.glob("*.schema.json")) == sorted(
        f"{contract.replace('/', '.')}.schema.json" for contract in STABLE_FIELDS
    )
    for contract, allowed in STABLE_FIELDS.items():
        schema = _schema(contract)
        assert schema["additionalProperties"] is False
        assert set(schema["properties"]) == set(allowed)
        assert set(schema["required"]) <= set(allowed)
        assert schema["properties"][_identifier_field(contract)] == {"const": contract}


def test_stable_workflow_artifacts_carry_exactly_their_published_fields(tmp_path: Path) -> None:
    case = create_micro_case(tmp_path / "case")
    working = tmp_path / "working"
    reported = run_complete_workflow(case, working)
    assert reported.returncode == 0, reported.stderr

    manifest = json.loads((working / "run-manifest.json").read_text(encoding="utf-8"))
    event = json.loads((working / "events.jsonl").read_text(encoding="utf-8"))
    spec = yaml.safe_load(case.spec.read_text(encoding="utf-8"))
    _assert_matches_schema(spec, "civ.eventspec/v1")
    _assert_matches_schema(event, "civ.event/v1")
    _assert_matches_schema(manifest, "civ.run-manifest/v1")
    _assert_matches_schema(
        json.loads((working / "metrics.json").read_text(encoding="utf-8")), "civ.metrics/v1"
    )
    _assert_matches_schema(manifest["submission"], "civ.submission-bundle/v1")
    _assert_matches_schema(manifest["submission"]["reproduction"], "civ.reproduction/v1")


@pytest.mark.parametrize(
    ("relative", "contract"),
    [
        ("kashiwa/right_turn.yaml", "civ.eventspec/v1"),
        ("french/left_turn.yaml", "civ.eventspec/v1"),
        ("reims/cave-encounter.yaml", "civ.eventspec/v1"),
        ("reims/cave-zones.json", "civ.point-resource/v1"),
    ],
)
def test_checked_in_examples_carry_exactly_their_published_fields(
    relative: str, contract: str
) -> None:
    path = REPOSITORY / "examples" / relative
    loader = json.loads if path.suffix == ".json" else yaml.safe_load

    _assert_matches_schema(loader(path.read_text(encoding="utf-8")), contract)


def test_detect_rejects_an_unknown_eventspec_field(tmp_path: Path) -> None:
    case = create_micro_case(tmp_path)
    case.spec.write_text(
        case.spec.read_text(encoding="utf-8") + "detector_notes: keep my scratch notes\n",
        encoding="utf-8",
    )

    result = run_civ(tmp_path, ["detect", str(case.spec), str(case.bag), "--dry-run"])

    assert result.returncode == 2
    assert result.stderr == (
        "civ: invalid EventSpec 'civ.eventspec/v1': unknown field 'detector_notes'\n"
    )


@pytest.mark.parametrize(
    ("artifact", "field", "diagnostic"),
    [
        (
            "events.jsonl",
            "confidence",
            "invalid event 'civ.event/v1': unknown field 'confidence'",
        ),
        (
            "run-manifest.json",
            "runtime_seconds",
            "invalid run manifest 'civ.run-manifest/v1': unknown field 'runtime_seconds'",
        ),
    ],
)
def test_clip_rejects_unknown_stable_fields_before_mutation(
    tmp_path: Path, artifact: str, field: str, diagnostic: str
) -> None:
    case, working = _detected_working(tmp_path)
    path = working / artifact
    document = json.loads(path.read_text(encoding="utf-8"))
    document[field] = 1
    _write_json(path, document)

    result = run_civ(tmp_path, ["clip", str(working / "events.jsonl"), str(case.bag)])

    assert result.returncode == 2
    assert result.stderr == f"civ: {diagnostic}\n"
    assert not (working / "evidence").exists()


def test_report_rejects_unknown_metrics_fields_before_creating_bundle(tmp_path: Path) -> None:
    case = create_micro_case(tmp_path / "case")
    working = tmp_path / "working"
    prepare_scored_submission(case, working)
    metrics_path = working / "metrics.json"
    metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
    metrics["elapsed_seconds"] = 0.25
    _write_json(metrics_path, metrics)
    manifest_path = working / "run-manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["metrics"]["sha256"] = sha256(metrics_path.read_bytes()).hexdigest()
    _write_json(manifest_path, manifest)

    result = run_civ(tmp_path, ["report", str(working)])

    assert result.returncode == 2
    assert result.stderr == (
        "civ: invalid metrics 'civ.metrics/v1': unknown field 'elapsed_seconds'\n"
    )
    assert not (working / "submission.zip").exists()
