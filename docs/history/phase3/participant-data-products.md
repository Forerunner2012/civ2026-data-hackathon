# Phase 3 participant data products

Status: **accepted for the Phase 3 data-product gate**

Recorded: 2026-08-28

The participant release is a deterministic, signals-only projection of the approved source
membership. Source recordings, instantiated recipes, sealed products, and runtime output remain
outside git. The repository contains only the generic builder, closed schemas, tests, and this
participant-safe acceptance record.

This tooling is intentionally separate from the frozen participant workflow. Organizers invoke it
with `uv run -m civ_workshop.data_products`; it does not add a command or artifact to the
participant `civ inspect -> detect -> clip -> score -> report` path.

## Contracts and deterministic transformation

One exact `civ.data-product-recipe/v1` document names the expected parent source ID and SHA-256,
product filename, membership split, ordered topic allowlist, licence/permission, attribution,
rights scope, and modification notices. A build refuses a parent hash mismatch or any selected
topic with no messages.

The builder emits:

- one MCAP containing only allowlisted messages;
- one canonical `civ.data-product-manifest/v1` with product and parent hashes, byte sizes,
  durations, message bounds/counts, schema identities, recipe ID/version/hash, provenance,
  licence, attribution, modifications, and exact product-plus-manifest disk bytes; and
- one canonical `civ.data-product-set/v1` for the participant release, with every product and
  manifest hash plus total required disk bytes.

The product writer copies message payloads, log timestamps, publish timestamps, sequences,
channel metadata, and embedded schema bytes unchanged. Schemas are identified in the manifest by
name, encoding, and SHA-256. MCAP record ordering follows the source reader, schemas/channels are
registered on first message occurrence, compression is fixed to `NONE`, and the library marker is
fixed to `civ-workshop/data-products-v1`. No build time or filesystem path enters an output.

```sh
uv run -m civ_workshop.data_products build SOURCE.mcap RECIPE.json --output OUTPUT_DIR
uv run -m civ_workshop.data_products set OUTPUT_DIR/*.manifest.json \
  --release-id civ-2026-phase3-participant-signals-v1 \
  --output OUTPUT_DIR/participant-products.json
uv run -m civ_workshop.data_products audit OUTPUT_DIR/participant-products.json
```

## Measured Kashiwa reduction

The approved warm-up source was scanned message-by-message before the allowlist was frozen:

| Measurement | Bytes | Share of uncompressed message payload |
|---|---:|---:|
| Source MCAP on disk | 6,435,997,156 | — |
| All uncompressed message payloads | 6,409,576,488 | 100% |
| Selected full-rate signal payloads | 8,119,584 | 0.127% |
| Deterministic signal product on disk | 11,161,467 | 0.174% of source-file bytes |

The largest excluded payloads validate the reduction rather than merely assuming it:

| Excluded topic | Payload bytes | Reason |
|---|---:|---|
| `/sensing/camera/traffic_light/image_raw` | 1,542,775,172 | camera context is not a default detector input |
| `/sensing/lidar/top/outlier_filtered/pointcloud` | 1,031,979,840 | point cloud |
| `/sensing/lidar/top/ouster/points` | 1,019,394,720 | point cloud |
| `/localization/util/measurement_range/pointcloud` | 889,078,320 | point cloud |
| `/perception/traffic_light_recognition/debug/rois` | 671,855,208 | debug imagery/context |
| `/sensing/camera/traffic_light/image_raw/compressed` | 100,174,952 | optional camera context |
| `/map/pointcloud_map` | excluded by closed allowlist | map and point cloud |

The Kashiwa allowlist retains 17 full-rate topics: acceleration and kinematic state; the object
presence flag; steering, brake, drive, wheel-speed, and vehicle feedback; GNSS fix; IMU; dynamic
and static transforms; and control-mode, gear, steering, indicator, and velocity status. The
detector topic `/pix_hooke/v2a_steerstafb` is therefore preserved at its original rate.

The Reims allowlist retains `/fix`, `/fix_velocity`, `/tf`,
`/zed/zed_node/imu/data`, and `/zed/zed_node/obj_det/objects`. It removes the ZED point cloud and
camera stream while retaining every input used by the detector and GNSS extension.

## Camera/context decision

Signals-only is the default and the only product published by this gate. Kashiwa's representative
raw camera payload alone is about 190 times the selected signal payload. Reims camera distribution
also requires downsampling, face/plate blurring, event-limited access, and post-event deletion
under the owner-approved boundary. An optional context pack therefore requires its own recipe,
privacy transformation, tests, manifest, and release decision; it is not silently mixed into the
default product.

## Real-product acceptance

The organizer build produced all approved products outside git:

| Scope | Products | Product bytes |
|---|---:|---:|
| Kashiwa warm-up | 1 | 11,161,467 |
| Kashiwa development | 7 | 80,435,700 |
| Reims development | 5 | 243,510,166 |
| **Participant release** | **13** | **335,107,333** |
| Organizer-sealed Kashiwa and Reims | 12 | retained outside the participant release |

Including all per-product manifests and the set manifest, participant disk space is exactly
**335,177,173 bytes** (about 320 MiB). The participant-set SHA-256 is
`d515c0a7cd748f8b2ad0cb41b93d8847b0917c2e6469be2f8be09582fc62ef9b`.

A second fresh build from every one of the 25 source-plus-recipe pairs matched all 25 product
SHA-256 values and all 25 per-product manifest SHA-256 values. Rebuilding the aggregate participant
set also reproduced the set hash above.

The release audit reopened and scanned all 13 participant MCAPs: 1,102,147 messages across the
exact allowlists. It verified every product/manifest hash link, topic count and schema identity;
rejected sealed membership; found no MCAP attachment or metadata record; and found no label-pack,
sealed-interval, organizer-path, ground-truth, or hidden-evaluation field or marker. The audit also
recomputed the exact disk requirement from the files.

## Rights and modifications

Kashiwa products retain the URT-Kashiwa CC BY 4.0 attribution and state that the recording was
filtered to explicit signals while camera, maps, point clouds, debug imagery, and other topics were
removed.

Reims products carry the original owner's CIV 2026 learning-and-demonstration permission, required
attribution, event-only access and post-event deletion boundary. They are not described as CC BY
or as a general public release. Because the default Reims products contain no imagery, they do not
depend on a claim that unblurred camera frames are participant-safe.
