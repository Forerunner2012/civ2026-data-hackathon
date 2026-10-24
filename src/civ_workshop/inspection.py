from __future__ import annotations

import json
import re
from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import Any

from mcap.exceptions import McapError
from mcap.reader import make_reader
from mcap_ros2.decoder import DecoderFactory, McapROS2DecodeError

from civ_workshop.artifacts import require_mapping
from civ_workshop.errors import CivError, SourceDataError
from civ_workshop.schema_pins import golden_schema_diagnostic


@dataclass(frozen=True)
class SampleValue:
    timestamp_ns: int
    value: object


class MessageDecoder:
    """Decode the message encodings supported by the participant workflow."""

    def __init__(self) -> None:
        self._ros2_factory = DecoderFactory()
        self._ros2_decoders: dict[int, Callable[[bytes], object]] = {}

    def decode(self, schema: Any, channel: Any, data: bytes) -> object:
        if channel.message_encoding == "json":
            try:
                return json.loads(data)
            except (UnicodeDecodeError, json.JSONDecodeError) as error:
                raise SourceDataError(f"topic {channel.topic} contains invalid JSON") from error
        if channel.message_encoding != "cdr":
            raise SourceDataError(
                f"topic {channel.topic} uses unsupported message encoding: "
                f"{channel.message_encoding}"
            )

        decoder = self._ros2_decoders.get(channel.id)
        if decoder is None:
            try:
                decoder = self._ros2_factory.decoder_for(channel.message_encoding, schema)
            except Exception as error:
                # The third-party parser raises public, built-in, and private
                # vendored exceptions for malformed schemas.
                raise SourceDataError(
                    f"topic {channel.topic} has invalid ROS 2 schema; "
                    f"provide a valid embedded ros2msg definition: {error}"
                ) from error
            if decoder is None:
                schema_encoding = schema.encoding if schema is not None else "missing"
                raise SourceDataError(
                    f"topic {channel.topic} uses unsupported CDR schema encoding: "
                    f"{schema_encoding}"
                )
            self._ros2_decoders[channel.id] = decoder
        try:
            return decoder(data)
        except McapROS2DecodeError as error:
            raise SourceDataError(
                f"topic {channel.topic} contains invalid ROS 2 CDR data: {error}"
            ) from error


def extract_field(message: object, field: str, subject: str) -> object:
    value = message
    for part in field.split("."):
        if isinstance(value, dict) and part in value:
            value = value[part]
        elif hasattr(value, part):
            value = getattr(value, part)
        else:
            raise CivError(f"{subject} field not found in decoded message: {field}")
    return value


def _schema_fields(schema_data: bytes) -> list[str]:
    document = json.loads(schema_data)
    if not isinstance(document, dict):
        return []

    def leaf_paths(schema: object, prefix: str) -> list[str]:
        if not isinstance(schema, dict):
            return [prefix] if prefix else []
        properties = schema.get("properties")
        if not isinstance(properties, dict) or not properties:
            return [prefix] if prefix else []
        fields: list[str] = []
        for raw_name, child_schema in properties.items():
            name = str(raw_name)
            path = f"{prefix}.{name}" if prefix else name
            fields.extend(leaf_paths(child_schema, path))
        return fields

    return sorted(leaf_paths(document, ""))


ROS_PRIMITIVES = {
    "bool",
    "byte",
    "char",
    "float32",
    "float64",
    "int8",
    "int16",
    "int32",
    "int64",
    "string",
    "uint8",
    "uint16",
    "uint32",
    "uint64",
    "wstring",
}


def _normalized_ros_type(type_name: str) -> str:
    return type_name.replace("/msg/", "/")


def _ros2msg_fields(schema_name: str, schema_data: bytes) -> list[str]:
    root_type = _normalized_ros_type(schema_name)
    definitions: dict[str, list[tuple[str, str]]] = {root_type: []}
    current_type = root_type
    for raw_line in schema_data.decode().splitlines():
        line = raw_line.split("#", 1)[0].strip()
        if not line:
            continue
        if line.startswith("="):
            continue
        if line.startswith("MSG:"):
            current_type = _normalized_ros_type(line.removeprefix("MSG:").strip())
            definitions.setdefault(current_type, [])
            continue
        if "=" in line:
            continue
        parts = line.split()
        if len(parts) == 2:
            definitions[current_type].append((parts[0], parts[1]))

    def leaf_paths(
        type_name: str, prefix: str, ancestors: frozenset[str]
    ) -> list[str]:
        fields: list[str] = []
        for raw_field_type, field_name in definitions.get(type_name, []):
            path = f"{prefix}.{field_name}" if prefix else field_name
            if re.search(r"\[.*\]$", raw_field_type):
                fields.append(path)
                continue
            field_type = raw_field_type
            if field_type in ROS_PRIMITIVES:
                fields.append(path)
                continue
            normalized = _normalized_ros_type(field_type)
            if "/" not in normalized:
                package = type_name.split("/", 1)[0]
                normalized = f"{package}/{normalized}"
            if normalized not in definitions or normalized in ancestors:
                fields.append(path)
                continue
            fields.extend(leaf_paths(normalized, path, ancestors | {normalized}))
        return fields

    return sorted(leaf_paths(root_type, "", frozenset({root_type})))


