from __future__ import annotations

import json
import zipfile
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

from civ_workshop.artifacts import file_sha256
from civ_workshop.data_products import build_data_product
from civ_workshop.errors import CivError
from civ_workshop.label_packs import (
    SCORING_POLICY,
    audit_label_pack_set,
    build_label_packs,
    load_label_pack,
    validate_label_pack,
)
from civ_workshop.scoring import score_submission
from tests.helpers import create_micro_case, run_complete_workflow, write_micro_bag


def _write_json(path: Path, value: object) -> None:
    path.write_text(
        json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def _document(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def _product_case(root: Path, dataset: str = "kashiwa") -> tuple[Path, Path, Path]:
    root.mkdir()
    source_id = f"{dataset}-sealed-source"
    source = root / f"{source_id}.mcap"
    recipe = root / "recipe.json"
    truth = root / "truth.json"
    write_micro_bag(source)
    source_sha256 = file_sha256(source)
    _write_json(
        recipe,
        {
            "attribution": "Synthetic organizer fixture.",
            "contract": "civ.data-product-recipe/v1",
            "dataset": dataset,
            "license": {"name": "Test-only", "url": None},
            "modifications": ["Filtered to the full-rate signal topic."],
            "product_name": f"{source_id}-signals.mcap",
            "recipe_id": f"{dataset}-signals-v1",
            "rights_scope": "Test-only.",
            "source": {"id": source_id, "sha256": source_sha256},
            "split": "sealed",
            "topics": ["/micro/signal"],
            "version": 1,
        },
    )
    result = build_data_product(source, recipe, root / "products")
    manifest = root / "products" / str(result["manifest"])
    _write_json(
        truth,
        {
            "dataset": dataset,
            "exclusion_intervals": [
                {
                    "end_ns": 4_000_000_000,
                    "exclusion_id": f"{dataset}-gap-1",
                    "reason": "missing required localization topic",
                    "source_id": source_id,
                    "source_sha256": source_sha256,
                    "start_ns": 3_000_000_000,
                }
            ],
            "format": "civ.phase3.source-relative-truth/v1",
            "intervals": [
                {
                    "end_ns": 2_000_000_000,
                    "interval_id": f"{dataset}-turn-1",
                    "kind": "turn",
                    "source_id": source_id,
                    "source_sha256": source_sha256,
                    "start_ns": 1_000_000_000,
                }
            ],
            "quality": {"global_completeness_approved": True},
            "split": "sealed",
            "target": "turn",
        },
    )
    return source, manifest, truth


def _pack_path(output: Path) -> Path:
    packs = list((output / "packs").glob("*.json"))
    assert len(packs) == 1
    return packs[0]


def _working_submission(root: Path, product_sha256: str) -> Path:
    working = root / "working"
    working.mkdir()
    _write_json(
        working / "run-manifest.json",
        {
            "contract": "civ.run-manifest/v1",
            "source": {"name": "sealed-signals.mcap", "sha256": product_sha256},
        },
    )
    event = {
        "bag_sha256": product_sha256,
        "contract": "civ.event/v1",
        "end_ns": 2_000_000_000,
        "event_id": "participant-prediction",
        "spec_sha256": "2" * 64,
        "start_ns": 1_000_000_000,
        "trigger_values": {},
    }
    _write_json(working / "events.jsonl", event)
    return working


def test_build_is_deterministic_and_binds_truth_to_exact_product(
    tmp_path: Path,
) -> None:
    source, manifest_path, truth_path = _product_case(tmp_path / "case")
    first = tmp_path / "first"
    second = tmp_path / "second"

    first_result = build_label_packs([truth_path], [manifest_path], first)
    second_result = build_label_packs([truth_path], [manifest_path], second)

    assert first_result == second_result == {
        "data_gap_count": 1,
        "label_count": 1,
        "pack_count": 1,
        "set_sha256": file_sha256(first / "label-pack-set.json"),
    }
    assert (first / "label-pack-set.json").read_bytes() == (
        second / "label-pack-set.json"
    ).read_bytes()
    first_pack = _pack_path(first)
    second_pack = _pack_path(second)
    assert first_pack.name == second_pack.name
    assert first_pack.read_bytes() == second_pack.read_bytes()
    assert audit_label_pack_set(first / "label-pack-set.json") == {
        **first_result,
        "valid": True,
    }

    pack = load_label_pack(first_pack, require_provenance=True)
    manifest = _document(manifest_path)
    assert pack["source_sha256"] == manifest["product"]["sha256"]
    assert pack["labels"] == [
        {
            "end_ns": 2_000_000_000,
            "label_id": "kashiwa-turn-1",
            "start_ns": 1_000_000_000,
        }
    ]
    assert pack["data_gaps"] == [
        {
            "end_ns": 4_000_000_000,
            "gap_id": "kashiwa-gap-1",
            "reason": "missing required localization topic",
            "start_ns": 3_000_000_000,
        }
    ]
    assert pack["provenance"] == {
        "product_manifest_sha256": file_sha256(manifest_path),
        "source_id": "kashiwa-sealed-source",
        "source_sha256": file_sha256(source),
        "timestamp_mapping": {
            "kind": "identity-log-time-ns",
            "product_message_end_ns": 4_000_000_000,
            "product_message_start_ns": 0,
            "source_message_end_ns": 4_000_000_000,
            "source_message_start_ns": 0,
            "writer": "civ-workshop/data-products-v1",
        },
        "truth_contract": "civ.phase3.source-relative-truth/v1",
        "truth_sha256": file_sha256(truth_path),
    }
    assert pack["scoring"] == SCORING_POLICY


def test_final_pack_scores_without_leaking_truth_or_organizer_provenance(
    tmp_path: Path,
) -> None:
    _source, manifest_path, truth_path = _product_case(tmp_path / "case")
    output = tmp_path / "labels"
    build_label_packs([truth_path], [manifest_path], output)
    pack_path = _pack_path(output)
    pack = load_label_pack(pack_path, require_provenance=True)
    working = _working_submission(tmp_path, str(pack["source_sha256"]))

    metrics = score_submission(working, pack_path)

    assert metrics["aggregate"] == {
        "counts": {"false_negative": 0, "false_positive": 0, "true_positive": 1},
        "f1": 1.0,
        "match_quality": {"mean_temporal_iou": 1.0},
        "precision": 1.0,
        "recall": 1.0,
    }
    public_text = "".join(
        path.read_text(encoding="utf-8")
        for path in (
            working / "events.jsonl",
            working / "metrics.json",
            working / "run-manifest.json",
        )
    )
    provenance = pack["provenance"]
    for private_value in (
        "kashiwa-turn-1",
        "kashiwa-gap-1",
        provenance["source_id"],
        provenance["source_sha256"],
        provenance["truth_sha256"],
        str(output),
    ):
        assert str(private_value) not in public_text


@pytest.mark.parametrize(
    ("mutation", "diagnostic"),
    [
        (
            lambda truth: truth.__setitem__("format", "civ.phase3.source-relative-truth/v2"),
            "unsupported source-relative truth",
        ),
        (
            lambda truth: truth["intervals"][0].__setitem__("source_sha256", "0" * 64),
            "truth hash mismatch",
        ),
        (
            lambda truth: truth["intervals"][0].__setitem__(
                "end_ns", 5_000_000_000
            ),
            "outside parent bounds",
        ),
        (
            lambda truth: truth["intervals"].append(dict(truth["intervals"][0])),
            "duplicate interval identifiers",
        ),
    ],
)
def test_builder_rejects_bad_truth_before_creating_output(
    tmp_path: Path,
    mutation: Callable[[dict[str, Any]], None],
    diagnostic: str,
) -> None:
    _source, manifest_path, truth_path = _product_case(tmp_path / "case")
    truth = _document(truth_path)
    mutation(truth)
    _write_json(truth_path, truth)
    output = tmp_path / "labels"

    with pytest.raises(CivError, match=diagnostic):
        build_label_packs([truth_path], [manifest_path], output)

    assert not output.exists()


def test_builder_rejects_lossy_product_bounds_and_mixed_sources(
    tmp_path: Path,
) -> None:
    _source, manifest_path, truth_path = _product_case(tmp_path / "case")
    manifest = _document(manifest_path)
    manifest["product"]["message_start_ns"] = 1_500_000_000
    _write_json(manifest_path, manifest)

    with pytest.raises(CivError, match="reduced-product message_start_ns mismatch"):
        build_label_packs([truth_path], [manifest_path], tmp_path / "lossy")

    _source, second_manifest, _truth = _product_case(tmp_path / "other", "reims")
    with pytest.raises(CivError, match="truth and reduced-product datasets do not match"):
        build_label_packs([truth_path], [second_manifest], tmp_path / "mixed")
    assert not (tmp_path / "lossy").exists()
    assert not (tmp_path / "mixed").exists()


def test_label_pack_validator_closes_fields_and_scoring_policy() -> None:
    base: dict[str, Any] = {
        "contract": "civ.label-pack/v1alpha1",
        "data_gaps": [],
        "dataset": "kashiwa",
        "labels": [
            {"end_ns": 20, "label_id": "turn-1", "start_ns": 10},
            {"end_ns": 40, "label_id": "turn-2", "start_ns": 30},
        ],
        "source_sha256": "1" * 64,
    }
    assert validate_label_pack(base)["labels"] == base["labels"]

    unknown = {**base, "organizer_path": "private"}
    with pytest.raises(CivError, match="unknown field 'organizer_path'"):
        validate_label_pack(unknown)

    overlap = {
        **base,
        "labels": [
            *base["labels"],
            {"end_ns": 45, "label_id": "turn-3", "start_ns": 35},
        ],
    }
    with pytest.raises(CivError, match="labels must not overlap"):
        validate_label_pack(overlap)

    changed_policy = {**base, "scoring": {**SCORING_POLICY, "temporal_iou_threshold": 0.25}}
    with pytest.raises(CivError, match="scoring policy does not match"):
        validate_label_pack(changed_policy)


def test_scoring_rejects_policy_change_before_mutating_outputs(tmp_path: Path) -> None:
    _source, manifest_path, truth_path = _product_case(tmp_path / "case")
    output = tmp_path / "labels"
    build_label_packs([truth_path], [manifest_path], output)
    pack_path = _pack_path(output)
    pack = _document(pack_path)
    pack["scoring"]["temporal_iou_threshold"] = 0.25
    _write_json(pack_path, pack)
    product_sha256 = _document(manifest_path)["product"]["sha256"]
    working = _working_submission(tmp_path, product_sha256)
    prior_metrics = b"prior metrics remain intact\n"
    (working / "metrics.json").write_bytes(prior_metrics)
    manifest_before = (working / "run-manifest.json").read_bytes()

    with pytest.raises(CivError, match="scoring policy does not match"):
        score_submission(working, pack_path)

    assert (working / "metrics.json").read_bytes() == prior_metrics
    assert (working / "run-manifest.json").read_bytes() == manifest_before


def test_report_and_submission_bundle_do_not_embed_private_pack_fields(
    tmp_path: Path,
) -> None:
    case = create_micro_case(tmp_path / "case")
    pack = _document(case.labels)
    pack["provenance"] = {
        "product_manifest_sha256": "3" * 64,
        "source_id": "ORGANIZER-PRIVATE-SOURCE",
        "source_sha256": "4" * 64,
        "timestamp_mapping": {
            "kind": "identity-log-time-ns",
            "product_message_end_ns": 4_000_000_000,
            "product_message_start_ns": 0,
            "source_message_end_ns": 4_000_000_000,
            "source_message_start_ns": 0,
            "writer": "civ-workshop/data-products-v1",
        },
        "truth_contract": "civ.phase3.source-relative-truth/v1",
        "truth_sha256": "5" * 64,
    }
    pack["scoring"] = SCORING_POLICY
    _write_json(case.labels, pack)
    working = tmp_path / "working"

    result = run_complete_workflow(case, working)

    assert result.returncode == 0, result.stderr
    with zipfile.ZipFile(working / "submission.zip") as archive:
        public_bytes = b"".join(archive.read(name) for name in archive.namelist())
    public_bytes += (working / "report.md").read_bytes()
    for private_value in (
        b"turn-1",
        b"ORGANIZER-PRIVATE-SOURCE",
        b"4" * 64,
        b"5" * 64,
        str(case.labels).encode(),
    ):
        assert private_value not in public_bytes


def test_builder_rejects_existing_output_without_mutation(tmp_path: Path) -> None:
    _source, manifest_path, truth_path = _product_case(tmp_path / "case")
    output = tmp_path / "labels"
    output.mkdir()
    marker = output / "keep.txt"
    marker.write_bytes(b"unchanged\n")

    with pytest.raises(CivError, match="output already exists"):
        build_label_packs([truth_path], [manifest_path], output)

    assert marker.read_bytes() == b"unchanged\n"


def test_set_audit_rejects_pack_tampering(tmp_path: Path) -> None:
    _source, manifest_path, truth_path = _product_case(tmp_path / "case")
    output = tmp_path / "labels"
    build_label_packs([truth_path], [manifest_path], output)
    pack_path = _pack_path(output)
    pack_path.write_bytes(pack_path.read_bytes() + b" ")

    with pytest.raises(CivError, match="label-pack set hash mismatch"):
        audit_label_pack_set(output / "label-pack-set.json")


def test_label_pack_read_diagnostic_redacts_organizer_directory(tmp_path: Path) -> None:
    private = tmp_path / "private-organizer-labels"
    private.mkdir()
    path = private / "broken.json"
    path.write_text("not json\n", encoding="utf-8")

    with pytest.raises(CivError) as captured:
        load_label_pack(path)

    assert str(private) not in str(captured.value)
    assert "<organizer-labels>" in str(captured.value)
