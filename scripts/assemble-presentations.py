"""Assemble verified slide PNGs into local image-based PPTX decks."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from importlib.metadata import version
from pathlib import Path

from pptx import Presentation
from pptx.oxml.ns import qn

WIDTH, HEIGHT = 12192000, 6858000


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest = json.loads((args.input / "render-manifest.json").read_text(encoding="utf-8-sig"))
    if manifest["kind"] != "civ.presentation-render/v1" or (
        manifest["width"],
        manifest["height"],
    ) != (1920, 1080):
        raise ValueError("Unsupported render manifest")
    expected = {"briefing": 15, "submission-checklist": 1}
    if {deck["name"]: len(deck["slides"]) for deck in manifest["decks"]} != expected:
        raise ValueError("Expected the approved 15+1 decks")
    if (args.output / "assembly-manifest.json").exists():
        raise ValueError("Refusing to overwrite an existing assembly receipt")
    if (
        args.input.resolve() != args.output.resolve()
        and (args.output / "render-manifest.json").exists()
    ):
        raise ValueError("Refusing to overwrite an existing render receipt")
    args.output.mkdir(parents=True, exist_ok=True)
    for deck in manifest["decks"]:
        if (args.output / (deck["name"] + ".pptx")).exists():
            raise ValueError("Refusing to overwrite an existing deck")
        for slide in deck["slides"]:
            if (
                Path(slide["file"]).name != slide["file"]
                or digest(args.input / slide["file"]) != slide["sha256"]
            ):
                raise ValueError("Slide image identity mismatch")
    if args.input.resolve() != args.output.resolve():
        (args.output / "render-manifest.json").write_bytes(
            (args.input / "render-manifest.json").read_bytes()
        )
    outputs = []
    for deck in manifest["decks"]:
        presentation = Presentation()
        presentation.slide_width, presentation.slide_height = WIDTH, HEIGHT
        presentation._element.find(qn("p:sldSz")).set("type", "screen16x9")
        presentation.core_properties.title = "CIV 2026 " + deck["name"]
        presentation.core_properties.author = "CIV 2026 organizers"
        for rendered in deck["slides"]:
            slide = presentation.slides.add_slide(presentation.slide_layouts[6])
            slide.shapes.add_picture(
                str(args.input / rendered["file"]), 0, 0, width=WIDTH, height=HEIGHT
            )
            slide.notes_slide.notes_text_frame.text = rendered["notes"]
        target = args.output / (deck["name"] + ".pptx")
        presentation.save(target)
        outputs.append(
            {
                "name": deck["name"],
                "file": target.name,
                "sha256": digest(target),
                "slides": len(deck["slides"]),
            }
        )
    receipt = {
        "kind": "civ.presentation-assembly/v1",
        "python_version": sys.version.split()[0],
        "python_pptx_version": version("python-pptx"),
        "render_manifest_sha256": digest(args.input / "render-manifest.json"),
        "width_emu": WIDTH,
        "height_emu": HEIGHT,
        "outputs": outputs,
    }
    (args.output / "assembly-manifest.json").write_text(
        json.dumps(receipt, indent=2), encoding="utf-8"
    )
    print("Assembled the approved 15+1 image-based widescreen decks locally.")


if __name__ == "__main__":
    main()
