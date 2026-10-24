from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from civ_workshop.artifacts import file_sha256
from civ_workshop.batch import run_batch
from civ_workshop.cohort_scoring import load_evaluation_plan
from civ_workshop.errors import CivError
from civ_workshop.intake import IntakeLedger
from civ_workshop.session import prepare_session
from tests.helpers import create_micro_case, run_civ
from tests.test_cohort_scoring import _bundle, _plan_for_case


def test_prepare_session_resolves_overrides_and_preserves_relocated_bindings(
    tmp_path: Path,
    monkeypatch: Any,
) -> None:
    case = create_micro_case(tmp_path / "source")
    profile = _plan_for_case(tmp_path, case)
    original = json.loads(profile.read_text())
    original["tracks"][0]["products"][0]["recording"]["path"] = " source/micro.mcap "
    original["tracks"][0]["products"][0]["manifest"]["path"] = " source/manifest.json "
    original["tracks"][0]["products"][0]["truth"]["path"] = " source/truth.json "
    profile.write_text(json.dumps(original))
    monkeypatch.setenv("CIV_SESSION_CUTOFF", "2030-01-02T12:00:00+09:00")
    monkeypatch.setenv("CIV_SESSION_ID", "environment-session")
    output = tmp_path / "new-session" / "plan.json"
    receipt = prepare_session(
        profile, output, session_id="explicit-session", participants=["new-team"]
    )
    plan = load_evaluation_plan(output)
    assert plan["session_id"] == "explicit-session"
    assert plan["cutoff"] == "2030-01-02T12:00:00+09:00"
    assert plan["participants"] == ["new-team"]
    assert plan["tracks"][0]["products"][0]["recording"]["path"] == str(
        (tmp_path / "source/micro.mcap").resolve()
    )
    for kind, name in (("manifest", "manifest.json"), ("truth", "truth.json")):
        assert plan["tracks"][0]["products"][0][kind]["path"] == str(
            (tmp_path / "source" / name).resolve()
        )
    assert receipt["plan_sha256"] == file_sha256(output)
    before = output.read_bytes()
    with pytest.raises(CivError, match="cannot prepare session"):
        prepare_session(profile, output)
    assert output.read_bytes() == before
    assert json.loads(profile.read_text()) == original
    invalid = tmp_path / "invalid.json"
    with pytest.raises(CivError, match="timezone"):
        prepare_session(profile, invalid, cutoff="2030-01-02T12:00:00")
    assert not invalid.exists()


def test_saved_future_plan_controls_intake_and_scoring_despite_environment_changes(
    tmp_path: Path,
    monkeypatch: Any,
) -> None:
    case = create_micro_case(tmp_path / "source")
    profile = _plan_for_case(tmp_path, case)
    plan = tmp_path / "future-plan.json"
    prepare_session(profile, plan, cutoff="2030-01-02T12:00:00+09:00")
    bundle = _bundle(tmp_path, (0.0, 3.0, 3.0, 0.0, 0.0), marker="future")
    ledger = tmp_path / "ledger"
    # Historical rows retain their original classification and provenance.
    legacy = IntakeLedger(ledger).accept_local(
        identity="team-a",
        track_id="micro-turn",
        received_at="2026-09-03T12:00:00+09:00",
        submitted_sha256=file_sha256(bundle),
        bundle_path=bundle,
        delivery_id="historical",
    )
    monkeypatch.setenv("CIV_SESSION_CUTOFF", "invalid-runtime-override")
    for delivery_id, received_at, expected in (
        ("exact", "2030-01-02T12:00:00+09:00", "on_time"),
        ("late", "2030-01-02T12:00:00.000001+09:00", "late"),
    ):
        result = run_civ(
            tmp_path,
            [
                "intake-local",
                str(bundle),
                "--ledger",
                str(ledger),
                "--plan",
                str(plan),
                "--identity",
                "team-a",
                "--track-id",
                "micro-turn",
                "--delivery-id",
                delivery_id,
                "--received-at",
                received_at,
                "--sha256",
                file_sha256(bundle),
            ],
        )
        assert result.returncode == 0, result.stderr
        receipt = json.loads(result.stdout)
        assert receipt["status"] == expected
        assert receipt["cutoff"] == "2030-01-02T12:00:00+09:00"
        assert receipt["evaluation_plan_sha256"] == file_sha256(plan)
    assert IntakeLedger(ledger).receipts(read_only=True)[0] == legacy
    summary = run_batch(ledger, None, tmp_path / "results", plan_path=plan)
    assert summary["counts"] == {"scored": 1}
    records = [
        json.loads(line) for line in (tmp_path / "results/results.jsonl").read_text().splitlines()
    ]
    assert records[0]["selected_submission"]["delivery_id"] == "exact"


def test_invalid_intake_plan_does_not_create_a_ledger(tmp_path: Path) -> None:
    result = run_civ(
        tmp_path,
        [
            "intake-local",
            "missing.zip",
            "--ledger",
            str(tmp_path / "ledger"),
            "--plan",
            str(tmp_path / "missing-plan.json"),
            "--identity",
            "team",
            "--delivery-id",
            "delivery",
            "--received-at",
            "2030-01-01T00:00:00Z",
            "--sha256",
            "0" * 64,
        ],
    )
    assert result.returncode == 2
    assert "evaluation plan does not exist" in result.stderr
    assert not (tmp_path / "ledger").exists()


def test_form_and_tally_intake_use_the_saved_plan(
    tmp_path: Path,
    monkeypatch: Any,
    capsys: Any,
) -> None:
    import civ_workshop.cli as cli
    import civ_workshop.tally as tally
    from tests.test_tally import _row, _write_csv

    case = create_micro_case(tmp_path / "source")
    profile = _plan_for_case(tmp_path, case)
    plan = tmp_path / "future.json"
    prepared = run_civ(
        tmp_path,
        [
            "prepare-session",
            "--plan",
            str(profile),
            "--output",
            str(plan),
            "--cutoff",
            "2030-01-02T12:00:00+09:00",
            "--session-id",
            "future-session",
        ],
    )
    assert prepared.returncode == 0, prepared.stderr
    bundle = _bundle(tmp_path, (0.0, 3.0, 3.0, 0.0, 0.0), marker="adapters")
    response = bundle.parent / "response.json"
    response.write_text(
        json.dumps(
            {
                "bundle": bundle.name,
                "identity": "team-a",
                "track_id": "micro-turn",
                "received_at": "2030-01-02T12:00:00+09:00",
                "delivery_id": "form-future",
                "sha256": file_sha256(bundle),
            }
        )
    )
    cli.main(
        ["intake-form", str(response), "--ledger", str(tmp_path / "form"), "--plan", str(plan)]
    )
    assert json.loads(capsys.readouterr().out)["status"] == "on_time"
    csv = tmp_path / "deliveries.csv"
    _write_csv(
        csv,
        [
            _row(
                "tally-future",
                "team-a",
                "2030-01-02 03:00:00",
                file_sha256(bundle),
                "https://storage.tally.so/uploads/fixture",
            )
        ],
    )
    monkeypatch.setattr(
        tally,
        "_download_tally_upload",
        lambda _url, destination: destination.write_bytes(bundle.read_bytes()),
    )
    cli.main(["intake-tally", str(csv), "--ledger", str(tmp_path / "tally"), "--plan", str(plan)])
    receipt = json.loads(capsys.readouterr().out)["outcomes"][0]["receipt"]
    assert receipt["status"] == "on_time"
    assert receipt["evaluation_plan_sha256"] == file_sha256(plan)
