# The help protocol: how does a stuck workstream surface itself, and what do coaches become?

Type: grilling
Status: resolved
Blocked by: 01

## Question

[Ticket 01](01-pace-car.md) decides the broadcast **tempo** — how a participant knows where they
should be. This ticket decides the other half: **sensing**, the raise-hand affordance, and what
§4.7's coaching role becomes once tempo is primary.

### The inversion to confirm

`HACKATHON-HANDOFF.md` §4.7 currently reads:

> coaches intervene on blocked tooling after a short timebox.

That is a *push* model: coaches roam, notice, intervene. At 1 coach to 8 workstreams, across a room
of experienced practitioners who do not signal distress, it does not work. If 01 lands, this becomes
a *pull* model: the participant self-diagnoses against the tempo, raises a flag, and a coach
responds. Coaching stops being surveillance and becomes triage.

The rewrite of §4.7 is this ticket's output.

## What this ticket must decide

### The raise-hand affordance

It has to be **socially free**. An experienced practitioner will not walk to the front of a room and
announce they are behind. Candidates:

- A **physical token** on the monitor — a coloured card or cup, green/red, or a small flag. Zero
  words, zero eye contact, visible from across the room. The classic workshop answer, and it works
  because it costs nothing to raise and nothing to lower.
- A **chat channel** — asynchronous, searchable, and one answer serves many. But it requires a
  network, and it is invisible to a coach who is helping someone else.
- **Coach rounds** — a coach visits every workstream on a fixed rotation, so nobody has to raise
  anything. Guarantees contact; guarantees interruption. At 8 workstreams per coach and a 30-minute
  rotation, contact is thin anyway.

Leading candidate: **token plus channel**, with rounds only at the checkpoints. Confirm or reject.

### Sensing: does the room instrument itself?

**[01](01-pace-car.md) has now resolved and it rejected telemetry *as tempo*, on a ground that
constrains this ticket:** telemetry is **descriptive** and tempo must be **prescriptive** — a board
reading *14 of 22 workstreams have their first event* normalises being behind on a slow morning.
Every line on the tempo board is a statement of budget, never of state. So if this ticket adopts
telemetry, it must be **coach-facing and not on the tempo board**, or the rejected failure mode
returns through the back door.

[Ticket 01](01-pace-car.md)'s candidate 4 — `civ` reporting milestones to a room board — is the only
mechanism that lets a coach see a quiet stall without asking. Decide it **here** rather than as
tempo, so it is built as a *radar* and not as a scoreboard.

The distinction is not cosmetic. A board reading *11 of 22 workstreams have a first French event* is
tempo. A board that names or ranks workstreams is a live leaderboard, and a live leaderboard in a
room of competitive practitioners changes behaviour in ways nobody has designed for — and
[ticket 21](../../civ2026-challenge-spec/issues/21-pitch-and-judging-model.md) deliberately put the
leaderboard at 14:30. Decide: aggregate-only, coach-visible-only, or not at all. Also decide whether
this is worth the build cost at all, or whether the checkpoint prompts in
[13](13-coach-guide-and-checkpoints.md) collect the same signal for free.

### Coach count, ratio and identity

[01](01-pace-car.md)'s update **removed** the headcount it had first added: with the live rabbit
dissolved into timed cards ([17](17-attendee-page.md)), no organizer is tied up driving it. That
person coaches.

Two consequences this ticket inherits: the cards answer the *common* questions, so coaches are left
with the uncommon ones — brief them for that — and a coach who answers the same question three times
has found a missing card, which on the day is too late to write.

- **How many coaches** for 15–30 workstreams, and is that a ratio or a fixed number? A pull model
  needs fewer than a push model, but a queue of three raised tokens with one coach is worse than no
  token at all.
- **Who are they** — the people who built the kit, so they can answer anything, or people
  deliberately kept naive so they coach the reasoning rather than the tool?
- **Do coaches also judge?** [Ticket 10](10-jury-composition.md) owns the answer, but this ticket
  states the constraint: a coach who spent 40 minutes with one duo cannot read that duo's report
  neutrally, and a 30-person room cannot be anonymised.

