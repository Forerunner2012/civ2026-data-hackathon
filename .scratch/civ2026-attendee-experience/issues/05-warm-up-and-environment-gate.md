# The warm-up: what happens in the first thirty minutes, and does it double as the environment gate?

Type: grilling
Status: resolved

## Question

Map one left this in the fog, blocked on knowing what a detector looks like and what data a team
holds. Both are now closed ([09](../../../docs/history/planning/challenge-spec/issues/09-detector-authoring-surface.md),
[17](../../../docs/history/planning/challenge-spec/issues/17-dataset-subsetting-and-distribution.md)), so the warm-up
is specifiable.

Three things now, because [01](01-pace-car.md)'s update 2 made the opening briefing **the only live
delivery in the day** and handed it here.

### Part 0 — the opening briefing

Short, before the hackathon starts, and **organizational rather than technical**: where things are,
what you are looking for, and what to do if you get lost. It must also introduce
[the attendee page](17-attendee-page.md) — that it exists, that it will progressively show what was
expected, and that **waiting for a hint is legitimate rather than a confession**. In a room selected
for expertise that last point does not go without saying.

Decide its length, its exact contents, and whether it happens before or after the environment gate
below.

### Part 1 — the shape of the opening

[Ticket 14](../../civ2026-challenge-spec/issues/14-bespoke-collection-scope.md) fixed the arc and it
is not negotiable:

> Manual analysis first, so the room feels how tedious finding events by hand is; then `civ` is
> introduced as the facilitator; then the payoff is how easily evidence can be collected across two
> structurally different datasets.

So the first block is **not** "run the tool". It is "find turns by hand in PlotJuggler on the fully
published warm-up route" ([ticket 17](../../../docs/history/planning/challenge-spec/issues/17-dataset-subsetting-and-distribution.md):
1 warm-up route, fully labelled). Open:

- **Collective or individual?** Led from the front in lockstep, or thirty people working alone with
  a handout? Lockstep guarantees a shared reference and gives the pace car a launch; individual
  respects a high skill floor that will find lockstep patronising.
- **How long is the tedium allowed to last?** The lesson lands the moment someone thinks *there has
  to be a better way*. Every minute after that is wasted, and this room reaches that thought fast.
- **Does the warm-up produce anything?** A candidate interval written down, a first `civ detect`
  run, a first clip — or nothing but a feeling.
- **Where is the first success?** §3.3's design principle is *low-friction first success*. Name the
  minute it lands and what it is.
- **Is the warm-up route shared with the room afterwards?** **[01](01-pace-car.md) has resolved this
  half:** yes — the published warm-up route is where [the attendee
  page](17-attendee-page.md) demonstrates from, on a **decoy event class** (hard braking). So the
  opening should put every participant on the same route the cards use, which is also what lets the
  warm-up double as an environment gate without a second setup step.

### Part 2 — the environment gate

[Ticket 04](../../../docs/history/planning/challenge-spec/issues/04-target-machine.md) accepted the BYOD risk with
its eyes open:

> with no pool of preloaded recovery laptops, a team whose WSL2 or Docker Desktop setup fails has no
> hardware swap — and that failure lands in the first thirty minutes, the exact window the design
> relies on for early success.

At 15–30 independent workstreams, **the only way to know every environment works is to make everyone
exercise it at a known minute.** Otherwise the first evidence that a container is broken arrives
when someone tries to batch at 01:00, and the day is gone.

So: **should the warm-up be the gate?** Everyone runs the same command by minute *N*; anyone who has
not succeeded is identified and routed to [06](06-fallback-and-recovery.md). That converts ticket 04's
accepted risk from a lurking failure into a scheduled checkpoint, and it gives 06 a concrete trigger
instead of a judgement call.

If yes, decide:

- **What the gate command is.** `civ doctor` proves the container; it does not prove the data
  downloaded, decoded and rendered. The gate probably has to touch a real bag.
- **The minute.** Early enough to recover, late enough that a slow starter is not misclassified.
- **How a failure is detected without a network** — does the participant self-report, does a coach
  sweep the room, or does the gate produce a token they hold up?
