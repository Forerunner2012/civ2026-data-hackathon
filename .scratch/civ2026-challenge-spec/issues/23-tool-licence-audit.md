# Do the golden-path tool licences compose cleanly?

Type: research
Status: open

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
