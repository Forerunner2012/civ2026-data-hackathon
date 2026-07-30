# Zone-monitoring extra track: champagne caves by GNSS

Type: grilling
Status: resolved

## Question

Proposed extra track on the French-city recording, using **localisation rather than kinematics**:
detect every occurrence of the vehicle passing in front of a champagne cave.

The chain:

1. Take GNSS position from `/fix` (`sensor_msgs/NavSatFix`), with `/fix_velocity` for speed.
2. Acquire the locations of the champagne caves in the city — **external data, not in the bag**.
3. Express zone monitoring as an EventSpec condition, producing timestamped intervals.
4. Extract evidence clips around each occurrence with the existing machinery.

## Why this is a strong addition

- **It exercises a different axis.** Kashiwa and the transfer task are both kinematic — yaw rate,
  speed, sign conventions. This is spatial. A team that has only ever written threshold conditions
  has to think about position, proximity and dwell.
- **It gives the agent track real work.** Ticket 12 scores an agent on a trace pointing to
  executed tools and evidence, and ticket 11 ships no model — which left the agent story thin for
  this edition. "Go and find where all the champagne caves are, geocode them, and emit a zone
  spec" is a genuinely bounded task with a **verifiable** output, which is exactly the shape a
  scored agent trace needs.
- **The ground truth may be computable rather than labelled.** Given a correct zone list and GNSS,
  the intersections are derivable. That would make this the only scored artifact in the event that
  needs no labelling pass — the difficulty moves into *acquiring the right zones*, not into
  agreeing what counts as an event.
- It is memorable. A room in Miyazaki will remember the detector that found champagne cellars.

## What has to be settled

- **Who acquires the zone list**, and does that require network access? This is the crux — see the
  grilling question. The required path is offline by §3.3, but a bonus track need not be.
