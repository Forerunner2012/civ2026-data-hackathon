from __future__ import annotations

import math
import re
import shutil
from collections import defaultdict
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import Any

from celpy import CELEvalError, CELParseError, Environment, celtypes
from celpy.adapter import json_to_cel
from mcap.exceptions import McapError
from mcap.reader import make_reader

from civ_workshop.artifacts import canonical_json, file_sha256
from civ_workshop.errors import CivError
from civ_workshop.event_spec import load_event_spec
from civ_workshop.inspection import MessageDecoder, extract_field
from civ_workshop.models import EventRecord, EventSpec, Interval, SignalBinding
from civ_workshop.resources import PointResource, load_point_resources, minimum_distance_m
from civ_workshop.submission_extension import (
    EXTENSION_CONTRACT,
    EXTENSION_MANIFEST_PATH,
    ExtensionEntry,
    load_extension_entries,
    media_type_for,
)


@dataclass(frozen=True)
class SignalHit:
    timestamp_ns: int
    values: dict[str, object]


@dataclass(frozen=True)
class DetectedInterval:
    interval: Interval
    trigger_values: dict[str, object]


def _cel_evaluation_diagnostic(error: CELEvalError, timestamp_ns: int) -> str:
    detail = str(error)
    missing = re.search(r"undeclared reference to '([^']+)'", detail)
    if missing:
        return (
            f"CEL condition references unknown name '{missing.group(1)}' at {timestamp_ns} ns; "
            "bind it under signals or derive"
        )
    if "modulus or divide by zero" in detail:
        return (
            f"CEL arithmetic error at {timestamp_ns} ns: division or modulus by zero; "
            "change the divisor"
        )
    if (
        "no such overload" in detail
        and "celtypes.IntType" in detail
        and "celtypes.DoubleType" in detail
    ):
        return (
            f"CEL type error at {timestamp_ns} ns: int and double are not implicitly coerced; "
            "use int(...) or double(...) explicitly"
        )
    return f"CEL evaluation failed at {timestamp_ns} ns"


def _validate_boolean_literal_comparisons(
    condition: str, values: dict[str, object], timestamp_ns: int
) -> None:
    comparisons = re.findall(
        r"\b([A-Za-z_][A-Za-z0-9_]*)\s*(?:==|!=)\s*(true|false)\b",
        condition,
    )
    comparisons.extend(
        (name, literal)
        for literal, name in re.findall(
            r"\b(true|false)\s*(?:==|!=)\s*([A-Za-z_][A-Za-z0-9_]*)\b",
            condition,
        )
    )
    for name, literal in comparisons:
        if name in values and not isinstance(values[name], bool):
            raise CivError(
                f"CEL type error at {timestamp_ns} ns: '{name}' must be bool when compared "
                f"with {literal}; use an explicit numeric comparison"
            )


def _validate_cel_expression(expression: Any) -> None:
    unsupported_operators = {
        "multiplication_div": "/",
        "multiplication_mod": "%",
        "relation_in": "in",
    }
    for node in expression.iter_subtrees():
        node_type = str(node.data)
        operator = unsupported_operators.get(node_type)
        if operator is not None:
            if operator == "in":
                raise CivError(
                    "CEL operator 'in' is not supported; "
                    "use logical and scalar comparison operators"
                )
            raise CivError(
                f"CEL operator '{operator}' is not supported; "
                "use +, -, *, comparisons, or derive"
            )
        if node_type == "expr" and len(node.children) == 3:
            raise CivError(
                "CEL operator '?:' is not supported; "
                "express the decision with &&, ||, and !"
            )
        if node_type == "ident_arg":
            function_name = str(node.children[0])
            if function_name not in {"int", "double"}:
                raise CivError(
                    f"CEL function '{function_name}' is not supported; "
                    "use only int(...) or double(...) conversions"
                )


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


