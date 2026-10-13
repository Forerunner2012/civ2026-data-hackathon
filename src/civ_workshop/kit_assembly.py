from __future__ import annotations

import argparse
import csv
import json
import math
import re
import shutil
import sys
from collections.abc import Mapping, Sequence
from pathlib import Path

from mcap.exceptions import McapError
from mcap.reader import make_reader
from mcap.writer import CompressionType, Writer

from civ_workshop.artifacts import canonical_json, file_sha256, read_json_file
from civ_workshop.errors import CivError
from civ_workshop.inspection import MessageDecoder, extract_field, inspect_bag
from civ_workshop.kit_inventory import (
    ACCEPTED_PRODUCT_SET_SHA256,
    CONTRACT,
    FORBIDDEN_PUBLIC_TERMS,
    PHASE5_RELEASE,
    TRACKED_ASSET_SOURCES,
    audit_kit_inventory,
)
from civ_workshop.presentation_files import verified_presentations
from civ_workshop.submission_extension import contained_archive_path, safe_archive_path

ASSEMBLY_CONTRACT = "civ.attendee-kit-assembly/v1"
INVENTORY_CONTRACT = CONTRACT
ASSEMBLY_FIELDS = {
    "contract",
    "release_id",
    "inventory_sha256",
    "files",
    "components",
    "required_disk_bytes",
    "disk_budget",
}
TWO_TIB = 2 * 1024**4
FOUR_SSD_BUDGET = 4 * TWO_TIB

FALLBACK_SIGNALS: dict[str, tuple[tuple[str, str], ...]] = {
    "kashiwa": (
        ("/pix_hooke/v2a_steerstafb", "vcu_chassis_steer_angle_fb"),
        ("/pix_hooke/v2a_drivestafb", "vcu_chassis_speed_fb"),
        ("/pix_hooke/v2a_brakestafb", "vcu_chassis_brake_padl_fb"),
        ("/perception/object_recognition/is_object_detected", "data"),
    ),
    "reims": (
        ("/zed/zed_node/imu/data", "angular_velocity.z"),
        ("/fix_velocity", "twist.twist.linear.x"),
        ("/fix_velocity", "twist.twist.linear.y"),
        ("/fix_velocity", "twist.twist.linear.z"),
        ("/fix", "latitude"),
        ("/fix", "longitude"),
    ),
}

PARTICIPANT_TEXT_SUFFIXES = frozenset(
    {
        ".html",
        ".js",
        ".json",
        ".md",
        ".ps1",
        ".sh",
        ".svg",
        ".ts",
        ".tsx",
        ".xml",
        ".yaml",
        ".yml",
    }
)
FORBIDDEN_ASSEMBLY_TARGET_PREFIXES = ("tool/source/",)
PARTICIPANT_RUNTIME_MODULES = (
    "artifacts.py",
    "clipping.py",
    "contracts.py",
    "detection.py",
    "doctor.py",
    "errors.py",
    "event_spec.py",
    "inspection.py",
    "models.py",
    "participant_cli.py",
    "participant_commands.py",
    "reporting.py",
    "resources.py",
    "schema_pins.py",
    "score_reference.py",
    "scoring.py",
    "submission.py",
    "submission_extension.py",
)
PRIVATE_RUNTIME_MODULES = frozenset(
    {
        "batch.py",
        "camera_context.py",
        "cli.py",
        "data_products.py",
        "intake.py",
        "kit_assembly.py",
        "presentation_files.py",
        "kit_inventory.py",
        "label_review.py",
        "label_packs.py",
        "release_freeze.py",
        "tally.py",
        "workstation_qualification.py",
    }
)
FORBIDDEN_ASSEMBLY_TEXT = (
    "/organizers",
    "civ intake-form",
    "civ intake-local",
    "civ intake-tally",
    "civ score-batch",
    "jury-pack-internal",
    "live_coach_token",
)
ABSOLUTE_PATH_PATTERN = re.compile(r"(?:[A-Za-z]:\\|/(?:home|Users)/)")


