# Participant package target

`participant/` is the Git-buildable `civ-workshop` package. It provides `civ` with
`doctor`, `inspect`, `sample`, `detect`, `clip`, `score`, `report`, and
`submission-init`. Its build copies the participant module allowlist and packaged
submission templates into a temporary uv-build project. The repository root
continues to build the organizer package.

Install the participant target from `main`:

```sh
uv tool install --python 3.12 "git+https://github.com/Forerunner2012/civ2026-data-hackathon.git@main#subdirectory=participant"
uv tool update-shell
```

Run these in native Windows AMD64 PowerShell or a native Linux AMD64 shell. WSL2 is an
optional way to use the Linux version on Windows. You need Git and uv for this connected
Git installation, plus CPython 3.10, 3.11 or 3.12. The command selects the recommended
Python 3.12 environment. uv installs the package dependencies automatically.

Restart your shell after PATH setup. From the workshop kit root, run `civ --help` and
`civ doctor --workspace working --bag data/YOUR-SIGNALS.mcap --offline-kit .`, using an
existing writable workspace and the supplied recording path. The default pure-MCAP
profile needs no ROS installation, Docker, Hyper-V, VM or administrator access.
See [runtime requirements and qualification](../docs/runtime-requirements.md) for
optional workflows and the distinction between intended and verified support.

Authorized Git access is required while the repository is private. If HTTPS access is
not configured, use an already authorized SSH source:

```text
uv tool install --python 3.12 "git+ssh://git@github.com/Forerunner2012/civ2026-data-hackathon.git@main#subdirectory=participant"
```

Do not put credentials in the command or install the organizer package from the repository root.

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


## Local wheel backup

Use the participant wheel and matching dependency wheels supplied for your OS, architecture
and Python version. Have uv and compatible Python available before going offline. From the
backup directory, run:

```text
uv tool install --offline --no-index --no-python-downloads --python 3.12 --find-links . ./civ_workshop-0.1.0-py3-none-any.whl
```

The filename above matches the current package version. Use the filename supplied with your
backup if the version changes. A participant wheel alone does not include dependency wheels
or Python. Frozen wheel recovery and moving-main updates have different source identities.
For resolver options, see the [uv CLI reference](https://docs.astral.sh/uv/reference/cli/).
