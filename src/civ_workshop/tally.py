"""Manual Tally CSV intake adapter.

The optional downloader argument is an internal test seam. The CLI always uses the bounded
stdlib HTTPS implementation and does not expose transport configuration to operators.
"""

from __future__ import annotations

import csv
import os
import re
from collections.abc import Callable, Iterator, Mapping
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any, Literal, TypedDict
from urllib.error import URLError
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

from civ_workshop.errors import CivError
from civ_workshop.intake import (
    MAX_DELIVERY_ID_CHARACTERS,
    MAX_IDENTITY_CHARACTERS,
    IntakeLedger,
    IntakeReceipt,
    _require_sha256,
)
from civ_workshop.reporting import MAX_SUBMISSION_BUNDLE_BYTES

TALLY_HEADERS = (
    "Submission ID",
    "Respondent ID",
    "Submitted at",
    "Participant or team identity",
    "SHA-256 printed by civ report",
    "Your submission.zip",
)
TALLY_IMPORT_CONTRACT = "civ.tally-import-summary/v1alpha1"
TALLY_STORAGE_HOST = "storage.tally.so"
TALLY_DOWNLOAD_TIMEOUT_SECONDS = 30
MAX_TALLY_UPLOAD_URL_CHARACTERS = 8_192
MAX_TALLY_CSV_BYTES = 5 * 1024 * 1024
MAX_TALLY_CSV_ROWS = 1_000
_DOWNLOAD_CHUNK_BYTES = 64 * 1024
_SENSITIVE_URL = re.compile(r"https?://[^\s\"']+", re.IGNORECASE)

DownloadTallyUpload = Callable[[str, Path], None]


class TallyReceiptPayload(TypedDict):
    contract: str
    delivery_id: str
    identity: str
    source: Literal["online", "local"]
    received_at_original: str
    received_at_utc: str
    bundle_sha256: str
    status: Literal["on_time", "late"]


class TallyOutcome(TypedDict, total=False):
    row: int
    delivery_id: str | None
    outcome: Literal["already_imported", "imported", "invalid"]
    receipt: TallyReceiptPayload
    diagnostic: str


class TallyImportCounts(TypedDict):
    already_imported: int
    imported: int
    invalid: int


class TallyImportSummary(TypedDict):
    contract: str
    rows: int
    counts: TallyImportCounts
    outcomes: list[TallyOutcome]


class _TallyDownloadFailure(Exception):
    pass


@dataclass(frozen=True)
class _TallyRow:
    delivery_id: str
    received_at: str
    identity: str
    submitted_sha256: str
    upload_url: str


def _required_text(row: Mapping[str | None, str | None], header: str, maximum: int) -> str:
    value = row.get(header)
    if value is None or not value.strip():
        raise CivError(f"Tally CSV field is required: {header}")
    normalized = value.strip()
    if len(normalized) > maximum:
        raise CivError(f"Tally CSV field exceeds {maximum} characters: {header}")
    return normalized


def _normalize_tally_submitted_at(value: str) -> str:
    raw = value.strip()
    if not raw:
        raise CivError("Tally Submitted at is required")
    if len(raw) > 64:
        raise CivError("Tally Submitted at exceeds 64 characters")
    try:
        parsed = datetime.fromisoformat(raw)
    except ValueError as error:
        raise CivError("Tally Submitted at must be a valid timezone-naive timestamp") from error
    if parsed.tzinfo is not None:
        raise CivError("Tally Submitted at must be timezone-naive UTC")
    return parsed.replace(tzinfo=timezone.utc).isoformat().replace("+00:00", "Z")


def _validate_tally_upload_url(value: str) -> str:
    url = value.strip()
    if not url:
        raise CivError("Tally upload URL is required")
    if len(url) > MAX_TALLY_UPLOAD_URL_CHARACTERS:
        raise CivError("Tally upload URL is too long")
    if any(character.isspace() for character in url):
        raise CivError("Tally upload URL contains whitespace")
    try:
        parsed = urlsplit(url)
        hostname = parsed.hostname
        port = parsed.port
    except ValueError as error:
        raise CivError("Tally upload URL is malformed") from error
    if (
        parsed.scheme.lower() != "https"
        or hostname is None
        or hostname.lower() != TALLY_STORAGE_HOST
        or port not in (None, 443)
        or parsed.username is not None
        or parsed.password is not None
        or not parsed.path
        or parsed.fragment
    ):
        raise CivError("Tally upload URL must be an HTTPS storage.tally.so URL")
    return url


