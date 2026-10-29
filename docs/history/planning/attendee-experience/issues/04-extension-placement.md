# Where do the extension module's 30–45 minutes come from?

Type: grilling
Status: resolved

## Question

Handed over explicitly by [ticket 25](../../challenge-spec/issues/25-geofence-agent-track.md),
which closed with:

> **Where do the 30-45 minutes come from?** […] This module has to be placed deliberately — inside
> the three hours, in the two-hour lunch, or as a separate optional session — and that is a
> run-of-show question, not a spec question. Carry it into the attendee-experience map as a
> placement decision with a known duration.

**What is settled and not reopened here:** the module is zone monitoring by GNSS in Reims — acquire
a cave list by any means, plug it in through the `resources:` seam and `min_distance_to`, run it,
look at the clips. A worked example spec ships. 40 m seed radius, CSV seed contract, judged
qualitatively. ~10–15 min acquiring zones, ~10 min writing the spec, ~10 min running and reacting.

**Open here:** when it happens, and what that placement does to its scoring.

## The collision map one did not notice

Ticket 25 says *judge it under the existing bonus*. [Ticket 21](../../challenge-spec/issues/21-pitch-and-judging-model.md)
closes submissions at **12:30** and machine-scores unattended. **Anything built after 12:30 cannot
enter the submission.** So placement and scoring are one decision, not two.

## The options

| | Placement | For | Against |
|---|---|---|---|
| **A** | Inside 09:30–12:30, optional branch after the Reims detector works | Stays scorable under the existing bonus, no new mechanism | The ladder has six stages and no slack. A 45-minute optional module inside 180 minutes is a schedule fantasy for all but one or two duos — and it becomes a **trap** for anyone chasing bonus who then misses 12:30. Also forces [03](03-cadence.md) to plan for two populations |
| **B** | In the two-hour lunch, organizer-led hands-on clinic | Costs nothing that is at risk; fixes a real gap — ticket 21 solved the *jury's* two hours and left the *participant's* as dead time; and it finally gives ticket 09 the **organizer demo** it always assumed existed, with the audience already in the room | Unscored, because submissions are closed. Asking people to work through lunch at a conference; attendance is uncertain; some will leave the venue |
| **C** | A separate slot in the conference week | Cleanest | Does not exist in the published programme, and creating one is not this map's gift |
| **D** | Pre-event, self-serve | Zero session cost | Leaks the `resources:` seam and half the toolchain before the day, and a self-serve tutorial is exactly the thing nobody does |
| **E** | B, plus a late `extension/` addendum window (say 14:00) | Keeps it scorable | Invents a second deadline, splits the submission, and the jury is mid-read. Ugly |

### Leading candidate from charting

**B, explicitly unscored** — and say so up front. The in-session extension bonus stays available for
whoever genuinely reaches it before 12:30, but the run of show does not budget for it. A candidate
shape: 12:30–13:00 real lunch, 13:00–13:45 clinic, 13:45–14:30 free, 14:30 results.

This resolves the collision honestly instead of inventing a late window, and it separates the two
things ticket 25 was carrying at once: a **bonus category** for people who extend the system unaided,
and a **teaching module** that everyone should get. They do not have to be the same event.

## What this ticket must decide

- The placement, and therefore whether the module is scored, unscored, or both-by-different-routes.
- If B: is it truly optional, how is attendance encouraged without coercion, and what happens to the
  people who skip it — does the 13:45–14:30 gap become dead time for them instead?
- Who runs it, and are they the same people the jury needs reading reports at that hour? The jury
  has **two hours to read 15–30 reports** ([ticket 21](../../challenge-spec/issues/21-pitch-and-judging-model.md));
  a clinic in the middle of that window competes for the same organizers. This is a real resourcing
  clash and [10](10-jury-composition.md) inherits it.
- Whether an unscored clinic still needs the worked example spec shipped in the kit, or whether it
  is handed out live.
- The framing sentence. Ticket 25's lesson is *the system took knowledge that was never in the bag*.
  If that lands at 13:45 with half the room absent, it is not the closing message — so
  [12](12-results-block.md) may need to carry it instead.

## Why this is on the frontier

Nothing blocks it, and [03](03-cadence.md) and [12](12-results-block.md) both wait on it: one plans
the three hours, the other plans the afternoon, and this decides which of them owns the module.

## Answer

**Split the lesson from the exercise. The lesson closes the event at 14:55; the exercise is a page
section unlocked at 12:30 that anyone can do at lunch, at home, or never.**

