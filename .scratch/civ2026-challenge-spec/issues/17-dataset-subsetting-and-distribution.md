# How does 112 GB reach BYOD laptops offline?

Type: grilling
Status: open

## Question

Surfaced by ticket 06. The dataset as published is **16 bags, ~7 GB each, ~112 GB total,
~400 000 messages per bag**. Ticket 04 fixed the environment as **BYOD containers, offline**.
Those two facts do not currently fit together, and nothing in §6's "CPU/laptop-sized variant and
distribution plan" has been sized.

What has to be settled:

- **How much data does a team actually need?** The three-hour ladder needs one warm-up bag, a
  handful of development bags, and a sealed test set the teams never hold. That is not 16 bags on
  every laptop.
- **What is the reduction?** Topic filtering is the big lever — dropping camera and point-cloud
  topics collapses size by orders of magnitude, and the URT logic (ticket 06) runs off
  acceleration, velocity, steering, gear, GNSS and object topics, not RGB. But ticket 10 suggests
  visual context is what makes a turn judgeable, so this trades directly against evidence quality.
  Note ticket 19 may force the camera decision anyway.
- **Time-window trimming** as a second lever: keep the segments around candidate events plus
  margin, rather than whole routes. Risk: this leaks where the events are.
- **How is it physically distributed?** With no venue download assumption and no organizer
  hardware, the realistic options are USB-C SSDs handed out, a pre-event download link, or a
  local LAN share in the room. Each has a failure mode; the pre-event download is the only one
  that does not consume session time.
- **Disk space on a BYOD laptop** is itself a prerequisite to publish alongside the RAM floor.

## Why this is on the frontier

Nothing blocks it. It is a hard constraint on ticket 04's environment and on the warm-up design
sitting in the map's fog.

## Note

Ticket 05 established that redistributing subsets is expressly permitted under CC BY 4.0 and that
attendees may keep them permanently; ticket 19 confirmed the camera topic is cleared, so this is
a pure size-and-logistics question, not a rights one. Attribution travels with the subset.

One thing worth doing early regardless of the answer: **take a pinned local copy of all 16 MCAPs
with checksums**, since the published distribution is a Drive folder the publisher can change at
any time. That is cheap insurance, not a deadline.
