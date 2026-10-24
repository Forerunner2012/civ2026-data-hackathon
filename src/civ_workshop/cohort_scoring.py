from __future__ import annotations

import hashlib
import math
import os
import re
import shutil
import subprocess
import sys
from collections.abc import Sequence
from datetime import datetime, timezone
from decimal import ROUND_HALF_EVEN, ROUND_HALF_UP, Decimal
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any, TypeGuard, cast

from mcap.exceptions import McapError
from mcap.reader import make_reader

from civ_workshop.artifacts import (
    canonical_json,
    file_sha256,
    read_json_file,
    require_mapping,
    require_string,
)
from civ_workshop.errors import CivError
from civ_workshop.event_spec import load_event_spec
from civ_workshop.intake import IntakeLedger, IntakeReceipt, open_validated_submission
from civ_workshop.label_packs import load_label_pack
from civ_workshop.reporting import submission_spec_path
from civ_workshop.resources import load_point_resources
from civ_workshop.runtime_identity import runtime_metadata
from civ_workshop.scoring import score_submission

PLAN_CONTRACT = "civ.evaluation-plan/v1alpha2"
RESULTS_CONTRACT = "civ.cohort-results/v1alpha1"
SUMMARY_CONTRACT = "civ.cohort-summary/v1alpha1"
_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,99}\Z")
_SHA256 = re.compile(r"[0-9a-f]{64}\Z")
PARTITIONS = frozenset({"warmup", "development", "sealed"})


def _closed(value: dict[str, Any], fields: set[str], context: str) -> None:
    unknown = sorted(set(value) - fields)
    if unknown:
        raise CivError(f"{context} has unknown field '{unknown[0]}'")


def _identifier(value: object, context: str) -> str:
    result = require_string(value, context)
    if _ID.fullmatch(result) is None:
        raise CivError(f"{context} must be a plain identifier")
    return result


def _sha(value: object, context: str) -> str:
    digest = require_string(value, context)
    if _SHA256.fullmatch(digest) is None:
        raise CivError(f"{context} must be a lowercase SHA-256")
    return digest


def _relative_or_absolute(base: Path, value: object, context: str) -> Path:
    raw = Path(require_string(value, context))
    return raw.resolve() if raw.is_absolute() else (base / raw).resolve()


def _parse_timestamp(value: object, context: str) -> datetime:
    text = require_string(value, context)
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError as error:
        raise CivError(f"{context} must be an ISO-8601 timestamp") from error
    if parsed.tzinfo is None:
        raise CivError(f"{context} must include a timezone")
    return parsed.astimezone(timezone.utc)


def load_evaluation_plan(path: Path) -> dict[str, Any]:
    return validate_evaluation_plan(read_json_file(path, "evaluation plan"))


def validate_evaluation_plan(plan: dict[str, Any]) -> dict[str, Any]:
    if plan.get("contract") != PLAN_CONTRACT:
        raise CivError(f"cohort replay requires contract '{PLAN_CONTRACT}'")
    _closed(
        plan,
        {
            "contract",
            "session_id",
            "cutoff",
            "participants",
            "tracks",
            "scoring_policy",
        },
        "evaluation plan",
    )
    require_string(plan.get("session_id"), "evaluation plan session_id")
    _parse_timestamp(plan.get("cutoff"), "evaluation plan cutoff")
    participants_value = plan.get("participants")
    if not isinstance(participants_value, list) or not participants_value:
        raise CivError("evaluation plan participants must be a non-empty identity list")
    participants = [_identifier(value, "participant identity") for value in participants_value]
    if len(set(participants)) != len(participants):
        raise CivError("evaluation plan participants must not repeat identities")
    tracks = plan.get("tracks")
    if not isinstance(tracks, list) or not tracks:
        raise CivError("evaluation plan tracks must be a non-empty list")
    track_ids: set[str] = set()
    for track_index, track_value in enumerate(tracks):
        track = require_mapping(track_value, f"evaluation plan track {track_index}")
        _closed(track, {"track_id", "dataset", "target", "replay", "products"}, "track")
        track_id = _identifier(track.get("track_id"), "track_id")
        if track_id in track_ids:
            raise CivError(f"evaluation plan repeats track_id '{track_id}'")
        track_ids.add(track_id)
        require_string(track.get("dataset"), f"track {track_id} dataset")
        require_string(track.get("target"), f"track {track_id} target")
        replay = require_mapping(track.get("replay"), f"track {track_id} replay")
        _closed(
            replay,
            {
                "event_spec_contracts",
                "allowed_topics",
                "resource_limits",
                "timeout_seconds",
                "retries",
            },
            f"track {track_id} replay",
        )
        contracts = replay.get("event_spec_contracts")
        topics = replay.get("allowed_topics")
        if (
            not isinstance(contracts, list)
            or not contracts
            or any(not isinstance(x, str) or not x for x in contracts)
        ):
            raise CivError(f"track {track_id} event_spec_contracts must be a non-empty list")
        if (
            not isinstance(topics, list)
            or not topics
            or any(not isinstance(x, str) or not x for x in topics)
        ):
            raise CivError(f"track {track_id} allowed_topics must be a non-empty string list")
        if len(set(topics)) != len(topics):
            raise CivError(f"track {track_id} allowed_topics must not contain duplicates")
        limits = require_mapping(replay.get("resource_limits"), f"track {track_id} resource_limits")
        _closed(limits, {"max_files", "max_bytes"}, f"track {track_id} resource_limits")
        _nonnegative_integer(limits.get("max_files"), f"track {track_id} max_files")
        _nonnegative_integer(limits.get("max_bytes"), f"track {track_id} max_bytes")
        timeout = replay.get("timeout_seconds")
        if not _finite_number(timeout) or timeout <= 0:
            raise CivError(f"track {track_id} timeout_seconds must be a positive finite number")
        _nonnegative_integer(replay.get("retries"), f"track {track_id} retries")
        products = track.get("products")
        if not isinstance(products, list) or not products:
            raise CivError(f"track {track_id} products must be a non-empty list")
        product_ids: set[str] = set()
        source_hashes: set[str] = set()
        for product_index, product_value in enumerate(products):
            product = require_mapping(product_value, f"track {track_id} product {product_index}")
            _closed(
                product,
                {"product_id", "partition", "recording", "manifest", "truth", "input_contract"},
                "product",
            )
            product_id = _identifier(product.get("product_id"), "product_id")
            if product_id in product_ids:
                raise CivError(f"track {track_id} repeats product_id '{product_id}'")
            product_ids.add(product_id)
            if product.get("partition") not in PARTITIONS:
                raise CivError(
                    f"product {product_id} partition must be warmup, development, or sealed"
                )
            for ref_name in ("recording", "manifest", "truth"):
                ref = require_mapping(product.get(ref_name), f"product {product_id} {ref_name}")
                _closed(ref, {"path", "sha256"}, f"product {product_id} {ref_name}")
                require_string(ref.get("path"), f"product {product_id} {ref_name} path")
                _sha(ref.get("sha256"), f"product {product_id} {ref_name} sha256")
            source_hash = product["recording"]["sha256"]
            if source_hash in source_hashes:
                raise CivError(f"track {track_id} repeats a recording source")
            source_hashes.add(source_hash)
            contract = require_mapping(
                product.get("input_contract"), f"product {product_id} input_contract"
            )
            _closed(contract, {"topics", "schemas"}, f"product {product_id} input_contract")
            expected_topics = contract.get("topics")
            schemas = contract.get("schemas")
            if (
                not isinstance(expected_topics, list)
                or not expected_topics
                or any(not isinstance(item, str) or not item for item in expected_topics)
            ):
                raise CivError(
                    f"product {product_id} input_contract topics must be a non-empty string list"
                )
            if len(set(expected_topics)) != len(expected_topics):
                raise CivError(
                    f"product {product_id} input_contract topics must not contain duplicates"
                )
            if not isinstance(schemas, list):
                raise CivError(f"product {product_id} input_contract schemas must be a list")
            schema_topics: set[str] = set()
            for schema in schemas:
                record = require_mapping(schema, f"product {product_id} schema")
                _closed(
                    record,
                    {
                        "topic",
                        "schema_name",
                        "schema_encoding",
                        "schema_sha256",
                        "message_encoding",
                    },
                    "schema binding",
                )
                for field in ("topic", "schema_name", "schema_encoding", "message_encoding"):
                    value = record.get(field)
                    if not isinstance(value, str) or (
                        field in {"topic", "message_encoding"} and not value.strip()
                    ):
                        raise CivError(f"product {product_id} schema {field} must be a string")
                topic = cast(str, record["topic"])
                if topic in schema_topics:
                    raise CivError(f"product {product_id} repeats a schema binding for {topic}")
                schema_topics.add(topic)
                schema_digest = record.get("schema_sha256")
                if schema_digest != "":
                    _sha(schema_digest, f"product {product_id} schema sha256")
            if schema_topics != set(expected_topics):
                raise CivError(
                    f"product {product_id} input_contract must bind every configured topic schema"
                )
    if "scoring_policy" in plan:
        scoring_policy = require_mapping(plan["scoring_policy"], "evaluation plan scoring_policy")
        _closed(
            scoring_policy,
            {
                "temporal_iou_threshold",
                "matching",
                "product_weights",
                "score_bearing_partitions",
                "missing_track",
                "failed_run",
                "empty_truth",
                "cross_product_events",
                "rounding",
                "receipt_timestamp_ties",
                "detection_points",
                "bonus_points",
                "manual_review",
                "evidence_policy_id",
                "reproducibility_policy_id",
            },
            "evaluation plan scoring_policy",
        )
    return plan


