# Add external geographic points to an EventSpec

First reproduce the core workflow in the [QuickStart](quickstart.md). This optional exercise adds participant-sourced geographic points to a Reims EventSpec. Keep supplied kit files read-only. Run commands from the unpacked kit root after [installing civ](setup.md).

The detector reads latitude and longitude from the recording's `/fix` GNSS messages, measures distance to the points in the configured resource, applies the EventSpec threshold, and uses its timing rules to form encounter intervals. The Cave track covers champagne caves and their associated headquarters, venues, visitor sites, and showrooms. Use the same supplied Reims recordings as the turn track and independently source your points. Organizer locations, truth intervals, hints identifying them, and practice labels for those locations are not supplied. The example JSON shows the format with illustrative coordinates; it does not solve the task.

## Prepare a separate workspace

Create the submission templates and copy the illustrative examples. The commands below use POSIX shell syntax:

```sh
civ submission-init working-points --shell posix
mkdir working-points/extension
cp examples/reims/cave-encounter.yaml working-points/detector/detector.yaml
cp examples/reims/cave-zones.json working-points/detector/cave-zones.json
```

Choose a new directory if `working-points` already exists. Replace `REIMS_SIGNALS.mcap` in the commands below with the exact supplied Reims signal recording. Inspect its GNSS fields before detection:

```text
civ inspect data/REIMS_SIGNALS.mcap
civ sample data/REIMS_SIGNALS.mcap --topic /fix --field latitude --limit 4
civ sample data/REIMS_SIGNALS.mcap --topic /fix --field longitude --limit 4
```

Expect timestamped latitude and longitude values. If `/fix` or a field is absent, check the selected recording before editing the EventSpec.

## Source points and record their origin

Acquire geographic points outside the recording and supplied kit, by manual research or tools. Sourcing may need connectivity. No paid model or API key is required. Record the source URL or citation, access date, method, coordinate reference, and relevant reuse terms for each point in `working-points/extension/provenance.md`. Do not include credentials, private paths or raw recordings.

Replace the illustrative points in your copy of `cave-zones.json`. Illustrative coordinates do not establish real encounters. The resource has exactly these top-level fields:

```json
{
  "contract": "civ.point-resource/v1",
  "coordinate_reference": "EPSG:4326",
  "points": [
    {"id": "illustrative-a", "latitude": 49.2583, "longitude": 4.0317}
  ]
}
```

Use WGS 84 decimal degrees, unique non-empty IDs and at least one point. Latitude must be finite and between -90 and 90; longitude must be finite and between -180 and 180. The schema is `schemas/civ.point-resource.v1.schema.json` in the kit.

The copied EventSpec binds `caves` to `cave-zones.json` relative to the EventSpec directory. Keep that file beside `detector.yaml`. Resource paths use `/`, stay inside that directory, and cannot be absolute paths or URLs. `min_distance_to` computes the nearest point's distance in metres using the latitude and longitude signals. The example condition accepts distances at most 40 metres. Its timing rules merge nearby detections; they do not identify individual places. The reserved `detector:` field cannot run custom code.

## Detect and inspect the evidence

```text
civ detect working-points/detector/detector.yaml data/REIMS_SIGNALS.mcap --output working-points --dry-run
civ detect working-points/detector/detector.yaml data/REIMS_SIGNALS.mcap --output working-points
civ clip working-points/events.jsonl data/REIMS_SIGNALS.mcap
```

Expect `events.jsonl`, `run-manifest.json`, the exact resource copy under `detector/`, and `extension/manifest.json`. The run manifest records the resource's SHA-256. Each extension entry records `kind`, `media_type`, archive-relative `path`, and lowercase `sha256`. Detection declares the copied point resource as `external-resource` at `detector/cave-zones.json` with media type `application/json`.

Inspect detected intervals and their `cave_distance_m` trigger values. Open local clips in a supplied viewer or sample the same GNSS interval. Zero events can be valid, especially with illustrative points. Check locations, coordinate units, timing and the distance threshold before changing them. Clips remain local.

Record the practice evaluation state without accessing truth:

```text
civ score working-points
```

Expect `working-points/metrics.json` with `status: "not_evaluated"`, null metrics, and its hash in the run manifest. These are unknown scores, not a failure or zero performance. Continue to reporting. Do not substitute turn labels, invent an empty truth pack, or make a reference from your detections. Organizers replay your submitted EventSpec and locations privately and use the common temporal IoU matcher and F1 to calculate the separate bonus of up to 10 points. See the [scoring reference](https://github.com/Forerunner2012/civ2026-data-hackathon/blob/develop/docs/reference/scoring.md).

## Declare provenance and package

After the last detection run, finish `extension/provenance.md`. Compute its exact file hash:

```sh
sha256sum working-points/extension/provenance.md
```

Append this entry to the existing `entries` array in `working-points/extension/manifest.json`, replacing the hash placeholder with the printed 64-character hash:

```json
{
  "kind": "provenance",
  "media_type": "text/markdown",
  "path": "extension/provenance.md",
  "sha256": "REPLACE_WITH_EXACT_LOWERCASE_SHA256"
}
```

Keep `contract` equal to `civ.submission-extension/v1`. Preserve the generated resource entry and sort all entries by `path`. Do not declare the manifest itself. Recompute the hash after editing provenance. Rerunning detection regenerates the extension manifest, so add your provenance declaration again after the final run.

The extension allows at most eight payloads, 1 MiB per payload and 4 MiB combined. Optional `agent-trace` and `regression-test` entries require the same exact hashes and supported text media. Intake treats those files as data and never executes them. The kit's `schemas/civ.submission-extension.v1.schema.json` defines the declaration.

Finish the report, figure, reproduction script and required metrics as described in the [QuickStart](quickstart.md#8-validate-and-keep-the-metadata-only-zip). Make the reproduction script use the bundled EventSpec and resource with the same recording. Then run:

```text
civ report working-points
```

Expect `working-points/submission.zip` and its SHA-256. An undeclared, changed, missing or oversized payload causes validation to fail. Submit only the validated ZIP and its printed hash. Recordings, clips, labels, caches and credentials stay out of the bundle.

The Cave bonus is automatic and separate from manual Evidence and other bonus awards. The existing agent-trace, advanced-method, and regression-test bonuses remain available under their own criteria; Cave participation alone does not earn them. See the [current point allocation](https://github.com/Forerunner2012/civ2026-data-hackathon/blob/develop/docs/reference/scoring.md#point-allocation).
