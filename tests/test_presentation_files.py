from __future__ import annotations

import hashlib
import json
from pathlib import Path
from zipfile import ZipFile

import pytest

from civ_workshop.presentation_files import verified_presentations


def _write_fixture(root: Path, *, widescreen: bool = True) -> tuple[Path, Path]:
    root.mkdir()
    ns_p = "http://schemas.openxmlformats.org/presentationml/2006/main"
    ns_a = "http://schemas.openxmlformats.org/drawingml/2006/main"
    ns_r = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
    png = b"synthetic-image-identity"

    def digest(data: bytes) -> str:
        return hashlib.sha256(data).hexdigest()

    decks, outputs = [], []
    for name, count in [("briefing", 13), ("submission-checklist", 1)]:
        slides = [
            {"file": f"{name}-{i}.png", "sha256": digest(png), "notes": ""} for i in range(count)
        ]
        decks.append({"name": name, "slides": slides})
        target = root / f"{name}.pptx"
        with ZipFile(target, "w") as archive:
            ids = "".join(f'<p:sldId id="{i + 256}"/>' for i in range(count))
            metadata = "screen16x9" if widescreen else "screen4x3"
            archive.writestr(
                "ppt/presentation.xml",
                (
                    f'<p:presentation xmlns:p="{ns_p}">'
                    f"<p:sldIdLst>{ids}</p:sldIdLst>"
                    f'<p:sldSz cx="12192000" cy="6858000" type="{metadata}"/>'
                    "</p:presentation>"
                ),
            )
            archive.writestr("ppt/media/image1.png", png)
            for i in range(1, count + 1):
                archive.writestr(
                    f"ppt/slides/slide{i}.xml",
                    (
                        f'<p:sld xmlns:p="{ns_p}" xmlns:a="{ns_a}" xmlns:r="{ns_r}">'
                        '<p:cSld><p:spTree><p:pic><p:blipFill><a:blip r:embed="rId1"/>'
                        '</p:blipFill><p:spPr><a:xfrm><a:off x="0" y="0"/>'
                        '<a:ext cx="12192000" cy="6858000"/></a:xfrm></p:spPr>'
                        "</p:pic></p:spTree></p:cSld></p:sld>"
                    ),
                )
                archive.writestr(
                    f"ppt/slides/_rels/slide{i}.xml.rels",
                    (
                        '<Relationships xmlns="http://schemas.openxmlformats.org/'
                        'package/2006/relationships"><Relationship Id="rId1" '
                        'Target="../media/image1.png"/></Relationships>'
                    ),
                )
        outputs.append(
            {
                "name": name,
                "file": target.name,
                "sha256": digest(target.read_bytes()),
                "slides": count,
            }
        )
    render = root / "render-manifest.json"
    render.write_text(
        json.dumps(
            {"kind": "civ.presentation-render/v1", "width": 1920, "height": 1080, "decks": decks}
        ),
        encoding="utf-8",
    )
    (root / "assembly-manifest.json").write_text(
        json.dumps(
            {
                "kind": "civ.presentation-assembly/v1",
                "render_manifest_sha256": digest(render.read_bytes()),
                "outputs": outputs,
            }
        ),
        encoding="utf-8",
    )
    return root / "briefing.pptx", root / "submission-checklist.pptx"


def test_verified_pair_preserves_geometry_and_image_identity(tmp_path: Path) -> None:
    root = tmp_path / "decks"
    expected = _write_fixture(root)
    assert verified_presentations(root) == expected


def test_legacy_widescreen_metadata_mismatch_is_rejected(tmp_path: Path) -> None:
    root = tmp_path / "decks"
    _write_fixture(root, widescreen=False)
    with pytest.raises(ValueError, match="Widescreen dimensions or metadata"):
        verified_presentations(root)


def test_changed_deck_and_render_receipt_are_rejected(tmp_path: Path) -> None:
    root = tmp_path / "decks"
    briefing, _ = _write_fixture(root)
    briefing.write_bytes(briefing.read_bytes() + b"changed")
    with pytest.raises(ValueError, match="Deck hash mismatch"):
        verified_presentations(root)
    (root / "render-manifest.json").write_text("{}", encoding="utf-8")
    with pytest.raises(ValueError, match="Render receipt changed"):
        verified_presentations(root)
