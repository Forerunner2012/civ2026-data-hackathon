# How does agentic work score?

Type: grilling
Status: open
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
