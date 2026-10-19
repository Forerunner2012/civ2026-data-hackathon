from __future__ import annotations

import json
import os
import struct
import threading
import zlib
from argparse import Namespace
from dataclasses import replace
from http.server import HTTPServer
from pathlib import Path
from typing import Any
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import pytest
from mcap.writer import CompressionType, Writer

import civ_workshop.organizer.label_review as label_review_module
from civ_workshop.artifacts import canonical_json, file_sha256
from civ_workshop.data_products import build_data_product
from civ_workshop.detection import detect_events
from civ_workshop.errors import CivError
from civ_workshop.label_packs import (
    audit_label_pack_set,
    build_label_packs,
    load_label_pack,
    validate_label_pack,
)
from civ_workshop.organizer.label_review import (
    ReviewApplication,
    _create_handler,
    _prepare_binding,
    _read_progress,
    _write_atomic,
    build_export_document,
    gate_review,
    initial_review_state,
    transition_review,
)
from civ_workshop.score_reference import validate_score_reference
from tests.helpers import MICRO_SPEC

EPOCH_NS = 1_791_300_000_000_000_123
CAMERA_TOPIC = "/camera/image/compressed"


def _mapping(value: object) -> dict[str, object]:
    assert isinstance(value, dict)
    assert all(isinstance(key, str) for key in value)
    mapping: dict[str, object] = value
    return mapping


def _records(value: object) -> list[dict[str, object]]:
    assert isinstance(value, list)
    return [_mapping(item) for item in value]


def _gate_reasons(value: object) -> list[str]:
    assert isinstance(value, list)
    reasons: list[str] = []
    for reason in value:
        assert isinstance(reason, str)
        reasons.append(reason)
    return reasons


def _png_pixel() -> bytes:
    def chunk(name: bytes, value: bytes) -> bytes:
        checksum = zlib.crc32(name + value) & 0xFFFFFFFF
        return struct.pack(">I", len(value)) + name + value + struct.pack(">I", checksum)

    header = struct.pack(">IIBBBBB", 1, 1, 8, 6, 0, 0, 0)
    pixels = zlib.compress(b"\x00\x20\x60\xa0\xff")
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", header) + chunk(
        b"IDAT", pixels
    ) + chunk(b"IEND", b"")


def _write_source(path: Path, values: tuple[float, ...] = (0.0, 2.0, 2.0, 0.0, 0.0)) -> None:
    schemas = {
        "/micro/signal": (
            "civ.micro.Signal",
            {"type": "object", "properties": {"value": {"type": "number"}}},
        ),
        "/micro/evidence": (
            "civ.micro.Evidence",
            {"type": "object", "properties": {"label": {"type": "string"}}},
        ),
    }
    with path.open("wb") as stream:
        writer = Writer(stream, compression=CompressionType.NONE)
        writer.start(profile="civ.micro", library="civ-label-review-test")
        channels = {}
        for topic, (name, schema) in schemas.items():
            schema_id = writer.register_schema(
                name=name,
                encoding="jsonschema",
                data=json.dumps(schema, sort_keys=True).encode(),
            )
            channels[topic] = writer.register_channel(
                schema_id=schema_id,
                topic=topic,
                message_encoding="json",
            )
        for second, value in enumerate(values):
            timestamp = EPOCH_NS + second * 1_000_000_000
            writer.add_message(
                channel_id=channels["/micro/signal"],
                log_time=timestamp,
                publish_time=timestamp,
                data=json.dumps({"value": value}).encode(),
            )
            writer.add_message(
                channel_id=channels["/micro/evidence"],
                log_time=timestamp,
                publish_time=timestamp,
                data=json.dumps({"label": f"synthetic-{second}"}).encode(),
            )
        writer.finish()


def _write_json(path: Path, value: object) -> None:
    path.write_text(f"{canonical_json(value)}\n", encoding="utf-8", newline="\n")


def _write_camera_context(root: Path, source: Path) -> Path:
    product_path = root / "approved-camera-context.mcap"
    timestamp = EPOCH_NS + 4_000_000_000
    with product_path.open("wb") as stream:
        writer = Writer(stream, compression=CompressionType.NONE)
        writer.start(profile="ros2", library="civ-label-review-camera-test")
        schema = writer.register_schema(
            name="sensor_msgs/msg/CompressedImage",
            encoding="jsonschema",
            data=json.dumps(
                {
                    "type": "object",
                    "properties": {
                        "format": {"type": "string"},
                        "data": {"type": "array", "items": {"type": "integer"}},
                    },
                },
                sort_keys=True,
            ).encode(),
        )
        channel = writer.register_channel(
            schema_id=schema,
            topic=CAMERA_TOPIC,
            message_encoding="json",
        )
        writer.add_message(
            channel_id=channel,
            log_time=timestamp,
            publish_time=timestamp,
            data=json.dumps({"format": "png", "data": list(_png_pixel())}).encode(),
        )
        writer.finish()

    approval_path = root / "synthetic-camera-approval.json"
    approval_document = {
        "approval_id": "synthetic-camera-approval",
        "authority": "Synthetic fixture owner",
        "contract": "civ.camera-context-privacy-rights-approval/v1",
        "decision": "approved",
        "frame_review_set_sha256": "a" * 64,
        "inspection_complete": True,
        "redaction_required": False,
        "rights_statement": "Synthetic test image only.",
    }
    _write_json(approval_path, approval_document)
    manifest_path = root / "approved-camera-context.manifest.json"
    _write_json(
        manifest_path,
        {
            "approval": {
                "authority": approval_document["authority"],
                "document_sha256": file_sha256(approval_path),
                "frame_review_set_sha256": approval_document["frame_review_set_sha256"],
                "id": approval_document["approval_id"],
                "rights_statement": approval_document["rights_statement"],
            },
            "calibration": {"status": "synthetic fixture", "topic": None},
            "contract": "civ.camera-context-manifest/v1",
            "dataset": "kashiwa",
            "parent": {"id": "synthetic-source", "sha256": file_sha256(source)},
            "product": {
                "byte_size": product_path.stat().st_size,
                "message_count": 1,
                "message_end_ns": timestamp,
                "message_start_ns": timestamp,
                "name": product_path.name,
                "sha256": file_sha256(product_path),
                "topics": [{"message_count": 1, "topic": CAMERA_TOPIC}],
            },
            "recipe": {
                "id": "synthetic-camera-context-v1",
                "sha256": "b" * 64,
                "version": 1,
            },
            "rights": {"attribution": "Synthetic fixture", "scope": "Test only"},
            "signal_product": {"name": "synthetic-signals.mcap", "sha256": "c" * 64},
            "split": "warmup",
            "time_bounds": {"end_ns": timestamp, "start_ns": timestamp},
            "transformation": "synthetic-test-fixture",
        },
    )
    return manifest_path


def _case(
    root: Path,
    *,
    with_camera_context: bool = False,
    source_values: tuple[float, ...] = (0.0, 2.0, 2.0, 0.0, 0.0),
) -> tuple[Namespace, ReviewApplication, str]:
    root.mkdir(parents=True, exist_ok=True)
    source = root / "synthetic.mcap"
    spec = root / "synthetic.yaml"
    run = root / "detected"
    progress = root / "review-progress.json"
    _write_source(source, source_values)
    camera_manifest = _write_camera_context(root, source) if with_camera_context else None
    spec.write_text(MICRO_SPEC, encoding="utf-8", newline="\n")
    detect_events(spec, source, run)
    args = Namespace(
        source=source,
        spec=spec,
        events=run / "events.jsonl",
        manifest=run / "run-manifest.json",
        dataset="kashiwa",
        source_id="synthetic-source",
        progress=progress,
        practice_output=root / "practice.json",
        organizer_output=root / "truth.json",
        camera_context_manifest=camera_manifest,
        port=0,
        no_browser=True,
    )
    binding, events, _, before_ns, after_ns = _prepare_binding(args)
    assert events
    state = initial_review_state(binding, events, binding.evidence_by_id)
    app = ReviewApplication(binding, state, before_ns=before_ns, after_ns=after_ns)
    return args, app, events[0].event_id


