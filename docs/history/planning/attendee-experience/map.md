# Map: CIV 2026 attendee experience

> Historical planning. Follow the [archive index](../README.md) for current guides and record boundaries.

Label: `wayfinder:map`

## Destination

**Every mechanism that makes 3 September work for 15–30 independent workstreams is decided —
tempo, support, recovery, placement, materials and the afternoon — so Phase 4 can author the
attendee kit and Phase 5 can rehearse it with no design question left open.**

Reached when an organizer can run the internal mini-hackathon end to end, from the pre-event week
to the 15:00 wrap, without inventing anything on the day. The map produces **decisions** and
**one-page specifications of the materials**; it does not author them.

> **Status: 17 of 18 resolved. The fog is empty.**
>
> **One ticket remains: [16](issues/16-decoy-event-class.md)** — the only item on this map that
> cannot be resolved from this repository. It needs one twenty-minute check against the Kashiwa
> warm-up route on a machine that holds the bags, and its risky half has already been designed away:
> the over-count it demonstrates is guaranteed by *sampling*, not by the data. What genuinely needs
> eyes is finding one honest false positive to narrate.
>
> [18](issues/18-rehearsal-observations.md) is the map's **exit condition** — six things a Phase 5
> rehearsal must observe. When it can run against those without inventing anything, the destination
> is reached.
>
> Most of this map was worked **AFK** and self-answered against recommendations. The exceptions,
> which are Matt's: [01](issues/01-pace-car.md)'s two updates, and the composition in
> [10](issues/10-jury-composition.md) and [15](issues/15-language-of-the-room.md). See
> [`charting-grill.md`](charting-grill.md) for what was decided on his behalf during charting and
> which calls are worth overturning first.

## Notes

- **Domain:** the lived experience of a three-hour ROS 2 data-investigation hackathon — the room,
  the tempo, the support, the afternoon. The challenge itself is settled elsewhere.
- **Map one is input, not material.** The [CIV 2026 challenge spec map](../challenge-spec/map.md)
  and its 25 resolved tickets are the decision authority. A ticket here may depend on them and may
  discover consequences of them; it may **not** reopen them. If a ticket concludes a map-one
  decision is wrong, it says so and stops — that is a fresh effort, not a step on this route.
- **Shut regardless of what this map finds:** the two-dataset order, the 12:30 submission deadline,
  and the 55 / 45 / 20 rubric with its 25-point Detection total.