### What a coach may and may not do

§4.7 already has the right instinct — *coaches ask for evidence and assumptions before suggesting
thresholds* — but it is one line and it is the whole pedagogy. Turn it into a rule a coach can
actually apply under time pressure. Specifically: is there a point in the session where a coach
**does** hand over a threshold, or a working spec, to keep someone in the event? If yes, when, and
what does it cost them on the leaderboard? A coach improvising that at 11:40 is worse than a stated
policy.

### The escalation ladder

Which failures route where. A tooling failure at minute 15 goes to [06](06-fallback-and-recovery.md)'s
recovery path, not to a coach's judgement. A conceptual stall at minute 100 is exactly a coach's
work. Name the categories and the handoff.

## Why it is blocked

The coach is responding to a gap between where someone is and where the room says they should be.
Until [01](01-pace-car.md) says what the room broadcasts, there is no gap to respond to — and
whether sensing is needed at all depends on whether 01 chose telemetry.

## Answer

**A two-sided card on the laptop, one sweep per beat, three to four coaches, and a rule that coaches
never hand over solutions — the page does, on schedule.**

### The finding that shaped everything else

[01](01-pace-car.md) made the page release hints, tips and eventually solutions on a timetable. That
does something to coaching that was not obvious before: **it removes the give-up decision entirely.**

The hardest question this ticket started with was *is there a point where a coach hands over a
working threshold to keep someone in the event, and what does it cost them?* — a judgement call made
under pressure at 11:40, differently by each coach, invisibly, unfairly.

**It no longer exists.** A coach never hands over a solution, because the page will, at a known
minute, to everyone. What a coach can do instead is **advance the page's schedule**, which
[01](01-pace-car.md) already gave them: help arrives for the whole room, visibly, at once.

> **Help is never private and never improvised.** A coach who wants to give more help pulls the
> schedule forward for everyone rather than rescuing one person quietly.

Fairness by construction, and one fewer thing to brief.

> **Amended by [17](17-attendee-page.md)'s Update 3.** Solutions now publish **after** the
> hackathon, so the page will not hand one over during the session either. The rule survives in its
> important half — **a coach still never hands over a threshold or a spec** — but its clean
> justification does not: advancing the schedule can no longer produce an answer.
>
> So around [03](03-cadence.md)'s 11:00 cliff, **coaching is the escalation of last resort again**.
> A coach *guides towards* a solution by working the participant's own hypothesis forward with the
> two questions below. That is a judgement rather than a rule, and
> [13](13-coach-guide-and-checkpoints.md)'s card has to carry the distinction —
> *guide, never hand over* — which is harder to hold under time pressure than *the page will do it*.

### The raise-hand affordance: one card, two sides

A folded card standing on the laptop. Nothing up means fine. Card up means *come and talk to me* —
and **which side is showing routes the request before the coach arrives**:

| Side | Means | Goes to |
|---|---|---|
| **A** | environment, tooling, "it will not run" | [06](06-fallback-and-recovery.md)'s recovery path |
| **B** | approach, "I do not know what to do next" | coaching |

Why a card and not a channel: it is socially free — no walking to the front, no announcing, no
audience — and it is the only mechanism here that **needs no network**.

That mattered when the LAN carried everything, and it matters more now: per
[08](08-room-requirements.md)'s Update 2, the page and submission both depend on **venue internet**
and the recovery runner on the room LAN. The help path must not join either list — when the network
is the problem, raising a hand cannot require the network. A chat channel is a fine *optional*
addition and must never be the only route.

Two states, not three. Three invites people to deliberate about which, which is a cost paid by
exactly the person who is already stuck.

### Sensing: no telemetry. One sweep per beat.

Instrumenting `civ` to report progress is rejected, and the reason is not build cost:

**The page is already a floor.** With solutions unlocking on a timetable, nobody can fall off the
map entirely — the worst case is that you receive help later than you would have liked. That
mitigates most of the silent-stall risk that made sensing look necessary.

