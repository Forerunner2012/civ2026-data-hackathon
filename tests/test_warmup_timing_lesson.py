from __future__ import annotations

from pathlib import Path

import yaml

REPOSITORY = Path(__file__).parents[1]
SPEC_PATH = REPOSITORY / "examples" / "kashiwa" / "deceleration_timing.yaml"
ACCEPTANCE_PATH = REPOSITORY / "docs" / "phase4" / "warmup-timing-acceptance.md"


def test_warmup_timing_example_is_deliberately_non_answer() -> None:
    spec = yaml.safe_load(SPEC_PATH.read_text(encoding="utf-8"))

    assert spec["name"] == "kashiwa-warmup-loose-deceleration-example"
    assert spec["signals"] == {
        "longitudinal_acceleration": {
            "topic": "/localization/acceleration",
            "field": "accel.accel.linear.x",
        }
    }
    assert spec["condition"] == "longitudinal_acceleration <= -0.25"
    assert spec["timing"] == {
        "min_duration": "0.5s",
        "merge_gap": "0.5s",
        "max_duration": "10s",
    }
    public_text = (
        f"{SPEC_PATH.read_text(encoding='utf-8')}\n{ACCEPTANCE_PATH.read_text(encoding='utf-8')}"
    )
    forbidden = (
        "ground_truth",
        "hidden_evaluation",
        "label_pack",
        "organizer_path",
        "sealed_interval",
        "source_path",
    )
    for term in forbidden:
        assert term not in public_text.lower()


def test_warmup_timing_record_preserves_real_counts_failure_and_approval() -> None:
    record = ACCEPTANCE_PATH.read_text(encoding="utf-8")

    assert "Human organizer approval: **approved**" in record
    assert "| Condition matches | 189 |" in record
    assert "| Gap-merged candidates | 14 |" in record
    assert "| Duration-qualified events | 4 |" in record
    assert "illustrative `41 -> 6` did not reproduce" in record
    assert "brake-pedal maximum `0`" in record
    assert "timing` fixes over-counting" in record
