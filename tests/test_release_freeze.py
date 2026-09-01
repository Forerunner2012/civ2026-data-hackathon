from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import civ_workshop.release_freeze as freeze_module
from civ_workshop.artifacts import canonical_json, file_sha256
from civ_workshop.contracts import STABLE_FIELDS
from civ_workshop.errors import CivError
from civ_workshop.release_freeze import (
    accept_global_legal_risk,
    audit_release_freeze,
    build_legal_approval_document,
    build_legal_review_template,
    build_release_freeze,
    normalize_spdx,
    render_legal_notices,
)


def _write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"{canonical_json(value)}\n", encoding="utf-8", newline="\n")


def _raw_spdx(
    path: Path,
    *,
    namespace: str,
    created: str,
    packages: list[dict[str, object]],
) -> None:
    _write_json(
        path,
        {
            "SPDXID": "SPDXRef-DOCUMENT",
            "creationInfo": {"created": created, "creators": ["Tool: fixture-1.0"]},
            "dataLicense": "CC0-1.0",
            "documentNamespace": namespace,
            "name": path.stem,
            "packages": packages,
            "relationships": [
                {
                    "relatedSpdxElement": package["SPDXID"],
                    "relationshipType": "DESCRIBES",
                    "spdxElementId": "SPDXRef-DOCUMENT",
                }
                for package in reversed(packages)
            ],
            "spdxVersion": "SPDX-2.3",
        },
    )


def _package(
    identifier: str,
    name: str,
    version: str,
    license_declared: str,
    purl: str,
) -> dict[str, object]:
    return {
        "SPDXID": identifier,
        "downloadLocation": "NOASSERTION",
        "externalRefs": [
            {
                "referenceCategory": "PACKAGE-MANAGER",
                "referenceLocator": purl,
                "referenceType": "purl",
            }
        ],
        "filesAnalyzed": False,
        "licenseConcluded": "NOASSERTION",
        "licenseDeclared": license_declared,
        "name": name,
        "versionInfo": version,
    }


def test_spdx_normalization_removes_tool_time_and_namespace_nondeterminism(
    tmp_path: Path,
) -> None:
    packages = [
        _package("SPDXRef-Package-z", "zeta", "2", "MIT", "pkg:pypi/zeta@2"),
        _package("SPDXRef-Package-a", "alpha", "1", "Apache-2.0", "pkg:pypi/alpha@1"),
    ]
    first_raw = tmp_path / "first-raw.json"
    second_raw = tmp_path / "second-raw.json"
    _raw_spdx(
        first_raw,
        namespace="https://random.invalid/one",
        created="2026-08-30T10:00:00Z",
        packages=packages,
    )
    _raw_spdx(
        second_raw,
        namespace="https://random.invalid/two",
        created="2026-08-30T11:00:00Z",
        packages=list(reversed(packages)),
    )
    first = tmp_path / "first.json"
    second = tmp_path / "second.json"

    first_result = normalize_spdx(
        first_raw,
        first,
        subject="public-site",
        subject_sha256="1" * 64,
        created="2026-08-30T00:00:00Z",
    )
    second_result = normalize_spdx(
        second_raw,
        second,
        subject="public-site",
        subject_sha256="1" * 64,
        created="2026-08-30T00:00:00Z",
    )

    assert first.read_bytes() == second.read_bytes()
    assert first_result == second_result
    document = json.loads(first.read_text(encoding="utf-8"))
    assert document["documentNamespace"] == (
        "https://civ.example/sbom/public-site/" + "1" * 64
    )
    assert [item["name"] for item in document["packages"]] == ["alpha", "zeta"]


