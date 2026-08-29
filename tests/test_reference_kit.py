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
ORGANIZER_COMMANDS = ("intake-form", "intake-tally", "intake-local", "score-batch")
REFERENCE_PATHS = [
    ("layouts/kashiwa-right-turn.pj4.xml", "examples/kashiwa/right_turn.yaml"),
    ("layouts/reims-left-turn.pj4.xml", "examples/reims/left_turn.yaml"),
]


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


@pytest.mark.parametrize(("layout", "example"), REFERENCE_PATHS)
def test_quickstart_and_layouts_reference_only_existing_files(layout: str, example: str) -> None:
    quickstart = QUICKSTART.read_text(encoding="utf-8")

    assert (REPOSITORY / layout).is_file()
    assert (REPOSITORY / example).is_file()
    assert layout in quickstart, "the quickstart never points a reader at this layout"
    for referenced in re.findall(r"(?:layouts|examples|schemas)/[\w./-]+", quickstart):
        assert (REPOSITORY / referenced).is_file(), f"quickstart links a missing file: {referenced}"
    # Participant artifacts stay offline: no download URL, signed or otherwise.
    for text in (quickstart, (REPOSITORY / layout).read_text(encoding="utf-8")):
        assert "http://" not in text and "https://" not in text


def test_quickstart_uses_only_public_participant_commands() -> None:
    quickstart = QUICKSTART.read_text(encoding="utf-8")

    invoked = set(re.findall(r"\bciv ([a-z-]+)", quickstart))
    assert invoked, "quickstart invokes no commands"
    assert invoked <= PARTICIPANT_COMMANDS, f"unexpected commands: {sorted(invoked)}"
    for organizer_command in ORGANIZER_COMMANDS:
        assert organizer_command not in quickstart


def test_quickstart_covers_every_golden_path_step_with_one_recovery_pointer() -> None:
    quickstart = QUICKSTART.read_text(encoding="utf-8")
    steps = re.split(r"^## \d\. ", quickstart, flags=re.M)[1:]

    assert [step.splitlines()[0] for step in steps] == [
        "Check the environment",
        "See what is in the bag",
        "Look at one signal",
        "Detect intervals",
        "Extract evidence",
    ]
    for step in steps:
        # Every step shows its command, its expected output, and how to recover.
        assert step.count("```text") >= 2
        assert step.strip().split("```")[-1].strip(), "step ends without a recovery pointer"


def test_quickstart_separates_working_evidence_from_the_metadata_bundle() -> None:
    quickstart = QUICKSTART.read_text(encoding="utf-8")

    assert "work/evidence/<event_id>.mcap" in quickstart
    assert "No bag and no clip is ever bundled" in quickstart


def test_quickstart_fits_one_rendered_page() -> None:
    lines = QUICKSTART.read_text(encoding="utf-8").splitlines()

    # A rendered page holds roughly 55 lines of body text; blank lines cost nothing.
    assert len([line for line in lines if line.strip()]) <= 80
