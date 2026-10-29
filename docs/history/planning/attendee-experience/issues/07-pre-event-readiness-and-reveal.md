# Pre-event: what does a participant hold before the day, and what is revealed on the day?

Type: grilling
Status: resolved

## Question

Map one left this as fog:

> **Pre-event setup session** for the BYOD environment risk in 04. The programme has no slot, so it
> would be remote and voluntary in the week before.

The logistics question and a design question turn out to be the same question, so this ticket
carries both.

## Part 1 — readiness

[Ticket 04](../../challenge-spec/issues/04-target-machine.md) requires *pre-event setup
instructions and a `civ doctor` check that attendees run before the day, with a support channel open
beforehand.* Nothing decides how.

- **Live session, async-first, or both?** Thirty international practitioners will be **travelling to
  Miyazaki** in the days before, across timezones, at a conference that starts 31 August with the
  hackathon on 3 September. That argues hard for async-first, with drop-in windows as a supplement
  rather than the mechanism. Confirm or reject.
- **What is the readiness token?** Something an organizer can *see*, so the room's state is known
  before anyone walks in. `civ doctor` output posted to a channel is the obvious candidate: it is an
  artifact, it is diffable, and it costs the participant one command.
- **Two independent readiness items**, and they fail differently: the **container** and the **data**.
  ~350 MB signals-only downloads in seconds; the image does not. Decide whether both are gated, and
  what the checksum-verification step is.
- **Coverage.** What happens for the participants who never respond? Realistically some fraction
  arrives cold. Decide the expected number, and whether the room design assumes it or absorbs it
  ([05](05-warm-up-and-environment-gate.md), [06](06-fallback-and-recovery.md)).
- **When does the support channel open and close**, and who staffs it during a conference week when
  the organizers are also attending the conference?

## Part 2 — the hold/reveal boundary

The pre-event pack must make an environment work **without teaching the challenge**.
Ticket 22 puts the
participant view on a public site and `handoff-site` enforces by test that the scenario does not
appear on it. So there is a hard constraint: *whatever ships early cannot carry the scenario.*

That creates a live tension nobody has resolved:

- Both datasets have to ship **pre-event** for offline safety
  ([04](../../challenge-spec/issues/04-target-machine.md),
  [17](../../challenge-spec/issues/17-dataset-subsetting-and-distribution.md)). So a curious
  participant holds the Reims bag before the transfer is revealed.
- The transfer is the event's difficulty (ticket 14).
  Its force depends on the participant meeting it as a **comprehension test**, not on the bytes being
  secret.
- In-room distribution *is* technically possible — ~350 MB over a room LAN — but it trades the
  offline guarantee for a surprise, and the surprise is weak: the bytes do not carry the framing.

Decide:

- **What ships pre-event**: the image, the data, the CLI, a quickstart, and how each is named. A
  neutrally-named dataset pack is not deception; it is simply not a briefing.
- **What is revealed at 09:30**: the brief (§4.3), the scenario, the rubric, the report template.
- **What is revealed at the transfer boundary**, if anything — or is the whole task known from 09:30
  and only the *doing* is staged? This is a genuine design choice and it changes the shape of
  [03](03-cadence.md)'s middle hour.
- **Whether pre-exposure is a fairness problem at all.** Recommendation to test: no. A participant
  who explores the Reims bag early has done exactly the investigation the event rewards, and
  penalising curiosity in a room of practitioners would be perverse. But say so, rather than leaving
  people to guess whether they are allowed to look.

## Why this is on the frontier

Nothing blocks it. It blocks [14](14-participant-materials.md) — the materials inventory cannot be
written until it is known which of them ship early and which are embargoed.

## Answer

**Async-first, gated on the same command pair as the in-session gate. Everything ships early except
the brief — and exploring the data beforehand is explicitly encouraged.**

### Part 1 — readiness

**Async-first, and the drop-ins move earlier than "the week before".** The conference starts 31
August and the hackathon is 3 September, so the week before is the week thirty international
practitioners are *travelling*. Live sessions land worst exactly when they are most needed.

- **Support channel opens two weeks out**, async, staffed by the people who built the kit, with a
  stated response window rather than an implied one.
- **Two live drop-ins at ~10 days out** — one Asia-friendly, one Europe-friendly — deliberately
  *before* travel begins. Supplements, not the mechanism.

**The readiness token is the gate command**, and it is the same one
[05](05-warm-up-and-environment-gate.md) uses on the day:

```
civ doctor && civ inspect <warm-up>
```