def _parse_tally_row(row: Mapping[str | None, str | None]) -> _TallyRow:
    if None in row:
        raise CivError("Tally CSV row contains unexpected extra columns")
    delivery_id = _required_text(row, "Submission ID", MAX_DELIVERY_ID_CHARACTERS)
    _required_text(row, "Respondent ID", MAX_DELIVERY_ID_CHARACTERS)
    received_at = _normalize_tally_submitted_at(_required_text(row, "Submitted at", 64))
    identity = _required_text(row, "Participant or team identity", MAX_IDENTITY_CHARACTERS)
    pasted_sha256 = _required_text(row, "SHA-256 printed by civ report", 64)
    try:
        submitted_sha256 = _require_sha256(pasted_sha256)
    except CivError as error:
        raise CivError(
            "Tally CSV SHA-256 field must be exactly 64 hexadecimal characters"
        ) from error
    upload_url = _validate_tally_upload_url(
        _required_text(row, "Your submission.zip", MAX_TALLY_UPLOAD_URL_CHARACTERS)
    )
    return _TallyRow(
        delivery_id=delivery_id,
        received_at=received_at,
        identity=identity,
        submitted_sha256=submitted_sha256,
        upload_url=upload_url,
    )


class _TallyRedirectHandler(HTTPRedirectHandler):
    def redirect_request(
        self,
        request: Request,
        file: Any,
        code: int,
        msg: str,
        headers: Any,
        newurl: str,
    ) -> Request | None:
        _validate_tally_upload_url(newurl)
        return super().redirect_request(request, file, code, msg, headers, newurl)


def _download_tally_upload(url: str, destination: Path) -> None:
    _validate_tally_upload_url(url)
    request = Request(url, headers={"User-Agent": "civ-workshop-intake/1"})
    try:
        opener = build_opener(_TallyRedirectHandler())
        with opener.open(request, timeout=TALLY_DOWNLOAD_TIMEOUT_SECONDS) as response:
            _validate_tally_upload_url(response.geturl())
            content_length = response.headers.get("Content-Length")
            if content_length is not None:
                try:
                    if int(content_length) > MAX_SUBMISSION_BUNDLE_BYTES:
                        raise _TallyDownloadFailure(
                            "downloaded upload exceeds the 12 MiB bundle limit"
                        )
                except ValueError:
                    pass
            copied = 0
            with destination.open("wb") as stream:
                while True:
                    remaining = MAX_SUBMISSION_BUNDLE_BYTES - copied
                    chunk = response.read(min(_DOWNLOAD_CHUNK_BYTES, remaining + 1))
                    if not chunk:
                        break
                    copied += len(chunk)
                    if copied > MAX_SUBMISSION_BUNDLE_BYTES:
                        raise _TallyDownloadFailure(
                            "downloaded upload exceeds the 12 MiB bundle limit"
                        )
                    stream.write(chunk)
                stream.flush()
                os.fsync(stream.fileno())
    except _TallyDownloadFailure:
        raise
    except (CivError, URLError, TimeoutError, OSError, ValueError) as error:
        raise _TallyDownloadFailure("Tally upload download failed") from error


def _redact_diagnostic(value: str) -> str:
    return _SENSITIVE_URL.sub("[redacted URL]", value)


def _receipt_for_delivery(ledger: IntakeLedger, delivery_id: str) -> IntakeReceipt | None:
    return next(
        (receipt for receipt in ledger.receipts() if receipt.delivery_id == delivery_id),
        None,
    )


def _receipt_payload(receipt: IntakeReceipt) -> TallyReceiptPayload:
    return {
        "contract": receipt.contract,
        "delivery_id": receipt.delivery_id,
        "identity": receipt.identity,
        "source": receipt.source,
        "received_at_original": receipt.received_at_original,
        "received_at_utc": receipt.received_at_utc,
        "bundle_sha256": receipt.bundle_sha256,
        "status": receipt.status,
    }


def _outcome_base(row_number: int, delivery_id: str | None) -> TallyOutcome:
    return {"row": row_number, "delivery_id": delivery_id}


