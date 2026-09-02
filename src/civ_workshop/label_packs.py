from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
import tempfile
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast

from mcap.exceptions import McapError
from mcap.reader import make_reader

from civ_workshop.artifacts import (
    canonical_json,
    file_sha256,
    interval_from_mapping,
    read_json_file,
    require_mapping,
    require_string,
)
from civ_workshop.errors import CivError

LABEL_PACK_CONTRACT = "civ.label-pack/v1alpha1"
TRUTH_CONTRACT = "civ.phase3.source-relative-truth/v1"
SET_CONTRACT = "civ.phase3.label-pack-set/v1"
DATA_PRODUCT_CONTRACT = "civ.data-product-manifest/v1"
DATA_PRODUCT_RECIPE_CONTRACT = "civ.data-product-recipe/v1"
DATA_PRODUCT_WRITER = "civ-workshop/data-products-v1"
SHA256_PATTERN = re.compile(r"[0-9a-f]{64}")
TEMPORAL_IOU_THRESHOLD = 0.5
SCORING_POLICY: dict[str, object] = {
    "assignment": "one_to_one_best",
    "duplicate_predictions": "false_positive",
    "metric": "f1",
    "temporal_iou_threshold": TEMPORAL_IOU_THRESHOLD,
}

PACK_FIELDS = frozenset(
    {
        "contract",
        "data_gaps",
        "dataset",
        "labels",
        "provenance",
        "scoring",
        "source_sha256",
    }
)
LABEL_FIELDS = frozenset({"end_ns", "label_id", "start_ns"})
GAP_FIELDS = frozenset({"end_ns", "gap_id", "reason", "start_ns"})
PROVENANCE_FIELDS = frozenset(
    {
        "product_manifest_sha256",
        "source_id",
        "source_sha256",
        "timestamp_mapping",
        "truth_contract",
        "truth_sha256",
    }
)
TIMESTAMP_MAPPING_FIELDS = frozenset(
    {
        "kind",
        "product_message_end_ns",
        "product_message_start_ns",
        "source_message_end_ns",
        "source_message_start_ns",
        "writer",
    }
)
SCORING_FIELDS = frozenset(SCORING_POLICY)
SET_FIELDS = frozenset({"format", "packs", "scoring"})
SET_ENTRY_FIELDS = frozenset(
    {"data_gap_count", "dataset", "label_count", "name", "sha256", "source_sha256"}
)
MANIFEST_FIELDS = frozenset(
    {"contract", "parent", "product", "provenance", "recipe", "required_disk_bytes"}
)
PARENT_FIELDS = frozenset(
    {
        "byte_size",
        "duration_ns",
        "message_count",
        "message_end_ns",
        "message_start_ns",
        "sha256",
        "source_id",
    }
)
PRODUCT_FIELDS = frozenset(
    {
        "byte_size",
        "duration_ns",
        "message_count",
        "message_end_ns",
        "message_start_ns",
        "name",
        "sha256",
        "topics",
    }
)
PROVENANCE_MANIFEST_FIELDS = frozenset(
    {"attribution", "dataset", "license", "modifications", "rights_scope", "split"}
)
RECIPE_MANIFEST_FIELDS = frozenset(
    {"contract", "id", "sha256", "topics", "version", "writer"}
)


@dataclass(frozen=True)
class ProductBinding:
    dataset: str
    manifest_sha256: str
    parent_end_ns: int
    parent_start_ns: int
    product_end_ns: int
    product_name: str
    product_sha256: str
    product_start_ns: int
    source_id: str
    source_sha256: str


@dataclass(frozen=True)
class TruthInterval:
    end_ns: int
    interval_id: str
    reason: str | None
    source_id: str
    source_sha256: str
    start_ns: int


@dataclass(frozen=True)
class TruthDocument:
    contract: str
    dataset: str
    gaps: tuple[TruthInterval, ...]
    intervals: tuple[TruthInterval, ...]
    sha256: str


def _closed(value: Mapping[str, object], allowed: frozenset[str], context: str) -> None:
    unknown = sorted(set(value) - allowed)
    if unknown:
        raise CivError(f"{context} has unknown field '{unknown[0]}'")


