from __future__ import annotations

import re
import zipfile
from pathlib import Path

from civ_workshop.artifacts import (
    canonical_json,
    file_sha256,
    read_events,
    read_json_file,
    require_mapping,
    require_string,
)
from civ_workshop.contracts import (
    STABLE_FIELDS,
    require_closed_fields,
    require_run_contracts,
    require_stable_contract,
)
from civ_workshop.errors import CivError
from civ_workshop.event_spec import load_event_spec
from civ_workshop.submission_extension import (
    EXTENSION_CONTRACT,
    EXTENSION_MANIFEST_PATH,
    ExtensionEntry,
    load_extension_entries,
)

REPORT_HEADINGS = (
    "Question and hypothesis",
    "Signals used, missing, or unreliable",
    "What transferred and what did not",
    "One failure and the resulting change",
    "Downstream action and deployment mode",
)
FIGURE_SUFFIXES = {".jpeg", ".jpg", ".png", ".svg", ".webp"}
MAX_SUBMISSION_BUNDLE_BYTES = 12 * 1024 * 1024
MAX_SUBMISSION_ENTRY_BYTES = 8 * 1024 * 1024
MAX_SUBMISSION_UNCOMPRESSED_BYTES = 10 * 1024 * 1024
MAX_SUBMISSION_ARCHIVE_ENTRIES = 16
TEMPLATE_MARKER = "CIV_TEMPLATE_REPLACE_ME"


def submission_spec_path(working: Path) -> Path:
    detector_directory = working / "detector"
    if not detector_directory.is_dir():
        raise CivError("submission is missing the detector directory")
    detector_files = sorted(path for path in detector_directory.rglob("*") if path.is_file())
    specs = [path for path in detector_files if path.suffix.lower() in {".yaml", ".yml"}]
    if len(specs) != 1:
        raise CivError("submission detector directory must contain exactly one EventSpec")
    spec_path = specs[0]
    event_spec = load_event_spec(spec_path)
    allowed = {spec_path.resolve()}
    for binding in event_spec.resources:
        resource_path = (spec_path.parent / Path(binding.path)).resolve()
        try:
            resource_path.relative_to(spec_path.parent.resolve())
        except ValueError as error:
            raise CivError(
                f"resources.{binding.name}.path must stay inside the bundled detector directory"
            ) from error
        allowed.add(resource_path)
    forbidden = [path for path in detector_files if path.resolve() not in allowed]
    if forbidden:
        names = ", ".join(path.relative_to(working).as_posix() for path in forbidden)
        raise CivError(f"detector directory contains undeclared artifacts: {names}")
    return spec_path


def _validate_report(working: Path) -> tuple[Path, Path]:
    report_path = working / "report.md"
    if not report_path.is_file():
        raise CivError("submission is missing report.md")
    try:
        report = report_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as error:
        raise CivError(f"cannot read report.md: {error}") from error
    if TEMPLATE_MARKER in report:
        raise CivError("report still contains CIV_TEMPLATE_REPLACE_ME prompts")
    headings = [line.lstrip("#").strip() for line in report.splitlines() if line.startswith("#")]
    missing_headings = [heading for heading in REPORT_HEADINGS if heading not in headings]
    if missing_headings:
        raise CivError(f"report is missing headings: {', '.join(missing_headings)}")

    figures = re.findall(r"!\[[^\]]*\]\(([^)]+)\)", report)
    if len(figures) != 1:
        raise CivError("report must reference exactly one figure")
    figure_path = (working / figures[0]).resolve()
    try:
        figure_path.relative_to(working.resolve())
    except ValueError as error:
        raise CivError("report figure must be inside the submission working directory") from error
    if not figure_path.is_file():
        raise CivError(f"report figure does not exist: {figures[0]}")
    if figure_path.parent != working.resolve() or figure_path.suffix.lower() not in FIGURE_SUFFIXES:
        raise CivError("report figure must be a top-level supported image file")
    try:
        if TEMPLATE_MARKER.encode() in figure_path.read_bytes():
            raise CivError("report figure is still the CIV_TEMPLATE_REPLACE_ME placeholder")
    except OSError as error:
        raise CivError(f"cannot read report figure: {error}") from error

    reproduction = [
        working / name for name in ("reproduce.ps1", "reproduce.sh") if (working / name).is_file()
    ]
    if len(reproduction) != 1:
        raise CivError("submission must contain exactly one reproduce.ps1 or reproduce.sh")
    try:
        reproduction_text = reproduction[0].read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as error:
        raise CivError(f"cannot read {reproduction[0].name}: {error}") from error
    command_lines = [
        line.strip()
        for line in reproduction_text.splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]
    detect_command = re.compile(r"^(?:&\s*)?(?:uv\s+run\s+)?civ\s+detect(?:\s|$)")
    if not any(detect_command.match(line) for line in command_lines):
        raise CivError("reproduction entry point must invoke civ detect")
    return figure_path, reproduction[0]


