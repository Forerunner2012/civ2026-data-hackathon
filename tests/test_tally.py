from __future__ import annotations

import csv
import json
from hashlib import sha256
from pathlib import Path

import pytest

import civ_workshop.cli as cli_module
from civ_workshop.errors import CivError
from civ_workshop.intake import IntakeLedger
from civ_workshop.reporting import build_report_bundle
from civ_workshop.tally import (
    MAX_TALLY_CSV_BYTES,
    MAX_TALLY_CSV_ROWS,
    TALLY_HEADERS,
    TALLY_HEADERS_WITH_TRACK,
    import_tally_csv,
)
from tests.helpers import MicroCase, create_micro_case, prepare_scored_submission


@pytest.fixture
def micro_case(tmp_path: Path) -> MicroCase:
    return create_micro_case(tmp_path)


def _bundle(
    micro_case: MicroCase, root: Path, name: str = "submission", marker: str | None = None
) -> Path:
    working = root / name
    prepare_scored_submission(micro_case, working)
    if marker is not None:
        with (working / "report.md").open("a", encoding="utf-8") as stream:
            stream.write(f"\nMarker: {marker}\n")
    build_report_bundle(working)
    return working / "submission.zip"


def _write_csv(
    path: Path, rows: list[dict[str, str]], headers: tuple[str, ...] = TALLY_HEADERS
) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)


def _row(
    delivery_id: str,
    identity: str,
    submitted_at: str,
    bundle_hash: str,
    url: str,
) -> dict[str, str]:
    return {
        "Submission ID": delivery_id,
        "Respondent ID": f"respondent-{delivery_id}",
        "Submitted at": submitted_at,
        "Participant or team identity": identity,
        "SHA-256 printed by civ report": bundle_hash,
        "Your submission.zip": url,
    }


def test_tally_csv_imports_bom_rows_and_normalizes_naive_utc(
    tmp_path: Path, micro_case: MicroCase
) -> None:
    bundle = _bundle(micro_case, tmp_path)
    bundle_hash = sha256(bundle.read_bytes()).hexdigest()
    csv_path = tmp_path / "tally.csv"
    _write_csv(
        csv_path,
        [
            {
                "Submission ID": "tally-001",
                "Respondent ID": "respondent-001",
                "Submitted at": "2026-08-21 20:17:20",
                "Participant or team identity": "team-001",
                "SHA-256 printed by civ report": bundle_hash,
                "Your submission.zip": "https://storage.tally.so/uploads/one",
            }
        ],
    )

    def download(url: str, destination: Path) -> None:
        assert url == "https://storage.tally.so/uploads/one"
        destination.write_bytes(bundle.read_bytes())

    summary = import_tally_csv(csv_path, tmp_path / "ledger", downloader=download)

    assert summary["contract"] == "civ.tally-import-summary/v1alpha1"
    assert summary["counts"] == {"already_imported": 0, "imported": 1, "invalid": 0}
    assert summary["outcomes"][0]["outcome"] == "imported"
    receipt = summary["outcomes"][0]["receipt"]
    assert receipt["delivery_id"] == "tally-001"
    assert receipt["received_at_original"] == "2026-08-21T20:17:20Z"
    assert receipt["received_at_utc"] == "2026-08-21T20:17:20+00:00"
    assert receipt["bundle_sha256"] == bundle_hash
    assert (
        IntakeLedger(tmp_path / "ledger").scorer_input("team-001").read_bytes()
        == bundle.read_bytes()
    )