def _state_with_spoofed_context(
    app: ReviewApplication, candidate_id: str, *, approved: bool = False
) -> dict[str, object]:
    state = _mapping(json.loads(canonical_json(app.state)))
    candidate = next(
        item for item in _records(state["candidates"]) if item["id"] == candidate_id
    )
    candidate["context_status"] = "available"
    candidate["missing_context"] = []
    if approved:
        candidate["decision"] = "approved"
        candidate["reviewer"] = "Synthetic reviewer"
        candidate["uncertainty_disposition"] = "clear"
        candidate["uncertainty_reason"] = ""
        candidate["practice_selected"] = True
        state["reviewer"] = "Synthetic reviewer"
        state["coverage_reviewed"] = True
        state["coverage_reviewer"] = "Synthetic reviewer"
        state["coverage_revision"] = state["geometry_revision"]
    return state


def _record_review(app: ReviewApplication, candidate_id: str) -> None:
    app.act({"type": "set-reviewer", "name": "Synthetic reviewer"})
    app.act(
        {
            "type": "approve",
            "candidate_id": candidate_id,
            "uncertainty_disposition": "accept_event",
            "uncertainty_reason": "Camera context is unavailable in the synthetic fixture.",
        }
    )
    app.act({"type": "set-practice", "candidate_id": candidate_id, "selected": True})
    app.act({"type": "signoff", "checked": True})


def _reopen(args: Namespace) -> ReviewApplication:
    binding, _, _, before_ns, after_ns = _prepare_binding(args)
    return ReviewApplication(
        binding,
        _read_progress(args.progress, binding),
        before_ns=before_ns,
        after_ns=after_ns,
    )


def _archived_snapshot(active_path: Path, contents: bytes) -> tuple[Path, dict[str, object]]:
    root = active_path.with_name(f"{active_path.name}.revisions")
    for snapshot in root.iterdir():
        content_path = snapshot / "content"
        if content_path.is_file() and content_path.read_bytes() == contents:
            metadata = _mapping(json.loads((snapshot / "metadata.json").read_text("utf-8")))
            return snapshot, metadata
    raise AssertionError(f"snapshot not found for {active_path.name}")


def test_completed_review_reopens_and_saves_unchanged_at_same_paths(tmp_path: Path) -> None:
    args, app, candidate_id = _case(tmp_path / "case")
    _record_review(app, candidate_id)
    app.export("practice")
    progress_before = args.progress.read_bytes()
    output_before = args.practice_output.read_bytes()
    archive_entries_before = sorted(
        path.name for path in Path(f"{args.progress}.revisions").iterdir()
    )

    reopened = _reopen(args)
    view = reopened.view()
    assert view["gate"] == []
    candidate = _records(_mapping(view["state"])["candidates"])[0]
    assert candidate["decision"] == "approved"
    assert candidate["practice_selected"] is True
    assert _records(_mapping(view["state"])["audit"])
    assert _mapping(view["state"])["coverage_reviewed"] is True
    reopened.save()
    reopened.reload()
    reopened.save()

    assert args.progress.read_bytes() == progress_before
    assert args.practice_output.read_bytes() == output_before
    assert sorted(path.name for path in Path(f"{args.progress}.revisions").iterdir()) == (
        archive_entries_before
    )


def test_refinement_and_reexport_archive_progress_and_both_output_revisions(
    tmp_path: Path,
) -> None:
    args, app, first_id = _case(
        tmp_path / "case", source_values=(0.0, 2.0, 2.0, 0.0, 0.0, 2.0, 2.0, 0.0, 0.0)
    )
    candidates = _records(app.state["candidates"])
    assert len(candidates) == 2
    second_id = str(candidates[1]["id"])
    _record_review(app, first_id)
    app.act(
        {
            "type": "approve",
            "candidate_id": second_id,
            "uncertainty_disposition": "accept_event",
            "uncertainty_reason": "Synthetic second event has no camera context.",
        }
    )
    app.act({"type": "set-practice", "candidate_id": second_id, "selected": True})
    app.act({"type": "signoff", "checked": True})
    assert gate_review(app.state) == []
    app.export("practice")
    app.export("organizer-private")
    old_outputs = {
        "practice": args.practice_output.read_bytes(),
        "organizer-private": args.organizer_output.read_bytes(),
    }

    first = next(item for item in _records(app.state["candidates"]) if item["id"] == first_id)
    start_ns = int(str(first["start_ns"])) + 10
    app.act(
        {
            "type": "edit",
            "candidate_id": first_id,
            "start_ns": str(start_ns),
            "end_ns": first["end_ns"],
            "reason": "Synthetic boundary refinement after reopening.",
        }
    )
    app.act(
        {
            "type": "reject",
            "candidate_id": second_id,
            "reason": "Synthetic decision changed after contextual review.",
            "uncertainty_disposition": "reject_candidate",
        }
    )
    app.act(
        {
            "type": "add-missed",
            "start_ns": str(EPOCH_NS + 3_500_000_000),
            "end_ns": str(EPOCH_NS + 4_000_000_000),
            "reason": "Synthetic missed event found during whole-source review.",
        }
    )
    missed_id = str(_records(app.state["candidates"])[-1]["id"])
    assert gate_review(app.state)
    app.act(
        {
            "type": "approve",
            "candidate_id": first_id,
            "uncertainty_disposition": "accept_event",
            "uncertainty_reason": "Synthetic refined event has no camera context.",
        }
    )
    app.act({"type": "set-practice", "candidate_id": first_id, "selected": True})
    app.act(
        {
            "type": "approve",
            "candidate_id": missed_id,
            "uncertainty_disposition": "accept_event",
            "uncertainty_reason": "Synthetic missed event has no camera context.",
        }
    )
    app.act({"type": "set-practice", "candidate_id": missed_id, "selected": True})
    app.act({"type": "signoff", "checked": True})
    assert gate_review(app.state) == []
    progress_before_reexport = args.progress.read_bytes()
    audit_before_reexport = _records(_mapping(json.loads(progress_before_reexport))["audit"])

    practice_result = app.export("practice")
    private_result = app.export("organizer-private")

    for target, output in (
        ("practice", args.practice_output),
        ("organizer-private", args.organizer_output),
    ):
        snapshot, metadata = _archived_snapshot(output, old_outputs[target])
        assert metadata["artifact"] == f"{target}-export"
        assert metadata["revision"] == 1
        assert metadata["sha256"] == file_sha256(snapshot / "content")
        assert output.read_bytes() != old_outputs[target]
    progress_snapshot, progress_metadata = _archived_snapshot(
        args.progress, progress_before_reexport
    )
    archived_progress = json.loads((progress_snapshot / "content").read_text("utf-8"))
    assert progress_metadata["artifact"] == "review-progress"
    assert progress_metadata["sha256"] == file_sha256(progress_snapshot / "content")
    assert _records(archived_progress["audit"]) == audit_before_reexport
    active_progress = json.loads(args.progress.read_text(encoding="utf-8"))
    assert active_progress["exports"]["practice"]["revision"] == 2
    assert active_progress["exports"]["organizer-private"]["revision"] == 2
    assert practice_result["revision"] == private_result["revision"] == 2
    assert args.practice_output.read_bytes() != old_outputs["practice"]
    assert args.organizer_output.read_bytes() != old_outputs["organizer-private"]


