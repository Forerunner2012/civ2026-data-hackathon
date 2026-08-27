# Minute-level cadence: the run of show at the resolution the room actually needs

Type: grilling
Status: resolved
Blocked by: 01, 04, 05

## Question

`HACKATHON-HANDOFF.md` §4.2 gives a six-stage ladder across three hours and calls itself, correctly,
a **rehearsal baseline, not an immutable minute plan**:

| Time | Stage |
|---|---|
| 00:00–00:30 | Observe — inspect one Kashiwa development route manually |
| 00:30–01:00 | Formalize — write and run a first EventSpec |
| 01:00–01:30 | Scale — batch the Kashiwa detector, inspect one failure |
| 01:30–02:15 | Transfer — map the event onto Reims IMU, GNSS velocity and object topics |
| 02:15–02:45 | Challenge — compare both datasets, resolve ambiguity, prepare the report |
| 02:45–03:00 | Submit |

Map one licensed this to move. **What it cannot do is stay at 30-minute resolution**, because a pace
car needs beats and a coach needs to know what "on time" means at 11:07.

## What this ticket must decide

### The beats

What the pace car actually announces, at what minutes, and what artifact each beat asserts you
should be holding. §4.7 proposes checkpoints at **30, 60, 90, 135 and 165 minutes**; those are
stage boundaries wearing a checkpoint's clothes. A beat that only ever fires when a stage ends tells
you you are late after it is too late to act.

Decide whether beats sit **inside** stages — a mid-stage beat at minute 45 saying *you should have a
condition that fires at all, even a bad one* is worth more than one at minute 60 saying *you should
have finished*.

**[01](01-pace-car.md) has resolved and it fixes the shape each beat must fill**, leaving only the
minutes to this ticket. Every beat is five fields: stage, `BY NOW YOU SHOULD HAVE`, `IF YOU DON'T`,
next beat, and where the rabbit is. Two constraints fall out of it:

- **`IF YOU DON'T` is mandatory and it is always a permission to do less.** A beat without a
  recovery line tells a stuck person they are stuck, which they already know. Any minute this ticket
  chooses must have a stateable recovery, or it is not a beat.
- **Beats state budget, never room state.** No beat may describe how the room is actually doing.
- **This ticket's minutes *are* the release timetable for [the attendee page](17-attendee-page.md).**
  One artifact, not two: each beat unlocks that stage's expectation, hints, tips and — once the
  stage's points are settled — its solution. A beat whose recovery line has nothing behind it on the
  page is only half a beat, and the page is where `IF YOU DON'T` points.

Worked examples of all five fields at four different minutes are in
[`prototypes/01-board-and-narration.md`](../prototypes/01-board-and-narration.md), including the
transfer-boundary board, which is the hardest.

### The three structural risks in the baseline

1. **The 00:00–00:30 Observe block is manual by design.** [Ticket 14](../../civ2026-challenge-spec/issues/14-bespoke-collection-scope.md)
   wants the room to *feel how tedious finding events by hand is*. That is deliberate friction in the
   window where [ticket 04](../../civ2026-challenge-spec/issues/04-target-machine.md) says
   environment failure lands. Two forms of pain in the same thirty minutes, and only one of them is
   pedagogical. [Ticket 05](05-warm-up-and-environment-gate.md) resolves the shape; this ticket
   resolves how many minutes it gets.
2. **The 01:30 transfer boundary is the cliff.** A participant whose Kashiwa detector is not working
   at 01:30 has to choose between finishing it and starting the thing worth 10 points on a dataset
   that shares no topics. Nothing in the current plan makes that choice for them. Decide whether the
   cadence issues an explicit **abandon-and-move instruction**, and whether the pace car says it out
   loud.
3. **02:45–03:00 for Submit is fifteen minutes for a reproduction run, a one-page report and an
   upload, times up to 30 workstreams hitting intake at once.** The report carries 45 points.
   Fifteen minutes is not a report-writing budget; it is a report-pasting budget. Decide whether
   report writing is folded earlier — a "write heading 3 now" beat at the transfer boundary, while
   what transferred is fresh — or whether Submit grows.