- **Licensed to move, inherited from map one:** checkpoint minutes (§4.2 is a rehearsal baseline,
  not a minute plan) and the 15/10 Detection split (provisional pending the internal evaluator run
  — which is not this map's business).
- **Skills to consult:** `/grilling` by default; `/prototype` for the pace car and any ticket whose
  answer is a shape rather than a choice; `/domain-modeling` where a term needs pinning.
- **Plan, don't do.** Where drafting words is the only honest way to settle a question — checkpoint
  prompts especially — draft an **exemplar inside the ticket** and say plainly that the full set is
  Phase 4 work.
- **Do not reintroduce schedule pressure.** Programme times are design inputs, not a countdown.
  Decide what the day *should* be.
- **Vocabulary.** Never System, Datasource, Signal, Trigger, Recording. Always bag, topic, field,
  EventSpec, detector, event, clip, manifest. ([ticket 07](../challenge-spec/issues/07-clean-room-boundary.md))
- **The scenario must not appear on the participant page.** `handoff-site` has a leakage test
  suite; if you touch the site, `npm test` must pass. ([ticket 22](../../../../.scratch/civ2026-challenge-spec/issues/22-public-site-organizer-gate.md))
- **`D:\Bags`, `D:\heex`, `C:\Program Files\MCAP`** in map-one tickets 17 and 24 are *provenance
  from another machine*, not dependencies. This map needs no bag data.
- As decisions close, update **§4.2 and §4.7** of `HACKATHON-HANDOFF.md` so the handoff and the map
  agree. Both sections currently describe a room that does not exist.

## Say it in plain words

Map one's coinages are opaque to a reader who was not in the room, including native and non-native
speakers alike. Its own tickets keep their wording — they are a decision record — but **everything
written from here on, and everything a coach or participant reads, uses the plain term.**

| Instead of | Say | Which means |
|---|---|---|
| sealed labels | **the answer key** | The list of time ranges the organizers write by hand: *route 7, a turn crossing oncoming traffic, 03:14.2 → 03:19.8* |
| sealed set / sealed routes | **the held-back routes** | Recordings participants never receive, and never see answers for. Scoring runs against these |
| development set | **the practice routes** | Recordings participants do get, with the answer key for 2–3 events only |
| unsealed labels | **the worked examples** | Those 2–3 published answers. They show where a turn starts and ends; they are not a training set |

If a term needs a paragraph to explain, it is the wrong term.

## Where this map hands over

This map ends at decisions. **The build is handed over through
`/to-spec` then
`/to-tickets`, not through a third map** — the route
`/ask-matt` calls the main flow, where these two maps are steps 1–2.

The reasoning, so nobody re-opens it: the build has almost no fog. Map one froze every contract it
needs — EventSpec's shape, the CLI surface, output schemas, evaluator semantics, licence posture — so
what remains is execution, and wayfinder tickets resolve decisions rather than slicing a build. A
third map would produce a project plan wearing a wayfinder costume.

**Spec the Phase 1 vertical slice first**, not the whole kit: `inspect → detect → clip → score →
report` on one Kashiwa bag then one Reims chunk, offline. It is already the shape `/to-tickets`
wants, it de-risks everything downstream, and specifying the rest afterwards means doing it with real
knowledge. The four requirements the organizer named — *does `civ` run on both stacks, does the page
advance on schedule, does the form accept a submission, can 15–30 entries be scored inside the lunch
window* — become archived requirements there rather than notes scattered across these tickets.

**Only one thing would justify a third map:** the vertical slice going badly. Then *what do we cut*
becomes real fog — drop the Reims dataset, drop `derive`, one dataset and a deeper report — and
those questions cannot be phrased sharply until the size of the slip is known.

## The fixed frame

Design inputs, all settled upstream. Listed once so no ticket re-derives them.

| | |
|---|---|
| When | Thu 3 Sep 2026, Miyazaki. Session **09:30–12:30**. Results **14:30–15:00**. Two-hour lunch between. |
| Who | **30 participants, solo or in duos** — 15–30 independent workstreams, all experienced with robotic/vehicular data. |
| What | Kashiwa (right turns) as warm-up, then Reims (**left** turns) as the scored transfer. The event is *the turn that crosses oncoming traffic*. |
| How | `civ` CLI, container-first BYOD, CPU-only, no recovery laptops, no model shipped. |
| Ladder | Rung 1 (CEL + `timing` + `evidence`) is the pass mark; rung 2 (`derive`) is the reach; rung 3 is the deferred extension. |
| Scoring | 55 machine at 12:30 / 45 jury from a capped one-page report over lunch / 20 bonus. |
| Data | Signals-only, ~350 MB; images an optional context pack. |

## Decisions so far

<!-- one line per closed ticket: gist, then zoom the link -->

- [The pace car](issues/01-pace-car.md) — **tempo is primary; coaching becomes the exception
  handler**, because the binding constraint is budget awareness, not skill or blockage, and that
  failure is invisible from outside. The mechanism is **a short opening briefing plus one
  progressive attendee page** — nothing else is live, and nobody drives anything during the session.
  The page shows what was expected at each stage, then hints, tips and finally solutions, on a
  timetable that runs itself and that a coach may nudge. **Solutions are handed over only after the
  hackathon** — during the session the ladder stops at hints and tips, and the pace car and coaches
  guide *towards* an answer without giving one. Live teaching is
  rejected outright — it penalises deep work, since the people most likely to miss it are the ones
  head-down doing what the event wants. Telemetry rejected *as tempo*: descriptive where tempo must
  be prescriptive. **Handedness is the one thing nothing ever solves.** Page design is
  [17](issues/17-attendee-page.md).
- [The help protocol](issues/02-help-protocol.md) — **a two-sided card on the laptop, one sweep per
  beat, **2–3 coaches** (the derived floor was 3–4; reality is 2–3, so sweeps go every other
  beat), and coaches never hand over solutions.** A coach who wants to give more help
  **advances the schedule for everyone** rather than rescuing one person quietly, so help is never
  private and never improvised. (The original justification — *the page will hand over the solution
  instead* — no longer holds now that solutions publish after the event, so around the 11:00 cliff
  coaching is the escalation of last resort again: **guide towards an answer, never hand one over.**)
  The card needs no network — when the network *is* the problem, raising a hand must not require it —
  and its two sides route to
  recovery or to coaching before a coach arrives. Telemetry rejected again, this time as *sensing*:
  the page is already a floor, so a per-beat sweep catches the rest. Coaches log who they helped, so
  [10](issues/10-jury-composition.md) can route conflicts. **Coaches do not rescue people from the
  designed friction** — warm-up tedium is the lesson. §4.7 rewritten in full.
- [Extension placement](issues/04-extension-placement.md) — **split the lesson from the exercise.**
  The lesson — *the system took knowledge that was never in the bag* — is three minutes and closes
  the event at 14:55, in front of everyone. The exercise is a **page section, unlocked in-session as
  an optional branch and scored** under the existing bonus; it stays on the page afterwards for
  everyone else. The organizer-led clinic is dropped: it was a coin flip on attendance and competed
  with the jury's only reading window. **Available and scored, but not budgeted for** — the run of
  show allocates it no time, and the brief says so, or it becomes a trap.
- [The warm-up and environment gate](issues/05-warm-up-and-environment-gate.md) — **the manual block
  is analogue (pen on a printed trace), the gate runs underneath it, and the real output is
  disagreement.** Two practitioners mark the same window differently, and that sets up intervals,
  tolerance, temporal IoU and sealed labels in one move — tedium is only the excuse. Paper means a
  broken laptop costs time but not the lesson, so the two frictions stop competing. The gate is
  `civ doctor && civ inspect <warm-up>`, signalled by **inverting the help card**: everyone starts
  with it up and puts it down on success, so recovery starts at minute 10 without anyone announcing
  anything.
- [Minute-level cadence](issues/03-cadence.md) — **seven beats after a choreographed opening, and
  the report is written in three instalments instead of at the end.** The transfer cliff at 11:00 is
  carried by three things, none of which is an answer: the permission stated plainly, the **transfer
  hints pulled forward to that beat**, and a coach. (An earlier version unlocked the Kashiwa solution
  there; that was reversed, which also **withdraws the near-ceiling prior** handed to the evaluator run.) Headings 1–2 land at 10:40, 3–4 at 11:45 while the transfer is fresh, 5 at 12:10 — a
  30-minute report budget instead of 15, and Submit becomes *finish and check* rather than *write*.
- [Recovery](issues/06-fallback-and-recovery.md) — **pair up.** A runner on an organizer box was
  designed and then **cut**: pairing covers a broken container and inadequate hardware identically,
  ranks solo and duo together anyway, and costs nothing to build. It produces a *complete* entry, not
  a degraded one. The fallback pack on the SSDs supports reasoning meanwhile. Cutting the runner also
  removed the room LAN, the organizer box, the cold standby and the corporate-VPN failure mode —
  nothing lives at a local address any more. Add a runner only if Phase 5 shows pairing does not
  hold.
- [Pre-event readiness and the reveal](issues/07-pre-event-readiness-and-reveal.md) — **async-first,
  drop-ins at ~10 days out**, because the week before is the week everyone is travelling. The
  readiness token is the same command pair as the in-session gate, so the gate becomes a re-check.
  **The whole task is known at 09:30** — a visible tempo requires a visible shape, so the transfer
  cannot be held back. Exploring the data beforehand is explicitly encouraged. **The embargoed thing
  is the scenario, not the paperwork** — the brief, rubric and run of show all ship early, and the
  leakage test is what enforces the line rather than a table. **Naming trap:** *URT*-Kashiwa expands
  to the scenario, so material says "the Kashiwa recordings", never the acronym.
- [Submission intake](issues/09-submission-intake.md) — **LAN endpoint on the organizer box, USB as
  the stated fallback, and unlimited resubmission.** Resubmission is not a nicety: two of
  [03](issues/03-cadence.md)'s beats are lies without it, and early submissions flatten the day's one
  thundering herd. Intake validates **structure only** and returns a hash-and-timestamp receipt,
  which also becomes [11](issues/11-prizes-and-recognition.md)'s tie-break. Hard 12:30 cutoff.
  **Superseded in large part:** submissions are now **metadata only — the spec, `events.jsonl`, an
  extended run manifest and the report, but no clips** — sent through a simple form. Everything hard
  about this ticket was a consequence of moving gigabytes, and kilobytes dissolve all of it. The run
  manifest carries what the clips used to prove; **clip validity weakens to self-attested**, offset
  by the spec being re-runnable on demand. Visualization moves to **one required figure in the
  report**.
- [Room requirements](issues/08-room-requirements.md) — **the venue is not the risk; the box is.**
  Successive resolutions shrank the venue ask to power, tables and one optional screen. Everything
  load-bearing is *brought*, and after four updates that list is short: **four 2 TB SSDs and
  consumables.** The venue is confirmed (desks, chairs, a screen showing the page and time-to-next-
  unlock); the residual risk moved to participants' own laptops, where **pairing is the mitigation**.
  No LAN, no organizer box, no cold standby, nothing to fail over. **Venue internet is the one
  dependency neither brought nor controlled** — and it degrades to things already in the room, since
  the SSDs carry the page export, the fallback pack, the data and the image.
- [Language of the room](issues/15-language-of-the-room.md) — **professional English throughout, C1
  lower bar**, on the precedent of CIV 2025. Monolingual materials, no translation workstream, no
  language constraint on coach staffing, and `report.md` in English. Say it in the pre-event pack.
  One consequence carried into [10](issues/10-jury-composition.md): a C1 floor means fluency varies
  for reasons unrelated to engineering quality, so anchors must never reward it.
- [Jury composition](issues/10-jury-composition.md) — **one organizer, two AI agents (Codex and
  Claude) with defined roles, plus a T-Lab project owner if confirmed.** `civ score` is not a juror.
  **This is a verification upgrade, not a throughput hack:** a human jury could only ever score the
  *report*, while agents can read the report **against the submission** — so every judgement-based
  score anchors to an artifact, which is the standard the event already asks of participants. The
  risk is that an LLM rewards good writing, so anchors are human-written and verifiable and the
  agents are pointed at the directory, not the prose. **Two agents is the determinism mechanism**:
  they score independently and disagreement routes to the human, inverting their job from reading
  everything shallowly to reading contested cases properly. Coaching conflicts largely dissolve —
  the agents coached nobody. Participants must be told, and the jury's own traces should be
  published alongside the scores.
- [The attendee page](issues/17-attendee-page.md) — **prose plus a deliberately holed YAML skeleton,
  served from the organizer box, advancing automatically.** The line between reconstructable and
  copy-pasteable sits **at the numbers**: topics and fields are given (lookup work), thresholds and
  the comparison **direction** are not (judgement). **The finding: releasing the Kashiwa solution
  arms the transfer test rather than undermining it** — a participant derives the sign from their own
  plot and carries a *signed* threshold into a country where traffic runs the other way, which is
  exactly what [ticket 18](../../../../.scratch/civ2026-challenge-spec/issues/18-urt-operational-definition.md)
  designed. **The format is the enforcement**: if the YAML is complete, the rule has been broken, and
  that is visible at a glance. Text not video, because a participant at 11:20 is skimming. Escalation
  differs in kind — hint says *where to look*, tip says *a technique or hazard*, solution says *the
  approach*. Advance-only: holding was dropped as solving no problem. Expect **Kashiwa Detection to
  become a near-ceiling category** — intended, and handed to the evaluator run as a prior.
  **Updates:** video is allowed back for the genuinely visual — a clip playing, a viewer interaction
  — as the exception, not the default; the rule for hints is **show a real command on the real
  dataset, with an example that is deliberately not the expected answer**; and the page is served
  over **Tailscale Funnel** rather than the room LAN, which kills the corporate-VPN failure mode and
  needs no client software or venue firewall change. The trade is that the dependency **moves from
  something the organizers control to something they do not** — venue internet plus a third party —
  so the static USB export is promoted to primary backup and Funnel is enabled only on the morning,
  since Funnel certificates appear in public transparency logs.
- [Prizes and recognition](issues/11-prizes-and-recognition.md) — **top three, plus *best transfer*
  and *most instructive failure*. **No prize: podium, applause and a public
  mention**, with anything further decided in the week of the event. Publication of entries was
  considered and dropped, which also removes a consent question from the brief. The failure award **is** the framing ticket 21 warned was
  needed. Both named awards are only adjudicable because [10](issues/10-jury-composition.md)'s agents
  read every entry. Ties break on earliest submission, using [09](issues/09-submission-intake.md)'s
  receipt.
- [The results block](issues/12-results-block.md) — **the organizer narrates; nobody presents or is
  interviewed; picks by ~13:15; awards ride on the walkthroughs.** The participant stays seated and
  gets applause — which costs the unrehearsed detail but removes all exposure, and makes
  metadata-only submissions sufficient, since spec, report and figure are all the organizer needs. The finding: **the AI jury makes per-entry feedback free**, so
  *every* participant receives a written assessment at 15:00 — which answers the question this block
  never could, and makes ticket 21's "every submission is genuinely assessed" true in the
  participant's hands. The transfer lesson moves into the reveal (told with evidence); **the wrap is
  the extension demo**, so the last thing anyone hears is *the pipeline you were handed is not the
  edge of what you can do*. Consent is sought for the failure walkthrough, and five candidates are
  flagged so a no costs nothing.
- [Coach guide and checkpoints](issues/13-coach-guide-and-checkpoints.md) — **the prompts were
  already written by [03](issues/03-cadence.md); what remained fits on one card.** Both sides drafted.
  The vocabulary ban is printed on it, because a coach reaching for a familiar word at speed is the
  one place no test suite can catch the clean-room breach — and so is *leave them*, the instruction
  that contradicts a coach's instinct hardest. Troubleshooting top ten fixed, surfacing a gap nobody
  had: **a corporate VPN reaches the internet but not the room LAN** — which cost page, intake and
  runner for one person while everything looked fine to everyone else. Since largely solved by moving
  the page and submission onto the public internet; it now costs only the recovery runner, and the
  gate's third clause survives as a general reachability check.
- [Participant materials](issues/14-participant-materials.md) — **three things on the desk;
  everything else is on the page.** The paper problem solved itself once
  [17](issues/17-attendee-page.md) absorbed the inventory: printed trace, help card, brief — the
  things that must survive the page being unreachable or be written on. **No cheat sheet, no pace
  card** — a sheet that duplicates a screen is what people hunt for at minute 95. Layouts ship
  pre-loaded; the submission skeleton is a `civ` command. The brief carries eight rules that exist
  nowhere else a participant would look, including that the jury is AI and that winners are published.
- [What the rehearsal must observe](issues/18-rehearsal-observations.md) — **Arnaud is the test.**
  Matt runs it alone wearing both caps; Arnaud plays attendee only, with the page and pace car and
  nothing else — the one person who did not design any of this. The question is *where does he stall,
  and what does he reach for*, which is worth more than a checklist run by its own author. Two people
  can test the mechanics and the cliff; they **cannot** test cards, pairing or sweeps, and that half
  stays unknown until the day. Six observations with stated failure signals back it up, because
  **every mechanism here degrades invisibly.** A pace car nobody
  reads still looks like a pace car; a help card nobody raises looks like a room with no problems. So
  **name a dedicated observer** — a rehearsal where everyone participates produces no observations.
  Three deliberate breakages: a broken container, **the network pulled mid-session** — internet and
  LAN separately, since they now have very different blast radii — and the organizer
  box killed. And one clarification of Phase 5's gate: advancing the page schedule is the sanctioned
  control, not a workaround; *answering a question the page should have answered* is the workaround,
  and each instance is a missing unit to write before the day.

## Not yet specified

Fog — in scope, not yet sharp enough to ticket. Graduates as the frontier advances.

*Empty. All three patches have graduated:* **what a rehearsal must observe** → ticket
[18](issues/18-rehearsal-observations.md); **cohort under- or over-fill** →
[13](issues/13-coach-guide-and-checkpoints.md); **what an attendee leaves with** → answered by
[12](issues/12-results-block.md) and [14](issues/14-participant-materials.md) (the published kit,
their own submission, and their feedback document).

## Out of scope

Ruled beyond this map's destination. Does not graduate; would need a fresh effort.

- **Authoring the materials.** This map specifies what each artifact must achieve, contain and be
  owned by. Writing the coach guide, the cheat sheet, the warm-up walkthrough and the layouts is
  Phase 4 execution.
- **The internal evaluator run** and the 15/10 Detection tuning that hangs off it. A scoring
  validation, not an experience decision.
- **Reopening map one.** Its 25 tickets are the decision authority; disagreement is a fresh effort.
