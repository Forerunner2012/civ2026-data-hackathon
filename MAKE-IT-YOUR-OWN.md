# Make it your own

Use this guide to adapt a session with the tools and contracts already in the repository. For a new code capability, use [CONTRIBUTING.md](CONTRIBUTING.md).

For participant operation, start with the [kit README](kit/README.md) and [QuickStart](docs/quickstart.md). At the repository root, `uv sync` prepares the organizer project. The participant-only CLI has a separate install target under `participant/`. Follow the [participant package instructions](participant/README.md).

## Adapt a session

1. Check the terms for each recording. Record its source, attribution, applicable license or permission, and modification limits. Keep recordings, evidence clips, and actual labels outside Git and participant submissions. Check distribution permission separately before adding a recording to a kit or sharing it.
2. Inventory each recording with `civ inspect` and `civ sample`. Record topic names, field paths, units, and timestamp bounds.
3. Copy an existing EventSpec and update its signal bindings, derivations, timing rules, conditions, and evidence topics. Follow the [EventSpec rules](docs/phase2/eventspec-cel-and-derive.md), inspect the [schema](schemas/civ.eventspec.v1.schema.json), and run the spec with `--dry-run` before reviewing event meaning against evidence.
4. Keep participant practice labels separate from organizer-only full truth. Participants use `civ score --labels` with a supplied source-bound reference, or `civ score` without labels to record unevaluated metrics and continue packaging. Organizer cohort scoring uses `civ score-batch --plan` with reviewed truth bound to each track and exact recording. Follow [Score a full cohort](docs/organizers/cohort-scoring.md).
5. Resolve a private evaluation-plan profile with `civ prepare-session`, then use the saved plan for intake and scoring. Configure the session identity, roster, cutoff, assignments, and supported points policy there. The [session settings reference](docs/session-settings.md) identifies the separate site and live-schedule settings.
6. Update participant instructions and kit references. Keep metadata-only submissions intact, and keep recordings and evidence clips local.
7. Run the checks for the changed contracts and record fresh session acceptance evidence. A passing check for the current session does not qualify a new dataset or kit.

## Example session

Imagine a session on 2027-02-18 at UTC+01:00 with fictional recordings named `harbor` and `campus`. These names and date identify no real inputs and grant no data rights. Set a session cutoff with an explicit offset through `civ prepare-session --cutoff`. Bind actual qualified products and references in the profile. A plan does not extend dataset support in product generation, reference building, or kit assembly. New datasets or unsupported matching behavior need code and new qualification; supported weights, allocations, and replay limits are plan settings. See [kit inventory](src/civ_workshop/kit_inventory.py), [kit assembly](src/civ_workshop/kit_assembly.py), and [scoring rules](docs/reference/scoring.md).