### The extension no longer complicates this — [04](04-extension-placement.md) resolved

**Plan 09:30–12:30 only.** No optional branch, no second population. The extension exercise is a
page section unlocked at 12:30; the run of show deliberately does not budget for the in-session
route.

### The opening is fixed — [05](05-warm-up-and-environment-gate.md) resolved

Roughly ~5 briefing / ~10 analogue marking with the gate running underneath / ~5 comparison /
~10 first `civ` run. That is thirty minutes and fits §4.2's Observe block without borrowing from
Formalize. **The minutes are still this ticket's**, but the shape is not.

### Output

A minute-level run of show for 09:30–12:30, with each beat's line and the artifact it asserts. The
afternoon is [12](12-results-block.md). §4.2 gets rewritten from this.

Keep the stage **order** and the **12:30 deadline** — both are shut. Everything between is open.

## Why it is blocked

The beats are the pace car's beats ([01](01-pace-car.md)); the opening block's length depends on
what the warm-up is ([05](05-warm-up-and-environment-gate.md)); and whether the plan carries an
optional branch depends on [04](04-extension-placement.md).

## Answer

**Seven beats after a choreographed opening; the report is written in three instalments rather than
at the end; and the transfer cliff is survivable because the Kashiwa solution unlocks exactly
there.**

### The finding: the solution is what makes "abandon" possible

Risk 2 was the cliff — a participant whose Kashiwa detector does not work at 11:00 must choose
between finishing it and starting the thing worth 10 points on a stack that shares no topics.
Telling them to move on does not work; it asks someone to abandon their only asset and walk into
harder terrain with nothing.

[01](01-pace-car.md)'s rule — *a stage's solution unlocks once its points are settled* — lands the
Kashiwa solution at **exactly this beat**. So 11:00 is not an instruction to abandon. It is:

> Stop improving it. Submit what you have. **Here is the Kashiwa solution.** Open the Reims data.

The solution is what makes abandoning psychologically possible, and it converts the day's most
dangerous moment into its most useful one. Nothing else in the design does this.

### The run of show

Opening is choreographed collectively per [05](05-warm-up-and-environment-gate.md), not beaten.
Beats begin once people are working alone.

| Time | | Stage | `BY NOW YOU SHOULD HAVE` | `IF YOU DON'T` | Page unlocks |
|---|---|---|---|---|---|
| 09:30 | | Briefing | — | — | — |
| 09:35 | | Observe | pen on the printed trace | — | — |
| 09:45 | | Observe | compared with a neighbour, and you disagree | — | — |
| 09:50 | | Observe | card down — the gate passed | card stays up; a coach is coming | — |
| **10:00** | **B1** | Formalize | a first `civ detect` on the warm-up route | run the shipped example spec unchanged and look at its output | Formalize expectation + hints |
| **10:20** | **B2** | Formalize | a condition that fires at all — even a bad one | loosen the threshold until it fires, then tighten | Formalize tips |
| **10:40** | **B3** | Scale | events across more than one route, and one failure you can name | run one route and move on — batch is not the lesson. **Write headings 1 and 2 now** | Scale hints + tips |
| **11:00** | **B4** | Transfer | a Kashiwa detector you are willing to stop improving, submitted once | stop improving it anyway. Submit what you have, take the solution, open the Reims data | **Kashiwa solution** + Transfer expectation |
| **11:25** | **B5** | Transfer | the Reims signals identified, and a condition that fires | the yaw and speed equivalents are in the hints. The manoeuvre is yours | Transfer hints |
| **11:45** | **B6** | Challenge | Reims events, however imperfect | take what you have. **Write headings 3 and 4 now**, while the transfer is fresh | Transfer tips |
| **12:10** | **B7** | Submit | a submission already accepted — and be improving it | submit an incomplete one now. You can submit again. **Write heading 5** | — |
| 12:30 | | Close | — | — | Reims solution + extension section |

Seven beats, roughly every 20–25 minutes. Stage **order** and the **12:30 deadline** are unchanged;
§4.2's boundaries move by minutes only.

### The report is written in three instalments

