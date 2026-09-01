from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from collections import Counter
from collections.abc import Mapping, Sequence
from hashlib import sha256
from pathlib import Path, PurePosixPath
from typing import Any

from civ_workshop.artifacts import canonical_json, file_sha256, read_json_file
from civ_workshop.camera_context import SET_CONTRACT as CAMERA_CONTEXT_SET_CONTRACT
from civ_workshop.contracts import require_closed_fields
from civ_workshop.data_products import audit_participant_set
from civ_workshop.errors import CivError

CONTRACT = "civ.participant-kit-inventory/v1"
PHASE4_RELEASE = "civ-2026-phase4-participant-kit-v1"
PHASE5_RELEASE = "civ-2026-phase5-camera-context-participant-kit-v2"
ACCEPTED_PRODUCT_SET_SHA256 = "d515c0a7cd748f8b2ad0cb41b93d8847b0917c2e6469be2f8be09582fc62ef9b"
ACCEPTED_PRODUCT_SET_RELEASE = "civ-2026-phase3-participant-signals-v1"
ACCEPTED_REQUIRED_DISK_BYTES = 335_177_173
ACCEPTED_MESSAGE_COUNT = 1_102_147
ACCEPTED_ROLES = Counter(
    {("kashiwa", "development"): 7, ("kashiwa", "warmup"): 1, ("reims", "development"): 5}
)
CONTAINER_IMAGE_DIGEST = "sha256:47f4017351802e878ff138c9e3aead0161de660914e79c252554968a91657560"
CONTAINER_IMAGE_NAME = "civ-phase4:attendee-candidate-558e85c"
RECOVERY_NOTICE = (
    "Two Kashiwa products derive from recovered recordings. Structural recovery made the "
    "recordings readable but does not prove that truncation lost no records. The caveat must "
    "remain with every distribution; corrupt-parent locations are intentionally omitted."
)
SHA256_PATTERN = re.compile(r"[0-9a-f]{64}")
COMMIT_PATTERN = re.compile(r"[0-9a-f]{40}")
FORBIDDEN_PUBLIC_TERMS = (
    "acceptance-proof",
    "ground_truth",
    "hidden_evaluation",
    "label_pack",
    "organizer_path",
    "sealed-source",
    "sealed_interval",
    "source_path",
    "truth-",
)

TRACKED_ASSETS: tuple[tuple[str, str], ...] = (
    ("participant-instructions", "README.md"),
    ("viewer-instructions", "viewer/README.md"),
    ("attribution", "ATTRIBUTION.md"),
    ("quickstart", "docs/quickstart.md"),
    ("layout", "layouts/kashiwa-right-turn.pj4.xml"),
    ("layout", "layouts/lichtblick-kashiwa-right-turn.json"),
    ("layout", "layouts/lichtblick-reims-left-turn.json"),
    ("layout", "layouts/reims-left-turn.pj4.xml"),
    ("example", "examples/kashiwa/right_turn.yaml"),
    ("example", "examples/reims/cave-encounter.yaml"),
    ("example", "examples/reims/cave-zones.json"),
    ("example", "examples/reims/left_turn.yaml"),
    ("schema", "schemas/civ.eventspec.v1.schema.json"),
    ("schema", "schemas/civ.event.v1.schema.json"),
    ("schema", "schemas/civ.point-resource.v1.schema.json"),
    ("schema", "schemas/civ.run-manifest.v1.schema.json"),
    ("schema", "schemas/civ.run-manifest.v2.schema.json"),
    ("schema", "schemas/civ.metrics.v1.schema.json"),
    ("schema", "schemas/civ.submission-bundle.v1.schema.json"),
    ("schema", "schemas/civ.submission-bundle.v2.schema.json"),
    ("schema", "schemas/civ.submission-extension.v1.schema.json"),
    ("schema", "schemas/civ.reproduction.v1.schema.json"),
    ("schema", "schemas/civ.data-product-manifest.v1.schema.json"),
    ("schema", "schemas/civ.data-product-set.v1.schema.json"),
    ("schema", "schemas/civ.camera-context-recipe.v1.schema.json"),
    ("schema", "schemas/civ.camera-context-privacy-rights-approval.v1.schema.json"),
    ("schema", "schemas/civ.camera-context-manifest.v1.schema.json"),
    ("schema", "schemas/civ.camera-context-set.v1.schema.json"),
    ("schema", "schemas/civ.participant-kit-inventory.v1.schema.json"),
    ("schema", "schemas/civ.attendee-fallback-pack.v1.schema.json"),
    ("schema", "schemas/civ.attendee-kit-assembly.v1.schema.json"),
    ("submission-template", "templates/submission/README.md"),
    ("submission-template", "templates/submission/detector.yaml"),
    ("submission-template", "templates/submission/figure.svg"),
    ("submission-template", "templates/submission/report.md"),
    ("submission-template", "templates/submission/reproduce.ps1"),
    ("submission-template", "templates/submission/reproduce.sh"),
)

