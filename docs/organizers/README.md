# Organizer guide

Prepare a session that takes participants from local recordings to a reproducible metadata-only
submission. Start with this checklist, then open the linked procedure for each step. CIV 2026
acceptance records describe the original event; another session needs its own permissions,
qualified inputs, machine checks and release approval.

## Prepare the session

1. Name the session owner, human event reviewer, data custodian and handout owner. Record the
   intended event definitions, dataset membership, timing and access boundaries. Use
   [Make it your own](../../MAKE-IT-YOUR-OWN.md) and the [settings reference](../session-settings.md)
   for the existing edit locations.
2. Verify recording and image permissions, attribution, retention and deletion requirements for
   the intended audience. Record exact source hashes and approved products. Use the
   [dataset authority record](../phase3/two-dataset-authority.md),
   [camera-context procedure](../phase5/camera-context-candidate.md) and
   [legal qualification procedure](../phase5/legal-risk-acceptance.md) as references. Historical
   permissions do not authorize another session or public imagery.
3. Prepare reviewed labels through the [acquisition skill](../../.agents/skills/civ-label-acquisition/SKILL.md)
   and [local review procedure](../phase3/label-review.md). EventSpecs propose intervals; a human
   decides their contextual meaning, records reasons and uncertainty, reviews missed events, and
   signs complete coverage after the final edit. Changing an input identity requires a new run
   and review revision. Preserve compatible earlier approvals within their exact scope.
4. Qualify complete practice coverage for each designated scoring source or chunk. Explicitly
   select every relevant approved interval. Warm-up and development product reviews export
   practice labels and retain their audit locally; they cannot export sealed truth. Prepare and
   audit approved sealed packs separately with the [organizer label-pack procedure](../phase3/organizer-label-packs.md).
   A successful export does not authorize a handout or publication. Record the permitted
   practice-pack identities, handout timing and owner before sharing them.
5. Build the attendee kit from verified inputs using the
   [inventory procedure](../phase4/participant-kit-inventory.md) and
   [assembly procedure](../phase5/camera-context-candidate.md). Keep canonical Markdown and its
   dependent summaries consistent; assemble guide copies through the existing inventory, rather
   than editing generated copies. Keep recordings, imagery, sealed packs and review progress out
   of Git. Review the [kit entry point](../../kit/README.md) from a participant's perspective.
6. Rehearse [the quickstart](../quickstart.md) on the target machines. Verify both dataset
   workflows, exact-source practice scoring, private scoring, submission reproduction and
   metadata-only bundles. Follow [workstation qualification](../phase5/workstation-qualification.md)
   and [release qualification](../phase5/release-freeze.md). A prior Windows or offline result
   does not qualify another machine or platform. Freeze only the inputs and capabilities that
   the current session has actually qualified.

## Run the session

1. Give participants their kit and confirmed instructions. Use the
   [website development guide](../../handoff-site/README.md) for local participant/live operation.
   Organizer, coaching and unreleased solution routes remain internal and are excluded from the
   public participant build. Keep private material off participant screens.
2. Let participants own their hypotheses and EventSpecs. Coach through evidence inspection and
   failure analysis; do not replace their decisions with an organizer solution. Use the
   [original facilitation and recovery runbook](../phase4/organizer-ops-jury-acceptance.md) as a
   reference, with the current session's recorded schedule and qualified recovery options.
3. Release only the authorized practice references at the recorded checkpoint. Participants
   score the exact matching source, explain false positives and missed events, and submit the
   [participant contract](../reference/participant-contracts.md). Recordings, evidence clips,
   labels and review audit stay outside the metadata-only submission bundle.

## Evaluate and finish

1. Follow [Score a full cohort](cohort-scoring.md) from its required-input checklist through
   plan setup, track-specific intake, replay, and result checks. Use its three-track example
   plan as the starting point for the session. Read the [scoring reference](../reference/scoring.md)
   for matching, aggregation, and pending point components. Keep truth and replay artifacts
   private, and inspect sealed metrics separately. Cohort outputs are nonofficial.
2. Apply the recorded jury and feedback process from the
   [organizer operations reference](../phase4/organizer-ops-jury-acceptance.md). Retain the local
   operational audit, with only the approved participant-facing results released.
3. Check the current release evidence, permissions and notice requirements before any handout,
   hosted preview or public release. Dataset qualification does not authorize deployment,
   repository visibility changes, publication or history rewriting. Follow the current
   [release gate](https://github.com/Forerunner2012/civ2026-data-hackathon/issues/68) and
   [payload/history clearance](https://github.com/Forerunner2012/civ2026-data-hackathon/issues/119).
   Complete the recorded retention and deletion steps.

## Local tools

From the repository root, use project mode:

```sh
uv sync --locked
```

The implemented loopback review interface supports exact interval edits, undo, save/reload,
whole-source signal/image inspection and independent candidate-profile comparison. It rejects
stale inputs and unsupported exclusions, and clears approval or completeness after relevant
edits. Use the exact commands in the [review procedure](../phase3/label-review.md); keep reviewer
identity, review progress and output paths local. Detection proposals never create truth.

The synthetic acquisition example exercises the production review and scoring consumers without
using recordings or real labels:

```sh
uv run python .agents/skills/civ-label-acquisition/scripts/synthetic_demo.py
```

Its fixed fixture decisions are tests, not a human approval method. Real review still needs the
named reviewer, permitted-use statement and exact source/spec/resource/context bindings.

## Presentation material

Use the [maintained briefing and submission checklist](../presentations/README.md) for the approved 13-slide introduction and separate end-of-hackathon reminder. Edit the HTML, prepare the source-bound illustrations and verify generated decks locally. Include only reviewed artifacts in the approved kit; source presence does not establish a hosted download or kit delivery.
