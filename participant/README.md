# Participant package target

`participant/` is the Git-buildable `civ-workshop` package. It provides `civ` with
`doctor`, `inspect`, `sample`, `detect`, `clip`, `score`, `report`, and
`submission-init`. Its build copies the participant module allowlist and packaged
submission templates into a temporary uv-build project. The repository root
continues to build the organizer package.

After this target reaches `main`, the intended connected install is:

```sh
uv tool install --python 3.12 "git+https://github.com/Forerunner2012/civ2026-data-hackathon.git@main#subdirectory=participant"
uv tool update-shell
```

Run these inside WSL2 for Windows amd64, or directly on Linux amd64, with Git, uv,
and compatible Python available. Restart the shell after PATH setup, then from
the kit root run `civ --help` and `civ doctor`. Authorized Git access is required
while the repository is private. GitHub-main availability and fresh WSL2/Linux
shell checks require post-merge qualification; development-host candidate tests
do not establish those gates.

For normal branch-following updates:

```sh
uv tool upgrade civ-workshop
```

Use `uv tool install` with the desired source to replace an existing source,
including an organizer-root installation of the same package. uv handles the
installed tool; no default `--force` is needed.

The tool resolver uses the participant metadata, not the repository's `uv.lock`.
The Git route intentionally follows compatible current dependencies. A frozen
wheel backup can have a different source and dependency identity. Record the
resolved Git commit, package/dependency versions, uv version, and Python patch in
qualification evidence outside submissions.

If an installation used a reviewed constraints file, `uv tool upgrade` retains
its saved values. Editing that file does not refresh the installed constraints.
After validating new values against the current participant metadata and project
lock, re-read them through uv's native install command:

```sh
uv tool install --python 3.12 --reinstall --upgrade --constraint participant-constraints.txt "git+https://github.com/Forerunner2012/civ2026-data-hackathon.git@main#subdirectory=participant"
```

`participant-constraints.txt` is an optional local qualification input, not a
shipped pin set. Do not permanently attach moving `main` to historical wheel
pins. The native update behavior was checked against a disposable remote with
two commits and a changed dependency floor; production `main` was untouched.
See [uv tool sources](https://docs.astral.sh/uv/guides/tools/#requesting-different-sources)
and [uv install options](https://docs.astral.sh/uv/reference/cli/#uv-tool-install).

For a local distribution check, run `uv build participant --out-dir tmp/participant-dist`.
The emitted sdist is a standalone participant uv-build project and can build its
wheel without the parent repository. Generated distributions stay outside Git.
