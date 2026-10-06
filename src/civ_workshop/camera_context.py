from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from mcap.reader import make_reader
from mcap.writer import CompressionType, Writer

from civ_workshop.artifacts import canonical_json, file_sha256, read_json_file
from civ_workshop.artifacts import require_mapping as _mapping
from civ_workshop.artifacts import require_string as _string
from civ_workshop.errors import CivError

RECIPE_CONTRACT = "civ.camera-context-recipe/v1"
MANIFEST_CONTRACT = "civ.camera-context-manifest/v1"
SET_CONTRACT = "civ.camera-context-set/v1"
APPROVAL_CONTRACT = "civ.camera-context-privacy-rights-approval/v1"
WRITER_ID = "civ-workshop/camera-context-v1"
SHA256 = re.compile(r"[0-9a-f]{64}")
EXPECTED_ROLES = Counter(
    {
        ("kashiwa", "warmup"): 1,
        ("kashiwa", "development"): 7,
        ("reims", "development"): 5,
    }
)


def _digest(value: object, context: str) -> str:
    result = _string(value, context)
    if SHA256.fullmatch(result) is None:
        raise CivError(f"{context} must be a lowercase SHA-256")
    return result


def _integer(value: object, context: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise CivError(f"{context} must be a non-negative integer")
    return value


def _closed(value: Mapping[str, object], expected: set[str], context: str) -> None:
    if set(value) != expected:
        raise CivError(f"{context} has unknown or missing fields")


def _approval(path: Path) -> dict[str, str]:
    document = read_json_file(path, "camera-context approval")
    _closed(
        document,
        {
            "contract",
            "approval_id",
            "authority",
            "decision",
            "frame_review_set_sha256",
            "inspection_complete",
            "redaction_required",
            "rights_statement",
        },
        "camera-context approval",
    )
    if document.get("contract") != APPROVAL_CONTRACT:
        raise CivError("camera-context approval has the wrong contract")
    if document.get("decision") != "approved" or document.get("inspection_complete") is not True:
        raise CivError("camera-context approval is not complete")
    if document.get("redaction_required") is not False:
        raise CivError("camera-context build supports only the approved no-redaction pipeline")
    return {
        "id": _string(document.get("approval_id"), "camera-context approval id"),
        "authority": _string(document.get("authority"), "camera-context approval authority"),
        "document_sha256": file_sha256(path),
        "frame_review_set_sha256": _digest(
            document.get("frame_review_set_sha256"), "camera-context frame review set SHA-256"
        ),
        "rights_statement": _string(
            document.get("rights_statement"), "camera-context approval rights statement"
        ),
    }


def _recipe(path: Path) -> dict[str, Any]:
    document = read_json_file(path, "camera-context recipe")
    _closed(
        document,
        {
            "contract",
            "recipe_id",
            "version",
            "product_name",
            "source",
            "signal_product",
            "dataset",
            "split",
            "topics",
            "time_bounds",
            "calibration",
            "rights",
        },
        "camera-context recipe",
    )
    if document.get("contract") != RECIPE_CONTRACT or document.get("version") != 1:
        raise CivError("camera-context recipe must be v1")
    source = _mapping(document.get("source"), "camera-context source")
    signal = _mapping(document.get("signal_product"), "camera-context signal product")
    bounds = _mapping(document.get("time_bounds"), "camera-context time bounds")
    calibration = _mapping(document.get("calibration"), "camera-context calibration")
    rights = _mapping(document.get("rights"), "camera-context rights")
    _closed(source, {"id", "sha256"}, "camera-context source")
    _closed(signal, {"name", "sha256", "manifest", "manifest_sha256"}, "camera-context signal")
    _closed(bounds, {"start_ns", "end_ns"}, "camera-context time bounds")
    _closed(calibration, {"status", "topic"}, "camera-context calibration")
    _closed(rights, {"attribution", "scope"}, "camera-context rights")
    topics = document.get("topics")
    if not isinstance(topics, list) or not topics:
        raise CivError("camera-context topics must be a non-empty list")
    selected = sorted({_string(item, "camera-context topic") for item in topics})
    if len(selected) != len(topics):
        raise CivError("camera-context topics must be unique")
    image_topics = [topic for topic in selected if topic.endswith("/compressed")]
    camera_info_topics = [topic for topic in selected if topic.endswith("/camera_info")]
    if len(image_topics) != 1 or len(selected) != len(image_topics) + len(camera_info_topics):
        raise CivError("camera-context topics must be one compressed image and optional CameraInfo")
    if len(camera_info_topics) > 1:
        raise CivError("camera-context recipe contains unrelated camera calibration")
    calibration_status = _string(calibration.get("status"), "camera-context calibration status")
    calibration_topic = calibration.get("topic")
    if camera_info_topics:
        if (
            calibration_status != "embedded-camera-info"
            or calibration_topic != camera_info_topics[0]
        ):
            raise CivError("camera-context CameraInfo calibration binding is inconsistent")
    elif calibration_status != "absent-not-inferred" or calibration_topic is not None:
        raise CivError("camera-context missing calibration must be explicit and not inferred")
    dataset = _string(document.get("dataset"), "camera-context dataset")
    if dataset not in {"kashiwa", "reims"}:
        raise CivError("camera-context dataset must be kashiwa or reims")
    split = _string(document.get("split"), "camera-context split")
    if split == "sealed":
        raise CivError("camera-context recipe must not be sealed")
    start_ns = _integer(bounds.get("start_ns"), "camera-context start")
    end_ns = _integer(bounds.get("end_ns"), "camera-context end")
    if start_ns > end_ns:
        raise CivError("camera-context time bounds are reversed")
    name = _string(document.get("product_name"), "camera-context product name")
    if Path(name).name != name or not name.endswith("-camera-context.mcap"):
        raise CivError("camera-context product name is invalid")
    return {
        **document,
        "source": {
            "id": _string(source["id"], "source id"),
            "sha256": _digest(source["sha256"], "source SHA-256"),
        },
        "signal_product": {
            "name": _string(signal["name"], "signal name"),
            "sha256": _digest(signal["sha256"], "signal SHA-256"),
            "manifest": _string(signal["manifest"], "signal manifest"),
            "manifest_sha256": _digest(signal["manifest_sha256"], "signal manifest SHA-256"),
        },
        "topics": selected,
        "dataset": dataset,
        "time_bounds": {"start_ns": start_ns, "end_ns": end_ns},
        "calibration": calibration,
        "rights": rights,
    }


def _write(
    source: Path, output: Path, topics: list[str], start_ns: int, end_ns: int
) -> dict[str, object]:
    schema_ids: dict[int, int] = {}
    channel_ids: dict[int, int] = {}
    counts: Counter[str] = Counter()
    first: int | None = None
    last: int | None = None
    with source.open("rb") as stream, output.open("xb") as destination:
        reader = make_reader(stream, validate_crcs=True)
        writer = Writer(destination, compression=CompressionType.NONE)
        writer.start(profile=reader.get_header().profile, library=WRITER_ID)
        for schema, channel, message in reader.iter_messages(topics=topics):
            if not start_ns <= message.log_time <= end_ns:
                continue
            schema_id = 0
            if schema is not None:
                schema_id = schema_ids.get(schema.id, 0)
                if not schema_id:
                    schema_id = writer.register_schema(schema.name, schema.encoding, schema.data)
                    schema_ids[schema.id] = schema_id
            channel_id = channel_ids.get(channel.id)
            if channel_id is None:
                channel_id = writer.register_channel(
                    schema_id=schema_id,
                    topic=channel.topic,
                    message_encoding=channel.message_encoding,
                    metadata=channel.metadata,
                )
                channel_ids[channel.id] = channel_id
            writer.add_message(
                channel_id=channel_id,
                log_time=message.log_time,
                publish_time=message.publish_time,
                sequence=message.sequence,
                data=message.data,
            )
            counts[channel.topic] += 1
            first = message.log_time if first is None else min(first, message.log_time)
            last = message.log_time if last is None else max(last, message.log_time)
        writer.finish()
    missing = sorted(set(topics) - set(counts))
    if missing or first is None or last is None:
        output.unlink(missing_ok=True)
        raise CivError(f"camera-context source is missing in-window topics: {', '.join(missing)}")
    return {
        "message_count": sum(counts.values()),
        "message_start_ns": first,
        "message_end_ns": last,
        "topics": [
            {"message_count": counts[topic], "topic": topic} for topic in sorted(counts)
        ],
    }


def build_camera_context(
    source: Path, signal_root: Path, recipe_path: Path, approval_path: Path, output_root: Path
) -> dict[str, object]:
    recipe = _recipe(recipe_path)
    approval = _approval(approval_path)
    if file_sha256(source) != recipe["source"]["sha256"]:
        raise CivError("camera-context source SHA-256 changed")
    signal = recipe["signal_product"]
    signal_path = signal_root / signal["name"]
    signal_manifest_path = signal_root / signal["manifest"]
    if (
        file_sha256(signal_path) != signal["sha256"]
        or file_sha256(signal_manifest_path) != signal["manifest_sha256"]
    ):
        raise CivError("matching signal product or manifest changed")
    signal_manifest = read_json_file(signal_manifest_path, "signal manifest")
    if signal_manifest.get("contract") != "civ.data-product-manifest/v1":
        raise CivError("matching signal manifest has the wrong contract")
    parent = _mapping(signal_manifest.get("parent"), "signal manifest parent")
    product = _mapping(signal_manifest.get("product"), "signal manifest product")
    provenance = _mapping(signal_manifest.get("provenance"), "signal manifest provenance")
    if (
        parent.get("source_id") != recipe["source"]["id"]
        or parent.get("sha256") != recipe["source"]["sha256"]
        or product.get("name") != signal["name"]
        or product.get("sha256") != signal["sha256"]
        or provenance.get("dataset") != recipe["dataset"]
        or provenance.get("split") != recipe["split"]
    ):
        raise CivError("camera-context recipe does not match the accepted signal product")
    bounds = recipe["time_bounds"]
    if (product.get("message_start_ns"), product.get("message_end_ns")) != (
        bounds["start_ns"],
        bounds["end_ns"],
    ):
        raise CivError("camera-context bounds do not match the signal product")
    output_root.mkdir(parents=True, exist_ok=True)
    output = output_root / recipe["product_name"]
    manifest_path = output_root / f"{output.name}.manifest.json"
    if output.exists() or manifest_path.exists():
        raise CivError("camera-context output already exists")
    stats = _write(source, output, recipe["topics"], bounds["start_ns"], bounds["end_ns"])
    manifest = {
        "approval": approval,
        "calibration": recipe["calibration"],
        "contract": MANIFEST_CONTRACT,
        "dataset": recipe["dataset"],
        "parent": recipe["source"],
        "product": {
            "byte_size": output.stat().st_size, "name": output.name,
            "sha256": file_sha256(output), **stats,
        },
        "recipe": {"id": recipe["recipe_id"], "sha256": file_sha256(recipe_path), "version": 1},
        "rights": recipe["rights"],
        "signal_product": signal,
        "split": recipe["split"],
        "time_bounds": bounds,
        "transformation": "topic-filter-and-time-bound-copy-v1",
    }
    manifest_path.write_text(f"{canonical_json(manifest)}\n", encoding="utf-8", newline="\n")
    return {
        "manifest": manifest_path.name,
        "manifest_sha256": file_sha256(manifest_path),
        "product": output.name,
        "product_sha256": manifest["product"]["sha256"],
    }


def audit_camera_context(product_path: Path, manifest_path: Path) -> dict[str, object]:
    manifest = read_json_file(manifest_path, "camera-context manifest")
    if manifest.get("contract") != MANIFEST_CONTRACT:
        raise CivError("camera-context manifest has the wrong contract")
    serialized = canonical_json(manifest).lower()
    if ":\\" in serialized or "/bags/" in serialized or "organizer_path" in serialized:
        raise CivError("camera-context manifest leaks an organizer path")
    product = _mapping(manifest.get("product"), "camera-context product")
    bounds = _mapping(manifest.get("time_bounds"), "camera-context time bounds")
    expected_topics_value = product.get("topics")
    if not isinstance(expected_topics_value, list) or not expected_topics_value:
        raise CivError("camera-context manifest topics must be a non-empty list")
    expected_counts: dict[str, int] = {}
    for item in expected_topics_value:
        topic_record = _mapping(item, "camera-context manifest topic")
        _closed(topic_record, {"message_count", "topic"}, "camera-context manifest topic")
        topic = _string(topic_record.get("topic"), "camera-context manifest topic name")
        expected_counts[topic] = _integer(
            topic_record.get("message_count"), "camera-context manifest topic count"
        )
    if len(expected_counts) != len(expected_topics_value):
        raise CivError("camera-context manifest contains duplicate topics")
    if product_path.name != product.get("name"):
        raise CivError("camera-context product name does not match its manifest")
    if product_path.stat().st_size != product.get("byte_size"):
        raise CivError("camera-context product size changed")
    if file_sha256(product_path) != product.get("sha256"):
        raise CivError("camera-context product SHA-256 changed")
    start_ns = _integer(bounds.get("start_ns"), "camera-context start")
    end_ns = _integer(bounds.get("end_ns"), "camera-context end")
    counts: Counter[str] = Counter()
    first: int | None = None
    last: int | None = None
    with product_path.open("rb") as stream:
        for _, channel, message in make_reader(stream, validate_crcs=True).iter_messages():
            if channel.topic not in expected_counts:
                raise CivError("camera-context product contains an extra topic")
            if not start_ns <= message.log_time <= end_ns:
                raise CivError("camera-context product contains an out-of-range message")
            counts[channel.topic] += 1
            first = message.log_time if first is None else min(first, message.log_time)
            last = message.log_time if last is None else max(last, message.log_time)
    if dict(counts) != expected_counts:
        raise CivError("camera-context product message counts changed")
    if (
        sum(counts.values()) != product.get("message_count")
        or first != product.get("message_start_ns")
        or last != product.get("message_end_ns")
    ):
        raise CivError("camera-context product message bounds changed")
    return {
        "byte_size": product["byte_size"],
        "message_count": product["message_count"],
        "sha256": product["sha256"],
        "valid": True,
    }


def build_set(manifests: Sequence[Path], output: Path) -> dict[str, object]:
    records = []
    roles: Counter[tuple[str, str]] = Counter()
    seen: set[str] = set()
    approval: dict[str, object] | None = None
    for path in manifests:
        manifest = read_json_file(path, "camera-context manifest")
        if manifest.get("contract") != MANIFEST_CONTRACT:
            raise CivError("camera-context set received the wrong manifest")
        parent = _mapping(manifest["parent"], "camera-context parent")
        source_id = _string(parent["id"], "camera-context source id")
        if source_id in seen:
            raise CivError("camera-context set contains duplicate source")
        seen.add(source_id)
        signal = _mapping(manifest["signal_product"], "camera-context signal")
        dataset = _string(manifest.get("dataset"), "camera-context dataset")
        split = _string(manifest.get("split"), "camera-context split")
        roles[(dataset, split)] += 1
        if approval is None:
            approval = _mapping(manifest["approval"], "camera-context approval")
        elif manifest["approval"] != approval:
            raise CivError("camera-context manifests do not share one exact approval")
        product = _mapping(manifest["product"], "camera-context product")
        audit_camera_context(path.parent / _string(product.get("name"), "product name"), path)
        records.append({
            "camera_context_bytes": product["byte_size"],
            "camera_context_product": product["name"],
            "camera_context_sha256": product["sha256"],
            "dataset": dataset,
            "manifest": path.name,
            "manifest_bytes": path.stat().st_size,
            "manifest_sha256": file_sha256(path),
            "message_count": product["message_count"],
            "message_end_ns": product["message_end_ns"],
            "message_start_ns": product["message_start_ns"],
            "signal_product": signal["name"],
            "signal_sha256": signal["sha256"],
            "source_id": source_id,
            "source_sha256": parent["sha256"],
            "split": split,
            "topics": product["topics"],
            "time_bounds": manifest["time_bounds"],
        })
    if len(records) != 13 or roles != EXPECTED_ROLES:
        raise CivError("camera-context set must contain the exact 13 participant roles")
    payload_bytes = sum(
        _integer(item["camera_context_bytes"], "camera-context product bytes")
        + _integer(item["manifest_bytes"], "camera-context manifest bytes")
        for item in records
    )
    document: dict[str, object] = {
        "approval": approval,
        "contract": SET_CONTRACT,
        "products": sorted(records, key=lambda item: item["source_id"]),
        "release_id": "civ-2026-phase5-camera-context-v1",
        "required_disk_bytes": 0,
    }
    while True:
        serialized = f"{canonical_json(document)}\n"
        required = payload_bytes + len(serialized.encode())
        if document["required_disk_bytes"] == required:
            break
        document["required_disk_bytes"] = required
    output.write_text(serialized, encoding="utf-8", newline="\n")
    return {
        "product_count": 13,
        "required_disk_bytes": required,
        "set_sha256": file_sha256(output),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(dest="command", required=True)
    build = commands.add_parser("build")
    build.add_argument("source", type=Path)
    build.add_argument("signal_root", type=Path)
    build.add_argument("recipe", type=Path)
    build.add_argument("approval", type=Path)
    build.add_argument("output", type=Path)
    aggregate = commands.add_parser("set")
    aggregate.add_argument("manifests", nargs="+", type=Path)
    aggregate.add_argument("--output", required=True, type=Path)
    audit = commands.add_parser("audit")
    audit.add_argument("product", type=Path)
    audit.add_argument("manifest", type=Path)
    return parser


def main(argv: Sequence[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    try:
        result = (
            build_camera_context(
                args.source,
                args.signal_root,
                args.recipe,
                args.approval,
                args.output,
            )
            if args.command == "build"
            else (
                build_set(args.manifests, args.output)
                if args.command == "set"
                else audit_camera_context(args.product, args.manifest)
            )
        )
    except CivError as error:
        print(f"camera-context: {error}", file=sys.stderr)
        raise SystemExit(2) from None
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
