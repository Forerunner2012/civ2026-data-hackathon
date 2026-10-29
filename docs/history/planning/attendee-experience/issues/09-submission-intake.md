# How do 15–30 submissions physically arrive at 12:30?

Type: grilling
Status: resolved

## Question

[Ticket 21](../../challenge-spec/issues/21-pitch-and-judging-model.md) named this and left
it open:

> **Submission intake at 12:30** for 15–30 entries, and it must be quick — a shared drive, a git
> remote or a physical hand-in. Undecided; it is execution, but it needs an owner.

It is more than execution, because the mechanism decides what a participant does in the last ten
minutes of a three-hour event, and that is squarely attendee experience. It is also the single
point in the day where **every workstream does the same thing simultaneously** — the one genuine
thundering herd.

## What is being moved

Per §6, a submission is a directory: `detector/`, `events.jsonl`, `evidence/` (compact MCAP clips),
`metrics.json`, `run-manifest.json`, `report.md`, optional `extension/`, and a `reproduce.ps1|sh`.
The clips dominate the size, and nobody has bounded them — *compact* is a rubric criterion, not a
limit. Sizing this is part of the ticket.

## The options

| | Mechanism | For | Against |
|---|---|---|---|
| **A** | LAN intake — an HTTP endpoint on an organizer machine in the room | Offline-safe, no accounts, fast, and the machine is plausibly the same one [06](06-fallback-and-recovery.md) uses as the shared runner | Something has to be built and hardened; one box is one failure |
| **B** | Git remote | Free provenance and history, familiar to this cohort | Needs accounts and auth, needs a network, and clips are binary blobs — the worst possible git payload |
| **C** | Shared cloud drive | Zero build | Breaks §3.3's local-first posture, needs venue internet for 30 concurrent uploads, and needs accounts |
| **D** | Physical hand-in — USB sticks to the desk | Cannot fail for network reasons | Serialises 30 people at one table at 12:30, and someone will hand in the wrong directory |

**Leading candidate: A, with D as the stated fallback.** It is the only option that is offline-safe,
account-free and fast, and it consolidates with the recovery runner. But see the risk below.

## What this ticket must decide

- The mechanism, and the fallback if it fails at 12:29.
- **Consolidation with [06](06-fallback-and-recovery.md).** One organizer box doing both intake and
  recovery runs is efficient and is also a single point of failure that would take the whole event
  with it. Decide deliberately; if consolidated, state the standby.
- **Validation at intake, or after?** A submission missing `run-manifest.json` scores zero on
  Reproducibility. Telling the participant at 12:29 is worth 15 points to them; telling them at
  14:30 is a grievance. Candidate: intake runs a **structural check only** — the directory shape,
  not the content — and returns pass/fail immediately. Anything deeper belongs to
  [ticket 15](../../challenge-spec/issues/15-ai-build-review-gates.md)'s evaluator gates.
- **Can a participant submit more than once?** Almost certainly yes — submitting early and improving
  is exactly the behaviour to encourage, and it de-risks 12:30 enormously. Decide whether the last
  submission wins and whether the pace car pushes an early-submit beat ([03](03-cadence.md)).
- **Size bound on `evidence/`.** Nobody has set one, and *volume reduction* is a scored criterion.
  Decide whether intake enforces a cap or merely records the size for scoring.
- **The receipt.** A participant who has submitted needs to *know* they have submitted. A returned
  hash, printed and pinned to the desk, ends the anxiety and gives the jury a tie-break record.
- **What happens after 12:30.** Hard cutoff, or a stated grace? Recommendation to test: hard, and
  visibly counted down by the pace car from 12:20, with the multiple-submission policy above making
  it survivable.

## Why this is on the frontier

Nothing blocks it. It blocks [08](08-room-requirements.md), which cannot state the network and
machine requirements until the mechanism is chosen.

## Answer

**Option A — LAN intake on the organizer box, USB hand-in as the stated fallback. Resubmission is
unlimited and actively encouraged; intake validates structure only and returns a receipt.**

### Resubmission is not a nicety — the cadence depends on it

[03](03-cadence.md) resolved with two beats that are lies if the first submission is final:

- **B4, 11:00:** *submit what you have, take the Kashiwa solution, open the Reims data.*
- **B7, 12:10:** *submit an incomplete one now. You can submit again.*

Those two lines are how the transfer cliff and the deadline are survived. So: **unlimited
resubmission, last one wins**, and the page pushes an early-submit beat rather than treating 12:30 as
the moment anything is handed over.

This also flattens the one genuine thundering herd in the day. If a third of the room has already
submitted by 11:05, 12:30 stops being a single simultaneous event.

### The mechanism

