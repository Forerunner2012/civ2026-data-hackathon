#!/usr/bin/env sh
set -eu

if [ "$#" -ne 1 ]; then
  echo "usage: ./reproduce.sh DATASET" >&2
  exit 2
fi

workspace=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
civ detect "$workspace/detector/detector.yaml" "$1" --output "$workspace"
