from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from dataclasses import asdict
from pathlib import Path

from civ_workshop.batch import run_batch
from civ_workshop.errors import CivError
from civ_workshop.intake import IntakeLedger, import_form_response
from civ_workshop.organizer.label_review import (
    add_label_review_command,
    dispatch_label_review_command,
)
from civ_workshop.participant_commands import add_participant_commands, dispatch_participant_command
from civ_workshop.tally import import_tally_csv


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="civ")
    commands = parser.add_subparsers(dest="command", required=True)

    add_participant_commands(commands)
    add_label_review_command(commands)

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

    batch_parser = commands.add_parser(
        "score-batch", help="score every authoritative submission in an intake ledger"
    )
    batch_parser.add_argument("--ledger", type=Path, required=True)
    batch_parser.add_argument("--labels", type=Path, required=True)
    batch_parser.add_argument("--output", type=Path, required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    try:
        if dispatch_label_review_command(args):
            return
        if dispatch_participant_command(args):
            return
        if args.command == "intake-form":
            receipt = import_form_response(args.response, args.ledger)
            print(json.dumps(asdict(receipt), sort_keys=True, separators=(",", ":")))
        elif args.command == "intake-tally":
            tally_summary = import_tally_csv(args.csv, args.ledger)
            print(json.dumps(tally_summary, sort_keys=True, separators=(",", ":")))
        elif args.command == "intake-local":
            receipt = IntakeLedger(args.ledger).accept_local(
                identity=args.identity,
                received_at=args.received_at,
                submitted_sha256=args.sha256,
                bundle_path=args.bundle,
                delivery_id=args.delivery_id,
            )
            print(json.dumps(asdict(receipt), sort_keys=True, separators=(",", ":")))
        elif args.command == "score-batch":
            batch_summary = run_batch(args.ledger, args.labels, args.output)
            print(json.dumps(batch_summary, sort_keys=True, separators=(",", ":")))
    except CivError as error:
        print(f"civ: {error}", file=sys.stderr)
        raise SystemExit(2) from None


if __name__ == "__main__":
    main()