def test_boundary_and_accepted_set_changes_invalidate_only_required_approvals(
    tmp_path: Path,
) -> None:
    args, app, first_id = _case(
        tmp_path / "case", source_values=(0.0, 2.0, 2.0, 0.0, 0.0, 2.0, 2.0, 0.0, 0.0)
    )
    candidates = _records(app.state["candidates"])
    assert len(candidates) == 2
    second_id = str(candidates[1]["id"])
    _record_review(app, first_id)
    app.act(
        {
            "type": "approve",
            "candidate_id": second_id,
            "uncertainty_disposition": "accept_event",
            "uncertainty_reason": "Synthetic event has no camera context.",
        }
    )
    app.act({"type": "signoff", "checked": True})
    first = next(item for item in _records(app.state["candidates"]) if item["id"] == first_id)

    app.act(
        {
            "type": "edit",
            "candidate_id": first_id,
            "start_ns": str(int(str(first["start_ns"])) + 10),
            "end_ns": first["end_ns"],
            "reason": "Synthetic boundary correction.",
        }
    )
    changed, unrelated = _records(app.state["candidates"])
    assert changed["decision"] == "pending"
    assert changed["reviewer"] is None
    assert unrelated["decision"] == "approved"
    assert app.state["coverage_reviewed"] is False

    app.act(
        {
            "type": "approve",
            "candidate_id": first_id,
            "uncertainty_disposition": "accept_event",
            "uncertainty_reason": "Synthetic corrected event has no camera context.",
        }
    )
    app.act({"type": "signoff", "checked": True})
    app.act(
        {
            "type": "reject",
            "candidate_id": first_id,
            "reason": "Synthetic reviewer changed the accepted-event decision.",
            "uncertainty_disposition": "reject_candidate",
        }
    )
    first, unrelated = _records(app.state["candidates"])
    assert first["decision"] == "rejected"
    assert unrelated["decision"] == "approved"
    assert app.state["coverage_reviewed"] is False


def test_identity_corruption_and_mismatched_output_refuse_without_writes(
    tmp_path: Path,
) -> None:
    args, app, candidate_id = _case(tmp_path / "case")
    _record_review(app, candidate_id)
    app.save()
    saved_progress = args.progress.read_bytes()
    mismatched_binding = replace(
        app.binding, identity={**app.binding.identity, "spec_sha256": "a" * 64}
    )
    with pytest.raises(CivError, match="identity does not match"):
        _read_progress(args.progress, mismatched_binding)
    assert args.progress.read_bytes() == saved_progress

    corrupted_progress = b"{not valid json\n"
    args.progress.write_bytes(corrupted_progress)
    with pytest.raises(CivError, match="cannot read local review progress"):
        _read_progress(args.progress, app.binding)
    assert args.progress.read_bytes() == corrupted_progress
    args.progress.write_bytes(saved_progress)

    reopened = _reopen(args)
    reopened.export("practice")
    exported_progress = args.progress.read_bytes()
    corrupted_output = b"{}\n"
    args.practice_output.write_bytes(corrupted_output)
    with pytest.raises(CivError, match="digest does not match progress"):
        _reopen(args)
    assert args.progress.read_bytes() == exported_progress
    assert args.practice_output.read_bytes() == corrupted_output


