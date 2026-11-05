"""Read-only proposal comparisons; profile agreement never grants review authority."""

from __future__ import annotations

import copy
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any

from civ_workshop.artifacts import (
    file_sha256,
    read_events,
    read_json_file,
    require_mapping,
    require_string,
)
from civ_workshop.errors import CivError
from civ_workshop.event_spec import load_event_spec
from civ_workshop.label_packs import _product_binding
from civ_workshop.resources import load_point_resources

if TYPE_CHECKING:
    from civ_workshop.organizer.label_review import ReviewBinding


def _bounds(record: dict[str, str]) -> tuple[int, int]:
    return int(record["start_ns"]), int(record["end_ns"])


def compare_intervals(
    baseline: list[dict[str, str]], alternative: list[dict[str, str]]
) -> dict[str, Any]:
    """Pair exact geometry first, then positive overlaps by descending intersection.

    This is a discovery display rule, not the frozen evaluator's matching policy.
    """
    left = sorted(baseline, key=lambda r: (*_bounds(r), r["event_id"]))
    right = sorted(alternative, key=lambda r: (*_bounds(r), r["event_id"]))
    pairs: list[tuple[int, int, int, int]] = []
    for i, old in enumerate(left):
        for j, new in enumerate(right):
            a, b = _bounds(old)
            c, d = _bounds(new)
            overlap = min(b, d) - max(a, c)
            if overlap > 0:
                pairs.append((0 if (a, b) == (c, d) else 1, -overlap, i, j))
    used_left: set[int] = set()
    used_right: set[int] = set()
    retained: list[dict[str, Any]] = []
    changed: list[dict[str, Any]] = []
    for exact, _, i, j in sorted(pairs):
        if i in used_left or j in used_right:
            continue
        used_left.add(i)
        used_right.add(j)
        (retained if exact == 0 else changed).append({"baseline": left[i], "alternative": right[j]})
    return {
        "retained": retained,
        "boundary_changed": changed,
        "removed": [old for i, old in enumerate(left) if i not in used_left],
        "added": [new for j, new in enumerate(right) if j not in used_right],
    }


@dataclass(frozen=True)
class ProfileComparisons:
    checks: tuple[tuple[Path, str], ...]
    profiles: tuple[dict[str, Any], ...]

    def recheck(self) -> None:
        for path, digest in self.checks:
            if file_sha256(path) != digest:
                raise CivError(
                    f"comparison input changed: {path.name}; reopen with a new inventory revision"
                )

    def view(self) -> list[dict[str, Any]]:
        self.recheck()
        return copy.deepcopy(list(self.profiles))