def _sha256(value: object, context: str) -> str:
    digest = require_string(value, context)
    if SHA256_PATTERN.fullmatch(digest) is None:
        raise CivError(f"{context} must be a lowercase SHA-256")
    return digest


def _integer(value: object, context: str, *, positive: bool = False) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise CivError(f"{context} must be an integer")
    if value < (1 if positive else 0):
        qualifier = "positive" if positive else "non-negative"
        raise CivError(f"{context} must be {qualifier}")
    return value


def _records(value: object, context: str) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        raise CivError(f"{context} must be a list")
    return [require_mapping(record, f"{context} {index}") for index, record in enumerate(value)]


def _validate_order_and_overlap(
    records: list[dict[str, object]], context: str
) -> None:
    ordered = sorted(
        records,
        key=lambda record: (
            cast(int, record["start_ns"]),
            cast(int, record["end_ns"]),
            str(record.get("label_id", record.get("gap_id", ""))),
        ),
    )
    if records != ordered:
        raise CivError(f"label pack {context} must use deterministic interval order")
    for previous, current in zip(records, records[1:], strict=False):
        if cast(int, current["start_ns"]) < cast(int, previous["end_ns"]):
            raise CivError(f"label pack {context} must not overlap")


def validate_label_pack(
    document: Mapping[str, object], *, require_provenance: bool = False
) -> dict[str, Any]:
    pack = {str(key): value for key, value in document.items()}
    _closed(pack, PACK_FIELDS, "label pack")
    if pack.get("contract") != LABEL_PACK_CONTRACT:
        raise CivError(
            f"unsupported label pack contract; expected '{LABEL_PACK_CONTRACT}'"
        )
    dataset = require_string(pack.get("dataset"), "label pack dataset")
    source_sha256 = _sha256(pack.get("source_sha256"), "label pack source_sha256")

    labels: list[dict[str, object]] = []
    label_ids: set[str] = set()
    for index, raw_label in enumerate(_records(pack.get("labels"), "label pack labels")):
        context = f"label {index}"
        _closed(raw_label, LABEL_FIELDS, context)
        interval = interval_from_mapping(raw_label, context)
        label_id = require_string(raw_label.get("label_id"), f"{context} label_id")
        if label_id in label_ids:
            raise CivError(f"label pack contains duplicate label_id '{label_id}'")
        label_ids.add(label_id)
        labels.append(
            {
                "end_ns": interval.end_ns,
                "label_id": label_id,
                "start_ns": interval.start_ns,
            }
        )
    _validate_order_and_overlap(labels, "labels")

    gaps: list[dict[str, object]] = []
    gap_ids: set[str] = set()
    for index, raw_gap in enumerate(_records(pack.get("data_gaps"), "label pack data_gaps")):
        context = f"data gap {index}"
        _closed(raw_gap, GAP_FIELDS, context)
        interval = interval_from_mapping(raw_gap, context)
        normalized: dict[str, object] = {
            "end_ns": interval.end_ns,
            "start_ns": interval.start_ns,
        }
        if "gap_id" in raw_gap:
            gap_id = require_string(raw_gap.get("gap_id"), f"{context} gap_id")
            if gap_id in gap_ids:
                raise CivError(f"label pack contains duplicate gap_id '{gap_id}'")
            gap_ids.add(gap_id)
            normalized["gap_id"] = gap_id
        if "reason" in raw_gap:
            normalized["reason"] = require_string(raw_gap.get("reason"), f"{context} reason")
        gaps.append(normalized)
    _validate_order_and_overlap(gaps, "data_gaps")

    provenance_value = pack.get("provenance")
    provenance: dict[str, object] | None = None
    if provenance_value is not None:
        provenance_input = require_mapping(provenance_value, "label pack provenance")
        _closed(provenance_input, PROVENANCE_FIELDS, "label pack provenance")
        mapping_input = require_mapping(
            provenance_input.get("timestamp_mapping"),
            "label pack provenance timestamp_mapping",
        )
        _closed(
            mapping_input,
            TIMESTAMP_MAPPING_FIELDS,
            "label pack provenance timestamp_mapping",
        )
        kind = require_string(
            mapping_input.get("kind"), "label pack timestamp mapping kind"
        )
        writer = require_string(
            mapping_input.get("writer"), "label pack timestamp mapping writer"
        )
        if kind != "identity-log-time-ns" or writer != DATA_PRODUCT_WRITER:
            raise CivError("label pack declares an unsupported timestamp mapping")
        provenance = {
            "product_manifest_sha256": _sha256(
                provenance_input.get("product_manifest_sha256"),
                "label pack provenance product_manifest_sha256",
            ),
            "source_id": require_string(
                provenance_input.get("source_id"), "label pack provenance source_id"
            ),
            "source_sha256": _sha256(
                provenance_input.get("source_sha256"),
                "label pack provenance source_sha256",
            ),
            "timestamp_mapping": {
                "kind": kind,
                "product_message_end_ns": _integer(
                    mapping_input.get("product_message_end_ns"),
                    "label pack product_message_end_ns",
                ),
                "product_message_start_ns": _integer(
                    mapping_input.get("product_message_start_ns"),
                    "label pack product_message_start_ns",
                ),
                "source_message_end_ns": _integer(
                    mapping_input.get("source_message_end_ns"),
                    "label pack source_message_end_ns",
                ),
                "source_message_start_ns": _integer(
                    mapping_input.get("source_message_start_ns"),
                    "label pack source_message_start_ns",
                ),
                "writer": writer,
            },
            "truth_contract": require_string(
                provenance_input.get("truth_contract"),
                "label pack provenance truth_contract",
            ),
            "truth_sha256": _sha256(
                provenance_input.get("truth_sha256"),
                "label pack provenance truth_sha256",
            ),
        }
        if provenance["truth_contract"] != TRUTH_CONTRACT:
            raise CivError("label pack provenance names unsupported source-relative truth")
    elif require_provenance:
        raise CivError("final organizer label pack requires provenance")

    scoring_value = pack.get("scoring")
    scoring: dict[str, object] | None = None
    if scoring_value is not None:
        scoring_input = require_mapping(scoring_value, "label pack scoring")
        _closed(scoring_input, SCORING_FIELDS, "label pack scoring")
        scoring = {field: scoring_input.get(field) for field in sorted(SCORING_FIELDS)}
        if scoring != SCORING_POLICY:
            raise CivError("label pack scoring policy does not match the evaluator")
    elif require_provenance:
        raise CivError("final organizer label pack requires an explicit scoring policy")

    normalized_pack: dict[str, Any] = {
        "contract": LABEL_PACK_CONTRACT,
        "data_gaps": gaps,
        "dataset": dataset,
        "labels": labels,
        "source_sha256": source_sha256,
    }
    if provenance is not None:
        normalized_pack["provenance"] = provenance
    if scoring is not None:
        normalized_pack["scoring"] = scoring
    return normalized_pack


