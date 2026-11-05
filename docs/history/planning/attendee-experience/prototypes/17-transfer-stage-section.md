# Prototype — the Transfer stage, drafted end to end

> **Amended by [ticket 17](../issues/17-attendee-page.md)'s Update 3.** Solutions are now handed over
> **after** the hackathon, not during it. So the `▸ SOLUTION — Kashiwa` block below is **post-event
> material**, not something that appears at 11:00. What appears at 11:00 is the **tip layer** — the
> hint and tip blocks drafted for 11:25, pulled forward — plus the permission line and a coach.
>
> The drafting still earns its keep: it is what established where the line between *reconstructable*
> and *copy-pasteable* sits, and the withheld comparison direction is still the thing that arms the
> transfer test. It just lands later.

Throwaway artifact for [ticket 17](../issues/17-attendee-page.md). The question it exists to settle:
**does "reconstructable, not copy-pasteable" survive contact with concrete words?**

The Transfer stage is the hardest case in the day. It spans [03](../issues/03-cadence.md)'s **B4
(11:00)**, where the Kashiwa solution unlocks, and **B5 (11:25)**, where the Reims hints do. If the
escalation holds here it holds everywhere.

Placeholders are marked `‹…›` — every number below is derived from data nobody on this map has, and
must be filled by whoever authors the real page.

---

## The stage section as it appears at 11:00 (B4)

```
────────────────────────────────────────────────────────────────
  TRANSFER                                      next beat 11:25
  11:00                             submissions close in 90 min

  BY NOW YOU SHOULD HAVE
  →  a Kashiwa detector you are willing to stop improving

  IF YOU DON'T
  →  stop improving it anyway. Submit what you have, take the
     solution below, and open the Reims data. Ten points are
     over there and none of them are here.

  ── just unlocked ─────────────────────────────────────────────
  ▸ SOLUTION — Kashiwa                                    [open]
  ▸ Transfer: what you are looking for                    [open]
────────────────────────────────────────────────────────────────
```

### ▸ SOLUTION — Kashiwa

> **This is the approach, not a spec. The numbers are yours to derive — they always were.**
>
> Three signals carry it. All of them are in the bags you already have:
>
> | | topic | field |
> |---|---|---|
> | rotation rate | `/localization/acceleration` | `accel.accel.angular.z` |
> | forward speed | `/vehicle/status/velocity_status` | `longitudinal_velocity_mps` |
> | something in the way | `/perception/object_recognition/is_object_detected` | `data` |
>
> The shape of the condition is a **turn happening** and **the vehicle actually moving** — a parked
> vehicle rotating on the spot is not a manoeuvre, and without a speed floor you will find several.
>
> ```yaml
> derive:
>   yaw_smooth: { from: yaw_rate, op: ewma, alpha: ‹pick one› }
>
> condition: yaw_smooth ‹?› ‹THRESH› && speed > ‹MIN_SPEED›
>
> timing:
>   min_duration: ‹how long is the shortest turn you believe?›
>   merge_gap:    ‹how long a pause still belongs to one turn?›
> ```
>
> **What we are not giving you, and why:**
>
> - **`‹THRESH›` and its comparison direction.** Plot `yaw_smooth` over a route you have labels for
>   and read it off. It takes two minutes and it is the only way you will know the sign convention
>   of this vehicle — which you are going to need shortly, and which nobody can hand you.
> - **`min_duration` and `merge_gap`.** These are judgements about what counts as one turn. You
>   already made those judgements this morning with a pen, and you already know your neighbour made
>   them differently.
> - **The evidence window.** Yours. It is scored on whether a human can see the event in it.
>
> If you take this and run it, you should have Kashiwa events in about ten minutes. Then leave it.

### ▸ Transfer: what you are looking for

> The Reims recording is a different vehicle, a different sensor stack, and a different country.
>
> There is **no Autoware stack and no vehicle bus** — no `/localization/*`, no `/vehicle/status/*`,
> no `/perception/object_recognition/*`. What there is: a ZED stereo rig and GNSS.
>
> The event is the same event. It is defined by **what the vehicle does relative to other traffic**,
> not by any topic name and not by any number above.
>
> Two questions to answer before you write anything:
>
> 1. Which topics carry the equivalents of rotation rate and forward speed here?
> 2. **Is the manoeuvre you are looking for the same manoeuvre?**
>
> The second question is the one worth your time.

---

## The same section at 11:25 (B5)