def test_archive_failure_and_stale_writer_preserve_active_progress(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    args, app, _ = _case(tmp_path / "case")
    app.act({"type": "set-reviewer", "name": "Synthetic reviewer"})
    progress_before_failure = args.progress.read_bytes()
    state_before_failure = canonical_json(app.state)
    real_archive = label_review_module._archive_snapshot

    def fail_archive(*args: object, **kwargs: object) -> None:
        raise CivError("synthetic archive failure")

    monkeypatch.setattr(label_review_module, "_archive_snapshot", fail_archive)
    with pytest.raises(CivError, match="synthetic archive failure"):
        app.act({"type": "set-reviewer", "name": "Changed reviewer"})
    assert args.progress.read_bytes() == progress_before_failure
    assert canonical_json(app.state) == state_before_failure

    monkeypatch.setattr(label_review_module, "_archive_snapshot", real_archive)
    stale = _reopen(args)
    app.act({"type": "set-reviewer", "name": "Primary writer"})
    progress_after_primary_write = args.progress.read_bytes()
    stale_state = canonical_json(stale.state)
    with pytest.raises(CivError, match="changed since this session opened"):
        stale.act({"type": "set-reviewer", "name": "Stale writer"})
    assert args.progress.read_bytes() == progress_after_primary_write
    assert canonical_json(stale.state) == stale_state


def test_new_review_refuses_progress_created_after_its_initial_read(tmp_path: Path) -> None:
    args, app, _ = _case(tmp_path / "case")
    initial_state = app.state
    _write_atomic(args.progress, f"{canonical_json(initial_state)}\n")
    progress_after_other_writer = args.progress.read_bytes()
    stale = ReviewApplication(
        app.binding,
        initial_state,
        before_ns=app.before_ns,
        after_ns=app.after_ns,
        progress_digest=None,
        progress_digest_is_current=True,
    )

    with pytest.raises(CivError, match="changed since this session opened"):
        stale.save()
    assert args.progress.read_bytes() == progress_after_other_writer


def test_export_write_failure_restores_progress_and_previous_output(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    args, app, candidate_id = _case(tmp_path / "case")
    _record_review(app, candidate_id)
    app.export("practice")
    progress_before = args.progress.read_bytes()
    output_before = args.practice_output.read_bytes()
    state_before = canonical_json(app.state)
    real_replace = os.replace
    failed = False

    def fail_progress_commit(source: Any, destination: Any) -> None:
        nonlocal failed
        source_path = Path(source)
        destination_path = Path(destination)
        if (
            not failed
            and destination_path == args.progress
            and source_path.is_file()
            and source_path.read_bytes() != progress_before
        ):
            failed = True
            raise OSError("synthetic progress replacement failure")
        real_replace(source, destination)

    monkeypatch.setattr(os, "replace", fail_progress_commit)
    with pytest.raises(CivError, match="cannot replace review files"):
        app.export("practice")

    assert failed
    assert args.progress.read_bytes() == progress_before
    assert args.practice_output.read_bytes() == output_before
    assert canonical_json(app.state) == state_before


def test_unsafe_review_path_collision_refuses_without_writes(tmp_path: Path) -> None:
    args, _, _ = _case(tmp_path / "case")
    source_before = args.source.read_bytes()
    args.practice_output = args.source
    with pytest.raises(CivError, match="separate paths"):
        _prepare_binding(args)
    args.practice_output = args.progress.with_name(f"{args.progress.name}.lock")
    with pytest.raises(CivError, match="lock path collides"):
        _prepare_binding(args)
    assert args.source.read_bytes() == source_before
    assert not args.progress.exists()


def test_initial_saved_progress_refreshes_context_before_gate(tmp_path: Path) -> None:
    args, app, candidate_id = _case(tmp_path / "case")
    saved = _state_with_spoofed_context(app, candidate_id, approved=True)
    _write_atomic(args.progress, f"{canonical_json(saved)}\n")

    loaded = ReviewApplication(
        app.binding,
        _read_progress(args.progress, app.binding),
        before_ns=app.before_ns,
        after_ns=app.after_ns,
    )

    assert _records(loaded.state["candidates"])[0]["context_status"] == "missing"
    assert any("explicit disposition for missing context" in reason
               for reason in _gate_reasons(loaded.view()["gate"]))


def test_reload_refreshes_saved_context_before_gate(tmp_path: Path) -> None:
    args, app, candidate_id = _case(tmp_path / "case")
    saved = _state_with_spoofed_context(app, candidate_id, approved=True)
    _write_atomic(args.progress, f"{canonical_json(saved)}\n")

    view = app.reload()

    assert _records(app.state["candidates"])[0]["context_status"] == "missing"
    assert any("explicit disposition for missing context" in reason
               for reason in _gate_reasons(view["gate"]))


def test_approval_uses_bound_context_not_saved_status(tmp_path: Path) -> None:
    _, app, candidate_id = _case(tmp_path / "case")
    app.state = _state_with_spoofed_context(app, candidate_id)
    app.state["reviewer"] = "Synthetic reviewer"

    with pytest.raises(CivError, match="missing context cannot be marked clear"):
        app.act(
            {
                "type": "approve",
                "candidate_id": candidate_id,
                "uncertainty_disposition": "clear",
            }
        )


def test_undo_refreshes_restored_context_in_authoritative_state(tmp_path: Path) -> None:
    _, app, candidate_id = _case(tmp_path / "case")
    app.state = _state_with_spoofed_context(app, candidate_id)

    app.act({"type": "set-reviewer", "name": "Synthetic reviewer"})
    app.act({"type": "undo"})

    assert _records(app.state["candidates"])[0]["context_status"] == "missing"
    assert _records(app.state["candidates"])[0]["missing_context"]


def test_direct_export_refreshes_context_before_gate(tmp_path: Path) -> None:
    args, app, candidate_id = _case(tmp_path / "case")
    app.state = _state_with_spoofed_context(app, candidate_id, approved=True)

    with pytest.raises(CivError, match="missing context"):
        app.export("practice")

    assert not args.practice_output.exists()


def test_exact_epoch_nanoseconds_round_trip_and_consumer_export(tmp_path: Path) -> None:
    args, app, candidate_id = _case(tmp_path / "case")
    start = EPOCH_NS + 1_000_000_001
    end = EPOCH_NS + 2_999_999_997
    app.act({"type": "set-reviewer", "name": "Synthetic reviewer"})
    app.act(
        {
            "type": "edit",
            "candidate_id": candidate_id,
            "start_ns": str(start),
            "end_ns": str(end),
            "reason": "Synthetic one-nanosecond boundary adjustment.",
        }
    )
    assert _records(app.state["candidates"])[0]["decision"] == "pending"
    app.act(
        {
            "type": "approve",
            "candidate_id": candidate_id,
            "uncertainty_disposition": "accept_event",
            "uncertainty_reason": "Synthetic camera context is unavailable.",
        }
    )
    app.act({"type": "set-practice", "candidate_id": candidate_id, "selected": True})
    app.act({"type": "signoff", "checked": True})
    app.save()
    saved = json.loads(args.progress.read_text(encoding="utf-8"))
    assert saved["candidates"][0]["start_ns"] == str(start)
    assert saved["candidates"][0]["end_ns"] == str(end)

    reloaded = app.reload()
    assert _records(_mapping(reloaded["state"])["candidates"])[0]["start_ns"] == str(start)
    assert _records(_mapping(reloaded["state"])["candidates"])[0]["end_ns"] == str(end)
    result = app.export("practice")
    assert result["target"] == "practice"
    output = json.loads(args.practice_output.read_text(encoding="utf-8"))
    checked = validate_score_reference(output)
    assert validate_label_pack(output) == output
    assert checked["labels"] == [
        {"end_ns": end, "label_id": candidate_id, "start_ns": start}
    ]
    assert "Synthetic reviewer" not in args.practice_output.read_text(encoding="utf-8")
    assert "Synthetic camera context is unavailable" not in args.practice_output.read_text(
        encoding="utf-8"
    )


def test_adjustment_undo_preserves_reason_in_local_audit(tmp_path: Path) -> None:
    _, app, candidate_id = _case(tmp_path / "case")
    _record_review(app, candidate_id)
    candidate = _records(app.state["candidates"])[0]
    original_start = candidate["start_ns"]
    original_end = candidate["end_ns"]
    assert isinstance(original_start, str)
    assert isinstance(original_end, str)
    app.act(
        {
            "type": "edit",
            "candidate_id": candidate_id,
            "start_ns": str(int(original_start) + 1),
            "end_ns": str(int(original_end) + 1),
            "reason": "Synthetic adjustment after approval.",
        }
    )
    assert _records(app.state["candidates"])[0]["decision"] == "pending"
    assert app.state["coverage_reviewed"] is False
    app.act({"type": "undo"})
    assert _records(app.state["candidates"])[0]["decision"] == "approved"
    assert _records(app.state["candidates"])[0]["start_ns"] == original_start
    audit = _records(app.state["audit"])
    undo = audit[-1]
    assert undo["action"] == "undo"
    assert _mapping(undo["undid"])["reason"] == "Synthetic adjustment after approval."
    assert gate_review(app.state) == []


def test_reasons_uncertainty_missed_signoff_and_unsupported_exclusion(tmp_path: Path) -> None:
    args, app, candidate_id = _case(tmp_path / "case")
    assert _records(app.state["candidates"])[0]["context_status"] == "missing"
    with pytest.raises(CivError, match="missing context"):
        transition_review(
            {**app.state, "reviewer": "Reviewer"},
            {
                "type": "approve",
                "candidate_id": candidate_id,
                "uncertainty_disposition": "clear",
            },
            app.binding.source_bounds,
        )
    with pytest.raises(CivError, match="rejection reason"):
        transition_review(
            {**app.state, "reviewer": "Reviewer"},
            {
                "type": "reject",
                "candidate_id": candidate_id,
                "reason": "",
                "uncertainty_disposition": "reject_candidate",
            },
            app.binding.source_bounds,
        )
    with pytest.raises(CivError, match="unsupported exclusion kind"):
        transition_review(
            {**app.state, "reviewer": "Reviewer"},
            {
                "type": "data-gap",
                "candidate_id": candidate_id,
                "reason": "Synthetic uncertainty",
                "exclusion_kind": "uncertain_event",
                "uncertainty_disposition": "scoring_data_gap",
            },
            app.binding.source_bounds,
        )

    _record_review(app, candidate_id)
    assert gate_review(app.state) == []
    app.act(
        {
            "type": "add-missed",
            "start_ns": str(EPOCH_NS + 3_500_000_000),
            "end_ns": str(EPOCH_NS + 3_800_000_000),
            "reason": "Synthetic full-recording review found a missed event.",
        }
    )
    assert app.state["coverage_reviewed"] is False
    assert gate_review(app.state)
    missed_id = _records(app.state["candidates"])[-1]["id"]
    assert isinstance(missed_id, str)
    app.act(
        {
            "type": "approve",
            "candidate_id": missed_id,
            "uncertainty_disposition": "accept_event",
            "uncertainty_reason": "Synthetic image context is unavailable.",
        }
    )
    assert gate_review(app.state)
    app.act({"type": "signoff", "checked": True})
    assert gate_review(app.state) == []
    assert args.progress.exists()


def test_practice_selection_excludes_private_only_and_private_truth_builds(tmp_path: Path) -> None:
    args, app, candidate_id = _case(tmp_path / "case")
    app.act({"type": "set-reviewer", "name": "Synthetic reviewer"})
    app.act(
        {
            "type": "approve",
            "candidate_id": candidate_id,
            "uncertainty_disposition": "accept_event",
            "uncertainty_reason": "Synthetic camera context is unavailable.",
        }
    )
    app.act({"type": "set-practice", "candidate_id": candidate_id, "selected": True})
    app.act(
        {
            "type": "add-missed",
            "start_ns": str(EPOCH_NS + 3_500_000_000),
            "end_ns": str(EPOCH_NS + 3_800_000_000),
            "reason": "Synthetic private-only event.",
        }
    )
    private_id = str(_records(app.state["candidates"])[-1]["id"])
    app.act(
        {
            "type": "approve",
            "candidate_id": private_id,
            "uncertainty_disposition": "accept_event",
            "uncertainty_reason": "Synthetic private-only event context is incomplete.",
        }
    )
    app.act({"type": "signoff", "checked": True})

    practice = build_export_document(
        app.state, "practice", spec_name="micro-high-signal",
        source_bounds=app.binding.source_bounds,
    )
    assert [item["label_id"] for item in practice["labels"]] == [candidate_id]
    assert "audit" not in practice and "source_id" not in practice
    truth = build_export_document(
        app.state, "organizer-private", spec_name="micro-high-signal",
        source_bounds=app.binding.source_bounds,
    )
    assert {item["interval_id"] for item in truth["intervals"]} == {
        candidate_id,
        private_id,
    }

    recipe = tmp_path / "recipe.json"
    product_root = tmp_path / "products"
    _write_json(
        recipe,
        {
            "attribution": "Synthetic fixture.",
            "contract": "civ.data-product-recipe/v1",
            "dataset": "kashiwa",
            "license": {"name": "Test-only", "url": None},
            "modifications": ["Filtered to the synthetic signal topic."],
            "product_name": "synthetic-signals.mcap",
            "recipe_id": "synthetic-signals-v1",
            "rights_scope": "Synthetic tests only.",
            "source": {
                "id": "synthetic-source",
                "sha256": file_sha256(args.source),
            },
            "split": "sealed",
            "topics": ["/micro/signal"],
            "version": 1,
        },
    )
    product_result = build_data_product(args.source, recipe, product_root)
    manifest = product_root / str(product_result["manifest"])
    _write_json(args.organizer_output, truth)
    output = tmp_path / "final-packs"
    build_label_packs([args.organizer_output], [manifest], output)
    assert audit_label_pack_set(output / "label-pack-set.json")["valid"] is True
    pack = load_label_pack(next((output / "packs").glob("*.json")), require_provenance=True)
    assert len(pack["labels"]) == 2


def test_saved_identity_and_candidate_membership_are_required(tmp_path: Path) -> None:
    args, app, candidate_id = _case(tmp_path / "case")
    _write_atomic(args.progress, f"{canonical_json(app.state)}\n")
    with pytest.raises(CivError, match="identity does not match"):
        _read_progress(
            args.progress,
            replace(
                app.binding,
                identity={**app.binding.identity, "spec_sha256": "0" * 64},
            ),
        )

    saved = json.loads(args.progress.read_text(encoding="utf-8"))
    saved["candidates"] = []
    _write_json(args.progress, saved)
    with pytest.raises(CivError, match="candidate set"):
        app.reload()
    with pytest.raises(CivError, match="candidate set"):
        from civ_workshop.organizer.label_review import review_command

        review_command(args)

    assert candidate_id not in json.loads(args.progress.read_text(encoding="utf-8"))["candidates"]


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("kind", "unknown", "candidate kind"),
        ("id", "forged-candidate", "identity changed"),
        ("start_ns", str(EPOCH_NS - 1), "outside source bounds"),
    ],
)
def test_reload_rejects_saved_candidate_kind_id_and_bounds(
    tmp_path: Path, field: str, value: str, message: str
) -> None:
    args, app, _ = _case(tmp_path / "case")
    app.save()
    saved = json.loads(args.progress.read_text(encoding="utf-8"))
    saved["candidates"][0][field] = value
    _write_json(args.progress, saved)
    with pytest.raises(CivError, match=message):
        app.reload()


