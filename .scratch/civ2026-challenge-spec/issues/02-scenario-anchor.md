# Which scenario anchors the challenge?

Type: grilling
Status: resolved

## Question

What kind of event do teams investigate in the Kashiwa bags — and how much freedom do they
have to choose it?

## Answer

**Unprotected right turns (URT)** — the purpose the dataset was collected for. Teams may also
catch other event types, as happened at the previous hackathon.

The pedagogical emphasis is on **creativity in how teams express and capture the scenario using
the OSS toolchain**, not on inventing a different event class. The interesting variation is in
signal choice, derived features, temporal composition and evidence framing — the same anchor
event reached by materially different routes.

Consequences carried forward:

- Scoring has to stay objective against a fixed class — resolved in ticket 03.
- "Other event types" needs a home in the bonus track — also ticket 03.
- The reference EventSpec sketched in `exploration/exploration-notes-INBOX.md`
  (`acceleration lt -3.0` AND `speed gt 2.0`) is a *hard-braking* example, not a URT one. A URT
  reference detector still has to be written; ticket 09 produces the first one.