def load_label_pack(path: Path, *, require_provenance: bool = False) -> dict[str, Any]:
    try:
        document = read_json_file(path, "label pack")
    except CivError as error:
        message = str(error)
        roots = {str(path.parent), str(path.parent.resolve())}
        for root in sorted(roots, key=len, reverse=True):
            if root not in {"", "."}:
                message = message.replace(root, "<organizer-labels>")
        raise CivError(message) from error
    return validate_label_pack(document, require_provenance=require_provenance)


def _mcap_statistics(path: Path) -> dict[str, int]:
    try:
        with path.open("rb") as stream:
            reader = make_reader(stream, validate_crcs=True)
            summary = reader.get_summary()
            if summary is not None and summary.statistics is not None:
                statistics = summary.statistics
                return {
                    "duration_ns": statistics.message_end_time
                    - statistics.message_start_time,
                    "message_count": statistics.message_count,
                    "message_end_ns": statistics.message_end_time,
                    "message_start_ns": statistics.message_start_time,
                }
        start_ns: int | None = None
        end_ns: int | None = None
        message_count = 0
        with path.open("rb") as stream:
            for _, _, message in make_reader(stream, validate_crcs=True).iter_messages():
                message_count += 1
                start_ns = message.log_time if start_ns is None else min(start_ns, message.log_time)
                end_ns = message.log_time if end_ns is None else max(end_ns, message.log_time)
    except (OSError, McapError) as error:
        raise CivError(f"cannot inspect reduced product: {error}") from error
    if start_ns is None or end_ns is None:
        raise CivError("reduced product contains no messages")
    return {
        "duration_ns": end_ns - start_ns,
        "message_count": message_count,
        "message_end_ns": end_ns,
        "message_start_ns": start_ns,
    }