def test_local_browser_is_loopback_token_gated_and_uses_exact_integer_fields(
    tmp_path: Path,
) -> None:
    _, app, _ = _case(tmp_path / "case")
    token = "synthetic-token"
    server = HTTPServer(("127.0.0.1", 0), _create_handler(app, token))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    host, port = server.server_address[:2]
    assert isinstance(host, str)
    assert isinstance(port, int)
    try:
        with urlopen(f"http://{host}:{port}/?token={token}", timeout=5) as response:
            html = response.read().decode("utf-8")
        assert 'id="start-ns"' in html
        assert "BigInt(candidate.start_ns)" in html
        request = Request(f"http://{host}:{port}/api/state?token=wrong")
        with pytest.raises(HTTPError) as error:
            urlopen(request, timeout=5)
        assert error.value.code == 403
        payload = json.dumps({"type": "set-reviewer", "name": "Synthetic reviewer"}).encode()
        request = Request(
            f"http://{host}:{port}/api/action",
            data=payload,
            headers={"Content-Type": "application/json", "X-CIV-Token": token},
            method="POST",
        )
        with urlopen(request, timeout=5) as response:
            result: dict[str, Any] = json.loads(response.read().decode("utf-8"))
        assert result["state"]["reviewer"] == "Synthetic reviewer"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def test_camera_context_refresh_cache_and_local_frame_ui(tmp_path: Path) -> None:
    _, app, candidate_id = _case(tmp_path / "case", with_camera_context=True)
    original = _records(app.state["candidates"])[0]
    original_start = original["start_ns"]
    original_end = original["end_ns"]
    assert original["context_status"] == "missing"

    token = "synthetic-camera-token"
    server = HTTPServer(("127.0.0.1", 0), _create_handler(app, token))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    host, port = server.server_address[:2]
    assert isinstance(host, str)
    assert isinstance(port, int)

    def post_action(payload: dict[str, object]) -> dict[str, object]:
        request = Request(
            f"http://{host}:{port}/api/action",
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json", "X-CIV-Token": token},
            method="POST",
        )
        with urlopen(request, timeout=5) as response:
            return _mapping(json.loads(response.read().decode("utf-8")))

    try:
        with urlopen(f"http://{host}:{port}/?token={token}", timeout=5) as response:
            html = response.read().decode("utf-8")
        assert 'id="frame"' in html
        assert "Synchronize signal and camera time" in html
        post_action({"type": "set-reviewer", "name": "Synthetic camera reviewer"})
        result = post_action(
            {
                "type": "edit",
                "candidate_id": candidate_id,
                "start_ns": str(EPOCH_NS + 3_000_000_000),
                "end_ns": str(EPOCH_NS + 4_000_000_000),
                "reason": "Synthetic adjustment to inspect the approved frame.",
            }
        )
        candidate = _records(_mapping(result["state"])["candidates"])[0]
        assert candidate["context_status"] == "available"
        assert candidate["camera_frames"] == [
            {"index": 0, "timestamp_ns": str(EPOCH_NS + 4_000_000_000)}
        ]
        assert _mapping(candidate["signals"])["signal"]
        with urlopen(
            f"http://{host}:{port}/api/frame/0?token={token}", timeout=5
        ) as response:
            assert response.headers.get_content_type() == "image/png"
            assert response.read() == _png_pixel()

        undone = _records(_mapping(post_action({"type": "undo"})["state"])["candidates"])[0]
        assert undone["start_ns"] == original_start
        assert undone["end_ns"] == original_end
        assert undone["context_status"] == "missing"
        assert undone["camera_frames"] == []
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def test_whole_source_window_outside_proposals_is_read_only(tmp_path: Path) -> None:
    _, app, _ = _case(tmp_path / "case", with_camera_context=True)
    before = canonical_json(app.state)
    evidence = app.evidence_window(
        {"start_ns": str(EPOCH_NS + 3_000_000_000), "end_ns": str(EPOCH_NS + 4_000_000_000)}
    )
    assert evidence["start_ns"] == str(EPOCH_NS + 3_000_000_000)
    assert evidence["end_ns"] == str(EPOCH_NS + 4_000_000_000)
    assert evidence["signals"]["signal"][-1]["timestamp_ns"] == str(EPOCH_NS + 4_000_000_000)
    assert evidence["camera_frames"]
    assert canonical_json(app.state) == before
    assert "source_bounds" in app.view()
    with pytest.raises(CivError, match="source bounds"):
        app.evidence_window({"start_ns": str(EPOCH_NS - 1), "end_ns": str(EPOCH_NS + 1)})
    app.binding.source_path.write_bytes(b"changed")
    with pytest.raises(CivError, match="changed"):
        app.evidence_window({"start_ns": str(EPOCH_NS), "end_ns": str(EPOCH_NS + 1)})


