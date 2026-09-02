# Phase 4 progressive attendee-experience acceptance

Status: **accepted**

Recorded: 2026-08-29

Human approval: the organizer approved the final participant wording and all seven post-event
worked approaches on 2026-08-29. This approval does not publish the solutions before the event;
release remains separately environment-gated and the route is absent from the public production
artifact.

## Accepted participant experience

The participant start page now presents one stable command path:
`doctor -> inspect -> sample -> detect -> clip -> score -> report`. It names the exact
participant-safe Kashiwa warm-up and Reims development products, both tracked layouts, the public
signal inventories, and the approved 15/10 Detection split. The optional extension is visible and
scored but has no scheduled beat.

The organizer-hosted live page advances monotonically through seven timed beats. Each current beat
has an expectation, hint, and tip. Future beat content stays in the server-only module and does not
enter browser assets. The real B2 teaching unit uses the accepted non-answer result
`189 matching samples -> 14 merged candidates -> 4 events` and preserves the zero-brake ambiguity:
timing corrects the count but does not settle meaning. No layer or worked approach resolves
handedness.

The report is prompted in three installments: headings 1 and 2 at B3, headings 3 and 4 at B6, and
heading 5 at B7. The desk set is exactly one write-on A4 signal trace derived from the accepted
participant product, one two-sided A5 help card, and one A4 participant brief. No separate cheat
sheet or pace card exists.

## Audience and release boundary

A normal public build serves the participant page at `/` and `/participants`, plus its static desk
and fallback assets. It contains no organizer, coach, API, live-session, or solution route. The
organizer-hosted internal build retains `/live`, `/live/coach`, and `/api/live`. `/solutions` is
internal-only and returns not found unless either an organizer preview flag is set or both its
checked-in approval state and post-event release flag allow it.

The public server bundle, client assets, rendered pages, fallback, and desk materials were scanned
for organizer vocabulary, private evaluation content, future guidance, private provenance, answer
intervals, scenario directions, secrets, and runtime paths. None was present. External MCAPs were
read in place only; no recording, organizer path, viewer/container state, generated PDF, screenshot,
or cache is committed.

## Verification evidence

- Full `npm run test`: three internal/public builds and 27 rendered-content, schedule/state,
  release-gate, static-export, production-route, leakage, and print-contract tests passed.
- `npm run lint`: passed.
- `git diff --check`: passed.
- The public artifact returned 404 for organizer, live, and solution routes and contained none of
  their route patterns or protected copy.
- Edge print-media rendering produced one 8.26 x 11.69 inch A4 brief, two 8.26 x 5.83 inch A5 help
  sides, and one 11.69 x 8.26 inch A4 trace. All four rendered pages were visually inspected at
  full resolution: text was legible and no content was clipped, overlapped, or split unexpectedly.
- Static materials use semantic headings, lists, labeled SVG text alternatives, sufficient
  monochrome structure, and no script. The live page exposes progress and countdown labels,
  `aria-live` status, labeled current layers, and a reduced-motion mode.

Phase 5 still owns fresh-host installation, event-network and hardware rehearsal, release-candidate
freeze, physical-media verification, notices/SBOM/source archive, and final go/no-go approval.