def _validate_manifest(
    working: Path,
    spec_path: Path,
    *,
    require_local_evidence: bool,
    require_submission: bool,
) -> str:
    manifest = read_json_file(working / "run-manifest.json", "run manifest")
    manifest_contract = require_string(manifest.get("contract"), "run manifest contract")
    source = require_mapping(manifest.get("source"), "run manifest source")
    source_hash = require_string(source.get("sha256"), "run manifest source sha256")
    spec = require_mapping(manifest.get("spec"), "run manifest spec")
    spec_hash = require_string(spec.get("sha256"), "run manifest spec sha256")
    if file_sha256(spec_path) != spec_hash:
        raise CivError("EventSpec hash does not match the run manifest")
    event_spec = load_event_spec(spec_path)
    raw_resources = manifest.get("resources", [])
    if not isinstance(raw_resources, list):
        raise CivError("run manifest resources must be a list")
    expected_resources = {
        binding.name: binding for binding in event_spec.resources
    }
    if len(raw_resources) != len(expected_resources):
        raise CivError("run manifest resources do not match the EventSpec bindings")
    seen_resources: set[str] = set()
    for index, raw_resource in enumerate(raw_resources):
        resource = require_mapping(raw_resource, f"run manifest resource {index}")
        name = require_string(resource.get("name"), f"run manifest resource {index} name")
        binding = expected_resources.get(name)
        if binding is None or name in seen_resources:
            raise CivError("run manifest resources do not match the EventSpec bindings")
        seen_resources.add(name)
        contract = require_string(
            resource.get("contract"), f"run manifest resource {index} contract"
        )
        path = require_string(resource.get("path"), f"run manifest resource {index} path")
        resource_hash = require_string(
            resource.get("sha256"), f"run manifest resource {index} sha256"
        )
        if contract != binding.contract or path != binding.path:
            raise CivError("run manifest resources do not match the EventSpec bindings")
        if re.fullmatch(r"[0-9a-f]{64}", resource_hash) is None:
            raise CivError(f"run manifest resource '{name}' sha256 is invalid")
        if manifest_contract == "civ.run-manifest/v2":
            bundled_resource = spec_path.parent / Path(binding.path)
            if bundled_resource.is_symlink():
                raise CivError(f"bundled resource '{name}' must not be a symlink")
            if not bundled_resource.is_file():
                raise CivError(f"bundled resource '{name}' is missing: {binding.path}")
            if file_sha256(bundled_resource) != resource_hash:
                raise CivError(f"bundled resource '{name}' hash changed: {binding.path}")

    events_path = working / "events.jsonl"
    events_metadata = require_mapping(manifest.get("events"), "run manifest events")
    if file_sha256(events_path) != require_string(
        events_metadata.get("sha256"), "run manifest events sha256"
    ):
        raise CivError("events.jsonl hash does not match the run manifest")
    events = read_events(events_path)
    require_run_contracts(manifest, [event.contract for event in events])
    if events_metadata.get("count") != len(events):
        raise CivError("event count does not match the run manifest")
    if events != sorted(events, key=lambda item: (item.interval, item.event_id)):
        raise CivError("events.jsonl is not deterministically ordered")
    for event in events:
        if event.bag_sha256 != source_hash or event.spec_sha256 != spec_hash:
            raise CivError(f"event {event.event_id} provenance does not match the run manifest")

    metrics_path = working / "metrics.json"
    metrics_metadata = require_mapping(manifest.get("metrics"), "run manifest metrics")
    if file_sha256(metrics_path) != require_string(
        metrics_metadata.get("sha256"), "run manifest metrics sha256"
    ):
        raise CivError("metrics.json hash does not match the run manifest")
    metrics = read_json_file(metrics_path, "metrics")
    if metrics.get("contract") == "civ.metrics/v2":
        require_closed_fields(metrics, kind="metrics", expected="civ.metrics/v2")
        if set(metrics) != STABLE_FIELDS["civ.metrics/v2"]:
            raise CivError("unevaluated metrics are missing required fields")
        empty = dict.fromkeys(("counts", "precision", "recall", "f1", "match_quality"))
        if (
            metrics.get("status") != "not_evaluated"
            or not isinstance(metrics.get("reason"), str)
            or not str(metrics["reason"]).strip()
            or metrics.get("label_pack_sha256") is not None
            or metrics.get("matching") is not None
            or metrics.get("aggregate") != empty
            or metrics.get("datasets") != [{**empty, "source_sha256": source_hash}]
        ):
            raise CivError("unevaluated metrics must have null scores and match the run source")
    else:
        require_stable_contract(
            metrics.get("contract"),
            kind="metrics",
            expected="civ.metrics/v1",
            candidate="civ.metrics/v1alpha1",
        )
        require_closed_fields(metrics, kind="metrics", expected="civ.metrics/v1")

    if require_submission and "submission" not in manifest:
        raise CivError("run manifest is missing the submission declaration")
    if "submission" in manifest:
        submission = require_mapping(manifest.get("submission"), "run manifest submission")
        expected_submission = (
            "civ.submission-bundle/v2"
            if manifest_contract == "civ.run-manifest/v2"
            else "civ.submission-bundle/v1"
        )
        require_stable_contract(
            submission.get("contract"),
            kind="submission bundle",
            expected=expected_submission,
            candidate="civ.submission-bundle/v1alpha1",
        )
        require_closed_fields(
            submission, kind="submission bundle", expected=expected_submission
        )
        reproduction = require_mapping(
            submission.get("reproduction"), "run manifest submission reproduction"
        )
        require_stable_contract(
            reproduction.get("contract"),
            kind="reproduction",
            expected="civ.reproduction/v1",
            candidate="civ.reproduction/v1alpha1",
        )
        require_closed_fields(reproduction, kind="reproduction", expected="civ.reproduction/v1")
        reproduction_name = require_string(
            reproduction.get("name"), "run manifest submission reproduction name"
        )
        reproduction_path = working / reproduction_name
        if reproduction_name not in {"reproduce.ps1", "reproduce.sh"}:
            raise CivError("run manifest submission reproduction name is invalid")
        if file_sha256(reproduction_path) != require_string(
            reproduction.get("sha256"), "run manifest submission reproduction sha256"
        ):
            raise CivError("reproduction hash does not match the run manifest")
        extension_declaration = submission.get("extension")
        if extension_declaration is not None:
            extension = require_mapping(
                extension_declaration, "run manifest submission extension"
            )
            if set(extension) != {"contract", "name", "sha256"}:
                raise CivError("run manifest submission extension declaration is invalid")
            if extension.get("contract") != EXTENSION_CONTRACT:
                raise CivError(
                    f"invalid submission extension contract '{extension.get('contract')}'; "
                    f"expected '{EXTENSION_CONTRACT}'"
                )
            if extension.get("name") != EXTENSION_MANIFEST_PATH:
                raise CivError(
                    f"submission extension name must be {EXTENSION_MANIFEST_PATH}"
                )
            extension_path = working / EXTENSION_MANIFEST_PATH
            if not extension_path.is_file():
                raise CivError("submission extension manifest is missing")
            if file_sha256(extension_path) != require_string(
                extension.get("sha256"), "run manifest submission extension sha256"
            ):
                raise CivError("submission extension manifest hash does not match the run manifest")

    raw_clips = manifest.get("clips")
    if not isinstance(raw_clips, list):
        raise CivError("run manifest clips must be a list")
    for index, raw_clip in enumerate(raw_clips):
        clip = require_mapping(raw_clip, f"run manifest clip {index}")
        clip_name = require_string(clip.get("name"), f"run manifest clip {index} name")
        clip_path = (working / clip_name).resolve()
        evidence_root = (working / "evidence").resolve()
        try:
            clip_path.relative_to(evidence_root)
        except ValueError as error:
            raise CivError(f"clip path is outside evidence/: {clip_name}") from error
        clip_hash = require_string(clip.get("sha256"), f"run manifest clip {index} sha256")
        if require_local_evidence:
            if not clip_path.is_file():
                raise CivError(f"manifest clip does not exist: {clip_name}")
            if file_sha256(clip_path) != clip_hash:
                raise CivError(f"clip hash does not match the run manifest: {clip_name}")
        if clip.get("valid") is not True:
            raise CivError(f"clip is not marked valid: {clip_name}")
    return manifest_contract


