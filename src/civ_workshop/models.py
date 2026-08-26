from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, order=True)
class Interval:
    start_ns: int
    end_ns: int


@dataclass(frozen=True)
class EventRecord:
    event_id: str
    bag_sha256: str
    spec_sha256: str
    interval: Interval
    trigger_values: dict[str, object]

    def as_dict(self) -> dict[str, object]:
        return {
            "bag_sha256": self.bag_sha256,
            "end_ns": self.interval.end_ns,
            "event_id": self.event_id,
            "spec_sha256": self.spec_sha256,
            "start_ns": self.interval.start_ns,
            "trigger_values": self.trigger_values,
        }


@dataclass(frozen=True)
class SignalBinding:
    topic: str
    field: str


@dataclass(frozen=True)
class Derivation:
    name: str
    operation: str
    sources: tuple[str, ...]
    alpha: float | None = None


@dataclass(frozen=True)
class EventSpec:
    contract: str
    name: str
    signals: dict[str, SignalBinding]
    derivations: tuple[Derivation, ...]
    condition: str
    min_duration_ns: int
    merge_gap_ns: int
    max_duration_ns: int
    evidence_before_ns: int
    evidence_after_ns: int
    evidence_topics: tuple[str, ...]
