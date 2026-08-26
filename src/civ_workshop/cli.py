from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from dataclasses import asdict
from pathlib import Path

from civ_workshop.batch import run_batch
from civ_workshop.clipping import clip_events
from civ_workshop.detection import detect_events
from civ_workshop.errors import CivError
from civ_workshop.inspection import inspect_bag, render_inventory
from civ_workshop.intake import IntakeLedger, import_form_response
from civ_workshop.reporting import build_report_bundle
from civ_workshop.scoring import score_submission
from civ_workshop.tally import import_tally_csv


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="civ")
    commands = parser.add_subparsers(dest="command", required=True)

    inspect_parser = commands.add_parser("inspect", help="inspect an MCAP bag")
    inspect_parser.add_argument("bag", type=Path)
    inspect_parser.add_argument("--json", action="store_true", dest="as_json")

    detect_parser = commands.add_parser("detect", help="detect events in an MCAP bag")
    detect_parser.add_argument("spec", type=Path)
    detect_parser.add_argument("dataset", type=Path)
    detect_parser.add_argument("--output", type=Path, default=Path.cwd())
    detect_parser.add_argument("--dry-run", action="store_true")

    clip_parser = commands.add_parser("clip", help="extract event evidence as MCAP")
    clip_parser.add_argument("events", type=Path)
    clip_parser.add_argument("dataset", type=Path)

    score_parser = commands.add_parser("score", help="score normalized event intervals")
    score_parser.add_argument("submission", type=Path)
    score_parser.add_argument("--labels", type=Path, required=True)

    report_parser = commands.add_parser("report", help="validate and bundle a submission")
    report_parser.add_argument("submission", type=Path)

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
        if args.command == "inspect":
            inventory = inspect_bag(args.bag)
            if args.as_json:
                print(json.dumps(inventory, sort_keys=True, separators=(",", ":")))
            else:
                print(render_inventory(args.bag, inventory), end="")
        elif args.command == "detect":
            detect_result = detect_events(
                args.spec, args.dataset, args.output, dry_run=args.dry_run
            )
            print(json.dumps(detect_result, sort_keys=True, separators=(",", ":")))
        elif args.command == "clip":
            clip_result = clip_events(args.events, args.dataset)
            print(json.dumps(clip_result, sort_keys=True, separators=(",", ":")))
        elif args.command == "score":
            score_result = score_submission(args.submission, args.labels)
            print(json.dumps(score_result, sort_keys=True, separators=(",", ":")))
        elif args.command == "report":
            report_result = build_report_bundle(args.submission)
            print(json.dumps(report_result, sort_keys=True, separators=(",", ":")))
        elif args.command == "intake-form":
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
