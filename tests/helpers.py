from __future__ import annotations

import json
import os
import subprocess
import sys
from collections.abc import Sequence
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path

from mcap.writer import CompressionType, Writer
from mcap_ros2.writer import Writer as Ros2Writer

NANOSECONDS = 1_000_000_000

MICRO_SPEC = """\
spec: civ.eventspec/v1
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
    "data_gaps": [],
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


MICRO_SIGNAL_VALUES = (0.0, 2.0, 2.0, 0.0, 0.0)


def write_micro_bag(path: Path, values: Sequence[float] = MICRO_SIGNAL_VALUES) -> None:
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
    signal_values = list(values)

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


def write_ros2_bool_bag(path: Path, values: Sequence[bool] = (True,)) -> None:
    with path.open("wb") as stream:
        writer = Ros2Writer(stream, compression=CompressionType.NONE)
        schema = writer.register_msgdef("std_msgs/msg/Bool", "bool data\n")
        for second, value in enumerate(values):
            timestamp = second * NANOSECONDS
            writer.write_message(
                topic="/ros2/enabled",
                schema=schema,
                message={"data": value},
                log_time=timestamp,
                publish_time=timestamp,
            )
        writer.finish()


def write_ros2_nested_bag(path: Path) -> None:
    schema_text = """\
civ_msgs/TurnState turn
================================================================================
MSG: civ_msgs/TurnState
geometry_msgs/Vector3 angular
================================================================================
MSG: geometry_msgs/Vector3
float64 x
float64 y
float64 z
"""
    with path.open("wb") as stream:
        writer = Ros2Writer(stream, compression=CompressionType.NONE)
        schema = writer.register_msgdef("civ_msgs/msg/TurnSample", schema_text)
        writer.write_message(
            topic="/ros2/turn",
            schema=schema,
            message={"turn": {"angular": {"x": 0.0, "y": 0.0, "z": -0.25}}},
            log_time=1_000_000_000,
            publish_time=1_000_000_000,
        )
        writer.finish()


def write_ros2_steering_bag(path: Path) -> None:
    values = [0, *([15] * 21), 0, 0, 0, 0, 0, 0, 0, 0, *([15] * 6), 0]
    with path.open("wb") as stream:
        writer = Ros2Writer(stream, compression=CompressionType.NONE)
        schema = writer.register_msgdef(
            "pix_hooke_driver_msgs/msg/V2aSteerStaFb",
            "int32 vcu_chassis_steer_angle_fb\n",
        )
        for second, value in enumerate(values):
            timestamp = second * NANOSECONDS
            writer.write_message(
                topic="/pix_hooke/v2a_steerstafb",
                schema=schema,
                message={"vcu_chassis_steer_angle_fb": value},
                log_time=timestamp,
                publish_time=timestamp,
            )
        writer.finish()


def write_ros2_french_turn_bag(path: Path) -> None:
    imu_schema_text = """\
geometry_msgs/Vector3 angular_velocity
================================================================================
MSG: geometry_msgs/Vector3
float64 x
float64 y
float64 z
"""
    velocity_schema_text = """\