def test_tally_csv_can_record_a_track_specific_delivery(
    tmp_path: Path, micro_case: MicroCase
) -> None:
    bundle = _bundle(micro_case, tmp_path)
    bundle_hash = sha256(bundle.read_bytes()).hexdigest()
    row = _row(
        "track-delivery",
        "team-track",
        "2026-09-03 03:00:00",
        bundle_hash,
        "https://storage.tally.so/uploads/track",
    )
    row["Track ID"] = "reims-cave"
    csv_path = tmp_path / "track-tally.csv"
    _write_csv(csv_path, [row], TALLY_HEADERS_WITH_TRACK)

    def download(_url: str, destination: Path) -> None:
        destination.write_bytes(bundle.read_bytes())

    summary = import_tally_csv(
        csv_path,
        tmp_path / "ledger",
        downloader=download,
    )

    assert summary["counts"]["imported"] == 1
    assert summary["outcomes"][0]["receipt"]["track_id"] == "reims-cave"
    assert IntakeLedger(tmp_path / "ledger").receipts()[0].track_id == "reims-cave"


def test_tally_rows_are_isolated_and_last_on_time_receipt_wins(
    tmp_path: Path, micro_case: MicroCase
) -> None:
    first_bundle = _bundle(micro_case, tmp_path, "first", marker="first")
    second_bundle = _bundle(micro_case, tmp_path, "second", marker="second")
    first_hash = sha256(first_bundle.read_bytes()).hexdigest()
    second_hash = sha256(second_bundle.read_bytes()).hexdigest()
    urls = {
        "https://storage.tally.so/uploads/first": first_bundle,
        "https://storage.tally.so/uploads/second": second_bundle,
    }
    csv_path = tmp_path / "tally.csv"
    _write_csv(
        csv_path,
        [
            _row("first", "team-1", "2026-09-03 03:00:00", first_hash, list(urls)[0]),
            _row("second", "team-1", "2026-09-03 03:20:00", second_hash, list(urls)[1]),
            _row("late", "team-1", "2026-09-03 03:30:01", first_hash, list(urls)[0]),
            _row("repeat", "team-2", "2026-09-03 03:10:00", first_hash, list(urls)[0]),
        ],
    )

    def download(url: str, destination: Path) -> None:
        destination.write_bytes(urls[url].read_bytes())

    summary = import_tally_csv(csv_path, tmp_path / "ledger", downloader=download)
    ledger = IntakeLedger(tmp_path / "ledger")

    assert summary["counts"] == {"already_imported": 0, "imported": 4, "invalid": 0}
    assert ledger.authoritative("team-1").delivery_id == "second"
    assert ledger.authoritative("team-1").bundle_sha256 == second_hash
    assert [receipt.delivery_id for receipt in ledger.quarantined()] == ["late"]
    assert ledger.scorer_input("team-2").read_bytes() == first_bundle.read_bytes()


def test_tally_rerun_is_idempotent_without_requiring_the_signed_url(
    tmp_path: Path, micro_case: MicroCase
) -> None:
    bundle = _bundle(micro_case, tmp_path)
    bundle_hash = sha256(bundle.read_bytes()).hexdigest()
    csv_path = tmp_path / "tally.csv"
    _write_csv(
        csv_path,
        [_row("same", "team", "2026-09-03 03:00:00", bundle_hash, "https://storage.tally.so/a")],
    )

    def download(_url: str, destination: Path) -> None:
        destination.write_bytes(bundle.read_bytes())

    first = import_tally_csv(csv_path, tmp_path / "ledger", downloader=download)

    def expired_download(_url: str, _destination: Path) -> None:
        raise AssertionError("an exact rerun should not download the upload")

    second = import_tally_csv(csv_path, tmp_path / "ledger", downloader=expired_download)

    assert first["counts"]["imported"] == 1
    assert second["counts"] == {"already_imported": 1, "imported": 0, "invalid": 0}
    assert second["outcomes"][0]["receipt"] == first["outcomes"][0]["receipt"]


