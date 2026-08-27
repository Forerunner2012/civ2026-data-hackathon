# Recovery: what happens to a workstream whose environment does not work?

Type: grilling
Status: resolved
Blocked by: 05

## Question

[Ticket 04](../../civ2026-challenge-spec/issues/04-target-machine.md) accepted BYOD with no
recovery hardware and named the mitigation:

> The **non-ROS fallback pack** (§4.7) — pre-extracted tables and clips so data reasoning continues
> when execution does not. This must be built and rehearsed, not sketched.

That is the whole spec. It answers *what do they read* and leaves the harder question untouched.

## The question map one left implicit

**Can someone on the fallback path produce a submission that scores?**

A participant whose container never worked cannot run `civ detect`, `civ clip` or `civ report`.
Against [ticket 21](../../civ2026-challenge-spec/issues/21-pitch-and-judging-model.md)'s rubric that
is:

| Category | Points | Reachable on tables and clips alone? |
|---|---:|---|
| Detection — Kashiwa | 15 | No — needs `events.jsonl` from a run |
| Detection — Reims | 10 | No |
| Evidence and extraction | 15 | No — machine-checks clip validity and volume reduction |
| Reproducibility | 15 | No — one command, pinned inputs, stable rerun |
| Investigation, Quality, Visualization | 45 | Partly — the report can still be written |

So "pre-extracted tables and clips" is a path to **55 points of nothing**. That is not a mitigation;
it is a consolation. And §3.4's success criterion — *at least 80% of entries complete both dataset
runs and a valid submission* — has no room for it.

## The answer map one already wrote down without noticing

[Ticket 17](../../civ2026-challenge-spec/issues/17-dataset-subsetting-and-distribution.md), in its
measurement update:

> **The "send only CLI calls to the organizer's machine" option** stays valuable for full-resolution
> or image-heavy work, and it has a side benefit worth naming: a run that only exists as a CLI
> invocation someone else executes is **reproducible by construction**, which is exactly what the
> Reproducibility category (15 points) is trying to measure.

**"Your spec, our runner."** A shared organizer machine executes `civ` invocations for anyone whose
environment failed. The participant still owns everything §4.5 says they own — signal selection,
thresholds, CEL, timing, evidence windows — and loses only the execution they were never being
scored on. The tables and clips become the *reasoning* support while that happens, not the whole
mitigation.

This turns ticket 04's accepted risk from *you learn but you cannot compete* into *you compete more
slowly*, which is a materially different day for that person.

## What this ticket must decide

- **Is "your spec, our runner" the primary recovery?** If yes it is a real build item — a machine, a
  queue, an operator, a turnaround time — not a leaflet, and it needs an owner before Phase 4.
- **The turnaround budget.** A participant submitting a spec and waiting eight minutes for a result
  cannot iterate. What is the acceptable round trip, and how many concurrent users does it hold at
  the 11:00 peak when everyone is batching?
- **Does it interact with [09](09-submission-intake.md)?** The intake machine and the runner machine
  are plausibly the same box on the same LAN. Decide whether that is efficiency or a single point of
  failure that takes the whole event with it.
- **Fairness.** A recovered participant is slower. Is that simply the cost, or does anything adjust?
  Recommendation to test: **nothing adjusts, and say so in advance.** Silent handicapping is worse
  than a stated cost, and the alternative is a jury arguing about it at 13:00.
- **The fallback pack contents**, now that it is support rather than substitute: which pre-extracted
  tables, at what rate, for **both** stacks (Autoware and ZED/GNSS share no topics), which pre-cut
  clips, and in what format a non-ROS tool can open.
- **Buddying up.** Can a broken solo join a working solo as a duo mid-session? Cheapest recovery
  there is, costs nothing to build, and [ticket 21](../../civ2026-challenge-spec/issues/21-pitch-and-judging-model.md)
  already ranks solo and duo together. Decide whether it is offered or merely tolerated.
- **The trigger and the exit. [05](05-warm-up-and-environment-gate.md) has resolved and delivered
  the trigger:** everyone starts the day with the help card **up**, and puts it down when
  `civ doctor && civ inspect <warm-up>` succeeds. A card still up at the end of the ~10-minute
  analogue block is this ticket's entry condition — concrete, timed, and detected without anyone
  having to admit anything. This ticket decides what happens next, and whether someone who fixes
  their environment at 10:30 rejoins the normal path or stays on the runner.