Option B was the leading candidate when this ticket was written. [01](01-pace-car.md) has since
resolved twice and made the organizer-led clinic inconsistent with the rest of the design — so the
answer keeps B's placement and drops its delivery.

### Why the clinic died

[01](01-pace-car.md) removed all live teaching. Its reason — *live teaching is missable, and the
people most likely to miss it are the ones doing what the event wants* — applies only partly at
lunch, where nobody is head-down against a deadline. But the other half applies fully: at a
conference, people leave the room, take calls, eat with someone. A 13:00 clinic is a coin flip on
attendance, and it puts the event's most memorable idea behind a door half the room will not walk
through.

It also created a resourcing clash: the jury has **two hours to read 15–30 reports**
([ticket 21](../../challenge-spec/issues/21-pitch-and-judging-model.md)), and a structured
clinic in the middle of that window competes for the same organizers.

### The split

**The lesson is three minutes and everyone gets it.**
[Ticket 25](../../challenge-spec/issues/25-geofence-agent-track.md) states it plainly: *the
system took knowledge that was never in the bag, and used it to find events I could not otherwise
have found.* That is a demonstration, not an exercise, and its strongest possible placement is the
**wrap at 14:55** — the last thing anyone hears, in front of the whole room, with the champagne
cellars as the image they leave with. [12](12-results-block.md) owns it and now has its closing
message.

**The exercise is 30–45 minutes and is genuinely optional.** It becomes a section of
[the attendee page](17-attendee-page.md), unlocked at 12:30 alongside the day's remaining solutions.
Self-serve, referrable, no staffing, consistent with everything [01](01-pace-car.md) decided — and
doable at lunch, on the plane, or six months later, which is exactly the right shape for something
[ticket 20](../../challenge-spec/issues/20-cohort-skill-floor-licensing.md) frames as *take
it, not join us*.

**Coaches are simply around** for the first 45 minutes of lunch, for anyone who wants to try it. No
structured session, no attendance expectation, no room booking, no clash with the jury. Roughly zero
cost, and it captures whatever energy exists without depending on it.

### Scoring: the split it forces, stated plainly

- **In-session extension work still scores** under the existing bonus, for whoever genuinely reaches
  it before 12:30. Unchanged from
  [ticket 25](../../challenge-spec/issues/25-geofence-agent-track.md).
- **The page version is unscored.** Submissions are closed; no late window is invented.
- **The run of show does not budget for the in-session route.** The ladder has six stages and no
  slack; pretending there is a 45-minute hole inside 180 minutes makes the extension a trap for
  anyone chasing bonus who then misses 12:30.

Say this in the brief. The failure mode is someone discovering at 12:20 that they gambled.

### What ships regardless

Unchanged from [ticket 25](../../challenge-spec/issues/25-geofence-agent-track.md), and now
needed for the page rather than for a clinic: the **worked example spec**, the CSV seed contract,
the 40 m radius, the bounded cave set. *Swap the resource and adjust the radius* — nobody has 45
minutes to discover `resources:` unaided, and that is more true self-serve than it was live.

## Update — the extension scores. It is not unscored.

Organizer's decision, and it **corrects the framing above**: the extension carries **additional
points under the existing 20-point bonus**, as
[ticket 25](../../challenge-spec/issues/25-geofence-agent-track.md) always intended. Calling
the taught version "unscored" was my invention and it is withdrawn.

**What changes:** the extension section unlocks on [the attendee page](17-attendee-page.md) **during
the session** — as an optional branch, not a post-12:30 release — so whoever reaches it before the
deadline can include it in their submission and be scored on it.

**What stays:** the run of show still does not *budget* time for it. The ladder has six stages and no
slack; scheduling 45 optional minutes inside 180 would make it a trap. So it is **available and
scored, but not planned for** — and the brief says exactly that, so nobody discovers at 12:20 that
they gambled.

**What this resolves:** the collision this ticket opened with is now handled by *availability*
rather than by declaring the module unscored. The lesson still closes the event at 14:55
([12](12-results-block.md)); the exercise is simply reachable earlier by anyone fast enough, and
remains on the page afterwards for everyone else.

### Consequences

- [03](03-cadence.md) plans **09:30–12:30 only**, with no optional branch and no second population
  to schedule for.
- [12](12-results-block.md) inherits the extension demo as its **wrap**, which answers a question it
  was already carrying: what closes the event.
- [17](17-attendee-page.md) gains a post-12:30 section, which means its release timetable runs past
  the submission deadline.
