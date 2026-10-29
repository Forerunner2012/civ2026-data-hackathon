# The pace car: what gives the room a proactive tempo?

Type: prototype
Status: resolved

> **Read `## Update 2` first — it is the operative decision.** This ticket is a chronology: the
> original `## Answer` proposed a live rabbit plus a board, Update 1 removed the rabbit, Update 2
> removed the board. What survives is **a short opening briefing plus one progressive attendee
> page** ([17](17-attendee-page.md)). The earlier sections are kept because their *arguments*
> survive — why tempo is primary, why telemetry is not tempo, and why `IF YOU DON'T` is the field
> that carries the design — but their *mechanisms* do not.

## Question

**Is a proactive, visible tempo the primary facilitation mechanism — with coaching demoted to the
exception handler — and if so, what concrete form does it take?**

This is the one genuinely new idea on the board. Everything else in this map fills in fog; this
changes how the room works.

### Why the inherited design does not hold

`HACKATHON-HANDOFF.md` §4.7 offers only **reactive** mechanisms:

> One shared Kashiwa warm-up; coaches intervene on blocked tooling after a short timebox.
> Visible checkpoints at 30, 60, 90, 135 and 165 minutes; tune them in rehearsal.

Both assume someone notices. With **15–30 independent workstreams** ([ticket 20](../../challenge-spec/issues/20-cohort-skill-floor-licensing.md))
and a handful of coaches, a person who is quietly stuck — not blocked on tooling, just going
slowly down a wrong branch — is invisible. A high skill floor makes this *worse*, not better:
experienced practitioners do not put their hand up, they keep debugging.

And these are practitioners who will not ask. The failure mode is not a room of blocked people; it
is a room of absorbed people who look fine at 11:00 and have nothing to submit at 12:30.

### The decomposition that matters

The brief conflates two problems. They are not the same mechanism.

| | Direction | Question it answers |
|---|---|---|
| **Tempo** | one-to-many, broadcast | *Where should I be right now?* |
| **Sensing** | many-to-one | *Who is quietly stuck?* |

A visible tempo does not help a coach notice anybody. What it does is move the noticing to the
**participant**: stuckness becomes self-diagnosed rather than coach-diagnosed. That is the thing
that scales to 30 workstreams, because it is the only mechanism whose cost does not grow with the
cohort.

**This ticket decides tempo.** Sensing, the raise-hand affordance and what coaches become is
[02](02-help-protocol.md), which this blocks.

## The candidate field

Drafted during charting so this session starts from a real field. Not pre-decided — reject any of
them.

**1. The rabbit — a live reference run.** An organizer works the identical ladder on a projected
screen, deliberately ~10–15 minutes ahead, narrating as they go. Ambient: look up at any moment and
see where you should be, and what it looks like when it is working.
*For:* it makes ticket 14's arc — *manual analysis is tedious → `civ` is the facilitator* — visible
rather than asserted. It is also the only candidate that shows people **what good looks like**.
*Against:* it is a spoiler. *Mitigation:* the rabbit runs the **warm-up route only**, never a scored
development route. Also costs a dedicated organizer for three hours.

**2. The board — a standing tempo display.** Always-on: current stage, current minute, next beat,
and the artifact you should be holding by now.
*For:* passive, cheap, no spoiler, no interruption, works while someone is head-down.
*Against:* tells you *that* you are behind, not what to do about it. Weak alone; strong as backing.

**3. The heartbeat.** A fixed beat every 15 minutes, one spoken line: *by now you should have…*
*For:* lowest tech in the room.
*Against:* highest interruption cost, and it punishes exactly the deep work the event wants.

**4. Telemetry.** `civ` reports milestones to a room leaderboard; the room's own progress becomes
the tempo — *11 of 22 workstreams have their first Reims event.*
*For:* the only candidate that also solves **sensing**, and the tempo it broadcasts is real rather
than planned. *Against:* build work in `civ` that nobody has scoped, needs a room LAN, and it edges
against local-first (defensible — a LAN is not SaaS, and [ticket 17](../../challenge-spec/issues/17-dataset-subsetting-and-distribution.md)
already contemplates an organizer machine on the network). Risk of turning tempo into a scoreboard,
which is a different and more corrosive pressure.

