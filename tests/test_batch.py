from __future__ import annotations

import json
import socket
from collections.abc import Sequence
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import Any

import pytest

from civ_workshop.artifacts import canonical_json, file_sha256, read_json_file
from civ_workshop.batch import BATCH_BUDGET_SECONDS, run_batch
from civ_workshop.errors import CivError
from civ_workshop.intake import IntakeLedger
from civ_workshop.models import EventRecord, Interval
from civ_workshop.reporting import build_report_bundle
from civ_workshop.scoring import score_submission
from tests.helpers import (
    MICRO_REPORT,
    NANOSECONDS,
    MicroCase,
    create_micro_case,
    prepare_scored_submission,
    run_civ,
)

# Runtime-generated stand-ins for the two accepted dataset families. The real Kashiwa and
# French recordings stay outside the repository; only their contracts are exercised here.
DATASETS = {
    "kashiwa": ((0.0, 2.0, 2.0, 0.0, 0.0), 1 * NANOSECONDS, 2 * NANOSECONDS),
    "french": ((0.0, 0.0, 2.0, 2.0, 0.0), 2 * NANOSECONDS, 3 * NANOSECONDS),
    "unscored": ((0.0, 2.0, 2.0, 2.0, 0.0), 1 * NANOSECONDS, 3 * NANOSECONDS),
}
PROFILES = ("competent", "low_quality", "duplicate_heavy", "incomplete", "missed")
ON_TIME = "2026-09-03T12:20:00+09:00"
RESUBMITTED = "2026-09-03T12:29:59+09:00"
LATE = "2026-09-03T12:31:00+09:00"


@dataclass(frozen=True)
class Cohort:
    ledger: Path
    labels: Path
    output: Path
    status: dict[str, str]
    profile: dict[str, str]
    authoritative: dict[str, str]


def _label_pack(case: MicroCase, dataset: str, start_ns: int, end_ns: int) -> None:
    case.labels.write_text(
        canonical_json(
            {
                "contract": "civ.label-pack/v1alpha1",
                "data_gaps": [],
                "dataset": dataset,
                "labels": [
                    {"end_ns": end_ns, "label_id": f"{dataset}-turn-1", "start_ns": start_ns}
                ],
                "source_sha256": file_sha256(case.bag),
            }
        ),
        encoding="utf-8",
        newline="\n",
    )


def _intervals(profile: str, start_ns: int, end_ns: int) -> list[tuple[int, int]]:
    if profile == "competent":
        return [(start_ns, end_ns)]
    if profile == "low_quality":
        return [(start_ns + 200_000_000, end_ns + 200_000_000)]
    if profile == "duplicate_heavy":
        return [
            (start_ns + offset, end_ns + offset)
            for offset in (0, 10_000_000, 20_000_000, 30_000_000)
        ]
    if profile == "incomplete":
        return []
    return [(end_ns + 2 * NANOSECONDS, end_ns + 3 * NANOSECONDS)]


def _rewrite_events(working: Path, intervals: Sequence[tuple[int, int]]) -> None:
    manifest: dict[str, Any] = read_json_file(working / "run-manifest.json", "run manifest")
    source_sha256 = str(manifest["source"]["sha256"])
    spec_sha256 = str(manifest["spec"]["sha256"])
    records = sorted(
        (
            EventRecord(
                event_id=sha256(
                    f"{source_sha256}:{spec_sha256}:{start_ns}:{end_ns}".encode()
                ).hexdigest(),
                bag_sha256=source_sha256,
                spec_sha256=spec_sha256,
                interval=Interval(start_ns, end_ns),
                trigger_values={"signal": 2.0},
            )
            for start_ns, end_ns in intervals
        ),
        key=lambda record: (record.interval, record.event_id),
    )
    events_path = working / "events.jsonl"
    events_path.write_text(
        "".join(f"{canonical_json(record.as_dict())}\n" for record in records),
        encoding="utf-8",
        newline="\n",
    )
    manifest["events"] = {
        "count": len(records),
        "name": "events.jsonl",
        "sha256": file_sha256(events_path),
    }
    (working / "run-manifest.json").write_text(
        f"{canonical_json(manifest)}\n", encoding="utf-8", newline="\n"
    )


