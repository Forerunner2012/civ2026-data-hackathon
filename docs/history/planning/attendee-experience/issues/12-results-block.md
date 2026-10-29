# The results block, minute by minute — and how four people present with fifteen minutes' notice

Type: grilling
Status: resolved
Blocked by: 04, 10

## Question

[Ticket 21](../../challenge-spec/issues/21-pitch-and-judging-model.md) fixed the shape of
14:30–15:00:

| When | What |
|---|---|
| 14:30–14:40 | Reveal: leaderboard, and what the scores actually showed |
| 14:40–14:55 | Walkthroughs from ~4 selected entries |
| 14:55–15:00 | Wrap on the transfer lesson |

The shape is settled. **The logistics are not, and they do not obviously work.**

## The problem nobody has solved

Walkthrough selection depends on jury scores. The jury finishes at ~14:30, which is when the block
starts. So the four selected participants get, at best, **fifteen minutes' notice** that they are
presenting to the room — and one of them is being selected for having **failed instructively**,
which is a harder thing to be told at short notice than to be told well.

Fifteen minutes of prep produces four bad three-minute talks. It also produces four anxious people
who spend the reveal not listening.

**Candidate that removes the problem entirely: do not ask them to present.** The organizer drives
the screen from the participant's *already-submitted artifacts* — the clip, the spec, the report —
and **interviews** them from their seat or from the front. Prep burden: zero. It also guarantees the
walkthrough shows the evidence rather than slides about the evidence, which is the entire point of
the event. And it lets the organizer control the arc across four entries, which four independent
presenters cannot.

Confirm or reject, and design accordingly.

## What this ticket must decide

- **Interview or presentation**, and if interview, who conducts it and how they prepare in the 30
  minutes they have.
- **When and how the four are told.** Privately, before the block, with a clear yes/no — and
  especially: **how the instructive-failure participant is asked.** Ticket 21 warns it reads as a
  booby prize unless framed. Framing it at 14:20 in a corridor is the worst possible version.
  Decide whether consent is sought and what happens if they decline.
- **Whether the picks can be made earlier.** If the jury flags candidates *as they read* rather than
  after scoring — a "worth showing" mark, independent of rank — selection can happen at 13:45 and
  everyone gets 45 minutes. That is a constraint on [10](10-jury-composition.md)'s reading protocol,
  and it is probably the single highest-value change available here.
- **What the reveal actually contains.** *What the scores showed* is the interesting part and the
  part with no owner: which signals people chose, where the field clustered, what the transfer did
  to the ranking. Someone has to prepare that between 14:00 and 14:30 from the machine scores.
  Decide who, and what the evaluator must emit to make it possible — that is a requirement on the
  build, not a slide.
- **The wrap. [04](04-extension-placement.md) has resolved and given it content:** the extension
  *lesson* — **the system took knowledge that was never in the bag, and used it to find events I
  could not otherwise have found** — closes the event at 14:55, demonstrated in three minutes with
  the Reims champagne cellars as the image people leave with. The *exercise* is self-serve on the
  page. So the open question narrows: does the wrap carry **both** that and the transfer lesson in
  five minutes, or does one of them move into the reveal?
- **Prize-giving placement**, in coordination with [11](11-prizes-and-recognition.md). Thirty
  minutes does not obviously hold a reveal, four walkthroughs, a wrap *and* an award ceremony.
- **What happens to the entries not shown** — 11 to 26 of them. Every submission was genuinely
  assessed, which was ticket 21's whole argument for this model. Decide how a participant who is
  not in the top four *sees* their own result, and when.

## Why it is blocked

[10](10-jury-composition.md) produces the scores and the picks and constrains when they exist.
[04](04-extension-placement.md) decides whether the extension message has already been delivered by
14:30, which changes what the wrap is for.

## Answer

**Interviews, not presentations. Picks by ~13:15. Awards ride on the walkthroughs. And every
participant gets written feedback, which is the thing this block could not previously offer.**

### The finding: the AI jury makes per-entry feedback free

This ticket's last open item was the one with no good answer — *what happens to the 11 to 26 entries
not shown?* [Ticket 21](../../challenge-spec/issues/21-pitch-and-judging-model.md) argued
for this whole model on the grounds that **every submission is genuinely assessed**, and then had no
way to let most participants experience that.

[10](10-jury-composition.md) solves it as a side effect. Two agents score every entry against
written anchors and produce a rationale per category. **So every participant can receive a written
assessment of their own submission** — what scored, what did not, and why — which no three-human
jury could have produced in two hours for thirty entries.

> **Everyone gets their feedback at 15:00**, delivered rather than requested. Not shown on screen —
> handed over, one document per entry.

That converts the block's weakest structural property into its strongest, and it makes ticket 21's
claim true in the participant's hands rather than only in the design.

**Two conditions**, both on [10](10-jury-composition.md): the agents must emit per-category rationale
as an output, not just a number; and a human should skim the set before release, because a
confidently wrong rationale handed to an expert is worse than no rationale.

### Interviews, confirmed

**Nobody presents.** An organizer interviews them; the artifacts are on screen rather than slides.

> **Amended after [09](09-submission-intake.md)'s update.** Submissions are now metadata-only, so
> the organizer does not hold the clips. **The four selected participants drive their own laptop**
> while being interviewed. Prep burden is still zero — it is their machine, their files, and they
> answer questions rather than presenting — and it is better than the original, since nobody has to
> hunt for someone else's evidence on an unfamiliar screen. They have an hour's notice from ~13:30,
> which is ample for "have your clip open".

- **Prep burden: zero.** Which was the entire problem.
- It guarantees the walkthrough shows **the evidence** rather than slides about the evidence.
- One person controls the arc across four entries, which four independent presenters cannot.
- The interviewer needs ~30 minutes with the artifacts, not the participant.

