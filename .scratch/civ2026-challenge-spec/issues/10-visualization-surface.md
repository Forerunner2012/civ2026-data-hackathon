# Is PlotJuggler 4 enough, or is Lichtblick required?

Type: prototype
Status: open

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
