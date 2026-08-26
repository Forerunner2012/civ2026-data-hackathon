# EventSpec local point resources

Status: **candidate contract for issue #17; stable promotion remains deferred to #20**

EventSpec may join a small, participant-visible local point set to live latitude/longitude signals
without a network lookup, organizer state, or executable detector extension. The module accepts one
resource contract: `civ.point-resource/v1alpha1`. Its machine-readable schema is
`schemas/civ.point-resource.v1alpha1.schema.json`.

## Binding

An EventSpec binds a resource by a portable path relative to its own directory:

```yaml
resources:
  caves:
    path: cave-zones.json
    contract: civ.point-resource/v1alpha1
```

Paths use POSIX `/` separators, must remain inside the EventSpec directory, and cannot be absolute,
parent-relative, or URLs. Detection reads the bytes locally and verifies that the file contract
matches the binding. No network primitive is used.

`detector:` is reserved for a later extension. Any present `detector:` field is rejected with a
correction; this candidate contract does not execute Python or another custom detector.

## Point resource

```json
{
  "contract": "civ.point-resource/v1alpha1",
  "coordinate_reference": "EPSG:4326",
  "points": [
    {"id": "cave-a", "latitude": 49.2583, "longitude": 4.0317}
  ]
}
```

Coordinates are WGS 84 decimal degrees. Latitude is in `[-90, 90]`; longitude is in `[-180, 180]`.
Both must be finite numbers. Point IDs are non-empty and unique. At least one point is required.
Points are ordered lexicographically by ID after validation so source-file ordering cannot affect
lookup behavior.

Rejected examples include:

- an empty `points` list: add at least one point;
- `EPSG:3857`: convert the resource to `EPSG:4326`;
- latitude `91`: provide a value between -90 and 90;
- duplicate point IDs: keep each ID once; and
- an unknown contract: provide `civ.point-resource/v1alpha1`.

Each failure names the resource and invalid field. An invalid live latitude or longitude similarly
names the `min_distance_to` derivation and required range.

## `min_distance_to`

The resource is exposed through a declarative derivation; CEL receives only its scalar result:

```yaml
derive:
  cave_distance_m:
    op: min_distance_to
    resource: caves
    from: [latitude, longitude]
condition: cave_distance_m <= 40.0
```

`from` is exactly `[latitude, longitude]`. Distance is the shortest haversine great-circle distance
to any point, in metres, using the fixed IUGG mean Earth radius `6,371,008.8 m`. The result is rounded
to six decimal places before CEL evaluation. Consequently an exact 40 m result satisfies `<= 40.0`,
while a 40.001 m result does not. Ties have the same scalar result; lexicographic point ordering
makes lookup traversal deterministic.

## Provenance and submission behavior

The run manifest records resources sorted by EventSpec binding name:

```json
{
  "resources": [
    {
      "contract": "civ.point-resource/v1alpha1",
      "name": "caves",
      "path": "cave-zones.json",
      "sha256": "...64 lowercase hexadecimal characters..."
    }
  ]
}
```

The SHA-256 covers the exact resource bytes used by detection. The copied EventSpec and manifest are
submitted, but the external resource bytes are not copied into the working detector directory or
metadata-only submission bundle. Reproduction therefore requires the declared local resource to be
restored beside the source EventSpec. The checked-in Reims example uses illustrative coordinates;
organizer coordinates and encounter intervals remain external.

Sorted resource hashes also participate in event identity when resources are present. Resource-free
EventSpecs retain their existing candidate event identities and output bytes.
