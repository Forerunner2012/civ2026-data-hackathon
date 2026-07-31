# The coach guide and the checkpoint prompts: what must each contain?

Type: prototype
Status: resolved
Blocked by: 02, 03

## Question

Map one left this as fog, to *tune against the rehearsal baseline and actual solo/duo pacing*.
[02](02-help-protocol.md) decides what a coach **is**; [03](03-cadence.md) decides **when** the beats
fire. This ticket specifies the two artifacts that carry those decisions into the room.

Per the map's Notes, this map does not author the materials. But checkpoint prompts are the one
place where the words *are* the decision — a prompt that asks the wrong thing is a wrong design, not
a wrong draft. So: **specify both artifacts fully, and draft an exemplar of each**, with the full
set left to Phase 4.

## The checkpoint prompts

Each beat from [03](03-cadence.md) needs a line. A prompt does three things at once and they pull
against each other:

- **asserts** what you should be holding by now (so a participant can self-diagnose — the mechanism
  [01](01-pace-car.md) depends on);
- **offers** the recovery if you are not (so self-diagnosis leads somewhere);
- **does not leak** the answer to a scored dataset.

Decide the fixed shape, then draft two exemplars in full — one from the Kashiwa half, one at the
**01:30 transfer boundary**, which is the hardest and most consequential prompt in the day. It has
to tell someone whose Kashiwa detector still does not work that they should abandon it and move,
without that reading as *you have failed*.

Also decide:

- Are prompts **spoken, displayed, or both**? [01](01-pace-car.md) may already answer this.
- Do they change if the room is broadly behind? A scripted prompt read to a room that is 20 minutes
  late is worse than no prompt.
- Are they bilingual? [15](15-language-of-the-room.md) decides.

## The coach guide

What a coach carries. It must be usable **while standing at someone's desk under time pressure** —
which rules out anything longer than a card, and makes the format part of the decision.

Contents to specify:

- **The intervention rule and the escalation ladder** are both **decided** in
  [02](02-help-protocol.md) — two questions in order, then respond to the hypothesis; and a
  five-row routing table. This ticket's job is to fit them on something a coach can hold while
  standing at a desk, not to redecide them.
- **The give-up policy, as amended.** [02](02-help-protocol.md) originally removed it entirely —
  *coaches never hand over solutions, the page does*. [17](17-attendee-page.md)'s Update 3 moved
  solutions to **after** the event, so the page will not either. What survives is the prohibition
  without its easy justification: **guide towards a solution, never hand one over — and nobody gets
  one today.** Advancing the page still helps the whole room, but it now delivers hints and tips
  rather than answers. Brief this hardest of all: it is a judgement held under time pressure, it
  bites worst at [03](03-cadence.md)'s 11:00 cliff, and the failure is invisible.
- **Cohort under- or over-fill.** Graduated here from the map's fog now that
  [01](01-pace-car.md) and [02](02-help-protocol.md) have chosen their mechanisms. What changes if
  10 people show up, or 40? The per-beat sweep is the thing that breaks first — 40 desks does not
  fit between beats at three coaches — and the coach floor is stated as a floor precisely so this is
  answerable. One paragraph in the guide, not a redesign.
- **A troubleshooting tree** for the environment — Phase 4 lists one; this decides its top ten
  entries, which is a question about *which failures are actually likely* on Windows/WSL2 and
  Ubuntu, not about writing them up.
- **The two topic inventories.** Autoware and ZED/GNSS share no topics
  ([ticket 17](../../civ2026-challenge-spec/issues/17-dataset-subsetting-and-distribution.md)), so a
  coach helping with the transfer needs both to hand. Decide whether that is coach-only or
  participant-facing — if participant-facing it belongs to [14](14-participant-materials.md) instead.
- **What a coach must never say**, including the vocabulary ban from
  [ticket 07](../../civ2026-challenge-spec/issues/07-clean-room-boundary.md): never System,
  Datasource, Signal, Trigger, Recording. A coach reaching for a familiar word at speed is exactly
  how that boundary gets breached in the room, where no test suite can catch it.
- **Coach briefing and rehearsal.** When do coaches get trained, and does the internal
  mini-hackathon double as their rehearsal?

