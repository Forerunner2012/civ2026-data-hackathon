from __future__ import annotations

import argparse
import re
import sys
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from tempfile import TemporaryDirectory
from typing import Any

from civ_workshop.artifacts import canonical_json, file_sha256, read_json_file
from civ_workshop.errors import CivError
from civ_workshop.kit_assembly import audit_assembly

CONTRACT = "civ.workstation-qualification/v1"
DECLARATION_CONTRACT = "civ.workstation-qualification-declaration/v1"
QUALIFICATION_ID = "civ-2026-phase5-workstation-qualification-v1"
ACCEPTED_FREEZE_SHA256 = "2003cc25fc24d57a56e84a50ff8a3d06ec6a7ab16cd95b78e2933dd27b91bf0f"
ACCEPTED_ASSEMBLY_SHA256 = "b661d18791f6d6a640ae35c595fc9b8a5ecccba94a451122977df831c6c2f097"
ACCEPTED_IMAGE_ID = "sha256:47f4017351802e878ff138c9e3aead0161de660914e79c252554968a91657560"
ACCEPTED_IMAGE_ARCHIVE_SHA256 = (
    "ff983defaa02671982ee78dbf13026d0d007c5c16082cd898658228875f289db"
)
ACCEPTED_DEVELOPMENT_SET_SHA256 = (
    "08a7bce5b2e3029ad5e8c12da395118443fd62850e99a8f7c4a329b5f3f2da02"
)
UNIVERSAL_FREEZE_SHA256 = "e7cbc09abcbfd2b1b0ac3c07cfbf5e6995f9c4d35e197edb33d441b11e5ce7c8"
UNIVERSAL_ASSEMBLY_SHA256 = "64c55f32a0b1898b8eadc4540a97e6d1b9c44f2b404abcb13df99326e9203bef"
UNIVERSAL_RELEASE_ID = "civ-2026-phase5-camera-context-release-freeze-v2"
OFFICIAL_LICHTBLICK_URL = "https://lichtblick-suite.github.io/lichtblick/"
REQUIRED_MACHINE_CLASSES = {"ubuntu-linux-amd64", "windows-amd64-wsl2"}
ADVERTISED_MACHINE_CLASS = "windows-amd64-wsl2"
REQUIRED_DATASETS = {"kashiwa", "reims"}
QUALIFICATION_SOURCE_SHA256 = {
    "kashiwa": "0188d748c0b49151e5af3f0c644e59e7cd1dda6ad7b41f8f5e64ada21b27056e",
    "reims": "9e37b7ee7a754707d15154b83ed797f3fa248cc6569f43e509cff5b2b642b110",
}
QUALIFICATION_LABEL_PACK_SHA256 = {
    "kashiwa": "5361ba59d734c22493ad5bc2f6d81eae5c17e399d7aa8a1b33753c60332ecb6a",
    "reims": "ad5d1b5525eeaa7fa35dd1ae4a457f903dc60d50deffe9bcb1f3887a60f8c204",
}
REQUIRED_COMMANDS = [
    "doctor",
    "inspect",
    "sample",
    "detect",
    "clip",
    "score",
    "report",
    "submission-init",
]
REQUIRED_VIEWERS = {"lichtblick", "plotjuggler"}
VIEWER_ASSET_SHA256 = {
    "lichtblick": "94420a37b3f9520091501842ee491966665090cfd23f40115f36f7ecf58ea2ec",
    "plotjuggler": "7b4674f10b48eadd43c195319f0aa5148324ad36464f870a14eb90253fdf4222",
}
VIEWER_LAYOUT_SHA256 = {
    ("lichtblick", "kashiwa"): "8a49a1fbe940b896a9fe7dcd95d19b79c09b0d60a733600f46fe4c7ce6903d84",
    ("lichtblick", "reims"): "8821afc2e9c5bb9ed366305b22065c53dc20cfcedaa3191e32875dfe705e8b62",
    ("plotjuggler", "kashiwa"): "1fde2907b5bfe8630aa55f89b5d1a5420aaf6672f66c1d8c75589715b5b725c0",
    ("plotjuggler", "reims"): "c79bcf876b0df1f2d72aeb34d2a929e809d054255d329518d3235c74db288716",
}
SHA256_PATTERN = re.compile(r"[0-9a-f]{64}")
ABSOLUTE_PATH_PATTERN = re.compile(r"(?:[A-Za-z]:\\|/(?:home|Users)/)")

