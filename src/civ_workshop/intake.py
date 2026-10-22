from __future__ import annotations

import os
import shutil
import sqlite3
import zipfile
from collections.abc import Iterator, Sequence
from contextlib import closing, contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from tempfile import NamedTemporaryFile, TemporaryDirectory
from typing import Literal, cast

from civ_workshop.artifacts import file_sha256, read_json_file, require_mapping, require_string
from civ_workshop.errors import CivError
from civ_workshop.reporting import (
    MAX_SUBMISSION_ARCHIVE_ENTRIES,
    MAX_SUBMISSION_BUNDLE_BYTES,
    MAX_SUBMISSION_ENTRY_BYTES,
    MAX_SUBMISSION_UNCOMPRESSED_BYTES,
    validate_submission_directory,
    write_canonical_submission_bundle,
)
from civ_workshop.submission_extension import contained_archive_path, safe_archive_path

TOKYO_CUTOFF = datetime.fromisoformat("2026-09-03T12:30:00+09:00").astimezone(timezone.utc)
MAX_FORM_RESPONSE_BYTES = 16 * 1024
MAX_IDENTITY_CHARACTERS = 200
MAX_DELIVERY_ID_CHARACTERS = 200


@dataclass(frozen=True)
class IntakeReceipt:
    contract: str
    delivery_id: str
    identity: str
    source: Literal["online", "local"]
    received_at_original: str
    received_at_utc: str
    bundle_sha256: str
    source_sha256: str | None
    status: Literal["on_time", "late"]
    track_id: str | None = None


@dataclass(frozen=True)
class ValidatedSubmission:
    bundle_sha256: str
    source_sha256: str


def latest_receipt(
    receipts: Sequence[IntakeReceipt],
    identity: str,
    status: Literal["on_time", "late"],
    *,
    track_id: str | None = None,
) -> IntakeReceipt | None:
    candidates = [
        (index, receipt)
        for index, receipt in enumerate(receipts)
        if receipt.identity == identity
        and receipt.status == status
        and (track_id is None or receipt.track_id == track_id)
    ]
    if not candidates:
        return None
    return max(
        candidates,
        key=lambda item: (datetime.fromisoformat(item[1].received_at_utc), item[0]),
    )[1]


def _parse_received_at(value: str) -> tuple[str, datetime]:
    original = value.strip()
    if not original:
        raise CivError("receipt timestamp is required")
    if len(original) > 64:
        raise CivError("receipt timestamp is too long")
    try:
        parsed = datetime.fromisoformat(original.replace("Z", "+00:00"))
    except ValueError as error:
        raise CivError("receipt timestamp must be ISO-8601 with a timezone") from error
    if parsed.tzinfo is None:
        raise CivError("receipt timestamp must include a timezone")
    return original, parsed.astimezone(timezone.utc)


def _require_sha256(value: str) -> str:
    normalized = value.strip().lower()
    invalid_characters = any(character not in "0123456789abcdef" for character in normalized)
    if len(normalized) != 64 or invalid_characters:
        raise CivError("pasted sha256 must be exactly 64 hexadecimal characters")
    return normalized


def _bounded_string(value: object, context: str, maximum: int) -> str:
    result = require_string(value, context)
    if len(result) > maximum:
        raise CivError(f"{context} exceeds {maximum} characters")
    return result


