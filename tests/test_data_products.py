from __future__ import annotations

import json
from hashlib import sha256
from pathlib import Path
from typing import Any

import pytest
from mcap.reader import make_reader

from civ_workshop.data_products import (
    audit_participant_set,
    build_data_product,
    build_participant_set,
)
from civ_workshop.errors import CivError
from tests.helpers import write_micro_bag


def _write_recipe(
    path: Path,
    source: Path,
    *,
    source_id: str = "KSH-test-development",
    split: str = "development",
) -> None:
    recipe = {
        "contract": "civ.data-product-recipe/v1",
        "recipe_id": "test-signals-v1",
        "version": 1,
        "product_name": f"{source_id}-signals.mcap",
        "source": {"id": source_id, "sha256": sha256(source.read_bytes()).hexdigest()},
        "dataset": "kashiwa",
        "split": split,
        "topics": ["/micro/signal"],
        "license": {"name": "CC BY 4.0", "url": "https://creativecommons.org/licenses/by/4.0/"},
        "attribution": "Synthetic fixture used for CIV tests.",
        "rights_scope": "Test-only redistribution.",
        "modifications": ["Filtered to the explicit full-rate signal topic."],
    }
    path.write_text(json.dumps(recipe, indent=2) + "\n", encoding="utf-8")


def _messages(path: Path) -> list[tuple[object, ...]]:
    with path.open("rb") as stream:
        return [
            (
                schema.name if schema else "",
                schema.encoding if schema else "",
                schema.data if schema else b"",
                channel.topic,
                channel.message_encoding,
                channel.metadata,
                message.log_time,
                message.publish_time,
                message.sequence,
                message.data,
            )
            for schema, channel, message in make_reader(
                stream, validate_crcs=True
            ).iter_messages(topics=["/micro/signal"])
        ]


def _document(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def test_build_data_product_is_byte_deterministic_and_preserves_messages(tmp_path: Path) -> None:
    source = tmp_path / "source.mcap"
    recipe = tmp_path / "recipe.json"
    write_micro_bag(source)
    _write_recipe(recipe, source)

    first = build_data_product(source, recipe, tmp_path / "first")
    second = build_data_product(source, recipe, tmp_path / "second")
    first_product = tmp_path / "first" / str(first["product"])
    second_product = tmp_path / "second" / str(second["product"])
    first_manifest = tmp_path / "first" / str(first["manifest"])
    second_manifest = tmp_path / "second" / str(second["manifest"])

    assert first_product.read_bytes() == second_product.read_bytes()
    assert first_manifest.read_bytes() == second_manifest.read_bytes()
    assert _messages(source) == _messages(first_product)

    manifest = _document(first_manifest)
    assert manifest["contract"] == "civ.data-product-manifest/v1"
    assert manifest["parent"]["sha256"] == sha256(source.read_bytes()).hexdigest()
    assert manifest["product"]["sha256"] == sha256(first_product.read_bytes()).hexdigest()
    assert manifest["product"]["topics"] == [
        {
            "message_count": 5,
            "message_encoding": "json",
            "schema_encoding": "jsonschema",
            "schema_name": "civ.micro.Signal",
            "schema_sha256": manifest["product"]["topics"][0]["schema_sha256"],
            "topic": "/micro/signal",
        }
    ]
    assert manifest["required_disk_bytes"] == (
        first_product.stat().st_size + first_manifest.stat().st_size
    )


def test_manifest_and_set_have_no_sealed_or_organizer_metadata(tmp_path: Path) -> None:
    source = tmp_path / "source.mcap"
    recipe = tmp_path / "recipe.json"
    write_micro_bag(source)
    _write_recipe(recipe, source)
    result = build_data_product(source, recipe, tmp_path / "release")
    manifest_path = tmp_path / "release" / str(result["manifest"])
    set_path = tmp_path / "release" / "participant-products.json"

    first = build_participant_set([manifest_path], set_path, "civ-2026-test")
    second_path = tmp_path / "release" / "participant-products-copy.json"
    second = build_participant_set([manifest_path], second_path, "civ-2026-test")

    assert set_path.read_bytes() == second_path.read_bytes()
    assert first["manifest_sha256"] == second["manifest_sha256"]
    assert first["required_disk_bytes"] == (
        (tmp_path / "release" / str(result["product"])).stat().st_size
        + manifest_path.stat().st_size
        + set_path.stat().st_size
    )
    assert audit_participant_set(set_path) == {
        "message_count": 5,
        "product_count": 1,
        "required_disk_bytes": first["required_disk_bytes"],
        "set_sha256": first["manifest_sha256"],
        "valid": True,
    }
    public_text = manifest_path.read_text(encoding="utf-8") + set_path.read_text(
        encoding="utf-8"
    )
    assert str(tmp_path) not in public_text
    for forbidden in (
        "label_pack",
        "sealed-source",
        "sealed_interval",
        "organizer_path",
        "hidden_evaluation",
        "ground_truth",
    ):
        assert forbidden not in public_text


def test_participant_set_rejects_sealed_product(tmp_path: Path) -> None:
    source = tmp_path / "source.mcap"
    recipe = tmp_path / "recipe.json"
    write_micro_bag(source)
    _write_recipe(recipe, source, source_id="KSH-test-sealed", split="sealed")
    result = build_data_product(source, recipe, tmp_path / "sealed")

    with pytest.raises(CivError, match="must not include a sealed product"):
        build_participant_set(
            [tmp_path / "sealed" / str(result["manifest"])],
            tmp_path / "participant.json",
            "civ-2026-test",
        )


def test_build_rejects_wrong_parent_hash_before_writing(tmp_path: Path) -> None:
    source = tmp_path / "source.mcap"
    recipe = tmp_path / "recipe.json"
    write_micro_bag(source)
    _write_recipe(recipe, source)
    value = _document(recipe)
    value["source"]["sha256"] = "0" * 64
    recipe.write_text(json.dumps(value) + "\n", encoding="utf-8")

    with pytest.raises(CivError, match="source SHA-256 does not match recipe"):
        build_data_product(source, recipe, tmp_path / "release")

    assert not (tmp_path / "release").exists()


def test_build_rejects_missing_topic_without_leaving_product(tmp_path: Path) -> None:
    source = tmp_path / "source.mcap"
    recipe = tmp_path / "recipe.json"
    write_micro_bag(source)
    _write_recipe(recipe, source)
    value = _document(recipe)
    value["topics"] = ["/missing"]
    recipe.write_text(json.dumps(value) + "\n", encoding="utf-8")

    with pytest.raises(CivError, match="source is missing recipe topics"):
        build_data_product(source, recipe, tmp_path / "release")

    assert not (tmp_path / "release" / "KSH-test-development-signals.mcap").exists()
