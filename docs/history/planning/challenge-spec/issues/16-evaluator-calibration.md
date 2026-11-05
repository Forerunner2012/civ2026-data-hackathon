# How is the URT evaluator calibrated?

> Historical planning. Follow the [archive index](../../README.md) for current guides and record boundaries.

Type: grilling
Status: resolved
Blocked by: 09

## Question

§5 Phase 3 requires temporal matching tolerance, a duplicate policy, missing-data cases, and
calibration "against multiple deliberately different detectors". Ticket 03 fixed the scoring
basis; this decides the semantics that make it fair.

What has to be settled:

- **Temporal tolerance:** how close must a detection be to a sealed URT label to count? A turn
  is an interval, not an instant — is the match on overlap, midpoint, or onset?
- **Duplicates:** one team emits three overlapping detections for one turn. One true positive
  and two false, or one true positive?
- **Missing data:** a bag with a gap in the localization topic — excluded, or scored with the
  gap as an expected challenge?
- **Partial credit:** is a detection that fires on the right turn but with a badly framed
  evidence window a hit for Detection and a miss for Evidence, or partly both?
- **Calibration set:** which deliberately different detectors do you run against it — a naive
  threshold, a good declarative spec, a deliberately overfit one? You need the score to
  separate them in the expected order before you trust it.

## Update after ticket 18

The definition is now **the right-turn manoeuvre interval**, so this ticket sharpens
considerably: it is interval matching, not conflict adjudication. And it inherits a
responsibility it did not have before — since detection no longer separates teams on cleverness,
**the tolerance semantics are what convert careful interval reasoning into points.** Set the
tolerance too loose and everyone scores the same; too tight and it rewards luck. That calibration
is now the single most consequential number in the rubric.

## Why it is blocked

Ticket 09 has to produce a real URT detector first — you cannot calibrate against submissions
whose shape is unknown. Ticket 06 supplies the only pre-existing outcome data to sanity-check
against.

## Note

This is where care pays off most. Calibration is not a coding problem — it needs real detector
runs against real bags and a human judging whether the ranking that comes out is the one a jury
would defend. Ticket 06 established there is no historical calibration data to lean on, so the
internal mini-hackathon is where this gets validated.

## Answer

Both labels and predictions are intervals (ticket 18), so the whole scheme is interval matching.

### Matching: temporal IoU ≥ 0.5

For a prediction `[p0, p1]` and a label `[l0, l1]`, IoU = intersection ÷ union. A match requires
IoU ≥ 0.5.

**Why IoU rather than "onset within ±1 s":** onset tolerance awards full marks to a detector that
fires at the right instant but runs thirty seconds long. IoU punishes a sloppy start *and* a
sloppy end — which is exactly the interval-precision skill ticket 18 left as the discriminator
after conflict geometry moved out of the core.

### Assignment: one-to-one, best match wins

For each label, the highest-IoU prediction above threshold becomes the true positive. Every other
prediction overlapping it is a **false positive**. Unmatched labels are false negatives.

**This is what gives `timing.merge_gap` teeth.** A team that skips debounce emits three
detections per turn and takes two false positives for it — converting the rung-1 requirement from
a schema field into something the score actually notices.

Report precision, recall and **F1** across all routes. F1 rather than raw counts, so no team can
win by flooding.

### Missing data

Where a required topic has a gap, exclude that window from **both** label and prediction sets.
Teams should not be punished for the organizers' data quality.

Kept separate: the one or two **deliberate** quality defects (§5 Phase 3) are scored under
*Quality and evaluation (15)*, not under Detection. Noticing and handling bad data is the lesson;
being silently penalised for it is not.

### Partial credit: none inside Detection

A match is a match. A correct interval with a badly framed evidence window loses points under
*Evidence and extraction (15)*. Keeping the categories orthogonal is what makes a disputed score
explainable in a 30-minute results slot.

### Calibration — the part that actually matters

Before trusting any of the above, run four deliberately different detectors:

| Detector | Expected rank |
|---|---|
| Competent rung-1 spec — condition + timing + evidence | 1st |
| Tuned to one route only | 2nd |
| Naive single threshold, no timing | 3rd |
| Correct condition, no debounce | 4th |

**If the evaluator does not produce that order, the tolerance or the matching rule is wrong — not
the detectors.** Tune the IoU threshold until the ranking is stable *and* the gaps are meaningful.
0.98 versus 0.97 is not a ranking, it is noise.

### The number to watch

If every team lands above 90, tolerance is too loose and Detection has stopped discriminating.
Post-ticket-18 that is the single largest scoring risk, and this calibration run is the only
place it gets caught before the room does.

All values here are **provisional until that run**. Ticket 06 established there is no historical
calibration data to lean on, so the internal mini-hackathon is where they get confirmed.

## Update - two sealed sets, two calibrations

Ticket 14's reversal means the evaluator scores transfer as well as detection.

The matching semantics above are unchanged and apply to both datasets: temporal IoU, one-to-one
best match, F1. What does not carry over is the **calibration**. The Reims recording comes from a
ZED IMU rather than Autoware localization, at different rates and with different noise
characteristics, on a continuous urban drive rather than staged campus routes. A tolerance tuned
on Kashiwa should not be assumed to hold - run the four-detector ranking check separately on each
set.

**Open sub-question this raises:** how the 100 points divide between Kashiwa detection and Reims
transfer. If transfer is where the difficulty now lives (ticket 20), the current 25-point
Detection category understates it, but loading too much onto transfer punishes anyone who stalls
on the second dataset. Belongs with the rubric rework in ticket 21.