- **The second trigger, from [02](02-help-protocol.md):** a card showing **side A** — environment,
  tooling, "it will not run" — routes here rather than to coaching, and is **timeboxed to ~10
  minutes** before escalating to "your spec, our runner". This ticket owns what that escalation
  actually is and who performs it.

## Why it is blocked

[05](05-warm-up-and-environment-gate.md) decides whether there is a gate and when it fires. Without
it, "when does recovery start" is a judgement call made under pressure by a coach who is already
busy.

## Update — cut the runner. Pairing already covers it.

**Does this need to exist at all?** No. Everything below stands as reasoning; the build does not.

[08](08-room-requirements.md)'s Update 3 made **pairing the stated mitigation for inadequate
hardware**. It covers a broken container identically, and
[ticket 21](../../civ2026-challenge-spec/issues/21-pitch-and-judging-model.md) already ranks solo and
duo together — so a paired participant has a **complete** entry, not a degraded one. That is a better
outcome than the runner produced, at zero build cost.

What the runner was buying: a scoring path for someone whose container failed. What pairing buys:
the same, instantly, with no machine, no watched directory, no concurrency cap, no plot rendering, no
cold standby, and **no room LAN** — the runner was the last thing on it.

### What this deletes

| Cut | Was in |
|---|---|
| Watched-directory runner, turnaround budget, concurrency cap | this ticket |
| Rendered-plot-image build ask | this ticket |
| Room LAN, switch, cabling, organizer box, cold standby | [08](08-room-requirements.md) |
| LAN-down coach role and rehearsal | [13](13-coach-guide-and-checkpoints.md), [18](18-rehearsal-observations.md) |
| The corporate-VPN failure mode, **entirely** | [13](13-coach-guide-and-checkpoints.md) |

That last one is free: with the page on Funnel and submission on a form, **nothing lives at a local
address**, so there is nothing for a full-tunnel VPN to block.

### What recovery is now

1. **Pair up.** Offered aloud in the briefing ([05](05-warm-up-and-environment-gate.md)); a coach
   suggests it at the gate.
2. **The fallback pack**, on the SSDs already in the room — tables and clips so reasoning continues
   while a container is fixed.
3. Keep fixing it in the background if a coach has time.

**Add the runner only if Phase 5 shows pairing does not cover it.** Cheap thing now, build later on
evidence — the same inversion used for the live rabbit and for telemetry.

---

## Superseded — the original answer

**"Your spec, our runner", built as a watched directory rather than a human queue. The laptop still
works — only the container failed — so recovery has to replace execution, not the workstation.**

### The framing that makes this small

The failure mode everyone pictured was *a broken laptop*. It is not. WSL2 or Docker Desktop failing
leaves a participant with a perfectly good machine: they can edit YAML, read
[the page](17-attendee-page.md), open a browser, look at images. **What they have lost is the ability
to execute `civ`, and nothing else.**

So recovery does not need to reconstruct a workstation. It needs one service: *something runs my
spec and gives me back the outputs.* Everything §4.5 says the participant owns — signal selection,
thresholds, CEL, timing, evidence windows — they still own. They lose the execution they were never
scored on.

### The mechanism: a watched directory, not an operator

Drop `spec.yaml` on the organizer machine; `events.jsonl`, the clips and a run manifest come back.
No queue, no operator, no one to interrupt.

- **A shell loop, not a service.** This is the cheapest thing that works, and it is testable in
  Phase 5 by dropping a file.
- **Turnaround is the runtime plus a polling interval.** No human latency, so iteration stays
  possible — which was the thing an operator-based queue would have destroyed.
- **Reproducible by construction.** The run manifest records exactly what was executed, which is
  what [ticket 17](../../civ2026-challenge-spec/issues/17-dataset-subsetting-and-distribution.md)
  noticed and precisely what Reproducibility's 15 points measure. A recovered participant is not
  disadvantaged on that category — arguably the reverse.
- **Not policed.** It is for people whose gate failed, on the honour system. If someone else uses
  it they simply get slower results than running locally. **Cap concurrency** so it cannot be
  swamped, and otherwise do not build an authorization story for a room of thirty colleagues.

