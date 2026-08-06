from __future__ import annotations

import json
import re
from collections import defaultdict
from hashlib import sha256
from pathlib import Path
from typing import Any

from mcap.exceptions import McapError
from mcap.reader import make_reader

from civ_workshop.artifacts import require_mapping
from civ_workshop.errors import CivError


def _schema_fields(schema_data: bytes) -> list[str]:
    document = json.loads(schema_data)
    if not isinstance(document, dict):
        return []
    properties = document.get("properties", {})
    if not isinstance(properties, dict):
        return []
    return sorted(str(name) for name in properties)


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
