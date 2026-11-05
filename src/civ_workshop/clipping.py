from __future__ import annotations

from pathlib import Path

from mcap.exceptions import McapError
from mcap.reader import make_reader
from mcap.writer import CompressionType, Writer

from civ_workshop.artifacts import (
    canonical_json,
    file_sha256,
    read_events,
    read_json_file,
    require_mapping,
    require_string,
)
from civ_workshop.contracts import require_run_contracts
from civ_workshop.errors import CivError
from civ_workshop.models import Interval


def _write_clip(
    bag_path: Path,
    clip_path: Path,
    topics: list[str],
    requested: Interval,
) -> tuple[Interval, list[str]]:
    clip_path.parent.mkdir(parents=True, exist_ok=True)
    actual_start: int | None = None
    actual_end: int | None = None
    actual_topics: set[str] = set()
    try:
        with bag_path.open("rb") as source, clip_path.open("wb") as destination:
            reader = make_reader(source, validate_crcs=True)
            header = reader.get_header()
            writer = Writer(destination, compression=CompressionType.NONE)
            writer.start(profile=header.profile, library="civ-workshop/0.1.0")
            schema_ids: dict[int, int] = {}
            channel_ids: dict[int, int] = {}
            for schema, channel, message in reader.iter_messages(
                topics=topics,
                start_time=requested.start_ns,
                end_time=requested.end_ns,
            ):
                output_schema_id = 0
                if schema is not None:
                    output_schema_id = schema_ids.get(schema.id, 0)
                    if not output_schema_id:
                        output_schema_id = writer.register_schema(
                            name=schema.name,
                            encoding=schema.encoding,
                            data=schema.data,
                        )
                        schema_ids[schema.id] = output_schema_id
                output_channel_id = channel_ids.get(channel.id)
                if output_channel_id is None:
                    output_channel_id = writer.register_channel(
                        schema_id=output_schema_id,
                        topic=channel.topic,
                        message_encoding=channel.message_encoding,
                        metadata=channel.metadata,
                    )
                    channel_ids[channel.id] = output_channel_id
                writer.add_message(
                    channel_id=output_channel_id,
                    log_time=message.log_time,
                    publish_time=message.publish_time,
                    sequence=message.sequence,
                    data=message.data,
                )
                actual_start = (
                    message.log_time
                    if actual_start is None
                    else min(actual_start, message.log_time)
                )
                actual_end = (
                    message.log_time if actual_end is None else max(actual_end, message.log_time)
                )
                actual_topics.add(channel.topic)
            writer.finish()
    except (OSError, McapError) as error:
        raise CivError(f"cannot extract clip {clip_path.name}: {error}") from error

    if actual_start is None or actual_end is None:
        raise CivError(
            f"clip window {requested.start_ns}..{requested.end_ns} contains no requested messages"
        )
    missing_topics = sorted(set(topics) - actual_topics)
    if missing_topics:
        raise CivError(f"clip is missing requested topics: {', '.join(missing_topics)}")
    try:
        with clip_path.open("rb") as stream:
            list(make_reader(stream, validate_crcs=True).iter_messages())
    except (OSError, McapError) as error:
        raise CivError(f"extracted clip is not valid MCAP: {clip_path}") from error
    return Interval(actual_start, actual_end), sorted(actual_topics)


def clip_events(events_path: Path, bag_path: Path) -> dict[str, object]:
    if not bag_path.is_file():
        raise CivError(f"bag does not exist: {bag_path}")
    working = events_path.parent
    events = read_events(events_path)
    manifest_path = working / "run-manifest.json"
    manifest = read_json_file(manifest_path, "run manifest")
    require_run_contracts(manifest, [event.contract for event in events])

    source = require_mapping(manifest.get("source"), "run manifest source")
    expected_bag_hash = require_string(source.get("sha256"), "run manifest source sha256")
    bag_hash = file_sha256(bag_path)
    if bag_hash != expected_bag_hash:
        raise CivError("dataset hash does not match the run manifest")
    evidence = require_mapping(manifest.get("evidence"), "run manifest evidence")
    before_ns = evidence.get("before_ns")
    after_ns = evidence.get("after_ns")
    raw_topics = evidence.get("topics")
    if (
        not isinstance(before_ns, int)
        or isinstance(before_ns, bool)
        or before_ns < 0
        or not isinstance(after_ns, int)
        or isinstance(after_ns, bool)
        or after_ns < 0
    ):
        raise CivError(
            "run manifest evidence window must contain non-negative integers, not booleans"
        )
    if not isinstance(raw_topics, list) or not raw_topics:
        raise CivError("run manifest evidence topics are invalid")
    topics = sorted(require_string(topic, "run manifest evidence topic") for topic in raw_topics)

    clips: list[dict[str, object]] = []
    for event in events:
        requested = Interval(
            max(0, event.interval.start_ns - before_ns),
            event.interval.end_ns + after_ns,
        )
        relative_name = f"evidence/{event.event_id}.mcap"
        clip_path = working / Path(relative_name)
        actual, actual_topics = _write_clip(bag_path, clip_path, topics, requested)
        clips.append(
            {
                "actual_end_ns": actual.end_ns,
                "actual_start_ns": actual.start_ns,
                "event_id": event.event_id,
                "input_bytes": bag_path.stat().st_size,
                "name": relative_name,
                "output_bytes": clip_path.stat().st_size,
                "requested_end_ns": requested.end_ns,
                "requested_start_ns": requested.start_ns,
                "sha256": file_sha256(clip_path),
                "topics": actual_topics,
                "valid": True,
            }
        )

    manifest["clips"] = clips
    manifest_path.write_text(f"{canonical_json(manifest)}\n", encoding="utf-8", newline="\n")
    return {"clip_count": len(clips)}