**5. The pace card.** A printed minute-by-minute card per desk.
*For:* zero infrastructure. *Against:* zero room energy, and it is the thing people stop reading at
minute 40. Belt-and-braces, not a mechanism.

### Leaning from charting, to confirm or reject

**1 + 2** as the pace car — the rabbit for the arc, the board for the ambient reference — with **4**
considered under [02](02-help-protocol.md) as the coach's radar rather than as tempo, so that
sensing does not get built as a scoreboard.

## What this ticket must decide

- Is tempo **primary** and coaching the exception, or is §4.7's ordering right after all?
- Which form(s), and who drives them for three hours.
- **The minimum viable form and its degraded fallback** — required output, because
  [08](08-room-requirements.md) cannot state what the venue must provide until this ticket says what
  it needs, and the design must survive a venue with one screen.
- The **spoiler boundary**: exactly what the rabbit may show, given eight sealed Kashiwa routes and
  four sealed Reims chunks. If the rabbit is one lap ahead on the warm-up route, what does it do
  for the remaining 150 minutes?
- What the pace car does when **the room is broadly ahead of it, or broadly behind it**. A pace car
  that is wrong for 20 workstreams is worse than none.
- Whether it launches from the warm-up ([05](05-warm-up-and-environment-gate.md)) and what it does
  at the 12:30 close.

## Why this is a prototype ticket

"How should it behave" is the key question, and the field above cannot be settled by argument.
Cheap artifacts to react to: a sketch of the board's actual contents at four different minutes, and
a written script of two minutes of rabbit narration at the Formalize→Scale boundary. If the
narration reads as a spoiler on paper, it will be one in the room.

## Why this is on the frontier

Nothing blocks it, and it blocks the most: [02](02-help-protocol.md), [03](03-cadence.md),
[08](08-room-requirements.md), and through them [13](13-coach-guide-and-checkpoints.md).

## Answer

**Yes — tempo is primary. The pace car is a rabbit plus a board: a live reference run on a decoy
event, and an always-on statement of budget. Coaching becomes the exception handler.**

Prototype: [`prototypes/01-board-and-narration.md`](../prototypes/01-board-and-narration.md) — the
board rendered at four minutes, and two minutes of rabbit narration written out.

### Why tempo is primary — the argument that decided it

The binding constraint on this event is **not skill, and not blockage. It is budget awareness.**

Every participant is an experienced practitioner ([ticket 20](../../challenge-spec/issues/20-cohort-skill-floor-licensing.md))
and every one of them can do this work. What they cannot do is do it in 180 minutes without knowing
the budget. A practitioner who spends 70 minutes perfecting a Kashiwa detector has done excellent
work and failed the event — and **nothing in the current design tells them 70 is too many.** The
rubric does not: it rewards quality. The ladder does not: it is a document nobody re-reads. The
coach does not: they are with someone else, and could not tell in ten seconds whether this person is
productively deep or lost.

That is why §4.7's reactive model fails, and it fails for a reason more specific than coach ratio:
**the failure mode is invisible from outside.** Not "blocked" — absorbed, down a defensible branch,
looking fine at 11:00 with nothing to submit at 12:30. No amount of roaming detects that.

Broadcast tempo is the only mechanism whose cost is **O(1) in cohort size**. It works by moving the
noticing to the participant: stuckness becomes self-diagnosed. Everything else in this map's
facilitation design is downstream of that inversion.

### The two mechanisms, and what each is for

**The board — always on, and it is the primary mechanism.** Five fields: wall clock, current stage,
`BY NOW YOU SHOULD HAVE`, `IF YOU DON'T`, next beat — plus `RABBIT IS AT`.

