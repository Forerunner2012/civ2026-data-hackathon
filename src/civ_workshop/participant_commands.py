from __future__ import annotations

import argparse
import json
from pathlib import Path

from civ_workshop.clipping import clip_events
from civ_workshop.detection import detect_events
from civ_workshop.doctor import render_doctor, run_doctor
from civ_workshop.inspection import inspect_bag, render_inventory, render_samples, sample_bag
from civ_workshop.reporting import build_report_bundle
from civ_workshop.scoring import score_submission
from civ_workshop.submission import scaffold_submission


def add_participant_commands(commands: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    doctor_parser = commands.add_parser("doctor", help="check the offline participant environment")
    doctor_parser.add_argument("--workspace", type=Path, default=Path.cwd())
    doctor_parser.add_argument("--bag", type=Path)
    doctor_parser.add_argument("--layout", type=Path)
    doctor_parser.add_argument("--offline-kit", type=Path, default=Path.cwd())
    doctor_parser.add_argument(
        "--profile",
        choices=("pure-mcap", "release-target"),
        default="pure-mcap",
        help="readiness policy to enforce (default: pure-mcap)",
    )
    doctor_parser.add_argument("--json", action="store_true", dest="as_json")

    inspect_parser = commands.add_parser("inspect", help="inspect an MCAP bag")
    inspect_parser.add_argument("bag", type=Path)
    inspect_parser.add_argument("--json", action="store_true", dest="as_json")

    sample_parser = commands.add_parser("sample", help="sample one field from an MCAP bag")
    sample_parser.add_argument("bag", type=Path)
    sample_parser.add_argument("--topic", required=True)
    sample_parser.add_argument("--field", required=True)
    sample_parser.add_argument("--start-ns", type=int)
    sample_parser.add_argument("--end-ns", type=int)
    sample_parser.add_argument("--limit", type=int, default=20)
    sample_parser.add_argument("--json", action="store_true", dest="as_json")

    detect_parser = commands.add_parser("detect", help="detect events in an MCAP bag")
    detect_parser.add_argument("spec", type=Path)
    detect_parser.add_argument("dataset", type=Path)
    detect_parser.add_argument("--output", type=Path, default=Path.cwd())
    detect_parser.add_argument("--dry-run", action="store_true")
    detect_parser.add_argument(
        "--explain",
        action="store_true",
        help="include matching-sample, merged-candidate and duration-rejection counts",
    )

    clip_parser = commands.add_parser("clip", help="extract event evidence as MCAP")
    clip_parser.add_argument("events", type=Path)
    clip_parser.add_argument("dataset", type=Path)

    score_parser = commands.add_parser("score", help="score normalized event intervals")
    score_parser.add_argument("submission", type=Path)
    score_parser.add_argument(
        "--labels",
        type=Path,
        help="matching practice pack; omit to record unevaluated metrics and continue packaging",
    )

    report_parser = commands.add_parser("report", help="validate and bundle a submission")
    report_parser.add_argument("submission", type=Path)

    submission_parser = commands.add_parser(
        "submission-init", help="create a deliberately incomplete submission workspace"
    )
    submission_parser.add_argument("workspace", type=Path)
    submission_parser.add_argument("--shell", choices=("powershell", "posix"), required=True)


def dispatch_participant_command(args: argparse.Namespace) -> bool:
    if args.command == "doctor":
        doctor_report = run_doctor(
            workspace=args.workspace,
            bag=args.bag,
            layout=args.layout,
            offline_kit=args.offline_kit,
            profile=args.profile,
        )
        if args.as_json:
            print(json.dumps(doctor_report, sort_keys=True, separators=(",", ":")))
        else:
            print(render_doctor(doctor_report), end="")
        if not doctor_report["ok"]:
            raise SystemExit(2)
    elif args.command == "inspect":
        inventory = inspect_bag(args.bag)
        if args.as_json:
            print(json.dumps(inventory, sort_keys=True, separators=(",", ":")))
        else:
            print(render_inventory(args.bag, inventory), end="")
    elif args.command == "sample":
        samples = sample_bag(
            args.bag,
            args.topic,
            args.field,
            start_ns=args.start_ns,
            end_ns=args.end_ns,
            limit=args.limit,
        )
        if args.as_json:
            print(json.dumps(samples, sort_keys=True, separators=(",", ":")))
        else:
            print(render_samples(samples), end="")
    elif args.command == "detect":
        detect_result = detect_events(
            args.spec, args.dataset, args.output, dry_run=args.dry_run, explain=args.explain
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
    elif args.command == "submission-init":
        submission_result = scaffold_submission(args.workspace, args.shell)
        print(json.dumps(submission_result, sort_keys=True, separators=(",", ":")))
    else:
        return False
    return True
