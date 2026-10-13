from __future__ import annotations

import argparse
import json
from pathlib import Path

from civ_workshop.artifacts import file_sha256
from civ_workshop.detection import detect_events
from civ_workshop.errors import CivError
from civ_workshop.score_reference import load_score_reference
from civ_workshop.scoring import score_submission


class CheckInputError(Exception):
    def __init__(self, category: str, message: str) -> None:
        super().__init__(message)
        self.category = category


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the existing detector and scorer for one supplied practice input set.",
        epilog=(
            "The caller chooses an authorized source, matching EventSpec, and complete "
            "human-reviewed practice pack. This helper checks source binding and consumer "
            "behavior. It does not verify authorization, human review, or label coverage."
        ),
    )
    parser.add_argument(
        "--source",
        type=Path,
        required=True,
        help="an MCAP file or a folder with exactly one top-level MCAP file",
    )
    parser.add_argument("--eventspec", type=Path, required=True, help="the matching EventSpec")
    parser.add_argument("--labels", type=Path, required=True, help="the reviewed practice pack")
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="a fresh output folder outside the supplied input folders",
    )
    return parser


def _resolve_source(source: Path) -> tuple[Path, Path]:
    try:
        exists = source.exists()
    except (OSError, RuntimeError, ValueError) as error:
        raise CheckInputError("source", "source input cannot be accessed") from error
    if not exists:
        raise CheckInputError("source", "source input does not exist")

    if source.is_dir():
        try:
            recordings = sorted(
                (
                    candidate
                    for candidate in source.iterdir()
                    if candidate.is_file() and candidate.suffix.casefold() == ".mcap"
                ),
                key=lambda candidate: candidate.name.casefold(),
            )
        except OSError as error:
            raise CheckInputError("source", "source folder cannot be read") from error
        if not recordings:
            raise CheckInputError("source", "source folder contains no top-level MCAP file")
        if len(recordings) != 1:
            raise CheckInputError(
                "source",
                "source folder contains multiple MCAP files; pass the intended MCAP file",
            )
        try:
            return recordings[0].resolve(strict=True), source.resolve(strict=True)
        except (OSError, RuntimeError, ValueError) as error:
            raise CheckInputError("source", "source input cannot be resolved") from error

    if not source.is_file() or source.suffix.casefold() != ".mcap":
        raise CheckInputError("source", "source input must be an MCAP file or folder")
    try:
        resolved_source = source.resolve(strict=True)
    except (OSError, RuntimeError, ValueError) as error:
        raise CheckInputError("source", "source input cannot be resolved") from error
    return resolved_source, resolved_source.parent


def _resolve_input_file(path: Path, category: str, message: str) -> Path:
    try:
        if not path.is_file():
            raise CheckInputError(category, message)
        return path.resolve(strict=True)
    except CheckInputError:
        raise
    except (OSError, RuntimeError, ValueError) as error:
        raise CheckInputError(category, message) from error


def _is_within(path: Path, root: Path) -> bool:
    return path == root or path.is_relative_to(root)


def _resolve_output(path: Path, input_roots: set[Path]) -> Path:
    try:
        if path.exists() or path.is_symlink():
            raise CheckInputError("output", "output folder must be new")
        if not path.parent.is_dir():
            raise CheckInputError("output", "output parent folder must exist")
        resolved = path.resolve()
    except CheckInputError:
        raise
    except (OSError, RuntimeError, ValueError) as error:
        raise CheckInputError("output", "output folder cannot be accessed") from error
    if any(_is_within(resolved, root) for root in input_roots):
        raise CheckInputError("output", "output folder must be outside the supplied input folders")
    return resolved


def _detect_diagnostic(error: Exception) -> str:
    if isinstance(error, CivError):
        message = str(error).casefold()
        if "resource" in message:
            return "detect consumer rejected an EventSpec resource path"
        if any(term in message for term in ("eventspec", "event spec", "condition", "signal")):
            return "detect consumer rejected the EventSpec"
        if "bag" in message or "mcap" in message:
            return "detect consumer rejected the source MCAP"
    return "detect consumer rejected the supplied inputs"


def _score_diagnostic(error: Exception) -> str:
    if isinstance(error, CivError):
        message = str(error)
        if message == "label pack source_sha256 does not match submission source sha256":
            return message
        if "label pack" in message.casefold() or "scoring reference" in message.casefold():
            return "score consumer rejected the label pack"
    return "score consumer rejected the detected run"


def _emit(document: dict[str, object]) -> None:
    print(json.dumps(document, sort_keys=True, separators=(",", ":")))


def _emit_input_error(error: CheckInputError) -> int:
    _emit(
        {
            "error": {
                "category": error.category,
                "message": str(error),
            }
        }
    )
    return 2


def _run(args: argparse.Namespace) -> int:
    try:
        source, source_root = _resolve_source(args.source)
        eventspec = _resolve_input_file(
            args.eventspec, "EventSpec", "EventSpec input does not exist or is not a file"
        )
        labels = _resolve_input_file(
            args.labels, "label_pack", "label pack input does not exist or is not a file"
        )
        input_roots = {source_root, eventspec.parent, labels.parent}
        output = _resolve_output(args.output, input_roots)
    except CheckInputError as error:
        return _emit_input_error(error)

    try:
        pack = load_score_reference(labels)
    except (CivError, OSError, RuntimeError, ValueError):
        return _emit_input_error(
            CheckInputError("label_pack", "label pack does not satisfy the scoring contract")
        )

    try:
        source_hash = file_sha256(source)
    except (CivError, OSError, RuntimeError, ValueError):
        return _emit_input_error(CheckInputError("source", "source MCAP cannot be read"))

    source_binding = "match" if pack["source_sha256"] == source_hash else "mismatch"
    try:
        output.mkdir()
    except (OSError, RuntimeError, ValueError):
        return _emit_input_error(
            CheckInputError("output", "output folder could not be created")
        )

    report: dict[str, object] = {
        "source_binding": source_binding,
        "detect": {"accepted": False, "diagnostic": "not run"},
        "score": {"accepted": False, "status": "not run"},
    }
    try:
        detect_events(eventspec, source, output)
    except Exception as error:
        report["detect"] = {
            "accepted": False,
            "diagnostic": _detect_diagnostic(error),
        }
        _emit(report)
        return 1
    report["detect"] = {"accepted": True}

    try:
        score_submission(output, labels)
    except Exception as error:
        report["score"] = {
            "accepted": False,
            "diagnostic": _score_diagnostic(error),
        }
        _emit(report)
        return 1

    report["score"] = {"accepted": True}
    _emit(report)
    return 0 if source_binding == "match" else 1


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        return _run(args)
    except (OSError, RuntimeError, ValueError):
        _emit_input_error(
            CheckInputError("path", "an input or output path could not be accessed")
        )
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
