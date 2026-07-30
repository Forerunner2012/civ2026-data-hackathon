# What is the model policy?

Type: grilling
Status: open

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
