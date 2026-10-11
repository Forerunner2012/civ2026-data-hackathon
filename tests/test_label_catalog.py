from pathlib import Path

import pytest

from civ_workshop.artifacts import canonical_json, file_sha256
from civ_workshop.errors import CivError
from civ_workshop.organizer.label_catalog import catalog_artifacts


def test_typed_catalog_reports_missing_mismatch_and_duplicate_bytes(tmp_path: Path) -> None:
    pack = tmp_path / "pack.json"
    pack.write_text(
        canonical_json(
            {
                "contract": "civ.label-pack/v1alpha1",
                "dataset": "kashiwa",
                "source_sha256": "a" * 64,
                "labels": [],
                "data_gaps": [],
            }
        )
    )
    records = [
        {
            "id": "reference",
            "kind": "consumer-pack",
            "path": pack.name,
            "sha256": file_sha256(pack),
        },
        {"id": "alias", "kind": "consumer-pack", "path": pack.name, "sha256": file_sha256(pack)},
        {
            "id": "wrong-type",
            "kind": "review-progress",
            "path": pack.name,
            "sha256": file_sha256(pack),
        },
        {"id": "changed", "kind": "consumer-pack", "path": pack.name, "sha256": "b" * 64},
        {"id": "missing", "kind": "consumer-pack", "path": "absent.json", "sha256": "c" * 64},
    ]
    inventory = tmp_path / "inventory.json"
    inventory.write_text(canonical_json({"artifacts": records}))
    result = catalog_artifacts(inventory)
    assert result == catalog_artifacts(inventory)
    assert result["valid"] is False
    artifacts = result["artifacts"]
    assert isinstance(artifacts, list)
    assert artifacts[0]["identity_verified"] is True
    assert artifacts[0]["review_compatibility"] == "reference-only"
    assert "artifact type" in artifacts[2]["errors"][0]
    assert "SHA-256 mismatch" in artifacts[3]["errors"][0]
    assert artifacts[4]["identity_verified"] is False
    assert result["duplicate_content"]


def test_private_approval_does_not_qualify_aggregate_or_review(tmp_path: Path) -> None:
    approval = tmp_path / "approval.json"
    approval.write_text(
        canonical_json(
            {
                "contract": "civ.release-development-authority-approval/v1",
                "decision": "approved",
                "development_authority": {
                    "set_sha256": "a" * 64,
                    "participant_distribution": False,
                    "sealed_authority_included": False,
                },
            }
        )
    )
    inventory = tmp_path / "inventory.json"
    inventory.write_text(
        canonical_json(
            {
                "artifacts": [
                    {
                        "id": "development-approval",
                        "kind": "approval",
                        "path": approval.name,
                        "sha256": file_sha256(approval),
                    }
                ]
            }
        )
    )
    result = catalog_artifacts(inventory)
    artifacts = result["artifacts"]
    assert isinstance(artifacts, list)
    authority = artifacts[0]["authority"]
    assert authority["aggregate_verified"] is False
    assert authority["participant_distribution"] is False
    assert authority["sealed_authority_included"] is False
    assert artifacts[0]["review_compatibility"] == "historical-authority-requires-binding-review"


@pytest.mark.parametrize("update", [{"sha256": "bad"}, {"kind": "automatic-truth"}])
def test_catalog_rejects_invalid_declarations(tmp_path: Path, update: dict[str, str]) -> None:
    record = {"id": "a", "kind": "consumer-pack", "path": "a.json", "sha256": "a" * 64}
    record.update(update)
    inventory = tmp_path / "inventory.json"
    inventory.write_text(canonical_json({"artifacts": [record]}))
    with pytest.raises(CivError):
        catalog_artifacts(inventory)


def test_catalog_cli_reads_relative_paths_and_fails_on_mismatch(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    import json

    from civ_workshop.cli import main

    pack = tmp_path / "pack.json"
    pack.write_text(
        canonical_json(
            {
                "contract": "civ.label-pack/v1alpha1",
                "dataset": "reims",
                "source_sha256": "a" * 64,
                "labels": [],
                "data_gaps": [],
            }
        )
    )
    entry = {
        "id": "reference",
        "kind": "consumer-pack",
        "path": pack.name,
        "sha256": file_sha256(pack),
    }
    inventory = tmp_path / "inventory.json"
    inventory.write_text(canonical_json({"artifacts": [entry]}))
    main(["labels", "catalog", "--inventory", str(inventory)])
    assert json.loads(capsys.readouterr().out)["valid"] is True
    entry["sha256"] = "b" * 64
    inventory.write_text(canonical_json({"artifacts": [entry]}))
    with pytest.raises(SystemExit) as error:
        main(["labels", "catalog", "--inventory", str(inventory)])
    assert error.value.code == 2
    assert json.loads(capsys.readouterr().out)["valid"] is False