- **What "routed to fallback" means socially.** Being publicly identified as broken at minute 15 in
  a room of thirty peers is its own harm. This has to be quiet.
- Whether the gate is *also* run in the pre-event week ([07](07-pre-event-readiness-and-reveal.md)),
  in which case the in-session gate is a re-check rather than a first contact — and should be much
  shorter.

## Tension to resolve, not paper over

The manual-analysis block is **deliberate friction** in the window where the day's worst
**accidental friction** lands. Two kinds of pain in the same thirty minutes, and only one of them is
pedagogical. A participant fighting Docker while being told to feel how tedious manual analysis is
will not distinguish the two. Options include front-loading the gate before the tedium, or making
the manual block explicitly analogue — paper, a projected plot, no laptop needed — so a broken
environment does not also cost the lesson.

## Why this is on the frontier

Nothing blocks it. It blocks [03](03-cadence.md) (how many minutes the opening gets) and
[06](06-fallback-and-recovery.md) (the trigger), and it is where [01](01-pace-car.md)'s pace car
starts.

## Answer

**The manual block is analogue — pen on a printed trace — so it costs nothing to a broken laptop.
The gate runs underneath it, signalled by inverting the help card. And the manual block's real
output is not tedium: it is disagreement.**

### The finding: the lesson is that experts do not agree

[Ticket 14](../../civ2026-challenge-spec/issues/14-bespoke-collection-scope.md) asks the room to
*feel how tedious finding events by hand is*. Taken literally that produces a weak exercise — a room
of practitioners registers "this is tedious" in about ninety seconds, and the remaining minutes are
theatre they will find patronising.

The stronger thing happens if you then **compare**. Two experienced practitioners mark the same
four-minute window and produce different intervals: different starts, different ends, one of them
counts a hesitation as two turns. Nobody is wrong.

That disagreement is the setup for everything downstream — why labels are **intervals** and not
timestamps ([ticket 18](../../civ2026-challenge-spec/issues/18-urt-operational-definition.md)), why
matching needs a **tolerance** and why it is temporal IoU ≥ 0.5
([ticket 16](../../../docs/history/planning/challenge-spec/issues/16-evaluator-calibration.md)), why `merge_gap` has
teeth, and why there is a sealed label set at all. All of that is otherwise abstract at 09:40 and
expensive to explain later.

**So the manual block's output is a disagreement, deliberately surfaced.** Tedium is the excuse;
disagreement is the lesson.

### Part 0 — the opening briefing

**Five minutes, organizational, before anything else.** Contents:

1. Where everything is — the page, the data, the intake, the coaches.
2. What you are looking for, at the level of *what the day is*, not the detector.
3. **What to do if you get lost:** the page will tell you what was expected, and waiting for a hint
   is legitimate. Say this out loud. In a room selected for expertise it does not go without saying,
   and it is the sentence that makes [01](01-pace-car.md)'s whole mechanism usable.
4. The card, both sides ([02](02-help-protocol.md)).
5. **Pairing is available, and normal.** Say it aloud. It covers a broken environment *and*
   underpowered hardware ([06](06-fallback-and-recovery.md),
   [08](08-room-requirements.md)), and nobody volunteers *my laptop is too weak* to a room of thirty
   peers unprompted. The window in which pairing still helps closes fast.
5. It ends with the gate instruction below — so containers are starting while the briefing finishes.

### Part 1 — the opening is analogue, and collective for ten minutes

**Pen on a printed trace of the published warm-up route.** Real signals, a real four-minute window,
one instruction: *mark every turn you can find.* Then compare with your neighbour.

Why paper rather than PlotJuggler:

- **It needs no working container**, which is the whole point — see Part 2.
- The tedium is *purer*. You are scanning, not fighting a tool, so what people feel is the actual
  problem rather than the viewer's learning curve.
- Everyone finishes together, so the comparison happens at a known minute.
- It makes the *there has to be a better way* moment land harder, and `civ` arriving straight
  afterwards gets maximum contrast.

