# Is PlotJuggler 4 enough, or is Lichtblick required?

Type: prototype
Status: resolved

## Question

`HACKATHON-HANDOFF.md` §8: PlotJuggler 4 only, or PlotJuggler 4 plus Lichtblick for robotic
context? §6 sets the rule as "Lichtblick only where images, transforms, point clouds, or
synchronized replay add required evidence".

URT sharpens this. An unprotected right turn is about **spatial relationships** — ego heading
against oncoming traffic — which is exactly the case where time-series plots may not be enough
to judge whether a detection is correct. If a team cannot *see* the turn, the 15-point
"Visualization and explanation" category becomes hard to earn and coaches cannot adjudicate
false positives.

## Why this is a prototype ticket

Open one Kashiwa URT event in PlotJuggler 4 alone and try to answer "is this really an
unprotected right turn?" from the signals. If yes, PlotJuggler-only holds. If you reach for
camera or transform context, Lichtblick earns its place — and its setup cost lands on the
container image from ticket 04.

Produce and link: a PlotJuggler layout for URT, plus a note on what was not decidable from it.

## Why this is on the frontier

Nothing blocks it. Decide before the container image is frozen — adding a second viewer after
the freeze is expensive.

## Answer

**PlotJuggler 4 is the required primary surface. Lichtblick ships in the image but is optional.**

Ticket 18 changed the calculus: with labels as right-turn *intervals*, a detection can be judged
from yaw rate and speed alone. Nothing on the required path needs 3D or camera context, so
Lichtblick cannot be a dependency for completing the challenge — which keeps the floor low and
the golden path single.

But **Evidence and extraction (15) plus Visualization and explanation (15) is 30 of 100 points**,
and ticket 19 cleared the camera topic. A team that can *show* the turn — ego view plus the
detected object — makes a materially better case in the results slot than one showing three
plotted scalars. Shipping Lichtblick and requiring nothing costs image size and buys that.

Evidence from ticket 06: the previous event's layouts were Foxglove-family, using 3D, Image,
Plot, RawMessages and StateTransitions panels. Whoever built them reached for visual context.

### Consequences

- Organizers prepare **PlotJuggler 4 layouts as the supported artifact** — topic inventory,
  yaw rate, speed, object flag on one synchronized timebase. This is what the warm-up teaches.
- A Lichtblick layout is provided **unsupported**, as a convenience for teams building their
  pitch.
- **Contingent on ticket 17 keeping a camera stream in the distributed subset.** If camera is
  dropped for size, drop Lichtblick with it — a 3D viewer over scalars only is dead weight.
