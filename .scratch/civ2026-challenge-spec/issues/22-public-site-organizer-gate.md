# Gate the organizer view before the site goes public

Type: task
Status: resolved

## Question

Ticket 20 established that **the workshop content and the website will be public for the event.**

`handoff-site` serves three routes: `/` (entry door), `/participants` and `/organizers`. The split
guarantees organizer material never enters the participant *bundle* — enforced by `server-only`
and by the leakage tests in `tests/rendered-html.test.mjs`. But **that is a content boundary, not
access control.** `/organizers` is unauthenticated: anyone with the URL reads the teaching goals,
the evaluation internals, the sealed-label mechanics, the phase gates and the full decision
history. The entry door links to it directly, which advertises it.

Options, in order of preference:

1. **Build the public site from the participant route only.** Deploy `/participants` as the public
   artifact and keep the organizer view local or on a separate private deployment. Cleanest —
   there is nothing to bypass because nothing is served.
2. **Gate `/organizers` in `worker/index.ts`** behind a shared credential from an environment
   binding, and drop the link from the public entry door.

Either way: remove the organizer link from the door on the public build, and keep the `noindex`
that is already in place.

## Why this is a task rather than a decision

The requirement is not in question — internal material must not be public. Only the mechanism is,
and both mechanisms are small.

## Answer

**Use option 1: production builds contain the participant app only; the full organizer app is a
local-development surface.** No credential, secret, or public organizer deployment is required.

`handoff-site/vite.config.ts` now gives vinext two source roots:

- `vinext build` scans `public-source/app`, whose `/` and `/participants` both render the
  participant view and which has no organizer route;
- `vinext dev` scans the full `app` tree, so organizers retain the entry door and the direct
  `/organizers` view locally.

This is an artifact boundary, not a navigation convention. The production worker returns 404 for
`/organizers`; the organizer route pattern and organizer-only phrases are absent from both the
server bundle and downloadable client assets. The public root has no organizer link. The internal
route keeps its existing `noindex` metadata for any future private deployment.

The rendered-output test suite enforces all four properties. `npm test` passes, and a local dev
probe confirmed `/organizers` still returns 200.
