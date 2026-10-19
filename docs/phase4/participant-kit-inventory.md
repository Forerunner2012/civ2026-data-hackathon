# Phase 4 participant-kit inventory contract

Status: **implemented; real inventory acceptance recorded below**

Recorded: 2026-08-29

The `civ.participant-kit-inventory/v1` contract stages one deterministic, participant-safe
inventory around the accepted Phase 3 signals-only product set. A populated inventory is generated
outside git. The repository contains only the closed schema, generic builder/auditor, tests, public
tracked assets, and this redacted acceptance record.

## Frozen scope

The inventory accepts only participant set
`d515c0a7cd748f8b2ad0cb41b93d8847b0917c2e6469be2f8be09582fc62ef9b`:
13 products, 1,102,147 messages, and 335,177,173 bytes including their public manifests and set
manifest. The roles are exactly one Kashiwa warm-up, seven Kashiwa development, and five Reims
development products. Each product and public manifest is recorded by participant-facing relative
path, exact SHA-256, and byte size.

The same inventory records:

- `civ-workshop` version, source commit, and `uv.lock` hash;
- the accepted Lyrical/Linux-amd64 container candidate image identity;
- supplied PlotJuggler and Lichtblick assets that match the Phase 4 accepted names, sizes, and
  hashes, with neither viewer allowed to ship alone;
- every public quickstart, reference layout, example, participant schema, and fixed submission
  template by tracked relative path, exact hash, and byte size;
- the deterministic directory layout and sorted `SHA256SUMS` procedure; and
- the two-recovered-recording caveat, without a corrupt-parent location.

External MCAPs and public manifests, viewer binaries, container state, caches, and organizer paths
are read-only inputs. The builder does not copy them and no populated inventory is committed.

## Signals-only and context boundary

`content_profile` is fixed to `signals-only` and the default `context_packs` list is empty. A future
camera/context entry is contract-valid only when it records its own manifest, manifest SHA-256,
required disk bytes, and a separate human privacy-and-rights approval ID plus approval-document
hash. The Phase 3 signals-only set cannot silently acquire camera or context payloads.

## Deterministic external procedure

Run from the repository, but place the output outside it:

```sh
uv run -m civ_workshop.kit_inventory build PARTICIPANT_SET_JSON \
  --repository . \
  --viewer PINNED_VIEWER_BINARY \
  --output EXTERNAL_KIT_ROOT/participant-kit.json
uv run -m civ_workshop.kit_inventory audit EXTERNAL_KIT_ROOT/participant-kit.json
```

Populate only the inventory's relative targets. Copy the generated checksum manifest to
`checksums/SHA256SUMS`, verify hashes after every copy, and reject extra or changed bytes. The
proposed directories are `checksums`, `container`, `data`, `docs`, `examples`, `layouts`,
`templates/submission`, and the two platform-specific viewer directories. Phase 5 still owns container export, clean-host
installation, final SSD byte verification, SBOM/notices/source archive, event-hardware rehearsal,
and release sign-off.

## Acceptance evidence

The real accepted Phase 3 participant directory was reopened and audited before inventory
generation. All 13 MCAPs and public manifests passed their exact hash, schema/topic, role, message,
disk-size, and leakage checks. Two independent inventory builds produced byte-identical JSON and
checksum manifests. The Windows PlotJuggler and Lichtblick inputs matched their accepted
117,766,332-byte and 266,309,046-byte SHA-256 pins. Linux viewer assets remain a Phase 5
physical-payload check.

The generated inventory contained no absolute path, label-pack or interval data, truth marker,
sealed identity, viewer state, container state, secret, camera/context entry, or untracked payload.
It remained outside git. Its exact hash is intentionally not frozen here because the tool source
commit changes when this implementation is committed; Phase 5 will freeze the final generated
inventory against that release commit and both physical platform payloads.
