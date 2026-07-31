# Who is the jury, and how do they score 15–30 reports in two hours?

Type: grilling
Status: resolved

## Question

Map one left this in the fog, waiting on [ticket 12](../../civ2026-challenge-spec/issues/12-agent-scoring.md),
which has since closed. [Ticket 21](../../civ2026-challenge-spec/issues/21-pitch-and-judging-model.md)
built the whole judging model on a jury it never sized:

> 12:30–14:30 — Jury splits the written reports between them and awards the judgement-based points.

## The arithmetic, first

**45 points** from `report.md` across three categories, plus **up to 20 bonus**, for **15–30
entries**, in **120 minutes** — during which the jury also eats.

At 3 jurors splitting the pile, that is 5–10 reports each, so 12–24 minutes per report. That is
comfortable for reading one page and brutal for reading one page *and* the evidence view *and* an
agent trace, which the Visualization (15) and bonus (10) categories both require. The categories are
not all one-page-readable, and this ticket has to reconcile that.

If reports are **split** rather than all read by all, then no single juror sees the whole field —
which means the rubric must be **absolute**, not comparative, and calibrated in advance, or the
ranking is an artifact of who read whom.

## What this ticket must decide

- **How many jurors, and who.** Named roles, not headcount: someone who knows the data, someone who
  knows the domain, someone who represents the audience the event is for.
- **Split or shared reading?** Split is the only thing that fits the clock. If split, decide the
  calibration ritual: candidate is **all jurors independently score the same two reports first**,
  compare, agree anchors, then split the rest. Costs 20 minutes of the 120 and buys a ranking that
  survives scrutiny.
- **Can a coach judge?** [02](02-help-protocol.md) has resolved and **guaranteed the input**:
  coaches log who they spent significant time with — a name and a rough duration. That is the part
  that cannot be reconstructed afterwards. The routing is this ticket's: with split reading across
  three jurors and 15–30 reports, steering around a handful of conflicts is easy, so decide whether
  it is separate populations, per-entry recusal, or a stated overlap. Note the constraint is real —
  the organizers who built the kit are the only people qualified to judge it *and* to coach it.
- **How the categories that are not one page get scored.** Visualization and explanation (15) is
  *jury reads the evidence and claims* — that is a clip and a layout, not prose. The agent bonus
  (10) is a trace. Decide what the jury actually opens, and how long that adds per entry.
- **The interaction with [04](04-extension-placement.md).** If the extension clinic lands at
  13:00–13:45, it consumes organizers inside the jury's only window. If jurors and clinic-runners
  are the same people, one of the two decisions has to give.
- **What the jury produces.** Scores alone, or scores plus the material [12](12-results-block.md)
  needs: the four walkthrough picks including the most instructive failure, and the two or three
  observations that make the reveal worth listening to.
- **Rubric anchors.** [Ticket 21](../../civ2026-challenge-spec/issues/21-pitch-and-judging-model.md)
  fixed the five report headings so each maps to one category. Decide whether each category needs
  written anchors (what a 5, a 10, a 15 looks like) — recommendation: yes, and drafting one worked
  example per category is inside this ticket's scope, since split reading is unsafe without them.

## Why this is on the frontier

Nothing blocks it — [ticket 12](../../civ2026-challenge-spec/issues/12-agent-scoring.md) was the
dependency and it closed. It blocks [11](11-prizes-and-recognition.md) and
[12](12-results-block.md).

## Answer

**A mixed jury: one organizer, two AI agents with defined roles (Codex and Claude), and — subject to
confirmation — one T-Lab project owner. The deterministic evaluator handles the 55 machine points
separately and is not part of the jury.**

Composition set by the organizer. What follows is what it implies, because it changes this ticket's
shape rather than just filling in a headcount.

### The finding: this is not a throughput hack, it is a verification upgrade

The arithmetic problem — 45 points plus 20 bonus, across 15–30 entries, in 120 minutes — dissolves.
But solving throughput is the least interesting thing about this composition.

A three-human jury reading one page each in 12–24 minutes could only ever score **the report**. It
could never open `events.jsonl`, check that the failure described in heading 4 corresponds to a real
detection, confirm that the clip in `evidence/` shows what the report claims, or follow an agent
trace back to the tool call that produced it — which is precisely what
[ticket 12](../../civ2026-challenge-spec/issues/12-agent-scoring.md) says the bonus requires.

**Agent jurors can read the report against the submission.** So the rule for this jury is:

> **Every judgement-based score is anchored to an artifact in the submission, not to the prose that
> describes it.**

That is a stricter standard than a human jury could have applied, and it is exactly the standard
§3.4 and [ticket 12](../../civ2026-challenge-spec/issues/12-agent-scoring.md) ask of *participants*.

### The failure mode to design against

