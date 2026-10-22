"""Read-only checks for the unapproved evaluation-plan drafts.

These checks expose prerequisites; they cannot create organizer authority.
"""

from __future__ import annotations

import math
from datetime import datetime
from pathlib import Path
from typing import Any

from civ_workshop.artifacts import file_sha256, read_json_file, require_mapping, require_string
from civ_workshop.errors import CivError
from civ_workshop.intake import TOKYO_CUTOFF, IntakeLedger, IntakeReceipt
from civ_workshop.label_packs import load_label_pack


def check_readiness(
    ledger_root: Path,
    *,
    plan_path: Path | None = None,
    preflight_path: Path | None = None,
    review_status_path: Path | None = None,
    approval_path: Path | None = None,
) -> dict[str, object]:
    if plan_path is not None:
        try:
            declared = read_json_file(plan_path, "evaluation plan")
        except CivError:
            declared = {}
        if declared.get("contract") == "civ.evaluation-plan/v1alpha2":
            return _check_cohort_readiness(
                ledger_root,
                plan_path=plan_path,
                preflight_path=preflight_path,
                review_status_path=review_status_path,
                approval_path=approval_path,
            )
    blockers: list[str] = []
    evidence: dict[str, object] = {}
    # No existing draft contract binds a named approval, confirmed session cutoff,
    # runtime rehearsal, or complete target-specific review to immutable inputs.
    # Do not accept invented approval fields or treat historical prose as approval.
    blockers.extend(
        [
            "approval: named organizer approval bound to the final plan is required; "
            "the current draft contract does not establish approval",
            "cutoff: session owner must confirm the cutoff; intake currently uses "
            f"the historical cutoff {TOKYO_CUTOFF.isoformat()}",
            "runtime: session owner must confirm a runtime rehearsal for the final plan",
            "ledger authority: session owner must designate the authoritative intake ledger",
        ]
    )
    receipts: list[IntakeReceipt] = []
    try:
        receipts = IntakeLedger(ledger_root).receipts(read_only=True)
        if not receipts:
            blockers.append("ledger: intake ledger holds no submissions")
        evidence["receipts"] = len(receipts)
    except CivError as error:
        blockers.append(f"ledger: {error}")

    plan: dict[str, Any] | None = None
    if plan_path is None:
        blockers.append("plan: an explicit evaluation plan is required")
    else:
        try:
            plan = read_json_file(plan_path, "evaluation plan")
            evidence["plan_sha256"] = file_sha256(plan_path)
            if plan.get("contract") != "civ.evaluation-plan/v1alpha1":
                raise CivError("unsupported evaluation plan contract")
            require_string(plan.get("session_id"), "evaluation plan session_id")
            cutoff_text = require_string(plan.get("cutoff"), "plan cutoff")
            evidence["declared_cutoff"] = cutoff_text
            try:
                cutoff = datetime.fromisoformat(cutoff_text.replace("Z", "+00:00"))
            except ValueError as error:
                raise CivError("plan cutoff must be an ISO-8601 timestamp") from error
            if cutoff.tzinfo is None:
                raise CivError("plan cutoff must include a timezone")
            if cutoff != TOKYO_CUTOFF:
                blockers.append("cutoff: plan cutoff differs from the intake implementation")
            selected_sources = _check_tracks(plan, plan_path.parent, blockers, evidence)
            for receipt in receipts:
                if receipt.source_sha256 not in selected_sources:
                    blockers.append(
                        f"source matching: delivery {receipt.delivery_id} has no selected "
                        "exact-source reference in this plan"
                    )
        except CivError as error:
            blockers.append(f"plan: {error}")

    if preflight_path is None:
        blockers.append("preflight: an explicit preflight record is required")
    else:
        try:
            preflight = read_json_file(preflight_path, "preflight")
            evidence["preflight_sha256"] = file_sha256(preflight_path)
            if preflight.get("plan_sha256") != evidence.get("plan_sha256"):
                blockers.append("preflight: plan_sha256 does not match the selected plan")
            recorded = preflight.get("official_blockers")
            if not isinstance(recorded, list) or any(not isinstance(x, str) for x in recorded):
                raise CivError("official_blockers must be a list of strings")
            blockers.extend(f"preflight unresolved: {item}" for item in recorded)
        except CivError as error:
            blockers.append(f"preflight: {error}")

    if review_status_path is None:
        blockers.append("review status: an explicit review-status record is required")
    else:
        try:
            evidence["review_status_sha256"] = file_sha256(review_status_path)
            blockers.append(
                "review status: human reconciliation of the selected plan, preflight and "
                "review-status record is required; later prose cannot supersede either record"
            )
        except CivError as error:
            blockers.append(f"review status: {error}")

    return {
        "contract": "civ.scoring-readiness/v1alpha1",
        "official_score": False,
        "ready": False,
        "blockers": blockers,
        "evidence": evidence,
    }


