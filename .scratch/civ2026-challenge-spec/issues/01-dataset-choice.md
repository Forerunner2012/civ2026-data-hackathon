# Which dataset carries the event?

Type: grilling
Status: resolved

## Question

Which dataset is the hero for the challenge, and is bespoke French-city collection on the
critical path or additive? Available: the URT-Kashiwa ROS 2 set reused from the previous
hackathon, new data expected in the same structure (ROS 2 / PX4), and a vehicle rig in a
French city able to collect event-based situations to order.

## Answer

**URT-Kashiwa is the hero dataset. The freeze depends only on it.** French-city bespoke bags
are **additive-only**, behind a hard drop-dead date after which they ship as extra development
bags or not at all — they can never block the freeze.

Reasoning: with under three months of runway, this is the only option that neither wastes the
rig nor bets the event on collection landing in time.

Accepted cost: two datasets means two topic inventories, two sets of PlotJuggler layouts and
two manifests to review. Ticket 14 bounds that cost by fixing the drop-dead date and deciding
what the bespoke bags are actually *for*.

Open dependency: this assumes URT-Kashiwa may be redistributed to attendees — **not yet
confirmed**. See ticket 05.
