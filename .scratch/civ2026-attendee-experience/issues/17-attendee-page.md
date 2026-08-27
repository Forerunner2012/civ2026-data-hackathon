# The attendee page: what unlocks, when, and how far does a solution go?

Type: prototype
Status: resolved

## Question

[Ticket 01](01-pace-car.md) resolved that tempo is primary, then reduced the mechanism twice: no
live rabbit, then no board. What survives is **one page**, and it carries the whole room.

The shape, as decided:

- **Progressive.** It shows **what was expected** at each stage, on a timetable authored ahead of
  the day.
- **Referrable.** Nothing is missable. A participant head-down at 10:40 loses nothing — which is why
  live teaching was rejected: it penalises exactly the deep work the event wants.
- **Localized and targeted.** One unit per concept or step, demonstrative — it *shows* how the step
  is done.
- **Escalating.** Hints, then tips, then solutions.
- **Self-running, coach-tunable.** The schedule advances itself; a coach may pull a unit forward or
  hold it.

The only live delivery in the day is a short opening briefing, and that is
[05](05-warm-up-and-environment-gate.md)'s.

## Where it is served — decide this first

**It is almost certainly not the public participant page.**
[Ticket 22](../../civ2026-challenge-spec/issues/22-public-site-organizer-gate.md) puts
`/participants` in the production build, and `handoff-site` enforces by test that the scenario does
not appear on it. A page that progressively reveals expectations, hints and **solutions** cannot
ship in a public pre-event bundle.

Options, cheapest first:

1. **Served from the organizer machine on the room LAN.** Tickets [06](06-fallback-and-recovery.md)
   and [09](09-submission-intake.md) already want that machine. Zero leakage risk, no build
   gymnastics, no test to satisfy — and it fails closed if the LAN dies, which
   [08](08-room-requirements.md) must price.
2. **Public site with a server-gated section.** Reuses deployed infrastructure; costs a real
   argument with the leakage suite and somewhere to hold content that must not ship early.
3. **A local file in the kit**, unlocked by a timed manifest. Works offline per §3.3, but "unlock"
   becomes a file people can simply open early.

Recommend 1, and check it against §3.3's local-first requirement: the LAN is an accelerator, and if
it dies the day must still be survivable — which argues for a static fallback bundle the coaches can
hand out.

## What this ticket must decide

### The unit set, and its escalation

What a stage's section contains, and how hint → tip → solution differs **in kind rather than in
amount**. Two units are already known, because they were the only parts of the live rabbit worth
keeping (drafted in
[`prototypes/01-board-and-narration.md`](../prototypes/01-board-and-narration.md)):

- **Sample versus interval.** A naive threshold fires 41 times; `timing` collapses it to 6. This is
  [ticket 09](../../civ2026-challenge-spec/issues/09-detector-authoring-surface.md)'s non-negotiable
  rung 1, and told rather than shown, most people discover it at 11:30 by scoring badly.
- **An honest false positive.** The only thing in the whole design that demonstrates §2's *failure
  is a deliverable* claim **before** a participant is asked to produce one.

### How far a solution goes

[01](01-pace-car.md) set the rule; this ticket implements it and finds where it breaks.

- A stage's solution unlocks **only once that stage's points are effectively settled** — Kashiwa's
  at the transfer boundary. It does not rescue a Kashiwa score; it unblocks the Reims attempt.
- Solutions are **reconstructable, not copy-pasteable**: the approach, the signals, the shape of the
  timing block — not a runnable spec.
- **Handedness is never solved.** It is now the only genuinely unaided thing in the day.

Test the second bullet hard. *Reconstructable* is easy to write and hard to hold: naming the field
`accel.accel.angular.z` is already most of the way to a spec. Decide where the line actually sits,
with a worked example rather than a principle.

### Format, and its lead time

*Show, don't describe* has a cost. Annotated command transcript, annotated screenshot, or a
60-second screen recording — the last is most convincing and most expensive, and video is Phase 4
authoring with a real lead time. Pick a format a coach can still edit the week before.

### The release model

- Unlocks run **automatically on the authored timetable**, so a room where every organizer is busy
  still gets its material. Fail-safe, not fail-quiet.
- A coach may **advance or hold**. Decide who holds that control, whether it is shared, and whether
  holding is ever right or only advancing is.
