# CIV 2026 data hackathon

This repository builds the offline attendee kit, participant-safe website, command-line workflow,
and organizer operations for the CIV 2026 Data Detective hackathon.

## Start here

- **Attending the hackathon:** follow the [QuickStart](docs/quickstart.md) from the root of the
  unpacked kit. It is the shortest path from environment check to a submission bundle.
- **Using an assembled offline kit:** open `site/index.html`, then read the kit's `README.md` for
  platform, viewer, fallback, and container details.
- **Developing this repository:** read [GLOSSARY.md](GLOSSARY.md) and
  [docs/agents/domain.md](docs/agents/domain.md), then use `uv sync` and `uv run pytest`.
- **Working on an issue:** follow [docs/agents/issue-tracker.md](docs/agents/issue-tracker.md).

## Reference sections

| Concern | Reference |
| --- | --- |
| First successful attendee run | [QuickStart](docs/quickstart.md) |
| Attendee kit operation and viewers | [kit/README.md](kit/README.md) |
| EventSpec contract and examples | [Phase 2 stable contracts](docs/phase2/stable-contracts-and-compatibility.md) |
| Participant kit inventory | [Phase 4 inventory](docs/phase4/participant-kit-inventory.md) |
| Release and workstation evidence | [Phase 5 release freeze](docs/phase5/release-freeze.md) |
| Website development | [handoff-site/README.md](handoff-site/README.md) |
| Adapt an existing session | [Make it your own](MAKE-IT-YOUR-OWN.md) and [session settings](docs/session-settings.md) |
| Contribute a new code capability | [CONTRIBUTING.md](CONTRIBUTING.md) |

Large viewer binaries, recordings, containers, generated bundles, and runtime evidence are release
inputs. Kit assembly includes these inputs and verifies their hashes. Keep them out of Git.

## A possible next format

This material can support other challenges in robotics data analysis, including AI-assisted work with data from edge systems. One possible format runs for two or three months, releases new dataset chunks progressively, and repeats evaluation at each release. Organizers would define the schedule, data permissions, labels, and evaluation rules for that format.

## Credits

Breakout-session suggestions came from [Powei Liao](https://www.linkedin.com/in/powei-liao/), [Dr. Matthieu Carré](https://www.linkedin.com/in/matthieucarreutc/), and Bo Qian.

We thank Tsukada Laboratory, [Prof. Manabu Tsukada](https://www.linkedin.com/in/manabutsukada/), and [Ehsan Javanmardi](https://www.linkedin.com/in/ehsan-javanmardi-7326b6a8/).

We also thank the CIV committee, including [Arnaud de La Fortelle](https://www.linkedin.com/in/arnaud-de-la-fortelle/), and the [CIV summer school](https://civ-summerschool.org/).

Development used [Orca](https://github.com/stablyai/orca) for agent orchestration and unattended remote work.

See [kit/ATTRIBUTION.md](kit/ATTRIBUTION.md) for the dataset attribution, modification notes, and
third-party notices. The file links to the [URT-Kashiwa source](https://github.com/tlab-wide/URT-Kashiwa)
and the [CC BY 4.0 license](https://creativecommons.org/licenses/by/4.0/).