def _product_binding(path: Path) -> ProductBinding:
    manifest = read_json_file(path, "data-product manifest")
    _closed(manifest, MANIFEST_FIELDS, "data-product manifest")
    if manifest.get("contract") != DATA_PRODUCT_CONTRACT:
        raise CivError(f"unsupported data-product manifest: {path.name}")
    parent = require_mapping(manifest.get("parent"), "data-product manifest parent")
    product = require_mapping(manifest.get("product"), "data-product manifest product")
    provenance = require_mapping(
        manifest.get("provenance"), "data-product manifest provenance"
    )
    recipe = require_mapping(manifest.get("recipe"), "data-product manifest recipe")
    _closed(parent, PARENT_FIELDS, "data-product manifest parent")
    _closed(product, PRODUCT_FIELDS, "data-product manifest product")
    _closed(provenance, PROVENANCE_MANIFEST_FIELDS, "data-product manifest provenance")
    _closed(recipe, RECIPE_MANIFEST_FIELDS, "data-product manifest recipe")

    dataset = require_string(provenance.get("dataset"), "data-product manifest dataset")
    if dataset not in {"kashiwa", "reims"}:
        raise CivError(f"unsupported sealed dataset '{dataset}'")
    if provenance.get("split") != "sealed":
        raise CivError("label packs require sealed data-product manifests")
    if recipe.get("contract") != DATA_PRODUCT_RECIPE_CONTRACT:
        raise CivError("data-product manifest names an unsupported recipe contract")
    if recipe.get("writer") != DATA_PRODUCT_WRITER:
        raise CivError("data-product manifest does not prove identity timestamp preservation")

    product_name = require_string(product.get("name"), "data-product manifest product name")
    if Path(product_name).name != product_name or not product_name.endswith(".mcap"):
        raise CivError("data-product manifest product name must be a plain .mcap filename")
    product_path = path.parent / product_name
    if not product_path.is_file():
        raise CivError(f"reduced product does not exist beside its manifest: {product_name}")
    product_sha256 = _sha256(
        product.get("sha256"), "data-product manifest product sha256"
    )
    if file_sha256(product_path) != product_sha256:
        raise CivError(f"reduced-product SHA-256 mismatch: {product_name}")
    if product_path.stat().st_size != _integer(
        product.get("byte_size"), "data-product manifest product byte_size", positive=True
    ):
        raise CivError(f"reduced-product byte size mismatch: {product_name}")

    statistics = _mcap_statistics(product_path)
    for field, actual in statistics.items():
        expected = _integer(product.get(field), f"data-product manifest product {field}")
        if expected != actual:
            raise CivError(f"reduced-product {field} mismatch: {product_name}")

    parent_start_ns = _integer(
        parent.get("message_start_ns"), "data-product manifest parent message_start_ns"
    )
    parent_end_ns = _integer(
        parent.get("message_end_ns"), "data-product manifest parent message_end_ns"
    )
    if parent_end_ns < parent_start_ns:
        raise CivError("data-product manifest parent message bounds are reversed")
    return ProductBinding(
        dataset=dataset,
        manifest_sha256=file_sha256(path),
        parent_end_ns=parent_end_ns,
        parent_start_ns=parent_start_ns,
        product_end_ns=statistics["message_end_ns"],
        product_name=product_name,
        product_sha256=product_sha256,
        product_start_ns=statistics["message_start_ns"],
        source_id=require_string(parent.get("source_id"), "data-product manifest source_id"),
        source_sha256=_sha256(
            parent.get("sha256"), "data-product manifest parent sha256"
        ),
    )