def _target(value: str) -> str:
    safe_archive_path(value, 'assembly target')
    return value


def _copy_file(source: Path, target: Path) -> None:
    if not source.is_file():
        raise CivError(f"assembly input does not exist: {source.name}")
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, target)


def _tree_inputs(source: Path, output: Path, prefix: str) -> list[tuple[Path, Path]]:
    if not source.is_dir():
        raise CivError(f"assembly input directory does not exist: {source.name}")
    inputs: list[tuple[Path, Path]] = []
    for path in sorted(item for item in source.rglob("*") if item.is_file()):
        relative = path.relative_to(source)
        if any(
            part in {"__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache"}
            for part in relative.parts
        ):
            continue
        if path.suffix in {".pyc", ".pyo"}:
            continue
        target = contained_archive_path(
            output, f"{prefix}/{relative.as_posix()}", "assembly target"
        )
        inputs.append((path, target))
    return inputs


def _scalar(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float, str)):
        return str(value)
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def _byte_size(record: Mapping[str, object], context: str) -> int:
    value = record.get("byte_size")
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise CivError(f"{context} byte_size must be a non-negative integer")
    return value


def _write_signal_table(source: Path, dataset: str, target: Path) -> int:
    signals = FALLBACK_SIGNALS[dataset]
    topics = sorted({topic for topic, _ in signals})
    fields = {
        topic: [field for signal_topic, field in signals if signal_topic == topic]
        for topic in topics
    }
    decoder = MessageDecoder()
    rows = 0
    start_ns: int | None = None
    target.parent.mkdir(parents=True, exist_ok=True)
    try:
        with source.open("rb") as stream, target.open("w", encoding="utf-8", newline="") as output:
            writer = csv.writer(output, lineterminator="\n")
            writer.writerow(("timestamp_ns", "relative_seconds", "topic", "field", "value"))
            for schema, channel, message in make_reader(stream, validate_crcs=True).iter_messages(
                topics=topics
            ):
                if start_ns is None:
                    start_ns = message.log_time
                payload = decoder.decode(schema, channel, message.data)
                for field in fields[channel.topic]:
                    writer.writerow(
                        (
                            message.log_time,
                            f"{(message.log_time - start_ns) / 1_000_000_000:.9f}",
                            channel.topic,
                            field,
                            _scalar(extract_field(payload, field, f"topic {channel.topic}")),
                        )
                    )
                    rows += 1
    except (OSError, McapError) as error:
        raise CivError(f"cannot build fallback table for {source.name}: {error}") from error
    if rows == 0:
        raise CivError(f"fallback table contains no rows: {source.name}")
    return rows


def _write_neutral_clip(
    source: Path, dataset: str, start_ns: int, end_ns: int, target: Path
) -> None:
    topics = sorted({topic for topic, _ in FALLBACK_SIGNALS[dataset]})
    target.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    try:
        with source.open("rb") as input_stream, target.open("wb") as output_stream:
            reader = make_reader(input_stream, validate_crcs=True)
            writer = Writer(output_stream, compression=CompressionType.NONE)
            writer.start(profile=reader.get_header().profile, library="civ-workshop/fallback-v1")
            schema_ids: dict[int, int] = {}
            channel_ids: dict[int, int] = {}
            for schema, channel, message in reader.iter_messages(
                topics=topics, start_time=start_ns, end_time=end_ns
            ):
                schema_id = 0
                if schema is not None:
                    schema_id = schema_ids.get(schema.id, 0)
                    if not schema_id:
                        schema_id = writer.register_schema(
                            name=schema.name, encoding=schema.encoding, data=schema.data
                        )
                        schema_ids[schema.id] = schema_id
                channel_id = channel_ids.get(channel.id)
                if channel_id is None:
                    channel_id = writer.register_channel(
                        schema_id=schema_id,
                        topic=channel.topic,
                        message_encoding=channel.message_encoding,
                        metadata=channel.metadata,
                    )
                    channel_ids[channel.id] = channel_id
                writer.add_message(
                    channel_id=channel_id,
                    log_time=message.log_time,
                    publish_time=message.publish_time,
                    sequence=message.sequence,
                    data=message.data,
                )
                count += 1
            writer.finish()
    except (OSError, McapError) as error:
        raise CivError(f"cannot build fallback clip for {source.name}: {error}") from error
    if count == 0:
        raise CivError(f"fallback clip contains no messages: {source.name}")


