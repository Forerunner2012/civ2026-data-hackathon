# CIV Data Hackathon

This context covers the participant analysis workflow and the organizer evaluation workflow for
the CIV 2026 data hackathon.

## Language

**Participant contract**:
A versioned, portable analysis artifact whose meaning must remain stable across participant and
organizer tooling.
_Avoid_: File format, attendee record

**EventSpec**:
A declarative participant specification that binds recorded signals and resources to deterministic
derivation, condition, timing, and evidence rules.
_Avoid_: Detector script, custom detector

**Normalized event**:
A deterministically identified time interval selected by an EventSpec from one source recording.
_Avoid_: Label, raw trigger

**Organizer-only artifact**:
An operational, transport, or sealed-evaluation record that is not authored or submitted as part
of the participant analysis contract.
_Avoid_: Participant contract, submission artifact

**Run manifest**:
The deterministic factual spine that relates one analysis run's source, specification, events,
evidence, metrics, resources, and submission provenance.
_Avoid_: Log, telemetry report

**Metadata-only submission bundle**:
The canonical participant handoff containing the detector, normalized events, metrics, report,
figure, reproduction entry point, and run manifest, but no source data or evidence clips.
_Avoid_: Dataset bundle, evidence archive

**Point resource**:
A participant-declared set of named geographic points used by deterministic EventSpec derivation.
_Avoid_: Map layer, detector code

**Evidence clip**:
A local MCAP excerpt surrounding a normalized event for inspection; it is working evidence, not a
submission artifact.
_Avoid_: Label, submission bundle
