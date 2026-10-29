# Domain docs

This repo has one domain context. Before exploring code or naming domain concepts, read the root `GLOSSARY.md` and relevant decisions in `docs/adr/`. If a decision directory or file is absent, continue without creating it.

## Use the glossary's vocabulary

Use glossary terms for issue titles, refactor proposals, hypotheses, and test names. Respect each term's `_Avoid_` list. Check existing terms before proposing one through `/domain-modeling`.

Keep entries to one or two sentences defining project-specific terms. Put implementation details in specs or ADRs.

## Record decisions sparingly

Create an ADR only for a decision that is hard to reverse, surprising without context, and the result of a real trade-off. Use the next sequential filename, such as `0001-slug.md`. Record the context, decision, and reason in one to three sentences. Add sections only when they help explain the decision.

If a proposal contradicts an ADR, name the conflict and explain why you recommend revisiting it.
