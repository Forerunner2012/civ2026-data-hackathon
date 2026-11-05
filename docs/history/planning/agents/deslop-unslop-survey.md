# Deslop and unslop survey

> Historical planning. Follow the [archive index](../README.md) for current guides and record boundaries.

Researched on 2026-10-05. The upstream links point to `main`, so their contents can change. This note records findings and recommendations. It does not set repository rules.

## Upstream scope

[Deslop](https://github.com/cursor/plugins/blob/main/cursor-team-kit/skills/deslop/SKILL.md) cleans code introduced by a branch, using the diff against `main`. It targets unnecessary comments, unusual defensive checks on trusted paths, `any` casts that bypass type errors, excessive nesting, and inconsistent style. It requires focused edits and unchanged behavior unless fixing a clear bug. It requests a short final summary.

[Unslop](https://github.com/cursor/plugins/blob/main/pstack/skills/unslop/SKILL.md) edits prose while preserving meaning and tone. It targets vague sourcing, inflated vocabulary, repetitive framing, decorative formatting, filler, jargon, dense sentences, and compressed fragments. It favors concrete facts, plain words, active voice, and complete sentences. The numbered rules have stable identifiers.

Its description says "Must always apply", and its frontmatter sets `disable-model-invocation: true`. That metadata describes the upstream skill. It does not make the skill a rule in this repository. Some rules ban particular punctuation and words.

Related plugin documentation: the [Cursor team kit README](https://github.com/cursor/plugins/blob/main/cursor-team-kit/README.md) lists deslop as a skill; the [pstack README](https://github.com/cursor/plugins/blob/main/pstack/README.md) describes poteto-mode routing to unslop.

## Existing repository conventions

- [Code review](https://github.com/mattpocock/skills/blob/main/skills/engineering/code-review/SKILL.md) reviews standards and specification compliance separately. Its code-smell checks require judgment, defer to repository standards, and skip checks enforced by tools. Deslop also addresses style consistency and unnecessary code. Code review reports findings, while deslop edits the code.
- [Retro](https://github.com/mattpocock/skills/blob/main/skills/engineering/retro/SKILL.md) assigns mechanical rules to deterministic checks and judgment calls to `CODING_STANDARDS.md`. No `CODING_STANDARDS.md` or `CONTRIBUTING.md` was found in the survey.
- [Writing for agents](https://github.com/mattpocock/skills/blob/main/skills/productivity/writing-for-agents/SKILL.md) addresses document structure, useful pointers, and pruning. Unslop complements its prose guidance.
- [AGENTS.md](../../../../AGENTS.md) points to tracker, triage, and [domain rules](../../../agents/domain.md). Domain rules require [glossary vocabulary](../../../../GLOSSARY.md) and relevant ADRs. The [tracker](../../../agents/issue-tracker.md) and [triage mapping](../../../agents/triage-labels.md) define issue workflows.

## Recommended placement

If adopted, put deslop's code checks in review standards and unslop's prose checklist in a document under `docs/agents/`. Keep AGENTS.md pointers brief.

Preserve technical terms, quotations, code punctuation, and contractual meaning when adapting unslop. Before cleanup, specify which diff to review and how to validate the edits. Writing preferences alone do not need a glossary term or ADR.
