> Historical planning. Follow the [archive index](../README.md) for current guides and record boundaries.

Clean room engineering
of the Heex data pipelines with more simplification as we don't really need the level of scale and depth we had at Heex
---

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

---
Theme of this CIV 2026
is abput workflows
like last year
but now overlaid with AI
not because it is a trend
because it is an enablers
Give you
but you ultimately approved

Intiial process it about:

- Make few slides to detail the approach for data collection and
- Automated robotics analytics, from first log to root cause. Automate your robotics data analysis. Go from raw logs to root cause.

Ai layering:

- Let AI agents debug your robotics logs so you can spend less time hunting and more time building.

Detail what the stack is currently (process)

- Fully online
- Partially offline -> computation offloaded
- Triage on device -> Learning offloaded

<https://docs.roboto.ai/learn/concepts.html>

---
Use plotjuggler 4.0
<https://github.com/PlotJuggler/PlotJuggler/tree/main-4.x>