def _nonnegative_integer(value: object, context: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise CivError(f"{context} must be a non-negative integer")
    return value


def _finite_number(value: object) -> TypeGuard[int | float]:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return False
    try:
        return math.isfinite(float(value))
    except OverflowError:
        return False


def _plan_path(base: Path, reference: dict[str, Any], context: str) -> Path:
    return _relative_or_absolute(base, reference.get("path"), f"{context} path")


def _actual_topic_contract(recording_path: Path, topics: set[str]) -> dict[str, dict[str, str]]:
    observed: dict[str, dict[str, str]] = {}
    try:
        with recording_path.open("rb") as stream:
            reader = make_reader(stream, validate_crcs=True)
            for schema, channel, _message in reader.iter_messages(topics=sorted(topics)):
                signature = {
                    "topic": channel.topic,
                    "schema_name": schema.name if schema is not None else "",
                    "schema_encoding": schema.encoding if schema is not None else "",
                    "schema_sha256": hashlib.sha256(schema.data).hexdigest()
                    if schema is not None
                    else "",
                    "message_encoding": channel.message_encoding,
                }
                existing = observed.get(channel.topic)
                if existing is not None and existing != signature:
                    raise CivError(f"product topic {channel.topic} changes schema or encoding")
                observed[channel.topic] = signature
    except CivError:
        raise
    except (OSError, McapError) as error:
        raise CivError(f"cannot validate product {recording_path.name} input schemas") from error
    missing = sorted(topics - set(observed))
    if missing:
        raise CivError(f"product is missing configured topics: {', '.join(missing)}")
    return observed


def validate_product(track: dict[str, Any], product: dict[str, Any], base: Path) -> dict[str, Any]:
    product_id = str(product["product_id"])
    recording = require_mapping(product["recording"], f"product {product_id} recording")
    manifest_ref = require_mapping(product["manifest"], f"product {product_id} manifest")
    truth_ref = require_mapping(product["truth"], f"product {product_id} truth")
    recording_path = _plan_path(base, recording, f"product {product_id} recording")
    manifest_path = _plan_path(base, manifest_ref, f"product {product_id} manifest")
    truth_path = _plan_path(base, truth_ref, f"product {product_id} truth")
    for path, ref, context in (
        (recording_path, recording, "recording"),
        (manifest_path, manifest_ref, "manifest"),
        (truth_path, truth_ref, "truth"),
    ):
        if not path.is_file():
            raise CivError(f"product {product_id} {context} does not exist")
        if file_sha256(path) != ref["sha256"]:
            raise CivError(f"product {product_id} {context} hash does not match plan")
    manifest = read_json_file(manifest_path, f"product {product_id} manifest")
    if manifest.get("contract") != "civ.data-product-manifest/v1":
        raise CivError(f"product {product_id} has an unsupported data-product manifest")
    manifest_product = require_mapping(
        manifest.get("product"), f"product {product_id} manifest product"
    )
    provenance = require_mapping(
        manifest.get("provenance"), f"product {product_id} manifest provenance"
    )
    byte_size = manifest_product.get("byte_size")
    if (
        isinstance(byte_size, bool)
        or not isinstance(byte_size, int)
        or manifest_product.get("name") != recording_path.name
        or manifest_product.get("sha256") != recording["sha256"]
    ):
        raise CivError(f"product {product_id} recording does not match manifest")
    try:
        if recording_path.stat().st_size != byte_size:
            raise CivError(f"product {product_id} recording size does not match manifest")
    except OSError as error:
        raise CivError(f"cannot inspect product {product_id} recording: {error}") from error
    if (
        provenance.get("dataset") != track["dataset"]
        or provenance.get("split") != product["partition"]
    ):
        raise CivError(f"product {product_id} dataset or partition does not match plan")
    expected_topics = set(cast(list[str], product["input_contract"]["topics"]))
    raw_manifest_topics = manifest_product.get("topics")
    if not isinstance(raw_manifest_topics, list):
        raise CivError(f"product {product_id} manifest topics must be a list")
    if any(not isinstance(item, dict) for item in raw_manifest_topics):
        raise CivError(f"product {product_id} manifest topics must contain objects")
    manifest_topics = require_mapping(
        {
            str(item.get("topic")): item
            for item in raw_manifest_topics
            if isinstance(item.get("topic"), str)
        },
        f"product {product_id} manifest topics",
    )
    if len(manifest_topics) != len(raw_manifest_topics):
        raise CivError(f"product {product_id} manifest repeats a topic")
    if not expected_topics.issubset(manifest_topics):
        raise CivError(f"product {product_id} manifest omits a configured topic")
    for schema in cast(list[dict[str, Any]], product["input_contract"]["schemas"]):
        actual = manifest_topics.get(schema["topic"])
        if not isinstance(actual, dict) or any(
            actual.get(field) != schema.get(field)
            for field in ("schema_name", "schema_encoding", "schema_sha256", "message_encoding")
        ):
            raise CivError(f"product {product_id} schema binding does not match manifest")
    actual_contract = _actual_topic_contract(recording_path, expected_topics)
    for schema in cast(list[dict[str, Any]], product["input_contract"]["schemas"]):
        actual = actual_contract.get(schema["topic"])
        if actual != schema:
            raise CivError(f"product {product_id} schema binding does not match recording")
    label_pack = load_label_pack(truth_path)
    if (
        label_pack["dataset"] != track["dataset"]
        or label_pack["source_sha256"] != recording["sha256"]
    ):
        raise CivError(f"product {product_id} truth does not match dataset and recording")
    return {
        "recording_path": recording_path,
        "manifest_path": manifest_path,
        "truth_path": truth_path,
        "manifest": manifest,
        "recording_sha256": recording["sha256"],
        "manifest_sha256": manifest_ref["sha256"],
        "truth_sha256": truth_ref["sha256"],
        "truth_count": len(label_pack["labels"]),
    }


def _select_receipt(
    receipts: list[IntakeReceipt],
    identity: str,
    track_id: str,
    cutoff: datetime,
    *,
    timestamp_tie_break: str | None = None,
) -> tuple[IntakeReceipt | None, bool]:
    candidates: list[tuple[int, IntakeReceipt]] = []
    late_found = False
    for index, receipt in enumerate(receipts):
        if receipt.identity != identity or receipt.track_id != track_id:
            continue
        received_at = _parse_timestamp(receipt.received_at_utc, "receipt received_at_utc")
        if received_at <= cutoff:
            candidates.append((index, receipt))
        else:
            late_found = True
    if not candidates:
        return None, late_found
    latest_time = max(
        _parse_timestamp(item[1].received_at_utc, "receipt received_at_utc") for item in candidates
    )
    tied = [
        item
        for item in candidates
        if _parse_timestamp(item[1].received_at_utc, "receipt received_at_utc") == latest_time
    ]
    if len(tied) == 1 or timestamp_tie_break == "earlier_ledger_sequence":
        chosen = tied[0]
    elif timestamp_tie_break == "later_ledger_sequence":
        chosen = tied[-1]
    else:
        raise CivError("equal receipt timestamps require an explicit tie-break policy")
    return chosen[1], late_found


def _submission_inputs(
    track: dict[str, Any], bundle_path: Path
) -> tuple[dict[str, Any], str, list[dict[str, str]]]:
    working_path: Path | None = None
    try:
        with open_validated_submission(bundle_path) as working:
            working_path = working
            return _inspect_submission_inputs(track, working)
    except CivError as error:
        message = str(error)
        for path, replacement in ((working_path, "<submission>"), (bundle_path, "<bundle>")):
            if path is not None:
                message = message.replace(str(path), replacement)
                message = message.replace(str(path.resolve()), replacement)
        raise CivError(message) from error


def _inspect_submission_inputs(
    track: dict[str, Any], working: Path
) -> tuple[dict[str, Any], str, list[dict[str, str]]]:
    spec_path = submission_spec_path(working)
    spec = load_event_spec(spec_path)
    replay = require_mapping(track["replay"], "track replay")
    if spec.contract not in replay["event_spec_contracts"]:
        raise CivError(
            f"EventSpec contract '{spec.contract}' is not allowed by track {track['track_id']}"
        )
    used_topics = {binding.topic for binding in spec.signals.values()}
    allowed_topics = set(cast(list[str], replay["allowed_topics"]))
    if not used_topics or not used_topics.issubset(allowed_topics):
        raise CivError("EventSpec signal topics exceed the track's configured topic allowlist")
    resources = load_point_resources(spec_path, spec.resources)
    limits = require_mapping(replay["resource_limits"], "track resource_limits")
    if len(resources) > limits["max_files"]:
        raise CivError("EventSpec resources exceed the configured file limit")
    resource_records: list[dict[str, str]] = []
    total_bytes = 0
    for name, resource in sorted(resources.items()):
        path = spec_path.parent / resource.binding.path
        try:
            total_bytes += path.stat().st_size
        except OSError as error:
            raise CivError(f"cannot inspect EventSpec resource '{name}'") from error
        resource_records.append(
            {
                "name": name,
                "path": resource.binding.path,
                "sha256": resource.sha256,
            }
        )
    if total_bytes > limits["max_bytes"]:
        raise CivError("EventSpec resources exceed the configured byte limit")
    return (
        {
            "spec_sha256": file_sha256(spec_path),
            "event_spec_contract": spec.contract,
            "signal_topics": sorted(used_topics),
            "resources": resource_records,
            "resource_bytes": total_bytes,
        },
        str(spec_path),
        resource_records,
    )


def _stable_failure(stderr: str, paths: Sequence[tuple[Path | None, str]]) -> str:
    message = stderr.strip() or "trusted replay process failed"
    for path, replacement in paths:
        if path is not None:
            message = message.replace(str(path), replacement).replace(
                str(path.resolve()), replacement
            )
    return " ".join(message.split())[:1000]


def _run_replay(
    spec_path: Path,
    product_path: Path,
    output_path: Path,
    *,
    timeout_seconds: float,
    retries: int,
) -> tuple[bool, str | None, int, str | None]:
    last_failure = "trusted replay process failed"
    failure_origin = "organizer"
    attempts = 0
    for attempt in range(1, retries + 2):
        attempts = attempt
        if output_path.exists():
            shutil.rmtree(output_path)
        try:
            completed = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "civ_workshop",
                    "detect",
                    str(spec_path),
                    str(product_path),
                    "--output",
                    str(output_path),
                ],
                cwd=spec_path.parent.parent,
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
                check=False,
                env={**os.environ, "CIV_REPLAY_ERROR_CODES": "1"},
            )
        except subprocess.TimeoutExpired:
            last_failure = f"trusted replay timed out after {timeout_seconds:g} seconds"
            failure_origin = "submission"
            continue
        except OSError as error:
            last_failure = f"trusted replay could not start: {error.__class__.__name__}"
            failure_origin = "organizer"
            continue
        if completed.returncode == 0 and (output_path / "events.jsonl").is_file():
            return True, None, attempts, None
        failure_origin = "submission" if completed.returncode == 2 else "organizer"
        last_failure = _stable_failure(
            completed.stderr,
            [
                (spec_path.parent.parent, "<submission>"),
                (output_path, "<replay-output>"),
                (product_path, "<product>"),
            ],
        )
    return False, last_failure, attempts, failure_origin


