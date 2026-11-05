# Integrated Phase 3 data and evaluation gate

> **Historical CIV 2026 record.** The dates, commands, artifact identities and acceptance
> below describe the original event and its recorded scope. Start a current session with the
> [QuickStart](../../quickstart.md), [organizer guide](../../organizers/README.md) and
> [participant contracts](../../reference/participant-contracts.md). See the
> [Phase 1–5 history index](../civ-2026.md) for later changes. This record does not grant
> new data rights, platform qualification or public-release approval.

Status: **accepted — all Phase 3 data and evaluation criteria pass**

Recorded: 2026-08-29 · Operator: Codex on the organizer workstation

This record integrates participant-safe reduced products, human-approved truth, organizer label
packs, human-approved calibration, real two-dataset intake and scoring, and the pinned offline Linux
release target. Organizer-only inputs and runtime outputs remain outside git. Public evidence is
limited to counts, aggregate measurements, immutable hashes, approvals, and redacted consequences.

## Gate inputs

| Input | Accepted evidence |
|---|---|
| Source membership | Kashiwa 1 warm-up + 7 development + 8 sealed; Reims 5 development + 4 sealed |
| Participant products | 13 products; 1,102,147 messages; 335,177,173 required disk bytes |
| Participant product set | `d515c0a7cd748f8b2ad0cb41b93d8847b0917c2e6469be2f8be09582fc62ef9b` |
| Organizer label packs | 12 packs; 32 approved intervals; zero data-gap exclusions |
| Label-pack set | `697ba3af68f9bf09d526d87070dd37e1972f9e5e264ed9ea099086dcd7dfc5a7` |
| Approved calibration profiles | `bf68005d97892263162e28feaf9fb3325c48a9dc39d223a519ef8eee87f72dcf` |
| Approved calibration interpretation | `dc8a2f65bd3ce67a31d836a57a251ba970c7423d29f0be2ce1c3786894b278f7` |
| Real throughput acceptance | `2bc89d7e26cb759f663744b4ac63b3c09ccc040c2c9c76d1b233f3bc7c1b14b0` |

The two recovered Kashiwa derivatives remain accepted inputs with their provenance caveat: MCAP
recovery rebuilt readable indexed files but cannot prove that source truncation lost no records.
Their corrupt parents remain preserved, and the caveat follows the derivatives into organizer
inventory and distribution notices. Nothing in this gate upgrades them to pristine reacquisitions.

## Step 1 — Products reproduce and stay participant-safe

The original and independently reproduced participant set manifests were byte-identical. Fresh
audits of both sets reopened all 13 MCAPs and returned the same counts, required disk bytes, and set
hash shown above. The audits rechecked product and manifest hashes, exact allowlists, message counts,
schema identities, membership, and absence of attachments and metadata records.

The default products contain only the approved full-rate signal topics. Camera, point cloud, map,
debug imagery, and unselected topics remain absent. No label pack, reviewed interval, organizer
path, ground-truth marker, or hidden-evaluation field appears in participant products or manifests.
Optional camera/context distribution remains a separate privacy and rights decision; this gate does
not silently add it.

## Step 2 — Truth has explicit human authority

Every proposed sealed interval received a human approve, reject, or adjust decision in its bounded
Kashiwa bag or Reims chunk review group. Both datasets then received a human-approved global check
for missed situations, unusually long events, adjacent fragments, and windows split across local
candidate or chunk boundaries.

The Kashiwa completeness review retained the reviewed-negative finding that four rejected approach
windows contain no complete target manoeuvre in the observed source bytes. Reims retained only its
human-approved clear manoeuvres; borderline development leads do not enter sealed Detection truth.
No planning candidate became truth merely because an automated search proposed it.

The final source-relative records passed bounds, ordering, uniqueness, and deterministic
serialization checks. Only the approved warm-up and deliberately partial development teaching
annotations are participant-visible; sealed intervals and reconstructable answers remain private.

## Step 3 — Label packs bind truth to exact products

Fresh audits of the original and independently reproduced label-pack sets both passed at the exact
set hash above. They contain 12 packs and 32 approved intervals with identity timestamp mapping and
zero data-gap exclusions. Every pack is keyed to the exact reduced-product SHA-256 seen in stable
run manifests and retains private traceability to its source-relative human decision.

The fixed evaluator semantics remain temporal IoU `0.5`, deterministic one-to-one best assignment,
duplicate predictions as false positives, and F1. Packs, intervals, provenance, and paths remain
absent from participant bundles, development products, public/site artifacts, and diagnostics.

