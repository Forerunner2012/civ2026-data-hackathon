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

## Deployment state and standing constraints

Recorded here because it existed nowhere in the repo — only in a temporary handoff document that
has since been deleted. This is operational state, not a decision.

**Nothing is deployed.** No site source was uploaded, no hosted version was saved, and nothing is
publicly reachable today.

**A Sites project shell exists.** Its non-secret project id is committed in
`handoff-site/.openai/hosting.json`. **Do not create the site again** — creating a second shell
for the same site is the failure mode this note exists to prevent.

**A private source upload was attempted and correctly refused**, because copying the source to an
external private repository had not been explicitly authorized. No repository credential was
stored anywhere. If authorization arrives, obtain a fresh short-lived credential, use it
in-memory per command, and never persist it.

**Publishing requires an explicit instruction from the organizer** — something unambiguous such
as "approve the private Sites source upload and deployment". Absent that, the site stays local.

When that authorization arrives, the sequence is:

1. Re-verify a clean tree and a clean production build (`npm test` must pass; the public artifact
   must still contain no organizer route or organizer-only text).
2. Compute the site-root commit from the approved branch state:
   `git subtree split --prefix=handoff-site <approved-commit>`.
3. Push that exact commit to the existing Sites source repository with a per-command, in-memory
   credential.
4. Package with the Sites plugin's `scripts/package-site.sh`.
5. Save one version, prefer owner-only deployment, poll to completion, then open the resulting URL.

**Before any public deployment**, confirm the artifact boundary above still holds — the tests are
the gate, and they should be re-run against the exact commit being published rather than against
the working tree.
