# CIV 2026 data hackathon

Inspect robotics recordings, write YAML EventSpecs, review detected intervals, and submit
reproducible results without bundling source data. Built for the CIV 2026 data hackathon,
this project includes a command-line workflow, an offline participant kit, a companion website,
and tools for organizers to prepare and score a session.

## Start here

| I want to | Start with |
| --- | --- |
| Take part in a session | [Participant quickstart](docs/quickstart.md) |
| Run a hackathon | [Organizer guide](docs/organizers/README.md) |
| Adapt it for another session | [Adapt a session](docs/organizers/adapt-session.md) |
| Contribute code or documentation | [Contributing](CONTRIBUTING.md) |

If you have an assembled kit, open `site/index.html` and its `README.md` for local paths,
viewers, and setup instructions. Use the inputs and runtime qualified for your session.

## Repository layout

| Directory | Purpose |
| --- | --- |
| [docs/](docs/README.md) | Participant guides, organizer procedures, reference, and project history. |
| [src/civ_workshop/](src/civ_workshop/) | Python CLI and analysis tools, with organizer review tools under `organizer/`. |
| [participant/](participant/README.md) | Package build target for the participant-only CLI. |
| [handoff-site/](handoff-site/README.md) | Companion website and its audience-specific builds. |
| [kit/](kit/README.md) | Offline kit templates, guide copies, and third-party notices. |
| [examples/](examples/README.md) | EventSpecs and point resources grouped by dataset. |
| [layouts/](layouts/README.md) | Lichtblick and PlotJuggler viewer layouts. |
| [practice-labels/](practice-labels/README.md) | Instructions for separately supplied practice references. |
| [schemas/](schemas/) | Versioned JSON schemas for analysis and organizer artifacts. |
| [scripts/](scripts/) | Onboarding and presentation helpers. |
| [tests/](tests/) | Automated checks and synthetic fixtures. |

Browse the [documentation index](docs/README.md) for contracts, scoring rules, and setup,
or read the [CIV 2026 history](docs/history/README.md) for the original implementation and event records.

Recordings and assembled kits are supplied separately. Keep recordings, imagery, viewer binaries,
containers, generated bundles, and runtime evidence out of Git. Each session needs its own
data permissions, runtime qualification, and release approval.

The root [LICENSE](LICENSE) covers eligible original contributions, and [THIRD-PARTY-NOTICES.md](THIRD-PARTY-NOTICES.md)
and [kit/ATTRIBUTION.md](kit/ATTRIBUTION.md) identify the separate terms for third-party materials and datasets.

## Credits

Breakout-session suggestions came from [Powei Liao](https://www.linkedin.com/in/powei-liao/), [Dr. Matthieu Carré](https://www.linkedin.com/in/matthieucarreutc/), and Bo Qian.

We thank Tsukada Laboratory, [Prof. Manabu Tsukada](https://www.linkedin.com/in/manabutsukada/), and [Ehsan Javanmardi](https://www.linkedin.com/in/ehsan-javanmardi-7326b6a8/).

We also thank the CIV committee, including [Arnaud de La Fortelle](https://www.linkedin.com/in/arnaud-de-la-fortelle/), and the [CIV summer school](https://civ-summerschool.org/).
