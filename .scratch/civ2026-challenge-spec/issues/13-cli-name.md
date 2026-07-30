# Is the CLI `cive` or `civ`?

Type: grilling
Status: resolved

## Question

`HACKATHON-HANDOFF.md` §8: `cive` or `civ` as the command name. §6 currently writes every
example as `cive`.

Small, but it is wired through the quickstart, the cheat sheet, every layout and doc example,
the container entrypoint and the submission `reproduce.ps1|sh`. Cheap now, tedious after the
Phase 2 freeze.

Worth checking before deciding:

- Does either name collide with an existing binary on a standard Ubuntu or WSL image?
- Is either name a package already taken on PyPI, if the kit is ever published?
- Ticket 07 (clean-room) may have an opinion: the name must not read as a Heex product name.

Recommendation to react to: keep `cive` — every existing example already uses it, `civ` reads
like an abbreviation of the conference rather than a tool, and the collision risk is lower.

## Why this is on the frontier

Nothing blocks it, and it is the cheapest close on the board. Take it when a session has
capacity left over.

## Answer

**`civ`.**

Overrides the recommendation recorded above, which favoured `cive` on the grounds that existing
examples used it. Existing examples are cheap to change now and expensive after the Phase 2
freeze, which was the actual argument this ticket raised.

Every occurrence must be updated together: §6's command block, the participant-facing toolkit
list on the handoff site, the quickstart and cheat sheet, the container entrypoint, and the
submission `reproduce.ps1|sh` template.

Clear of the ticket 07 boundary: `civ` carries no product terminology.
