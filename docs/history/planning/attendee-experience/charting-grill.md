# Charting grill — CIV 2026 attendee experience

> Historical planning. Follow the [archive index](../README.md) for current guides and record boundaries.

> **Read this first if you are Matt.** This was an **AFK night session**. You asked for one
> grilling question at a time with a recommended answer; you also said that for this session I
> should not block on you and should take my own recommendation every time. So every answer below
> is **mine, not yours**. Each one is marked `AFK — provisional`.
>
> The destination (Q1–Q4) and the scope boundaries (Q5–Q6) are the ones worth overturning before
> anyone works a ticket, because they set what every ticket is for. Everything from Q7 onward is
> *frontier mapping* — it decides which tickets exist, not what they answer, so a wrong call there
> costs a ticket, not a map.
>
> Correct anything here by editing the map and the affected tickets. Nothing below is a decision
> of record; the tickets are.

Charting session: 2026-07-30. Map: [`map.md`](../../../../.scratch/civ2026-attendee-experience/map.md). Predecessor: the CIV 2026 challenge spec
map, 25 tickets, all resolved.

---

## Round 1 — naming the destination

### Q1. What kind of thing is this map finding its way to?

Map one's destination was *a complete challenge spec, so owners can build the kit without
re-litigating anything*. It ended at the spec; building was downstream. What is the equivalent
sentence here?

| Option | What it means | Trade-off |
|---|---|---|
| **A. The attendee-experience spec** | The parallel of map one: §4.2 and §4.7 rewritten and closed, plus everything they were missing | Symmetric and familiar, but "spec" invites the map to drift into authoring the materials |
| **B. The room design** | Only the mechanisms that make 15–30 independent workstreams work: tempo, coaching, recovery | Sharp and small, but strands the jury, the prizes and the afternoon, which you explicitly listed as in scope |
| **C. Everything an attendee touches** | Including the brief, cheat sheet, warm-up walkthrough, layouts, site copy | Too wide. Content authoring is execution; this map would never close |
| **D. A rehearsable day** | The destination is a *gate*: Phase 5's internal mini-hackathon can be run without an organizer inventing anything on the day | Keeps the map honest about producing decisions, and borrows map one's proven "so that X can proceed" shape |

**Recommendation: D, phrased as a gate.** The tell is what map one did well — its destination named
a *downstream unblock* ("owners can build the kit"), not an artifact. The equivalent unblock here
is Phase 4 (*package the attendee experience*) and Phase 5 (*rehearse*). If those two phases have
no open design question, the map is done.

B is the tempting answer because the pace car is the exciting part, but you listed jury, prizes,
pre-event setup and extension placement as inherited open work, and none of those are "the room".

> **AFK — provisional. Answered D.**

---

### Q2. Does this map produce decisions only, or does it also produce the materials?

Map one had one exception to plan-don't-do (ticket 06, retrieving an artifact a decision waited on).

| Option | Trade-off |
|---|---|
| **A. Decisions only** | Clean, matches wayfinder's default and map one's precedent. Risk: "the coach guide" stays a noun nobody has written |
| **B. Decisions plus the templates that *are* the decision** | Checkpoint prompts and a report template are hard to decide without drafting the words. Risk: the map becomes a content shop |
| **C. Decisions plus a one-page spec per artifact** | Each material gets *what it must achieve, what it must contain, who owns it* — but not its prose | Slightly more work per ticket, but it is the thing Phase 4 actually needs |

**Recommendation: C.** "Ship a coach guide" is not a decision anyone can act on. "The coach guide
contains X, Y, Z; a coach may not do W; it is owned by the facilitation owner" is. Where drafting a
few example lines is the only honest way to settle a question — checkpoint prompts especially —
draft them as an **exemplar inside the ticket**, and say plainly that the full set is Phase 4 work.

This is the same move ticket 09 made: it wrote a real EventSpec to settle a question, then said the
values were placeholders.

> **AFK — provisional. Answered C.**

---

### Q3. Where exactly is the boundary against map one?

**Recommendation:** map one's 25 resolved tickets are **input, not material**. This map may *depend
on* them, may *discover a consequence of* them, and may **not** reopen them. If a ticket here
concludes that a map-one decision is wrong, it stops and says so rather than quietly overturning
it — that is a fresh effort, not a step on this route.

Two specific things stay shut regardless of what this map finds:

- the **two-dataset order** and the **12:30 deadline**;
- the **55/45/20 rubric** and the 25-point Detection total.