**An LLM scoring a written document rewards good writing.** That is the whole risk, and it is the
same error [ticket 12](../../civ2026-challenge-spec/issues/12-agent-scoring.md) already banned in
the other direction — *never prompt style*. The analogue here is *never prose style*.

[15](15-language-of-the-room.md) sharpens it: with a **C1 lower bar**, fluency varies across the
cohort for reasons that have nothing to do with engineering quality. A jury that rewards fluency
scores the wrong thing and does so invisibly.

Mitigations, all mandatory:

- **Point the agents at the submission directory, not at `report.md` alone.** The report is the
  index; the artifacts are the evidence.
- **Anchors are written by a human** and are verifiable rather than impressionistic: *does heading 3
  name a specific thing that did not transfer? does heading 4's failure correspond to an interval in
  `events.jsonl`?* This mirrors
  [ticket 15](../../civ2026-challenge-spec/issues/15-ai-build-review-gates.md)'s rule that a human
  writes the Tier A assertions.
- **Explicitly instruct against rewarding fluency, length or confidence.**

### The ensemble, and what disagreement is for

Two agents is not redundancy — it is the determinism mechanism. LLM scoring is not reproducible, so
do not pretend otherwise:

1. **Codex and Claude score every entry independently**, from the same anchors, without seeing each
   other's output.
2. **Agreement within a threshold → the score stands.**
3. **Disagreement beyond it → the human organizer arbitrates**, and that is where their two hours go.

This inverts the human's job from *reading everything shallowly* to *reading the contested cases
properly*, which is a much better use of the only person in the room who understands both stacks.
Divergence between two different models on the same anchors is also a useful signal in itself: it
usually means the anchor is ambiguous, which is worth knowing before the reveal.

### The conflict of interest largely dissolves

[02](02-help-protocol.md) required coaches to log who they spent significant time with, so this
ticket could route around conflicts. **The agents coached nobody**, so the bulk of the scoring is
conflict-free by construction.

What remains: the human organizer arbitrates contested entries and may have coached some of them.
The log from [02](02-help-protocol.md) still earns its place — for arbitration, declare it, and where
a conflicted entry is contested, prefer the T-Lab owner as arbiter if they are confirmed.

### Roles

| | Scores | Reads |
|---|---|---|
| **Codex agent** | all entries, independently | the full submission directory |
| **Claude agent** | all entries, independently | the full submission directory |
| **Organizer** | contested entries only; owns the anchors | whatever arbitration needs |
| **T-Lab project owner** *(TBC)* | domain sanity on Investigation and Quality; preferred arbiter for conflicted entries | a sample, plus contested cases |
| **`civ score`** | **not a juror.** The 55 machine points, unattended, deterministic | — |

**The T-Lab owner is unconfirmed** and the design must not depend on them. If they come, they arbitrate
conflicts and lend domain credibility; if not, nothing structural breaks.

### Tell the participants, and show the traces

**Non-negotiable for legitimacy:** the brief states that judgement-based scoring is performed by AI
agents against human-written anchors, with a human arbitrating disagreement. Discovering this
afterwards would poison an otherwise excellent result.

And then go further, because the opportunity is unusually good: **publish the jury agents' traces
alongside the scores.** [Ticket 12](../../civ2026-challenge-spec/issues/12-agent-scoring.md) asks
participants for *a trace that points to executed tools and the evidence they produced*. A jury that
holds itself to the same standard it is grading against is the strongest possible statement of what
this event believes, and it costs nothing but the decision to do it. [12](12-results-block.md)
should consider whether that belongs in the reveal.

### What the jury must produce for the afternoon

Beyond scores, [12](12-results-block.md) needs material and it needs it **before 14:30**:

- **The four walkthrough picks**, including the most instructive failure. Agents can flag *worth
  showing* as they read, independent of rank — which means picks can exist by ~13:15 rather than
  14:30, and that was [12](12-results-block.md)'s hardest logistical problem.
- **Two or three observations** for the reveal: where the field clustered, what the transfer did to
  the ranking, which signals people chose.

Agent scoring makes both cheap. Require them as outputs, not as a favour.

### What this hands on

- **[11](11-prizes-and-recognition.md)**: an award like *best transfer* is now adjudicable, because
  every entry is read by both agents — no split-reading blind spot.
- **[12](12-results-block.md)**: picks available early; the fifteen-minutes-notice problem is
  solvable.
- **Owner needed:** somebody writes the anchors and the agent briefs, and that is real work with a
  Phase 4 lead time. It should be rehearsed against the deliberate-detector submissions from
  [ticket 16](../../civ2026-challenge-spec/issues/16-evaluator-calibration.md) — those are known-bad
  and known-good entries, which is exactly what you need to check a rubric prompt before trusting it.
