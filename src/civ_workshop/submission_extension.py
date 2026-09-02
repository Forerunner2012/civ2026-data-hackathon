from __future__ import annotations

import mimetypes
import re
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

from civ_workshop.artifacts import file_sha256, read_json_file, require_mapping, require_string
from civ_workshop.errors import CivError

EXTENSION_CONTRACT = "civ.submission-extension/v1"
EXTENSION_MANIFEST_PATH = "extension/manifest.json"
MAX_EXTENSION_PAYLOADS = 8
MAX_EXTENSION_PAYLOAD_BYTES = 1024 * 1024
MAX_EXTENSION_UNCOMPRESSED_BYTES = 4 * 1024 * 1024

EXTENSION_KINDS = frozenset(
    {"external-resource", "provenance", "agent-trace", "regression-test"}
)
MEDIA_TYPES_BY_SUFFIX = {
    ".csv": "text/csv",
    ".json": "application/json",
    ".jsonl": "application/x-ndjson",
    ".md": "text/markdown",
    ".txt": "text/plain",
    ".yaml": "application/yaml",
    ".yml": "application/yaml",
}
FORBIDDEN_SUFFIXES = frozenset(
    {
        ".bag",
        ".bin",
        ".ckpt",
        ".db3",
        ".mcap",
        ".onnx",
        ".pickle",
        ".pkl",
        ".pt",
        ".pth",
        ".pyc",
        ".zip",
    }
)
FORBIDDEN_PARTS = frozenset(
    {
        ".cache",
        ".git",
        ".venv",
        "cache",
        "caches",
        "checkpoint",
        "checkpoints",
        "clip",
        "clips",
        "environment",
        "environments",
        "evidence",
        "frame",
        "frames",
        "label",
        "labels",
        "model",
        "models",
        "recording",
        "recordings",
        "runtime",
        "secret",
        "secrets",
        "state",
        "weights",
    }
)
SHA256_PATTERN = re.compile(r"[0-9a-f]{64}")


@dataclass(frozen=True, order=True)
class ExtensionEntry:
    path: str
    kind: str
    sha256: str
    media_type: str

    def as_dict(self) -> dict[str, str]:
        return {
            "kind": self.kind,
            "media_type": self.media_type,
            "path": self.path,
            "sha256": self.sha256,
        }


def safe_archive_path(value: str, context: str) -> PurePosixPath:
    candidate = PurePosixPath(value)
    if (
        not value
        or "\\" in value
        or candidate.is_absolute()
        or ".." in candidate.parts
        or "." in candidate.parts
        or value.endswith("/")
        or candidate.as_posix() != value
    ):
        raise CivError(f"{context} must be a contained archive-relative POSIX path")
    return candidate


def media_type_for(path: Path) -> str:
    media_type = MEDIA_TYPES_BY_SUFFIX.get(path.suffix.lower())
    if media_type is None:
        guessed, _ = mimetypes.guess_type(path.name)
        raise CivError(
            f"extension payload has forbidden or unsupported media type: {path.as_posix()}"
            + (f" ({guessed})" if guessed else "")
        )
    return media_type


def _validate_payload_name(path: PurePosixPath, kind: str) -> None:
    lowered_parts = {part.casefold() for part in path.parts}
    lowered_stems = {PurePosixPath(part).stem.casefold() for part in path.parts}
    if (
        lowered_parts & FORBIDDEN_PARTS
        or lowered_stems & FORBIDDEN_PARTS
        or path.suffix.casefold() in FORBIDDEN_SUFFIXES
    ):
        raise CivError(f"extension payload is forbidden: {path.as_posix()}")
    if kind != "external-resource" and path.parts[0] != "extension":
        raise CivError(f"extension {kind} payload must be under extension/: {path.as_posix()}")
    if path.as_posix() == EXTENSION_MANIFEST_PATH:
        raise CivError("extension manifest cannot declare itself as a payload")


