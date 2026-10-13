"""Check generated deck hashes, dimensions, image identity and slide geometry."""

from __future__ import annotations

import hashlib
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from zipfile import BadZipFile, ZipFile

NS = {
    "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
}
REL = "{http://schemas.openxmlformats.org/package/2006/relationships}"


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _verify_presentations(root: Path) -> tuple[Path, ...]:
    """Verify the generated artifact pair before copying it into a kit."""
    render = json.loads((root / "render-manifest.json").read_text(encoding="utf-8-sig"))
    assembly = json.loads((root / "assembly-manifest.json").read_text(encoding="utf-8-sig"))
    if not isinstance(render, dict) or not isinstance(assembly, dict):
        raise ValueError("Presentation receipts must be objects")
    if digest((root / "render-manifest.json").read_bytes()) != assembly["render_manifest_sha256"]:
        raise ValueError("Render receipt changed")
    if (
        render.get("kind") != "civ.presentation-render/v1"
        or assembly.get("kind") != "civ.presentation-assembly/v1"
    ):
        raise ValueError("Unsupported presentation receipt kind")
    if (render.get("width"), render.get("height")) != (1920, 1080):
        raise ValueError("Render canvas mismatch")
    expected = {"briefing": 13, "submission-checklist": 1}
    if len(assembly["outputs"]) != 2 or len(render["decks"]) != 2:
        raise ValueError("Expected exactly the two approved decks")
    if {item["name"]: item["slides"] for item in assembly["outputs"]} != expected:
        raise ValueError("Expected 13+1 deck outputs")
    for output, deck in zip(assembly["outputs"], render["decks"], strict=True):
        if output["name"] != deck["name"] or output["file"] != output["name"] + ".pptx":
            raise ValueError("Deck identity mismatch")
        data = (root / output["file"]).read_bytes()
        if digest(data) != output["sha256"]:
            raise ValueError("Deck hash mismatch")
        with ZipFile(root / output["file"]) as archive:
            presentation = ET.fromstring(archive.read("ppt/presentation.xml"))
            size = presentation.find("p:sldSz", NS)
            if (
                size is None
                or (int(size.attrib["cx"]), int(size.attrib["cy"])) != (12192000, 6858000)
                or size.attrib.get("type") != "screen16x9"
            ):
                raise ValueError("Widescreen dimensions or metadata mismatch")
            slide_ids = presentation.findall("p:sldIdLst/p:sldId", NS)
            if len(slide_ids) != expected[output["name"]]:
                raise ValueError("Slide count mismatch")
            for number, image in enumerate(deck["slides"], 1):
                slide = ET.fromstring(archive.read(f"ppt/slides/slide{number}.xml"))
                shapes = slide.find("p:cSld/p:spTree", NS)
                pictures = slide.findall("p:cSld/p:spTree/p:pic", NS)
                if (
                    shapes is None
                    or len(pictures) != 1
                    or any(
                        child.tag.rsplit("}", 1)[-1] in {"sp", "graphicFrame", "grpSp", "cxnSp"}
                        for child in shapes
                    )
                ):
                    raise ValueError("Expected exactly one full-slide picture")
                picture = pictures[0]
                offset = picture.find("p:spPr/a:xfrm/a:off", NS)
                extent = picture.find("p:spPr/a:xfrm/a:ext", NS)
                if (
                    offset is None
                    or extent is None
                    or offset.attrib != {"x": "0", "y": "0"}
                    or extent.attrib != {"cx": "12192000", "cy": "6858000"}
                ):
                    raise ValueError("Picture does not fill the slide")
                blip = picture.find("p:blipFill/a:blip", NS)
                if blip is None:
                    raise ValueError("Slide image relationship missing")
                relation_id = blip.attrib["{" + NS["r"] + "}embed"]
                relations = ET.fromstring(archive.read(f"ppt/slides/_rels/slide{number}.xml.rels"))
                target = next(
                    item.attrib["Target"]
                    for item in relations.findall(REL + "Relationship")
                    if item.attrib["Id"] == relation_id
                )
                media = str((Path("ppt/slides") / target).as_posix()).replace("slides/../", "")
                if digest(archive.read(media)) != image["sha256"]:
                    raise ValueError("Embedded image differs from verified capture")
    return tuple(root / output["file"] for output in assembly["outputs"])


def verified_presentations(root: Path) -> tuple[Path, ...]:
    """Return only the artifact pair whose identities and slide structure are verified."""
    try:
        return _verify_presentations(root)
    except (
        OSError,
        ValueError,
        KeyError,
        TypeError,
        StopIteration,
        BadZipFile,
        ET.ParseError,
    ) as error:
        raise ValueError(f"invalid presentation artifacts: {error}") from error
