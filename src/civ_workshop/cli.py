from __future__ import annotations

import argparse
import json
import os
import sys
from collections.abc import Sequence
from dataclasses import asdict
from pathlib import Path

from civ_workshop.artifacts import file_sha256, read_json_file
from civ_workshop.batch import run_batch
from civ_workshop.cohort_scoring import load_evaluation_plan
from civ_workshop.errors import CivError, SourceDataError
from civ_workshop.intake import IntakeLedger, import_form_response
from civ_workshop.organizer.decision_records import append_decision
from civ_workshop.organizer.label_review import (
    add_label_review_command,
    dispatch_label_review_command,
)
from civ_workshop.organizer.scoring_readiness import check_readiness
from civ_workshop.participant_commands import add_participant_commands, dispatch_participant_command
from civ_workshop.session import prepare_session
from civ_workshop.tally import import_tally_csv


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="civ")
    commands = parser.add_subparsers(dest="command", required=True)

    add_participant_commands(commands)
    add_label_review_command(commands)
    decision_parser = commands.add_parser(
        "record-decision", help="append an organizer decision with existing artifact evidence"
    )
    decision_parser.add_argument("record", type=Path, help="JSON record")
    decision_parser.add_argument("--log", type=Path, required=True)

    form_parser = commands.add_parser(
        "intake-form", help="import one exported online form response"
    )
    form_parser.add_argument("response", type=Path)
    form_parser.add_argument("--ledger", type=Path, required=True)

    tally_parser = commands.add_parser(
        "intake-tally", help="import a manually exported Tally submissions CSV"
    )
    tally_parser.add_argument("csv", type=Path, metavar="TALLY_CSV")
    tally_parser.add_argument("--ledger", type=Path, required=True)

    local_parser = commands.add_parser(
        "intake-local", help="record one local or USB submission bundle"
    )
    local_parser.add_argument("bundle", type=Path)
    local_parser.add_argument("--ledger", type=Path, required=True)
    local_parser.add_argument("--identity", required=True)
    local_parser.add_argument("--received-at", required=True)
    local_parser.add_argument("--sha256", required=True)
    local_parser.add_argument("--delivery-id", required=True)
    local_parser.add_argument("--track-id", help="track-specific submission identifier")
    for intake_parser in (form_parser, tally_parser, local_parser):
        intake_parser.add_argument(
            "--plan",
            type=Path,
            help="saved plan supplying the cutoff; omission uses the historical 2026 cutoff",
        )

    session_parser = commands.add_parser(
        "prepare-session", help="resolve a plan profile and session overrides into a new saved plan"
    )
    session_parser.add_argument("--plan", type=Path, required=True, help="evaluation plan profile")
    session_parser.add_argument(
        "--output", type=Path, required=True, help="new plan; never overwritten"
    )
    session_parser.add_argument(
        "--cutoff", help="ISO-8601 cutoff; overrides CIV_SESSION_CUTOFF/profile"
    )
    session_parser.add_argument("--session-id", help="overrides CIV_SESSION_ID/profile")
    session_parser.add_argument(
        "--participant", action="append", help="replace roster; repeat per ID"
    )

    batch_parser = commands.add_parser(
        "score-batch", help="score every authoritative submission in an intake ledger"
    )
    batch_parser.add_argument("--ledger", type=Path, required=True)
    batch_parser.add_argument("--labels", type=Path, help="legacy diagnostic label-pack directory")
    batch_parser.add_argument("--output", type=Path, required=True)
    batch_parser.add_argument(
        "--official",
        action="store_true",
        help="require official automatic scoring readiness; final totals need manual review",
    )
    batch_parser.add_argument(
        "--approval", type=Path, help="legacy readiness input; not used for cohort replay"
    )
    readiness_parser = commands.add_parser(
        "score-readiness", help="report unresolved official scoring prerequisites without writes"
    )
    readiness_parser.add_argument("--ledger", type=Path, required=True)
    readiness_parser.add_argument("--approval", type=Path)
    for command_parser in (batch_parser, readiness_parser):
        command_parser.add_argument("--plan", type=Path)
        command_parser.add_argument("--preflight", type=Path, help="legacy readiness input")
        command_parser.add_argument("--review-status", type=Path, help="legacy readiness input")
    return parser


def main(argv: Sequence[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    try:
        if dispatch_label_review_command(args):
            return
        if dispatch_participant_command(args):
            return
        cutoff = None
        plan_sha256 = None
        if args.command in ("intake-form", "intake-tally", "intake-local") and args.plan:
            plan = load_evaluation_plan(args.plan)
            cutoff = plan["cutoff"]
            plan_sha256 = file_sha256(args.plan)
        if args.command == "prepare-session":
            print(
                json.dumps(
                    prepare_session(
                        args.plan,
                        args.output,
                        cutoff=args.cutoff,
                        session_id=args.session_id,
                        participants=args.participant,
                    ),
                    sort_keys=True,
                )
            )
        elif args.command == "record-decision":
            append_decision(args.log, read_json_file(args.record, "decision record"))
        elif args.command == "intake-form":
            receipt = import_form_response(
                args.response, args.ledger, cutoff=cutoff, evaluation_plan_sha256=plan_sha256
            )
            print(json.dumps(asdict(receipt), sort_keys=True, separators=(",", ":")))
        elif args.command == "intake-tally":
            tally_summary = import_tally_csv(
                args.csv, args.ledger, cutoff=cutoff, evaluation_plan_sha256=plan_sha256
            )
            print(json.dumps(tally_summary, sort_keys=True, separators=(",", ":")))
        elif args.command == "intake-local":
            receipt = IntakeLedger(
                args.ledger, cutoff=cutoff, evaluation_plan_sha256=plan_sha256
            ).accept_local(
                identity=args.identity,
                received_at=args.received_at,
                submitted_sha256=args.sha256,
                bundle_path=args.bundle,
                delivery_id=args.delivery_id,
                track_id=args.track_id,
            )
            print(json.dumps(asdict(receipt), sort_keys=True, separators=(",", ":")))
        elif args.command == "score-readiness":
            readiness = check_readiness(
                args.ledger,
                plan_path=args.plan,
                preflight_path=args.preflight,
                review_status_path=args.review_status,
                approval_path=args.approval,
            )
            print(json.dumps(readiness, sort_keys=True, separators=(",", ":")))
            raise SystemExit(0 if readiness.get("ready") is True else 2)
        elif args.command == "score-batch":
            batch_summary = run_batch(
                args.ledger,
                args.labels,
                args.output,
                official=args.official,
                plan_path=args.plan,
                preflight_path=args.preflight,
                review_status_path=args.review_status,
                approval_path=args.approval,
            )
            print(json.dumps(batch_summary, sort_keys=True, separators=(",", ":")))
    except CivError as error:
        print(f"civ: {error}", file=sys.stderr)
        if os.environ.get("CIV_REPLAY_ERROR_CODES") == "1":
            from mcap.exceptions import McapError

            cause: BaseException | None = error
            while cause is not None:
                if isinstance(cause, (OSError, McapError, SourceDataError)):
                    raise SystemExit(3) from None
                cause = cause.__cause__
        raise SystemExit(2) from None


if __name__ == "__main__":
    main()