TRACKED_ASSET_SOURCES = {
    f"templates/submission/{name}": f"src/civ_workshop/_templates/submission/{name}"
    for name in (
        "README.md",
        "detector.yaml",
        "figure.svg",
        "report.md",
        "reproduce.ps1",
        "reproduce.sh",
    )
}
TRACKED_ASSET_SOURCES.update(
    {
        "README.md": "kit/README.md",
        "viewer/README.md": "kit/viewer/README.md",
        "ATTRIBUTION.md": "kit/ATTRIBUTION.md",
    }
)

VIEWER_ASSETS: dict[str, dict[str, object]] = {
    "PlotJuggler-3.999.3-Windows-x64.exe": {
        "byte_size": 117_766_332,
        "platform": "windows-amd64",
        "sha256": "7b4674f10b48eadd43c195319f0aa5148324ad36464f870a14eb90253fdf4222",
    },
    "PlotJuggler-3.999.3-x86_64.AppImage": {
        "byte_size": 134_646_264,
        "platform": "linux-amd64",
        "sha256": "f6aa1a4019e8b7a4f730c4771b9d3b1df58db4e745a93cdda43b425692b626c2",
    },
    "lichtblick-1.28.0-win.exe": {
        "byte_size": 266_309_046,
        "platform": "windows-amd64",
        "sha256": "94420a37b3f9520091501842ee491966665090cfd23f40115f36f7ecf58ea2ec",
    },
    "lichtblick-1.28.0-linux-x64.tar.gz": {
        "byte_size": 162_728_473,
        "platform": "linux-amd64",
        "sha256": "0cbe3ce585f1aad154ed6340ac2b2f919d395e53ebd5a4b78faf8e7fe7f2be37",
    },
    "lichtblick-1.28.0-mac-universal.dmg": {
        "byte_size": 264_949_393,
        "platform": "macos-universal",
        "sha256": "7ad612abb223cb3da04b20b0e0b4874dcd49b97104849b48e9a8d094ebe7302c",
    },
}


