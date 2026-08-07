from __future__ import annotations

import time
import tracemalloc
from dataclasses import dataclass
from pathlib import Path
from typing import cast

from civ_workshop import __version__
from civ_workshop.artifacts import (
    canonical_json,
    file_sha256,
    read_json_file,
    require_mapping,
    require_string,
)
from civ_workshop.errors import CivError
from civ_workshop.intake import (
    TOKYO_CUTOFF,
    IntakeLedger,
    latest_receipt,
    open_validated_submission,
)
from civ_workshop.scoring import TEMPORAL_IOU_THRESHOLD, score_submission

BATCH_BUDGET_SECONDS = 45 * 60
SLOW_ENTRY_COUNT = 5
SCORER_VERSIONS = {
    "batch_contract": "civ.batch-result/v1alpha1",
    "metrics_contract": "civ.metrics/v1alpha1",
    "temporal_iou_threshold": TEMPORAL_IOU_THRESHOLD,
    "tool_version": __version__,
}


@dataclass(frozen=True)
class LabelPack:
    path: Path
    dataset: str
    sha256: str


@dataclass(frozen=True)
class EntryOutcome:
    status: str
    validation: str
    datasets: list[dict[str, object]]
    diagnostics: list[str]


def _load_label_packs(labels_root: Path) -> dict[str, LabelPack]:
    if not labels_root.is_dir():
        raise CivError(f"organizer label directory does not exist: {labels_root}")
    packs: dict[str, LabelPack] = {}
    for path in sorted(labels_root.glob("*.json")):
        pack = read_json_file(path, "label pack")
        if pack.get("contract") != "civ.label-pack/v1alpha1":
            raise CivError(f"unsupported label pack contract: {path.name}")
        source_sha256 = require_string(pack.get("source_sha256"), "label pack source_sha256")
        if source_sha256 in packs:
            raise CivError(f"two organizer label packs declare the same source: {source_sha256}")
        packs[source_sha256] = LabelPack(
            path=path,
            dataset=require_string(pack.get("dataset"), "label pack dataset"),
            sha256=file_sha256(path),
        )
    if not packs:
        raise CivError(f"no organizer label packs exist in {labels_root}")
    return packs


def _score_bundle(bundle_path: Path, packs: dict[str, LabelPack]) -> EntryOutcome:
    try:
        with open_validated_submission(bundle_path) as working:
            manifest = read_json_file(working / "run-manifest.json", "run manifest")
            source_sha256 = require_string(
                require_mapping(manifest.get("source"), "run manifest source").get("sha256"),
                "run manifest source sha256",
            )
            pack = packs.get(source_sha256)
            if pack is None:
                return EntryOutcome(
                    "failed",
                    "passed",
                    [],
                    [f"no organizer label pack matches the submission source {source_sha256}"],
                )
            try:
                metrics = score_submission(working, pack.path)
            except CivError as error:
                return EntryOutcome("failed", "passed", [], [str(error)])
            datasets = cast(list[dict[str, object]], metrics["datasets"])
            return EntryOutcome("scored", "passed", datasets, [])
    except CivError as error:
        return EntryOutcome("invalid", "failed", [], [str(error)])


def _redact(message: str, labels_root: Path) -> str:
    """Keep organizer label locations out of participant-visible diagnostics."""

    return message.replace(str(labels_root.resolve()), "<organizer-labels>").replace(
        str(labels_root), "<organizer-labels>"
    )


def _write_json_lines(path: Path, records: list[dict[str, object]]) -> None:
    text = "".join(f"{canonical_json(record)}\n" for record in records)
    try:
        path.write_text(text, encoding="utf-8", newline="\n")
    except OSError as error:
        raise CivError(f"cannot write batch result {path}: {error}") from error