def _check_cohort_readiness(
    ledger_root: Path,
    *,
    plan_path: Path,
    preflight_path: Path | None,
    review_status_path: Path | None,
    approval_path: Path | None,
) -> dict[str, object]:
    from civ_workshop.cohort_scoring import (
        check_computation_approval,
        input_fingerprint,
        load_evaluation_plan,
        policy_blockers,
    )

    blockers: list[str] = []
    evidence: dict[str, object] = {}
    receipts: list[IntakeReceipt] = []
    ledger_sha: str | None = None
    try:
        ledger = IntakeLedger(ledger_root)
        if ledger.database_path.is_file():
            receipts = ledger.receipts(read_only=True)
            ledger_sha = file_sha256(ledger.database_path)
        else:
            blockers.append("ledger: no intake ledger exists; no deliveries are recorded")
        evidence["receipts"] = len(receipts)
        evidence["ledger_sha256"] = ledger_sha
    except CivError as error:
        blockers.append(f"ledger: {error}")

    plan: dict[str, Any] | None = None
    try:
        plan = load_evaluation_plan(plan_path)
        evidence["plan_sha256"] = file_sha256(plan_path)
        evidence["runtime"] = plan["runtime"]
        evidence["tracks"] = [track["track_id"] for track in plan["tracks"]]
        blockers.extend(policy_blockers(plan))
    except CivError as error:
        blockers.append(f"plan: {error}")

    input_digest: str | None = None
    try:
        input_digest, fingerprint_diagnostics = input_fingerprint(ledger_root, plan_path)
        if input_digest is not None:
            evidence["input_fingerprint"] = input_digest
        blockers.extend(f"inputs: {item}" for item in fingerprint_diagnostics)
    except CivError as error:
        blockers.append(f"inputs: {error}")
    preflight_digest: str | None = None
    if preflight_path is None:
        blockers.append("preflight: an explicit cohort preflight record is required")
    else:
        try:
            preflight = read_json_file(preflight_path, "preflight")
            preflight_digest = file_sha256(preflight_path)
            evidence["preflight_sha256"] = preflight_digest
            _closed_fields(
                preflight,
                {
                    "contract",
                    "plan_sha256",
                    "input_fingerprint",
                    "ledger_designation",
                    "runtime_rehearsal",
                    "reference_reviews",
                    "human_component_scores",
                    "official_blockers",
                },
                "cohort preflight",
            )
            if preflight.get("contract") != "civ.cohort-preflight/v1alpha1":
                raise CivError("unsupported cohort preflight contract")
            if preflight.get("plan_sha256") != evidence.get("plan_sha256"):
                blockers.append("preflight: plan_sha256 does not match the selected plan")
            if preflight.get("input_fingerprint") != input_digest or input_digest is None:
                blockers.append(
                    "preflight: input_fingerprint does not match current scoring inputs"
                )
            if plan is not None:
                try:
                    evidence["human_component_scores"] = _human_component_scores(
                        preflight.get("human_component_scores"),
                        _require_string_list(plan["participants"]),
                    )
                except CivError as error:
                    blockers.append(f"human component scores: {error}")
            designation = require_mapping(preflight.get("ledger_designation"), "ledger designation")
            _closed_fields(
                designation,
                {"ledger_sha256", "designated_by", "designated_at"},
                "ledger designation",
            )
            if designation.get("ledger_sha256") != ledger_sha:
                blockers.append(
                    "ledger designation: ledger_sha256 does not match the current ledger"
                )
            require_string(designation.get("designated_by"), "ledger designation designated_by")
            _timestamp(designation.get("designated_at"), "ledger designation designated_at")

            if plan is not None:
                runtime_record = _bound_artifact(
                    preflight.get("runtime_rehearsal"),
                    preflight_path.parent,
                    "runtime rehearsal",
                    blockers,
                )
                if runtime_record is not None:
                    _closed_fields(
                        runtime_record,
                        {
                            "contract",
                            "plan_sha256",
                            "input_fingerprint",
                            "runtime_identity",
                            "tool_version",
                            "python_version",
                            "implementation_sha256",
                            "environment_sha256",
                            "outcome",
                        },
                        "runtime rehearsal artifact",
                    )
                    if runtime_record.get("contract") != "civ.runtime-rehearsal/v1alpha1":
                        blockers.append("runtime rehearsal: unsupported evidence contract")
                    if (
                        runtime_record.get("plan_sha256") != evidence.get("plan_sha256")
                        or runtime_record.get("input_fingerprint") != input_digest
                    ):
                        blockers.append(
                            "runtime rehearsal: plan or input fingerprint does not match"
                        )
                    if runtime_record.get("runtime_identity") != plan["runtime"]["identity"]:
                        blockers.append(
                            "runtime rehearsal: runtime identity does not match the plan"
                        )
                    if (
                        runtime_record.get("tool_version") != plan["runtime"]["tool_version"]
                        or runtime_record.get("python_version") != plan["runtime"]["python_version"]
                        or runtime_record.get("implementation_sha256")
                        != plan["runtime"]["implementation_sha256"]
                        or runtime_record.get("environment_sha256")
                        != plan["runtime"]["environment_sha256"]
                    ):
                        blockers.append(
                            "runtime rehearsal: measured runtime does not match the plan"
                        )
                    if runtime_record.get("outcome") != "passed":
                        blockers.append("runtime rehearsal: outcome is not passed")

                reviews = preflight.get("reference_reviews")
                expected_reviews = {
                    (str(track["track_id"]), str(product["product_id"])): (track, product)
                    for track in plan["tracks"]
                    for product in track["products"]
                }
                if not isinstance(reviews, list):
                    blockers.append("references: reference_reviews must be a list")
                else:
                    seen_reviews: set[tuple[str, str]] = set()
                    for index, item in enumerate(reviews):
                        row = require_mapping(item, f"reference review {index}")
                        _closed_fields(
                            row, {"track_id", "product_id", "artifact"}, "reference review"
                        )
                        key = (
                            require_string(row.get("track_id"), "reference review track_id"),
                            require_string(row.get("product_id"), "reference review product_id"),
                        )
                        if key not in expected_reviews:
                            blockers.append(f"references: unexpected review for {key[0]}/{key[1]}")
                            continue
                        if key in seen_reviews:
                            blockers.append(f"references: duplicate review for {key[0]}/{key[1]}")
                            continue
                        seen_reviews.add(key)
                        review_artifact = _bound_artifact(
                            row.get("artifact"),
                            preflight_path.parent,
                            f"reference review {key[0]}/{key[1]}",
                            blockers,
                        )
                        if review_artifact is None:
                            continue
                        _closed_fields(
                            review_artifact,
                            {
                                "contract",
                                "track_id",
                                "product_id",
                                "target",
                                "truth_sha256",
                                "decision",
                                "coverage",
                                "reviewer",
                                "reviewed_at",
                            },
                            "reference review artifact",
                        )
                        track, product = expected_reviews[key]
                        for field, expected in (
                            ("contract", "civ.reference-review-approval/v1alpha1"),
                            ("track_id", key[0]),
                            ("product_id", key[1]),
                            ("target", track["target"]),
                            ("truth_sha256", product["truth"]["sha256"]),
                            ("decision", "approved"),
                            ("coverage", "complete"),
                        ):
                            if review_artifact.get(field) != expected:
                                blockers.append(
                                    "references: review evidence does not approve the "
                                    f"configured {field} for {key[0]}/{key[1]}"
                                )
                        require_string(review_artifact.get("reviewer"), "reference review reviewer")
                        _timestamp(
                            review_artifact.get("reviewed_at"), "reference review reviewed_at"
                        )
                    missing_reviews = sorted(set(expected_reviews) - seen_reviews)
                    blockers.extend(
                        f"references: missing review for {track_id}/{product_id}"
                        for track_id, product_id in missing_reviews
                    )
            recorded = preflight.get("official_blockers")
            if not isinstance(recorded, list) or any(
                not isinstance(item, str) for item in recorded
            ):
                blockers.append("preflight: official_blockers must be a list of strings")
            else:
                blockers.extend(f"preflight unresolved: {item}" for item in recorded)
        except CivError as error:
            blockers.append(f"preflight: {error}")
    if review_status_path is None:
        blockers.append("review status: an explicit cohort review-status record is required")
    else:
        try:
            review_digest = file_sha256(review_status_path)
            evidence["review_status_sha256"] = review_digest
            review_status = read_json_file(review_status_path, "cohort review status")
            _closed_fields(
                review_status,
                {
                    "contract",
                    "plan_sha256",
                    "input_fingerprint",
                    "preflight_sha256",
                    "decision",
                    "reviewer",
                    "reviewed_at",
                    "confirmations",
                },
                "cohort review status",
            )
            if review_status.get("contract") != "civ.cohort-review-status/v1alpha1":
                blockers.append("review status: unsupported cohort review-status contract")
            if review_status.get("plan_sha256") != evidence.get("plan_sha256"):
                blockers.append("review status: plan_sha256 does not match the selected plan")
            if review_status.get("input_fingerprint") != input_digest or input_digest is None:
                blockers.append(
                    "review status: input_fingerprint does not match current scoring inputs"
                )
            if (
                review_status.get("preflight_sha256") != preflight_digest
                or preflight_digest is None
            ):
                blockers.append(
                    "review status: preflight_sha256 does not match the current preflight"
                )
            if review_status.get("decision") != "approved":
                blockers.append("review status: decision is not approved")
            require_string(review_status.get("reviewer"), "review status reviewer")
            _timestamp(review_status.get("reviewed_at"), "review status reviewed_at")
            confirmations = require_mapping(
                review_status.get("confirmations"), "review confirmations"
            )
            _closed_fields(
                confirmations,
                {"cutoff", "runtime", "ledger", "references", "scoring_policy"},
                "review confirmations",
            )
            for name in ("cutoff", "runtime", "ledger", "references", "scoring_policy"):
                if confirmations.get(name) is not True:
                    blockers.append(f"review status: confirmation '{name}' is not true")
        except CivError as error:
            blockers.append(f"review status: {error}")

    review_status_digest = evidence.get("review_status_sha256")
    if not isinstance(review_status_digest, str):
        review_status_digest = None
    blockers.extend(
        check_computation_approval(
            approval_path,
            plan_path=plan_path,
            input_digest=input_digest,
            preflight_sha256=preflight_digest,
            review_status_sha256=review_status_digest,
        )
    )

    return {
        "contract": "civ.scoring-readiness/v1alpha2",
        "official_score": False,
        "ready": not blockers,
        "blockers": blockers,
        "evidence": evidence,
    }


