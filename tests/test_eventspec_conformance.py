from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
import yaml
from mcap.writer import CompressionType, Writer

from tests.helpers import run_civ

CONFORMANCE_PATH = Path(__file__).parent / "fixtures" / "cel" / "conformance.yaml"


def _conformance_cases() -> list[dict[str, Any]]:
    document = yaml.safe_load(CONFORMANCE_PATH.read_text(encoding="utf-8"))
    assert document["runtime"] == "cel-python==0.5.0"
    return list(document["cases"])


def _write_conformance_bag(path: Path, messages: list[dict[str, object]]) -> None:
    with path.open("wb") as stream:
        writer = Writer(stream, compression=CompressionType.NONE)
        writer.start(profile="civ.cel-conformance", library="human-authored-conformance")
        schema_id = writer.register_schema(
            name="civ.conformance.Signals",
            encoding="jsonschema",
            data=b'{"type":"object"}',
        )
        channel_id = writer.register_channel(
            schema_id=schema_id,
            topic="/conformance",
            message_encoding="json",
        )
        for second, message in enumerate(messages):
            timestamp = second * 1_000_000_000
            writer.add_message(
                channel_id=channel_id,
                log_time=timestamp,
                publish_time=timestamp,
                data=json.dumps(message, allow_nan=False, sort_keys=True).encode(),
            )
        writer.finish()


@pytest.mark.parametrize("case", _conformance_cases(), ids=lambda case: str(case["name"]))
def test_human_authored_cel_conformance_through_public_detect(
    case: dict[str, Any], tmp_path: Path
) -> None:
    messages = list(case["messages"])
    signal_names = list(messages[0])
    bag = tmp_path / "conformance.mcap"
    spec = tmp_path / "conformance.yaml"
    output = tmp_path / "working"
    _write_conformance_bag(bag, messages)
    bindings = "\n".join(
        f"  {name}: {{topic: /conformance, field: {name}}}" for name in signal_names
    )
    spec.write_text(
        "spec: civ.eventspec/v1\n"
        f"name: {case['name']}\n"
        "signals:\n"
        f"{bindings}\n"
        f"condition: {case['condition']}\n"
        "timing:\n"
        "  min_duration: 1s\n"
        "  merge_gap: 1.1s\n"
        "  max_duration: 10s\n"
        "evidence:\n"
        "  before: 0s\n"
        "  after: 0s\n"
        "  topics: [/conformance]\n",
        encoding="utf-8",
    )

    result = run_civ(tmp_path, ["detect", str(spec), str(bag), "--output", str(output)])

    assert result.returncode == 0, result.stderr
    event = json.loads((output / "events.jsonl").read_text(encoding="utf-8"))
    assert [event["start_ns"], event["end_ns"]] == case["expected_interval_ns"]


def test_cel_rejects_null_signal_values_with_a_stable_correction(tmp_path: Path) -> None:
    bag = tmp_path / "null.mcap"
    spec = tmp_path / "null.yaml"
    _write_conformance_bag(bag, [{"optional": None}])
    spec.write_text(
        """\
spec: civ.eventspec/v1
name: null-input
signals:
  optional: {topic: /conformance, field: optional}
condition: optional == null
timing: {min_duration: 0s, merge_gap: 0s, max_duration: 1s}
evidence: {before: 0s, after: 0s, topics: [/conformance]}
""",
        encoding="utf-8",
    )

    result = run_civ(tmp_path, ["detect", str(spec), str(bag)])

    assert result.returncode == 2
    assert result.stderr == (
        "civ: CEL input 'optional' is null at 0 ns; bind a non-null field or derive a fallback\n"
    )


def test_cel_rejects_implicit_integer_double_coercion(tmp_path: Path) -> None:
    bag = tmp_path / "mixed-numeric.mcap"
    spec = tmp_path / "mixed-numeric.yaml"
    _write_conformance_bag(bag, [{"count": 2}])
    spec.write_text(
        """\
spec: civ.eventspec/v1
name: mixed-numeric
signals:
  count: {topic: /conformance, field: count}
condition: count >= 2.0
timing: {min_duration: 0s, merge_gap: 0s, max_duration: 1s}
evidence: {before: 0s, after: 0s, topics: [/conformance]}
""",
        encoding="utf-8",
    )

    result = run_civ(tmp_path, ["detect", str(spec), str(bag)])

    assert result.returncode == 2
    assert result.stderr == (
        "civ: CEL type error at 0 ns: int and double are not implicitly coerced; "
        "use int(...) or double(...) explicitly\n"
    )


def test_cel_rejects_missing_names_with_a_stable_correction(tmp_path: Path) -> None:
    bag = tmp_path / "missing.mcap"
    spec = tmp_path / "missing.yaml"
    _write_conformance_bag(bag, [{"present": 1}])
    spec.write_text(
        """\
spec: civ.eventspec/v1
name: missing-name
signals:
  present: {topic: /conformance, field: present}
condition: missing > 0
timing: {min_duration: 0s, merge_gap: 0s, max_duration: 1s}
evidence: {before: 0s, after: 0s, topics: [/conformance]}
""",
        encoding="utf-8",
    )

    result = run_civ(tmp_path, ["detect", str(spec), str(bag)])

    assert result.returncode == 2
    assert result.stderr == (
        "civ: CEL condition references unknown name 'missing' at 0 ns; "
        "bind it under signals or derive\n"
    )


