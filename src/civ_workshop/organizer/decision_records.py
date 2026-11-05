"""Structured local decision records for organizer preparation and scoring checks."""

from __future__ import annotations

import csv
import io
import json
from collections.abc import Mapping
from datetime import datetime, timezone
from pathlib import Path

from civ_workshop.errors import CivError

HEADER = ("ts", "phase", "decision", "why", "evidence", "result")


def _validate(text: str, base: Path) -> list[list[str]]:
    try:
        rows = list(csv.reader(io.StringIO(text, newline=""), delimiter="\t", strict=True))
    except csv.Error as error:
        raise CivError(f"invalid decision TSV: {error}") from error
    if not rows or rows[0] != list(HEADER):
        raise CivError("decision TSV header must be: " + ", ".join(HEADER))
    for number, row in enumerate(rows[1:], 2):
        if len(row) != len(HEADER) or any("\n" in cell or "\r" in cell for cell in row):
            raise CivError(f"decision TSV row {number} must have six single-line cells")
        # Evidence is a JSON array of artifact paths, never a shell-delimited list.
        try:
            paths = json.loads(row[4])
        except ValueError as error:
            raise CivError(f"decision TSV row {number} evidence must be a JSON array") from error
        if not isinstance(paths, list) or not paths or any(
            not isinstance(path, str) or not path for path in paths
        ):
            raise CivError(f"decision TSV row {number} evidence must contain artifact paths")
        for path in paths:
            if not (base / path).exists():
                raise CivError(
                    f"decision TSV row {number} evidence artifact does not exist: {path}"
                )
    return rows


def append_decision(path: Path, record: Mapping[str, object]) -> None:
    """Append one validated structured record; refuse malformed historical files.

    Callers serialize records as JSON files so shell interpolation never constructs TSV.
    This writer assumes one organizer owns the log; it is not a concurrent ledger.
    """
    if set(record) != set(HEADER) - {"ts"}:
        raise CivError("decision record requires phase, decision, why, evidence, result")
    cells = [datetime.now(timezone.utc).isoformat()]
    for field in HEADER[1:]:
        value = record[field]
        if field == "evidence":
            cells.append(json.dumps(value, ensure_ascii=False))
        else:
            if not isinstance(value, str) or not value.strip():
                raise CivError(f"decision record {field} must be a non-empty string")
            cells.append(" ".join(value.split()))
    try:
        existing = path.read_text(encoding="utf-8") if path.exists() else ""
        if existing:
            _validate(existing, path.parent)
        stream = io.StringIO(newline="")
        writer = csv.writer(stream, delimiter="\t", lineterminator="\n")
        if not existing:
            writer.writerow(HEADER)
        writer.writerow(cells)
        addition = ("\n" if existing and not existing.endswith("\n") else "") + stream.getvalue()
        expected = _validate(existing + addition, path.parent)
        # Validate before creating even the parent or the output file.
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8", newline="") as output:
            output.write(addition)
        if _validate(path.read_text(encoding="utf-8"), path.parent) != expected:
            raise CivError("decision TSV postcondition failed")
    except OSError as error:
        raise CivError(f"cannot write decision record: {error}") from error
