from __future__ import annotations

import argparse
import json
import re
import sys
from collections.abc import Mapping, Sequence
from hashlib import sha256
from pathlib import Path
from typing import Any

from mcap.exceptions import McapError
from mcap.reader import make_reader
from mcap.writer import CompressionType, Writer

from civ_workshop.artifacts import canonical_json, file_sha256, read_json_file
from civ_workshop.errors import CivError

RECIPE_CONTRACT = "civ.data-product-recipe/v1"
MANIFEST_CONTRACT = "civ.data-product-manifest/v1"
SET_CONTRACT = "civ.data-product-set/v1"
WRITER_ID = "civ-workshop/data-products-v1"
SHA256_PATTERN = re.compile(r"[0-9a-f]{64}")
SPLITS = frozenset({"warmup", "development", "sealed"})
FORBIDDEN_PARTICIPANT_TERMS = (
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

RECIPE_FIELDS = frozenset(
    {
        "contract",
        "recipe_id",
        "version",
        "product_name",
        "source",
        "dataset",
        "split",
        "topics",
        "license",
        "attribution",
        "rights_scope",
        "modifications",
    }
)
SOURCE_FIELDS = frozenset({"id", "sha256"})
LICENSE_FIELDS = frozenset({"name", "url"})
MANIFEST_FIELDS = frozenset(
    {"contract", "product", "parent", "recipe", "provenance", "required_disk_bytes"}
)
SET_FIELDS = frozenset({"contract", "release_id", "products", "required_disk_bytes"})
SET_PRODUCT_FIELDS = frozenset(
    {
        "source_id",
        "dataset",
        "split",
        "name",
        "sha256",
        "manifest",
        "manifest_sha256",
        "byte_size",
    }
)


def _canonical_with_disk_total(
    document: dict[str, object], base_bytes: int
) -> tuple[str, int]:
    required = base_bytes
    while True:
        document["required_disk_bytes"] = required
        text = f"{canonical_json(document)}\n"
        next_required = base_bytes + len(text.encode("utf-8"))
        if next_required == required:
            return text, required
        required = next_required


def _mapping(value: object, context: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise CivError(f"{context} must be a mapping")
    return {str(key): item for key, item in value.items()}


def _closed(value: Mapping[str, object], allowed: frozenset[str], context: str) -> None:
    unknown = sorted(set(value) - allowed)
    if unknown:
        raise CivError(f"{context} has unknown field '{unknown[0]}'")


def _string(value: object, context: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise CivError(f"{context} must be a non-empty string")
    return value.strip()


def _string_list(value: object, context: str, *, allow_empty: bool = False) -> list[str]:
    if not isinstance(value, list) or (not value and not allow_empty):
        suffix = " a list" if allow_empty else " a non-empty list"
        raise CivError(f"{context} must be{suffix}")
    result = [_string(item, f"{context} item") for item in value]
    if len(set(result)) != len(result):
        raise CivError(f"{context} must not contain duplicates")
    return result


def _sha256(value: object, context: str) -> str:
    digest = _string(value, context)
    if SHA256_PATTERN.fullmatch(digest) is None:
        raise CivError(f"{context} must be a lowercase SHA-256")
    return digest


def _load_recipe(path: Path) -> dict[str, Any]:
    recipe = read_json_file(path, "data-product recipe")
    _closed(recipe, RECIPE_FIELDS, "data-product recipe")
    if recipe.get("contract") != RECIPE_CONTRACT:
        raise CivError(f"data-product recipe contract must be '{RECIPE_CONTRACT}'")

    recipe_id = _string(recipe.get("recipe_id"), "data-product recipe recipe_id")
    version = recipe.get("version")
    if isinstance(version, bool) or not isinstance(version, int) or version < 1:
        raise CivError("data-product recipe version must be a positive integer")
    product_name = _string(recipe.get("product_name"), "data-product recipe product_name")
    if Path(product_name).name != product_name or not product_name.endswith(".mcap"):
        raise CivError("data-product recipe product_name must be a plain .mcap filename")

    source = _mapping(recipe.get("source"), "data-product recipe source")
    _closed(source, SOURCE_FIELDS, "data-product recipe source")
    source_id = _string(source.get("id"), "data-product recipe source id")
    source_sha256 = _sha256(source.get("sha256"), "data-product recipe source sha256")

    dataset = _string(recipe.get("dataset"), "data-product recipe dataset")
    split = _string(recipe.get("split"), "data-product recipe split")
    if split not in SPLITS:
        raise CivError(f"data-product recipe split must be one of: {', '.join(sorted(SPLITS))}")
    topics = sorted(_string_list(recipe.get("topics"), "data-product recipe topics"))

    license_record = _mapping(recipe.get("license"), "data-product recipe license")
    _closed(license_record, LICENSE_FIELDS, "data-product recipe license")
    license_name = _string(license_record.get("name"), "data-product recipe license name")
    license_url = license_record.get("url")
    if license_url is not None:
        license_url = _string(license_url, "data-product recipe license url")

    attribution = _string(recipe.get("attribution"), "data-product recipe attribution")
    rights_scope = _string(recipe.get("rights_scope"), "data-product recipe rights_scope")
    modifications = _string_list(
        recipe.get("modifications"), "data-product recipe modifications"
    )
    return {
        "contract": RECIPE_CONTRACT,
        "recipe_id": recipe_id,
        "version": version,
        "product_name": product_name,
        "source": {"id": source_id, "sha256": source_sha256},
        "dataset": dataset,
        "split": split,
        "topics": topics,
        "license": {"name": license_name, "url": license_url},
        "attribution": attribution,
        "rights_scope": rights_scope,
        "modifications": modifications,
    }


def _source_statistics(path: Path) -> dict[str, int]:
    try:
        with path.open("rb") as stream:
            summary = make_reader(stream, validate_crcs=True).get_summary()
        if summary is not None and summary.statistics is not None:
            statistics = summary.statistics
            return {
                "message_count": statistics.message_count,
                "message_start_ns": statistics.message_start_time,
                "message_end_ns": statistics.message_end_time,
                "duration_ns": statistics.message_end_time - statistics.message_start_time,
            }
        start_ns: int | None = None
        end_ns: int | None = None
        count = 0
        with path.open("rb") as stream:
            for _, _, message in make_reader(stream, validate_crcs=True).iter_messages():
                count += 1
                start_ns = message.log_time if start_ns is None else min(start_ns, message.log_time)
                end_ns = message.log_time if end_ns is None else max(end_ns, message.log_time)
    except (OSError, McapError) as error:
        raise CivError(f"cannot inspect source MCAP: {error}") from error
    if start_ns is None or end_ns is None:
        raise CivError("source MCAP contains no messages")
    return {
        "message_count": count,
        "message_start_ns": start_ns,
        "message_end_ns": end_ns,
        "duration_ns": end_ns - start_ns,
    }


def _write_product(source_path: Path, product_path: Path, topics: list[str]) -> dict[str, Any]:
    schema_ids: dict[int, int] = {}
    channel_ids: dict[int, int] = {}
    topic_records: dict[str, dict[str, Any]] = {}
    message_count = 0
    start_ns: int | None = None
    end_ns: int | None = None
    try:
        with source_path.open("rb") as source, product_path.open("xb") as destination:
            reader = make_reader(source, validate_crcs=True)
            header = reader.get_header()
            writer = Writer(destination, compression=CompressionType.NONE)
            writer.start(profile=header.profile, library=WRITER_ID)
            for schema, channel, message in reader.iter_messages(topics=topics):
                output_schema_id = 0
                schema_name = ""
                schema_encoding = ""
                schema_sha256 = ""
                if schema is not None:
                    output_schema_id = schema_ids.get(schema.id, 0)
                    if not output_schema_id:
                        output_schema_id = writer.register_schema(
                            name=schema.name,
                            encoding=schema.encoding,
                            data=schema.data,
                        )
                        schema_ids[schema.id] = output_schema_id
                    schema_name = schema.name
                    schema_encoding = schema.encoding
                    schema_sha256 = sha256(schema.data).hexdigest()
                output_channel_id = channel_ids.get(channel.id)
                if output_channel_id is None:
                    output_channel_id = writer.register_channel(
                        schema_id=output_schema_id,
                        topic=channel.topic,
                        message_encoding=channel.message_encoding,
                        metadata=channel.metadata,
                    )
                    channel_ids[channel.id] = output_channel_id
                writer.add_message(
                    channel_id=output_channel_id,
                    log_time=message.log_time,
                    publish_time=message.publish_time,
                    sequence=message.sequence,
                    data=message.data,
                )
                record = topic_records.setdefault(
                    channel.topic,
                    {
                        "message_count": 0,
                        "message_encoding": channel.message_encoding,
                        "schema_encoding": schema_encoding,
                        "schema_name": schema_name,
                        "schema_sha256": schema_sha256,
                        "topic": channel.topic,
                    },
                )
                identity = (
                    record["message_encoding"],
                    record["schema_encoding"],
                    record["schema_name"],
                    record["schema_sha256"],
                )
                current_identity = (
                    channel.message_encoding,
                    schema_encoding,
                    schema_name,
                    schema_sha256,
                )
                if identity != current_identity:
                    raise CivError(
                        f"topic {channel.topic} changes schema or encoding within source"
                    )
                record["message_count"] += 1
                message_count += 1
                start_ns = (
                    message.log_time if start_ns is None else min(start_ns, message.log_time)
                )
                end_ns = message.log_time if end_ns is None else max(end_ns, message.log_time)
            writer.finish()
    except FileExistsError as error:
        raise CivError(f"product already exists: {product_path}") from error
    except (OSError, McapError) as error:
        product_path.unlink(missing_ok=True)
        raise CivError(f"cannot build data product: {error}") from error

    missing_topics = sorted(set(topics) - set(topic_records))
    if missing_topics:
        product_path.unlink(missing_ok=True)
        raise CivError(f"source is missing recipe topics: {', '.join(missing_topics)}")
    if start_ns is None or end_ns is None:
        product_path.unlink(missing_ok=True)
        raise CivError("data product contains no messages")
    try:
        with product_path.open("rb") as stream:
            list(make_reader(stream, validate_crcs=True).iter_messages())
    except (OSError, McapError) as error:
        product_path.unlink(missing_ok=True)
        raise CivError(f"data product failed MCAP validation: {error}") from error
    return {
        "duration_ns": end_ns - start_ns,
        "message_count": message_count,
        "message_end_ns": end_ns,
        "message_start_ns": start_ns,
        "topics": [topic_records[topic] for topic in sorted(topic_records)],
    }


def build_data_product(
    source_path: Path, recipe_path: Path, output_directory: Path
) -> dict[str, object]:
    if not source_path.is_file():
        raise CivError(f"source MCAP does not exist: {source_path}")
    recipe = _load_recipe(recipe_path)
    expected_source_hash = str(_mapping(recipe["source"], "recipe source")["sha256"])
    actual_source_hash = file_sha256(source_path)
    if actual_source_hash != expected_source_hash:
        raise CivError(
            "source SHA-256 does not match recipe: "
            f"expected {expected_source_hash}, got {actual_source_hash}"
        )

    try:
        output_directory.mkdir(parents=True, exist_ok=True)
    except OSError as error:
        raise CivError(f"cannot create output directory: {error}") from error
    product_name = str(recipe["product_name"])
    product_path = output_directory / product_name
    manifest_path = output_directory / f"{product_name}.manifest.json"
    if manifest_path.exists():
        raise CivError(f"manifest already exists: {manifest_path}")

    source_statistics = _source_statistics(source_path)
    product_statistics = _write_product(source_path, product_path, list(recipe["topics"]))
    product_bytes = product_path.stat().st_size
    recipe_hash = file_sha256(recipe_path)
    source_record = _mapping(recipe["source"], "recipe source")
    manifest: dict[str, object] = {
        "contract": MANIFEST_CONTRACT,
        "parent": {
            "byte_size": source_path.stat().st_size,
            "duration_ns": source_statistics["duration_ns"],
            "message_count": source_statistics["message_count"],
            "message_end_ns": source_statistics["message_end_ns"],
            "message_start_ns": source_statistics["message_start_ns"],
            "sha256": actual_source_hash,
            "source_id": source_record["id"],
        },
        "product": {
            "byte_size": product_bytes,
            **product_statistics,
            "name": product_name,
            "sha256": file_sha256(product_path),
        },
        "provenance": {
            "attribution": recipe["attribution"],
            "dataset": recipe["dataset"],
            "license": recipe["license"],
            "modifications": recipe["modifications"],
            "rights_scope": recipe["rights_scope"],
            "split": recipe["split"],
        },
        "recipe": {
            "contract": RECIPE_CONTRACT,
            "id": recipe["recipe_id"],
            "sha256": recipe_hash,
            "topics": recipe["topics"],
            "version": recipe["version"],
            "writer": WRITER_ID,
        },
        "required_disk_bytes": 0,
    }
    manifest_text, required_disk_bytes = _canonical_with_disk_total(manifest, product_bytes)
    try:
        manifest_path.write_text(manifest_text, encoding="utf-8", newline="\n")
    except OSError as error:
        product_path.unlink(missing_ok=True)
        raise CivError(f"cannot write data-product manifest: {error}") from error
    return {
        "manifest": manifest_path.name,
        "manifest_sha256": file_sha256(manifest_path),
        "product": product_name,
        "product_sha256": _mapping(manifest["product"], "manifest product")["sha256"],
        "required_disk_bytes": required_disk_bytes,
    }


def _load_manifest(path: Path) -> dict[str, Any]:
    manifest = read_json_file(path, "data-product manifest")
    _closed(manifest, MANIFEST_FIELDS, "data-product manifest")
    if manifest.get("contract") != MANIFEST_CONTRACT:
        raise CivError(f"data-product manifest contract must be '{MANIFEST_CONTRACT}'")
    return manifest


def build_participant_set(
    manifest_paths: Sequence[Path], output_path: Path, release_id: str
) -> dict[str, object]:
    release_id = _string(release_id, "release id")
    if not manifest_paths:
        raise CivError("participant set requires at least one product manifest")
    products: list[dict[str, object]] = []
    seen_names: set[str] = set()
    seen_sources: set[str] = set()
    product_bytes_total = 0
    for path in manifest_paths:
        manifest = _load_manifest(path)
        product = _mapping(manifest.get("product"), "data-product manifest product")
        parent = _mapping(manifest.get("parent"), "data-product manifest parent")
        provenance = _mapping(manifest.get("provenance"), "data-product manifest provenance")
        split = _string(provenance.get("split"), "data-product manifest split")
        if split == "sealed":
            raise CivError("participant set must not include a sealed product")
        name = _string(product.get("name"), "data-product manifest product name")
        source_id = _string(parent.get("source_id"), "data-product manifest source id")
        if name in seen_names or source_id in seen_sources:
            raise CivError("participant set contains a duplicate product name or source id")
        seen_names.add(name)
        seen_sources.add(source_id)
        byte_size = product.get("byte_size")
        if isinstance(byte_size, bool) or not isinstance(byte_size, int) or byte_size < 1:
            raise CivError("data-product manifest product byte_size must be positive")
        product_bytes_total += byte_size
        products.append(
            {
                "byte_size": byte_size,
                "dataset": _string(
                    provenance.get("dataset"), "data-product manifest dataset"
                ),
                "manifest": path.name,
                "manifest_sha256": file_sha256(path),
                "name": name,
                "sha256": _sha256(
                    product.get("sha256"), "data-product manifest product sha256"
                ),
                "source_id": source_id,
                "split": split,
            }
        )
    products.sort(key=lambda item: (str(item["dataset"]), str(item["source_id"])))
    base_bytes = product_bytes_total + sum(
        path.stat().st_size for path in manifest_paths
    )
    set_manifest: dict[str, object] = {
        "contract": SET_CONTRACT,
        "products": products,
        "release_id": release_id,
        "required_disk_bytes": 0,
    }
    set_text, required_disk_bytes = _canonical_with_disk_total(set_manifest, base_bytes)
    try:
        output_path.write_text(set_text, encoding="utf-8", newline="\n")
    except OSError as error:
        raise CivError(f"cannot write participant-set manifest: {error}") from error
    return {
        "manifest": output_path.name,
        "manifest_sha256": file_sha256(output_path),
        "product_count": len(products),
        "required_disk_bytes": required_disk_bytes,
    }


def audit_participant_set(set_path: Path) -> dict[str, object]:
    document = read_json_file(set_path, "participant-set manifest")
    _closed(document, SET_FIELDS, "participant-set manifest")
    if document.get("contract") != SET_CONTRACT:
        raise CivError(f"participant-set manifest contract must be '{SET_CONTRACT}'")
    raw_products = document.get("products")
    if not isinstance(raw_products, list) or not raw_products:
        raise CivError("participant-set manifest products must be a non-empty list")
    serialized_set = canonical_json(document).lower()
    for term in FORBIDDEN_PARTICIPANT_TERMS:
        if term in serialized_set:
            raise CivError(f"participant-set manifest contains forbidden term '{term}'")

    total_bytes = set_path.stat().st_size
    audited_messages = 0
    audited_products = 0
    for index, raw_entry in enumerate(raw_products):
        entry = _mapping(raw_entry, f"participant-set product {index}")
        _closed(entry, SET_PRODUCT_FIELDS, f"participant-set product {index}")
        split = _string(entry.get("split"), f"participant-set product {index} split")
        if split not in {"warmup", "development"}:
            raise CivError("participant-set manifest contains a sealed or unknown split")
        product_name = _string(
            entry.get("name"), f"participant-set product {index} name"
        )
        manifest_name = _string(
            entry.get("manifest"), f"participant-set product {index} manifest"
        )
        if Path(product_name).name != product_name or Path(manifest_name).name != manifest_name:
            raise CivError("participant-set filenames must not contain paths")
        product_path = set_path.parent / product_name
        manifest_path = set_path.parent / manifest_name
        if not product_path.is_file() or not manifest_path.is_file():
            raise CivError(f"participant-set product files are incomplete for {product_name}")
        if file_sha256(product_path) != _sha256(
            entry.get("sha256"), f"participant-set product {index} sha256"
        ):
            raise CivError(f"participant product hash mismatch: {product_name}")
        if file_sha256(manifest_path) != _sha256(
            entry.get("manifest_sha256"),
            f"participant-set product {index} manifest_sha256",
        ):
            raise CivError(f"participant manifest hash mismatch: {manifest_name}")

        manifest = _load_manifest(manifest_path)
        serialized_manifest = canonical_json(manifest).lower()
        for term in FORBIDDEN_PARTICIPANT_TERMS:
            if term in serialized_manifest:
                raise CivError(f"participant manifest contains forbidden term '{term}'")
        product = _mapping(manifest.get("product"), "data-product manifest product")
        parent = _mapping(manifest.get("parent"), "data-product manifest parent")
        recipe = _mapping(manifest.get("recipe"), "data-product manifest recipe")
        provenance = _mapping(manifest.get("provenance"), "data-product manifest provenance")
        expected_topics = _string_list(
            recipe.get("topics"), "data-product manifest recipe topics"
        )
        if provenance.get("split") != split or parent.get("source_id") != entry.get("source_id"):
            raise CivError(f"participant manifest provenance mismatch: {manifest_name}")
        if product.get("name") != product_name or product.get("sha256") != entry.get("sha256"):
            raise CivError(f"participant manifest product mismatch: {manifest_name}")

        observed: dict[str, dict[str, Any]] = {}
        try:
            with product_path.open("rb") as stream:
                reader = make_reader(stream, validate_crcs=True)
                if any(reader.iter_attachments()) or any(reader.iter_metadata()):
                    raise CivError(
                        "participant product contains attachment or metadata records: "
                        f"{product_name}"
                    )
                for schema, channel, _message in reader.iter_messages():
                    audit_text = canonical_json(
                        {
                            "channel_metadata": channel.metadata,
                            "message_encoding": channel.message_encoding,
                            "schema_encoding": schema.encoding if schema else "",
                            "schema_name": schema.name if schema else "",
                            "topic": channel.topic,
                        }
                    ).lower()
                    for term in FORBIDDEN_PARTICIPANT_TERMS:
                        if term in audit_text:
                            raise CivError(
                                f"participant product metadata contains forbidden term '{term}'"
                            )
                    schema_hash = sha256(schema.data).hexdigest() if schema else ""
                    topic = observed.setdefault(
                        channel.topic,
                        {
                            "message_count": 0,
                            "message_encoding": channel.message_encoding,
                            "schema_encoding": schema.encoding if schema else "",
                            "schema_name": schema.name if schema else "",
                            "schema_sha256": schema_hash,
                            "topic": channel.topic,
                        },
                    )
                    topic["message_count"] += 1
                    audited_messages += 1
        except (OSError, McapError) as error:
            raise CivError(f"cannot audit participant product {product_name}: {error}") from error
        if sorted(observed) != sorted(expected_topics):
            raise CivError(f"participant product topic allowlist mismatch: {product_name}")
        expected_records = product.get("topics")
        if expected_records != [observed[topic] for topic in sorted(observed)]:
            raise CivError(f"participant product topic manifest mismatch: {product_name}")
        total_bytes += product_path.stat().st_size + manifest_path.stat().st_size
        audited_products += 1

    required_disk_bytes = document.get("required_disk_bytes")
    if required_disk_bytes != total_bytes:
        raise CivError(
            "participant-set required_disk_bytes does not match its products and manifests"
        )
    return {
        "message_count": audited_messages,
        "product_count": audited_products,
        "required_disk_bytes": total_bytes,
        "set_sha256": file_sha256(set_path),
        "valid": True,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m civ_workshop.data_products",
        description="Build deterministic organizer-owned participant data products",
    )
    commands = parser.add_subparsers(dest="command", required=True)
    build = commands.add_parser("build", help="filter one source MCAP using an exact recipe")
    build.add_argument("source", type=Path)
    build.add_argument("recipe", type=Path)
    build.add_argument("--output", type=Path, required=True)
    participant_set = commands.add_parser(
        "set", help="build a participant-safe aggregate manifest"
    )
    participant_set.add_argument("manifests", type=Path, nargs="+")
    participant_set.add_argument("--release-id", required=True)
    participant_set.add_argument("--output", type=Path, required=True)
    audit = commands.add_parser("audit", help="audit a participant release directory")
    audit.add_argument("set_manifest", type=Path)
    return parser


def main(argv: Sequence[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "build":
            result = build_data_product(args.source, args.recipe, args.output)
        elif args.command == "set":
            result = build_participant_set(args.manifests, args.output, args.release_id)
        else:
            result = audit_participant_set(args.set_manifest)
        print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    except CivError as error:
        print(f"data-products: {error}", file=sys.stderr)
        raise SystemExit(2) from None


if __name__ == "__main__":
    main()