def test_tally_conflicting_duplicate_is_invalid_and_preserves_existing_receipt(
    tmp_path: Path, micro_case: MicroCase
) -> None:
    first_bundle = _bundle(micro_case, tmp_path, "first", marker="first")
    second_bundle = _bundle(micro_case, tmp_path, "second", marker="second")
    first_hash = sha256(first_bundle.read_bytes()).hexdigest()
    second_hash = sha256(second_bundle.read_bytes()).hexdigest()
    csv_path = tmp_path / "tally.csv"
    _write_csv(
        csv_path,
        [_row("same", "team", "2026-09-03 03:00:00", first_hash, "https://storage.tally.so/one")],
    )

    def download_first(_url: str, destination: Path) -> None:
        destination.write_bytes(first_bundle.read_bytes())

    import_tally_csv(csv_path, tmp_path / "ledger", downloader=download_first)
    _write_csv(
        csv_path,
        [
            _row(
                "same",
                "other-team",
                "2026-09-03 03:01:00",
                second_hash,
                "https://storage.tally.so/two",
            )
        ],
    )

    def unexpected_download(_url: str, _destination: Path) -> None:
        raise AssertionError("a conflicting duplicate should not download")

    summary = import_tally_csv(csv_path, tmp_path / "ledger", downloader=unexpected_download)

    assert summary["counts"] == {"already_imported": 0, "imported": 0, "invalid": 1}
    assert summary["outcomes"][0]["diagnostic"] == "conflicting duplicate delivery id"
    assert IntakeLedger(tmp_path / "ledger").authoritative("team").bundle_sha256 == first_hash


def test_tally_hash_mismatch_and_download_failure_do_not_stop_later_rows(
    tmp_path: Path, micro_case: MicroCase
) -> None:
    bundle = _bundle(micro_case, tmp_path)
    bundle_hash = sha256(bundle.read_bytes()).hexdigest()
    signed_url = "https://storage.tally.so/uploads/file?token=secret-token"
    csv_path = tmp_path / "tally.csv"
    _write_csv(
        csv_path,
        [
            _row("bad-hash", "bad-hash-team", "2026-09-03 03:00:00", "0" * 64, signed_url),
            _row("failed", "failed-team", "2026-09-03 03:01:00", bundle_hash, signed_url),
            _row("good", "good-team", "2026-09-03 03:02:00", bundle_hash, signed_url),
        ],
    )

    calls = [0]

    def download(_url: str, destination: Path) -> None:
        # The adapter deliberately gives every row a private fixed filename; use a call count to
        # make this fake deterministic without inspecting provider data.
        calls[0] += 1
        if calls[0] == 2:
            raise RuntimeError(signed_url)
        destination.write_bytes(bundle.read_bytes())

    summary = import_tally_csv(csv_path, tmp_path / "ledger", downloader=download)
    output = json.dumps(summary, sort_keys=True)

    assert summary["counts"] == {"already_imported": 0, "imported": 1, "invalid": 2}
    assert "uploaded bundle hash does not match" in summary["outcomes"][0]["diagnostic"]
    assert summary["outcomes"][1]["diagnostic"] == "Tally upload download failed"
    assert signed_url not in output
    assert "secret-token" not in output
    assert IntakeLedger(tmp_path / "ledger").authoritative("good-team").bundle_sha256 == bundle_hash


