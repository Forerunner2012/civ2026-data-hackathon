from __future__ import annotations

import json
import os
from base64 import b64decode
from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as distribution_version
from pathlib import Path

import pytest

from civ_workshop.cli import main
from tests.helpers import (
    MicroCase,
    create_micro_case,
    run_civ,
    write_micro_bag,
    write_nested_json_bag,
    write_raw_schema_bag,
    write_ros2_nested_bag,
)


@pytest.fixture
def micro_case(tmp_path: Path) -> MicroCase:
    return create_micro_case(tmp_path)


def test_sample_emits_stable_bounded_json(micro_case: MicroCase) -> None:
    result = run_civ(
        micro_case.root,
        [
            "sample",
            str(micro_case.bag),
            "--topic",
            "/micro/signal",
            "--field",
            "value",
            "--start-ns",
            "1000000000",
            "--end-ns",
            "3000000000",
            "--limit",
            "2",
            "--json",
        ],
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout == (
        '{"bag":"micro.mcap","field":"value","samples":['
        '{"timestamp_ns":1000000000,"value":2.0},'
        '{"timestamp_ns":2000000000,"value":2.0}],'
        '"topic":"/micro/signal","window":'
        '{"end_ns":3000000000,"limit":2,"start_ns":1000000000}}\n'
    )


def test_sample_decodes_nested_ros2_field_and_renders_human_output(tmp_path: Path) -> None:
    bag = tmp_path / "nested.mcap"
    write_ros2_nested_bag(bag)

    result = run_civ(
        tmp_path,
        ["sample", str(bag), "--topic", "/ros2/turn", "--field", "turn.angular.z"],
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout == (
        "Bag: nested.mcap\n"
        "Signal: /ros2/turn.turn.angular.z\n"
        "Window: all timestamps, first 20 samples\n"
        "Samples:\n"
        "  1000000000 ns  -0.25\n"
    )


def test_sample_discovers_and_decodes_nested_json_field(tmp_path: Path) -> None:
    bag = tmp_path / "nested-json.mcap"
    write_nested_json_bag(bag)

    result = run_civ(
        tmp_path,
        [
            "sample",
            str(bag),
            "--topic",
            "/micro/pose",
            "--field",
            "pose.position.x",
            "--json",
        ],
    )

    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["samples"] == [
        {"timestamp_ns": 2_000_000_000, "value": 4.5}
    ]


@pytest.mark.parametrize(
    ("arguments", "diagnostic"),
    [
        (["--topic", "/absent", "--field", "value"], "topic not found in bag: /absent"),
        (
            ["--topic", "/micro/signal", "--field", "absent"],
            "field not found on topic /micro/signal: absent; run civ inspect",
        ),
        (
            ["--topic", "/micro/signal", "--field", "value", "--limit", "0"],
            "sample limit must be greater than zero",
        ),
        (
            ["--topic", "/micro/signal", "--field", "value", "--start-ns", "-1"],
            "sample start must be zero or greater",
        ),
        (
            [
                "--topic",
                "/micro/signal",
                "--field",
                "value",
                "--start-ns",
                "2",
                "--end-ns",
                "1",
            ],
            "sample start must be less than or equal to end",
        ),
        (
            [
                "--topic",
                "/micro/signal",
                "--field",
                "value",
                "--start-ns",
                "9000000000",
            ],
            "sample window contains no messages",
        ),
    ],
)
def test_sample_rejects_invalid_requests_actionably(
    micro_case: MicroCase, arguments: list[str], diagnostic: str
) -> None:
    result = run_civ(micro_case.root, ["sample", str(micro_case.bag), *arguments])

    assert result.returncode == 2
    assert diagnostic in result.stderr


def test_sample_preserves_explicit_ros2idl_unsupported_warning(tmp_path: Path) -> None:
    bag = tmp_path / "tier4.mcap"
    write_raw_schema_bag(
        bag,
        schema_encoding="ros2idl",
        message_encoding="cdr",
        schema_data=b"module tier4_msgs {};",
    )

    result = run_civ(
        tmp_path,
        ["sample", str(bag), "--topic", "/tier4/mode", "--field", "mode"],
    )

    assert result.returncode == 2
    assert (
        "field discovery unsupported for ros2idl on topic /tier4/mode; "
        "dynamic IDL decoding remains unsupported"
    ) in result.stderr


def test_inspect_warns_when_golden_path_schema_hash_mismatches(tmp_path: Path) -> None:
    bag = tmp_path / "mismatched-steering.mcap"
    write_raw_schema_bag(
        bag,
        schema_encoding="ros2msg",
        message_encoding="cdr",
        schema_data=b"int32 vcu_chassis_steer_angle_fb\n",
        schema_name="pix_hooke_driver_msgs/msg/V2aSteerStaFb",
        topic="/pix_hooke/v2a_steerstafb",
    )

    result = run_civ(tmp_path, ["inspect", str(bag), "--json"])

    assert result.returncode == 0, result.stderr
    warnings = json.loads(result.stdout)["warnings"]
    assert len(warnings) == 1
    assert "embedded schema hash mismatch" in warnings[0]
    assert (
        "expected 4c3724cf5ee83ef9cbd127585519e80c7828341fcd626d4d588d22d406918eea"
        in warnings[0]
    )


def test_inspect_accepts_exact_embedded_golden_path_schema_fixture(tmp_path: Path) -> None:
    bag = tmp_path / "pinned-imu.mcap"
    fixture = Path(__file__).parent / "fixtures" / "schemas" / "reims-imu.ros2msg.b64"
    schema_data = b64decode(fixture.read_text(encoding="ascii"))
    write_raw_schema_bag(
        bag,
        schema_encoding="ros2msg",
        message_encoding="cdr",
        schema_data=schema_data,
        schema_name="sensor_msgs/msg/Imu",
        topic="/zed/zed_node/imu/data",
    )

    result = run_civ(tmp_path, ["inspect", str(bag), "--json"])

    assert result.returncode == 0, result.stderr
    inventory = json.loads(result.stdout)
    assert inventory["warnings"] == []
    assert inventory["topics"][0]["schema_sha256"] == (
        "244d9e9566de33e36bf560d79a41a17d1a1b44c49bdaf2bd809aa7efb1389334"
    )
    assert "angular_velocity.z" in inventory["topics"][0]["fields"]


def test_sample_rejects_unknown_schema_on_pinned_golden_path_topic(tmp_path: Path) -> None:
    bag = tmp_path / "unknown-steering.mcap"
    write_raw_schema_bag(
        bag,
        schema_encoding="ros2msg",
        message_encoding="cdr",
        schema_data=b"int32 angle\n",
        schema_name="other_msgs/msg/Steering",
        topic="/pix_hooke/v2a_steerstafb",
    )

    result = run_civ(
        tmp_path,
        [
            "sample",
            str(bag),
            "--topic",
            "/pix_hooke/v2a_steerstafb",
            "--field",
            "angle",
        ],
    )

    assert result.returncode == 2
    assert "unknown golden-path schema other_msgs/msg/Steering (ros2msg)" in result.stderr
    assert "use the pinned golden-path bag/schema source" in result.stderr


def _doctor_fixture(tmp_path: Path) -> tuple[Path, Path, Path, dict[str, str]]:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    bag = tmp_path / "sample.mcap"
    write_micro_bag(bag)
    layout = tmp_path / "signals.xml"
    layout.write_text("<root />\n", encoding="utf-8")
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    viewer = bin_dir / ("plotjuggler.EXE" if os.name == "nt" else "plotjuggler")
    viewer.write_text("#!/bin/sh\n", encoding="utf-8")
    viewer.chmod(0o755)
    env = {
        "PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}",
        "ROS_DISTRO": "lyrical",
    }
    return workspace, bag, layout, env


def test_doctor_pure_mcap_profile_passes_without_ros_layout_or_viewer(
    tmp_path: Path,
) -> None:
    workspace, bag, _, _ = _doctor_fixture(tmp_path)
    empty_path = tmp_path / "empty-bin"
    empty_path.mkdir()
    repo = Path(__file__).parents[1]

    result = run_civ(
        tmp_path,
        [
            "doctor",
            "--workspace",
            str(workspace),
            "--bag",
            str(bag),
            "--offline-kit",
            str(repo),
            "--json",
        ],
        env={"PATH": str(empty_path), "ROS_DISTRO": ""},
    )

    assert result.returncode == 0, result.stdout
    report = json.loads(result.stdout)
    assert report["profile"] == "pure-mcap"
    assert report["ok"] is True
    checks = {check["name"]: check for check in report["checks"]}
    assert checks["ros"]["required"] is False
    assert checks["ros"]["status"] == "warn"
    assert checks["visualization"]["required"] is False
    assert checks["visualization"]["status"] == "warn"


def test_doctor_release_target_rejects_wrong_platform_ros_and_visualization(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    workspace, bag, _, _ = _doctor_fixture(tmp_path)
    repo = Path(__file__).parents[1]
    monkeypatch.setattr("civ_workshop.doctor.platform.system", lambda: "Windows")
    monkeypatch.setattr("civ_workshop.doctor.platform.release", lambda: "11")
    monkeypatch.setattr("civ_workshop.doctor.platform.machine", lambda: "AMD64")
    monkeypatch.setattr("civ_workshop.doctor.shutil.which", lambda _command: None)
    monkeypatch.delenv("ROS_DISTRO", raising=False)

    with pytest.raises(SystemExit) as exit_info:
        main(
            [
                "doctor",
                "--profile",
                "release-target",
                "--workspace",
                str(workspace),
                "--bag",
                str(bag),
                "--offline-kit",
                str(repo),
                "--json",
            ]
        )

    assert exit_info.value.code == 2
    report = json.loads(capsys.readouterr().out)
    failed = {
        check["name"]: check
        for check in report["checks"]
        if check["required"] and check["status"] == "fail"
    }
    assert set(failed) == {"ros", "platform", "visualization"}
    assert all(check["action"] for check in failed.values())


def test_doctor_release_target_accepts_lichtblick_without_plotjuggler_layout(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    workspace, bag, _, _ = _doctor_fixture(tmp_path)
    repo = Path(__file__).parents[1]
    monkeypatch.setattr("civ_workshop.doctor.platform.system", lambda: "Linux")
    monkeypatch.setattr("civ_workshop.doctor.platform.release", lambda: "6.17")
    monkeypatch.setattr("civ_workshop.doctor.platform.machine", lambda: "x86_64")
    monkeypatch.setattr(
        "civ_workshop.doctor.platform.freedesktop_os_release",
        lambda: {"ID": "ubuntu", "VERSION_ID": "26.04"},
    )
    monkeypatch.setattr(
        "civ_workshop.doctor.shutil.which",
        lambda command: "/opt/lichtblick/lichtblick" if command == "lichtblick" else None,
    )
    monkeypatch.setenv("ROS_DISTRO", "lyrical")

    main(
        [
            "doctor",
            "--profile",
            "release-target",
            "--workspace",
            str(workspace),
            "--bag",
            str(bag),
            "--offline-kit",
            str(repo),
            "--json",
        ]
    )

    report = json.loads(capsys.readouterr().out)
    assert report["ok"] is True
    checks = {check["name"]: check for check in report["checks"]}
    assert checks["platform"]["required"] is True
    assert checks["visualization"] == {
        "action": None,
        "detail": "Lichtblick at /opt/lichtblick/lichtblick",
        "name": "visualization",
        "required": True,
        "status": "pass",
    }


def test_doctor_windows_pure_mcap_keeps_platform_nonblocking(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    workspace, bag, _, _ = _doctor_fixture(tmp_path)
    repo = Path(__file__).parents[1]
    monkeypatch.setattr("civ_workshop.doctor.platform.system", lambda: "Windows")
    monkeypatch.setattr("civ_workshop.doctor.platform.release", lambda: "11")
    monkeypatch.setattr("civ_workshop.doctor.platform.machine", lambda: "AMD64")
    monkeypatch.setattr("civ_workshop.doctor.shutil.which", lambda _command: None)
    monkeypatch.delenv("ROS_DISTRO", raising=False)

    main(
        [
            "doctor",
            "--workspace",
            str(workspace),
            "--bag",
            str(bag),
            "--offline-kit",
            str(repo),
            "--json",
        ]
    )

    report = json.loads(capsys.readouterr().out)
    assert report["ok"] is True
    checks = {check["name"]: check for check in report["checks"]}
    assert checks["platform"]["required"] is False
    assert checks["platform"]["status"] == "pass"
    assert checks["platform"]["detail"].startswith("Windows 11 AMD64;")


def test_doctor_rejects_unsupported_python_through_public_cli(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    workspace, bag, _, _ = _doctor_fixture(tmp_path)
    repo = Path(__file__).parents[1]
    monkeypatch.setattr("civ_workshop.doctor.sys.version_info", (3, 13, 0))
    monkeypatch.setattr("civ_workshop.doctor.platform.python_version", lambda: "3.13.0")

    with pytest.raises(SystemExit) as exit_info:
        main(
            [
                "doctor",
                "--workspace",
                str(workspace),
                "--bag",
                str(bag),
                "--offline-kit",
                str(repo),
            ]
        )

    assert exit_info.value.code == 2
    output = capsys.readouterr().out
    assert "[FAIL] python: CPython 3.13.0" in output
    assert "install and run civ with CPython 3.10, 3.11, or 3.12" in output


def test_doctor_rejects_structurally_invalid_mcap_through_public_cli(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    workspace, bag, _, _ = _doctor_fixture(tmp_path)
    bag.write_bytes(b"not an mcap")
    repo = Path(__file__).parents[1]
    monkeypatch.setattr("civ_workshop.doctor.shutil.which", lambda _command: None)

    with pytest.raises(SystemExit) as exit_info:
        main(
            [
                "doctor",
                "--workspace",
                str(workspace),
                "--bag",
                str(bag),
                "--offline-kit",
                str(repo),
            ]
        )

    assert exit_info.value.code == 2
    output = capsys.readouterr().out
    assert "[FAIL] bag: invalid MCAP opening or closing magic" in output
    assert "pass a structurally valid MCAP file with --bag" in output


def test_doctor_pure_mcap_passes_with_plotjuggler_visualization_route(
    tmp_path: Path,
) -> None:
    workspace, bag, layout, env = _doctor_fixture(tmp_path)
    repo = Path(__file__).parents[1]

    result = run_civ(
        tmp_path,
        [
            "doctor",
            "--workspace",
            str(workspace),
            "--bag",
            str(bag),
            "--layout",
            str(layout),
            "--offline-kit",
            str(repo),
            "--json",
        ],
        env=env,
    )

    assert result.returncode == 0, result.stderr
    report = json.loads(result.stdout)
    assert report["ok"] is True
    assert [check["name"] for check in report["checks"]] == [
        "python",
        "dependencies",
        "ros",
        "workspace",
        "bag",
        "offline-kit",
        "platform",
        "visualization",
    ]
    assert all(
        check["status"] == "pass" for check in report["checks"] if check["required"]
    )
    visualization = report["checks"][-1]
    assert visualization["required"] is False
    assert visualization["status"] == "pass"
    assert "PlotJuggler with" in visualization["detail"]


def test_doctor_fails_required_checks_with_corrective_actions(tmp_path: Path) -> None:
    empty_path = tmp_path / "empty-bin"
    empty_path.mkdir()

    result = run_civ(
        tmp_path,
        [
            "doctor",
            "--workspace",
            str(tmp_path / "missing-workspace"),
            "--bag",
            str(tmp_path / "missing.mcap"),
            "--layout",
            str(tmp_path / "missing.xml"),
            "--offline-kit",
            str(tmp_path / "missing-kit"),
        ],
        env={"PATH": str(empty_path), "ROS_DISTRO": "humble"},
    )

    assert result.returncode == 2
    assert "Doctor: FAILED" in result.stdout
    assert "Profile: pure-mcap" in result.stdout
    assert "[WARN] ros:" in result.stdout
    assert "source ROS 2 Lyrical when checking the release target" in result.stdout
    assert "[FAIL] workspace:" in result.stdout
    assert "create the workspace directory" in result.stdout
    assert "[FAIL] bag:" in result.stdout
    assert "pass an existing MCAP file with --bag" in result.stdout
    assert "[FAIL] offline-kit:" in result.stdout
    assert "run from the unpacked offline kit or pass --offline-kit" in result.stdout
    assert "[WARN] visualization:" in result.stdout
    assert "install Lichtblick, or install PlotJuggler and pass its layout" in result.stdout


def test_doctor_rejects_missing_dependency_through_public_cli(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    workspace, bag, layout, _ = _doctor_fixture(tmp_path)
    repo = Path(__file__).parents[1]

    def missing_dependency(package: str) -> str:
        if package == "mcap":
            raise PackageNotFoundError(package)
        return distribution_version(package)

    monkeypatch.setattr("civ_workshop.doctor.version", missing_dependency)
    monkeypatch.setattr("civ_workshop.doctor.shutil.which", lambda _command: "viewer")
    monkeypatch.setenv("ROS_DISTRO", "lyrical")

    with pytest.raises(SystemExit) as exit_info:
        main(
            [
                "doctor",
                "--workspace",
                str(workspace),
                "--bag",
                str(bag),
                "--layout",
                str(layout),
                "--offline-kit",
                str(repo),
            ]
        )

    assert exit_info.value.code == 2
    output = capsys.readouterr().out
    assert "[FAIL] dependencies: mcap is missing" in output
    assert "restore the pinned offline environment with uv sync --frozen" in output


def test_doctor_rejects_unwritable_workspace_through_public_cli(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    workspace, bag, layout, _ = _doctor_fixture(tmp_path)
    repo = Path(__file__).parents[1]

    monkeypatch.setattr("civ_workshop.doctor.os.access", lambda _path, _mode: False)
    monkeypatch.setattr("civ_workshop.doctor.shutil.which", lambda _command: "viewer")
    monkeypatch.setenv("ROS_DISTRO", "lyrical")

    with pytest.raises(SystemExit) as exit_info:
        main(
            [
                "doctor",
                "--workspace",
                str(workspace),
                "--bag",
                str(bag),
                "--layout",
                str(layout),
                "--offline-kit",
                str(repo),
            ]
        )

    assert exit_info.value.code == 2
    output = capsys.readouterr().out
    assert "[FAIL] workspace: not writable:" in output
    assert "choose a writable directory and pass it with --workspace" in output
