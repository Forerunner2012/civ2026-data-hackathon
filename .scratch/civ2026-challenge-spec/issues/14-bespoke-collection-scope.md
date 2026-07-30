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

The honest recommendation is now **rule this out of scope** rather than set a date.

- **The event is 35 days out** (Thu 3 Sep 2026, verified in ticket 08). Collecting, cleaning,
  manifesting, inventorying and building layouts for a second dataset inside that window, while
  evaluation and rehearsal are the acknowledged long poles, is not credible.
- **The handedness problem is confirmed by the publisher**, who describe URT as "equivalent to
  unprotected left turns in Europe". France is right-hand traffic: the French bags would contain
  the *mirror* manoeuvre. Detector and layout reuse does not hold.
- **The personal-data posture is far worse.** Ticket 05 found Kashiwa is a controlled campus with
  staged actors; French-city bags are open public roads — uninvolved pedestrians, real plates,
  real addresses, real GDPR, and none of it covered by CC BY 4.0. This is a bigger problem than
  the one ticket 19 is already trying to close in time.
- The same-programme Kashiwa collection event (7–9 Sep 2026) also lands *after* CIV 2026.

Ruling this out of scope is a scoping act and therefore the user's call, not the agent's — but
the effort is better spent as seed data for a future edition.