def _evaluate_hits(
    spec: EventSpec, bag_path: Path, resources: dict[str, PointResource]
) -> list[SignalHit]:
    try:
        environment = Environment()
        expression = environment.compile(spec.condition)
        _validate_cel_expression(expression)
        program = environment.program(expression)
    except CELParseError as error:
        raise CivError(
            f"invalid CEL condition at line {error.line}, column {error.column}; "
            "correct the expression syntax"
        ) from error

    bindings_by_topic: dict[str, list[tuple[str, SignalBinding]]] = defaultdict(list)
    for name, binding in spec.signals.items():
        bindings_by_topic[binding.topic].append((name, binding))
    latest: dict[str, object] = {}
    derived: dict[str, float] = {}
    seen_topics: set[str] = set()
    hits: list[SignalHit] = []
    decoder = MessageDecoder()
    try:
        with bag_path.open("rb") as stream:
            reader = make_reader(stream, validate_crcs=True)
            for schema, channel, message in reader.iter_messages(
                topics=sorted(bindings_by_topic)
            ):
                seen_topics.add(channel.topic)
                payload = decoder.decode(schema, channel, message.data)
                changed: set[str] = set()
                for signal_name, binding in bindings_by_topic[channel.topic]:
                    latest[signal_name] = extract_field(
                        payload, binding.field, f"signal {signal_name}"
                    )
                    changed.add(signal_name)
                if len(latest) != len(spec.signals):
                    continue
                for derivation in spec.derivations:
                    if not any(source in changed for source in derivation.sources):
                        continue
                    available_values = {**latest, **derived}
                    numeric_values: list[float] = []
                    for source in derivation.sources:
                        source_value = available_values[source]
                        if isinstance(source_value, bool) or not isinstance(
                            source_value, (int, float)
                        ):
                            raise CivError(
                                f"derive.{derivation.name}.from '{source}' must produce "
                                "a finite number"
                            )
                        numeric_value = float(source_value)
                        if not math.isfinite(numeric_value):
                            raise CivError(
                                f"derive.{derivation.name}.from '{source}' must produce "
                                "a finite number"
                            )
                        numeric_values.append(numeric_value)
                    if derivation.operation == "ewma":
                        previous = derived.get(derivation.name)
                        alpha = derivation.alpha
                        if alpha is None:
                            raise CivError(f"derive.{derivation.name}.alpha is required for ewma")
                        derived[derivation.name] = (
                            numeric_values[0]
                            if previous is None
                            else alpha * numeric_values[0] + (1 - alpha) * previous
                        )
                    elif derivation.operation == "magnitude":
                        derived[derivation.name] = math.sqrt(
                            sum(value * value for value in numeric_values)
                        )
                    else:
                        resource_name = derivation.resource
                        if resource_name is None:
                            raise CivError(
                                f"derive.{derivation.name}.resource is required for "
                                "min_distance_to"
                            )
                        derived[derivation.name] = minimum_distance_m(
                            resources[resource_name],
                            numeric_values[0],
                            numeric_values[1],
                            derivation.name,
                        )
                    if not math.isfinite(derived[derivation.name]):
                        raise CivError(
                            f"derive.{derivation.name} produced a non-finite result; "
                            "check its inputs and parameters"
                        )
                    changed.add(derivation.name)
                if len(derived) != len(spec.derivations):
                    continue
                values = {**latest, **derived}
                null_inputs = sorted(name for name, value in values.items() if value is None)
                if null_inputs:
                    raise CivError(
                        f"CEL input '{null_inputs[0]}' is null at {message.log_time} ns; "
                        "bind a non-null field or derive a fallback"
                    )
                for name, value in sorted(values.items()):
                    supported = (
                        isinstance(value, (bool, int))
                        or (isinstance(value, float) and math.isfinite(value))
                    )
                    if not supported:
                        value_type = "string" if isinstance(value, str) else type(value).__name__
                        if isinstance(value, float):
                            value_type = "non-finite double"
                        raise CivError(
                            f"CEL input '{name}' has unsupported type {value_type} at "
                            f"{message.log_time} ns; bind a bool, int, or finite double"
                        )
                _validate_boolean_literal_comparisons(spec.condition, values, message.log_time)
                try:
                    activation = {name: json_to_cel(value) for name, value in values.items()}
                    condition_result = program.evaluate(activation)
                except CELEvalError as error:
                    raise CivError(_cel_evaluation_diagnostic(error, message.log_time)) from error
                if not isinstance(condition_result, celtypes.BoolType):
                    result_type = type(condition_result).__name__.removesuffix("Type").lower()
                    raise CivError(
                        f"CEL condition returned {result_type} at {message.log_time} ns; "
                        "make the condition return bool"
                    )
                matches = bool(condition_result)
                if matches:
                    hits.append(SignalHit(message.log_time, values))
    except (OSError, McapError) as error:
        raise CivError(f"cannot detect events in {bag_path}: {error}") from error

    missing_topics = sorted(set(bindings_by_topic) - seen_topics)
    if missing_topics:
        raise CivError(f"EventSpec topics not found in bag: {', '.join(missing_topics)}")
    return hits


