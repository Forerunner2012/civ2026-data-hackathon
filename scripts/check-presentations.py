"""Validate local presentation artifacts before approved kit assembly."""

import argparse
from pathlib import Path

from civ_workshop.presentation_files import verified_presentations

parser = argparse.ArgumentParser()
parser.add_argument("--input", type=Path, required=True)
args = parser.parse_args()
verified_presentations(args.input)
print("PASS: deck hashes, 13+1 slides, widescreen metadata and exact full-slide images.")