def _validate_extension(
    working: Path, spec_path: Path, manifest_contract: str
) -> list[ExtensionEntry]:
    entries = load_extension_entries(working)
    if manifest_contract == "civ.run-manifest/v1":
        if entries or (working / EXTENSION_MANIFEST_PATH).exists():
            raise CivError("v1 submission bundle cannot contain extension artifacts")
        return []
    event_spec = load_event_spec(spec_path)
    resource_paths = {
        (spec_path.parent / Path(binding.path)).relative_to(working).as_posix()
        for binding in event_spec.resources
    }
    declared_resource_paths = {
        entry.path for entry in entries if entry.kind == "external-resource"
    }
    if declared_resource_paths != resource_paths:
        raise CivError(
            "submission extension external-resource entries do not match EventSpec resources"
        )
    extension_root = working / "extension"
    actual_extension_files = {
        path.relative_to(working).as_posix()
        for path in extension_root.rglob("*")
        if path.is_file()
    }
    declared_extension_files = {EXTENSION_MANIFEST_PATH} | {
        entry.path for entry in entries if entry.path.startswith("extension/")
    }
    undeclared = sorted(actual_extension_files - declared_extension_files)
    if undeclared:
        raise CivError(f"submission extension contains undeclared payload: {undeclared[0]}")
    return entries


