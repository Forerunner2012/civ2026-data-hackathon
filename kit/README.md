# CIV 2026 offline attendee kit

## Start here

Investigate an incomplete report of vehicle behaviour. Inspect the recordings, write an EventSpec, and test your reasoning on a different recording. Check the evidence, explain one failure, and recommend a next action. Build a reproducible metadata-only bundle. Recordings and evidence clips stay local.

1. Open `site/index.html` for the static participant page. It does not show live room state.
2. Open [setup and recovery](docs/setup.md) to install the participant CLI and check recovery requirements.
3. Follow the [QuickStart](docs/quickstart.md) from `civ doctor` through `submission.zip`.
4. Try the optional [external-point exercise](docs/extension.md) after reproducing the core workflow.
5. Keep kit inputs read-only. Work in `working/` or another participant-owned directory.

Organizers are encouraged to share complete source-bound practice labels in the same space as participant kits, at a time they choose. These labels support learning and self-evaluation, but development metrics do not guarantee sealed-evaluation results; evaluation truth remains organizer-only.

Paths on this page are relative to the unpacked kit root. The [runtime requirements](docs/runtime-requirements.md) separate intended support from completed execution and lists optional tools.

## Viewer reference

Use the [viewer guide](viewer/README.md) for pinned versions, platform files, upstream references, and checksum checks. Viewer availability does not qualify a CLI platform. Use the runtime route confirmed for your session.

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