def test_cel_condition_must_return_boolean(tmp_path: Path) -> None:
    bag = tmp_path / "non-boolean.mcap"
    spec = tmp_path / "non-boolean.yaml"
    _write_conformance_bag(bag, [{"count": 2}])
    spec.write_text(
        """\
spec: civ.eventspec/v1
name: non-boolean
signals:
  count: {topic: /conformance, field: count}
condition: count + 1
timing: {min_duration: 0s, merge_gap: 0s, max_duration: 1s}
evidence: {before: 0s, after: 0s, topics: [/conformance]}
""",
        encoding="utf-8",
    )

    result = run_civ(tmp_path, ["detect", str(spec), str(bag)])

    assert result.returncode == 2
    assert result.stderr == (
        "civ: CEL condition returned int at 0 ns; make the condition return bool\n"
    )


def test_cel_rejects_boolean_integer_equality_runtime_divergence(tmp_path: Path) -> None:
    bag = tmp_path / "mixed-equality.mcap"
    spec = tmp_path / "mixed-equality.yaml"
    _write_conformance_bag(bag, [{"count": 1}])
    spec.write_text(
        """\
spec: civ.eventspec/v1
name: mixed-equality
signals:
  count: {topic: /conformance, field: count}
condition: count == true
timing: {min_duration: 0s, merge_gap: 0s, max_duration: 1s}
evidence: {before: 0s, after: 0s, topics: [/conformance]}
""",
        encoding="utf-8",
    )

    result = run_civ(tmp_path, ["detect", str(spec), str(bag)])

    assert result.returncode == 2
    assert result.stderr == (
        "civ: CEL type error at 0 ns: 'count' must be bool when compared with true; "
        "use an explicit numeric comparison\n"
    )


def test_cel_rejects_division_outside_the_frozen_operator_subset(
    tmp_path: Path,
) -> None:
    bag = tmp_path / "divide-zero.mcap"
    spec = tmp_path / "divide-zero.yaml"
    _write_conformance_bag(bag, [{"count": 2}])
    spec.write_text(
        """\
spec: civ.eventspec/v1
name: divide-zero
signals:
  count: {topic: /conformance, field: count}
condition: (count / 0) > 1
timing: {min_duration: 0s, merge_gap: 0s, max_duration: 1s}
evidence: {before: 0s, after: 0s, topics: [/conformance]}
""",
        encoding="utf-8",
    )

    result = run_civ(tmp_path, ["detect", str(spec), str(bag)])

    assert result.returncode == 2
    assert result.stderr == (
        "civ: CEL operator '/' is not supported; use +, -, *, comparisons, or derive\n"
    )


def test_cel_parse_error_has_deterministic_location_and_correction(tmp_path: Path) -> None:
    bag = tmp_path / "parse-error.mcap"
    spec = tmp_path / "parse-error.yaml"
    _write_conformance_bag(bag, [{"signal": 2.0}])
    spec.write_text(
        """\
spec: civ.eventspec/v1
name: parse-error
signals:
  signal: {topic: /conformance, field: signal}
condition: signal >
timing: {min_duration: 0s, merge_gap: 0s, max_duration: 1s}
evidence: {before: 0s, after: 0s, topics: [/conformance]}
""",
        encoding="utf-8",
    )

    result = run_civ(tmp_path, ["detect", str(spec), str(bag)])

    assert result.returncode == 2
    assert result.stderr == (
        "civ: invalid CEL condition at line 1, column 8; correct the expression syntax\n"
    )


def test_cel_rejects_values_outside_the_frozen_scalar_types(tmp_path: Path) -> None:
    bag = tmp_path / "string.mcap"
    spec = tmp_path / "string.yaml"
    _write_conformance_bag(bag, [{"label": "turn"}])
    spec.write_text(
        """\
spec: civ.eventspec/v1
name: string-input
signals:
  label: {topic: /conformance, field: label}
condition: label == "turn"
timing: {min_duration: 0s, merge_gap: 0s, max_duration: 1s}
evidence: {before: 0s, after: 0s, topics: [/conformance]}
""",
        encoding="utf-8",
    )

    result = run_civ(tmp_path, ["detect", str(spec), str(bag)])

    assert result.returncode == 2
    assert result.stderr == (
        "civ: CEL input 'label' has unsupported type string at 0 ns; "
        "bind a bool, int, or finite double\n"
    )


@pytest.mark.parametrize(
    ("condition", "diagnostic"),
    [
        (
            "count % 2 == 0",
            "CEL operator '%' is not supported; use +, -, *, comparisons, or derive",
        ),
        (
            "count in 1",
            "CEL operator 'in' is not supported; use logical and scalar comparison operators",
        ),
        (
            "count > 0 ? true : false",
            "CEL operator '?:' is not supported; express the decision with &&, ||, and !",
        ),
        (
            "size(count) > 0",
            "CEL function 'size' is not supported; use only int(...) or double(...) conversions",
        ),
    ],
)
def test_cel_rejects_operators_and_functions_outside_the_frozen_subset(
    condition: str, diagnostic: str, tmp_path: Path
) -> None:
    bag = tmp_path / "unsupported.mcap"
    spec = tmp_path / "unsupported.yaml"
    _write_conformance_bag(bag, [{"count": 2}])
    spec.write_text(
        "spec: civ.eventspec/v1\n"
        "name: unsupported-cel\n"
        "signals:\n"
        "  count: {topic: /conformance, field: count}\n"
        f"condition: {json.dumps(condition)}\n"
        "timing: {min_duration: 0s, merge_gap: 0s, max_duration: 1s}\n"
        "evidence: {before: 0s, after: 0s, topics: [/conformance]}\n",
        encoding="utf-8",
    )

    result = run_civ(tmp_path, ["detect", str(spec), str(bag)])

    assert result.returncode == 2
    assert result.stderr == f"civ: {diagnostic}\n"