Map one already licensed two things to move, and this map inherits that licence: **checkpoint
minutes** (§4.2 is a rehearsal baseline) and the **15/10 Detection split** (provisional pending the
internal evaluator run — and that run is not this map's business).

> **AFK — provisional. Answered as above.**

---

### Q4. So: what is the destination sentence?

> **Every mechanism that makes 3 September work for 15–30 independent workstreams is decided —
> tempo, support, recovery, placement, materials and the afternoon — so that Phase 4 can author the
> attendee kit and Phase 5 can rehearse it with no design question left open. The map produces
> decisions and one-page specifications of the materials; it does not author them.**

Reached when: an organizer can run the internal mini-hackathon end to end, from the pre-event week
to the 15:00 wrap, without inventing anything.

> **AFK — provisional. Answered as above.**

---

## Round 2 — mapping the frontier, breadth-first

### Q5. Is "the pace car" one question or several?

You called it the one genuinely new idea. Before ticketing it, it needs decomposing, because the
brief conflates two different problems:

- **Tempo** — one-to-many, proactive, broadcast: *everyone knows where they should be.*
- **Sensing** — many-to-one: *coaches know who is quietly stuck.*

These are not the same mechanism and they do not have the same solution. A visible tempo does not
help a coach notice anybody. What it does is move the noticing to the **participant**: stuckness
becomes self-diagnosed rather than coach-diagnosed, and *that* is what scales to 30 workstreams.
Coaching then becomes demand-driven — the exception handler you predicted — but only if there is a
socially cheap way to raise a hand.

**Recommendation: two tickets.** [01 The pace car](../../../../.scratch/civ2026-attendee-experience/issues/01-pace-car.md) decides the broadcast
tempo. [02 The help protocol](../../../../.scratch/civ2026-attendee-experience/issues/02-help-protocol.md) decides how a stuck workstream surfaces
itself, how coaches triage, and what §4.7 becomes. 01 blocks 02, because what a coach is
*responding to* depends on what the room is broadcasting.

> **AFK — provisional. Answered: two tickets, 01 blocks 02.**

---

### Q6. Do the pace car's candidate forms need drafting now, or is that ticket 01's job?

**Recommendation: draft them now, decide in the ticket.** Charting is cheap; the ticket is where the
100K-token session happens. Five candidates, so 01 starts from a real field rather than a blank
page:

1. **The rabbit — a live reference run.** An organizer works the identical ladder on a projected
   screen, deliberately ~10–15 minutes ahead, narrating. Ambient: look up, see where you should be.
   Strong pedagogy — it makes the *manual analysis is tedious → `civ` is the facilitator* arc
   visible instead of asserted. Risk: it is a spoiler. Mitigation: the rabbit runs the **warm-up
   route only**, never a scored development route.
2. **The board — a standing tempo display.** Current stage, current minute, next beat, and the
   artifact you should be holding by now. Passive, cheap, no spoiler. Weak: tells you *that* you
   are behind, not what to do.
3. **The heartbeat.** A fixed beat every 15 minutes with one spoken line: *by now you should have…*
   Lowest tech. Highest interruption cost, and it punishes deep work.
4. **Telemetry.** `civ` reports milestones to a room leaderboard; the room's own progress becomes
   the tempo. This is the only candidate that also solves the **sensing** problem. Costs: build
   work in `civ`, a room LAN, and it edges against local-first (defensible — a LAN is not SaaS).
5. **The pace card.** A printed minute-by-minute card per desk. Zero infrastructure, zero room
   energy, and it is the thing people stop reading at minute 40.

**Leaning, for 01 to confirm or reject: 1 + 2 as the pace car** (rabbit for the arc, board for the
ambient reference), with 4 considered separately under 02 as the coach's radar rather than as tempo.
5 is a cheap belt-and-braces addition, not a mechanism.

> **AFK — provisional. Answered: draft five candidates into ticket 01; do not pre-decide.**

---

### Q7. Where do ticket 25's 30–45 minutes go — and does the answer break its scoring?

Ticket 25 handed this over explicitly with the duration known and the placement open. The options
are in-session, in the lunch, or a separate slot. What map one did **not** notice is that the choice
collides with ticket 21's 12:30 close.

- **In-session** competes with the scored deadline. The three-hour ladder has six stages and zero
  slack; inserting an optional 45-minute module into 180 minutes is a schedule fantasy for all but
  one or two duos. It also turns the extension into a trap for anyone chasing bonus points.
- **In the lunch** costs nothing that is at risk, and fixes a real gap: ticket 21 solved the
  *jury's* two hours and left the *participant's* two hours as dead time. But submissions closed at
  12:30, so anything built at lunch **cannot be scored** — and ticket 25 says judge it under the
  existing bonus.
- **A separate slot** is cleanest and does not exist in the published programme.

**Recommendation, for ticket 04 to confirm:** the extension module is an **organizer-led hands-on
clinic in the lunch**, and it is **unscored**. The in-session extension bonus stays available for
whoever genuinely reaches it before 12:30, but the run of show does not budget for it. This
resolves the collision honestly instead of inventing a late-submission window, and it gives the
event the thing ticket 09 always assumed existed — *the organizer demo* — with the audience already
in the room.

Flag: this is the one place where the recommendation touches a map-one decision's edge (ticket 25's
"judge it under the existing bonus"). It does not overturn it — the bonus route survives — but it
does say the taught version is not the scored version. Worth your eye.