def test_tally_rejects_malformed_and_oversized_uploads_but_keeps_rows_isolated(
    tmp_path: Path, micro_case: MicroCase
) -> None:
    bundle = _bundle(micro_case, tmp_path)
    bundle_hash = sha256(bundle.read_bytes()).hexdigest()
    csv_path = tmp_path / "tally.csv"
    _write_csv(
        csv_path,
        [
            _row(
                "malformed",
                "bad",
                "2026-09-03 03:00:00",
                "0" * 64,
                "https://storage.tally.so/bad",
            ),
            _row(
                "oversized",
                "big",
                "2026-09-03 03:01:00",
                bundle_hash,
                "https://storage.tally.so/big",
            ),
            _row(
                "good",
                "good",
                "2026-09-03 03:02:00",
                bundle_hash,
                "https://storage.tally.so/good",
            ),
        ],
    )

    def download(url: str, destination: Path) -> None:
        if url.endswith("/bad"):
            destination.write_bytes(b"not-a-zip")
        elif url.endswith("/big"):
            destination.write_bytes(b"x" * (12 * 1024 * 1024 + 1))
        else:
            destination.write_bytes(bundle.read_bytes())

    summary = import_tally_csv(csv_path, tmp_path / "ledger", downloader=download)

    assert summary["counts"] == {"already_imported": 0, "imported": 1, "invalid": 2}
    assert "submission bundle" in summary["outcomes"][0]["diagnostic"]
    assert "12 MiB" in summary["outcomes"][1]["diagnostic"]
    assert IntakeLedger(tmp_path / "ledger").authoritative("good").bundle_sha256 == bundle_hash


def test_tally_requires_the_exact_export_headers(tmp_path: Path) -> None:
    csv_path = tmp_path / "wrong.csv"
    csv_path.write_text("Submission ID,Submitted at\nfoo,2026-09-03 03:00:00\n", encoding="utf-8")

    with pytest.raises(CivError, match="headers"):
        import_tally_csv(csv_path, tmp_path / "ledger", downloader=lambda *_: None)


def test_tally_bounds_the_export_before_importing_any_rows(tmp_path: Path) -> None:
    csv_path = tmp_path / "too-many.csv"
    row = _row(
        "delivery",
        "team",
        "2026-09-03 03:00:00",
        "0" * 64,
        "https://storage.tally.so/file",
    )
    _write_csv(csv_path, [row] * (MAX_TALLY_CSV_ROWS + 1))

    with pytest.raises(CivError, match="1000-row"):
        import_tally_csv(csv_path, tmp_path / "ledger", downloader=lambda *_: None)
    assert not (tmp_path / "ledger" / "intake.sqlite3").exists()

    oversized_csv = tmp_path / "oversized.csv"
    oversized_csv.write_bytes(b"x" * (MAX_TALLY_CSV_BYTES + 1))
    with pytest.raises(CivError, match="5 MiB"):
        import_tally_csv(oversized_csv, tmp_path / "ledger", downloader=lambda *_: None)


def test_tally_rejects_non_tally_upload_hosts_without_downloading(
    tmp_path: Path, micro_case: MicroCase
) -> None:
    bundle = _bundle(micro_case, tmp_path)
    bundle_hash = sha256(bundle.read_bytes()).hexdigest()
    csv_path = tmp_path / "tally.csv"
    _write_csv(
        csv_path,
        [_row("bad-url", "team", "2026-09-03 03:00:00", bundle_hash, "https://example.test/file")],
    )

    def unexpected_download(_url: str, _destination: Path) -> None:
        raise AssertionError("invalid URL must be rejected before downloading")

    summary = import_tally_csv(csv_path, tmp_path / "ledger", downloader=unexpected_download)

    assert summary["counts"] == {"already_imported": 0, "imported": 0, "invalid": 1}
    assert "storage.tally.so" in summary["outcomes"][0]["diagnostic"]


def test_intake_tally_cli_dispatches_the_manual_csv_path(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    expected = {
        "contract": "civ.tally-import-summary/v1alpha1",
        "rows": 0,
        "counts": {"already_imported": 0, "imported": 0, "invalid": 0},
        "outcomes": [],
    }

    def fake_import(csv_path: Path, ledger_root: Path) -> dict[str, object]:
        assert csv_path == tmp_path / "submissions.csv"
        assert ledger_root == tmp_path / "ledger"
        return expected

    monkeypatch.setattr(cli_module, "import_tally_csv", fake_import)
    cli_module.main(
        ["intake-tally", str(tmp_path / "submissions.csv"), "--ledger", str(tmp_path / "ledger")]
    )

    assert json.loads(capsys.readouterr().out) == expected
