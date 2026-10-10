# Contributing

This guide covers open-source contributions that add code capabilities. To adapt a session with existing tools, follow [Make it your own](MAKE-IT-YOUR-OWN.md).

## Check EventSpec first

Before proposing code, check whether existing EventSpec signal bindings, derivations, conditions, timing rules, and evidence rules express the need. Follow the [EventSpec rules](docs/phase2/eventspec-cel-and-derive.md). If they do, adapt the session without adding a runtime capability.

## Agree on a bounded change

Use the [issue-tracker instructions](docs/agents/issue-tracker.md) to describe the missing behavior in a GitHub issue. Identify the module that owns the behavior, then agree on a small extension and its acceptance checks before implementation.

## Add a synthetic example and checks

Add a synthetic example that exercises the new capability and meaningful regression checks. From the repository root, run `uv sync` to install the organizer project, then run `uv run pytest`. For handoff-site changes, follow the [site development guide](handoff-site/README.md) to run `npm ci`, `npm run test`, and `npm run lint`. Do not commit recordings, actual labels, private paths, or credentials.

## Keep participant contracts stable

Preserve the participant contract and the metadata-only submission boundary. If a capability needs a contract change, agree on that design separately before implementation. Keep full-truth labels and review records organizer-only.