> **AFK — provisional. Answered: ticket it as [04](../../../../.scratch/civ2026-attendee-experience/issues/04-extension-placement.md), lunch clinic
> as the leading candidate, and make the scoring collision explicit in the ticket body.**

---

### Q8. Is the warm-up one question, and does it carry more than warming up?

Ticket 14 fixed the arc: **manual analysis first, so the room feels how tedious finding events by
hand is; then `civ` is introduced as the facilitator.** So the first block is not "run the tool" —
it is "find turns by hand in PlotJuggler on a fully-labelled route".

The insight worth ticketing: at 30 independent workstreams, a synchronised opening is the only way
to know every environment actually works before anyone is alone with it. Ticket 04 accepted the
BYOD risk and noted the failure "lands in the first thirty minutes". **So make the warm-up the
environment gate.** Find the broken laptops at minute 10, not minute 90 — and that also gives
ticket 06 a concrete trigger for the fallback path instead of a vibe.

**Recommendation:** one ticket, [05](../../../../.scratch/civ2026-attendee-experience/issues/05-warm-up-and-environment-gate.md), which decides the
warm-up's shape *and* whether it doubles as the gate. It does not block on 01, because the warm-up
is where the pace car launches rather than something the pace car shapes.

> **AFK — provisional. Answered: one ticket, includes the gate question.**

---

### Q9. Can someone on the fallback pack produce a scoring submission?

This is the question ticket 04 left implicit and it is sharper than "what goes in the pack".
A participant whose container never worked cannot run `civ detect`, `civ clip` or `civ report` —
which is 30 of the 55 machine-scored points gone (Evidence 15, Reproducibility 15) before anyone
looks at their reasoning.

Ticket 17 already wrote the answer down without noticing it was one:

> **The "send only CLI calls to the organizer's machine" option** stays valuable […] a run that
> only exists as a CLI invocation someone else executes is **reproducible by construction**.

**Recommendation, for ticket 06:** the primary recovery is **"your spec, our runner"** — a shared
organizer machine on the room LAN executes `civ` invocations for anyone whose environment failed.
The pre-extracted tables and clips are the *reasoning* support while that happens, not the whole
mitigation. Buddying-up into a duo is the social fallback. This turns ticket 04's accepted risk
from "you learn but you cannot compete" into "you compete more slowly", which is a materially
different day for that person.

> **AFK — provisional. Answered: ticket [06](../../../../.scratch/civ2026-attendee-experience/issues/06-fallback-and-recovery.md), blocked by 05,
> and it must decide the scoring path, not just the pack contents.**

---

### Q10. Pre-event: is the setup session the whole question?

No — and this is where the leakage constraint bites. The pre-event pack has to make an environment
work **without teaching the challenge**, because the participant page cannot carry the scenario.
That pairs a logistics question with a design question, and they are the same question: *what does
a participant hold before the day, and what is revealed on the day?*

Note the live tension worth naming in the ticket: both datasets have to ship pre-event for offline
safety (tickets 04, 17), which means a curious participant holds the Reims bag before the transfer
is revealed. Signals-only Reims is ~350 MB, so in-room distribution is *technically* possible over
LAN — but that trades the offline guarantee for a surprise, and the surprise is weak anyway, since
the bytes do not carry the framing.

Most participants will be **travelling to Miyazaki** in the days before, which argues hard for
async-first over a live session.

**Recommendation:** one ticket, [07](../../../../.scratch/civ2026-attendee-experience/issues/07-pre-event-readiness-and-reveal.md), covering the
readiness mechanism, the readiness *token* (`civ doctor` output as the artifact), and the
hold-versus-reveal boundary.

> **AFK — provisional. Answered: one ticket, all three parts.**

