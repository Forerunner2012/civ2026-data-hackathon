from __future__ import annotations

import json
import zipfile
from hashlib import sha256
from pathlib import Path

import pytest

from civ_workshop.artifacts import canonical_json, file_sha256
from civ_workshop.detection import detect_events
from civ_workshop.errors import CivError
from civ_workshop.intake import IntakeLedger, open_validated_submission, validate_submission_bundle
from civ_workshop.reporting import (
    build_report_bundle,
    validate_submission_directory,
    write_canonical_submission_bundle,
)
from civ_workshop.submission_extension import MAX_EXTENSION_PAYLOAD_BYTES
from tests.helpers import (
    MICRO_REPORT,
    MicroCase,
    create_micro_case,
    prepare_scored_submission,
    run_civ,
)


def _resource_case(root: Path) -> tuple[MicroCase, Path]:
    case = create_micro_case(root)
    resource = root / "caves.json"
    resource.write_text(
        canonical_json(
            {
                "contract": "civ.point-resource/v1",
                "coordinate_reference": "EPSG:4326",
                "points": [{"id": "target", "latitude": 2.0, "longitude": 2.0}],
            }
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )
    case.spec.write_text(
        case.spec.read_text(encoding="utf-8")
        .replace(
            "  signal:\n    topic: /micro/signal\n    field: value\n",
            "  latitude: {topic: /micro/signal, field: value}\n"
            "  longitude: {topic: /micro/signal, field: value}\n"
            "resources:\n"
            "  caves: {path: caves.json, contract: civ.point-resource/v1}\n"
            "derive:\n"
            "  cave_distance_m: {op: min_distance_to, resource: caves, "
            "from: [latitude, longitude]}\n",
        )
        .replace("condition: signal > 1.0", "condition: cave_distance_m <= 0.1"),
        encoding="utf-8",
    )
    return case, resource


def _add_extension_payloads(working: Path) -> dict[str, bytes]:
    payloads = {
        "extension/agent-trace.jsonl": b'{"artifact":"events.jsonl","tool":"civ detect"}\n',
        "extension/provenance.md": b"Source: participant-curated point list.\n",
        "extension/regression-test.json": b'{"failure":"outside radius","expected_events":0}\n',
    }
    for relative, content in payloads.items():
        path = working / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
    manifest_path = working / "extension" / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    media_types = {
        ".json": "application/json",
        ".jsonl": "application/x-ndjson",
        ".md": "text/markdown",
    }
    kinds = {
        "agent-trace.jsonl": "agent-trace",
        "provenance.md": "provenance",
        "regression-test.json": "regression-test",
    }
    for relative, content in payloads.items():
        path = Path(relative)
        manifest["entries"].append(
            {
                "kind": kinds[path.name],
                "media_type": media_types[path.suffix],
                "path": relative,
                "sha256": sha256(content).hexdigest(),
            }
        )
    manifest["entries"].sort(key=lambda entry: entry["path"])
    manifest_path.write_text(canonical_json(manifest) + "\n", encoding="utf-8", newline="\n")
    return payloads


def _legacy_v1_bundle(case: MicroCase, root: Path) -> Path:
    working = root / "legacy-v1"
    prepare_scored_submission(case, working)
    build_report_bundle(working)
    manifest_path = working / "run-manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["contract"] = "civ.run-manifest/v1"
    manifest["submission"] = {
        "contract": "civ.submission-bundle/v1",
        "reproduction": manifest["submission"]["reproduction"],
    }
    manifest_path.write_text(canonical_json(manifest) + "\n", encoding="utf-8", newline="\n")
    entries = validate_submission_directory(working, require_submission=True)
    bundle = working / "submission-v1.zip"
    write_canonical_submission_bundle(bundle, working, entries)
    return bundle


def test_v2_bundle_carries_exact_inert_extension_bytes_and_reproduces_offline(
    tmp_path: Path,
) -> None:
    case, resource = _resource_case(tmp_path / "case")
    working = tmp_path / "working"
    prepare_scored_submission(case, working)
    payloads = _add_extension_payloads(working)

    first = build_report_bundle(working)
    first_bytes = (working / "submission.zip").read_bytes()
    second = build_report_bundle(working)

    assert second == first
    assert (working / "submission.zip").read_bytes() == first_bytes
    with zipfile.ZipFile(working / "submission.zip") as archive:
        assert archive.read("detector/caves.json") == resource.read_bytes()
        for relative, content in payloads.items():
            assert archive.read(relative) == content

    with open_validated_submission(working / "submission.zip") as extracted:
        reproduced = tmp_path / "reproduced"
        detect_events(
            extracted / "detector" / "detector.yaml",
            case.bag,
            reproduced,
        )
        assert (reproduced / "events.jsonl").read_bytes() == (
            extracted / "events.jsonl"
        ).read_bytes()


def test_v1_and_v2_bundles_share_deterministic_form_and_usb_authority(
    tmp_path: Path,
) -> None:
    case = create_micro_case(tmp_path / "case")
    v1 = _legacy_v1_bundle(case, tmp_path)
    working = tmp_path / "current-v2"
    prepare_scored_submission(case, working)
    build_report_bundle(working)
    v2 = working / "submission.zip"
    ledger = IntakeLedger(tmp_path / "intake")

    first = ledger.accept_local(
        identity="team-mixed",
        received_at="2026-09-03T12:00:00+09:00",
        submitted_sha256=file_sha256(v1),
        bundle_path=v1,
        delivery_id="usb-v1",
    )
    final = ledger.accept_online(
        identity="team-mixed",
        received_at="2026-09-03T12:10:00+09:00",
        submitted_sha256=file_sha256(v2),
        bundle_path=v2,
        delivery_id="form-v2",
    )

    assert first.source_sha256 == final.source_sha256
    assert ledger.authoritative("team-mixed") == final
    assert ledger.scorer_input("team-mixed").read_bytes() == v2.read_bytes()
    assert validate_submission_bundle(v1) == file_sha256(v1)


def test_point_submission_without_practice_truth_reaches_intake_and_reproduces(
    tmp_path: Path,
) -> None:
    case, resource = _resource_case(tmp_path / "case")
    working = tmp_path / "working"
    # The participant workflow must succeed without reading any truth file.
    case.labels.unlink()
    for command in (
        ["detect", str(case.spec), str(case.bag), "--output", str(working)],
        ["clip", str(working / "events.jsonl"), str(case.bag)],
        ["score", str(working)],
    ):
        result = run_civ(case.root, command)
        assert result.returncode == 0, result.stderr
    metrics = json.loads((working / "metrics.json").read_text())
    assert metrics["status"] == "not_evaluated"
    assert metrics["aggregate"] == {
        "counts": None,
        "precision": None,
        "recall": None,
        "f1": None,
        "match_quality": None,
    }
    assert metrics["label_pack_sha256"] is None
    (working / "report.md").write_text(MICRO_REPORT, encoding="utf-8")
    (working / "figure.svg").write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="10"></svg>\n',
        encoding="utf-8",
    )
    (working / "reproduce.sh").write_text(
        "civ detect detector/detector.yaml REIMS.mcap --output replay\n"
        "civ clip replay/events.jsonl REIMS.mcap\nciv score replay\n",
        encoding="utf-8",
    )
    result = run_civ(case.root, ["report", str(working)])
    assert result.returncode == 0, result.stderr
    ledger = IntakeLedger(tmp_path / "intake")
    receipt = ledger.accept_local(
        identity="team-points",
        track_id="reims-caves-optional",
        received_at="2026-09-03T12:00:00+09:00",
        submitted_sha256=file_sha256(working / "submission.zip"),
        bundle_path=working / "submission.zip",
        delivery_id="points-no-truth",
    )
    assert receipt.track_id == "reims-caves-optional"
    with open_validated_submission(working / "submission.zip") as extracted:
        reproduced = tmp_path / "reproduced"
        detect_events(extracted / "detector/detector.yaml", case.bag, reproduced)
        assert (reproduced / "events.jsonl").read_bytes() == (working / "events.jsonl").read_bytes()
        assert (extracted / "detector/caves.json").read_bytes() == resource.read_bytes()


