# Prototype — the tempo board at four minutes, and two minutes of rabbit narration

> **Superseded in form, kept as a primary source.** [Ticket 01](../issues/01-pace-car.md) went on to
> remove the live rabbit and then the board itself. Everything now lives on
> [the attendee page](../issues/17-attendee-page.md).
>
> What still stands, and is why this file is kept: **the four mockups read correctly as that page's
> per-stage sections** — drop the `RABBIT IS AT` line — and they are the evidence for the finding
> that **`IF YOU DON'T` is the field that carries the design**. Part 2 is no longer a live script;
> it is the draft of the two teaching units worth keeping, and the verdict below is why.

Throwaway artifacts made to answer [ticket 01](../issues/01-pace-car.md). The question they exist to
settle: **does the rabbit read as a spoiler on paper?** If it does, it will be one in the room.

Times below use §4.2's rehearsal baseline (Observe 09:30, Formalize 10:00, Scale 10:30, Transfer
11:00, Challenge 11:45, Submit 12:15). **The minutes are [ticket 03](../issues/03-cadence.md)'s to
set.** What this prototype fixes is the board's *shape* and the rabbit's *register*.

---

## Part 1 — the board, rendered at four minutes

Five fields, plus the rabbit's position. Everything is legible from the back of a room.

### 09:52 — Observe, mid-stage

```
┌──────────────────────────────────────────────────────────────┐
│  09:52                                submissions close 12:30│
│                                                              │
│   OBSERVE                                    next beat 10:00 │
│                                                              │
│   BY NOW YOU SHOULD HAVE                                     │
│   →  one candidate interval, found by eye, written down      │
│                                                              │
│   IF YOU DON'T                                               │
│   →  pick any one. Precision is not the lesson yet.          │
│                                                              │
│   RABBIT IS AT   PlotJuggler — choosing which signal to trust│
└──────────────────────────────────────────────────────────────┘
```

### 10:22 — Formalize, mid-stage

```
┌──────────────────────────────────────────────────────────────┐
│  10:22                                submissions close 12:30│
│                                                              │
│   FORMALIZE                                  next beat 10:30 │
│                                                              │
│   BY NOW YOU SHOULD HAVE                                     │
│   →  a condition that fires at all — even a bad one          │
│                                                              │
│   IF YOU DON'T                                               │
│   →  loosen the threshold until it fires, then tighten it.   │
│                                                              │
│   RABBIT IS AT   adding timing: watching 41 hits become 6    │
└──────────────────────────────────────────────────────────────┘
```

The mid-stage beat is the one §4.7's 30/60/90 checkpoints cannot express. *A condition that fires at
all, even a bad one* is a much lower bar than "finished Formalize", and it is the bar that catches
someone at 10:22 rather than telling them at 10:30 that they are already late.

### 11:02 — the transfer boundary

The hardest board of the day.

```
┌──────────────────────────────────────────────────────────────┐
│  11:02                                submissions close 12:30│
│                                                              │
│   TRANSFER                                   next beat 11:20 │
│                                                              │
│   BY NOW YOU SHOULD HAVE                                     │
│   →  a Kashiwa detector you are willing to stop improving    │
│                                                              │
│   IF YOU DON'T                                               │
│   →  stop improving it anyway. Submit what you have,         │
│      then open the Reims data. Ten points are over there.   │
│                                                              │
│   RABBIT IS AT   still on Kashiwa — one failure to look at   │
└──────────────────────────────────────────────────────────────┘
```

Two things this board is doing that no other mechanism in the design does:

- It issues the **abandon-and-move instruction** that [ticket 03](../issues/03-cadence.md) identifies
  as the day's cliff, and it issues it to the whole room at once so it is not a personal verdict.
- *A detector you are willing to stop improving* is deliberately not *a working detector*. It asks
  for a decision, not an achievement, so someone whose detector is poor can still comply.

### 12:19 — Submit

```
┌──────────────────────────────────────────────────────────────┐
│  12:19                                submissions close 12:30│
│                                                              │
│   SUBMIT                                     close in 11 min │
│                                                              │
│   BY NOW YOU SHOULD HAVE                                     │
│   →  a submission already accepted — and be improving it     │
│                                                              │
│   IF YOU DON'T                                               │
│   →  submit an incomplete one now. You can submit again.     │
│                                                              │
│   RABBIT IS AT   submitted at 12:05                          │
└──────────────────────────────────────────────────────────────┘
```

*Rabbit submitted at 12:05* is the whole early-submit policy delivered without a lecture. It depends
on [ticket 09](../issues/09-submission-intake.md) allowing resubmission; if it does not, this board
is a lie and the rabbit must not model it.

