# Which participant-facing artifacts must exist, what must each achieve, and who owns it?

Type: grilling
Status: resolved
Blocked by: 03, 05, 07, 15

## Question

Phase 4 of `HACKATHON-HANDOFF.md` lists the attendee kit as a shopping list:

> prepare Kashiwa and Reims layouts, warm-up, brief, cheat sheet, submission template and fixed
> one-page report template

A list of nouns is not something an owner can build. This ticket turns it into an inventory where
each entry states **what it must achieve**, **what it must contain**, **when it is handed over**,
and **who owns it** — the specification, not the prose. Writing them is Phase 4.

> **[01](01-pace-car.md) changed this ticket's centre of gravity.** [The attendee
> page](17-attendee-page.md) is now the central participant artifact — it carries the timetable,
> what was expected at each stage, hints, tips and solutions. Most of the inventory below should
> probably live *on it* rather than on paper, and this ticket's real question becomes **what is left
> that is not the page, and why**.

## The inventory to complete

| Artifact | The open question |
|---|---|
| **The brief** | §4.3 has a paragraph. Does it survive contact with a room of 30 practitioners at 09:30, and what else is handed over with it — rubric, deadline, report template, the *what the runner executes* line from [ticket 09](../../challenge-spec/issues/09-detector-authoring-surface.md)? |
| **The cheat sheet** | One page a participant keeps open all day. What is on it: the CLI surface, the EventSpec skeleton, or the two topic inventories? It cannot be all three |
| **The report template** | Five fixed headings, one page, hard cap. Is the cap words, characters or a rendered page — and is it enforced at intake ([09](09-submission-intake.md)) or trusted? |
| **Viewer layouts** | Two, sharing no topics. What must each show on open, and does the participant get them pre-loaded or build their own? |
| **The submission template** | A skeleton directory, or a `civ` command that scaffolds one? |
| **The warm-up material** | Whatever shape [05](05-warm-up-and-environment-gate.md) chose — handout, script, or projected walkthrough |
| **Pre-event pack** | Fixed by [07](07-pre-event-readiness-and-reveal.md): what ships early and how it is named without carrying the scenario |
| **Pace card**, if [01](01-pace-car.md) kept one | Contents at desk resolution |

## Constraints every entry inherits

- **The leakage rule.** [Ticket 22](../../../../../.scratch/civ2026-challenge-spec/issues/22-public-site-organizer-gate.md)
  keeps the scenario off the participant site and `handoff-site` enforces it by test. Each artifact
  must be marked **public-early**, **public-on-the-day**, or **organizer-only**, and anything touching
  the site must keep `npm test` green.
- **The vocabulary ban** ([ticket 07](../../challenge-spec/issues/07-clean-room-boundary.md)):
  never System, Datasource, Signal, Trigger, Recording. Always bag, topic, field, EventSpec,
  detector, event, clip, manifest.
- **Language** ([15](15-language-of-the-room.md)) — which artifacts are bilingual and which are not.
- **Everything is public and CC BY 4.0** ([ticket 20](../../challenge-spec/issues/20-cohort-skill-floor-licensing.md)),
  so these are also the artifacts a stranger downloads six months later with no room around them.
  Decide which ones must stand alone and which may assume the day.

## The question behind the inventory

**How much paper can one person hold while doing a three-hour investigation?** A brief, a cheat
sheet, a pace card, a report template, two topic inventories and two layouts is already too much,
and the fastest way to lose someone is to make them search for the right sheet at minute 95. Decide
the **hierarchy**: what is always in front of them, what is one reach away, and what is on the site.

## Why it is blocked

The inventory is downstream of shape. [05](05-warm-up-and-environment-gate.md) decides what warm-up
material is, [03](03-cadence.md) decides what the pace card says, [07](07-pre-event-readiness-and-reveal.md)
decides what ships early, and [15](15-language-of-the-room.md) decides what language each is in.

## Answer

**Three things on the desk. Everything else is on the page. The hierarchy is the deliverable.**

### The finding: the paper problem solved itself

This ticket's real question was *how much paper can one person hold while doing a three-hour
investigation?* — and the honest answer when it was written was "less than we were about to give
them".

[17](17-attendee-page.md) resolved it without meaning to. A progressive page that carries the
timetable, expectations, hints, tips, solutions and both topic inventories absorbs almost the entire
inventory. **What is left on paper is what must survive the page being unreachable, or must be
written on.**

That is the hierarchy, and it is short.

### On the desk — three items, always

| | Why paper | Owner |
|---|---|---|
| **The printed signal trace** | [05](05-warm-up-and-environment-gate.md)'s analogue block is deliberately laptop-free. You mark it with a pen | unassigned |
| **The help card**, two sides | [02](02-help-protocol.md). Must work with no network and no screen. Doubles as the gate token — starts up, goes down when `civ doctor && civ inspect` passes | unassigned |
| **The brief**, one page | Read at 09:30, referred to all day, and the one thing that must be legible if the LAN is gone | unassigned |

