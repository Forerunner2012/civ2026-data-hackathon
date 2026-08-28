from __future__ import annotations

from pathlib import Path

from civ_workshop.artifacts import (
    canonical_json,
    file_sha256,
    interval_from_mapping,
    read_events,
    read_json_file,
    require_mapping,
    require_string,
)
from civ_workshop.contracts import require_run_contracts
from civ_workshop.errors import CivError
from civ_workshop.label_packs import TEMPORAL_IOU_THRESHOLD, load_label_pack
from civ_workshop.models import Interval


def _temporal_iou(left: Interval, right: Interval) -> float:
    intersection = max(0, min(left.end_ns, right.end_ns) - max(left.start_ns, right.start_ns))
    union = max(left.end_ns, right.end_ns) - min(left.start_ns, right.start_ns)
    return intersection / union


def _overlaps_gap(interval: Interval, gaps: list[Interval]) -> bool:
    return any(
        min(interval.end_ns, gap.end_ns) > max(interval.start_ns, gap.start_ns)
        for gap in gaps
    )


def score_submission(working: Path, labels_path: Path) -> dict[str, object]:
    if not working.is_dir():
        raise CivError(f"submission working directory does not exist: {working}")
    events = read_events(working / "events.jsonl")
    manifest = read_json_file(working / "run-manifest.json", "run manifest")
    require_run_contracts(manifest, [event.contract for event in events])
    source = require_mapping(manifest.get("source"), "run manifest source")
    submission_source_sha256 = require_string(
        source.get("sha256"), "run manifest source sha256"
    )
    label_pack = load_label_pack(labels_path)
    dataset = str(label_pack["dataset"])
    source_sha256 = str(label_pack["source_sha256"])
    if source_sha256 != submission_source_sha256:
        raise CivError("label pack source_sha256 does not match submission source sha256")
    for event in events:
        if event.bag_sha256 != submission_source_sha256:
            raise CivError(
                f"event {event.event_id} source does not match the submission source sha256"
            )
    raw_labels = label_pack.get("labels")
    if not isinstance(raw_labels, list):
        raise CivError("label pack labels must be a list")
    raw_gaps = label_pack.get("data_gaps")
    if not isinstance(raw_gaps, list):
        raise CivError("label pack data_gaps must be a list")

    all_predictions = [event.interval for event in events]
    all_expected = [
        interval_from_mapping(require_mapping(label, f"label {index}"), f"label {index}")
        for index, label in enumerate(raw_labels)
    ]
    gaps = [
        interval_from_mapping(require_mapping(gap, f"data gap {index}"), f"data gap {index}")
        for index, gap in enumerate(raw_gaps)
    ]
    predictions = [
        prediction
        for prediction in all_predictions
        if not _overlaps_gap(prediction, gaps)
    ]
    expected = [label for label in all_expected if not _overlaps_gap(label, gaps)]
    candidates: list[tuple[float, int, int]] = []
    for label_index, label in enumerate(expected):
        for prediction_index, prediction in enumerate(predictions):
            iou = _temporal_iou(label, prediction)
            if iou >= TEMPORAL_IOU_THRESHOLD:
                candidates.append((iou, label_index, prediction_index))
    candidates.sort(key=lambda item: (-item[0], item[1], item[2]))
    matched_labels: set[int] = set()
    matched_predictions: set[int] = set()
    matched_ious: list[float] = []
    for iou, label_index, prediction_index in candidates:
        if label_index in matched_labels or prediction_index in matched_predictions:
            continue
        matched_labels.add(label_index)
        matched_predictions.add(prediction_index)
        matched_ious.append(iou)

    true_positive = len(matched_labels)
    false_positive = len(predictions) - true_positive
    false_negative = len(expected) - true_positive
    precision = true_positive / len(predictions) if predictions else 0.0
    recall = true_positive / len(expected) if expected else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    counts = {
        "false_negative": false_negative,
        "false_positive": false_positive,
        "true_positive": true_positive,
    }
    match_quality = {
        "mean_temporal_iou": round(sum(matched_ious) / len(matched_ious), 12)
        if matched_ious
        else 0.0
    }
    aggregate: dict[str, object] = {
        "counts": counts,
        "f1": round(f1, 12),
        "match_quality": match_quality,
        "precision": round(precision, 12),
        "recall": round(recall, 12),
    }
    metrics: dict[str, object] = {
        "aggregate": aggregate,
        "contract": "civ.metrics/v1",
        "datasets": [
            {
                **aggregate,
                "dataset": dataset,
                "excluded": {
                    "data_gaps": len(gaps),
                    "labels": len(all_expected) - len(expected),
                    "predictions": len(all_predictions) - len(predictions),
                },
                "source_sha256": source_sha256,
            }
        ],
        "label_pack_sha256": file_sha256(labels_path),
        "matching": {
            "assignment": "one_to_one_best",
            "temporal_iou_threshold": TEMPORAL_IOU_THRESHOLD,
        },
    }
    metrics_path = working / "metrics.json"
    metrics_path.write_text(f"{canonical_json(metrics)}\n", encoding="utf-8", newline="\n")

    manifest_path = working / "run-manifest.json"
    manifest["metrics"] = {"name": "metrics.json", "sha256": file_sha256(metrics_path)}
    manifest_path.write_text(f"{canonical_json(manifest)}\n", encoding="utf-8", newline="\n")
    return metrics