## Why this is a prototype ticket

The prompts cannot be judged in the abstract. Draft them, read them aloud against the cadence, and
see whether the transfer-boundary prompt sounds like help or like an accusation.

## Why it is blocked

The prompts are the beats' words ([03](03-cadence.md)) and the guide is the coach's role written
down ([02](02-help-protocol.md)). Neither exists yet.

## Answer

**The checkpoint prompts are already written — [03](03-cadence.md) drafted all seven. What remains is
one card, and it fits on one card.**

### The prompts are done

[03](03-cadence.md)'s beat table *is* the prompt set: seven beats, each with `BY NOW YOU SHOULD HAVE`
and `IF YOU DON'T`, including the transfer-boundary prompt this ticket was written to worry about.
The three questions it listed are answered elsewhere:

- **Spoken or displayed?** *Displayed*, on [the attendee page](17-attendee-page.md).
  [01](01-pace-car.md) removed all live delivery except the opening briefing, so nothing is read
  aloud.
- **Do they change if the room is behind?** No. The prompts are statements of **budget**, never of
  room state. What changes is the *release schedule*, and [17](17-attendee-page.md) made that
  **advance-only** — a coach pulls material forward, the prompt itself is untouched.
- **Bilingual?** No. [15](15-language-of-the-room.md): professional English, C1 floor.

Phase 4 reviews the wording; it does not redesign it.

### The coach card — exemplar

One card, two sides, carried. It exists to be read while standing at a desk, so everything that is
not usable in ten seconds is not on it.

```
─── FRONT ──────────────────────────────────────────────────────
 BEFORE YOU SAY ANYTHING, ASK — IN THIS ORDER

   1.  "What have you got so far?"
   2.  "What do you think is happening?"

 Then answer the hypothesis. Not the code.

 GUIDE TOWARDS THE SOLUTION. NEVER HAND ONE OVER.
 No thresholds, no specs, not even at 11:00.
 Solutions publish AFTER the event — nobody gets one today.
 If the room needs more, ADVANCE THE PAGE: the next hints
 and tips, for everyone, at once, visibly.

 CARD UP, SIDE A → environment. ~10 min, then the runner.
 CARD UP, SIDE B → approach. This is your job.
────────────────────────────────────────────────────────────────

─── BACK ───────────────────────────────────────────────────────
 WHERE IT GOES

   won't run ................ 10 min, then PAIR THEM UP.
   "what do I do next" ...... the page. Point, don't answer.
   approach / stuck ......... you
   struggling in the warm-up  LEAVE THEM. That is the lesson.
   same question 3x ......... note it. Do not patch the page.

 NEVER SAY
   System · Datasource · Signal · Trigger · Recording
   Say: bag · topic · field · EventSpec · detector ·
        event · clip · manifest

 SWEEP once per beat. Glance, do not interrupt.
 LOG who you spent real time with — the jury needs it.
────────────────────────────────────────────────────────────────
```

Drafting it settled two things. **The vocabulary ban has to be on the card**
([ticket 07](../../civ2026-challenge-spec/issues/07-clean-room-boundary.md)) — a coach reaching for a
familiar word at speed is exactly how that boundary gets breached, and it is the one place no test
suite can catch it. And **"leave them"** has to be printed, because it is the instruction that
contradicts a coach's instinct hardest.

### The troubleshooting tree — the ten that actually happen

Ordered by likelihood on Windows/WSL2 and Ubuntu. Phase 4 writes the fixes; this fixes the list.

1. Docker Desktop not running, or WSL2 backend not enabled
2. Virtualization disabled in BIOS — the one that cannot be fixed in the room
3. **Corporate VPN or firewall blocking the room LAN** — see below
4. Insufficient disk for the image
5. Image never pulled, and no internet on the day
6. Data path wrong, or data never downloaded
7. Mounted-volume permission errors on Windows paths
8. GUI apps cannot display — WSLg or X server
9. Checksum mismatch on the data
10. Container starts but `civ inspect` fails on a schema

**Item 3 is a gap nobody had considered**, and it deserves spelling out because it behaves unlike
every other failure here.