What is left is the person who neither raises a card nor reads the page. **A single sweep at each
beat** catches them: coaches walk the room once per beat, glancing at screens, not interrupting. Six
or so sweeps across the session, zero build, no LAN dependency, and it doubles as the ambient
presence that makes raising a card feel normal.

If Phase 5 rehearsal shows the sweep misses people, **telemetry is the upgrade** — cheap thing now,
expensive thing only if evidence demands it.

### Coach count and identity

**Three minimum, four preferred. A floor, not a ratio.**

The arithmetic: a sweep of 30 desks at ~20 seconds each is 10 minutes for one coach — most of the
gap between beats. Split three ways it is 3–4 minutes, leaving room to answer cards. Below three, a
sweep does not fit between beats and two simultaneous cards block it.

This is affordable precisely because [01](01-pace-car.md) freed the pace car driver.

**Who:** the people who built the kit. There is no time to train naive coaches on two sensor stacks
that share no topics, and the page has already absorbed the questions a naive coach could have
answered.

### Coaches and the jury

The constraint this ticket owes [10](10-jury-composition.md), plus a mechanism so it is not just a
principle:

The organizers who built the kit are the only people qualified to judge it *and* to coach it, so
full separation may not be affordable. **Coaches log who they spent significant time with** — a
name and a rough duration, nothing more. With split reading across three jurors and 15–30 reports,
routing around a handful of conflicts is easy. [10](10-jury-composition.md) decides the routing;
this ticket guarantees the input exists, which is the part that is impossible to reconstruct
afterwards.

### What a coach does, in ten seconds

Two questions, in order, before anything else:

1. **"What have you got so far?"** — forces the participant to articulate their actual state, which
   is often where they find the answer themselves.
2. **"What do you think is happening?"** — surfaces the hypothesis.

Then respond to the hypothesis, not to the code. This is §4.7's *ask for evidence and assumptions
before suggesting thresholds*, made applicable while standing at a desk.

**And one prohibition that is easy to miss:** coaches must not rescue people from the *designed*
friction. [Ticket 14](../../civ2026-challenge-spec/issues/14-bespoke-collection-scope.md) wants the
room to feel how tedious finding events by hand is before `civ` arrives as the facilitator. A coach
whose instinct is to shortcut that destroys the arc the whole event is built on. Struggling in the
warm-up is not a failure state.

### The escalation ladder

| Category | Route | Note |
|---|---|---|
| Environment / tooling | [06](06-fallback-and-recovery.md), timeboxed | Not a coaching judgement. If unfixed in ~10 minutes, go to "your spec, our runner" |
| Approach / conceptual | Coach, two questions above | The core of the job |
| "What do I do next?" | The page | Point at it; do not answer it |
| Designed friction | **Leave them** | Warm-up tedium is the lesson |
| Same question three times | A missing page unit | Too late to write on the day — rehearsal feedback, and [13](13-coach-guide-and-checkpoints.md)'s to capture |

### §4.7 rewrite

The output. It replaces the bullets wholesale rather than amending them:

> Thirty experienced practitioners work solo or in duos, ranked together on one leaderboard, and the
> room is paced by a progressive attendee page rather than by intervention. Participants
> self-diagnose against what the page says was expected; a two-sided card on the laptop asks for a
> coach, and which side shows routes the request to recovery or to coaching before anyone arrives.
> Three to four coaches sweep the room once per beat and otherwise answer cards. Coaches ask what a
> participant has and what they think is happening before discussing thresholds; they never hand
> over a solution, because the page does that on a schedule, and a coach who wants to give more help
> advances the schedule for everyone. Environment failures are timeboxed and routed to the recovery
> path, not debugged at the desk. The warm-up's tedium is deliberate and is not coached away.

### Not decided here

Coach **briefing and rehearsal**, the troubleshooting tree, and the wording of the two questions on
a card a coach can hold are [13](13-coach-guide-and-checkpoints.md)'s.
