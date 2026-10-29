# What must the physical room provide, and what is the design if it does not?

Type: grilling
Status: resolved
Blocked by: 01, 02, 06, 09

## Question

Nothing in map one describes the room. Every mechanism this map installs assumes physical
affordances that nobody has asked the venue for, and the ask has to be made early enough to change
— a conference room allocation in Miyazaki is not adjustable on 2 September.

This ticket collects the requirements the upstream tickets generate and turns them into a single
statement of what the venue must provide, plus the **degraded design** for each thing it might not.

## What has to be collected

- **Display surfaces. [01](01-pace-car.md) has resolved and delivered its half:** **one optional
  screen.** Two updates removed first the live rabbit and then the board, so everything now lives on
  [the attendee page](17-attendee-page.md), on participants' own laptops. The one screen at the front
  projects *that same page* — one artifact in two placements, so the room gets peripheral awareness
  at no authoring or staffing cost. Without it the day still works. This is a much easier venue ask
  than the two surfaces this ticket was originally going to carry.
- **The LAN is now load-bearing, not an accelerator.** [17](17-attendee-page.md) recommends serving
  the page from the organizer machine, which means a LAN failure takes hints, tips and solutions with
  it — on top of intake ([09](09-submission-intake.md)) and the recovery runner
  ([06](06-fallback-and-recovery.md)). §3.3 requires the required path to survive offline. **Price
  the single-point-of-failure explicitly** and decide the static fallback bundle coaches hand out.
- **Network.** [02](02-help-protocol.md) may want a chat channel or telemetry;
  [06](06-fallback-and-recovery.md) may want an organizer runner machine;
  [09](09-submission-intake.md) needs intake for 15–30 entries at once. All of these want a **room
  LAN**, which is not the same as venue wifi and is not the same as internet. §3.3 requires the
  required path to be offline-capable, so the LAN must be an accelerator, never a dependency. Decide
  what is brought (a switch, an access point, cabling) versus requested.
- **Power** for 30 laptops running containers for three hours, which is a real electrical ask and a
  real trip-hazard problem.
- **Seating and circulation.** A pull-based help protocol needs a coach to *see* a raised token from
  across the room and reach the desk without climbing over people. Rows of theatre seating defeat
  both. Decide the layout, and whether duos sit together.
- **Where the organizer machines sit** — runner ([06](06-fallback-and-recovery.md)) and intake
  ([09](09-submission-intake.md)) — and whether they are the same box.
- **The lunch clinic room**, if [04](04-extension-placement.md) lands in the lunch. Same room or
  another, and is the room even held between 12:30 and 14:30?
- **The results room** at 14:30 — [12](12-results-block.md) needs a screen and, if walkthroughs are
  interview-style, a way to put a participant's submitted artifacts on it.
- **Physical consumables**: help tokens, pace cards, printed briefs, USB fallback media
  ([17](../../challenge-spec/issues/17-dataset-subsetting-and-distribution.md) keeps USB as
  the data fallback), and who carries them to Japan.

## The output that matters

Two lists, because they go to different people:

1. **A venue ask** — what to request now, with a deadline, and who owns the request.
2. **A degradation table** — for each affordance, what the design becomes without it. One screen
   instead of two. No LAN. Fixed theatre seating. Under-powered sockets. Each of these has a
   plausible answer, and each is a disaster if first discovered on the morning.

## Why it is blocked

It is a collector. Asking the venue for things before [01](01-pace-car.md),
[02](02-help-protocol.md), [06](06-fallback-and-recovery.md) and [09](09-submission-intake.md) have
chosen their mechanisms would be guessing — and each of those tickets is required to state its own
minimum, so this ticket sums minimums rather than inventing them.

## Answer

**The venue ask is small — power, a table layout and one optional screen. Everything load-bearing is
brought, not requested, because everything load-bearing is now the LAN.**

### The finding: the venue is not the risk. The box is.

Successive resolutions shrank the venue ask to almost nothing — [01](01-pace-car.md) removed the
second screen and then the board, [04](04-extension-placement.md) removed the lunch clinic and its
room booking. What replaced them is a **single organizer machine** serving
[the page](17-attendee-page.md), [06](06-fallback-and-recovery.md)'s runner and
[09](09-submission-intake.md)'s intake.