def run_batch(ledger_root: Path, labels_root: Path, output_root: Path) -> dict[str, object]:
    packs = _load_label_packs(labels_root)
    ledger = IntakeLedger(ledger_root)
    receipts = ledger.receipts()
    identities = sorted({receipt.identity for receipt in receipts})
    if not identities:
        raise CivError(f"intake ledger holds no submissions: {ledger_root}")

    entries: list[dict[str, object]] = []
    timings: list[dict[str, object]] = []
    input_bytes = 0
    tracemalloc.start()
    started = time.perf_counter()
    for identity in identities:
        entry_started = time.perf_counter()
        receipt = latest_receipt(receipts, identity, "on_time")
        if receipt is None:
            receipt = latest_receipt(receipts, identity, "late")
            if receipt is None:
                raise CivError(f"intake ledger lost the receipts for identity: {identity}")
            outcome = EntryOutcome(
                "quarantined",
                "skipped",
                [],
                [f"no on-time submission exists for identity: {identity}"],
            )
        else:
            try:
                bundle_path = ledger.bundle_for(receipt)
                input_bytes += bundle_path.stat().st_size
                outcome = _score_bundle(bundle_path, packs)
            except CivError as error:
                outcome = EntryOutcome("invalid", "failed", [], [str(error)])
            except Exception as error:  # one entry must never stop the batch
                outcome = EntryOutcome(
                    "failed", "passed", [], [f"unexpected scorer failure: {error}"]
                )
        entries.append(
            {
                "bundle_sha256": receipt.bundle_sha256,
                "contract": "civ.batch-result/v1alpha1",
                "datasets": outcome.datasets,
                "delivery_id": receipt.delivery_id,
                "diagnostics": [
                    _redact(diagnostic, labels_root) for diagnostic in outcome.diagnostics
                ],
                "identity": identity,
                "received_at_original": receipt.received_at_original,
                "received_at_utc": receipt.received_at_utc,
                "scorer": SCORER_VERSIONS,
                "source": receipt.source,
                "status": outcome.status,
                "validation": outcome.validation,
            }
        )
        timings.append(
            {
                "elapsed_seconds": round(time.perf_counter() - entry_started, 6),
                "identity": identity,
                "status": outcome.status,
            }
        )
    total_elapsed = time.perf_counter() - started
    peak_traced_bytes = tracemalloc.get_traced_memory()[1]
    tracemalloc.stop()

    counts = {
        status: sum(1 for entry in entries if entry["status"] == status)
        for status in ("failed", "invalid", "quarantined", "scored")
    }
    datasets: dict[str, int] = {}
    for entry in entries:
        for dataset in cast(list[dict[str, object]], entry["datasets"]):
            name = str(dataset["dataset"])
            datasets[name] = datasets.get(name, 0) + 1
    summary: dict[str, object] = {
        "contract": "civ.batch-summary/v1alpha1",
        "counts": counts,
        "cutoff_utc": TOKYO_CUTOFF.isoformat(),
        "datasets": dict(sorted(datasets.items())),
        "entries": len(entries),
        "label_packs": [
            {"dataset": pack.dataset, "sha256": pack.sha256, "source_sha256": source_sha256}
            for source_sha256, pack in sorted(packs.items(), key=lambda item: item[1].dataset)
        ],
        "receipts": {
            "late": sum(1 for receipt in receipts if receipt.status == "late"),
            "on_time": sum(1 for receipt in receipts if receipt.status == "on_time"),
            "total": len(receipts),
        },
        "scorer": SCORER_VERSIONS,
    }

    try:
        output_root.mkdir(parents=True, exist_ok=True)
    except OSError as error:
        raise CivError(f"cannot create batch output directory: {error}") from error
    results_path = output_root / "results.jsonl"
    summary_path = output_root / "summary.json"
    _write_json_lines(results_path, entries)
    _write_json_lines(summary_path, [summary])

    performance: dict[str, object] = {
        "budget_seconds": BATCH_BUDGET_SECONDS,
        "contract": "civ.batch-performance/v1alpha1",
        "disk": {
            "input_bundle_bytes": input_bytes,
            "result_bytes": results_path.stat().st_size + summary_path.stat().st_size,
        },
        "entries": len(entries),
        # ponytail: tracemalloc counts Python allocations only; read peak RSS from the
        # container harness if the acceptance record ever needs true resident memory.
        "peak_traced_memory_bytes": peak_traced_bytes,
        "slowest_entries": sorted(
            timings, key=lambda item: (-cast(float, item["elapsed_seconds"]), str(item["identity"]))
        )[:SLOW_ENTRY_COUNT],
        "total_elapsed_seconds": round(total_elapsed, 6),
        "within_budget": total_elapsed <= BATCH_BUDGET_SECONDS,
    }
    _write_json_lines(output_root / "performance.json", [performance])
    return summary