def load_profile_comparisons(inventory_path: Path, active: ReviewBinding) -> ProfileComparisons:
    # Reuse the complete production run validator, without creating another writer.
    from civ_workshop.organizer.label_review import _identity_for_inputs

    if active.signal_product_manifest_path is None:
        raise CivError("profile comparison requires an exact warm-up/development product manifest")
    product = _product_binding(
        active.signal_product_manifest_path, permitted_splits=frozenset({"warmup", "development"})
    )
    if (
        product.product_sha256 != active.identity["source_sha256"]
        or product.dataset != active.identity["dataset"]
        or product.source_id != active.identity["source_id"]
    ):
        raise CivError("comparison product identity does not match active review")
    validated_active, _, _, _, _, _ = _identity_for_inputs(
        active.source_path,
        active.spec_path,
        active.events_path,
        active.manifest_path,
        str(active.identity["dataset"]),
        str(active.identity["source_id"]),
        None,
    )
    for key in (
        "source_sha256",
        "spec_sha256",
        "events_sha256",
        "manifest_sha256",
        "resource_set_sha256",
    ):
        if validated_active.identity[key] != active.identity[key]:
            raise CivError("active review identity changed before comparison")
    inventory_path = inventory_path.resolve()
    inventory_hash = file_sha256(inventory_path)
    inventory = read_json_file(inventory_path, "profile comparison inventory")
    if set(inventory) != {"profiles"}:
        raise CivError("comparison inventory requires only profiles")
    declarations = inventory["profiles"]
    if not isinstance(declarations, list) or not declarations:
        raise CivError("comparison inventory requires a non-empty profiles list")
    baseline = [
        {
            "event_id": event.event_id,
            "start_ns": str(event.interval.start_ns),
            "end_ns": str(event.interval.end_ns),
        }
        for event in read_events(active.events_path)
    ]
    checks: dict[Path, str] = {inventory_path: inventory_hash}

    def remember(path: Path, digest: str) -> None:
        if path in checks and checks[path] != digest:
            raise CivError(f"comparison inputs disagree about identity: {path.name}")
        checks[path] = digest

    for path, key in (
        (active.source_path, "source_sha256"),
        (active.spec_path, "spec_sha256"),
        (active.events_path, "events_sha256"),
        (active.manifest_path, "manifest_sha256"),
        (active.signal_product_manifest_path, "signal_product_manifest_sha256"),
    ):
        remember(path, str(active.identity[key]))
    active_spec = load_event_spec(active.spec_path)
    for resource in load_point_resources(active.spec_path, active_spec.resources).values():
        remember((active.spec_path.parent / resource.binding.path).resolve(), resource.sha256)
    identifiers: set[str] = set()
    run_paths = {active.manifest_path.parent.resolve()}
    profiles: list[dict[str, Any]] = []
    for raw in declarations:
        entry = require_mapping(raw, "comparison profile")
        if set(entry) != {"id", "spec", "run"}:
            raise CivError("comparison profile requires only id, spec and run")
        identifier = require_string(entry["id"], "comparison profile id")
        if identifier in identifiers:
            raise CivError("comparison profile ids must be unique")
        identifiers.add(identifier)
        paths = []
        for field in ("spec", "run"):
            path = Path(require_string(entry[field], f"comparison {field}"))
            paths.append(
                (inventory_path.parent / path).resolve()
                if not path.is_absolute()
                else path.resolve()
            )
        spec_path, run_path = paths
        if run_path in run_paths:
            raise CivError("comparison profiles require independent run directories")
        run_paths.add(run_path)
        binding, events, _, _, _, _ = _identity_for_inputs(
            active.source_path,
            spec_path,
            run_path / "events.jsonl",
            run_path / "run-manifest.json",
            str(active.identity["dataset"]),
            str(active.identity["source_id"]),
            None,
        )
        for path, key in (
            (spec_path, "spec_sha256"),
            (binding.events_path, "events_sha256"),
            (binding.manifest_path, "manifest_sha256"),
        ):
            remember(path, str(binding.identity[key]))
        spec = load_event_spec(spec_path)
        for resource in load_point_resources(spec_path, spec.resources).values():
            remember((spec_path.parent / resource.binding.path).resolve(), resource.sha256)
        intervals = [
            {
                "event_id": event.event_id,
                "start_ns": str(event.interval.start_ns),
                "end_ns": str(event.interval.end_ns),
            }
            for event in events
        ]
        profiles.append(
            {
                "id": identifier,
                "name": spec.name,
                "identity": dict(binding.identity),
                "condition": spec.condition,
                "timing_ns": {
                    "min_duration": str(spec.min_duration_ns),
                    "merge_gap": str(spec.merge_gap_ns),
                    "max_duration": str(spec.max_duration_ns),
                },
                "spec_text": spec_path.read_text(encoding="utf-8"),
                "intervals": intervals,
                "differences": compare_intervals(baseline, intervals),
                "qualification": "candidate comparison only; not truth or scoring",
            }
        )
    result = ProfileComparisons(
        tuple(sorted(checks.items(), key=lambda item: str(item[0]))), tuple(profiles)
    )
    result.recheck()
    return result
