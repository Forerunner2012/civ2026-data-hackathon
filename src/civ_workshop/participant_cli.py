from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence

from civ_workshop.errors import CivError
from civ_workshop.participant_commands import add_participant_commands, dispatch_participant_command


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="civ")
    commands = parser.add_subparsers(dest="command", required=True)
    add_participant_commands(commands)
    return parser


def main(argv: Sequence[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    try:
        dispatch_participant_command(args)
    except CivError as error:
        print(f"civ: {error}", file=sys.stderr)
        raise SystemExit(2) from None


if __name__ == "__main__":
    main()
