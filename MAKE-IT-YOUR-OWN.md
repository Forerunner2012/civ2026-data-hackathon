# Make it your own

Use this guide to adapt a session with the tools and contracts already in the repository. For a new code capability, use [CONTRIBUTING.md](CONTRIBUTING.md).

For participant operation, start with the [kit README](kit/README.md) and [QuickStart](docs/quickstart.md). At the repository root, `uv sync` prepares the organizer project. The participant-only CLI has a separate install target under `participant/`. Follow the [participant package instructions](participant/README.md).

## Adapt a session

1. Check the terms for each recording. Record its source, attribution, applicable license or permission, and modification limits. Keep recordings, evidence clips, and actual labels outside Git and participant submissions. Check distribution permission separately before adding a recording to a kit or sharing it.
2. Inventory each recording with `civ inspect` and `civ sample`. Record topic names, field paths, units, and timestamp bounds.
3. Copy an existing EventSpec and update its signal bindings, derivations, timing rules, conditions, and evidence topics. Follow the [EventSpec rules](docs/phase2/eventspec-cel-and-derive.md), inspect the [schema](schemas/civ.eventspec.v1.schema.json), and run the spec with `--dry-run` before reviewing event meaning against evidence.
4. Keep participant practice labels separate from organizer-only full truth. Use `civ score --labels` with its existing scoring-reference contract in [score_reference.py](src/civ_workshop/score_reference.py). Organizer cohort scoring uses `civ score-batch --labels` and the sealed [organizer label-pack contract](docs/phase3/organizer-label-packs.md), implemented in [label_packs.py](src/civ_workshop/label_packs.py). The current batch loader accepts exactly `kashiwa` and `reims`.
5. Change values at their current source locations. Use the [session settings reference](docs/session-settings.md). The repository has no central session settings file or new configuration schema.
6. Update participant instructions and kit references. Keep metadata-only submissions intact, and keep recordings and evidence clips local.
7. Run the checks for the changed contracts and record fresh session acceptance evidence. A passing check for the current session does not qualify a new dataset or kit.

## Example session

Imagine a session on 2027-02-18 at UTC+01:00 with fictional recordings named `harbor` and `campus`. These fictional names and date do not identify real recordings or grant rights to use them. The current batch and kit code does not accept those dataset names. Adding dataset membership, changing scoring policy, or changing kit composition requires code and new acceptance evidence. See [batch label mapping](src/civ_workshop/batch.py), [kit inventory](src/civ_workshop/kit_inventory.py), [kit assembly](src/civ_workshop/kit_assembly.py), and [scoring rules](src/civ_workshop/score_reference.py).