**An HTTP upload endpoint on the organizer machine, on the room LAN.** Offline-safe, account-free,
fast, and it is already the box serving [the page](17-attendee-page.md) and running
[06](06-fallback-and-recovery.md)'s watched directory.

Rejected: git (accounts, auth, and clips are the worst possible git payload), cloud drive (breaks
§3.3's local-first posture and needs venue internet for 30 concurrent uploads), USB-only (serialises
thirty people at one table at 12:30).

**USB hand-in stays as the stated fallback**, exercised in rehearsal, not invented on the day.

It carries one case beyond a LAN failure, identified in [13](13-coach-guide-and-checkpoints.md): a
participant on a **full-tunnel corporate VPN** cannot reach this endpoint even though the room
network is healthy. [05](05-warm-up-and-environment-gate.md)'s gate now tests page reachability so
they are found at 09:50 rather than at 12:25 — but the fallback they are routed to is **this one**,
and the static page export does not cover it. Keep USB hand-in available all session, not only as a
LAN-down contingency.

**One property worth naming:** a participant on [06](06-fallback-and-recovery.md)'s runner already
has their outputs *on this box*. Their submission can reference a completed run rather than
uploading it back, which removes the one step where the recovery path would otherwise be slower than
the normal one.

### Validation: structure only, and immediately

Intake checks the **directory shape** — is `run-manifest.json` there, is `report.md` there, is
`events.jsonl` parseable — and returns pass or fail on the spot. Nothing deeper.

The reason is a participant-experience one: a submission missing `run-manifest.json` scores zero on
Reproducibility. Telling someone at 12:29 is worth 15 points to them. Telling them at 14:30 is a
grievance nobody can fix. Anything beyond structure belongs to
[ticket 15](../../challenge-spec/issues/15-ai-build-review-gates.md)'s evaluator gates, which
run unattended after the close.

### The receipt

Intake returns a **content hash and a timestamp**, displayed and printable. Three jobs:

1. A participant who has submitted *knows* they have submitted, which ends the 12:25 anxiety that
   otherwise makes people resubmit blindly.
2. It is the tie-break record — [11](11-prizes-and-recognition.md) can break ties on **earliest
   submission of the winning entry**, which is only possible if the timestamps exist.
3. It is provenance for the jury.

### Size

**A generous hard cap — order 2 GB per submission — published in advance and enforced.**

Realistic submissions are far below it: signals-only Reims is ~350 MB for 38 minutes
([ticket 24](../../../../../.scratch/civ2026-challenge-spec/issues/24-survey-reims-bag.md)), and a set of few-second
evidence clips over a handful of topics is a fraction of that. Anything approaching 2 GB has
misunderstood *compact evidence* so completely that a clear rejection is more useful than silent
acceptance.

**Intake records the size; scoring judges it.** Volume reduction is a rubric criterion, not a gate —
the cap exists so thirty simultaneous uploads cannot take the LAN down, not to grade anyone.

### The cutoff

**Hard at 12:30.** No grace, and the page counts down from B7 at 12:10. That is only defensible
because resubmission is unlimited: everyone has been told since 11:00 to have *something* in, and
B7 says it again twenty minutes before the close.

### Consolidation and its cost

> **Superseded.** [06](06-fallback-and-recovery.md) later cut the recovery runner and
> [08](08-room-requirements.md) cut the LAN and the box with it. Submission is a form; there is
> nothing to consolidate and no standby to hold.

[06](06-fallback-and-recovery.md) originally decided this: **the same box serves the page, the recovery
runner and intake.** One thing to build, harden and test.

It is also a genuine single point of failure that would take all three at once. **The cold standby
laptop is mandatory**, with the same image and the same data, and
[08](08-room-requirements.md) carries it. Rehearse the failover in Phase 5 — an untested standby is
a story, not a mitigation.

### What this hands on

- **[08](08-room-requirements.md)** is now unblocked on network and machine: room LAN, one box, one
  cold standby, plus USB media.
- **[11](11-prizes-and-recognition.md)** gets its tie-break input.
- **Owner needed:** the intake endpoint is a small build item with no owner, and it is on the
  critical path for the whole afternoon.

## Update — metadata only, submitted through a form

Organizer's decision, and it is the larger of the two changes: **submissions carry the *metadata* of
the work, not the evidence data itself.** No clips are collected. Transport becomes a simple form
(Google Forms / Drive) rather than a built endpoint.

### Why this is bigger than a transport change

Everything difficult about this ticket was a consequence of moving gigabytes: the 2 GB cap, the
thundering herd at 12:30, the LAN being load-bearing, concurrency, the build item with no owner.
**A metadata-only submission is kilobytes.** All of it goes away, and a form becomes not just
adequate but obviously right.

The 2 GB cap, the size-based rejection and the concurrency reasoning above are **superseded**.