```
────────────────────────────────────────────────────────────────
  TRANSFER                                      next beat 11:45
  11:25                             submissions close in 65 min

  BY NOW YOU SHOULD HAVE
  →  the Reims signals identified, and a condition that fires

  IF YOU DON'T
  →  the signal equivalents are in the hints below. The
     manoeuvre is yours.

  ── just unlocked ─────────────────────────────────────────────
  ▸ HINT — where the Reims equivalents live                [open]
  ▸ TIP — deriving what the stack does not publish           [open]
────────────────────────────────────────────────────────────────
```

### ▸ HINT — where the Reims equivalents live

> You are looking for two things and the bag has both, under different names.
>
> - **Rotation rate.** The ZED publishes an IMU. Look at what an `sensor_msgs/Imu` carries and ask
>   which component of it is the vehicle turning.
> - **Forward speed.** There is no wheel encoder and no vehicle bus. There is GNSS, and GNSS gives
>   you more than position.
>
> `civ inspect` on any Reims development chunk lists every topic and its type. Start there rather
> than guessing.

### ▸ TIP — deriving what the stack does not publish

> Kashiwa handed you smoothed, vehicle-frame quantities. This stack does not.
>
> - IMU angular velocity is **noisier** than what you were reading this morning. The `derive` stage
>   exists for exactly this; whatever smoothing you used on Kashiwa is a starting point, not an
>   answer, and the sample rates are not the same.
> - GNSS velocity is a **vector**. You want the component that means "moving forward", and you
>   should satisfy yourself that it means that on this rig.
> - Sample rates differ across these topics by more than an order of magnitude. Think about what
>   your condition is being evaluated against.
>
> **Not in this tip, and not coming later:** whether the threshold that worked in Kashiwa works
> here. That one is the exercise.

---

## What drafting this settled

### 1. The line holds, and it sits at the numbers — not at the topics

*Reconstructable, not copy-pasteable* looked unworkable in the abstract: naming
`accel.accel.angular.z` felt like handing over the spec. Written out, the split is obvious and
stable:

| Given | Withheld |
|---|---|
| Which signals, by topic and field | Every threshold and duration |
| The shape of the condition | The comparison **direction** |
| Which blocks the spec needs | The evidence window |

**Topic archaeology is lookup work; thresholds are judgement.** Giving the first and withholding the
second costs a participant nothing they were being scored on and saves them the twenty minutes that
were about to eat their transfer.

### 2. The format is the enforcement

The solution above **cannot be pasted and run** — it has `‹…›` holes in it by construction. That is
not a stylistic choice; it is the policy made structural, and it removes any judgement call from
whoever authors the remaining stages. If the YAML is complete, the rule has been broken, and that is
visible at a glance in review.

### 3. Giving away the Kashiwa solution is what *sets* the trap

This is the finding that surprised me, and it inverts the worry the ticket was written with.

The solution deliberately withholds **the comparison direction** — `yaw_smooth ‹?› ‹THRESH›`. A
participant derives it from their own plot, gets a working Kashiwa detector, and carries a signed
threshold into a country where traffic runs the other way.
Ticket 18 designed exactly
this: *copy a threshold and you find nothing.*

So the solution is safe to hand over at 11:00 **because** handing it over arms the comprehension
test. Withholding it would have protected nothing and would have left slow participants with no
Kashiwa detector *and* no transfer.

The trap must not be cruel, and it is not: the 11:25 tip says plainly *whatever worked in Kashiwa is
a starting point, not an answer*, and the 11:00 solution says *you will need the sign convention
shortly*. Two warnings, neither of them the answer.

### 4. The escalation differs in kind, and the kinds are nameable

| | What it gives | Example above |
|---|---|---|
| **Hint** | *where to look.* Never what you will find | "The ZED publishes an IMU. Which component is the vehicle turning?" |
| **Tip** | *a technique or a hazard.* Never a value | "IMU angular velocity is noisier. `derive` exists for this." |
| **Solution** | *the approach in full.* Never the numbers | The table and the holed YAML |

Each is answerable in one line by its author, which is what makes 20-odd units writable in Phase 4
without the ladder collapsing into "more detail, then even more detail".

### 5. Prose plus a holed skeleton beats video, and it is not close

Drafting made the format decision for itself. A participant reading this at 11:20 with seventy
minutes left is **skimming**, and a 60-second recording is a terrible interface for someone in a
hurry — unskimmable, unsearchable, uneditable the week before, and it does not survive
[08](../issues/08-room-requirements.md)'s mandated static USB export.

Screenshots stay for the genuinely visual units — a plot with an interval drawn on it, a clip frame.
Everything else is text.
