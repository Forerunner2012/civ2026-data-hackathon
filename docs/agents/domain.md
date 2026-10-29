# Domain docs

Read this repo's glossary and relevant decisions before exploring code or naming domain concepts.

## Before exploring, read these

- Read `GLOSSARY.md` at the repo root. If `GLOSSARY-MAP.md` exists, follow it to the glossaries relevant to your task.
- Read relevant ADRs in `docs/adr/`. In repos with multiple contexts, also check `src/<context>/docs/adr/` for decisions specific to each context.

If these files are missing, continue without reporting their absence or proposing new files. The `/domain-modeling` skill creates them when a term or decision is resolved. `/grill-with-docs` and `/improve-codebase-architecture` use that skill.

## File structure

This repo has one context and uses the root glossary and ADR directory.

```
/
├── GLOSSARY.md
├── docs/adr/
│   ├── 0001-event-sourced-orders.md
│   └── 0002-postgres-for-write-model.md
└── src/
```

Repos with multiple contexts use a root `GLOSSARY-MAP.md`.

```
/
├── GLOSSARY-MAP.md
├── docs/adr/                          ← system-wide decisions
└── src/
    ├── ordering/
    │   ├── GLOSSARY.md
    │   └── docs/adr/                  ← context-specific decisions
    └── billing/
        ├── GLOSSARY.md
        └── docs/adr/
```

## Use the glossary's vocabulary

Use the terms defined in `GLOSSARY.md` for issue titles, refactor proposals, hypotheses, and test names. Respect each term's `_Avoid_` list.

If a concept is missing, check whether an existing term fits. If the glossary needs a new term, note it for `/domain-modeling`.

Keep glossary entries to one or two sentences defining project-specific domain terms, with `_Avoid_` synonyms where useful. Keep implementation details in specs or ADRs.

## Record decisions sparingly

Create an ADR only when a decision is hard to reverse, surprising without context, and the result of a real trade-off.

Use sequential filenames such as `0001-slug.md` and `0002-slug.md`. Increment the highest existing number. Record the context, decision, and reason in one to three sentences. Add sections only when they help explain the decision.

## Flag ADR conflicts

If your proposal contradicts an ADR, name the conflict and explain why you recommend revisiting the decision. For example:

> This proposal contradicts ADR-0007 on event-sourced orders. Explain here why the decision needs review.
