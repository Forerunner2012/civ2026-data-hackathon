# How is the URT evaluator calibrated?

Type: grilling
Status: open
Blocked by: 06, 09, 18

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

## Why it is blocked

Ticket 09 has to produce a real URT detector first — you cannot calibrate against submissions
whose shape is unknown. Ticket 06 supplies the only pre-existing outcome data to sanity-check
against.

## Note

This is where care pays off most. Calibration is not a coding problem — it needs real detector
runs against real bags and a human judging whether the ranking that comes out is the one a jury
would defend. Ticket 06 established there is no historical calibration data to lean on, so the
internal mini-hackathon is where this gets validated.
