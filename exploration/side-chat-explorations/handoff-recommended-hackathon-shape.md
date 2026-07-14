Yes. The market shows a clear progression from simple filtering to reusable engineering knowledge. For an awareness-oriented hackathon, participants should experience that progression without implementing a complete rules engine.

## Types of detection and investigation

| Level | Example | What students learn |
|---|---|---|
| Metadata filtering | Vehicle X, software v3, last week | Locating potentially relevant recordings |
| Single comparison | `acceleration < -3` | Mapping a physical situation to a signal |
| Boolean composition | `turning AND object_detected` | Combining partial evidence |
| Derived signal | derivative, norm, moving average | Raw values are not always directly actionable |
| Temporal condition | condition sustained for 2 s | Distinguishing noise from behaviour |
| State transition | `AUTONOMOUS → DISENGAGED` | Detecting operational changes |
| Sequence | braking, then disengagement within 5 s | Expressing scenarios rather than isolated points |
| Pattern similarity | Find signals shaped like this example | Finding behaviour without an explicit threshold |
| Statistical anomaly | Deviation from previous runs/baseline | Detecting unexpected rather than predefined events |
| Root-cause investigation | Compare signals before an event | Forming and testing causal hypotheses |
| Automated action | Match → annotate, clip, notify or process | Connecting detection to an engineering workflow |

Root-cause analysis is not itself another filter. It is a process:

```text
detect symptom
→ open synchronized context
→ compare related signals and previous runs
→ formulate hypothesis
→ test it
→ preserve evidence
→ optionally encode the finding as a new rule
```

## What representative tools offer

| Tool | Relevant capabilities | Main lesson for CIVE |
|---|---|---|
| **Foxglove** | Message-field comparisons; condition groups where conditions are ANDed and groups ORed; string, numeric and boolean operators; derived values such as norm, delta and derivative; saved searches and timeline matches. [Search documentation](https://docs.foxglove.dev/docs/data/search), [message-path syntax](https://docs.foxglove.dev/docs/visualization/message-path-syntax) | A friendly way to move from data browsing to reusable search, but temporal sequences and sophisticated detection still need scripts or another engine. |
| **Rerun** | Filters by episode, entity and time; DataFusion expressions, joins, aggregations, time alignment and conversion to dataframes; synchronized 2D/3D, logs and time-series views. [Dataframe queries](https://rerun.io/docs/concepts/query-and-transform/dataframe-queries), [view operations](https://rerun.io/docs/howto/query-and-transform/view_operations) | Strong evidence and investigation surface. It provides query primitives, not a complete declarative anomaly/rules engine. |
| **Roboto** | Custom processing Actions; time-anchored events; automatic execution after ingestion; native one- or multi-dimensional signal-similarity matching, including speed-invariant matching; read-only AI-assisted exploration. [Actions](https://docs.roboto.ai/learn/actions.html), [signal similarity](https://docs.roboto.ai/reference/python-sdk/roboto/analytics/index.html), [AI Chat](https://docs.roboto.ai/user-guides/using-ai-chat.html) | Particularly interesting beyond thresholds: students can select an example manoeuvre and search for similar occurrences. |
| **Sift** | CEL rules over multiple channels; `&&`, `||`, comparisons and derived channels; rolling windows and stateful functions; reusable/versioned functions; live and historical execution; annotations, reports and investigations. [Rules](https://docs.siftstack.com/learning-path/tutorial-4/step-1), [calculated channels](https://docs.siftstack.com/documentation/transform/calculated-channels/overview) | The richest inspiration for a progressive EventSpec: simple predicate → derived signal → temporal rule → reusable engineering knowledge. |
| **Formant** | Threshold triggers, multiple bit conditions using AND/OR, periodic or state-transition triggering, then alerts, events, robot commands or configuration changes. [Event configuration](https://docs.formant.io/docs/getting-started-create-an-event-and-configure-notifications) | Demonstrates that detection is connected to an operational response, not merely a timestamp. |
| **PlotJuggler** | Derivative, moving average, integration and other transforms; multi-input/single-output Lua functions; reusable layouts; ROS bag and live ROS integration. [Official repository](https://github.com/PlotJuggler/PlotJuggler) | Excellent for manually discovering and validating conditions, but not by itself a fleet-scale event-management system. |

Foxglove, Roboto, Sift and Formant should primarily be treated as product-design references. Their platform capabilities should not be assumed to be open source. PlotJuggler is OSS, while Rerun provides an OSS core with additional platform capabilities.

## Recommended hackathon shape

Given the **conscientisation** objective, I would not ask every team to invent an advanced detector. Instead, expose a “rule ladder”:

1. **Observe:** find one occurrence manually.
2. **Formalize:** express it as one comparison.
3. **Contextualize:** add a second condition using AND or OR.
4. **Temporalize:** require persistence, transition or ordering.
5. **Scale:** execute the rule automatically across several bags.
6. **Challenge:** inspect a false positive or false negative.
7. **Transfer:** explain how the same process would apply to their professional project.

A three-hour version could be:

- 30 min: guided data exploration;
- 30 min: simple condition;
- 45 min: compound or temporal condition;
- 30 min: automated batch execution;
- 30 min: false-positive/root-cause investigation;
- 15 min: professional transfer pitch.

The central deliverable should therefore not just be “the best detector.” Each team should present:

- the engineering question;
- available and missing data;
- the rule or matching method chosen;
- one piece of supporting evidence;
- one failure or ambiguity;
- how it would scale to acquisition, validation or operations;
- what action should follow a match.

This would raise awareness of the complete data workflow while still allowing advanced students to explore temporal rules, similarity search, anomaly detection or agents.

---