## Step 4 — Calibration separates deliberate strategies

The organizer approved all four development-only profile pairs before any sealed execution. After
the frozen run and its byte-identical reproduction, the approved sealed aggregate was:

| Dataset | Competent-timed | Naive threshold | Route-overfit | No-debounce |
|---|---:|---:|---:|---:|
| Kashiwa F1 | 0.875000 | 0.656250 | 0.652174 | 0.348624 |
| Reims F1 | 0.521739 | 0.720000 | 0.000000 | 0.642857 |

The human organizer approved classifying the Reims inversion as a profile flaw exposed by real
dataset behavior, not an evaluator flaw. The added competent-profile speed and persistence
assumptions did not transfer, while the deliberately route-specific profile collapsed under the
distribution shift it was designed to expose. No one naive threshold led both datasets, and only
one profile reached 90 percent of the best F1 on each stack.

The organizer retained **15 Kashiwa / 10 Reims** without adjustment. The total Detection budget
remains 25 points.

## Step 5 — Real paired intake and lunch scoring

One real Kashiwa run and one real Reims run completed stable `clip -> score -> report`. Fresh copies
reproduced both seven-entry metadata-only bundles byte-for-byte at 6,914 and 10,207 bytes. Evidence
clips were validated locally and excluded from the archives.

Twenty complete participant identities each carried one authoritative Kashiwa and one authoritative
Reims run. Ten pairs crossed the Tally adapter and ten crossed local/USB intake. An earlier form
submission and an earlier local submission proved that the later on-time bundle wins independently
per dataset without erasing its companion. One invalid Tally hash, one late-only component, one
missing component, and one bundle corrupted after intake were isolated without stopping the batch.

Two Windows batch passes produced 20 complete and three incomplete identities in 2.951289 and
3.163442 seconds against the 2,700-second budget. Peak resident memory for the complete harness was
39,862,272 bytes; peak traced Python allocation was about 1.22 MB. The deterministic factual files
reproduced byte-for-byte:

- `results.jsonl`: `f395ab2eba941ee10067d0fbca90b802d7c2244fd9aec0f5bb5f91c3cee84b49`;
- `summary.json`: `38c0f096d396247b16969b9e0a3c96e02c52ab5d2ac6b40f1c555b11d6f84e71`.

## Step 6 — Pinned offline Lyrical replay

The Phase 3 path reran with current repository code in the retained prepared image derived from the
official pinned base:

| Environment item | Recorded value |
|---|---|
| Base digest | `sha256:122a787d0eb7e1b2c18370e35ef394332db5c11d242bea6f05f2b2911e26b04d` |
| Prepared local image | `sha256:abf90cdd46b446a185f24bc2a7097a49b34b57c415ff227e02ae55c17c7cd423` |
| OS / ROS / architecture | Ubuntu 26.04 LTS / Lyrical / linux-amd64 (`x86_64`) |
| Python / tool | CPython 3.12.11 / `civ-workshop` 0.1.0 |
| Container isolation | `--network none`; no GPU device; no NVIDIA tooling |
| Mount policy | repository, products, packs, and dependency volume read-only; output only writable |

Each real dataset completed `inspect -> detect -> clip -> score -> report -> intake-local`, followed
by one paired batch. The complete 20-pair ledger then scored twice. Every GNU `time -v` record showed
zero socket messages sent and received.

| Dataset | Command | Wall time | Peak RSS |
|---|---|---:|---:|
| Kashiwa | inspect | 3.05 s | 47,708 KB |
| Kashiwa | detect | 2.22 s | 47,572 KB |
| Kashiwa | clip | 1.86 s | 46,344 KB |
| Kashiwa | score | 1.45 s | 41,720 KB |
| Kashiwa | report | 1.30 s | 42,864 KB |
| Kashiwa | intake-local | 1.04 s | 43,392 KB |
| Reims | inspect | 4.83 s | 46,628 KB |
| Reims | detect | 40.21 s | 47,516 KB |
| Reims | clip | 2.64 s | 45,788 KB |
| Reims | score | 1.04 s | 41,556 KB |
| Reims | report | 1.04 s | 42,452 KB |
| Reims | intake-local | 1.26 s | 43,292 KB |

The paired batch took 1.73 seconds with 43,364 KB peak RSS. The two full cohort processes each took
4.87 seconds including startup, with 43,016 and 42,944 KB peak RSS; internal scoring time was
3.594217 and 3.482627 seconds. Both cross-platform submission bundles matched their Windows bytes,
and both cohort runs reproduced the exact Windows `results.jsonl` and `summary.json` hashes above.

