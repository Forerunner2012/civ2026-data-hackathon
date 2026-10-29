# What is awarded, to whom, and what does that reward?

Type: grilling
Status: resolved
Blocked by: 10

## Question

Map one left prize structure in the fog. Nothing anywhere says what a winner gets, how many winners
there are, or what the event is signalling by choosing them.

Prizes are not decoration at this cohort. **What gets a prize is what the room understands the event
to have been about** — and this event has a deliberate, slightly unusual set of values that the
default "top 3 on the leaderboard" would flatten.

## The values the awards should carry

Named in map one, and worth restating because the award structure either reinforces them or
contradicts them:

- **Failure is a deliverable.** §2 says so; [ticket 21](../../challenge-spec/issues/21-pitch-and-judging-model.md)
  puts the *most instructive failure* in the results block and warns that it will read as a booby
  prize unless framed. An award solves the framing problem in a way that a walkthrough slot does not.
- **Transfer is the difficulty.** [Ticket 14](../../../../../.scratch/civ2026-challenge-spec/issues/14-bespoke-collection-scope.md)
  moved the event's whole point onto the second dataset. A single overall leaderboard buries that
  under 100 points of everything else.
- **Solo and duo rank together** ([ticket 21](../../challenge-spec/issues/21-pitch-and-judging-model.md)).
  Any award structure that quietly re-splits them reopens a closed decision.

## What this ticket must decide

