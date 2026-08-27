# What must the attendee-experience rehearsal actually observe?

Type: grilling
Status: resolved

## Question

Graduated from the map's fog once [01](01-pace-car.md), [02](02-help-protocol.md) and
[06](06-fallback-and-recovery.md) chose their mechanisms.

This map's destination is *Phase 5 can rehearse it with no design question left open*. Phase 5 exists
as a gate — *a two-hour internal mini-hackathon completes with no organizer-only workaround* — but
nothing says what an attendee-experience rehearsal is **watching for**. A rehearsal that only checks
"did the software work" would pass while every mechanism this map installed silently failed.

## Update — the rehearsal is two people, and Arnaud is the test

Organizer's decision. It **replaces the six-observation checklist below** as the primary framing,
though the observations survive as what to watch for.

**The shape:** Matt runs it alone, wearing the organizer and attendee caps at once. **Arnaud plays
attendee only**, with access to the attendee page and the pace car and nothing else. It is
experimentation with the thing live, not a formal gate.

### The reframe: one fresh pair of eyes is worth more than a checklist

Arnaud is the only person available who **did not design any of this**. That makes the rehearsal's
real question much simpler than six observations:

> **Where does Arnaud stall, and what does he reach for when he does?**

Every mechanism in this map exists to be used by someone who has not read the map. A checklist run
by the person who wrote it tests the checklist. Arnaud tests the design.

Specifically, watch for the three things nobody can self-assess:

- **Does he open the page unprompted**, or does he ask Matt what to do next? Asking is the failure —
  it means the page is not the first thing he reaches for, and on the day there is no Matt per desk.
- **Does he stall at the 11:00 cliff?** It lost its solution handover
  ([17](17-attendee-page.md) Update 3) and is now carried by permission, pulled-forward hints and a
  coach. Arnaud is the only chance to see whether that is enough before thirty people meet it.
- **Is any hint or tip unreadable to someone who did not write it?** Every stall is a page unit to
  rewrite, and [13](13-coach-guide-and-checkpoints.md) already established that discovering these on
  the day is too late.

### What two people can and cannot test

Being honest about this matters more than pretending the rehearsal covers everything.

| Testable with two | Not testable — stays unknown until 3 September |
|---|---|
| `civ` runs on both stacks, offline | Will anyone **raise a help card**? |
| The page advances on schedule | Will anyone **pair up** when their laptop fails? |
| The form accepts a submission | Does a **per-beat sweep** catch a quiet staller? |
| 15–30 entries score inside the lunch window | Does a **room** self-diagnose against the page? |
| The 11:00 cliff, on one person | |
| **The analogue block's disagreement** — two people marking the same window is exactly the exercise | |

The right-hand column is the social half of the design, and it fails **softly**: if nobody raises a
card, coaches still sweep; if nobody pairs, a broken laptop still has the fallback pack. Accept the
gap rather than recruiting bodies to close it — but know it is there, and brief coaches to assume
those mechanisms may not fire.

Observation 4 lands unexpectedly well: **two people is the minimum and sufficient number** to
discover that experienced practitioners mark the same turn differently. Matt and Arnaud should do
this exercise **before** labelling the answer key, since it is the same act and it produces the
boundary convention the key depends on.

## Answer

**Six observations. Each one corresponds to a mechanism that has never been run, and each has a
stated failure signal — because most of these fail by looking fine.**

### The principle

Every mechanism here was chosen because it degrades **invisibly**. A pace car nobody reads still
looks like a pace car. A help card nobody raises looks like a room with no problems. So the rehearsal
must observe **behaviour**, not completion — and someone must be assigned to watch rather than
participate.

**Name a dedicated observer.** A rehearsal where everyone is a participant produces no observations.

### The six

