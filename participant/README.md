# Participant package target

`participant/` builds the Git-installable `civ-workshop` package. It exposes only `doctor`, `inspect`, `sample`, `detect`, `clip`, `score`, `report` and `submission-init`. Use the [participant setup guide](../docs/setup.md) for connected installation, PATH, updates, optional constraints and recovery from matching wheels. Follow the [QuickStart](../docs/quickstart.md) after installation.

The build copies the participant module allowlist and packaged submission templates into a temporary uv-build project. The repository root builds the organizer package. The Git target resolves dependencies from participant metadata, not the repository's `uv.lock`. Qualification records source/dependency identity separately from frozen wheel backups; see [runtime requirements](../docs/runtime-requirements.md).

For a local distribution check, run `uv build participant --out-dir tmp/participant-dist`. The emitted sdist is a standalone participant uv-build project; it builds its wheel without the parent repository. Generated distributions stay outside Git.