So the question this ticket was written to answer — *what if the venue does not provide X* — has
largely become *what if our own box dies*. That is a better problem to have, because it is entirely
within the organizers' control, and it is the one that must be rehearsed.

### The venue ask

Small enough to make now, and it should be made now — a room allocation in Miyazaki is not adjustable
on 2 September.

| Ask | Why | Owner |
|---|---|---|
| **Power for 30 laptops, 3 hours** | Containers, no GPU. Distribution and trip hazards are the real problem, not total draw | unassigned |
| **Tables, not theatre rows** | [02](02-help-protocol.md)'s cards must be visible across the room and reachable without climbing over people. Duos sit together | unassigned |
| **One projection surface** *(optional)* | Shows the same page participants have open. Peripheral awareness at zero authoring cost | unassigned |
| **Permission to run our own network gear** | See below. This is the one that gets refused late if not asked early | unassigned |
| **Room held 12:30–14:30** *(weak)* | Coaches are around for the first 45 minutes of lunch ([04](04-extension-placement.md)). No structured session, so this is convenience not requirement | unassigned |
| **Results room 14:30, screen** | [12](12-results-block.md) needs to put a participant's submitted artifacts on it | unassigned |

### Brought, not requested

**Do not depend on venue wifi for anything.** It is not a room LAN and it is not under anyone's
control.

- A **switch or access point, and cabling**, carried in and set up the day before.
- **The organizer box.**
- **A cold standby laptop** — same image, same data, mandated by
  [06](06-fallback-and-recovery.md). Untested, it is a story rather than a mitigation, so **rehearse
  the failover in Phase 5.**
- **Four 2 TB high-speed SSDs**, confirmed as available. Each is a complete **event-in-a-box**: the
  container image (the payload that actually matters — nobody can quickly download a ROS 2 image in
  the room), both datasets with checksums, the optional image context pack, the static export of
  [the attendee page](17-attendee-page.md), and [06](06-fallback-and-recovery.md)'s fallback pack.
  **Formatted exFAT** — the only filesystem both Windows and Ubuntu read *and write* natively — with
  **USB-C and USB-A adapters**, loaded and checksum-verified before travelling.
  See [07](07-pre-event-readiness-and-reveal.md); they circulate on arrival rather than being held
  for failures.
- **Consumables:** help cards for 30+ ([02](02-help-protocol.md)), printed signal traces for 30
  ([05](05-warm-up-and-environment-gate.md)), printed briefs, report templates. Someone carries these
  to Japan — name them.

### Degradation table

For each thing, what the day becomes without it. None of these should be discovered on the morning.

| Missing | What happens | Cost |
|---|---|---|
| **The projection surface** | Everyone still has the page on their own laptop | Low — peripheral awareness only |
| **The LAN** | The static page export goes out on USB; intake falls back to USB hand-in; **[06](06-fallback-and-recovery.md)'s runner is gone** and anyone with a broken container is on tables and clips alone | **High.** The one genuinely bad case |
| **The organizer box** | Cold standby, rehearsed | Medium — minutes, if the failover was practised |
| **Tables** | Cards still work; coach circulation degrades; the analogue block's neighbour comparison gets awkward | Medium |
| **Power** | Nothing else matters | Fatal — ask early, verify on site the day before |
| **Room over lunch** | Coaches are simply elsewhere; the extension exercise is self-serve anyway | Low, by design |

**The LAN row is the one to act on.** It is the single dependency whose loss is not gracefully
absorbed, because it takes hints, solutions, recovery and intake together. Two cheap mitigations,
both stated here so they are not improvised: the **static page export on USB**, and **rehearsing the
day without the LAN at all** in Phase 5 — not as a stunt, but because §3.3 requires the required path
to survive offline and nobody has ever checked that the *facilitation* survives it too.

### Setup the day before