### What the four mockups taught

1. **`IF YOU DON'T` is the field that matters.** Drafting these, `BY NOW YOU SHOULD HAVE` was easy
   and almost useless on its own — it tells a stuck person they are stuck, which they know. The
   recovery line is where the design lives, and every one of them is a *permission to do less*. That
   is the pace car's actual content: not "hurry up" but "you are allowed to stop".
2. **The board must never state the room's actual state.** Every line above is a statement of
   *budget*. A board that said "14 of 22 workstreams have their first event" would be describing,
   and on a slow morning it would normalise being behind. See the telemetry rejection in the answer.
3. **`RABBIT IS AT` is what makes two screens one mechanism.** Without it, the board and the rabbit
   are separate things competing for attention. With it, the board tells you whether looking up is
   worth the interruption.

---

## Part 2 — two minutes of rabbit narration, Formalize → Scale

**Setup.** The rabbit is a dedicated organizer working the *published warm-up route* on a projected
screen, ~12 minutes ahead of the baseline. It is building a **hard-braking** detector — a decoy event
class, not the turn that crosses oncoming traffic. Delivered conversationally, at working volume, to
nobody in particular. Nobody is required to watch.

> *[on screen: PlotJuggler, longitudinal velocity plotted, a spec file open beside it]*
>
> "Okay — so I've got a condition that fires. Deceleration below my threshold. Let me just run it
> and see what falls out.
>
> *[runs `civ detect`]*
>
> Forty-one events. On one route. Which is obviously wrong — I did not brake hard forty-one times.
> So let's look at what it actually caught.
>
> *[opens the events list]*
>
> There — and there, and there. Look at the timestamps: 0.04 seconds apart. That's not forty-one
> brakings. That's *one* braking, sampled forty-one times, and my condition is true at every sample.
> Which is the thing I want you to notice, because it is going to happen to all of you: a threshold
> gives you samples, and what you want is intervals.
>
> So — `timing`. Minimum duration, so a single noisy sample doesn't count as an event. And a merge
> gap, so two hits half a second apart are understood as one thing.
>
> *[edits the spec, reruns]*
>
> Six. That's more like it. And now the interesting question is whether six is *right* — because I
> could get any number I like by moving that merge gap, and I have no way of knowing which one is
> true unless I go and look.
>
> *[extracts a clip, plays it]*
>
> That one's real. That one's real. That one — that's a speed bump, and I'm calling it a braking
> event. So that's a false positive I've now got to decide what to do about, and *that* is the thing
> worth writing down, because 'here's a case my detector gets wrong and here's why' is worth more in
> the report than a clean number.
>
> Right. I'm going to go and run this across the rest of the route. You should be somewhere around
> having a condition that fires."

**Duration:** ~2 minutes at speaking pace.

### The verdict this prototype was built to produce

**It does not read as a spoiler.** Every mechanic in it — `civ detect`, the sample-versus-interval
problem, `timing`, `merge_gap`, clip extraction, an honest false positive — is a property of the
*toolchain*. Nothing in it is a property of the *event*. There is no threshold anyone can copy,
because deceleration is not what is being scored, and no discussion of what makes a turn a turn.

Three things the script surfaced that argument alone would not have:

1. **The decoy is not a compromise, it is better.** A rabbit demonstrating the real event would have
   to be coy — "I've got a condition here, never mind what it is" — and coyness is unwatchable. Hard
   braking lets the rabbit be completely open, which is the only register in which this works.
2. **The `merge_gap` moment is the single most valuable two minutes in the day**, and it is exactly
   what [ticket 09](../../challenge-spec/issues/09-detector-authoring-surface.md) called the
   non-negotiable rung: *without `timing`, a team emits one detection per sample where yaw rate was
   high, not one per turn.* 41 → 6 shows that in fifteen seconds. Told rather than shown, most people
   discover it at 11:30 by scoring badly.
3. **The rabbit must narrate its own failure.** The speed-bump false positive is doing more work
   than everything before it: it is the only mechanism in the entire event design that demonstrates
   §2's *failure is a deliverable* claim **before** the participant is asked to produce one. A rabbit
   that only succeeds teaches the opposite of what the rubric rewards.

### What the script also exposed as a build dependency

The narration assumes the warm-up route contains hard-braking events, that a naive threshold really
does produce a wildly over-counted number, and that at least one of them is a defensible false
positive. All three are plausible and none is verified — nobody has looked. Graduated as
[ticket 16](../issues/16-decoy-event-class.md).