def _build_bundle(
    case: MicroCase, working: Path, marker: str, intervals: Sequence[tuple[int, int]]
) -> Path:
    _rewrite_events(working, intervals)
    (working / "report.md").write_text(
        f"{MICRO_REPORT}\nEntry: {marker}\n", encoding="utf-8", newline="\n"
    )
    score_submission(working, case.labels)
    build_report_bundle(working)
    return working / "submission.zip"


def _plan() -> list[tuple[str, str, str, str]]:
    """Identity, dataset, detector profile and expected terminal status for 30 entries."""

    entries: list[tuple[str, str, str, str]] = []
    for index in range(20):
        dataset = "kashiwa" if index % 2 == 0 else "french"
        entries.append((f"team-{index + 1:02d}", dataset, PROFILES[index % 5], "scored"))
    for index in range(20, 23):
        entries.append((f"team-{index + 1:02d}", "unscored", "competent", "failed"))
    for index in range(23, 26):
        entries.append((f"team-{index + 1:02d}", "kashiwa", "competent", "invalid"))
    for index in range(26, 30):
        entries.append((f"team-{index + 1:02d}", "french", "competent", "quarantined"))
    return entries


@pytest.fixture(scope="module")
def cohort(tmp_path_factory: pytest.TempPathFactory) -> Cohort:
    root = tmp_path_factory.mktemp("cohort")
    labels = root / "organizer-labels"
    labels.mkdir()
    cases: dict[str, tuple[MicroCase, Path, int, int]] = {}
    for dataset, (values, start_ns, end_ns) in DATASETS.items():
        case = create_micro_case(root / f"case-{dataset}", values)
        _label_pack(case, dataset, start_ns, end_ns)
        working = root / f"working-{dataset}"
        prepare_scored_submission(case, working)
        cases[dataset] = (case, working, start_ns, end_ns)
        if dataset != "unscored":
            (labels / f"{dataset}.json").write_bytes(case.labels.read_bytes())

    ledger = IntakeLedger(root / "intake")
    status: dict[str, str] = {}
    profile: dict[str, str] = {}
    authoritative: dict[str, str] = {}
    corrupted: list[str] = []
    for identity, dataset, profile_name, expected in _plan():
        case, working, start_ns, end_ns = cases[dataset]
        status[identity] = expected
        profile[identity] = profile_name
        missed = _intervals("missed", start_ns, end_ns)
        if identity == "team-01":
            # An earlier on-time bundle that the later resubmission must replace.
            superseded = _build_bundle(case, working, f"{identity}-first", missed)
            ledger.accept_online(
                identity=identity,
                received_at=ON_TIME,
                submitted_sha256=file_sha256(superseded),
                bundle_path=superseded,
                delivery_id=f"{identity}-superseded",
            )
        bundle = _build_bundle(case, working, identity, _intervals(profile_name, start_ns, end_ns))
        digest = file_sha256(bundle)
        accept = ledger.accept_online if int(identity[-2:]) % 2 else ledger.accept_local
        accept(
            identity=identity,
            received_at=LATE if expected == "quarantined" else RESUBMITTED,
            submitted_sha256=digest,
            bundle_path=bundle,
            delivery_id=f"{identity}-primary",
        )
        authoritative[identity] = digest
        if expected == "invalid":
            corrupted.append(digest)
        if identity == "team-02":
            # A late resubmission must never displace the authoritative on-time bundle.
            ignored = _build_bundle(case, working, f"{identity}-late", missed)
            ledger.accept_local(
                identity=identity,
                received_at=LATE,
                submitted_sha256=file_sha256(ignored),
                bundle_path=ignored,
                delivery_id=f"{identity}-late",
            )

    for digest in corrupted:
        (ledger.bundles_path / f"{digest}.zip").write_bytes(b"corrupted at rest")

    output = root / "results"
    run_batch(ledger.root, labels, output)
    return Cohort(
        ledger=ledger.root,
        labels=labels,
        output=output,
        status=status,
        profile=profile,
        authoritative=authoritative,
    )


