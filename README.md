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

Large viewer binaries, recordings, containers, generated bundles, and runtime evidence are release
inputs. Kit assembly includes these inputs and verifies their hashes. Keep them out of Git.
