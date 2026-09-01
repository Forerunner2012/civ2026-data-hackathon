from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

import pytest

import civ_workshop.workstation_qualification as qualification
from civ_workshop.artifacts import canonical_json, file_sha256
from civ_workshop.contracts import STABLE_FIELDS
from civ_workshop.errors import CivError
from civ_workshop.workstation_qualification import (
    audit_workstation_qualification,
    build_declaration_template,
    build_workstation_qualification,
)


def _write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"{canonical_json(value)}\n", encoding="utf-8", newline="\n")


def _attempt(seed: str) -> dict[str, object]:
    return {
        "commands": qualification.REQUIRED_COMMANDS,
        "disk_bytes": 2000,
        "exit_codes": [0] * len(qualification.REQUIRED_COMMANDS),
        "output_bytes": 1000,
        "output_set_sha256": seed * 64,
        "peak_rss_bytes": 50_000_000,
        "wall_time_ms": 3000,
    }


def _machine(machine_id: str, machine_class: str) -> dict[str, object]:
    return {
        "environment": {
            "architecture": "amd64",
            "container_runtime": "Docker Engine 29",
            "cpu_model": "event CPU",
            "display": "1920x1080",
            "graphics_adapter": "integrated graphics",
            "logical_cpu_count": 8,
            "memory_bytes": 16_000_000_000,
            "os_name": "Windows" if machine_class.startswith("windows") else "Ubuntu",
            "os_version": "fixture",
            "scaling_percent": 100,
        },
        "isolation": {
            "gpu_requested": False,
            "network_disabled": True,
            "output_only_writable": True,
            "release_inputs_read_only": True,
        },
        "machine_class": machine_class,
        "machine_id": machine_id,
        "prerequisites": {
            "developer_cache_present": False,
            "documented_prerequisites_only": True,
            "fresh_install": True,
            "network_fetch_after_isolation": False,
            "release_media_only": True,
            "repository_checkout_present": False,
            "user_profile_state_reused": False,
        },
        "runs": [
            {
                "attempts": [_attempt("a"), _attempt("a")],
                "dataset": "kashiwa",
                "label_pack_sha256": qualification.QUALIFICATION_LABEL_PACK_SHA256[
                    "kashiwa"
                ],
                "source_sha256": qualification.QUALIFICATION_SOURCE_SHA256["kashiwa"],
            },
            {
                "attempts": [_attempt("b"), _attempt("b")],
                "dataset": "reims",
                "label_pack_sha256": qualification.QUALIFICATION_LABEL_PACK_SHA256[
                    "reims"
                ],
                "source_sha256": qualification.QUALIFICATION_SOURCE_SHA256["reims"],
            },
        ],
    }


def _viewer(viewer: str, dataset: str) -> dict[str, object]:
    return {
        "approval_id": "human-viewer-fixture",
        "asset_sha256": qualification.VIEWER_ASSET_SHA256[viewer],
        "checksum_verified": True,
        "dataset": dataset,
        "evidence_sha256": ("3" if dataset == "kashiwa" else "4") * 64,
        "file_association_usable": True,
        "fonts_usable": True,
        "graphics_usable": True,
        "installed": True,
        "launched_offline": True,
        "layout_sha256": qualification.VIEWER_LAYOUT_SHA256[(viewer, dataset)],
        "machine_id": "windows-fresh-01",
        "offline_failure_message_usable": True,
        "permissions_usable": True,
        "scaling_usable": True,
        "viewer": viewer,
    }


