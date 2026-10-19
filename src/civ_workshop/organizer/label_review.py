from __future__ import annotations

import argparse
import copy
import json
import math
import os
import secrets
import shutil
import sys
import tempfile
import webbrowser
from collections.abc import Mapping, Sequence
from contextlib import suppress
from dataclasses import dataclass
from hashlib import sha256
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any, cast
from urllib.parse import parse_qs, urlsplit

from mcap.exceptions import McapError
from mcap.reader import make_reader

from civ_workshop.artifacts import (
    canonical_json,
    file_sha256,
    read_events,
    read_json_file,
    require_mapping,
    require_string,
)
from civ_workshop.camera_context import audit_camera_context
from civ_workshop.errors import CivError
from civ_workshop.event_spec import load_event_spec
from civ_workshop.inspection import MessageDecoder, extract_field
from civ_workshop.label_packs import (
    _product_binding,
    _truth_document,
    validate_label_pack,
)
from civ_workshop.models import SignalBinding
from civ_workshop.organizer.label_catalog import add_catalog_command, catalog_command
from civ_workshop.organizer.label_profiles import ProfileComparisons, load_profile_comparisons
from civ_workshop.resources import load_point_resources
from civ_workshop.score_reference import SCORING_POLICY, validate_score_reference

PROGRESS_FORMAT = "civ.label-review-progress/v1"
ARCHIVE_FORMAT = "civ.label-review-archive/v1"
TRUTH_FORMAT = "civ.phase3.source-relative-truth/v1"
EVENT_CONTRACT = "civ.event/v1"
MAX_SIGNAL_POINTS = 500
MAX_FRAME_BYTES = 12 * 1024 * 1024


@dataclass(frozen=True)
class Frame:
    index: int
    timestamp_ns: int


@dataclass(frozen=True)
class CameraFrames:
    product_path: Path
    product_sha256: str
    topic: str
    frames: tuple[Frame, ...]


@dataclass(frozen=True)
class ReviewBinding:
    source_path: Path
    spec_path: Path
    events_path: Path
    manifest_path: Path
    progress_path: Path
    camera_manifest_path: Path | None
    source_bounds: tuple[int, int]
    identity: dict[str, object]
    evidence_by_id: dict[str, dict[str, object]]
    camera_frames: CameraFrames | None
    practice_output: Path | None
    truth_output: Path | None
    spec_name: str
    event_ids: frozenset[str]
    signal_product_manifest_path: Path | None = None


def _nonnegative_ns(value: object, context: str) -> int:
    if isinstance(value, bool):
        raise CivError(f"{context} must be a non-negative integer nanosecond value")
    if isinstance(value, int):
        result = value
    elif isinstance(value, str) and value.isascii() and value.isdigit():
        result = int(value)
    else:
        raise CivError(f"{context} must be a non-negative integer nanosecond value")
    if result < 0:
        raise CivError(f"{context} must be a non-negative integer nanosecond value")
    return result


def _source_window(request: Mapping[str, object], bounds: tuple[int, int]) -> tuple[int, int]:
    start_ns = _nonnegative_ns(request.get("start_ns"), "window start_ns")
    end_ns = _nonnegative_ns(request.get("end_ns"), "window end_ns")
    if not bounds[0] <= start_ns < end_ns <= bounds[1]:
        raise CivError("evidence window must be a positive interval inside source bounds")
    return start_ns, end_ns


def _required_reason(value: object, context: str) -> str:
    reason = require_string(value, context)
    if not reason.strip():
        raise CivError(f"{context} is required")
    return reason.strip()


def _read_source_bounds(path: Path) -> tuple[int, int]:
    if not path.is_file():
        raise CivError(f"source recording does not exist: {path}")
    try:
        with path.open("rb") as stream:
            reader = make_reader(stream, validate_crcs=True)
            summary = reader.get_summary()
            if summary is not None and summary.statistics is not None:
                statistics = summary.statistics
                return statistics.message_start_time, statistics.message_end_time
            first: int | None = None
            last: int | None = None
            for _, _, message in reader.iter_messages():
                first = message.log_time if first is None else min(first, message.log_time)
                last = message.log_time if last is None else max(last, message.log_time)
    except (OSError, McapError) as error:
        raise CivError(f"cannot inspect source recording: {error}") from error
    if first is None or last is None:
        raise CivError("source recording contains no messages")
    return first, last


def _window(start_ns: int, end_ns: int, before_ns: int, after_ns: int) -> tuple[int, int]:
    return max(0, start_ns - before_ns), end_ns + after_ns


def _json_signal_value(value: object) -> object:
    if isinstance(value, bool):
        return 1.0 if value else 0.0
    if isinstance(value, (int, float)):
        number = float(value)
        if math.isfinite(number):
            return number
    if isinstance(value, str):
        return value[:160]
    return str(value)[:160]


