from __future__ import annotations

import json
import subprocess
import sys
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

from mcap.writer import CompressionType, Writer

NANOSECONDS = 1_000_000_000

MICRO_SPEC = """\
spec: civ.eventspec/v1alpha1
name: micro-high-signal
signals:
  signal:
    topic: /micro/signal
    field: value
condition: signal > 1.0
timing:
  min_duration: 1s
  merge_gap: 1.1s
  max_duration: 10s
evidence:
  before: 0.5s
  after: 0.5s
  topics:
    - /micro/signal
    - /micro/evidence
"""

MICRO_LABEL_PACK = {
    "contract": "civ.label-pack/v1alpha1",
    "dataset": "micro",
    "labels": [{"end_ns": 2_000_000_000, "label_id": "turn-1", "start_ns": 1_000_000_000}],
}

MICRO_REPORT = """\
# Question and hypothesis
The signal marks the interval.

# Signals used, missing, or unreliable
The micro signal is complete.

# What transferred and what did not
The interval contract transferred.

# One failure and the resulting change
Sampling over-counted; timing collapsed it.

# Downstream action and deployment mode
Review the local evidence clip.

![Evidence interval](figure.svg)
"""


@dataclass(frozen=True)
class MicroCase:
    root: Path
    bag: Path
    spec: Path
    labels: Path


def write_micro_bag(path: Path) -> None:
    schemas = {
        "/micro/signal": (
            "civ.micro.Signal",
            {"type": "object", "properties": {"value": {"type": "number"}}},
        ),
        "/micro/evidence": (
            "civ.micro.Evidence",
            {"type": "object", "properties": {"label": {"type": "string"}}},
        ),
    }
    signal_values = [0.0, 2.0, 2.0, 0.0, 0.0]

    with path.open("wb") as stream:
        writer = Writer(stream, compression=CompressionType.NONE)
        writer.start(profile="civ.micro", library="civ-test-fixture")
        channels: dict[str, int] = {}
        for topic, (name, schema) in schemas.items():
            schema_id = writer.register_schema(
                name=name,
                encoding="jsonschema",
                data=json.dumps(schema, sort_keys=True).encode(),
            )
            channels[topic] = writer.register_channel(
                schema_id=schema_id,
                topic=topic,
                message_encoding="json",
            )

        for second, value in enumerate(signal_values):
            timestamp = second * NANOSECONDS
            writer.add_message(
                channel_id=channels["/micro/signal"],
                log_time=timestamp,
                publish_time=timestamp,
                data=json.dumps({"value": value}).encode(),
            )
            writer.add_message(
                channel_id=channels["/micro/evidence"],
                log_time=timestamp,
                publish_time=timestamp,
                data=json.dumps({"label": f"frame-{second}"}).encode(),
            )
        writer.finish()


def create_micro_case(root: Path) -> MicroCase:
    bag = root / "micro.mcap"
    spec = root / "detector.yaml"
    labels = root / "labels.json"
    write_micro_bag(bag)
    spec.write_text(MICRO_SPEC, encoding="utf-8")
    labels.write_text(json.dumps(MICRO_LABEL_PACK, sort_keys=True), encoding="utf-8")
    return MicroCase(root=root, bag=bag, spec=spec, labels=labels)


def run_civ(cwd: Path, arguments: Sequence[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "civ_workshop", *arguments],
        cwd=cwd,
        text=True,
        capture_output=True,
        check=False,
    )


def detect_micro_case(case: MicroCase, working: Path) -> subprocess.CompletedProcess[str]:
    return run_civ(
        case.root,
        ["detect", str(case.spec), str(case.bag), "--output", str(working)],
    )


def prepare_scored_submission(case: MicroCase, working: Path) -> None:
    commands = [
        ["detect", str(case.spec), str(case.bag), "--output", str(working)],
        ["clip", str(working / "events.jsonl"), str(case.bag)],
        ["score", str(working), "--labels", str(case.labels)],
    ]
    for command in commands:
        result = run_civ(case.root, command)
        if result.returncode:
            raise AssertionError(result.stderr)
    (working / "report.md").write_text(MICRO_REPORT, encoding="utf-8")
    (working / "figure.svg").write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="10"></svg>\n',
        encoding="utf-8",
    )
    (working / "reproduce.ps1").write_text(
        "civ detect detector/detector.yaml micro.mcap\n", encoding="utf-8"
    )


def run_complete_workflow(case: MicroCase, working: Path) -> subprocess.CompletedProcess[str]:
    prepare_scored_submission(case, working)
    return run_civ(case.root, ["report", str(working)])