- **Never self-unlocked.** Letting participants open everything destroys
  [ticket 14](../../civ2026-challenge-spec/issues/14-bespoke-collection-scope.md)'s arc — the room is
  supposed to *feel how tedious finding events by hand is* before `civ` arrives as the facilitator.
  If everything is open at minute 5, nobody feels it.

### The scoring consequence, to price rather than discover

Timed solutions compress **Kashiwa's 15 Detection points**.
[Ticket 20](../../civ2026-challenge-spec/issues/20-cohort-skill-floor-licensing.md) calls the Kashiwa
core a warm-up, so some compression is intended, and map one has already licensed the 15/10 split to
move after the internal evaluator run. **This ticket states the expected compression as an input to
that tuning**; it does not change the split, which is map one's and the evaluator's.

### Interaction with the rest

- **[03](03-cadence.md)'s minutes *are* this page's release timetable.** One artifact, not two.
- **[05](05-warm-up-and-environment-gate.md)** owns the opening briefing, which must say the page
  exists, what it will do, and that waiting for a hint is legitimate rather than a confession.
- **[02](02-help-protocol.md)**: the page answers the common questions, leaving coaches the uncommon
  ones. A coach answering the same question three times has found a missing unit — too late to write
  on the day. Mechanism, or rehearsal feedback only?
- **[14](14-participant-materials.md)**: this page is now the *central* participant artifact, and
  most of that inventory should probably live on it rather than on paper.

## Why this is a prototype ticket

Draft one stage's section in full — expectation, hint, tip, solution — and the escalation either
survives contact with concrete words or it does not. Draft the **Kashiwa solution at the transfer
boundary**, because that is where *reconstructable, not copy-pasteable* is hardest.

## Why this is on the frontier

Nothing blocks it. It is the mechanism [01](01-pace-car.md) resolved to, and
[03](03-cadence.md)'s beats are its schedule.

## Answer

**Prose plus a deliberately holed YAML skeleton, served from the organizer box, advancing on the
timetable. The line between reconstructable and copy-pasteable sits at the numbers — and handing
over the Kashiwa solution is what arms the transfer test rather than what undermines it.**

Prototype: [`prototypes/17-transfer-stage-section.md`](../prototypes/17-transfer-stage-section.md) —
the Transfer stage drafted end to end at both its beats.

### The finding: the solution sets the trap

The worry this ticket was written with was that releasing the Kashiwa solution at 11:00 would give
away too much. Drafting it inverted that.

The solution names the topics and fields and shows the condition's shape, but withholds **the
comparison direction** — `yaw_smooth ‹?› ‹THRESH›`. A participant derives the sign from their own
plot, gets a working Kashiwa detector, and carries a **signed** threshold into a country where
traffic runs the other way.
[Ticket 18](../../civ2026-challenge-spec/issues/18-urt-operational-definition.md) designed precisely
this outcome: *copy a threshold and you find nothing.*

**So the solution is safe to release because releasing it arms the comprehension test.** Withholding
it would have protected nothing and left slow participants with neither a Kashiwa detector nor a
transfer attempt.

The trap must not be cruel and is not: the 11:00 solution says *you will need the sign convention
shortly*, and the 11:25 tip says *whatever worked in Kashiwa is a starting point, not an answer*.
Two warnings, neither of them the answer.

### Where the line sits

| Given | Withheld |
|---|---|
| Which signals, by topic and field | Every threshold and duration |
| The shape of the condition | The comparison **direction** |
| Which blocks the spec needs | The evidence window |

**Topic archaeology is lookup work; thresholds are judgement.** Giving the first costs nothing anyone
was scored on and saves the twenty minutes that were about to eat someone's transfer.

### The format is the enforcement

Solutions ship as **prose plus a YAML skeleton with `‹…›` holes in it**. They cannot be pasted and
run, by construction.

This is not a style choice. It removes the judgement call from whoever authors the remaining twenty
stages, and it makes a violation visible at a glance in review: **if the YAML is complete, the rule
has been broken.**

### Format: text, not video

Decided by drafting. A participant reading this at 11:20 with seventy minutes left is **skimming**,
and a 60-second recording is a terrible interface for someone in a hurry — unskimmable,
unsearchable, uneditable the week before, and it does not survive
[08](08-room-requirements.md)'s mandated static USB export.

- **Default: annotated prose and command transcripts.**
- **Screenshots** only where the point is genuinely visual — a plot with an interval drawn on it, a
  clip frame.
- **No video.** It also removes the Phase 4 lead time that was this ticket's largest unknown.

### The escalation, in kinds

