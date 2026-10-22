"""Build private product-bound Cave references from trusted GNSS detection."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

from civ_workshop.artifacts import (
    canonical_json,
    file_sha256,
    interval_from_mapping,
    read_json_file,
    require_mapping,
    require_string,
)
from civ_workshop.detection import detect_events
from civ_workshop.errors import CivError
from civ_workshop.event_spec import load_event_spec
from civ_workshop.label_packs import (
    _product_binding,
    validate_label_pack,
)
from civ_workshop.resources import load_point_resources
from civ_workshop.score_reference import SCORE_REFERENCE_CONTRACT as LABEL_PACK_CONTRACT


@dataclass(frozen=True)
class CaveProductInput:
    product_id: str
    recording_path: Path
    manifest_path: Path | None
    expected_recording_sha256: str | None = None
    expected_manifest_sha256: str | None = None


def _write_json(path: Path, value: object) -> None:
    path.write_text(f"{canonical_json(value)}\n", encoding="utf-8", newline="\n")


def _event_records(
    events_path: Path, source_sha256: str, spec_sha256: str
) -> list[dict[str, object]]:
    labels: list[dict[str, object]] = []
    seen: set[str] = set()
    try:
        lines = events_path.read_text(encoding="utf-8").splitlines()
    except OSError as error:
        raise CivError("trusted Cave detection did not produce an events file") from error
    for index, line in enumerate(lines):
        try:
            raw = json.loads(line)
        except json.JSONDecodeError as error:
            raise CivError(f"Cave detection event {index} is invalid JSON") from error
        event = require_mapping(raw, f"Cave detection event {index}")
        if event.get("contract") != "civ.event/v1":
            raise CivError(f"Cave detection event {index} has an unsupported contract")
        if event.get("bag_sha256") != source_sha256 or event.get("spec_sha256") != spec_sha256:
            raise CivError(f"Cave detection event {index} is not bound to the selected inputs")
        event_id = require_string(event.get("event_id"), f"Cave detection event {index} event_id")
        if event_id in seen:
            raise CivError("Cave detection produced duplicate event identifiers")
        seen.add(event_id)
        interval = interval_from_mapping(event, f"Cave detection event {index}")
        labels.append(
            {
                "end_ns": interval.end_ns,
                "label_id": event_id,
                "start_ns": interval.start_ns,
            }
        )
    return labels


def _failure_status(message: str) -> tuple[str, str]:
    if "EventSpec topics not found in bag" in message:
        return "missing_gnss", "required_gnss_topic_missing"
    return "invalid_gnss", "trusted_detection_rejected_input"


def _generate_one(
    product: CaveProductInput,
    *,
    event_spec_path: Path,
    event_spec_sha256: str,
    location_resource_sha256: str,
    references_directory: Path,
    diagnostics_directory: Path,
) -> dict[str, object]:
    base_record: dict[str, object] = {
        "product_id": product.product_id,
        "event_spec_sha256": event_spec_sha256,
        "location_resource_sha256": location_resource_sha256,
        "human_review": "not_performed",
    }
    if not product.recording_path.is_file():
        return {**base_record, "status": "missing_product"}
    if product.manifest_path is None or not product.manifest_path.is_file():
        return {**base_record, "status": "missing_product_manifest"}

    recording_sha256 = file_sha256(product.recording_path)
    manifest_sha256 = file_sha256(product.manifest_path)
    base_record.update(
        {
            "source_product_sha256": recording_sha256,
            "product_manifest_sha256": manifest_sha256,
        }
    )
    if (
        product.expected_recording_sha256 is not None
        and recording_sha256 != product.expected_recording_sha256
    ) or (
        product.expected_manifest_sha256 is not None
        and manifest_sha256 != product.expected_manifest_sha256
    ):
        return {**base_record, "status": "invalid_product_binding"}
    try:
        binding = _product_binding(
            product.manifest_path,
            permitted_splits=frozenset({"warmup", "development", "sealed"}),
        )
        manifest = read_json_file(product.manifest_path, "Cave data-product manifest")
        partition = require_string(
            require_mapping(manifest.get("provenance"), "product provenance").get("split"),
            "product split",
        )
        if binding.dataset != "reims" or binding.product_sha256 != recording_sha256:
            raise CivError("Cave product is not a bound Reims recording")
    except CivError:
        return {**base_record, "status": "invalid_product_binding"}

    diagnostic_path = diagnostics_directory / product.product_id
    try:
        detect_events(event_spec_path, product.recording_path, diagnostic_path)
    except CivError as error:
        status, failure_code = _failure_status(str(error))
        return {
            **base_record,
            "partition": partition,
            "status": status,
            "failure_code": failure_code,
        }

    run_manifest = read_json_file(diagnostic_path / "run-manifest.json", "Cave detection manifest")
    source = require_mapping(run_manifest.get("source"), "Cave run-manifest source")
    spec = require_mapping(run_manifest.get("spec"), "Cave run-manifest EventSpec")
    if source.get("sha256") != recording_sha256 or spec.get("sha256") != event_spec_sha256:
        raise CivError("Cave detection manifest does not bind the selected product and EventSpec")
    resource_records = run_manifest.get("resources")
    if not isinstance(resource_records, list) or not any(
        isinstance(item, dict) and item.get("sha256") == location_resource_sha256
        for item in resource_records
    ):
        raise CivError("Cave detection manifest does not bind the selected location resource")

    events_path = diagnostic_path / "events.jsonl"
    labels = _event_records(events_path, recording_sha256, event_spec_sha256)
    label_pack = validate_label_pack(
        {
            "contract": LABEL_PACK_CONTRACT,
            "data_gaps": [],
            "dataset": "reims",
            "labels": labels,
            "source_sha256": recording_sha256,
        }
    )
    reference_path = references_directory / f"{product.product_id}.json"
    _write_json(reference_path, label_pack)
    label_pack_sha256 = file_sha256(reference_path)
    return {
        **base_record,
        "partition": partition,
        "status": "generated" if labels else "generated_zero_encounter",
        "event_count": len(labels),
        "detection_events_sha256": file_sha256(events_path),
        "generated_labels_sha256": label_pack_sha256,
        "reference_path": reference_path.relative_to(references_directory.parent).as_posix(),
    }


def generate_cave_references(
    products: list[CaveProductInput],
    *,
    event_spec_path: Path,
    location_resource_path: Path,
    output_directory: Path,
) -> dict[str, object]:
    """Run the supplied Cave EventSpec and write organizer-only references outside Git."""
    if not products:
        raise CivError("Cave reference generation requires at least one assigned product")
    if len({product.product_id for product in products}) != len(products):
        raise CivError("Cave reference generation contains duplicate product IDs")
    repository_root = Path(__file__).resolve().parents[3]
    resolved_output = output_directory.resolve()
    if resolved_output.is_relative_to(repository_root):
        raise CivError("private Cave reference output must be outside the repository")
    if output_directory.exists():
        raise CivError(f"private Cave reference output already exists: {output_directory}")
    if not event_spec_path.is_file() or not location_resource_path.is_file():
        raise CivError("Cave EventSpec and point resource must exist")

    event_spec = load_event_spec(event_spec_path)
    latitude = event_spec.signals.get("latitude")
    longitude = event_spec.signals.get("longitude")
    if (
        latitude is None
        or longitude is None
        or latitude.topic != "/fix"
        or latitude.field != "latitude"
        or longitude.topic != "/fix"
        or longitude.field != "longitude"
    ):
        raise CivError("Cave EventSpec must bind latitude and longitude from /fix")
    point_resources = load_point_resources(event_spec_path, event_spec.resources)
    event_spec_sha256 = file_sha256(event_spec_path)
    location_resource_sha256 = file_sha256(location_resource_path)
    if not any(item.sha256 == location_resource_sha256 for item in point_resources.values()):
        raise CivError("Cave EventSpec does not bind the supplied location resource")

    references_directory = output_directory / "references"
    diagnostics_directory = output_directory / "diagnostics"
    references_directory.mkdir(parents=True)
    diagnostics_directory.mkdir()
    products_records = [
        _generate_one(
            product,
            event_spec_path=event_spec_path,
            event_spec_sha256=event_spec_sha256,
            location_resource_sha256=location_resource_sha256,
            references_directory=references_directory,
            diagnostics_directory=diagnostics_directory,
        )
        for product in products
    ]
    index = {
        "contract": "civ.organizer-cave-reference-set/v1alpha1",
        "event_spec_sha256": event_spec_sha256,
        "location_resource_sha256": location_resource_sha256,
        "products": products_records,
        "target": "Cave encounters derived from recorded Reims /fix GNSS",
    }
    index_path = output_directory / "generation-index.json"
    _write_json(index_path, index)
    statuses = [str(item["status"]) for item in products_records]
    return {
        "product_count": len(products_records),
        "generated_count": sum(
            status in {"generated", "generated_zero_encounter"} for status in statuses
        ),
        "zero_encounter_count": statuses.count("generated_zero_encounter"),
        "missing_gnss_count": statuses.count("missing_gnss"),
        "invalid_gnss_count": statuses.count("invalid_gnss"),
        "invalid_product_count": sum(
            status in {"missing_product", "missing_product_manifest", "invalid_product_binding"}
            for status in statuses
        ),
        "index_sha256": file_sha256(index_path),
        "index_path": str(index_path),
    }


def _resolve_plan_path(plan_path: Path, value: object, context: str) -> Path:
    text = require_string(value, context)
    path = Path(text)
    return path.resolve() if path.is_absolute() else (plan_path.parent / path).resolve()


def _manifest_for_product(
    recording_path: Path, recording_sha256: str
) -> Path | None:
    matches: list[Path] = []
    for candidate in recording_path.parent.glob("*.manifest.json"):
        try:
            manifest = read_json_file(candidate, "data-product manifest")
            product = require_mapping(manifest.get("product"), "data-product manifest product")
        except CivError:
            continue
        if (
            product.get("name") == recording_path.name
            and product.get("sha256") == recording_sha256
        ):
            matches.append(candidate)
    return matches[0] if len(matches) == 1 else None


def _plan_products(plan_path: Path, track_id: str) -> list[CaveProductInput]:
    plan = read_json_file(plan_path, "evaluation plan")
    tracks = plan.get("tracks")
    if isinstance(tracks, list):
        selected = next(
            (
                item
                for item in tracks
                if isinstance(item, dict) and item.get("track_id") == track_id
            ),
            None,
        )
    else:
        track_map = require_mapping(tracks, "evaluation plan tracks")
        selected = track_map.get(track_id)
    track = require_mapping(selected, f"evaluation plan track {track_id}")
    products = track.get("products")
    if not isinstance(products, list) or not products:
        raise CivError(f"evaluation plan track {track_id} has no assigned products")

    result: list[CaveProductInput] = []
    for index, raw in enumerate(products):
        product = require_mapping(raw, f"evaluation plan product {index}")
        product_id_value = product.get("product_id")
        recording = require_mapping(product.get("recording"), "evaluation plan recording")
        recording_path = _resolve_plan_path(
            plan_path, recording.get("path"), "evaluation plan recording path"
        )
        product_id = (
            require_string(product_id_value, "evaluation plan product_id")
            if product_id_value is not None
            else recording_path.stem.removesuffix("-signals")
        )
        if re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,99}", product_id) is None:
            raise CivError(f"evaluation plan product {index} has an unsafe product ID")
        recording_sha256 = require_string(
            recording.get("sha256"), "evaluation plan recording sha256"
        )
        manifest_value = product.get("manifest")
        manifest_path: Path | None
        if isinstance(manifest_value, dict):
            manifest_path = _resolve_plan_path(
                plan_path, manifest_value.get("path"), "evaluation plan manifest path"
            )
            expected_manifest_sha256 = require_string(
                manifest_value.get("sha256"), "evaluation plan manifest sha256"
            )
        else:
            manifest_path = _manifest_for_product(recording_path, recording_sha256)
            expected_manifest_sha256 = None
        result.append(
            CaveProductInput(
                product_id=product_id,
                recording_path=recording_path,
                manifest_path=manifest_path,
                expected_recording_sha256=recording_sha256,
                expected_manifest_sha256=expected_manifest_sha256,
            )
        )
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m civ_workshop.organizer.cave_references",
        description="Generate private Cave references from an assigned product track",
    )
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--track", required=True)
    parser.add_argument("--event-spec", type=Path, required=True)
    parser.add_argument("--locations", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    try:
        summary = generate_cave_references(
            _plan_products(args.plan, args.track),
            event_spec_path=args.event_spec,
            location_resource_path=args.locations,
            output_directory=args.output,
        )
        print(json.dumps(summary, sort_keys=True, separators=(",", ":")))
    except CivError as error:
        print(f"cave-references: {error}", file=sys.stderr)
        raise SystemExit(2) from None


if __name__ == "__main__":
    main()
