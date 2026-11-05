# Data Hackathon CIV 2026

> Historical planning. Follow the [archive index](../README.md) for current guides and record boundaries.

## Identified goals

- Make it like a workshop / data handling crash course for data in general with differetn sensors typed data mixed
  - Inspired from <https://www.aihero.dev/workshops/ai-coding-crash-course>
  - Have reflexion with data extraction, collection, triage, storage, exploitation at the age of Agentic workflows
  - Thinks of Strategic & Tactical scope regarding data usage
- Run in the ROS2 ecosystem
  - Rosbag
  - Use OSS tools with OSS tools (local as possible), like Plotjugglerv4, MCAP format for storage, MCAP CLI for filtering or operations, ...
  - Docker for container resolving heavy burden on isolation & dependencies (if we use pre-packaged images)
- Capture the same logic than the CIV2025 with Heex: data extraction, collection and annotations at the edge, for collection than full upload. But here we cannot use Heex. So we need to substitue Heex here.

## Inspiration sources to use

### Raw notes on CIV2025 Hackathon

#### Main goals

Capture and experience with Heex the keys steps of a data pipeline: data extraction, collection and annotations at the edge, for collection than full upload.

-> Smart Data extraction & triage
Heex Solution can not be used.

```txt
A lot of the pain points I heard for the last point are fundamentally data and tooling problems: finding the right evidence when something goes wrong, turning hours of bags into minutes of insight, and keeping a tight learn→fix→validate loop.
That’s exactly where the #SmartData approach of Heex Technologies helps with an event-driven architecture for edge-first, craftable, modifiable (via OTA updates), and repeatable data pipelines.
```

#### EXternal resources on CIV2025 Hackathon

- Main sources
  - Smart-Data Hackathon v2
    - Organizer Page: `<data-root>/notes/Smart-Data Hackathon v2 - Organizer Page.md`
    - Participant Main Session: `<data-root>/notes/Smart-Data Hackathon v2 - Participant Main Session.md`
  - Correction with full automotion (no longer actionnable as Heex is offline): `<data-root>/samples`
  - Dataset from Tokyo University: `<data-root>/notes/Internal Notes on Dataset from Tokyo University.md`

- Second tier
  - Mail for Hackathon + CIV 2025 invite: `<data-root>/notes/CIV2025 - Mail for Hackathon + CIV 2025 invite.md`
  - URT-Kashiwa Smart-Data [Hackathon | Hands-on] (v2) Session [Maintained] section in `<data-root>/notes/Demonstrators.md`
  - Smart-Data Hackathon - Getting Heex replay with Tier4+Autoware custom messages: `<data-root>/notes/Smart-Data Hackathon - Getting replay with custom messages.md`
  - Smart-Data Hackathon v2 Participants’ Feedback: `<data-root>/notes/Smart-Data Hackathon - Participants’ Feedback.md`
  - Smart-Data Hackathon v2 - Participant Preparation Session: `<data-root>/notes/Smart-Data Hackathon v2 - Participant Preparation.md`
  - Upgrade from v1 to v2: `<data-root>/notes/Smart-Data Hackathon v2 - Upgrading effort from v1.md`
- Other Quickstarts

### Scoping for Dataviz and Data QUality for actionable results

datacraft is a company that organize hackathons. their vision is relevant for this new cv 2026 hackathon:

```txt
datacraft conçoit et anime des challenges pour sensibiliser, former et engager les collaborateurs autour d’une thématique Data ou IA, en associant apprentissage et mise en pratique sur des cas réels à travers un format alliant :
Une alternance d’apports théoriques, de quiz interactifs et d’ateliers pratiques.
Une compétition en équipes autour de challenges concrets inspirés du quotidien afin d’identifier l’impact de la data et de l’IA sur vos métiers
Thématiques possibles

Topics:
Data Quality
Data Gouvernance
IA Générative et prompt engineering
Data Visualisation MLOps et industrialisation de l’IA Éthique et IA responsable
```

### Twists possibles

#### Agentic Twist

Depending on the guidance, we see two subject to address: robotics, edge, AI agents, simulation, logs, and real engineering pain, either advanced visualization with dataviz for edge devices and robots or an interactive interface in the form of a video game.

AgentOps Black Box
It hits AI agents, MCP, observability, evaluation, governance, DevOps, and enterprise adoption. It is technically deep but still demoable.
This is the strongest overall concept because it synthesizes observability, evaluation, governance, debugging, and demo impact.

Why it feels inevitable: every serious agent system will need traceability, replay, and regression testing.
> Sentry for AI agents
as physical AI scales and ROS2 gets adopted