| | Gives | Never |
|---|---|---|
| **Expectation** | what you should be holding | — |
| **Hint** | *where to look* | what you will find |
| **Tip** | *a technique or a hazard* | a value |
| **Solution** | *the approach in full* | the numbers |

Each is answerable in one line by its author, which is what makes ~20 units writable in Phase 4
without the ladder degenerating into "more detail, then even more detail".

### Where it is served

**Option 1 — the organizer box on the room LAN.** It is already serving
[06](06-fallback-and-recovery.md)'s runner and [09](09-submission-intake.md)'s intake, it has zero
leakage risk against
[ticket 22](../../civ2026-challenge-spec/issues/22-public-site-organizer-gate.md)'s suite, and it
needs no build gymnastics.

**With a static export on USB**, mandated by [08](08-room-requirements.md), which is the LAN-down
path and also the artifact that ships publicly after the event under
[ticket 20](../../civ2026-challenge-spec/issues/20-cohort-skill-floor-licensing.md)'s CC BY.

### Release: automatic, advance-only

- **Automatic on [03](03-cadence.md)'s timetable.** Fail-safe: a room where every organizer is busy
  still gets its material.
- **Any coach may advance. Nobody may hold.** Holding was in the original framing and is dropped —
  it solves no problem and punishes the people who are on time. If the room is behind, advancing
  helps; if ahead, nothing is needed. One direction, one shared control, no way to misuse it.
- **Never self-unlocked**, per [ticket 14](../../civ2026-challenge-spec/issues/14-bespoke-collection-scope.md)'s
  arc. If everything is open at minute 5, nobody ever feels why `civ` is worth having.

### The scoring consequence, stated as an input rather than discovered

**Expect Kashiwa Detection to become a near-ceiling category.** Anyone who takes the 11:00 solution
can produce Kashiwa events in roughly ten minutes, and 90 minutes remain.

That is **intended** — [ticket 20](../../civ2026-challenge-spec/issues/20-cohort-skill-floor-licensing.md)
calls the Kashiwa core a warm-up and
[ticket 14](../../civ2026-challenge-spec/issues/14-bespoke-collection-scope.md) moved the difficulty
to transfer. Discrimination lives in Reims Detection (10), Evidence (15), Reproducibility (15) and
the 45 jury points.

**Hand this to the internal evaluator run as a prior**, not as a request: map one already licensed
the 15/10 split to move after that run, and this is the strongest single reason it might. It is
not this map's decision.

### On coaches finding missing units

[02](02-help-protocol.md) asked whether there should be a mechanism for a coach who answers the same
question three times. **No mechanism.** It is rehearsal feedback — a missing unit discovered at 11:20
cannot be written well, and a coach improvising one into the page mid-session breaks the guarantee
that everyone got the same material at the same time. Note it, fix it for next edition, answer the
question by hand today.

### What this hands on

- **[14](14-participant-materials.md)**: the page is the central artifact and most of that inventory
  belongs on it. What stays on paper is now a short list — the printed trace
  ([05](05-warm-up-and-environment-gate.md)), the help cards ([02](02-help-protocol.md)), the brief.
- **[16](16-decoy-event-class.md)** supplies the example for the 10:20 `timing` unit and nothing
  else.
- **Owner needed:** ~20 units to author in Phase 4, plus the static export. Text-only makes it
  tractable, and the two hardest are already drafted.

## Update 3 — solutions are handed over **after** the hackathon, not during it

Organizer's decision, and it **reverses the timed-solution rule** that Update 2 and
[03](03-cadence.md) were built on.

> During the session the page goes **expectation → hint → tip**, and stops there. The pace car and
> the coaches **guide attendees towards** a solution; nobody is handed one. **Solutions are released
> after the hackathon.**

### What this fixes, and it is not small

The timed-solution design had one cost I had priced and handed on as a prior: **Kashiwa Detection
becoming a near-ceiling category**, because anyone taking the 11:00 solution could produce events in
ten minutes. **That cost disappears.** Detection keeps its full discriminating power on both
datasets, and the note handed to the internal evaluator run — *expect Kashiwa to compress* — is
**withdrawn**. The 15/10 split is no longer under pressure from this map.

It also removes the awkwardness of a scored event whose answers were published mid-scoring.

### What it costs, and what replaces it

[03](03-cadence.md)'s **B4 at 11:00** was built on *stop improving it, submit what you have, **take
the solution**, open the Reims data.* The solution was what made abandoning psychologically
possible — you were not asked to walk away with nothing.

