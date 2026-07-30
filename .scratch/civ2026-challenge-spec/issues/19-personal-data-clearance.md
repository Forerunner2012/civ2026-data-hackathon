# Is the camera imagery clear to redistribute?

Type: task
Status: open

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

## Why this is the highest-urgency item on the board

It gates the camera topic, which gates the evidence experience, the viewer decision (ticket 10)
and the subset size (ticket 17). Track A costs an afternoon and removes the central unknown.
Track B costs one email to someone already on the committee. At 35 days, both should have started
before anything else on this map.

## Note

T-Lab publishing these frames themselves under CC BY 4.0 is a materially different posture from
a private transfer, but it does not extinguish Heex's own obligations when Heex further
distributes the same material.
