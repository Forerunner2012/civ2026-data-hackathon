from __future__ import annotations

import json
import zipfile
from pathlib import Path

import pytest

from civ_workshop.artifacts import file_sha256
from civ_workshop.detection import detect_events
from civ_workshop.errors import CivError
from civ_workshop.submission_extension import declare_extension_payloads, load_extension_entries
from tests.helpers import create_micro_case, prepare_scored_submission, run_civ


def test_declarations_package_exact_payloads_and_survive_detection(tmp_path: Path) -> None:
    case = create_micro_case(tmp_path / "case")
    working = tmp_path / "working"
    prepare_scored_submission(case, working)
    extension = working / "extension"
    extension.mkdir()
    contents = {
        "provenance.md": "Source citation.\n",
        "agent-trace.jsonl": '{"tool":"civ detect"}\n',
        "regression-test.json": '{"failure":"overlong interval","expected_events":0}\n',
    }
    arguments = ["report", str(working)]
    for name, content in contents.items():
        (extension / name).write_text(content, encoding="utf-8")
        kind = {
            "provenance.md": "provenance",
            "agent-trace.jsonl": "agent-trace",
            "regression-test.json": "regression-test",
        }[name]
        arguments += ["--extension", kind, "extension/" + name]
    result = run_civ(case.root, arguments)
    assert result.returncode == 0, result.stderr
    manifest = extension / "manifest.json"
    before = manifest.read_bytes()
    with zipfile.ZipFile(working / "submission.zip") as archive:
        for name in contents:
            assert archive.read("extension/" + name) == (extension / name).read_bytes()
    detect_events(case.spec, case.bag, working)
    assert manifest.read_bytes() == before
    payload = extension / "provenance.md"
    payload.write_text("Updated source citation.\n")
    with pytest.raises(CivError, match="hash changed"):
        detect_events(case.spec, case.bag, working)
    declare_extension_payloads(working, [["provenance", "extension/provenance.md"]])
    detect_events(case.spec, case.bag, working)
    entries = load_extension_entries(working)
    assert len(entries) == 3
    assert next(e for e in entries if e.kind == "provenance").sha256 == file_sha256(payload)


@pytest.mark.parametrize(
    ("kind", "path"),
    [
        ("agent-trace", "../outside.json"),
        ("external-resource", "extension/test.json"),
        ("regression-test", "extension/manifest.json"),
        ("agent-trace", "extension/trace.py"),
    ],
)
def test_invalid_declaration_does_not_replace_manifest(
    tmp_path: Path, kind: str, path: str
) -> None:
    extension = tmp_path / "extension"
    extension.mkdir()
    (extension / "test.json").write_text("{}")
    declare_extension_payloads(tmp_path, [["regression-test", "extension/test.json"]])
    manifest = extension / "manifest.json"
    before = manifest.read_bytes()
    with pytest.raises(CivError):
        declare_extension_payloads(tmp_path, [[kind, path]])
    assert manifest.read_bytes() == before


def test_refresh_cannot_hide_an_unrelated_changed_payload(tmp_path: Path) -> None:
    extension = tmp_path / "extension"
    extension.mkdir()
    for name in ("first.md", "second.md"):
        (extension / name).write_text("Original")
    declarations = [["provenance", "extension/first.md"], ["agent-trace", "extension/second.md"]]
    declare_extension_payloads(tmp_path, declarations)
    manifest = extension / "manifest.json"
    before = manifest.read_bytes()
    (extension / "second.md").write_text("Changed")
    with pytest.raises(CivError, match="hash changed"):
        declare_extension_payloads(tmp_path, declarations[:1])
    assert manifest.read_bytes() == before
    assert len(json.loads(before)["entries"]) == 2