def _closed_fields(value: dict[str, Any], allowed: set[str], context: str) -> None:
    unknown = sorted(set(value) - allowed)
    if unknown:
        raise CivError(f"{context} has unknown field '{unknown[0]}'")


def _require_string_list(value: object) -> list[str]:
    if not isinstance(value, list) or not value or any(
        not isinstance(item, str) or not item for item in value
    ):
        raise CivError("evaluation plan participants must be a non-empty string list")
    return [item for item in value if isinstance(item, str)]


def _human_component_scores(
    value: object, participants: list[str]
) -> dict[str, dict[str, dict[str, object]]]:
    rows = require_mapping(value, "human component scores")
    if set(rows) != set(participants):
        raise CivError("records must cover every registered participant exactly once")
    normalized: dict[str, dict[str, dict[str, object]]] = {}
    for identity in participants:
        participant = require_mapping(rows[identity], f"scores for {identity}")
        _closed_fields(participant, {"evidence", "reproducibility"}, f"scores for {identity}")
        normalized[identity] = {}
        for component in ("evidence", "reproducibility"):
            score = require_mapping(participant.get(component), f"{identity} {component} score")
            _closed_fields(
                score,
                {"points", "reviewer", "reviewed_at", "notation"},
                f"{identity} {component} score",
            )
            points = score.get("points")
            if isinstance(points, bool) or not isinstance(points, (int, float)):
                raise CivError(f"{identity} {component} points must be between 0 and 15")
            try:
                finite_points = math.isfinite(float(points))
            except OverflowError:
                finite_points = False
            if not finite_points or not 0 <= points <= 15:
                raise CivError(f"{identity} {component} points must be between 0 and 15")
            normalized[identity][component] = {
                "points": points,
                "reviewer": require_string(
                    score.get("reviewer"), f"{identity} {component} reviewer"
                ),
                "reviewed_at": _timestamp(
                    score.get("reviewed_at"), f"{identity} {component} reviewed_at"
                ),
                "notation": require_string(
                    score.get("notation"), f"{identity} {component} notation"
                ),
            }
    return normalized


