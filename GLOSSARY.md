# CIV data hackathon

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
A deterministic record that links one analysis run's source, specification, events,
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

**RT**:
The Kashiwa right-turn detection target.
_Avoid_: Reims turn target

**R&LT**:
The Reims right-or-left-turn detection target.
_Avoid_: Left-turn-only target

**Dataset**:
A source family, currently Kashiwa or Reims; it does not identify one exact recording.
_Avoid_: Product, chunk

**Track**:
A detector target with its own participant submissions, assigned products, organizer references,
and scoring allocation.
_Avoid_: Dataset

**Product**:
An exact source-bound recording and its manifest, assigned to one or more tracks.
_Avoid_: Dataset, source family

**Partition**:
A product's warm-up, development, or sealed access classification; it does not establish truth
completeness or score eligibility.
_Avoid_: Track

**Participant submission**:
One track-specific ZIP delivery whose validated EventSpec and declared resources are replay inputs.
_Avoid_: Organizer replay result

**Submitted events and metrics**:
Participant-generated practice or audit artifacts that do not serve as cohort predictions.
_Avoid_: Replay events, organizer score

**Replay events**:
Predictions produced by the organizer's trusted runtime from a selected EventSpec and assigned
product.
_Avoid_: Submitted events

**Organizer reference**:
Truth approved for one track and exact product; full truth and review evidence remain organizer-only.
_Avoid_: Practice pack

**Cohort result**:
The recorded scoring outcomes for one participant across the tracks and products in an evaluation
plan.
_Avoid_: Product score

**Computation approval**:
A human approval bound to the exact plan and scoring-input fingerprint; it does not approve
publication.
_Avoid_: Publication approval
