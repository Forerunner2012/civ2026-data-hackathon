from __future__ import annotations

import json
from collections import Counter
from hashlib import sha256
from pathlib import Path
from typing import Any

import pytest

import civ_workshop.kit_inventory as inventory_module
from civ_workshop.artifacts import canonical_json, file_sha256
from civ_workshop.contracts import STABLE_FIELDS
from civ_workshop.data_products import (
    audit_participant_set,
    build_data_product,
    build_participant_set,
)
from civ_workshop.errors import CivError
from civ_workshop.kit_inventory import audit_kit_inventory, build_kit_inventory
from tests.helpers import write_micro_bag

REPOSITORY = Path(__file__).parents[1]


def _write_recipe(path: Path, source: Path, source_id: str, dataset: str, split: str) -> None:
    recipe = {
        "contract": "civ.data-product-recipe/v1",
        "recipe_id": f"{source_id}-signals-v1",
        "version": 1,
        "product_name": f"{source_id}-signals.mcap",
        "source": {"id": source_id, "sha256": sha256(source.read_bytes()).hexdigest()},
        "dataset": dataset,
        "split": split,
        "topics": ["/micro/signal"],
        "license": {"name": "test permission", "url": None},
        "attribution": "Synthetic CIV inventory fixture.",
        "rights_scope": "Test-only redistribution.",
        "modifications": ["Filtered to the explicit signal topic."],
    }
    path.write_text(json.dumps(recipe) + "\n", encoding="utf-8")


