from __future__ import annotations

import json
import shutil
from collections import defaultdict
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path

from celpy import CELEvalError, CELParseError, Environment
from mcap.exceptions import McapError
from mcap.reader import make_reader

from civ_workshop.artifacts import canonical_json, file_sha256
from civ_workshop.errors import CivError
from civ_workshop.event_spec import load_event_spec
from civ_workshop.models import EventRecord, EventSpec, Interval, SignalBinding


@dataclass(frozen=True)
class SignalHit:
    timestamp_ns: int
    values: dict[str, object]


@dataclass(frozen=True)
class DetectedInterval:
    interval: Interval
    trigger_values: dict[str, object]


def _extract_field(message: object, field: str, signal_name: str) -> object:
    value = message
    for part in field.split("."):
        if not isinstance(value, dict) or part not in value:
            raise CivError(f"signal {signal_name} field not found in JSON message: {field}")
        value = value[part]
    return value


def _event_segments(hits: list[SignalHit], spec: EventSpec) -> list[DetectedInterval]:
    if not hits:
        return []
    segments: list[DetectedInterval] = []
    start = hits[0].timestamp_ns
    previous = hits[0].timestamp_ns
    trigger_values = hits[0].values
    for hit in hits[1:]:
        if hit.timestamp_ns - previous <= spec.merge_gap_ns:
            previous = hit.timestamp_ns
            continue
        segments.append(DetectedInterval(Interval(start, previous), trigger_values))
        start = hit.timestamp_ns
        previous = hit.timestamp_ns
        trigger_values = hit.values
    segments.append(DetectedInterval(Interval(start, previous), trigger_values))
    return [
        segment
        for segment in segments
        if spec.min_duration_ns
        <= segment.interval.end_ns - segment.interval.start_ns
        <= spec.max_duration_ns
    ]


def _evaluate_hits(spec: EventSpec, bag_path: Path) -> list[SignalHit]:
    try:
        environment = Environment()
        program = environment.program(environment.compile(spec.condition))
    except CELParseError as error:
        raise CivError(f"invalid CEL condition: {error}") from error

    bindings_by_topic: dict[str, list[tuple[str, SignalBinding]]] = defaultdict(list)
    for name, binding in spec.signals.items():
        bindings_by_topic[binding.topic].append((name, binding))
    latest: dict[str, object] = {}
    seen_topics: set[str] = set()
    hits: list[SignalHit] = []
    try:
        with bag_path.open("rb") as stream:
            reader = make_reader(stream, validate_crcs=True)
            for _, channel, message in reader.iter_messages(topics=sorted(bindings_by_topic)):
                seen_topics.add(channel.topic)
                if channel.message_encoding != "json":
                    raise CivError(
                        f"topic {channel.topic} uses unsupported message encoding: "
                        f"{channel.message_encoding}"
                    )
                try:
                    payload = json.loads(message.data)
                except (UnicodeDecodeError, json.JSONDecodeError) as error:
                    raise CivError(f"topic {channel.topic} contains invalid JSON") from error
                for signal_name, binding in bindings_by_topic[channel.topic]:
                    latest[signal_name] = _extract_field(payload, binding.field, signal_name)
                if len(latest) != len(spec.signals):
                    continue
                try:
                    matches = bool(program.evaluate(dict(latest)))
                except CELEvalError as error:
                    raise CivError(
                        f"CEL evaluation failed at {message.log_time}: {error}"
                    ) from error
                if matches:
                    hits.append(SignalHit(message.log_time, dict(latest)))
    except (OSError, McapError) as error:
        raise CivError(f"cannot detect events in {bag_path}: {error}") from error

    missing_topics = sorted(set(bindings_by_topic) - seen_topics)
    if missing_topics:
        raise CivError(f"EventSpec topics not found in bag: {', '.join(missing_topics)}")
    return hits


def _event_records(
    spec: EventSpec, spec_hash: str, bag_hash: str, hits: list[SignalHit]
) -> list[EventRecord]:
    records: list[EventRecord] = []
    for detected in _event_segments(hits, spec):
        interval = detected.interval
        identity = sha256(
            f"{bag_hash}:{spec_hash}:{interval.start_ns}:{interval.end_ns}".encode()
        ).hexdigest()
        records.append(
            EventRecord(
                event_id=identity,
                bag_sha256=bag_hash,
                spec_sha256=spec_hash,
                interval=interval,
                trigger_values=detected.trigger_values,
            )
        )
    return records


def detect_events(
    spec_path: Path, bag_path: Path, output: Path, *, dry_run: bool = False
) -> dict[str, object]:
    spec = load_event_spec(spec_path)
    if not bag_path.is_file():
        raise CivError(f"bag does not exist: {bag_path}")
    bag_hash = file_sha256(bag_path)
    spec_hash = file_sha256(spec_path)
    events = _event_records(spec, spec_hash, bag_hash, _evaluate_hits(spec, bag_path))
    plan: dict[str, object] = {"dry_run": dry_run, "event_count": len(events)}
    if dry_run:
        return plan

    output.mkdir(parents=True, exist_ok=True)
    detector_directory = output / "detector"
    detector_directory.mkdir(exist_ok=True)
    copied_spec = detector_directory / spec_path.name
    try:
        if copied_spec.resolve() != spec_path.resolve():
            shutil.copyfile(spec_path, copied_spec)
    except OSError as error:
        raise CivError(f"cannot copy EventSpec into working directory: {error}") from error

    events_text = "".join(f"{canonical_json(event.as_dict())}\n" for event in events)
    events_path = output / "events.jsonl"
    events_path.write_text(events_text, encoding="utf-8", newline="\n")
    manifest = {
        "contract": "civ.run-manifest/v1alpha1",
        "events": {
            "count": len(events),
            "name": "events.jsonl",
            "sha256": file_sha256(events_path),
        },
        "evidence": {
            "after_ns": spec.evidence_after_ns,
            "before_ns": spec.evidence_before_ns,
            "topics": list(spec.evidence_topics),
        },
        "source": {"name": bag_path.name, "sha256": bag_hash},
        "spec": {"contract": spec.contract, "name": spec.name, "sha256": spec_hash},
    }
    (output / "run-manifest.json").write_text(
        f"{canonical_json(manifest)}\n", encoding="utf-8", newline="\n"
    )
    return plan
