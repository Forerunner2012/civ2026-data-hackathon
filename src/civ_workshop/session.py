"""Resolve session overrides once into the existing evaluation-plan contract."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from civ_workshop.artifacts import canonical_json, file_sha256, require_string
from civ_workshop.cohort_scoring import load_evaluation_plan, validate_evaluation_plan
from civ_workshop.errors import CivError


def prepare_session(
    profile: Path,
    output: Path,
    *,
    cutoff: str | None = None,
    session_id: str | None = None,
    participants: list[str] | None = None,
) -> dict[str, Any]:
    """Materialize a profile without replacing an existing plan or changing input files."""
    profile = profile.resolve()
    output = output.resolve()
    plan = load_evaluation_plan(profile)
    plan["cutoff"] = (
        cutoff if cutoff is not None else os.environ.get("CIV_SESSION_CUTOFF", plan["cutoff"])
    )
    plan["session_id"] = (
        session_id
        if session_id is not None
        else os.environ.get("CIV_SESSION_ID", plan["session_id"])
    )
    if participants is not None:
        plan["participants"] = participants
    for track in plan["tracks"]:
        for product in track["products"]:
            for kind in ("recording", "manifest", "truth"):
                source = Path(require_string(product[kind]["path"], f"product {kind} path"))
                product[kind]["path"] = str(
                    source.resolve()
                    if source.is_absolute()
                    else (profile.parent / source).resolve()
                )
    validate_evaluation_plan(plan)
    created = False
    try:
        output.parent.mkdir(parents=True, exist_ok=True)
        with output.open("x", encoding="utf-8", newline="\n") as stream:
            created = True
            stream.write(canonical_json(plan) + "\n")
    except (OSError, CivError) as error:
        if created:
            output.unlink(missing_ok=True)
        raise CivError(f"cannot prepare session: {error}") from error
    return {
        "plan": str(output),
        "plan_sha256": file_sha256(output),
        "session_id": plan["session_id"],
        "cutoff": plan["cutoff"],
        "participants": plan["participants"],
    }