def _bundle_entries(
    working: Path,
    spec_path: Path,
    figure_path: Path,
    reproduction_path: Path,
    extension_entries: list[ExtensionEntry],
) -> list[Path]:
    required = [
        spec_path,
        working / "events.jsonl",
        figure_path,
        working / "metrics.json",
        working / "report.md",
        reproduction_path,
        working / "run-manifest.json",
    ]
    if extension_entries:
        required.append(working / EXTENSION_MANIFEST_PATH)
        required.extend(working / entry.path for entry in extension_entries)
    missing = [path.name for path in required if not path.is_file()]
    if missing:
        raise CivError(f"submission is missing required artifacts: {', '.join(sorted(missing))}")
    return sorted(required, key=lambda path: path.relative_to(working).as_posix())


def _validate_bundle_limits(working: Path, entries: list[Path]) -> None:
    if len(entries) > MAX_SUBMISSION_ARCHIVE_ENTRIES:
        raise CivError(
            f"submission has more than {MAX_SUBMISSION_ARCHIVE_ENTRIES} metadata artifacts"
        )
    total_size = 0
    projected_archive_size = 22
    for path in entries:
        try:
            size = path.stat().st_size
        except OSError as error:
            raise CivError(f"cannot inspect submission artifact {path}: {error}") from error
        relative_name = path.relative_to(working).as_posix()
        if size > MAX_SUBMISSION_ENTRY_BYTES:
            raise CivError(
                f"submission artifact exceeds {MAX_SUBMISSION_ENTRY_BYTES} bytes: {relative_name}"
            )
        total_size += size
        projected_archive_size += size + 76 + 2 * len(relative_name.encode("utf-8"))
    if total_size > MAX_SUBMISSION_UNCOMPRESSED_BYTES:
        raise CivError(
            "submission metadata exceeds "
            f"{MAX_SUBMISSION_UNCOMPRESSED_BYTES} uncompressed bytes"
        )
    if projected_archive_size > MAX_SUBMISSION_BUNDLE_BYTES:
        raise CivError(
            f"submission bundle would exceed {MAX_SUBMISSION_BUNDLE_BYTES} bytes"
        )


