#!/usr/bin/env python
r"""Stream the Reims MCAP recording and reproduce ticket 24's measurements.

Run without creating a project environment:

    uv run --no-project --with mcap==1.4.0 --with mcap-ros2-support==0.5.7 -- \
      python .scratch/civ2026-challenge-spec/research/survey_reims_bag.py \
      "D:\Bags\Data Hackathon\2025-07-30 Recording sessions" \
      --output "$env:TEMP\civ2026-reims-bag-survey.json"
"""

from __future__ import annotations

import argparse
import bisect
import itertools
import json
import math
import statistics
from collections import Counter
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from mcap_ros2.reader import read_ros2_messages

FIX_TOPIC = "/fix"
VELOCITY_TOPIC = "/fix_velocity"
IMU_TOPIC = "/zed/zed_node/imu/data"
OBJECTS_TOPIC = "/zed/zed_node/obj_det/objects"
TOPICS = [FIX_TOPIC, VELOCITY_TOPIC, IMU_TOPIC, OBJECTS_TOPIC]
EARTH_RADIUS_M = 6_371_008.8


def percentile(values: list[float], fraction: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    position = fraction * (len(ordered) - 1)
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    weight = position - lower
    return ordered[lower] * (1 - weight) + ordered[upper] * weight


def iso_time(seconds: float) -> str:
    return datetime.fromtimestamp(seconds, tz=timezone.utc).isoformat()


def haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = phi2 - phi1
    dlambda = math.radians(lon2 - lon1)
    a = (
        math.sin(dphi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    )
    return 2 * EARTH_RADIUS_M * math.asin(min(1.0, math.sqrt(a)))


def local_distance_m(
    lat: float, lon: float, reference_lat: float, reference_lon: float
) -> float:
    x = math.radians(lon - reference_lon) * math.cos(
        math.radians((lat + reference_lat) / 2)
    )
    y = math.radians(lat - reference_lat)
    return EARTH_RADIUS_M * math.hypot(x, y)


def wrap_radians(value: float) -> float:
    return (value + math.pi) % (2 * math.pi) - math.pi


def circular_mean(values: Iterable[float]) -> float | None:
    values = list(values)
    if not values:
        return None
    return math.atan2(
        sum(math.sin(value) for value in values),
        sum(math.cos(value) for value in values),
    )


@dataclass
class Fix:
    t: float
    lat: float
    lon: float
    altitude: float
    status: int
    service: int
    covariance_type: int
    sigma_horizontal_m: float | None


@dataclass
class Velocity:
    t: float
    speed_mps: float
    course_rad: float


class TurnDetector:
    """Segment sustained yaw excursions with a speed floor and short-gap merge."""

    def __init__(
        self,
        *,
        direction: int,
        threshold_rad_s: float,
        minimum_angle_deg: float,
        speed_floor_mps: float = 0.5,
        minimum_duration_s: float = 0.7,
        merge_gap_s: float = 0.75,
    ) -> None:
        self.direction = direction
        self.threshold_rad_s = threshold_rad_s
        self.minimum_angle_rad = math.radians(minimum_angle_deg)
        self.speed_floor_mps = speed_floor_mps
        self.minimum_duration_s = minimum_duration_s
        self.merge_gap_s = merge_gap_s
        self.events: list[dict[str, Any]] = []
        self.current: dict[str, Any] | None = None
        self.previous_t: float | None = None

    def feed(
        self,
        *,
        t: float,
        yaw_rate_rad_s: float,
        speed_mps: float,
        lat: float | None,
        lon: float | None,
    ) -> None:
        directional_rate = self.direction * yaw_rate_rad_s
        meets = (
            directional_rate >= self.threshold_rad_s
            and speed_mps >= self.speed_floor_mps
        )

        if self.current is not None and self.previous_t is not None:
            dt = t - self.previous_t
            if 0 < dt < 0.25 and t - self.current["last_active"] <= self.merge_gap_s:
                self.current["positive_angle_rad"] += max(directional_rate, 0.0) * dt
                self.current["net_angle_rad"] += directional_rate * dt

        if meets:
            if self.current is None:
                self.current = {
                    "start": t,
                    "last_active": t,
                    "positive_angle_rad": 0.0,
                    "net_angle_rad": 0.0,
                    "peak_rate_rad_s": directional_rate,
                    "peak_time": t,
                    "peak_lat": lat,
                    "peak_lon": lon,
                    "minimum_speed_mps": speed_mps,
                    "maximum_speed_mps": speed_mps,
                }
            else:
                self.current["last_active"] = t
                self.current["minimum_speed_mps"] = min(
                    self.current["minimum_speed_mps"], speed_mps
                )
                self.current["maximum_speed_mps"] = max(
                    self.current["maximum_speed_mps"], speed_mps
                )
                if directional_rate > self.current["peak_rate_rad_s"]:
                    self.current["peak_rate_rad_s"] = directional_rate
                    self.current["peak_time"] = t
                    self.current["peak_lat"] = lat
                    self.current["peak_lon"] = lon
        elif (
            self.current is not None
            and t - self.current["last_active"] > self.merge_gap_s
        ):
            self._finish()

        self.previous_t = t

    def finish(self) -> None:
        if self.current is not None:
            self._finish()

    def _finish(self) -> None:
        assert self.current is not None
        duration = self.current["last_active"] - self.current["start"]
        if (
            duration >= self.minimum_duration_s
            and self.current["positive_angle_rad"] >= self.minimum_angle_rad
        ):
            event = dict(self.current)
            event["end"] = event.pop("last_active")
            event["duration_s"] = duration
            event["positive_angle_deg"] = math.degrees(event.pop("positive_angle_rad"))
            event["net_angle_deg"] = math.degrees(event.pop("net_angle_rad"))
            event["peak_rate_deg_s"] = math.degrees(event.pop("peak_rate_rad_s"))
            self.events.append(event)
        self.current = None


def nearest_velocity(
    velocities: list[Velocity], velocity_times: list[float], t: float
) -> Velocity | None:
    if not velocities:
        return None
    index = bisect.bisect_left(velocity_times, t)
    candidates = []
    if index < len(velocities):
        candidates.append(velocities[index])
    if index:
        candidates.append(velocities[index - 1])
    return min(candidates, key=lambda item: abs(item.t - t))


def course_change_deg(
    velocities: list[Velocity],
    *,
    start: float,
    end: float,
    window_s: float = 2.5,
) -> float | None:
    before = [
        velocity.course_rad
        for velocity in velocities
        if start - window_s <= velocity.t < start and velocity.speed_mps >= 1.0
    ]
    after = [
        velocity.course_rad
        for velocity in velocities
        if end < velocity.t <= end + window_s and velocity.speed_mps >= 1.0
    ]
    before_mean = circular_mean(before)
    after_mean = circular_mean(after)
    if before_mean is None or after_mean is None:
        return None
    return math.degrees(wrap_radians(after_mean - before_mean))


def summarize_stops(fixes: list[Fix], velocities: list[Velocity]) -> dict[str, Any]:
    velocity_times = [sample.t for sample in velocities]
    stationary_groups: list[list[Fix]] = []
    current: list[Fix] = []

    for fix in fixes:
        velocity = nearest_velocity(velocities, velocity_times, fix.t)
        is_stationary = velocity is not None and velocity.speed_mps < 0.3
        contiguous = not current or fix.t - current[-1].t <= 0.75
        if is_stationary and contiguous:
            current.append(fix)
        else:
            if current and current[-1].t - current[0].t >= 5.0:
                stationary_groups.append(current)
            current = [fix] if is_stationary else []
    if current and current[-1].t - current[0].t >= 5.0:
        stationary_groups.append(current)

    stops: list[dict[str, Any]] = []
    for group in stationary_groups:
        center_lat = statistics.median(sample.lat for sample in group)
        center_lon = statistics.median(sample.lon for sample in group)
        distances = [
            local_distance_m(sample.lat, sample.lon, center_lat, center_lon)
            for sample in group
        ]
        stops.append(
            {
                "start_utc": iso_time(group[0].t),
                "duration_s": group[-1].t - group[0].t,
                "samples": len(group),
                "center_lat": center_lat,
                "center_lon": center_lon,
                "radial_jitter_p50_m": percentile(distances, 0.50),
                "radial_jitter_p95_m": percentile(distances, 0.95),
                "radial_jitter_max_m": max(distances),
            }
        )

    p95_values = [stop["radial_jitter_p95_m"] for stop in stops]
    max_values = [stop["radial_jitter_max_m"] for stop in stops]
    return {
        "definition": "speed < 0.3 m/s for at least 5 s",
        "stop_count": len(stops),
        "median_stop_duration_s": (
            statistics.median(stop["duration_s"] for stop in stops) if stops else None
        ),
        "median_of_stop_p95_jitter_m": (
            statistics.median(p95_values) if p95_values else None
        ),
        "p95_of_stop_p95_jitter_m": percentile(p95_values, 0.95),
        "maximum_observed_radial_jitter_m": max(max_values) if max_values else None,
        "stops": stops,
    }


def route_summary(fixes: list[Fix], velocities: list[Velocity]) -> dict[str, Any]:
    if not fixes:
        return {}
    velocity_times = [sample.t for sample in velocities]
    filtered_distance = 0.0
    for previous, current in itertools.pairwise(fixes):
        velocity = nearest_velocity(velocities, velocity_times, current.t)
        segment = haversine_m(previous.lat, previous.lon, current.lat, current.lon)
        if (
            current.t - previous.t <= 1.0
            and velocity is not None
            and velocity.speed_mps >= 0.5
            and segment <= 30.0
        ):
            filtered_distance += segment

    sigmas = [
        fix.sigma_horizontal_m for fix in fixes if fix.sigma_horizontal_m is not None
    ]
    track = []
    for index, fix in enumerate(fixes):
        if index % 4 == 0 or index == len(fixes) - 1:
            velocity = nearest_velocity(velocities, velocity_times, fix.t)
            track.append(
                {
                    "elapsed_s": fix.t - fixes[0].t,
                    "latitude": fix.lat,
                    "longitude": fix.lon,
                    "speed_mps": (velocity.speed_mps if velocity is not None else None),
                }
            )

    return {
        "start_utc": iso_time(fixes[0].t),
        "end_utc": iso_time(fixes[-1].t),
        "duration_s": fixes[-1].t - fixes[0].t,
        "samples": len(fixes),
        "bounding_box": {
            "south": min(fix.lat for fix in fixes),
            "west": min(fix.lon for fix in fixes),
            "north": max(fix.lat for fix in fixes),
            "east": max(fix.lon for fix in fixes),
        },
        "filtered_route_length_km": filtered_distance / 1000,
        "fix_status_counts": dict(sorted(Counter(fix.status for fix in fixes).items())),
        "fix_service_counts": dict(
            sorted(Counter(fix.service for fix in fixes).items())
        ),
        "covariance_type_counts": dict(
            sorted(Counter(fix.covariance_type for fix in fixes).items())
        ),
        "reported_horizontal_sigma_m": {
            "median": statistics.median(sigmas) if sigmas else None,
            "p95": percentile(sigmas, 0.95),
            "max": max(sigmas) if sigmas else None,
        },
        "satellite_count_available": False,
        "track_every_fourth_fix": track,
        "stationary_jitter": summarize_stops(fixes, velocities),
    }


def enrich_events(
    events: list[dict[str, Any]],
    *,
    recording_start: float,
    velocities: list[Velocity],
    object_frames: list[tuple[float, Counter[str]]],
) -> list[dict[str, Any]]:
    enriched = []
    for index, event in enumerate(events, start=1):
        nearby_frames = [
            labels
            for t, labels in object_frames
            if event["start"] - 2 <= t <= event["end"] + 2
        ]
        frames_with_vehicle = sum(
            1 for labels in nearby_frames if labels.get("VEHICLE", 0)
        )
        frames_with_person = sum(
            1 for labels in nearby_frames if labels.get("PERSON", 0)
        )
        result = {
            "id": index,
            "start_utc": iso_time(event["start"]),
            "end_utc": iso_time(event["end"]),
            "elapsed_minutes": (event["start"] - recording_start) / 60,
            "duration_s": event["duration_s"],
            "integrated_positive_yaw_deg": event["positive_angle_deg"],
            "integrated_net_yaw_deg": event["net_angle_deg"],
            "peak_yaw_rate_deg_s": event["peak_rate_deg_s"],
            "minimum_speed_mps": event["minimum_speed_mps"],
            "maximum_speed_mps": event["maximum_speed_mps"],
            "latitude": event["peak_lat"],
            "longitude": event["peak_lon"],
            "course_change_deg": course_change_deg(
                velocities, start=event["start"], end=event["end"]
            ),
            "object_frames_near_event": len(nearby_frames),
            "vehicle_frame_fraction": (
                frames_with_vehicle / len(nearby_frames) if nearby_frames else None
            ),
            "person_frame_fraction": (
                frames_with_person / len(nearby_frames) if nearby_frames else None
            ),
        }
        enriched.append(result)
    return enriched


def analyze_main(files: list[Path]) -> dict[str, Any]:
    fixes: list[Fix] = []
    velocities: list[Velocity] = []
    object_frames: list[tuple[float, Counter[str]]] = []
    object_labels: Counter[str] = Counter()
    object_message_count = 0
    frames_with_objects = 0
    imu_count = 0
    imu_rates: list[float] = []
    recording_start: float | None = None
    recording_end: float | None = None
    latest_speed = 0.0
    latest_lat: float | None = None
    latest_lon: float | None = None
    ema_yaw: float | None = None
    ema_t: float | None = None

    configurations = [
        (threshold, angle)
        for threshold in (0.04, 0.06, 0.08, 0.10)
        for angle in (20.0, 30.0, 45.0)
    ]
    detectors = {
        (direction, threshold, angle): TurnDetector(
            direction=direction,
            threshold_rad_s=threshold,
            minimum_angle_deg=angle,
        )
        for direction in (1, -1)
        for threshold, angle in configurations
    }

    for number, path in enumerate(files, start=1):
        print(f"[{number}/{len(files)}] {path.name}", flush=True)
        for decoded in read_ros2_messages(path, topics=TOPICS, log_time_order=False):
            t = decoded.log_time_ns / 1e9
            recording_start = t if recording_start is None else min(recording_start, t)
            recording_end = t if recording_end is None else max(recording_end, t)
            topic = decoded.channel.topic
            message = decoded.ros_msg

            if topic == FIX_TOPIC:
                covariance = message.position_covariance
                horizontal_variance = max(0.0, covariance[0], covariance[4])
                fixes.append(
                    Fix(
                        t=t,
                        lat=message.latitude,
                        lon=message.longitude,
                        altitude=message.altitude,
                        status=message.status.status,
                        service=message.status.service,
                        covariance_type=message.position_covariance_type,
                        sigma_horizontal_m=math.sqrt(horizontal_variance),
                    )
                )
                latest_lat = message.latitude
                latest_lon = message.longitude
            elif topic == VELOCITY_TOPIC:
                linear = message.twist.twist.linear
                latest_speed = math.hypot(linear.x, linear.y, linear.z)
                velocities.append(
                    Velocity(
                        t=t,
                        speed_mps=latest_speed,
                        course_rad=math.atan2(linear.y, linear.x),
                    )
                )
            elif topic == IMU_TOPIC:
                imu_count += 1
                raw_yaw = message.angular_velocity.z
                imu_rates.append(raw_yaw)
                if ema_yaw is None or ema_t is None or t - ema_t > 1.0:
                    ema_yaw = raw_yaw
                else:
                    dt = max(0.0, t - ema_t)
                    alpha = 1 - math.exp(-dt / 0.15)
                    ema_yaw += alpha * (raw_yaw - ema_yaw)
                ema_t = t
                for detector in detectors.values():
                    detector.feed(
                        t=t,
                        yaw_rate_rad_s=ema_yaw,
                        speed_mps=latest_speed,
                        lat=latest_lat,
                        lon=latest_lon,
                    )
            elif topic == OBJECTS_TOPIC:
                object_message_count += 1
                labels = Counter(obj.label for obj in message.objects)
                object_labels.update(labels)
                if labels:
                    frames_with_objects += 1
                object_frames.append((t, labels))

    for detector in detectors.values():
        detector.finish()

    assert recording_start is not None
    assert recording_end is not None
    velocities.sort(key=lambda sample: sample.t)
    fixes.sort(key=lambda sample: sample.t)
    object_frames.sort(key=lambda sample: sample[0])

    sensitivity = []
    for threshold, angle in configurations:
        sensitivity.append(
            {
                "threshold_rad_s": threshold,
                "minimum_angle_deg": angle,
                "positive_count": len(detectors[(1, threshold, angle)].events),
                "negative_count": len(detectors[(-1, threshold, angle)].events),
            }
        )

    canonical_positive = detectors[(1, 0.06, 20.0)].events
    canonical_negative = detectors[(-1, 0.06, 20.0)].events
    return {
        "files": [str(path) for path in files],
        "recording_start_utc": iso_time(recording_start),
        "recording_end_utc": iso_time(recording_end),
        "duration_s": recording_end - recording_start,
        "message_counts": {
            "fix": len(fixes),
            "velocity": len(velocities),
            "imu": imu_count,
            "objects": object_message_count,
        },
        "route": route_summary(fixes, velocities),
        "yaw_rate_rad_s": {
            "p01": percentile(imu_rates, 0.01),
            "p05": percentile(imu_rates, 0.05),
            "median": percentile(imu_rates, 0.50),
            "p95": percentile(imu_rates, 0.95),
            "p99": percentile(imu_rates, 0.99),
        },
        "turn_detection": {
            "method": {
                "smoothing": "EMA, 0.15 s time constant",
                "canonical_threshold_rad_s": 0.06,
                "canonical_minimum_angle_deg": 20.0,
                "speed_floor_mps": 0.5,
                "minimum_duration_s": 0.7,
                "merge_gap_s": 0.75,
            },
            "sensitivity": sensitivity,
            "positive_candidates": enrich_events(
                canonical_positive,
                recording_start=recording_start,
                velocities=velocities,
                object_frames=object_frames,
            ),
            "negative_candidates": enrich_events(
                canonical_negative,
                recording_start=recording_start,
                velocities=velocities,
                object_frames=object_frames,
            ),
        },
        "objects": {
            "message_count": object_message_count,
            "frames_with_objects": frames_with_objects,
            "frame_fraction_with_objects": (
                frames_with_objects / object_message_count
                if object_message_count
                else None
            ),
            "label_occurrences": dict(object_labels.most_common()),
        },
    }


def analyze_gnss_only(path: Path) -> dict[str, Any]:
    fixes: list[Fix] = []
    velocities: list[Velocity] = []
    first_t: float | None = None
    last_t: float | None = None
    topic_counts: Counter[str] = Counter()
    for decoded in read_ros2_messages(path, topics=[FIX_TOPIC, VELOCITY_TOPIC]):
        t = decoded.log_time_ns / 1e9
        first_t = t if first_t is None else min(first_t, t)
        last_t = t if last_t is None else max(last_t, t)
        topic = decoded.channel.topic
        topic_counts[topic] += 1
        message = decoded.ros_msg
        if topic == FIX_TOPIC:
            covariance = message.position_covariance
            horizontal_variance = max(0.0, covariance[0], covariance[4])
            fixes.append(
                Fix(
                    t=t,
                    lat=message.latitude,
                    lon=message.longitude,
                    altitude=message.altitude,
                    status=message.status.status,
                    service=message.status.service,
                    covariance_type=message.position_covariance_type,
                    sigma_horizontal_m=math.sqrt(horizontal_variance),
                )
            )
        else:
            linear = message.twist.twist.linear
            velocities.append(
                Velocity(
                    t=t,
                    speed_mps=math.hypot(linear.x, linear.y, linear.z),
                    course_rad=math.atan2(linear.y, linear.x),
                )
            )
    fixes.sort(key=lambda sample: sample.t)
    velocities.sort(key=lambda sample: sample.t)
    return {
        "file": str(path),
        "recording_start_utc": iso_time(first_t) if first_t is not None else None,
        "recording_end_utc": iso_time(last_t) if last_t is not None else None,
        "duration_s": (
            last_t - first_t if first_t is not None and last_t is not None else None
        ),
        "topic_counts": dict(topic_counts),
        "route": route_summary(fixes, velocities),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("recording_root", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    session_directory = args.recording_root / "rosbag2_2025_07_31-13_24_53"
    main_files = sorted(session_directory.glob("*.mcap"))
    standalone = args.recording_root / "rosbag2_2025_07_30-17_00_08_0.mcap"
    if len(main_files) != 9:
        raise SystemExit(f"Expected 9 main chunks, found {len(main_files)}")
    if not standalone.exists():
        raise SystemExit(f"Standalone bag not found: {standalone}")

    result = {
        "generated_utc": datetime.now(tz=timezone.utc).isoformat(),
        "main_session": analyze_main(main_files),
        "standalone_session": analyze_gnss_only(standalone),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")

    main_session = result["main_session"]
    print(f"Wrote {args.output}")
    print(
        "Canonical candidates:",
        len(main_session["turn_detection"]["positive_candidates"]),
        "positive /",
        len(main_session["turn_detection"]["negative_candidates"]),
        "negative",
    )
    print("Bounding box:", main_session["route"]["bounding_box"])


if __name__ == "__main__":
    main()