def _safe_archive_infos(archive: zipfile.ZipFile) -> list[zipfile.ZipInfo]:
    infos = archive.infolist()
    if len(infos) > MAX_SUBMISSION_ARCHIVE_ENTRIES:
        raise CivError(
            f"submission bundle has more than {MAX_SUBMISSION_ARCHIVE_ENTRIES} artifacts"
        )
    names = [info.filename for info in infos]
    if len(names) != len(set(names)):
        raise CivError("submission bundle contains duplicate artifact names")
    if len({name.casefold() for name in names}) != len(names):
        raise CivError("submission bundle contains case-colliding artifact names")
    total_size = 0
    for info in infos:
        # ZipInfo.filename can normalize backslashes on Windows before validation.
        name = info.orig_filename
        try:
            safe_archive_path(name, "submission bundle artifact path")
        except CivError as error:
            raise CivError(f"submission bundle contains an unsafe artifact path: {name}") from error
        if info.flag_bits & 0x1:
            raise CivError(f"submission bundle artifact is encrypted: {name}")
        if (info.external_attr >> 16) & 0o170000 == 0o120000:
            raise CivError(f"submission bundle artifact is symlinked: {name}")
        if info.compress_type != zipfile.ZIP_STORED:
            raise CivError("submission bundle must use the stored ZIP format emitted by civ report")
        if info.file_size > MAX_SUBMISSION_ENTRY_BYTES:
            raise CivError(
                f"submission bundle artifact exceeds {MAX_SUBMISSION_ENTRY_BYTES} bytes: {name}"
            )
        total_size += info.file_size
        if total_size > MAX_SUBMISSION_UNCOMPRESSED_BYTES:
            raise CivError(
                f"submission bundle expands beyond {MAX_SUBMISSION_UNCOMPRESSED_BYTES} bytes"
            )
    return infos


def _files_are_identical(first: Path, second: Path) -> bool:
    with first.open("rb") as first_stream, second.open("rb") as second_stream:
        while True:
            first_chunk = first_stream.read(1024 * 1024)
            second_chunk = second_stream.read(1024 * 1024)
            if first_chunk != second_chunk:
                return False
            if not first_chunk:
                return True


def _extract_validated_submission(bundle_path: Path, extracted: Path) -> None:
    if not bundle_path.is_file():
        raise CivError(f"submission bundle does not exist: {bundle_path}")
    try:
        if bundle_path.stat().st_size > MAX_SUBMISSION_BUNDLE_BYTES:
            raise CivError(f"submission bundle exceeds {MAX_SUBMISSION_BUNDLE_BYTES} bytes")
    except OSError as error:
        raise CivError(f"cannot inspect submission bundle: {error}") from error
    try:
        with zipfile.ZipFile(bundle_path) as archive:
            infos = _safe_archive_infos(archive)
            names = [info.filename for info in infos]
            destinations = [
                contained_archive_path(extracted, info.filename, "submission bundle artifact path")
                for info in infos
            ]
            for info, destination in zip(infos, destinations, strict=True):
                name = info.filename
                destination.parent.mkdir(parents=True, exist_ok=True)
                with archive.open(info) as source, destination.open("xb") as target:
                    shutil.copyfileobj(source, target, length=1024 * 1024)
                if destination.stat().st_size != info.file_size:
                    raise CivError(f"submission bundle artifact size changed while reading: {name}")
            expected_paths = validate_submission_directory(
                extracted, require_local_evidence=False, require_submission=True
            )
            expected = {path.relative_to(extracted).as_posix() for path in expected_paths}
            unexpected = sorted(set(names) - expected)
            missing = sorted(expected - set(names))
            if unexpected or missing:
                details = []
                if unexpected:
                    details.append(f"unexpected: {', '.join(unexpected)}")
                if missing:
                    details.append(f"missing: {', '.join(missing)}")
                raise CivError(f"unexpected submission artifacts ({'; '.join(details)})")
            canonical_bundle = extracted / ".canonical-submission.zip"
            write_canonical_submission_bundle(canonical_bundle, extracted, expected_paths)
            if not _files_are_identical(bundle_path, canonical_bundle):
                raise CivError("submission bundle must be the unchanged ZIP emitted by civ report")
            canonical_bundle.unlink()
    except (OSError, zipfile.BadZipFile, RuntimeError) as error:
        raise CivError(f"cannot read submission bundle: {error}") from error


@contextmanager
def open_validated_submission(bundle_path: Path) -> Iterator[Path]:
    """Yield a private working directory holding the validated bundle contents."""

    with TemporaryDirectory(prefix="civ-intake-") as temporary:
        _extract_validated_submission(bundle_path.resolve(), Path(temporary))
        yield Path(temporary)


