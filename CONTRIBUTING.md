# Contributing

This guide covers open-source contributions that add code capabilities. To adapt a session with existing tools, follow [Make it your own](MAKE-IT-YOUR-OWN.md).

## Check EventSpec first

Before proposing code, check whether existing EventSpec signal bindings, derivations, conditions, timing rules, and evidence rules express the need. Follow the [EventSpec rules](docs/phase2/eventspec-cel-and-derive.md). If they do, adapt the session without adding a runtime capability.

## Agree on a bounded change

Use the [issue-tracker instructions](docs/agents/issue-tracker.md) to describe the missing behavior in a GitHub issue. Identify the module that owns the behavior, then agree on a small extension and its acceptance checks before implementation.

## Set up and check the change

From the repository root, synchronize the existing Python project and run its checks:

```powershell
uv sync
uv run ruff check src tests
uv run mypy src
uv run pytest
```

Add a synthetic example and meaningful regression checks for a new capability. Use permitted local
fixtures; keep recordings, actual labels, private paths, credentials and generated artifacts out
of commits.

For website changes, work in `handoff-site/` and follow the
[site development guide](handoff-site/README.md) for `npm ci`, `npm run test` and `npm run lint`.
Participant platform/install qualification is separate from this contributor project setup.

## Optional onboarding check

For an authorized chunk folder or a direct MCAP path, run this command:

```powershell
uv run python scripts/onboarding_check.py `
  --source AUTHORIZED_CHUNK_OR_MCAP `
  --eventspec MATCHING_EVENTSPEC `
  --labels REVIEWED_PRACTICE_PACK `
  --output FRESH_OUTPUT_FOLDER
```

The folder must contain exactly one top-level MCAP file. Pass the MCAP path directly when a folder contains more than one. The helper calls the detector and scorer functions used by `civ detect` and `civ score --labels`. It validates the pack and source hash. Choose an authorized source, a matching EventSpec, and a complete human-reviewed practice pack before you run the helper. The helper does not establish authorization, human review, or label coverage. It writes to a new output folder outside the input folders.

## Keep documentation consistent

Use [GLOSSARY.md](GLOSSARY.md) for the repository's domain vocabulary. Canonical Markdown owns
workflow commands and rules; the website summarizes them, and the kit receives exact guide copies
through its inventory/assembly process. Update the canonical page and affected summaries together,
validate links and commands, and leave generated kit copies to the assembler. Preserve historical
acceptance evidence within its recorded scope.

The [agent conventions](AGENTS.md) and [issue-tracker guide](docs/agents/issue-tracker.md) describe
repository workflows when needed. Contributing a code capability does not require Orca or another
agent tool.

## Keep participant contracts stable

Preserve the participant contract and the metadata-only submission boundary. If a capability needs a contract change, agree on that design separately before implementation. Keep full-truth labels and review records organizer-only.