def _results(output: Path) -> dict[str, dict[str, Any]]:
    lines = (output / "results.jsonl").read_text(encoding="utf-8").splitlines()
    records = [json.loads(line) for line in lines]
    assert [record["identity"] for record in records] == sorted(
        record["identity"] for record in records
    )
    return {str(record["identity"]): record for record in records}


def _summary(output: Path) -> dict[str, Any]:
    return dict(json.loads((output / "summary.json").read_text(encoding="utf-8")))


def _dataset_metrics(record: dict[str, Any]) -> dict[str, Any]:
    assert len(record["datasets"]) == 1
    return dict(record["datasets"][0])


def test_summary_accounts_for_every_cohort_entry_exactly_once(cohort: Cohort) -> None:
    summary = _summary(cohort.output)
    results = _results(cohort.output)

    assert summary["entries"] == 30
    assert len(results) == 30
    assert sum(summary["counts"].values()) == 30
    assert summary["counts"] == {"failed": 3, "invalid": 3, "quarantined": 4, "scored": 20}
    assert summary["datasets"] == {"french": 10, "kashiwa": 10}
    assert summary["receipts"] == {"late": 5, "on_time": 27, "total": 32}
    assert {identity: record["status"] for identity, record in results.items()} == cohort.status


def test_every_result_records_full_provenance_in_deterministic_order(cohort: Cohort) -> None:
    results = _results(cohort.output)
    record = results["team-01"]

    assert list(record) == sorted(record)
    assert record["bundle_sha256"] == cohort.authoritative["team-01"]
    assert record["received_at_original"] == RESUBMITTED
    assert record["received_at_utc"] == "2026-09-03T03:29:59+00:00"
    assert record["delivery_id"] == "team-01-primary"
    assert record["scorer"]["metrics_contract"] == "civ.metrics/v1"
    assert record["scorer"]["temporal_iou_threshold"] == 0.5
    assert record["scorer"]["tool_version"]
    assert record["validation"] == "passed"
    assert _dataset_metrics(record)["dataset"] == "kashiwa"


def test_only_the_authoritative_on_time_bundle_is_scored(cohort: Cohort) -> None:
    results = _results(cohort.output)

    assert results["team-02"]["bundle_sha256"] == cohort.authoritative["team-02"]
    assert results["team-02"]["status"] == "scored"
    quarantined = results["team-27"]
    assert quarantined["status"] == "quarantined"
    assert quarantined["validation"] == "skipped"
    assert quarantined["datasets"] == []
    assert "no on-time submission" in quarantined["diagnostics"][0]


def test_each_profile_is_scored_with_the_proven_evaluator_semantics(cohort: Cohort) -> None:
    results = _results(cohort.output)
    by_profile = {
        cohort.profile[identity]: _dataset_metrics(record)
        for identity, record in results.items()
        if record["status"] == "scored"
    }

    assert by_profile["competent"]["counts"] == {
        "false_negative": 0,
        "false_positive": 0,
        "true_positive": 1,
    }
    assert by_profile["competent"]["f1"] == 1.0
    assert by_profile["low_quality"]["match_quality"]["mean_temporal_iou"] == pytest.approx(
        2 / 3
    )
    assert by_profile["duplicate_heavy"]["precision"] == 0.25
    assert by_profile["duplicate_heavy"]["recall"] == 1.0
    assert by_profile["incomplete"]["counts"] == {
        "false_negative": 1,
        "false_positive": 0,
        "true_positive": 0,
    }
    assert by_profile["missed"]["counts"] == {
        "false_negative": 1,
        "false_positive": 1,
        "true_positive": 0,
    }


