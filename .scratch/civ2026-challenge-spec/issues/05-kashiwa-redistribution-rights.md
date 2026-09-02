# Are URT-Kashiwa redistribution terms sufficient?

Type: research
Status: resolved

## Question

Under what licence and terms is the URT-Kashiwa dataset held, and do those terms permit
**redistributing a subset to attendees** at CIV 2026 — including offline copies they keep on
their own machines afterwards?

Reuse at a previous hackathon does not by itself establish a redistribution right: the prior
event may have run under a different agreement, on organizer-controlled hardware, or under
terms that have since lapsed.

Facts to establish:

- The exact licence or data-sharing agreement covering the set, and who the counterparty is.
- Whether redistribution to third parties (attendees) is permitted, and whether it is limited
  to the event or extends to keeping the data.
- Attribution, share-alike or publication constraints that would bind attendee submissions.
- Whether derived artifacts — extracted clips, labels, sampled tables — inherit the same terms.
- Any personal-data exposure in the bags (faces, plates, GPS traces around identifiable homes)
  and what the prior event did about it.
- Whether the same terms cover the newly expected ROS 2 / PX4 data.

## Why this is on the frontier

Ticket 01 assumes attendees can be handed Kashiwa data offline. If that assumption fails, the
hero dataset changes and most of the map is re-cut — so this is worth resolving early even
though nothing is blocked on it yet.

## Notes

Resolvable by a `/research` subagent plus whatever agreement paperwork exists outside the repo.
The repo contains no licence file for the dataset.

## Answer

Full findings with verbatim licence clauses and sources:
[`../research/05-kashiwa-redistribution-rights.md`](../research/05-kashiwa-redistribution-rights.md).

**Copyright: cleared.** URT-Kashiwa is `github.com/tlab-wide/URT-Kashiwa`, published by Tsukada
Laboratory, The University of Tokyo, under **CC BY 4.0**. Subset redistribution is expressly
granted ("in whole **or in part**"), the grant is irrevocable, and attendees keep offline copies
**as of right** — as direct licensees of UTokyo, not by the organizers' grace. Attribution is the
only condition: no share-alike, no embargo, no research-only limit. Ticket 01's assumption holds.

Three operative consequences:

1. **The organizers may not impose a delete-after-the-event clause** on Kashiwa material —
   §2(a)(5)(b) forbids downstream restrictions, so such a rule would breach the licence being
   relied on. Attendee submissions may be licensed however they like.
2. **Mirror the data now.** §6(c) lets T-Lab stop distributing at any time without affecting
   granted rights — rights survive, *access* does not. Take a pinned local copy of all 16 MCAPs
   with checksums and a retrieval date before further planning depends on them.
3. Sealed labels the organizers author are the one grey case. Cheapest fix: publish them CC BY
   4.0 anyway and stop caring.

**Personal data: not cleared — verified silence, not verified safety.** No consent,
anonymisation, ethics, APPI or GDPR statement exists in any published artifact, and CC BY 4.0
§2(b)(1) expressly does not license privacy or personality rights. The bags carry a front RGB
camera and GNSS. Graduated to **ticket 19** — since **closed**: T-Lab participates in the
hackathon, so the data relationship is a direct collaboration with the publishing lab and the
camera topic is cleared. Attribution remains the one live obligation.

Two corrections to this ticket's framing, both verified: the event is in **Miyazaki, Japan**, not
France (GDPR reaches Heex via its Reims establishment, not the venue); and the dataset's
corresponding author, Manabu Tsukada, is on the CIV 2026 organizing committee — every remaining
unknown is one email away.

**Newly collected data is not covered.** The grant attaches only to the 16 routes published
2025-09-24. Immaterial for the freeze, since ticket 01 already made Kashiwa the only dependency.