def _truth_interval(
    record: Mapping[str, object], context: str, *, gap: bool
) -> TruthInterval:
    source_id = require_string(record.get("source_id"), f"{context} source_id")
    source_sha256 = _sha256(record.get("source_sha256"), f"{context} source_sha256")
    interval = interval_from_mapping(dict(record), context)
    identifier_field = "gap_id" if gap else "interval_id"
    alternate_field = "exclusion_id" if gap else identifier_field
    identifier = require_string(
        record.get(identifier_field, record.get(alternate_field)),
        f"{context} {identifier_field}",
    )
    reason_value = record.get("reason") if gap else None
    reason = require_string(reason_value, f"{context} reason") if reason_value is not None else None
    return TruthInterval(
        end_ns=interval.end_ns,
        interval_id=identifier,
        reason=reason,
        source_id=source_id,
        source_sha256=source_sha256,
        start_ns=interval.start_ns,
    )


def _truth_document(path: Path) -> TruthDocument:
    truth = read_json_file(path, "source-relative truth")
    if truth.get("format") != TRUTH_CONTRACT:
        raise CivError(f"unsupported source-relative truth: {path.name}")
    dataset = require_string(truth.get("dataset"), "source-relative truth dataset")
    if dataset not in {"kashiwa", "reims"}:
        raise CivError(f"unsupported source-relative truth dataset '{dataset}'")
    if truth.get("split") != "sealed":
        raise CivError("label packs require sealed source-relative truth")
    intervals = tuple(
        _truth_interval(record, f"truth interval {index}", gap=False)
        for index, record in enumerate(_records(truth.get("intervals"), "truth intervals"))
    )
    gaps = tuple(
        _truth_interval(record, f"truth exclusion {index}", gap=True)
        for index, record in enumerate(
            _records(truth.get("exclusion_intervals"), "truth exclusion_intervals")
        )
    )
    identifiers = [interval.interval_id for interval in (*intervals, *gaps)]
    if len(identifiers) != len(set(identifiers)):
        raise CivError("source-relative truth contains duplicate interval identifiers")
    return TruthDocument(
        contract=TRUTH_CONTRACT,
        dataset=dataset,
        gaps=gaps,
        intervals=intervals,
        sha256=file_sha256(path),
    )