def test_zero_proposals_can_inspect_and_add_missed_event(tmp_path: Path) -> None:
    args, _, _ = _case(tmp_path / "case")
    args.spec.write_text(MICRO_SPEC.replace("signal > 1.0", "signal > 99.0"))
    # Preserve the original run and create a distinct revision with no proposals.
    run = tmp_path / "zero-run"
    detect_events(args.spec, args.source, run)
    args.events = run / "events.jsonl"
    args.manifest = run / "run-manifest.json"
    binding, events, _, before_ns, after_ns = _prepare_binding(args)
    assert not events
    app = ReviewApplication(
        binding,
        initial_review_state(binding, events, binding.evidence_by_id),
        before_ns=before_ns,
        after_ns=after_ns,
    )
    evidence = app.evidence_window(
        {"start_ns": str(EPOCH_NS), "end_ns": str(EPOCH_NS + 4_000_000_000)}
    )
    assert evidence["signals"]["signal"]
    app.act({"type": "set-reviewer", "name": "Fixture reviewer"})
    app.act(
        {
            "type": "add-missed",
            "start_ns": str(EPOCH_NS + 1_000_000_000),
            "end_ns": str(EPOCH_NS + 2_000_000_000),
            "reason": "Fixture event found in full source",
        }
    )
    assert gate_review(app.state)
    with pytest.raises(CivError, match="does not match"):
        _read_progress(
            args.progress, replace(binding, identity={**binding.identity, "spec_sha256": "a" * 64})
        )


def test_checked_windows_save_reload_edit_invalidation_and_undo(tmp_path: Path) -> None:
    _, app, candidate_id = _case(tmp_path / "case")
    app.act({"type": "set-reviewer", "name": "Fixture reviewer"})
    app.act(
        {"type": "check-window", "start_ns": str(EPOCH_NS), "end_ns": str(EPOCH_NS + 4_000_000_000)}
    )
    assert app.state["coverage_reviewed"] is False
    assert gate_review(app.state)
    app.reload()
    assert app.state["checked_windows"]
    app.act(
        {
            "type": "edit",
            "candidate_id": candidate_id,
            "start_ns": str(EPOCH_NS + 1_100_000_000),
            "end_ns": str(EPOCH_NS + 1_900_000_000),
            "reason": "Fixture boundary correction",
        }
    )
    assert app.state["checked_windows"] == []
    app.act({"type": "undo"})
    assert app.state["checked_windows"]
    assert app.state["coverage_reviewed"] is False


