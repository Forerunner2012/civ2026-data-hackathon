"""Read-only checks for the unapproved evaluation-plan drafts.

These checks expose prerequisites; they cannot create organizer authority.
"""

from __future__ import annotations

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


def _check_cohort_readiness(ledger_root: Path, *, plan_path: Path) -> dict[str, object]:
    from civ_workshop.cohort_scoring import input_fingerprint, load_evaluation_plan, policy_blockers

    blockers: list[str] = []
    evidence: dict[str, object] = {}
    try:
        plan = load_evaluation_plan(plan_path)
        digest, diagnostics = input_fingerprint(ledger_root, plan_path)
        evidence["plan_sha256"] = file_sha256(plan_path)
        evidence["input_fingerprint"] = digest
        blockers.extend(item for item in diagnostics if not item.startswith("submission:"))
        blockers.extend(policy_blockers(plan))
    except CivError as error:
        blockers.append(str(error))
    return {
        "contract": "civ.scoring-readiness/v1alpha2",
        "official_score": False,
        "ready": not blockers,
        "blockers": blockers,
        "evidence": evidence,
    }


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
