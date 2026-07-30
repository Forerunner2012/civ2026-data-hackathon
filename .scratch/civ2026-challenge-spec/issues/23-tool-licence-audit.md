# Do the golden-path tool licences compose cleanly?

Type: research
Status: resolved

## Question

Ticket 20's inbound obligation: the tools used and combined in the hackathon material must not
create an IP or licence problem, given the kit and content will be published permissively
(MIT/Apache-2.0 for code, CC BY 4.0 for content).

Audit every dependency on the golden path. For each, record licence and version, whether it is
**bundled** into the distributed container or merely invoked, what attribution or source-offer
obligation redistribution creates, and whether any of it conflicts with publishing the kit
permissively:

- **PlotJuggler 4** — the required primary viewer (ticket 10), and the one most worth checking
  carefully. Verify the current licence and whether shipping it inside the image changes the
  obligation.
- **Lichtblick** — shipped but optional.
- **ROS 2** distribution, plus the `autoware_*`, `tier4_*` and `pix_*` message packages that
  ticket 06 found are required for the custom-message signals.
- **MCAP** libraries, **Polars**, the **CEL** runtime, and the container base image.

Deliverable: the licence/SBOM inventory §5 Phase 5 already requires, produced early enough that a
tool choice can still change if something does not compose.

## Note

**Bundling is the risk multiplier.** Invoking a tool the user installed is a materially different
position from shipping it inside a distributed image — and ticket 04 made a container the only
delivery mechanism, so almost everything here is bundled.

## Answer

**Go, with an artifact-level release gate.** The named tools compose: nothing forces CIV-owned
code away from MIT/Apache-2.0, and no software licence conflicts with CC BY 4.0 content or data.
But the distributed container is a mixed-licence aggregate, not an MIT/Apache artifact as a
whole. Full inventory and primary-source citations are in
[`../research/23-tool-licence-audit.md`](../research/23-tool-licence-audit.md).

### Decisions

- Standardize the required path on **ROS 2 Humble / Ubuntu 22.04**, starting from the smallest
  practical `ros:humble-ros-base-jammy` image. Freeze by multi-arch digest, not tag alone.
- Keep PlotJuggler required, but describe the current upstream line accurately: the latest
  identified release is **3.999.3, “PlotJuggler 4: beta2”**, not a stable PlotJuggler 4 release.
  Pin and hash the exact tested asset. Keep Lichtblick optional; it ships only if its exact asset
  is pinned, tested and audited, otherwise cut it before freeze.
- Treat both viewers as standalone **MPL-2.0** programs. CIV files remain MIT/Apache, but the
  release must preserve notices and make the exact covered viewer source available. Any modified
  MPL-covered file remains MPL.
- Pin `autoware_auto_vehicle_msgs`, `tier4_vehicle_msgs` and `pix_hooke_driver_msgs` by repository
  commit **and matching MCAP schema hash**. Prefer decoding from embedded MCAP schemas; bundle
  compiled custom-message packages only if the vertical slice proves they are required.
- Pin MCAP CLI, `mcap`, `mcap-ros2-support`, Polars and the CEL implementation independently with
  hashes. Use `cel-python` 0.5.0 as the initial Apache-2.0 candidate, conditional on deterministic
  conformance tests for every EventSpec operator and type used by scoring.
- Do not delete Debian copyright records in image cleanup. Keep the dataset beside the image, not
  inside software layers, so CC BY attribution and software notices stay separate.

### Release gate

Phase 5 must produce, for the **built image digest**, a machine-readable SBOM and
`THIRD_PARTY_NOTICES.md` covering every apt package, Python wheel, CLI and viewer asset. It must
also preserve Debian copyright files, archive matching MPL viewer source, provide the reviewed
source-compliance path for GPL/LGPL findings, and record CC BY attribution separately.

The image does not ship until two built-artifact checks pass: all unknown/NOASSERTION and
copyleft findings are reviewed, and every MPL/GPL/LGPL binary has its required notice, source or
relinking path. This is compliance execution downstream of the spec, not an unresolved tool
choice.
