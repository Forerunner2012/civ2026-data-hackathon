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
    IntakeReceipt,
    latest_receipt,
    open_validated_submission,
)
from civ_workshop.label_packs import TEMPORAL_IOU_THRESHOLD, load_label_pack
from civ_workshop.organizer.scoring_readiness import check_readiness, require_official_readiness
from civ_workshop.scoring import score_submission

BATCH_BUDGET_SECONDS = 45 * 60
SLOW_ENTRY_COUNT = 5
SCORER_VERSIONS = {
    "batch_contract": "civ.batch-result/v1alpha1",
    "metrics_contract": "civ.metrics/v1",
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


@dataclass(frozen=True)
class RoutedReceipt:
    receipt: IntakeReceipt
    bundle_path: Path
    pack: LabelPack | None
    source_sha256: str | None
    diagnostic: str | None = None


def _load_label_packs(labels_root: Path) -> dict[str, LabelPack]:
    if not labels_root.is_dir():
        raise CivError(f"organizer label directory does not exist: {labels_root}")
    packs: dict[str, LabelPack] = {}
    for path in sorted(labels_root.glob("*.json")):
        try:
            pack = load_label_pack(path)
        except CivError as error:
            raise CivError(f"invalid organizer label pack {path.name}: {error}") from error
        source_sha256 = str(pack["source_sha256"])
        if source_sha256 in packs:
            raise CivError(f"two organizer label packs declare the same source: {source_sha256}")
        packs[source_sha256] = LabelPack(
            path=path,
            dataset=str(pack["dataset"]),
            sha256=file_sha256(path),
        )
    if not packs:
        raise CivError(f"no organizer label packs exist in {labels_root}")
    datasets = {pack.dataset for pack in packs.values()}
    if datasets != {"kashiwa", "reims"}:
        raise CivError(
            "organizer product mapping must contain exactly kashiwa and reims; "
            f"found: {', '.join(sorted(datasets)) or 'none'}"
        )
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


def _route_receipt(
    ledger: IntakeLedger, receipt: IntakeReceipt, packs: dict[str, LabelPack]
) -> RoutedReceipt:
    stored_source = receipt.source_sha256
    try:
        bundle_path = ledger.bundle_for(receipt)
        source_sha256 = stored_source
        if source_sha256 is None:
            with open_validated_submission(bundle_path) as working:
                manifest = read_json_file(working / "run-manifest.json", "run manifest")
                source_sha256 = require_string(
                    require_mapping(manifest.get("source"), "run manifest source").get("sha256"),
                    "run manifest source sha256",
                )
        return RoutedReceipt(
            receipt=receipt,
            bundle_path=bundle_path,
            pack=packs.get(source_sha256),
            source_sha256=source_sha256,
        )
    except CivError as error:
        return RoutedReceipt(
            receipt=receipt,
            bundle_path=ledger.bundles_path / f"{receipt.bundle_sha256}.zip",
            pack=packs.get(stored_source) if stored_source is not None else None,
            source_sha256=stored_source,
            diagnostic=str(error),
        )


def _component(
    dataset: str,
    routes: list[RoutedReceipt],
    packs: dict[str, LabelPack],
) -> tuple[dict[str, object], list[dict[str, object]], int]:
    on_time = latest_receipt(
        [route.receipt for route in routes],
        routes[0].receipt.identity if routes else "",
        "on_time",
    )
    if on_time is None:
        late = latest_receipt(
            [route.receipt for route in routes],
            routes[0].receipt.identity if routes else "",
            "late",
        )
        diagnostic = (
            f"no submission exists for dataset: {dataset}"
            if late is None
            else f"no on-time submission exists for dataset: {dataset}"
        )
        return (
            {
                "bundle_sha256": None,
                "dataset": dataset,
                "datasets": [],
                "delivery_id": None,
                "diagnostics": [diagnostic],
                "received_at_original": None,
                "received_at_utc": None,
                "source": None,
                "source_sha256": None,
                "status": "missing" if late is None else "late-only",
                "validation": "skipped",
            },
            [],
            0,
        )
    route = next(route for route in routes if route.receipt == on_time)
    if route.diagnostic is not None:
        return (
            {
                "bundle_sha256": on_time.bundle_sha256,
                "dataset": dataset,
                "datasets": [],
                "delivery_id": on_time.delivery_id,
                "diagnostics": [route.diagnostic],
                "received_at_original": on_time.received_at_original,
                "received_at_utc": on_time.received_at_utc,
                "source": on_time.source,
                "source_sha256": route.source_sha256,
                "status": "malformed",
                "validation": "failed",
            },
            [],
            0,
        )
    outcome = _score_bundle(route.bundle_path, packs)
    return (
        {
            "bundle_sha256": on_time.bundle_sha256,
            "dataset": dataset,
            "datasets": outcome.datasets,
            "delivery_id": on_time.delivery_id,
            "diagnostics": outcome.diagnostics,
            "received_at_original": on_time.received_at_original,
            "received_at_utc": on_time.received_at_utc,
            "source": on_time.source,
            "source_sha256": route.source_sha256,
            "status": outcome.status,
            "validation": outcome.validation,
        },
        outcome.datasets,
        route.bundle_path.stat().st_size,
    )


def _delivery_records(
    routes: list[RoutedReceipt], components: list[dict[str, object]]
) -> list[dict[str, object]]:
    authorities = {
        str(component["dataset"]): component
        for component in components
        if component["delivery_id"] is not None
    }
    deliveries: list[dict[str, object]] = []
    for route in routes:
        receipt = route.receipt
        dataset = route.pack.dataset if route.pack is not None else None
        authority = authorities.get(dataset or "")
        if route.diagnostic is not None:
            state = "malformed"
        elif dataset is None:
            state = "cross-dataset"
        elif authority is not None and receipt.delivery_id == authority["delivery_id"]:
            state = "authoritative"
        elif receipt.status == "late":
            state = "late-only"
        elif (
            authority is not None
            and receipt.source_sha256 == authority["source_sha256"]
            and receipt.bundle_sha256 == authority["bundle_sha256"]
        ):
            state = "duplicate-source"
        else:
            state = "superseded"
        deliveries.append(
            {
                "bundle_sha256": receipt.bundle_sha256,
                "dataset": dataset,
                "delivery_id": receipt.delivery_id,
                "received_at_original": receipt.received_at_original,
                "received_at_utc": receipt.received_at_utc,
                "source": receipt.source,
                "source_sha256": route.source_sha256,
                "state": state,
                "status": receipt.status,
            }
        )
    return deliveries


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


def run_batch(
    ledger_root: Path, labels_root: Path, output_root: Path,
    *, official: bool = False, plan_path: Path | None = None,
    preflight_path: Path | None = None, review_status_path: Path | None = None,
) -> dict[str, object]:
    readiness = check_readiness(
        ledger_root, plan_path=plan_path, preflight_path=preflight_path,
        review_status_path=review_status_path,
    )
    if official:
        require_official_readiness(readiness)
    packs = _load_label_packs(labels_root)
    ledger = IntakeLedger(ledger_root)
    receipts = ledger.receipts(read_only=True)
    identities = sorted({receipt.identity for receipt in receipts})
    if not identities:
        raise CivError(f"intake ledger holds no submissions: {ledger_root}")

    entries: list[dict[str, object]] = []
    timings: list[dict[str, object]] = []
    input_bytes = 0
    tracemalloc.start()
    started = time.perf_counter()
    expected_datasets = sorted({pack.dataset for pack in packs.values()})
    for identity in identities:
        entry_started = time.perf_counter()
        routes = [
            _route_receipt(ledger, receipt, packs)
            for receipt in receipts
            if receipt.identity == identity
        ]
        components: list[dict[str, object]] = []
        scored_datasets: list[dict[str, object]] = []
        for dataset in expected_datasets:
            dataset_routes = [
                route
                for route in routes
                if route.pack is not None and route.pack.dataset == dataset
            ]
            component, component_datasets, component_bytes = _component(
                dataset, dataset_routes, packs
            )
            components.append(component)
            scored_datasets.extend(component_datasets)
            input_bytes += component_bytes
        complete = all(component["status"] == "scored" for component in components)
        deliveries = _delivery_records(routes, components)
        diagnostics = [
            f"{component['dataset']}: {diagnostic}"
            for component in components
            for diagnostic in cast(list[str], component["diagnostics"])
        ]
        entries.append(
            {
                "components": components,
                "contract": "civ.batch-result/v1alpha1",
                "datasets": scored_datasets,
                "deliveries": deliveries,
                "diagnostics": [
                    _redact(diagnostic, labels_root) for diagnostic in diagnostics
                ],
                "identity": identity,
                "official_score": False,
                "scorer": SCORER_VERSIONS,
                "status": "complete" if complete else "incomplete",
            }
        )
        timings.append(
            {
                "elapsed_seconds": round(time.perf_counter() - entry_started, 6),
                "identity": identity,
                "status": "complete" if complete else "incomplete",
            }
        )
    total_elapsed = time.perf_counter() - started
    peak_traced_bytes = tracemalloc.get_traced_memory()[1]
    tracemalloc.stop()

    counts = {
        status: sum(1 for entry in entries if entry["status"] == status)
        for status in ("complete", "incomplete")
    }
    dataset_counts: dict[str, int] = {}
    for entry in entries:
        for dataset_metrics in cast(list[dict[str, object]], entry["datasets"]):
            name = str(dataset_metrics["dataset"])
            dataset_counts[name] = dataset_counts.get(name, 0) + 1
    summary: dict[str, object] = {
        "contract": "civ.batch-summary/v1alpha1",
        "counts": counts,
        "cutoff_utc": TOKYO_CUTOFF.isoformat(),
        "datasets": dict(sorted(dataset_counts.items())),
        "entries": len(entries),
        "official_score": False,
        "readiness": readiness,
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