DECLARATION_FIELDS = {
    "contract",
    "qualification_id",
    "machines",
    "viewer_checks",
    "web_route",
    "recovery",
    "interventions",
}
MACHINE_FIELDS = {
    "machine_id",
    "machine_class",
    "environment",
    "prerequisites",
    "isolation",
    "runs",
}
ENVIRONMENT_FIELDS = {
    "os_name",
    "os_version",
    "architecture",
    "cpu_model",
    "logical_cpu_count",
    "memory_bytes",
    "graphics_adapter",
    "display",
    "scaling_percent",
    "container_runtime",
}
PREREQUISITE_FIELDS = {
    "fresh_install",
    "documented_prerequisites_only",
    "release_media_only",
    "repository_checkout_present",
    "developer_cache_present",
    "user_profile_state_reused",
    "network_fetch_after_isolation",
}
ISOLATION_FIELDS = {
    "network_disabled",
    "gpu_requested",
    "release_inputs_read_only",
    "output_only_writable",
}
RUN_FIELDS = {"dataset", "source_sha256", "label_pack_sha256", "attempts"}
ATTEMPT_FIELDS = {
    "commands",
    "exit_codes",
    "wall_time_ms",
    "peak_rss_bytes",
    "output_bytes",
    "disk_bytes",
    "output_set_sha256",
}
VIEWER_FIELDS = {
    "machine_id",
    "viewer",
    "dataset",
    "asset_sha256",
    "layout_sha256",
    "checksum_verified",
    "installed",
    "launched_offline",
    "scaling_usable",
    "fonts_usable",
    "graphics_usable",
    "file_association_usable",
    "permissions_usable",
    "offline_failure_message_usable",
    "evidence_sha256",
    "approval_id",
}
WEB_FIELDS = {"url", "connected_check_passed", "evidence_sha256", "approval_id"}
RECOVERY_FIELDS = {
    "machine_id",
    "viewer",
    "uninstall_passed",
    "reinstall_passed",
    "documented_path",
    "profile_isolation_passed",
    "evidence_sha256",
    "approval_id",
}
INTERVENTION_FIELDS = {
    "step",
    "failure",
    "resolution",
    "status",
    "release_bytes_changed",
}


@dataclass(frozen=True)
class AcceptedRelease:
    assembly_sha256: str
    contract: str
    freeze_sha256: str
    release_id: str


ACCEPTED_RELEASES: Mapping[str, AcceptedRelease] = {
    ACCEPTED_FREEZE_SHA256: AcceptedRelease(
        assembly_sha256=ACCEPTED_ASSEMBLY_SHA256,
        contract="civ.release-freeze/v1",
        freeze_sha256=ACCEPTED_FREEZE_SHA256,
        release_id="civ-2026-phase5-release-freeze-v1",
    ),
    UNIVERSAL_FREEZE_SHA256: AcceptedRelease(
        assembly_sha256=UNIVERSAL_ASSEMBLY_SHA256,
        contract="civ.release-freeze/v2",
        freeze_sha256=UNIVERSAL_FREEZE_SHA256,
        release_id=UNIVERSAL_RELEASE_ID,
    ),
}