def _artifact_directory(
    output_root: Path, namespace: str, identity: str, track_id: str, product_id: str
) -> Path:
    identity_key = hashlib.sha256(identity.encode("utf-8")).hexdigest()[:16]
    return output_root / "replays" / namespace / identity_key / track_id / product_id


def _resource_fingerprint(
    ledger: IntakeLedger,
    receipts: list[IntakeReceipt],
    tracks: list[dict[str, Any]],
    base: Path,
    cutoff: datetime,
    timestamp_tie_break: str | None,
    participants: list[str],
) -> tuple[dict[str, Any], list[str]]:
    diagnostics: list[str] = []
    selections: list[dict[str, Any]] = []
    track_ids = {str(track["track_id"]) for track in tracks}
    participant_ids = set(participants)
    receipt_identities = {receipt.identity for receipt in receipts}
    for identity in sorted(receipt_identities - participant_ids):
        deliveries = sorted(
            receipt.delivery_id for receipt in receipts if receipt.identity == identity
        )
        diagnostics.append(
            f"receipts for unregistered participant '{identity}' require reconciliation "
            f"(deliveries: {', '.join(deliveries)})"
        )
    for receipt in receipts:
        if receipt.track_id is None:
            diagnostics.append(
                f"delivery '{receipt.delivery_id}' has no track_id and requires reconciliation"
            )
        elif receipt.track_id not in track_ids:
            diagnostics.append(
                f"delivery '{receipt.delivery_id}' has unknown track_id '{receipt.track_id}' "
                "and requires reconciliation"
            )
    identities = sorted(participant_ids)
    for identity in identities:
        for track in tracks:
            track_id = str(track["track_id"])
            selected, _late = _select_receipt(
                receipts,
                identity,
                track_id,
                cutoff,
                timestamp_tie_break=timestamp_tie_break,
            )
            if selected is None:
                continue
            item: dict[str, Any] = {
                "identity": identity,
                "track_id": track_id,
                "delivery_id": selected.delivery_id,
                "received_at_utc": selected.received_at_utc,
                "bundle_sha256": selected.bundle_sha256,
            }
            if selected.validation_error is not None:
                item["validation_error"] = selected.validation_error
                diagnostics.append(
                    f"submission: {identity}/{track_id}: {selected.validation_error}"
                )
                selections.append(item)
                continue
            try:
                bundle = ledger.bundle_for(selected)
            except CivError as error:
                diagnostics.append(f"ledger: {identity}/{track_id}: {error}")
                selections.append(item)
                continue
            try:
                details, _spec_path_unused, _resource_records_unused = _submission_inputs(
                    track, bundle
                )
                item["submission_inputs"] = details
                used_topics = set(details["signal_topics"])
                for product in track["products"]:
                    configured_topics = set(product["input_contract"]["topics"])
                    if not used_topics.issubset(configured_topics):
                        diagnostics.append(
                            f"submission: {identity}/{track_id}/{product['product_id']}: "
                            "EventSpec topics are "
                            "not present in the product input contract"
                        )
            except CivError as error:
                diagnostics.append(
                    f"submission: {identity}/{track_id}: selected submission cannot be "
                    f"fingerprinted: {error}"
                )
            selections.append(item)
    product_inputs: list[dict[str, Any]] = []
    for track in tracks:
        for product in track["products"]:
            try:
                valid = validate_product(track, product, base)
                product_inputs.append(
                    {
                        "track_id": track["track_id"],
                        "product_id": product["product_id"],
                        "partition": product["partition"],
                        "recording_sha256": valid["recording_sha256"],
                        "manifest_sha256": valid["manifest_sha256"],
                        "truth_sha256": valid["truth_sha256"],
                    }
                )
            except CivError as error:
                diagnostics.append(f"{track['track_id']}/{product['product_id']}: {error}")
    ledger_digest = file_sha256(ledger.database_path) if ledger.database_path.is_file() else None
    snapshot = {
        "contract": "civ.cohort-scoring-inputs/v1alpha1",
        "plan_sha256": None,
        "ledger_sha256": ledger_digest,
        "selected_submissions": selections,
        "products": product_inputs,
    }
    return snapshot, diagnostics


