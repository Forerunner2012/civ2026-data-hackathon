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
from civ_workshop.errors import CivError
from civ_workshop.models import Interval


def _temporal_iou(left: Interval, right: Interval) -> float:
    intersection = max(0, min(left.end_ns, right.end_ns) - max(left.start_ns, right.start_ns))
    union = max(left.end_ns, right.end_ns) - min(left.start_ns, right.start_ns)
    if union == 0:
        return 1.0 if left == right else 0.0
    return intersection / union


def score_submission(working: Path, labels_path: Path) -> dict[str, object]:
    if not working.is_dir():
        raise CivError(f"submission working directory does not exist: {working}")
    events = read_events(working / "events.jsonl")
    label_pack = read_json_file(labels_path, "label pack")
    if label_pack.get("contract") != "civ.label-pack/v1alpha1":
        raise CivError("unsupported label pack contract")
    dataset = require_string(label_pack.get("dataset"), "label pack dataset")
    raw_labels = label_pack.get("labels")
    if not isinstance(raw_labels, list):
        raise CivError("label pack labels must be a list")

    predictions = [event.interval for event in events]
    expected = [
        interval_from_mapping(require_mapping(label, f"label {index}"), f"label {index}")
        for index, label in enumerate(raw_labels)
    ]
    candidates: list[tuple[float, int, int]] = []
    for label_index, label in enumerate(expected):
        for prediction_index, prediction in enumerate(predictions):
            iou = _temporal_iou(label, prediction)
            if iou >= 0.5:
                candidates.append((iou, label_index, prediction_index))
    candidates.sort(key=lambda item: (-item[0], item[1], item[2]))
    matched_labels: set[int] = set()
    matched_predictions: set[int] = set()
    for _, label_index, prediction_index in candidates:
        if label_index in matched_labels or prediction_index in matched_predictions:
            continue
        matched_labels.add(label_index)
        matched_predictions.add(prediction_index)

    true_positive = len(matched_labels)
    false_positive = len(predictions) - true_positive
    false_negative = len(expected) - true_positive
    precision = true_positive / len(predictions) if predictions else 0.0
    recall = true_positive / len(expected) if expected else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    metrics = {
        "contract": "civ.metrics/v1alpha1",
        "counts": {
            "false_negative": false_negative,
            "false_positive": false_positive,
            "true_positive": true_positive,
        },
        "dataset": dataset,
        "f1": round(f1, 12),
        "label_pack_sha256": file_sha256(labels_path),
        "matching": {"assignment": "one_to_one_best", "temporal_iou_threshold": 0.5},
        "precision": round(precision, 12),
        "recall": round(recall, 12),
    }
    metrics_path = working / "metrics.json"
    metrics_path.write_text(f"{canonical_json(metrics)}\n", encoding="utf-8", newline="\n")

    manifest_path = working / "run-manifest.json"
    manifest = read_json_file(manifest_path, "run manifest")
    manifest["metrics"] = {"name": "metrics.json", "sha256": file_sha256(metrics_path)}
    manifest_path.write_text(f"{canonical_json(manifest)}\n", encoding="utf-8", newline="\n")
    return metrics