def _mapping(value: object, context: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise CivError(f"{context} must be a mapping")
    return {str(key): item for key, item in value.items()}


def _string(value: object, context: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise CivError(f"{context} must be a non-empty string")
    return value.strip()


def _sha256(value: object, context: str) -> str:
    digest = _string(value, context)
    if SHA256_PATTERN.fullmatch(digest) is None:
        raise CivError(f"{context} must be a lowercase SHA-256")
    return digest


def _positive_integer(value: object, context: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise CivError(f"{context} must be a positive integer")
    return value


def _target(path: str) -> str:
    candidate = PurePosixPath(path)
    if candidate.is_absolute() or ".." in candidate.parts or str(candidate) != path:
        raise CivError(f"kit target must be a normalized relative path: {path}")
    return path


def _write_text(path: Path, text: str, context: str) -> None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8", newline="\n")
    except OSError as error:
        raise CivError(f"cannot write {context}: {error}") from error


def _tracked_assets(repository: Path) -> list[dict[str, object]]:
    assets: list[dict[str, object]] = []
    for role, relative in TRACKED_ASSETS:
        source = TRACKED_ASSET_SOURCES.get(relative, relative)
        path = repository / Path(source)
        if not path.is_file():
            raise CivError(f"tracked kit asset does not exist: {relative}")
        assets.append(
            {
                "byte_size": path.stat().st_size,
                "path": _target(relative),
                "role": role,
                "sha256": file_sha256(path),
            }
        )
    return assets


def _viewers(paths: Sequence[Path]) -> list[dict[str, object]]:
    if not paths:
        raise CivError("participant kit requires at least one pinned viewer asset")
    viewers: list[dict[str, object]] = []
    seen: set[str] = set()
    for path in paths:
        pin = VIEWER_ASSETS.get(path.name)
        if pin is None:
            raise CivError(f"viewer asset is not pinned: {path.name}")
        if path.name in seen:
            raise CivError(f"duplicate viewer asset: {path.name}")
        seen.add(path.name)
        if not path.is_file():
            raise CivError(f"viewer asset does not exist: {path}")
        if path.stat().st_size != pin["byte_size"] or file_sha256(path) != pin["sha256"]:
            raise CivError(f"viewer asset does not match its accepted pin: {path.name}")
        platform = str(pin["platform"])
        viewers.append(
            {
                "byte_size": pin["byte_size"],
                "name": path.name,
                "platform": platform,
                "sha256": pin["sha256"],
                "target": _target(f"viewer/{platform}/{path.name}"),
            }
        )
    names = {str(item["name"]) for item in viewers}
    has_plotjuggler = any(name.startswith("PlotJuggler-") for name in names)
    has_lichtblick = any(name.startswith("lichtblick-") for name in names)
    if has_plotjuggler != has_lichtblick:
        raise CivError("PlotJuggler and Lichtblick must be staged together")
    if names != set(VIEWER_ASSETS):
        missing = sorted(set(VIEWER_ASSETS) - names)
        raise CivError(
            "participant kit requires every pinned platform viewer; missing: "
            + ", ".join(missing)
        )
    return sorted(viewers, key=lambda item: (str(item["platform"]), str(item["name"])))


def _context_packs(values: Sequence[Mapping[str, object]]) -> list[dict[str, object]]:
    packs: list[dict[str, object]] = []
    for index, value in enumerate(values):
        context = f"context pack {index}"
        if set(value) != {"name", "manifest", "manifest_sha256", "required_disk_bytes", "approval"}:
            raise CivError(f"{context} must carry its manifest, size, and separate approval")
        approval = _mapping(value.get("approval"), f"{context} approval")
        if set(approval) != {"id", "sha256"}:
            raise CivError(f"{context} approval must contain exactly id and sha256")
        packs.append(
            {
                "approval": {
                    "id": _string(approval.get("id"), f"{context} approval id"),
                    "sha256": _sha256(approval.get("sha256"), f"{context} approval sha256"),
                },
                "manifest": _target(_string(value.get("manifest"), f"{context} manifest")),
                "manifest_sha256": _sha256(
                    value.get("manifest_sha256"), f"{context} manifest sha256"
                ),
                "name": _string(value.get("name"), f"{context} name"),
                "required_disk_bytes": _positive_integer(
                    value.get("required_disk_bytes"), f"{context} required disk bytes"
                ),
            }
        )
    return sorted(packs, key=lambda item: str(item["name"]))


def _camera_context_pack(set_path: Path) -> dict[str, object]:
    document = read_json_file(set_path, "camera-context product set")
    if document.get("contract") != CAMERA_CONTEXT_SET_CONTRACT:
        raise CivError("camera-context product set has the wrong contract")
    products = document.get("products")
    if not isinstance(products, list) or len(products) != 13:
        raise CivError("camera-context product set must contain exactly 13 products")
    roles: Counter[tuple[str, str]] = Counter()
    for index, raw in enumerate(products):
        product = _mapping(raw, f"camera-context product {index}")
        roles[
            (
                _string(product.get("dataset"), f"camera-context product {index} dataset"),
                _string(product.get("split"), f"camera-context product {index} split"),
            )
        ] += 1
    if roles != ACCEPTED_ROLES:
        raise CivError("camera-context product set does not match the accepted participant roles")
    approval = _mapping(document.get("approval"), "camera-context set approval")
    return {
        "approval": {
            "id": _string(approval.get("id"), "camera-context approval id"),
            "sha256": _sha256(
                approval.get("document_sha256"), "camera-context approval sha256"
            ),
        },
        "manifest": "context/camera-context-products.json",
        "manifest_sha256": file_sha256(set_path),
        "name": "camera-context-v1",
        "required_disk_bytes": _positive_integer(
            document.get("required_disk_bytes"), "camera-context required disk bytes"
        ),
    }


def _product_set(set_path: Path) -> tuple[dict[str, object], list[dict[str, object]]]:
    audit = audit_participant_set(set_path)
    if audit != {
        "message_count": ACCEPTED_MESSAGE_COUNT,
        "product_count": 13,
        "required_disk_bytes": ACCEPTED_REQUIRED_DISK_BYTES,
        "set_sha256": ACCEPTED_PRODUCT_SET_SHA256,
        "valid": True,
    }:
        raise CivError("participant product set is not the accepted Phase 3 set")
    document = read_json_file(set_path, "participant product set")
    if document.get("release_id") != ACCEPTED_PRODUCT_SET_RELEASE:
        raise CivError("participant product set has the wrong release identity")
    raw_products = document.get("products")
    if not isinstance(raw_products, list):
        raise CivError("participant product set products must be a list")
    roles: Counter[tuple[str, str]] = Counter()
    products: list[dict[str, object]] = []
    checksum_entries: list[dict[str, object]] = []
    for index, raw in enumerate(raw_products):
        entry = _mapping(raw, f"participant product {index}")
        dataset = _string(entry.get("dataset"), f"participant product {index} dataset")
        split = _string(entry.get("split"), f"participant product {index} split")
        roles[(dataset, split)] += 1
        name = _string(entry.get("name"), f"participant product {index} name")
        manifest = _string(entry.get("manifest"), f"participant product {index} manifest")
        product_target = _target(f"data/{name}")
        manifest_target = _target(f"data/{manifest}")
        product_hash = _sha256(entry.get("sha256"), f"participant product {index} sha256")
        manifest_hash = _sha256(
            entry.get("manifest_sha256"), f"participant product {index} manifest sha256"
        )
        byte_size = _positive_integer(
            entry.get("byte_size"), f"participant product {index} byte size"
        )
        products.append(
            {
                "byte_size": byte_size,
                "dataset": dataset,
                "manifest": manifest_target,
                "manifest_sha256": manifest_hash,
                "name": product_target,
                "sha256": product_hash,
                "source_id": _string(
                    entry.get("source_id"), f"participant product {index} source id"
                ),
                "split": split,
            }
        )
        checksum_entries.extend(
            [
                {"sha256": product_hash, "target": product_target},
                {"sha256": manifest_hash, "target": manifest_target},
            ]
        )
    if roles != ACCEPTED_ROLES:
        raise CivError("participant product set does not have the accepted dataset roles")
    set_target = "data/participant-products.json"
    checksum_entries.append({"sha256": ACCEPTED_PRODUCT_SET_SHA256, "target": set_target})
    return (
        {
            "manifest": set_target,
            "message_count": ACCEPTED_MESSAGE_COUNT,
            "product_count": 13,
            "products": products,
            "release_id": ACCEPTED_PRODUCT_SET_RELEASE,
            "required_disk_bytes": ACCEPTED_REQUIRED_DISK_BYTES,
            "sha256": ACCEPTED_PRODUCT_SET_SHA256,
        },
        checksum_entries,
    )


def _checksum_text(entries: Sequence[Mapping[str, object]]) -> str:
    ordered = sorted(entries, key=lambda item: str(item["target"]))
    targets = [str(item["target"]) for item in ordered]
    if len(set(targets)) != len(targets):
        raise CivError("participant kit contains duplicate target paths")
    return "".join(f"{item['sha256']}  {item['target']}\n" for item in ordered)


def build_kit_inventory(
    set_path: Path,
    repository: Path,
    viewer_paths: Sequence[Path],
    output_path: Path,
    *,
    source_commit: str,
    context_packs: Sequence[Mapping[str, object]] = (),
    context_set_path: Path | None = None,
) -> dict[str, object]:
    if COMMIT_PATTERN.fullmatch(source_commit) is None:
        raise CivError("tool source commit must be a lowercase 40-character Git commit")
    product_set, checksum_entries = _product_set(set_path)
    tracked_assets = _tracked_assets(repository)
    viewers = _viewers(viewer_paths)
    if context_set_path is not None and context_packs:
        raise CivError("camera-context set and manual context packs are mutually exclusive")
    contexts = _context_packs(
        [_camera_context_pack(context_set_path)] if context_set_path is not None else context_packs
    )
    lock_path = repository / "uv.lock"
    if not lock_path.is_file():
        raise CivError("tool lockfile does not exist: uv.lock")
    lockfile: dict[str, object] = {
        "byte_size": lock_path.stat().st_size,
        "path": "uv.lock",
        "sha256": file_sha256(lock_path),
    }
    tool: dict[str, object] = {
        "lockfile": lockfile,
        "name": "civ-workshop",
        "source_commit": source_commit,
        "version": "0.1.0",
    }
    for asset in tracked_assets:
        checksum_entries.append({"sha256": asset["sha256"], "target": asset["path"]})
    for viewer in viewers:
        checksum_entries.append({"sha256": viewer["sha256"], "target": viewer["target"]})
    checksum_entries.append({"sha256": lockfile["sha256"], "target": lockfile["path"]})
    for pack in contexts:
        checksum_entries.append({"sha256": pack["manifest_sha256"], "target": pack["manifest"]})

    inventory: dict[str, object] = {
        "container_candidate": {
            "image_digest": CONTAINER_IMAGE_DIGEST,
            "name": CONTAINER_IMAGE_NAME,
            "platform": "linux-amd64",
        },
        "content_profile": "signals-plus-camera-context" if contexts else "signals-only",
        "context_packs": contexts,
        "contract": CONTRACT,
        "layout": {
            "checksum_manifest": "checksums/SHA256SUMS",
            "directories": [
                "checksums",
                "container",
                *(["context"] if contexts else []),
                "data",
                "docs",
                "examples",
                "layouts",
                "templates/submission",
                "viewer/linux-amd64",
                "viewer/macos-universal",
                "viewer/windows-amd64",
            ],
            "inventory": "participant-kit.json",
        },
        "product_set": product_set,
        "recovery_notice": RECOVERY_NOTICE,
        "release_id": PHASE5_RELEASE if contexts else PHASE4_RELEASE,
        "required_disk_bytes": 0,
        "tool": tool,
        "tracked_assets": tracked_assets,
        "viewers": viewers,
    }
    base_bytes = (
        ACCEPTED_REQUIRED_DISK_BYTES
        + sum(
            _positive_integer(asset["byte_size"], "tracked asset byte size")
            for asset in tracked_assets
        )
        + sum(_positive_integer(viewer["byte_size"], "viewer byte size") for viewer in viewers)
        + _positive_integer(lockfile["byte_size"], "lockfile byte size")
        + sum(
            _positive_integer(pack["required_disk_bytes"], "context pack required disk bytes")
            for pack in contexts
        )
    )
    while True:
        inventory_text = f"{canonical_json(inventory)}\n"
        inventory_hash = sha256(inventory_text.encode()).hexdigest()
        checksum_text = _checksum_text(
            [*checksum_entries, {"sha256": inventory_hash, "target": "participant-kit.json"}]
        )
        required = base_bytes + len(inventory_text.encode()) + len(checksum_text.encode())
        if inventory["required_disk_bytes"] == required:
            break
        inventory["required_disk_bytes"] = required
    if output_path.name != "participant-kit.json":
        raise CivError("participant-kit inventory output must be named participant-kit.json")
    _write_text(output_path, inventory_text, "participant-kit inventory")
    checksum_path = output_path.parent / "checksums" / "SHA256SUMS"
    _write_text(checksum_path, checksum_text, "participant-kit checksum manifest")
    return {
        "checksum_manifest": "checksums/SHA256SUMS",
        "context_pack_count": len(contexts),
        "inventory": output_path.name,
        "inventory_sha256": file_sha256(output_path),
        "product_count": 13,
        "required_disk_bytes": required,
        "viewer_count": len(viewers),
    }


def audit_kit_inventory(path: Path) -> dict[str, object]:
    document = read_json_file(path, "participant-kit inventory")
    if document.get("contract") != CONTRACT:
        raise CivError(f"participant-kit inventory contract must be '{CONTRACT}'")
    require_closed_fields(document, kind="participant-kit inventory", expected=CONTRACT)
    serialized = canonical_json(document).lower()
    for term in FORBIDDEN_PUBLIC_TERMS:
        if term in serialized:
            raise CivError(f"participant-kit inventory contains forbidden term '{term}'")
    contexts_value = document.get("context_packs")
    has_context = isinstance(contexts_value, list) and bool(contexts_value)
    expected_release = PHASE5_RELEASE if has_context else PHASE4_RELEASE
    expected_profile = "signals-plus-camera-context" if has_context else "signals-only"
    if document.get("release_id") != expected_release:
        raise CivError("participant-kit inventory has the wrong release identity")
    if document.get("content_profile") != expected_profile:
        raise CivError("participant-kit inventory has the wrong content profile")
    product_set = _mapping(document.get("product_set"), "participant-kit product set")
    if set(product_set) != {
        "manifest",
        "message_count",
        "product_count",
        "products",
        "release_id",
        "required_disk_bytes",
        "sha256",
    }:
        raise CivError("participant-kit product set has unknown or missing fields")
    if (
        product_set.get("sha256") != ACCEPTED_PRODUCT_SET_SHA256
        or product_set.get("release_id") != ACCEPTED_PRODUCT_SET_RELEASE
        or product_set.get("required_disk_bytes") != ACCEPTED_REQUIRED_DISK_BYTES
        or product_set.get("message_count") != ACCEPTED_MESSAGE_COUNT
        or product_set.get("product_count") != 13
        or product_set.get("manifest") != "data/participant-products.json"
    ):
        raise CivError("participant-kit inventory does not reference the accepted product set")
    products = product_set.get("products")
    if not isinstance(products, list) or len(products) != 13:
        raise CivError("participant-kit inventory must contain exactly 13 products")
    roles: Counter[tuple[str, str]] = Counter()
    checksum_entries: list[dict[str, object]] = [
        {
            "sha256": ACCEPTED_PRODUCT_SET_SHA256,
            "target": "data/participant-products.json",
        }
    ]
    product_fields = {
        "byte_size",
        "dataset",
        "manifest",
        "manifest_sha256",
        "name",
        "sha256",
        "source_id",
        "split",
    }
    for index, raw in enumerate(products):
        product = _mapping(raw, f"participant-kit product {index}")
        if set(product) != product_fields:
            raise CivError(f"participant-kit product {index} has unknown or missing fields")
        dataset = _string(product.get("dataset"), f"participant-kit product {index} dataset")
        split = _string(product.get("split"), f"participant-kit product {index} split")
        roles[(dataset, split)] += 1
        name = _target(_string(product.get("name"), f"participant-kit product {index} name"))
        manifest = _target(
            _string(product.get("manifest"), f"participant-kit product {index} manifest")
        )
        if not name.startswith("data/") or not manifest.startswith("data/"):
            raise CivError("participant-kit products and manifests must stay in data/")
        checksum_entries.extend(
            [
                {
                    "sha256": _sha256(
                        product.get("sha256"), f"participant-kit product {index} sha256"
                    ),
                    "target": name,
                },
                {
                    "sha256": _sha256(
                        product.get("manifest_sha256"),
                        f"participant-kit product {index} manifest sha256",
                    ),
                    "target": manifest,
                },
            ]
        )
        _positive_integer(product.get("byte_size"), f"participant-kit product {index} byte size")
        _string(product.get("source_id"), f"participant-kit product {index} source id")
    if roles != ACCEPTED_ROLES:
        raise CivError("participant-kit inventory has the wrong dataset roles")

    tool = _mapping(document.get("tool"), "participant-kit tool")
    if set(tool) != {"lockfile", "name", "source_commit", "version"}:
        raise CivError("participant-kit tool has unknown or missing fields")
    if tool.get("name") != "civ-workshop" or tool.get("version") != "0.1.0":
        raise CivError("participant-kit tool has the wrong stable identity")
    source_commit = _string(tool.get("source_commit"), "participant-kit tool source commit")
    if COMMIT_PATTERN.fullmatch(source_commit) is None:
        raise CivError("participant-kit tool source commit is invalid")
    lockfile = _mapping(tool.get("lockfile"), "participant-kit tool lockfile")
    if set(lockfile) != {"byte_size", "path", "sha256"} or lockfile.get("path") != "uv.lock":
        raise CivError("participant-kit tool lockfile has the wrong identity")
    lockfile_bytes = _positive_integer(
        lockfile.get("byte_size"), "participant-kit tool lockfile byte size"
    )
    checksum_entries.append(
        {
            "sha256": _sha256(lockfile.get("sha256"), "participant-kit tool lockfile sha256"),
            "target": "uv.lock",
        }
    )

    container = _mapping(document.get("container_candidate"), "container candidate")
    if container != {
        "image_digest": CONTAINER_IMAGE_DIGEST,
        "name": CONTAINER_IMAGE_NAME,
        "platform": "linux-amd64",
    }:
        raise CivError("participant-kit inventory has the wrong container candidate")

    raw_viewers = document.get("viewers")
    if not isinstance(raw_viewers, list) or not raw_viewers:
        raise CivError("participant-kit inventory requires at least one viewer")
    viewer_bytes = 0
    seen_viewers: set[str] = set()
    for index, raw in enumerate(raw_viewers):
        viewer = _mapping(raw, f"participant-kit viewer {index}")
        if set(viewer) != {"byte_size", "name", "platform", "sha256", "target"}:
            raise CivError(f"participant-kit viewer {index} has unknown or missing fields")
        name = _string(viewer.get("name"), f"participant-kit viewer {index} name")
        pin = VIEWER_ASSETS.get(name)
        platform = _string(viewer.get("platform"), f"participant-kit viewer {index} platform")
        target = _target(_string(viewer.get("target"), f"participant-kit viewer {index} target"))
        if (
            pin is None
            or name in seen_viewers
            or platform != pin["platform"]
            or target != f"viewer/{platform}/{name}"
            or viewer.get("sha256") != pin["sha256"]
            or viewer.get("byte_size") != pin["byte_size"]
        ):
            raise CivError(f"participant-kit viewer {index} does not match an accepted pin")
        seen_viewers.add(name)
        viewer_bytes += _positive_integer(
            viewer.get("byte_size"), f"participant-kit viewer {index} byte size"
        )
        checksum_entries.append({"sha256": viewer["sha256"], "target": target})

    has_plotjuggler = any(name.startswith("PlotJuggler-") for name in seen_viewers)
    has_lichtblick = any(name.startswith("lichtblick-") for name in seen_viewers)
    if has_plotjuggler != has_lichtblick:
        raise CivError("participant-kit PlotJuggler and Lichtblick must be staged together")
    if seen_viewers != set(VIEWER_ASSETS):
        missing = sorted(set(VIEWER_ASSETS) - seen_viewers)
        raise CivError(
            "participant-kit requires every pinned platform viewer; missing: "
            + ", ".join(missing)
        )

    raw_assets = document.get("tracked_assets")
    if not isinstance(raw_assets, list) or len(raw_assets) != len(TRACKED_ASSETS):
        raise CivError("participant-kit inventory has the wrong tracked asset set")
    asset_bytes = 0
    observed_assets: list[tuple[str, str]] = []
    for index, raw in enumerate(raw_assets):
        asset = _mapping(raw, f"participant-kit tracked asset {index}")
        if set(asset) != {"byte_size", "path", "role", "sha256"}:
            raise CivError(f"participant-kit tracked asset {index} has unknown or missing fields")
        role = _string(asset.get("role"), f"participant-kit tracked asset {index} role")
        target = _target(_string(asset.get("path"), f"participant-kit tracked asset {index} path"))
        observed_assets.append((role, target))
        asset_bytes += _positive_integer(
            asset.get("byte_size"), f"participant-kit tracked asset {index} byte size"
        )
        checksum_entries.append(
            {
                "sha256": _sha256(
                    asset.get("sha256"), f"participant-kit tracked asset {index} sha256"
                ),
                "target": target,
            }
        )
    if tuple(observed_assets) != TRACKED_ASSETS:
        raise CivError("participant-kit inventory has the wrong tracked asset roles or paths")

    contexts = document.get("context_packs")
    if not isinstance(contexts, list):
        raise CivError("participant-kit context_packs must be a list")
    normalized_contexts = _context_packs(
        [_mapping(item, "participant-kit context pack") for item in contexts]
    )
    context_bytes = sum(
        _positive_integer(pack["required_disk_bytes"], "context pack required disk bytes")
        for pack in normalized_contexts
    )
    checksum_entries.extend(
        {"sha256": pack["manifest_sha256"], "target": pack["manifest"]}
        for pack in normalized_contexts
    )
    if document.get("recovery_notice") != RECOVERY_NOTICE:
        raise CivError("participant-kit inventory is missing the recovery caveat")
    layout = _mapping(document.get("layout"), "participant-kit layout")
    expected_directories = [
        "checksums",
        "container",
        *(["context"] if has_context else []),
        "data",
        "docs",
        "examples",
        "layouts",
        "templates/submission",
        "viewer/linux-amd64",
        "viewer/macos-universal",
        "viewer/windows-amd64",
    ]
    if layout != {
        "checksum_manifest": "checksums/SHA256SUMS",
        "directories": expected_directories,
        "inventory": "participant-kit.json",
    }:
        raise CivError("participant-kit inventory has the wrong deterministic layout")
    checksum_path = path.parent / "checksums" / "SHA256SUMS"
    if not checksum_path.is_file():
        raise CivError("participant-kit checksum manifest is missing")
    checksum_entries.append({"sha256": file_sha256(path), "target": "participant-kit.json"})
    expected_checksums = _checksum_text(checksum_entries)
    try:
        observed_checksums = checksum_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as error:
        raise CivError(f"cannot read participant-kit checksum manifest: {error}") from error
    if observed_checksums != expected_checksums:
        raise CivError("participant-kit checksum manifest is not canonical or complete")
    required_disk_bytes = _positive_integer(
        document.get("required_disk_bytes"), "participant-kit required disk bytes"
    )
    expected_bytes = (
        ACCEPTED_REQUIRED_DISK_BYTES
        + viewer_bytes
        + asset_bytes
        + lockfile_bytes
        + context_bytes
        + path.stat().st_size
        + checksum_path.stat().st_size
    )
    if required_disk_bytes != expected_bytes:
        raise CivError("participant-kit required_disk_bytes does not match its inventory")
    return {
        "context_pack_count": len(contexts),
        "inventory_sha256": file_sha256(path),
        "product_count": len(products),
        "required_disk_bytes": required_disk_bytes,
        "valid": True,
        "viewer_count": len(raw_viewers),
    }


def _git_head(repository: Path) -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=repository,
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError) as error:
        raise CivError(f"cannot resolve tool source commit: {error}") from error
    return result.stdout.strip()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m civ_workshop.kit_inventory",
        description="Build and audit the deterministic participant-safe kit inventory",
    )
    commands = parser.add_subparsers(dest="command", required=True)
    build = commands.add_parser("build", help="build an inventory from external payload inputs")
    build.add_argument("product_set", type=Path)
    build.add_argument("--repository", type=Path, required=True)
    build.add_argument("--viewer", action="append", default=[], type=Path)
    build.add_argument("--context-set", type=Path)
    build.add_argument("--output", type=Path, required=True)
    audit = commands.add_parser("audit", help="audit a generated kit inventory and checksums")
    audit.add_argument("inventory", type=Path)
    return parser


def main(argv: Sequence[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "build":
            result = build_kit_inventory(
                args.product_set,
                args.repository,
                args.viewer,
                args.output,
                source_commit=_git_head(args.repository),
                context_set_path=args.context_set,
            )
        else:
            result = audit_kit_inventory(args.inventory)
        print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    except CivError as error:
        print(f"kit-inventory: {error}", file=sys.stderr)
        raise SystemExit(2) from None


if __name__ == "__main__":
    main()