def input_fingerprint(
    ledger_root: Path,
    plan_path: Path,
    *,
    receipt_snapshot: list[IntakeReceipt] | None = None,
) -> tuple[str | None, list[str]]:
    plan = load_evaluation_plan(plan_path)
    ledger = IntakeLedger(ledger_root)
    if receipt_snapshot is not None:
        receipts = list(receipt_snapshot)
    elif ledger.database_path.is_file():
        try:
            receipts = ledger.receipts(read_only=True)
        except CivError as error:
            return None, [f"ledger: {error}"]
    else:
        receipts = []
    cutoff = _parse_timestamp(plan["cutoff"], "evaluation plan cutoff")
    policy = plan.get("scoring_policy")
    tie_break = policy.get("receipt_timestamp_ties") if isinstance(policy, dict) else None
    if not isinstance(tie_break, str):
        tie_break = None
    snapshot, diagnostics = _resource_fingerprint(
        ledger,
        receipts,
        cast(list[dict[str, Any]], plan["tracks"]),
        plan_path.parent,
        cutoff,
        cast(str, tie_break),
        cast(list[str], plan["participants"]),
    )
    snapshot["plan_sha256"] = file_sha256(plan_path)
    if snapshot["ledger_sha256"] is None:
        diagnostics.append("ledger: intake database does not exist")
    return hashlib.sha256(canonical_json(snapshot).encode("utf-8")).hexdigest(), diagnostics


def _rounding_blockers(rounding: object) -> list[str]:
    if not isinstance(rounding, dict):
        return ["scoring policy: rounding must define mode and decimal_places"]
    blockers = []
    if rounding.get("mode") not in ("half_even", "half_up"):
        blockers.append("scoring policy: rounding mode must be half_even or half_up")
    places = rounding.get("decimal_places")
    if isinstance(places, bool) or not isinstance(places, int) or not 0 <= places <= 12:
        blockers.append("scoring policy: rounding decimal_places must be from 0 to 12")
    return blockers


def policy_blockers(plan: dict[str, Any]) -> list[str]:
    policy = plan.get("scoring_policy")
    if not isinstance(policy, dict):
        return [
            "scoring policy: explicit aggregation and scoring decisions are required",
            "scoring policy: set manual_review to organizer_or_agent for Evidence and "
            "Reproducibility",
        ]
    required = {
        "temporal_iou_threshold",
        "matching",
        "product_weights",
        "score_bearing_partitions",
        "missing_track",
        "failed_run",
        "empty_truth",
        "cross_product_events",
        "rounding",
        "receipt_timestamp_ties",
        "detection_points",
    }
    missing = sorted(required - set(policy))
    blockers = [f"scoring policy: missing decision '{field}'" for field in missing]
    if policy.get("manual_review") != "organizer_or_agent":
        blockers.append(
            "scoring policy: set manual_review to organizer_or_agent for Evidence and "
            "Reproducibility"
        )
    if policy.get("temporal_iou_threshold") != 0.5:
        blockers.append("scoring policy: temporal_iou_threshold must remain 0.5")
    if policy.get("matching") != "one_to_one_best":
        blockers.append("scoring policy: matching must remain one_to_one_best")
    if policy.get("receipt_timestamp_ties") not in (
        "later_ledger_sequence",
        "earlier_ledger_sequence",
    ):
        blockers.append(
            "scoring policy: receipt_timestamp_ties must select either earlier_ledger_sequence "
            "or later_ledger_sequence"
        )
    if policy.get("cross_product_events") != "score_within_product":
        blockers.append("scoring policy: cross-product event handling must be score_within_product")
    if policy.get("score_bearing_partitions") is not None:
        partitions = policy["score_bearing_partitions"]
        if (
            not isinstance(partitions, list)
            or not partitions
            or any(item not in ("warmup", "development", "sealed") for item in partitions)
        ):
            blockers.append(
                "scoring policy: score_bearing_partitions must explicitly select partitions"
            )
    if policy.get("missing_track") not in ("zero", "exclude"):
        blockers.append("scoring policy: missing_track must be zero or exclude")
    if policy.get("failed_run") not in ("zero", "exclude"):
        blockers.append("scoring policy: failed_run must be zero or exclude")
    if policy.get("empty_truth") not in ("zero", "perfect_empty", "exclude"):
        blockers.append("scoring policy: empty_truth must be zero, perfect_empty, or exclude")
    blockers.extend(_rounding_blockers(policy.get("rounding")))
    if policy.get("detection_points") is not None:
        points = policy["detection_points"]
        if not isinstance(points, dict):
            blockers.append("scoring policy: detection_points must map track IDs to allocations")
        else:
            known = {str(track["track_id"]) for track in cast(list[dict[str, Any]], plan["tracks"])}
            bonus = policy.get("bonus_points", {})
            if not isinstance(bonus, dict):
                blockers.append("scoring policy: bonus_points must map track IDs to allocations")
                bonus = {}
            if (
                set(points) & set(bonus)
                or set(points) | set(bonus) != known
                or any(not _finite_number(value) or value < 0 for value in bonus.values())
                or any(not _finite_number(value) or value < 0 for value in points.values())
            ):
                blockers.append(
                    "scoring policy: detection_points and bonus_points must assign each track "
                    "one non-negative allocation"
                )
    weights = policy.get("product_weights")
    if not isinstance(weights, dict):
        blockers.append(
            "scoring policy: product_weights must map every track and score-bearing product"
        )
    else:
        selected_partitions = policy.get("score_bearing_partitions")
        if isinstance(selected_partitions, list):
            for track in cast(list[dict[str, Any]], plan["tracks"]):
                track_id = str(track["track_id"])
                track_weights = weights.get(track_id)
                if not isinstance(track_weights, dict):
                    blockers.append(f"scoring policy: product_weights missing track '{track_id}'")
                    continue
                expected_products = {
                    str(product["product_id"])
                    for product in track["products"]
                    if product["partition"] in selected_partitions
                }
                if not expected_products:
                    blockers.append(
                        f"scoring policy: track '{track_id}' has no score-bearing products"
                    )
                if set(track_weights) != expected_products:
                    blockers.append(
                        f"scoring policy: product_weights for '{track_id}' must match its "
                        "score-bearing products"
                    )
                numeric_weights = list(track_weights.values())
                if any(not _finite_number(value) or value < 0 for value in numeric_weights):
                    blockers.append(
                        f"scoring policy: product_weights for '{track_id}' must be finite "
                        "and non-negative"
                    )
                elif expected_products and sum(numeric_weights) <= 0:
                    blockers.append(
                        f"scoring policy: product_weights for '{track_id}' must have a positive sum"
                    )
    return blockers