def validate_submission_directory(
    working: Path,
    *,
    require_local_evidence: bool = True,
    require_submission: bool = False,
) -> list[Path]:
    working = working.resolve()
    if not working.is_dir():
        raise CivError(f"submission working directory does not exist: {working}")
    figure_path, reproduction_path = _validate_report(working)
    spec_path = submission_spec_path(working)
    manifest_contract = _validate_manifest(
        working,
        spec_path,
        require_local_evidence=require_local_evidence,
        require_submission=require_submission,
    )
    extension_entries = _validate_extension(working, spec_path, manifest_contract)
    entries = _bundle_entries(
        working, spec_path, figure_path, reproduction_path, extension_entries
    )
    folded_names = [path.relative_to(working).as_posix().casefold() for path in entries]
    if len(folded_names) != len(set(folded_names)):
        raise CivError("submission contains duplicate or case-colliding artifact paths")
    symlinks = [path.relative_to(working).as_posix() for path in entries if path.is_symlink()]
    if symlinks:
        raise CivError(f"submission artifacts must not be symlinks: {symlinks[0]}")
    _validate_bundle_limits(working, entries)
    return entries


def write_canonical_submission_bundle(
    bundle_path: Path, working: Path, entries: list[Path]
) -> None:
    try:
        with zipfile.ZipFile(bundle_path, "w", compression=zipfile.ZIP_STORED) as archive:
            for path in sorted(
                entries, key=lambda candidate: candidate.relative_to(working).as_posix()
            ):
                relative_name = path.relative_to(working).as_posix()
                info = zipfile.ZipInfo(relative_name, date_time=(1980, 1, 1, 0, 0, 0))
                info.compress_type = zipfile.ZIP_STORED
                info.create_system = 3
                info.external_attr = 0o100644 << 16
                archive.writestr(info, path.read_bytes())
    except OSError as error:
        raise CivError(f"cannot assemble submission bundle: {error}") from error


def build_report_bundle(working: Path) -> dict[str, str]:
    working = working.resolve()
    entries = validate_submission_directory(working)
    reproduction_path = next(
        path for path in entries if path.name in {"reproduce.ps1", "reproduce.sh"}
    )
    manifest_path = working / "run-manifest.json"
    manifest = read_json_file(manifest_path, "run manifest")
    manifest["contract"] = "civ.run-manifest/v2"
    submission: dict[str, object] = {
        "contract": "civ.submission-bundle/v2",
        "reproduction": {
            "contract": "civ.reproduction/v1",
            "name": reproduction_path.name,
            "sha256": file_sha256(reproduction_path),
        },
    }
    extension_path = working / EXTENSION_MANIFEST_PATH
    if extension_path.is_file():
        submission["extension"] = {
            "contract": EXTENSION_CONTRACT,
            "name": EXTENSION_MANIFEST_PATH,
            "sha256": file_sha256(extension_path),
        }
    manifest["submission"] = submission
    manifest_path.write_text(f"{canonical_json(manifest)}\n", encoding="utf-8", newline="\n")
    entries = validate_submission_directory(working, require_submission=True)
    bundle_path = working / "submission.zip"
    write_canonical_submission_bundle(bundle_path, working, entries)
    return {"bundle": bundle_path.name, "sha256": file_sha256(bundle_path)}
