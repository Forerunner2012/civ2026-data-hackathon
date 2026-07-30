# Is the camera imagery clear to redistribute?

Type: task
Status: resolved

## Question

Graduated from ticket 05, which cleared copyright and explicitly did **not** clear personal data.

CC BY 4.0 §2(b)(1) does not license privacy or personality rights, and T-Lab has published **no
statement whatsoever** on consent, anonymisation, blurring or ethics review — verified across the
`LICENSE`, `README.md`, `CITATION.cff`, both lab pages, the Drive folder and the demo video.
"It's CC BY, so we're fine" is not available.

The bags carry `/sensing/camera/traffic_light/image_raw` and precise GNSS. Recording was on the
UTokyo Kashiwa Campus with, per the release post, "controlled interactions", "one pedestrian" and
"one opponent vehicle" — which *suggests* staged lab members rather than unwitting public, but
suggestion is not a consent record, and a staged pedestrian is still an identifiable person.

Two tracks, run in parallel:

**A. Look at the frames — no external dependency, available today.** Decode a sample of
`image_raw` across several routes and see whether identifiable faces or plates are present.
Three outcomes:

- none → record the finding with the sample method, keep the camera topic, move on;
- present → blur (an adaptation, so flag it as a modification under §3(a)(1)(b)) or drop the
  camera topic from the distributed subset. Dropping is cheap for the detector logic and
  expensive for the evidence experience — and it interacts with tickets 10 and 17;
- ambiguous → default to blurring and ask.

**B. One email to T-Lab.** Manabu Tsukada is the dataset's corresponding author *and* on the CIV
2026 organizing committee. Ask in a single message: consent status for the pedestrian and
opponent-vehicle driver; whether any anonymisation was applied; written confirmation that CC BY
4.0 covers the camera imagery specifically; comfort with use at an event supported by a
commercial sponsor; and whether future recordings will carry the same licence.

Then: whether Heex is controller or processor for the redistributed subset under GDPR Art. 3(1),
via its French establishment. That is a question for counsel once A and B land.

## Why it matters

It gates the camera topic, which feeds the evidence experience, the viewer decision (ticket 10)
and the subset size (ticket 17).

## Answer

**Closed by the organizers: the rights are in hand.** T-Lab is a participant in the hackathon,
not a distant third-party licensor, so the data relationship is direct and the copyright grant
(CC BY 4.0, ticket 05) is backed by an active collaboration with the publishing lab. Manabu
Tsukada is on the organizing committee.

The camera topic is therefore **cleared for use**, and the open question in ticket 05 is closed
with it.

Two things carried forward as ordinary kit work rather than blockers:

- **Attribution still travels with the data.** CC BY's one condition is unaffected by the
  collaboration — the `NOTICE` file and the attribution string from the research note ship with
  any redistributed subset. Sits in the map's fog with the rest of the licensing surface.
- **Look at the frames anyway, as part of building the subset.** Not for clearance — for
  knowing the data. Whoever cuts the subset (ticket 17) and writes the labels (ticket 18) has to
  open the camera topic regardless, and that is the natural moment to notice anything worth
  mentioning to T-Lab.

Research backing, retained for the record:
[`../research/05-kashiwa-redistribution-rights.md`](../research/05-kashiwa-redistribution-rights.md).