### Picks land at ~13:15, not 14:30

The fifteen-minutes-notice problem is solved upstream: [10](10-jury-composition.md) requires the
agents to flag *worth showing* **as they read**, independently of rank. Scoring is not the
bottleneck it was for a human jury.

So the four are known early, told **privately and individually by about 13:30**, and get an hour
rather than fifteen minutes.

**How the instructive-failure participant is asked** is the part to get right, and it is a scripted
conversation, not an improvised one:

> *We want to walk through yours because the dead end you hit is the most useful thing in the room —
> it is the one everybody else will recognise. You would be doing us a favour. Are you happy for us
> to show it?*

**Consent is sought, and no is accepted without negotiation.** If they decline, take the next
candidate — [10](10-jury-composition.md) should flag five, not four, precisely so this costs nothing.
Nobody should learn they are the failure exhibit in a corridor at 14:20.

### The reveal, and what the evaluator must emit

*What the scores showed* is the interesting half of the reveal and had no owner. It is prepared
between ~13:30 and 14:30 by the organizer, from data the machine scorer must be **built to produce**:

- distribution of Kashiwa vs Reims Detection — expected to be a near-ceiling category against a
  spread one, per [17](17-attendee-page.md);
- which signals and fields entries chose, and how many converged on the same ones;
- how much the transfer moved the ranking relative to Kashiwa alone;
- evidence volume-reduction spread.

**No build ask.** `civ score` emits per-entry results; the organizer pastes 15–30 rows into a
spreadsheet and sorts. Cross-submission aggregation as a CLI feature is a tool built once, for one
person, for thirty rows, on one afternoon. Cut it — add it if a second edition wants it.

### The shape

| | | |
|---|---|---|
| 14:30–14:38 | **Reveal** | Leaderboard, then what the scores showed. Announce that the jury was two AI agents against human anchors, with a human arbitrating — [10](10-jury-composition.md) requires it, and here is where it is said |
| 14:38–14:54 | **Four interviews, ~4 min each** | Awards are given **as each entry comes up**, not in a separate ceremony. Three of [11](11-prizes-and-recognition.md)'s five recognitions are being walked through anyway |
| 14:54–15:00 | **Wrap** | Below |

**Awards ride on the walkthroughs.** Thirty minutes cannot hold a reveal, four interviews, five
recognitions *and* a ceremony. Merging them costs nothing and makes each award land on the work
rather than on a name.

### The wrap carries the extension, and the transfer lesson moves into the reveal

[04](04-extension-placement.md) put the extension *lesson* here — *the system took knowledge that was
never in the bag, and used it to find events I could not otherwise have found* — as a three-minute
demonstration with the Reims cellars as the closing image.

Six minutes cannot carry that **and** the transfer lesson. So:

- **The transfer lesson moves into the reveal**, where it belongs anyway: *here is what the second
  dataset did to the ranking* is the transfer lesson, told with evidence rather than asserted.
- **The wrap is the extension demo**, and it ends on the horizon rather than on the scoreboard. The
  last thing anyone hears is *the pipeline you were handed is not the edge of what you can do* —
  which is also the message that sends people to the published kit
  ([ticket 20](../../challenge-spec/issues/20-cohort-skill-floor-licensing.md)'s *take it,
  not join us*).

## Update — the organizer narrates. No interviews, no presentations.

Organizer's decision, and it removes the participant from the front of the room entirely.

**Nobody is interviewed and nobody presents.** The organizer walks the room through the selected
entries — spec, report heading 3, the required figure — and the participant stays in their seat and
receives applause. [Ticket 21](../../challenge-spec/issues/21-pitch-and-judging-model.md)'s
~4 walkthroughs are preserved; only the delivery changes.

### Why this is better than the interview it replaces

The interview design existed to solve a prep-burden problem. This removes the problem rather than
managing it:

- **Zero burden and zero exposure.** Not even "have your clip open". Nobody is put on the spot in
  front of thirty peers in a second language.
- **It dissolves the consent problem** for the instructive-failure entry — mostly. Being *shown* is
  still being shown, so **tell them beforehand** rather than springing it, and keep
  [10](10-jury-composition.md)'s five-candidate flag so a decline costs nothing. But the ask drops
  from *will you stand up and explain your dead end* to *may we show this*, which is a far easier
  conversation.
- **[09](09-submission-intake.md)'s metadata-only submission is now sufficient.** The organizer needs
  the spec, the report and the figure — all submitted. No clips, no participant laptop, no
  hunting on an unfamiliar machine. The awkward dependency the previous update introduced is gone.
- The organizer keeps full control of the arc across four entries and of the clock.

**Cost:** the participant's own voice is lost, and with it the unrehearsed detail that makes a
walkthrough memorable. Mitigate by quoting their report directly — heading 3 and heading 4 are
already written in their words, which is exactly the material worth reading aloud.

**Preparation** moves entirely to the organizer: ~30 minutes with four submissions between the picks
landing at ~13:15 and the block at 14:30. That is the same window the reveal is prepared in, so it is
one person's afternoon and should be stated as such.

### What this hands on

- **[10](10-jury-composition.md)**: flag **five** worth-showing candidates, emit per-category
  rationale, and have a human skim it before release. All three are outputs, not favours.
- **Owner needed:** the interviewer, and whoever assembles thirty feedback documents between 14:00
  and 15:00. Both are small; neither is assigned.
- **Fog cleared:** *what an attendee leaves with* — the feedback document, the published kit, and
  their own submission. It stops being fog and becomes a line in
  [14](14-participant-materials.md).
