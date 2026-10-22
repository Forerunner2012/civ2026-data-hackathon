from __future__ import annotations

import json
import sys
from datetime import datetime
from hashlib import sha256
from pathlib import Path
from types import SimpleNamespace
from typing import Any, cast

import pytest
from mcap.reader import make_reader

from civ_workshop import __version__
from civ_workshop.artifacts import file_sha256
from civ_workshop.batch import run_batch
from civ_workshop.cohort_scoring import (
    _aggregate_detection,
    _run_replay,
    _select_receipt,
    input_fingerprint,
    load_evaluation_plan,
)
from civ_workshop.errors import CivError
from civ_workshop.intake import IntakeLedger, IntakeReceipt
from civ_workshop.organizer.scoring_readiness import check_readiness
from civ_workshop.reporting import build_report_bundle
from civ_workshop.runtime_identity import measured_runtime_identity
from tests.helpers import MICRO_REPORT, create_micro_case, prepare_scored_submission

ON_TIME = "2026-09-03T11:30:00+09:00"


def _product_contract(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    topics: dict[str, dict[str, str]] = {}
    with path.open("rb") as stream:
        for schema, channel, _message in make_reader(stream, validate_crcs=True).iter_messages():
            topics[channel.topic] = {
                "topic": channel.topic,
                "schema_name": schema.name if schema is not None else "",
                "schema_encoding": schema.encoding if schema is not None else "",
                "schema_sha256": sha256(schema.data).hexdigest()
                if schema is not None
                else "0" * 64,
                "message_encoding": channel.message_encoding,
            }
    selected = [topics["/micro/signal"]]
    return ["/micro/signal"], selected


def _truth(path: Path, source_sha256: str, *, empty: bool = False) -> None:
    document = {
        "contract": "civ.label-pack/v1alpha1",
        "dataset": "micro",
        "source_sha256": source_sha256,
        "labels": []
        if empty
        else [{"label_id": "target", "start_ns": 1_000_000_000, "end_ns": 2_000_000_000}],
        "data_gaps": [],
    }
    path.write_text(json.dumps(document, sort_keys=True), encoding="utf-8")


def _product_record(
    case: Any,
    *,
    product_id: str,
    partition: str,
    track_id: str,
) -> dict[str, Any]:
    topics, schemas = _product_contract(case.bag)
    manifest_path = case.root / f"{product_id}.manifest.json"
    manifest = {
        "contract": "civ.data-product-manifest/v1",
        "product": {
            "name": case.bag.name,
            "sha256": file_sha256(case.bag),
            "byte_size": case.bag.stat().st_size,
            "topics": [{**schema, "message_count": 1} for schema in schemas],
        },
        "provenance": {"dataset": "micro", "split": partition},
    }
    manifest_path.write_text(json.dumps(manifest, sort_keys=True), encoding="utf-8")
    truth_path = case.root / f"{track_id}-{product_id}.truth.json"
    _truth(
        truth_path,
        file_sha256(case.bag),
        empty=track_id.endswith("empty"),
    )
    return {
        "product_id": product_id,
        "partition": partition,
        "recording": {"path": str(case.bag), "sha256": file_sha256(case.bag)},
        "manifest": {"path": str(manifest_path), "sha256": file_sha256(manifest_path)},
        "truth": {"path": str(truth_path), "sha256": file_sha256(truth_path)},
        "input_contract": {"topics": topics, "schemas": schemas},
    }


def _plan_for_case(
    tmp_path: Path,
    case: Any,
    track_ids: tuple[str, ...] = ("micro-turn",),
    *,
    tie_break: str = "later_ledger_sequence",
    participants: tuple[str, ...] = ("team-a",),
) -> Path:
    tracks: list[dict[str, Any]] = []
    for track_id in track_ids:
        tracks.append(
            {
                "track_id": track_id,
                "dataset": "micro",
                "target": f"synthetic target {track_id}",
                "replay": {
                    "event_spec_contracts": ["civ.eventspec/v1"],
                    "allowed_topics": ["/micro/signal"],
                    "resource_limits": {"max_files": 0, "max_bytes": 0},
                    "timeout_seconds": 30,
                    "retries": 0,
                },
                "products": [
                    _product_record(
                        case,
                        product_id="micro-sealed",
                        partition="sealed",
                        track_id=track_id,
                    )
                ],
            }
        )
    plan = {
        "contract": "civ.evaluation-plan/v1alpha2",
        "session_id": "synthetic-cohort",
        "cutoff": "2026-09-03T12:30:00+09:00",
        "runtime": {
            "identity": "synthetic-local-runtime",
            "tool_version": __version__,
            "python_version": (
                f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
            ),
            **measured_runtime_identity(),
        },
        "participants": list(participants),
        "tracks": tracks,
        "scoring_policy": {
            "temporal_iou_threshold": 0.5,
            "matching": "one_to_one_best",
            "product_weights": {track_id: {"micro-sealed": 1.0} for track_id in track_ids},
            "score_bearing_partitions": ["sealed"],
            "missing_track": "zero",
            "failed_run": "zero",
            "empty_truth": "perfect_empty",
            "cross_product_events": "score_within_product",
            "rounding": {"decimal_places": 6, "mode": "half_even"},
            "receipt_timestamp_ties": tie_break,
            "detection_points": {track_id: 15.0 for track_id in track_ids},
            "evidence_policy_id": "synthetic-evidence-policy",
            "reproducibility_policy_id": "synthetic-reproducibility-policy",
        },
    }
    path = tmp_path / "evaluation-plan.json"
    path.write_text(json.dumps(plan, sort_keys=True), encoding="utf-8")
    return path


def _bundle(tmp_path: Path, values: tuple[float, ...], *, marker: str) -> Path:
    case = create_micro_case(tmp_path / f"submission-{marker}", values=values)
    working = tmp_path / f"working-{marker}"
    prepare_scored_submission(case, working)
    script_marker = tmp_path / "script-ran.txt"
    (working / "reproduce.ps1").write_text(
        f"civ detect detector/detector.yaml micro.mcap\nSet-Content '{script_marker}' '{marker}'\n",
        encoding="utf-8",
    )
    (working / "report.md").write_text(
        f"{MICRO_REPORT}\nSynthetic submission: {marker}\n", encoding="utf-8"
    )
    build_report_bundle(working)
    return working / "submission.zip"


def _results(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in (path / "results.jsonl").read_text().splitlines()]


def test_score_batch_replays_event_spec_against_each_track_truth_and_never_runs_script(
    tmp_path: Path,
) -> None:
    product_case = create_micro_case(tmp_path / "sealed-product")
    plan = _plan_for_case(tmp_path, product_case, ("micro-turn", "micro-empty"))
    ledger = IntakeLedger(tmp_path / "ledger")
    bundle = _bundle(tmp_path, (0.0, 0.0, 0.0, 0.0, 0.0), marker="participant-no-events")
    for track_id in ("micro-turn", "micro-empty"):
        ledger.accept_local(
            identity="team-a",
            track_id=track_id,
            received_at=ON_TIME,
            submitted_sha256=file_sha256(bundle),
            bundle_path=bundle,
            delivery_id=f"{track_id}-delivery",
        )

    summary = run_batch(ledger.root, None, tmp_path / "results", plan_path=plan)

    records = _results(tmp_path / "results")
    assert summary["outcomes"] == 2
    assert len(records) == 2
    by_track = {record["track_id"]: record for record in records}
    assert by_track["micro-turn"]["status"] == "scored"
    assert by_track["micro-turn"]["metrics"]["aggregate"]["counts"]["true_positive"] == 1
    assert by_track["micro-turn"]["replay"]["event_count"] == 1
    assert by_track["micro-empty"]["status"] == "scored"
    assert by_track["micro-empty"]["metrics"]["aggregate"]["counts"]["false_positive"] == 1
    assert by_track["micro-empty"]["replay"]["zero_events"] is False
    computed = cast(dict[str, Any], summary["computed_detection"])["participants"]["team-a"][
        "tracks"
    ]
    assert computed["micro-turn"]["detection_points"] == 15.0
    assert computed["micro-empty"]["detection_points"] == 0.0
    assert not (tmp_path / "script-ran.txt").exists()
    replay_files = sorted((tmp_path / "results" / "replays").rglob("events.jsonl"))
    assert replay_files
    first_results = (tmp_path / "results" / "results.jsonl").read_bytes()
    first_summary = (tmp_path / "results" / "summary.json").read_bytes()
    first_replays = [path.read_bytes() for path in replay_files]

    run_batch(ledger.root, None, tmp_path / "results", plan_path=plan)

    assert (tmp_path / "results" / "results.jsonl").read_bytes() == first_results
    assert (tmp_path / "results" / "summary.json").read_bytes() == first_summary
    assert [path.read_bytes() for path in replay_files] == first_replays


def test_successful_zero_event_replay_is_distinct_from_failure(tmp_path: Path) -> None:
    case = create_micro_case(tmp_path / "sealed-product", values=(0.0, 0.0, 0.0, 0.0, 0.0))
    plan = _plan_for_case(tmp_path, case, ("micro-empty",), participants=("team-quiet",))
    ledger = IntakeLedger(tmp_path / "ledger")
    bundle = _bundle(tmp_path, (0.0, 0.0, 0.0, 0.0, 0.0), marker="quiet-team")
    ledger.accept_local(
        identity="team-quiet",
        track_id="micro-empty",
        received_at=ON_TIME,
        submitted_sha256=file_sha256(bundle),
        bundle_path=bundle,
        delivery_id="quiet-delivery",
    )

    summary = run_batch(ledger.root, None, tmp_path / "results", plan_path=plan)

    record = _results(tmp_path / "results")[0]
    assert record["status"] == "scored"
    assert record["replay"]["event_count"] == 0
    assert record["replay"]["zero_events"] is True
    assert record["failure"] is None
    computed = cast(dict[str, Any], summary["computed_detection"])
    participants = cast(dict[str, Any], computed["participants"])
    quiet_track = cast(dict[str, Any], participants["team-quiet"])["tracks"]["micro-empty"]
    assert quiet_track["detection_points"] == 15.0


def test_score_batch_replays_all_assigned_partitions(tmp_path: Path) -> None:
    warmup = create_micro_case(tmp_path / "warmup-product", values=(0.0, 0.0, 0.0, 0.0, 0.0))
    development = create_micro_case(
        tmp_path / "development-product", values=(0.0, 3.0, 3.0, 0.0, 0.0)
    )
    sealed = create_micro_case(tmp_path / "sealed-product", values=(0.0, 2.0, 2.0, 0.0, 0.0))
    plan = _plan_for_case(tmp_path, sealed, participants=("team-all",))
    plan_document = json.loads(plan.read_text())
    track = plan_document["tracks"][0]
    track["products"] = [
        _product_record(
            warmup, product_id="micro-warmup", partition="warmup", track_id="micro-turn"
        ),
        _product_record(
            development,
            product_id="micro-development",
            partition="development",
            track_id="micro-turn",
        ),
        _product_record(
            sealed, product_id="micro-sealed", partition="sealed", track_id="micro-turn"
        ),
    ]
    plan.write_text(json.dumps(plan_document, sort_keys=True), encoding="utf-8")
    ledger = IntakeLedger(tmp_path / "ledger")
    bundle = _bundle(tmp_path, (0.0, 2.0, 2.0, 0.0, 0.0), marker="all-partitions")
    ledger.accept_local(
        identity="team-all",
        track_id="micro-turn",
        received_at=ON_TIME,
        submitted_sha256=file_sha256(bundle),
        bundle_path=bundle,
        delivery_id="all-partitions-delivery",
    )

    summary = run_batch(ledger.root, None, tmp_path / "results", plan_path=plan)

    records = _results(tmp_path / "results")
    assert summary["outcomes"] == 3
    assert {record["partition"] for record in records} == {
        "warmup",
        "development",
        "sealed",
    }
    assert all(record["status"] == "scored" for record in records)
    assert sum(record["replay"]["event_count"] for record in records) == 2


def test_replay_failure_reports_attempts_and_stable_diagnostics(
    tmp_path: Path, monkeypatch: Any
) -> None:
    submission = tmp_path / "private-submission-path"
    spec_path = submission / "detector" / "detector.yaml"
    product_path = tmp_path / "private-product-path" / "recording.mcap"
    output_path = tmp_path / "private-output-path"
    calls = 0

    def fail_replay(*_args: Any, **_kwargs: Any) -> SimpleNamespace:
        nonlocal calls
        calls += 1
        return SimpleNamespace(
            returncode=1,
            stderr=f"failed {spec_path} {product_path} {output_path}",
        )

    monkeypatch.setattr("civ_workshop.cohort_scoring.subprocess.run", fail_replay)

    succeeded, failure, attempts = _run_replay(
        spec_path,
        product_path,
        output_path,
        timeout_seconds=1,
        retries=2,
    )

    assert succeeded is False
    assert attempts == calls == 3
    assert failure is not None
    assert failure.startswith("failed <submission>")
    assert failure.endswith(" <product> <replay-output>")
    assert str(tmp_path) not in failure


def test_detection_points_use_unrounded_weighted_f1(tmp_path: Path) -> None:
    case = create_micro_case(tmp_path / "sealed-product")
    plan_path = _plan_for_case(tmp_path, case)
    plan = json.loads(plan_path.read_text())
    plan["scoring_policy"]["rounding"] = {"decimal_places": 1, "mode": "half_up"}
    record = {
        "identity": "team-rounding",
        "track_id": "micro-turn",
        "product_id": "micro-sealed",
        "status": "scored",
        "metrics": {
            "aggregate": {"counts": {"true_positive": 1, "false_positive": 0, "false_negative": 1}}
        },
    }

    computed, blockers = _aggregate_detection([record], plan)

    assert blockers == []
    assert computed is not None
    track_score = computed["participants"]["team-rounding"]["tracks"]["micro-turn"]
    assert track_score["f1"] == 0.7
    assert track_score["detection_points"] == 10.0


def test_latest_track_receipt_is_selected_and_corrupt_latest_does_not_fall_back(
    tmp_path: Path,
) -> None:
    case = create_micro_case(tmp_path / "sealed-product")
    plan = _plan_for_case(tmp_path, case)
    ledger = IntakeLedger(tmp_path / "ledger")
    older = _bundle(tmp_path, (0.0, 2.0, 2.0, 0.0, 0.0), marker="older")
    latest = _bundle(tmp_path, (0.0, 0.0, 0.0, 0.0, 0.0), marker="latest")
    for bundle, delivery_id in ((older, "older"), (latest, "latest")):
        ledger.accept_local(
            identity="team-a",
            track_id="micro-turn",
            received_at=ON_TIME,
            submitted_sha256=file_sha256(bundle),
            bundle_path=bundle,
            delivery_id=delivery_id,
        )
    selected = ledger.receipts()[-1]
    ledger.bundle_for(selected).write_bytes(b"corrupted after intake")

    run_batch(ledger.root, None, tmp_path / "results", plan_path=plan)

    record = _results(tmp_path / "results")[0]
    assert record["selected_submission"]["delivery_id"] == "latest"
    assert record["status"] == "failed"
    assert record["replay"]["attempts"] == 0
    assert record["replay"]["failure_stage"] == "submission_validation"
    assert "missing or corrupt" in record["failure"]


def test_equal_timestamp_tie_rule_is_plan_bound(tmp_path: Path) -> None:
    case = create_micro_case(tmp_path / "sealed-product")
    plan = _plan_for_case(
        tmp_path, case, tie_break="earlier_ledger_sequence", participants=("team-tie",)
    )
    ledger = IntakeLedger(tmp_path / "ledger")
    first = _bundle(tmp_path, (0.0, 2.0, 2.0, 0.0, 0.0), marker="first-tie")
    second = _bundle(tmp_path, (0.0, 0.0, 0.0, 0.0, 0.0), marker="second-tie")
    for bundle, delivery_id in ((first, "first-tie"), (second, "second-tie")):
        ledger.accept_local(
            identity="team-tie",
            track_id="micro-turn",
            received_at=ON_TIME,
            submitted_sha256=file_sha256(bundle),
            bundle_path=bundle,
            delivery_id=delivery_id,
        )

    run_batch(ledger.root, None, tmp_path / "results", plan_path=plan)

    record = _results(tmp_path / "results")[0]
    assert record["selected_submission"]["delivery_id"] == "first-tie"


def test_equal_timestamp_without_a_declared_tie_rule_fails_closed() -> None:
    timestamp = "2026-09-03T02:30:00+00:00"
    receipts = [
        IntakeReceipt(
            contract="civ.intake-receipt/v1alpha1",
            delivery_id=delivery_id,
            identity="team-a",
            source="local",
            received_at_original=timestamp,
            received_at_utc=timestamp,
            bundle_sha256="a" * 64,
            source_sha256=None,
            status="on_time",
            track_id="micro-turn",
        )
        for delivery_id in ("first", "second")
    ]

    with pytest.raises(CivError, match="explicit tie-break policy"):
        _select_receipt(
            receipts,
            "team-a",
            "micro-turn",
            datetime.fromisoformat("2026-09-03T12:30:00+09:00"),
        )


def test_track_selection_uses_track_id_and_plan_cutoff_not_legacy_status(
    tmp_path: Path,
) -> None:
    case = create_micro_case(tmp_path / "sealed-product")
    plan = _plan_for_case(tmp_path, case)
    plan_document = json.loads(plan.read_text())
    plan_document["cutoff"] = "2026-09-03T13:00:00+09:00"
    plan.write_text(json.dumps(plan_document, sort_keys=True), encoding="utf-8")
    ledger = IntakeLedger(tmp_path / "ledger")
    bundle = _bundle(tmp_path, (0.0, 2.0, 2.0, 0.0, 0.0), marker="cutoff")
    ledger.accept_local(
        identity="team-a",
        track_id="other-track",
        received_at=ON_TIME,
        submitted_sha256=file_sha256(bundle),
        bundle_path=bundle,
        delivery_id="wrong-track",
    )
    ledger.accept_local(
        identity="team-a",
        track_id="micro-turn",
        received_at="2026-09-03T12:45:00+09:00",
        submitted_sha256=file_sha256(bundle),
        bundle_path=bundle,
        delivery_id="eligible-by-plan",
    )
    ledger.accept_local(
        identity="team-a",
        track_id="micro-turn",
        received_at="2026-09-03T13:01:00+09:00",
        submitted_sha256=file_sha256(bundle),
        bundle_path=bundle,
        delivery_id="after-plan-cutoff",
    )

    run_batch(ledger.root, None, tmp_path / "results", plan_path=plan)

    record = _results(tmp_path / "results")[0]
    assert record["status"] == "scored"
    assert record["selected_submission"]["delivery_id"] == "eligible-by-plan"


def test_unknown_track_receipt_blocks_readiness_and_is_audited(tmp_path: Path) -> None:
    case = create_micro_case(tmp_path / "sealed-product")
    plan = _plan_for_case(tmp_path, case)
    ledger = IntakeLedger(tmp_path / "ledger")
    bundle = _bundle(tmp_path, (0.0, 2.0, 2.0, 0.0, 0.0), marker="misspelled-track")
    ledger.accept_local(
        identity="team-a",
        track_id="micro-trun",
        received_at=ON_TIME,
        submitted_sha256=file_sha256(bundle),
        bundle_path=bundle,
        delivery_id="mistyped-track-delivery",
    )

    readiness = check_readiness(ledger.root, plan_path=plan)
    summary = run_batch(ledger.root, None, tmp_path / "results", plan_path=plan)

    assert readiness["ready"] is False
    blockers = cast(list[object], readiness["blockers"])
    assert any("mistyped-track-delivery" in str(item) for item in blockers)
    dispositions = cast(list[dict[str, object]], summary["receipt_dispositions"])
    disposition = dispositions[0]
    assert disposition["delivery_id"] == "mistyped-track-delivery"
    assert disposition["track_disposition"] == "unknown_track_id"
    assert disposition["reconciliation_required"] is True


def test_registered_participant_with_no_deliveries_gets_missing_track_results(
    tmp_path: Path,
) -> None:
    case = create_micro_case(tmp_path / "sealed-product")
    plan = _plan_for_case(tmp_path, case, participants=("team-no-deliveries", "team-zero"))
    ledger = IntakeLedger(tmp_path / "empty-ledger")

    summary = run_batch(ledger.root, None, tmp_path / "results", plan_path=plan)

    records = _results(tmp_path / "results")
    assert [record["identity"] for record in records] == ["team-no-deliveries", "team-zero"]
    assert all(record["status"] == "missing-track" for record in records)
    assert summary["registered_participants"] == 2
    assert summary["receipt_dispositions"] == []


def test_run_batch_rejects_receipt_added_after_readiness(tmp_path: Path, monkeypatch: Any) -> None:
    case = create_micro_case(tmp_path / "sealed-product")
    plan = _plan_for_case(tmp_path, case)
    ledger = IntakeLedger(tmp_path / "ledger")
    first = _bundle(tmp_path, (0.0, 2.0, 2.0, 0.0, 0.0), marker="before-ready")
    later = _bundle(tmp_path, (0.0, 0.0, 0.0, 0.0, 0.0), marker="after-ready")
    ledger.accept_local(
        identity="team-a",
        track_id="micro-turn",
        received_at=ON_TIME,
        submitted_sha256=file_sha256(first),
        bundle_path=first,
        delivery_id="before-ready",
    )
    original_check = check_readiness

    def check_then_accept(*args: Any, **kwargs: Any) -> dict[str, object]:
        result = original_check(*args, **kwargs)
        ledger.accept_local(
            identity="team-a",
            track_id="micro-turn",
            received_at=ON_TIME,
            submitted_sha256=file_sha256(later),
            bundle_path=later,
            delivery_id="after-ready",
        )
        return result

    monkeypatch.setattr("civ_workshop.batch.check_readiness", check_then_accept)
    output = tmp_path / "stale-readiness-results"

    with pytest.raises(CivError, match="changed after readiness"):
        run_batch(ledger.root, None, output, plan_path=plan)

    assert not output.exists()


def test_run_batch_rechecks_bound_inputs_before_publishing_outputs(
    tmp_path: Path, monkeypatch: Any
) -> None:
    case = create_micro_case(tmp_path / "sealed-product")
    plan = _plan_for_case(tmp_path, case)
    ledger = IntakeLedger(tmp_path / "ledger")
    first = _bundle(tmp_path, (0.0, 2.0, 2.0, 0.0, 0.0), marker="during-replay")
    later = _bundle(tmp_path, (0.0, 0.0, 0.0, 0.0, 0.0), marker="during-replay-new")
    ledger.accept_local(
        identity="team-a",
        track_id="micro-turn",
        received_at=ON_TIME,
        submitted_sha256=file_sha256(first),
        bundle_path=first,
        delivery_id="during-replay-first",
    )
    original_replay = _run_replay

    def replay_then_accept(*args: Any, **kwargs: Any) -> tuple[bool, str | None, int]:
        result = original_replay(*args, **kwargs)
        ledger.accept_local(
            identity="team-a",
            track_id="micro-turn",
            received_at=ON_TIME,
            submitted_sha256=file_sha256(later),
            bundle_path=later,
            delivery_id="during-replay-later",
        )
        return result

    monkeypatch.setattr("civ_workshop.cohort_scoring._run_replay", replay_then_accept)
    output = tmp_path / "changed-inputs-results"

    with pytest.raises(CivError, match="changed during replay"):
        run_batch(ledger.root, None, output, plan_path=plan)

    assert not output.exists()


def test_evaluation_plan_rejects_unmeasured_runtime_identity(tmp_path: Path) -> None:
    case = create_micro_case(tmp_path / "sealed-product")
    plan = _plan_for_case(tmp_path, case)
    plan_document = json.loads(plan.read_text())
    plan_document["runtime"]["implementation_sha256"] = "0" * 64
    plan.write_text(json.dumps(plan_document, sort_keys=True), encoding="utf-8")

    with pytest.raises(CivError, match="implementation_sha256 does not match"):
        load_evaluation_plan(plan)


def test_cohort_readiness_fingerprint_binds_plan_ledger_bundle_product_and_truth(
    tmp_path: Path,
) -> None:
    case = create_micro_case(tmp_path / "sealed-product")
    plan = _plan_for_case(tmp_path, case)
    ledger = IntakeLedger(tmp_path / "ledger")
    bundle = _bundle(tmp_path, (0.0, 2.0, 2.0, 0.0, 0.0), marker="fingerprint")
    ledger.accept_local(
        identity="team-a",
        track_id="micro-turn",
        received_at=ON_TIME,
        submitted_sha256=file_sha256(bundle),
        bundle_path=bundle,
        delivery_id="fingerprint-delivery",
    )

    before, errors = input_fingerprint(ledger.root, plan)
    readiness = check_readiness(ledger.root, plan_path=plan)
    assert errors == []
    assert before is not None
    assert readiness["ready"] is False
    evidence = cast(dict[str, Any], readiness["evidence"])
    blockers = cast(list[str], readiness["blockers"])
    assert evidence["input_fingerprint"] == before
    assert any("approval" in blocker for blocker in blockers)

    plan_document = json.loads(plan.read_text())
    truth_path = Path(plan_document["tracks"][0]["products"][0]["truth"]["path"])
    truth_path.write_text(truth_path.read_text() + "\n", encoding="utf-8")
    after, errors = input_fingerprint(ledger.root, plan)
    assert after is not None
    assert any("truth hash does not match plan" in error for error in errors)


def test_computation_approval_goes_stale_when_receipt_snapshot_changes(tmp_path: Path) -> None:
    from civ_workshop.cohort_scoring import check_computation_approval

    case = create_micro_case(tmp_path / "sealed-product")
    plan = _plan_for_case(tmp_path, case)
    ledger = IntakeLedger(tmp_path / "ledger")
    bundle = _bundle(tmp_path, (0.0, 2.0, 2.0, 0.0, 0.0), marker="approval")
    ledger.accept_local(
        identity="team-a",
        track_id="micro-turn",
        received_at=ON_TIME,
        submitted_sha256=file_sha256(bundle),
        bundle_path=bundle,
        delivery_id="approval-first",
    )
    fingerprint, diagnostics = input_fingerprint(ledger.root, plan)
    assert fingerprint is not None and diagnostics == []
    approval = tmp_path / "approval.json"
    preflight_sha = "a" * 64
    review_status_sha = "b" * 64
    approval.write_text(
        json.dumps(
            {
                "contract": "civ.computation-approval/v1alpha1",
                "plan_sha256": file_sha256(plan),
                "input_fingerprint": fingerprint,
                "preflight_sha256": preflight_sha,
                "review_status_sha256": review_status_sha,
                "approved_by": "Synthetic reviewer",
                "approved_at": ON_TIME,
            }
        ),
        encoding="utf-8",
    )
    assert (
        check_computation_approval(
            approval,
            plan_path=plan,
            input_digest=fingerprint,
            preflight_sha256=preflight_sha,
            review_status_sha256=review_status_sha,
        )
        == []
    )

    ledger.accept_local(
        identity="team-a",
        track_id="micro-turn",
        received_at=ON_TIME,
        submitted_sha256=file_sha256(bundle),
        bundle_path=bundle,
        delivery_id="approval-second",
    )
    changed, diagnostics = input_fingerprint(ledger.root, plan)
    assert changed is not None and diagnostics == [] and changed != fingerprint
    assert "input_fingerprint does not match current scoring inputs" in str(
        check_computation_approval(
            approval,
            plan_path=plan,
            input_digest=changed,
            preflight_sha256=preflight_sha,
            review_status_sha256=review_status_sha,
        )
    )


def test_readiness_checks_hashed_runtime_and_reference_reviews(
    tmp_path: Path, monkeypatch: Any
) -> None:
    case = create_micro_case(tmp_path / "sealed-product")
    plan = _plan_for_case(tmp_path, case)
    ledger = IntakeLedger(tmp_path / "ledger")
    bundle = _bundle(tmp_path, (0.0, 2.0, 2.0, 0.0, 0.0), marker="reviewed")
    ledger.accept_local(
        identity="team-a",
        track_id="micro-turn",
        received_at=ON_TIME,
        submitted_sha256=file_sha256(bundle),
        bundle_path=bundle,
        delivery_id="reviewed-delivery",
    )
    plan_doc = json.loads(plan.read_text())
    track = plan_doc["tracks"][0]
    product = track["products"][0]
    fingerprint, errors = input_fingerprint(ledger.root, plan)
    assert fingerprint is not None and errors == []

    runtime_path = tmp_path / "runtime-rehearsal.json"
    runtime_path.write_text(
        json.dumps(
            {
                "contract": "civ.runtime-rehearsal/v1alpha1",
                "plan_sha256": file_sha256(plan),
                "input_fingerprint": fingerprint,
                "runtime_identity": plan_doc["runtime"]["identity"],
                "tool_version": plan_doc["runtime"]["tool_version"],
                "python_version": plan_doc["runtime"]["python_version"],
                "implementation_sha256": plan_doc["runtime"]["implementation_sha256"],
                "environment_sha256": plan_doc["runtime"]["environment_sha256"],
                "outcome": "passed",
            }
        ),
        encoding="utf-8",
    )
    reference_path = tmp_path / "reference-review.json"
    reference_path.write_text(
        json.dumps(
            {
                "contract": "civ.reference-review-approval/v1alpha1",
                "track_id": track["track_id"],
                "product_id": product["product_id"],
                "target": track["target"],
                "truth_sha256": product["truth"]["sha256"],
                "decision": "approved",
                "coverage": "complete",
                "reviewer": "Synthetic reference reviewer",
                "reviewed_at": ON_TIME,
            }
        ),
        encoding="utf-8",
    )
    preflight_path = tmp_path / "preflight.json"
    preflight_path.write_text(
        json.dumps(
            {
                "contract": "civ.cohort-preflight/v1alpha1",
                "plan_sha256": file_sha256(plan),
                "input_fingerprint": fingerprint,
                "ledger_designation": {
                    "ledger_sha256": file_sha256(ledger.database_path),
                    "designated_by": "Synthetic ledger owner",
                    "designated_at": ON_TIME,
                },
                "runtime_rehearsal": {
                    "path": runtime_path.name,
                    "sha256": file_sha256(runtime_path),
                },
                "reference_reviews": [
                    {
                        "track_id": track["track_id"],
                        "product_id": product["product_id"],
                        "artifact": {
                            "path": reference_path.name,
                            "sha256": file_sha256(reference_path),
                        },
                    }
                ],
                "human_component_scores": {
                    "team-a": {
                        "evidence": {
                            "points": 12.5,
                            "reviewer": "Synthetic evidence reviewer",
                            "reviewed_at": ON_TIME,
                            "notation": "Evidence is bound to the selected submission.",
                        },
                        "reproducibility": {
                            "points": 13.0,
                            "reviewer": "Synthetic reproducibility reviewer",
                            "reviewed_at": ON_TIME,
                            "notation": "Replay instructions are complete and reproducible.",
                        },
                    }
                },
                "official_blockers": [],
            }
        ),
        encoding="utf-8",
    )
    review_path = tmp_path / "review-status.json"
    review_path.write_text(
        json.dumps(
            {
                "contract": "civ.cohort-review-status/v1alpha1",
                "plan_sha256": file_sha256(plan),
                "input_fingerprint": fingerprint,
                "preflight_sha256": file_sha256(preflight_path),
                "decision": "approved",
                "reviewer": "Synthetic organizer",
                "reviewed_at": ON_TIME,
                "confirmations": {
                    "cutoff": True,
                    "runtime": True,
                    "ledger": True,
                    "references": True,
                    "scoring_policy": True,
                },
            }
        ),
        encoding="utf-8",
    )
    approval_path = tmp_path / "approval.json"
    approval_path.write_text(
        json.dumps(
            {
                "contract": "civ.computation-approval/v1alpha1",
                "plan_sha256": file_sha256(plan),
                "input_fingerprint": fingerprint,
                "preflight_sha256": file_sha256(preflight_path),
                "review_status_sha256": file_sha256(review_path),
                "approved_by": "Synthetic computation approver",
                "approved_at": ON_TIME,
            }
        ),
        encoding="utf-8",
    )

    report = check_readiness(
        ledger.root,
        plan_path=plan,
        preflight_path=preflight_path,
        review_status_path=review_path,
        approval_path=approval_path,
    )

    assert report["ready"] is False
    blockers = str(report["blockers"])
    assert "approval:" not in blockers
    assert "preflight:" not in blockers
    assert "references:" not in blockers
    assert "review status:" not in blockers
    assert "Evidence (15 machine points)" in blockers
    assert "Reproducibility (15 machine points)" in blockers

    summary = run_batch(
        ledger.root,
        None,
        tmp_path / "approved-results",
        plan_path=plan,
        preflight_path=preflight_path,
        review_status_path=review_path,
        approval_path=approval_path,
    )
    technical = cast(dict[str, Any], summary["technical_scores"])
    participant = cast(dict[str, Any], technical["participants"])["team-a"]
    assert summary["official_score"] is False
    assert participant["status"] == "pending_machine_components"
    assert participant["evidence_points"] is None
    assert participant["reproducibility_points"] is None
    assert participant["pending_components"] == ["evidence", "reproducibility"]
    assert participant["technical_total_points"] is None
    detection = cast(dict[str, Any], summary["computed_detection"])["participants"]["team-a"]
    assert participant["detection_points"] == detection["total_detection_points"]

    # Ignore the unresolved machine calculations only in this synthetic test so
    # approval revocation is tested independently from the scoring-policy blocker.
    monkeypatch.setattr("civ_workshop.cohort_scoring.policy_blockers", lambda _plan: [])
    approved_readiness = check_readiness(
        ledger.root,
        plan_path=plan,
        preflight_path=preflight_path,
        review_status_path=review_path,
        approval_path=approval_path,
    )
    assert approved_readiness["ready"] is True
    output_root = tmp_path / "approved-results"
    committed_before = {
        path.relative_to(output_root).as_posix(): file_sha256(path)
        for path in output_root.rglob("*")
        if path.is_file()
    }
    original_approval = approval_path.read_text(encoding="utf-8")

    def replay_then_revoke_approval(
        *args: Any, **kwargs: Any
    ) -> tuple[bool, str | None, int]:
        result = _run_replay(*args, **kwargs)
        approval_path.write_text(
            json.dumps({"contract": "REVOKED-SYNTHETIC-APPROVAL"}), encoding="utf-8"
        )
        return result

    monkeypatch.setattr(
        "civ_workshop.cohort_scoring._run_replay", replay_then_revoke_approval
    )
    from civ_workshop.cohort_scoring import run_cohort_batch

    try:
        with pytest.raises(CivError, match="readiness or approval chain changed"):
            run_cohort_batch(
                ledger.root,
                plan,
                output_root,
                official=True,
                readiness=approved_readiness,
                preflight_path=preflight_path,
                review_status_path=review_path,
                approval_path=approval_path,
            )
        committed_after = {
            path.relative_to(output_root).as_posix(): file_sha256(path)
            for path in output_root.rglob("*")
            if path.is_file()
        }
        assert committed_after == committed_before
    finally:
        approval_path.write_text(original_approval, encoding="utf-8")


def test_legacy_human_scores_do_not_complete_machine_components(tmp_path: Path) -> None:
    case = create_micro_case(tmp_path / "sealed-product")
    plan = _plan_for_case(tmp_path, case)
    ledger = tmp_path / "ledger"
    fingerprint, _diagnostics = input_fingerprint(ledger, plan)
    preflight_path = tmp_path / "preflight-without-human-scores.json"
    preflight_path.write_text(
        json.dumps(
            {
                "contract": "civ.cohort-preflight/v1alpha1",
                "plan_sha256": file_sha256(plan),
                "input_fingerprint": fingerprint,
                "human_component_scores": None,
            }
        ),
        encoding="utf-8",
    )
    report = check_readiness(
        ledger,
        plan_path=plan,
        preflight_path=preflight_path,
    )

    assert report["ready"] is False
    blockers = str(report["blockers"])
    assert "human component scores" not in blockers
    assert "Evidence (15 machine points)" in blockers
    assert "Reproducibility (15 machine points)" in blockers


def test_official_cohort_scoring_writes_nothing_when_readiness_is_blocked(
    tmp_path: Path,
) -> None:
    case = create_micro_case(tmp_path / "sealed-product")
    plan = _plan_for_case(tmp_path, case)
    ledger = IntakeLedger(tmp_path / "ledger")
    bundle = _bundle(tmp_path, (0.0, 2.0, 2.0, 0.0, 0.0), marker="official-blocked")
    ledger.accept_local(
        identity="team-a",
        track_id="micro-turn",
        received_at=ON_TIME,
        submitted_sha256=file_sha256(bundle),
        bundle_path=bundle,
        delivery_id="official-blocked-delivery",
    )
    output = tmp_path / "official-results"

    with pytest.raises(CivError, match="official scoring blocked"):
        run_batch(ledger.root, None, output, official=True, plan_path=plan)

    assert not output.exists()