def _rounded(value: float | Decimal, rounding: dict[str, Any]) -> float:
    places = int(rounding["decimal_places"])
    mode = ROUND_HALF_EVEN if rounding["mode"] == "half_even" else ROUND_HALF_UP
    return float(Decimal(str(value)).quantize(Decimal(1).scaleb(-places), rounding=mode))


def _pooled_detection_metrics(records: list[dict[str, Any]]) -> dict[str, Any]:
    counts = {"true_positive": 0, "false_positive": 0, "false_negative": 0}
    outcomes: dict[str, int] = {}
    for record in records:
        status = str(record["status"])
        outcomes[status] = outcomes.get(status, 0) + 1
        if status == "scored":
            for name in counts:
                counts[name] += int(record["metrics"]["aggregate"]["counts"][name])
    tp, fp, fn = (counts[name] for name in ("true_positive", "false_positive", "false_negative"))
    scored = outcomes.get("scored", 0)
    return {
        "counts": counts if scored else None,
        "precision": round(tp / (tp + fp), 12) if scored and tp + fp else None,
        "recall": round(tp / (tp + fn), 12) if scored and tp + fn else None,
        "f1": round(2 * tp / (2 * tp + fp + fn), 12) if scored and 2 * tp + fp + fn else None,
        "products": len(records),
        "outcomes": dict(sorted(outcomes.items())),
        "status": "complete" if scored == len(records) else "partial" if scored else "unavailable",
    }


def _detection_metrics(records: list[dict[str, Any]]) -> dict[str, Any]:
    grouped: dict[str, dict[str, list[dict[str, Any]]]] = {}
    for record in records:
        grouped.setdefault(str(record["identity"]), {}).setdefault(
            str(record["track_id"]), []
        ).append(record)
    participants: dict[str, Any] = {}
    for identity, tracks in sorted(grouped.items()):
        track_metrics = {}
        for track_id, track_records in sorted(tracks.items()):
            partitions = sorted({str(record["partition"]) for record in track_records})
            track_metrics[track_id] = {
                "aggregate": _pooled_detection_metrics(track_records),
                "partitions": {
                    partition: _pooled_detection_metrics(
                        [record for record in track_records if record["partition"] == partition]
                    )
                    for partition in partitions
                },
            }
        participants[identity] = {"tracks": track_metrics}
    return {"aggregation": "pooled_counts", "participants": participants}


