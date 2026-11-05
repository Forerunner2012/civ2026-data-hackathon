from __future__ import annotations

import json
from argparse import Namespace
from pathlib import Path

import pytest

from civ_workshop.artifacts import canonical_json, file_sha256
from civ_workshop.detection import detect_events
from civ_workshop.errors import CivError
from civ_workshop.organizer.label_profiles import compare_intervals, load_profile_comparisons
from civ_workshop.organizer.label_review import (
    ReviewApplication,
    _prepare_binding,
    _read_progress,
    gate_review,
    initial_review_state,
)
from tests.test_label_review import _record_review, _reduced_case, _write_json


def _comparison_case(root: Path, *, resources: bool = False) -> tuple[Namespace, Path, Path, Path]:
    args = _reduced_case(root)
    spec = root / "alternative.yaml"
    text = args.spec.read_text(encoding="utf-8").replace("signal > 1.0", "signal < 1.0")
    text = text.replace("micro-high-signal", "micro-alternative")
    if resources:
        text = text.replace(
            "condition:",
            "resources:\n  landmarks:\n    path: landmarks.json\n"
            "    contract: civ.point-resource/v1\ncondition:",
        )
        _write_json(
            root / "landmarks.json",
            {
                "contract": "civ.point-resource/v1",
                "coordinate_reference": "EPSG:4326",
                "points": [{"id": "fixture", "latitude": 35.0, "longitude": 139.0}],
            },
        )
    spec.write_text(text, encoding="utf-8")
    run = root / "alternative-run"
    detect_events(spec, args.source, run)
    inventory = root / "comparisons.json"
    _write_json(
        inventory, {"profiles": [{"id": "alternative", "spec": spec.name, "run": run.name}]}
    )
    return args, inventory, spec, run


def test_geometry_comparison_is_deterministic_and_not_event_id_matching() -> None:
    def interval(name: str, start: int, end: int) -> dict[str, str]:
        return {"event_id": name, "start_ns": str(start), "end_ns": str(end)}

    baseline = [interval("old-a", 10, 20), interval("old-b", 30, 40), interval("old-c", 80, 90)]
    alternative = [
        interval("new-a", 10, 20),
        interval("new-b", 32, 43),
        interval("new-d", 100, 110),
    ]
    result = compare_intervals(baseline, alternative)
    assert result == compare_intervals(list(reversed(baseline)), list(reversed(alternative)))
    assert {key: len(value) for key, value in result.items()} == {
        "retained": 1,
        "boundary_changed": 1,
        "removed": 1,
        "added": 1,
    }
    assert compare_intervals([], []) == {
        "retained": [],
        "boundary_changed": [],
        "removed": [],
        "added": [],
    }


def test_comparison_is_reference_only_and_existing_missed_action_clears_signoff(
    tmp_path: Path,
) -> None:
    args, inventory, _, _ = _comparison_case(tmp_path / "case")
    binding, events, _, before_ns, after_ns = _prepare_binding(args)
    app = ReviewApplication(
        binding,
        initial_review_state(binding, events, binding.evidence_by_id),
        before_ns=before_ns,
        after_ns=after_ns,
    )
    _record_review(app, events[0].event_id)
    app.save()
    frozen = {str(path): file_sha256(path) for path in (args.events, args.manifest, args.progress)}
    before = canonical_json(app.state)
    comparisons = load_profile_comparisons(inventory, binding)
    app.comparisons = comparisons
    profiles = app.view()["comparisons"]
    assert isinstance(profiles, list) and len(profiles) == 1
    assert canonical_json(app.state) == before
    profile = profiles[0]
    assert profile["identity"]["spec_sha256"] != binding.identity["spec_sha256"]
    assert profile["timing_ns"]["min_duration"] == "1000000000"
    interval = profile["differences"]["added"][0]
    assert int(interval["start_ns"]) > 2**53
    assert comparisons.view() == profiles
    for path, digest in frozen.items():
        assert file_sha256(Path(path)) == digest
    app.act(
        {
            "type": "add-missed",
            "start_ns": interval["start_ns"],
            "end_ns": interval["end_ns"],
            "reason": "Synthetic contextual review confirmed a missed event",
        }
    )
    assert app.state["coverage_reviewed"] is False
    candidates = app.state["candidates"]
    assert isinstance(candidates, list)
    assert candidates[-1]["decision"] == "pending"
    assert gate_review(app.state)


