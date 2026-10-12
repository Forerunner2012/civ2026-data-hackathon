# Add external geographic points to an EventSpec

First reproduce the core workflow in the [QuickStart](quickstart.md). This optional exercise adds participant-sourced geographic points to a Reims EventSpec. Keep supplied kit files read-only. Run commands from the unpacked kit root after [installing civ](setup.md).

## Prepare a separate workspace

Create the submission templates and copy the illustrative examples. In PowerShell:

```powershell
civ submission-init working-points --shell powershell
New-Item -ItemType Directory working-points/extension | Out-Null
Copy-Item examples/reims/cave-encounter.yaml working-points/detector/detector.yaml
Copy-Item examples/reims/cave-zones.json working-points/detector/cave-zones.json
```

In a Linux shell:

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

Use a complete, matching practice pack for this geographic-point event only if one is explicitly supplied. Turn labels measure a different event and cannot validate geographic encounters. Otherwise inspect events manually and follow the coach's scoring instructions before packaging. Do not substitute turn labels or create a reference from your detections. The [scoring reference](https://github.com/Forerunner2012/civ2026-data-hackathon/blob/develop/docs/reference/scoring.md) explains the existing policy. Online reference lookup needs connectivity; detection uses local files.

With an explicitly supplied, matching geographic-point practice pack, run:

```text
civ score working-points --labels PRACTICE_POINTS_LABELS.json
```

Expect `working-points/metrics.json` and its hash in the run manifest. Replace the placeholder with the supplied local pack path.

## Declare provenance and package

After the last detection run, finish `extension/provenance.md`. Compute its exact file hash. In PowerShell:

```powershell
(Get-FileHash working-points/extension/provenance.md -Algorithm SHA256).Hash.ToLowerInvariant()
```

In a Linux shell:

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

Finish the report, figure, reproduction script and required metrics as described in the [QuickStart](quickstart.md#8-validate-package-and-submit). Make the reproduction script use the bundled EventSpec and resource with the same recording. Then run:

```text
civ report working-points
```

Expect `working-points/submission.zip` and its SHA-256. An undeclared, changed, missing or oversized payload causes validation to fail. Submit only the validated ZIP and its printed hash. Recordings, clips, labels, caches and credentials stay out of the bundle.

The core must reproduce before bonus evidence can count. This exercise alone does not earn every bonus award. See the [approved bonus anchors](https://github.com/Forerunner2012/civ2026-data-hackathon/blob/develop/docs/phase5/extension-aware-submission-v2.md#bonus-anchors).
