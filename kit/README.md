# CIV 2026 offline attendee kit

## Start here

1. Open `site/index.html` for the participant page and the room's current instructions.
2. Follow `docs/quickstart.md` for the ordered command path from `civ doctor` to
   `submission.zip`.
3. Keep all kit inputs read only and do your work in `working/` or another participant-owned
   directory.

The QuickStart is the operational path. The reference sections below explain platform choices,
viewers, fallback material, safety boundaries, and the container in more detail.

## Viewer reference

The pinned offline viewers are under `viewer/<platform>/`; read `viewer/README.md` before running
one and verify its file against `checksums/SHA256SUMS`. The kit carries:

- PlotJuggler `3.999.3` for Windows amd64 and Linux amd64;
- Lichtblick `1.28.0` for Windows amd64, Linux amd64, and macOS universal.

PlotJuggler does not publish a macOS binary for this pinned release. macOS attendees can use the
supplied Lichtblick build for visual inspection; the qualified CLI/container route remains the one
stated by the event organizers.

Upstream project and release references:

- PlotJuggler: <https://github.com/PlotJuggler/PlotJuggler> ·
  <https://github.com/PlotJuggler/PlotJuggler/releases>
- Lichtblick: <https://github.com/lichtblick-suite/lichtblick> ·
  <https://github.com/lichtblick-suite/lichtblick/releases>

On a connected machine, the official no-install Lichtblick app is available at
<https://lichtblick-suite.github.io/lichtblick/>. The core QuickStart does not depend on it.

## Layout and context reference

Use `layouts/lichtblick-kashiwa-right-turn.json` or
`layouts/lichtblick-reims-left-turn.json` with Lichtblick. Open one `data/*-signals.mcap` and its
same-source companion from `context/kashiwa/` or `context/reims/` in one session. Matching source
identity and time bounds put them on one timeline.

PlotJuggler uses the corresponding `*.pj4.xml` layout for signal manipulation. Camera context is
optional and is never an input to the required detector.

## Fallback reference

If a laptop, container, or viewer fails, pair with another participant. While it is repaired,
`fallback/kashiwa` and `fallback/reims` keep the analysis moving:

- `tables/*.csv` are full-rate, long-form signal tables;
- `plots/*.svg` are neutral overviews, not answer keys;
- `clips/*.mcap` are fixed-position, non-answer windows.

Fallback work supports reasoning; the paired primary path still produces the scored EventSpec,
events, metrics, report, and metadata submission.

## Data and submission boundary

Camera-context MCAPs are viewing inputs only. Context, frames, signal MCAPs, and evidence clips
remain outside the submission bundle. Before use, verify `checksums/ASSEMBLY-SHA256SUMS`. Do not
rename or edit kit inputs.

The two recovered Kashiwa recordings retain the caveat in `participant-kit.json`: structural
recovery made them readable but cannot prove that no records were lost to truncation.

## Runtime reference

The participant runtime at `runtime/source` exposes only `doctor`, `inspect`, `sample`, `detect`,
`clip`, `score`, `report`, and `submission-init`. Private intake, cohort scoring, product
construction, and held-back preparation modules are absent.

From `runtime/source`, set `UV_CACHE_DIR` to `../../offline/uv-cache`, then run:

```text
uv sync --frozen --offline --no-dev
```

The pinned Linux container path is self-contained:

```text
docker load --input container/civ-phase4-attendee-candidate-558e85c.tar
docker run --rm --read-only --network none --mount type=bind,src=KIT_ROOT,dst=/kit,readonly --mount type=bind,src=WORK_ROOT,dst=/work civ-phase4:attendee-candidate-558e85c doctor --workspace /work --bag /kit/data/KSH-64ac27cd029b-signals.mcap --offline-kit /kit
```

Replace `KIT_ROOT` and `WORK_ROOT` with absolute host directories; only `WORK_ROOT` is writable.
Docker exposes no GPU unless explicitly requested, and this command requests none.