geometry_msgs/TwistWithCovariance twist
================================================================================
MSG: geometry_msgs/TwistWithCovariance
geometry_msgs/Twist twist
================================================================================
MSG: geometry_msgs/Twist
geometry_msgs/Vector3 linear
================================================================================
MSG: geometry_msgs/Vector3
float64 x
float64 y
float64 z
"""
    with path.open("wb") as stream:
        writer = Ros2Writer(stream, compression=CompressionType.NONE)
        imu_schema = writer.register_msgdef("sensor_msgs/msg/Imu", imu_schema_text)
        velocity_schema = writer.register_msgdef(
            "geometry_msgs/msg/TwistWithCovarianceStamped", velocity_schema_text
        )
        for index in range(40):
            timestamp = index * 250_000_000
            yaw_rate = 0.0
            speed = 2.0 if 19 <= index <= 23 else 4.0
            if 4 <= index <= 7:
                yaw_rate = 0.1
            elif 12 <= index <= 15:
                yaw_rate = -0.1
            elif 20 <= index <= 22 or 36 <= index <= 37:
                yaw_rate = 0.1
            writer.write_message(
                topic="/zed/zed_node/imu/data",
                schema=imu_schema,
                message={"angular_velocity": {"x": 0.0, "y": 0.0, "z": yaw_rate}},
                log_time=timestamp,
                publish_time=timestamp,
            )
            writer.write_message(
                topic="/fix_velocity",
                schema=velocity_schema,
                message={
                    "twist": {
                        "twist": {"linear": {"x": speed, "y": 0.0, "z": 0.0}}
                    }
                },
                log_time=timestamp,
                publish_time=timestamp,
            )
        writer.finish()


def write_raw_ros2_bag(path: Path, schema_data: bytes) -> None:
    with path.open("wb") as stream:
        writer = Writer(stream, compression=CompressionType.NONE)
        writer.start(profile="ros2", library="civ-test-fixture")
        schema_id = writer.register_schema(
            name="civ_msgs/msg/Broken",
            encoding="ros2msg",
            data=schema_data,
        )
        channel_id = writer.register_channel(
            schema_id=schema_id,
            topic="/ros2/broken",
            message_encoding="cdr",
        )
        writer.add_message(
            channel_id=channel_id,
            log_time=1_000_000_000,
            publish_time=1_000_000_000,
            data=b"\x00",
        )
        writer.finish()


def write_nested_json_bag(path: Path) -> None:
    schema = {
        "type": "object",
        "properties": {
            "pose": {
                "type": "object",
                "properties": {
                    "position": {
                        "type": "object",
                        "properties": {"x": {"type": "number"}},
                    }
                },
            }
        },
    }
    with path.open("wb") as stream:
        writer = Writer(stream, compression=CompressionType.NONE)
        writer.start(profile="civ.micro", library="civ-test-fixture")
        schema_id = writer.register_schema(
            name="civ.micro.Pose",
            encoding="jsonschema",
            data=json.dumps(schema, sort_keys=True).encode(),
        )
        channel_id = writer.register_channel(
            schema_id=schema_id,
            topic="/micro/pose",
            message_encoding="json",
        )
        writer.add_message(
            channel_id=channel_id,
            log_time=2_000_000_000,
            publish_time=2_000_000_000,
            data=b'{"pose":{"position":{"x":4.5}}}',
        )
        writer.finish()


def write_raw_schema_bag(
    path: Path,
    *,
    schema_encoding: str,
    message_encoding: str,
    schema_data: bytes = b"",
    schema_name: str = "tier4_msgs/msg/Mode",
    topic: str = "/tier4/mode",
) -> None:
    with path.open("wb") as stream:
        writer = Writer(stream, compression=CompressionType.NONE)
        writer.start(profile="ros2", library="civ-test-fixture")
        schema_id = writer.register_schema(
            name=schema_name,
            encoding=schema_encoding,
            data=schema_data,
        )
        channel_id = writer.register_channel(
            schema_id=schema_id,
            topic=topic,
            message_encoding=message_encoding,
        )
        writer.add_message(
            channel_id=channel_id,
            log_time=1_000_000_000,
            publish_time=1_000_000_000,
            data=b"\x00",
        )
        writer.finish()


def create_micro_case(root: Path, values: Sequence[float] = MICRO_SIGNAL_VALUES) -> MicroCase:
    root.mkdir(parents=True, exist_ok=True)
    bag = root / "micro.mcap"
    spec = root / "detector.yaml"
    labels = root / "labels.json"
    write_micro_bag(bag, values)
    spec.write_text(MICRO_SPEC, encoding="utf-8")
    label_pack = {**MICRO_LABEL_PACK, "source_sha256": sha256(bag.read_bytes()).hexdigest()}
    labels.write_text(json.dumps(label_pack, sort_keys=True), encoding="utf-8")
    return MicroCase(root=root, bag=bag, spec=spec, labels=labels)


def run_civ(
    cwd: Path,
    arguments: Sequence[str],
    *,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    process_env = os.environ.copy()
    if env is not None:
        process_env.update(env)
    return subprocess.run(
        [sys.executable, "-m", "civ_workshop", *arguments],
        cwd=cwd,
        env=process_env,
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
