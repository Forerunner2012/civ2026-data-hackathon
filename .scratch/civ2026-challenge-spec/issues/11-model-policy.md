# What is the model policy?

Type: grilling
Status: resolved

## Question

`HACKATHON-HANDOFF.md` §8: no model supplied, one pinned local CPU model, or a shared on-site
inference service?

Constraints already fixed: §3.5 rules out requiring a GPU, a paid model or an API key; §3.3
requires the deterministic core to work with no model at all; ticket 04 fixed a CPU-only
container as the only environment.

What has to be settled:

- If a model ships in the image, which one, at what size, and what does it cost in image size
  and first-run time on a BYOD laptop?
- Is CPU inference fast enough to be useful inside a three-hour session, or does it become a
  trap that burns a team's middle hour?
- A shared on-site service contradicts "local-first and offline-capable" (§3.3) and adds a
  single point of failure for the room. Is that trade ever worth it?
- If no model ships: can teams bring their own, and does that create an unfair advantage the
  scoring has to account for?
- Does the answer differ for the bonus track versus the required path?

## Why this is on the frontier

Nothing blocks it now that ticket 04 has fixed the environment. It blocks ticket 12 — how
agentic work scores depends on what teams can actually run.

## Answer

**No model is shipped.**

- Ticket 04 fixed a CPU-only BYOD container, and ticket 17 is already fighting the size of what
  attendees must download. A bundled model makes both worse for something the required path
  must not need.
- §3.3 requires the deterministic core to work with no model at all, and §3.5 rules out requiring
  a GPU, a paid model or an API key. A shipped model would sit unused on the required path and
  become a trap on the optional one: CPU inference inside a three-hour session burns the middle
  hour for most teams that try it.
- A shared on-site inference service contradicts "local-first and offline-capable" and adds a
  single point of failure for the whole room.

**Teams may bring their own** — nothing forbids it, and with ticket 09 confining Python to the
deferred extra track, a model can only contribute to bonus work that is judged qualitatively
anyway. No fairness problem arises in the scored core, because the scored core cannot use one.

**Revisit when the extra track is designed.** That is the point at which a pinned local model
might earn its place, and by then the image and the golden path will be settled.