### What is submitted

| | Size | Purpose |
|---|---|---|
| **The EventSpec** | ~1 KB | The participant's actual work |
| **`events.jsonl`** | small — intervals, not data | Detection scoring; the jury's factual anchor |
| **`run-manifest.json`**, extended | small | Everything below |
| **`report.md`** | one page | 45 jury points |
| **One figure**, embedded or linked | small | See Visualization, below |

The **run manifest carries what the clips used to prove**: per-clip topics retained, window
durations, input bytes versus output bytes, source bag and spec hashes, timings, and `civ clip`'s own
validity check result. §6 already specifies a run manifest of *versions, hashes, parameters,
timings* — this extends an existing artifact rather than inventing one.

### Does the rubric survive? Mostly, with one honest weakening

[Ticket 21](../../challenge-spec/issues/21-pitch-and-judging-model.md)'s Evidence and
extraction (15) machine-checks *clip validity, correct topics, volume reduction*:

- **Correct topics** — in the manifest. Unaffected.
- **Volume reduction** — bytes in versus bytes out, in the manifest. Unaffected, and arguably
  cleaner as a number than as an inspected file.
- **Clip validity** — **weakened.** It becomes self-attested: `civ clip` validates locally and
  records the result. Say so plainly rather than pretending otherwise.

**The compensating control is that the spec is submitted.** Anything can be re-run by an organizer,
on the sealed data, at any time. That also opens a stronger option for the build to consider:
**score Detection by executing the participant's spec** rather than by trusting their
`events.jsonl`. It changes nothing about
[ticket 16](../../challenge-spec/issues/16-evaluator-calibration.md)'s semantics — temporal
IoU, one-to-one matching, F1 — only where the events come from. Flagged for the evaluator owner, not
decided here.

**Visualization (15)** was *jury reads the evidence and claims*, and there are now no clips to read.
So the report must carry **one figure** — a plot or a still with the interval marked. That is a
requirement on [14](14-participant-materials.md)'s report template, and it is arguably a better test
than a raw clip: choosing one frame that makes the case is the skill.

### Two things this also buys

- **No thirty copies of clipped camera footage on a third-party drive.**
  [Ticket 19](../../../../../.scratch/civ2026-challenge-spec/issues/19-personal-data-clearance.md) cleared the imagery,
  so this was not a blocker — but not collecting it is simpler on rights, storage and attribution,
  and it removes a conversation nobody needs to have.
- **The participant keeps their evidence**, which fits
  [ticket 20](../../challenge-spec/issues/20-cohort-skill-floor-licensing.md)'s *take it, not
  join us* posture better than surrendering it does.

### What still has to hold

- **Unlimited resubmission** — unchanged and still load-bearing. Two of
  [03](03-cadence.md)'s beats depend on it. A form supports this natively; last response wins, keyed
  on participant identity.
- **The receipt.** A form's confirmation is weaker than the hash-and-timestamp receipt specified
  above. Keep a timestamp at minimum, since [11](11-prizes-and-recognition.md) breaks ties on it.
  Have `civ` print the submission's content hash locally so the participant can paste it into the
  form — that recovers most of the property for free.
- **Structural validation moves earlier.** A form cannot check the directory shape, so **`civ` must
  validate before the participant submits** and refuse to emit a submission blob that is missing
  `run-manifest.json`. Better than intake-time checking anyway: it fails at 11:00 rather than 12:29.
- **Internet dependency.** A form needs venue internet, which
  [08](08-room-requirements.md) now names as the highest-cost failure. **Keep a local or USB
  fallback**, and note this closes [13](13-coach-guide-and-checkpoints.md)'s VPN case outright — a
  full-tunnel VPN reaches Google fine.

### Consequences

- **[05](05-warm-up-and-environment-gate.md)**: the gate's third clause becomes a **general
  internet-reachability check** — opening the page proves the same path submission will take, since
  both now run over the public internet. It no longer tests the LAN at all.
- **[08](08-room-requirements.md)**: the room LAN drops to serving only
  [06](06-fallback-and-recovery.md)'s runner and is close to optional — but **venue internet becomes
  the highest-cost dependency**, and it is the one thing neither brought nor controlled. See that
  ticket's Update 2, including the cheap fix of serving the page on **both** paths.
- **[12](12-results-block.md)**: the organizer can no longer drive walkthroughs from submitted clips.
  The four selected participants should **drive their own laptop while being interviewed** — which
  preserves the zero-prep property and is better anyway, since it is their machine and their files.
- **[10](10-jury-composition.md)**: the agents read the report against the **spec, `events.jsonl` and
  the manifest**. They were never going to verify a video clip, so little is lost.
- **[14](14-participant-materials.md)**: the report template gains a required figure.
