from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from civ_workshop.artifacts import file_sha256
from civ_workshop.batch import run_batch
from civ_workshop.errors import CivError
from civ_workshop.intake import IntakeLedger
from civ_workshop.organizer.scoring_readiness import check_readiness
from civ_workshop.reporting import build_report_bundle
from tests.helpers import create_micro_case, prepare_scored_submission, run_civ


def draft(tmp_path: Path) -> tuple[Path, dict[str, Any]]:
    tracks = {}
    for dataset, values in (("kashiwa", [0.0, 2.0, 0.0]), ("reims", [0.0, 3.0, 0.0])):
        case = create_micro_case(tmp_path / dataset, values=values)
        pack = json.loads(case.labels.read_text())
        pack["dataset"] = dataset
        case.labels.write_text(json.dumps(pack), encoding="utf-8")
        tracks[dataset] = {
            "event_rule": "synthetic target",
            "mode": "detection",
            "reference_status": "reviewed",
            "products": [{
                "recording": {"path": str(case.bag), "sha256": file_sha256(case.bag)},
                "labels": {"path": str(case.labels), "sha256": file_sha256(case.labels)},
            }],
        }
    plan = {
        "contract": "civ.evaluation-plan/v1alpha1", "session_id": "fixture",
        "cutoff": "2026-09-03T12:30:00+09:00", "tracks": tracks,
    }
    path = tmp_path / "plan.json"
    path.write_text(json.dumps(plan), encoding="utf-8")
    return path, plan


def test_readiness_requires_authority_and_does_not_create_a_ledger(tmp_path: Path) -> None:
    ledger = tmp_path / "missing-ledger"
    result = check_readiness(ledger)
    assert result["official_score"] is False
    assert result["ready"] is False
    text = str(result["blockers"])
    for gate in ("approval", "cutoff", "runtime", "ledger", "plan", "preflight", "review status"):
        assert gate in text
    assert not ledger.exists()


@pytest.mark.parametrize("newline", ["\n", "\r\n"])
def test_review_prose_and_empty_preflight_cannot_approve_a_plan(
    tmp_path: Path, newline: str,
) -> None:
    path, plan = draft(tmp_path)
    plan["approved"] = True  # Unknown fields cannot confer authority.
    path.write_text(json.dumps(plan, indent=2), encoding="utf-8", newline=newline)
    preflight = tmp_path / "preflight.json"
    preflight.write_text(json.dumps({
        "plan_sha256": file_sha256(path), "official_blockers": [],
    }))
    status = tmp_path / "REVIEW-STATUS.md"
    status.write_text("All reviews approved.\n", newline=newline)
    result = check_readiness(
        tmp_path / "ledger", plan_path=path, preflight_path=preflight, review_status_path=status,
    )
    assert result["ready"] is False
    assert "human reconciliation" in str(result["blockers"])
    assert "complete source-bound label coverage" in str(result["blockers"])
    assert "named organizer approval" in str(result["blockers"])


@pytest.mark.parametrize("problem", ["hash", "source", "dataset", "review", "products"])
def test_readiness_reports_reference_blockers(tmp_path: Path, problem: str) -> None:
    path, plan = draft(tmp_path)
    track = plan["tracks"]["reims"]
    product = track["products"][0]
    expected = ""
    if problem == "hash":
        product["labels"]["sha256"] = "0" * 64
        expected = "label pack hash does not match plan"
    elif problem == "source":
        product["recording"]["sha256"] = "0" * 64
        expected = "source hash or dataset does not match plan"
    elif problem == "dataset":
        pack_path = Path(product["labels"]["path"])
        pack = json.loads(pack_path.read_text())
        pack["dataset"] = "kashiwa"
        pack_path.write_text(json.dumps(pack))
        product["labels"]["sha256"] = file_sha256(pack_path)
        expected = "source hash or dataset does not match plan"
    elif problem == "review":
        track["reference_status"] = "review-required"
        expected = "reference_status is not reviewed"
    else:
        track["products"] = []
        expected = "no products selected"
    path.write_text(json.dumps(plan))
    result = check_readiness(tmp_path / "ledger", plan_path=path)
    assert expected in str(result["blockers"])
    assert result["official_score"] is False


def test_preflight_hash_and_recorded_blockers_are_not_overridden(tmp_path: Path) -> None:
    path, _ = draft(tmp_path)
    preflight = tmp_path / "preflight.json"
    preflight.write_text(json.dumps({
        "plan_sha256": "0" * 64, "official_blockers": ["Reims review pending"],
    }))
    result = check_readiness(tmp_path / "ledger", plan_path=path, preflight_path=preflight)
    assert "plan_sha256 does not match" in str(result["blockers"])
    assert "Reims review pending" in str(result["blockers"])


def test_readiness_reports_intake_without_exact_selected_source(tmp_path: Path) -> None:
    path, _ = draft(tmp_path)
    case = create_micro_case(tmp_path / "other-source", values=[0.0, 5.0, 0.0])
    working = tmp_path / "submission"
    prepare_scored_submission(case, working)
    build_report_bundle(working)
    bundle = working / "submission.zip"
    ledger = IntakeLedger(tmp_path / "ledger")
    ledger.accept_local(
        identity="fixture", received_at="2026-09-03T12:00:00+09:00",
        submitted_sha256=file_sha256(bundle), bundle_path=bundle, delivery_id="unmatched",
    )
    result = check_readiness(ledger.root, plan_path=path)
    assert "delivery unmatched has no selected exact-source reference" in str(result["blockers"])


def test_official_batch_fails_before_creating_any_output(tmp_path: Path) -> None:
    with pytest.raises(CivError, match="official scoring blocked"):
        run_batch(tmp_path / "ledger", tmp_path / "labels", tmp_path / "out", official=True)
    assert list(tmp_path.iterdir()) == []


def test_readiness_cli_returns_structured_failure_without_writes(tmp_path: Path) -> None:
    result = run_civ(tmp_path, ["score-readiness", "--ledger", str(tmp_path / "ledger")])
    assert result.returncode == 2
    assert json.loads(result.stdout)["official_score"] is False
    assert not (tmp_path / "ledger").exists()


def test_read_only_receipts_preserve_database_bytes(tmp_path: Path) -> None:
    ledger = IntakeLedger(tmp_path / "ledger")
    assert ledger.receipts() == []
    before = ledger.database_path.read_bytes()
    files = set(ledger.root.iterdir())
    assert ledger.receipts(read_only=True) == []
    assert ledger.database_path.read_bytes() == before
    assert set(ledger.root.iterdir()) == files


def test_read_only_receipts_refuse_wal_without_modifying_it(tmp_path: Path) -> None:
    ledger = IntakeLedger(tmp_path / "ledger")
    ledger.receipts()
    wal = ledger.database_path.with_name("intake.sqlite3-wal")
    wal.write_bytes(b"fixture WAL sentinel")
    before = {path: path.read_bytes() for path in ledger.root.iterdir()}
    with pytest.raises(CivError, match="closed ledger snapshot"):
        ledger.receipts(read_only=True)
    assert {path: path.read_bytes() for path in ledger.root.iterdir()} == before
