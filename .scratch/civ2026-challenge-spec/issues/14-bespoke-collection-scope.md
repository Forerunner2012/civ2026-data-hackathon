# What do the bespoke French-city bags add, and when is their drop-dead date?

Type: grilling
Status: open

## Question

Ticket 01 made the French-city bags additive-only. This ticket makes "additive" concrete before
effort goes into them.

The rig can collect event-based situations to order: localization, signal behaviour, state
transitions, pattern matching.

What has to be settled:

- **What are they for?** Extra development bags, a second sealed test set, a demo for the
  warm-up, or seed data for a future edition? Each implies very different preparation.
- **The drop-dead date.** After which point does bespoke data stop being included at all? It
  has to sit far enough before the Phase 2 freeze that layouts, manifests and inventories can
  still absorb it.
- Do these bags share the Kashiwa topic and schema structure closely enough to reuse the same
  detector and layouts? If not, the "two inventories" cost from ticket 01 gets much larger.
- Right-hand traffic in France versus left-hand in Kashiwa: an unprotected *right* turn is a
  fundamentally different manoeuvre in the two countries. Does that break reuse of the URT
  detector, and is that a problem or a teaching opportunity?
- Do the same redistribution terms apply, or is this data cleanly CIV-owned? (Cross-check
  ticket 05.)

## Why this is on the frontier

Nothing blocks it, and the drop-dead date needs to exist *now* to be meaningful — a deadline
set after the fact is not a deadline.

## Update after tickets 05, 06 and 08

Schedule is explicitly not an argument here. Two substantive points remain, and they pull in
opposite directions:

**Against including them in the scored challenge:**

- **The handedness problem is confirmed by the publisher**, who describe URT as "equivalent to
  unprotected left turns in Europe". France is right-hand traffic, so the French bags hold the
  *mirror* manoeuvre. A URT detector written against Kashiwa will not transfer unchanged, and
  neither will the layouts. That breaks the "same detector, more bags" story.
- **Different personal-data posture.** Kashiwa is a controlled campus with staged actors and a
  participating publisher (ticket 19). French-city bags are open public roads — uninvolved
  pedestrians, real plates, real addresses — governed by whatever Heex arranges for its own rig,
  with no CC BY 4.0 umbrella. Solvable, but it is separate work with a different owner.

**For including them, and worth weighing seriously:**

- The mirrored manoeuvre is arguably the *best possible* transfer exercise. "Your detector works
  in Kashiwa — now make it work where the traffic runs the other way" is exactly the reusable-
  logic lesson §2 is trying to teach, and it is a far better use of the rig than extra bags of
  the same thing.
- It would make the bonus/advanced track genuinely about generalisation rather than about
  bolting an agent onto a working detector.

So the real question is not "in or out" but **which role**: additional dev bags (weak — handedness
breaks reuse), a sealed generalisation test (strong), or a demo asset. Decide the role first.