- **How many overall places**, and whether the leaderboard alone determines them.
- **Named awards beyond the leaderboard.** Candidates, to accept or reject: *best transfer* (what the
  event is actually testing), *most instructive failure* (makes §2's claim real), *best evidence*
  (the thing the whole toolchain exists for). Each named award is a message; each one also dilutes
  the leaderboard. Decide how many the room can hold in a 30-minute results block.
- **What is physically awarded.** Money, hardware, conference kudos, or nothing material.
  30 practitioners at an academic-industrial conference are not primarily there for a prize, and an
  award that is obviously token is better than one that is awkwardly small. Budget is an input this
  ticket needs and does not have — get it or state the assumption.
- **Is anything awarded for the extension track?** [Ticket 25](../../challenge-spec/issues/25-geofence-agent-track.md)
  judges it qualitatively under the bonus, and [04](04-extension-placement.md) may move it out of
  the scored session entirely. If it becomes an unscored lunch clinic, an award for it is
  incoherent — decide whether that costs it too much and whether recognition replaces it.
- **Ties.** With machine scoring to the point and a small field, ties are likely. Decide the
  tie-break before the reveal, not during it. Candidate: earlier submission time, which also gives
  [09](09-submission-intake.md)'s receipt a second purpose.
- **Who announces**, and whether prize-giving is inside the 30-minute results block or after it.

## Why it is blocked

[10](10-jury-composition.md) decides who scores what and produces the walkthrough picks. An award
structure that the jury cannot actually adjudicate — *best transfer* requires someone to have read
heading 3 across the whole field, which split reading may prevent — is a structure that fails at
14:25.

## Answer

**Top three overall, plus two named awards — *best transfer* and *most instructive failure*. The
substantive prize is publication, not an object.**

### The finding: the best prize available is free, durable and on-brand

[Ticket 20](../../challenge-spec/issues/20-cohort-skill-floor-licensing.md) already decided
that the workshop content and the site go **public, CC BY 4.0**. So the event can offer something
that costs nothing, lasts, and is worth more to this cohort than an object:

> **Winning entries are published on the public site** — the spec, the evidence, the report, with
> attribution — as worked examples for whoever finds the kit later.

Thirty practitioners at an academic-industrial conference are not primarily there for a prize, and a
token object is either forgettable or awkwardly small. A published, attributed piece of work is
citable, shareable and genuinely useful to the recipient. It also improves the kit: the public
material gains real submissions instead of only organizer examples.

**Budget assumption, stated because this ticket does not have the figure:** assume no meaningful
prize budget. If one appears, it should buy something small and physical *on top of* publication,
never instead of it. Get the number if it exists; do not block on it.

### The awards

| | What it rewards | Why it exists |
|---|---|---|
| **1st, 2nd, 3rd overall** | the leaderboard, all 100 points plus bonus | Ordinary and expected; the field would feel unfinished without it |
| **Best transfer** | report heading 3 and Reims Detection | [Ticket 14](../../../../../.scratch/civ2026-challenge-spec/issues/14-bespoke-collection-scope.md) moved the event's whole point onto the second dataset. A single overall leaderboard buries it under 100 points of everything else |
| **Most instructive failure** | an honest dead end, well analysed | §2 makes failure a deliverable. [Ticket 21](../../challenge-spec/issues/21-pitch-and-judging-model.md) warns it reads as a booby prize unless framed — **an award is the framing.** A walkthrough slot alone is not |

**Five recognitions, no more.** A 30-minute results block cannot hold more, and each additional
named award dilutes the ones that carry a message.

**Nothing for the extension track.** [04](04-extension-placement.md) made the taught version unscored
and self-serve; an award for it would be incoherent. If someone genuinely builds it in-session before
12:30 it scores under the existing bonus and can surface in the leaderboard — that is enough.

### Both named awards are adjudicable, which they would not have been

[10](10-jury-composition.md) matters here. Under a split-reading human jury, *best transfer* would
have been unawardable — no single juror would have read heading 3 across the whole field. **Both
agents read every entry**, so a field-wide comparative award is now sound rather than an educated
guess. Worth stating, because it is the reason these two awards are safe to promise in the brief.

### Ties

**Earliest submission of the tied score wins**, using [09](09-submission-intake.md)'s receipt
timestamps.

Decided *before* the reveal, not during it. It also gives the receipt a second purpose and quietly
rewards the behaviour [03](03-cadence.md) spends the day encouraging — submit early, improve after.

### Solo and duo

**One leaderboard, unchanged.** [Ticket 21](../../challenge-spec/issues/21-pitch-and-judging-model.md)
settled it and no award here re-splits them. Say so in the brief so nobody feels ambushed.

### Announcement

Inside the results block, and **[12](12-results-block.md) owns the placement** — thirty minutes must
hold a reveal, four walkthroughs, five recognitions and a wrap. The likely shape is that awards ride
*on* the walkthroughs rather than forming a separate ceremony, since three of the five are probably
being walked through anyway.

## Update — no prize. Podium, applause, and a public mention.

Organizer's decision, and it **replaces publication-as-the-prize** above.

> **Nothing material is awarded.** A podium, the room's applause, and a **public mention**. Anything
> beyond that is decided in the week of the event, not now.

### What changes

- **Publication of winning entries is dropped as a commitment.** A *mention* names someone; it does
  not put their spec, evidence and report on the public site. That is a materially lighter thing and
  it removes a consent question the brief would otherwise have had to carry —
  [14](14-participant-materials.md)'s brief loses that bullet.
- **The budget question closes.** There is no budget to chase, so the assumption stated above becomes
  a decision. Nothing hangs on a figure arriving.
- **Deliberately unfinished.** The specifics wait for the week of the event. Recorded here so nobody
  re-derives it, and so Phase 4 does not print anything that promises more.

### What survives unchanged

Top three on the leaderboard, plus **best transfer** and **most instructive failure** — five
recognitions, no more. The reasoning holds independently of what is handed over: the failure award is
still the *framing* that stops
[ticket 21](../../challenge-spec/issues/21-pitch-and-judging-model.md)'s instructive-failure
slot reading as a booby prize, and both named awards are still adjudicable only because
[10](10-jury-composition.md)'s agents read every entry.

Ties still break on earliest submission. Solo and duo still rank together.

### Worth saying out loud at the podium

With nothing material at stake, the recognition *is* the reward, so the words carry all of it. In
particular the failure award needs its sentence prepared rather than improvised — this is the one
place where a throwaway line turns an intended honour into a consolation.

### What this hands on

- **[12](12-results-block.md)**: five recognitions to place, and a strong hint that they merge with
  the walkthroughs rather than following them.
- **[14](14-participant-materials.md)**: the brief must state the awards, the tie-break, the one
  leaderboard, and — importantly — **that winning entries are published**, since that is a consent
  question and not a surprise to spring afterwards.
