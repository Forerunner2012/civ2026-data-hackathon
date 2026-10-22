from __future__ import annotations

import json
from pathlib import Path

import pytest

from civ_workshop.artifacts import file_sha256, read_json_file
from civ_workshop.errors import CivError
from civ_workshop.label_packs import ProductBinding, load_label_pack
from civ_workshop.organizer.cave_references import (
    CaveProductInput,
    generate_cave_references,
)


def _inputs(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> tuple[
    CaveProductInput, Path, Path
]:
    recording = tmp_path / "product.mcap"
    recording.write_bytes(b"synthetic product bytes")
    manifest = tmp_path / "product.manifest.json"
    manifest.write_text(json.dumps({"provenance": {"split": "development"}}), encoding="utf-8")
    binding = ProductBinding(
        dataset="reims",
        manifest_sha256=file_sha256(manifest),
        parent_end_ns=10,
        parent_start_ns=0,
        product_end_ns=10,
        product_name=recording.name,
        product_sha256=file_sha256(recording),
        product_start_ns=0,
        source_id="synthetic-source",
        source_sha256="a" * 64,
    )
    monkeypatch.setattr(
        "civ_workshop.organizer.cave_references._product_binding",
        lambda *_args, **_kwargs: binding,
    )
    examples = Path(__file__).resolve().parents[1] / "examples" / "reims"
    return (
        CaveProductInput("reims-dev-0", recording, manifest),
        examples / "cave-encounter.yaml",
        examples / "cave-zones.json",
    )


def _write_empty_detection(
    output: Path, *, recording: Path, event_spec: Path, locations: Path
) -> None:
    output.mkdir(parents=True)
    (output / "events.jsonl").write_text("", encoding="utf-8")
    (output / "run-manifest.json").write_text(
        json.dumps(
            {
                "source": {"sha256": file_sha256(recording)},
                "spec": {"sha256": file_sha256(event_spec)},
                "resources": [{"sha256": file_sha256(locations)}],
            }
        ),
        encoding="utf-8",
    )


def test_successful_zero_encounter_writes_a_product_bound_empty_reference(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    product, event_spec, locations = _inputs(tmp_path, monkeypatch)

    def detect(spec_path: Path, recording: Path, output: Path) -> dict[str, int]:
        _write_empty_detection(
            output, recording=recording, event_spec=spec_path, locations=locations
        )
        return {"event_count": 0}

    monkeypatch.setattr("civ_workshop.organizer.cave_references.detect_events", detect)
    output = tmp_path / "private-reference-output"
    summary = generate_cave_references(
        [product],
        event_spec_path=event_spec,
        location_resource_path=locations,
        output_directory=output,
    )

    assert summary["generated_count"] == 1
    assert summary["zero_encounter_count"] == 1
    index = read_json_file(output / "generation-index.json", "generation index")
    record = index["products"][0]
    assert record["status"] == "generated_zero_encounter"
    assert record["human_review"] == "not_performed"
    assert record["reference_path"] == "references/reims-dev-0.json"
    reference_path = output / str(record["reference_path"])
    pack = load_label_pack(reference_path)
    assert pack["source_sha256"] == file_sha256(product.recording_path)
    assert pack["labels"] == []
    assert record["generated_labels_sha256"] == file_sha256(reference_path)


@pytest.mark.parametrize(
    ("message", "expected"),
    [
        ("EventSpec topics not found in bag: /fix", "missing_gnss"),
        ("CEL input latitude must produce a finite number", "invalid_gnss"),
    ],
)
def test_gnss_failures_are_reported_without_a_reference(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    message: str,
    expected: str,
) -> None:
    product, event_spec, locations = _inputs(tmp_path, monkeypatch)

    def detect(_spec_path: Path, _recording: Path, _output: Path) -> dict[str, int]:
        raise CivError(message)

    monkeypatch.setattr("civ_workshop.organizer.cave_references.detect_events", detect)
    output = tmp_path / "private-reference-output"
    summary = generate_cave_references(
        [product],
        event_spec_path=event_spec,
        location_resource_path=locations,
        output_directory=output,
    )

    assert summary["generated_count"] == 0
    assert summary["missing_gnss_count"] == (1 if expected == "missing_gnss" else 0)
    assert summary["invalid_gnss_count"] == (1 if expected == "invalid_gnss" else 0)
    index = read_json_file(output / "generation-index.json", "generation index")
    record = index["products"][0]
    assert record["status"] == expected
    assert "generated_labels_sha256" not in record
    assert not (output / "references" / f"{product.product_id}.json").exists()


def test_private_reference_output_is_rejected_inside_repository(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    product, event_spec, locations = _inputs(tmp_path, monkeypatch)
    repository_root = Path(__file__).resolve().parents[1]
    output = repository_root / "tmp" / "must-not-create-private-reference"

    with pytest.raises(CivError, match="outside the repository"):
        generate_cave_references(
            [product],
            event_spec_path=event_spec,
            location_resource_path=locations,
            output_directory=output,
        )

    assert not output.exists()