def test_failing_entries_reach_terminal_results_without_stopping_the_batch(
    cohort: Cohort,
) -> None:
    results = _results(cohort.output)
    unscored = results["team-21"]
    corrupt = results["team-24"]

    assert unscored["status"] == "failed"
    assert unscored["validation"] == "passed"
    assert unscored["datasets"] == []
    assert "no organizer label pack matches the submission source" in unscored["diagnostics"][0]
    assert corrupt["status"] == "invalid"
    assert corrupt["validation"] == "failed"
    assert "missing or corrupt" in corrupt["diagnostics"][0]
    assert all(not results[identity]["diagnostics"] for identity in ("team-01", "team-20"))


def test_organizer_labels_never_leak_into_the_batch_output(cohort: Cohort) -> None:
    emitted = "".join(
        (cohort.output / name).read_text(encoding="utf-8")
        for name in ("results.jsonl", "summary.json", "performance.json")
    )

    assert "kashiwa-turn-1" not in emitted
    assert "french-turn-1" not in emitted
    assert "organizer-labels" not in emitted
    assert str(cohort.labels) not in emitted
    assert "label_pack_sha256" not in emitted


def test_repeating_the_batch_reproduces_byte_identical_results(
    cohort: Cohort, tmp_path: Path
) -> None:
    repeat = tmp_path / "repeat"
    run_batch(cohort.ledger, cohort.labels, repeat)

    for name in ("results.jsonl", "summary.json"):
        assert (repeat / name).read_bytes() == (cohort.output / name).read_bytes()
    assert (repeat / "performance.json").is_file()


def test_performance_record_supports_the_lunch_window_budget(cohort: Cohort) -> None:
    performance = json.loads((cohort.output / "performance.json").read_text(encoding="utf-8"))

    assert performance["budget_seconds"] == BATCH_BUDGET_SECONDS == 2700
    assert performance["entries"] == 30
    assert performance["within_budget"] is True
    assert 0 < performance["total_elapsed_seconds"] < BATCH_BUDGET_SECONDS
    assert performance["peak_traced_memory_bytes"] > 0
    assert performance["disk"]["input_bundle_bytes"] > 0
    assert performance["disk"]["result_bytes"] > 0
    slowest = performance["slowest_entries"]
    assert len(slowest) == 5
    assert slowest == sorted(slowest, key=lambda item: -item["elapsed_seconds"])
    assert all({"elapsed_seconds", "identity", "status"} == set(entry) for entry in slowest)


def test_batch_opens_no_network_connection(
    cohort: Cohort, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def forbidden(*arguments: object, **keywords: object) -> None:
        raise AssertionError("the lunch batch must not touch the network")

    monkeypatch.setattr(socket, "socket", forbidden)
    monkeypatch.setattr(socket, "create_connection", forbidden)

    summary = run_batch(cohort.ledger, cohort.labels, tmp_path / "offline")

    assert summary["entries"] == 30


def test_one_command_scores_the_cohort_and_reports_missing_inputs(
    cohort: Cohort, tmp_path: Path
) -> None:
    result = run_civ(
        tmp_path,
        [
            "score-batch",
            "--ledger",
            str(cohort.ledger),
            "--labels",
            str(cohort.labels),
            "--output",
            str(tmp_path / "cli"),
        ],
    )

    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["counts"]["scored"] == 20

    empty = run_civ(
        tmp_path,
        [
            "score-batch",
            "--ledger",
            str(cohort.ledger),
            "--labels",
            str(tmp_path / "absent"),
            "--output",
            str(tmp_path / "cli-empty"),
        ],
    )

    assert empty.returncode == 2
    assert "organizer label directory does not exist" in empty.stderr


def test_batch_rejects_ambiguous_organizer_label_packs(cohort: Cohort, tmp_path: Path) -> None:
    labels = tmp_path / "ambiguous"
    labels.mkdir()
    for name in ("kashiwa.json", "kashiwa-copy.json"):
        (labels / name).write_bytes((cohort.labels / "kashiwa.json").read_bytes())

    with pytest.raises(CivError, match="same source"):
        run_batch(cohort.ledger, labels, tmp_path / "ambiguous-output")
