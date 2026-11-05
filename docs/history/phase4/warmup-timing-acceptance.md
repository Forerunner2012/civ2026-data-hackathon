# Phase 4 Kashiwa warm-up timing lesson

Status: **accepted for participant teaching**

Recorded: 2026-08-29 · Human organizer approval: **approved**

This gate validates one deliberately non-answer example for the 10:20 Formalize beat. It teaches
the difference between matching samples and normalized events on the real participant warm-up
product. It does not teach, name, or approximate the scored manoeuvre detector.

## Participant-visible input

The bounded run used the accepted signals-only Kashiwa warm-up product:

- product: `KSH-64ac27cd029b-signals.mcap`;
- SHA-256: `942a12299a80500ea780a1cfae5e59d0f3ef5b481ed7741db8d07968a4d82803`;
- observed acceleration window: 84.584 seconds and 3,392 messages; and
- inspected signals: longitudinal acceleration, brake-pedal feedback, and speed feedback only.

No label, scored interval, held-back identity, private route, organizer path, or handedness signal
was read. The source product, authoring scripts, EventSpec working copy, and runtime output remained
outside git.

## Non-answer EventSpec

The checked-in `examples/kashiwa/deceleration_timing.yaml` uses a deliberately loose longitudinal
deceleration condition:

```yaml
condition: longitudinal_acceleration <= -0.25
timing:
  min_duration: 0.5s
  merge_gap: 0.5s
  max_duration: 10s
```

This is a teaching example, not a scoring recommendation. It is intentionally weak enough to make
one semantic failure inspectable.

The participant-reproducible bounded command is:

```sh
civ detect examples/kashiwa/deceleration_timing.yaml \
  data/KSH-64ac27cd029b-signals.mcap --output work/timing-lesson --dry-run
```

The recorded run used `uv run civ detect` from the source checkout with the same arguments.
It returned `{"dry_run":true,"event_count":4}` on Windows 11 Pro amd64 with CPython 3.12.13 and
`civ-workshop` 0.1.0.

## Observed normalization

The authoring scan preserved all three stages rather than substituting illustrative numbers:

| Stage | Observed count | Meaning |
|---|---:|---|
| Condition matches | 189 | individual acceleration samples where the condition is true |
| Gap-merged candidates | 14 | intervals after joining hits no more than 0.5 seconds apart |
| Duration-qualified events | 4 | candidates lasting at least 0.5 seconds |

The older design draft's illustrative `41 -> 6` did not reproduce and must not appear in final
participant copy. A stronger `-0.75` condition produced `60 -> 1`, but that retained interval had a
real brake response and did not supply the required honest ambiguity. These outcomes are retained
here so the chosen example is not mistaken for the only threshold tried or a scoring optimum.

## Honest ambiguity

One of the four duration-qualified events has brake-pedal maximum `0`. During it, speed feedback
stays near zero and negative (`-0.29` to `-0.04` in the recorded values). The acceleration-only
condition therefore cannot defensibly call it hard braking: it could reflect low-speed motion or a
measurement disturbance.

That is the approved narrative. `timing` fixes over-counting; it does not prove that a condition
means what its author intended. Participants should normalize first, then inspect evidence and
revise the condition.

## Assigned page beat

At the 10:20 Formalize beat, the progressive page may use only these layers:

- **Expectation:** your condition fires; matching samples are not yet events.
- **Hint:** run the non-answer deceleration example on the real warm-up product and compare matches
  with the dry-run event count.
- **Tip:** the real trace produced `189 -> 14 -> 4`; `merge_gap` joins nearby hits and
  `min_duration` rejects short candidates. One retained event still has no brake response, so
  inspect meaning as well as count.

No during-session layer may substitute the scored detector, disclose handedness, or turn this
example into a runnable scored solution. The human organizer explicitly approved this count and
ambiguity interpretation before final participant authoring.

## Prototype provenance

The throwaway click-through remains off main on branch `prototype/issue-40-warmup-timing`, commit
`8e0a482ada5272c68409e16533709f1f96ffa7d7`, HTML SHA-256
`25ba7607234cd310e5ba10bfeeb722ce284f5738d1487efc20500a7fb8880ef1`. Main retains only the
validated EventSpec and this redacted decision record.