def validated_submission(bundle_path: Path) -> ValidatedSubmission:
    with open_validated_submission(bundle_path) as working:
        manifest = read_json_file(working / "run-manifest.json", "run manifest")
        source_sha256 = require_string(
            require_mapping(manifest.get("source"), "run manifest source").get("sha256"),
            "run manifest source sha256",
        )
    return ValidatedSubmission(bundle_sha256=file_sha256(bundle_path), source_sha256=source_sha256)


def validate_submission_bundle(bundle_path: Path) -> str:
    return validated_submission(bundle_path).bundle_sha256


def _receipt_from_row(record: sqlite3.Row) -> IntakeReceipt:
    return IntakeReceipt(
        contract="civ.intake-receipt/v1alpha1",
        delivery_id=cast(str, record["delivery_id"]),
        identity=cast(str, record["identity"]),
        source=cast(Literal["online", "local"], record["source"]),
        received_at_original=cast(str, record["received_at_original"]),
        received_at_utc=cast(str, record["received_at_utc"]),
        bundle_sha256=cast(str, record["bundle_sha256"]),
        source_sha256=cast(str | None, record["source_sha256"]),
        status=cast(Literal["on_time", "late"], record["status"]),
        track_id=cast(str | None, record["track_id"]),
    )


class IntakeLedger:
    def __init__(self, root: Path) -> None:
        self.root = root.resolve()
        self.database_path = self.root / "intake.sqlite3"
        self.bundles_path = self.root / "bundles"

    @contextmanager
    def _connection(self) -> Iterator[sqlite3.Connection]:
        connection: sqlite3.Connection | None = None
        try:
            self.root.mkdir(parents=True, exist_ok=True)
            connection = sqlite3.connect(self.database_path, timeout=30)
            connection.row_factory = sqlite3.Row
            connection.execute("PRAGMA journal_mode=WAL")
            connection.execute("PRAGMA synchronous=FULL")
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS receipts (
                    sequence INTEGER PRIMARY KEY AUTOINCREMENT,
                    delivery_id TEXT NOT NULL UNIQUE,
                    identity TEXT NOT NULL,
                    source TEXT NOT NULL CHECK (source IN ('online', 'local')),
                    received_at_original TEXT NOT NULL,
                    received_at_utc TEXT NOT NULL,
                    bundle_sha256 TEXT NOT NULL,
                    source_sha256 TEXT,
                    track_id TEXT,
                    status TEXT NOT NULL CHECK (status IN ('on_time', 'late'))
                )
                """
            )
            columns = {
                cast(str, row["name"])
                for row in connection.execute("PRAGMA table_info(receipts)").fetchall()
            }
            if "source_sha256" not in columns:
                connection.execute("ALTER TABLE receipts ADD COLUMN source_sha256 TEXT")
            if "track_id" not in columns:
                connection.execute("ALTER TABLE receipts ADD COLUMN track_id TEXT")
            yield connection
        except OSError as error:
            raise CivError(f"cannot create intake ledger directory: {error}") from error
        except sqlite3.Error as error:
            raise CivError(f"cannot access intake ledger: {error}") from error
        finally:
            if connection is not None:
                connection.close()

    def receipts(self, *, read_only: bool = False) -> list[IntakeReceipt]:
        if read_only:
            # Scoring must neither initialize nor migrate an intake ledger.
            # mode=ro alone can still create WAL shared-memory sidecars. Require
            # a closed snapshot, then make SQLite treat every source byte as immutable.
            wal_path = self.database_path.with_name(self.database_path.name + "-wal")
            if wal_path.exists():
                raise CivError("read-only scoring requires a closed ledger snapshot without a WAL")
            try:
                with closing(
                    sqlite3.connect(self.database_path.as_uri() + "?mode=ro&immutable=1", uri=True)
                ) as connection:
                    connection.row_factory = sqlite3.Row
                    columns = {
                        row["name"] for row in connection.execute("PRAGMA table_info(receipts)")
                    }
                    source = "source_sha256" if "source_sha256" in columns else "NULL"
                    track = "track_id" if "track_id" in columns else "NULL"
                    rows = connection.execute(
                        "SELECT delivery_id, identity, source, received_at_original, "
                        "received_at_utc, bundle_sha256, "
                        f"{source} AS source_sha256, {track} AS track_id, status "
                        "FROM receipts ORDER BY sequence"
                    ).fetchall()
                return [_receipt_from_row(row) for row in rows]
            except sqlite3.Error as error:
                raise CivError(f"cannot read existing intake ledger: {error}") from error
        with self._connection() as connection:
            rows = connection.execute(
                """
                SELECT delivery_id, identity, source, received_at_original, received_at_utc,
                       bundle_sha256, source_sha256, track_id, status
                FROM receipts
                ORDER BY sequence
                """
            ).fetchall()
        return [_receipt_from_row(row) for row in rows]

    def authoritative(self, identity: str) -> IntakeReceipt:
        receipts = self.receipts()
        on_time_sources = {
            receipt.source_sha256
            for receipt in receipts
            if receipt.identity == identity
            and receipt.status == "on_time"
            and receipt.source_sha256 is not None
        }
        if len(on_time_sources) > 1:
            raise CivError(
                "authority is dataset-specific for this identity; use score-batch with the "
                "organizer product mapping"
            )
        receipt = latest_receipt(receipts, identity, "on_time")
        if receipt is None:
            raise CivError(f"no on-time submission exists for identity: {identity}")
        return receipt

    def quarantined(self) -> list[IntakeReceipt]:
        return [receipt for receipt in self.receipts() if receipt.status == "late"]

    def bundle_for(self, receipt: IntakeReceipt) -> Path:
        path = self.bundles_path / f"{receipt.bundle_sha256}.zip"
        if not path.is_file() or file_sha256(path) != receipt.bundle_sha256:
            raise CivError(
                f"authoritative bundle is missing or corrupt for identity: {receipt.identity}"
            )
        return path

    def scorer_input(self, identity: str) -> Path:
        return self.bundle_for(self.authoritative(identity))

    def accept_online(
        self,
        *,
        identity: str,
        received_at: str,
        submitted_sha256: str,
        bundle_path: Path,
        delivery_id: str,
        track_id: str | None = None,
    ) -> IntakeReceipt:
        return self._accept(
            identity=identity,
            received_at=received_at,
            submitted_sha256=submitted_sha256,
            bundle_path=bundle_path,
            delivery_id=delivery_id,
            source="online",
            track_id=track_id,
        )

    def accept_local(
        self,
        *,
        identity: str,
        received_at: str,
        submitted_sha256: str,
        bundle_path: Path,
        delivery_id: str,
        track_id: str | None = None,
    ) -> IntakeReceipt:
        return self._accept(
            identity=identity,
            received_at=received_at,
            submitted_sha256=submitted_sha256,
            bundle_path=bundle_path,
            delivery_id=delivery_id,
            source="local",
            track_id=track_id,
        )

    @contextmanager
    def _snapshot_bundle(self, bundle_path: Path) -> Iterator[Path]:
        snapshot_path: Path | None = None
        try:
            self.root.mkdir(parents=True, exist_ok=True)
            with (
                bundle_path.open("rb") as source,
                NamedTemporaryFile(
                    mode="wb",
                    prefix=".incoming-",
                    suffix=".zip",
                    dir=self.root,
                    delete=False,
                ) as target,
            ):
                snapshot_path = Path(target.name)
                copied = 0
                while chunk := source.read(1024 * 1024):
                    copied += len(chunk)
                    if copied > MAX_SUBMISSION_BUNDLE_BYTES:
                        raise CivError(
                            f"submission bundle exceeds {MAX_SUBMISSION_BUNDLE_BYTES} bytes"
                        )
                    target.write(chunk)
                target.flush()
                os.fsync(target.fileno())
            yield snapshot_path
        except OSError as error:
            raise CivError(f"cannot snapshot submission bundle: {error}") from error
        finally:
            if snapshot_path is not None:
                try:
                    snapshot_path.unlink(missing_ok=True)
                except OSError as error:
                    raise CivError(
                        f"cannot clean up submission bundle snapshot: {error}"
                    ) from error

    def _accept(
        self,
        *,
        identity: str,
        received_at: str,
        submitted_sha256: str,
        bundle_path: Path,
        delivery_id: str,
        source: Literal["online", "local"],
        track_id: str | None = None,
    ) -> IntakeReceipt:
        normalized_identity = identity.strip()
        if not normalized_identity:
            raise CivError("participant identity is required")
        if len(normalized_identity) > MAX_IDENTITY_CHARACTERS:
            raise CivError(f"participant identity exceeds {MAX_IDENTITY_CHARACTERS} characters")
        normalized_delivery_id = delivery_id.strip()
        if not normalized_delivery_id:
            raise CivError("delivery id is required")
        if len(normalized_delivery_id) > MAX_DELIVERY_ID_CHARACTERS:
            raise CivError(f"delivery id exceeds {MAX_DELIVERY_ID_CHARACTERS} characters")
        normalized_track_id = track_id.strip() if track_id is not None else None
        if normalized_track_id == "":
            raise CivError("track id must not be empty")
        if (
            normalized_track_id is not None
            and len(normalized_track_id) > MAX_DELIVERY_ID_CHARACTERS
        ):
            raise CivError(f"track id exceeds {MAX_DELIVERY_ID_CHARACTERS} characters")
        # Reject unsafe names before creating ledger or snapshot artifacts. The
        # immutable snapshot is validated again before a receipt is recorded.
        try:
            if bundle_path.stat().st_size > MAX_SUBMISSION_BUNDLE_BYTES:
                raise CivError(f"submission bundle exceeds {MAX_SUBMISSION_BUNDLE_BYTES} bytes")
            with zipfile.ZipFile(bundle_path) as archive:
                _safe_archive_infos(archive)
        except (OSError, zipfile.BadZipFile, RuntimeError) as error:
            raise CivError(f"cannot read submission bundle: {error}") from error
        with self._connection() as connection:
            duplicate = connection.execute(
                "SELECT 1 FROM receipts WHERE delivery_id = ?", (normalized_delivery_id,)
            ).fetchone()
        if duplicate is not None:
            raise CivError(f"duplicate delivery id: {normalized_delivery_id}")

        original_timestamp, received_utc = _parse_received_at(received_at)
        with self._snapshot_bundle(bundle_path) as snapshot:
            validated = validated_submission(snapshot)
            bundle_sha256 = validated.bundle_sha256
            if _require_sha256(submitted_sha256) != bundle_sha256:
                raise CivError(f"pasted sha256 does not match the bundle: expected {bundle_sha256}")

            receipt = IntakeReceipt(
                contract="civ.intake-receipt/v1alpha1",
                delivery_id=normalized_delivery_id,
                identity=normalized_identity,
                source=source,
                received_at_original=original_timestamp,
                received_at_utc=received_utc.isoformat(),
                bundle_sha256=bundle_sha256,
                source_sha256=validated.source_sha256,
                status="on_time" if received_utc <= TOKYO_CUTOFF else "late",
                track_id=normalized_track_id,
            )
            try:
                with self._connection() as connection, connection:
                    connection.execute(
                        """
                        INSERT INTO receipts (
                            delivery_id, identity, source, received_at_original, received_at_utc,
                            bundle_sha256, source_sha256, track_id, status
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            receipt.delivery_id,
                            receipt.identity,
                            receipt.source,
                            receipt.received_at_original,
                            receipt.received_at_utc,
                            receipt.bundle_sha256,
                            receipt.source_sha256,
                            receipt.track_id,
                            receipt.status,
                        ),
                    )
                    self._publish_bundle(snapshot, bundle_sha256)
                    try:
                        snapshot.unlink()
                    except OSError as error:
                        raise CivError(
                            f"cannot clean up submission bundle snapshot: {error}"
                        ) from error
            except CivError as error:
                if "UNIQUE constraint failed: receipts.delivery_id" in str(error):
                    raise CivError(f"duplicate delivery id: {normalized_delivery_id}") from None
                raise
            return receipt

    def _publish_bundle(self, bundle_path: Path, bundle_sha256: str) -> None:
        stored_bundle = self.bundles_path / f"{bundle_sha256}.zip"
        temporary_path: Path | None = None
        try:
            self.bundles_path.mkdir(parents=True, exist_ok=True)
            if stored_bundle.is_file() and file_sha256(stored_bundle) == bundle_sha256:
                return
            with (
                bundle_path.open("rb") as source,
                NamedTemporaryFile(
                    mode="wb",
                    prefix=".pending-",
                    suffix=".zip",
                    dir=self.bundles_path,
                    delete=False,
                ) as target,
            ):
                temporary_path = Path(target.name)
                shutil.copyfileobj(source, target, length=1024 * 1024)
                target.flush()
                os.fsync(target.fileno())
            if file_sha256(temporary_path) != bundle_sha256:
                raise CivError("submission bundle changed while it was being stored")
            os.replace(temporary_path, stored_bundle)
            temporary_path = None
        except OSError as error:
            raise CivError(f"cannot store submission bundle: {error}") from error
        finally:
            if temporary_path is not None:
                try:
                    temporary_path.unlink(missing_ok=True)
                except OSError as error:
                    raise CivError(f"cannot clean up pending submission bundle: {error}") from error

        if file_sha256(stored_bundle) != bundle_sha256:
            raise CivError("stored submission bundle failed its content-hash check")