def _group_truth(
    truth: TruthDocument, binding: ProductBinding
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    labels: list[dict[str, object]] = []
    gaps: list[dict[str, object]] = []
    for record, target in (
        *((record, labels) for record in truth.intervals),
        *((record, gaps) for record in truth.gaps),
    ):
        if record.source_id != binding.source_id:
            continue
        if record.source_sha256 != binding.source_sha256:
            raise CivError(
                f"source-relative truth hash mismatch for source {binding.source_id}"
            )
        if not (
            binding.parent_start_ns <= record.start_ns < record.end_ns <= binding.parent_end_ns
        ):
            raise CivError(
                f"source-relative interval is outside parent bounds: {record.interval_id}"
            )
        if not (
            binding.product_start_ns <= record.start_ns < record.end_ns <= binding.product_end_ns
        ):
            raise CivError(
                f"identity timestamp mapping is lossy for interval {record.interval_id}"
            )
        if target is labels:
            target.append(
                {
                    "end_ns": record.end_ns,
                    "label_id": record.interval_id,
                    "start_ns": record.start_ns,
                }
            )
        else:
            gap: dict[str, object] = {
                "end_ns": record.end_ns,
                "gap_id": record.interval_id,
                "start_ns": record.start_ns,
            }
            if record.reason is not None:
                gap["reason"] = record.reason
            target.append(gap)
    labels.sort(
        key=lambda item: (
            cast(int, item["start_ns"]),
            cast(int, item["end_ns"]),
            str(item["label_id"]),
        )
    )
    gaps.sort(
        key=lambda item: (
            cast(int, item["start_ns"]),
            cast(int, item["end_ns"]),
            str(item["gap_id"]),
        )
    )
    return labels, gaps


def _pack_document(binding: ProductBinding, truth: TruthDocument) -> dict[str, Any]:
    labels, gaps = _group_truth(truth, binding)
    document: dict[str, object] = {
        "contract": LABEL_PACK_CONTRACT,
        "data_gaps": gaps,
        "dataset": binding.dataset,
        "labels": labels,
        "provenance": {
            "product_manifest_sha256": binding.manifest_sha256,
            "source_id": binding.source_id,
            "source_sha256": binding.source_sha256,
            "timestamp_mapping": {
                "kind": "identity-log-time-ns",
                "product_message_end_ns": binding.product_end_ns,
                "product_message_start_ns": binding.product_start_ns,
                "source_message_end_ns": binding.parent_end_ns,
                "source_message_start_ns": binding.parent_start_ns,
                "writer": DATA_PRODUCT_WRITER,
            },
            "truth_contract": truth.contract,
            "truth_sha256": truth.sha256,
        },
        "scoring": SCORING_POLICY,
        "source_sha256": binding.product_sha256,
    }
    return validate_label_pack(document, require_provenance=True)


def build_label_packs(
    truth_paths: Sequence[Path],
    manifest_paths: Sequence[Path],
    output_directory: Path,
) -> dict[str, object]:
    if output_directory.exists():
        raise CivError(f"label-pack output already exists: {output_directory}")
    if not truth_paths or not manifest_paths:
        raise CivError("label-pack build requires truth and data-product manifests")

    truths = [_truth_document(path) for path in truth_paths]
    truth_by_dataset = {truth.dataset: truth for truth in truths}
    if len(truth_by_dataset) != len(truths):
        raise CivError("label-pack build contains duplicate truth datasets")
    bindings = [_product_binding(path) for path in manifest_paths]
    source_ids = [binding.source_id for binding in bindings]
    product_hashes = [binding.product_sha256 for binding in bindings]
    if len(source_ids) != len(set(source_ids)) or len(product_hashes) != len(set(product_hashes)):
        raise CivError("label-pack build contains duplicate source or product identities")
    if set(truth_by_dataset) != {binding.dataset for binding in bindings}:
        raise CivError("truth and reduced-product datasets do not match")

    known_sources = {binding.source_id: binding for binding in bindings}
    for truth in truths:
        for record in (*truth.intervals, *truth.gaps):
            binding = known_sources.get(record.source_id)
            if binding is None or binding.dataset != truth.dataset:
                raise CivError(
                    f"source-relative truth has no matching reduced product: {record.source_id}"
                )
            if binding.source_sha256 != record.source_sha256:
                raise CivError(
                    f"source-relative truth hash mismatch for source {record.source_id}"
                )

    packs = [
        (binding, _pack_document(binding, truth_by_dataset[binding.dataset]))
        for binding in sorted(bindings, key=lambda item: (item.dataset, item.product_sha256))
    ]
    try:
        output_directory.parent.mkdir(parents=True, exist_ok=True)
        staging = Path(
            tempfile.mkdtemp(
                prefix=f".{output_directory.name}.building-", dir=output_directory.parent
            )
        )
    except OSError as error:
        raise CivError(f"cannot prepare label-pack output: {error}") from error
    try:
        packs_directory = staging / "packs"
        packs_directory.mkdir()
        index_records: list[dict[str, object]] = []
        for binding, pack in packs:
            name = f"{binding.dataset}-{binding.product_sha256}.json"
            path = packs_directory / name
            path.write_text(f"{canonical_json(pack)}\n", encoding="utf-8", newline="\n")
            index_records.append(
                {
                    "data_gap_count": len(pack["data_gaps"]),
                    "dataset": binding.dataset,
                    "label_count": len(pack["labels"]),
                    "name": name,
                    "sha256": file_sha256(path),
                    "source_sha256": binding.product_sha256,
                }
            )
        index: dict[str, object] = {
            "format": SET_CONTRACT,
            "packs": index_records,
            "scoring": SCORING_POLICY,
        }
        index_path = staging / "label-pack-set.json"
        index_path.write_text(
            f"{canonical_json(index)}\n", encoding="utf-8", newline="\n"
        )
        staging.replace(output_directory)
    except (OSError, CivError) as error:
        shutil.rmtree(staging, ignore_errors=True)
        if isinstance(error, CivError):
            raise
        raise CivError(f"cannot write organizer label packs: {error}") from error

    final_index = output_directory / "label-pack-set.json"
    return {
        "data_gap_count": sum(len(pack["data_gaps"]) for _, pack in packs),
        "label_count": sum(len(pack["labels"]) for _, pack in packs),
        "pack_count": len(packs),
        "set_sha256": file_sha256(final_index),
    }


def audit_label_pack_set(index_path: Path) -> dict[str, object]:
    index = read_json_file(index_path, "label-pack set")
    _closed(index, SET_FIELDS, "label-pack set")
    if index.get("format") != SET_CONTRACT:
        raise CivError(f"unsupported label-pack set; expected '{SET_CONTRACT}'")
    scoring = require_mapping(index.get("scoring"), "label-pack set scoring")
    _closed(scoring, SCORING_FIELDS, "label-pack set scoring")
    if scoring != SCORING_POLICY:
        raise CivError("label-pack set scoring policy does not match the evaluator")
    entries = _records(index.get("packs"), "label-pack set packs")
    if not entries:
        raise CivError("label-pack set packs must not be empty")

    packs_directory = index_path.parent / "packs"
    if not packs_directory.is_dir():
        raise CivError("label-pack set packs directory does not exist")
    names: set[str] = set()
    sources: set[str] = set()
    label_count = 0
    data_gap_count = 0
    for entry_index, entry in enumerate(entries):
        context = f"label-pack set entry {entry_index}"
        _closed(entry, SET_ENTRY_FIELDS, context)
        name = require_string(entry.get("name"), f"{context} name")
        if Path(name).name != name or not name.endswith(".json"):
            raise CivError(f"{context} name must be a plain JSON filename")
        source_sha256 = _sha256(entry.get("source_sha256"), f"{context} source_sha256")
        if name in names or source_sha256 in sources:
            raise CivError("label-pack set contains a duplicate name or source")
        names.add(name)
        sources.add(source_sha256)
        pack_path = packs_directory / name
        if file_sha256(pack_path) != _sha256(entry.get("sha256"), f"{context} sha256"):
            raise CivError(f"label-pack set hash mismatch: {name}")
        pack = load_label_pack(pack_path, require_provenance=True)
        expected_labels = _integer(entry.get("label_count"), f"{context} label_count")
        expected_gaps = _integer(entry.get("data_gap_count"), f"{context} data_gap_count")
        if (
            entry.get("dataset") != pack["dataset"]
            or source_sha256 != pack["source_sha256"]
            or expected_labels != len(pack["labels"])
            or expected_gaps != len(pack["data_gaps"])
        ):
            raise CivError(f"label-pack set entry does not match pack: {name}")
        label_count += expected_labels
        data_gap_count += expected_gaps
    actual_names = {path.name for path in packs_directory.glob("*.json")}
    if actual_names != names:
        raise CivError("label-pack set does not account for every pack file")
    return {
        "data_gap_count": data_gap_count,
        "label_count": label_count,
        "pack_count": len(entries),
        "set_sha256": file_sha256(index_path),
        "valid": True,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m civ_workshop.label_packs",
        description="Build and audit product-bound organizer-only label packs",
    )
    commands = parser.add_subparsers(dest="command", required=True)
    build = commands.add_parser("build", help="emit packs from truth and product manifests")
    build.add_argument("--truth", type=Path, nargs="+", required=True)
    build.add_argument("--manifests", type=Path, nargs="+", required=True)
    build.add_argument("--output", type=Path, required=True)
    audit = commands.add_parser("audit", help="audit one emitted label-pack set")
    audit.add_argument("set_manifest", type=Path)
    return parser


def main(argv: Sequence[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "build":
            result = build_label_packs(args.truth, args.manifests, args.output)
        else:
            result = audit_label_pack_set(args.set_manifest)
        print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    except CivError as error:
        print(f"label-packs: {error}", file=sys.stderr)
        raise SystemExit(2) from None


if __name__ == "__main__":
    main()