- **Does EventSpec need a spatial primitive?** Haversine distance is expressible in CEL
  arithmetic but unpleasant. Cleaner options: a `derive` op such as `distance_to(lat, lon)`
  (ticket 09's rung 2), or a dedicated `zones:` block with named circles or polygons. Either is a
  schema extension and should be decided before EventSpec is frozen, not after.
- **Dwell versus pass.** Is passing at 50 km/h an occurrence, or does it require slowing? The
  `timing` block from ticket 09 already handles minimum duration, which may be enough.
- **GNSS accuracy versus zone radius.** Urban multipath will move fixes by metres. Zone radius has
  to absorb that, and the tolerance interacts with ticket 16's matching semantics.
- **Scored or judged?** If the truth is computable, this could carry points; if the interest is in
  the acquisition, qualitative judgement may fit better.
- **Which city, and are the caves actually on the route?** Determinable by decoding `/fix` from the
  bag — folded into ticket 24's survey.

## Relationship to the other extra track

Ticket 09 deferred rung 3 — Python detectors and conflict geometry — to "the organizer demo and an
extra track". This is a *second* candidate for that slot. They are not obviously the same track:
one is about geometric reasoning over perception output, the other about external data acquisition
and spatial predicates. Decide whether the extra track holds both, one, or splits in two.

## Answer

**Participants acquire the zone list themselves — by any means. The point is not the agent; it is
that things plug in and out.**

Fully scripted agent workflow, a conversation with a chat assistant, an OpenStreetMap query, or
twenty minutes with a map and a spreadsheet are all legitimate. **Method is deliberately
unconstrained**, because the lesson is that the horizon extends past the pipeline they were
handed.

### Rename the idea: this is the extension track

Calling it an "AI agent track" undersells it and mis-frames what is being taught. What a
participant should leave with is: *the system took knowledge that was never in the bag, and used
it to find events I could not otherwise have found.* An agent is one convenient way to fill that
gap, not the gap itself.

This also unifies the extra track. Ticket 09 deferred rung 3 — Python detectors and conflict
geometry — to "the organizer demo and an extra track". Both that and this are the same move:
**extend the system past what was provided.** One extends the *computation*, the other extends the
*inputs*. One track, two exemplars.

### The design consequence: EventSpec needs an external-resource seam

For things to plug in, the zone list must be a **referenced artifact**, not something baked into a
condition. That is a schema extension on top of ticket 09 and should land before EventSpec is
frozen:

```yaml
resources:
  champagne_caves:
    type: geojson              # or csv: name, lat, lon, radius
    path: ./zones/caves.geojson

signals:
  gnss:  { topic: /fix, field: "" }              # NavSatFix lat/lon
  speed: { topic: /fix_velocity, field: twist.twist.linear.x }

derive:
  dist_to_cave: { from: gnss, op: min_distance_to, resource: champagne_caves }

condition: dist_to_cave < 40.0 && speed > 0.5

timing:
  min_duration: 1.0s
  merge_gap: 5s

evidence:
  before: 3s
  after: 3s
  topics: [ /fix, /zed/zed_node/rgb/image_rect_color/compressed ]
```

Two things this buys beyond the champagne caves:

- **The seam is general.** Any external dataset — POIs, map geometry, road classifications, a
  weather log — plugs in through `resources:` the same way. That is the extensibility lesson made
  structural instead of rhetorical.
- **One new `derive` op carries it**: `min_distance_to`. The rest is the machinery that already
  exists.

### Scoring: qualitative, not against a sealed list

Judge it under the existing bonus, on whether the extension is real and defensible — not by
diffing against an organizer-held list of caves.

Reason: if method is free and acquisition is the exercise, scoring against a sealed reference
punishes someone who found eight of eleven caves through sound reasoning, and rewards whoever
happened to hit the best data source. What matters is that the zones are plausible, the predicate
is sound, the evidence clips actually show a cave, and the participant can say where the knowledge
came from. That is also precisely what ticket 12 asks an agent trace to demonstrate.

### Still to settle, and cheap

- **Zone file format** — GeoJSON, or a flat CSV of `name, lat, lon, radius`. CSV is friendlier to
  hand-editing and to a chat assistant emitting a list; GeoJSON handles polygons. Recommend CSV
  for the seed contract, with GeoJSON accepted.
- **Radius versus road-to-resource distance.** Ticket 24 measured sub-metre typical jitter, so
  GNSS error is not the binding constraint. The seed radius is 40 m because the road passes
  Martel at 15.6 m and Pommery at 35.7 m. The `timing.min_duration` block suppresses glancing hits.
- **City and route viability** — ticket 24 identifies Reims and two clear 40 m encounters. This
  is a small extension exercise, not a many-cave hunt.

## Update - measured GNSS characteristics

From `mcap info` on the French recording:

- **`/fix` (NavSatFix) is 4 Hz**, and `/fix_velocity` likewise. At 50 km/h that is ~3.5 m of travel
  between fixes; at 30 km/h, ~2 m.
- `/tf` runs at 229 Hz and `/zed/zed_node/imu/data` at 191 Hz, so the *pose* is available far more
  finely than the *fix* - worth knowing if zone entry timing needs to be sharper than 250 ms.

Consequences for the zone predicate:

- **Correction:** 4 Hz does not require a tens-of-metres radius. At 50 km/h the vehicle travels
  ~3.5 m between fixes; it cannot cross a 10 m-radius zone between adjacent samples on a
  centreline pass. The earlier claim that it could was arithmetic error.
- Ticket 24's stationary analysis found 0.26 m median per-stop p95 radial jitter, 0.81 m at the
  95th percentile of stops and 1.32 m maximum observed displacement. Sampling and jitter are both
  adequate.
- A **40 m seed radius** is still appropriate, but because of the measured road-to-address
  geometry: Martel is 15.6 m from the track and Pommery 35.7 m. Ruinart at 65.4 m should not be
  pulled in by silently inflating one global radius.
- `timing.min_duration` should remain sample-aware. A 1 s default is legible at 4 Hz and rejects
  isolated fixes without turning the exercise into parameter tuning.
