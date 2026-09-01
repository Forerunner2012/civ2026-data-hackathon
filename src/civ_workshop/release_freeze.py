from __future__ import annotations

import argparse
import re
import sys
from collections.abc import Mapping, Sequence
from hashlib import sha256
from pathlib import Path, PurePosixPath
from typing import Any

from civ_workshop.artifacts import canonical_json, file_sha256, read_json_file
from civ_workshop.contracts import require_closed_fields
from civ_workshop.errors import CivError
from civ_workshop.kit_assembly import audit_assembly

CONTRACT = "civ.release-freeze/v1"
DECLARATION_CONTRACT = "civ.release-freeze-declaration/v1"
LEGAL_REVIEW_CONTRACT = "civ.release-legal-review/v1"
LEGAL_APPROVAL_CONTRACT = "civ.release-legal-approval/v1"
PACKAGE_REVIEW_MODE = "package-reviewed"
GLOBAL_RISK_MODE = "global-risk-acceptance"
GLOBAL_RISK_STATEMENT = (
    "The reviewer accepts the exact frozen SBOM inventory for this event release without "
    "package-level licence conclusions. Scanner NOASSERTION values and corresponding-source "
    "uncertainty remain recorded and are accepted release risks."
)
PACKAGE_REVIEW_STATEMENT = "Package-level legal review completed with zero unresolved items."
RELEASE_ID = "civ-2026-phase5-release-freeze-v1"
ACCEPTED_SOURCE_COMMIT = "bc0cb9cfb98b92665626a5b64c9a65571e80aaf2"
ACCEPTED_ASSEMBLY_SHA256 = "b661d18791f6d6a640ae35c595fc9b8a5ecccba94a451122977df831c6c2f097"
ACCEPTED_INVENTORY_SHA256 = "aee496467d4537acca417d3481e8cec81c0e8db4e945fd10b3aac7dfb56c27bf"
ACCEPTED_IMAGE_ID = "sha256:47f4017351802e878ff138c9e3aead0161de660914e79c252554968a91657560"
ACCEPTED_IMAGE_NAME = "civ-phase4:attendee-candidate-558e85c"
ACCEPTED_IMAGE_ARCHIVE_SHA256 = (
    "ff983defaa02671982ee78dbf13026d0d007c5c16082cd898658228875f289db"
)
ACCEPTED_IMAGE_ARCHIVE_BYTES = 464_562_688
RECOVERY_NOTICE = (
    "Two Kashiwa products derive from recovered recordings. Structural recovery made the "
    "recordings readable but does not prove that truncation lost no records. The caveat must "
    "remain with every distribution; corrupt-parent locations are intentionally omitted."
)
SHA256_PATTERN = re.compile(r"[0-9a-f]{64}")
COMMIT_PATTERN = re.compile(r"[0-9a-f]{40}")
CREATED_PATTERN = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z")
DATE_PATTERN = re.compile(r"\d{4}-\d{2}-\d{2}")
SUBJECT_PATTERN = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
COPYLEFT_PATTERN = re.compile(r"(?:A?GPL|LGPL|MPL|EPL|CDDL)-", re.IGNORECASE)
ABSOLUTE_PATH_PATTERN = re.compile(r"(?:[A-Za-z]:\\|/(?:home|Users)/)")
PARTICIPANT_COMPONENT_METADATA = {
    "ATTRIBUTION.md": ("attribution", "all"),
    "README.md": ("instructions", "all"),
    "checksums": ("integrity", "all"),
    "container": ("participant-runtime-image", "linux-amd64"),
    "data": ("participant-data", "all"),
    "docs": ("participant-documentation", "all"),
    "examples": ("participant-examples", "all"),
    "fallback": ("offline-fallback", "all"),
    "layouts": ("viewer-layouts", "all"),
    "offline": ("offline-dependencies", "windows-amd64"),
    "participant-kit.json": ("participant-inventory", "all"),
    "runtime": ("participant-runtime-source", "all"),
    "schemas": ("participant-contract-schemas", "all"),
    "site": ("public-static-site", "all"),
    "templates": ("submission-templates", "all"),
    "viewer": ("offline-viewers", "windows-amd64"),
}

DECLARATION_FIELDS = {
    "contract",
    "source_commit",
    "architecture",
    "artifacts",
    "sboms",
    "legal_review_target",
    "legal_approval_target",
    "notices_target",
    "development_authority",
}
LEGAL_REVIEW_FIELDS = {
    "contract",
    "sboms",
    "packages",
    "source_archives",
    "unresolved_count",
    "approval_id",
    "review_mode",
}
LEGAL_APPROVAL_FIELDS = {
    "contract",
    "id",
    "decision",
    "review_sha256",
    "notices_sha256",
    "licence_artifacts",
    "source_artifacts",
    "review_mode",
    "accepted_unresolved_count",
    "risk_statement",
    "authority",
    "approved_on",
    "source",
}
LEGAL_APPROVAL_ARTIFACT_FIELDS = {"target", "sha256"}
ARCHITECTURE_FIELDS = {
    "container_platforms",
    "viewer_platforms",
    "advertised_participant_platforms",
    "decision",
    "approval",
}
APPROVAL_FIELDS = {"id", "document_sha256"}
ARTIFACT_DECLARATION_FIELDS = {"role", "target", "platform", "provenance"}
SBOM_DECLARATION_FIELDS = {"subject", "target"}
DEVELOPMENT_AUTHORITY_FIELDS = {
    "set_sha256",
    "record_count",
    "datasets",
    "approval",
    "participant_distribution",
    "sealed_authority_included",
}
LEGAL_PACKAGE_FIELDS = {
    "key",
    "sbom_sha256",
    "spdx_id",
    "name",
    "version",
    "scanner_license",
    "source_locator",
    "resolution",
    "concluded_license",
    "source_target",
    "evidence",
}