def test_evidence_beyond_every_detected_window(tmp_path: Path) -> None:
    _, app, candidate_id = _case(
        tmp_path / "long", source_values=(0.0, 2.0, 2.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
    )
    original = _mapping(app.binding.evidence_by_id[candidate_id]["signals"])
    original_points = _records(original["signal"])
    assert (
        max(int(str(point["timestamp_ns"])) for point in original_points)
        <= EPOCH_NS + 4_000_000_000
    )
    evidence = app.evidence_window(
        {"start_ns": str(EPOCH_NS + 6_000_000_000), "end_ns": str(EPOCH_NS + 8_000_000_000)}
    )
    assert len(evidence["signals"]["signal"]) == 3
    assert evidence["signals"]["signal"][0]["timestamp_ns"] == str(EPOCH_NS + 6_000_000_000)
    assert evidence["status"] == "missing"
    assert gate_review(app.state)


def test_window_http_auth_bounds_and_exact_nanoseconds(tmp_path: Path) -> None:
    _, app, _ = _case(tmp_path / "case")
    server = HTTPServer(("127.0.0.1", 0), _create_handler(app, "fixture-token"))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    url = f"http://127.0.0.1:{server.server_port}/api/window"
    body = json.dumps({"start_ns": str(EPOCH_NS), "end_ns": str(EPOCH_NS + 4_000_000_000)}).encode()
    try:
        with pytest.raises(HTTPError) as denied:
            urlopen(Request(url, data=body), timeout=5)
        assert denied.value.code == 403
        with urlopen(
            Request(url, data=body, headers={"X-CIV-Token": "fixture-token"}), timeout=5
        ) as response:
            result = json.load(response)
        assert result["start_ns"] == str(EPOCH_NS)
        assert result["end_ns"] == str(EPOCH_NS + 4_000_000_000)
        invalid = json.dumps({"start_ns": True, "end_ns": str(EPOCH_NS + 1)}).encode()
        with pytest.raises(HTTPError) as rejected:
            urlopen(Request(url, data=invalid, headers={"X-CIV-Token": "fixture-token"}), timeout=5)
        assert rejected.value.code == 400
    finally:
        server.shutdown()
        thread.join(timeout=5)
        server.server_close()


def _reduced_case(root: Path, *, split: str = "warmup") -> Namespace:
    args, _, _ = _case(root, with_camera_context=True)
    original_source = args.source
    recipe = root / "warmup-recipe.json"
    _write_json(
        recipe,
        {
            "attribution": "Synthetic fixture",
            "contract": "civ.data-product-recipe/v1",
            "dataset": "kashiwa",
            "license": {"name": "Test-only", "url": None},
            "modifications": ["Filtered synthetic signals"],
            "product_name": "warmup-signals.mcap",
            "recipe_id": "fixture-warmup-v1",
            "rights_scope": "Synthetic tests only",
            "source": {"id": "synthetic-source", "sha256": file_sha256(original_source)},
            "split": split,
            "topics": ["/micro/signal"],
            "version": 1,
        },
    )
    products = root / "products"
    result = build_data_product(original_source, recipe, products)
    args.source = products / "warmup-signals.mcap"
    args.signal_product_manifest = products / str(result["manifest"])
    camera = json.loads(args.camera_context_manifest.read_text(encoding="utf-8"))
    camera["split"] = split
    camera["signal_product"] = {
        "name": args.source.name,
        "sha256": file_sha256(args.source),
        "manifest": args.signal_product_manifest.name,
        "manifest_sha256": file_sha256(args.signal_product_manifest),
    }
    _write_json(args.camera_context_manifest, camera)
    run = root / "reduced-run"
    detect_events(args.spec, args.source, run)
    args.events = run / "events.jsonl"
    args.manifest = run / "run-manifest.json"
    return args


def test_reduced_product_review_requires_exact_context_manifest_binding(tmp_path: Path) -> None:
    args = _reduced_case(tmp_path / "case")
    binding, events, _, before_ns, after_ns = _prepare_binding(args)
    assert binding.identity["source_sha256"] == file_sha256(args.source)
    assert binding.identity["signal_product_manifest_sha256"] == file_sha256(
        args.signal_product_manifest
    )
    assert binding.camera_frames is not None
    app = ReviewApplication(
        binding,
        initial_review_state(binding, events, binding.evidence_by_id),
        before_ns=before_ns,
        after_ns=after_ns,
    )
    _record_review(app, events[0].event_id)
    practice = build_export_document(
        app.state, "practice", spec_name=binding.spec_name, source_bounds=binding.source_bounds
    )
    assert practice["source_sha256"] == file_sha256(args.source)
    app.save()
    app.reload()
    args.signal_product_manifest.write_text(
        args.signal_product_manifest.read_text(encoding="utf-8") + " "
    )
    with pytest.raises(CivError, match="signal-product manifest changed"):
        app.reload()
    with pytest.raises(CivError, match="signal-product manifest changed"):
        app.act({"type": "signoff", "checked": True})
    with pytest.raises(CivError, match="signal-product manifest changed"):
        app.export("practice")


@pytest.mark.parametrize("field", ["manifest_sha256", "sha256", "name"])
def test_reduced_context_rejects_wrong_signal_identity(tmp_path: Path, field: str) -> None:
    args = _reduced_case(tmp_path / "case")
    camera = json.loads(args.camera_context_manifest.read_text(encoding="utf-8"))
    camera["signal_product"][field] = "wrong.mcap" if field == "name" else "b" * 64
    _write_json(args.camera_context_manifest, camera)
    with pytest.raises(CivError, match="signal-product identity"):
        _prepare_binding(args)


def test_reduced_context_requires_explicit_sidecar_and_preserves_sealed_only_builder(
    tmp_path: Path,
) -> None:
    from civ_workshop.label_packs import _product_binding

    args = _reduced_case(tmp_path / "case")
    with pytest.raises(CivError, match="require sealed"):
        _product_binding(args.signal_product_manifest)
    args.signal_product_manifest = None
    with pytest.raises(CivError, match="source identity"):
        _prepare_binding(args)


@pytest.mark.parametrize("change", ["parent", "dataset", "split"])
def test_reduced_context_rejects_cross_source_or_membership(tmp_path: Path, change: str) -> None:
    args = _reduced_case(tmp_path / "case")
    camera = json.loads(args.camera_context_manifest.read_text(encoding="utf-8"))
    if change == "parent":
        camera["parent"]["sha256"] = "b" * 64
    elif change == "dataset":
        camera["dataset"] = "reims"
    else:
        camera["split"] = "development"
    _write_json(args.camera_context_manifest, camera)
    with pytest.raises(CivError, match="identity|dataset"):
        _prepare_binding(args)


@pytest.mark.parametrize("split", ["warmup", "development"])
def test_nonsealed_product_refuses_private_export_and_preserves_practice(
    tmp_path: Path, split: str
) -> None:
    args = _reduced_case(tmp_path / "case", split=split)
    binding, events, _, before_ns, after_ns = _prepare_binding(args)
    app = ReviewApplication(
        binding,
        initial_review_state(binding, events, binding.evidence_by_id),
        before_ns=before_ns,
        after_ns=after_ns,
    )
    _record_review(app, events[0].event_id)
    app.save()
    saved_progress = args.progress.read_bytes()
    app.reload()
    assert gate_review(app.state) == []
    with pytest.raises(CivError, match="warm-up/development"):
        app.export("organizer-private")
    assert not args.organizer_output.exists()
    assert args.progress.read_bytes() == saved_progress
    with pytest.raises(CivError, match="warm-up/development"):
        build_export_document(
            app.state, "organizer-private", spec_name=binding.spec_name,
            source_bounds=binding.source_bounds,
        )
    view = app.view()
    outputs = view["outputs"]
    blockers = view["output_blockers"]
    assert isinstance(outputs, dict) and isinstance(blockers, dict)
    assert outputs["organizer-private"] is False
    assert outputs["practice"] is True
    assert "warm-up/development" in blockers["organizer-private"]
    app.export("practice")
    practice = json.loads(args.practice_output.read_text(encoding="utf-8"))
    assert practice["source_sha256"] == file_sha256(args.source)
    assert practice == build_export_document(
        app.state, "practice", spec_name=binding.spec_name, source_bounds=binding.source_bounds
    )
    progress = json.loads(args.progress.read_text(encoding="utf-8"))
    assert progress["exports"]["practice"]["sha256"] == file_sha256(args.practice_output)


def test_launch_guidance_does_not_create_reviewer_or_decisions(tmp_path: Path) -> None:
    _, original, _ = _case(tmp_path, with_camera_context=True)
    app = ReviewApplication(
        original.binding,
        original.state,
        before_ns=original.before_ns,
        after_ns=original.after_ns,
        review_rule="Synthetic contextual rule, not a threshold",
        default_reviewer="Fixture reviewer",
    )
    before = canonical_json(app.state)
    view = app.view()
    assert view["review_rule"] == "Synthetic contextual rule, not a threshold"
    assert view["default_reviewer"] == "Fixture reviewer"
    assert canonical_json(app.state) == before
    assert "Name the reviewer." in gate_review(app.state)
    assert all(item["decision"] == "pending" for item in _records(app.state["candidates"]))


def test_launch_hints_preserve_saved_review_and_consumer_output(tmp_path: Path) -> None:
    _, original, candidate_id = _case(tmp_path, with_camera_context=True)
    _record_review(original, candidate_id)
    original.save()
    before = canonical_json(original.state)
    app = ReviewApplication(
        original.binding,
        _read_progress(original.binding.progress_path, original.binding),
        before_ns=original.before_ns,
        after_ns=original.after_ns,
        review_rule="Synthetic guidance only",
        default_reviewer="Different launch hint",
    )
    view = app.reload()
    assert canonical_json(app.state) == before
    assert _mapping(view["state"])["reviewer"] == original.state["reviewer"]
    assert gate_review(app.state) == []
    document = build_export_document(
        app.state, "practice", spec_name=app.binding.spec_name,
        source_bounds=app.binding.source_bounds,
    )
    assert document == build_export_document(
        original.state, "practice", spec_name=original.binding.spec_name,
        source_bounds=original.binding.source_bounds,
    )
    assert "review_rule" not in document and "default_reviewer" not in document


def _organizer_camera_case(root: Path) -> Namespace:
    args, _, _ = _case(root, with_camera_context=True)
    camera_manifest = json.loads(args.camera_context_manifest.read_text())
    camera_path = root / camera_manifest["product"]["name"]
    raw = root / "private-original.mcap"
    from mcap.reader import make_reader

    with raw.open("wb") as stream:
        writer = Writer(stream, compression=CompressionType.NONE)
        writer.start()
        for part in (args.source, camera_path):
            with part.open("rb") as source_stream:
                reader = make_reader(source_stream)
                channels = {}
                for schema, channel, message in reader.iter_messages():
                    if channel.id not in channels:
                        assert schema is not None
                        sid = writer.register_schema(schema.name, schema.encoding, schema.data)
                        channels[channel.id] = writer.register_channel(
                            channel.topic, channel.message_encoding, sid
                        )
                    timestamp = (
                        EPOCH_NS + 2_000_000_000 if part == camera_path else message.log_time
                    )
                    writer.add_message(channels[channel.id], timestamp, message.data, timestamp)
        writer.finish()
    recipe = root / "sealed-recipe.json"
    _write_json(
        recipe,
        {
            "contract": "civ.data-product-recipe/v1",
            "recipe_id": "private-test-v1",
            "version": 1,
            "product_name": "sealed-signals.mcap",
            "source": {"id": "synthetic-source", "sha256": file_sha256(raw)},
            "dataset": "kashiwa",
            "split": "sealed",
            "topics": ["/micro/signal"],
            "license": {"name": "Synthetic fixture", "url": None},
            "attribution": "Synthetic fixture",
            "rights_scope": "Synthetic tests only",
            "modifications": ["Signals only"],
        },
    )
    result = build_data_product(raw, recipe, root / "sealed")
    args.source = root / "sealed/sealed-signals.mcap"
    args.signal_product_manifest = root / "sealed" / str(result["manifest"])
    args.camera_context_manifest = None
    args.practice_output = None
    args.organizer_camera_manifest = root / "private-camera.json"
    _write_json(
        args.organizer_camera_manifest,
        {
            "contract": "civ.organizer-camera-context/v1",
            "dataset": "kashiwa",
            "source_id": "synthetic-source",
            "source": {"path": str(raw.resolve()), "sha256": file_sha256(raw)},
            "image_topic": CAMERA_TOPIC,
            "authorization": {
                "authority": "Synthetic owner",
                "scope": "organizer-local-review",
                "statement": "Synthetic fixture only",
            },
        },
    )
    detect_events(args.spec, args.source, root / "private-run")
    args.events = root / "private-run/events.jsonl"
    args.manifest = root / "private-run/run-manifest.json"
    return args


def test_private_sealed_camera_and_parent_bound_export(tmp_path: Path) -> None:
    args = _organizer_camera_case(tmp_path)
    binding, events, _, before, after = _prepare_binding(args)
    app = ReviewApplication(
        binding,
        initial_review_state(binding, events, binding.evidence_by_id),
        before_ns=before,
        after_ns=after,
    )
    assert binding.camera_frames is not None
    assert app.frame(0)[0] == "image/png"
    assert app.view()["outputs"] == {"organizer-private": True, "practice": False}
    assert app.view()["gate"]
    assert not args.organizer_output.exists()
    app.act({"type": "set-reviewer", "name": "Synthetic reviewer"})
    app.act(
        {"type": "approve", "candidate_id": events[0].event_id, "uncertainty_disposition": "clear"}
    )
    app.act({"type": "signoff", "checked": True})
    app.export("organizer-private")
    truth = json.loads(args.organizer_output.read_text())
    raw = json.loads(args.organizer_camera_manifest.read_text())["source"]
    assert truth["intervals"][0]["source_sha256"] == raw["sha256"]
    packs = tmp_path / "private-packs"
    build_label_packs([args.organizer_output], [args.signal_product_manifest], packs)
    assert audit_label_pack_set(packs / "label-pack-set.json")["valid"] is True
    assert args.progress.exists()


@pytest.mark.parametrize("completed", [False, True])
def test_private_camera_review_reopens_revises_and_reexports(
    tmp_path: Path, completed: bool,
) -> None:
    args = _organizer_camera_case(tmp_path)
    binding, events, _, before, after = _prepare_binding(args)
    app = ReviewApplication(
        binding, initial_review_state(binding, events, binding.evidence_by_id),
        before_ns=before, after_ns=after,
    )
    app.act({"type": "set-reviewer", "name": "Synthetic reviewer"})
    app.act({
        "type": "approve", "candidate_id": events[0].event_id,
        "uncertainty_disposition": "clear",
    })
    app.save()
    if completed:
        app.act({"type": "signoff", "checked": True})
        app.export("organizer-private")
    previous_progress = args.progress.read_bytes()
    previous_truth = args.organizer_output.read_bytes() if completed else None
    reopened = _reopen(args)
    reopened.save()
    assert args.progress.read_bytes() == previous_progress
    if previous_truth is not None:
        assert args.organizer_output.read_bytes() == previous_truth
    candidate = _records(reopened.state["candidates"])[0]
    assert candidate["decision"] == "approved"
    assert reopened.state["coverage_reviewed"] is completed
    start_ns = int(str(candidate["start_ns"])) + 10
    reopened.act({
        "type": "edit", "candidate_id": events[0].event_id,
        "start_ns": str(start_ns), "end_ns": candidate["end_ns"],
        "reason": "Synthetic boundary revision after reopening.",
    })
    assert gate_review(reopened.state)
    reopened.act({
        "type": "approve", "candidate_id": events[0].event_id,
        "uncertainty_disposition": "clear",
    })
    reopened.act({"type": "signoff", "checked": True})
    reopened.export("organizer-private")
    truth = json.loads(args.organizer_output.read_text())
    assert truth["intervals"][0]["start_ns"] == start_ns
    assert truth["intervals"][0]["source_sha256"] == binding.identity["source_parent_sha256"]
    _archived_snapshot(args.progress, previous_progress)
    if previous_truth is not None:
        _archived_snapshot(args.organizer_output, previous_truth)
    assert gate_review(_reopen(args).state) == []
    packs = tmp_path / "revised-packs"
    build_label_packs([args.organizer_output], [args.signal_product_manifest], packs)
    assert audit_label_pack_set(packs / "label-pack-set.json")["valid"] is True


def test_private_camera_authorization_change_blocks_review_write(tmp_path: Path) -> None:
    args = _organizer_camera_case(tmp_path)
    binding, events, _, before, after = _prepare_binding(args)
    app = ReviewApplication(
        binding, initial_review_state(binding, events, binding.evidence_by_id),
        before_ns=before, after_ns=after,
    )
    app.save()
    progress_before = args.progress.read_bytes()
    document = json.loads(args.organizer_camera_manifest.read_text())
    document["authorization"]["scope"] = "revoked"
    _write_json(args.organizer_camera_manifest, document)
    with pytest.raises(CivError, match="camera"):
        app.act({"type": "set-reviewer", "name": "Synthetic reviewer"})
    assert args.progress.read_bytes() == progress_before
    assert not args.organizer_output.exists()


@pytest.mark.parametrize("target", ["progress", "organizer_output"])
def test_private_camera_authorization_cannot_be_overwritten(tmp_path: Path, target: str) -> None:
    args = _organizer_camera_case(tmp_path)
    original = args.organizer_camera_manifest.read_bytes()
    setattr(args, target, args.organizer_camera_manifest)
    with pytest.raises(CivError, match="separate paths"):
        _prepare_binding(args)
    assert args.organizer_camera_manifest.read_bytes() == original


@pytest.mark.parametrize(
    "change",
    [
        "scope",
        "hash",
        "source",
        "dataset",
        "topic",
        "practice",
        "no-manifest",
        "mixed",
        "nonsealed",
    ],
)
def test_private_camera_rejects_unauthorized_or_mismatched_inputs(
    tmp_path: Path, change: str
) -> None:
    args = _organizer_camera_case(tmp_path)
    document = json.loads(args.organizer_camera_manifest.read_text())
    if change == "scope":
        document["authorization"]["scope"] = "participant-distribution"
    elif change == "hash":
        document["source"]["sha256"] = "0" * 64
    elif change == "source":
        document["source_id"] = "different-source"
    elif change == "dataset":
        document["dataset"] = "reims"
    elif change == "topic":
        document["image_topic"] = "/micro/signal"
    elif change == "practice":
        args.practice_output = tmp_path / "must-not-exist.json"
    elif change == "no-manifest":
        args.signal_product_manifest = None
    elif change == "mixed":
        args.camera_context_manifest = tmp_path / "approved-camera-context.manifest.json"
    elif change == "nonsealed":
        manifest = json.loads(args.signal_product_manifest.read_text())
        manifest["provenance"]["split"] = "development"
        _write_json(args.signal_product_manifest, manifest)
    _write_json(args.organizer_camera_manifest, document)
    with pytest.raises(CivError):
        _prepare_binding(args)
    assert not args.organizer_output.exists()


def test_adding_private_camera_requires_new_progress_identity(tmp_path: Path) -> None:
    args = _organizer_camera_case(tmp_path)
    camera = args.organizer_camera_manifest
    signal = args.signal_product_manifest
    args.organizer_camera_manifest = None
    args.signal_product_manifest = None
    old, events, _, _, _ = _prepare_binding(args)
    _write_atomic(
        args.progress, canonical_json(initial_review_state(old, events, old.evidence_by_id))
    )
    original = args.progress.read_bytes()
    args.organizer_camera_manifest = camera
    args.signal_product_manifest = signal
    current, _, _, _, _ = _prepare_binding(args)
    with pytest.raises(CivError, match="identity"):
        _read_progress(args.progress, current)
    assert args.progress.read_bytes() == original