Drafting it produced the finding that matters: **`IF YOU DON'T` is the field that carries the
design, and every one of them is a permission to do less.** *Pick any one, precision is not the
lesson yet.* *Loosen the threshold until it fires.* *Stop improving it anyway.* The pace car's
content is not "hurry up"; it is "you are allowed to stop". In a room selected for expertise, that
is the permission nobody grants themselves.

**The rabbit — a live reference run, and it is the accelerant.** A dedicated organizer works the
same ladder on a projected screen, narrating, on the **published warm-up route**, building a
**decoy detector**.

### The spoiler boundary — the decoy rule

This is the part that makes a rabbit viable at all, and it took the prototype to find.

A rabbit that demonstrates the real event is impossible: showing a working Kashiwa turn spec hands
over 15 points, and showing the Reims remap hands over the comprehension test. But a rabbit that is
*coy* — "I have a condition here, never mind what it is" — is unwatchable, and an unwatchable rabbit
is a wasted organizer for three hours.

**So the rabbit targets a different event class entirely.** Hard braking on the warm-up route.
[Ticket 09](../../challenge-spec/issues/09-detector-authoring-surface.md) notes the INBOX
example was already hard-braking, so there is precedent and the class is unmistakably distinct.

The rule, stated so a driver can apply it live:

| The rabbit may | The rabbit may never |
|---|---|
| Show any `civ` command, any EventSpec section, any PlotJuggler operation, any failure iteration | Target a turn, of any handedness |
| Work the published warm-up route and Reims development chunks `_0`–`_4` | Touch a sealed route or chunk |
| Narrate its own false positives and dead ends | **Discuss handedness** |

**Handedness is the line.** [Ticket 18](../../../../../.scratch/civ2026-challenge-spec/issues/18-urt-operational-definition.md)
made the transfer a comprehension test — *the turn that crosses oncoming traffic*, right in Kashiwa,
left in France — and that is the one thing the rabbit must never illuminate.

### What the rabbit does for the remaining 150 minutes

It walks the **whole** ladder on the decoy, including the transfer. But its lead inverts:

- **Kashiwa half: ~12 minutes ahead.** Spoiler risk is lowest and acceleration is worth most.
- **From the transfer beat: ~10 minutes behind.** It arrives at the Reims stack *after* most of the
  room. Anyone moving has already passed it; anyone stuck on grunt work finds a demonstration
  waiting.

**The rabbit leads on mechanics and trails on comprehension.** One rule, and it inverts exactly
where the spoiler risk inverts.

This does mean the rabbit eventually demonstrates *deriving speed from `/fix_velocity` on a stack
with no vehicle bus* — the topic-archaeology half of the transfer. That is deliberate:
[ticket 18](../../../../../.scratch/civ2026-challenge-spec/issues/18-urt-operational-definition.md) explicitly
converts transfer *from a topic remap into a comprehension test*, so the remap is not what is being
scored. Removing grunt work while leaving the comprehension test intact aims the difficulty at the
thing worth testing.

**Flagged as the sharpest judgement call in this resolution.** If it is rejected, the cheap fallback
is: the rabbit stops at the transfer beat and the Reims half is board-only. That costs the stuck
participants and costs nothing else.

### Telemetry is rejected as tempo

[Ticket 25](../../challenge-spec/issues/25-geofence-agent-track.md)-style instrumentation —
`civ` reporting milestones to a room board — is the only candidate that also solves sensing, and it
is still the wrong answer **here**, for a reason independent of build cost:

**Telemetry is descriptive; tempo must be prescriptive.** A board reading *14 of 22 workstreams have
their first event* describes the room. On a slow morning it broadcasts *being 20 minutes behind is
normal* — it normalises the failure it exists to prevent. Every line on the board must be a
statement of **budget**, never of state.

Sensing is a real problem and it is [02](02-help-protocol.md)'s. Deciding it there keeps it built as
a coach's radar rather than as a live leaderboard —
[ticket 21](../../challenge-spec/issues/21-pitch-and-judging-model.md) deliberately put the
leaderboard at 14:30.

### Minimum viable form and degraded fallback

