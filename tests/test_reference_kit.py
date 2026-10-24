from __future__ import annotations

import re
import xml.etree.ElementTree as ElementTree
from pathlib import Path

import pytest
import yaml

REPOSITORY = Path(__file__).parents[1]
QUICKSTART = REPOSITORY / "docs" / "quickstart.md"
PARTICIPANT_COMMANDS = {
    "clip",
    "detect",
    "doctor",
    "inspect",
    "report",
    "sample",
    "score",
    "submission-init",
}
ORGANIZER_COMMANDS = (
    "intake-form", "intake-tally", "intake-local", "score-batch",
    "score-readiness", "record-decision",
)
REFERENCE_PATHS = [
    ("layouts/kashiwa-right-turn.pj4.xml", "examples/kashiwa/right_turn.yaml"),
    ("layouts/reims-left-turn.pj4.xml", "examples/reims/left_turn.yaml"),
]
OPTIONAL_CONTEXT_TOPICS = {
    "/sensing/camera/traffic_light/image_raw/compressed",
    "/zed/zed_node/rgb/image_rect_color/compressed",
}


def _curves(layout: Path) -> list[str]:
    root = ElementTree.parse(layout).getroot()
    return [curve.attrib["name"] for curve in root.iter("curve")]


def _spec_topics(spec_path: Path) -> tuple[dict[str, set[str]], set[str]]:
    """Return the fields bound per signal topic and every topic the spec names.

    A topic can carry several bindings: the Reims path reads three components off
    /fix_velocity.
    """

    spec = yaml.safe_load(spec_path.read_text(encoding="utf-8"))
    signals: dict[str, set[str]] = {}
    for binding in spec["signals"].values():
        signals.setdefault(binding["topic"], set()).add(binding["field"])
    return signals, set(signals) | set(spec["evidence"]["topics"])


@pytest.mark.parametrize(("layout", "example"), REFERENCE_PATHS)
def test_layout_curves_resolve_to_signals_the_reference_spec_names(
    layout: str, example: str
) -> None:
    signals, topics = _spec_topics(REPOSITORY / example)
    curves = _curves(REPOSITORY / layout)

    assert curves, "layout declares no curves"
    for curve in curves:
        # PlotJuggler names a series <topic>/<field path>; the longest matching topic wins.
        matches = [topic for topic in topics if curve.startswith(f"{topic}/")]
        assert matches, f"curve {curve} needs a topic the reference path does not name"
        topic = max(matches, key=len)
        field = curve.removeprefix(f"{topic}/")
        if topic in signals:
            bound = {name.replace(".", "/") for name in signals[topic]}
            assert field in bound, (
                f"curve {curve} does not plot a field bound by the EventSpec"
            )


@pytest.mark.parametrize(("_layout", "example"), REFERENCE_PATHS)
def test_reference_specs_clip_only_signals_in_the_default_kit(
    _layout: str, example: str
) -> None:
    _, topics = _spec_topics(REPOSITORY / example)

    assert topics.isdisjoint(OPTIONAL_CONTEXT_TOPICS)


@pytest.mark.parametrize(("layout", "example"), REFERENCE_PATHS)
def test_quickstart_and_layouts_reference_only_existing_files(layout: str, example: str) -> None:
    quickstart = QUICKSTART.read_text(encoding="utf-8")

    assert (REPOSITORY / layout).is_file()
    assert (REPOSITORY / example).is_file()
    assert layout in quickstart, "the quickstart never points a reader at this layout"
    for referenced in re.findall(r"(?:layouts|examples|schemas)/[\w./-]+", quickstart):
        assert (REPOSITORY / referenced).is_file(), f"quickstart links a missing file: {referenced}"
    # Connected installation precedes the offline analysis; layouts remain local.
    analysis = quickstart.split("## The route at a glance", 1)[1]
    for text in (analysis, (REPOSITORY / layout).read_text(encoding="utf-8")):
        assert "http://" not in text and "https://" not in text


def test_quickstart_uses_only_public_participant_commands() -> None:
    quickstart = QUICKSTART.read_text(encoding="utf-8")

    invoked = set(re.findall(r"\bciv ([a-z][a-z-]*)", quickstart))
    assert invoked, "quickstart invokes no commands"
    assert invoked <= PARTICIPANT_COMMANDS, f"unexpected commands: {sorted(invoked)}"
    for organizer_command in ORGANIZER_COMMANDS:
        assert organizer_command not in quickstart


def test_quickstart_covers_every_golden_path_step_and_product() -> None:
    quickstart = QUICKSTART.read_text(encoding="utf-8")
    steps = re.split(r"^## \d\. ", quickstart, flags=re.M)[1:]

    assert [step.splitlines()[0] for step in steps] == [
        "Check the environment",
        "Inventory topics and fields",
        "Sample one signal and look at the recording",
        "Create your working submission once",
        "Detect intervals",
        "Extract local evidence",
        "Score against the supplied practice labels",
        "Validate and keep the metadata-only ZIP",
    ]
    for product in (
        "events.jsonl",
        "run-manifest.json",
        "evidence/<event_id>.mcap",
        "metrics.json",
        "submission.zip",
    ):
        assert product in quickstart


def test_quickstart_separates_working_evidence_from_the_metadata_bundle() -> None:
    quickstart = QUICKSTART.read_text(encoding="utf-8")

    assert "working/evidence/<event_id>.mcap" in quickstart
    assert "No bag and no clip is ever bundled" in quickstart


def test_quickstart_visualizes_the_command_dependency_chain() -> None:
    quickstart = QUICKSTART.read_text(encoding="utf-8")

    assert "```mermaid" in quickstart
    offsets = [quickstart.index(f"## {index}.") for index in range(1, 9)]
    assert offsets == sorted(offsets)