def _timestamp(value: object, context: str) -> str:
    text = require_string(value, context)
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError as error:
        raise CivError(f"{context} must be an ISO-8601 timestamp") from error
    if parsed.tzinfo is None:
        raise CivError(f"{context} must include a timezone")
    return parsed.isoformat()


def _bound_artifact(
    value: object,
    base: Path,
    context: str,
    blockers: list[str],
) -> dict[str, Any] | None:
    try:
        reference = require_mapping(value, f"{context} artifact reference")
        _closed_fields(reference, {"path", "sha256"}, f"{context} artifact reference")
        path_text = require_string(reference.get("path"), f"{context} artifact path")
        path = Path(path_text)
        path = path.resolve() if path.is_absolute() else (base / path).resolve()
        expected_hash = require_string(reference.get("sha256"), f"{context} artifact sha256")
        if file_sha256(path) != expected_hash:
            raise CivError("artifact hash does not match")
        return read_json_file(path, context)
    except CivError as error:
        blockers.append(f"{context}: {error}")
        return None


def _check_tracks(
    plan: dict[str, Any],
    base: Path,
    blockers: list[str],
    evidence: dict[str, object],
) -> set[str]:
    tracks = require_mapping(plan.get("tracks"), "plan tracks")
    if not {"kashiwa", "reims"}.issubset(tracks):
        blockers.append("target: plan must define both kashiwa and reims")
    seen: set[str] = set()
    validated: set[str] = set()
    targets: dict[str, str] = {}
    for dataset, value in tracks.items():
        track = require_mapping(value, f"track {dataset}")
        if track.get("mode") != "detection":
            continue
        targets[dataset] = require_string(track.get("event_rule"), f"{dataset} event_rule")
        if track.get("reference_status") != "reviewed":
            blockers.append(f"reference {dataset}: reference_status is not reviewed")
        blockers.append(
            f"target {dataset}: human confirmation of the event rule and complete "
            "source-bound label coverage is required; label packs do not encode that signoff"
        )
        products = track.get("products")
        if not isinstance(products, list) or not products:
            blockers.append(f"reference {dataset}: no products selected")
            continue
        for index, value in enumerate(products):
            context = f"reference {dataset} product {index}"
            try:
                product = require_mapping(value, context)
                recording = require_mapping(product.get("recording"), f"{context} recording")
                labels = require_mapping(product.get("labels"), f"{context} labels")
                source_hash = require_string(recording.get("sha256"), f"{context} source hash")
                if source_hash in seen:
                    raise CivError("duplicate source hash in selected products")
                seen.add(source_hash)
                label_path = base / require_string(labels.get("path"), f"{context} label path")
                if file_sha256(label_path) != labels.get("sha256"):
                    raise CivError("label pack hash does not match plan")
                pack = load_label_pack(label_path)
                if pack["source_sha256"] != source_hash or pack["dataset"] != dataset:
                    raise CivError("label pack source hash or dataset does not match plan")
                validated.add(source_hash)
            except CivError as error:
                blockers.append(f"{context}: {error}")
    evidence["event_rules"] = targets
    evidence["matched_reference_sources"] = sorted(validated)
    return validated


def require_official_readiness(report: dict[str, object]) -> None:
    """Reject official scoring unless every versioned readiness gate passed."""
    blockers = report.get("blockers", [])
    if report.get("ready") is not True or not isinstance(blockers, list) or blockers:
        raise CivError(f"official scoring blocked (result remains nonofficial): {blockers}")