def inspect_bag(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise CivError(f"bag does not exist: {path}")

    topic_counts: dict[str, int] = defaultdict(int)
    topic_details: dict[str, dict[str, Any]] = {}
    warnings: set[str] = set()
    start_time: int | None = None
    end_time: int | None = None

    try:
        with path.open("rb") as stream:
            reader = make_reader(stream, validate_crcs=True)
            for schema, channel, message in reader.iter_messages():
                start_time = (
                    message.log_time if start_time is None else min(start_time, message.log_time)
                )
                end_time = message.log_time if end_time is None else max(end_time, message.log_time)
                topic_counts[channel.topic] += 1

                fields: list[str] = []
                schema_id = 0
                schema_name = ""
                schema_encoding = ""
                schema_sha256 = ""
                if schema is None:
                    warnings.add(f"{channel.topic}: no embedded schema")
                else:
                    pin_diagnostic = golden_schema_diagnostic(channel.topic, schema)
                    if pin_diagnostic is not None:
                        warnings.add(pin_diagnostic)
                    schema_id = schema.id
                    schema_name = schema.name
                    schema_encoding = schema.encoding
                    schema_sha256 = sha256(schema.data).hexdigest()
                    if schema.encoding == "jsonschema":
                        try:
                            fields = _schema_fields(schema.data)
                        except (UnicodeDecodeError, json.JSONDecodeError):
                            warnings.add(f"{channel.topic}: invalid JSON schema")
                    elif schema.encoding == "ros2msg":
                        try:
                            fields = _ros2msg_fields(schema.name, schema.data)
                        except UnicodeDecodeError:
                            warnings.add(f"{channel.topic}: invalid ros2msg schema")
                    else:
                        encoding = schema.encoding or "unknown"
                        warnings.add(f"{channel.topic}: field discovery unsupported for {encoding}")

                topic_details[channel.topic] = {
                    "fields": fields,
                    "message_encoding": channel.message_encoding,
                    "schema_encoding": schema_encoding,
                    "schema_id": schema_id,
                    "schema_name": schema_name,
                    "schema_sha256": schema_sha256,
                    "topic": channel.topic,
                }
    except (OSError, McapError) as error:
        raise CivError(f"cannot inspect bag {path}: {error}") from error

    if start_time is None or end_time is None:
        raise CivError(f"bag contains no messages: {path}")

    duration_ns = end_time - start_time
    duration_seconds = duration_ns / 1_000_000_000
    topics: list[dict[str, Any]] = []
    for topic in sorted(topic_details):
        detail = topic_details[topic]
        count = topic_counts[topic]
        topics.append(
            {
                **detail,
                "message_count": count,
                "message_rate_hz": round(count / duration_seconds, 6) if duration_seconds else 0.0,
            }
        )

    return {
        "duration_ns": duration_ns,
        "end_time_ns": end_time,
        "start_time_ns": start_time,
        "topics": topics,
        "warnings": sorted(warnings),
    }


def render_inventory(path: Path, inventory: dict[str, Any]) -> str:
    start = int(inventory["start_time_ns"])
    end = int(inventory["end_time_ns"])
    duration = int(inventory["duration_ns"])
    lines = [
        f"Bag: {path.name}",
        f"Duration: {duration / 1_000_000_000:.3f}s ({start}..{end} ns)",
        "Topics:",
    ]
    for raw_topic in inventory["topics"]:
        topic = require_mapping(raw_topic, "inspection topic")
        fields = ", ".join(str(field) for field in topic["fields"])
        rate = float(topic["message_rate_hz"])
        lines.append(
            f"  {topic['topic']}  {topic['message_count']} messages  {rate:g} Hz  "
            f"{topic['schema_name']}  fields: {fields or '-'}"
        )
    for warning in inventory["warnings"]:
        lines.append(f"Warning: {warning}")
    return "\n".join(lines) + "\n"


def sample_bag(
    path: Path,
    topic: str,
    field: str,
    *,
    start_ns: int | None = None,
    end_ns: int | None = None,
    limit: int = 20,
) -> dict[str, Any]:
    if limit <= 0:
        raise CivError("sample limit must be greater than zero")
    if start_ns is not None and start_ns < 0:
        raise CivError("sample start must be zero or greater")
    if end_ns is not None and end_ns < 0:
        raise CivError("sample end must be zero or greater")
    if start_ns is not None and end_ns is not None and start_ns > end_ns:
        raise CivError("sample start must be less than or equal to end")
    if not path.is_file():
        raise CivError(f"bag does not exist: {path}")

    decoder = MessageDecoder()
    values: list[SampleValue] = []
    saw_topic = False
    field_checked = False
    try:
        with path.open("rb") as stream:
            reader = make_reader(stream, validate_crcs=True)
            for schema, channel, message in reader.iter_messages(topics=[topic]):
                saw_topic = True
                if not field_checked:
                    if schema is None:
                        raise CivError(
                            f"topic {topic} has no embedded schema; choose a discoverable topic"
                        )
                    pin_diagnostic = golden_schema_diagnostic(topic, schema)
                    if pin_diagnostic is not None:
                        raise CivError(
                            f"{pin_diagnostic}; use the pinned golden-path bag/schema source"
                        )
                    if schema.encoding == "jsonschema":
                        try:
                            fields = _schema_fields(schema.data)
                        except (UnicodeDecodeError, json.JSONDecodeError) as error:
                            raise CivError(f"topic {topic} has an invalid JSON schema") from error
                    elif schema.encoding == "ros2msg":
                        try:
                            fields = _ros2msg_fields(schema.name, schema.data)
                        except UnicodeDecodeError as error:
                            raise CivError(
                                f"topic {topic} has an invalid ros2msg schema"
                            ) from error
                    else:
                        encoding = schema.encoding or "unknown"
                        warning = ""
                        if encoding == "ros2idl":
                            warning = "; dynamic IDL decoding remains unsupported"
                        raise CivError(
                            f"field discovery unsupported for {encoding} on topic {topic}{warning}"
                        )
                    if field not in fields:
                        raise CivError(
                            f"field not found on topic {topic}: {field}; run civ inspect"
                        )
                    field_checked = True

                if start_ns is not None and message.log_time < start_ns:
                    continue
                if end_ns is not None and message.log_time > end_ns:
                    continue
                payload = decoder.decode(schema, channel, message.data)
                values.append(
                    SampleValue(
                        timestamp_ns=message.log_time,
                        value=extract_field(payload, field, f"topic {topic}"),
                    )
                )
                if len(values) == limit:
                    break
    except (OSError, McapError) as error:
        raise CivError(f"cannot sample bag {path}: {error}") from error

    if not saw_topic:
        raise CivError(f"topic not found in bag: {topic}")
    if not values:
        raise CivError(f"sample window contains no messages for topic {topic}")
    return {
        "bag": path.name,
        "field": field,
        "samples": [
            {"timestamp_ns": sample.timestamp_ns, "value": sample.value}
            for sample in values
        ],
        "topic": topic,
        "window": {"end_ns": end_ns, "limit": limit, "start_ns": start_ns},
    }


def render_samples(result: dict[str, Any]) -> str:
    window = require_mapping(result["window"], "sample window")
    start_ns = window["start_ns"]
    end_ns = window["end_ns"]
    if start_ns is None and end_ns is None:
        bounds = "all timestamps"
    elif start_ns is None:
        bounds = f"through {end_ns} ns"
    elif end_ns is None:
        bounds = f"from {start_ns} ns"
    else:
        bounds = f"{start_ns}..{end_ns} ns"
    lines = [
        f"Bag: {result['bag']}",
        f"Signal: {result['topic']}.{result['field']}",
        f"Window: {bounds}, first {window['limit']} samples",
        "Samples:",
    ]
    for raw_sample in result["samples"]:
        sample = require_mapping(raw_sample, "sample")
        value = json.dumps(sample["value"], sort_keys=True, separators=(",", ":"))
        lines.append(f"  {sample['timestamp_ns']} ns  {value}")
    return "\n".join(lines) + "\n"
