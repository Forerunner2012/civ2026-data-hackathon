Yes—but the “vertical-slice prototype” is first an organizer exercise used to validate the future participant experience.

Participants would perform the same reasoning, but they would not rebuild all the infrastructure.

### Organizer prototype

Before the hackathon, you prove that this complete journey works on one bag:

```text
MCAP → exploration → detector → batch execution → evidence clip → score
```

This produces the prepared CLI, container, schemas, sample solution and automatic evaluator.

### Participant experience

Participants would then:

1. Explore one development bag manually.
2. Identify relevant topics, fields and time windows.
3. Formulate a detection hypothesis.
4. Write an `EventSpec` or a small detector function.
5. Run it automatically over multiple bags.
6. Review false positives, missed events and extracted clips.
7. Improve the detector and rerun it.
8. Submit their detector, results and explanation.

The scaling is automated:

```text
# Participant designs one detector
cive detect detector.yaml dataset/dev/

# The tool applies it to every bag
# and produces:
events.jsonl
evidence/*.mcap
metrics.json
run-manifest.json
```

Participants should not need to implement:

- MCAP parsing;
- ROS message discovery;
- batch scheduling;
- clip extraction;
- hashing and provenance;
- scoring infrastructure.

Their work is the valuable part: understanding the data, designing the event logic, validating it at scale and explaining the evidence.

For a three-hour hackathon, I would provide the complete pipeline and ask participants to implement only the detector and analysis. For a full-day format, advanced teams could also extend the pipeline or add agentic investigation.

---

>
> When you say "implement only the detector and analysis", do you mean the extraction/collection rules or the system that runs the rules as well ?
>

I mean the participants implement the extraction/collection logic, while the system that executes that logic is provided by the organizers.

Participants own:

- signals and fields to inspect;
- preprocessing or derived features;
- thresholds or model inference;
- temporal combinations such as AND, duration and ordering;
- deduplication/debounce parameters;
- evidence-window duration;
- topics to retain in the extracted clip;
- statistical analysis and interpretation.

The organizer provides:

- MCAP/ROS decoding;
- iteration over every bag;
- time synchronization;
- detector execution;
- clip generation;
- standardized outputs and provenance;
- scoring against hidden labels.

The contract could support either configuration:

```yaml
condition:
  all:
    - acceleration: {lt: -3.0}
    - speed: {gt: 2.0}
evidenceWindow:
  before: 4s
  after: 6s
topicsToCollect:
  - /localization/acceleration
  - /vehicle/status/velocity
  - /sensing/camera/front
```

Or custom code:

```python
def detect(signals) -> list[EventCandidate]:
    # Participant-owned detection logic
    ...
```

The provided runner then executes it:

```text
cive detect participant_detector.py dataset/
```

So they implement something executable—not merely write an explanation—but they do not spend the hackathon building the generic execution engine.

Extending the runner could be an advanced bonus track, but making it mandatory would shift the challenge from data investigation toward infrastructure development.