def _decimate(samples: list[dict[str, object]]) -> list[dict[str, object]]:
    if len(samples) <= MAX_SIGNAL_POINTS:
        return samples
    return [
        samples[(index * (len(samples) - 1)) // (MAX_SIGNAL_POINTS - 1)]
        for index in range(MAX_SIGNAL_POINTS)
    ]


def _collect_signals(
    source_path: Path,
    bindings: Mapping[str, object],
    windows: Mapping[str, tuple[int, int]],
) -> dict[str, dict[str, list[dict[str, object]]]]:
    if not windows:
        return {}
    signal_bindings: dict[str, tuple[str, str]] = {}
    by_topic: dict[str, list[tuple[str, str]]] = {}
    for name, raw_binding in bindings.items():
        if isinstance(raw_binding, SignalBinding):
            topic = raw_binding.topic
            field = raw_binding.field
        else:
            binding = require_mapping(raw_binding, f"signal {name}")
            topic = require_string(binding.get("topic"), f"signal {name} topic")
            field = require_string(binding.get("field"), f"signal {name} field")
        signal_bindings[name] = (topic, field)
        by_topic.setdefault(topic, []).append((name, field))

    samples: dict[str, dict[str, list[dict[str, object]]]] = {
        candidate_id: {name: [] for name in signal_bindings} for candidate_id in windows
    }
    decoder = MessageDecoder()
    try:
        for topic, signal_fields in sorted(by_topic.items()):
            with source_path.open("rb") as stream:
                reader = make_reader(stream, validate_crcs=True)
                for schema, channel, message in reader.iter_messages(
                    topics=[topic],
                    start_time=min(window[0] for window in windows.values()),
                    end_time=max(window[1] for window in windows.values()) + 1,
                ):
                    matching = [
                        candidate_id
                        for candidate_id, (start_ns, end_ns) in windows.items()
                        if start_ns <= message.log_time <= end_ns
                    ]
                    if not matching:
                        continue
                    payload = decoder.decode(schema, channel, message.data)
                    for name, field in signal_fields:
                        value = _json_signal_value(extract_field(payload, field, f"topic {topic}"))
                        for candidate_id in matching:
                            samples[candidate_id][name].append(
                                {"timestamp_ns": str(message.log_time), "value": value}
                            )
    except (OSError, McapError) as error:
        raise CivError(f"cannot read source signals: {error}") from error

    return {
        candidate_id: {name: _decimate(points) for name, points in candidate_signals.items()}
        for candidate_id, candidate_signals in samples.items()
    }


def _advance_geometry_revision(state: dict[str, object]) -> None:
    revision = state.get("geometry_revision")
    if isinstance(revision, bool) or not isinstance(revision, int) or revision < 0:
        raise CivError("review geometry revision is invalid")
    state["geometry_revision"] = revision + 1
    state["checked_windows"] = []


def _invalidate_coverage(state: dict[str, object]) -> None:
    state["coverage_reviewed"] = False
    state["coverage_revision"] = -1
    state["coverage_reviewer"] = None


def _camera_frames(
    manifest_path: Path,
    *,
    source_sha256: str,
    source_id: str,
    dataset: str,
    signal_product_manifest_path: Path | None = None,
) -> CameraFrames:
    manifest = read_json_file(manifest_path, "camera-context manifest")
    if manifest.get("contract") != "civ.camera-context-manifest/v1":
        raise CivError("camera-context manifest has the wrong contract")
    parent = require_mapping(manifest.get("parent"), "camera-context source")
    if signal_product_manifest_path is not None:
        signal_binding = _product_binding(
            signal_product_manifest_path, permitted_splits=frozenset({"warmup", "development"})
        )
        signal = require_mapping(manifest.get("signal_product"), "camera-context signal product")
        signal_manifest = read_json_file(signal_product_manifest_path, "signal-product manifest")
        provenance = require_mapping(signal_manifest.get("provenance"), "signal provenance")
        if (
            signal_binding.product_sha256 != source_sha256
            or signal_binding.product_sha256 != signal.get("sha256")
            or signal_binding.product_name != signal.get("name")
            or signal_product_manifest_path.name != signal.get("manifest")
            or signal_binding.manifest_sha256 != signal.get("manifest_sha256")
            or signal_binding.source_sha256 != parent.get("sha256")
            or signal_binding.source_id != parent.get("id")
            or signal_binding.source_id != source_id
            or signal_binding.dataset != dataset
            or provenance.get("split") != manifest.get("split")
        ):
            raise CivError("camera-context signal-product identity does not match this review")
    elif parent.get("sha256") != source_sha256 or parent.get("id") != source_id:
        raise CivError("camera-context source identity does not match this review")
    if manifest.get("dataset") != dataset or manifest.get("split") == "sealed":
        raise CivError("camera-context dataset or split does not permit this review")

    approval = require_mapping(manifest.get("approval"), "camera-context approval")
    approval_fields = (
        "id",
        "authority",
        "rights_statement",
        "frame_review_set_sha256",
        "document_sha256",
    )
    for field in approval_fields:
        require_string(approval.get(field), f"camera-context approval {field}")
    product = require_mapping(manifest.get("product"), "camera-context product")
    product_name = require_string(product.get("name"), "camera-context product name")
    if Path(product_name).name != product_name:
        raise CivError("camera-context product name must be a basename")
    product_path = manifest_path.parent / product_name
    audit_camera_context(product_path, manifest_path)
    topic_records = product.get("topics")
    if not isinstance(topic_records, list):
        raise CivError("camera-context product topics must be a list")
    image_topics: list[str] = []
    for raw in topic_records:
        topic_record = require_mapping(raw, "camera-context topic")
        topic = require_string(topic_record.get("topic"), "camera-context topic")
        if topic.endswith("/compressed"):
            image_topics.append(topic)
    if len(image_topics) != 1:
        raise CivError("camera-context must contain exactly one approved compressed image topic")

    frames: list[Frame] = []
    try:
        with product_path.open("rb") as stream:
            reader = make_reader(stream, validate_crcs=True)
            for _, _, message in reader.iter_messages(topics=image_topics):
                frames.append(Frame(index=len(frames), timestamp_ns=message.log_time))
    except (OSError, McapError) as error:
        raise CivError(f"cannot read approved camera context: {error}") from error
    return CameraFrames(
        product_path=product_path,
        product_sha256=file_sha256(product_path),
        topic=image_topics[0],
        frames=tuple(frames),
    )


def _camera_frame_bytes(camera: CameraFrames, index: int) -> tuple[str, bytes]:
    if index < 0 or index >= len(camera.frames):
        raise CivError("camera-context frame index is out of range")
    decoder = MessageDecoder()
    try:
        with camera.product_path.open("rb") as stream:
            reader = make_reader(stream, validate_crcs=True)
            for frame_index, (schema, channel, message) in enumerate(
                reader.iter_messages(topics=[camera.topic])
            ):
                if frame_index != index:
                    continue
                decoded = decoder.decode(schema, channel, message.data)
                image_format = str(extract_field(decoded, "format", "camera context")).lower()
                raw = extract_field(decoded, "data", "camera context")
                if isinstance(raw, bytes):
                    data = raw
                elif isinstance(raw, (bytearray, list)):
                    data = bytes(raw)
                elif hasattr(raw, "tobytes"):
                    data = raw.tobytes()
                else:
                    raise CivError("camera-context image data has an unsupported representation")
                if len(data) > MAX_FRAME_BYTES:
                    raise CivError("camera-context image exceeds the local display size limit")
                if "jpeg" in image_format or "jpg" in image_format:
                    return "image/jpeg", data
                if "png" in image_format:
                    return "image/png", data
                raise CivError("camera-context image format is not supported for display")
    except (OSError, McapError) as error:
        raise CivError(f"cannot decode approved camera context: {error}") from error
    raise CivError("camera-context frame is unavailable")


def _candidate_context(
    candidate_id: str,
    start_ns: int,
    end_ns: int,
    signals: Mapping[str, list[dict[str, object]]],
    camera: CameraFrames | None,
    before_ns: int,
    after_ns: int,
) -> dict[str, object]:
    window_start, window_end = _window(start_ns, end_ns, before_ns, after_ns)
    frames = []
    if camera is not None:
        all_frames = [
            {"index": frame.index, "timestamp_ns": str(frame.timestamp_ns)}
            for frame in camera.frames
            if window_start <= frame.timestamp_ns <= window_end
        ]
        if len(all_frames) > 80:
            frames = [
                all_frames[(index * (len(all_frames) - 1)) // 79]
                for index in range(80)
            ]
        else:
            frames = all_frames
    missing: list[str] = []
    if camera is None:
        missing.append("No rights-approved camera context was supplied.")
    elif not frames:
        missing.append("No approved camera frames overlap this interval.")
    if not any(points for points in signals.values()):
        missing.append("No configured signal samples overlap this interval.")
    return {
        "camera_frames": frames,
        "end_ns": str(end_ns),
        "missing_context": missing,
        "status": "available" if not missing else "missing",
        "start_ns": str(start_ns),
        "signals": dict(signals),
    }


def _identity_for_inputs(
    source_path: Path,
    spec_path: Path,
    events_path: Path,
    manifest_path: Path,
    dataset: str,
    source_id: str,
    camera_manifest_path: Path | None,
    signal_product_manifest_path: Path | None = None,
) -> tuple[ReviewBinding, list[Any], dict[str, Any], CameraFrames | None, int, int]:
    source_path = source_path.resolve()
    spec_path = spec_path.resolve()
    events_path = events_path.resolve()
    manifest_path = manifest_path.resolve()
    if dataset not in {"kashiwa", "reims"}:
        raise CivError("dataset must be kashiwa or reims")
    source_id = require_string(source_id, "source id")
    source_hash = file_sha256(source_path)
    spec_hash = file_sha256(spec_path)
    events_hash = file_sha256(events_path)
    manifest_hash = file_sha256(manifest_path)
    spec = load_event_spec(spec_path)
    resources = load_point_resources(spec_path, spec.resources)
    resource_records = [resource.provenance() for _, resource in sorted(resources.items())]
    resource_hash = sha256(canonical_json(resource_records).encode("utf-8")).hexdigest()

    manifest = read_json_file(manifest_path, "run manifest")
    if manifest.get("contract") != "civ.run-manifest/v2":
        raise CivError("label review requires a stable civ.run-manifest/v2")
    source_record = require_mapping(manifest.get("source"), "run manifest source")
    spec_record = require_mapping(manifest.get("spec"), "run manifest EventSpec")
    events_record = require_mapping(manifest.get("events"), "run manifest events")
    if source_record.get("sha256") != source_hash:
        raise CivError("source recording SHA-256 does not match the detected events")
    if spec_record.get("sha256") != spec_hash or spec_record.get("contract") != spec.contract:
        raise CivError("EventSpec identity does not match the detected events")
    if events_record.get("sha256") != events_hash:
        raise CivError("events file does not match the run manifest")
    if manifest.get("resources", []) != resource_records:
        raise CivError("EventSpec resources do not match the run manifest")

    events = read_events(events_path)
    if events_record.get("count") != len(events):
        raise CivError("events file count does not match the run manifest")
    event_ids: set[str] = set()
    for event in events:
        if event.contract != EVENT_CONTRACT:
            raise CivError("label review requires stable civ.event/v1 records")
        if event.event_id in event_ids:
            raise CivError("events file contains duplicate event IDs")
        event_ids.add(event.event_id)
        if event.bag_sha256 != source_hash:
            raise CivError(f"source mismatch for candidate {event.event_id}")
        if event.spec_sha256 != spec_hash:
            raise CivError(f"EventSpec mismatch for candidate {event.event_id}")

    source_bounds = _read_source_bounds(source_path)
    for event in events:
        if not (
            source_bounds[0] <= event.interval.start_ns < event.interval.end_ns <= source_bounds[1]
        ):
            raise CivError(f"candidate interval is outside source bounds: {event.event_id}")

    signal_product_manifest_path = (
        signal_product_manifest_path.resolve() if signal_product_manifest_path else None
    )
    if signal_product_manifest_path is not None and camera_manifest_path is None:
        raise CivError("a signal-product manifest requires approved camera context")
    camera_manifest_path = camera_manifest_path.resolve() if camera_manifest_path else None
    camera: CameraFrames | None = None
    camera_manifest_hash: str | None = None
    if camera_manifest_path is not None:
        camera = _camera_frames(
            camera_manifest_path,
            source_sha256=source_hash,
            source_id=source_id,
            dataset=dataset,
            signal_product_manifest_path=signal_product_manifest_path,
        )
        camera_manifest_hash = file_sha256(camera_manifest_path)

    evidence_windows = {
        event.event_id: _window(
            event.interval.start_ns,
            event.interval.end_ns,
            spec.evidence_before_ns,
            spec.evidence_after_ns,
        )
        for event in events
    }
    signal_data = _collect_signals(source_path, spec.signals, evidence_windows)
    evidence_by_id = {
        event.event_id: _candidate_context(
            event.event_id,
            event.interval.start_ns,
            event.interval.end_ns,
            signal_data[event.event_id],
            camera,
            spec.evidence_before_ns,
            spec.evidence_after_ns,
        )
        for event in events
    }
    identity: dict[str, object] = {
        "camera_context_manifest_sha256": camera_manifest_hash,
        "camera_context_product_sha256": camera.product_sha256 if camera else None,
        "dataset": dataset,
        "events_sha256": events_hash,
        "manifest_sha256": manifest_hash,
        "resource_set_sha256": resource_hash,
        "source_id": source_id,
        "source_sha256": source_hash,
        "source_start_ns": str(source_bounds[0]),
        "source_end_ns": str(source_bounds[1]),
        "spec_sha256": spec_hash,
    }
    if signal_product_manifest_path is not None:
        identity["signal_product_manifest_sha256"] = file_sha256(signal_product_manifest_path)
    binding = ReviewBinding(
        source_path=source_path,
        spec_path=spec_path,
        events_path=events_path,
        manifest_path=manifest_path,
        progress_path=Path(),
        camera_manifest_path=camera_manifest_path,
        source_bounds=source_bounds,
        identity=identity,
        evidence_by_id=evidence_by_id,
        camera_frames=camera,
        practice_output=None,
        truth_output=None,
        spec_name=spec.name,
        event_ids=frozenset(event_ids),
        signal_product_manifest_path=signal_product_manifest_path,
    )
    return binding, events, manifest, camera, spec.evidence_before_ns, spec.evidence_after_ns


def initial_review_state(
    binding: ReviewBinding,
    events: Sequence[Any],
    evidence_by_id: Mapping[str, Mapping[str, object]],
) -> dict[str, object]:
    candidates: list[dict[str, object]] = []
    for event in events:
        evidence = evidence_by_id[event.event_id]
        missing_context = evidence.get("missing_context")
        if not isinstance(missing_context, list) or not all(
            isinstance(item, str) for item in missing_context
        ):
            raise CivError("review evidence missing_context is invalid")
        candidates.append(
            {
                "adjustment_history": [],
                "context_status": evidence["status"],
                "decision": "pending",
                "event_id": event.event_id,
                "exclusion_kind": None,
                "id": event.event_id,
                "kind": "detected",
                "missing_context": list(cast(list[str], missing_context)),
                "practice_selected": False,
                "reason": "",
                "reviewer": None,
                "start_ns": str(event.interval.start_ns),
                "end_ns": str(event.interval.end_ns),
                "uncertainty_disposition": "unresolved",
                "uncertainty_reason": "",
            }
        )
    return {
        "audit": [],
        "candidates": candidates,
        "checked_windows": [],
        "coverage_revision": -1,
        "coverage_reviewed": False,
        "coverage_reviewer": None,
        "exports": {},
        "format": PROGRESS_FORMAT,
        "geometry_revision": 0,
        "identity": dict(binding.identity),
        "reviewer": "",
        "revision": 0,
        "output_paths": _configured_output_paths(binding),
    }


def _configured_output_paths(binding: ReviewBinding) -> dict[str, str]:
    paths: dict[str, str] = {}
    if binding.practice_output is not None:
        paths["practice"] = str(binding.practice_output)
    if binding.truth_output is not None:
        paths["organizer-private"] = str(binding.truth_output)
    return paths


def _candidate(state: dict[str, object], candidate_id: object) -> dict[str, object]:
    identifier = require_string(candidate_id, "candidate id")
    candidates = state.get("candidates")
    if not isinstance(candidates, list):
        raise CivError("review candidates must be a list")
    for item in candidates:
        if isinstance(item, dict) and item.get("id") == identifier:
            return cast(dict[str, object], item)
    raise CivError(f"review candidate does not exist: {identifier}")


def _reviewer(state: dict[str, object]) -> str:
    return require_string(state.get("reviewer"), "reviewer name")


def _audit(state: dict[str, object], record: Mapping[str, object]) -> None:
    audit = state.get("audit")
    if not isinstance(audit, list):
        raise CivError("review audit must be a list")
    audit.append(dict(record))
    revision = state.get("revision")
    if isinstance(revision, bool) or not isinstance(revision, int):
        raise CivError("review revision must be an integer")
    state["revision"] = revision + 1


def transition_review(
    current: Mapping[str, object],
    action: Mapping[str, object],
    source_bounds: tuple[int, int],
) -> dict[str, object]:
    state = copy.deepcopy(dict(current))
    action_type = require_string(action.get("type"), "review action type")
    if action_type == "set-reviewer":
        reviewer = require_string(action.get("name"), "reviewer name")
        state["reviewer"] = reviewer
        _audit(state, {"action": action_type, "reviewer": reviewer})
        return state

    if action_type == "check-window":
        start_ns, end_ns = _source_window(action, source_bounds)
        reviewer = _reviewer(state)
        windows = state.setdefault("checked_windows", [])
        if not isinstance(windows, list):
            raise CivError("checked windows must be a list")
        record = {"start_ns": str(start_ns), "end_ns": str(end_ns), "reviewer": reviewer}
        if record not in windows:
            windows.append(record)
        _audit(state, {"action": action_type, **record})
        return state

    if action_type == "signoff":
        checked = action.get("checked")
        if not isinstance(checked, bool):
            raise CivError("missed-event signoff must be checked or unchecked")
        reviewer = _reviewer(state)
        state["coverage_reviewed"] = checked
        state["coverage_revision"] = state.get("geometry_revision") if checked else -1
        state["coverage_reviewer"] = reviewer if checked else None
        _audit(state, {"action": action_type, "checked": checked, "reviewer": reviewer})
        return state

    if action_type == "add-missed":
        reviewer = _reviewer(state)
        start_ns = _nonnegative_ns(action.get("start_ns"), "missed-event start_ns")
        end_ns = _nonnegative_ns(action.get("end_ns"), "missed-event end_ns")
        if not source_bounds[0] <= start_ns < end_ns <= source_bounds[1]:
            raise CivError("missed event must be a positive interval inside source bounds")
        reason = _required_reason(action.get("reason"), "missed-event evidence note")
        raw_candidates = state.get("candidates")
        if not isinstance(raw_candidates, list):
            raise CivError("review candidates must be a list")
        number = 1
        existing_ids = {str(item.get("id")) for item in raw_candidates if isinstance(item, dict)}
        while f"missed-{number:04d}" in existing_ids:
            number += 1
        identifier = f"missed-{number:04d}"
        raw_candidates.append(
            {
                "adjustment_history": [],
                "context_status": "missing",
                "decision": "pending",
                "event_id": None,
                "exclusion_kind": None,
                "id": identifier,
                "kind": "missed",
                "missing_context": ["Signal and camera context is refreshed for this interval."],
                "practice_selected": False,
                "reason": "",
                "reviewer": None,
                "start_ns": str(start_ns),
                "end_ns": str(end_ns),
                "uncertainty_disposition": "unresolved",
                "uncertainty_reason": "",
            }
        )
        _advance_geometry_revision(state)
        _invalidate_coverage(state)
        _audit(
            state,
            {
                "action": action_type,
                "candidate_id": identifier,
                "reason": reason,
                "reviewer": reviewer,
                "start_ns": str(start_ns),
                "end_ns": str(end_ns),
            },
        )
        return state

    candidate = _candidate(state, action.get("candidate_id"))
    candidate_id = str(candidate["id"])
    reviewer = _reviewer(state)
    was_accepted = candidate.get("decision") == "approved"

    if action_type == "edit":
        start_ns = _nonnegative_ns(action.get("start_ns"), "start_ns")
        end_ns = _nonnegative_ns(action.get("end_ns"), "end_ns")
        if not source_bounds[0] <= start_ns < end_ns <= source_bounds[1]:
            raise CivError("edited interval must be a positive interval inside source bounds")
        reason = _required_reason(action.get("reason"), "adjustment reason")
        adjustments = candidate.get("adjustment_history")
        if not isinstance(adjustments, list):
            raise CivError("adjustment history must be a list")
        adjustments.append(
            {
                "end_ns": str(candidate["end_ns"]),
                "new_end_ns": str(end_ns),
                "new_start_ns": str(start_ns),
                "reason": reason,
                "reviewer": reviewer,
                "start_ns": str(candidate["start_ns"]),
            }
        )
        candidate.update(
            {
                "decision": "pending",
                "end_ns": str(end_ns),
                "exclusion_kind": None,
                "practice_selected": False,
                "reason": "",
                "reviewer": None,
                "start_ns": str(start_ns),
                "uncertainty_disposition": "unresolved",
                "uncertainty_reason": "",
            }
        )
        _advance_geometry_revision(state)
        _invalidate_coverage(state)
        _audit(
            state,
            {
                "action": action_type,
                "candidate_id": candidate_id,
                "reason": reason,
                "reviewer": reviewer,
                "start_ns": str(start_ns),
                "end_ns": str(end_ns),
            },
        )
        return state

    if action_type == "approve":
        disposition = require_string(
            action.get("uncertainty_disposition"), "uncertainty disposition"
        )
        if disposition not in {"clear", "accept_event"}:
            raise CivError("approval requires clear or accept_event uncertainty disposition")
        if candidate.get("context_status") == "missing" and disposition == "clear":
            raise CivError("missing context cannot be marked clear; record an explicit disposition")
        uncertainty_reason = ""
        if disposition == "accept_event":
            uncertainty_reason = _required_reason(
                action.get("uncertainty_reason"), "uncertainty reason"
            )
        candidate.update(
            {
                "decision": "approved",
                "exclusion_kind": None,
                "practice_selected": False,
                "reason": "",
                "reviewer": reviewer,
                "uncertainty_disposition": disposition,
                "uncertainty_reason": uncertainty_reason,
            }
        )
        if was_accepted != (candidate.get("decision") == "approved"):
            _invalidate_coverage(state)
        _audit(
            state,
            {
                "action": action_type,
                "candidate_id": candidate_id,
                "reviewer": reviewer,
                "uncertainty_disposition": disposition,
                "uncertainty_reason": uncertainty_reason,
            },
        )
        return state

    if action_type == "reject":
        reason = _required_reason(action.get("reason"), "rejection reason")
        disposition = require_string(
            action.get("uncertainty_disposition"), "uncertainty disposition"
        )
        if disposition != "reject_candidate":
            raise CivError("rejection requires the explicit reject_candidate disposition")
        candidate.update(
            {
                "decision": "rejected",
                "exclusion_kind": None,
                "practice_selected": False,
                "reason": reason,
                "reviewer": reviewer,
                "uncertainty_disposition": disposition,
                "uncertainty_reason": reason,
            }
        )
        if was_accepted != (candidate.get("decision") == "approved"):
            _invalidate_coverage(state)
        _audit(
            state,
            {
                "action": action_type,
                "candidate_id": candidate_id,
                "reason": reason,
                "reviewer": reviewer,
                "uncertainty_disposition": disposition,
            },
        )
        return state

    if action_type == "data-gap":
        reason = _required_reason(action.get("reason"), "data-gap reason")
        exclusion_kind = require_string(action.get("exclusion_kind"), "exclusion kind")
        if exclusion_kind != "scoring_data_gap":
            raise CivError(f"unsupported exclusion kind '{exclusion_kind}'")
        disposition = require_string(
            action.get("uncertainty_disposition"), "uncertainty disposition"
        )
        if disposition != "scoring_data_gap":
            raise CivError("data-gap exclusion requires scoring_data_gap disposition")
        candidate.update(
            {
                "decision": "data_gap",
                "exclusion_kind": exclusion_kind,
                "practice_selected": False,
                "reason": reason,
                "reviewer": reviewer,
                "uncertainty_disposition": disposition,
                "uncertainty_reason": reason,
            }
        )
        if was_accepted != (candidate.get("decision") == "approved"):
            _invalidate_coverage(state)
        _audit(
            state,
            {
                "action": action_type,
                "candidate_id": candidate_id,
                "exclusion_kind": exclusion_kind,
                "reason": reason,
                "reviewer": reviewer,
            },
        )
        return state

    if action_type == "set-practice":
        selected = action.get("selected")
        if not isinstance(selected, bool):
            raise CivError("practice selection must be true or false")
        if selected and candidate.get("decision") not in {"approved", "data_gap"}:
            raise CivError("only approved events or supported data gaps can enter practice output")
        candidate["practice_selected"] = selected
        _audit(
            state,
            {
                "action": action_type,
                "candidate_id": candidate_id,
                "reviewer": reviewer,
                "selected": selected,
            },
        )
        return state

    raise CivError(f"unsupported review action '{action_type}'")


def gate_review(state: Mapping[str, object]) -> list[str]:
    reasons: list[str] = []
    try:
        _reviewer(dict(state))
    except CivError:
        reasons.append("Name the reviewer.")
    if state.get("coverage_reviewed") is not True or state.get("coverage_revision") != state.get(
        "geometry_revision"
    ):
        reasons.append("Sign off the missed-event review after the last interval change.")
    candidates = state.get("candidates")
    if not isinstance(candidates, list):
        return reasons + ["Review candidates are invalid."]
    for raw in candidates:
        if not isinstance(raw, dict):
            reasons.append("Review candidate is invalid.")
            continue
        candidate = cast(dict[str, object], raw)
        identifier = str(candidate.get("id", "unknown"))
        decision = candidate.get("decision")
        if decision == "pending":
            reasons.append(f"Resolve candidate {identifier}.")
            continue
        if decision == "rejected" and not str(candidate.get("reason", "")).strip():
            reasons.append(f"Add a rejection reason for {identifier}.")
        if decision == "data_gap":
            if candidate.get("exclusion_kind") != "scoring_data_gap":
                reasons.append(f"Unsupported exclusion kind for {identifier}.")
            if not str(candidate.get("reason", "")).strip():
                reasons.append(f"Add a data-gap reason for {identifier}.")
            if candidate.get("uncertainty_disposition") != "scoring_data_gap":
                reasons.append(f"Resolve uncertainty for {identifier}.")
        if decision == "approved" and candidate.get("uncertainty_disposition") not in {
            "clear",
            "accept_event",
        }:
            reasons.append(f"Resolve uncertainty for {identifier}.")
        if (
            decision == "rejected"
            and candidate.get("uncertainty_disposition") != "reject_candidate"
        ):
            reasons.append(f"Resolve uncertainty for {identifier}.")
        if candidate.get("context_status") == "missing" and candidate.get(
            "uncertainty_disposition"
        ) in {"unresolved", "clear"}:
            reasons.append(f"Record an explicit disposition for missing context on {identifier}.")
        if candidate.get("uncertainty_disposition") == "accept_event" and not str(
            candidate.get("uncertainty_reason", "")
        ).strip():
            reasons.append(f"Add an uncertainty reason for {identifier}.")
        if decision not in {"approved", "rejected", "data_gap"}:
            reasons.append(f"Unsupported decision for {identifier}.")
        adjustments = candidate.get("adjustment_history")
        if not isinstance(adjustments, list) or any(
            not isinstance(item, dict) or not str(item.get("reason", "")).strip()
            for item in adjustments
        ):
            reasons.append(f"Adjustment history is incomplete for {identifier}.")
    return list(dict.fromkeys(reasons))


def _ordered_records(
    records: list[dict[str, object]], id_field: str
) -> list[dict[str, object]]:
    return sorted(
        records,
        key=lambda item: (
            int(cast(str, item["start_ns"])),
            int(cast(str, item["end_ns"])),
            str(item[id_field]),
        ),
    )


def _private_export_blocker(identity: Mapping[str, object]) -> str | None:
    # Explicit signal-product bindings currently accept only warmup/development.
    # Use the existing identity field so previously saved progress stays reusable.
    if identity.get("signal_product_manifest_sha256") is not None:
        return (
            "Organizer-private sealed truth cannot represent warm-up/development products. "
            "Export practice labels and retain the review audit locally."
        )
    return None


def build_export_document(
    state: Mapping[str, object],
    target: str,
    *,
    spec_name: str,
    source_bounds: tuple[int, int],
) -> dict[str, Any]:
    errors = gate_review(state)
    if errors:
        raise CivError("review is incomplete: " + " ".join(errors))
    identity = require_mapping(state.get("identity"), "review identity")
    candidates_value = state.get("candidates")
    if not isinstance(candidates_value, list):
        raise CivError("review candidates are invalid")
    candidates = [require_mapping(item, "review candidate") for item in candidates_value]
    for candidate in candidates:
        start_ns = _nonnegative_ns(candidate.get("start_ns"), "review start_ns")
        end_ns = _nonnegative_ns(candidate.get("end_ns"), "review end_ns")
        if not source_bounds[0] <= start_ns < end_ns <= source_bounds[1]:
            raise CivError(f"review interval is outside source bounds: {candidate.get('id')}")
        if candidate.get("decision") == "data_gap" and candidate.get(
            "exclusion_kind"
        ) != "scoring_data_gap":
            raise CivError(
                f"unsupported exclusion kind for {candidate.get('id')}: "
                f"{candidate.get('exclusion_kind')}"
            )
        if candidate.get("exclusion_kind") not in {None, "scoring_data_gap"}:
            raise CivError(f"unsupported exclusion kind for {candidate.get('id')}")

    if target == "practice":
        selected = [item for item in candidates if item.get("practice_selected") is True]
        labels = [
            {
                "end_ns": int(cast(str, item["end_ns"])),
                "label_id": str(item["id"]),
                "start_ns": int(cast(str, item["start_ns"])),
            }
            for item in selected
            if item.get("decision") == "approved"
        ]
        if not labels:
            raise CivError(
                "practice export needs at least one explicitly selected approved interval"
            )
        gaps = [
            {
                "end_ns": int(cast(str, item["end_ns"])),
                "gap_id": str(item["id"]),
                "reason": str(item["reason"]),
                "start_ns": int(cast(str, item["start_ns"])),
            }
            for item in selected
            if item.get("decision") == "data_gap"
        ]
        document: dict[str, Any] = {
            "contract": "civ.label-pack/v1alpha1",
            "data_gaps": _ordered_records(gaps, "gap_id"),
            "dataset": str(identity["dataset"]),
            "labels": _ordered_records(labels, "label_id"),
            "scoring": dict(SCORING_POLICY),
            "source_sha256": str(identity["source_sha256"]),
        }
        participant_pack = validate_score_reference(document)
        validate_label_pack(participant_pack)
        return participant_pack

    if target != "organizer-private":
        raise CivError(f"unknown review output target '{target}'")

    if blocker := _private_export_blocker(identity):
        raise CivError(blocker)

    if str(identity.get("dataset")) not in {"kashiwa", "reims"}:
        raise CivError("organizer-private output requires a supported dataset")
    intervals: list[dict[str, object]] = []
    exclusions: list[dict[str, object]] = []
    for item in candidates:
        start_ns = _nonnegative_ns(item.get("start_ns"), "review start_ns")
        end_ns = _nonnegative_ns(item.get("end_ns"), "review end_ns")
        if item.get("decision") == "approved":
            intervals.append(
                {
                    "end_ns": end_ns,
                    "interval_id": str(item["id"]),
                    "kind": spec_name,
                    "source_id": str(identity["source_id"]),
                    "source_sha256": str(identity["source_sha256"]),
                    "start_ns": start_ns,
                }
            )
        elif item.get("decision") == "data_gap":
            if item.get("exclusion_kind") != "scoring_data_gap":
                raise CivError(f"unsupported exclusion kind for {item.get('id')}")
            exclusions.append(
                {
                    "end_ns": end_ns,
                    "exclusion_id": str(item["id"]),
                    "reason": str(item["reason"]),
                    "source_id": str(identity["source_id"]),
                    "source_sha256": str(identity["source_sha256"]),
                    "start_ns": start_ns,
                }
            )
    document = {
        "dataset": str(identity["dataset"]),
        "exclusion_intervals": _ordered_records(exclusions, "exclusion_id"),
        "format": TRUTH_FORMAT,
        "intervals": _ordered_records(intervals, "interval_id"),
        "quality": {"global_completeness_approved": True},
        "split": "sealed",
        "target": spec_name,
    }
    serialized = f"{canonical_json(document)}\n"
    try:
        with tempfile.TemporaryDirectory(prefix="civ-label-review-") as directory:
            candidate_path = Path(directory) / "truth.json"
            candidate_path.write_text(serialized, encoding="utf-8", newline="\n")
            _truth_document(candidate_path)
    except OSError as error:
        raise CivError(f"cannot validate organizer-private truth: {error}") from error
    return document


def _write_atomic(path: Path, serialized: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            newline="\n",
            prefix=f".{path.name}.",
            suffix=".tmp",
            dir=path.parent,
            delete=False,
        ) as stream:
            temporary = Path(stream.name)
            stream.write(serialized)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    except OSError as error:
        if "temporary" in locals():
            temporary.unlink(missing_ok=True)
        raise CivError(f"cannot save local review progress: {error}") from error


def _archive_root(path: Path) -> Path:
    return path.with_name(f"{path.name}.revisions")


def _path_key(path: Path) -> str:
    return os.path.normcase(str(path.resolve()))


def _path_contains(parent: Path, child: Path) -> bool:
    try:
        common = Path(os.path.commonpath((str(parent), str(child))))
    except ValueError:
        return False
    return os.path.normcase(str(common)) == os.path.normcase(str(parent))


def _configured_archive_paths(binding: ReviewBinding) -> dict[str, Path]:
    archives = {"progress": _archive_root(binding.progress_path)}
    if binding.practice_output is not None:
        archives["practice"] = _archive_root(binding.practice_output)
    if binding.truth_output is not None:
        archives["organizer-private"] = _archive_root(binding.truth_output)
    return archives


def _digest_bytes(contents: bytes) -> str:
    return sha256(contents).hexdigest()


def _read_active_file(path: Path) -> bytes | None:
    if path.is_symlink():
        raise CivError(f"review path is a symbolic link: {path.name}")
    if not path.exists():
        return None
    if not path.is_file():
        raise CivError(f"review path is not a file: {path.name}")
    try:
        return path.read_bytes()
    except OSError as error:
        raise CivError(f"cannot read review file {path.name}: {error}") from error


def _stage_bytes(path: Path, contents: bytes) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb",
            prefix=f".{path.name}.",
            suffix=".tmp",
            dir=path.parent,
            delete=False,
        ) as stream:
            temporary = Path(stream.name)
            stream.write(contents)
            stream.flush()
            os.fsync(stream.fileno())
        return temporary
    except OSError as error:
        if "temporary" in locals():
            temporary.unlink(missing_ok=True)
        raise CivError(f"cannot stage review file {path.name}: {error}") from error


def _archive_snapshot(
    path: Path, contents: bytes, *, artifact: str, revision: int
) -> None:
    digest = _digest_bytes(contents)
    root = _archive_root(path)
    if root.is_symlink():
        raise CivError(f"review archive path is a symbolic link: {root.name}")
    metadata = {
        "active_filename": path.name,
        "artifact": artifact,
        "format": ARCHIVE_FORMAT,
        "revision": revision,
        "sha256": digest,
    }
    destination = root / f"revision-{revision:08d}-{digest}"
    try:
        root.mkdir(parents=True, exist_ok=True)
        if destination.exists():
            if destination.is_symlink() or not destination.is_dir():
                raise CivError(f"review archive revision is unsafe: {destination.name}")
            content_path = destination / "content"
            metadata_path = destination / "metadata.json"
            if (
                content_path.is_symlink()
                or metadata_path.is_symlink()
                or not content_path.is_file()
                or not metadata_path.is_file()
            ):
                raise CivError(f"review archive revision is corrupted: {destination.name}")
            archived = content_path.read_bytes()
            archived_metadata = json.loads(
                metadata_path.read_text(encoding="utf-8")
            )
            if archived != contents or archived_metadata != metadata:
                raise CivError(f"review archive revision is corrupted: {destination.name}")
            return

        temporary = Path(tempfile.mkdtemp(prefix=".snapshot-", dir=root))
        try:
            with (temporary / "content").open("wb") as stream:
                stream.write(contents)
                stream.flush()
                os.fsync(stream.fileno())
            with (temporary / "metadata.json").open("wb") as stream:
                stream.write(f"{canonical_json(metadata)}\n".encode())
                stream.flush()
                os.fsync(stream.fileno())
            os.rename(temporary, destination)
        except Exception:
            shutil.rmtree(temporary, ignore_errors=True)
            raise
    except CivError:
        raise
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise CivError(f"cannot archive review file {path.name}: {error}") from error


def _writer_lock_path(progress_path: Path) -> Path:
    return progress_path.with_name(f"{progress_path.name}.lock")


def _transaction_write(
    progress_path: Path,
    changes: Mapping[Path, bytes],
    expected_digests: Mapping[Path, str | None],
    snapshots: Mapping[Path, tuple[str, int]],
    *,
    force_paths: frozenset[Path] = frozenset(),
) -> dict[Path, str]:
    lock_path = _writer_lock_path(progress_path)
    if lock_path.is_symlink():
        raise CivError(f"review writer lock path is a symbolic link: {lock_path.name}")
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        descriptor = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError as error:
        raise CivError(
            "another review writer holds the progress lock; reload before writing"
        ) from error
    except OSError as error:
        raise CivError(f"cannot acquire review writer lock: {error}") from error

    staged: dict[Path, Path] = {}
    backups: dict[Path, Path] = {}
    previous: dict[Path, bytes | None] = {}
    modified: list[Path] = []
    try:
        with os.fdopen(descriptor, "w", encoding="ascii") as stream:
            stream.write(f"{os.getpid()}\n")
            stream.flush()
            os.fsync(stream.fileno())

        for path in changes:
            old_bytes = _read_active_file(path)
            previous[path] = old_bytes
            old_digest = _digest_bytes(old_bytes) if old_bytes is not None else None
            if old_digest != expected_digests.get(path):
                if path == progress_path:
                    raise CivError(
                        "saved review changed since this session opened; reload before writing"
                    )
                raise CivError(
                    f"review output changed since this session opened: {path.name}"
                )

        actual_changes = {
            path: contents
            for path, contents in changes.items()
            if path in force_paths or previous[path] != contents
        }
        if not actual_changes:
            return {
                path: _digest_bytes(contents)
                for path, contents in changes.items()
            }

        for path, contents in actual_changes.items():
            staged[path] = _stage_bytes(path, contents)
        for path in actual_changes:
            old_bytes = previous[path]
            if old_bytes is not None:
                artifact, revision = snapshots[path]
                _archive_snapshot(path, old_bytes, artifact=artifact, revision=revision)

        commit_order = [path for path in actual_changes if path != progress_path]
        if progress_path in actual_changes:
            commit_order.append(progress_path)
        try:
            for path in commit_order:
                if previous[path] is not None:
                    backups[path] = _stage_bytes(path, b"")
                    os.replace(path, backups[path])
                    modified.append(path)
                os.replace(staged[path], path)
                if path not in modified:
                    modified.append(path)
        except Exception as error:
            rollback_error: Exception | None = None
            for path in reversed(modified):
                old_bytes = previous[path]
                try:
                    if old_bytes is None:
                        path.unlink(missing_ok=True)
                    else:
                        backup = backups[path]
                        os.replace(backup, path)
                except Exception as rollback_failure:
                    rollback_error = rollback_failure
                    break
            if rollback_error is not None:
                raise CivError(
                    "review write failed and active files could not be restored; "
                    "use the archived revisions to recover"
                ) from rollback_error
            if isinstance(error, CivError):
                raise
            raise CivError(f"cannot replace review files: {error}") from error

        return {
            path: _digest_bytes(contents)
            for path, contents in changes.items()
        }
    finally:
        for temporary in staged.values():
            temporary.unlink(missing_ok=True)
        for backup in backups.values():
            backup.unlink(missing_ok=True)
        with suppress(OSError):
            lock_path.unlink(missing_ok=True)


def _read_progress_document(
    path: Path, binding: ReviewBinding
) -> tuple[dict[str, object], bytes]:
    contents = _read_active_file(path)
    if contents is None:
        raise CivError(f"local review progress does not exist: {path}")
    try:
        state = require_mapping(json.loads(contents.decode("utf-8")), "local review progress")
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise CivError(f"cannot read local review progress {path.name}: {error}") from error
    if state.get("format") != PROGRESS_FORMAT:
        raise CivError("saved progress has an unsupported format")
    if state.get("identity") != binding.identity:
        raise CivError("saved progress source or EventSpec identity does not match")
    revision = state.get("revision")
    geometry_revision = state.get("geometry_revision")
    coverage_revision = state.get("coverage_revision")
    if (
        isinstance(revision, bool)
        or not isinstance(revision, int)
        or revision < 0
        or isinstance(geometry_revision, bool)
        or not isinstance(geometry_revision, int)
        or geometry_revision < 0
        or isinstance(coverage_revision, bool)
        or not isinstance(coverage_revision, int)
        or coverage_revision < -1
    ):
        raise CivError("saved progress revision metadata is invalid")
    if not isinstance(state.get("reviewer"), str) or not isinstance(
        state.get("coverage_reviewed"), bool
    ):
        raise CivError("saved progress review status is invalid")
    coverage_reviewer = state.get("coverage_reviewer")
    if coverage_reviewer is not None and not isinstance(coverage_reviewer, str):
        raise CivError("saved progress coverage reviewer is invalid")
    if state["coverage_reviewed"] and (
        coverage_revision != geometry_revision
        or not isinstance(coverage_reviewer, str)
        or not coverage_reviewer.strip()
    ):
        raise CivError("saved progress completeness signoff is inconsistent")
    if not state["coverage_reviewed"] and coverage_revision != -1:
        raise CivError("saved progress completeness signoff is inconsistent")
    audit = state.get("audit")
    if not isinstance(audit, list) or len(audit) > revision:
        raise CivError("saved progress audit history is invalid")
    audit_actions = {
        "add-missed",
        "approve",
        "check-window",
        "data-gap",
        "edit",
        "reject",
        "set-practice",
        "set-reviewer",
        "signoff",
        "undo",
    }
    for record in audit:
        entry = require_mapping(record, "saved review audit record")
        action = require_string(entry.get("action"), "saved review audit action")
        if action not in audit_actions:
            raise CivError(f"saved review audit action is unsupported: {action}")
        audit_reviewer = entry.get("reviewer")
        if not isinstance(audit_reviewer, str) or (
            action != "undo" and not audit_reviewer.strip()
        ):
            raise CivError("saved review audit reviewer is invalid")
    candidates = state.get("candidates")
    if not isinstance(candidates, list):
        raise CivError("saved progress candidates are invalid")
    seen: set[str] = set()
    detected_ids: set[str] = set()
    for item in candidates:
        candidate = require_mapping(item, "saved review candidate")
        identifier = require_string(candidate.get("id"), "saved candidate id")
        if identifier in seen:
            raise CivError("saved progress contains duplicate candidate IDs")
        seen.add(identifier)
        kind = candidate.get("kind")
        if kind == "detected":
            if candidate.get("event_id") != identifier or identifier not in binding.event_ids:
                raise CivError(f"saved detected candidate identity changed: {identifier}")
            detected_ids.add(identifier)
        elif kind == "missed":
            suffix = identifier.removeprefix("missed-")
            if (
                candidate.get("event_id") is not None
                or not identifier.startswith("missed-")
                or len(suffix) < 4
                or not suffix.isascii()
                or not suffix.isdigit()
            ):
                raise CivError(f"saved missed-event identity is invalid: {identifier}")
        else:
            raise CivError(f"saved candidate kind is unsupported: {identifier}")
        if (
            candidate.get("decision") == "data_gap"
            and candidate.get("exclusion_kind") != "scoring_data_gap"
        ):
            raise CivError(f"unsupported exclusion kind for {identifier}")
        if candidate.get("exclusion_kind") not in {None, "scoring_data_gap"}:
            raise CivError(
                f"unsupported exclusion kind for {identifier}: {candidate.get('exclusion_kind')}"
            )
        if candidate.get("decision") not in {
            "pending",
            "approved",
            "rejected",
            "data_gap",
        }:
            raise CivError(f"unsupported saved review decision for {identifier}")
        if candidate.get("uncertainty_disposition") not in {
            "unresolved",
            "clear",
            "accept_event",
            "reject_candidate",
            "scoring_data_gap",
        }:
            raise CivError(f"saved uncertainty disposition is invalid for {identifier}")
        expected_disposition = {
            "pending": "unresolved",
            "rejected": "reject_candidate",
            "data_gap": "scoring_data_gap",
        }.get(str(candidate["decision"]))
        if expected_disposition is not None and candidate.get(
            "uncertainty_disposition"
        ) != expected_disposition:
            raise CivError(f"saved decision disposition is inconsistent for {identifier}")
        if candidate.get("decision") == "approved" and candidate.get(
            "uncertainty_disposition"
        ) not in {"clear", "accept_event"}:
            raise CivError(f"saved approval disposition is inconsistent for {identifier}")
        if not isinstance(candidate.get("practice_selected"), bool):
            raise CivError(f"saved practice selection is invalid for {identifier}")
        if not isinstance(candidate.get("reason"), str) or not isinstance(
            candidate.get("uncertainty_reason"), str
        ):
            raise CivError(f"saved review reason is invalid for {identifier}")
        if not isinstance(candidate.get("adjustment_history"), list):
            raise CivError(f"saved adjustment history is invalid for {identifier}")
        candidate_reviewer = candidate.get("reviewer")
        if candidate_reviewer is not None and not isinstance(candidate_reviewer, str):
            raise CivError(f"saved candidate reviewer is invalid for {identifier}")
        if candidate.get("practice_selected") and candidate.get("decision") not in {
            "approved",
            "data_gap",
        }:
            raise CivError(f"saved practice selection is incompatible for {identifier}")
        if candidate.get("decision") in {"approved", "rejected", "data_gap"} and (
            not isinstance(candidate_reviewer, str) or not candidate_reviewer.strip()
        ):
            raise CivError(f"saved decision reviewer is missing for {identifier}")
        if candidate.get("decision") in {"rejected", "data_gap"} and not str(
            candidate.get("reason", "")
        ).strip():
            raise CivError(f"saved decision reason is missing for {identifier}")
        for field in ("start_ns", "end_ns"):
            if not isinstance(candidate.get(field), str):
                raise CivError(f"saved {field} must be an exact integer string for {identifier}")
        start_ns = _nonnegative_ns(candidate.get("start_ns"), "saved candidate start_ns")
        end_ns = _nonnegative_ns(candidate.get("end_ns"), "saved candidate end_ns")
        if not binding.source_bounds[0] <= start_ns < end_ns <= binding.source_bounds[1]:
            raise CivError(f"saved review interval is outside source bounds: {identifier}")
        for raw_adjustment in cast(list[object], candidate["adjustment_history"]):
            adjustment = require_mapping(raw_adjustment, "saved adjustment history entry")
            require_string(adjustment.get("reason"), "saved adjustment reason")
            require_string(adjustment.get("reviewer"), "saved adjustment reviewer")
            boundaries: dict[str, int] = {}
            for field in ("start_ns", "end_ns", "new_start_ns", "new_end_ns"):
                value = adjustment.get(field)
                if not isinstance(value, str):
                    raise CivError(f"saved adjustment {field} is invalid for {identifier}")
                boundaries[field] = _nonnegative_ns(value, f"saved adjustment {field}")
            for start_field, end_field in (
                ("start_ns", "end_ns"),
                ("new_start_ns", "new_end_ns"),
            ):
                if not binding.source_bounds[0] <= boundaries[start_field] < boundaries[
                    end_field
                ] <= binding.source_bounds[1]:
                    raise CivError(f"saved adjustment is outside source bounds: {identifier}")
    if detected_ids != set(binding.event_ids):
        raise CivError("saved progress candidate set does not match the detected events")
    exports = state.get("exports", {})
    if not isinstance(exports, dict):
        raise CivError("saved export metadata is invalid")
    configured_outputs = _configured_output_paths(binding)
    for target, raw_metadata in exports.items():
        if target not in {"practice", "organizer-private"} or target not in configured_outputs:
            raise CivError("saved export metadata does not match configured output paths")
        metadata = require_mapping(raw_metadata, f"saved {target} export metadata")
        export_revision = metadata.get("revision")
        export_digest = metadata.get("sha256")
        if (
            isinstance(export_revision, bool)
            or not isinstance(export_revision, int)
            or export_revision < 1
            or not isinstance(export_digest, str)
            or len(export_digest) != 64
            or any(character not in "0123456789abcdef" for character in export_digest)
        ):
            raise CivError(f"saved {target} export metadata is invalid")
    output_paths = state.get("output_paths")
    if exports and output_paths is None:
        raise CivError("saved export metadata has no bound output paths")
    if output_paths is not None:
        if not isinstance(output_paths, dict) or any(
            not isinstance(key, str) or not isinstance(value, str)
            for key, value in output_paths.items()
        ):
            raise CivError("saved output paths are invalid")
        normalized_saved = {key: os.path.normcase(value) for key, value in output_paths.items()}
        normalized_configured = {
            key: os.path.normcase(value) for key, value in configured_outputs.items()
        }
        if normalized_saved != normalized_configured:
            raise CivError("configured output paths do not match saved review")
    windows = state.get("checked_windows", [])
    if not isinstance(windows, list):
        raise CivError("saved checked windows must be a list")
    for raw_window in windows:
        checked = require_mapping(raw_window, "saved checked window")
        _source_window(checked, binding.source_bounds)
        require_string(checked.get("reviewer"), "checked-window reviewer")
    state["checked_windows"] = windows
    return cast(dict[str, object], state), contents


def _read_progress(path: Path, binding: ReviewBinding) -> dict[str, object]:
    state, _ = _read_progress_document(path, binding)
    return state


def _load_html() -> bytes:
    path = Path(__file__).parent / "label_review.html"
    try:
        return path.read_bytes()
    except OSError as error:
        raise CivError(f"cannot load the local review interface: {error}") from error


def _validate_output_bytes(target: str, contents: bytes, binding: ReviewBinding) -> None:
    try:
        document = require_mapping(
            json.loads(contents.decode("utf-8")), f"existing {target} output"
        )
        if target == "practice":
            checked = validate_score_reference(document)
            validate_label_pack(checked)
            if (
                checked.get("source_sha256") != binding.identity.get("source_sha256")
                or checked.get("dataset") != binding.identity.get("dataset")
            ):
                raise CivError("practice output source identity does not match")
            return
        if target != "organizer-private":
            raise CivError(f"unknown review output target '{target}'")
        if (
            document.get("target") != binding.spec_name
            or document.get("quality") != {"global_completeness_approved": True}
        ):
            raise CivError("organizer-private output target does not match")
        with tempfile.TemporaryDirectory(prefix="civ-label-review-output-") as directory:
            candidate = Path(directory) / "truth.json"
            candidate.write_bytes(contents)
            truth = _truth_document(candidate)
        if truth.dataset != binding.identity.get("dataset"):
            raise CivError("organizer-private output dataset does not match")
        for interval in (*truth.intervals, *truth.gaps):
            if (
                interval.source_id != binding.identity.get("source_id")
                or interval.source_sha256 != binding.identity.get("source_sha256")
                or not binding.source_bounds[0]
                <= interval.start_ns
                < interval.end_ns
                <= binding.source_bounds[1]
            ):
                raise CivError("organizer-private output source identity does not match")
    except (CivError, UnicodeDecodeError, json.JSONDecodeError, OSError) as error:
        raise CivError(f"existing {target} output is invalid or mismatched") from error


class ReviewApplication:
    def __init__(
        self,
        binding: ReviewBinding,
        state: dict[str, object],
        *,
        before_ns: int,
        after_ns: int,
        comparisons: ProfileComparisons | None = None,
        review_rule: str | None = None,
        default_reviewer: str | None = None,
        progress_digest: str | None = None,
        progress_digest_is_current: bool = False,
    ) -> None:
        self.binding = binding
        self.comparisons = comparisons
        self.review_rule = (
            require_string(review_rule, "review rule") if review_rule is not None else None
        )
        self.default_reviewer = (
            require_string(default_reviewer, "default reviewer")
            if default_reviewer is not None
            else None
        )
        self.state = state
        self.before_ns = before_ns
        self.after_ns = after_ns
        self.history: list[dict[str, object]] = []
        self.frame_cache: dict[int, tuple[str, bytes]] = {}
        progress_bytes = _read_active_file(binding.progress_path)
        if progress_digest_is_current:
            self._progress_digest = progress_digest
        else:
            self._progress_digest = (
                _digest_bytes(progress_bytes) if progress_bytes is not None else None
            )
        self._output_digests: dict[str, str] = {}
        self._output_revisions: dict[str, int] = {}
        self._validate_active_outputs(state)
        self._refresh_context(self.state)

    def save(self) -> None:
        self._refresh_context(self.state)
        self._write_state(self.state)

    def reload(self) -> dict[str, object]:
        state, contents = _read_progress_document(self.binding.progress_path, self.binding)
        self._validate_active_outputs(state)
        self._refresh_context(state)
        self.state = state
        self._progress_digest = _digest_bytes(contents)
        self.history.clear()
        return self.view()

    def _validate_active_outputs(self, state: Mapping[str, object]) -> None:
        exports = state.get("exports", {})
        if not isinstance(exports, Mapping):
            raise CivError("saved export metadata is invalid")
        output_digests: dict[str, str] = {}
        output_revisions: dict[str, int] = {}
        configured = {
            "practice": self.binding.practice_output,
            "organizer-private": self.binding.truth_output,
        }
        for target, output in configured.items():
            metadata_value = exports.get(target)
            metadata = (
                require_mapping(metadata_value, f"saved {target} export metadata")
                if metadata_value is not None
                else None
            )
            if output is None:
                if metadata is not None:
                    raise CivError("saved export metadata does not match configured output paths")
                continue
            contents = _read_active_file(output)
            if contents is None:
                if metadata is not None:
                    raise CivError(f"saved {target} output is missing")
                continue
            digest = _digest_bytes(contents)
            if metadata is not None:
                if metadata.get("sha256") != digest:
                    raise CivError(f"saved {target} output digest does not match progress")
                revision = metadata.get("revision")
                if isinstance(revision, bool) or not isinstance(revision, int):
                    raise CivError(f"saved {target} output revision is invalid")
                output_revisions[target] = revision
            else:
                _validate_output_bytes(target, contents, self.binding)
                output_revisions[target] = 1
            output_digests[target] = digest
        self._output_digests = output_digests
        self._output_revisions = output_revisions

    def _recheck_active_outputs(self) -> None:
        configured = {
            "practice": self.binding.practice_output,
            "organizer-private": self.binding.truth_output,
        }
        for target, output in configured.items():
            if output is None:
                continue
            contents = _read_active_file(output)
            current = _digest_bytes(contents) if contents is not None else None
            if current != self._output_digests.get(target):
                raise CivError(f"review output changed since this session opened: {output.name}")

    def _write_state(self, state: dict[str, object]) -> None:
        self._recheck_active_outputs()
        old_revision = self.state.get("revision", 0)
        if isinstance(old_revision, bool) or not isinstance(old_revision, int):
            raise CivError("review revision is invalid")
        serialized = f"{canonical_json(state)}\n".encode()
        result = _transaction_write(
            self.binding.progress_path,
            {self.binding.progress_path: serialized},
            {self.binding.progress_path: self._progress_digest},
            {self.binding.progress_path: ("review-progress", old_revision)},
        )
        self._progress_digest = result[self.binding.progress_path]

    def _evidence_for(self, candidate: Mapping[str, object]) -> dict[str, object]:
        candidate_id = str(candidate.get("id"))
        start_ns = _nonnegative_ns(candidate.get("start_ns"), "candidate start_ns")
        end_ns = _nonnegative_ns(candidate.get("end_ns"), "candidate end_ns")
        cached = self.binding.evidence_by_id.get(candidate_id)
        if (
            cached is not None
            and cached.get("start_ns") == str(start_ns)
            and cached.get("end_ns") == str(end_ns)
        ):
            return dict(cached)
        spec = load_event_spec(self.binding.spec_path)
        windows = {
            candidate_id: _window(start_ns, end_ns, self.before_ns, self.after_ns)
        }
        signals = _collect_signals(
            self.binding.source_path,
            spec.signals,
            windows,
        )[candidate_id]
        evidence = _candidate_context(
            candidate_id,
            start_ns,
            end_ns,
            signals,
            self.binding.camera_frames,
            self.before_ns,
            self.after_ns,
        )
        self.binding.evidence_by_id[candidate_id] = evidence
        return evidence

    def evidence_window(self, request: Mapping[str, object]) -> dict[str, Any]:
        start_ns, end_ns = _source_window(request, self.binding.source_bounds)
        self.recheck_inputs()
        spec = load_event_spec(self.binding.spec_path)
        signals = _collect_signals(
            self.binding.source_path, spec.signals, {"source-window": (start_ns, end_ns)}
        )["source-window"]
        return _candidate_context(
            "source-window", start_ns, end_ns, signals, self.binding.camera_frames, 0, 0
        )

    def view(self) -> dict[str, object]:
        self._refresh_context(self.state)
        state = copy.deepcopy(self.state)
        private_blocker = _private_export_blocker(self.binding.identity)
        return {
            "source_bounds": {
                "start_ns": str(self.binding.source_bounds[0]),
                "end_ns": str(self.binding.source_bounds[1]),
            },
            "gate": gate_review(self.state),
            "identity": self.binding.identity,
            "can_undo": bool(self.history),
            "outputs": {
                "organizer-private": (
                    self.binding.truth_output is not None and private_blocker is None
                ),
                "practice": self.binding.practice_output is not None,
            },
            "comparisons": self.comparisons.view() if self.comparisons else [],
            "review_rule": self.review_rule,
            "default_reviewer": self.default_reviewer,
            "output_blockers": {"organizer-private": private_blocker},
            "state": state,
        }

    def act(self, action: Mapping[str, object]) -> dict[str, object]:
        self._refresh_context(self.state)
        if action.get("type") == "undo":
            if not self.history:
                raise CivError("there is no review action to undo")
            previous = copy.deepcopy(self.history[-1])
            current_audit = self.state.get("audit")
            undone = (
                copy.deepcopy(current_audit[-1])
                if isinstance(current_audit, list) and current_audit
                else {"action": "unknown"}
            )
            audit = previous.get("audit")
            if not isinstance(audit, list):
                raise CivError("review audit must be a list")
            audit.append(
                {
                    "action": "undo",
                    "reviewer": str(previous.get("reviewer", "")),
                    "undid": undone,
                }
            )
            if "exports" in self.state:
                previous["exports"] = copy.deepcopy(self.state["exports"])
            if "output_paths" in self.state:
                previous["output_paths"] = copy.deepcopy(self.state["output_paths"])
            revision = self.state.get("revision")
            if isinstance(revision, bool) or not isinstance(revision, int):
                raise CivError("review revision is invalid")
            previous["revision"] = revision + 1
            self._refresh_context(previous)
            self._write_state(previous)
            self.history.pop()
            self.state = previous
            return self.view()
        next_state = transition_review(self.state, action, self.binding.source_bounds)
        self._refresh_context(next_state)
        self._write_state(next_state)
        self.history.append(self.state)
        self.state = next_state
        return self.view()

    def _refresh_context(self, state: dict[str, object]) -> None:
        if self.comparisons is not None:
            self.comparisons.recheck()
        self._recheck_signal_manifest()
        candidates = state.get("candidates")
        if not isinstance(candidates, list):
            raise CivError("review candidates are invalid")
        for raw in candidates:
            if not isinstance(raw, dict):
                raise CivError("review candidate is invalid")
            candidate = cast(dict[str, object], raw)
            evidence = self._evidence_for(candidate)
            candidate.update(
                {
                    "camera_frames": copy.deepcopy(evidence["camera_frames"]),
                    "signals": copy.deepcopy(evidence["signals"]),
                    "context_status": evidence["status"],
                    "missing_context": copy.deepcopy(evidence["missing_context"]),
                }
            )

    def _recheck_signal_manifest(self) -> None:
        path = self.binding.signal_product_manifest_path
        if path is not None and file_sha256(path) != self.binding.identity.get(
            "signal_product_manifest_sha256"
        ):
            raise CivError("signal-product manifest changed during review")

    def recheck_inputs(self) -> None:
        self._recheck_signal_manifest()
        if file_sha256(self.binding.source_path) != self.binding.identity["source_sha256"]:
            raise CivError("source recording changed during review")
        if file_sha256(self.binding.spec_path) != self.binding.identity["spec_sha256"]:
            raise CivError("EventSpec changed during review")
        if file_sha256(self.binding.events_path) != self.binding.identity["events_sha256"]:
            raise CivError("candidate events changed during review")
        if file_sha256(self.binding.manifest_path) != self.binding.identity["manifest_sha256"]:
            raise CivError("run manifest changed during review")
        spec = load_event_spec(self.binding.spec_path)
        resources = load_point_resources(self.binding.spec_path, spec.resources)
        resource_records = [
            resource.provenance() for _, resource in sorted(resources.items())
        ]
        resource_hash = sha256(canonical_json(resource_records).encode("utf-8")).hexdigest()
        if resource_hash != self.binding.identity["resource_set_sha256"]:
            raise CivError("EventSpec resources changed during review")
        if self.binding.camera_frames is not None and file_sha256(
            self.binding.camera_frames.product_path
        ) != self.binding.identity["camera_context_product_sha256"]:
            raise CivError("approved camera context changed during review")
        if self.binding.camera_manifest_path is not None and file_sha256(
            self.binding.camera_manifest_path
        ) != self.binding.identity["camera_context_manifest_sha256"]:
            raise CivError("camera-context approval changed during review")

    def export(self, target: str) -> dict[str, object]:
        self._recheck_active_outputs()
        self.recheck_inputs()
        self._refresh_context(self.state)
        output = (
            self.binding.practice_output
            if target == "practice"
            else self.binding.truth_output
            if target == "organizer-private"
            else None
        )
        if output is None:
            raise CivError(f"no output path was configured for '{target}'")
        document = build_export_document(
            self.state,
            target,
            spec_name=self.binding.spec_name,
            source_bounds=self.binding.source_bounds,
        )
        output_bytes = f"{canonical_json(document)}\n".encode()
        output_digest = _digest_bytes(output_bytes)
        previous_output = _read_active_file(output)
        old_output_revision = self._output_revisions.get(target, 1 if previous_output else 0)
        if previous_output is not None:
            _validate_output_bytes(target, previous_output, self.binding)

        next_state = copy.deepcopy(self.state)
        exports_value = next_state.get("exports", {})
        if not isinstance(exports_value, dict):
            raise CivError("saved export metadata is invalid")
        exports = copy.deepcopy(exports_value)
        exports[target] = {
            "revision": old_output_revision + 1,
            "sha256": output_digest,
        }
        next_state["exports"] = exports
        next_state["output_paths"] = _configured_output_paths(self.binding)
        review_revision = self.state.get("revision")
        if isinstance(review_revision, bool) or not isinstance(review_revision, int):
            raise CivError("review revision is invalid")
        next_state["revision"] = review_revision + 1
        progress_bytes = f"{canonical_json(next_state)}\n".encode()
        snapshots: dict[Path, tuple[str, int]] = {
            self.binding.progress_path: ("review-progress", review_revision),
            output: (f"{target}-export", old_output_revision),
        }
        results = _transaction_write(
            self.binding.progress_path,
            {output: output_bytes, self.binding.progress_path: progress_bytes},
            {
                output: self._output_digests.get(target),
                self.binding.progress_path: self._progress_digest,
            },
            snapshots,
            force_paths=frozenset({output}),
        )
        self.state = next_state
        self._progress_digest = results[self.binding.progress_path]
        self._output_digests[target] = results[output]
        self._output_revisions[target] = old_output_revision + 1
        return {
            "name": output.name,
            "revision": old_output_revision + 1,
            "sha256": output_digest,
            "target": target,
        }

    def frame(self, index: int) -> tuple[str, bytes]:
        if self.binding.camera_frames is None:
            raise CivError("no rights-approved camera context is available")
        if index not in self.frame_cache:
            self.frame_cache[index] = _camera_frame_bytes(self.binding.camera_frames, index)
        return self.frame_cache[index]


def _create_handler(app: ReviewApplication, token: str) -> type[BaseHTTPRequestHandler]:
    class Handler(BaseHTTPRequestHandler):
        server_version = "CIVLabelReview/1"

        def log_message(self, format: str, *args: object) -> None:
            return

        def _send(self, status: int, body: bytes, content_type: str) -> None:
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("Referrer-Policy", "no-referrer")
            self.send_header(
                "Content-Security-Policy",
                "default-src 'self'; img-src 'self'; connect-src 'self'; "
                "style-src 'self' 'unsafe-inline'; script-src 'self' 'unsafe-inline'; "
                "base-uri 'none'; frame-ancestors 'none'; form-action 'self'",
            )
            self.end_headers()
            self.wfile.write(body)

        def _token_from_query(self) -> bool:
            query = parse_qs(urlsplit(self.path).query)
            return secrets.compare_digest(query.get("token", [""])[0], token)

        def _authorized(self, *, query: bool = False) -> bool:
            supplied = (
                parse_qs(urlsplit(self.path).query).get("token", [""])[0]
                if query
                else self.headers.get("X-CIV-Token", "")
            )
            return secrets.compare_digest(supplied, token)

        def _json_body(self) -> dict[str, Any]:
            try:
                length = int(self.headers.get("Content-Length", "0"))
            except ValueError as error:
                raise CivError("request length is invalid") from error
            if length < 0 or length > 1024 * 1024:
                raise CivError("request body exceeds the local interface limit")
            try:
                value = json.loads(self.rfile.read(length).decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError) as error:
                raise CivError("request body must be valid UTF-8 JSON") from error
            return require_mapping(value, "review request")

        def _json(self, status: int, value: object) -> None:
            body = (json.dumps(value, ensure_ascii=False, separators=(",", ":"))).encode("utf-8")
            self._send(status, body, "application/json; charset=utf-8")

        def do_GET(self) -> None:
            path = urlsplit(self.path).path
            if self.client_address[0] not in {"127.0.0.1", "::1"}:
                self._send(403, b"Local review only.", "text/plain; charset=utf-8")
                return
            if path == "/":
                if not self._token_from_query():
                    self._send(403, b"Local review token is required.", "text/plain; charset=utf-8")
                    return
                try:
                    body = _load_html()
                except CivError as error:
                    self._json(500, {"error": str(error)})
                    return
                self._send(200, body, "text/html; charset=utf-8")
                return
            if path == "/api/state":
                if not self._authorized(query=True):
                    self._json(403, {"error": "Local review token is required."})
                    return
                self._json(200, app.view())
                return
            if path.startswith("/api/frame/"):
                if not self._authorized(query=True):
                    self._send(403, b"Local review token is required.", "text/plain; charset=utf-8")
                    return
                try:
                    index = int(path.removeprefix("/api/frame/"))
                    content_type, data = app.frame(index)
                except (ValueError, CivError) as error:
                    self._send(404, str(error).encode("utf-8"), "text/plain; charset=utf-8")
                    return
                self._send(200, data, content_type)
                return
            self._send(404, b"Not found.", "text/plain; charset=utf-8")

        def do_POST(self) -> None:
            if self.client_address[0] not in {"127.0.0.1", "::1"}:
                self._json(403, {"error": "Local review only."})
                return
            if not self._authorized():
                self._json(403, {"error": "Local review token is required."})
                return
            path = urlsplit(self.path).path
            try:
                if path == "/api/window":
                    result = app.evidence_window(self._json_body())
                elif path == "/api/action":
                    result = app.act(self._json_body())
                elif path == "/api/save":
                    app.save()
                    result = app.view()
                elif path == "/api/reload":
                    result = app.reload()
                elif path == "/api/export":
                    request = self._json_body()
                    target = require_string(request.get("target"), "output target")
                    result = app.export(target)
                else:
                    self._send(404, b"Not found.", "text/plain; charset=utf-8")
                    return
            except CivError as error:
                self._json(400, {"error": str(error), "gate": gate_review(app.state)})
                return
            except (OSError, ValueError, TypeError) as error:
                self._json(400, {"error": str(error), "gate": gate_review(app.state)})
                return
            self._json(200, result)

    return Handler


def _prepare_binding(
    args: argparse.Namespace,
) -> tuple[ReviewBinding, list[Any], dict[str, Any], int, int]:
    camera_manifest = args.camera_context_manifest
    binding, events, manifest, camera, before_ns, after_ns = _identity_for_inputs(
        args.source,
        args.spec,
        args.events,
        args.manifest,
        args.dataset,
        args.source_id,
        camera_manifest,
        getattr(args, "signal_product_manifest", None),
    )
    raw_active_paths = [
        path
        for path in (args.progress, args.practice_output, args.organizer_output)
        if path is not None
    ]
    for path in raw_active_paths:
        if path.is_symlink():
            raise CivError(f"review path is a symbolic link: {path.name}")
    progress_path = args.progress.resolve()
    practice_output = args.practice_output.resolve() if args.practice_output else None
    truth_output = args.organizer_output.resolve() if args.organizer_output else None
    inputs = [binding.source_path, binding.spec_path, binding.events_path, binding.manifest_path]
    if binding.signal_product_manifest_path is not None:
        inputs.append(binding.signal_product_manifest_path)
    if camera_manifest:
        inputs.append(camera_manifest.resolve())
    if camera is not None:
        inputs.append(camera.product_path.resolve())
    outputs = [path for path in (practice_output, truth_output) if path is not None]
    active_paths = [progress_path, *outputs]
    if len({_path_key(path) for path in [*inputs, *active_paths]}) != len(inputs) + len(
        active_paths
    ):
        raise CivError("review inputs, progress, and outputs must use separate paths")
    if len({_path_key(path) for path in outputs}) != len(outputs):
        raise CivError("practice and organizer-private outputs must use separate paths")
    for path in active_paths:
        if path.exists() and not path.is_file():
            raise CivError(f"review path is not a file: {path.name}")
    if practice_output is None and truth_output is None:
        raise CivError("configure at least one distinct review output path")

    binding = ReviewBinding(
        source_path=binding.source_path,
        spec_path=binding.spec_path,
        events_path=binding.events_path,
        manifest_path=binding.manifest_path,
        progress_path=progress_path,
        camera_manifest_path=camera_manifest.resolve() if camera_manifest else None,
        source_bounds=binding.source_bounds,
        identity=binding.identity,
        evidence_by_id=binding.evidence_by_id,
        camera_frames=camera,
        practice_output=practice_output,
        truth_output=truth_output,
        spec_name=binding.spec_name,
        event_ids=binding.event_ids,
        signal_product_manifest_path=binding.signal_product_manifest_path,
    )
    archives = _configured_archive_paths(binding)
    archive_keys = {_path_key(path) for path in archives.values()}
    if len(archive_keys) != len(archives):
        raise CivError("review archive paths must be distinct")
    lock_path = _writer_lock_path(progress_path)
    if _path_key(lock_path) in {_path_key(path) for path in [*inputs, *active_paths]}:
        raise CivError("review writer lock path collides with an input or active file")
    guarded_paths = [*inputs, *active_paths, lock_path]
    for archive in archives.values():
        if archive.is_symlink() or (archive.exists() and not archive.is_dir()):
            raise CivError(f"review archive path is unsafe: {archive.name}")
        if any(
            _path_contains(archive, path) or _path_contains(path, archive)
            for path in guarded_paths
        ):
            raise CivError("review archive paths must not overlap inputs or active files")
    return binding, events, manifest, before_ns, after_ns


def review_command(args: argparse.Namespace) -> None:
    binding, events, _, before_ns, after_ns = _prepare_binding(args)
    inventory = getattr(args, "comparison_inventory", None)
    comparisons = load_profile_comparisons(inventory, binding) if inventory else None
    has_progress = binding.progress_path.exists()
    if has_progress:
        state, progress_bytes = _read_progress_document(binding.progress_path, binding)
        progress_digest = _digest_bytes(progress_bytes)
    else:
        if any(
            path is not None and path.exists()
            for path in (binding.practice_output, binding.truth_output)
        ):
            raise CivError("review outputs exist without compatible saved progress")
        state = initial_review_state(binding, events, binding.evidence_by_id)
        progress_digest = None
    app = ReviewApplication(
        binding,
        state,
        before_ns=before_ns,
        after_ns=after_ns,
        comparisons=comparisons,
        review_rule=getattr(args, "review_rule", None),
        default_reviewer=getattr(args, "reviewer", None),
        progress_digest=progress_digest,
        progress_digest_is_current=True,
    )
    if not has_progress:
        app.save()
    token = secrets.token_urlsafe(24)
    server = HTTPServer(("127.0.0.1", args.port), _create_handler(app, token))
    host, port = cast(tuple[str, int], server.server_address[:2])
    url = f"http://{host}:{port}/?token={token}"
    print(f"Local label review: {url}", flush=True)
    if not args.no_browser:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Local label review stopped.", file=sys.stderr)
    finally:
        server.server_close()


def add_label_review_command(
    commands: argparse._SubParsersAction[argparse.ArgumentParser],
) -> None:
    labels = commands.add_parser("labels", help="review organizer labels locally")
    subcommands = labels.add_subparsers(dest="labels_command", required=True)
    add_catalog_command(subcommands)
    review = subcommands.add_parser(
        "review",
        help="review detected intervals in a local browser and export source-bound labels",
    )
    review.add_argument("--comparison-inventory", type=Path)
    review.add_argument("--review-rule", help="organizer-approved contextual event rule to display")
    review.add_argument(
        "--reviewer", help="prefill the named reviewer; saved reviewer takes precedence"
    )
    review.add_argument("--source", type=Path, required=True)
    review.add_argument("--spec", type=Path, required=True)
    review.add_argument("--events", type=Path, required=True)
    review.add_argument("--manifest", type=Path, required=True)
    review.add_argument("--dataset", choices=("kashiwa", "reims"), required=True)
    review.add_argument("--source-id", required=True)
    review.add_argument("--progress", type=Path, required=True)
    review.add_argument("--practice-output", type=Path)
    review.add_argument("--organizer-output", type=Path)
    review.add_argument("--camera-context-manifest", type=Path)
    review.add_argument("--signal-product-manifest", type=Path)
    review.add_argument("--port", type=int, default=0)
    review.add_argument("--no-browser", action="store_true")


def dispatch_label_review_command(args: argparse.Namespace) -> bool:
    if args.command == "labels" and args.labels_command == "catalog":
        catalog_command(args)
        return True
    if args.command == "labels" and args.labels_command == "review":
        if args.port < 0 or args.port > 65535:
            raise CivError("local review port must be between 0 and 65535")
        review_command(args)
        return True
    return False
