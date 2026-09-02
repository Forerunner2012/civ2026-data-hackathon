# What example does the `timing` teaching unit use, before the Kashiwa solution unlocks?

Type: task
Status: open

> **Rewritten for clarity.** The first version of this ticket described a three-hour live rabbit and
> was hard to follow once that rabbit no longer existed. The question is much smaller than it looked.

> **Smaller again, after [17](17-attendee-page.md)'s update.** The organizer's rule for hints is
> *show a real command on the real dataset, with an example that is deliberately not the expected
> answer.* That removes the risky half of this ticket:
>
> **The over-count is guaranteed by sampling, not by the data.** A condition that stays true across a
> two-second manoeuvre at 100 Hz produces ~200 sample hits and one event — whatever the signal is. So
> the *demonstration cannot fail*, and the "is the ratio dramatic?" check below is no longer a risk,
> only a way to get real numbers to print.
>
> **Option B is therefore unnecessary** and option A is safe. What genuinely still needs eyes on data
> is the **honest false positive** — that one cannot be derived from first principles.

## The question, plainly

At **10:20** ([03](03-cadence.md)'s beat B2), [the attendee page](17-attendee-page.md) teaches the
single most important mechanic in the toolchain:

> A naive threshold fires on every *sample* where the condition is true. `timing` — `min_duration`
> and `merge_gap` — is what turns those samples into *intervals*, i.e. into events.

[Ticket 09](../../civ2026-challenge-spec/issues/09-detector-authoring-surface.md) calls this the
non-negotiable rung: *without `timing`, a team emits one detection per sample where yaw rate was
high, not one per turn.* Shown, it takes fifteen seconds. Not shown, most people discover it at 11:30
by scoring badly.

**The demonstration needs an example. It cannot be the real one.** The Kashiwa turn detector does not
unlock until 11:00 ([03](03-cadence.md)'s B4), so demonstrating `timing` on it at 10:20 would hand
over the answer forty minutes early and compress Kashiwa's 15 Detection points further than
[17](17-attendee-page.md) intends.

**So: what does it demonstrate on instead?**

## The options

| | Example | For | Against |
|---|---|---|---|
| **A** | **Hard braking on the published warm-up route.** Real data the participant already holds | Credible, reproducible by the participant, and unmistakably not a turn — [ticket 09](../../civ2026-challenge-spec/issues/09-detector-authoring-surface.md) notes the prior INBOX example was already hard-braking | Needs one check against real data, which nobody has done |
| **B** | A **tiny synthetic trace** shipped with the kit | Zero data dependency. Guaranteed to produce a dramatic over-count because it is built to. Closes this ticket immediately | Reads as a textbook exercise rather than *your data, your problem*, which is most of why the moment lands |
| **C** | The **real turn detector**, accepting early release | No new asset at all | Gives away the Kashiwa answer at 10:20 and undercuts [03](03-cadence.md)'s cliff design, where the solution's arrival at 11:00 is what makes abandoning possible |

**Recommendation: A, with B as the fallback** if the data does not cooperate. C is a real option only
if the organizers decide Kashiwa should be almost entirely un-scored, which is a bigger decision than
this ticket.

## Why this is a task, and what it needs

**One check, once, at authoring time.** The participant never has to reproduce it — they need to
*see* it — so this is an organizer running a few commands on one route and writing down what came
out. Roughly twenty minutes.

- [ ] Run a naive deceleration threshold over the **Kashiwa warm-up route**. Record the raw hit count.
- [ ] Apply `timing` (`min_duration`, `merge_gap`). Record the collapsed count.
- [ ] **Confirm the ratio is dramatic.** The draft narration uses 41 → 6. If the real numbers are
      7 → 6, the demonstration is dead and the answer is option B.
- [ ] Find **one honest false positive** among the detections — the draft guesses a speed bump;
      anything defensible will do. This matters as much as the count: it is the only place in the
      design that shows §2's *failure is a deliverable* claim **before** a participant is asked to
      produce one.
- [ ] Write the resulting spec down. It is a **kit teaching asset**, not a scored artifact.

## Ride-along: measure Kashiwa per-topic bytes while you are there

Map one's [ticket 17](../../civ2026-challenge-spec/issues/17-dataset-subsetting-and-distribution.md)
closes with *Kashiwa has not been measured — run `mcap du` on one Kashiwa route before fixing the
numbers.* It is the **same machine, the same bag and the same session** as the check above, so do
both in one trip.

**It matters much less than it did.** The original reason was sizing physical distribution, and
[07](07-pre-event-readiness-and-reveal.md)'s four 2 TB SSDs made that moot. Two reasons survive, both
small:

1. **The pre-event download size has to be true.** [07](07-pre-event-readiness-and-reveal.md) tells
   participants signals-only downloads in seconds. That is measured for Reims (~350 MB for 38
   minutes) and *inferred* for Kashiwa, which carries **uncompressed** `image_raw` plus clustering
   point clouds. The inference is almost certainly right; it is still an inference in a document
   participants will act on.
2. **The camera retention decision depends on it.**
   [Ticket 17](../../civ2026-challenge-spec/issues/17-dataset-subsetting-and-distribution.md) wants
   `/sensing/camera/traffic_light/image_raw` kept at ~5 Hz and 640×360, and
   [ticket 10](../../civ2026-challenge-spec/issues/10-visualization-surface.md)'s evidence and
   visualization value rests on a camera stream existing. If the reduction does not land, that
   contingency fires.

Adds about ten minutes: `mcap du` on one route, then the same after dropping point clouds and the
map and rate-limiting the camera.

## Ride-along 2: count the event types properly

Organizer's note, explicitly deferred: **recheck the recordings for a better count of event-specific
types.** Same trip, same machine.

It matters for exactly one thing — how many categories the answer key carries.
[Ticket 03](../../civ2026-challenge-spec/issues/03-scoring-basis.md) scores **only** the turn that
crosses oncoming traffic, so any other category is optional colour: useful for the extension track
and for the report's *what else did you find*, worth nothing on the 25 points. So this is a
nice-to-have on the trip, not a gate.

## Access note — the one thing this map cannot do

This map holds no bag data, and the paths in map-one
[tickets 17](../../civ2026-challenge-spec/issues/17-dataset-subsetting-and-distribution.md) and
[24](../../civ2026-challenge-spec/issues/24-survey-reims-bag.md) (`D:\Bags`, `C:\Program
Files\MCAP`) are **provenance from another machine**, not dependencies.

**This is the only ticket on the map that cannot be resolved from the repository.** Hand it to
whoever has the data with the checklist above; do not wait on it, because option B is a complete
answer if the check is inconvenient.

## Why this is on the frontier

Nothing blocks it and it blocks nothing — [17](17-attendee-page.md)'s design holds whichever example
is chosen. It is a small build dependency with a lead time: the unit cannot be authored until the
example exists.