Risk 3 was that Submit gave fifteen minutes to a report worth **45 of 100 points** — a
report-pasting budget, not a writing one. Growing Submit steals from the work; so instead each
heading is written **at the beat where its content is freshest**:

| Heading | Written at | Why there |
|---|---|---|
| 1. Question and hypothesis · 2. Signals used, missing, unreliable | **B3, 10:40** | Both are settled by the end of Formalize and get vaguer every minute after |
| 3. What transferred and what did not · 4. One failure and what you changed | **B6, 11:45** | Immediately after the transfer. Heading 3 is the one [ticket 21](../../civ2026-challenge-spec/issues/21-pitch-and-judging-model.md) added to make the transfer insight scoreable, and it is unrecoverable an hour later |
| 5. Downstream action and deployment mode | **B7, 12:10** | Reflective; it is the only one that genuinely belongs at the end |

Three prompts of about five minutes each, plus the final fifteen. **A 30-minute report budget instead
of 15**, taken from time that was going to be spent worse. Submit becomes *finish and check* rather
than *write*.

Each prompt is two lines on the page, not a break in the room.

### Risk 1 is resolved upstream

[05](05-warm-up-and-environment-gate.md) made the manual block analogue and ran the gate underneath
it, so deliberate and accidental friction no longer compete for the same thirty minutes. This ticket
only had to spend the minutes: 5 / 10 / 5 / 10.

### Two requirements this places on other tickets

- **[09](09-submission-intake.md) must allow resubmission.** B4 asks people to submit a partial
  Kashiwa entry at 11:00 and B7 tells them to submit incomplete at 12:10. Both are lies if the first
  submission is final, and the cliff stops working. If 09 decides otherwise, B4 and B7 must change.
- **[17](17-attendee-page.md) must have material behind every `IF YOU DON'T`.** The rightmost column
  is its release schedule. A beat whose recovery has nothing behind it on the page is half a beat.

## Update — no solutions during the session, so the cliff is carried differently

[17](17-attendee-page.md)'s Update 3 moves solution handover to **after** the hackathon. Two rows of
the table above change, and the finding this ticket opened with is **partly withdrawn**.

### What changes

| Beat | Was | Now |
|---|---|---|
| **B4, 11:00** | *…take the solution, open the Reims data* → unlocks **Kashiwa solution** | *stop improving it anyway. Submit what you have and open the Reims data — **the transfer hints are open now**, and a coach will work through it with you.* → unlocks **Transfer expectation + hints** (pulled forward from B5) |
| **12:30 close** | Reims solution + extension section | **Extension section only.** Solutions publish after the event |

Everything else — the seven beats, the minutes, the three report instalments — is unchanged.

### The finding, corrected

This ticket claimed *the solution is what makes abandoning possible*, and that the cliff was
"survivable because the Kashiwa solution unlocks exactly there". **That prop is gone**, so the claim
has to be weaker and honest: the cliff is now carried by **three things, none of which is an answer**
— the permission stated plainly, the transfer hints arriving at the same moment, and a coach.

That is genuinely less strong. It is also the correct trade, because the alternative cost was
**Kashiwa Detection compressing to a near-ceiling category**, which this ticket was quietly
accepting. Detection keeps its full range on both datasets, and the prior handed to the internal
evaluator run is withdrawn.

**Pulling the transfer hints forward from B5 to B4 is the compensation**, and it should be treated as
load-bearing rather than cosmetic: at the moment someone is asked to abandon their work, something
has to arrive.

### Consequence for coaching

[02](02-help-protocol.md) built its cleanest rule — *coaches never hand over solutions, the page
does* — on a page that no longer will. **Around the cliff, coaching becomes the escalation of last
resort again.** Coaches guide *towards* a solution using the two questions; they still do not hand
over a threshold or a spec. [13](13-coach-guide-and-checkpoints.md)'s card must carry the
distinction, because it is now a judgement rather than a rule.

### Left to rehearsal

The minutes are a **rehearsal baseline**, as §4.2 always was. Phase 5 may move any beat. What it may
not move without reopening this ticket: the **three writing instalments**, the **Kashiwa solution at
the cliff**, and the rule that every beat has a stateable recovery.