That prop is gone. What carries the cliff instead:

- **The permission itself, stated plainly.** *A detector you are willing to stop improving* asks for
  a decision, not an achievement.
- **The tip layer, unlocked at exactly that beat** — the strongest non-answer available: which
  topics carry the equivalents, that the stack has no vehicle bus, that IMU angular velocity is
  noisier. Enough to start, not enough to skip the thinking.
- **Coaches, deliberately.** [02](02-help-protocol.md) said coaches never hand over solutions
  because the page would. The page no longer will, so the coach's role at the cliff is **to guide
  towards one** — the two questions, then work the participant's own hypothesis forward.

**This is the one place where [02](02-help-protocol.md)'s "advance the schedule instead of helping
privately" no longer fully applies**, because advancing the schedule can no longer produce an
answer. Coaching becomes the escalation of last resort again, and
[13](13-coach-guide-and-checkpoints.md)'s card must say so.

### The escalation, revised

| | Gives | Never | When |
|---|---|---|---|
| **Expectation** | what you should be holding | — | at the beat |
| **Hint** | *where to look* | what you will find | at the beat |
| **Tip** | *a technique or a hazard* | a value, or the approach | at the beat |
| **Coach** | questions that move your own hypothesis | a threshold, a spec | on request |
| **Solution** | the approach in full | the numbers | **after the event** |

**Handedness is still never resolved** — not even after the event, in the sense that the released
solution shows the approach and leaves the sign convention to the reader.

### Consequences

- [03](03-cadence.md)'s beat table: **B4 loses its solution unlock**, and B7/12:30 no longer
  releases a Reims solution. The page's post-12:30 unlock is the extension section only.
- The prototype's `▸ SOLUTION — Kashiwa` block becomes **post-event material**; what appears at 11:00
  is its tip layer. Noted at the top of
  [`prototypes/17-transfer-stage-section.md`](../prototypes/17-transfer-stage-section.md).
- [09](09-submission-intake.md)'s scoring reasoning is unaffected.
- **Solutions still have to be written**, just published later — so the Phase 4 authoring job is the
  same size, with a softer deadline for that layer.

## Update — video where it earns it, and the rule for what a hint shows

Two refinements from the organizer, both narrowing rather than reversing.

### 1. Video for the most visible things only

The blanket "no video" above is **overturned in part**. Video is right where the point is genuinely
visual and where *motion* is the content — text cannot carry those, and a screenshot barely can:

- **A clip playing.** What a good evidence window looks like, which is otherwise the vaguest thing
  in the rubric.
- **Navigating PlotJuggler** to zoom in on an interval — an interaction, not a state.
- Anything where "watch this happen" is genuinely shorter than reading it.

Everything else stays **text and annotated transcripts**, for the reasons already established: a
participant at 11:20 is skimming, text is editable the week before, and it survives
[08](08-room-requirements.md)'s static USB export. **Video is the exception, justified per unit —
not the default.**

Practical consequence: keep clips **short and silent-safe** (captioned, no narration required), so
they work in a noisy room without headphones and can be re-cut quickly if a command changes.

### 2. The rule for hints, tips and examples

> **Show a real command or operation, run on the real dataset — with an example that is deliberately
> not the expected answer.**

This is sharper than *reconstructable, not copy-pasteable*, and it applies to the layer below
solutions:

| Layer | Shows | Uses |
|---|---|---|
| **Hint / tip / example** | a command or operation being performed | **real data, a non-answer example** |
| **Solution** | the approach | the real signals, holed at the numbers |

Why it is better than either alternative considered: a **synthetic** example reads as a textbook and
loses *your data, your problem*; the **real answer** gives the game away. Running `civ detect` on the
actual warm-up route with a condition that is not the one being scored gets the credibility of real
data at none of the cost.

It also means every unit can use real commands and real output, which makes the Phase 4 authoring
job concrete: run the thing, paste what happened, annotate it.

### What this does to [16](16-decoy-event-class.md)

It nearly dissolves it. The `timing` unit no longer needs a *carefully chosen event class with a
dramatic collapse ratio* — it needs **any condition that stays true for a while**, because the
over-count is a property of **sampling, not of the data**: a condition true across a two-second
manoeuvre at 100 Hz produces two hundred sample hits and one event, whatever the signal is.

