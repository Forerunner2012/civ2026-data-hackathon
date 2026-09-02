# Phase 3 real two-dataset throughput acceptance

Status: **accepted for the real score, report, intake, and batch gate**

Recorded: 2026-08-29

The complete stable participant path was exercised with real reviewed Kashiwa and Reims reduced
products, then expanded to 20 complete paired participant identities. Three additional identities
proved that missing, late-only, and malformed components remain explicit and isolated. Source data,
evidence clips, organizer label packs, per-product identities, and runtime state remain outside git.

## Real stable bundles

One real Kashiwa run and one real Reims run completed the stable `clip -> score -> report` path.
Each report bundle was rebuilt from a fresh copy of its working artifacts and reproduced
byte-for-byte. The resulting metadata-only bundles were:

| Dataset | Bundle bytes | Archive entries |
|---|---:|---:|
| Kashiwa | 6,914 | 7 |
| Reims | 10,207 | 7 |

Both archives contained exactly one stable EventSpec plus `events.jsonl`, `figure.svg`,
`metrics.json`, `report.md`, `reproduce.ps1`, and `run-manifest.json`. Neither archive contained an
MCAP, evidence directory, label or gap identity, original-source or truth hash, organizer path, or
label-pack payload. Local evidence clips were validated by `report` and deliberately excluded from
the metadata-only bundle.

The bundles validated `civ.eventspec/v1`, `civ.event/v1`, `civ.metrics/v1`,
`civ.run-manifest/v1`, `civ.submission-bundle/v1`, and `civ.reproduction/v1` without rewriting or
compatibility fallback.

## Intake and authority

Twenty complete identities each submitted one authoritative Kashiwa bundle and one authoritative
Reims bundle:

- teams 01-10 submitted 20 dataset runs through an offline replay of the exact Tally CSV adapter;
- teams 11-20 submitted 20 dataset runs through the local/USB adapter;
- one earlier form response for team 01 was superseded by its later on-time Tally Kashiwa run; and
- one earlier local Kashiwa run for team 11 was superseded by its later on-time local run.

The authoritative content hashes matched the exact `civ report` bundles. Selection remained keyed
by participant identity and provenance-derived dataset, so a resubmission in one dataset did not
replace its companion dataset.

The Tally import accepted all 20 valid rows and isolated one deliberately incorrect pasted hash.
The ledger also recorded 26 local deliveries and one form delivery. No adapter required manual
repair.

## Isolated failure identities

Three further identities exercised terminal component states while all 20 complete entries still
scored:

| Scenario | Kashiwa component | Reims component | Aggregate entry |
|---|---|---|---|
| Reims submitted only after cutoff | scored | late-only | incomplete |
| No Reims delivery | scored | missing | incomplete |
| Stored Reims bundle corrupted after accepted intake | scored | malformed | incomplete |

The batch therefore emitted 20 complete and three incomplete entries. It scored 23 Kashiwa
components and 20 Reims components. Every complete result contained exactly two dataset components;
none of the incomplete identities masqueraded as a complete participant entry.

## Unattended batch measurements

The same ledger was scored twice with `civ score-batch`. Both passes used tool version `0.1.0`,
stable metrics contract `civ.metrics/v1`, temporal IoU `0.5`, and batch-result contract
`civ.batch-result/v1alpha1`.

| Measurement | First pass | Second pass |
|---|---:|---:|
| Entries | 23 | 23 |
| Wall time | 2.951289 s | 3.163442 s |
| Lunch budget | 2,700 s | 2,700 s |
| Within budget | yes | yes |
| Peak traced Python memory | 1,223,999 bytes | 1,221,347 bytes |
| Authoritative input bundle bytes | 363,162 | 363,162 |
| Results plus summary bytes | 73,333 | 73,333 |

Peak resident memory for the complete harness was 39,862,272 bytes. End-to-end harness time,
including real bundle construction, all adapters, failure injection, two batches, deterministic
comparisons, and leakage scans, was 12.537288 seconds. Its working disk footprint was 27,102,130
bytes, including local evidence and both batch outputs.

The timing-bearing performance records intentionally differ between passes. The deterministic
factual outputs reproduced byte-for-byte:

- `results.jsonl`: `f395ab2eba941ee10067d0fbca90b802d7c2244fd9aec0f5bb5f91c3cee84b49`;
- `summary.json`: `38c0f096d396247b16969b9e0a3c96e02c52ab5d2ac6b40f1c555b11d6f84e71`.

## Leakage boundary

The private scan covered every real bundle and both complete batch-output trees. It rejected MCAP
or evidence archive entries and searched for organizer label locations, label and gap identities,
gap reasons, original-source hashes, and approved-truth hashes. No forbidden value was present.
Participant-known reduced-product identity remains valid stable provenance and was not misclassified
as sealed truth.

The aggregate-only acceptance record has SHA-256
`2bc89d7e26cb759f663744b4ac63b3c09ccc040c2c9c76d1b233f3bc7c1b14b0`. Instantiated bundles,
receipts, ledgers, Tally exports, label packs, batch results, and measurement state remain
organizer-only artifacts outside git.
