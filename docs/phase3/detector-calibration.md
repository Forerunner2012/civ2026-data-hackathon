# Phase 3 detector calibration

Status: **accepted for the two-dataset calibration gate**

Recorded: 2026-08-29

The organizer approved four development-only calibration profiles before sealed execution, then
approved the resulting interpretation and retained the provisional **15 Kashiwa / 10 Reims**
Detection allocation. The total Detection budget remains 25 points.

Profile definitions, instantiated runs, label packs, per-product results, source identities, and
sealed intervals remain organizer-only artifacts outside git. This record contains only aggregate
metrics, immutable hashes, and the approved interpretation.

## Preregistration boundary

The competent-timed, route-overfit, naive-single-threshold, and no-debounce profiles were built from
12 development products: seven Kashiwa and five Reims. The development evidence contained 18
normalized Kashiwa intervals after one overlapping human-adjustment ambiguity was excluded, and six
Reims intervals. No sealed product or label pack was opened until the organizer approved profile-set
SHA-256 `bf68005d97892263162e28feaf9fb3325c48a9dc39d223a519ef8eee87f72dcf`.

The preregistered qualitative roles were:

- competent-timed: a directional signal with development-timed persistence and debounce;
- route-overfit: a deliberately tight route and speed signature expected to lose recall under
  distribution shift;
- naive-single-threshold: one directional threshold with reference timing; and
- no-debounce: the same naive signal with only short continuity merging, expected to fragment.

Development F1 separated the profiles without sealed tuning:

| Profile | Kashiwa | Reims |
|---|---:|---:|
| Competent-timed | 0.864865 | 0.526316 |
| Naive-single-threshold | 0.666667 | 0.357143 |
| Route-overfit | 0.486486 | 0.166667 |
| No-debounce | 0.265306 | 0.250000 |

## Frozen sealed execution

All four frozen profiles ran against every sealed product: eight Kashiwa and four Reims. Every run
used temporal IoU `0.5`, deterministic one-to-one best matching, duplicate false positives, and F1.
No evaluator setting or profile changed after sealed results became visible.

| Dataset | Profile | Precision | Recall | F1 | Mean matched IoU |
|---|---|---:|---:|---:|---:|
| Kashiwa | Competent-timed | 0.840000 | 0.913043 | 0.875000 | 0.880912 |
| Kashiwa | Naive-single-threshold | 0.512195 | 0.913043 | 0.656250 | 0.880912 |
| Kashiwa | Route-overfit | 0.652174 | 0.652174 | 0.652174 | 0.621418 |
| Kashiwa | No-debounce | 0.220930 | 0.826087 | 0.348624 | 0.680009 |
| Reims | Naive-single-threshold | 0.562500 | 1.000000 | 0.720000 | 0.825388 |
| Reims | No-debounce | 0.473684 | 1.000000 | 0.642857 | 0.801308 |
| Reims | Competent-timed | 0.428571 | 0.666667 | 0.521739 | 0.704558 |
| Reims | Route-overfit | 0.000000 | 0.000000 | 0.000000 | 0.000000 |

The organizer result SHA-256 is
`59970d9350fdcd9489aaf93a0bce9d1de30ab2cf85ebb84d262f70fc118d74c4`. The aggregate-only review
SHA-256 is `88294a1244a14de7bf632c3c681db535ebfb5a8c8257797b0cca78492c01a636`.
Running the same approved profile bytes against the independently reproduced products and packs
reproduced both files byte-for-byte, together with the approval and execution-manifest files.

## Interpretation

Kashiwa retained the expected competent-timed lead. Reims inverted that expectation: the naive
profile ranked first, no-debounce ranked second, and competent-timed ranked third. The organizer
classified this as a **profile flaw exposed by real dataset behavior**, not an evaluator flaw:

- the fixed evaluator behaved consistently across every profile;
- the naive Reims profile recovered all targets with better temporal overlap;
- the competent profile's additional speed and persistence assumptions missed targets and produced
  poorer temporal boundaries; and
- the deliberately route-specific Reims profile's collapse is consistent with distribution shift.

Only the leading profile on each dataset reached 90 percent of that dataset's best F1. The Kashiwa
gap between first and second was `0.218750`; the Reims gap was `0.077143`. The naive profile was not
best on both datasets, so the evidence does not support one universal magic threshold.

## Approved point allocation

Applying the retained 15/10 maxima to F1 gives this review projection:

| Profile | Kashiwa / 15 | Reims / 10 | Total / 25 |
|---|---:|---:|---:|
| Competent-timed | 13.125000 | 5.217391 | 18.342391 |
| Naive-single-threshold | 9.843750 | 7.200000 | 17.043750 |
| No-debounce | 5.229358 | 6.428571 | 11.657929 |
| Route-overfit | 9.782609 | 0.000000 | 9.782609 |

The larger Kashiwa membership supports its 15-point share, while the 10-point Reims component is
large enough to change the combined ordering and expose transfer failure. The organizer approved
the interpretation and allocation without adjustment. The organizer-only approved interpretation
has SHA-256 `dc8a2f65bd3ce67a31d836a57a251ba970c7423d29f0be2ce1c3786894b278f7`.

## Leakage boundary

The public evidence contains no sealed interval, event identity, source identity, per-product
metric, label-pack payload, organizer path, or detector output. Instantiated calibration artifacts
and runtime state remain outside git and participant distributions.
