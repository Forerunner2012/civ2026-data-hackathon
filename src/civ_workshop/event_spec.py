from __future__ import annotations

from pathlib import Path, PurePosixPath
from typing import Any

import yaml
from yaml import YAMLError
from yaml.nodes import MappingNode, Node, ScalarNode

from civ_workshop.artifacts import require_mapping, require_string
from civ_workshop.errors import CivError
from civ_workshop.models import Derivation, EventSpec, ResourceBinding, SignalBinding


def _duplicate_derive_name(document: Node | None) -> str | None:
    if not isinstance(document, MappingNode):
        return None
    derive_node: Node | None = None
    for key, value in document.value:
        if isinstance(key, ScalarNode) and key.value == "derive":
            derive_node = value
            break
    if not isinstance(derive_node, MappingNode):
        return None
    seen: set[str] = set()
    for key, _ in derive_node.value:
        if not isinstance(key, ScalarNode):
            continue
        name = str(key.value)
        if name in seen:
            return name
        seen.add(name)
    return None


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


def _resource_bindings(root: dict[str, Any]) -> tuple[ResourceBinding, ...]:
    raw_resources = root.get("resources")
    if raw_resources is None:
        return ()
    resources = require_mapping(raw_resources, "EventSpec resources")
    if not resources:
        raise CivError("EventSpec resources must not be empty")
    bindings: list[ResourceBinding] = []
    for name, raw_binding in sorted(resources.items()):
        context = f"resources.{name}"
        binding = require_mapping(raw_binding, context)
        path_text = require_string(binding.get("path"), f"{context}.path")
        resource_path = PurePosixPath(path_text)
        invalid_path = (
            "\\" in path_text
            or resource_path.is_absolute()
            or not resource_path.parts
            or any(part in {"", ".", ".."} for part in resource_path.parts)
            or ":" in resource_path.parts[0]
        )
        if invalid_path:
            raise CivError(
                f"{context}.path must be a relative POSIX path inside the EventSpec directory"
            )
        contract = require_string(binding.get("contract"), f"{context}.contract")
        if contract != "civ.point-resource/v1alpha1":
            raise CivError(f"{context}.contract is unsupported: {contract}")
        bindings.append(ResourceBinding(name=name, path=path_text, contract=contract))
    return tuple(bindings)


def _derivations(
    root: dict[str, Any],
    signals: dict[str, SignalBinding],
    resources: tuple[ResourceBinding, ...],
) -> tuple[Derivation, ...]:
    raw_derive = root.get("derive")
    if raw_derive is None:
        return ()
    derive = require_mapping(raw_derive, "EventSpec derive")
    derivations: list[Derivation] = []
    for name, raw_derivation in derive.items():
        context = f"derive.{name}"
        derivation_config = require_mapping(raw_derivation, context)
        operation = require_string(derivation_config.get("op"), f"{context}.op")
        if operation not in {"ewma", "magnitude", "min_distance_to"}:
            raise CivError(
                f"{context}.op has unknown operation '{operation}'; "
                "use one of: ewma, magnitude, min_distance_to"
            )
        raw_sources = derivation_config.get("from")
        sources: tuple[str, ...]
        if operation == "ewma":
            sources = (require_string(raw_sources, f"{context}.from"),)
            raw_alpha = derivation_config.get("alpha")
            if isinstance(raw_alpha, bool) or not isinstance(raw_alpha, (int, float)):
                raise CivError(f"{context}.alpha must be a number greater than 0 and at most 1")
            alpha = float(raw_alpha)
            if not 0 < alpha <= 1:
                raise CivError(f"{context}.alpha must be greater than 0 and at most 1")
            resource = None
        else:
            minimum_sources = 2
            if not isinstance(raw_sources, list) or len(raw_sources) < minimum_sources:
                raise CivError(f"{context}.from must list at least two numeric inputs")
            if operation == "min_distance_to" and len(raw_sources) != 2:
                raise CivError(
                    f"{context}.from must list latitude and longitude exactly once"
                )
            sources = tuple(
                require_string(source, f"{context}.from input") for source in raw_sources
            )
            alpha = None
            if operation == "min_distance_to":
                resource = require_string(
                    derivation_config.get("resource"), f"{context}.resource"
                )
                resource_names = {binding.name for binding in resources}
                if resource not in resource_names:
                    raise CivError(
                        f"{context}.resource references unknown resource '{resource}'; "
                        "define it under resources"
                    )
            else:
                resource = None
        derivations.append(
            Derivation(
                name=name,
                operation=operation,
                sources=sources,
                alpha=alpha,
                resource=resource,
            )
        )
    derived_names = {derivation.name for derivation in derivations}
    for derivation in derivations:
        if derivation.name in signals:
            raise CivError(
                f"derive.{derivation.name} duplicates a signal name; choose a unique derived name"
            )
        unknown_sources = [
            source
            for source in derivation.sources
            if source not in signals and source not in derived_names
        ]
        if unknown_sources:
            raise CivError(
                f"derive.{derivation.name}.from references unknown input '{unknown_sources[0]}'; "
                "bind it under signals or define it under derive"
            )

    ordered: list[Derivation] = []
    available = set(signals)
    pending = list(derivations)
    while pending:
        ready = next(
            (
                derivation
                for derivation in pending
                if all(source in available for source in derivation.sources)
            ),
            None,
        )
        if ready is None:
            cycle = ", ".join(sorted(derivation.name for derivation in pending))
            raise CivError(f"derive dependency cycle contains: {cycle}; remove the cycle")
        ordered.append(ready)
        available.add(ready.name)
        pending.remove(ready)
    return tuple(ordered)


def load_event_spec(path: Path) -> EventSpec:
    if not path.is_file():
        raise CivError(f"EventSpec does not exist: {path}")
    try:
        text = path.read_text(encoding="utf-8")
        document = yaml.compose(text)
        raw = yaml.safe_load(text)
    except (OSError, UnicodeDecodeError, YAMLError) as error:
        raise CivError(f"cannot read EventSpec {path}: {error}") from error

    duplicate_derive_name = _duplicate_derive_name(document)
    if duplicate_derive_name is not None:
        raise CivError(
            f"derive name '{duplicate_derive_name}' is duplicated; keep each derive name once"
        )

    root = require_mapping(raw, "EventSpec")
    contract = require_string(root.get("spec"), "EventSpec spec")
    if contract != "civ.eventspec/v1alpha1":
        raise CivError(f"unsupported EventSpec contract: {contract}")
    if "detector" in root:
        raise CivError(
            "EventSpec detector is reserved; remove detector and use signals, derive, and resources"
        )
    timing = require_mapping(root.get("timing"), "EventSpec timing")
    min_duration_ns = _duration_ns(timing.get("min_duration"), "timing.min_duration")
    max_duration_ns = _duration_ns(timing.get("max_duration"), "timing.max_duration")
    if min_duration_ns > max_duration_ns:
        raise CivError("timing.min_duration must not exceed timing.max_duration")
    evidence = require_mapping(root.get("evidence"), "EventSpec evidence")
    raw_topics = evidence.get("topics")
    if not isinstance(raw_topics, list) or not raw_topics:
        raise CivError("evidence.topics must be a non-empty list")

    signals = _signal_bindings(root)
    resources = _resource_bindings(root)
    return EventSpec(
        contract=contract,
        name=require_string(root.get("name"), "EventSpec name"),
        signals=signals,
        resources=resources,
        derivations=_derivations(root, signals, resources),
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
