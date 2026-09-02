# Where is the clean-room boundary against the Heex pipelines?

Type: grilling
Status: resolved
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

## Answer

**Independent functional reimplementation with provenance review**, and the boundary is drawn
around the **Heex stack and its terminology** — not around the domain logic.

### What is inside the line (must not be reused)

- **Terminology.** Never *System*, *Datasource*, *Signal*, *Trigger*, *Recording*. The kit speaks
  the OSS vocabulary instead: **bag, topic, field, EventSpec, detector, event, clip, manifest,
  run**. This is the substantive part of the rule — the risk is not that the kit computes
  something similar, it is that the kit reads as a re-skin of the product.
- The product's entity/architecture model, its CLI verbs and API shapes, its session and replay
  mechanics, its scripts, and its UI.

### What is outside the line (reusable as-is or as inspiration)

- **Condition expressions and their thresholds.** These describe the physics of this vehicle in
  this dataset — `angular.z <= -0.5` for a right turn, `linear.x <= -3.0` for heavy braking,
  `is_object_detected == true` for presence. Reusing them is reusing knowledge about the data,
  not the product. Ticket 06 has the full set restored.
- ROS topic paths, message types and field paths. Standard Autoware/`tier4_*`/`pix_*` schemas.
- The workflow shape — inspect, sample, author, detect, clip, score, report — which is the
  observable capability §3.3 explicitly permits replacing.

### Provenance review

Per component, record one line: what it functionally provides, and what the author consulted.
That is proportionate for an OSS teaching kit. A strict two-team clean room — spec writers who
have seen the product, implementers who have not — buys nothing here, because the reusable part
is domain knowledge and the excluded part is a naming and architecture discipline that a reviewer
can check by reading.

### Concrete check before the freeze

Grep the kit, the docs and the site for the excluded vocabulary. Zero hits is the gate. The CLI
name `civ` (ticket 13) is already clear of it.