def _event_records(
    spec: EventSpec,
    spec_hash: str,
    bag_hash: str,
    hits: list[SignalHit],
    resources: dict[str, PointResource],
) -> list[EventRecord]:
    records: list[EventRecord] = []
    provenance = f"{bag_hash}:{spec_hash}"
    if resources:
        resource_hashes = ":".join(
            resource.sha256 for _, resource in sorted(resources.items())
        )
        provenance = f"{provenance}:{resource_hashes}"
    for detected in _event_segments(hits, spec):
        interval = detected.interval
        identity = sha256(
            f"{provenance}:{interval.start_ns}:{interval.end_ns}".encode()
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
    resources = load_point_resources(spec_path, spec.resources)
    if not bag_path.is_file():
        raise CivError(f"bag does not exist: {bag_path}")
    bag_hash = file_sha256(bag_path)
    spec_hash = file_sha256(spec_path)
    events = _event_records(
        spec,
        spec_hash,
        bag_hash,
        _evaluate_hits(spec, bag_path, resources),
        resources,
    )
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

    extension_entries = [
        entry for entry in load_extension_entries(output) if entry.kind != "external-resource"
    ]
    try:
        for _, resource in sorted(resources.items()):
            source = (spec_path.parent / Path(resource.binding.path)).resolve()
            destination = detector_directory / Path(resource.binding.path)
            destination.parent.mkdir(parents=True, exist_ok=True)
            if destination.resolve() != source:
                shutil.copyfile(source, destination)
            extension_entries.append(
                ExtensionEntry(
                    path=destination.relative_to(output).as_posix(),
                    kind="external-resource",
                    sha256=resource.sha256,
                    media_type=media_type_for(destination),
                )
            )
        if extension_entries:
            extension_entries = sorted(extension_entries)
            extension_manifest = output / EXTENSION_MANIFEST_PATH
            extension_manifest.parent.mkdir(parents=True, exist_ok=True)
            extension_document = {
                "contract": EXTENSION_CONTRACT,
                "entries": [entry.as_dict() for entry in extension_entries],
            }
            extension_manifest.write_text(
                f"{canonical_json(extension_document)}\n",
                encoding="utf-8",
                newline="\n",
            )
    except OSError as error:
        raise CivError(
            f"cannot stage EventSpec resources into working directory: {error}"
        ) from error

    events_text = "".join(f"{canonical_json(event.as_dict())}\n" for event in events)
    events_path = output / "events.jsonl"
    events_path.write_text(events_text, encoding="utf-8", newline="\n")
    manifest: dict[str, object] = {
        "contract": "civ.run-manifest/v2",
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
    if resources:
        manifest["resources"] = [
            resource.provenance() for _, resource in sorted(resources.items())
        ]
    (output / "run-manifest.json").write_text(
        f"{canonical_json(manifest)}\n", encoding="utf-8", newline="\n"
    )
    return plan
