# Ticket 23 — golden-path tool licence audit

Research date: 2026-07-30  
Scope: the top-level tools named by ticket 23, the exact custom-message packages identified by
ticket 06, and the licence work created by distributing them in the attendee container.

> **Planning analysis, not legal advice.** This is an engineering inventory against the
> projects' own repositories, manifests, licence texts and official documentation. A release
> owner still needs to scan the exact built image and have the chosen source-delivery/trademark
> treatment reviewed before public distribution.

## Executive finding

**The named top-level tools compose, but the release is not yet licence-ready.** Nothing here
forces CIV-owned code away from MIT or Apache-2.0, and nothing conflicts with distributing the
dataset and attendee content under CC BY 4.0. PlotJuggler and Lichtblick are MPL-2.0, which is
file-level copyleft: their covered files remain MPL and their exact source must remain available,
but independent CIV files can retain their own licence. The Apache-2.0 and MIT components are
straightforward notice-preservation cases.

The two material release gates are:

1. **The exact viewer binaries have not been selected or scanned.** Their top-level MPL-2.0
   licences are clean, but an AppImage/deb/Electron bundle includes third-party components whose
   notices and possible LGPL relinking terms must be audited from the actual artifact.
2. **A container base is not selected or digest-pinned.** A ROS/Ubuntu image is an aggregate of
   many independently licensed packages; the Apache-2.0 licence on the Dockerfile repository does
   not license the image contents. The final image therefore needs a generated SBOM, retained
   package copyright files, and a concrete corresponding-source process for any copyleft
   packages.

Bundling is indeed the multiplier. The planning baseline distributes all of these components in
one offline image. PlotJuggler and Lichtblick are standalone programs merely launched by CIV,
but the organizers still become redistributors of their binaries. MCAP, Polars and the CEL
runtime are imported by the runner. ROS packages, message packages and the base operating-system
packages are image contents. An aggregate container does **not** acquire one global MIT,
Apache-2.0 or CC BY licence; each layer and component keeps its own terms.

## Inventory and decisions