Required output for [08](08-room-requirements.md).

| Available | Design |
|---|---|
| **Two surfaces + a driver** | Full design. Board permanent on one, rabbit live on the other |
| **One surface + a driver** *(minimum viable)* | Board permanent. Rabbit **takes the screen for four scheduled slots of ~4 minutes** at beats, then hands back. Preserves both mechanisms; loses ambient glanceability of the rabbit — which `RABBIT IS AT` partly covers anyway |
| **No surface** | Printed pace cards per desk + spoken beats. Survivable, weak, and the rabbit is gone entirely |

**The board is what survives.** If exactly one mechanism can exist, it is the board: self-diagnosis
is the primary mechanism and the rabbit is an accelerant on top of it.

### When the room is broadly ahead or behind

- **Behind:** the driver has **one licensed adjustment for the day** — declare a *stage slip* once,
  moving all remaining beats. **The 12:30 deadline never moves**, so a slip is spent out of the
  Challenge stage, and the board says which stage paid. One adjustment, stated in advance, so it is
  a decision rather than a drift.
- **Ahead:** nothing adjusts. Early finishers submit early and may attempt the extension bonus
  ([04](04-extension-placement.md)).

### Staffing consequence

**The pace car driver is a dedicated role for three hours and cannot also coach.** Coaches are
counted on top ([02](02-help-protocol.md)). This is a headcount fact both [02](02-help-protocol.md)
and [15](15-language-of-the-room.md) inherit — and if the room is bilingual, the driver is the one
person whose language coverage is not optional.

### Launch and close

The rabbit launches from the warm-up ([05](05-warm-up-and-environment-gate.md)) — same route, same
first commands, which is what lets the warm-up double as an environment gate without a second
setup. At 12:30 the board freezes on the close and the rabbit stops; the afternoon is
[12](12-results-block.md)'s.

### Not decided here

The **minutes** are [03](03-cadence.md)'s — this ticket fixes the board's shape and the rabbit's
register, not the schedule. The **decoy's viability in the data** is
[16](16-decoy-event-class.md).

## Update — the rabbit dissolves into timed teaching material

**There is no live rabbit.** The pace car is **the board plus a set of timed teaching cards**:
small, targeted units, each scoped to one concept or step, each *showing* how it is done,
pre-authored, released on a schedule, and pullable forward or held by a coach live.

Design and open questions move to [17](17-attendee-page.md). What follows is why, and what it
changes here.

### Why the live rabbit was wrong

**A live rabbit penalises deep work.** It is a broadcast at a moment: it helps you only if you are
stuck *and* looking up *and* it happens to be on the right step. The people most likely to miss it
are the ones head-down doing exactly what the event wants — and having missed it, they cannot get it
back. Teaching that is missable is a design flaw, not a delivery detail.

Material is available **when the participant needs it**, per workstream, at no cost per extra
participant. It is strictly better at the job the rabbit was worst at, and the two moments the
rabbit was genuinely good at — the `merge_gap` collapse and the narrated false positive — survive
intact as cards.

### What this changes

| | Was | Now |
|---|---|---|
| Staffing during the session | 1 organizer, 3 hours, cannot coach | **None.** That person coaches |
| Screens | 2, degrading to 1 | **1** — the board |
| `RABBIT IS AT` board field | where the rabbit has got to | **`LATEST CARD`** — what just unlocked |
| `IF YOU DON'T` | a one-line recovery with nowhere to point | points at the card that shows it |
| Room broadly behind | "one licensed stage slip" per day | **replaced by live override** — a coach holds or advances the schedule. The clumsy rule is unnecessary |
| Failure mode | live demo goes wrong, in front of everyone | a card is badly written, and is fixed once, before the day |

### What survives unchanged

- **Tempo is primary; coaching is the exception handler.** The argument was never about the rabbit.
- **The board**, in full — five fields, budget never state, `IF YOU DON'T` as a permission to do
  less. Its one changed field is above.
