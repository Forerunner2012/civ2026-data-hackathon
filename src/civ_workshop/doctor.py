from __future__ import annotations

import os
import platform
import re
import shutil
import sys
from contextlib import suppress
from dataclasses import asdict, dataclass
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class DoctorCheck:
    name: str
    status: str
    required: bool
    detail: str
    action: str | None = None


REQUIRED_DEPENDENCIES = (
    ("cel-python", (0, 5, 0), (0, 5, 1), "0.5.0"),
    ("civ-workshop", (0, 1, 0), None, ">=0.1.0"),
    ("mcap", (1, 4, 0), (2, 0, 0), ">=1.4.0,<2"),
    ("mcap-ros2-support", (0, 5, 7), (0, 6, 0), ">=0.5.7,<0.6"),
    ("PyYAML", (6, 0, 2), (7, 0, 0), ">=6.0.2,<7"),
)
MCAP_MAGIC = b"\x89MCAP0\r\n"


def _version_tuple(raw_version: str) -> tuple[int, ...]:
    match = re.match(r"^(\d+)(?:\.(\d+))?(?:\.(\d+))?", raw_version)
    if match is None:
        return ()
    return tuple(int(part or 0) for part in match.groups())


def _python_check() -> DoctorCheck:
    current = sys.version_info[:3]
    supported = (3, 10) <= current[:2] < (3, 13)
    return DoctorCheck(
        name="python",
        status="pass" if supported else "fail",
        required=True,
        detail=f"CPython {platform.python_version()} (required >=3.10,<3.13)",
        action=None if supported else "install and run civ with CPython 3.10, 3.11, or 3.12",
    )


def _dependency_check() -> DoctorCheck:
    installed: list[str] = []
    problems: list[str] = []
    for package, minimum, maximum, requirement in REQUIRED_DEPENDENCIES:
        try:
            installed_version = version(package)
        except PackageNotFoundError:
            problems.append(f"{package} is missing")
            continue
        installed.append(f"{package} {installed_version}")
        parsed = _version_tuple(installed_version)
        if not parsed or parsed < minimum or (maximum is not None and parsed >= maximum):
            problems.append(f"{package} {installed_version} does not satisfy {requirement}")
    return DoctorCheck(
        name="dependencies",
        status="fail" if problems else "pass",
        required=True,
        detail="; ".join(problems if problems else installed),
        action=(
            "restore the pinned offline environment with uv sync --frozen"
            if problems
            else None
        ),
    )


def _path_check(
    name: str,
    path: Path | None,
    *,
    kind: str,
    missing_action: str,
) -> DoctorCheck:
    exists = path is not None and (path.is_dir() if kind == "directory" else path.is_file())
    detail = (
        str(path.resolve())
        if exists and path is not None
        else f"missing: {path or 'not provided'}"
    )
    return DoctorCheck(
        name=name,
        status="pass" if exists else "fail",
        required=True,
        detail=detail,
        action=None if exists else missing_action,
    )


def _bag_check(path: Path | None) -> DoctorCheck:
    existing = _path_check(
        "bag",
        path,
        kind="file",
        missing_action="pass an existing MCAP file with --bag",
    )
    if existing.status == "fail" or path is None:
        return existing
    try:
        with path.open("rb") as stream:
            opening_magic = stream.read(len(MCAP_MAGIC))
            stream.seek(-len(MCAP_MAGIC), os.SEEK_END)
            closing_magic = stream.read(len(MCAP_MAGIC))
    except (OSError, ValueError) as error:
        return DoctorCheck(
            name="bag",
            status="fail",
            required=True,
            detail=f"cannot read MCAP structure: {error}",
            action="pass a readable, structurally valid MCAP file with --bag",
        )
    if opening_magic != MCAP_MAGIC or closing_magic != MCAP_MAGIC:
        return DoctorCheck(
            name="bag",
            status="fail",
            required=True,
            detail="invalid MCAP opening or closing magic",
            action="pass a structurally valid MCAP file with --bag",
        )
    return existing