One command pair, two failure modes covered: `doctor` proves the container, `inspect` proves the
data arrived, decodes and carries the topics it should. Post the output to the channel. It is an
artifact an organizer can *see*, it is diffable, and it costs the participant one line.

**The in-session gate is therefore a re-check, not first contact** — which is what makes
[05](05-warm-up-and-environment-gate.md)'s ten-minute window realistic instead of optimistic.

**Coverage: assume a fifth to a third arrive cold.** Not a failure to plan against but a number to
design for, and the design already absorbs it — [05](05-warm-up-and-environment-gate.md)'s gate
catches them at 09:50 and [06](06-fallback-and-recovery.md)'s runner carries whoever cannot be fixed.
Chasing non-responders is worth doing once and not worth doing three times.

### Part 2 — the reveal boundary, which [01](01-pace-car.md) has already decided

The question was whether the Reims task is revealed at 09:30 or held to the transfer boundary.
**It cannot be held**, and the reason is structural rather than pedagogical:

[01](01-pace-car.md) and [03](03-cadence.md) put the whole timetable in front of the room — a page
that says *TRANSFER, 11:00, by now you should have a Kashiwa detector you are willing to stop
improving*. **A visible tempo requires a visible shape.** Hiding the second dataset would mean hiding
the timetable, which would remove the mechanism the entire facilitation design rests on.

So: **the whole task is known at 09:30. Only the sealed data is secret.** The handedness insight is
not hidden either — it is simply never solved for them ([17](17-attendee-page.md)), which is a
different and better thing.

### What ships when

**Corrected.** The first version of this row said *brief, scenario, rubric, report template* all
arrive at 09:30. That was too coarse and it contradicted the live participant site, which already
publishes the brief and the rubric. The site is right; this table was wrong.

**The embargoed thing is the scenario, not the paperwork.** §4.3's brief is deliberately an
*incomplete incident report* — it never names the manoeuvre — and the rubric reveals nothing about
the event while helping people arrive prepared, which serves §3.4's *80% complete both dataset runs*
better than withholding it. Conflating the two would have forced a working public page to be
stripped for no gain.

| | Pre-event | 09:30 |
|---|---|---|
| Container image, `civ`, quickstart | ✅ | |
| **Both datasets**, with checksums | ✅ | |
| The gate command and the support channel | ✅ | |
| **Brief (§4.3)** — the incomplete incident report | ✅ | |
| **Rubric, scoring rules, recognition, report template** | ✅ | |
| The run of show, and what to bring | ✅ | |
| **The scenario** — which manoeuvre, on which recordings | | ✅ |
| [The attendee page](17-attendee-page.md), its hints and its unlocks | | ✅ |

**What enforces it is the test, not this table.** `handoff-site`'s leakage suite bans the scenario
from the public bundle by pattern
(ticket 22). Anything that
belongs in the 09:30 column and reaches the site will fail `npm test` — so the boundary is executable
rather than remembered, and this table is documentation of it rather than the control.

### Exploring the data beforehand is allowed, and say so

A participant who opens the Reims bag in August has done exactly the investigation the event
rewards. Penalising that in a room of practitioners would be perverse, it is unenforceable, and it
converts otherwise dead pre-event time into preparation — which helps §3.4's *80% complete both
dataset runs* more than any other cheap lever available.

**State it explicitly.** The failure mode is not someone exploring; it is someone who *wanted* to and
did not know whether they were allowed.

### The naming trap, which is real and easy to miss

Ticket 22 keeps the scenario
off the participant page and `handoff-site` enforces it by test. But the hero dataset is published as
**URT-Kashiwa**, and *URT* expands to the scenario. **The dataset's own name is a leak.**

- Pre-event material and the public page say **"the Kashiwa recordings"**. Never the expansion, never
  the acronym.
- Accept that a determined participant can find the upstream dataset and infer. That is fine — the
  event is a comprehension test, not a secret, and
  ticket 18 made the
  difficulty the mirrored manoeuvre rather than the word.
- **What must hold is the test**, and the test reads the built bundle. Anything added to the site
  must keep `npm test` green.

## Update — four 2 TB high-speed SSDs exist

Confirmed by the organizer. This does not reopen
[ticket 17](../../challenge-spec/issues/17-dataset-subsetting-and-distribution.md), which
already named USB SSDs as the venue fallback — it makes that fallback real and well-resourced, and it
changes how this ticket's cold-arrival risk is handled.

### The highest-value payload is the image, not the data