def _fixture(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> tuple[Path, Path, Path, dict[str, Any]]:
    freeze = tmp_path / "release-freeze.json"
    _write_json(
        freeze,
        {
            "assembly": {
                "image": {
                    "archive_sha256": qualification.ACCEPTED_IMAGE_ARCHIVE_SHA256,
                    "id": qualification.ACCEPTED_IMAGE_ID,
                },
                "manifest_sha256": qualification.ACCEPTED_ASSEMBLY_SHA256,
            },
            "contract": "civ.release-freeze/v1",
            "development_authority": {
                "participant_distribution": False,
                "set_sha256": qualification.ACCEPTED_DEVELOPMENT_SET_SHA256,
            },
            "release_id": "civ-2026-phase5-release-freeze-v1",
        },
    )
    assembly = tmp_path / "attendee-kit-assembly.json"
    _write_json(assembly, {"fixture": True})
    real_file_sha256 = file_sha256

    def frozen_hash(path: Path) -> str:
        if path == freeze:
            return qualification.ACCEPTED_FREEZE_SHA256
        return real_file_sha256(path)

    monkeypatch.setattr(qualification, "file_sha256", frozen_hash)
    monkeypatch.setattr(
        qualification,
        "audit_assembly",
        lambda _path: {"manifest_sha256": qualification.ACCEPTED_ASSEMBLY_SHA256},
    )
    declaration: dict[str, Any] = {
        "contract": qualification.DECLARATION_CONTRACT,
        "interventions": [
            {
                "failure": "first profile lacked a file association",
                "release_bytes_changed": False,
                "resolution": "reinstalled the same verified viewer bytes",
                "status": "resolved",
                "step": "viewer recovery",
            }
        ],
        "machines": [
            _machine("windows-fresh-01", "windows-amd64-wsl2"),
            _machine("ubuntu-fresh-01", "ubuntu-linux-amd64"),
        ],
        "qualification_id": qualification.QUALIFICATION_ID,
        "recovery": {
            "approval_id": "human-recovery-fixture",
            "documented_path": "evidence/recovery.md",
            "evidence_sha256": "5" * 64,
            "machine_id": "windows-fresh-01",
            "profile_isolation_passed": True,
            "reinstall_passed": True,
            "uninstall_passed": True,
            "viewer": "lichtblick",
        },
        "viewer_checks": [
            _viewer(viewer, dataset)
            for viewer in sorted(qualification.REQUIRED_VIEWERS)
            for dataset in sorted(qualification.REQUIRED_DATASETS)
        ],
        "web_route": {
            "approval_id": "human-connected-route-fixture",
            "connected_check_passed": True,
            "evidence_sha256": "6" * 64,
            "url": qualification.OFFICIAL_LICHTBLICK_URL,
        },
    }
    declaration_path = tmp_path / "declaration.json"
    _write_json(declaration_path, declaration)
    return freeze, assembly, declaration_path, declaration


def test_qualification_is_deterministic_closed_and_auditable(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    freeze, assembly, declaration, _ = _fixture(tmp_path, monkeypatch)
    first = tmp_path / "first.json"
    second = tmp_path / "second.json"

    first_result = build_workstation_qualification(freeze, assembly, declaration, first)
    second_result = build_workstation_qualification(freeze, assembly, declaration, second)

    assert first.read_bytes() == second.read_bytes()
    assert first_result == second_result
    document = json.loads(first.read_text(encoding="utf-8"))
    assert set(document) == STABLE_FIELDS[qualification.CONTRACT]
    assert first_result == {
        "machine_count": 2,
        "manifest_sha256": file_sha256(first),
        "run_count": 4,
        "status": "accepted",
        "viewer_check_count": 4,
    }
    assert audit_workstation_qualification(first, freeze, assembly) == first_result


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        (
            lambda document: document["machines"][0]["prerequisites"].__setitem__(
                "developer_cache_present", True
            ),
            "developer_cache_present must be false",
        ),
        (
            lambda document: document["machines"][0]["isolation"].__setitem__(
                "network_disabled", False
            ),
            "network_disabled must be true",
        ),
        (
            lambda document: document["machines"][0]["runs"][0]["attempts"][1].__setitem__(
                "output_set_sha256", "9" * 64
            ),
            "output set is not deterministic",
        ),
        (
            lambda document: document["machines"][0]["runs"][0].__setitem__(
                "label_pack_sha256", "9" * 64
            ),
            "not the authorized development input",
        ),
        (
            lambda document: document["viewer_checks"][0].__setitem__(
                "approval_id", "agent-approval"
            ),
            "explicit human authority",
        ),
        (
            lambda document: document["viewer_checks"][0].__setitem__(
                "asset_sha256", "9" * 64
            ),
            "viewer asset does not match",
        ),
        (
            lambda document: document["interventions"][0].__setitem__(
                "status", "open"
            ),
            "remains unresolved",
        ),
        (
            lambda document: document["interventions"][0].__setitem__(
                "release_bytes_changed", True
            ),
            "release_bytes_changed must be false",
        ),
    ],
)
def test_qualification_rejects_unaccepted_evidence(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    mutation: Any,
    message: str,
) -> None:
    freeze, assembly, declaration_path, declaration = _fixture(tmp_path, monkeypatch)
    changed = copy.deepcopy(declaration)
    mutation(changed)
    _write_json(declaration_path, changed)

    with pytest.raises(CivError, match=message):
        build_workstation_qualification(
            freeze, assembly, declaration_path, tmp_path / "qualification.json"
        )


def test_qualification_rejects_another_release_freeze(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    freeze, assembly, declaration, _ = _fixture(tmp_path, monkeypatch)
    monkeypatch.setattr(qualification, "file_sha256", file_sha256)

    with pytest.raises(CivError, match="accepted Phase 5 identity"):
        build_workstation_qualification(
            freeze, assembly, declaration, tmp_path / "qualification.json"
        )


def test_workstation_schema_is_closed_and_pins_the_contract() -> None:
    schema_path = Path("schemas/civ.workstation-qualification.v1.schema.json")
    schema = json.loads(schema_path.read_text(encoding="utf-8"))

    assert schema["additionalProperties"] is False
    assert schema["properties"]["contract"]["const"] == qualification.CONTRACT
    assert set(schema["required"]) == STABLE_FIELDS[qualification.CONTRACT]


def test_declaration_template_pins_inputs_but_cannot_assert_acceptance(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    freeze, assembly, _, _ = _fixture(tmp_path, monkeypatch)
    template = tmp_path / "template.json"

    result = build_declaration_template(freeze, assembly, template)
    document = json.loads(template.read_text(encoding="utf-8"))

    assert result["status"] == "pending-human"
    assert len(document["machines"]) == 2
    assert len(document["viewer_checks"]) == 4
    assert document["viewer_checks"][0]["asset_sha256"] in set(
        qualification.VIEWER_ASSET_SHA256.values()
    )
    with pytest.raises(CivError):
        build_workstation_qualification(
            freeze, assembly, template, tmp_path / "qualification.json"
        )
