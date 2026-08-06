from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from yaml import YAMLError

from civ_workshop.artifacts import require_mapping, require_string
from civ_workshop.errors import CivError
from civ_workshop.models import EventSpec, SignalBinding


def _duration_ns(value: object, context: str) -> int:
    text = require_string(value, context)
    units = {"ns": 1, "ms": 1_000_000, "s": 1_000_000_000}
    for suffix in ("ms", "ns", "s"):
        if text.endswith(suffix):
            try:
                amount = float(text[: -len(suffix)])
            except ValueError as error:
                raise CivError(f"{context} has an invalid duration: {text}") from error
            duration = int(amount * units[suffix])
            if duration < 0:
                raise CivError(f"{context} must not be negative")
            return duration
    raise CivError(f"{context} must use ns, ms, or s units")


def _signal_bindings(root: dict[str, Any]) -> dict[str, SignalBinding]:
    raw_signals = require_mapping(root.get("signals"), "EventSpec signals")
    if not raw_signals:
        raise CivError("EventSpec signals must not be empty")
    signals: dict[str, SignalBinding] = {}
    for signal_name, raw_binding in raw_signals.items():
        binding = require_mapping(raw_binding, f"signal {signal_name}")
        signals[signal_name] = SignalBinding(
            topic=require_string(binding.get("topic"), f"signal {signal_name} topic"),
            field=require_string(binding.get("field"), f"signal {signal_name} field"),
        )
    return signals


def load_event_spec(path: Path) -> EventSpec:
    if not path.is_file():
        raise CivError(f"EventSpec does not exist: {path}")
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, YAMLError) as error:
        raise CivError(f"cannot read EventSpec {path}: {error}") from error

    root = require_mapping(raw, "EventSpec")
    contract = require_string(root.get("spec"), "EventSpec spec")
    if contract != "civ.eventspec/v1alpha1":
        raise CivError(f"unsupported EventSpec contract: {contract}")
    timing = require_mapping(root.get("timing"), "EventSpec timing")
    min_duration_ns = _duration_ns(timing.get("min_duration"), "timing.min_duration")
    max_duration_ns = _duration_ns(timing.get("max_duration"), "timing.max_duration")
    if min_duration_ns > max_duration_ns:
        raise CivError("timing.min_duration must not exceed timing.max_duration")
    evidence = require_mapping(root.get("evidence"), "EventSpec evidence")
    raw_topics = evidence.get("topics")
    if not isinstance(raw_topics, list) or not raw_topics:
        raise CivError("evidence.topics must be a non-empty list")

    return EventSpec(
        contract=contract,
        name=require_string(root.get("name"), "EventSpec name"),
        signals=_signal_bindings(root),
        condition=require_string(root.get("condition"), "EventSpec condition"),
        min_duration_ns=min_duration_ns,
        merge_gap_ns=_duration_ns(timing.get("merge_gap"), "timing.merge_gap"),
        max_duration_ns=max_duration_ns,
        evidence_before_ns=_duration_ns(evidence.get("before"), "evidence.before"),
        evidence_after_ns=_duration_ns(evidence.get("after"), "evidence.after"),
        evidence_topics=tuple(
            sorted(require_string(topic, "evidence topic") for topic in raw_topics)
        ),
    )
