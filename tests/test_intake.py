from __future__ import annotations

import json
import sqlite3
import zipfile
from concurrent.futures import ThreadPoolExecutor
from hashlib import sha256
from pathlib import Path

import pytest

import civ_workshop.intake as intake_module
from civ_workshop.errors import CivError
from civ_workshop.intake import (
    MAX_FORM_RESPONSE_BYTES,
    IntakeLedger,
    IntakeReceipt,
    import_form_response,
)
from civ_workshop.reporting import MAX_SUBMISSION_ENTRY_BYTES, build_report_bundle
from tests.helpers import MicroCase, create_micro_case, prepare_scored_submission, run_civ


@pytest.fixture
def micro_case(tmp_path: Path) -> MicroCase:
    return create_micro_case(tmp_path)


def _bundle(micro_case: MicroCase, root: Path, suffix: str = "") -> Path:
    working = root / f"working-{suffix or 'first'}"
    prepare_scored_submission(micro_case, working)
    if suffix:
        with (working / "report.md").open("a", encoding="utf-8") as report:
            report.write(f"\nIteration: {suffix}\n")
    build_report_bundle(working)
    return working / "submission.zip"


def test_existing_intake_ledger_adds_nullable_source_provenance_column(
    tmp_path: Path,
) -> None:
    root = tmp_path / "legacy-intake"
    root.mkdir()
    database = root / "intake.sqlite3"
    with sqlite3.connect(database) as connection:
        connection.execute(
            """
            CREATE TABLE receipts (
                sequence INTEGER PRIMARY KEY AUTOINCREMENT,
                delivery_id TEXT NOT NULL UNIQUE,
                identity TEXT NOT NULL,
                source TEXT NOT NULL,
                received_at_original TEXT NOT NULL,
                received_at_utc TEXT NOT NULL,
                bundle_sha256 TEXT NOT NULL,
                status TEXT NOT NULL
            )
            """
        )
        connection.execute(
            """
            INSERT INTO receipts (
                delivery_id, identity, source, received_at_original, received_at_utc,
                bundle_sha256, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "legacy-delivery",
                "legacy-team",
                "local",
                "2026-09-03T12:00:00+09:00",
                "2026-09-03T03:00:00+00:00",
                "0" * 64,
                "on_time",
            ),
        )

    receipts = IntakeLedger(root).receipts()

    assert len(receipts) == 1
    assert receipts[0].source_sha256 is None


def test_online_and_usb_adapters_preserve_identical_bundle_and_scorer_input(
    micro_case: MicroCase, tmp_path: Path
) -> None:
    bundle = _bundle(micro_case, tmp_path)
    bundle_hash = sha256(bundle.read_bytes()).hexdigest()
    ledger = IntakeLedger(tmp_path / "intake")

    online = ledger.accept_online(
        identity="team-online",
        received_at="2026-09-03T03:29:00Z",
        submitted_sha256=bundle_hash,
        bundle_path=bundle,
        delivery_id="form-response-001",
    )
    local = ledger.accept_local(
        identity="team-usb",
        received_at="2026-09-03T12:29:30+09:00",
        submitted_sha256=bundle_hash,
        bundle_path=bundle,
        delivery_id="usb-receipt-001",
    )

    assert online.bundle_sha256 == local.bundle_sha256 == bundle_hash
    assert online.received_at_original == "2026-09-03T03:29:00Z"
    assert online.received_at_utc == "2026-09-03T03:29:00+00:00"
    assert local.received_at_utc == "2026-09-03T03:29:30+00:00"
    assert ledger.scorer_input("team-online").read_bytes() == bundle.read_bytes()
    assert ledger.scorer_input("team-usb").read_bytes() == bundle.read_bytes()


def test_last_valid_on_time_submission_wins_and_late_receipts_are_quarantined(
    micro_case: MicroCase, tmp_path: Path
) -> None:
    first_bundle = _bundle(micro_case, tmp_path, "first")
    final_bundle = _bundle(micro_case, tmp_path, "final")
    ledger = IntakeLedger(tmp_path / "intake")

    first = ledger.accept_local(
        identity="team-1",
        received_at="2026-09-03T12:00:00+09:00",
        submitted_sha256=sha256(first_bundle.read_bytes()).hexdigest(),
        bundle_path=first_bundle,
        delivery_id="usb-first",
    )
    exact_cutoff = ledger.accept_online(
        identity="team-1",
        received_at="2026-09-03T12:30:00+09:00",
        submitted_sha256=sha256(final_bundle.read_bytes()).hexdigest(),
        bundle_path=final_bundle,
        delivery_id="form-final",
    )
    late = ledger.accept_local(
        identity="team-1",
        received_at="2026-09-03T12:30:00.000001+09:00",
        submitted_sha256=sha256(first_bundle.read_bytes()).hexdigest(),
        bundle_path=first_bundle,
        delivery_id="usb-late",
    )

    assert first.status == "on_time"
    assert exact_cutoff.status == "on_time"
    assert exact_cutoff.received_at_utc == "2026-09-03T03:30:00+00:00"
    assert late.status == "late"
    assert ledger.authoritative("team-1") == exact_cutoff
    assert ledger.quarantined() == [late]
    assert ledger.scorer_input("team-1").read_bytes() == final_bundle.read_bytes()


def test_authority_is_scoped_per_dataset_rather_than_per_identity(
    micro_case: MicroCase, tmp_path: Path
) -> None:
    second_case = create_micro_case(tmp_path / "second-dataset", (0.0, 3.0, 3.0, 0.0, 0.0))
    first_bundle = _bundle(micro_case, tmp_path, "first-dataset")
    second_bundle = _bundle(second_case, tmp_path, "second-dataset")
    ledger = IntakeLedger(tmp_path / "intake")

    first = ledger.accept_online(
        identity="team-1",
        received_at="2026-09-03T12:00:00+09:00",
        submitted_sha256=sha256(first_bundle.read_bytes()).hexdigest(),
        bundle_path=first_bundle,
        delivery_id="form-first-dataset",
    )
    second = ledger.accept_local(
        identity="team-1",
        received_at="2026-09-03T12:20:00+09:00",
        submitted_sha256=sha256(second_bundle.read_bytes()).hexdigest(),
        bundle_path=second_bundle,
        delivery_id="usb-second-dataset",
    )

    assert first.source_sha256 != second.source_sha256
    assert [first.status, second.status] == ["on_time", "on_time"]
    # The later bundle must not silently replace a different dataset's entry.
    for lookup in (ledger.authoritative, ledger.scorer_input):
        with pytest.raises(CivError, match="authority is dataset-specific"):
            lookup("team-1")
    assert ledger.receipts() == [first, second]
    assert ledger.bundle_for(first).read_bytes() == first_bundle.read_bytes()
    assert ledger.bundle_for(second).read_bytes() == second_bundle.read_bytes()


def test_invalid_and_duplicate_deliveries_do_not_replace_an_earlier_valid_submission(
    micro_case: MicroCase, tmp_path: Path
) -> None:
    bundle = _bundle(micro_case, tmp_path)
    bundle_hash = sha256(bundle.read_bytes()).hexdigest()
    ledger = IntakeLedger(tmp_path / "intake")
    accepted = ledger.accept_online(
        identity="team-1",
        received_at="2026-09-03T12:00:00+09:00",
        submitted_sha256=bundle_hash,
        bundle_path=bundle,
        delivery_id="form-valid",
    )

    with pytest.raises(CivError, match="participant identity is required"):
        ledger.accept_local(
            identity="  ",
            received_at="2026-09-03T12:10:00+09:00",
            submitted_sha256=bundle_hash,
            bundle_path=bundle,
            delivery_id="usb-no-identity",
        )
    with pytest.raises(CivError, match="pasted sha256 does not match"):
        ledger.accept_online(
            identity="team-1",
            received_at="2026-09-03T12:10:00+09:00",
            submitted_sha256="0" * 64,
            bundle_path=bundle,
            delivery_id="form-bad-hash",
        )
    with pytest.raises(CivError, match="duplicate delivery id"):
        ledger.accept_online(
            identity="team-1",
            received_at="2026-09-03T12:10:00+09:00",
            submitted_sha256=bundle_hash,
            bundle_path=bundle,
            delivery_id="form-valid",
        )
    with pytest.raises(CivError, match="pasted sha256 does not match"):
        ledger.accept_local(
            identity="team-1",
            received_at="2026-09-03T12:15:00+09:00",
            submitted_sha256="0" * 64,
            bundle_path=bundle,
            delivery_id="usb-bad-hash",
        )

    malformed = tmp_path / "malformed.zip"
    with zipfile.ZipFile(bundle) as source, zipfile.ZipFile(malformed, "w") as target:
        for name in source.namelist():
            target.writestr(name, source.read(name))
        target.writestr("evidence/clip.mcap", b"raw evidence")
    with pytest.raises(CivError, match="unexpected submission artifacts"):
        ledger.accept_local(
            identity="team-2",
            received_at="2026-09-03T12:20:00+09:00",
            submitted_sha256=sha256(malformed.read_bytes()).hexdigest(),
            bundle_path=malformed,
            delivery_id="usb-malformed",
        )

    assert ledger.receipts() == [accepted]
    assert ledger.authoritative("team-1") == accepted


def test_cli_imports_form_export_and_usb_bundle_through_the_same_contract(
    micro_case: MicroCase, tmp_path: Path
) -> None:
    bundle = _bundle(micro_case, tmp_path)
    bundle_hash = sha256(bundle.read_bytes()).hexdigest()
    form_response = tmp_path / "form-response.json"
    form_response.write_text(
        json.dumps(
            {
                "bundle": bundle.name,
                "delivery_id": "google-response-001",
                "identity": "team-form",
                "received_at": "2026-09-03T12:20:00+09:00",
                "sha256": bundle_hash,
            }
        ),
        encoding="utf-8",
    )
    bundle.replace(tmp_path / bundle.name)
    ledger = tmp_path / "ledger"

    online = run_civ(
        tmp_path,
        ["intake-form", str(form_response), "--ledger", str(ledger)],
    )
    local = run_civ(
        tmp_path,
        [
            "intake-local",
            str(tmp_path / bundle.name),
            "--ledger",
            str(ledger),
            "--identity",
            "team-usb",
            "--received-at",
            "2026-09-03T12:21:00+09:00",
            "--sha256",
            bundle_hash,
            "--delivery-id",
            "usb-response-001",
        ],
    )

    assert online.returncode == 0, online.stderr
    assert local.returncode == 0, local.stderr
    online_receipt = json.loads(online.stdout)
    local_receipt = json.loads(local.stdout)
    assert online_receipt["bundle_sha256"] == local_receipt["bundle_sha256"] == bundle_hash
    assert online_receipt["source"] == "online"
    assert local_receipt["source"] == "local"
    assert online_receipt["status"] == local_receipt["status"] == "on_time"


def test_intake_rejects_compressed_and_oversized_archives_before_extraction(
    micro_case: MicroCase, tmp_path: Path
) -> None:
    bundle = _bundle(micro_case, tmp_path)
    compressed = tmp_path / "compressed.zip"
    with zipfile.ZipFile(bundle) as source, zipfile.ZipFile(
        compressed, "w", compression=zipfile.ZIP_DEFLATED
    ) as target:
        for name in source.namelist():
            target.writestr(name, source.read(name))
    oversized = tmp_path / "oversized.zip"
    with zipfile.ZipFile(oversized, "w", compression=zipfile.ZIP_STORED) as target:
        target.writestr("figure.svg", b"x" * (MAX_SUBMISSION_ENTRY_BYTES + 1))

    ledger = IntakeLedger(tmp_path / "intake")
    with pytest.raises(CivError, match="stored ZIP format"):
        ledger.accept_local(
            identity="team-compressed",
            received_at="2026-09-03T12:00:00+09:00",
            submitted_sha256=sha256(compressed.read_bytes()).hexdigest(),
            bundle_path=compressed,
            delivery_id="compressed-delivery",
        )
    with pytest.raises(CivError, match="artifact exceeds"):
        ledger.accept_local(
            identity="team-oversized",
            received_at="2026-09-03T12:00:00+09:00",
            submitted_sha256=sha256(oversized.read_bytes()).hexdigest(),
            bundle_path=oversized,
            delivery_id="oversized-delivery",
        )
    assert ledger.receipts() == []


def test_intake_rejects_a_repacked_copy_of_a_civ_report_bundle(
    micro_case: MicroCase, tmp_path: Path
) -> None:
    bundle = _bundle(micro_case, tmp_path)
    repacked = tmp_path / "repacked.zip"
    with zipfile.ZipFile(bundle) as source, zipfile.ZipFile(
        repacked, "w", compression=zipfile.ZIP_STORED
    ) as target:
        for name in source.namelist():
            target.writestr(name, source.read(name))

    ledger = IntakeLedger(tmp_path / "intake")
    with pytest.raises(CivError, match="unchanged ZIP emitted by civ report"):
        ledger.accept_local(
            identity="team-repacked",
            received_at="2026-09-03T12:00:00+09:00",
            submitted_sha256=sha256(repacked.read_bytes()).hexdigest(),
            bundle_path=repacked,
            delivery_id="repacked-delivery",
        )
    assert ledger.receipts() == []


def test_intake_validates_and_stores_one_owned_snapshot_when_source_changes(
    micro_case: MicroCase, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    bundle = _bundle(micro_case, tmp_path)
    original_bytes = bundle.read_bytes()
    bundle_hash = sha256(original_bytes).hexdigest()
    validate_snapshot = intake_module.validate_submission_bundle

    def replace_source_then_validate(snapshot: Path) -> str:
        assert snapshot.resolve() != bundle.resolve()
        bundle.write_bytes(b"caller replaced the upload path")
        return validate_snapshot(snapshot)

    monkeypatch.setattr(
        intake_module, "validate_submission_bundle", replace_source_then_validate
    )
    ledger = IntakeLedger(tmp_path / "intake")
    receipt = ledger.accept_online(
        identity="team-snapshot",
        received_at="2026-09-03T12:00:00+09:00",
        submitted_sha256=bundle_hash,
        bundle_path=bundle,
        delivery_id="snapshot-delivery",
    )

    assert receipt.bundle_sha256 == bundle_hash
    assert ledger.scorer_input("team-snapshot").read_bytes() == original_bytes


def test_snapshot_cleanup_failure_cannot_commit_a_receipt_reported_as_rejected(
    micro_case: MicroCase, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    bundle = _bundle(micro_case, tmp_path)
    bundle_hash = sha256(bundle.read_bytes()).hexdigest()
    ledger = IntakeLedger(tmp_path / "intake")
    unlink = Path.unlink

    def reject_snapshot_cleanup(path: Path, missing_ok: bool = False) -> None:
        if path.name.startswith(".incoming-"):
            raise PermissionError("simulated snapshot cleanup failure")
        unlink(path, missing_ok=missing_ok)

    monkeypatch.setattr(Path, "unlink", reject_snapshot_cleanup)
    with pytest.raises(CivError, match="cannot clean up submission bundle snapshot"):
        ledger.accept_local(
            identity="team-cleanup",
            received_at="2026-09-03T12:00:00+09:00",
            submitted_sha256=bundle_hash,
            bundle_path=bundle,
            delivery_id="cleanup-delivery",
        )

    assert ledger.receipts() == []


def test_report_and_form_envelope_enforce_the_published_intake_limits(
    micro_case: MicroCase, tmp_path: Path
) -> None:
    working = tmp_path / "working-too-large"
    prepare_scored_submission(micro_case, working)
    (working / "figure.svg").write_bytes(b"x" * (MAX_SUBMISSION_ENTRY_BYTES + 1))
    with pytest.raises(CivError, match="submission artifact exceeds"):
        build_report_bundle(working)
    assert not (working / "submission.zip").exists()

    escaping = tmp_path / "escaping-response.json"
    escaping.write_text(
        json.dumps(
            {
                "bundle": "../submission.zip",
                "delivery_id": "escape",
                "identity": "team",
                "received_at": "2026-09-03T12:00:00+09:00",
                "sha256": "0" * 64,
            }
        ),
        encoding="utf-8",
    )
    with pytest.raises(CivError, match="one sibling .zip file"):
        import_form_response(escaping, tmp_path / "intake")

    oversized_response = tmp_path / "oversized-response.json"
    oversized_response.write_text("x" * (MAX_FORM_RESPONSE_BYTES + 1), encoding="utf-8")
    with pytest.raises(CivError, match="form response exceeds"):
        import_form_response(oversized_response, tmp_path / "intake")


def test_concurrent_duplicate_delivery_is_atomic_and_corrupt_bundle_is_repaired(
    micro_case: MicroCase, tmp_path: Path
) -> None:
    bundle = _bundle(micro_case, tmp_path)
    bundle_hash = sha256(bundle.read_bytes()).hexdigest()
    ledger = IntakeLedger(tmp_path / "intake")
    ledger.bundles_path.mkdir(parents=True)
    (ledger.bundles_path / f"{bundle_hash}.zip").write_bytes(b"interrupted copy")
    assert ledger.receipts() == []

    def accept() -> IntakeReceipt | str:
        try:
            return ledger.accept_local(
                identity="team-atomic",
                received_at="2026-09-03T12:00:00+09:00",
                submitted_sha256=bundle_hash,
                bundle_path=bundle,
                delivery_id="same-transport-delivery",
            )
        except CivError as error:
            return str(error)

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(lambda _: accept(), range(2)))

    assert sum(isinstance(result, IntakeReceipt) for result in results) == 1
    duplicate_errors = [result for result in results if isinstance(result, str)]
    assert sum("duplicate delivery id" in result for result in duplicate_errors) == 1, (
        duplicate_errors
    )
    assert len(ledger.receipts()) == 1
    assert ledger.scorer_input("team-atomic").read_bytes() == bundle.read_bytes()
