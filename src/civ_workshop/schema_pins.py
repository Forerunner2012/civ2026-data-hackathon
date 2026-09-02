from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from typing import Any


@dataclass(frozen=True)
class GoldenSchemaPin:
    topic: str
    schema_name: str
    schema_encoding: str
    schema_sha256: str


GOLDEN_SCHEMA_PINS = {
    "/pix_hooke/v2a_steerstafb": GoldenSchemaPin(
        topic="/pix_hooke/v2a_steerstafb",
        schema_name="pix_hooke_driver_msgs/msg/V2aSteerStaFb",
        schema_encoding="ros2msg",
        schema_sha256="4c3724cf5ee83ef9cbd127585519e80c7828341fcd626d4d588d22d406918eea",
    ),
    "/fix_velocity": GoldenSchemaPin(
        topic="/fix_velocity",
        schema_name="geometry_msgs/msg/TwistWithCovarianceStamped",
        schema_encoding="ros2msg",
        schema_sha256="d2905f17c4de4e92d693447c2d64ce2b70f916cee14318bce69c1969f71121fd",
    ),
    "/zed/zed_node/imu/data": GoldenSchemaPin(
        topic="/zed/zed_node/imu/data",
        schema_name="sensor_msgs/msg/Imu",
        schema_encoding="ros2msg",
        schema_sha256="244d9e9566de33e36bf560d79a41a17d1a1b44c49bdaf2bd809aa7efb1389334",
    ),
}


def golden_schema_diagnostic(topic: str, schema: Any) -> str | None:
    pin = GOLDEN_SCHEMA_PINS.get(topic)
    if pin is None:
        return None
    if schema is None:
        return f"{topic}: pinned golden-path topic has no embedded schema"
    if schema.name != pin.schema_name or schema.encoding != pin.schema_encoding:
        encoding = schema.encoding or "unknown"
        return (
            f"{topic}: unknown golden-path schema {schema.name} ({encoding}); "
            f"expected {pin.schema_name} ({pin.schema_encoding})"
        )
    actual_sha256 = sha256(schema.data).hexdigest()
    if actual_sha256 != pin.schema_sha256:
        return (
            f"{topic}: embedded schema hash mismatch for {pin.schema_name}; "
            f"expected {pin.schema_sha256}, got {actual_sha256}"
        )
    return None
