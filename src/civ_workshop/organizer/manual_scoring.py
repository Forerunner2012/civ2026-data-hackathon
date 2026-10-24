from __future__ import annotations

from typing import Any


def review_sheet(
    participants: list[str], plan_sha256: str, input_fingerprint: str | None
) -> dict[str, Any]:
    """Prepare a private worksheet; generating it never awards or approves points."""
    return {
        "status": "pending_manual_review",
        "plan_sha256": plan_sha256,
        "input_fingerprint": input_fingerprint,
        "criteria": {
            "evidence": {
                "maximum_points": 15,
                "subcriteria": {
                    "relevant_synchronized_topics": 5,
                    "bounded_windows_and_event_coverage": 5,
                    "measured_extraction_and_limitations": 5,
                },
            },
            "reproducibility": {
                "maximum_points": 15,
                "subcriteria": {
                    "one_documented_reproduction_command": 5,
                    "exact_inputs_resources_and_environment": 5,
                    "repeatable_outputs_and_explained_differences": 5,
                },
            },
        },
        "participants": {
            identity: {
                "reviewer": None,
                "evidence_points": None,
                "reproducibility_points": None,
                "artifact_references_and_reasons": [],
            }
            for identity in participants
        },
        "instructions": (
            "Organizer or agent review: award 0-5 for each subcriterion and cite artifacts. "
            "Keep jury and other bonus awards separately. Cave points are automatic and "
            "require no manual or Evidence award. Complete final totals outside this runner."
        ),
    }