So the demonstration is guaranteed to work by construction. What remains in
[16](16-decoy-event-class.md) is only the part that genuinely needs eyes on data: producing the real
numbers to print, and finding **one honest false positive** to narrate.

## Update — served over Tailscale Funnel, not the room LAN

Organizer's decision, and it supersedes the "option 1, room LAN" choice above. The page is hosted on
the organizer machine and published to the public internet via **Tailscale Funnel** at an HTTPS
`*.ts.net` address.

### What it fixes

- **The VPN problem disappears.** A full-tunnel corporate VPN routes public internet traffic
  normally, so [13](13-coach-guide-and-checkpoints.md)'s item 3 stops applying to the page.
- **No client software** for participants — Funnel is public HTTPS, unlike tailnet-only serving.
- **No inbound ports, no venue firewall change.** The box needs only outbound connectivity, which
  removes the *"permission to run our own network gear"* row from
  [08](08-room-requirements.md)'s venue ask being load-bearing for the page.
- **Valid TLS** without certificate work.
- **It works before and after the room.** Participants can reach it from a hotel the night before,
  and afterwards until it is turned off — which suits an artifact that ships publicly anyway under
  [ticket 20](../../civ2026-challenge-spec/issues/20-cohort-skill-floor-licensing.md)'s CC BY.

### What it costs, and this is the real trade

**The dependency moves from something the organizers control to something they do not.**
[08](08-room-requirements.md)'s finding was *the venue is not the risk; the box is* — precisely
because everything load-bearing was brought into the room. Funnel reverses that: the page now
depends on **venue internet** (unverified, and nobody has tested its uplink) **plus a third-party
relay** and an account.

Against §3.3's *local-first and offline-capable*: the **required path** is unaffected — `civ` still
runs locally against local data, with no SaaS on the scored route. What becomes
internet-dependent is **facilitation**. That is a defensible line, but it must be a stated one, not
an accident.

**So the static USB export stops being a nicety and becomes the primary contingency**, and
[18](18-rehearsal-observations.md)'s "pull the LAN" rehearsal should become **"kill the internet"**,
which is the more likely failure of the two.

### Leakage — the constraint that needs an explicit answer

The page carries the scenario, the hints and the **solutions**. Funnel makes it publicly reachable,
and Funnel hostnames are not truly obscure: the HTTPS certificate appears in **public certificate
transparency logs**, so the address is discoverable by anyone scraping them.

This does not endanger anything in a security sense — it is a hackathon's hint text — but it is
exactly what [ticket 22](../../civ2026-challenge-spec/issues/22-public-site-organizer-gate.md)'s
leakage suite exists to prevent *before the event*. **The mitigation is timing:**

- **Enable Funnel on the morning of 3 September, not before.** Pre-event exposure is then nil, which
  is the only window that matters.
- Do not link it from the public participant site, so
  [ticket 22](../../civ2026-challenge-spec/issues/22-public-site-organizer-gate.md)'s suite is
  untouched and `npm test` stays green.
- Treat the URL as unlisted, not secret, and design nothing that depends on it being private.

### Recommended split: funnel the page, keep intake local

**Do not funnel [09](09-submission-intake.md)'s intake by default.** Serving a small read-only page
through a relay is a very different profile from up to thirty submissions of up to 2 GB each. Funnel
throughput for bulk upload is a **question to verify, not to assume**.

| | Path | Why |
|---|---|---|
| **The page** | Funnel | Small, read-only, high value, VPN-proof |
| **Intake** | Room LAN, with USB hand-in | Local bandwidth, no third party on the thing that cannot fail at 12:30 |
| **Recovery runner** ([06](06-fallback-and-recovery.md)) | Room LAN | Same reasoning; iteration needs local latency |

**Worth building if cheap:** have the submission step try the **LAN address first and fall back to a
funnelled intake endpoint**. That gives local speed normally and a working path for a VPN-blocked
participant, and it is the only change that would fully close
[13](13-coach-guide-and-checkpoints.md)'s item 3 rather than routing it to USB.

### Consequences

- **[05](05-warm-up-and-environment-gate.md)'s gate keeps its third clause**, but it now tests
  *intake* reachability rather than the page — that is the clause that still catches a VPN-blocked
  participant before 12:25.
- **[08](08-room-requirements.md)**: the venue ask loses the page, gains a **verified internet
  uplink**; the degradation table's worst row becomes internet loss.
- **Owner needed:** whose tailnet, who enables Funnel on the morning, and who turns it off after.