| # | Observe | Passes if | Fails if | Owner mechanism |
|---|---|---|---|---|
| 1 | **Does anyone read the page unprompted?** | People open it between beats without being told | It is open in a tab nobody looks at, and personas ask a human what to do next | [17](17-attendee-page.md), [01](01-pace-car.md) |
| 2 | **Does anyone raise a card?** | At least one card goes up for side B during the run | Zero cards all session. This is the **most likely silent failure** — it means the affordance is not socially free, not that nobody was stuck | [02](02-help-protocol.md) |
| 3 | **Does the 11:00 cliff work?** | Someone with a poor Kashiwa detector actually stops, submits, takes the solution and opens the Reims data | They keep polishing Kashiwa past 11:20. The cliff is the day's single most dangerous moment and the only one with no second chance | [03](03-cadence.md) |
| 4 | **Does the analogue block produce disagreement?** | Two personas mark the same window differently, and notice | Everyone marks the same thing, or nobody compares. If disagreement does not surface, [05](05-warm-up-and-environment-gate.md)'s lesson did not land and the whole intervals/tolerance story stays abstract | [05](05-warm-up-and-environment-gate.md) |
| 5 | **Does the gate catch a broken environment quietly, and does pairing actually happen?** | A deliberately broken persona is identified by ~09:50 and **paired** by ~10:05, without being announced | Nobody notices; or they are noticed loudly; or nobody will pair, which is the failure that would force the runner back | [05](05-warm-up-and-environment-gate.md), [06](06-fallback-and-recovery.md) |
| 6 | **Is the report actually written in instalments?** | Headings appear at B3, B6, B7 | Everything is written after 12:10. [03](03-cadence.md)'s three-instalment design is the only reason Submit fits in fifteen minutes, and it is the easiest thing in the day to ignore | [03](03-cadence.md) |

### Three things that must be deliberately broken

Clean-install rehearsals prove nothing about a design built almost entirely from failure paths.
[Ticket 04](../../civ2026-challenge-spec/issues/04-target-machine.md) already requires *a
deliberately broken environment, not only clean installs*. Extend it:

1. **A broken container**, to exercise the gate → runner path end to end (observation 5).
2. **The internet pulled mid-session.** The only network failure left
   ([08](08-room-requirements.md) Update 4): the page and submission both go, for everyone at once,
   and it is the one dependency the organizers do not control. Rehearse coaches distributing the SSD
   page export and running USB hand-in under time pressure — on the day they *are* the distribution
   mechanism and they will have done it never.

*Was three. The cold-standby failover went with the organizer box, and the LAN failure went with the
recovery runner ([06](06-fallback-and-recovery.md)) — there is no box and no LAN to break.*

### Two things to rehearse outside the session

- **The jury.** Run [10](10-jury-composition.md)'s agents and anchors against the deliberate-detector
  submissions from
  [ticket 16](../../civ2026-challenge-spec/issues/16-evaluator-calibration.md) — known-good and
  known-bad entries are exactly what checks a rubric prompt before it is trusted. Watch specifically
  for **fluency being rewarded**, which is the failure [10](10-jury-composition.md) is designed
  against and the one that will not announce itself.
- **The results block.** Especially the interview format and the consent conversation for the
  instructive-failure walkthrough ([12](12-results-block.md)). Both are scripted; neither has been
  spoken aloud.

### What "no organizer-only workaround" means here

Phase 5's gate language needs one clarification for this map's mechanisms: an organizer **advancing
the page schedule** is not a workaround — it is the sanctioned control
([02](02-help-protocol.md), [17](17-attendee-page.md)). An organizer **answering a question the page
should have answered** is a workaround, and it means a missing unit.

Count the second kind. Each instance is a page unit to write before the event, and
[13](13-coach-guide-and-checkpoints.md) already established that discovering them on the day is too
late.

### What this hands on

- **Owner needed:** the dedicated observer, and someone to run the deliberate-failure injections.
- This ticket is the **exit condition of the map** — when Phase 5 can run against these six
  observations without inventing anything, the destination is reached.
