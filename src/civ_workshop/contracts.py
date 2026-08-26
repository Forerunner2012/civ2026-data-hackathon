from __future__ import annotations

import re
from collections.abc import Iterable, Mapping

from civ_workshop.errors import CivError

# Top-level fields of each stable participant artifact. Stable schemas are closed by
# default, so anything else is rejected. tests/test_stable_contracts.py pins these to the
# published schemas/civ.*.v1.schema.json properties.
STABLE_FIELDS: dict[str, frozenset[str]] = {
    "civ.eventspec/v1": frozenset(
        {"spec", "name", "signals", "resources", "derive", "condition", "timing", "evidence"}
    ),
    "civ.point-resource/v1": frozenset({"contract", "coordinate_reference", "points"}),
    "civ.event/v1": frozenset(
        {
            "contract",
            "event_id",
            "bag_sha256",
            "spec_sha256",
            "start_ns",
            "end_ns",
            "trigger_values",
        }
    ),
    "civ.run-manifest/v1": frozenset(
        {
            "contract",
            "source",
            "spec",
            "events",
            "evidence",
            "resources",
            "clips",
            "metrics",
            "submission",
        }
    ),
    "civ.metrics/v1": frozenset(
        {"contract", "aggregate", "datasets", "label_pack_sha256", "matching"}
    ),
    "civ.submission-bundle/v1": frozenset({"contract", "reproduction"}),
    "civ.reproduction/v1": frozenset({"contract", "name", "sha256"}),
}


def require_closed_fields(value: Mapping[str, object], *, kind: str, expected: str) -> None:
    unknown = sorted(set(value) - STABLE_FIELDS[expected])
    if unknown:
        raise CivError(f"invalid {kind} '{expected}': unknown field '{unknown[0]}'")


def require_contract_present(actual: object, *, kind: str, expected: str) -> str:
    if not isinstance(actual, str) or not actual.strip():
        raise CivError(f"{kind} contract is required; expected '{expected}'")
    return actual.strip()


def require_coherent_contracts(contracts: Iterable[object]) -> None:
    identifiers = sorted({value for value in contracts if isinstance(value, str) and value})
    versions = {identifier.rsplit("/", 1)[-1] for identifier in identifiers}
    if versions == {"v1", "v1alpha1"}:
        raise CivError(
            "mixed participant contract versions: "
            f"{', '.join(identifiers)}; regenerate the complete working directory "
            "with one civ-workshop version"
        )


def require_run_contracts(
    manifest: Mapping[str, object], event_contracts: Iterable[object]
) -> None:
    """Reject mixed working directories first, then any non-stable member."""

    event_contracts = list(event_contracts)
    require_coherent_contracts([manifest.get("contract"), *event_contracts])
    require_stable_contract(
        manifest.get("contract"),
        kind="run manifest",
        expected="civ.run-manifest/v1",
        candidate="civ.run-manifest/v1alpha1",
    )
    require_closed_fields(manifest, kind="run manifest", expected="civ.run-manifest/v1")
    for contract in event_contracts:
        require_stable_contract(
            contract,
            kind="event",
            expected="civ.event/v1",
            candidate="civ.event/v1alpha1",
        )


def require_stable_contract(
    actual: object,
    *,
    kind: str,
    expected: str,
    candidate: str,
) -> str:
    actual = require_contract_present(actual, kind=kind, expected=expected)
    if actual == expected:
        return actual
    if actual == candidate:
        raise CivError(
            f"unsupported {kind} contract '{actual}'; expected '{expected}'; "
            "regenerate with the stable civ workflow"
        )

    namespace = expected.rsplit("/", 1)[0]
    if actual.startswith(f"{namespace}/"):
        version = actual.removeprefix(f"{namespace}/")
        major = re.fullmatch(r"v(\d+)(?:alpha\d+|beta\d+)?", version)
        if major is not None and int(major.group(1)) > 1:
            raise CivError(
                f"unsupported {kind} contract '{actual}'; "
                f"this civ-workshop supports '{expected}'"
            )
        if re.fullmatch(r"v\d+(?:alpha\d+|beta\d+)", version):
            raise CivError(
                f"unsupported {kind} contract '{actual}'; expected '{expected}'"
            )
    raise CivError(f"invalid {kind} contract '{actual}'; expected '{expected}'")
