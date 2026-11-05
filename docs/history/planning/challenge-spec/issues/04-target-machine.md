# What machine must the required path run on?

> Historical planning. Follow the [archive index](../../README.md) for current guides and record boundaries.

Type: grilling
Status: resolved

## Question

What is the minimum supported machine for the required path, and how is the environment
delivered — native bundles, containers, or organizer-provided hardware?

## Answer

**Container-first, BYOD only.** Windows/WSL2 and Ubuntu, CPU-only baseline. One image to build
and test rather than a native build matrix. This also resolves §8's "native bundles vs
container-first" item.

**Risk accepted, explicitly:** with no pool of preloaded recovery laptops, a team whose WSL2 or
Docker Desktop setup fails has no hardware swap — and that failure lands in the first thirty
minutes, the exact window the design relies on for early success.

Mitigations that are now load-bearing rather than optional:

- The **non-ROS fallback pack** (§4.7) — pre-extracted tables and clips so data reasoning
  continues when execution does not. This must be built and rehearsed, not sketched.
- **Pre-event setup instructions and a `cive doctor` check** that attendees run *before* the
  day, with a support channel open beforehand.
- Phase 5 rehearsal must include a deliberately broken environment, not only clean installs.