**One build ask, if it is cheap:** have the runner also return a **rendered plot image** of the
signals in each evidence window. Without PlotJuggler a recovered participant cannot see anything,
and Visualization is 15 jury points. One plotting call on the runner keeps that category reachable.
If it is not cheap, say so and accept the loss explicitly rather than discovering it on the day.

### Consolidation with intake

**Same box as [09](09-submission-intake.md), deliberately** — one thing to build, one thing to
harden, one thing to test, and it is already the box serving
[the page](17-attendee-page.md).

That makes it a genuine single point of failure that would take the page, intake and recovery
together. **A cold standby laptop with the same image and the same data is mandatory**, and
[08](08-room-requirements.md) carries it. §3.3 requires the day to survive offline; it must also
survive this box dying at 11:15.

### Fairness: nothing adjusts, and say so in advance

A recovered participant is slower. That is the cost, it is not compensated, and there is no separate
category or leaderboard. Silent handicapping is worse than a stated cost, and the alternative is a
jury arguing about it at 13:00 with no policy to point at.

**Recovery is a service, not a track.** Someone who fixes their container at 10:30 simply stops
using it. Same submission, same rubric, same 12:30.

### Buddying up: offered, not merely tolerated — and it now carries two failure modes

**Upgraded by [08](08-room-requirements.md)'s Update 3.** The organizer's stated mitigation for a
participant arriving with **inadequate hardware** is that they pair into a duo. So buddying up is no
longer only an environment fallback; it covers:

1. **A broken environment** — the container will not run.
2. **Underpowered hardware** — it runs, badly, or not at all.

The second has no other mitigation at all: [ticket 04](../../civ2026-challenge-spec/issues/04-target-machine.md)
accepted BYOD with no spare machines, and "your spec, our runner" helps someone whose container is
broken, not someone whose laptop is merely slow. **That makes pairing the only answer to a real and
likely case**, which raises it from a nicety to a named mitigation.

It must be **offered aloud in the opening briefing** ([05](05-warm-up-and-environment-gate.md)).
Nobody volunteers *my laptop is too weak* to a room of thirty peers unprompted, and the window in
which pairing is still useful closes fast.

A broken solo may join a working solo as a duo, mid-session. It is the cheapest recovery available,
costs nothing to build, and
[ticket 21](../../civ2026-challenge-spec/issues/21-pitch-and-judging-model.md) already ranks solo and
duo together so there is no scoring wrinkle. **Say it in the opening briefing**
([05](05-warm-up-and-environment-gate.md)), because nobody will propose it themselves at 10:15.

### The fallback pack, now that it is support rather than substitute

Its job is to keep *reasoning* possible during the minutes before the runner is in use, and to
support anyone working away from their own machine:

- **Pre-extracted signal tables** — the detector-relevant topics only, at full rate, in a format any
  non-ROS tool opens. **Both stacks**: Autoware and ZED/GNSS share no topics, so this is two packs,
  not one.
- **Pre-rendered signal plots.** [05](05-warm-up-and-environment-gate.md) already requires a printed
  trace of the warm-up route for the analogue block — extend that set rather than authoring a second
  one.
- **A handful of pre-cut clips** per stack.

It is no longer load-bearing on its own, which is the substantive change from
[ticket 04](../../civ2026-challenge-spec/issues/04-target-machine.md)'s framing.

### The two triggers, and what happens at each

| Trigger | When | Action |
|---|---|---|
| Card still up at the end of the analogue block ([05](05-warm-up-and-environment-gate.md)) | ~09:50 | Coach goes over. Fix attempt begins |
| Card raised on **side A** mid-session ([02](02-help-protocol.md)) | any time | Same, timeboxed |

**Timebox: ~10 minutes of fixing, then the runner.** Not "until it is fixed" — an hour lost to
Docker is worse than a day spent on the runner, and the person doing the fixing is a coach who is
needed elsewhere. Fixing may continue in the background; it stops being the participant's problem.

### What this hands on

- **[08](08-room-requirements.md)**: the cold standby laptop, and the box's power and network needs.
- **[09](09-submission-intake.md)**: consolidation is decided here; 09 owns the intake half.
- **[13](13-coach-guide-and-checkpoints.md)**: the 10-minute timebox is a coach instruction, and the
  hardest part of it is stopping.
