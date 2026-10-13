# Workshop presentations

Maintain the editable [briefing](briefing.html) and [submission checklist](submission-checklist.html) here. Matt reviews the editorial content. The briefing has 13 slides for a 15–20-minute introduction; the separate checklist covers the end-of-hackathon submission. Both use a 1920 by 1080 canvas and produce one full-slide image per 16:9 PPTX slide.

## Edit the sources

Edit each `data-slide` section in the HTML. Keep the accepted participant introduction and Inspect → Detect → Check evidence → Submit progression. Use the [quickstart](../quickstart.md), [setup guide](../setup.md), [participant contracts](../reference/participant-contracts.md) and [scoring reference](../reference/scoring.md) for facts. Avoid adding command inventories to the slides.

`theme.css` follows the main hackathon site's colors and typography. `slides.js` provides local slide selection and arrow-key progression. `size-chart.js` contains only the selected-parent size accounting, not the event-count or time-split datasets.

The HTML sources display placeholders until the prepared illustration inputs are supplied to the renderer. They are maintained source, not a claim that those illustrations or labels ship in the repository.

## Prepare the illustrated warm-up

Use the same authorized warm-up recording, complete matching practice pack and EventSpec throughout. Keep input files read-only. Create participant-owned working outputs separately and measure a single refinement before writing its result into the talk. Preserve a private receipt linking source, spec, labels, outputs and illustration hashes.

The prepared example changes minimum duration from 0.5 s to 3 s. Its local measured result removes the false positive while retaining the three reviewed turns. This result belongs to that warm-up, not other recordings or official evaluation. Practice metrics are diagnostic.

The illustration manifest is a local rendering input with `source_sha256`, `label_pack_sha256`, `assets` and `evidence`. Each asset has an absolute local `path` and its verified `sha256`. Keep this manifest and its source paths outside Git. Required PNG roles are:

- `steering-trace.png`
- `false-positive-context.png`
- `detected-intervals.png`
- `practice-comparison.png`
- `refinement-comparison.png`

Supply measured text under `evidence.readiness`, `evidence.baseline-metrics` and `evidence.refined-metrics` and `evidence.submission`. The submission text must come from a validated metadata-only ZIP and its actual hash. The renderer rejects missing or changed inputs. The current preparation uses a CLI-derived scientific signal plot; it does not claim a native viewer screenshot. The supplied viewer remains available through the kit quickstart. Review this illustration choice with the finished deck.

Do not disclose development or sealed event counts, collection totals, split percentages or proportional split widths. Only the warm-up's three reviewed turns are shown. Keep hidden numbers out of source, notes, assets, tooltips and accessible text. The file-size diagram is a distinct byte-size measurement; it keeps its labeled units and separate camera-context scope.

## Generate locally

These are organizer presentation tools, not participant runtime dependencies. Use Node 22 or newer and an installed Chromium browser, plus uv for the Python helpers. No browser download or host configuration is part of these commands. The checked route used Windows Edge with Node 24; other render hosts remain unverified.

From the repository root, first prepare the project environment for the shared artifact and kit checks:

```text
uv sync --locked
```

Choose a new output directory under the ignored `tmp/` directory. Provide the actual reviewed asset manifest and installed browser path:

```text
node scripts/render-presentations.mjs --sources docs/presentations --browser <installed-browser-path> --assets <prepared-assets-manifest> --output tmp/presentations
uv run --no-project --with python-pptx==1.0.2 -- python scripts/assemble-presentations.py --input tmp/presentations --output tmp/presentations
uv run python scripts/check-presentations.py --input tmp/presentations
```

The standalone assembler uses the tested `python-pptx` version without creating another project. The checker uses the shared organizer module and therefore runs in project mode. Rendering refuses an existing output directory, verifies asset hashes, checks clipping and footer collisions, and detects external page-asset requests. Assembly refuses existing decks and sets both geometry and `screen16x9` metadata explicitly. The checker verifies exact image identity, deck hashes, counts and full-slide geometry.

Inspect every captured slide for legibility, source accuracy and visual corruption before approving the decks. The structural check alone cannot detect every raster defect. Keep the render and assembly manifests alongside generated outputs. Repeated render images should be compared by hash. PPTX ZIP metadata can vary between builds; do not claim byte identity without measuring it.

## Include verified decks in a kit

When the generated pair is reviewed for the approved kit, add `--presentations-root <verified-output-directory>` to the existing `uv run -m civ_workshop.kit_assembly assemble` command. Other required kit inputs remain unchanged. The default assembly has no presentation dependency.

The builder verifies the pair before creating the kit output, copies only `briefing.pptx` and `submission-checklist.pptx` into `presentations/`, and writes a small retrieval README. If the assembled brief exists, it gets relative links to those included files. File records, component sizes and assembly checksums cover the copies. The maintained source brief and private preparation manifests remain untouched.

Do not add website download links until an approved artifact exists at the stated location. Repository source links do not establish kit or hosted-download availability. Actual supplied-kit acceptance and release/publication decisions remain separate from synthetic assembly checks.

## Original materials

Preserve the original 20-slide briefing and one-slide checklist at [commit 728de9e](https://github.com/Forerunner2012/civ2026-data-hackathon/tree/728de9ead538cacf8cd576940c3b3f959a6fd444/.scratch). The maintenance decision is recorded in [issue #92](https://github.com/Forerunner2012/civ2026-data-hackathon/issues/92); [issue #106](https://github.com/Forerunner2012/civ2026-data-hackathon/issues/106) owns implementation and integration. Original assets and history remain intact. No publication or deployment follows from local generation.
