# Where is the clean-room boundary against the Heex pipelines?

Type: grilling
Status: open
Blocked by: 06

## Question

`HACKATHON-HANDOFF.md` §8: strict legal clean-room process, or independent functional
reimplementation with provenance review?

`exploration/exploration-notes-INBOX.md` states the intent as "clean room engineering of the
Heex data pipelines with more simplification". §3.3 sets the principle: *replace observable
workflow capabilities, not protected code, names, UI, or historical thresholds.*

What has to be settled:

- Which is being replaced — observable behaviour, or something closer to the implementation?
- Who on the team has seen Heex internals, and does that contaminate them as an author?
- Does a strict two-team clean room (spec writers who have seen it, implementers who have not)
  fit in this runway at all, or is provenance review the only realistic option?
- What provenance evidence gets recorded per component, and who reviews it?
- Names and thresholds: is `cive`/`civ` sufficiently distinct, and are any carried-over
  numeric thresholds traceable to Heex rather than independently derived?
- Does anything here need legal sign-off before the kit is published as OSS?

## Why it is blocked

Ticket 06 has to establish what the prior solution actually contains before a boundary can be
drawn around it.
