# Existing-repository publication evidence

This dossier supplies evidence for [#119](https://github.com/Forerunner2012/civ2026-data-hackathon/issues/119)
and the human clearance gate [#67](https://github.com/Forerunner2012/civ2026-data-hackathon/issues/67).
It is a factual inventory, not publication acceptance. All clearance statuses are provisional.

## Approved direction

The maintainer chose publication of this repository with its development history, wayfinder
maps, epics, and sub-issues preserved. Original contributions have an approved MIT boundary
and the approved holder `Copyright (c) 2026 Matthieu Carré and contributors`.
Copied material retains its own terms. Recordings remain external.

Reims is an optional restricted participant track, with access requested from its owner.
Both dataset workflows must qualify before first publication. Publication waits for the complete
rerun kit. The maintainer requires serious approval of an exact remediation plan before any
history rewrite. These policy choices are settled. Concrete rights and release acceptance are pending.

## Snapshot

The refreshed Git snapshot contains 41 advertised refs, 131 reachable commits, 762 distinct
blobs, 311 distinct paths, and 764 historical blob/path pairs. The unique blob payload totals
10,947,184 bytes. Counts cover reachable history, rather than only branch-tip files.
There are 24 branch refs, 16 PR-head refs, one PR-merge ref, and no advertised tags.

The fixed source identities are:

| Reference | Commit |
| --- | --- |
| `develop` | `9cac1e959869a9a42e15ffb073ab673d8ff6997b` |
| `main`, following authorized PR #104 | `37b05439f73376ccc9131697a472ad0ee0fe3c36` |
| PR #125, the preceding typing fix | `cf869ac8b9776a67fbef8d87cb291faf15da8b5f` |
| Historical presentation branch | `728de9ead538cacf8cd576940c3b3f959a6fd444` |

The snapshot includes PR #125's advertised merge ref. It predates this dossier's own pushed
branch and PR. New refs, comments, commits, or release assets require another inventory before
publication. The audit did not change any existing remote ref.

## Evidence files

| File | Contents |
| --- | --- |
| [refs.tsv](refs.tsv) | Exact advertised ref names, commits, and short join IDs. |
| [objects.tsv](objects.tsv) | Every reachable blob's Git ID, SHA-256, byte count, historical paths, refs, screening markers, and provisional clearance status. |
| [path-refs.tsv](path-refs.tsv) | Exact blob/path pairs and the refs whose reachable commits contain that pair. |
| [archive-inventory.json](archive-inventory.json) | Member hashes, byte counts, XML text counts, relationship counts, and OCR results for both historical PowerPoint archives. |
| [image-inspection.json](image-inspection.json) | Slide-image and thumbnail hashes, thumbnail OCR counts, and QR detection/decoding status. |
| [github-surfaces.tsv](github-surfaces.tsv) | Description/comment identities, URLs, byte counts, and bounded screening markers. No bodies or matched values. |
| [deployments.tsv](deployments.tsv) | Deployment IDs, source commits, refs, environments, latest reported status, and hashed destinations. |
| [summary.json](summary.json) | Git snapshot and blob-screening totals. |
| [collect-evidence.py](collect-evidence.py) | Read-only collector with the exact screening patterns and frozen ref input. |
| [secret-scan.json](secret-scan.json) | Redacted Gitleaks execution identity, scope, result, and limits. |
| [ros-time-comparison.json](ros-time-comparison.json) | Immutable upstream comparisons and the remaining text mismatch. |
| [sites-license-evidence.json](sites-license-evidence.json) | Upstream license pins, Git blob IDs, and SHA-256 values. |
| [ros-license-evidence.json](ros-license-evidence.json) | The pinned ROS license identity. |
| [evidence-sha256.json](evidence-sha256.json) | SHA-256 values for the machine-readable evidence files. |

An object's path list and ref list are separate inventories. Their combinations are established
by `path-refs.tsv`, not by taking the Cartesian product of the two lists. All listed refs are
historical exposure evidence, not recommendations to delete refs.

## Screening results and limits

Every inventoried blob received bounded byte-pattern screening. ZIP members received the same
screening after extraction. Base64 schema fixtures were decoded and hashed. No recognized
private-key, GitHub-token, AWS-access-key, or quoted credential-assignment pattern matched a blob.
No Git LFS pointer or MCAP magic matched an inventoried blob.

Those negative results are limited to the recorded patterns. They do not establish that all
secrets, encodings, archives, personal information, or private truth are absent.
Generic passwords, unfamiliar credential formats, QR contents, arbitrary binaries, and
semantic privacy decisions require further review.

A separate Gitleaks 8.30.1 run used its default rules, `--log-opts=--all`, archive depth 3,
decode depth 5, ignored inline allow comments, and 100% redaction. It reported zero findings
across 120 commits with scannable diffs, approximately 4.14 MB. That scope includes the
fetched refs and the first dossier commit. It differs from the frozen inventory's count
because merge commits without scanned diffs do not contribute to the scanner count.
This additional negative result does not establish privacy, copyright, or secret clearance.

A second Gitleaks run scanned an ignored directory containing all 762 frozen blob versions.
PowerPoint bytes were named `.zip` for archive traversal without altering their hashes.
The scanner reported zero findings across approximately 9.04 MB of scannable content.
Binary images still require OCR and human review. Scanner byte totals are not the inventory's
unique-blob byte total.

The blob screening flags 54 object versions for local-path markers, two for contact markers,
two for operational links, 121 for truth/review terminology, and 65 for geographic terminology.
Markers are review leads, not findings of prohibited disclosure. For example, schema namespaces,
synthetic fixtures, public teaching examples, and review-tool source can contain such terms.
Matched values remain organizer-local and are not copied into this dossier.

The contact and operational-link flags occur in historical versions of
`.scratch/civ2026-challenge-spec/research/05-kashiwa-redistribution-rights.md`.
Their publication disposition remains pending. Source-derived acceptance notes and historical
review helpers also need comparison with the actual permission boundary.
The illustrative Reims point examples are not classified as recorded route coordinates.

## Historical presentations

| Deck | Git blob | Bytes | Slides | Archive members |
| --- | --- | ---: | ---: | ---: |
| `.scratch/hackathon-eve-briefing.pptx` | `e2976162feaf9f32b3da5be68cd31b48417ed378` | 1,965,810 | 20 | 96 |
| `.scratch/hackathon-submission-checklist-slide.pptx` | `0d1eaae937acaa6707d9eeeb3fb41e0637b752b4` | 138,224 | 1 | 39 |

The slide content is rasterized. Local RapidOCR extraction completed for all 21 slide images.
Both document thumbnails also received OCR, with no detected text. OCR can miss text and does
not establish image rights, privacy clearance, or the absence of faces and plates.

Local QR inspection covered the 23 images. Four QR codes were detected and three decoded.
One detected code remains undecoded. QR values, OCR text, document-property values, and extracted
media remain in ignored organizer-local evidence, rather than this committed report.
Neither archive has external relationship targets. Printer-settings binary members are
inventoried and screened, but their full semantics are not interpreted.

No new deck-specific visual-design or embedded-asset permission was established. Human privacy
and rights review remains required before clearance. Current source exclusions cannot clear
the historical branch. The chronology of participant-website acceptance before presentation
changes remains intact. This inspection does not change either presentation.

## Third-party origins and notices

The older audit's unknown Sites origins are superseded by pinned first-party evidence.
The current favicon is an exact MIT-licensed Sites template copy. The build plugin is an
adapted MIT implementation with known local changes. The original upstream notices are now
retained in [THIRD-PARTY-NOTICES.md](../../../THIRD-PARTY-NOTICES.md) and `LICENSES/`.

The CIV favicon replacement is authorized in principle. Specific artwork is still pending.
The Sites copyright license does not establish product-mark permission. Neither the favicon
nor the plugin is deleted or rewritten by this dossier.

Four complete ROS message texts match the pinned `common_interfaces` sources. The transitive
`Time` fields match both inspected `rcl_interfaces` pins, but the text differs, including the
`[0, 10e9)` versus `[0, 1e9)` comment. The exact transformation remains unresolved.
The pinned Apache-2.0 license copy is retained, and fixture bytes remain unchanged.
Notice retention does not complete all attribution or distribution obligations.

Root notices need verification in each actual wheel, standalone source archive, website build,
and offline kit. Dataset credits and external viewer licenses remain separate. The historical
event's unresolved package-risk records do not qualify a new public payload.

## Other GitHub surfaces

At the recorded API inspection, this repository is private, has no forks, and has wiki and
discussions disabled. The API reports no releases, Actions artifacts, or Actions workflow runs.
These observations do not cover external deployment or hosting caches.

The later deployment API inventory contains 45 records with their latest reported success or
failure statuses. Destination URLs are hashed rather than reproduced. A GitHub success status
does not prove that an output is still reachable, privacy-cleared, or equivalent to its source.
Actual deployed bytes and provider caches remain outside this inspection.

The description/comment snapshot contains 124 issue-or-PR descriptions and 187 issue comments.
Its bounded screening finds no private-key or GitHub-token pattern. Three records have local-path
markers. New comments and PRs created during this session are outside that earlier snapshot.
PR inline-review comments were retrieved separately for organizer-local review.
Retained review bodies, attachments, external permission documents, deployment outputs, and
provider caches are not comprehensively cleared. Historical authorship metadata contains two
author identities and three committer identities. Their values are withheld from this report.

## Clearance register

| Scope | Factual status | Remaining gate |
| --- | --- | --- |
| Original contributions | MIT boundary and holder approved. | Root grant and actual distribution metadata/notice propagation. |
| Sites plugin | Adapted upstream MIT origin supported; notice retained. | Shipping-artifact notice verification. |
| Sites favicon | Exact template origin supported; notice retained. | Authorized CIV replacement artwork and review. |
| ROS schema fixture | Four exact message matches; license retained. | Exact `Time` text transformation and applicable attribution completion. |
| Historical decks | Archive, image, OCR, and QR inventories supplied. | Human asset-rights/privacy acceptance and undecoded QR disposition. |
| Source-derived notes and historical helpers | Exact objects, paths, and exposed refs supplied. | Comparison with actual permission and disclosure boundaries. |
| Reims recordings | External, restricted, optional participant track. | Owner access terms for reruns and Windows product/truth qualification. |
| Current and historical Git payload | Bounded screening supplied. | Broader secrets/privacy review and exact final-ref acceptance. |
| Built artifacts and external surfaces | Inventory gaps named. | Concrete final payloads, attachment review, and hosting/cache inspection. |

No object is declared proven nonpublishable solely from a screening marker. No rewrite candidate
is approved. A concrete rewrite proposal requires exact paths, blobs, affected commits/refs,
permission or disclosure evidence, a private backup and restore proof, and collaborator impact.
Existing clones, forks, retained PR refs, and provider caches belong in that impact assessment.
The maintainer's explicit approval must precede any rewrite or destructive ref operation.

## Collection and verification

The Linux session used read-only Git and GitHub operations, including `git ls-remote`, fetches
of PR head/merge refs into `refs/afk-audit/`, `git rev-list`, `git ls-tree`, `git cat-file`, and
paginated `gh api` reads. The collector is retained locally at
`collect-evidence.py`, together with its exact patterns and frozen `refs.tsv` input.
Project dependencies and the lockfile are unchanged. OCR used an isolated uv environment.

From the repository root, the following command regenerates Git object/path counts,
blob hashes, bounded marker totals, archive member inventories, and slide-image OCR.
All frozen commit objects must be available locally, including fetched PR head/merge refs.

```bash
uv run --locked --with rapidocr==3.10.0 --with onnxruntime==1.31.0 python docs/release/public-history-audit-2026-10-10/collect-evidence.py
```

The collector writes to `tmp/public-history-audit-reproduction/` and fails before extracting
content if that location is not Git-ignored. Private OCR/XML text is generated there for local
review. It must not be force-added to Git. The frozen snapshot does not change when remote
refs move. OCR text can differ between engines or hosts, so image hashes establish identity.
The collector does not perform human privacy/rights acceptance or regenerate GitHub's historical
API state. Description/comment counts can be checked from the frozen `github-surfaces.tsv`.

The evidence permits independent verification from the listed immutable objects. For example,
`git cat-file blob <git_blob>` reproduces bytes for SHA-256 comparison, and
`git ls-tree -r <commit>` verifies a path at a commit. Marker counts alone do not establish a
publication boundary. Final clearance requires a fresh snapshot and the concrete human gates.