**No cheat sheet and no pace card.** Both were in the original list; both are now duplicates of the
page, and a sheet that duplicates a screen is the thing people search for at minute 95 and cannot
find.

### On the page — everything else

Timetable and beats · what was expected per stage · hints, tips, solutions · **both topic
inventories** (participant-facing, per [13](13-coach-guide-and-checkpoints.md), since `civ inspect`
produces them anyway) · the report template · the submission structure · the extension section from
12:30.

**Plus the static export**, carried on [07](07-pre-event-readiness-and-reveal.md)'s SSDs. It is the
**internet-down** path — since [17](17-attendee-page.md) put the page on Tailscale Funnel, that is
the failure that costs it — *and* the artifact that ships publicly afterwards under
[ticket 20](../../challenge-spec/issues/20-cohort-skill-floor-licensing.md)'s CC BY.

### What the brief must contain

§4.3's paragraph is not enough. It is the only artifact that carries the day's rules, and several of
them were decided across this map and exist nowhere else a participant would look:

1. The scenario and the two datasets.
2. The rubric, and that **solo and duo rank on one leaderboard**.
3. **12:30 is hard, and you may resubmit as often as you like** ([09](09-submission-intake.md)) —
   this changes behaviour more than anything else on the page and must not be buried.
4. **The page will tell you what was expected, and waiting for a hint is legitimate**
   ([05](05-warm-up-and-environment-gate.md) says it aloud; the brief makes it durable).
5. **Judgement-based scoring is done by AI agents against human-written anchors, with a human
   arbitrating** ([10](10-jury-composition.md)). Non-negotiable for legitimacy.
6. **Awards, the tie-break, and that winning entries are published** — a consent question
   ([11](11-prizes-and-recognition.md)), not a surprise to spring afterwards.
7. The line from [ticket 09](../../challenge-spec/issues/09-detector-authoring-surface.md):
   the constraint is **what the runner executes for the scored submission**, not what you may write.
8. Everyone gets written feedback at 15:00 ([12](12-results-block.md)).

### The rest of the inventory, settled

- **Report template** — five fixed headings. Cap is **one rendered page**. **It now requires one
  figure** — a plot or a still with the interval marked — because
  [09](09-submission-intake.md)'s metadata-only submission means the jury has no clip to read and
  Visualization is 15 points. Choosing the one frame that makes the case is arguably a better test
  than shipping raw evidence. Validation happens in `civ` before submission, not at intake.
- **Submission template** — a `civ` command that scaffolds the directory, not a zip to copy. Removes
  a class of structural failures at intake.
- **Viewer layouts** — two, **pre-loaded**. Building a layout is not the exercise and burns minutes
  that belong to the transfer. Each opens showing the signals that stack's detector needs.
- **Warm-up material** — the printed trace above, plus the comparison sheet the neighbour exercise is
  captured on.
- **Pre-event pack** — fixed by [07](07-pre-event-readiness-and-reveal.md). Add
  [13](13-coach-guide-and-checkpoints.md)'s finding: **"disable your VPN for the session"**, because a
  corporate VPN reaches the internet but not the room LAN — which now only costs the recovery
  runner, but is unintuitive enough to be worth one line.

### Classification, and the naming rule

| | Artifacts |
|---|---|
| **public-early** | Pre-event pack, quickstart, image, data, `civ` |
| **public-on-the-day** | Brief, the page and everything on it, layouts, templates |
| **organizer-only** | Coach card, troubleshooting tree, jury anchors, sealed labels |

Every public-early artifact inherits [07](07-pre-event-readiness-and-reveal.md)'s naming rule: **"the
Kashiwa recordings", never the acronym**, because *URT* expands to the scenario and
[ticket 22](../../../../../.scratch/civ2026-challenge-spec/issues/22-public-site-organizer-gate.md)'s suite tests the
built bundle. All artifacts are **English only** ([15](15-language-of-the-room.md)) and inherit the
vocabulary ban ([ticket 07](../../challenge-spec/issues/07-clean-room-boundary.md)).

### Standing alone after the event

Everything goes public CC BY. **The page must read as a self-contained tutorial to a stranger six
months later** — which it nearly does already, since it was designed to be referrable rather than
attended. The brief will read as an event document, and that is fine; it should not be rewritten to
pretend otherwise.

### What this hands on

- **Owner needed on every row.** This is the Phase 4 authoring list, and it is now short enough to
  assign in one sitting.
- **Fog cleared:** *what an attendee leaves with* — the published kit, their own submission, and
  their feedback document from [12](12-results-block.md).
