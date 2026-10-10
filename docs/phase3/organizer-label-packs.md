# Phase 3 organizer label packs

Status: **accepted for the Phase 3 product-to-truth binding gate**

Recorded: 2026-08-28

## Current audience scope

The accepted record below documents the sealed organizer product and its binding evidence as of
2026-08-28. Its organizer-only statements apply to that sealed full-truth product and private
provenance. A designated practice pack may use the same `civ.label-pack/v1alpha1` identifier and be
supplied separately for participant self-evaluation under the approved distribution; both types
remain outside participant-authored submission payloads. This historical record does not identify
a practice source or chunk, select a pack, or establish a release path. See the [stable-contract
audience guidance](../phase2/stable-contracts-and-compatibility.md#organizer-only-exclusions) and
[local review and coverage guidance](label-review.md).

Label packs are sealed organizer-only inputs. They are never participant-authored, placed in a
submission bundle, copied into a report, or published with development data. The checked-in surface
is limited to generic builder/validator code, tests, and this redacted acceptance record. Source
truth, instantiated packs, reduced sealed recordings, and runtime output remain outside git.

The participant workflow and its stable `v1` contracts are unchanged. Organizers build and audit
packs through the separate module:

```powershell
uv run -m civ_workshop.label_packs build `
  --truth KASHIWA_TRUTH.json REIMS_TRUTH.json `
  --manifests SEALED_PRODUCT_MANIFESTS `
  --output ORGANIZER_OUTPUT
uv run -m civ_workshop.label_packs audit ORGANIZER_OUTPUT/label-pack-set.json
```

`ORGANIZER_OUTPUT/packs` is the directory supplied to `civ score-batch --labels`.

## Closed organizer contract

The evaluator continues to consume the exact organizer-only identifier
`civ.label-pack/v1alpha1`. Any other identifier is rejected. Its closed top-level field set is:

- `contract`, `dataset`, `source_sha256`, `labels`, and `data_gaps`;
- optional private `provenance`; and
- optional `scoring` policy.

Labels have only `label_id`, `start_ns`, and `end_ns`. Data gaps have `start_ns`, `end_ns`, and
optional `gap_id` and `reason`. Unknown top-level or interval fields are rejected. IDs must be
unique, bounds must be non-negative and positive-length, and each list must be deterministically
ordered and non-overlapping. Touching endpoints do not overlap.

The final Phase 3 builder and set auditor require both private provenance and the complete scoring
policy. Historical minimal test packs remain readable through the same closed field set, but cannot
pass the final-pack audit. There is no version guessing, field rewriting, or best-effort migration.

## Product binding and timestamp semantics

The top-level `source_sha256` is deliberately the SHA-256 of the exact reduced MCAP that a
participant run names in its `civ.run-manifest/v1`. Private provenance separately retains:

- the original source identity and SHA-256;
- the approved source-relative truth contract and SHA-256;
- the reduced-product manifest SHA-256; and
- the source and product message bounds plus the identity timestamp-mapping declaration.

Before writing any pack, the builder validates every input set as one unit. It requires sealed
Kashiwa or Reims product manifests, distinct source and product identities, matching truth and
product datasets, and one exact product for every truth-referenced source. It re-hashes each MCAP,
checks its byte size and MCAP summary against the manifest, and accepts only products emitted by
the fixed `civ-workshop/data-products-v1` identity-preserving writer.

Truth intervals remain absolute MCAP log-time nanoseconds; no offset, rounding, resampling, or
clock conversion is applied. Every interval must fit inside both the original-source bounds and
the actual reduced-product bounds. A trimmed endpoint, source-hash mismatch, missing product, or
ambiguous mapping rejects the complete build before the requested output directory exists.

Intervals use half-open `[start_ns, end_ns)` duration semantics. A data gap excludes a label or
prediction only when they have positive temporal overlap; merely touching the gap boundary does
not exclude it. Gap exclusions are reported in stable metrics but the gap intervals themselves
remain sealed.

## Frozen evaluator behavior

Every final pack declares, and the shared scorer validator enforces, the existing policy:

- temporal IoU threshold `0.5`, inclusive;
- candidate matches ordered by highest IoU, then stable label and prediction order;
- greedy one-to-one best assignment;
- every unmatched duplicate prediction is a false positive; and
- precision, recall, and F1 remain the scoring metrics.

A pack attempting to change any of these values is rejected before `metrics.json`, the run
manifest, or batch output is mutated. Calibration may compare detector profiles later, but cannot
silently reinterpret these pack bytes.

## Leak boundary

Participant metrics retain only the organizer pack SHA-256 for reproducibility. Batch results may
retain the participant-known reduced-product hash, dataset, and pack hash, but never label IDs,
intervals, gap contents, original-source provenance, truth hashes, or organizer paths. Diagnostics
redact the organizer labels root. Submission bundles, reports, site files, development products,
and public documentation contain no pack payload or filesystem location.

The automated leak gate exercises a final provenance-rich pack through scoring and confirms that
the normalized events, metrics, and run manifest contain none of its label IDs, gap IDs,
original-source identity/hash, truth hash, or organizer path. Existing batch and bundle tests cover
the same boundary for cohort results and participant archives.

## Real-product acceptance

The organizer build consumed both human-approved source-relative truth records and all 12 sealed
reduced-product manifests. It emitted 12 packs containing 32 approved manoeuvre intervals and zero
data-gap exclusions. All intervals survived the reduction under identity log-time mapping; no
ambiguous or lossy source-to-product mapping was accepted.

A second build from the independently reproduced reduced products emitted the same 12 pack files
and set manifest byte-for-byte. Both set audits passed with SHA-256
`697ba3af68f9bf09d526d87070dd37e1972f9e5e264ed9ea099086dcd7dfc5a7`. Individual pack hashes,
source identities, provenance, interval values, and artifact locations remain organizer-only.
