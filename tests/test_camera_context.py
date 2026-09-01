from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import pytest
from mcap.reader import make_reader
from mcap.writer import CompressionType, Writer

from civ_workshop.artifacts import canonical_json, file_sha256
from civ_workshop.camera_context import (
    APPROVAL_CONTRACT,
    MANIFEST_CONTRACT,
    RECIPE_CONTRACT,
    SET_CONTRACT,
    build_camera_context,
    build_set,
)
from civ_workshop.errors import CivError

IMAGE_TOPIC = "/camera/image/compressed"
INFO_TOPIC = "/camera/camera_info"


def _write_json(path: Path, value: Mapping[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"{canonical_json(value)}\n", encoding="utf-8", newline="\n")


def _write_source(path: Path) -> None:
    with path.open("wb") as stream:
        writer = Writer(stream, compression=CompressionType.NONE)
        writer.start(profile="ros2", library="camera-context-test")
        schema = writer.register_schema("fixture/msg/Bytes", "ros2msg", b"uint8[] data\n")
        channels = {
            topic: writer.register_channel(
                schema_id=schema,
                topic=topic,
                message_encoding="cdr",
            )
            for topic in (IMAGE_TOPIC, INFO_TOPIC, "/vehicle/signal")
        }
        for sequence, (topic, log_time) in enumerate(
            (
                (IMAGE_TOPIC, 9),
                (IMAGE_TOPIC, 10),
                (INFO_TOPIC, 10),
                ("/vehicle/signal", 15),
                (IMAGE_TOPIC, 20),
                (INFO_TOPIC, 20),
                (IMAGE_TOPIC, 21),
            )
        ):
            writer.add_message(
                channel_id=channels[topic],
                log_time=log_time,
                publish_time=log_time + 1,
                sequence=sequence,
                data=bytes((sequence,)),
            )
        writer.finish()


def _write_context_product(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as stream:
        writer = Writer(stream, compression=CompressionType.NONE)
        writer.start(profile="ros2", library="camera-context-test")
        schema = writer.register_schema("fixture/msg/Bytes", "ros2msg", b"uint8[] data\n")
        channel = writer.register_channel(
            schema_id=schema,
            topic=IMAGE_TOPIC,
            message_encoding="cdr",
        )
        for sequence, log_time in enumerate((10, 20)):
            writer.add_message(
                channel_id=channel,
                log_time=log_time,
                publish_time=log_time,
                sequence=sequence,
                data=bytes((sequence,)),
            )
        writer.finish()


def _fixture(tmp_path: Path) -> tuple[Path, Path, Path, Path]:
    source = tmp_path / "source.mcap"
    signal_root = tmp_path / "signals"
    signal_root.mkdir()
    signal = signal_root / "KSH-fixture-signals.mcap"
    signal.write_bytes(b"accepted signal bytes")
    signal_manifest = signal_root / "KSH-fixture-signals.mcap.manifest.json"
    _write_source(source)
    _write_json(
        signal_manifest,
        {
            "contract": "civ.data-product-manifest/v1",
            "parent": {"source_id": "KSH-fixture", "sha256": file_sha256(source)},
            "product": {
                "message_start_ns": 10,
                "message_end_ns": 20,
                "name": signal.name,
                "sha256": file_sha256(signal),
            },
            "provenance": {"dataset": "kashiwa", "split": "warmup"},
        },
    )
    approval = tmp_path / "approval.json"
    _write_json(
        approval,
        {
            "contract": APPROVAL_CONTRACT,
            "approval_id": "fixture-approval",
            "authority": "Fixture Event Owner",
            "decision": "approved",
            "frame_review_set_sha256": "a" * 64,
            "inspection_complete": True,
            "redaction_required": False,
            "rights_statement": "Approved for this exact fixture set.",
        },
    )
    recipe = tmp_path / "recipe.json"
    _write_json(
        recipe,
        {
            "contract": RECIPE_CONTRACT,
            "recipe_id": "KSH-fixture-camera-context-v1",
            "version": 1,
            "product_name": "KSH-fixture-camera-context.mcap",
            "source": {"id": "KSH-fixture", "sha256": file_sha256(source)},
            "signal_product": {
                "name": signal.name,
                "sha256": file_sha256(signal),
                "manifest": signal_manifest.name,
                "manifest_sha256": file_sha256(signal_manifest),
            },
            "dataset": "kashiwa",
            "split": "warmup",
            "topics": [IMAGE_TOPIC, INFO_TOPIC],
            "time_bounds": {"start_ns": 10, "end_ns": 20},
            "calibration": {"status": "embedded-camera-info", "topic": INFO_TOPIC},
            "rights": {"attribution": "Fixture", "scope": "Test only"},
        },
    )
    return source, signal_root, recipe, approval


def _document(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def test_build_is_byte_deterministic_bounded_and_camera_only(tmp_path: Path) -> None:
    source, signal_root, recipe, approval = _fixture(tmp_path)
    first = tmp_path / "build-1"
    second = tmp_path / "build-2"

    build_camera_context(source, signal_root, recipe, approval, first)
    build_camera_context(source, signal_root, recipe, approval, second)

    product_name = "KSH-fixture-camera-context.mcap"
    manifest_name = f"{product_name}.manifest.json"
    assert (first / product_name).read_bytes() == (second / product_name).read_bytes()
    assert (first / manifest_name).read_bytes() == (second / manifest_name).read_bytes()
    with (first / product_name).open("rb") as stream:
        messages = list(make_reader(stream, validate_crcs=True).iter_messages())
    assert [(channel.topic, message.log_time) for _, channel, message in messages] == [
        (IMAGE_TOPIC, 10),
        (INFO_TOPIC, 10),
        (IMAGE_TOPIC, 20),
        (INFO_TOPIC, 20),
    ]
    manifest = _document(first / manifest_name)
    assert manifest["contract"] == MANIFEST_CONTRACT
    assert manifest["dataset"] == "kashiwa"
    assert manifest["split"] == "warmup"
    assert manifest["product"]["message_count"] == 4
    assert manifest["time_bounds"] == {"start_ns": 10, "end_ns": 20}
    assert str(tmp_path).lower() not in (first / manifest_name).read_text().lower()


def test_build_rejects_changed_source_before_creating_output(tmp_path: Path) -> None:
    source, signal_root, recipe, approval = _fixture(tmp_path)
    source.write_bytes(source.read_bytes() + b"changed")
    output = tmp_path / "output"

    with pytest.raises(CivError, match="source SHA-256 changed"):
        build_camera_context(source, signal_root, recipe, approval, output)

    assert not output.exists()


@pytest.mark.parametrize(
    ("change", "message"),
    [
        ({"split": "sealed"}, "must not be sealed"),
        ({"topics": [IMAGE_TOPIC, "/vehicle/signal"]}, "one compressed image"),
        ({"calibration": {"status": "absent-not-inferred", "topic": None}}, "binding"),
    ],
)
def test_recipe_rejects_sealed_extra_topics_and_false_calibration(
    tmp_path: Path, change: dict[str, object], message: str
) -> None:
    source, signal_root, recipe, approval = _fixture(tmp_path)
    document = _document(recipe)
    document.update(change)
    _write_json(recipe, document)

    with pytest.raises(CivError, match=message):
        build_camera_context(source, signal_root, recipe, approval, tmp_path / "output")


def test_build_requires_complete_attributable_approval(tmp_path: Path) -> None:
    source, signal_root, recipe, approval = _fixture(tmp_path)
    document = _document(approval)
    document["authority"] = ""
    _write_json(approval, document)

    with pytest.raises(CivError, match="authority"):
        build_camera_context(source, signal_root, recipe, approval, tmp_path / "output")


def test_set_requires_exact_13_roles_and_is_deterministic(tmp_path: Path) -> None:
    manifests: list[Path] = []
    approval = {"id": "approval", "authority": "Event Owner", "document_sha256": "a" * 64}
    for index in range(13):
        dataset = "kashiwa" if index < 8 else "reims"
        split = "warmup" if index == 0 else "development"
        source_id = f"KSH-{index:02d}" if dataset == "kashiwa" else f"RMS-CHUNK-{index - 8}"
        path = tmp_path / "manifests" / f"{source_id}.manifest.json"
        product_name = f"{source_id}-camera-context.mcap"
        product_path = path.parent / product_name
        _write_context_product(product_path)
        _write_json(
            path,
            {
                "contract": MANIFEST_CONTRACT,
                "approval": approval,
                "dataset": dataset,
                "split": split,
                "parent": {"id": source_id, "sha256": "b" * 64},
                "product": {
                    "name": product_name,
                    "sha256": file_sha256(product_path),
                    "byte_size": product_path.stat().st_size,
                    "message_count": 2,
                    "message_start_ns": 10,
                    "message_end_ns": 20,
                    "topics": [{"topic": IMAGE_TOPIC, "message_count": 2}],
                },
                "signal_product": {"name": f"{source_id}-signals.mcap", "sha256": "d" * 64},
                "time_bounds": {"start_ns": 10, "end_ns": 20},
            },
        )
        manifests.append(path)

    first = tmp_path / "set-1.json"
    second = tmp_path / "set-2.json"
    build_set(manifests, first)
    build_set(list(reversed(manifests)), second)

    assert first.read_bytes() == second.read_bytes()
    assert _document(first)["contract"] == SET_CONTRACT
    with pytest.raises(CivError, match="exact 13 participant roles"):
        build_set(manifests[:-1], tmp_path / "incomplete.json")
