# What does the sealed ground truth score against?

> Historical planning. Follow the [archive index](../../README.md) for current guides and record boundaries.

Type: grilling
Status: resolved

## Question

If teams may catch event types beyond URT, what does the hidden/sealed ground truth score
against? Label-matching needs a fixed event class; open-ended event definitions do not have one.

## Answer

**Sealed labels exist for unprotected right turns only.** The 25-point detection category is
scored against those labels, so it stays objective and comparable across teams. Other event
types are judged **qualitatively in the bonus/advanced track**.

Reasoning: it preserves the objective backbone of the 100-point score, it matches the framing
in ticket 02 that creativity belongs in *how* teams capture the event, and it bounds labelling
— the scarcest resource in this runway — to a single class.

Consequences carried forward:

- Only one class needs sealed ground truth, inter-annotator agreement and tolerance semantics.
  Ticket 16 designs that.
- The bonus track needs a rubric that a jury can apply without labels. Currently folded into
  §4.6's 20 bonus points; revisit when ticket 12 settles how agentic work scores.