def _write_plot(table: Path, dataset: str, target: Path) -> None:
    preferred_topic, preferred_field = FALLBACK_SIGNALS[dataset][0]
    points: list[tuple[float, float]] = []
    with table.open("r", encoding="utf-8", newline="") as stream:
        for row in csv.DictReader(stream):
            if row["topic"] != preferred_topic or row["field"] != preferred_field:
                continue
            try:
                points.append((float(row["relative_seconds"]), float(row["value"])))
            except ValueError:
                continue
    if not points:
        raise CivError(f"cannot render fallback plot from {table.name}")
    stride = max(1, math.ceil(len(points) / 1200))
    points = points[::stride]
    min_x, max_x = points[0][0], points[-1][0]
    min_y = min(value for _, value in points)
    max_y = max(value for _, value in points)
    x_span = max(max_x - min_x, 1.0)
    y_span = max(max_y - min_y, 1.0)
    polyline = " ".join(
        f"{40 + 1120 * (x - min_x) / x_span:.2f},{30 + 300 * (max_y - y) / y_span:.2f}"
        for x, y in points
    )
    title = f"{dataset.title()} neutral signal overview: {preferred_topic}.{preferred_field}"
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="380" '
        'viewBox="0 0 1200 380">\n'
        f"<title>{title}</title><desc>Full-route signal overview; not an answer interval.</desc>\n"
        '<rect width="1200" height="380" fill="white"/>'
        '<path d="M40 30V330H1160" fill="none" stroke="#333"/>\n'
        f'<polyline points="{polyline}" fill="none" stroke="#165d7a" stroke-width="2"/>\n'
        f'<text x="40" y="365" font-family="sans-serif" font-size="16">{title}</text>\n</svg>\n'
    )
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(svg, encoding="utf-8", newline="\n")


