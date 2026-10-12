# CIV 2026 offline attendee kit

## Start here

Investigate an incomplete report of vehicle behaviour. Inspect the recordings, write an EventSpec, and test your reasoning on a different recording. Check the evidence, explain one failure, and recommend a next action. Start with the participant page and kit README, then follow the kit's `docs/quickstart.md`. Submit a reproducible metadata-only bundle. Recordings and evidence clips stay local.

1. Open `site/index.html` for the static participant page. It does not show live room state.
2. Open [setup and recovery](docs/setup.md) to install the participant CLI and check recovery requirements.
3. Follow the [QuickStart](docs/quickstart.md) from `civ doctor` through `submission.zip`.
4. Try the optional [external-point exercise](docs/extension.md) after reproducing the core workflow.
5. Keep kit inputs read-only. Work in `working/` or another participant-owned directory.

Paths on this page are relative to the unpacked kit root. The [runtime requirements](docs/runtime-requirements.md) separate intended support from completed execution and lists optional tools.

## Viewer reference

The pinned offline viewers are under `viewer/<platform>/`; read `viewer/README.md` before running one and verify its file against `checksums/SHA256SUMS`. The kit carries:

- PlotJuggler `3.999.3` for Windows amd64 and Linux amd64;
- Lichtblick `1.28.0` for Windows amd64, Linux amd64, and macOS universal.

PlotJuggler does not publish a macOS binary for this pinned release. macOS attendees can use the supplied Lichtblick build for visual inspection; the qualified CLI/container route remains the one stated by the event organizers.

Upstream project and release references:

- PlotJuggler: <https://github.com/PlotJuggler/PlotJuggler> ·
  <https://github.com/PlotJuggler/PlotJuggler/releases>
- Lichtblick: <https://github.com/lichtblick-suite/lichtblick> ·
  <https://github.com/lichtblick-suite/lichtblick/releases>

On a connected machine, the official no-install Lichtblick app is available at
<https://lichtblick-suite.github.io/lichtblick/>. The core QuickStart does not depend on it.

## Layout and context reference

Use `layouts/lichtblick-kashiwa-right-turn.json` or `layouts/lichtblick-reims-left-turn.json` with Lichtblick. Open one `data/*-signals.mcap` and its same-source companion from `context/kashiwa/` or `context/reims/` in one session. Matching source identity and time bounds put them on one timeline.

PlotJuggler uses the corresponding `*.pj4.xml` layout for signal manipulation. Camera context is optional and is never an input to the required detector.

## Fallback reference

If a laptop, container, or viewer fails, pair with another participant. While it is repaired, `fallback/kashiwa` and `fallback/reims` keep the analysis moving:

- `tables/*.csv` are full-rate, long-form signal tables;
- `plots/*.svg` are neutral overviews, not answer keys;
- `clips/*.mcap` are fixed-position, non-answer windows.

Fallback work supports reasoning; the paired primary path still produces the scored EventSpec, events, metrics, report, and metadata submission.

## Data and submission boundary

Camera-context MCAPs are viewing inputs only. Context, frames, signal MCAPs, and evidence clips remain outside the submission bundle. A v2 bundle may carry only bounded manifest-declared EventSpec resources, provenance, inert agent traces, and regression tests; intake never executes the latter two. Before use, verify `checksums/ASSEMBLY-SHA256SUMS`. Do not rename or edit kit inputs.

For dataset and tool attribution, modification notes, and third-party notices, see [`ATTRIBUTION.md`](ATTRIBUTION.md).

The two recovered Kashiwa recordings retain the caveat in `participant-kit.json`: structural recovery made them readable but cannot prove that no records were lost to truncation.

## Runtime reference

Use `docs/setup.md` for the current native CLI route. The commands below describe historical assembled source and optional container recovery. Docker and WSL2 are not prerequisites for the native CLI.

The participant runtime at `runtime/source` exposes only `doctor`, `inspect`, `sample`, `detect`, `clip`, `score`, `report`, and `submission-init`. Private intake, cohort scoring, product construction, and held-back preparation modules are absent.

From `runtime/source`, set `UV_CACHE_DIR` to `../../offline/uv-cache`, then run:

```text
uv sync --frozen --offline --no-dev
```

The pinned Linux container path is self-contained:

```text
docker load --input container/civ-phase4-attendee-candidate-558e85c.tar
docker run --rm --read-only --network none --mount type=bind,src=KIT_ROOT,dst=/kit,readonly --mount type=bind,src=WORK_ROOT,dst=/work civ-phase4:attendee-candidate-558e85c doctor --workspace /work --bag /kit/data/KSH-64ac27cd029b-signals.mcap --offline-kit /kit
```

Replace `KIT_ROOT` and `WORK_ROOT` with absolute host directories; only `WORK_ROOT` is writable. Docker exposes no GPU unless explicitly requested, and this command requests none.
