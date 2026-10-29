# CIV 2026 data hackathon

Run a data hackathon where participants inspect robotics recordings, write YAML EventSpecs,
review detected intervals and build a reproducible metadata-only bundle. This repository contains
the reusable command-line workflow, offline attendee-kit builder, participant-safe website and
organizer procedures developed for CIV 2026.

## Start here

- **Participants:** follow the [QuickStart](docs/quickstart.md) from the root of the supplied kit.
  Use the setup and runtime inputs qualified for your session.
- **Organizers:** follow the [organizer guide](docs/organizers/README.md) to prepare data permissions,
  human label review, kit construction, facilitation and evaluation.
- **Contributors:** follow [CONTRIBUTING.md](CONTRIBUTING.md) to develop a bounded code capability
  and run the project checks. Adapt a session with existing tools through
  [Make it your own](MAKE-IT-YOUR-OWN.md).
- **Using an assembled kit:** open `site/index.html`, then read its `README.md` for local paths,
  viewers and qualified recovery options.

Each session records its own recording/image permissions, platform qualification and release
approval. CIV 2026 evidence applies to the exact original artifacts and recorded scope.

## References

| Concern | Reference |
| --- | --- |
| Participant workflow | [QuickStart](docs/quickstart.md) and [kit guide](kit/README.md) |
| Participant contract and scoring | [Contracts](docs/reference/participant-contracts.md) and [scoring](docs/reference/scoring.md) |
| EventSpec expressions and external resources | [EventSpec rules](docs/phase2/eventspec-cel-and-derive.md) and [resource reference](docs/phase2/eventspec-resources.md) |
| Session preparation, kit construction and release checks | [Organizer guide](docs/organizers/README.md) |
| Website development | [Site guide](handoff-site/README.md) |
| Adapt existing session settings | [Make it your own](MAKE-IT-YOUR-OWN.md) and [settings reference](docs/session-settings.md) |
| History | [Implementation, live event, feedback, and rework](docs/history/civ-2026.md) |

Recordings, imagery, viewer binaries, containers, generated bundles and runtime evidence are
separate release inputs. Kit assembly verifies their identities. Keep them out of Git.

The root [LICENSE](LICENSE) covers eligible original contributions, and [THIRD-PARTY-NOTICES.md](THIRD-PARTY-NOTICES.md)
and [kit/ATTRIBUTION.md](kit/ATTRIBUTION.md) identify the separate terms for third-party materials and datasets.

## Credits

Breakout-session suggestions came from [Powei Liao](https://www.linkedin.com/in/powei-liao/), [Dr. Matthieu Carré](https://www.linkedin.com/in/matthieucarreutc/), and Bo Qian.

We thank Tsukada Laboratory, [Prof. Manabu Tsukada](https://www.linkedin.com/in/manabutsukada/), and [Ehsan Javanmardi](https://www.linkedin.com/in/ehsan-javanmardi-7326b6a8/).

We also thank the CIV committee, including [Arnaud de La Fortelle](https://www.linkedin.com/in/arnaud-de-la-fortelle/), and the [CIV summer school](https://civ-summerschool.org/).

Development used [Orca](https://github.com/stablyai/orca) for agent orchestration and unattended remote work.