Everything above assumes access to the room on **2 September**: gear in, network up, box and standby
imaged and tested, consumables laid out, and one end-to-end rehearsal of gate → page → runner →
intake. Without that access the morning absorbs it, and the morning is the thirty minutes the whole
design depends on. **Confirm room access the day before as part of the venue ask.**

## Update 4 — no room LAN. No organizer box. Nothing to bring but consumables.

[06](06-fallback-and-recovery.md) cut the recovery runner, which was the **only** thing left on the
room LAN. So the LAN goes, and with it everything that existed to support it.

### Final architecture

| Service | Path | If it fails |
|---|---|---|
| Attendee page | Funnel, public internet | Static export on the SSDs |
| Submission | Form, public internet | USB hand-in |
| Recovery | **Pairing** | Fallback pack on the SSDs |
| Data and image | SSDs, circulating on arrival | Pre-event download |

**No switch, no cabling, no access point, no organizer box, no cold standby, no failover to
rehearse.** Update 2's "serve the page on the LAN as well" is withdrawn — the SSD export is already
the second path, and a third is not free.

**Everything now degrades to something already in the room**, because the SSDs carry the page export,
the fallback pack, the data and the image.

### Revised degradation table

| Missing | What happens | Cost |
|---|---|---|
| **Venue internet** | Page falls to the SSD export; submission falls to USB hand-in. Both already exist and are already carried | Medium — the only row that matters, and it is covered |
| **Power** | Nothing else matters | Fatal — verify on 2 September |
| **Screen** | Everyone still has the page on their own laptop | Low |
| **Desks/chairs** | Confirmed present | — |

### What is still brought

Four 2 TB SSDs, help cards, printed traces, briefs, power strips, USB-C and USB-A adapters. That is
the whole list. Updates 1–3's venue ask, network gear and standby machine are **superseded**.

## Update 3 — the venue is confirmed. What is left is the participants' own kit.

Organizer's confirmation, and it closes most of this ticket:

> **The venue has what is needed** — desks, chairs, and a screen to display the attendee page and
> the progress towards the next hints. What is still needed is that **participants bring appropriate
> hardware**, and **power plugs**.

So the venue ask below is **satisfied**, and the residual risk moves from the room to the laptops.

### The screen shows progress-to-next-unlock, not just the page

Worth capturing, because it is a design detail rather than a facility: the room screen carries the
page **and how long until the next hints unlock**. That is the tempo made visible for the whole room
at once — a participant does not have to switch tabs to know whether to keep pushing or wait. It is
the one thing the shared screen does that thirty individual laptops do not.

### The residual risk is hardware, and duos are the mitigation

*Participants have appropriate material* is an assumption, not a guarantee, and
[ticket 04](../../challenge-spec/issues/04-target-machine.md) accepted BYOD with no spare
machines. **Someone arriving with an underpowered laptop pairs into a duo** — the organizer's stated
mitigation, and it costs nothing:
[ticket 21](../../challenge-spec/issues/21-pitch-and-judging-model.md) already ranks solo and
duo together, so there is no scoring wrinkle.

This makes [06](06-fallback-and-recovery.md)'s buddying-up carry **two** failure modes rather than
one — a broken environment *and* inadequate hardware — which raises it from a nicety to a named
mitigation. It has to be **offered in the opening briefing**
([05](05-warm-up-and-environment-gate.md)), because nobody volunteers "my laptop is too weak" to a
room of peers unaided.

### Consequences

- **The venue ask table below is closed.** Power and desks are confirmed; the screen exists.
- **Say the hardware expectation in the pre-event pack** ([07](07-pre-event-readiness-and-reveal.md))
  in concrete terms — RAM, free disk, and that a container will run — rather than "appropriate
  material", which nobody can self-assess against.
- **Bring the power strips anyway.** "Power plugs" is the row most likely to be under-provisioned for
  thirty laptops, and it is the one whose absence is fatal.

## Update 2 — the final architecture, and the inversion nobody chose

Three organizer decisions landed in sequence — the page to **Tailscale Funnel**, submission to a
**form**, data onto **four 2 TB SSDs** — and Update 1 below only propagated the first. This is the
settled picture and it **supersedes both the finding and the degradation table above.**