Container working directories used 1,925,398 Kashiwa bytes and 7,035,340 Reims bytes. All integrated
container output used 9,236,432 bytes, including local evidence, two ledgers, two cohort outputs,
telemetry, and the paired proof.

## Step 7 — Repository, schema, and site gates

The final gate uses the declared repository checks, not an intermediate subset:

- all Python tests;
- Ruff over the repository;
- strict mypy over `src` and `tests`;
- stable contract and schema conformance tests;
- fresh audits of both original/reproduced product and label-pack sets;
- public handoff-site build, all internal/no-form/public tests, and ESLint;
- participant/client/server/static-fallback organizer-content leakage assertions;
- explicit public-document scans for organizer paths, source identities, intervals, and label/gap
  fields; and
- `git diff --check`.

Generated site output, caches, runtime artifacts, datasets, packs, ledgers, bundles, and container
state remain uncommitted.

## Failure and intervention log

| # | Step | What happened | Resolution and consequence |
|---|---|---|---|
| 1 | Kashiwa inventory | Two source files were truncated and could not pass structural validation. | The organizer approved readable recovered derivatives with an explicit no-loss-proof caveat; corrupt parents remain preserved. |
| 2 | Kashiwa review | Four rejected approach windows lacked a complete target manoeuvre in observed bytes. | Retained as reviewed negatives; no synthetic positive interval was added. |
| 3 | Calibration exploration | A literal zero-duration no-debounce profile emitted invalid zero-length events. | Before preregistration, changed it to the smallest valid duration with short continuity merging; the organizer approved only the corrected frozen hash. |
| 4 | Calibration result | Reims ranked the naive profile above competent-timed. | Investigated rather than retuned; the organizer approved the profile-transfer classification and 15/10 split. |
| 5 | Real report preparation | Calibration working artifacts had never run `clip`, so `report` correctly rejected their absent clip inventory. | Executed the real stable clip step; local evidence remained outside bundles. |
| 6 | Real leakage scan | A participant-known reduced-product identity also appeared in private provenance and triggered an over-broad token scan. | Classified the public product identity separately while retaining full source/truth hashes, labels, gaps, paths, MCAPs, and evidence as forbidden. |
| 7 | Real telemetry | The first Windows peak-RSS call lacked explicit ctypes signatures. | Added the platform signatures and reran the entire acceptance; no evaluator or artifact changed. |
| 8 | Container precondition | Docker Desktop's Linux daemon was initially stopped. | Started the existing daemon; no image pull or dependency download occurred. |
| 9 | Container attempt 1 | The read-only dependency volume was mounted at `/state`, but its prepared Python symlink targets `/opt/civ-state`. | The run stopped before any project command; remounted the same volume read-only at its original path and completed successfully. |

No acceptance criterion was overridden. Every retry either stopped before mutation or reran the
complete affected gate.

## Routed consequences

- **Phase 4 attendee kit:** publish the now-final 15/10 wording; prepare the audited 13-product set
  and pinned container for T-1 and event-day SSD distribution; keep optional camera/context behind
  its separate privacy and rights gate; pin the final viewer assets and participant layouts.
- **Phase 5 release candidate:** rehearse these exact hashes on event hardware; freeze the release
  image, dependency archive, SBOM/notices/source archive, recovery media, and post-event deletion
  procedure. The prepared organizer image used here is local runtime state, not yet a release image.
- **Recovered Kashiwa derivatives:** retain the recovery command/version provenance, adjacent corrupt
  parents, and no-loss-proof caveat in every downstream organizer and distribution record.
- **Contracts and evaluator:** no Phase 4 or Phase 5 contract change is required. The stable
  participant `v1` artifacts, fixed matching semantics, and dataset-specific authority all passed.

## Final criterion table

| # | Criterion | Result | Evidence |
|---|---|---|---|
| 1 | Reduced products reproduce and public manifests remain truth-free | PASS | Step 1 |
| 2 | Every sealed interval and global completeness check has human authority | PASS | Step 2 |
| 3 | Final packs bind exact products and do not leak | PASS | Step 3 |
| 4 | Four frozen profiles discriminate; interpretation and 15/10 are approved | PASS | Step 4 |
| 5 | Real paired score/report/intake/batch finishes unattended inside lunch | PASS | Step 5 |
| 6 | Current stable path passes pinned offline Lyrical CPU replay | PASS | Step 6 |
| 7 | Full Python, schema, site, leakage, lint/type, and diff gates pass | PASS | Step 7 |
| 8 | One redacted record captures passes, failures, approvals, and routing | PASS | This record |