def _platform_check(*, release_target: bool) -> DoctorCheck:
    system = platform.system()
    machine = platform.machine()
    os_release: dict[str, str] = {}
    if system == "Linux":
        with suppress(OSError):
            os_release = platform.freedesktop_os_release()
    distro = os_release.get("ID", "unknown")
    distro_version = os_release.get("VERSION_ID", "unknown")
    target_ok = (
        system == "Linux"
        and machine.casefold() in {"amd64", "x86_64"}
        and distro.casefold() == "ubuntu"
        and distro_version == "26.04"
    )
    host = f"{system} {platform.release()} {machine}"
    if system == "Linux":
        host = f"{host}; distro={distro} {distro_version}"
    return DoctorCheck(
        name="platform",
        status="pass" if target_ok or not release_target else "fail",
        required=release_target,
        detail=f"{host}; release target is Ubuntu 26.04 linux-amd64",
        action=(
            None
            if target_ok or not release_target
            else "run the release-target check on Ubuntu 26.04 linux-amd64"
        ),
    )


def run_doctor(
    *,
    workspace: Path,
    bag: Path | None,
    layout: Path | None,
    offline_kit: Path,
    profile: str = "pure-mcap",
) -> dict[str, Any]:
    release_target = profile == "release-target"
    checks = [_python_check(), _dependency_check()]

    ros_distro = os.environ.get("ROS_DISTRO")
    ros_ok = ros_distro == "lyrical"
    checks.append(
        DoctorCheck(
            name="ros",
            status="pass" if ros_ok else ("fail" if release_target else "warn"),
            required=release_target,
            detail=(
                f"ROS_DISTRO={ros_distro or 'unset'}; "
                "ROS 2 Lyrical is required for the release target"
            ),
            action=(
                None
                if ros_ok
                else "source ROS 2 Lyrical when checking the release target"
            ),
        )
    )

    workspace_check = _path_check(
        "workspace",
        workspace,
        kind="directory",
        missing_action="create the workspace directory and pass it with --workspace",
    )
    if workspace_check.status == "pass" and not os.access(workspace, os.W_OK):
        workspace_check = DoctorCheck(
            name="workspace",
            status="fail",
            required=True,
            detail=f"not writable: {workspace.resolve()}",
            action="choose a writable directory and pass it with --workspace",
        )
    checks.append(workspace_check)
    checks.append(_bag_check(bag))
    kit_required = ("pyproject.toml", "uv.lock", "examples", "schemas")
    missing_kit_entries = [name for name in kit_required if not (offline_kit / name).exists()]
    checks.append(
        DoctorCheck(
            name="offline-kit",
            status="fail" if missing_kit_entries else "pass",
            required=True,
            detail=(
                f"missing {', '.join(missing_kit_entries)} from {offline_kit}"
                if missing_kit_entries
                else str(offline_kit.resolve())
            ),
            action=(
                "run from the unpacked offline kit or pass --offline-kit"
                if missing_kit_entries
                else None
            ),
        )
    )

    checks.append(_platform_check(release_target=release_target))
    plotjuggler = shutil.which("plotjuggler") or shutil.which("PlotJuggler")
    lichtblick = shutil.which("lichtblick") or shutil.which("Lichtblick")
    layout_ok = layout is not None and layout.is_file()
    visualization_ok = bool(lichtblick or (plotjuggler and layout_ok))
    routes: list[str] = []
    if plotjuggler and layout is not None and layout.is_file():
        routes.append(f"PlotJuggler with {layout.resolve()}")
    if lichtblick:
        routes.append(f"Lichtblick at {lichtblick}")
    checks.append(
        DoctorCheck(
            name="visualization",
            status=(
                "pass" if visualization_ok else ("fail" if release_target else "warn")
            ),
            required=release_target,
            detail=(
                "; ".join(routes)
                if routes
                else "no usable route; use Lichtblick or PlotJuggler with --layout"
            ),
            action=(
                None
                if visualization_ok
                else "install Lichtblick, or install PlotJuggler and pass its layout"
            ),
        )
    )

    ok = all(check.status == "pass" for check in checks if check.required)
    return {"checks": [asdict(check) for check in checks], "ok": ok, "profile": profile}


def render_doctor(report: dict[str, Any]) -> str:
    lines = [
        f"Doctor: {'READY' if report['ok'] else 'FAILED'}",
        f"Profile: {report['profile']}",
    ]
    for raw_check in report["checks"]:
        check = dict(raw_check)
        lines.append(f"[{str(check['status']).upper()}] {check['name']}: {check['detail']}")
        if check["action"] is not None:
            lines.append(f"  Action: {check['action']}")
    return "\n".join(lines) + "\n"