### Where everything actually lives

| Service | Path | Backup |
|---|---|---|
| [The attendee page](17-attendee-page.md) | Funnel, public internet | Static export on the SSDs |
| [Submission](09-submission-intake.md) | Form, public internet | USB hand-in |
| [Recovery runner](06-fallback-and-recovery.md) | **Room LAN — the only thing left on it** | Sneakernet via SSD |
| Data and image | **SSDs**, circulating on arrival | Pre-event download |

### The inversion

Update 1 said *the venue is not the risk; the box is*, because everything load-bearing was carried
into the room. **That is no longer true.** The two most participant-visible services now run over the
public internet, and **venue internet is the one dependency that is neither brought nor controlled.**

Each decision was individually right — Funnel buys VPN immunity, the form removes gigabyte transfers,
the SSDs remove the download risk. The aggregate is worth seeing rather than discovering: the design
began fully self-contained and is now internet-dependent for page and submission.

**Correspondingly, the room LAN has become nearly optional.** It carries one service for a handful of
people, with a workable manual fallback.

### One cheap change that removes the single point of failure

**Serve the page on the LAN as well as through Funnel.** Same server, same content, bound to both —
near-zero cost, and it converts *the page needs the internet* into **the page needs either the
internet or the LAN**. Two independent paths, and both would have to fail.

Do it. It is the highest-value line in this update and it costs an extra bind address.

### Revised degradation table

| Missing | What happens | Cost |
|---|---|---|
| **Venue internet** | Submission falls to USB hand-in. The page survives **only if** it is also served on the LAN — otherwise it falls to the SSD export | **Highest.** Not controlled, not brought |
| **Room LAN** | Recovery runner only, a handful of people, sneakernet via SSD. Plus the page's second path | **Low now** — it was the worst row an update ago |
| **Both** | SSD export for the page, USB hand-in for submission, manual recovery. Survivable, entirely on rehearsal | High, and the case Phase 5 must actually run |
| **Organizer box** | Recovery runner. Cold standby, rehearsed | Medium |
| **Power** | Nothing else matters | Fatal — verify on site on 2 September |
| **Tables** | Cards still work; coach circulation degrades; the analogue block's neighbour comparison gets awkward | Medium |
| **Projection surface** | Everyone still has the page on their own laptop | Low |

### What still holds from Update 1

The venue ask, the brought-not-requested list, and setup access on 2 September are unchanged — except
that **a verified internet uplink is now the most important row on it**, and it is the one to test on
2 September rather than assume.

### Update 1 — the page moves to Tailscale Funnel, and the worst row changes

[17](17-attendee-page.md)'s update publishes the page over the public internet rather than the room
LAN. Three changes here:

- **The venue ask gains a row and softens another.** Add **a verified internet uplink** — tested on
  2 September, not assumed. *Permission to run our own network gear* stops being load-bearing for
  the page, though it stays for intake and the runner.
- **The degradation table's worst case is no longer the LAN.** Losing the room LAN now costs intake
  and the recovery runner, both of which have USB paths. **Losing venue internet costs the page** —
  hints, tips and solutions — for everyone at once, **and, since [09](09-submission-intake.md)'s
  update, submission too.** That is the new highest-cost row, and it is the one dependency the
  organizers do not control. **The SSDs mitigate the page** — each carries the static export — but
  the mitigation for *submission* is USB hand-in, which must therefore stay available all session
  rather than only as a contingency.
- **The static USB export is promoted from contingency to primary backup**, and
  [18](18-rehearsal-observations.md)'s deliberate breakage should be **"kill the internet"** as well
  as "pull the LAN". The internet failure is both more likely and more damaging.

Net: the *total* ask is smaller and the *controllable* fraction is lower. That is a reasonable trade
for removing the VPN failure mode, but it should be made knowingly.

### What this hands on

- **Owner needed** on every row of the venue ask, and on who carries the physical items.
- **[13](13-coach-guide-and-checkpoints.md)**: coaches need to know what to do in the LAN-down *and*
  internet-down cases, because that is when they become the distribution mechanism.
