from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import zipfile
from pathlib import Path
from typing import Literal, TypedDict

import pytest
from mcap.writer import CompressionType, Writer

import civ_workshop.kit_assembly as assembly_module
from civ_workshop.artifacts import canonical_json, file_sha256
from civ_workshop.errors import CivError
from civ_workshop.kit_assembly import assemble_kit, audit_assembly, build_fallback_pack
from civ_workshop.kit_inventory import (
    ACCEPTED_PRODUCT_SET_SHA256,
    TRACKED_ASSET_SOURCES,
    TRACKED_ASSETS,
)
from civ_workshop.participant_cli import build_parser as build_participant_parser
from tests.helpers import create_micro_case
from tests.test_participant_runtime import participant_workflow

REPOSITORY = Path(__file__).parents[1]


class _OptionalAssemblyInputs(TypedDict, total=False):
    context_root: Path | None


class _AssemblyInputs(_OptionalAssemblyInputs):
    inventory_path: Path
    repository: Path
    data_root: Path
    viewer_paths: list[Path]
    site_root: Path
    fallback_root: Path
    cache_root: Path
    container_archive: Path
    output: Path


class _SignalProductSet(TypedDict):
    products: list[dict[str, object]]


class _CameraContextInventory(TypedDict):
    context_packs: list[dict[str, object]]
    product_set: _SignalProductSet


def test_participant_runtime_exposes_only_the_public_command_path() -> None:
    help_text = build_participant_parser().format_help()

    for command in (
        "clip",
        "detect",
        "doctor",
        "inspect",
        "report",
        "sample",
        "score",
        "submission-init",
    ):
        assert command in help_text
    for private_command in ("intake-form", "intake-local", "intake-tally", "score-batch"):
        assert private_command not in help_text


def _write_json_bag(path: Path, dataset: str) -> None:
    signals = assembly_module.FALLBACK_SIGNALS[dataset]
    fields_by_topic: dict[str, list[str]] = {}
    for topic, field in signals:
        fields_by_topic.setdefault(topic, []).append(field)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as stream:
        writer = Writer(stream, compression=CompressionType.NONE)
        writer.start(profile="test", library="kit-assembly-test")
        for topic, fields in fields_by_topic.items():
            properties: dict[str, object] = {}
            payload: dict[str, object] = {}
            for field in fields:
                schema_cursor = properties
                payload_cursor = payload
                parts = field.split(".")
                for part in parts[:-1]:
                    node = schema_cursor.setdefault(part, {"type": "object", "properties": {}})
                    assert isinstance(node, dict)
                    child = node["properties"]
                    assert isinstance(child, dict)
                    schema_cursor = child
                    payload_node = payload_cursor.setdefault(part, {})
                    assert isinstance(payload_node, dict)
                    payload_cursor = payload_node
                schema_cursor[parts[-1]] = {"type": "number"}
                payload_cursor[parts[-1]] = 1.25
            schema = json.dumps({"type": "object", "properties": properties}).encode()
            schema_id = writer.register_schema(
                name=f"{dataset}/{topic}", encoding="jsonschema", data=schema
            )
            channel_id = writer.register_channel(
                schema_id=schema_id, topic=topic, message_encoding="json"
            )
            for index in range(20):
                writer.add_message(
                    channel_id=channel_id,
                    log_time=index * 100_000_000,
                    publish_time=index * 100_000_000,
                    data=json.dumps(payload).encode(),
                )
        writer.finish()