def build_fallback_pack(product_set_path: Path, data_root: Path, output: Path) -> dict[str, object]:
    product_set = read_json_file(product_set_path, "participant product set")
    if file_sha256(product_set_path) != ACCEPTED_PRODUCT_SET_SHA256:
        raise CivError("fallback pack requires the accepted participant product set")
    products = product_set.get("products")
    if not isinstance(products, list) or len(products) != 13:
        raise CivError("fallback pack requires exactly 13 participant products")
    if output.exists():
        raise CivError("fallback output must not already exist")
    output.mkdir(parents=True)
    rows_by_dataset = {"kashiwa": 0, "reims": 0}
    representatives: dict[str, tuple[Path, Path]] = {}
    for raw in products:
        if not isinstance(raw, dict):
            raise CivError("participant product entry must be a mapping")
        dataset = str(raw.get("dataset"))
        name = str(raw.get("name"))
        if dataset not in FALLBACK_SIGNALS or Path(name).name != name:
            raise CivError("participant product has an unsupported fallback identity")
        source = data_root / name
        if file_sha256(source) != raw.get("sha256"):
            raise CivError(f"fallback source does not match participant product: {name}")
        table = output / dataset / "tables" / f"{Path(name).stem}.csv"
        rows_by_dataset[dataset] += _write_signal_table(source, dataset, table)
        representatives.setdefault(dataset, (source, table))
    for dataset, (source, table) in representatives.items():
        inventory = inspect_bag(source)
        start = int(inventory["start_time_ns"])
        end = int(inventory["end_time_ns"])
        duration = end - start
        window = min(10_000_000_000, max(1, duration // 8))
        anchors = (start, start + max(0, (duration - window) // 2), max(start, end - window))
        for index, anchor in enumerate(anchors, start=1):
            _write_neutral_clip(
                source,
                dataset,
                anchor,
                min(end, anchor + window),
                output / dataset / "clips" / f"neutral-window-{index}.mcap",
            )
        _write_plot(table, dataset, output / dataset / "plots" / "signal-overview.svg")
    files = _file_records(output, excluded=set())
    fallback_bytes = sum(_byte_size(item, "fallback file") for item in files)
    manifest: dict[str, object] = {
        "contract": "civ.attendee-fallback-pack/v1",
        "product_set_sha256": ACCEPTED_PRODUCT_SET_SHA256,
        "datasets": [
            {
                "dataset": dataset,
                "full_rate_rows": rows_by_dataset[dataset],
                "neutral_clip_count": 3,
            }
            for dataset in sorted(rows_by_dataset)
        ],
        "files": files,
        "required_disk_bytes": fallback_bytes,
    }
    manifest_path = output / "fallback-manifest.json"
    manifest_path.write_text(f"{canonical_json(manifest)}\n", encoding="utf-8", newline="\n")
    return {
        "file_count": len(files) + 1,
        "required_disk_bytes": fallback_bytes + manifest_path.stat().st_size,
    }


def _file_records(root: Path, *, excluded: set[str]) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        target = path.relative_to(root).as_posix()
        if target in excluded:
            continue
        records.append(
            {
                "byte_size": path.stat().st_size,
                "sha256": file_sha256(path),
                "target": _target(target),
            }
        )
    return records


def _verify_static_site(site_root: Path) -> None:
    required = ("index.html", "participants/index.html", "session-fallback.html")
    for relative in required:
        if not (site_root / relative).is_file():
            raise CivError(f"static participant export is missing {relative}")
    text = "\n".join(
        path.read_text(encoding="utf-8", errors="ignore")
        for path in site_root.rglob("*")
        if path.is_file() and path.suffix in {".html", ".js", ".json"}
    ).lower()
    for term in (*FORBIDDEN_PUBLIC_TERMS, "jury-pack-internal", "live_coach_token", "/organizers"):
        if term in text:
            raise CivError(f"static participant export contains forbidden term '{term}'")


def _verify_participant_assembly(
    root: Path, records: Sequence[Mapping[str, object]]
) -> None:
    for record in records:
        target = _target(str(record["target"]))
        if target.startswith(FORBIDDEN_ASSEMBLY_TARGET_PREFIXES):
            raise CivError(f"attendee kit contains private source target: {target}")
        if target.startswith("runtime/source/src/civ_workshop/") and Path(target).name in (
            PRIVATE_RUNTIME_MODULES
        ):
            raise CivError(f"attendee kit contains private runtime module: {target}")
        path = contained_archive_path(root, target, "assembly target")
        if path.suffix.casefold() not in PARTICIPANT_TEXT_SUFFIXES:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        folded = text.casefold()
        for term in FORBIDDEN_ASSEMBLY_TEXT:
            if term.casefold() in folded:
                raise CivError(
                    f"attendee kit text contains private operation '{term}': {target}"
                )
        if ABSOLUTE_PATH_PATTERN.search(text):
            raise CivError(f"attendee kit text contains an absolute host path: {target}")


def _copy_participant_runtime(repository: Path, target: Path) -> None:
    _copy_file(repository / "kit" / "participant-pyproject.toml", target / "pyproject.toml")
    _copy_file(repository / "uv.lock", target / "uv.lock")
    package_source = repository / "src" / "civ_workshop"
    package_target = target / "src" / "civ_workshop"
    for name in PARTICIPANT_RUNTIME_MODULES:
        _copy_file(package_source / name, package_target / name)
    package_target.mkdir(parents=True, exist_ok=True)
    (package_target / "__init__.py").write_text(
        '"""Offline participant tooling for the CIV 2026 data hackathon."""\n',
        encoding="utf-8",
        newline="\n",
    )
    (package_target / "__main__.py").write_text(
        "from civ_workshop.participant_cli import main\n\nmain()\n",
        encoding="utf-8",
        newline="\n",
    )


def _context_inputs(
    inventory: Mapping[str, object], context_root: Path | None
) -> list[tuple[Path, str, str]]:
    raw_packs = inventory.get("context_packs", [])
    if not isinstance(raw_packs, list):
        raise CivError("assembly inventory context packs must be a list")
    if not raw_packs:
        if context_root is not None:
            raise CivError("assembly received an unused camera-context root")
        return []
    if context_root is None or len(raw_packs) != 1:
        raise CivError("assembly requires the one explicit camera-context root")
    pack = raw_packs[0]
    if not isinstance(pack, dict):
        raise CivError("assembly camera-context pack must be a mapping")
    set_target = _target(str(pack.get("manifest")))
    set_source = context_root / Path(set_target).name
    if file_sha256(set_source) != pack.get("manifest_sha256"):
        raise CivError("assembly camera-context set does not match inventory")
    context_set = read_json_file(set_source, "camera-context product set")
    if context_set.get("contract") != "civ.camera-context-set/v1":
        raise CivError("assembly camera-context set has the wrong contract")
    approval = context_set.get("approval")
    pack_approval = pack.get("approval")
    if (
        not isinstance(approval, dict)
        or not isinstance(pack_approval, dict)
        or approval.get("id") != pack_approval.get("id")
        or approval.get("document_sha256") != pack_approval.get("sha256")
    ):
        raise CivError("assembly camera-context approval does not match inventory")
    raw_product_set = inventory.get("product_set")
    if not isinstance(raw_product_set, dict):
        raise CivError("assembly participant product set must be a mapping")
    raw_signals = raw_product_set.get("products")
    if not isinstance(raw_signals, list):
        raise CivError("assembly participant products must be a list")
    signals: dict[str, tuple[str, str]] = {}
    for raw in raw_signals:
        if not isinstance(raw, dict):
            raise CivError("assembly participant product must be a mapping")
        signals[str(raw.get("source_id"))] = (
            Path(str(raw.get("name"))).name,
            str(raw.get("sha256")),
        )
    raw_products = context_set.get("products")
    if not isinstance(raw_products, list) or len(raw_products) != 13:
        raise CivError("assembly camera-context set must contain exactly 13 products")
    inputs: list[tuple[Path, str, str]] = [(set_source, set_target, str(pack["manifest_sha256"]))]
    observed_bytes = set_source.stat().st_size
    seen: set[str] = set()
    for raw in raw_products:
        if not isinstance(raw, dict):
            raise CivError("assembly camera-context product must be a mapping")
        source_id = str(raw.get("source_id"))
        if source_id in seen or signals.get(source_id) != (
            raw.get("signal_product"),
            raw.get("signal_sha256"),
        ):
            raise CivError("assembly camera-context signal binding is invalid")
        seen.add(source_id)
        dataset = str(raw.get("dataset"))
        if dataset not in {"kashiwa", "reims"}:
            raise CivError("assembly camera-context dataset is invalid")
        for name_field, hash_field, byte_field in (
            (
            "camera_context_product",
            "camera_context_sha256",
            "camera_context_bytes",
        ),
            ("manifest", "manifest_sha256", "manifest_bytes"),
        ):
            name = str(raw.get(name_field))
            if Path(name).name != name:
                raise CivError("assembly camera-context name is not a basename")
            target_name = _target(f"context/{dataset}/{name}")
            source = context_root / "participant" / dataset / name
            digest = str(raw.get(hash_field))
            expected_bytes = raw.get(byte_field)
            if (
                not source.is_file()
                or source.stat().st_size != expected_bytes
                or file_sha256(source) != digest
            ):
                raise CivError(f"assembly camera-context input does not match: {name}")
            observed_bytes += source.stat().st_size
            inputs.append((source, target_name, digest))
    if seen != set(signals) or observed_bytes != pack.get("required_disk_bytes"):
        raise CivError("assembly camera-context membership or byte total is invalid")
    return inputs


def assemble_kit(
    inventory_path: Path,
    repository: Path,
    data_root: Path,
    viewer_paths: Sequence[Path],
    site_root: Path,
    fallback_root: Path,
    cache_root: Path,
    container_archive: Path,
    output: Path,
    context_root: Path | None = None,
    presentations_root: Path | None = None,
) -> dict[str, object]:
    audit_kit_inventory(inventory_path)
    inventory = read_json_file(inventory_path, "participant kit inventory")
    if inventory.get("contract") != INVENTORY_CONTRACT:
        raise CivError("assembly requires the participant-kit inventory")
    if output.exists():
        raise CivError("assembly output must not already exist")
    presentation_files: tuple[Path, ...] = ()
    if presentations_root is not None:
        try:
            presentation_files = verified_presentations(presentations_root)
        except (OSError, ValueError, KeyError, StopIteration) as error:
            raise CivError(f"presentation input validation failed: {error}") from error
    _verify_static_site(site_root)
    fallback_manifest = read_json_file(
        fallback_root / "fallback-manifest.json", "fallback manifest"
    )
    if fallback_manifest.get("product_set_sha256") != ACCEPTED_PRODUCT_SET_SHA256:
        raise CivError("fallback pack does not match the accepted product set")
    viewer_by_name = {path.name: path for path in viewer_paths}
    context_copies = [
        (source, contained_archive_path(output, target, "assembly target"), digest)
        for source, target, digest in _context_inputs(inventory, context_root)
    ]
    tree_inputs = [
        entry
        for source, prefix in (
            (site_root, "site"),
            (fallback_root, "fallback"),
            (cache_root, "offline/uv-cache"),
            (
                repository / "src" / "civ_workshop" / "_templates" / "submission",
                "runtime/source/src/civ_workshop/_templates/submission",
            ),
        )
        for entry in _tree_inputs(source, output, prefix)
    ]
    output.mkdir(parents=True)
    product_set = inventory["product_set"]
    assert isinstance(product_set, dict)
    for product in product_set["products"]:
        assert isinstance(product, dict)
        for source_name, target_name, digest in (
            (Path(str(product["name"])).name, str(product["name"]), str(product["sha256"])),
            (
                Path(str(product["manifest"])).name,
                str(product["manifest"]),
                str(product["manifest_sha256"]),
            ),
        ):
            source = data_root / source_name
            if file_sha256(source) != digest:
                raise CivError(f"assembly data input does not match inventory: {source_name}")
            _copy_file(source, contained_archive_path(output, target_name, "assembly target"))
    set_source = data_root / Path(str(product_set["manifest"])).name
    if file_sha256(set_source) != product_set["sha256"]:
        raise CivError("assembly product-set manifest does not match inventory")
    _copy_file(
        set_source, contained_archive_path(output, str(product_set["manifest"]), "assembly target")
    )
    for context_source, context_target, context_digest in context_copies:
        if file_sha256(context_source) != context_digest:
            raise CivError(f"assembly camera-context changed during copy: {context_source.name}")
        _copy_file(context_source, context_target)
    for asset in inventory["tracked_assets"]:
        assert isinstance(asset, dict)
        target_name = str(asset["path"])
        source_name = TRACKED_ASSET_SOURCES.get(target_name, target_name)
        source = repository / source_name
        if file_sha256(source) != asset["sha256"]:
            raise CivError(f"tracked assembly asset changed after inventory: {target_name}")
        _copy_file(source, contained_archive_path(output, target_name, "assembly target"))
    for viewer in inventory["viewers"]:
        assert isinstance(viewer, dict)
        viewer_source = viewer_by_name.get(str(viewer["name"]))
        if viewer_source is None or file_sha256(viewer_source) != viewer["sha256"]:
            raise CivError(f"assembly viewer input does not match inventory: {viewer['name']}")
        _copy_file(
            viewer_source, contained_archive_path(output, str(viewer["target"]), "assembly target")
        )
    _copy_file(inventory_path, output / "participant-kit.json")
    _copy_file(
        inventory_path.parent / "checksums" / "SHA256SUMS",
        output / "checksums" / "SHA256SUMS",
    )
    for tree_source, tree_target in tree_inputs:
        _copy_file(tree_source, tree_target)
    _copy_file(
        container_archive,
        output / "container" / "civ-phase4-attendee-candidate-558e85c.tar",
    )
    _copy_participant_runtime(repository, output / "runtime" / "source")
    if presentation_files:
        target = output / "presentations"
        target.mkdir()
        for presentation in presentation_files:
            _copy_file(presentation, target / presentation.name)
        (target / "README.md").write_text(
            "# Workshop presentations\n\n"
            "- [Briefing](briefing.pptx)\n"
            "- [Submission checklist](submission-checklist.pptx)\n\n"
            "These are the reviewed decks supplied for this kit. "
            "Use the session brief for intake and deadline instructions.\n",
            encoding="utf-8",
        )
        brief = output / "site" / "desk" / "brief.html"
        if brief.is_file():
            links = (
                '<p class="presentation-links">Workshop presentations: '
                '<a href="../../presentations/briefing.pptx">Briefing</a> · '
                '<a href="../../presentations/submission-checklist.pptx">Submission checklist</a>'
                "</p>"
            )
            text = brief.read_text(encoding="utf-8")
            if "</body>" not in text:
                raise CivError("assembled brief has no body insertion point")
            brief.write_text(text.replace("</body>", links + "</body>"), encoding="utf-8")
    records = _file_records(
        output, excluded={"attendee-kit-assembly.json", "checksums/ASSEMBLY-SHA256SUMS"}
    )
    _verify_participant_assembly(output, records)
    components: dict[str, int] = {}
    for record in records:
        component = str(record["target"]).split("/", 1)[0]
        components[component] = components.get(component, 0) + _byte_size(record, "assembly file")
    manifest = {
        "components": [
            {"name": name, "required_disk_bytes": components[name]} for name in sorted(components)
        ],
        "contract": ASSEMBLY_CONTRACT,
        "disk_budget": {
            "drive_count": 4,
            "per_drive_bytes": TWO_TIB,
            "fleet_bytes": FOUR_SSD_BUDGET,
        },
        "files": records,
        "inventory_sha256": file_sha256(inventory_path),
        "release_id": (
            "civ-2026-phase5-camera-context-attendee-kit-v2"
            if inventory.get("release_id") == PHASE5_RELEASE
            else "civ-2026-phase4-attendee-kit-v1"
        ),
        "required_disk_bytes": sum(components.values()),
    }
    manifest_path = output / "attendee-kit-assembly.json"
    manifest_path.write_text(f"{canonical_json(manifest)}\n", encoding="utf-8", newline="\n")
    all_records = _file_records(output, excluded={"checksums/ASSEMBLY-SHA256SUMS"})
    checksum = "".join(f"{item['sha256']}  {item['target']}\n" for item in all_records)
    checksum_path = output / "checksums" / "ASSEMBLY-SHA256SUMS"
    checksum_path.parent.mkdir(parents=True, exist_ok=True)
    checksum_path.write_text(checksum, encoding="utf-8", newline="\n")
    return audit_assembly(manifest_path)


def audit_assembly(manifest_path: Path) -> dict[str, object]:
    document = read_json_file(manifest_path, "attendee kit assembly")
    if set(document) != ASSEMBLY_FIELDS or document.get("contract") != ASSEMBLY_CONTRACT:
        raise CivError("attendee kit assembly has unknown or missing fields")
    root = manifest_path.parent
    files = document.get("files")
    if not isinstance(files, list) or not files:
        raise CivError("attendee kit assembly files must be non-empty")
    seen: set[str] = set()
    total = 0
    for raw in files:
        if not isinstance(raw, dict) or set(raw) != {"target", "sha256", "byte_size"}:
            raise CivError("attendee kit assembly file has unknown or missing fields")
        target = _target(str(raw["target"]))
        if target in seen:
            raise CivError("attendee kit assembly contains duplicate targets")
        seen.add(target)
        path = contained_archive_path(root, target, "assembly target")
        if (
            not path.is_file()
            or path.stat().st_size != raw["byte_size"]
            or file_sha256(path) != raw["sha256"]
        ):
            raise CivError(f"attendee kit assembly file does not match: {target}")
        total += _byte_size(raw, "attendee kit assembly file")
    if total != document.get("required_disk_bytes"):
        raise CivError("attendee kit assembly byte total does not match")
    if total > TWO_TIB:
        raise CivError("attendee kit does not fit one carried SSD")
    _verify_participant_assembly(root, files)
    checksum_path = root / "checksums" / "ASSEMBLY-SHA256SUMS"
    expected_records = _file_records(root, excluded={"checksums/ASSEMBLY-SHA256SUMS"})
    expected = "".join(f"{item['sha256']}  {item['target']}\n" for item in expected_records)
    if checksum_path.read_text(encoding="utf-8") != expected:
        raise CivError("attendee kit assembly checksum manifest is not canonical or complete")
    return {
        "file_count": len(files),
        "manifest_sha256": file_sha256(manifest_path),
        "required_disk_bytes": total,
        "valid": True,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build the deterministic offline attendee kit")
    commands = parser.add_subparsers(dest="command", required=True)
    fallback = commands.add_parser("fallback")
    fallback.add_argument("product_set", type=Path)
    fallback.add_argument("--data-root", type=Path, required=True)
    fallback.add_argument("--output", type=Path, required=True)
    assemble = commands.add_parser("assemble")
    assemble.add_argument("inventory", type=Path)
    assemble.add_argument("--repository", type=Path, required=True)
    assemble.add_argument("--data-root", type=Path, required=True)
    assemble.add_argument("--viewer", action="append", default=[], type=Path)
    assemble.add_argument("--site-root", type=Path, required=True)
    assemble.add_argument("--fallback-root", type=Path, required=True)
    assemble.add_argument("--cache-root", type=Path, required=True)
    assemble.add_argument("--container-archive", type=Path, required=True)
    assemble.add_argument("--context-root", type=Path)
    assemble.add_argument("--presentations-root", type=Path)
    assemble.add_argument("--output", type=Path, required=True)
    audit = commands.add_parser("audit")
    audit.add_argument("manifest", type=Path)
    return parser


def main(argv: Sequence[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "fallback":
            result = build_fallback_pack(args.product_set, args.data_root, args.output)
        elif args.command == "assemble":
            result = assemble_kit(
                args.inventory,
                args.repository,
                args.data_root,
                args.viewer,
                args.site_root,
                args.fallback_root,
                args.cache_root,
                args.container_archive,
                args.output,
                args.context_root,
                args.presentations_root,
            )
        else:
            result = audit_assembly(args.manifest)
        print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    except CivError as error:
        print(f"kit-assembly: {error}", file=sys.stderr)
        raise SystemExit(2) from None


if __name__ == "__main__":
    main()
