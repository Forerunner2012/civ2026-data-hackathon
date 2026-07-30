# How does agentic work score?

Type: grilling
Status: resolved
Blocked by: 11

## Question

`HACKATHON-HANDOFF.md` §8: agent as an unscored demonstration, agent bonus worth up to 10
points, or a separate advanced prize?

§4.6 currently assumes the 10-point bonus. §2 frames AI as "an enabler, not a trend", and §3.5
rules out grading prompt style.

What has to be settled:

- If it scores, what evidence does a team submit — a tool trace? What makes a trace *good*?
- How is that judged consistently by a jury under time pressure, without drifting into
  rewarding prompt style?
- Does a scored agent track advantage teams who arrive with existing agent tooling?
- §4.6's rule that "bonus cannot compensate for an irreproducible core" — does it survive
  contact with a team that produces a brilliant agent trace and a broken run?
- If it becomes a separate prize, who judges it and when, given the Transfer block is already
  tight (see ticket 08)?

## Why it is blocked

Ticket 11 decides what teams can actually run on a CPU-only BYOD container. Scoring a capability
the environment cannot deliver would be a design error.

## Answer

**Agent bonus, up to 10 points**, as §4.6 already assumes. Not an unscored demo, not a separate
prize.

- A separate prize needs its own judging and its own ceremony, and the results slot is 30 minutes
  (ticket 08). It would also elevate agentic work above the evidence contract the event is
  actually about.
- An unscored demo makes it decorative, which contradicts §2's framing of AI as a genuine
  enabler.

**What earns the points:** a trace that points to *executed tools and the evidence they
produced*. Not prompt quality, not transcript length, not eloquence — §3.5 rules out grading
prompt style, and the jury should be able to follow a claim back to a tool call and an artifact.
§4.6's rule stands unchanged: bonus cannot compensate for a core that does not reproduce.

### Said plainly, because it is a real consequence

With ticket 09 deferring Python to the extra track and this ticket shipping no model, **the agent
track is thin for 2026**. Attendees bring their own tooling to a declarative, deterministic core.
That is consistent with "AI as enabler, not headline" — but it means the AI story of this edition
is carried mostly by **how the kit was built** (ticket 15) rather than by what attendees do
during the session. Worth being honest about in the framing rather than overselling an agent
track that has little room to operate.