def _fallback_fixture(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> tuple[Path, Path]:
    data_root = tmp_path / "data"
    products = []
    for index in range(13):
        dataset = "kashiwa" if index < 8 else "reims"
        name = f"{dataset}-{index}.mcap"
        path = data_root / name
        _write_json_bag(path, dataset)
        products.append({"dataset": dataset, "name": name, "sha256": file_sha256(path)})
    set_path = data_root / "participant-products.json"
    set_path.write_text(
        f"{canonical_json({'contract': 'civ.data-product-set/v1', 'products': products})}\n",
        encoding="utf-8",
    )
    real_sha = file_sha256

    def accepted_set(path: Path) -> str:
        return ACCEPTED_PRODUCT_SET_SHA256 if path == set_path else real_sha(path)

    monkeypatch.setattr(assembly_module, "file_sha256", accepted_set)
    return set_path, data_root


def test_fallback_pack_is_deterministic_and_covers_both_stacks(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    set_path, data_root = _fallback_fixture(tmp_path, monkeypatch)
    first = tmp_path / "fallback-first"
    second = tmp_path / "fallback-second"

    first_result = build_fallback_pack(set_path, data_root, first)
    second_result = build_fallback_pack(set_path, data_root, second)

    assert first_result == second_result
    assert (first / "fallback-manifest.json").read_bytes() == (
        second / "fallback-manifest.json"
    ).read_bytes()
    manifest = json.loads((first / "fallback-manifest.json").read_text(encoding="utf-8"))
    assert [item["dataset"] for item in manifest["datasets"]] == ["kashiwa", "reims"]
    assert all(item["neutral_clip_count"] == 3 for item in manifest["datasets"])
    assert len(list((first / "kashiwa" / "tables").glob("*.csv"))) == 8
    assert len(list((first / "reims" / "tables").glob("*.csv"))) == 5
    assert "not an answer interval" in (
        first / "kashiwa" / "plots" / "signal-overview.svg"
    ).read_text(encoding="utf-8")


def test_fallback_refuses_changed_product(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    set_path, data_root = _fallback_fixture(tmp_path, monkeypatch)
    (data_root / "kashiwa-0.mcap").write_bytes(b"changed")

    with pytest.raises(CivError, match="does not match participant product"):
        build_fallback_pack(set_path, data_root, tmp_path / "fallback")


@pytest.fixture
def assembly_inputs(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> _AssemblyInputs:
    data_root = tmp_path / "data"
    data_root.mkdir()
    product = data_root / "route.mcap"
    manifest = data_root / "route.mcap.manifest.json"
    product.write_bytes(b"product")
    manifest.write_text("{}\n", encoding="utf-8")
    product_set = data_root / "participant-products.json"
    product_set.write_text("{}\n", encoding="utf-8")
    viewer = tmp_path / "viewer.exe"
    viewer.write_bytes(b"viewer")
    inventory = tmp_path / "participant-kit.json"
    inventory_document = {
        "contract": "civ.participant-kit-inventory/v1",
        "product_set": {
            "manifest": "data/participant-products.json",
            "sha256": file_sha256(product_set),
            "products": [
                {
                    "name": "data/route.mcap",
                    "sha256": file_sha256(product),
                    "manifest": "data/route.mcap.manifest.json",
                    "manifest_sha256": file_sha256(manifest),
                }
            ],
        },
        "tracked_assets": [],
        "viewers": [
            {
                "name": viewer.name,
                "target": "viewer/windows/viewer.exe",
                "sha256": file_sha256(viewer),
            }
        ],
    }
    inventory.write_text(f"{canonical_json(inventory_document)}\n", encoding="utf-8")
    (tmp_path / "checksums").mkdir()
    (tmp_path / "checksums" / "SHA256SUMS").write_text(
        "synthetic inventory checksum fixture\n", encoding="utf-8"
    )
    site = tmp_path / "site"
    (site / "participants").mkdir(parents=True)
    for relative in ("index.html", "participants/index.html", "session-fallback.html"):
        (site / relative).write_text("<html>participant</html>\n", encoding="utf-8")
    fallback = tmp_path / "fallback"
    fallback.mkdir()
    (fallback / "fallback-manifest.json").write_text(
        f"{canonical_json({'product_set_sha256': ACCEPTED_PRODUCT_SET_SHA256})}\n",
        encoding="utf-8",
    )
    cache = tmp_path / "cache"
    cache.mkdir()
    (cache / "blob").write_bytes(b"dependency")
    (cache / ".lock").write_bytes(b"")
    container = tmp_path / "container.tar"
    container.write_bytes(b"container")
    monkeypatch.setattr(assembly_module, "audit_kit_inventory", lambda _: {"valid": True})

    return {
        "inventory_path": inventory,
        "repository": REPOSITORY,
        "data_root": data_root,
        "viewer_paths": [viewer],
        "site_root": site,
        "fallback_root": fallback,
        "cache_root": cache,
        "container_archive": container,
        "output": tmp_path / "assembled",
    }


@pytest.mark.skipif(os.name == "nt", reason="requires a POSIX filename invalid on Windows")
@pytest.mark.parametrize("tree", ["site_root", "fallback_root", "cache_root", "templates"])
def test_assembly_rejects_invalid_later_tree_entry_before_output(
    tmp_path: Path,
    assembly_inputs: _AssemblyInputs,
    tree: Literal["site_root", "fallback_root", "cache_root", "templates"],
) -> None:
    if tree == "templates":
        repository = tmp_path / "repository"
        assembly_inputs["repository"] = repository
        source = repository / "src" / "civ_workshop" / "_templates" / "submission"
        source.mkdir(parents=True)
    else:
        source = assembly_inputs[tree]
    output = assembly_inputs["output"]
    assert isinstance(source, Path)
    assert isinstance(output, Path)
    (source / "aaa-valid.txt").write_bytes(b"valid earlier entry")
    (source / "zzz-invalid.txt:stream").write_bytes(b"invalid later entry")

    with pytest.raises(CivError, match="assembly target.*archive-relative POSIX path"):
        assemble_kit(**assembly_inputs)

    assert not output.exists()


def test_assembly_copies_closed_inputs_and_detects_changes(
    tmp_path: Path, assembly_inputs: _AssemblyInputs
) -> None:
    result = assemble_kit(**assembly_inputs)

    assert result["valid"] is True
    assert audit_assembly(tmp_path / "assembled" / "attendee-kit-assembly.json") == result
    assert (tmp_path / "assembled" / "site" / "participants" / "index.html").is_file()
    assert (tmp_path / "assembled" / "offline" / "uv-cache" / ".lock").stat().st_size == 0
    assert not (tmp_path / "assembled" / "tool").exists()
    runtime_source = tmp_path / "assembled" / "runtime" / "source"
    runtime = runtime_source / "src" / "civ_workshop"
    assert (runtime / "participant_cli.py").is_file()
    assert (runtime / "score_reference.py").is_file()
    assert not any((runtime / name).exists() for name in assembly_module.PRIVATE_RUNTIME_MODULES)
    help_result = subprocess.run(
        [
            sys.executable,
            "-I",
            "-c",
            (
                "import sys; "
                "sys.path.insert(0, 'src'); "
                "from civ_workshop.participant_cli import main; "
                "main(['--help'])"
            ),
        ],
        cwd=runtime_source,
        capture_output=True,
        text=True,
        check=False,
    )
    assert help_result.returncode == 0, help_result.stderr
    assert "usage:" in help_result.stdout
    case = create_micro_case(tmp_path / "synthetic-workflow")

    def invoke(arguments: list[str]) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "-I", "-c",
             "import sys; sys.path.insert(0, sys.argv.pop(1)); "
             "from civ_workshop.participant_cli import main; main(sys.argv[1:])",
             str(runtime_source / "src"), *arguments],
            cwd=case.root, capture_output=True, text=True, check=False,
        )

    participant_workflow(case, case.root / "submission", invoke)
    (tmp_path / "assembled" / "data" / "route.mcap").write_bytes(b"tampered")
    with pytest.raises(CivError, match="does not match"):
        audit_assembly(tmp_path / "assembled" / "attendee-kit-assembly.json")


def test_static_export_leakage_gate_rejects_private_route(tmp_path: Path) -> None:
    site = tmp_path / "site"
    (site / "participants").mkdir(parents=True)
    (site / "index.html").write_text("/organizers", encoding="utf-8")
    (site / "participants" / "index.html").write_text("participant", encoding="utf-8")
    (site / "session-fallback.html").write_text("fallback", encoding="utf-8")

    with pytest.raises(CivError, match="forbidden term"):
        assembly_module._verify_static_site(site)


def _camera_context_fixture(
    tmp_path: Path, invalid_field: str | None = None, signal: dict[str, object] | None = None
) -> tuple[Path, _CameraContextInventory]:
    context_root = tmp_path / "context-source"
    products: list[dict[str, object]] = []
    signals: list[dict[str, object]] = []
    payload_bytes = 0
    for index in range(13):
        dataset = "kashiwa" if index < 8 else "reims"
        source_id = f"source-{index}"
        signal_name = f"{source_id}-signals.mcap"
        signal_sha256 = f"{index + 1:064x}"
        if signal is None:
            signals.append(
                {
                    "name": f"data/{signal_name}",
                    "sha256": signal_sha256,
                    "source_id": source_id,
                }
            )
        else:
            signal_name = Path(str(signal["name"])).name
            signal_sha256 = str(signal["sha256"])
            signals.append(dict(signal, source_id=source_id))
        product_name = f"{source_id}-camera-context.mcap"
        manifest_name = f"{product_name}.manifest.json"
        if index == 12:
            if invalid_field == "camera_context_product":
                product_name = "bad.txt:stream"
            elif invalid_field == "manifest":
                manifest_name = "bad.txt:stream"
        directory = context_root / "participant" / dataset
        directory.mkdir(parents=True, exist_ok=True)
        product_path = directory / product_name
        manifest_path = directory / manifest_name
        product_path.write_bytes(f"camera-{index}".encode())
        manifest_path.write_text("{}\n", encoding="utf-8")
        payload_bytes += product_path.stat().st_size + manifest_path.stat().st_size
        products.append(
            {
                "camera_context_bytes": product_path.stat().st_size,
                "camera_context_product": product_name,
                "camera_context_sha256": file_sha256(product_path),
                "dataset": dataset,
                "manifest": manifest_name,
                "manifest_bytes": manifest_path.stat().st_size,
                "manifest_sha256": file_sha256(manifest_path),
                "signal_product": signal_name,
                "signal_sha256": signal_sha256,
                "source_id": source_id,
            }
        )
    set_path = context_root / "camera-context-products.json"
    context_set: dict[str, object] = {
        "approval": {"id": "approval", "document_sha256": "a" * 64},
        "contract": "civ.camera-context-set/v1",
        "products": products,
        "required_disk_bytes": 0,
    }
    while True:
        serialized = f"{canonical_json(context_set)}\n"
        required = payload_bytes + len(serialized.encode())
        if context_set["required_disk_bytes"] == required:
            break
        context_set["required_disk_bytes"] = required
    set_path.write_text(serialized, encoding="utf-8", newline="\n")
    inventory: _CameraContextInventory = {
        "context_packs": [
            {
                "approval": {"id": "approval", "sha256": "a" * 64},
                "manifest": "context/camera-context-products.json",
                "manifest_sha256": file_sha256(set_path),
                "required_disk_bytes": required,
            }
        ],
        "product_set": {"products": signals},
    }

    return context_root, inventory


def test_camera_context_inputs_require_exact_signal_bindings(tmp_path: Path) -> None:
    context_root, inventory = _camera_context_fixture(tmp_path)
    products = inventory["product_set"]["products"]

    inputs = assembly_module._context_inputs(inventory, context_root)

    assert len(inputs) == 27
    assert inputs[0][1] == "context/camera-context-products.json"
    products[0]["sha256"] = "f" * 64
    with pytest.raises(CivError, match="signal binding"):
        assembly_module._context_inputs(inventory, context_root)


@pytest.mark.skipif(os.name == "nt", reason="requires a POSIX filename invalid on Windows")
@pytest.mark.parametrize("invalid_field", ["camera_context_product", "manifest"])
def test_assembly_rejects_invalid_later_context_entry_before_output(
    tmp_path: Path, assembly_inputs: _AssemblyInputs, invalid_field: str
) -> None:
    inventory_path = assembly_inputs["inventory_path"]
    output = assembly_inputs["output"]
    assert isinstance(inventory_path, Path)
    assert isinstance(output, Path)
    inventory = json.loads(inventory_path.read_text(encoding="utf-8"))
    signal = inventory["product_set"]["products"][0]
    context_root, context_inventory = _camera_context_fixture(tmp_path, invalid_field, signal)
    inventory["context_packs"] = context_inventory["context_packs"]
    inventory["product_set"]["products"] = context_inventory["product_set"]["products"]
    inventory_path.write_text(canonical_json(inventory), encoding="utf-8")
    assembly_inputs["context_root"] = context_root

    with pytest.raises(CivError, match="assembly target.*archive-relative POSIX path"):
        assemble_kit(**assembly_inputs)

    assert not output.exists()


@pytest.mark.parametrize(
    ("target", "content", "message"),
    [
        ("tool/source/src/civ_workshop/batch.py", "pass\n", "private source target"),
        (
            "runtime/source/src/civ_workshop/intake.py",
            "pass\n",
            "private runtime module",
        ),
        ("docs/private.md", "Run civ score-batch now.\n", "private operation"),
        ("docs/path.md", "D:\\private\\labels.json\n", "absolute host path"),
    ],
)
def test_assembly_leakage_gate_rejects_private_payload(
    tmp_path: Path, target: str, content: str, message: str
) -> None:
    path = tmp_path / target
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    records = assembly_module._file_records(tmp_path, excluded=set())

    with pytest.raises(CivError, match=message):
        assembly_module._verify_participant_assembly(tmp_path, records)


def test_assembly_preserves_guides_notices_and_local_links(
    tmp_path: Path, assembly_inputs: _AssemblyInputs
) -> None:
    targets = {target for _, target in TRACKED_ASSETS}
    notice_targets = {
        "THIRD-PARTY-NOTICES.md",
        "LICENSES/OpenAI-Sites-2023-MIT.txt",
        "LICENSES/ROS-Apache-2.0.txt",
        "LICENSES/CIV-MIT.txt",
        "LICENSES/MCAP-MIT.txt",
        "site/LICENSES/Geist-OFL-1.1.txt",
        "viewer/README.md",
        "viewer/NOTICES.md",
        "viewer/LICENSES/Lichtblick-MPL-2.0.txt",
        "viewer/LICENSES/PlotJuggler-MPL-2.0.txt",
        "container/NOTICES.md",
    }
    assert notice_targets <= targets
    attribution_targets = notice_targets - {"viewer/README.md"}
    assert {role for role, target in TRACKED_ASSETS if target in attribution_targets} == {
        "attribution"
    }
    inventory_path = assembly_inputs["inventory_path"]
    inventory = json.loads(inventory_path.read_text("utf-8"))
    inventory["tracked_assets"] = [
        {
            "path": target,
            "sha256": file_sha256(REPOSITORY / TRACKED_ASSET_SOURCES.get(target, target)),
        }
        for target in sorted(targets)
    ]
    inventory_path.write_text(canonical_json(inventory) + "\n", encoding="utf-8")
    assemble_kit(**assembly_inputs)
    output = assembly_inputs["output"]
    index = (output / "THIRD-PARTY-NOTICES.md").read_text("utf-8")
    for target in attribution_targets - {"THIRD-PARTY-NOTICES.md"}:
        assert f"`{target}`" in index or target in index
        assert (output / target).is_file()
    assembly_manifest = json.loads((output / "attendee-kit-assembly.json").read_text("utf-8"))
    recorded_hashes = {record["target"]: record["sha256"] for record in assembly_manifest["files"]}
    assembly_checksums = (output / "checksums/ASSEMBLY-SHA256SUMS").read_text("utf-8")
    for target in attribution_targets:
        digest = file_sha256(output / target)
        assert recorded_hashes[target] == digest
        assert f"{digest}  {target}" in assembly_checksums
    for target in targets:
        source = REPOSITORY / TRACKED_ASSET_SOURCES.get(target, target)
        copied = output / target
        assert copied.read_bytes() == source.read_bytes()
        for destination in re.findall(r"\]\(([^)]+)\)", copied.read_text("utf-8")):
            if "://" in destination or destination.startswith("#"):
                continue
            assert (copied.parent / destination.split("#", 1)[0]).exists(), destination
    (output / "LICENSES/MCAP-MIT.txt").write_text("changed after assembly\n", encoding="utf-8")
    with pytest.raises(CivError, match="does not match"):
        audit_assembly(output / "attendee-kit-assembly.json")


def test_optional_presentations_are_copied_hashed_and_linked(
    tmp_path: Path, assembly_inputs: _AssemblyInputs
) -> None:
    from tests.test_presentation_files import _write_fixture

    root = tmp_path / "reviewed-presentations"
    briefing, checklist = _write_fixture(root)
    site_root = assembly_inputs["site_root"]
    brief = site_root / "desk" / "brief.html"
    brief.parent.mkdir()
    brief.write_text("<html><body><h1>Session brief</h1></body></html>", encoding="utf-8")
    assemble_kit(**assembly_inputs, presentations_root=root)
    output = assembly_inputs["output"]
    assert file_sha256(output / "presentations/briefing.pptx") == file_sha256(briefing)
    assert file_sha256(output / "presentations/submission-checklist.pptx") == file_sha256(checklist)
    assert "../../presentations/briefing.pptx" in (output / "site/desk/brief.html").read_text()
    assert "presentation-links" not in brief.read_text()
    result = audit_assembly(output / "attendee-kit-assembly.json")
    assert result["valid"] is True
    (output / "presentations/briefing.pptx").write_bytes(b"changed")
    with pytest.raises(CivError, match="hash|match"):
        audit_assembly(output / "attendee-kit-assembly.json")


def test_invalid_optional_presentations_fail_before_assembly_output(
    tmp_path: Path, assembly_inputs: _AssemblyInputs
) -> None:
    from tests.test_presentation_files import _write_fixture

    root = tmp_path / "invalid-presentations"
    _write_fixture(root, widescreen=False)
    with pytest.raises(CivError, match="presentation input validation failed"):
        assemble_kit(**assembly_inputs, presentations_root=root)
    assert not assembly_inputs["output"].exists()


def _released_pack(assembly_inputs: _AssemblyInputs, path: Path) -> Path:
    inventory = json.loads(assembly_inputs["inventory_path"].read_text())
    product = inventory["product_set"]["products"][0]
    path.write_text(
        canonical_json(
            {
                "contract": "civ.label-pack/v1alpha1",
                "dataset": "fixture",
                "source_sha256": product["sha256"],
                "labels": [],
                "data_gaps": [],
            }
        )
    )
    return path


def test_session_materials_are_exact_audited_copies(
    tmp_path: Path, assembly_inputs: _AssemblyInputs
) -> None:
    pack = _released_pack(assembly_inputs, tmp_path / "practice.json")
    brief = tmp_path / "brief.md"
    brief.write_text("# Session\n[Practice](practice-labels/practice.json)\n")
    originals = {p: p.read_bytes() for p in (pack, brief)}
    result = assemble_kit(**assembly_inputs, practice_packs=[pack], session_brief=brief)
    output = assembly_inputs["output"]
    assert result["valid"] is True
    for source, target in ((pack, "practice-labels/practice.json"), (brief, "SESSION-BRIEF.md")):
        assert (output / target).read_bytes() == originals[source]
        assert source.read_bytes() == originals[source]
    assert "SESSION-BRIEF.md" in (output / "SESSION-MATERIALS.md").read_text()
    (output / "practice-labels/practice.json").write_text("changed")
    with pytest.raises(CivError, match="does not match"):
        audit_assembly(output / "attendee-kit-assembly.json")


def test_session_pack_must_match_a_participant_product_before_output(
    tmp_path: Path, assembly_inputs: _AssemblyInputs
) -> None:
    pack = _released_pack(assembly_inputs, tmp_path / "practice.json")
    document = json.loads(pack.read_text())
    document["source_sha256"] = "0" * 64
    pack.write_text(canonical_json(document))
    with pytest.raises(CivError, match="does not match a participant product"):
        assemble_kit(**assembly_inputs, practice_packs=[pack])
    assert not assembly_inputs["output"].exists()


@pytest.mark.parametrize("text", ["[Missing](missing.md)", "private /organizers route"])
def test_session_brief_cannot_bypass_navigation_or_privacy_checks(
    tmp_path: Path, assembly_inputs: _AssemblyInputs, text: str
) -> None:
    brief = tmp_path / "brief.md"
    brief.write_text(text)
    with pytest.raises(CivError, match="missing from the kit|private operation"):
        assemble_kit(**assembly_inputs, session_brief=brief)


def test_session_inputs_are_exposed_by_cli() -> None:
    parser = assembly_module.build_parser()
    args = parser.parse_args(
        [
            "assemble",
            "inventory.json",
            "--repository",
            ".",
            "--data-root",
            "data",
            "--viewer",
            "viewer",
            "--site-root",
            "site",
            "--fallback-root",
            "fallback",
            "--cache-root",
            "cache",
            "--container-archive",
            "container.tar",
            "--output",
            "out",
            "--participant-wheel",
            "participant.whl",
            "--practice-pack",
            "one.json",
            "--practice-pack",
            "two.json",
            "--session-brief",
            "brief.md",
        ]
    )
    assert args.practice_pack == [Path("one.json"), Path("two.json")]
    assert args.participant_wheel == Path("participant.whl")


@pytest.mark.parametrize(
    "destination",
    [
        'guide.md "Setup"',
        "guide.md 'Setup'",
        "guide.md (Setup)",
        "<guide.md>",
        '<guide.md> "Setup"',
        "./guide.md",
        '././guide.md#setup "Setup"',
        '<./guide.md#setup> "Setup"',
    ],
)
def test_session_brief_accepts_markdown_destinations(tmp_path: Path, destination: str) -> None:
    output = tmp_path / "output"
    output.mkdir()
    (output / "guide.md").write_text("# Setup\n", encoding="utf-8")
    brief = tmp_path / "brief.md"
    brief.write_text(f"[Guide]({destination})\n", encoding="utf-8")
    original = brief.read_bytes()
    assembly_module._copy_session_inputs(output, [(brief, "SESSION-BRIEF.md")])
    assert (output / "SESSION-BRIEF.md").read_bytes() == original


@pytest.mark.parametrize(
    "destination",
    [
        'missing.md "Setup"',
        "<missing.md>",
        "./missing.md",
        '../outside.md "Setup"',
        "<./../outside.md>",
        "./../outside.md",
        'missing.md "https://example.com"',
    ],
)
def test_session_brief_rejects_missing_or_outside_destinations(
    tmp_path: Path, destination: str
) -> None:
    output = tmp_path / "output"
    output.mkdir()
    (tmp_path / "outside.md").write_text("Outside the kit\n", encoding="utf-8")
    brief = tmp_path / "brief.md"
    brief.write_text(f"[Guide]({destination})\n", encoding="utf-8")
    with pytest.raises(CivError, match="missing from the kit|contained archive-relative"):
        assembly_module._copy_session_inputs(output, [(brief, "SESSION-BRIEF.md")])


def test_session_brief_rejects_symlink_outside_kit(tmp_path: Path) -> None:
    output = tmp_path / "output"
    output.mkdir()
    outside = tmp_path / "outside.md"
    outside.write_text("Outside the kit\n", encoding="utf-8")
    try:
        (output / "guide.md").symlink_to(outside)
    except OSError as error:
        pytest.skip(f"symlinks unavailable: {error}")
    brief = tmp_path / "brief.md"
    brief.write_text('[Guide](<./guide.md> "Setup")\n', encoding="utf-8")
    with pytest.raises(CivError, match="resolves outside its intended root"):
        assembly_module._copy_session_inputs(output, [(brief, "SESSION-BRIEF.md")])


@pytest.mark.parametrize(
    "member",
    [
        "civ_workshop/_templates/submission/README.md",
        "civ_workshop/_templates/submission/detector.yaml",
        "civ_workshop-0.1.0.dist-info/METADATA",
        "civ_workshop-0.1.0.dist-info/WHEEL",
        "civ_workshop-0.1.0.dist-info/licenses/LICENSE.txt",
    ],
)
@pytest.mark.parametrize("text", ["private /organizers route", "CIV SCORE-BATCH", r"C:\private"])
def test_session_wheel_reuses_participant_text_privacy_rules(
    tmp_path: Path, assembly_inputs: _AssemblyInputs, member: str, text: str
) -> None:
    wheel = tmp_path / "participant.whl"
    with zipfile.ZipFile(wheel, "w") as archive:
        for name in (*assembly_module.PARTICIPANT_RUNTIME_MODULES, "__init__.py", "__main__.py"):
            archive.writestr(f"civ_workshop/{name}", "# Synthetic public module\n")
        archive.writestr(
            "civ_workshop-0.1.0.dist-info/entry_points.txt",
            "[console_scripts]\nciv = civ_workshop.participant_cli:main\n",
        )
        archive.writestr(member, text)
    original = wheel.read_bytes()
    with pytest.raises(CivError, match="private operation|absolute host path"):
        assemble_kit(**assembly_inputs, participant_wheel=wheel)
    assert not assembly_inputs["output"].exists()
    assert wheel.read_bytes() == original


def test_real_participant_wheel_is_supported_and_organizer_entrypoint_is_rejected(
    tmp_path: Path, assembly_inputs: _AssemblyInputs
) -> None:
    wheel_root = tmp_path / "dist"
    built = subprocess.run(
        ["uv", "build", str(REPOSITORY / "participant"), "--wheel", "--out-dir", str(wheel_root)],
        text=True,
        capture_output=True,
        check=False,
    )
    assert built.returncode == 0, built.stderr
    wheel = next(wheel_root.glob("*.whl"))
    original = wheel.read_bytes()
    result = assemble_kit(**assembly_inputs, participant_wheel=wheel)
    assert result["valid"] is True
    assert (
        assembly_inputs["output"] / "runtime/wheels" / wheel.name
    ).read_bytes() == original
    assert wheel.read_bytes() == original
    assert audit_assembly(assembly_inputs["output"] / "attendee-kit-assembly.json") == result
    rejected = tmp_path / "organizer.whl"
    with zipfile.ZipFile(wheel) as source, zipfile.ZipFile(rejected, "w") as target:
        for name in source.namelist():
            content = source.read(name)
            if name.endswith("entry_points.txt"):
                content = content.replace(
                    b"civ_workshop.participant_cli:main", b"civ_workshop.cli:main"
                )
            target.writestr(name, content)
    with pytest.raises(CivError, match="participant CLI"):
        assembly_module._session_inputs(
            json.loads(assembly_inputs["inventory_path"].read_text()), rejected, (), None
        )