def _mapping(value: object, context: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise CivError(f"{context} must be a mapping")
    return {str(key): item for key, item in value.items()}


def _sequence(value: object, context: str) -> list[object]:
    if not isinstance(value, list):
        raise CivError(f"{context} must be a list")
    return list(value)


def _string(value: object, context: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise CivError(f"{context} must be a non-empty string")
    return value.strip()


def _sha256(value: object, context: str) -> str:
    digest = _string(value, context)
    if SHA256_PATTERN.fullmatch(digest) is None:
        raise CivError(f"{context} must be a lowercase SHA-256")
    return digest


def _non_negative_integer(value: object, context: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise CivError(f"{context} must be a non-negative integer")
    return value


def _positive_integer(value: object, context: str) -> int:
    result = _non_negative_integer(value, context)
    if result == 0:
        raise CivError(f"{context} must be a positive integer")
    return result


def _target(value: object, context: str = "release target") -> str:
    target = _string(value, context)
    path = PurePosixPath(target)
    if path.is_absolute() or ".." in path.parts or str(path) != target or "\\" in target:
        raise CivError(f"{context} must be a normalized relative path: {target}")
    return target


def _closed(value: Mapping[str, object], allowed: set[str], context: str) -> None:
    unknown = sorted(set(value) - allowed)
    if unknown:
        raise CivError(f"{context} has unknown field '{unknown[0]}'")


def _write_text(path: Path, content: str, context: str) -> None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8", newline="\n")
    except OSError as error:
        raise CivError(f"cannot write {context}: {error}") from error


def _approval(value: object, context: str) -> dict[str, str]:
    approval = _mapping(value, context)
    _closed(approval, APPROVAL_FIELDS, context)
    if set(approval) != APPROVAL_FIELDS:
        raise CivError(f"{context} must record id and document_sha256")
    approval_id = _string(approval["id"], f"{context} id")
    if not approval_id.startswith("human-"):
        raise CivError(f"{context} id must identify explicit human authority")
    return {
        "id": approval_id,
        "document_sha256": _sha256(
            approval["document_sha256"], f"{context} document_sha256"
        ),
    }


def _spdx_document(path: Path, context: str) -> dict[str, Any]:
    document = _mapping(read_json_file(path, context), context)
    if document.get("spdxVersion") != "SPDX-2.3":
        raise CivError(f"{context} must use SPDX-2.3")
    packages = _sequence(document.get("packages"), f"{context} packages")
    if not packages:
        raise CivError(f"{context} must contain at least one package")
    for index, item in enumerate(packages):
        package = _mapping(item, f"{context} package {index}")
        _string(package.get("SPDXID"), f"{context} package {index} SPDXID")
        _string(package.get("name"), f"{context} package {index} name")
    return document


def normalize_spdx(
    source: Path,
    output: Path,
    *,
    subject: str,
    subject_sha256: str,
    created: str,
) -> dict[str, object]:
    if SUBJECT_PATTERN.fullmatch(subject) is None:
        raise CivError("SPDX subject must be a lowercase kebab-case identifier")
    subject_digest = _sha256(subject_sha256, "SPDX subject_sha256")
    if CREATED_PATTERN.fullmatch(created) is None:
        raise CivError("SPDX created must be an exact UTC second such as 2026-08-30T00:00:00Z")
    document = _spdx_document(source, "SPDX input")
    creation = _mapping(document.get("creationInfo"), "SPDX creationInfo")
    creators = _sequence(creation.get("creators"), "SPDX creators")
    if not creators:
        raise CivError("SPDX creators must not be empty")
    creation["created"] = created
    creation["creators"] = sorted(_string(item, "SPDX creator") for item in creators)
    document["creationInfo"] = creation
    document["documentNamespace"] = f"https://civ.example/sbom/{subject}/{subject_digest}"
    document["name"] = f"civ-2026-{subject}-sbom"

    packages = [
        _mapping(item, "SPDX package")
        for item in _sequence(document["packages"], "SPDX packages")
    ]
    packages.sort(
        key=lambda item: (
            str(item.get("name", "")),
            str(item.get("versionInfo", "")),
            str(item.get("SPDXID", "")),
        )
    )
    for package in packages:
        if isinstance(package.get("externalRefs"), list):
            package["externalRefs"] = sorted(
                package["externalRefs"],
                key=lambda item: canonical_json(_mapping(item, "SPDX external reference")),
            )
    document["packages"] = packages
    if isinstance(document.get("relationships"), list):
        document["relationships"] = sorted(
            (_mapping(item, "SPDX relationship") for item in document["relationships"]),
            key=lambda item: (
                str(item.get("spdxElementId", "")),
                str(item.get("relationshipType", "")),
                str(item.get("relatedSpdxElement", "")),
            ),
        )
    if isinstance(document.get("documentDescribes"), list):
        document["documentDescribes"] = sorted(
            _string(item, "SPDX documentDescribes entry")
            for item in document["documentDescribes"]
        )
    _write_text(output, f"{canonical_json(document)}\n", "normalized SPDX")
    return {
        "byte_size": output.stat().st_size,
        "package_count": len(packages),
        "sha256": file_sha256(output),
        "spdx_version": "SPDX-2.3",
        "subject": subject,
    }


def _source_locator(package: Mapping[str, object]) -> str:
    references = package.get("externalRefs")
    if isinstance(references, list):
        for item in references:
            reference = _mapping(item, "SPDX external reference")
            if reference.get("referenceType") == "purl":
                return _string(reference.get("referenceLocator"), "SPDX purl")
    download = package.get("downloadLocation")
    if isinstance(download, str) and download not in {"", "NONE", "NOASSERTION"}:
        return download
    return "NOASSERTION"


def _legal_package_records(
    sbom_paths: Sequence[Path],
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    packages: list[dict[str, object]] = []
    sboms: list[dict[str, object]] = []
    for path in sbom_paths:
        document = _spdx_document(path, f"SBOM {path.name}")
        digest = file_sha256(path)
        document_packages = _sequence(document["packages"], f"SBOM {path.name} packages")
        sboms.append({"package_count": len(document_packages), "sha256": digest})
        for item in document_packages:
            package = _mapping(item, f"SBOM {path.name} package")
            spdx_id = _string(package.get("SPDXID"), "SPDX package id")
            key = sha256(f"{digest}\0{spdx_id}".encode()).hexdigest()
            scanner_license = package.get("licenseDeclared")
            if not isinstance(scanner_license, str) or not scanner_license.strip():
                scanner_license = "NOASSERTION"
            packages.append(
                {
                    "concluded_license": None,
                    "evidence": None,
                    "key": key,
                    "name": _string(package.get("name"), "SPDX package name"),
                    "resolution": "pending",
                    "sbom_sha256": digest,
                    "scanner_license": scanner_license.strip(),
                    "source_locator": _source_locator(package),
                    "source_target": None,
                    "spdx_id": spdx_id,
                    "version": str(package.get("versionInfo", "NOASSERTION")),
                }
            )
    packages.sort(key=lambda item: (str(item["name"]), str(item["version"]), str(item["key"])))
    sboms.sort(key=lambda item: str(item["sha256"]))
    return packages, sboms


def _render_notices(packages: Sequence[Mapping[str, object]]) -> str:
    lines = [
        "# CIV 2026 third-party notices",
        "",
        "This file is generated from the frozen SPDX package inventory and the human legal review.",
        "It records package identity and review evidence; the separately archived licence/source",
        "materials remain authoritative.",
        "",
    ]
    for package in sorted(
        packages,
        key=lambda item: (
            str(item.get("name", "")),
            str(item.get("version", "")),
            str(item.get("key", "")),
        ),
    ):
        lines.extend(
            [
                f"## {package['name']} {package['version']}",
                "",
                f"- SPDX package: `{package['spdx_id']}`",
                f"- Recorded licence: `{package['concluded_license']}`",
                f"- Source: `{package['source_locator']}`",
                f"- Review evidence: {package['evidence']}",
                "",
            ]
        )
        source_target = package.get("source_target")
        if isinstance(source_target, str) and source_target:
            lines.insert(len(lines) - 1, f"- Archived source: `{source_target}`")
    return "\n".join(lines)


def build_legal_review_template(
    sbom_paths: Sequence[Path], output: Path, notices_output: Path
) -> dict[str, object]:
    if not sbom_paths:
        raise CivError("at least one SPDX SBOM is required")
    packages, sboms = _legal_package_records(sbom_paths)
    review: dict[str, object] = {
        "approval_id": None,
        "contract": LEGAL_REVIEW_CONTRACT,
        "packages": packages,
        "review_mode": "pending",
        "sboms": sboms,
        "source_archives": [],
        "unresolved_count": len(packages),
    }
    _write_text(output, f"{canonical_json(review)}\n", "legal review template")
    pending = [
        {
            **package,
            "concluded_license": package["scanner_license"],
            "evidence": "PENDING HUMAN LEGAL REVIEW",
        }
        for package in packages
    ]
    _write_text(notices_output, _render_notices(pending), "third-party notice template")
    return {
        "package_count": len(packages),
        "review_sha256": file_sha256(output),
        "unresolved_count": len(packages),
    }


def accept_global_legal_risk(
    review_path: Path,
    output: Path,
    *,
    approval_id: str,
    source_archives: Sequence[str] = (),
) -> dict[str, object]:
    if not approval_id.startswith("human-"):
        raise CivError("legal approval_id must identify explicit human authority")
    review = _mapping(read_json_file(review_path, "legal review"), "legal review")
    _closed(review, LEGAL_REVIEW_FIELDS, "legal review")
    if set(review) != LEGAL_REVIEW_FIELDS:
        raise CivError("legal review is missing a required field")
    if review.get("contract") != LEGAL_REVIEW_CONTRACT:
        raise CivError(f"legal review contract must be '{LEGAL_REVIEW_CONTRACT}'")
    if review.get("review_mode") not in {"pending", GLOBAL_RISK_MODE}:
        raise CivError("only a pending or global-risk review can receive global acceptance")
    packages = [
        _mapping(item, "legal package")
        for item in _sequence(review.get("packages"), "legal review packages")
    ]
    noassertion_count = 0
    for package in packages:
        _closed(package, LEGAL_PACKAGE_FIELDS, "legal package")
        if set(package) != LEGAL_PACKAGE_FIELDS:
            raise CivError("legal package is missing a required field")
        scanner_license = _string(package.get("scanner_license"), "scanner licence")
        if scanner_license == "NOASSERTION":
            noassertion_count += 1
        package["concluded_license"] = scanner_license
        package["evidence"] = GLOBAL_RISK_STATEMENT
        package["resolution"] = "risk-accepted"
        package["source_target"] = None
    review["approval_id"] = approval_id
    review["packages"] = packages
    review["review_mode"] = GLOBAL_RISK_MODE
    review["source_archives"] = sorted(
        {_target(item, "legal source archive") for item in source_archives}
    )
    review["unresolved_count"] = len(packages)
    _write_text(output, f"{canonical_json(review)}\n", "global legal risk review")
    return {
        "noassertion_count": noassertion_count,
        "package_count": len(packages),
        "review_mode": GLOBAL_RISK_MODE,
        "review_sha256": file_sha256(output),
        "unresolved_count": len(packages),
    }


def render_legal_notices(review_path: Path, output: Path) -> dict[str, object]:
    review = _mapping(read_json_file(review_path, "legal review"), "legal review")
    _closed(review, LEGAL_REVIEW_FIELDS, "legal review")
    if set(review) != LEGAL_REVIEW_FIELDS:
        raise CivError("legal review is missing a required field")
    if review.get("contract") != LEGAL_REVIEW_CONTRACT:
        raise CivError(f"legal review contract must be '{LEGAL_REVIEW_CONTRACT}'")
    packages = [
        _mapping(item, "legal package")
        for item in _sequence(review.get("packages"), "legal review packages")
    ]
    review_mode = _string(review.get("review_mode"), "legal review_mode")
    if review_mode not in {PACKAGE_REVIEW_MODE, GLOBAL_RISK_MODE}:
        raise CivError("legal review_mode is not final")
    for package in packages:
        _closed(package, LEGAL_PACKAGE_FIELDS, "legal package")
        if set(package) != LEGAL_PACKAGE_FIELDS:
            raise CivError("legal package is missing a required field")
        name = _string(package.get("name"), "legal package name")
        expected_resolution = "approved" if review_mode == PACKAGE_REVIEW_MODE else "risk-accepted"
        if package.get("resolution") != expected_resolution:
            raise CivError(f"legal package remains unresolved: {name}")
        concluded = _string(package.get("concluded_license"), "concluded licence")
        if review_mode == PACKAGE_REVIEW_MODE and concluded == "NOASSERTION":
            raise CivError(f"legal package has no concluded licence: {name}")
        if review_mode == GLOBAL_RISK_MODE and concluded != package.get("scanner_license"):
            raise CivError(f"risk-accepted package changed scanner licence: {name}")
        _string(package.get("evidence"), "legal package evidence")
        source_target = package.get("source_target")
        if source_target is not None:
            _target(source_target, "legal source_target")
    notices = _render_notices(packages)
    _write_text(output, notices, "third-party notices")
    return {
        "notice_sha256": file_sha256(output),
        "package_count": len(packages),
        "review_mode": review_mode,
    }


def build_legal_approval_document(
    review_path: Path,
    notices_path: Path,
    evidence_root: Path,
    output: Path,
    *,
    licence_targets: Sequence[str],
    source_targets: Sequence[str],
    authority: str,
    approved_on: str,
    source_statement: str,
) -> dict[str, object]:
    review = _mapping(read_json_file(review_path, "legal review"), "legal review")
    _closed(review, LEGAL_REVIEW_FIELDS, "legal review")
    if set(review) != LEGAL_REVIEW_FIELDS:
        raise CivError("legal review is missing a required field")
    review_mode = _string(review.get("review_mode"), "legal review_mode")
    if review_mode not in {PACKAGE_REVIEW_MODE, GLOBAL_RISK_MODE}:
        raise CivError("legal review_mode is not final")
    approval_id = _string(review.get("approval_id"), "legal approval_id")
    if not approval_id.startswith("human-"):
        raise CivError("legal approval_id must identify explicit human authority")
    packages = [
        _mapping(item, "legal package")
        for item in _sequence(review.get("packages"), "legal review packages")
    ]
    expected_notices = _render_notices(packages)
    if notices_path.read_text(encoding="utf-8") != expected_notices:
        raise CivError("third-party notices do not match the legal review")

    def identities(targets: Sequence[str], context: str) -> list[dict[str, str]]:
        records: list[dict[str, str]] = []
        for raw_target in sorted(set(targets)):
            target = _target(raw_target, context)
            path = evidence_root / Path(target)
            if not path.is_file():
                raise CivError(f"{context} does not exist: {target}")
            records.append({"sha256": file_sha256(path), "target": target})
        if not records:
            raise CivError(f"at least one {context} is required")
        return records

    unresolved_count = _non_negative_integer(
        review.get("unresolved_count"), "legal unresolved_count"
    )
    if DATE_PATTERN.fullmatch(approved_on) is None:
        raise CivError("legal approval date must use YYYY-MM-DD")
    approval = {
        "accepted_unresolved_count": unresolved_count,
        "approved_on": approved_on,
        "authority": _string(authority, "legal approval authority"),
        "contract": LEGAL_APPROVAL_CONTRACT,
        "decision": "approved" if review_mode == PACKAGE_REVIEW_MODE else "risk-accepted",
        "id": approval_id,
        "licence_artifacts": identities(licence_targets, "licence artifact"),
        "notices_sha256": file_sha256(notices_path),
        "review_mode": review_mode,
        "review_sha256": file_sha256(review_path),
        "risk_statement": (
            PACKAGE_REVIEW_STATEMENT
            if review_mode == PACKAGE_REVIEW_MODE
            else GLOBAL_RISK_STATEMENT
        ),
        "source_artifacts": identities(source_targets, "source artifact"),
        "source": _string(source_statement, "legal approval source"),
    }
    _write_text(output, f"{canonical_json(approval)}\n", "legal approval")
    return {
        "approval_sha256": file_sha256(output),
        "decision": approval["decision"],
        "review_mode": review_mode,
        "unresolved_count": unresolved_count,
    }


def _artifact_record(root: Path, declaration: Mapping[str, object]) -> dict[str, object]:
    _closed(declaration, ARTIFACT_DECLARATION_FIELDS, "artifact declaration")
    if set(declaration) != ARTIFACT_DECLARATION_FIELDS:
        raise CivError("artifact declaration must contain role, target, platform, and provenance")
    target = _target(declaration["target"])
    path = root / Path(target)
    if not path.is_file():
        raise CivError(f"release artifact does not exist: {target}")
    return {
        "byte_size": path.stat().st_size,
        "platform": _string(declaration["platform"], f"{target} platform"),
        "provenance": _string(declaration["provenance"], f"{target} provenance"),
        "role": _string(declaration["role"], f"{target} role"),
        "sha256": file_sha256(path),
        "target": target,
    }


def _validate_legal_review(
    path: Path,
    sbom_records: Sequence[Mapping[str, object]],
    evidence_root: Path,
) -> tuple[str, list[dict[str, object]], str, int]:
    review = _mapping(read_json_file(path, "legal review"), "legal review")
    _closed(review, LEGAL_REVIEW_FIELDS, "legal review")
    if review.get("contract") != LEGAL_REVIEW_CONTRACT:
        raise CivError(f"legal review contract must be '{LEGAL_REVIEW_CONTRACT}'")
    expected_sboms: list[dict[str, object]] = sorted(
        (
            {
                "package_count": _positive_integer(record["package_count"], "SBOM package_count"),
                "sha256": _sha256(record["sha256"], "SBOM sha256"),
            }
            for record in sbom_records
        ),
        key=lambda item: str(item["sha256"]),
    )
    if review.get("sboms") != expected_sboms:
        raise CivError("legal review does not bind the exact frozen SBOMs")
    sbom_paths = [
        evidence_root / Path(_target(record.get("target"), "legal SBOM target"))
        for record in sbom_records
    ]
    expected_packages, _ = _legal_package_records(sbom_paths)
    expected_by_key = {str(item["key"]): item for item in expected_packages}
    packages = [
        _mapping(item, "legal package")
        for item in _sequence(review.get("packages"), "legal review packages")
    ]
    review_mode = _string(review.get("review_mode"), "legal review_mode")
    if review_mode not in {PACKAGE_REVIEW_MODE, GLOBAL_RISK_MODE}:
        raise CivError("legal review_mode is not final")
    expected_count = sum(
        _positive_integer(item["package_count"], "SBOM package_count")
        for item in expected_sboms
    )
    if len(packages) != expected_count or len(expected_by_key) != expected_count:
        raise CivError("legal review package count does not cover every SBOM package")
    keys: set[str] = set()
    for package in packages:
        _closed(package, LEGAL_PACKAGE_FIELDS, "legal package")
        if set(package) != LEGAL_PACKAGE_FIELDS:
            raise CivError("legal package is missing a required field")
        key = _sha256(package["key"], "legal package key")
        if key in keys:
            raise CivError(f"duplicate legal package key: {key}")
        keys.add(key)
        expected_package = expected_by_key.get(key)
        if expected_package is None:
            raise CivError(f"legal package does not belong to a frozen SBOM: {key}")
        for field in (
            "sbom_sha256",
            "spdx_id",
            "name",
            "version",
            "scanner_license",
            "source_locator",
        ):
            if package[field] != expected_package[field]:
                raise CivError(f"legal package changed frozen {field}: {key}")
        expected_resolution = "approved" if review_mode == PACKAGE_REVIEW_MODE else "risk-accepted"
        if package.get("resolution") != expected_resolution:
            raise CivError(f"legal package remains unresolved: {package.get('name', key)}")
        concluded = _string(package.get("concluded_license"), "concluded licence")
        if review_mode == PACKAGE_REVIEW_MODE and concluded == "NOASSERTION":
            raise CivError(f"legal package has no concluded licence: {package.get('name', key)}")
        if review_mode == GLOBAL_RISK_MODE and concluded != package.get("scanner_license"):
            raise CivError(f"risk-accepted package changed scanner licence: {key}")
        _string(package.get("evidence"), "legal package evidence")
        source_target = package.get("source_target")
        if review_mode == PACKAGE_REVIEW_MODE and COPYLEFT_PATTERN.search(concluded):
            source = _target(source_target, "copyleft source_target")
            if not (evidence_root / Path(source)).is_file():
                raise CivError(f"copyleft source archive does not exist: {source}")
        elif source_target is not None:
            source = _target(source_target, "legal source_target")
            if not (evidence_root / Path(source)).is_file():
                raise CivError(f"legal source archive does not exist: {source}")
    unresolved_count = _non_negative_integer(
        review.get("unresolved_count"), "legal unresolved_count"
    )
    expected_unresolved = 0 if review_mode == PACKAGE_REVIEW_MODE else len(packages)
    if unresolved_count != expected_unresolved:
        raise CivError("legal review unresolved_count does not match review_mode")
    source_archives = sorted(
        _target(item, "legal source archive")
        for item in _sequence(review.get("source_archives"), "legal source_archives")
    )
    if len(source_archives) != len(set(source_archives)):
        raise CivError("legal source_archives must be unique")
    for target in source_archives:
        if not (evidence_root / Path(target)).is_file():
            raise CivError(f"legal source archive does not exist: {target}")
    approval_id = _string(review.get("approval_id"), "legal approval_id")
    if not approval_id.startswith("human-"):
        raise CivError("legal approval_id must identify explicit human authority")
    if keys != set(expected_by_key):
        raise CivError("legal review does not cover every frozen SBOM package")
    return approval_id, packages, review_mode, unresolved_count


def _legal_approval_artifacts(
    artifacts: Sequence[Mapping[str, object]], roles: set[str]
) -> list[dict[str, str]]:
    return sorted(
        (
            {
                "sha256": _sha256(item.get("sha256"), "legal approval artifact sha256"),
                "target": _target(item.get("target"), "legal approval artifact target"),
            }
            for item in artifacts
            if item.get("role") in roles
        ),
        key=lambda item: item["target"],
    )


def _validate_legal_approval(
    path: Path,
    *,
    approval_id: str,
    legal_review: Mapping[str, object],
    notices: Mapping[str, object],
    artifacts: Sequence[Mapping[str, object]],
    review_mode: str,
    unresolved_count: int,
) -> dict[str, str]:
    approval = _mapping(read_json_file(path, "legal approval"), "legal approval")
    _closed(approval, LEGAL_APPROVAL_FIELDS, "legal approval")
    if set(approval) != LEGAL_APPROVAL_FIELDS:
        raise CivError("legal approval is missing a required field")
    if approval.get("contract") != LEGAL_APPROVAL_CONTRACT:
        raise CivError(f"legal approval contract must be '{LEGAL_APPROVAL_CONTRACT}'")
    if approval.get("id") != approval_id:
        raise CivError("legal approval id does not match the package review")
    expected_decision = "approved" if review_mode == PACKAGE_REVIEW_MODE else "risk-accepted"
    if approval.get("decision") != expected_decision:
        raise CivError(f"legal approval decision must be '{expected_decision}'")
    if approval.get("review_mode") != review_mode:
        raise CivError("legal approval review_mode does not match the review")
    if approval.get("accepted_unresolved_count") != unresolved_count:
        raise CivError("legal approval does not accept the exact unresolved count")
    expected_statement = (
        PACKAGE_REVIEW_STATEMENT if review_mode == PACKAGE_REVIEW_MODE else GLOBAL_RISK_STATEMENT
    )
    if approval.get("risk_statement") != expected_statement:
        raise CivError("legal approval risk statement does not match the review mode")
    _string(approval.get("authority"), "legal approval authority")
    approved_on = _string(approval.get("approved_on"), "legal approval approved_on")
    if DATE_PATTERN.fullmatch(approved_on) is None:
        raise CivError("legal approval date must use YYYY-MM-DD")
    _string(approval.get("source"), "legal approval source")
    if approval.get("review_sha256") != legal_review.get("sha256"):
        raise CivError("legal approval does not bind the exact package review")
    if approval.get("notices_sha256") != notices.get("sha256"):
        raise CivError("legal approval does not bind the exact third-party notices")
    expected_licences = _legal_approval_artifacts(artifacts, {"licence"})
    expected_sources = _legal_approval_artifacts(
        artifacts, {"corresponding-source", "written-offer"}
    )
    if not expected_licences or approval.get("licence_artifacts") != expected_licences:
        raise CivError("legal approval does not bind every licence artifact")
    if not expected_sources or approval.get("source_artifacts") != expected_sources:
        raise CivError("legal approval does not bind every source artifact")
    return {"document_sha256": file_sha256(path), "id": approval_id}


def _architecture(value: object) -> dict[str, object]:
    architecture = _mapping(value, "architecture decision")
    _closed(architecture, ARCHITECTURE_FIELDS, "architecture decision")
    if set(architecture) != ARCHITECTURE_FIELDS:
        raise CivError("architecture decision is missing a required field")

    def platforms(field: str) -> list[str]:
        values = sorted(
            _string(item, f"architecture {field}")
            for item in _sequence(architecture[field], f"architecture {field}")
        )
        if not values or len(values) != len(set(values)):
            raise CivError(f"architecture {field} must contain unique platform names")
        return values

    container_platforms = platforms("container_platforms")
    if container_platforms != ["linux-amd64"]:
        raise CivError("the frozen container architecture must remain exactly linux-amd64")
    return {
        "advertised_participant_platforms": platforms("advertised_participant_platforms"),
        "approval": _approval(architecture["approval"], "architecture approval"),
        "container_platforms": container_platforms,
        "decision": _string(architecture["decision"], "architecture decision"),
        "viewer_platforms": platforms("viewer_platforms"),
    }


def _development_authority(value: object) -> dict[str, object]:
    authority = _mapping(value, "development authority")
    _closed(authority, DEVELOPMENT_AUTHORITY_FIELDS, "development authority")
    if set(authority) != DEVELOPMENT_AUTHORITY_FIELDS:
        raise CivError("development authority is missing a required field")
    datasets = sorted(
        _string(item, "development authority dataset")
        for item in _sequence(authority["datasets"], "development authority datasets")
    )
    if datasets != ["kashiwa", "reims"]:
        raise CivError("development authority must cover exactly kashiwa and reims")
    if authority["participant_distribution"] is not False:
        raise CivError("development authority must remain outside participant distribution")
    if authority["sealed_authority_included"] is not False:
        raise CivError("development authority must not include sealed scoring authority")
    return {
        "approval": _approval(authority["approval"], "development authority approval"),
        "datasets": datasets,
        "participant_distribution": False,
        "record_count": _positive_integer(authority["record_count"], "development record_count"),
        "sealed_authority_included": False,
        "set_sha256": _sha256(authority["set_sha256"], "development authority set_sha256"),
    }


def _participant_components(
    files: Sequence[Mapping[str, object]], manifest_sha256: str
) -> list[dict[str, object]]:
    grouped: dict[str, list[dict[str, object]]] = {}
    for item in files:
        target = _target(item.get("target"), "assembly component target")
        component = target.split("/", 1)[0]
        if component not in PARTICIPANT_COMPONENT_METADATA:
            raise CivError(f"assembly contains an unknown participant component: {component}")
        grouped.setdefault(component, []).append(
            {
                "byte_size": _non_negative_integer(
                    item.get("byte_size"), f"assembly component {target} byte_size"
                ),
                "sha256": _sha256(
                    item.get("sha256"), f"assembly component {target} sha256"
                ),
                "target": target,
            }
        )
    if set(grouped) != set(PARTICIPANT_COMPONENT_METADATA):
        missing = sorted(set(PARTICIPANT_COMPONENT_METADATA) - set(grouped))
        if missing:
            raise CivError(f"assembly is missing participant component: {missing[0]}")
        raise CivError("assembly participant component set changed")

    result: list[dict[str, object]] = []
    for name in sorted(grouped):
        records = sorted(grouped[name], key=lambda item: str(item["target"]))
        identity = "".join(
            f"{item['sha256']}  {item['target']}\n" for item in records
        ).encode("utf-8")
        role, platform = PARTICIPANT_COMPONENT_METADATA[name]
        result.append(
            {
                "file_count": len(records),
                "name": name,
                "platform": platform,
                "provenance": f"phase4-assembly:{manifest_sha256}",
                "required_disk_bytes": sum(
                    _non_negative_integer(item["byte_size"], "component byte_size")
                    for item in records
                ),
                "role": role,
                "set_sha256": sha256(identity).hexdigest(),
            }
        )
    return result


def _assembly_record(manifest_path: Path) -> dict[str, object]:
    audit = audit_assembly(manifest_path)
    manifest_sha256 = _sha256(audit.get("manifest_sha256"), "assembly manifest_sha256")
    if manifest_sha256 != ACCEPTED_ASSEMBLY_SHA256:
        raise CivError("assembly does not match the accepted Phase 4 manifest")
    document = _mapping(read_json_file(manifest_path, "assembly manifest"), "assembly manifest")
    if document.get("inventory_sha256") != ACCEPTED_INVENTORY_SHA256:
        raise CivError("assembly does not bind the accepted Phase 4 inventory")
    files = [
        _mapping(item, "assembly file")
        for item in _sequence(document.get("files"), "assembly files")
    ]
    archive = next(
        (
            item
            for item in files
            if item.get("sha256") == ACCEPTED_IMAGE_ARCHIVE_SHA256
            and item.get("byte_size") == ACCEPTED_IMAGE_ARCHIVE_BYTES
        ),
        None,
    )
    if archive is None:
        raise CivError("assembly does not contain the accepted container archive")
    return {
        "components": _participant_components(files, manifest_sha256),
        "file_count": _positive_integer(audit.get("file_count"), "assembly file_count"),
        "image": {
            "archive_byte_size": ACCEPTED_IMAGE_ARCHIVE_BYTES,
            "archive_sha256": ACCEPTED_IMAGE_ARCHIVE_SHA256,
            "id": ACCEPTED_IMAGE_ID,
            "name": ACCEPTED_IMAGE_NAME,
            "platform": "linux-amd64",
        },
        "inventory_sha256": ACCEPTED_INVENTORY_SHA256,
        "manifest_sha256": manifest_sha256,
        "release_id": _string(document.get("release_id"), "assembly release_id"),
        "required_disk_bytes": _positive_integer(
            audit.get("required_disk_bytes"), "assembly required_disk_bytes"
        ),
    }


def build_release_freeze(
    assembly_manifest: Path,
    evidence_root: Path,
    declaration_path: Path,
    output: Path,
) -> dict[str, object]:
    declaration = _mapping(
        read_json_file(declaration_path, "release declaration"), "release declaration"
    )
    _closed(declaration, DECLARATION_FIELDS, "release declaration")
    if set(declaration) != DECLARATION_FIELDS:
        raise CivError("release declaration is missing a required field")
    if declaration.get("contract") != DECLARATION_CONTRACT:
        raise CivError(f"release declaration contract must be '{DECLARATION_CONTRACT}'")
    source_commit = _string(declaration["source_commit"], "source_commit")
    if COMMIT_PATTERN.fullmatch(source_commit) is None or source_commit != ACCEPTED_SOURCE_COMMIT:
        raise CivError("release freeze must bind the accepted Phase 4 source commit")
    assembly = _assembly_record(assembly_manifest)
    architecture = _architecture(declaration["architecture"])
    development_authority = _development_authority(declaration["development_authority"])

    artifact_declarations = [
        _mapping(item, "artifact declaration")
        for item in _sequence(declaration["artifacts"], "release artifacts")
    ]
    artifacts = sorted(
        (_artifact_record(evidence_root, item) for item in artifact_declarations),
        key=lambda item: str(item["target"]),
    )
    targets = [str(item["target"]) for item in artifacts]
    if len(targets) != len(set(targets)):
        raise CivError("release artifact targets must be unique")
    roles = {str(item["role"]) for item in artifacts}
    for required_role in {
        "approval",
        "licence",
        "sbom",
        "third-party-notices",
    }:
        if required_role not in roles:
            raise CivError(f"release artifacts are missing required role '{required_role}'")

    sbom_declarations = [
        _mapping(item, "SBOM declaration")
        for item in _sequence(declaration["sboms"], "release SBOMs")
    ]
    sboms: list[dict[str, object]] = []
    for item in sbom_declarations:
        _closed(item, SBOM_DECLARATION_FIELDS, "SBOM declaration")
        if set(item) != SBOM_DECLARATION_FIELDS:
            raise CivError("SBOM declaration must contain subject and target")
        target = _target(item["target"], "SBOM target")
        artifact = next((record for record in artifacts if record["target"] == target), None)
        if artifact is None or artifact["role"] != "sbom":
            raise CivError(f"SBOM target is not declared as an SBOM artifact: {target}")
        spdx_document = _spdx_document(evidence_root / Path(target), f"SBOM {target}")
        subject = _string(item["subject"], f"SBOM {target} subject")
        namespace = _string(
            spdx_document.get("documentNamespace"), f"SBOM {target} namespace"
        )
        if not namespace.startswith(f"https://civ.example/sbom/{subject}/"):
            raise CivError(f"SBOM {target} is not deterministically normalized for {subject}")
        sboms.append(
            {
                "byte_size": artifact["byte_size"],
                "package_count": len(
                    _sequence(spdx_document["packages"], f"SBOM {target} packages")
                ),
                "sha256": artifact["sha256"],
                "spdx_version": "SPDX-2.3",
                "subject": subject,
                "target": target,
            }
        )
    sboms.sort(key=lambda item: str(item["subject"]))
    if len(sboms) != 2 or {item["subject"] for item in sboms} != {"container", "public-site"}:
        raise CivError("release freeze requires exactly container and public-site SBOMs")

    legal_target = _target(declaration["legal_review_target"], "legal review target")
    legal_approval_target = _target(
        declaration["legal_approval_target"], "legal approval target"
    )
    notices_target = _target(declaration["notices_target"], "notices target")
    legal_artifact = next((item for item in artifacts if item["target"] == legal_target), None)
    legal_approval_artifact = next(
        (item for item in artifacts if item["target"] == legal_approval_target), None
    )
    notices_artifact = next((item for item in artifacts if item["target"] == notices_target), None)
    if legal_artifact is None or legal_artifact["role"] != "legal-review":
        raise CivError("legal review must be declared as a legal-review artifact")
    if legal_approval_artifact is None or legal_approval_artifact["role"] != "approval":
        raise CivError("legal approval must be declared as an approval artifact")
    if notices_artifact is None or notices_artifact["role"] != "third-party-notices":
        raise CivError("notices target must be declared as a third-party-notices artifact")
    legal_approval_id, legal_packages, legal_review_mode, legal_unresolved_count = (
        _validate_legal_review(
        evidence_root / Path(legal_target), sboms, evidence_root
        )
    )
    if legal_review_mode == PACKAGE_REVIEW_MODE:
        for required_role in {"corresponding-source", "written-offer"}:
            if required_role not in roles:
                raise CivError(
                    "package-reviewed release artifacts are missing required role "
                    f"'{required_role}'"
                )
    elif "corresponding-source" not in roles:
        raise CivError("global risk acceptance must retain available source evidence")
    expected_notices = _render_notices(legal_packages)
    actual_notices = (evidence_root / Path(notices_target)).read_text(encoding="utf-8")
    if actual_notices != expected_notices:
        raise CivError("third-party notices do not match the approved legal package review")
    legal_approval = _validate_legal_approval(
        evidence_root / Path(legal_approval_target),
        approval_id=legal_approval_id,
        legal_review=legal_artifact,
        notices=notices_artifact,
        artifacts=artifacts,
        review_mode=legal_review_mode,
        unresolved_count=legal_unresolved_count,
    )
    approval_hashes = {
        str(_mapping(architecture["approval"], "architecture approval")["document_sha256"]),
        str(
            _mapping(
                development_authority["approval"], "development authority approval"
            )["document_sha256"]
        ),
        legal_approval["document_sha256"],
    }
    frozen_approval_hashes = {
        str(item["sha256"]) for item in artifacts if item["role"] == "approval"
    }
    missing_approvals = sorted(approval_hashes - frozen_approval_hashes)
    if missing_approvals:
        raise CivError(
            "release artifacts do not contain every human approval document: "
            f"{missing_approvals[0]}"
        )

    evidence_bytes = sum(
        _non_negative_integer(item["byte_size"], "artifact byte_size")
        for item in artifacts
    )
    freeze_document: dict[str, object] = {
        "architecture": architecture,
        "artifacts": artifacts,
        "assembly": assembly,
        "contract": CONTRACT,
        "development_authority": development_authority,
        "legal": {
            "approval": legal_approval,
            "notice_sha256": notices_artifact["sha256"],
            "notice_target": notices_target,
            "package_count": len(legal_packages),
            "review_mode": legal_review_mode,
            "review_sha256": legal_artifact["sha256"],
            "review_target": legal_target,
            "unresolved_count": legal_unresolved_count,
        },
        "recovery_notice": RECOVERY_NOTICE,
        "release_id": RELEASE_ID,
        "required_disk_bytes": _positive_integer(
            assembly["required_disk_bytes"], "assembly required_disk_bytes"
        )
        + evidence_bytes,
        "sboms": sboms,
        "source_commit": source_commit,
    }
    _write_text(output, f"{canonical_json(freeze_document)}\n", "release freeze manifest")
    checksum_lines = [f"{item['sha256']}  {item['target']}\n" for item in artifacts]
    checksum_lines.append(f"{file_sha256(output)}  {output.name}\n")
    _write_text(
        output.parent / "SHA256SUMS",
        "".join(sorted(checksum_lines, key=lambda line: line.split("  ", 1)[1])),
        "release checksum manifest",
    )
    return audit_release_freeze(output, assembly_manifest, evidence_root)


def audit_release_freeze(
    manifest_path: Path, assembly_manifest: Path, evidence_root: Path
) -> dict[str, object]:
    document = _mapping(read_json_file(manifest_path, "release freeze"), "release freeze")
    if document.get("contract") != CONTRACT:
        raise CivError(f"release freeze contract must be '{CONTRACT}'")
    require_closed_fields(document, kind="release freeze", expected=CONTRACT)
    if document.get("release_id") != RELEASE_ID:
        raise CivError(f"release freeze release_id must be '{RELEASE_ID}'")
    if document.get("source_commit") != ACCEPTED_SOURCE_COMMIT:
        raise CivError("release freeze source commit changed")
    assembly = _assembly_record(assembly_manifest)
    if document.get("assembly") != assembly:
        raise CivError("release freeze assembly identity changed")
    _architecture(document.get("architecture"))
    _development_authority(document.get("development_authority"))
    artifacts = [
        _mapping(item, "release artifact")
        for item in _sequence(document.get("artifacts"), "release artifacts")
    ]
    targets: list[str] = []
    for item in artifacts:
        target = _target(item.get("target"))
        targets.append(target)
        path = evidence_root / Path(target)
        if not path.is_file():
            raise CivError(f"release artifact does not exist: {target}")
        if item.get("sha256") != file_sha256(path) or item.get("byte_size") != path.stat().st_size:
            raise CivError(f"release artifact does not match freeze: {target}")
    if targets != sorted(targets) or len(targets) != len(set(targets)):
        raise CivError("release artifacts must be sorted and unique")
    sboms = [
        _mapping(item, "release SBOM")
        for item in _sequence(document.get("sboms"), "release SBOMs")
    ]
    legal = _mapping(document.get("legal"), "release legal record")
    legal_review_target = _target(legal.get("review_target"), "legal review target")
    legal_review_artifact = next(
        (item for item in artifacts if item.get("target") == legal_review_target), None
    )
    if legal_review_artifact is None or legal_review_artifact.get("role") != "legal-review":
        raise CivError("release legal review artifact is missing")
    legal_approval_record = _mapping(legal.get("approval"), "release legal approval")
    legal_approval_artifact = next(
        (
            item
            for item in artifacts
            if item.get("role") == "approval"
            and item.get("sha256") == legal_approval_record.get("document_sha256")
        ),
        None,
    )
    if legal_approval_artifact is None:
        raise CivError("release legal approval artifact is missing")
    approval_id, legal_packages, legal_review_mode, legal_unresolved_count = (
        _validate_legal_review(
        evidence_root / Path(legal_review_target), sboms, evidence_root
        )
    )
    if legal.get("review_mode") != legal_review_mode:
        raise CivError("release legal review_mode changed")
    if legal.get("unresolved_count") != legal_unresolved_count:
        raise CivError("release legal unresolved_count changed")
    notice_path = evidence_root / Path(_target(legal.get("notice_target"), "notice target"))
    if legal.get("notice_sha256") != file_sha256(notice_path):
        raise CivError("third-party notices changed")
    if notice_path.read_text(encoding="utf-8") != _render_notices(legal_packages):
        raise CivError("third-party notices do not match the approved legal package review")
    notices_artifact = next(
        (item for item in artifacts if item.get("target") == legal.get("notice_target")), None
    )
    if notices_artifact is None:
        raise CivError("release third-party notices artifact is missing")
    validated_approval = _validate_legal_approval(
        evidence_root / Path(str(legal_approval_artifact["target"])),
        approval_id=approval_id,
        legal_review=legal_review_artifact,
        notices=notices_artifact,
        artifacts=artifacts,
        review_mode=legal_review_mode,
        unresolved_count=legal_unresolved_count,
    )
    if validated_approval != legal_approval_record:
        raise CivError("release legal approval identity changed")
    required = _positive_integer(document.get("required_disk_bytes"), "required_disk_bytes")
    expected_required = _positive_integer(
        assembly["required_disk_bytes"], "assembly required_disk_bytes"
    ) + sum(
        _non_negative_integer(item.get("byte_size"), "artifact byte_size") for item in artifacts
    )
    if required != expected_required:
        raise CivError("release freeze required_disk_bytes is inconsistent")
    checksum_path = manifest_path.parent / "SHA256SUMS"
    if not checksum_path.is_file():
        raise CivError("release checksum manifest does not exist")
    expected_lines = [f"{item['sha256']}  {item['target']}\n" for item in artifacts]
    expected_lines.append(f"{file_sha256(manifest_path)}  {manifest_path.name}\n")
    if checksum_path.read_text(encoding="utf-8") != "".join(
        sorted(expected_lines, key=lambda line: line.split("  ", 1)[1])
    ):
        raise CivError("release checksum manifest does not match")
    serialized = manifest_path.read_text(encoding="utf-8")
    if ABSOLUTE_PATH_PATTERN.search(serialized):
        raise CivError("release freeze contains an absolute host path")
    return {
        "artifact_count": len(artifacts),
        "manifest_sha256": file_sha256(manifest_path),
        "package_count": sum(
            _positive_integer(item["package_count"], "SBOM package_count")
            for item in sboms
        ),
        "required_disk_bytes": required,
        "valid": True,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Prepare, build, and audit the Phase 5 release freeze"
    )
    commands = parser.add_subparsers(dest="command", required=True)
    normalize = commands.add_parser("normalize-spdx")
    normalize.add_argument("source", type=Path)
    normalize.add_argument("output", type=Path)
    normalize.add_argument("--subject", required=True)
    normalize.add_argument("--subject-sha256", required=True)
    normalize.add_argument("--created", required=True)
    legal = commands.add_parser("legal-template")
    legal.add_argument("sboms", nargs="+", type=Path)
    legal.add_argument("--output", required=True, type=Path)
    legal.add_argument("--notices", required=True, type=Path)
    accept_risk = commands.add_parser("accept-global-risk")
    accept_risk.add_argument("review", type=Path)
    accept_risk.add_argument("--output", required=True, type=Path)
    accept_risk.add_argument("--approval-id", required=True)
    accept_risk.add_argument("--source", action="append", default=[])
    notices = commands.add_parser("render-notices")
    notices.add_argument("review", type=Path)
    notices.add_argument("--output", required=True, type=Path)
    approval = commands.add_parser("legal-approval")
    approval.add_argument("review", type=Path)
    approval.add_argument("notices", type=Path)
    approval.add_argument("evidence_root", type=Path)
    approval.add_argument("--output", required=True, type=Path)
    approval.add_argument("--licence", action="append", default=[])
    approval.add_argument("--source", action="append", default=[])
    approval.add_argument("--authority", required=True)
    approval.add_argument("--approved-on", required=True)
    approval.add_argument("--source-statement", required=True)
    build = commands.add_parser("build")
    build.add_argument("assembly", type=Path)
    build.add_argument("evidence_root", type=Path)
    build.add_argument("declaration", type=Path)
    build.add_argument("output", type=Path)
    audit = commands.add_parser("audit")
    audit.add_argument("manifest", type=Path)
    audit.add_argument("assembly", type=Path)
    audit.add_argument("evidence_root", type=Path)
    return parser


def main(argv: Sequence[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "normalize-spdx":
            result = normalize_spdx(
                args.source,
                args.output,
                subject=args.subject,
                subject_sha256=args.subject_sha256,
                created=args.created,
            )
        elif args.command == "legal-template":
            result = build_legal_review_template(args.sboms, args.output, args.notices)
        elif args.command == "accept-global-risk":
            result = accept_global_legal_risk(
                args.review,
                args.output,
                approval_id=args.approval_id,
                source_archives=args.source,
            )
        elif args.command == "render-notices":
            result = render_legal_notices(args.review, args.output)
        elif args.command == "legal-approval":
            result = build_legal_approval_document(
                args.review,
                args.notices,
                args.evidence_root,
                args.output,
                licence_targets=args.licence,
                source_targets=args.source,
                authority=args.authority,
                approved_on=args.approved_on,
                source_statement=args.source_statement,
            )
        elif args.command == "build":
            result = build_release_freeze(
                args.assembly, args.evidence_root, args.declaration, args.output
            )
        else:
            result = audit_release_freeze(args.manifest, args.assembly, args.evidence_root)
    except CivError as error:
        print(f"civ release-freeze: {error}", file=sys.stderr)
        raise SystemExit(2) from error
    print(canonical_json(result))


if __name__ == "__main__":
    main()