This ticket separated two readiness items that fail differently: the **container** and the **data**.
Signals-only is ~350 MB and downloads in seconds; **the ROS 2 Humble image does not.** So the thing
worth carrying on an SSD is the one nobody could quickly fix in the room.

Load each SSD with, in order of value:

1. **The container image**, exported and ready to `docker load`.
2. **Both datasets**, signals-only, with checksums.
3. **The optional image context pack** — 2 TB makes this free to carry, where a download would not be
   ([ticket 17](../../challenge-spec/issues/17-dataset-subsetting-and-distribution.md)
   measured signals+images at ~8 GB for the Reims session).
4. **The static export of [the attendee page](17-attendee-page.md)**, which
   [08](08-room-requirements.md) mandates as the internet-down path.
5. **[06](06-fallback-and-recovery.md)'s fallback pack.**

That makes each SSD a complete event-in-a-box, which is also the answer to the internet-down
scenario.

### Circulate them on arrival, not at the gate

**Do not hold them for failures.** Have the SSDs moving from the moment people enter the room, so
*data not downloaded* and *image not pulled* are fixed before 09:30 rather than caught by
[05](05-warm-up-and-environment-gate.md)'s gate at 09:50. The gate should be finding *broken*
environments, not *absent* ones.

Rough throughput: 4 drives across 30 people is ~7–8 each. The constraint is not bandwidth — it is
plugging, mounting and queueing. Budget for it as a physical logistics problem, not a transfer one.

### Four details that are cheap now and painful on the day

- **Format them exFAT.** It is the only filesystem both Windows and Ubuntu read *and write* natively
  with no extra driver, and [ticket 04](../../challenge-spec/issues/04-target-machine.md)
  fixed the environment as Windows/WSL2 **and** Ubuntu.
- **Carry USB-C and USB-A adapters.** BYOD means the port mix is unknown.
- **Load and verify checksums before travelling**, not in Miyazaki.
- **Name an owner who carries them**, alongside [08](08-room-requirements.md)'s other physical items.

### What it changes upstream

The *assume a fifth to a third arrive cold* estimate stands, but the **consequence** softens: a cold
arrival is now a two-minute copy rather than a lost morning. Chasing non-responders stays worth doing
once and not worth doing three times.

## Update — participants get **2–3 worked examples**, not a labelled development set

Organizer's decision, and it fills in the cell map one
[ticket 17](../../challenge-spec/issues/17-dataset-subsetting-and-distribution.md) left as
just *"partial"*.

> On the development routes, publish the answer key for **2–3 events maximum**. Not seven, not one
> per route.

### Why this is the right number

The given-away answers do one job and it is **not** practice: they communicate **where a turn starts
and ends**. That is the convention the whole 25-point Detection category hangs on, and it cannot be
described in prose — *the turn begins when the steering goes in* and *when the yaw rate crosses a
threshold* produce different intervals, and matching at 50% overlap is sensitive to which you meant.

Two or three worked examples convey it exactly. More of them stop being examples and start being a
**training set**: with enough labelled events, a participant tunes thresholds until they fit, and the
score measures curve-fitting rather than comprehension — the precise failure
ticket 18 designed the event
to avoid.

**Consequence to state in the brief:** the examples show the convention, they are not a validation
set, and there are deliberately few. Otherwise the first thing a practitioner asks at 10:15 is *where
are the rest of the labels*.

### The examples must come from the boundary convention, not before it

Sequencing, since it is easy to get backwards: Matt and Arnaud agree the boundary convention first —
by both marking the same route independently and comparing
([18](18-rehearsal-observations.md)) — **then** cut 2–3 of those agreed events as the published
examples, **then** label the held-back routes to the same convention. Publishing examples drawn
before the convention exists would ship the disagreement rather than resolve it.

### Still to do, deferred

**Recheck the recordings for a proper count of event types.** Not now, per the organizer. It affects
how many categories the answer key carries and whether anything beyond the target turn is worth
labelling — [ticket 03](../../challenge-spec/issues/03-scoring-basis.md) scores only the turn
that crosses oncoming traffic, so extra categories are optional colour. Folded into the data trip in
[16](16-decoy-event-class.md).

### What this hands on

- **[14](14-participant-materials.md)** can now mark every artifact public-early / public-on-the-day
  / organizer-only, and inherits the naming rule.
- **[05](05-warm-up-and-environment-gate.md)**'s ten-minute gate is justified by the pre-event
  re-check assumption stated here.
- **Owner needed:** the support channel and the non-responder chase are a person's job in late
  August, and nobody holds it.
