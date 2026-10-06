from __future__ import annotations

import re
from collections.abc import Mapping
from pathlib import Path
from typing import Any, cast

from civ_workshop.artifacts import (
    interval_from_mapping,
    read_json_file,
    require_mapping,
    require_string,
)
from civ_workshop.errors import CivError

SCORE_REFERENCE_CONTRACT = "civ.label-pack/v1alpha1"
SHA256_PATTERN = re.compile(r"[0-9a-f]{64}")
TEMPORAL_IOU_THRESHOLD = 0.5
SCORING_POLICY: dict[str, object] = {
    "assignment": "one_to_one_best",
    "duplicate_predictions": "false_positive",
    "metric": "f1",
    "temporal_iou_threshold": TEMPORAL_IOU_THRESHOLD,
}
REFERENCE_FIELDS = frozenset(
    {"contract", "data_gaps", "dataset", "labels", "provenance", "scoring", "source_sha256"}
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


def _closed(value: Mapping[str, object], allowed: frozenset[str], context: str) -> None:
    unknown = sorted(set(value) - allowed)
    if unknown:
        raise CivError(f"{context} has unknown field '{unknown[0]}'")


def _sha256(value: object, context: str) -> str:
    digest = require_string(value, context)
    if SHA256_PATTERN.fullmatch(digest) is None:
        raise CivError(f"{context} must be a lowercase SHA-256")
    return digest


def _integer(value: object, context: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise CivError(f"{context} must be a non-negative integer")
    return value


def _records(value: object, context: str) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        raise CivError(f"{context} must be a list")
    return [require_mapping(record, f"{context} {index}") for index, record in enumerate(value)]


def _validate_order_and_overlap(records: list[dict[str, object]], context: str) -> None:
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


def parse_reference_intervals(
    document: Mapping[str, object], *, context_name: str, labels_context: str, gaps_context: str
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    labels: list[dict[str, object]] = []
    label_ids: set[str] = set()
    for index, raw_label in enumerate(_records(document.get("labels"), labels_context)):
        context = f"label {index}"
        _closed(raw_label, LABEL_FIELDS, context)
        interval = interval_from_mapping(raw_label, context)
        label_id = require_string(raw_label.get("label_id"), f"{context} label_id")
        if label_id in label_ids:
            raise CivError(f"{context_name} contains duplicate label_id '{label_id}'")
        label_ids.add(label_id)
        labels.append(
            {"end_ns": interval.end_ns, "label_id": label_id, "start_ns": interval.start_ns}
        )
    _validate_order_and_overlap(labels, "labels")

    gaps: list[dict[str, object]] = []
    gap_ids: set[str] = set()
    for index, raw_gap in enumerate(_records(document.get("data_gaps"), gaps_context)):
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
                raise CivError(f"{context_name} contains duplicate gap_id '{gap_id}'")
            gap_ids.add(gap_id)
            normalized["gap_id"] = gap_id
        if "reason" in raw_gap:
            normalized["reason"] = require_string(raw_gap.get("reason"), f"{context} reason")
        gaps.append(normalized)
    _validate_order_and_overlap(gaps, "data_gaps")

    return labels, gaps


def validate_score_reference(document: Mapping[str, object]) -> dict[str, Any]:
    reference = {str(key): value for key, value in document.items()}
    _closed(reference, REFERENCE_FIELDS, "scoring reference")
    if reference.get("contract") != SCORE_REFERENCE_CONTRACT:
        raise CivError(
            f"unsupported scoring reference; expected '{SCORE_REFERENCE_CONTRACT}'"
        )
    dataset = require_string(reference.get("dataset"), "scoring reference dataset")
    source_sha256 = _sha256(
        reference.get("source_sha256"), "scoring reference source_sha256"
    )

    labels, gaps = parse_reference_intervals(
        reference, context_name="scoring reference",
        labels_context="scoring labels", gaps_context="scoring data gaps",
    )

    normalized_reference: dict[str, Any] = {
        "contract": SCORE_REFERENCE_CONTRACT,
        "data_gaps": gaps,
        "dataset": dataset,
        "labels": labels,
        "source_sha256": source_sha256,
    }
    provenance_value = reference.get("provenance")
    if provenance_value is not None:
        provenance = require_mapping(provenance_value, "scoring reference provenance")
        _closed(provenance, PROVENANCE_FIELDS, "scoring reference provenance")
        mapping = require_mapping(
            provenance.get("timestamp_mapping"), "scoring reference timestamp mapping"
        )
        _closed(mapping, TIMESTAMP_MAPPING_FIELDS, "scoring reference timestamp mapping")
        normalized_reference["provenance"] = {
            "product_manifest_sha256": _sha256(
                provenance.get("product_manifest_sha256"), "product manifest sha256"
            ),
            "source_id": require_string(provenance.get("source_id"), "source id"),
            "source_sha256": _sha256(provenance.get("source_sha256"), "source sha256"),
            "timestamp_mapping": {
                "kind": require_string(mapping.get("kind"), "timestamp mapping kind"),
                "product_message_end_ns": _integer(
                    mapping.get("product_message_end_ns"), "product message end"
                ),
                "product_message_start_ns": _integer(
                    mapping.get("product_message_start_ns"), "product message start"
                ),
                "source_message_end_ns": _integer(
                    mapping.get("source_message_end_ns"), "source message end"
                ),
                "source_message_start_ns": _integer(
                    mapping.get("source_message_start_ns"), "source message start"
                ),
                "writer": require_string(mapping.get("writer"), "timestamp mapping writer"),
            },
            "truth_contract": require_string(provenance.get("truth_contract"), "truth contract"),
            "truth_sha256": _sha256(provenance.get("truth_sha256"), "truth sha256"),
        }
    scoring_value = reference.get("scoring")
    if scoring_value is not None:
        scoring = require_mapping(scoring_value, "scoring reference policy")
        _closed(scoring, SCORING_FIELDS, "scoring reference policy")
        normalized_scoring = {field: scoring.get(field) for field in sorted(SCORING_FIELDS)}
        if normalized_scoring != SCORING_POLICY:
            raise CivError("label pack scoring policy does not match the evaluator")
        normalized_reference["scoring"] = normalized_scoring
    return normalized_reference


def load_score_reference(path: Path) -> dict[str, Any]:
    try:
        document = read_json_file(path, "label pack")
    except CivError as error:
        message = str(error)
        roots = {str(path.parent), str(path.parent.resolve())}
        for root in sorted(roots, key=len, reverse=True):
            if root not in {"", "."}:
                message = message.replace(root, "<scoring-reference>")
        raise CivError(message) from error
    return validate_score_reference(document)