---

### Q11. Is the physical room a ticket, and is it circular with the pace car?

It looks circular — the pace car needs to know what screens exist, and the room requirements depend
on the pace car's form. It is not, if ticket 01 is required to state a **minimum viable form** and a
degraded fallback. Then the room ticket collects requirements from 01, 02, 06 and 09 and states
what the venue must provide and what the design becomes if it does not.

Nobody has designed the room's physical affordances at all: screens, power for 30 laptops, a room
LAN, seating that lets coaches circulate, and where the organizer runner machine sits.

**Recommendation:** ticket [08](../../../../.scratch/civ2026-attendee-experience/issues/08-room-requirements.md), blocked by 01, 02, 06, 09.

> **AFK — provisional. Answered: yes, ticket it, blocked downstream.**

---

### Q12. Is the language of the room a question nobody has asked?

Yes, and I think it is a real gap. CIV 2026 is in **Miyazaki**; T-Lab participates; the cohort is 30
international practitioners; the dataset is Japanese and the transfer dataset is Reims. Map one
settled cohort and skill floor (ticket 20) and never touched language.

This is not cosmetic at this cohort size. It decides: the language of the brief and the cheat sheet,
whether checkpoints are called bilingually, whether coach coverage must include a Japanese speaker,
what language `report.md` may be written in — and therefore what the jury must be able to read.

**Recommendation:** ticket [15](../../../../.scratch/civ2026-attendee-experience/issues/15-language-of-the-room.md), on the frontier, unblocked. It
is small, it is cheap to settle, and it blocks the materials inventory.

> **AFK — provisional. Answered: yes, new ticket, and flag it to you as a genuine gap rather than
> an inherited one.**

---

### Q13. How does the afternoon split into tickets?

Three distinct questions, one blocking chain:

- **Jury** ([10](../../../../.scratch/civ2026-attendee-experience/issues/10-jury-composition.md)) — how many, who, whether a coach may judge someone
  they coached, and the reading protocol that gets 45 + 20 points across 15–30 reports in two
  hours. Frontier.
- **Prizes and recognition** ([11](../../../../.scratch/civ2026-attendee-experience/issues/11-prizes-and-recognition.md)) — blocked by 10.
- **The results block minute by minute** ([12](../../../../.scratch/civ2026-attendee-experience/issues/12-results-block.md)) — blocked by 10 and 04.
  The hard part is not the reveal; it is that four walkthrough participants get ~15 minutes' notice.
  Leading candidate: the organizer drives the screen from the *submitted artifacts* and interviews
  the participant, so prep burden is zero.

> **AFK — provisional. Answered: three tickets, chained.**

---

### Q14. What is left, and what stays fog?

Ticketed: [03 cadence](../../../../.scratch/civ2026-attendee-experience/issues/03-cadence.md) (blocked by 01, 04, 05), [09 submission
intake](../../../../.scratch/civ2026-attendee-experience/issues/09-submission-intake.md) (frontier), [13 coach guide and checkpoint
prompts](../../../../.scratch/civ2026-attendee-experience/issues/13-coach-guide-and-checkpoints.md) (blocked by 02, 03), [14 participant materials
inventory](../../../../.scratch/civ2026-attendee-experience/issues/14-participant-materials.md) (blocked by 03, 05, 07, 15).

Left as fog, because I cannot phrase them sharply until the frontier advances:

- **What the rehearsal must observe about the room** — Phase 5 exists, but what an attendee-
  experience rehearsal is *watching for* depends on which mechanisms 01, 02 and 06 install.
- **Cohort under- or over-fill.** If 10 show up, or 40, which mechanisms break first? Waits on 01
  and 02, since the answer is "whichever ones assume a ratio".
- **What an attendee leaves with.** Ticket 20 settled *take it, not join us*; the experience
  question — what is physically or digitally in their hands at 15:00 — waits on 12.

Ruled **out of scope**: authoring the materials, the internal evaluator run, and anything that
reopens map one.

> **AFK — provisional. Answered as above.**

---

## What I would put to you first, in the morning

1. **Q1/Q4 — the destination sentence.** Everything else hangs off it.
2. **Q7 — the extension clinic being unscored.** It is the only recommendation here that presses on
   a map-one decision's edge, and it changes what ticket 04 is allowed to conclude.
3. **Q9 — "your spec, our runner".** If you reject it, ticket 06 gets much bleaker and ticket 04's
   accepted risk gets worse, not better.
4. **Q12 — language.** New, unasked, and cheap to settle now versus expensive to discover in Phase 4.