def import_form_response(response_path: Path, ledger_root: Path) -> IntakeReceipt:
    response_path = response_path.resolve()
    try:
        if response_path.stat().st_size > MAX_FORM_RESPONSE_BYTES:
            raise CivError(f"form response exceeds {MAX_FORM_RESPONSE_BYTES} bytes")
    except OSError as error:
        raise CivError(f"cannot inspect form response: {error}") from error
    response = read_json_file(response_path, "form response")
    bundle_value = _bounded_string(response.get("bundle"), "form response bundle", 255)
    try:
        relative_bundle = safe_archive_path(bundle_value, "form response bundle")
    except CivError as error:
        raise CivError("form response bundle must name one sibling .zip file") from error
    if (
        "\\" in bundle_value
        or relative_bundle.is_absolute()
        or len(relative_bundle.parts) != 1
        or relative_bundle.suffix.lower() != ".zip"
    ):
        raise CivError("form response bundle must name one sibling .zip file")
    bundle_path = (response_path.parent / relative_bundle.name).resolve()
    try:
        bundle_path.relative_to(response_path.parent.resolve())
    except ValueError as error:
        raise CivError("form response bundle resolves outside the response directory") from error
    return IntakeLedger(ledger_root).accept_online(
        identity=_bounded_string(
            response.get("identity"), "form response identity", MAX_IDENTITY_CHARACTERS
        ),
        received_at=_bounded_string(response.get("received_at"), "form response received_at", 64),
        submitted_sha256=_bounded_string(response.get("sha256"), "form response sha256", 64),
        bundle_path=bundle_path,
        delivery_id=_bounded_string(
            response.get("delivery_id"),
            "form response delivery_id",
            MAX_DELIVERY_ID_CHARACTERS,
        ),
        track_id=(
            _bounded_string(
                response.get("track_id"), "form response track_id", MAX_DELIVERY_ID_CHARACTERS
            )
            if response.get("track_id") is not None
            else None
        ),
    )
