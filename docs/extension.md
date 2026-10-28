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

Finish `extension/provenance.md`, the report, figure, reproduction script and metrics before packaging. Declare provenance with:

```text
civ report working-points --extension provenance extension/provenance.md
```

Paths are relative to the submission workspace, not the shell's current directory. The command hashes the exact payload bytes, preserves other declarations, validates the full extension, and writes the sorted `extension/manifest.json` before packaging. It does not edit or execute payloads. The manifest keeps contract `civ.submission-extension/v1`.

After editing a declared payload, repeat its `--extension KIND PATH` argument to refresh that hash. An unrelated changed or invalid declaration remains an error. All requested declarations are validated together before the manifest is replaced. A later packaging failure leaves the valid declarations saved, so complete the core artifacts and retry `civ report`.

Rerunning detection preserves valid non-resource declarations and refreshes generated resource entries. If an edited payload has a stale hash, explicitly refresh its declaration before detection. Detection does not silently accept changed payload bytes. For a fresh reproduction workspace, copy the detector/resources and extension payloads plus manifest before detection.

The extension allows at most eight payloads, 1 MiB per payload and 4 MiB combined. Optional `agent-trace` and `regression-test` entries require the same exact hashes and supported text media. Intake treats those files as data and never executes them. The kit's `schemas/civ.submission-extension.v1.schema.json` defines the declaration.

## Include a grounded trace and a failure-derived test

These examples show the shape of participant-authored evidence. Replace every placeholder with observations from tools you actually ran and artifacts you produced. Do not claim that this illustrative example is your own executed work. Packaging validates structure and hashes; it does not grant bonus eligibility.

For `extension/agent-trace.jsonl`, retain a short tool-to-artifact chain. For example, one JSON record per actual invocation:

```json
{"tool":"civ detect","arguments":["detector/detector.yaml","SOURCE_NAME","--output","working-points"],"exit_code":0,"inputs":{"source_sha256":"ACTUAL_SOURCE_SHA256","spec_sha256":"ACTUAL_SPEC_SHA256"},"outputs":[{"path":"events.jsonl","sha256":"ACTUAL_EVENTS_SHA256"}],"observation":"ACTUAL_EVENT_ID and interval support the claim in report heading 4"}
```

The grounded-trace bonus requires claims linked to executed tools and produced artifacts in the accepted v2 extension. A transcript outside the accepted ZIP, prompt style, confidence, transcript length and model choice do not qualify. Include no credentials, private absolute paths, raw recordings or labels.

For `extension/regression-test.json`, connect one demonstrated failure to a check that would catch its return. An inert example for an overlong merged candidate is:

```json
{
  "failure_evidence": {"artifact":"report.md","section":"One failure and the resulting change","observation":"REPLACE_WITH_ACTUAL_RECORDED_FAILURE"},
  "case": {"condition_hit_times_ns":[0,1000000000,2000000000],"min_duration_ns":0,"merge_gap_ns":1100000000,"max_duration_ns":1000000000},
  "check": {"expected_event_count":0,"would_catch":"Emitting or capping a merged interval that exceeds maximum duration"}
}
```

The test's synthetic interval is 2 s long and exceeds its 1 s maximum. Adapt the case to your demonstrated failure and resulting change. A generic checksum check or an unconnected hypothetical failure does not establish eligibility. This JSON is an inert test specification for review, not an executable test runner. Organizers never execute submitted tests.

Declare the actual files together with provenance:

```text
civ report working-points --extension provenance extension/provenance.md --extension agent-trace extension/agent-trace.jsonl --extension regression-test extension/regression-test.json
```

Inspect the ZIP using a local archive viewer. It must contain the exact declared payload paths plus `extension/manifest.json`; each entry's lowercase SHA-256 must match that member's bytes. Reopening and validating the ZIP confirms inclusion, not the truth of the claims. Submit that unchanged ZIP and its printed hash.

Finish the report, figure, reproduction script and required metrics as described in the [QuickStart](quickstart.md#8-validate-and-keep-the-metadata-only-zip). Make the reproduction script use the bundled EventSpec and resource with the same recording. Then run:

```text
civ report working-points
```

Expect `working-points/submission.zip` and its SHA-256. An undeclared, changed, missing or oversized payload causes validation to fail. Submit only the validated ZIP and its printed hash. Recordings, clips, labels, caches and credentials stay out of the bundle.

The Cave bonus is automatic and separate from manual Evidence and other bonus awards. The existing agent-trace, advanced-method, and regression-test bonuses remain available under their own criteria; Cave participation alone does not earn them. See the [current point allocation](https://github.com/Forerunner2012/civ2026-data-hackathon/blob/develop/docs/reference/scoring.md#point-allocation).