@pytest.mark.parametrize("mutation", ["score", "missing_matching", "missing_label_hash"])
def test_unevaluated_metrics_enforce_the_contract(tmp_path: Path, mutation: str) -> None:
    from civ_workshop.scoring import score_submission

    case = create_micro_case(tmp_path / "case")
    working = tmp_path / "working"
    prepare_scored_submission(case, working)
    score_submission(working)
    path = working / "metrics.json"
    metrics = json.loads(path.read_text())
    if mutation == "score":
        metrics["aggregate"]["f1"] = 1.0
    else:
        del metrics["matching" if mutation == "missing_matching" else "label_pack_sha256"]
    path.write_text(canonical_json(metrics) + "\n", encoding="utf-8")
    manifest_path = working / "run-manifest.json"
    manifest = json.loads(manifest_path.read_text())
    manifest["metrics"]["sha256"] = file_sha256(path)
    manifest_path.write_text(canonical_json(manifest) + "\n", encoding="utf-8")
    with pytest.raises(CivError, match="unevaluated metrics"):
        build_report_bundle(working)


@pytest.mark.parametrize(
    ("mutation", "diagnostic"),
    [
        ("missing", "payload is missing"),
        ("changed", "payload hash changed"),
        ("traversing", "contained archive-relative POSIX path"),
        ("drive", "contained archive-relative POSIX path"),
        ("stream", "contained archive-relative POSIX path"),
        ("device", "contained archive-relative POSIX path"),
        ("alias", "contained archive-relative POSIX path"),
        ("forbidden", "payload is forbidden"),
        ("case-collision", "duplicate or case-colliding path"),
    ],
)
def test_v2_rejects_invalid_extension_payloads(
    tmp_path: Path, mutation: str, diagnostic: str
) -> None:
    case, _ = _resource_case(tmp_path / mutation / "case")
    working = tmp_path / mutation / "working"
    prepare_scored_submission(case, working)
    payloads = _add_extension_payloads(working)
    manifest_path = working / "extension" / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    target = working / "extension" / "provenance.md"
    if mutation == "missing":
        target.unlink()
    elif mutation == "changed":
        target.write_text("changed", encoding="utf-8")
    elif mutation == "traversing":
        manifest["entries"][1]["path"] = "../provenance.md"
    elif mutation in {"drive", "stream", "device", "alias"}:
        manifest["entries"][1]["path"] = {
            "drive": "C:provenance.md",
            "stream": "extension/provenance.md:stream",
            "device": "extension/NUL.md",
            "alias": "extension/provenance.md.",
        }[mutation]
    elif mutation == "forbidden":
        forbidden = working / "extension" / "labels.json"
        forbidden.write_bytes(payloads["extension/regression-test.json"])
        manifest["entries"][1] = {
            "kind": "regression-test",
            "media_type": "application/json",
            "path": "extension/labels.json",
            "sha256": file_sha256(forbidden),
        }
    else:
        duplicate = dict(manifest["entries"][1])
        duplicate["path"] = duplicate["path"].upper()
        manifest["entries"].append(duplicate)
        manifest["entries"].sort(key=lambda entry: entry["path"])
    manifest_path.write_text(canonical_json(manifest) + "\n", encoding="utf-8")

    with pytest.raises(CivError, match=diagnostic):
        build_report_bundle(working)
    assert not (working / "submission.zip").exists()


def test_v2_rejects_extension_payload_size_limit(tmp_path: Path) -> None:
    case = create_micro_case(tmp_path / "case")
    working = tmp_path / "working"
    prepare_scored_submission(case, working)
    payload = working / "extension" / "trace.txt"
    payload.parent.mkdir(parents=True)
    payload.write_bytes(b"x" * (MAX_EXTENSION_PAYLOAD_BYTES + 1))
    manifest = {
        "contract": "civ.submission-extension/v1",
        "entries": [
            {
                "kind": "agent-trace",
                "media_type": "text/plain",
                "path": "extension/trace.txt",
                "sha256": file_sha256(payload),
            }
        ],
    }
    (working / "extension" / "manifest.json").write_text(
        canonical_json(manifest) + "\n", encoding="utf-8"
    )

    with pytest.raises(CivError, match="extension payload exceeds"):
        build_report_bundle(working)
