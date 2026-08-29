from __future__ import annotations

import json
from pathlib import Path

import pytest
from mcap.writer import CompressionType, Writer

import civ_workshop.kit_assembly as assembly_module
from civ_workshop.artifacts import canonical_json, file_sha256
from civ_workshop.errors import CivError
from civ_workshop.kit_assembly import assemble_kit, audit_assembly, build_fallback_pack
from civ_workshop.kit_inventory import ACCEPTED_PRODUCT_SET_SHA256
from civ_workshop.participant_cli import build_parser as build_participant_parser

REPOSITORY = Path(__file__).parents[1]


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


def test_assembly_copies_closed_inputs_and_detects_changes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
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

    result = assemble_kit(
        inventory,
        REPOSITORY,
        data_root,
        [viewer],
        site,
        fallback,
        cache,
        container,
        tmp_path / "assembled",
    )

    assert result["valid"] is True
    assert audit_assembly(tmp_path / "assembled" / "attendee-kit-assembly.json") == result
    assert (tmp_path / "assembled" / "site" / "participants" / "index.html").is_file()
    assert (tmp_path / "assembled" / "offline" / "uv-cache" / ".lock").stat().st_size == 0
    assert not (tmp_path / "assembled" / "tool").exists()
    runtime = tmp_path / "assembled" / "runtime" / "source" / "src" / "civ_workshop"
    assert (runtime / "participant_cli.py").is_file()
    assert (runtime / "score_reference.py").is_file()
    assert not any((runtime / name).exists() for name in assembly_module.PRIVATE_RUNTIME_MODULES)
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
