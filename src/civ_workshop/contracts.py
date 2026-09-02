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
    "civ.run-manifest/v2": frozenset(
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
    "civ.submission-bundle/v2": frozenset({"contract", "extension", "reproduction"}),
    "civ.submission-extension/v1": frozenset({"contract", "entries"}),
    "civ.reproduction/v1": frozenset({"contract", "name", "sha256"}),
    "civ.data-product-recipe/v1": frozenset(
        {
            "contract",
            "recipe_id",
            "version",
            "product_name",
            "source",
            "dataset",
            "split",
            "topics",
            "license",
            "attribution",
            "rights_scope",
            "modifications",
        }
    ),
    "civ.data-product-manifest/v1": frozenset(
        {"contract", "product", "parent", "recipe", "provenance", "required_disk_bytes"}
    ),
    "civ.data-product-set/v1": frozenset(
        {"contract", "release_id", "products", "required_disk_bytes"}
    ),
    "civ.camera-context-recipe/v1": frozenset(
        {
            "contract",
            "recipe_id",
            "version",
            "product_name",
            "source",
            "signal_product",
            "dataset",
            "split",
            "topics",
            "time_bounds",
            "calibration",
            "rights",
        }
    ),
    "civ.camera-context-privacy-rights-approval/v1": frozenset(
        {
            "contract",
            "approval_id",
            "authority",
            "decision",
            "frame_review_set_sha256",
            "inspection_complete",
            "redaction_required",
            "rights_statement",
        }
    ),
    "civ.camera-context-manifest/v1": frozenset(
        {
            "contract",
            "approval",
            "calibration",
            "dataset",
            "parent",
            "product",
            "recipe",
            "rights",
            "signal_product",
            "split",
            "time_bounds",
            "transformation",
        }
    ),
    "civ.camera-context-set/v1": frozenset(
        {"contract", "release_id", "approval", "products", "required_disk_bytes"}
    ),
    "civ.participant-kit-inventory/v1": frozenset(
        {
            "contract",
            "release_id",
            "content_profile",
            "product_set",
            "tool",
            "container_candidate",
            "viewers",
            "tracked_assets",
            "recovery_notice",
            "context_packs",
            "layout",
            "required_disk_bytes",
        }
    ),
    "civ.attendee-fallback-pack/v1": frozenset(
        {"contract", "product_set_sha256", "datasets", "files", "required_disk_bytes"}
    ),
    "civ.attendee-kit-assembly/v1": frozenset(
        {
            "contract",
            "release_id",
            "inventory_sha256",
            "files",
            "components",
            "required_disk_bytes",
            "disk_budget",
        }
    ),
    "civ.release-freeze/v1": frozenset(
        {
            "contract",
            "release_id",
            "source_commit",
            "assembly",
            "architecture",
            "artifacts",
            "sboms",
            "legal",
            "development_authority",
            "recovery_notice",
            "required_disk_bytes",
        }
    ),
    "civ.release-freeze/v2": frozenset(
        {
            "contract",
            "release_id",
            "source_commit",
            "assembly",
            "architecture",
            "artifacts",
            "sboms",
            "legal",
            "development_authority",
            "recovery_notice",
            "required_disk_bytes",
        }
    ),
    "civ.workstation-qualification/v1": frozenset(
        {
            "contract",
            "qualification_id",
            "release",
            "machines",
            "viewer_checks",
            "web_route",
            "recovery",
            "interventions",
            "status",
        }
    ),
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
    manifest_contract = require_contract_present(
        manifest.get("contract"), kind="run manifest", expected="civ.run-manifest/v2"
    )
    if manifest_contract not in {"civ.run-manifest/v1", "civ.run-manifest/v2"}:
        require_stable_contract(
            manifest_contract,
            kind="run manifest",
            expected="civ.run-manifest/v2",
            candidate="civ.run-manifest/v1alpha1",
        )
    require_closed_fields(manifest, kind="run manifest", expected=manifest_contract)
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