def _aggregate_detection(
    records: list[dict[str, Any]], plan: dict[str, Any]
) -> tuple[dict[str, Any] | None, list[str]]:
    policy = plan.get("scoring_policy")
    if not isinstance(policy, dict):
        return None, ["scoring policy: detection aggregation is not configured"]
    if policy.get("temporal_iou_threshold") != 0.5 or policy.get("matching") != "one_to_one_best":
        return None, [
            "scoring policy: configured matching does not match the implemented temporal-IoU policy"
        ]
    if (
        policy.get("receipt_timestamp_ties")
        not in ("later_ledger_sequence", "earlier_ledger_sequence")
        or policy.get("cross_product_events") != "score_within_product"
    ):
        return None, [
            "scoring policy: receipt tie or product-boundary policy is not supported by this scorer"
        ]
    needed = (
        "score_bearing_partitions",
        "missing_track",
        "failed_run",
        "empty_truth",
        "rounding",
    )
    if any(name not in policy for name in needed):
        return None, ["scoring policy: detection aggregation decisions are incomplete"]
    weights_all = policy.get("product_weights", {})
    partitions = policy["score_bearing_partitions"]
    points_all = policy.get("detection_points", {})
    bonus_all = policy.get("bonus_points", {})
    rounding = policy["rounding"]
    rounding_errors = _rounding_blockers(rounding)
    if rounding_errors:
        return None, rounding_errors
    if (
        not isinstance(weights_all, dict)
        or not isinstance(partitions, list)
        or not isinstance(points_all, dict)
        or not isinstance(bonus_all, dict)
        or not isinstance(rounding, dict)
    ):
        return None, ["scoring policy: detection aggregation fields have invalid shapes"]
    for name in ("missing_track", "failed_run"):
        if policy[name] not in ("zero", "exclude"):
            return None, [f"scoring policy: {name} must be zero or exclude"]
    if policy["empty_truth"] not in ("zero", "perfect_empty", "exclude"):
        return None, ["scoring policy: empty_truth must be zero, perfect_empty, or exclude"]
    if (
        not partitions
        or any(
            not isinstance(partition, str) or partition not in PARTITIONS
            for partition in partitions
        )
        or len(set(partitions)) != len(partitions)
    ):
        return None, ["scoring policy: score-bearing partitions are invalid"]

    plan_tracks = cast(list[dict[str, Any]], plan["tracks"])
    known_tracks = {str(track["track_id"]) for track in plan_tracks}
    if (
        set(weights_all) - known_tracks
        or (set(points_all) | set(bonus_all)) - known_tracks
        or set(points_all) & set(bonus_all)
    ):
        return None, ["scoring policy: weights and Detection allocations name unknown tracks"]
    allocations = {**points_all, **bonus_all}
    track_errors: dict[str, str] = {}
    allocation_errors: dict[str, str] = {}
    outcome_blockers: list[str] = []
    for track in plan_tracks:
        track_id = str(track["track_id"])
        track_weights = weights_all.get(track_id)
        if not isinstance(track_weights, dict):
            track_errors[track_id] = f"scoring policy: product weights are missing for '{track_id}'"
            continue
        expected_products = {
            str(product["product_id"])
            for product in track["products"]
            if product["partition"] in partitions
        }
        if not expected_products:
            track_errors[track_id] = (
                f"scoring policy: track '{track_id}' has no score-bearing products"
            )
        elif set(track_weights) != expected_products:
            track_errors[track_id] = (
                f"scoring policy: product weights for '{track_id}' do not match "
                "score-bearing products"
            )
        elif any(not _finite_number(weight) or weight < 0 for weight in track_weights.values()):
            track_errors[track_id] = f"scoring policy: product weights for '{track_id}' are invalid"
        elif expected_products and sum(track_weights.values()) <= 0:
            track_errors[track_id] = f"scoring policy: product weights for '{track_id}' sum to zero"
        allocation = allocations.get(track_id)
        if not _finite_number(allocation) or allocation < 0:
            allocation_errors[track_id] = (
                f"scoring policy: Detection points for '{track_id}' are missing or invalid"
            )

    outcome_map = {
        (str(record["identity"]), str(record["track_id"]), str(record["product_id"])): record
        for record in records
    }
    identities = sorted({str(record["identity"]) for record in records})
    participant_scores: dict[str, Any] = {}
    for identity in identities:
        track_scores: dict[str, Any] = {}
        for track in plan_tracks:
            track_id = str(track["track_id"])
            track_weights = weights_all.get(track_id)
            point_allocation = allocations.get(track_id)
            points_field = "bonus_points" if track_id in bonus_all else "detection_points"
            if track_id in track_errors:
                track_scores[track_id] = {
                    "f1": None,
                    points_field: None,
                    "products": [],
                    "pending_reason": track_errors[track_id],
                }
                continue
            track_weights = cast(dict[str, Any], track_weights)
            weighted_f1 = Decimal(0)
            used_weight = Decimal(0)
            product_audit: list[dict[str, Any]] = []
            for product in track["products"]:
                if product["partition"] not in partitions:
                    continue
                product_id = str(product["product_id"])
                weight_value = track_weights.get(product_id)
                if not _finite_number(weight_value) or weight_value < 0:
                    return None, [
                        f"scoring policy: explicit finite product weight missing for "
                        f"{track_id}/{product_id}"
                    ]
                weight = Decimal(str(weight_value))
                record = outcome_map.get((identity, track_id, product_id))
                value: Decimal | None = None
                disposition = "scored"
                if record is None or record["status"] in ("missing-track", "late-only"):
                    disposition = "missing-track"
                    if policy["missing_track"] == "zero":
                        value = Decimal(0)
                elif record["status"] != "scored":
                    disposition = "failed-run"
                    if record.get("failure_origin") == "organizer":
                        disposition = "organizer-failure-rerun-required"
                    elif policy["failed_run"] == "zero":
                        value = Decimal(0)
                else:
                    metrics = require_mapping(record["metrics"], "cohort product metrics")
                    aggregate = require_mapping(
                        metrics.get("aggregate"), "cohort aggregate metrics"
                    )
                    counts = require_mapping(aggregate.get("counts"), "cohort counts")
                    tp = int(counts["true_positive"])
                    fp = int(counts["false_positive"])
                    fn = int(counts["false_negative"])
                    denominator = 2 * tp + fp + fn
                    value = Decimal(2 * tp) / Decimal(denominator) if denominator else Decimal(0)
                    if tp + fn == 0:
                        disposition = "empty-truth"
                        if policy["empty_truth"] == "exclude":
                            value = None
                        elif policy["empty_truth"] == "perfect_empty":
                            value = Decimal(1) if counts.get("false_positive") == 0 else Decimal(0)
                if value is not None:
                    weighted_f1 += value * weight
                    used_weight += weight
                product_audit.append(
                    {
                        "product_id": product_id,
                        "weight": float(weight),
                        "f1": float(value) if value is not None else None,
                        "disposition": disposition,
                    }
                )
            organizer_failure = any(
                item["disposition"] == "organizer-failure-rerun-required" for item in product_audit
            )
            if used_weight == 0 or organizer_failure:
                track_scores[track_id] = {
                    "f1": None,
                    points_field: None,
                    "products": product_audit,
                }
                reason = (
                    f"organizer failure requires rerun for '{track_id}'"
                    if organizer_failure
                    else f"no scored product weight remains for '{track_id}'"
                )
                track_scores[track_id]["pending_reason"] = reason
                outcome_blockers.append(f"{identity}: {reason}")
            else:
                exact_f1 = weighted_f1 / used_weight
                f1 = _rounded(exact_f1, rounding)
                score = (
                    _rounded(Decimal(str(point_allocation)) * exact_f1, rounding)
                    if track_id not in allocation_errors
                    else None
                )
                track_scores[track_id] = {
                    "f1": f1,
                    points_field: score,
                    "products": product_audit,
                }
            if track_id in allocation_errors:
                track_scores[track_id]["pending_reason"] = allocation_errors[track_id]
        participant_scores[identity] = {
            "tracks": track_scores,
            "total_detection_points": (
                _rounded(
                    sum(
                        Decimal(str(score["detection_points"]))
                        for track_id, score in track_scores.items()
                        if track_id not in bonus_all
                    ),
                    rounding,
                )
                if all(
                    score.get("detection_points") is not None
                    for track_id, score in track_scores.items()
                    if track_id not in bonus_all
                )
                else None
            ),
            "total_bonus_points": (
                _rounded(
                    sum(
                        Decimal(str(track_scores[track_id]["bonus_points"]))
                        for track_id in bonus_all
                    ),
                    rounding,
                )
                if all(
                    track_scores[track_id].get("bonus_points") is not None for track_id in bonus_all
                )
                else None
            ),
        }
    return {
        "contract": "civ.detection-aggregation/v1alpha1",
        "component": "Detection",
        "participants": participant_scores,
    }, list(track_errors.values()) + list(allocation_errors.values()) + outcome_blockers


def _selection_records(
    receipts: list[IntakeReceipt],
    tracks: list[dict[str, Any]],
    participants: list[str],
    cutoff: datetime,
    timestamp_tie_break: str | None,
) -> tuple[list[str], dict[tuple[str, str], tuple[IntakeReceipt | None, bool]]]:
    identities = sorted(set(participants) | {receipt.identity for receipt in receipts})
    selected: dict[tuple[str, str], tuple[IntakeReceipt | None, bool]] = {}
    for identity in identities:
        for track in tracks:
            track_id = str(track["track_id"])
            selected[(identity, track_id)] = _select_receipt(
                receipts,
                identity,
                track_id,
                cutoff,
                timestamp_tie_break=timestamp_tie_break,
            )
    return identities, selected


def _receipt_dispositions(
    receipts: list[IntakeReceipt],
    selections: dict[tuple[str, str], tuple[IntakeReceipt | None, bool]],
    tracks: list[dict[str, Any]],
    participants: list[str],
    cutoff: datetime,
) -> list[dict[str, Any]]:
    registered = set(participants)
    track_ids = {str(track["track_id"]) for track in tracks}
    dispositions: list[dict[str, Any]] = []
    for receipt in receipts:
        if receipt.track_id is None:
            track_disposition = "missing_track_id"
        elif receipt.track_id not in track_ids:
            track_disposition = "unknown_track_id"
        elif _parse_timestamp(receipt.received_at_utc, "receipt received_at_utc") > cutoff:
            track_disposition = "late"
        else:
            selected, _late = selections[(receipt.identity, receipt.track_id)]
            track_disposition = (
                "selected"
                if selected is not None and selected.delivery_id == receipt.delivery_id
                else "superseded"
            )
        participant_disposition = (
            "registered" if receipt.identity in registered else "unregistered_identity"
        )
        dispositions.append(
            {
                "delivery_id": receipt.delivery_id,
                "identity": receipt.identity,
                "track_id": receipt.track_id,
                "participant_disposition": participant_disposition,
                "track_disposition": track_disposition,
                "validation_error": receipt.validation_error,
                "reconciliation_required": (
                    participant_disposition != "registered"
                    or track_disposition in {"missing_track_id", "unknown_track_id"}
                ),
            }
        )
    return dispositions