@pytest.mark.parametrize("field", ["inventory", "spec", "events", "manifest", "resource"])
def test_changed_comparison_artifact_refuses_actions_before_progress_write(
    tmp_path: Path, field: str
) -> None:
    args, inventory, spec, run = _comparison_case(tmp_path / "case", resources=True)
    binding, events, _, before_ns, after_ns = _prepare_binding(args)
    comparisons = load_profile_comparisons(inventory, binding)
    app = ReviewApplication(
        binding,
        initial_review_state(binding, events, binding.evidence_by_id),
        before_ns=before_ns,
        after_ns=after_ns,
        comparisons=comparisons,
    )
    app.save()
    saved = args.progress.read_bytes()
    current = canonical_json(app.state)
    changed = {
        "inventory": inventory,
        "spec": spec,
        "events": run / "events.jsonl",
        "manifest": run / "run-manifest.json",
        "resource": spec.parent / "landmarks.json",
    }[field]
    changed.write_bytes(changed.read_bytes() + b"\n")
    with pytest.raises(CivError, match="comparison input changed"):
        app.act({"type": "set-reviewer", "name": "Should not apply"})
    with pytest.raises(CivError, match="comparison input changed"):
        comparisons.view()
    assert args.progress.read_bytes() == saved
    assert canonical_json(app.state) == current


@pytest.mark.parametrize(
    "change",
    [
        "source",
        "spec",
        "events",
        "resources",
        "duplicate-id",
        "duplicate-run",
        "unknown-field",
        "sealed",
        "unbound",
    ],
)
def test_comparison_rejects_invalid_or_sealed_inputs(tmp_path: Path, change: str) -> None:
    args, inventory, spec, run = _comparison_case(tmp_path / "case", resources=True)
    binding, _, _, _, _ = _prepare_binding(args)
    manifest_path = run / "run-manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if change in {"source", "spec", "events"}:
        manifest[change]["sha256"] = "b" * 64
        _write_json(manifest_path, manifest)
    elif change == "resources":
        manifest["resources"] = []
        _write_json(manifest_path, manifest)
    elif change.startswith("duplicate"):
        doc = json.loads(inventory.read_text(encoding="utf-8"))
        entry = dict(doc["profiles"][0])
        if change == "duplicate-run":
            entry["id"] = "other"
        doc["profiles"].append(entry)
        _write_json(inventory, doc)
    elif change == "unknown-field":
        _write_json(inventory, {"profiles": [], "truth": True})
    elif change == "sealed":
        sidecar = json.loads(args.signal_product_manifest.read_text(encoding="utf-8"))
        sidecar["provenance"]["split"] = "sealed"
        _write_json(args.signal_product_manifest, sidecar)
    else:
        from dataclasses import replace

        binding = replace(binding, signal_product_manifest_path=None)
    with pytest.raises(CivError):
        load_profile_comparisons(inventory, binding)


def test_selecting_another_profile_refuses_old_progress_and_keeps_original_bytes(
    tmp_path: Path,
) -> None:
    args, _, spec, run = _comparison_case(tmp_path / "case")
    binding, events, _, before_ns, after_ns = _prepare_binding(args)
    app = ReviewApplication(
        binding,
        initial_review_state(binding, events, binding.evidence_by_id),
        before_ns=before_ns,
        after_ns=after_ns,
    )
    _record_review(app, events[0].event_id)
    app.save()
    paths = (args.events, args.manifest, args.progress, args.spec)
    before = {str(path): file_sha256(path) for path in paths}
    args.spec, args.events, args.manifest = spec, run / "events.jsonl", run / "run-manifest.json"
    changed, _, _, _, _ = _prepare_binding(args)
    with pytest.raises(CivError, match="identity"):
        _read_progress(args.progress, changed)
    for path, digest in before.items():
        assert file_sha256(Path(path)) == digest


def test_stale_active_resources_cannot_be_rebound_through_a_fresh_alternative(
    tmp_path: Path,
) -> None:
    args, inventory, spec, run = _comparison_case(tmp_path / "case", resources=True)
    resource_block = (
        "resources:\n  landmarks:\n    path: landmarks.json\n"
        "    contract: civ.point-resource/v1\ncondition:"
    )
    args.spec.write_text(
        args.spec.read_text(encoding="utf-8").replace("condition:", resource_block),
        encoding="utf-8",
    )
    baseline = args.spec.parent / "baseline-with-resource"
    detect_events(args.spec, args.source, baseline)
    args.events, args.manifest = baseline / "events.jsonl", baseline / "run-manifest.json"
    binding, _, _, _, _ = _prepare_binding(args)
    resource = spec.parent / "landmarks.json"
    resource.write_bytes(resource.read_bytes() + b"\n")
    fresh = spec.parent / "fresh-alternative"
    detect_events(spec, args.source, fresh)
    _write_json(inventory, {"profiles": [{"id": "fresh", "spec": spec.name, "run": fresh.name}]})
    with pytest.raises(CivError, match="resources"):
        load_profile_comparisons(inventory, binding)
