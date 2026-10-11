"""Read-only organizer identities. Catalog entries never authorize review or export."""

from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any

from civ_workshop.artifacts import file_sha256, read_json_file, require_mapping, require_string
from civ_workshop.errors import CivError
from civ_workshop.event_spec import load_event_spec
from civ_workshop.label_packs import load_label_pack

JSON_TYPES = {
    "product-manifest": ("contract", "civ.data-product-manifest/v1"),
    "consumer-pack": ("contract", "civ.label-pack/v1alpha1"),
    "review-progress": ("format", "civ.label-review-progress/v1"),
    "run-manifest": ("contract", "civ.run-manifest/v1"),
    "approval": ("contract", "civ.release-development-authority-approval/v1"),
}


def _closed(value: dict[str, Any], fields: frozenset[str], context: str) -> None:
    if unknown := sorted(set(value) - fields):
        raise CivError(f"{context} has unknown fields: {unknown[0]}")


def _digest(value: object) -> str:
    text = require_string(value, "artifact SHA-256")
    if re.fullmatch(r"[0-9a-f]{64}", text) is None:
        raise CivError("artifact SHA-256 must be 64 lowercase hexadecimal characters")
    return text


def _inspect(path: Path, kind: str) -> dict[str, object] | None:
    if kind == "eventspec":
        load_event_spec(path)
        return None
    if kind == "recording":
        with path.open("rb") as stream:
            if stream.read(8) != b"\x89MCAP0\r\n":
                raise CivError("artifact type recording requires MCAP bytes")
        return None
    field, expected = JSON_TYPES[kind]
    document = read_json_file(path, "catalog artifact")
    if document.get(field) != expected:
        raise CivError(f"artifact type {kind} requires {expected}")
    if kind == "consumer-pack":
        load_label_pack(path)
    if kind == "review-progress":
        identity = require_mapping(document.get("identity"), "review progress identity")
        _digest(identity.get("source_sha256"))
        _digest(identity.get("spec_sha256"))
        if not isinstance(document.get("candidates"), list):
            raise CivError("artifact type review-progress requires candidate decisions")
    if kind != "approval":
        return None
    authority = require_mapping(document.get("development_authority"), "development authority")
    if document.get("decision") != "approved":
        raise CivError("historical development approval is not approved")
    if (
        authority.get("participant_distribution") is not False
        or authority.get("sealed_authority_included") is not False
    ):
        raise CivError("private development approval must exclude distribution and sealed use")
    return {
        "approved_set_sha256": _digest(authority.get("set_sha256")),
        "aggregate_verified": False,
        "aggregate_procedure": "unresolved; supply the original approval procedure separately",
        "participant_distribution": False,
        "sealed_authority_included": False,
    }


def catalog_artifacts(inventory_path: Path) -> dict[str, Any]:
    inventory = read_json_file(inventory_path, "local artifact inventory")
    _closed(inventory, frozenset({"artifacts"}), "local artifact inventory")
    raw_records = inventory.get("artifacts")
    if not isinstance(raw_records, list) or not raw_records:
        raise CivError("local artifact inventory requires a non-empty artifacts list")
    records: list[dict[str, Any]] = []
    identifiers: set[str] = set()
    by_hash: dict[str, list[str]] = defaultdict(list)
    for raw in raw_records:
        entry = require_mapping(raw, "artifact declaration")
        _closed(entry, frozenset({"id", "kind", "path", "sha256"}), "artifact declaration")
        identifier = require_string(entry.get("id"), "artifact id")
        if identifier in identifiers:
            raise CivError("artifact ids must be unique")
        identifiers.add(identifier)
        kind = require_string(entry.get("kind"), "artifact kind")
        if kind not in {*JSON_TYPES, "recording", "eventspec"}:
            raise CivError(f"unsupported catalog artifact kind: {kind}")
        expected = _digest(entry.get("sha256"))
        path = Path(require_string(entry.get("path"), "artifact path"))
        if not path.is_absolute():
            path = inventory_path.parent / path
        record: dict[str, Any] = {
            "id": identifier,
            "kind": kind,
            "path": str(path.resolve()),
            "expected_sha256": expected,
            "observed_sha256": None,
            "identity_verified": False,
            "review_compatibility": "reference-only",
            "errors": [],
        }
        errors: list[str] = []
        try:
            actual = file_sha256(path)
            record["observed_sha256"] = actual
            by_hash[actual].append(identifier)
            if actual != expected:
                raise CivError("artifact SHA-256 mismatch")
            authority = _inspect(path, kind)
            if file_sha256(path) != actual:
                raise CivError("artifact changed during catalog inspection")
            record["identity_verified"] = True
            if authority is not None:
                record["authority"] = authority
                record["review_compatibility"] = "historical-authority-requires-binding-review"
            elif kind == "review-progress":
                record["review_compatibility"] = "requires-current-adapter-binding-check"
        except (CivError, OSError) as error:
            errors.append(str(error))
            record["review_compatibility"] = "mismatch"
        record["errors"] = errors
        records.append(record)
    return {
        "kind": "organizer-local-identity-catalog-not-truth",
        "valid": all(record["identity_verified"] for record in records),
        "artifacts": records,
        "duplicate_content": [
            {"sha256": digest, "artifact_ids": sorted(ids)}
            for digest, ids in sorted(by_hash.items())
            if len(ids) > 1
        ],
        "qualification": "byte and artifact-type identity only; not review or export approval",
    }


def add_catalog_command(commands: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    parser = commands.add_parser(
        "catalog", help="inspect explicitly declared local artifact identities"
    )
    parser.add_argument("--inventory", type=Path, required=True)


def catalog_command(args: argparse.Namespace) -> None:
    result = catalog_artifacts(args.inventory)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
    if not result["valid"]:
        raise CivError("local artifact catalog contains identity mismatches")