**Collective for the manual block only.** The shared experience *is* the content there. From the
first `civ` run onward it is individual — a room at this skill floor will find sustained lockstep
patronising, and rightly.

**First success** is the first `civ detect` on the warm-up route producing intervals the participant
can hold against the ones they just drew by hand. That is §3.3's low-friction first success and the
introduction of the tool in one move, and it is the moment the day actually starts.

### Part 2 — the gate runs underneath, and the card signals it

**Yes, the warm-up is the environment gate.** The mechanism:

- The briefing ends with: *start your container, run `civ doctor && civ inspect <warm-up>`, **and
  open the page**.* `doctor` proves the container; `inspect` proves the data arrived, decodes and has
  the topics it should; **opening the page proves the participant can reach the organizer box.**
  `doctor` alone is not enough, and neither are the first two.

  **Why the third clause exists, in its final form.** It began as a fix for
  [13](13-coach-guide-and-checkpoints.md)'s corporate-VPN case. Since then
  [17](17-attendee-page.md) moved the page to Tailscale Funnel and
  [09](09-submission-intake.md) moved submission to a form, so **both now run over the public
  internet** and the VPN case is largely gone.

  The clause stays anyway, and it is now a **general reachability check**: opening the page proves
  the participant has working internet from this seat with this laptop, which is the same path
  submission takes. Whatever blocks one — VPN, proxy, captive portal, a dead uplink — blocks the
  other. Catching that at 09:50 rather than at 12:25 is worth one extra instruction, and it is the
  only clause that tests anything outside the machine.
- **Everyone starts with the card up, side A.** You put it down when the command succeeds.
- Ten minutes later the room is doing paper work and a handful of cards are still up. Coaches walk
  to those desks. Nobody is announced, nobody self-reports out loud, and the participant did not
  have to decide they were in trouble.

This is the inverted default — cards up, going down on success — and it reverts to
[02](02-help-protocol.md)'s normal meaning immediately afterwards.

**It resolves the double-friction tension** the ticket flagged: the deliberate friction is on paper
and the accidental friction is being fixed in parallel, so a broken laptop costs a participant time
but not the lesson. Recovery starts at minute 10 rather than at minute 90.

**Pre-event, this is a re-check, not first contact.** [07](07-pre-event-readiness-and-reveal.md)
should have every participant run the same pair of commands in the week before, which is what makes
a ten-minute in-session gate realistic rather than optimistic.

**And the gate looks for *broken*, not *absent*.** [07](07-pre-event-readiness-and-reveal.md)'s four
2 TB SSDs circulate from the moment people arrive, carrying the container image and both datasets, so
anyone who never downloaded is fixed before 09:30. A missing image or missing data should not reach
this gate at all — which is what keeps the ten minutes honest.

### Shape and rough minutes

Minutes are [03](03-cadence.md)'s; this is the shape it should fit.

| | |
|---|---|
| ~5 min | Briefing. Ends with the gate command |
| ~10 min | Analogue marking, collective. Containers starting, cards coming down, coaches on the ones that do not |
| ~5 min | Compare. Surface the disagreement and name what it implies |
| ~10 min | First `civ` run on the warm-up route; hold the output against your pen marks |

That is thirty minutes and it fits §4.2's Observe block without borrowing from Formalize.

### What this hands on

- **[06](06-fallback-and-recovery.md)** gets its trigger: *card still up at the end of the analogue
  block.* Concrete, timed, and detected without anyone having to admit anything.
- **[14](14-participant-materials.md)** gains an artifact nobody had listed: **the printed trace**,
  one per participant, plus whatever the comparison is captured on.
- **[17](17-attendee-page.md)** should carry the disagreement result forward — the page's first
  expectation is *you have marked intervals and you do not agree with your neighbour*, which is a
  much better opening line than *you have inspected a bag*.
- **[13](13-coach-guide-and-checkpoints.md)**: coaches must not help during the analogue block. There
  is nothing to help with, and interrupting it damages the comparison.