def _mapping(value: object, context: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise CivError(f"{context} must be a mapping")
    return {str(key): item for key, item in value.items()}


def _sequence(value: object, context: str) -> list[object]:
    if not isinstance(value, list):
        raise CivError(f"{context} must be a list")
    return list(value)


def _closed(value: Mapping[str, object], fields: set[str], context: str) -> None:
    unknown = sorted(set(value) - fields)
    missing = sorted(fields - set(value))
    if unknown:
        raise CivError(f"{context} has unknown field '{unknown[0]}'")
    if missing:
        raise CivError(f"{context} is missing field '{missing[0]}'")


def _string(value: object, context: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise CivError(f"{context} must be a non-empty string")
    result = value.strip()
    if ABSOLUTE_PATH_PATTERN.search(result):
        raise CivError(f"{context} must not expose an absolute host path")
    return result


def _sha256(value: object, context: str) -> str:
    result = _string(value, context)
    if SHA256_PATTERN.fullmatch(result) is None:
        raise CivError(f"{context} must be a lowercase SHA-256")
    return result


def _human(value: object, context: str) -> str:
    result = _string(value, context)
    if not result.startswith("human-"):
        raise CivError(f"{context} must identify explicit human authority")
    return result


def _positive_integer(value: object, context: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise CivError(f"{context} must be a positive integer")
    return value


def _non_negative_integer(value: object, context: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise CivError(f"{context} must be a non-negative integer")
    return value


def _is(value: object, expected: bool, context: str) -> bool:
    if value is not expected:
        raise CivError(f"{context} must be {str(expected).lower()}")
    return expected


def _target(value: object, context: str) -> str:
    result = _string(value, context)
    path = PurePosixPath(result)
    if path.is_absolute() or ".." in path.parts or str(path) != result or "\\" in result:
        raise CivError(f"{context} must be a normalized relative path")
    return result


def _accepted_release(freeze_path: Path, assembly_path: Path) -> dict[str, object]:
    freeze_sha256 = file_sha256(freeze_path)
    profile = ACCEPTED_RELEASES.get(freeze_sha256)
    if profile is None:
        raise CivError("release freeze does not match the accepted Phase 5 identity")
    freeze = _mapping(read_json_file(freeze_path, "release freeze"), "release freeze")
    if freeze.get("contract") != profile.contract:
        raise CivError("release freeze contract is not accepted")
    if freeze.get("release_id") != profile.release_id:
        raise CivError("release freeze id does not match its accepted identity")
    assembly = _mapping(freeze.get("assembly"), "release freeze assembly")
    image = _mapping(assembly.get("image"), "release freeze image")
    development = _mapping(freeze.get("development_authority"), "development authority")
    if assembly.get("manifest_sha256") != profile.assembly_sha256:
        raise CivError("release freeze assembly identity changed")
    if image.get("id") != ACCEPTED_IMAGE_ID:
        raise CivError("release freeze image identity changed")
    if image.get("archive_sha256") != ACCEPTED_IMAGE_ARCHIVE_SHA256:
        raise CivError("release freeze image archive identity changed")
    if development.get("set_sha256") != ACCEPTED_DEVELOPMENT_SET_SHA256:
        raise CivError("release freeze development authority changed")
    if development.get("participant_distribution") is not False:
        raise CivError("development authority must remain organizer-only")
    audit = audit_assembly(assembly_path)
    if audit.get("manifest_sha256") != profile.assembly_sha256:
        raise CivError("copied release media does not match the accepted assembly")
    return {
        "assembly_manifest_sha256": profile.assembly_sha256,
        "development_set_sha256": ACCEPTED_DEVELOPMENT_SET_SHA256,
        "freeze_manifest_sha256": profile.freeze_sha256,
        "image_archive_sha256": ACCEPTED_IMAGE_ARCHIVE_SHA256,
        "image_id": ACCEPTED_IMAGE_ID,
        "release_id": profile.release_id,
    }


def _environment(value: object, context: str) -> dict[str, object]:
    item = _mapping(value, context)
    _closed(item, ENVIRONMENT_FIELDS, context)
    return {
        "architecture": _string(item["architecture"], f"{context} architecture"),
        "container_runtime": _string(item["container_runtime"], f"{context} container runtime"),
        "cpu_model": _string(item["cpu_model"], f"{context} CPU model"),
        "display": _string(item["display"], f"{context} display"),
        "graphics_adapter": _string(item["graphics_adapter"], f"{context} graphics adapter"),
        "logical_cpu_count": _positive_integer(
            item["logical_cpu_count"], f"{context} logical CPU count"
        ),
        "memory_bytes": _positive_integer(item["memory_bytes"], f"{context} memory bytes"),
        "os_name": _string(item["os_name"], f"{context} OS name"),
        "os_version": _string(item["os_version"], f"{context} OS version"),
        "scaling_percent": _positive_integer(
            item["scaling_percent"], f"{context} scaling percent"
        ),
    }


def _attempt(value: object, context: str) -> dict[str, object]:
    item = _mapping(value, context)
    _closed(item, ATTEMPT_FIELDS, context)
    commands = [
        _string(entry, f"{context} command")
        for entry in _sequence(item["commands"], f"{context} commands")
    ]
    if commands != REQUIRED_COMMANDS:
        raise CivError(f"{context} must exercise the complete participant command sequence")
    exit_codes = _sequence(item["exit_codes"], f"{context} exit codes")
    if len(exit_codes) != len(REQUIRED_COMMANDS) or any(code != 0 for code in exit_codes):
        raise CivError(f"{context} command sequence must contain only successful exit codes")
    return {
        "commands": commands,
        "disk_bytes": _positive_integer(item["disk_bytes"], f"{context} disk bytes"),
        "exit_codes": [0] * len(REQUIRED_COMMANDS),
        "output_bytes": _positive_integer(item["output_bytes"], f"{context} output bytes"),
        "output_set_sha256": _sha256(
            item["output_set_sha256"], f"{context} output set SHA-256"
        ),
        "peak_rss_bytes": _positive_integer(item["peak_rss_bytes"], f"{context} peak RSS"),
        "wall_time_ms": _positive_integer(item["wall_time_ms"], f"{context} wall time"),
    }


def _run(value: object, context: str) -> dict[str, object]:
    item = _mapping(value, context)
    _closed(item, RUN_FIELDS, context)
    dataset = _string(item["dataset"], f"{context} dataset")
    if dataset not in REQUIRED_DATASETS:
        raise CivError(f"{context} dataset is not authorized")
    source_sha256 = _sha256(item["source_sha256"], f"{context} source SHA-256")
    label_pack_sha256 = _sha256(
        item["label_pack_sha256"], f"{context} label-pack SHA-256"
    )
    if source_sha256 != QUALIFICATION_SOURCE_SHA256[dataset]:
        raise CivError(f"{context} source is not the frozen qualification product")
    if label_pack_sha256 != QUALIFICATION_LABEL_PACK_SHA256[dataset]:
        raise CivError(f"{context} label pack is not the authorized development input")
    attempts = [
        _attempt(raw, f"{context} attempt {index}")
        for index, raw in enumerate(_sequence(item["attempts"], f"{context} attempts"), 1)
    ]
    if len(attempts) != 2:
        raise CivError(f"{context} requires exactly two fresh-output attempts")
    if attempts[0]["output_set_sha256"] != attempts[1]["output_set_sha256"]:
        raise CivError(f"{context} output set is not deterministic")
    return {
        "attempts": attempts,
        "dataset": dataset,
        "label_pack_sha256": label_pack_sha256,
        "source_sha256": source_sha256,
    }


def _machine(value: object, context: str) -> dict[str, object]:
    item = _mapping(value, context)
    _closed(item, MACHINE_FIELDS, context)
    machine_class = _string(item["machine_class"], f"{context} class")
    if machine_class not in REQUIRED_MACHINE_CLASSES:
        raise CivError(f"{context} class is not part of the qualification matrix")
    prerequisites = _mapping(item["prerequisites"], f"{context} prerequisites")
    _closed(prerequisites, PREREQUISITE_FIELDS, f"{context} prerequisites")
    for field in {"fresh_install", "documented_prerequisites_only", "release_media_only"}:
        _is(prerequisites[field], True, f"{context} prerequisites {field}")
    for field in {
        "repository_checkout_present",
        "developer_cache_present",
        "user_profile_state_reused",
        "network_fetch_after_isolation",
    }:
        _is(prerequisites[field], False, f"{context} prerequisites {field}")
    isolation = _mapping(item["isolation"], f"{context} isolation")
    _closed(isolation, ISOLATION_FIELDS, f"{context} isolation")
    for field in {"network_disabled", "release_inputs_read_only", "output_only_writable"}:
        _is(isolation[field], True, f"{context} isolation {field}")
    _is(isolation["gpu_requested"], False, f"{context} isolation gpu_requested")
    runs = [
        _run(raw, f"{context} run {index}")
        for index, raw in enumerate(_sequence(item["runs"], f"{context} runs"), 1)
    ]
    if {str(run["dataset"]) for run in runs} != REQUIRED_DATASETS or len(runs) != 2:
        raise CivError(f"{context} must qualify both datasets exactly once")
    return {
        "environment": _environment(item["environment"], f"{context} environment"),
        "isolation": {key: isolation[key] for key in sorted(ISOLATION_FIELDS)},
        "machine_class": machine_class,
        "machine_id": _string(item["machine_id"], f"{context} id"),
        "prerequisites": {key: prerequisites[key] for key in sorted(PREREQUISITE_FIELDS)},
        "runs": sorted(runs, key=lambda run: str(run["dataset"])),
    }


def _viewer_check(value: object, context: str) -> dict[str, object]:
    item = _mapping(value, context)
    _closed(item, VIEWER_FIELDS, context)
    viewer = _string(item["viewer"], f"{context} viewer")
    dataset = _string(item["dataset"], f"{context} dataset")
    if viewer not in REQUIRED_VIEWERS or dataset not in REQUIRED_DATASETS:
        raise CivError(f"{context} viewer or dataset is not in the accepted matrix")
    asset_sha256 = _sha256(item["asset_sha256"], f"{context} asset SHA-256")
    layout_sha256 = _sha256(item["layout_sha256"], f"{context} layout SHA-256")
    if asset_sha256 != VIEWER_ASSET_SHA256[viewer]:
        raise CivError(f"{context} viewer asset does not match the frozen release")
    if layout_sha256 != VIEWER_LAYOUT_SHA256[(viewer, dataset)]:
        raise CivError(f"{context} layout does not match the frozen release")
    for field in {
        "checksum_verified",
        "installed",
        "launched_offline",
        "scaling_usable",
        "fonts_usable",
        "graphics_usable",
        "file_association_usable",
        "permissions_usable",
        "offline_failure_message_usable",
    }:
        _is(item[field], True, f"{context} {field}")
    return {
        "approval_id": _human(item["approval_id"], f"{context} approval"),
        "asset_sha256": asset_sha256,
        "checksum_verified": True,
        "dataset": dataset,
        "evidence_sha256": _sha256(item["evidence_sha256"], f"{context} evidence SHA-256"),
        "file_association_usable": True,
        "fonts_usable": True,
        "graphics_usable": True,
        "installed": True,
        "launched_offline": True,
        "layout_sha256": layout_sha256,
        "machine_id": _string(item["machine_id"], f"{context} machine id"),
        "offline_failure_message_usable": True,
        "permissions_usable": True,
        "scaling_usable": True,
        "viewer": viewer,
    }


def _web_route(value: object) -> dict[str, object]:
    item = _mapping(value, "connected web route")
    _closed(item, WEB_FIELDS, "connected web route")
    if item["url"] != OFFICIAL_LICHTBLICK_URL:
        raise CivError("connected web route must be the official Lichtblick application")
    _is(item["connected_check_passed"], True, "connected web route check")
    return {
        "approval_id": _human(item["approval_id"], "connected web route approval"),
        "connected_check_passed": True,
        "evidence_sha256": _sha256(item["evidence_sha256"], "connected web route evidence"),
        "url": OFFICIAL_LICHTBLICK_URL,
    }


def _recovery(value: object, machine_ids: set[str]) -> dict[str, object]:
    item = _mapping(value, "participant recovery")
    _closed(item, RECOVERY_FIELDS, "participant recovery")
    if item["machine_id"] not in machine_ids:
        raise CivError("participant recovery machine is not qualified")
    if item["viewer"] not in REQUIRED_VIEWERS:
        raise CivError("participant recovery viewer is not accepted")
    for field in {"uninstall_passed", "reinstall_passed", "profile_isolation_passed"}:
        _is(item[field], True, f"participant recovery {field}")
    return {
        "approval_id": _human(item["approval_id"], "participant recovery approval"),
        "documented_path": _target(item["documented_path"], "participant recovery path"),
        "evidence_sha256": _sha256(item["evidence_sha256"], "participant recovery evidence"),
        "machine_id": _string(item["machine_id"], "participant recovery machine"),
        "profile_isolation_passed": True,
        "reinstall_passed": True,
        "uninstall_passed": True,
        "viewer": _string(item["viewer"], "participant recovery viewer"),
    }


def _intervention(value: object, context: str) -> dict[str, object]:
    item = _mapping(value, context)
    _closed(item, INTERVENTION_FIELDS, context)
    if item["status"] != "resolved":
        raise CivError(f"{context} remains unresolved")
    _is(item["release_bytes_changed"], False, f"{context} release_bytes_changed")
    return {
        "failure": _string(item["failure"], f"{context} failure"),
        "release_bytes_changed": False,
        "resolution": _string(item["resolution"], f"{context} resolution"),
        "status": "resolved",
        "step": _string(item["step"], f"{context} step"),
    }


def _template_attempt() -> dict[str, object]:
    return {
        "commands": REQUIRED_COMMANDS,
        "disk_bytes": 0,
        "exit_codes": [None] * len(REQUIRED_COMMANDS),
        "output_bytes": 0,
        "output_set_sha256": None,
        "peak_rss_bytes": 0,
        "wall_time_ms": 0,
    }


def _template_machine(machine_class: str) -> dict[str, object]:
    return {
        "environment": {
            "architecture": "REPLACE_ME",
            "container_runtime": "REPLACE_ME",
            "cpu_model": "REPLACE_ME",
            "display": "REPLACE_ME",
            "graphics_adapter": "REPLACE_ME",
            "logical_cpu_count": 0,
            "memory_bytes": 0,
            "os_name": "REPLACE_ME",
            "os_version": "REPLACE_ME",
            "scaling_percent": 0,
        },
        "isolation": {
            "gpu_requested": True,
            "network_disabled": False,
            "output_only_writable": False,
            "release_inputs_read_only": False,
        },
        "machine_class": machine_class,
        "machine_id": "REPLACE_ME",
        "prerequisites": {
            "developer_cache_present": True,
            "documented_prerequisites_only": False,
            "fresh_install": False,
            "network_fetch_after_isolation": True,
            "release_media_only": False,
            "repository_checkout_present": True,
            "user_profile_state_reused": True,
        },
        "runs": [
            {
                "attempts": [_template_attempt(), _template_attempt()],
                "dataset": dataset,
                "label_pack_sha256": QUALIFICATION_LABEL_PACK_SHA256[dataset],
                "source_sha256": QUALIFICATION_SOURCE_SHA256[dataset],
            }
            for dataset in sorted(REQUIRED_DATASETS)
        ],
    }


def build_declaration_template(
    freeze_manifest: Path, assembly_manifest: Path, output: Path
) -> dict[str, object]:
    _accepted_release(freeze_manifest, assembly_manifest)
    document = {
        "contract": DECLARATION_CONTRACT,
        "interventions": [],
        "machines": [
            _template_machine(machine_class)
            for machine_class in sorted(REQUIRED_MACHINE_CLASSES)
        ],
        "qualification_id": QUALIFICATION_ID,
        "recovery": {
            "approval_id": None,
            "documented_path": "evidence/recovery.md",
            "evidence_sha256": None,
            "machine_id": "REPLACE_ME",
            "profile_isolation_passed": False,
            "reinstall_passed": False,
            "uninstall_passed": False,
            "viewer": "REPLACE_ME",
        },
        "viewer_checks": [
            {
                "approval_id": None,
                "asset_sha256": VIEWER_ASSET_SHA256[viewer],
                "checksum_verified": False,
                "dataset": dataset,
                "evidence_sha256": None,
                "file_association_usable": False,
                "fonts_usable": False,
                "graphics_usable": False,
                "installed": False,
                "launched_offline": False,
                "layout_sha256": VIEWER_LAYOUT_SHA256[(viewer, dataset)],
                "machine_id": "REPLACE_ME",
                "offline_failure_message_usable": False,
                "permissions_usable": False,
                "scaling_usable": False,
                "viewer": viewer,
            }
            for viewer in sorted(REQUIRED_VIEWERS)
            for dataset in sorted(REQUIRED_DATASETS)
        ],
        "web_route": {
            "approval_id": None,
            "connected_check_passed": False,
            "evidence_sha256": None,
            "url": OFFICIAL_LICHTBLICK_URL,
        },
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(f"{canonical_json(document)}\n", encoding="utf-8", newline="\n")
    return {
        "machine_count": 2,
        "status": "pending-human",
        "template_sha256": file_sha256(output),
        "viewer_check_count": 4,
    }


def build_workstation_qualification(
    freeze_manifest: Path,
    assembly_manifest: Path,
    declaration_path: Path,
    output: Path,
) -> dict[str, object]:
    release = _accepted_release(freeze_manifest, assembly_manifest)
    declaration = _mapping(
        read_json_file(declaration_path, "workstation declaration"), "workstation declaration"
    )
    _closed(declaration, DECLARATION_FIELDS, "workstation declaration")
    if declaration["contract"] != DECLARATION_CONTRACT:
        raise CivError(f"workstation declaration contract must be '{DECLARATION_CONTRACT}'")
    if declaration["qualification_id"] != QUALIFICATION_ID:
        raise CivError("workstation qualification id changed")
    machines = [
        _machine(raw, f"machine {index}")
        for index, raw in enumerate(_sequence(declaration["machines"], "machines"), 1)
    ]
    classes = {str(machine["machine_class"]) for machine in machines}
    machine_ids = {str(machine["machine_id"]) for machine in machines}
    if classes != REQUIRED_MACHINE_CLASSES or len(machines) != 2 or len(machine_ids) != 2:
        raise CivError("qualification requires one fresh Windows/WSL2 and one fresh Ubuntu machine")
    advertised_ids = {
        str(machine["machine_id"])
        for machine in machines
        if machine["machine_class"] == ADVERTISED_MACHINE_CLASS
    }
    checks = [
        _viewer_check(raw, f"viewer check {index}")
        for index, raw in enumerate(_sequence(declaration["viewer_checks"], "viewer checks"), 1)
    ]
    matrix = {(str(check["viewer"]), str(check["dataset"])) for check in checks}
    required_matrix = {
        (viewer, dataset) for viewer in REQUIRED_VIEWERS for dataset in REQUIRED_DATASETS
    }
    if matrix != required_matrix:
        raise CivError("viewer checks must cover both viewers and both datasets")
    if len(checks) != 4 or {str(check["machine_id"]) for check in checks} != advertised_ids:
        raise CivError("viewer checks must run once on the advertised fresh Windows machine")
    interventions = [
        _intervention(raw, f"intervention {index}")
        for index, raw in enumerate(
            _sequence(declaration["interventions"], "interventions"), 1
        )
    ]
    document = {
        "contract": CONTRACT,
        "interventions": interventions,
        "machines": sorted(machines, key=lambda machine: str(machine["machine_class"])),
        "qualification_id": QUALIFICATION_ID,
        "recovery": _recovery(declaration["recovery"], machine_ids),
        "release": release,
        "status": "accepted",
        "viewer_checks": sorted(
            checks, key=lambda check: (str(check["viewer"]), str(check["dataset"]))
        ),
        "web_route": _web_route(declaration["web_route"]),
    }
    serialized = f"{canonical_json(document)}\n"
    if ABSOLUTE_PATH_PATTERN.search(serialized):
        raise CivError("workstation qualification exposes an absolute host path")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(serialized, encoding="utf-8", newline="\n")
    return {
        "machine_count": len(machines),
        "manifest_sha256": file_sha256(output),
        "run_count": sum(
            len(_sequence(machine["runs"], "qualified machine runs")) for machine in machines
        ),
        "status": "accepted",
        "viewer_check_count": len(checks),
    }


def audit_workstation_qualification(
    manifest_path: Path, freeze_manifest: Path, assembly_manifest: Path
) -> dict[str, object]:
    document = _mapping(
        read_json_file(manifest_path, "workstation qualification"), "workstation qualification"
    )
    if document.get("contract") != CONTRACT:
        raise CivError("workstation qualification contract is not accepted")
    declaration = {
        "contract": DECLARATION_CONTRACT,
        "interventions": document.get("interventions"),
        "machines": document.get("machines"),
        "qualification_id": document.get("qualification_id"),
        "recovery": document.get("recovery"),
        "viewer_checks": document.get("viewer_checks"),
        "web_route": document.get("web_route"),
    }
    with TemporaryDirectory(
        prefix=".workstation-qualification-audit-", dir=manifest_path.parent
    ) as temporary_directory:
        temporary_root = Path(temporary_directory)
        temporary = temporary_root / "declaration.json"
        temporary.write_text(
            f"{canonical_json(declaration)}\n", encoding="utf-8", newline="\n"
        )
        rebuilt = temporary_root / "qualification.json"
        result = build_workstation_qualification(
            freeze_manifest, assembly_manifest, temporary, rebuilt
        )
        if rebuilt.read_bytes() != manifest_path.read_bytes():
            raise CivError("workstation qualification is not canonical or inputs changed")
        return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build and audit Phase 5 workstation qualification"
    )
    commands = parser.add_subparsers(dest="command", required=True)
    template = commands.add_parser("template")
    template.add_argument("freeze", type=Path)
    template.add_argument("assembly", type=Path)
    template.add_argument("output", type=Path)
    build = commands.add_parser("build")
    build.add_argument("freeze", type=Path)
    build.add_argument("assembly", type=Path)
    build.add_argument("declaration", type=Path)
    build.add_argument("output", type=Path)
    audit = commands.add_parser("audit")
    audit.add_argument("manifest", type=Path)
    audit.add_argument("freeze", type=Path)
    audit.add_argument("assembly", type=Path)
    return parser


def main(argv: Sequence[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "template":
            result = build_declaration_template(args.freeze, args.assembly, args.output)
        elif args.command == "build":
            result = build_workstation_qualification(
                args.freeze, args.assembly, args.declaration, args.output
            )
        else:
            result = audit_workstation_qualification(args.manifest, args.freeze, args.assembly)
    except CivError as error:
        print(f"civ workstation-qualification: {error}", file=sys.stderr)
        raise SystemExit(2) from None
    print(canonical_json(result))


if __name__ == "__main__":
    main()