- **Telemetry stays rejected as tempo**, on the same descriptive-versus-prescriptive ground.
- **Handedness is still the line.** No card may resolve *the turn that crosses oncoming traffic*.

### The decoy mostly stops mattering

The decoy existed because a *continuous, public, live* rabbit could not show the real event without
leaking and could not be coy without being unwatchable. **Pre-authored material released to everyone
at once has neither problem** — there is no advantage to whoever looked up at the right second.

More to the point, most cards teach the **toolchain**, not the event: sample-versus-interval,
`timing`, clip extraction, reading a manifest. Those need *an* example, not a *safe* one.

So hard braking survives as a **convenience**, not a spoiler-avoidance device, and
[16](16-decoy-event-class.md) shrinks accordingly — one clean demonstrable instance for one card,
Kashiwa only. It is no longer a lead-time dependency on three hours of material.

## Update 2 — the board collapses into the page; the only live thing is the opening briefing

Final shape. Two mechanisms, and neither needs an operator during the session:

1. **An opening briefing**, before the hackathon starts. Human, short, and **organizational rather
   than technical**: where things are, what you are looking for, and what to do if you get lost.
   This is the *only* live delivery in the day.
2. **The attendee page**, which progressively shows **what was expected**, on a timetable — with
   hints, tips and eventually solutions released in step. Design is [17](17-attendee-page.md).

### The board is gone

It was a separate always-on display carrying `BY NOW YOU SHOULD HAVE` / `IF YOU DON'T`. The page
now carries exactly that, per stage, so the board is duplicate content on a second surface with a
second thing to keep in sync.

**What is lost is the channel, not the content:** a page needs a tab switch, and someone deep in
PlotJuggler does not switch tabs. The lazy fix is one artifact in two placements — **project the
same page at the front**. No extra authoring, no extra operator, and the venue ask drops to one
optional screen.

The board's design work is not wasted: its five fields and the finding that **`IF YOU DON'T` is the
field that carries the design** become the shape of each stage's section on the page. The mockups in
[`prototypes/01-board-and-narration.md`](../prototypes/01-board-and-narration.md) still read
correctly as page sections.

### Solutions are now in scope, and they are the sharp edge

*Hints/tips/**solutions** in a timely manner* is a genuine change: nothing before this released
answers. It is what makes the day finishable — §3.4 wants **80% of entries to complete both dataset
runs** — and it is also what compresses the scoring.

The rule this ticket sets, for [17](17-attendee-page.md) to implement:

- **A stage's solution unlocks only once that stage's points are effectively settled.** Kashiwa's
  unlocks at the transfer boundary. It does not rescue a Kashiwa score; it unblocks the Reims
  attempt, which is where the difficulty was deliberately moved
  ([ticket 14](../../../../../.scratch/civ2026-challenge-spec/issues/14-bespoke-collection-scope.md)).
- **Solutions are reconstructable, not copy-pasteable.** The approach, the signals, the shape of the
  timing block — not a runnable spec. Preserves a gradient and keeps assembly as real work.
- **Handedness is never solved.** Unchanged, and it is now the only thing in the day that is
  genuinely unaided.

**Consequence to hand over, not to swallow:** this compresses Kashiwa's 15 Detection points.
[Ticket 20](../../challenge-spec/issues/20-cohort-skill-floor-licensing.md) already calls the
Kashiwa core a warm-up so some compression is intended, and map one has already licensed the 15/10
split to move after the internal evaluator run — **so this is an input to that tuning.** Say so when
handing over; do not let it be discovered.

### The staffing ledger, which was the point

| | Before the day | During the session |
|---|---|---|
| Live teaching | — | **none** |
| Pace car driver | — | **none** |
| Board operator | — | **none** |
| Briefer | write it | ~5 minutes, once, at the start |
| Page | author content + timetable (Phase 4) | runs itself; a coach may nudge the schedule |
| Coaches | brief them | coaching, full-time, all of them |

Everything expensive moved to before the day, where it can be reviewed, rehearsed and fixed. Nothing
during the session depends on a person being in the right place at the right minute.