def _publish_cohort_outputs(staging_root: Path, output_root: Path, artifact_namespace: str) -> None:
    outputs = [Path("results.jsonl"), Path("summary.json"), Path("manual-review-template.json")]
    replay_output = Path("replays") / artifact_namespace
    if (staging_root / replay_output).is_dir():
        outputs.append(replay_output)
    backup_root = staging_root / ".previous"
    backed_up: list[tuple[Path, Path]] = []
    published: list[Path] = []
    try:
        output_root.mkdir(parents=True, exist_ok=True)
        for relative in outputs:
            source = staging_root / relative
            destination = output_root / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            if destination.exists():
                backup = backup_root / relative
                backup.parent.mkdir(parents=True, exist_ok=True)
                os.replace(destination, backup)
                backed_up.append((destination, backup))
            os.replace(source, destination)
            published.append(destination)
    except OSError as error:
        for destination in reversed(published):
            if destination.is_dir():
                shutil.rmtree(destination, ignore_errors=True)
            else:
                destination.unlink(missing_ok=True)
        for destination, backup in reversed(backed_up):
            if backup.exists():
                destination.parent.mkdir(parents=True, exist_ok=True)
                os.replace(backup, destination)
        raise CivError(f"cannot commit cohort scoring outputs: {error}") from error


