from __future__ import annotations

import json
from hashlib import sha256
from pathlib import Path
from typing import Any

from civ_workshop.contracts import require_closed_fields
from civ_workshop.errors import CivError
from civ_workshop.models import EventRecord, Interval


def require_mapping(value: object, context: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise CivError(f"{context} must be a mapping")
    return {str(key): item for key, item in value.items()}


def require_string(value: object, context: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise CivError(f"{context} must be a non-empty string")
    return value.strip()


def file_sha256(path: Path) -> str:
    digest = sha256()
    try:
        with path.open("rb") as stream:
            while chunk := stream.read(1024 * 1024):
                digest.update(chunk)
    except OSError as error:
        raise CivError(f"cannot read {path}: {error}") from error
    return digest.hexdigest()


def canonical_json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def read_json_file(path: Path, context: str) -> dict[str, Any]:
    if not path.is_file():
        raise CivError(f"{context} does not exist: {path}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise CivError(f"cannot read {context} {path}: {error}") from error
    return require_mapping(value, context)


def interval_from_mapping(value: dict[str, Any], context: str) -> Interval:
    start = value.get("start_ns")
    end = value.get("end_ns")
    if isinstance(start, bool) or not isinstance(start, int):
        raise CivError(f"{context} start_ns must be an integer")
    if isinstance(end, bool) or not isinstance(end, int):
        raise CivError(f"{context} end_ns must be an integer")
    if start < 0:
        raise CivError(f"{context} start_ns must be non-negative")
    if end < 0:
        raise CivError(f"{context} end_ns must be non-negative")
    if end <= start:
        raise CivError(f"{context} end_ns must be greater than start_ns")
    return Interval(start_ns=start, end_ns=end)


def read_events(path: Path) -> list[EventRecord]:
    if not path.is_file():
        raise CivError(f"events file does not exist: {path}")
    events: list[EventRecord] = []
    try:
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            if not line.strip():
                continue
            try:
                value = json.loads(line)
            except json.JSONDecodeError as error:
                raise CivError(f"invalid event JSON on line {line_number}: {error}") from error
            context = f"event on line {line_number}"
            event = require_mapping(value, context)
            interval = interval_from_mapping(event, context)
            trigger_values = require_mapping(
                event.get("trigger_values"), f"{context} trigger_values"
            )
            # A candidate record carries no contract; the caller resolves it against the
            # manifest so the enclosing provenance picks the diagnostic. Only a record that
            # claims the stable contract is held to the closed stable field set.
            raw_contract = event.get("contract")
            if raw_contract == "civ.event/v1":
                require_closed_fields(event, kind="event", expected="civ.event/v1")
            events.append(
                EventRecord(
                    contract=raw_contract.strip() if isinstance(raw_contract, str) else "",
                    event_id=require_string(event.get("event_id"), f"{context} event_id"),
                    bag_sha256=require_string(event.get("bag_sha256"), f"{context} bag_sha256"),
                    spec_sha256=require_string(event.get("spec_sha256"), f"{context} spec_sha256"),
                    interval=interval,
                    trigger_values=trigger_values,
                )
            )
    except (OSError, UnicodeDecodeError) as error:
        raise CivError(f"cannot read events {path}: {error}") from error
    return events
