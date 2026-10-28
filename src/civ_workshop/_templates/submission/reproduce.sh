#!/usr/bin/env sh
set -eu

if [ "$#" -lt 1 ] || [ "$#" -gt 3 ]; then
  echo "usage: ./reproduce.sh DATASET [PRACTICE_LABELS|-] [NEW_OUTPUT]" >&2
  exit 2
fi

workspace=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
dataset=$(CDPATH= cd -- "$(dirname -- "$1")" && pwd)/$(basename -- "$1")
labels=${2:--}
if [ "$labels" != "-" ]; then
  labels=$(CDPATH= cd -- "$(dirname -- "$labels")" && pwd)/$(basename -- "$labels")
fi
destination=$workspace
if [ "$#" -eq 3 ]; then
  # mkdir refuses an existing output; the completed submission stays unchanged.
  mkdir -- "$3"
  destination=$(CDPATH= cd -- "$3" && pwd)
  cp -R -- "$workspace/detector" "$destination/detector"
  if [ -d "$workspace/extension" ]; then
    cp -R -- "$workspace/extension" "$destination/extension"
  fi
  for artifact in "$workspace/report.md" "$workspace/reproduce.sh" \
      "$workspace"/*.svg "$workspace"/*.png "$workspace"/*.jpg \
      "$workspace"/*.jpeg "$workspace"/*.webp; do
    if [ -f "$artifact" ]; then cp -- "$artifact" "$destination/"; fi
  done
fi

civ detect "$destination/detector/detector.yaml" "$dataset" --output "$destination"
civ clip "$destination/events.jsonl" "$dataset"
if [ "$labels" = "-" ]; then
  civ score "$destination"
else
  civ score "$destination" --labels "$labels"
fi
civ report "$destination"
