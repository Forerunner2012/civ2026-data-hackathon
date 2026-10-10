"""Exercise the qualified label-review adapter with generated synthetic inputs."""

from __future__ import annotations

import json
import queue
import subprocess
import sys
import tempfile
import threading
import time
from argparse import Namespace
from pathlib import Path
from typing import Any, Callable
from urllib.error import HTTPError
from urllib.parse import parse_qs, urlencode, urlsplit
from urllib.request import Request, urlopen

from mcap.writer import CompressionType, Writer

from civ_workshop.artifacts import canonical_json, file_sha256
from civ_workshop.data_products import build_data_product
from civ_workshop.errors import CivError
from civ_workshop.label_packs import load_label_pack, validate_label_pack
from civ_workshop.organizer.label_review import (
    ReviewApplication,
    _prepare_binding,
    _read_progress,
)
from civ_workshop.score_reference import validate_score_reference

EPOCH_NS = 1_791_300_000_000_000_123
SYNTHETIC_SPEC = """\
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


def _check(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def _write_json(path: Path, value: object) -> None:
    path.write_text(f"{canonical_json(value)}\n", encoding="utf-8", newline="\n")


def _write_source(path: Path) -> None:
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
    with path.open("wb") as stream:
        writer = Writer(stream, compression=CompressionType.NONE)
        writer.start(profile="civ.micro", library="civ-label-acquisition-fixture")
        channels: dict[str, int] = {}
        for topic, (name, schema) in schemas.items():
            schema_id = writer.register_schema(
                name=name,
                encoding="jsonschema",
                data=json.dumps(schema, sort_keys=True).encode("utf-8"),
            )
            channels[topic] = writer.register_channel(
                schema_id=schema_id,
                topic=topic,
                message_encoding="json",
            )
        for second, value in enumerate((0.0, 2.0, 2.0, 0.0, 0.0)):
            timestamp = EPOCH_NS + second * 1_000_000_000
            writer.add_message(
                channel_id=channels["/micro/signal"],
                log_time=timestamp,
                publish_time=timestamp,
                data=json.dumps({"value": value}).encode("utf-8"),
            )
            writer.add_message(
                channel_id=channels["/micro/evidence"],
                log_time=timestamp,
                publish_time=timestamp,
                data=json.dumps({"label": f"synthetic-{second}"}).encode("utf-8"),
            )
        writer.finish()


def _review_args(
    *,
    source: Path,
    spec: Path,
    run: Path,
    progress: Path,
    practice: Path,
    truth: Path,
) -> Namespace:
    return Namespace(
        source=source,
        spec=spec,
        events=run / "events.jsonl",
        manifest=run / "run-manifest.json",
        dataset="kashiwa",
        source_id="synthetic-source",
        progress=progress,
        practice_output=practice,
        organizer_output=truth,
        camera_context_manifest=None,
        port=0,
        no_browser=True,
    )


def _run(command: list[str]) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(command, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as error:
        raise RuntimeError(
            f"Command failed: {command!r}\nstdout:\n{error.stdout}\nstderr:\n{error.stderr}"
        ) from error


def _start_review(args: Namespace) -> tuple[subprocess.Popen[str], threading.Thread, str, str]:
    command = [
        sys.executable,
        "-m",
        "civ_workshop.cli",
        "labels",
        "review",
        "--source",
        str(args.source),
        "--spec",
        str(args.spec),
        "--events",
        str(args.events),
        "--manifest",
        str(args.manifest),
        "--dataset",
        str(args.dataset),
        "--source-id",
        str(args.source_id),
        "--progress",
        str(args.progress),
        "--practice-output",
        str(args.practice_output),
        "--organizer-output",
        str(args.organizer_output),
        "--port",
        "0",
        "--no-browser",
    ]
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        bufsize=1,
    )
    output: queue.Queue[str] = queue.Queue()

    def read_output() -> None:
        if process.stdout is not None:
            for line in process.stdout:
                output.put(line.rstrip("\r\n"))

    reader = threading.Thread(target=read_output, daemon=True)
    reader.start()
    captured: list[str] = []
    deadline = time.monotonic() + 20
    while time.monotonic() < deadline:
        if process.poll() is not None and output.empty():
            break
        try:
            line = output.get(timeout=0.1)
        except queue.Empty:
            continue
        captured.append(line)
        prefix = "Local label review: "
        if line.startswith(prefix):
            review_url = line[len(prefix) :]
            token = parse_qs(urlsplit(review_url).query).get("token", [""])[0]
            if token:
                return process, reader, review_url, token
            break
    if process.poll() is None:
        process.terminate()
        process.wait(timeout=5)
    raise RuntimeError("Review service did not start:\n" + "\n".join(captured))


def _stop_review(process: subprocess.Popen[str], reader: threading.Thread) -> None:
    if process.poll() is None:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)
    reader.join(timeout=1)


def _request_json(url: str, method: str, token: str) -> tuple[int, Any]:
    request = Request(url, headers={"X-CIV-Token": token}, method=method)
    try:
        with urlopen(request, timeout=5) as response:
            status = response.status
            body = response.read()
    except HTTPError as error:
        status = error.code
        body = error.read()
    try:
        return status, json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return status, {"error": body.decode("utf-8", errors="replace")}


def _get_state(review_url: str, token: str) -> dict[str, Any]:
    parts = urlsplit(review_url)
    query = urlencode({"token": token})
    url = f"{parts.scheme}://{parts.netloc}/api/state?{query}"
    status, value = _request_json(url, "GET", token)
    _check(status == 200 and isinstance(value, dict), f"State request failed: {value}")
    return value


def _post(
    review_url: str, token: str, path: str, value: dict[str, object]
) -> dict[str, Any]:
    parts = urlsplit(review_url)
    data = json.dumps(value, separators=(",", ":")).encode("utf-8")
    request = Request(
        f"{parts.scheme}://{parts.netloc}{path}",
        data=data,
        headers={"Content-Type": "application/json", "X-CIV-Token": token},
        method="POST",
    )
    try:
        with urlopen(request, timeout=5) as response:
            status = response.status
            body = response.read()
    except HTTPError as error:
        status = error.code
        body = error.read()
    try:
        parsed = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        parsed = {"error": body.decode("utf-8", errors="replace")}
    if status != 200 or not isinstance(parsed, dict):
        raise RuntimeError(f"POST {path} failed with HTTP {status}: {parsed}")
    return parsed


def _expect_rejection(
    review_url: str,
    token: str,
    path: str,
    value: dict[str, object],
    expected: str,
) -> None:
    parts = urlsplit(review_url)
    data = json.dumps(value, separators=(",", ":")).encode("utf-8")
    request = Request(
        f"{parts.scheme}://{parts.netloc}{path}",
        data=data,
        headers={"Content-Type": "application/json", "X-CIV-Token": token},
        method="POST",
    )
    try:
        with urlopen(request, timeout=5) as response:
            status = response.status
            body = response.read()
    except HTTPError as error:
        status = error.code
        body = error.read()
    try:
        parsed = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        parsed = {"error": body.decode("utf-8", errors="replace")}
    message = str(parsed.get("error", "")) if isinstance(parsed, dict) else str(parsed)
    _check(status == 400 and expected in message, f"Expected refusal '{expected}', got {parsed}")


def _expect_civ_error(operation: Callable[[], object], expected: str) -> None:
    try:
        operation()
    except CivError as error:
        _check(expected in str(error), f"Expected '{expected}', got '{error}'")
        return
    raise RuntimeError(f"Expected adapter refusal containing '{expected}'")


def _expect_binding_refusal(args: Namespace, expected: str) -> None:
    try:
        _prepare_binding(args)
    except CivError as error:
        _check(expected in str(error), f"Expected '{expected}', got '{error}'")
        return
    raise RuntimeError(f"Expected identity refusal containing '{expected}'")


def _candidate(state: dict[str, Any], identifier: str) -> dict[str, Any]:
    candidates = state["state"]["candidates"] if "state" in state else state["candidates"]
    return next(item for item in candidates if item["id"] == identifier)


def _validate_stale_inputs(
    source: Path,
    spec: Path,
    events_path: Path,
    manifest_path: Path,
    progress: Path,
    root: Path,
) -> None:
    stale_args = _review_args(
        source=source,
        spec=spec,
        run=events_path.parent,
        progress=progress,
        practice=root / "stale-practice.json",
        truth=root / "stale-truth.json",
    )
    binding, _, _, before_ns, after_ns = _prepare_binding(stale_args)
    state = _read_progress(binding.progress_path, binding)
    app = ReviewApplication(binding, state, before_ns=before_ns, after_ns=after_ns)

    for path, changed, expected in (
        (events_path, events_path.read_bytes() + b"\n", "candidate events changed during review"),
        (manifest_path, manifest_path.read_bytes() + b"\n", "run manifest changed during review"),
        (spec, spec.read_bytes() + b"\n", "EventSpec changed during review"),
        (source, source.read_bytes() + b"stale", "source recording changed during review"),
    ):
        original = path.read_bytes()
        path.write_bytes(changed)
        try:
            _expect_civ_error(lambda: app.export("practice"), expected)
        finally:
            path.write_bytes(original)

    _check(not stale_args.practice_output.exists(), "Stale input created practice output")


def main() -> None:
    root = Path(tempfile.mkdtemp(prefix="civ-label-acquisition-"))
    source = root / "synthetic.mcap"
    spec = root / "synthetic.yaml"
    run = root / "detected"
    progress = root / "review-progress.json"
    practice = root / "practice-label-pack.json"
    truth = root / "source-relative-truth.json"
    spec.write_text(SYNTHETIC_SPEC, encoding="utf-8", newline="\n")
    _write_source(source)

    expected_source_hash = file_sha256(source)
    _run(
        [
            sys.executable,
            "-m",
            "civ_workshop.cli",
            "detect",
            str(spec),
            str(source),
            "--output",
            str(run),
        ]
    )
    events_path = run / "events.jsonl"
    manifest_path = run / "run-manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    _check(manifest["source"]["sha256"] == expected_source_hash, "Detection source hash changed")
    detected = [
        json.loads(line)
        for line in events_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    _check(len(detected) == 1, f"Expected one synthetic proposal, found {len(detected)}")
    candidate_id = str(detected[0]["event_id"])

    base_args = _review_args(
        source=source,
        spec=spec,
        run=run,
        progress=root / "mismatch-progress.json",
        practice=root / "mismatch-practice.json",
        truth=root / "mismatch-truth.json",
    )
    wrong_source = root / "wrong-source.mcap"
    wrong_source.write_bytes(source.read_bytes() + b"wrong synthetic source")
    wrong_source_args = _review_args(
        source=wrong_source,
        spec=spec,
        run=run,
        progress=base_args.progress,
        practice=base_args.practice_output,
        truth=base_args.organizer_output,
    )
    _expect_binding_refusal(wrong_source_args, "source recording SHA-256")

    wrong_spec = root / "wrong-spec.yaml"
    wrong_spec.write_bytes(spec.read_bytes() + b"# changed synthetic EventSpec identity\n")
    wrong_spec_args = _review_args(
        source=source,
        spec=wrong_spec,
        run=run,
        progress=base_args.progress,
        practice=base_args.practice_output,
        truth=base_args.organizer_output,
    )
    _expect_binding_refusal(wrong_spec_args, "EventSpec identity does not match")

    wrong_events = root / "wrong-events.jsonl"
    wrong_events.write_bytes(events_path.read_bytes() + b"\n")
    wrong_event_args = Namespace(**vars(base_args))
    wrong_event_args.events = wrong_events
    _expect_binding_refusal(wrong_event_args, "events file does not match the run manifest")

    review_args = _review_args(
        source=source,
        spec=spec,
        run=run,
        progress=progress,
        practice=practice,
        truth=truth,
    )
    process, reader, review_url, token = _start_review(review_args)
    try:
        parts = urlsplit(review_url)
        root_url = f"{parts.scheme}://{parts.netloc}/?{urlencode({'token': token})}"
        with urlopen(root_url, timeout=5) as response:
            html = response.read()
        _check(response.status == 200 and html, "Local review page did not load")

        initial = _get_state(review_url, token)
        candidate = _candidate(initial, candidate_id)
        _check(candidate["context_status"] == "missing", "Fixture should have missing context")
        _check(bool(candidate["missing_context"]), "Missing context needs an explanation")

        _expect_rejection(
            review_url,
            token,
            "/api/export",
            {"target": "practice"},
            "review is incomplete",
        )
        _post(review_url, token, "/api/action", {"type": "set-reviewer", "name": "Synthetic reviewer (fixture only)"})
        _expect_rejection(
            review_url,
            token,
            "/api/action",
            {
                "type": "approve",
                "candidate_id": candidate_id,
                "uncertainty_disposition": "clear",
            },
            "missing context",
        )
        _expect_rejection(
            review_url,
            token,
            "/api/action",
            {
                "type": "reject",
                "candidate_id": candidate_id,
                "reason": " ",
                "uncertainty_disposition": "reject_candidate",
            },
            "rejection reason",
        )
        _expect_rejection(
            review_url,
            token,
            "/api/action",
            {
                "type": "data-gap",
                "candidate_id": candidate_id,
                "reason": "Synthetic unsupported exclusion.",
                "exclusion_kind": "uncertain_event",
                "uncertainty_disposition": "scoring_data_gap",
            },
            "unsupported exclusion kind",
        )

        _post(
            review_url,
            token,
            "/api/action",
            {
                "type": "approve",
                "candidate_id": candidate_id,
                "uncertainty_disposition": "accept_event",
                "uncertainty_reason": "The synthetic fixture has no camera context.",
            },
        )
        _post(
            review_url,
            token,
            "/api/action",
            {"type": "set-practice", "candidate_id": candidate_id, "selected": True},
        )
        _post(review_url, token, "/api/action", {"type": "signoff", "checked": True})

        start_ns = EPOCH_NS + 1_000_000_001
        end_ns = EPOCH_NS + 2_999_999_997
        edited = _post(
            review_url,
            token,
            "/api/action",
            {
                "type": "edit",
                "candidate_id": candidate_id,
                "start_ns": str(start_ns),
                "end_ns": str(end_ns),
                "reason": "Synthetic adjustment to exact nanosecond boundaries.",
            },
        )
        edited_candidate = _candidate(edited, candidate_id)
        _check(edited_candidate["decision"] == "pending", "Edit must clear approval")
        _check(not edited_candidate["practice_selected"], "Edit must clear practice selection")
        _check(edited["state"]["coverage_reviewed"] is False, "Edit must clear coverage signoff")
        _expect_rejection(
            review_url,
            token,
            "/api/export",
            {"target": "practice"},
            "review is incomplete",
        )

        undone = _post(review_url, token, "/api/action", {"type": "undo"})
        restored = _candidate(undone, candidate_id)
        _check(restored["decision"] == "approved", "Undo should restore the prior decision")
        _check(restored["start_ns"] != str(start_ns), "Undo should restore prior boundaries")
        _check(
            undone["state"]["audit"][-1]["undid"]["reason"]
            == "Synthetic adjustment to exact nanosecond boundaries.",
            "Undo audit should retain the adjustment reason",
        )

        _post(
            review_url,
            token,
            "/api/action",
            {
                "type": "edit",
                "candidate_id": candidate_id,
                "start_ns": str(start_ns),
                "end_ns": str(end_ns),
                "reason": "Synthetic adjustment to exact nanosecond boundaries.",
            },
        )
        _post(
            review_url,
            token,
            "/api/action",
            {
                "type": "approve",
                "candidate_id": candidate_id,
                "uncertainty_disposition": "accept_event",
                "uncertainty_reason": "The synthetic fixture has no camera context.",
            },
        )
        _post(
            review_url,
            token,
            "/api/action",
            {"type": "set-practice", "candidate_id": candidate_id, "selected": True},
        )
        missed = _post(
            review_url,
            token,
            "/api/action",
            {
                "type": "add-missed",
                "start_ns": str(EPOCH_NS + 3_500_000_000),
                "end_ns": str(EPOCH_NS + 3_800_000_000),
                "reason": "Synthetic full-recording review found a missed event.",
            },
        )
        missed_candidate = missed["state"]["candidates"][-1]
        missed_id = str(missed_candidate["id"])
        _post(
            review_url,
            token,
            "/api/action",
            {
                "type": "approve",
                "candidate_id": missed_id,
                "uncertainty_disposition": "accept_event",
                "uncertainty_reason": "The synthetic missed event has no camera context.",
            },
        )
        _expect_rejection(
            review_url,
            token,
            "/api/export",
            {"target": "practice"},
            "review is incomplete",
        )
        _post(review_url, token, "/api/action", {"type": "signoff", "checked": True})
        _post(review_url, token, "/api/save", {})
        reloaded = _post(review_url, token, "/api/reload", {})
        _check(not reloaded["gate"], "Reloaded review should pass its gate")
        _check(
            reloaded["state"]["candidates"][0]["start_ns"] == str(start_ns)
            and reloaded["state"]["candidates"][0]["end_ns"] == str(end_ns),
            "Nanosecond strings must survive save and reload",
        )
        audit = reloaded["state"]["audit"]
        _check(
            any(
                item.get("action") == "edit"
                and item.get("reason") == "Synthetic adjustment to exact nanosecond boundaries."
                for item in audit
            ),
            "Local audit should retain adjustment reasons after reload",
        )
        _check(
            any(item.get("action") == "add-missed" for item in audit),
            "Local audit should retain the missed-event decision",
        )
        _check(
            reloaded["state"]["candidates"][0]["uncertainty_reason"]
            == "The synthetic fixture has no camera context.",
            "Missing-context uncertainty reason should survive reload",
        )

        _post(review_url, token, "/api/export", {"target": "practice"})
        _post(review_url, token, "/api/export", {"target": "organizer-private"})
    finally:
        _stop_review(process, reader)

    practice_text = practice.read_text(encoding="utf-8")
    practice_document = json.loads(practice_text)
    validate_score_reference(practice_document)
    validate_label_pack(practice_document)
    _check(
        practice_document["labels"]
        == [{"end_ns": end_ns, "label_id": candidate_id, "start_ns": start_ns}],
        "Practice consumer should parse exact integer nanoseconds for selected labels",
    )
    _check("source_id" not in practice_document, "Practice output must not include private source ID")
    _check("Synthetic reviewer" not in practice_text, "Practice output must not include reviewer")
    _check("adjustment" not in practice_text.lower(), "Practice output must not include audit reasons")
    _check(str(root) not in practice_text, "Practice output must not include local paths")

    duplicate_args = _review_args(
        source=source,
        spec=spec,
        run=run,
        progress=progress,
        practice=root / "practice-label-pack-repeat.json",
        truth=root / "source-relative-truth-repeat.json",
    )
    duplicate_binding, _, _, before_ns, after_ns = _prepare_binding(duplicate_args)
    duplicate_state = _read_progress(duplicate_binding.progress_path, duplicate_binding)
    duplicate_app = ReviewApplication(
        duplicate_binding,
        duplicate_state,
        before_ns=before_ns,
        after_ns=after_ns,
    )
    duplicate_app.export("practice")
    duplicate_app.export("organizer-private")
    _check(
        practice.read_bytes() == duplicate_args.practice_output.read_bytes(),
        "Repeated export of fixed reviewed inputs must produce identical bytes",
    )
    _check(
        truth.read_bytes() == duplicate_args.organizer_output.read_bytes(),
        "Repeated private export of fixed reviewed inputs must produce identical bytes",
    )

    truth_document = json.loads(truth.read_text(encoding="utf-8"))
    _check(len(truth_document["intervals"]) == 2, "Private truth should include both approved events")
    _check(
        {item["interval_id"] for item in truth_document["intervals"]}
        == {candidate_id, missed_id},
        "Private truth should include the missed event excluded from practice",
    )

    recipe = root / "synthetic-product-recipe.json"
    _write_json(
        recipe,
        {
            "attribution": "Synthetic fixture only.",
            "contract": "civ.data-product-recipe/v1",
            "dataset": "kashiwa",
            "license": {"name": "Synthetic fixture only", "url": None},
            "modifications": ["Filtered to the synthetic signal topic."],
            "product_name": "synthetic-signals.mcap",
            "recipe_id": "synthetic-signals-v1",
            "rights_scope": "Synthetic fixture only.",
            "source": {"id": "synthetic-source", "sha256": expected_source_hash},
            "split": "sealed",
            "topics": ["/micro/signal"],
            "version": 1,
        },
    )
    product_root = root / "synthetic-products"
    product_result = build_data_product(source, recipe, product_root)
    product_manifest = product_root / str(product_result["manifest"])
    label_pack_root = root / "organizer-label-packs"
    _run(
        [
            sys.executable,
            "-m",
            "civ_workshop.label_packs",
            "build",
            "--truth",
            str(truth),
            "--manifests",
            str(product_manifest),
            "--output",
            str(label_pack_root),
        ]
    )
    audit_result = _run(
        [
            sys.executable,
            "-m",
            "civ_workshop.label_packs",
            "audit",
            str(label_pack_root / "label-pack-set.json"),
        ]
    )
    _check(json.loads(audit_result.stdout)["valid"] is True, "Private label-pack audit failed")
    private_pack_path = next((label_pack_root / "packs").glob("*.json"))
    private_pack = load_label_pack(private_pack_path, require_provenance=True)
    _check(len(private_pack["labels"]) == 2, "Private consumer should receive both truth intervals")

    _validate_stale_inputs(
        source,
        spec,
        events_path,
        manifest_path,
        progress,
        root,
    )

    human_command = (
        f'uv run civ labels review --source "{source}" --spec "{spec}" '
        f'--events "{events_path}" --manifest "{manifest_path}" --dataset kashiwa '
        f'--source-id synthetic-source --progress "{root / "human-review-progress.json"}" '
        f'--practice-output "{root / "human-practice.json"}" '
        f'--organizer-output "{root / "human-private-truth.json"}"'
    )
    print("Synthetic CIV label acquisition validation passed.")
    print("No real recording, label, permission, credential, or image was used.")
    print(f"Fixture directory: {root}")
    print("Open a separate human review session with:")
    print(human_command)


if __name__ == "__main__":
    main()