def _accepted_fixture(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> tuple[Path, list[Path]]:
    products = tmp_path / "products"
    manifests: list[Path] = []
    roles: Counter[tuple[str, str]] = Counter()
    for index in range(13):
        dataset = "kashiwa" if index < 8 else "reims"
        split = "warmup" if index == 0 else "development"
        roles[(dataset, split)] += 1
        source = tmp_path / f"source-{index}.mcap"
        recipe = tmp_path / f"recipe-{index}.json"
        write_micro_bag(source)
        _write_recipe(recipe, source, f"fixture-{index:02d}", dataset, split)
        result = build_data_product(source, recipe, products)
        manifests.append(products / str(result["manifest"]))
    set_path = products / "participant-products.json"
    built = build_participant_set(manifests, set_path, "fixture-participant-set")
    audit = audit_participant_set(set_path)
    monkeypatch.setattr(inventory_module, "ACCEPTED_PRODUCT_SET_SHA256", built["manifest_sha256"])
    monkeypatch.setattr(inventory_module, "ACCEPTED_PRODUCT_SET_RELEASE", "fixture-participant-set")
    monkeypatch.setattr(
        inventory_module, "ACCEPTED_REQUIRED_DISK_BYTES", built["required_disk_bytes"]
    )
    monkeypatch.setattr(inventory_module, "ACCEPTED_MESSAGE_COUNT", audit["message_count"])
    monkeypatch.setattr(inventory_module, "ACCEPTED_ROLES", roles)

    plotjuggler = tmp_path / "PlotJuggler-test.exe"
    plotjuggler.write_bytes(b"pinned PlotJuggler fixture")
    lichtblick = tmp_path / "lichtblick-test.exe"
    lichtblick.write_bytes(b"pinned Lichtblick fixture")
    viewers = [plotjuggler, lichtblick]
    monkeypatch.setattr(
        inventory_module,
        "VIEWER_ASSETS",
        {
            viewer.name: {
                "byte_size": viewer.stat().st_size,
                "platform": "windows-amd64",
                "sha256": sha256(viewer.read_bytes()).hexdigest(),
            }
            for viewer in viewers
        },
    )
    return set_path, viewers


def _document(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def test_inventory_is_deterministic_closed_and_does_not_copy_external_inputs(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    set_path, viewers = _accepted_fixture(tmp_path, monkeypatch)
    first_path = tmp_path / "first" / "participant-kit.json"
    second_path = tmp_path / "second" / "participant-kit.json"
    commit = "1" * 40

    first = build_kit_inventory(set_path, REPOSITORY, viewers, first_path, source_commit=commit)
    second = build_kit_inventory(set_path, REPOSITORY, viewers, second_path, source_commit=commit)

    assert first_path.read_bytes() == second_path.read_bytes()
    assert (first_path.parent / "checksums" / "SHA256SUMS").read_bytes() == (
        second_path.parent / "checksums" / "SHA256SUMS"
    ).read_bytes()
    assert first == second
    generated = sorted(
        path.relative_to(first_path.parent).as_posix()
        for path in first_path.parent.rglob("*")
        if path.is_file()
    )
    assert generated == [
        "checksums/SHA256SUMS",
        "participant-kit.json",
    ]
    document = _document(first_path)
    assert document["contract"] == "civ.participant-kit-inventory/v1"
    assert document["content_profile"] == "signals-only"
    assert document["context_packs"] == []
    assert document["product_set"]["product_count"] == 13
    assert document["tool"]["source_commit"] == commit
    assert (
        document["container_candidate"]["image_digest"] == inventory_module.CONTAINER_IMAGE_DIGEST
    )
    assert str(tmp_path).lower() not in first_path.read_text(encoding="utf-8").lower()
    assert set(document) == STABLE_FIELDS["civ.participant-kit-inventory/v1"]
    assert audit_kit_inventory(first_path)["valid"] is True


def test_inventory_checksum_manifest_covers_products_manifests_and_tracked_assets(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    set_path, viewers = _accepted_fixture(tmp_path, monkeypatch)
    output = tmp_path / "kit" / "participant-kit.json"
    build_kit_inventory(set_path, REPOSITORY, viewers, output, source_commit="2" * 40)

    document = _document(output)
    checksums = (output.parent / "checksums" / "SHA256SUMS").read_text(encoding="utf-8")
    lines = checksums.splitlines()
    assert lines == sorted(lines, key=lambda line: line.split("  ", 1)[1])
    assert len(lines) == (
        13 * 2
        + 1
        + len(inventory_module.TRACKED_ASSETS)
        + len(viewers)
        + 2  # lockfile and inventory
    )
    for product in document["product_set"]["products"]:
        assert f"{product['sha256']}  {product['name']}" in lines
        assert f"{product['manifest_sha256']}  {product['manifest']}" in lines
    for asset in document["tracked_assets"]:
        assert f"{asset['sha256']}  {asset['path']}" in lines
    guide_targets = {asset["path"] for asset in document["tracked_assets"]}
    assert {
        "docs/setup.md",
        "docs/runtime-requirements.md",
        "docs/extension.md",
        "docs/submission-fields.md",
    } <= guide_targets
    submission_guide = next(
        asset
        for asset in document["tracked_assets"]
        if asset["path"] == "docs/submission-fields.md"
    )
    assert submission_guide["role"] == "participant-instructions"
    template_targets = {
        asset["path"]
        for asset in document["tracked_assets"]
        if asset["role"] == "submission-template"
    }
    assert template_targets == {
        "templates/submission/README.md",
        "templates/submission/detector.yaml",
        "templates/submission/figure.svg",
        "templates/submission/report.md",
        "templates/submission/reproduce.ps1",
        "templates/submission/reproduce.sh",
    }


def test_inventory_rejects_context_without_separate_human_approval(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    set_path, viewers = _accepted_fixture(tmp_path, monkeypatch)

    with pytest.raises(CivError, match="manifest, size, and separate approval"):
        build_kit_inventory(
            set_path,
            REPOSITORY,
            viewers,
            tmp_path / "kit" / "participant-kit.json",
            source_commit="3" * 40,
            context_packs=[
                {
                    "name": "camera-context",
                    "manifest": "context/camera.json",
                    "manifest_sha256": "4" * 64,
                    "required_disk_bytes": 100,
                }
            ],
        )


def test_inventory_records_explicit_camera_context_set(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    set_path, viewers = _accepted_fixture(tmp_path, monkeypatch)
    products = []
    for index in range(13):
        dataset = "kashiwa" if index < 8 else "reims"
        products.append(
            {
                "dataset": dataset,
                "source_id": f"source-{index}",
                "split": "warmup" if index == 0 else "development",
            }
        )
    context_set = tmp_path / "context" / "camera-context-products.json"
    context_set.parent.mkdir()
    context_document = {
        "approval": {"id": "matthieu-carre-approval", "document_sha256": "a" * 64},
        "contract": "civ.camera-context-set/v1",
        "products": products,
        "release_id": "civ-2026-phase5-camera-context-v1",
        "required_disk_bytes": 123,
    }
    context_set.write_text(
        f"{canonical_json(context_document)}\n",
        encoding="utf-8",
        newline="\n",
    )
    output = tmp_path / "kit" / "participant-kit.json"

    build_kit_inventory(
        set_path,
        REPOSITORY,
        viewers,
        output,
        source_commit="7" * 40,
        context_set_path=context_set,
    )

    document = _document(output)
    assert document["release_id"] == "civ-2026-phase5-camera-context-participant-kit-v2"
    assert document["content_profile"] == "signals-plus-camera-context"
    assert document["layout"]["directories"][2] == "context"
    assert document["context_packs"] == [
        {
            "approval": {"id": "matthieu-carre-approval", "sha256": "a" * 64},
            "manifest": "context/camera-context-products.json",
            "manifest_sha256": file_sha256(context_set),
            "name": "camera-context-v1",
            "required_disk_bytes": 123,
        }
    ]
    assert audit_kit_inventory(output)["context_pack_count"] == 1


def test_inventory_rejects_unpinned_or_changed_viewer(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    set_path, viewers = _accepted_fixture(tmp_path, monkeypatch)
    viewers[0].write_bytes(b"changed")

    with pytest.raises(CivError, match="does not match its accepted pin"):
        build_kit_inventory(
            set_path,
            REPOSITORY,
            viewers,
            tmp_path / "kit" / "participant-kit.json",
            source_commit="5" * 40,
        )


def test_inventory_records_recovery_caveat_without_external_parent_locations(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    set_path, viewers = _accepted_fixture(tmp_path, monkeypatch)
    output = tmp_path / "kit" / "participant-kit.json"
    build_kit_inventory(set_path, REPOSITORY, viewers, output, source_commit="6" * 40)

    notice = _document(output)["recovery_notice"]
    assert notice == inventory_module.RECOVERY_NOTICE
    assert "does not prove that truncation lost no records" in notice
    assert ":\\" not in notice and "/bags/" not in notice.lower()


def test_inventory_rejects_incomplete_viewer_pair(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    set_path, viewers = _accepted_fixture(tmp_path, monkeypatch)

    with pytest.raises(CivError, match="PlotJuggler and Lichtblick must be staged together"):
        build_kit_inventory(
            set_path,
            REPOSITORY,
            viewers[:1],
            tmp_path / "kit" / "participant-kit.json",
            source_commit="7" * 40,
        )
