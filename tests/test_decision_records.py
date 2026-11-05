from __future__ import annotations

import csv
import io
import json
from pathlib import Path

import pytest

from civ_workshop.errors import CivError
from civ_workshop.organizer.decision_records import HEADER, append_decision


def record(evidence: str) -> dict[str, object]:
    return {
        "phase": "check", "decision": 'checked "source"\tand\noutput',
        "why": "verify artifact", "evidence": [evidence], "result": "open",
    }


@pytest.mark.parametrize("newline", ["\n", "\r\n"])
def test_tsv_round_trip_handles_shell_characters_and_newlines(tmp_path: Path, newline: str) -> None:
    evidence = 'run with spaces, semicolons; and `r.txt'
    (tmp_path / evidence).write_text("proof")
    log = tmp_path / "decisions.tsv"
    append_decision(log, record(evidence))
    log.write_text(log.read_text(), newline=newline)
    before = log.read_bytes()
    append_decision(log, record(evidence))
    assert log.read_bytes().startswith(before)
    rows = list(csv.reader(io.StringIO(log.read_text()), delimiter="\t"))
    assert rows[0] == list(HEADER)
    assert len(rows) == 3
    assert all(len(row) == 6 for row in rows)
    assert json.loads(rows[1][4]) == [evidence]
    assert rows[1][2] == 'checked "source" and output'


@pytest.mark.parametrize("bad", [
    "wrong\theader\n", "ts\tphase\tdecision\twhy\tevidence\tresult\nx\ty\n",
])
def test_malformed_history_is_preserved(tmp_path: Path, bad: str) -> None:
    (tmp_path / "proof").touch()
    log = tmp_path / "decisions.tsv"
    log.write_text(bad)
    before = log.read_bytes()
    with pytest.raises(CivError, match="decision TSV"):
        append_decision(log, record("proof"))
    assert log.read_bytes() == before


def test_missing_evidence_stops_before_writing(tmp_path: Path) -> None:
    log = tmp_path / "missing-parent" / "decisions.tsv"
    with pytest.raises(CivError, match="artifact does not exist"):
        append_decision(log, record("run-002/missing.json"))
    assert not log.parent.exists()
