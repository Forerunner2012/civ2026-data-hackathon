# Cohort, skill floor and the definition of "open source"

Type: grilling
Status: resolved

## Question

§5 Phase 0's gate lists team count, required skill floor and the definition of "open source"
alongside scenario, duration, data rights and hardware. The original §8 queue never carried them,
so the first map closed without them. This ticket closes the remainder.

## Answer

### Cohort

**30 participants, working solo or in duos.** Not teams of 3–5.

This contradicts §4.7 and §4.2, which assume 3–5 person teams and a three-minute pitch each, and
it produces **15–30 submissions** rather than six or eight. The consequences are large enough to
have their own ticket — see 21.

Second-order effect: a solo participant cannot split investigation from detector authoring from
pitch preparation, so §4.7's role suggestions become a checklist for one person rather than a
division of labour. The ladder has to be completable by one pair of hands in three hours.

### Skill floor

**High. Every participant has experience with robotic or vehicular data**; replaying and analysing
recordings is not a barrier.

This is the most consequential correction to the earlier design. Ticket 18 deliberately made the
scored core a threshold-plus-timing exercise and recorded "detection no longer separates teams on
cleverness" as an accepted cost. That cost was tolerable for a mixed-skill room. **For 30
practitioners it is not** — the Kashiwa core is a warm-up, not a challenge.

Resolved by ticket 14's reversal: the difficulty moves into the transfer to a second dataset.

### Definition of "open source"

Two distinct obligations:

1. **Inbound — tool licences must compose cleanly.** The tools used and combined in the hackathon
   material must not create an IP or licence problem once that material is published. This needs
   an actual audit of every dependency on the golden path — see ticket 23.
2. **Outbound — the kit and content ship permissively.** Free use, reuse and extension, with
   credit *suggested* rather than onerously required. Practically: a permissive code licence
   (MIT or Apache-2.0) for the runner and CLI, and CC BY 4.0 for the workshop content and the
   site, which also composes cleanly with the Kashiwa attribution obligation from ticket 05.

**The workshop content and the website will be public for the event.** That has an immediate
consequence for the organizer view — see ticket 22.

## Update - the CLI is published too

The `civ` CLI ships public alongside the workshop content, so participants can tune or customise
it. **No contributions are expected back** - it is a gift, not a community project.

Two consequences worth carrying:

- **It extends the extensibility lesson one level down.** Ticket 25 makes external *data* plug in
  through the `resources:` seam; a published, forkable CLI means the *tool* is a seam too. "If the
  runner does not do what you need, change it" is a stronger closing message than "here is our
  tool".
- **Framing and maintenance expectations.** Say "take it" rather than "join us". No issue tracker
  triage, no PR review burden, no roadmap implied. That also keeps the ticket 07 clean-room story
  simple: the published artifact stands alone and owes nothing upstream.