def load_extension_entries(working: Path) -> list[ExtensionEntry]:
    manifest_path = working / EXTENSION_MANIFEST_PATH
    if not manifest_path.is_file():
        return []
    manifest = read_json_file(manifest_path, "submission extension manifest")
    if set(manifest) != {"contract", "entries"}:
        unknown = sorted(set(manifest) - {"contract", "entries"})
        if unknown:
            raise CivError(
                f"invalid submission extension '{EXTENSION_CONTRACT}': "
                f"unknown field '{unknown[0]}'"
            )
        raise CivError("submission extension manifest requires contract and entries")
    if manifest.get("contract") != EXTENSION_CONTRACT:
        raise CivError(
            f"invalid submission extension contract '{manifest.get('contract')}'; "
            f"expected '{EXTENSION_CONTRACT}'"
        )
    raw_entries = manifest.get("entries")
    if not isinstance(raw_entries, list) or not raw_entries:
        raise CivError("submission extension entries must be a non-empty list")
    if len(raw_entries) > MAX_EXTENSION_PAYLOADS:
        raise CivError(
            f"submission extension has more than {MAX_EXTENSION_PAYLOADS} payloads"
        )
    raw_paths = [
        require_string(
            require_mapping(raw_entry, f"submission extension entry {index}").get("path"),
            f"submission extension entry {index} path",
        )
        for index, raw_entry in enumerate(raw_entries)
    ]
    folded_paths = [path.casefold() for path in raw_paths]
    if len(folded_paths) != len(set(folded_paths)):
        raise CivError("submission extension contains a duplicate or case-colliding path")

    entries: list[ExtensionEntry] = []
    seen_paths: set[str] = set()
    total_size = 0
    for index, raw_entry in enumerate(raw_entries):
        entry = require_mapping(raw_entry, f"submission extension entry {index}")
        required_fields = {"kind", "media_type", "path", "sha256"}
        if set(entry) != required_fields:
            unknown = sorted(set(entry) - required_fields)
            if unknown:
                raise CivError(
                    f"submission extension entry {index} has unknown field '{unknown[0]}'"
                )
            raise CivError(f"submission extension entry {index} is incomplete")
        kind = require_string(entry.get("kind"), f"submission extension entry {index} kind")
        if kind not in EXTENSION_KINDS:
            raise CivError(f"submission extension entry {index} kind is unsupported: {kind}")
        relative = require_string(
            entry.get("path"), f"submission extension entry {index} path"
        )
        archive_path = safe_archive_path(relative, f"submission extension entry {index} path")
        folded = relative.casefold()
        if folded in seen_paths:
            raise CivError(
                "submission extension contains a duplicate or case-colliding path: "
                f"{relative}"
            )
        seen_paths.add(folded)
        _validate_payload_name(archive_path, kind)
        sha256 = require_string(
            entry.get("sha256"), f"submission extension entry {index} sha256"
        )
        if SHA256_PATTERN.fullmatch(sha256) is None:
            raise CivError(f"submission extension entry '{relative}' sha256 is invalid")
        media_type = require_string(
            entry.get("media_type"), f"submission extension entry {index} media type"
        )
        payload = working.joinpath(*archive_path.parts)
        if payload.is_symlink():
            raise CivError(f"submission extension payload must not be a symlink: {relative}")
        if not payload.is_file():
            raise CivError(f"submission extension payload is missing: {relative}")
        expected_media_type = media_type_for(payload)
        if media_type != expected_media_type:
            raise CivError(
                f"submission extension entry '{relative}' media type must be {expected_media_type}"
            )
        if file_sha256(payload) != sha256:
            raise CivError(f"submission extension payload hash changed: {relative}")
        size = payload.stat().st_size
        if size > MAX_EXTENSION_PAYLOAD_BYTES:
            raise CivError(
                "submission extension payload exceeds "
                f"{MAX_EXTENSION_PAYLOAD_BYTES} bytes: {relative}"
            )
        total_size += size
        entries.append(ExtensionEntry(relative, kind, sha256, media_type))
    if total_size > MAX_EXTENSION_UNCOMPRESSED_BYTES:
        raise CivError(
            "submission extension payloads exceed "
            f"{MAX_EXTENSION_UNCOMPRESSED_BYTES} combined bytes"
        )
    if entries != sorted(entries):
        raise CivError("submission extension entries must be sorted by archive-relative path")
    return entries