def run_cohort_batch(
    ledger_root: Path,
    plan_path: Path,
    output_root: Path,
    *,
    official: bool = False,
) -> dict[str, object]:
    plan = load_evaluation_plan(plan_path)
    tracks = cast(list[dict[str, Any]], plan["tracks"])
    ledger = IntakeLedger(ledger_root)
    receipts = ledger.receipts(read_only=True) if ledger.database_path.is_file() else []
    cutoff = _parse_timestamp(plan["cutoff"], "evaluation plan cutoff")
    official_score = official
    input_digest, fingerprint_diagnostics = input_fingerprint(
        ledger_root, plan_path, receipt_snapshot=receipts
    )
    blockers = policy_blockers(plan) + [
        f"inputs: {item}" for item in fingerprint_diagnostics if not item.startswith("submission:")
    ]
    if official and blockers:
        raise CivError(f"official scoring blocked: {'; '.join(blockers)}")
    runtime = runtime_metadata()
    scoring_policy = plan.get("scoring_policy")
    tie_break = (
        scoring_policy.get("receipt_timestamp_ties") if isinstance(scoring_policy, dict) else None
    )
    if not isinstance(tie_break, str):
        tie_break = None
    participants = cast(list[str], plan["participants"])
    identities, selections = _selection_records(
        receipts, tracks, participants, cutoff, cast(str, tie_break)
    )
    receipt_dispositions = _receipt_dispositions(receipts, selections, tracks, participants, cutoff)
    result_records: list[dict[str, Any]] = []
    counts: dict[str, int] = {}
    plan_sha = file_sha256(plan_path)
    ledger_sha = file_sha256(ledger.database_path) if ledger.database_path.is_file() else None
    artifact_namespace = (
        input_digest or hashlib.sha256(f"{plan_sha}:{ledger_sha}".encode("ascii")).hexdigest()
    )
    product_cache: dict[tuple[str, str], tuple[dict[str, Any] | None, str | None]] = {}
    for track in tracks:
        for product in track["products"]:
            key = (str(track["track_id"]), str(product["product_id"]))
            try:
                product_cache[key] = (validate_product(track, product, plan_path.parent), None)
            except CivError as error:
                product_cache[key] = (None, str(error))
    try:
        output_root.parent.mkdir(parents=True, exist_ok=True)
        staging_context = TemporaryDirectory(
            prefix=f".{output_root.name}.cohort-staging-", dir=output_root.parent
        )
    except OSError as error:
        raise CivError(f"cannot stage cohort scoring output: {error}") from error
    staging_root = Path(staging_context.name)
    for identity in identities:
        for track in tracks:
            track_id = str(track["track_id"])
            selected, late_found = selections[(identity, track_id)]
            if selected is None:
                state = "late-only" if late_found else "missing-track"
                for product in track["products"]:
                    record = {
                        "contract": RESULTS_CONTRACT,
                        "official_score": official_score,
                        "official_scope": "automatic_components" if official else None,
                        "identity": identity,
                        "track_id": track_id,
                        "product_id": product["product_id"],
                        "partition": product["partition"],
                        "dataset": track["dataset"],
                        "status": state,
                        "selected_submission": None,
                        "product": {
                            "recording_sha256": product["recording"]["sha256"],
                            "manifest_sha256": product["manifest"]["sha256"],
                            "truth_sha256": product["truth"]["sha256"],
                        },
                        "truth_count": None,
                        "replay": None,
                        "metrics": None,
                    }
                    result_records.append(record)
                    counts[state] = counts.get(state, 0) + 1
                continue
            selected_base = {
                "delivery_id": selected.delivery_id,
                "received_at_utc": selected.received_at_utc,
                "bundle_sha256": selected.bundle_sha256,
                "track_id": selected.track_id,
            }
            submission_error = selected.validation_error
            storage_error: str | None = None
            submission_metadata: dict[str, Any] = {}
            if submission_error is None:
                try:
                    bundle = ledger.bundle_for(selected)
                except CivError as error:
                    storage_error = str(error)
                else:
                    try:
                        submission_metadata, _spec_path_unused, _resource_records_unused = (
                            _submission_inputs(track, bundle)
                        )
                    except CivError as error:
                        submission_error = str(error)
            for product in track["products"]:
                product_valid, product_error = product_cache[(track_id, str(product["product_id"]))]
                assignment_submission_error = submission_error
                if (
                    product_error is None
                    and submission_error is None
                    and storage_error is None
                    and not set(submission_metadata["signal_topics"]).issubset(
                        set(product["input_contract"]["topics"])
                    )
                ):
                    assignment_submission_error = (
                        "EventSpec topics are not present in the product input contract"
                    )
                replay_record: dict[str, Any] | None = None
                metrics: dict[str, Any] | None = None
                failure = storage_error or assignment_submission_error or product_error
                replay_failure_origin: str | None = None
                failure_stage = (
                    "ledger_storage"
                    if storage_error
                    else "submission_validation"
                    if assignment_submission_error
                    else "product_validation"
                    if product_error
                    else None
                )
                replay_attempts = 0
                status = "failed"
                artifact_path: Path | None = None
                working_path: Path | None = None
                temp_output: Path | None = None
                bundle_path: Path | None = None
                if failure is None and product_valid is not None:
                    try:
                        bundle_path = ledger.bundle_for(selected)
                        with (
                            open_validated_submission(bundle_path) as working,
                            TemporaryDirectory(prefix="civ-cohort-replay-") as replay_temp,
                        ):
                            working_path = working
                            spec_path = submission_spec_path(working)
                            replay = require_mapping(track["replay"], "track replay")
                            temp_output = Path(replay_temp) / "output"
                            succeeded, failure, replay_attempts, replay_failure_origin = (
                                _run_replay(
                                    spec_path,
                                    cast(Path, product_valid["recording_path"]),
                                    temp_output,
                                    timeout_seconds=float(replay["timeout_seconds"]),
                                    retries=int(replay["retries"]),
                                )
                            )
                            if succeeded:
                                metrics = score_submission(
                                    temp_output, cast(Path, product_valid["truth_path"])
                                )
                                events = read_json_file(
                                    temp_output / "run-manifest.json", "replay run manifest"
                                ).get("events", {})
                                replay_record = {
                                    **submission_metadata,
                                    "event_count": events.get("count")
                                    if isinstance(events, dict)
                                    else None,
                                    "zero_events": events.get("count") == 0
                                    if isinstance(events, dict)
                                    else False,
                                    "attempts": replay_attempts,
                                    "events_sha256": file_sha256(temp_output / "events.jsonl"),
                                    "metrics_sha256": file_sha256(temp_output / "metrics.json"),
                                }
                                artifact_path = _artifact_directory(
                                    staging_root,
                                    artifact_namespace,
                                    identity,
                                    track_id,
                                    str(product["product_id"]),
                                )
                                artifact_path.parent.mkdir(parents=True, exist_ok=True)
                                if artifact_path.exists():
                                    shutil.rmtree(artifact_path)
                                shutil.copytree(temp_output, artifact_path)
                                replay_record["artifact"] = artifact_path.relative_to(
                                    staging_root
                                ).as_posix()
                                status = "scored"
                            else:
                                status = "failed"
                                failure_stage = "trusted_replay"
                    except (CivError, OSError) as error:
                        failure = _stable_failure(
                            str(error),
                            [
                                (working_path, "<submission>"),
                                (temp_output, "<replay-output>"),
                                (cast(Path, product_valid["recording_path"]), "<product>"),
                                (bundle_path, "<bundle>"),
                                (artifact_path, "<organizer-output>"),
                            ],
                        )
                        status = "failed"
                        failure_stage = "scoring_or_artifact_write"
                if status == "failed" and replay_record is None:
                    replay_record = {
                        **submission_metadata,
                        "attempts": replay_attempts,
                        "failure_stage": failure_stage or "cohort_scoring",
                    }
                record = {
                    "contract": RESULTS_CONTRACT,
                    "official_score": official_score,
                    "official_scope": "automatic_components" if official else None,
                    "identity": identity,
                    "track_id": track_id,
                    "product_id": product["product_id"],
                    "partition": product["partition"],
                    "dataset": track["dataset"],
                    "status": status,
                    "selected_submission": selected_base,
                    "product": {
                        "recording_sha256": product["recording"]["sha256"],
                        "manifest_sha256": product["manifest"]["sha256"],
                        "truth_sha256": product["truth"]["sha256"],
                    },
                    "truth_count": product_valid["truth_count"]
                    if product_valid is not None
                    else None,
                    "replay": replay_record,
                    "metrics": metrics,
                    "failure": failure,
                    "failure_origin": (
                        "organizer"
                        if failure
                        and (
                            failure_stage
                            in (
                                "ledger_storage",
                                "product_validation",
                                "scoring_or_artifact_write",
                            )
                            or (
                                failure_stage == "trusted_replay"
                                and replay_failure_origin == "organizer"
                            )
                        )
                        else "submission"
                        if failure
                        else None
                    ),
                }
                result_records.append(record)
                counts[status] = counts.get(status, 0) + 1
    computed_detection, aggregation_blockers = _aggregate_detection(result_records, plan)
    blockers.extend(aggregation_blockers)
    if official and blockers:
        staging_context.cleanup()
        raise CivError(f"official scoring blocked: {'; '.join(blockers)}")
    technical_scores: dict[str, dict[str, object]] = {}
    detection_rows = (
        cast(dict[str, Any], computed_detection["participants"])
        if isinstance(computed_detection, dict)
        else {}
    )
    for identity in participants:
        detection_points = detection_rows.get(identity, {}).get("total_detection_points")
        technical_scores[identity] = {
            "detection_points": detection_points,
            "evidence_points": None,
            "reproducibility_points": None,
            "technical_total_points": None,
            "pending_components": (
                (["detection"] if detection_points is None else [])
                + ["evidence", "reproducibility"]
            ),
            "status": "pending_manual_review"
            if isinstance(scoring_policy, dict)
            and scoring_policy.get("manual_review") == "organizer_or_agent"
            else "pending_machine_components",
        }
    results_path = staging_root / "results.jsonl"
    results_path.write_text(
        "".join(f"{canonical_json(record)}\n" for record in result_records),
        encoding="utf-8",
        newline="\n",
    )
    summary = {
        "contract": SUMMARY_CONTRACT,
        "official_score": official_score,
        "official_scope": "automatic_components" if official else None,
        "final_total_points": None,
        "final_score_status": "pending_manual_review",
        "plan_sha256": plan_sha,
        "input_fingerprint": input_digest,
        "runtime": runtime,
        "blockers": blockers,
        "input_diagnostics": fingerprint_diagnostics,
        "detection_metrics": _detection_metrics(result_records),
        "computed_detection": computed_detection,
        "technical_scores": {
            "maximum_points": (
                sum(
                    float(value)
                    for value in cast(dict[str, Any], scoring_policy)["detection_points"].values()
                )
                + 30.0
                if isinstance(scoring_policy, dict)
                and isinstance(scoring_policy.get("detection_points"), dict)
                and isinstance(scoring_policy.get("bonus_points", {}), dict)
                and set(scoring_policy["detection_points"])
                == {
                    track["track_id"]
                    for track in tracks
                    if track["track_id"] not in scoring_policy.get("bonus_points", {})
                }
                and all(
                    _finite_number(value) and value >= 0
                    for value in cast(dict[str, Any], scoring_policy["detection_points"]).values()
                )
                else None
            ),
            "status": "pending_manual_review"
            if isinstance(scoring_policy, dict)
            and scoring_policy.get("manual_review") == "organizer_or_agent"
            else "pending_machine_components",
            "pending_components": (
                ["detection"]
                if any(row["detection_points"] is None for row in technical_scores.values())
                else []
            )
            + ["evidence", "reproducibility"],
            "participants": technical_scores,
        },
        "counts": dict(sorted(counts.items())),
        "identities": len(identities),
        "registered_participants": len(participants),
        "unregistered_identities": sorted(
            {receipt.identity for receipt in receipts} - set(participants)
        ),
        "receipt_dispositions": receipt_dispositions,
        "tracks": len(tracks),
        "products_per_track": {track["track_id"]: len(track["products"]) for track in tracks},
        "outcomes": len(result_records),
        "receipt_selection": {
            "cutoff": plan["cutoff"],
            "timestamp_tie_break": tie_break,
            "selection": "latest eligible receipt per identity and track",
        },
    }
    (staging_root / "summary.json").write_text(
        f"{canonical_json(summary)}\n", encoding="utf-8", newline="\n"
    )
    from civ_workshop.organizer.manual_scoring import review_sheet

    (staging_root / "manual-review-template.json").write_text(
        f"{canonical_json(review_sheet(participants, plan_sha, input_digest))}\n",
        encoding="utf-8",
        newline="\n",
    )
    final_digest, final_diagnostics = input_fingerprint(ledger_root, plan_path)
    if final_digest != input_digest or final_diagnostics != fingerprint_diagnostics:
        staging_context.cleanup()
        raise CivError(
            "scoring inputs changed during replay; no cohort scoring outputs were committed"
        )
    _publish_cohort_outputs(staging_root, output_root, artifact_namespace)
    staging_context.cleanup()
    return summary