def _process_tally_row(
    row_number: int,
    raw_row: Mapping[str | None, str | None],
    ledger: IntakeLedger,
    downloader: DownloadTallyUpload,
) -> TallyOutcome:
    delivery_value = raw_row.get("Submission ID")
    delivery_id = delivery_value.strip() if delivery_value else None
    base = _outcome_base(row_number, delivery_id)
    try:
        row = _parse_tally_row(raw_row)
        existing = _receipt_for_delivery(ledger, row.delivery_id)
        if existing is not None:
            if (
                existing.source == "online"
                and existing.identity == row.identity
                and existing.received_at_original == row.received_at
                and existing.bundle_sha256 == row.submitted_sha256
            ):
                return {
                    **base,
                    "delivery_id": row.delivery_id,
                    "outcome": "already_imported",
                    "receipt": _receipt_payload(existing),
                }
            return {
                **base,
                "delivery_id": row.delivery_id,
                "outcome": "invalid",
                "diagnostic": "conflicting duplicate delivery id",
            }

        with TemporaryDirectory(prefix="civ-tally-") as temporary:
            downloaded = Path(temporary) / "submission.zip"
            try:
                downloader(row.upload_url, downloaded)
            except Exception as error:
                raise _TallyDownloadFailure("Tally upload download failed") from error
            if not downloaded.is_file():
                raise _TallyDownloadFailure("Tally upload download failed")
            try:
                if downloaded.stat().st_size > MAX_SUBMISSION_BUNDLE_BYTES:
                    raise _TallyDownloadFailure("downloaded upload exceeds the 12 MiB bundle limit")
            except OSError as error:
                raise _TallyDownloadFailure("Tally upload download failed") from error
            receipt = ledger.accept_online(
                identity=row.identity,
                received_at=row.received_at,
                submitted_sha256=row.submitted_sha256,
                bundle_path=downloaded,
                delivery_id=row.delivery_id,
            )
        return {
            **base,
            "delivery_id": row.delivery_id,
            "outcome": "imported",
            "receipt": _receipt_payload(receipt),
        }
    except _TallyDownloadFailure as error:
        return {**base, "outcome": "invalid", "diagnostic": _redact_diagnostic(str(error))}
    except CivError as error:
        diagnostic = str(error)
        if "pasted sha256 does not match" in diagnostic:
            diagnostic = "uploaded bundle hash does not match the CSV SHA-256"
        elif "duplicate delivery id" in diagnostic:
            diagnostic = "conflicting duplicate delivery id"
        return {
            **base,
            "outcome": "invalid",
            "diagnostic": _redact_diagnostic(diagnostic),
        }


@contextmanager
def _open_tally_csv(csv_path: Path) -> Iterator[csv.DictReader[str]]:
    try:
        if csv_path.stat().st_size > MAX_TALLY_CSV_BYTES:
            raise CivError("Tally CSV exceeds the 5 MiB import limit")
        stream = csv_path.open("r", encoding="utf-8-sig", newline="")
    except CivError:
        raise
    except OSError as error:
        raise CivError("cannot read Tally CSV") from error
    try:
        yield csv.DictReader(stream, strict=True)
    except csv.Error as error:
        raise CivError("cannot parse Tally CSV: malformed CSV") from error
    except UnicodeDecodeError as error:
        raise CivError("cannot parse Tally CSV: expected UTF-8") from error
    finally:
        stream.close()


def import_tally_csv(
    csv_path: Path,
    ledger_root: Path,
    *,
    downloader: DownloadTallyUpload | None = None,
) -> TallyImportSummary:
    """Import a manually exported Tally CSV into the shared online intake ledger."""

    ledger = IntakeLedger(ledger_root)
    download = downloader or _download_tally_upload
    outcomes: list[TallyOutcome] = []
    with _open_tally_csv(csv_path.resolve()) as reader:
        if tuple(reader.fieldnames or ()) != TALLY_HEADERS:
            raise CivError("Tally CSV headers do not match the expected export")
        try:
            rows = list(reader)
        except csv.Error as error:
            raise CivError("cannot parse Tally CSV: malformed CSV") from error
        if len(rows) > MAX_TALLY_CSV_ROWS:
            raise CivError("Tally CSV exceeds the 1000-row import limit")
        for row_number, row in enumerate(rows, start=1):
            outcomes.append(_process_tally_row(row_number, row, ledger, download))
    counts: TallyImportCounts = {
        "already_imported": sum(outcome["outcome"] == "already_imported" for outcome in outcomes),
        "imported": sum(outcome["outcome"] == "imported" for outcome in outcomes),
        "invalid": sum(outcome["outcome"] == "invalid" for outcome in outcomes),
    }
    return {
        "contract": TALLY_IMPORT_CONTRACT,
        "rows": len(outcomes),
        "counts": counts,
        "outcomes": outcomes,
    }