A corporate laptop running an always-on VPN in full-tunnel mode has **local-subnet access disabled by
policy**: the internet works, and a machine on the same room network does not. It is plausible at
this cohort — [ticket 04](../../civ2026-challenge-spec/issues/04-target-machine.md) made the event
BYOD and these are work laptops. *Inferred from the architecture, not observed; treat it as a
plausible failure mode to design for rather than a known one.*

Why it is nasty:

- It hits **one person, not the room**, so it reads as that person being broken rather than as
  infrastructure.
- It takes out **three things at once** for them: [the page](17-attendee-page.md),
  [09](09-submission-intake.md)'s intake, and [06](06-fallback-and-recovery.md)'s runner.
- **Every check we have passes.** `civ doctor` is fine, the container is fine, the internet is fine.
  The only symptom is "I cannot open the page."
- Worst case is the one that matters: they work all morning and find at **12:25 that they cannot
  submit**.

**Gone entirely.** [06](06-fallback-and-recovery.md) cut the recovery runner and with it the room LAN,
so **nothing lives at a local address**. There is nothing for a full-tunnel VPN to block. Drop it
from the list; the gate's third clause survives as a plain internet check, which is worth keeping for
captive portals and dead uplinks.

*Superseded reasoning below, kept because the gate clause came out of it.*

**Mostly solved since this was written.** [17](17-attendee-page.md) moved the page to Tailscale
Funnel and [09](09-submission-intake.md) moved submission to a form, so **both run over the public
internet**, which a full-tunnel VPN routes normally. What remains on the room LAN is
[06](06-fallback-and-recovery.md)'s recovery runner — needed by a handful of people, with sneakernet
via SSD behind it.

So this drops from *takes three services for one person, undetected until 12:25* to *one degraded
fallback path for one person, in the rare case they also need recovery.*

**What survives, and is still worth doing:**

1. **The gate keeps its third clause** — `civ doctor && civ inspect <warm-up>` **and open the page**
   ([05](05-warm-up-and-environment-gate.md)). It is now a general reachability check rather than a
   VPN check: whatever blocks the page — VPN, proxy, captive portal, dead uplink — blocks submission
   too, since both take the same path. It is the only clause that tests anything outside the machine.
2. **"Disable your VPN for the session"** stays in the pre-event pack
   ([07](07-pre-event-readiness-and-reveal.md)). One line, and it clears the recovery-runner case as
   well.
3. Keep it on the troubleshooting list, demoted. The symptom — *everything works except reaching one
   local address* — is unintuitive enough that a coach who has not seen it will burn ten minutes.

### The topic inventories are participant-facing

Both stacks, on the page, not coach-only. `civ inspect` produces them anyway, so withholding is
pointless and only slows people down — and [17](17-attendee-page.md)'s rule already allows showing
real operations on real data. Coaches carry a printed copy for speed at the desk.

### Cohort under- or over-fill

Graduated here from the map's fog. **The per-beat sweep is what breaks first.** At three coaches it
is ~3–4 minutes each across 30 desks; at 40 participants it no longer fits between beats.

- **40+:** add a fourth and fifth coach, or sweep every second beat. Do not shorten the sweep — a
  glance that is too quick to see anything is worse than none.
- **10–15:** three coaches is generous, and the sweep becomes near-continuous. Nothing breaks.

[02](02-help-protocol.md)'s coach count is a **floor** precisely so this is answerable. One paragraph
in the guide, not a redesign.

### Briefing and rehearsal

- **Coaches are rehearsed at the internal mini-hackathon** (Phase 5), playing the coach role against
  solo and duo personas — not observing it. The card is used there or it is not tested.
- **A 30-minute pre-brief on 2 September**, during room setup, covering the day's specifics and the
  internet-down role. It is the only network failure left ([08](08-room-requirements.md) Update 4):
  page and submission both go, and **coaches become the distribution mechanism** for the SSD page
  export and for USB hand-in. Practise it once ([18](18-rehearsal-observations.md)).

### What this hands on

- **[07](07-pre-event-readiness-and-reveal.md)**: add *disable your VPN* to the pre-event pack.
- **[14](14-participant-materials.md)**: the topic inventories are participant-facing and belong on
  the page.
- **Owner needed:** the troubleshooting fixes, and printing the cards.
