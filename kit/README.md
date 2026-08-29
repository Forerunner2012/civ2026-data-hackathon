# CIV 2026 offline attendee kit

Start with `site/index.html`. If the room page or internet is unavailable, this static page carries
the same participant wording and links to the printable desk material.

The primary path is the prepared container plus the `civ` command sequence shown on the page.
PlotJuggler 4 beta2 (`3.999.3`) and Lichtblick (`1.28.0`) are both pinned signal viewers. On a
connected machine, prefer the official no-install Lichtblick web app at
https://lichtblick-suite.github.io/lichtblick/; this avoids running an executable carried beside
the data. The pinned desktop artifacts remain in `viewer/` for the offline path. Verify them against
`checksums/SHA256SUMS` before running them.

Use `layouts/lichtblick-kashiwa-right-turn.json` or
`layouts/lichtblick-reims-left-turn.json` with Lichtblick. Their source layouts were visually
checked with one Kashiwa and one Reims participant MCAP. PlotJuggler uses the corresponding
`*.pj4.xml` layouts.

If a laptop or container fails, pair with another participant. While the environment is repaired,
`fallback/kashiwa` and `fallback/reims` keep the analysis moving without ROS or a viewer:

- `tables/*.csv` are full-rate, long-form signal tables. Open them in a spreadsheet, DuckDB,
  Polars, pandas, or another CSV-capable tool.
- `plots/*.svg` are neutral overviews, not answer keys.
- `clips/*.mcap` are fixed-position, non-answer windows for inspection or transfer testing.

Fallback work supports reasoning; the paired primary path still produces the scored EventSpec,
events, metrics, report, and metadata-only submission.

Before use, verify `checksums/ASSEMBLY-SHA256SUMS`. Do not rename or edit kit inputs. Work only in a
separate participant-owned directory. The two recovered Kashiwa recordings retain the caveat in
`participant-kit.json`: structural recovery made them readable but cannot prove no records were
lost to truncation.

The kit contains a participant-only runtime source at `runtime/source`. It exposes `doctor`,
`inspect`, `sample`, `detect`, `clip`, `score`, `report`, and `submission-init`; private intake,
cohort scoring, product construction, and held-back-data preparation modules are absent. From that
directory, set `UV_CACHE_DIR` to `../../offline/uv-cache` and run
`uv sync --frozen --offline --no-dev`.

The pinned Linux path is self-contained:

```text
docker load --input container/civ-phase4-attendee-candidate-558e85c.tar
docker run --rm --read-only --network none --mount type=bind,src=KIT_ROOT,dst=/kit,readonly --mount type=bind,src=WORK_ROOT,dst=/work civ-phase4:attendee-candidate-558e85c doctor --workspace /work --bag /kit/data/KSH-64ac27cd029b-signals.mcap --offline-kit /kit
```

Replace `KIT_ROOT` and `WORK_ROOT` with absolute host directories; only `WORK_ROOT` is writable.
Docker exposes no GPU unless one is explicitly requested, and this command requests none. Phase 5
will freeze event-hardware wrappers and physical SSD copies around these exact inputs.