def _release_fixture(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> tuple[Path, Path, Path]:
    assembly = tmp_path / "assembly" / "attendee-kit-assembly.json"
    assembly_files = []
    for component in freeze_module.PARTICIPANT_COMPONENT_METADATA:
        if component == "container":
            assembly_files.append(
                {
                    "byte_size": freeze_module.ACCEPTED_IMAGE_ARCHIVE_BYTES,
                    "sha256": freeze_module.ACCEPTED_IMAGE_ARCHIVE_SHA256,
                    "target": "container/candidate.tar",
                }
            )
        else:
            target = component if "." in component else f"{component}/fixture"
            assembly_files.append(
                {"byte_size": 1, "sha256": "a" * 64, "target": target}
            )
    _write_json(
        assembly,
        {
            "files": assembly_files,
            "inventory_sha256": freeze_module.ACCEPTED_INVENTORY_SHA256,
            "release_id": "civ-2026-phase4-attendee-kit-v1",
        },
    )
    monkeypatch.setattr(
        freeze_module,
        "audit_assembly",
        lambda _: {
            "file_count": 3225,
            "manifest_sha256": freeze_module.ACCEPTED_ASSEMBLY_SHA256,
            "required_disk_bytes": 1_307_178_032,
            "valid": True,
        },
    )

    evidence = tmp_path / "evidence"
    raw_container = tmp_path / "raw-container.json"
    raw_site = tmp_path / "raw-site.json"
    _raw_spdx(
        raw_container,
        namespace="https://random.invalid/container",
        created="2026-08-30T10:00:00Z",
        packages=[
            _package(
                "SPDXRef-Package-container",
                "container-dependency",
                "1.0",
                "MPL-2.0",
                "pkg:generic/container-dependency@1.0",
            )
        ],
    )
    _raw_spdx(
        raw_site,
        namespace="https://random.invalid/site",
        created="2026-08-30T10:00:00Z",
        packages=[
            _package(
                "SPDXRef-Package-site",
                "site-dependency",
                "2.0",
                "MIT",
                "pkg:npm/site-dependency@2.0",
            )
        ],
    )
    container_sbom = evidence / "sbom/container.spdx.json"
    site_sbom = evidence / "sbom/site.spdx.json"
    normalize_spdx(
        raw_container,
        container_sbom,
        subject="container",
        subject_sha256="2" * 64,
        created="2026-08-30T00:00:00Z",
    )
    normalize_spdx(
        raw_site,
        site_sbom,
        subject="public-site",
        subject_sha256="3" * 64,
        created="2026-08-30T00:00:00Z",
    )

    legal_review = evidence / "legal/review.json"
    notices = evidence / "legal/THIRD-PARTY-NOTICES.md"
    build_legal_review_template([container_sbom, site_sbom], legal_review, notices)
    review: dict[str, Any] = json.loads(legal_review.read_text(encoding="utf-8"))
    source = evidence / "source/container-dependency.tar.gz"
    source.parent.mkdir(parents=True)
    source.write_bytes(b"exact corresponding source")
    for package in review["packages"]:
        package["concluded_license"] = package["scanner_license"]
        package["evidence"] = "human legal review fixture"
        package["resolution"] = "approved"
        package["source_target"] = (
            "source/container-dependency.tar.gz"
            if package["scanner_license"] == "MPL-2.0"
            else None
        )
    review["approval_id"] = "human-legal-fixture"
    review["review_mode"] = freeze_module.PACKAGE_REVIEW_MODE
    review["source_archives"] = ["source/container-dependency.tar.gz"]
    review["unresolved_count"] = 0
    _write_json(legal_review, review)
    render_legal_notices(legal_review, notices)

    static_files = {
        "approvals/architecture.json": b"architecture approval",
        "approvals/development.json": b"development approval",
        "legal/LICENSE.txt": b"licence text",
        "legal/SOURCE-OFFER.md": b"written source offer",
    }
    for relative, content in static_files.items():
        path = evidence / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
    architecture_hash = file_sha256(evidence / "approvals/architecture.json")
    development_hash = file_sha256(evidence / "approvals/development.json")
    legal_approval = evidence / "approvals/legal.json"
    _write_json(
        legal_approval,
        {
            "accepted_unresolved_count": 0,
            "approved_on": "2026-08-30",
            "authority": "fixture reviewer",
            "contract": freeze_module.LEGAL_APPROVAL_CONTRACT,
            "decision": "approved",
            "id": "human-legal-fixture",
            "licence_artifacts": [
                {
                    "sha256": file_sha256(evidence / "legal/LICENSE.txt"),
                    "target": "legal/LICENSE.txt",
                }
            ],
            "notices_sha256": file_sha256(notices),
            "review_sha256": file_sha256(legal_review),
            "review_mode": freeze_module.PACKAGE_REVIEW_MODE,
            "risk_statement": freeze_module.PACKAGE_REVIEW_STATEMENT,
            "source_artifacts": [
                {
                    "sha256": file_sha256(evidence / "legal/SOURCE-OFFER.md"),
                    "target": "legal/SOURCE-OFFER.md",
                },
                {
                    "sha256": file_sha256(source),
                    "target": "source/container-dependency.tar.gz",
                },
            ],
            "source": "explicit fixture review decision",
        },
    )

    declarations = [
        ("approval", "approvals/architecture.json", "all", "human architecture decision"),
        ("approval", "approvals/development.json", "organizer-only", "human authority"),
        ("approval", "approvals/legal.json", "all", "human legal decision"),
        ("licence", "legal/LICENSE.txt", "all", "fixture licence archive"),
        ("legal-review", "legal/review.json", "organizer-only", "human package review"),
        (
            "third-party-notices",
            "legal/THIRD-PARTY-NOTICES.md",
            "all",
            "generated from approved package review",
        ),
        ("written-offer", "legal/SOURCE-OFFER.md", "all", "human-approved source offer"),
        ("sbom", "sbom/container.spdx.json", "linux-amd64", "fixture SPDX tool"),
        ("sbom", "sbom/site.spdx.json", "all", "fixture SPDX tool"),
        (
            "corresponding-source",
            "source/container-dependency.tar.gz",
            "all",
            "fixture source archive",
        ),
    ]
    declaration = tmp_path / "declaration.json"
    _write_json(
        declaration,
        {
            "architecture": {
                "advertised_participant_platforms": ["windows-amd64-host"],
                "approval": {
                    "document_sha256": architecture_hash,
                    "id": "human-architecture-fixture",
                },
                "container_platforms": ["linux-amd64"],
                "decision": "single container architecture on an approved host",
                "viewer_platforms": ["windows-amd64"],
            },
            "artifacts": [
                {"platform": platform, "provenance": provenance, "role": role, "target": target}
                for role, target, platform, provenance in declarations
            ],
            "contract": freeze_module.DECLARATION_CONTRACT,
            "development_authority": {
                "approval": {
                    "document_sha256": development_hash,
                    "id": "human-development-fixture",
                },
                "datasets": ["reims", "kashiwa"],
                "participant_distribution": False,
                "record_count": 24,
                "sealed_authority_included": False,
                "set_sha256": "5" * 64,
            },
            "legal_review_target": "legal/review.json",
            "legal_approval_target": "approvals/legal.json",
            "notices_target": "legal/THIRD-PARTY-NOTICES.md",
            "sboms": [
                {"subject": "container", "target": "sbom/container.spdx.json"},
                {"subject": "public-site", "target": "sbom/site.spdx.json"},
            ],
            "source_commit": freeze_module.ACCEPTED_SOURCE_COMMIT,
        },
    )
    return assembly, evidence, declaration


def test_global_risk_acceptance_preserves_unresolved_sbom_facts(
    tmp_path: Path,
) -> None:
    raw = tmp_path / "raw.json"
    _raw_spdx(
        raw,
        namespace="https://random.invalid/risk",
        created="2026-08-30T10:00:00Z",
        packages=[
            _package(
                "SPDXRef-Package-risk",
                "unasserted-dependency",
                "1.0",
                "NOASSERTION",
                "pkg:generic/unasserted-dependency@1.0",
            )
        ],
    )
    sbom = tmp_path / "sbom.json"
    normalize_spdx(
        raw,
        sbom,
        subject="container",
        subject_sha256="2" * 64,
        created="2026-08-30T00:00:00Z",
    )
    pending = tmp_path / "pending.json"
    build_legal_review_template([sbom], pending, tmp_path / "pending-notices.md")
    accepted = tmp_path / "accepted.json"

    result = accept_global_legal_risk(
        pending,
        accepted,
        approval_id="human-risk-fixture",
    )
    notices = tmp_path / "notices.md"
    notice_result = render_legal_notices(accepted, notices)

    review = json.loads(accepted.read_text(encoding="utf-8"))
    assert result["noassertion_count"] == 1
    assert result["unresolved_count"] == 1
    assert review["review_mode"] == freeze_module.GLOBAL_RISK_MODE
    assert review["packages"][0]["resolution"] == "risk-accepted"
    assert review["packages"][0]["concluded_license"] == "NOASSERTION"
    assert notice_result["review_mode"] == freeze_module.GLOBAL_RISK_MODE


def test_pending_legal_template_blocks_release_freeze(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    assembly, evidence, declaration = _release_fixture(tmp_path, monkeypatch)
    review_path = evidence / "legal/review.json"
    review = json.loads(review_path.read_text(encoding="utf-8"))
    review["packages"][0]["resolution"] = "pending"
    review["unresolved_count"] = 1
    _write_json(review_path, review)

    with pytest.raises(CivError, match="remains unresolved"):
        render_legal_notices(review_path, tmp_path / "pending-notices.md")

    with pytest.raises(CivError, match="remains unresolved"):
        build_release_freeze(
            assembly, evidence, declaration, tmp_path / "freeze/release-freeze.json"
        )


def test_release_freeze_is_deterministic_closed_and_detects_mutation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    assembly, evidence, declaration = _release_fixture(tmp_path, monkeypatch)
    first = tmp_path / "first/release-freeze.json"
    second = tmp_path / "second/release-freeze.json"

    first_result = build_release_freeze(assembly, evidence, declaration, first)
    second_result = build_release_freeze(assembly, evidence, declaration, second)

    assert first.read_bytes() == second.read_bytes()
    assert (first.parent / "SHA256SUMS").read_bytes() == (
        second.parent / "SHA256SUMS"
    ).read_bytes()
    assert first_result == second_result
    document = json.loads(first.read_text(encoding="utf-8"))
    assert set(document) == STABLE_FIELDS[freeze_module.CONTRACT]
    assert document["assembly"]["manifest_sha256"] == freeze_module.ACCEPTED_ASSEMBLY_SHA256
    assert {item["name"] for item in document["assembly"]["components"]} == set(
        freeze_module.PARTICIPANT_COMPONENT_METADATA
    )
    assert document["legal"]["unresolved_count"] == 0
    assert document["development_authority"]["participant_distribution"] is False
    assert str(tmp_path).lower() not in first.read_text(encoding="utf-8").lower()
    assert audit_release_freeze(first, assembly, evidence) == first_result

    (evidence / "legal/LICENSE.txt").write_bytes(b"changed")
    with pytest.raises(CivError, match="does not match freeze"):
        audit_release_freeze(first, assembly, evidence)


def test_release_freeze_accepts_explicit_global_legal_risk(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    assembly, evidence, declaration = _release_fixture(tmp_path, monkeypatch)
    review_path = evidence / "legal/review.json"
    review = json.loads(review_path.read_text(encoding="utf-8"))
    review["approval_id"] = None
    review["review_mode"] = "pending"
    review["unresolved_count"] = len(review["packages"])
    _write_json(review_path, review)
    accept_global_legal_risk(
        review_path,
        review_path,
        approval_id="human-risk-fixture",
    )
    notices = evidence / "legal/THIRD-PARTY-NOTICES.md"
    render_legal_notices(review_path, notices)
    approval_path = evidence / "approvals/legal.json"
    build_legal_approval_document(
        review_path,
        notices,
        evidence,
        approval_path,
        licence_targets=["legal/LICENSE.txt"],
        source_targets=[
            "legal/SOURCE-OFFER.md",
            "source/container-dependency.tar.gz",
        ],
        authority="fixture reviewer",
        approved_on="2026-09-01",
        source_statement="explicit fixture global risk decision",
    )

    result = build_release_freeze(
        assembly, evidence, declaration, tmp_path / "freeze/release-freeze.json"
    )
    document = json.loads(
        (tmp_path / "freeze/release-freeze.json").read_text(encoding="utf-8")
    )

    assert result["valid"] is True
    assert document["legal"]["review_mode"] == freeze_module.GLOBAL_RISK_MODE
    assert document["legal"]["unresolved_count"] == len(review["packages"])


def test_release_freeze_rejects_unfrozen_approval_document(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    assembly, evidence, declaration = _release_fixture(tmp_path, monkeypatch)
    document = json.loads(declaration.read_text(encoding="utf-8"))
    document["architecture"]["approval"]["document_sha256"] = "9" * 64
    _write_json(declaration, document)

    with pytest.raises(CivError, match="every human approval document"):
        build_release_freeze(
            assembly, evidence, declaration, tmp_path / "freeze/release-freeze.json"
        )


def test_release_freeze_rejects_legal_approval_for_another_review(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    assembly, evidence, declaration = _release_fixture(tmp_path, monkeypatch)
    approval_path = evidence / "approvals/legal.json"
    approval = json.loads(approval_path.read_text(encoding="utf-8"))
    approval["review_sha256"] = "9" * 64
    _write_json(approval_path, approval)

    with pytest.raises(CivError, match="does not bind the exact package review"):
        build_release_freeze(
            assembly, evidence, declaration, tmp_path / "freeze/release-freeze.json"
        )


def test_release_freeze_rejects_missing_participant_component(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    assembly, evidence, declaration = _release_fixture(tmp_path, monkeypatch)
    document = json.loads(assembly.read_text(encoding="utf-8"))
    document["files"] = [
        item for item in document["files"] if item["target"] != "templates/fixture"
    ]
    _write_json(assembly, document)

    with pytest.raises(CivError, match="missing participant component: templates"):
        build_release_freeze(
            assembly, evidence, declaration, tmp_path / "freeze/release-freeze.json"
        )