| Component | Version/selection status | Planned relationship | Licence | Redistribution result | Decision |
|---|---|---|---|---|---|
| PlotJuggler 4 | Required, **not pinned**. The current upstream release is tag `3.999.3`, named “PlotJuggler 4: beta2”; despite the beta name, GitHub publishes it as the latest release. [Release](https://github.com/PlotJuggler/PlotJuggler/releases/tag/3.999.3) | Bundled standalone viewer, invoked rather than linked into CIV | MPL-2.0. [Project licence](https://github.com/PlotJuggler/PlotJuggler/blob/main/LICENSE.md) | Preserve notices; keep exact covered source available and tell recipients how to obtain it. CIV's separate files stay MIT/Apache. No MPL relinking requirement. The exact binary's third-party payload is still unaudited. | Smoke-test and pin one exact asset plus SHA-256. Archive the matching source tag. Do not say “PlotJuggler 4 stable”: the current artifact calls itself beta2. |
| Lichtblick | Optional-but-shipped, **not pinned**. Current upstream release is `v1.28.0`. [Release](https://github.com/lichtblick-suite/lichtblick/releases/tag/v1.28.0) | Bundled standalone viewer, invoked rather than linked | MPL-2.0; its licence identifies BMW and Foxglove copyright. [Project licence](https://github.com/Lichtblick-Suite/lichtblick/blob/develop/LICENSE) | Same MPL source-availability and notice duties as PlotJuggler. Electron/web build dependencies remain an artifact-level audit item. | Pin the exact desktop/web artifact and digest, or drop it before freeze if camera evidence no longer justifies its SBOM and image-size cost. |
| ROS 2 | **Humble is the intended distro by inference**, because ticket 06 identifies the Kashiwa bags as Humble and the planned environment says to pin one distro. This has not yet been recorded as a release pin. Humble's Tier-1 Linux platform is Ubuntu 22.04 Jammy and its EOL is May 2027, after the event. [Humble release/platform page](https://docs.ros.org/en/humble/Releases/Release-Humble-Hawksbill.html), [ROS distribution table](https://docs.ros.org/en/humble/Releases.html) | Bundled runtime/tooling | No single licence covers a ROS distribution. The official Humble `.repos` manifest composes many separately licensed repositories; it is a version-set manifest, not a licensing umbrella. [Humble repositories file](https://github.com/ros2/ros2/blob/humble/ros2.repos) | CIV code can remain MIT/Apache, but every installed deb retains its own terms. Source, notice and relinking duties can only be concluded from the exact package closure. | Confirm Humble; pin the base image by multi-arch digest and snapshot every installed deb/version. Prefer the smallest `ros-base` closure rather than a desktop image. |
| `autoware_auto_vehicle_msgs` | Package version `1.0.0`; upstream's last source commit is `818d3587` (2022-03-03). [Package manifest](https://gitlab.com/autowarefoundation/autoware.auto/autoware_auto_msgs/-/blob/master/autoware_auto_vehicle_msgs/package.xml), [repository](https://gitlab.com/autowarefoundation/autoware.auto/autoware_auto_msgs) | Planned bundled schema package/generated type support | Apache-2.0 (“Apache 2” in the manifest). [Repository licence](https://gitlab.com/autowarefoundation/autoware.auto/autoware_auto_msgs/-/blob/master/LICENSE) | Include Apache-2.0 text; retain copyright/patent/attribution notices; mark modified source files; propagate a NOTICE if the selected artifact contains one. No source offer or relinking requirement. | Pin commit `818d3587` or the exact Humble binary package version and verify its schemas against the MCAP schema records. |
| `tier4_vehicle_msgs` (and its `tier4_control_msgs` message dependency) | Manifest says `0.1.0`, but the active `tier4/universe` branch is mutable and the package version alone is not an adequate schema pin. [Package manifest](https://github.com/tier4/tier4_autoware_msgs/blob/tier4/universe/tier4_vehicle_msgs/package.xml) | Planned bundled schema package/generated type support | Apache-2.0 for the containing repository. [Repository licence](https://github.com/tier4/tier4_autoware_msgs/blob/tier4/universe/LICENSE) | Same Apache-2.0 obligations; no source offer or relinking requirement. | Select a commit by comparing message definitions to the bag's embedded schema, then pin that commit. “Latest `0.1.0`” is not reproducible. |
| `pix_hooke_driver_msgs` | Manifest says `0.9.0`; no source commit is selected. [Package manifest](https://github.com/pixmoving-moveit/pix_driver/blob/main/pix_hooke_driver_msgs/package.xml) | Planned bundled schema package/generated type support; the vehicle driver itself is not required merely to decode messages | Apache-2.0. [Repository licence](https://github.com/pixmoving-moveit/pix_driver/blob/main/LICENSE) | Same Apache-2.0 obligations; no source offer or relinking requirement. | Bundle only the message package and required standard interfaces, not the CAN/vehicle driver. Pin the schema-matching commit, not merely `0.9.0`. |
| MCAP Python/ROS 2 libraries and CLI | **Not pinned.** Current upstream releases are Python `mcap` `v1.4.0`, `mcap-ros2-support` `v0.5.7`, and CLI `v0.3.0`. [Python release](https://github.com/foxglove/mcap/releases/tag/releases/python/mcap/v1.4.0), [ROS 2 support release](https://github.com/foxglove/mcap/releases/tag/releases/python/mcap-ros2-support/v0.5.7), [CLI release](https://github.com/foxglove/mcap/releases/tag/releases/mcap-cli/v0.3.0) | Libraries bundled/imported by the runner; CLI bundled and invoked | MIT. [Repository licence](https://github.com/foxglove/mcap/blob/main/LICENSE) | Retain the copyright and MIT permission notice in copies or substantial portions. No source offer or relinking requirement. | Pin all three independently; record wheel/binary hashes. The installed CLI on the planning machine is evidence of availability, not a release pin. |
| Python Polars | **Not pinned.** Current Python release is `1.43.1`. [Release](https://github.com/pola-rs/polars/releases/tag/py-1.43.1) | Bundled/imported by the runner | MIT. [Project licence](https://github.com/pola-rs/polars/blob/main/LICENSE) | Retain the licence/copyright notice. No source offer or relinking requirement from Polars itself. The exact wheel's Rust dependency notices belong in the generated SBOM. | Pin the Python wheel version and hashes after the minimum-CPU test; do not rely on the mutable latest wheel. |
| CEL runtime | **No runtime has been selected.** The natural Python candidate is `cel-python`/`celpy` `0.5.0`, which PyPI describes as a beta pure-Python CEL implementation; that is a recommendation, not an existing decision. [PyPI release](https://pypi.org/project/cel-python/0.5.0/), [upstream repository](https://github.com/cloud-custodian/cel-python) | Would be bundled/imported by the Python runner | Candidate is Apache-2.0. [Candidate licence](https://github.com/cloud-custodian/cel-python/blob/main/LICENSE) | Apache-2.0 notice duties; no source offer or relinking requirement from the candidate itself. Its dependency closure still needs SBOM coverage. | Choose the runtime on conformance/determinism grounds, then pin it. If `cel-python` is chosen, use `0.5.0` plus hashes and test every EventSpec operator/type against the CEL conformance semantics relied upon by scoring. |
| Container base | **Not selected or digest-pinned.** The smallest official candidate is `ros:humble-ros-base-jammy`; Docker documents that it is built from the official Ubuntu image plus official ROS debs. [Official ROS image](https://hub.docker.com/_/ros) | Necessarily bundled; every base layer is redistributed | Mixed. The OSRF Dockerfile repository is Apache-2.0, but that licence does not replace the licences of Ubuntu and ROS packages. Ubuntu itself is an aggregate of works under their own licences. [OSRF Docker definitions](https://github.com/osrf/docker_images), [Ubuntu IP/licence policy](https://ubuntu.com/legal/intellectual-property-policy) | Preserve each package's notices; satisfy source-conveyance/source-offer terms for GPL-family binaries and any LGPL relinking terms found in the final closure. Avoid implying Canonical endorsement or branding a modified image as Ubuntu. | Select an image digest; inventory every installed package; preserve `/usr/share/doc/*/copyright`; archive or provide a reviewed corresponding-source mechanism; run a licence scanner against the final image, not only the Dockerfile. |

### Message-package scope

Ticket 06 names two custom packages explicitly: `tier4_vehicle_msgs` and
`pix_hooke_driver_msgs`. Its `/vehicle/status/*` signals also use
`autoware_auto_vehicle_msgs` in this Humble-era dataset. This audit therefore covers those three
source families, not every current package matching the broad prefixes `autoware_*`, `tier4_*`
or `pix_*`. Their standard ROS dependencies (`std_msgs`, `geometry_msgs`,
`builtin_interfaces`, ROSIDL runtime) enter through the pinned ROS package closure and must
appear in the final SBOM.

For reproducibility, **message package version strings are insufficient**. ROS message layouts
can change without a useful package-version distinction for this dataset. The release owner
should extract the MCAP schema records, compare them with the selected `.msg`/IDL files, and
record repository commit plus schema hashes. If the Python MCAP path can decode entirely from
the schemas embedded in each MCAP, the container may not need compiled Autoware/PIX packages at
runtime; keeping only exact schema sources would reduce both image and licence surface. That is
a technical inference to verify in the vertical slice, not a current decision.

## What each licence actually requires here

### MPL-2.0 viewers

MPL-2.0 defines a “Larger Work” as covered software combined with other material in separate
files and permits that larger work under terms of the distributor's choice, while the covered
software remains subject to MPL. Executable distribution requires the covered source to be
available by reasonable means, recipients to be told how to obtain it, and existing notices to
remain intact. [MPL-2.0 §§1.7, 3.2–3.4](https://www.mozilla.org/media/MPL/2.0/index.f75d2927d3c1.txt)

Mozilla's official FAQ describes MPL as file-level copyleft, confirms that MPL may be combined
with Apache/BSD code, and says a distributor of a complete unchanged upstream executable
typically needs no new step if the upstream distributor already complied—while still advising
the redistributor to verify the source notice and actual source availability.
[MPL FAQ Q1, Q7–Q13](https://www.mozilla.org/en-US/MPL/2.0/FAQ/)

Applied here:

- launching the viewers as separate applications does not put CIV source files under MPL;
- shipping them inside the image is still external binary distribution;
- include each MPL text and a source-availability entry naming the exact tag/commit and source
  archive; mirror the archive with the release rather than depending only on a moving branch;
- publish any organizer modifications to MPL-covered files under MPL;
- MPL itself does **not** demand relinkable objects. Any relinking obligation would come from a
  linked LGPL dependency in the selected viewer artifact, hence the required artifact scan.

### Apache-2.0 components

Apache-2.0 §4 requires a copy of the licence, prominent change notices in modified files,
retention of relevant copyright/patent/trademark/attribution notices, and propagation of
attribution from an upstream `NOTICE` file when one is present.
[Apache-2.0 §4](https://www.apache.org/licenses/LICENSE-2.0)

It does not require publication of corresponding source or relinkable objects. CIV code may be
MIT, Apache-2.0, or dual-licensed; the bundled Apache components still need their own licence and
notices. The final wheel/deb/image—not merely the source repository—determines whether a NOTICE
or additional attribution file is present.

### MIT components

MCAP and Polars require their copyright and permission notice to accompany copies or substantial
portions. Their top-level MIT licences create no source-offer or relinking duty.
[MCAP licence](https://github.com/foxglove/mcap/blob/main/LICENSE),
[Polars licence](https://github.com/pola-rs/polars/blob/main/LICENSE)

### Ubuntu/ROS base and copyleft packages

The official ROS image is explicitly built from Ubuntu and ROS Debian packages, and the Ubuntu
project requires every Debian package to install verbatim copyright/licence information at
`/usr/share/doc/<package>/copyright`.
[ROS image composition](https://hub.docker.com/_/ros),
[Ubuntu packaging documentation](https://ubuntu.com/project/docs/how-ubuntu-is-made/concepts/debian-directory/)

Therefore “base image: Apache-2.0” would be false. The exact image can contain MIT, BSD,
Apache-2.0, MPL, GPL, LGPL and other licences. GPL/LGPL obligations attach only to the relevant
components; they do not convert unrelated CIV files or CC BY data merely because all are
container layers. But they may require corresponding source, installation/relinking information,
or retained notices. That conclusion must be generated from the frozen image's package and file
inventory.

Ubuntu's own policy also says Ubuntu is an aggregate and that modified redistribution associated
with Ubuntu trademarks needs special care. Name the image as the CIV kit, describe Ubuntu/ROS
factually in third-party notices, and do not imply endorsement.
[Ubuntu IP policy §§1–5](https://ubuntu.com/legal/intellectual-property-policy)

## Compatibility with the planned publication licences

- **CIV-owned code under MIT and/or Apache-2.0:** compatible with every named top-level
  dependency. MPL viewer files remain MPL; Apache and MIT dependency files retain their
  licences; the image as a whole should not be labelled “MIT” or “Apache-2.0”.
- **Attendee material/data under CC BY 4.0:** no software licence above purports to relicense
  independent data or prose. Keep dataset/content attribution in a separate `DATA-LICENSES`
  section or file: credit the creator, link the licence, retain supplied notices and indicate
  modifications as CC BY 4.0 requires.
  [CC BY 4.0 §3(a)](https://creativecommons.org/licenses/by/4.0/legalcode.en)
- **Recommended physical separation:** distribute the data beside the container, as ticket 17
  already plans, rather than baking 100+ GB of CC BY recordings into software layers. This makes
  the two notice regimes and update paths unambiguous; it is operational hygiene, not a licence
  requirement.

## Release gate / concrete SBOM deliverable

Before Phase 5, produce one machine-readable SBOM for the exact image digest and one human-readable
`THIRD_PARTY_NOTICES.md` with:

1. image name, multi-arch digest, Dockerfile commit and build date;
2. every apt package and exact version (`dpkg-query`), every Python distribution and wheel hash,
   and standalone viewer/CLI asset hashes;
3. the licence text and upstream source URL/tag/commit for PlotJuggler, Lichtblick, MCAP,
   Polars, the selected CEL runtime and each custom-message source family;
4. preserved Debian copyright records (do not delete them in a size-cleanup layer);
5. matching source archives for the two MPL viewers and organizer modifications, plus the
   reviewed corresponding-source mechanism for GPL/LGPL packages;
6. any third-party notice bundle from the exact PlotJuggler and Lichtblick artifacts;
7. a separate CC BY data/content attribution and modification record.

Then run two checks against the **built image**, not the lockfiles:

- a licence/SBOM scan with “unknown”, “NOASSERTION”, GPL/AGPL and LGPL findings reviewed
  manually; and
- a source/notices audit proving that every MPL/GPL/LGPL binary finding has a matching source or
  other required compliance path, and that any LGPL static linkage has the needed relinking
  materials.

## Decisions ticket 23 should close

The licence answer itself is **go, with conditions**. The ticket can close once it records these
release decisions:

1. ROS 2 **Humble** on a digest-pinned `ros:humble-ros-base-jammy`-derived image (or another
   explicitly named, digest-pinned base).
2. One exact PlotJuggler 4 beta asset and one exact Lichtblick asset, each hashed and tested; or
   Lichtblick removed before freeze.
3. `autoware_auto_vehicle_msgs`, `tier4_vehicle_msgs` and `pix_hooke_driver_msgs` pinned by
   repository commit and verified MCAP schema hash.
4. MCAP CLI/Python/ROS 2 support, Polars and a CEL implementation pinned independently.
5. The notices/SBOM/source bundle above assigned to a release owner and made a release gate.

None of the current top-level licence choices needs replacement. The remaining risk is artifact
selection and compliance execution, not incompatibility between MIT/Apache code, MPL viewers and
CC BY content.
