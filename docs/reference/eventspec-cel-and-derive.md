# EventSpec CEL and derivation rules

These rules apply to the stable `civ.eventspec/v1` contract. Issue #16 established the behavior; issue #20 promoted the stable identifier.

The participant EventSpec uses the stable `civ.eventspec/v1` contract after the atomic stable-contract
promotion. This document defines its expression and derivation behavior. The executable conformance source is
`tests/fixtures/cel/conformance.yaml`, pinned to `cel-python==0.5.0`.

## CEL condition subset

Every condition is evaluated after all declared signals and derivations have produced a value. The
condition must return a CEL boolean.

The participant activation accepts only:

- `bool`;
- `int`; and
- finite `double`.

Null, strings, collections, objects, and non-finite doubles are rejected before evaluation with the
input name and message timestamp. Integers and doubles are not implicitly coerced. Use `int(...)` or
`double(...)` when a conversion is intentional. Comparing a boolean literal with a non-boolean
binding is rejected rather than inheriting Python's `bool`/`int` equality behavior.

The frozen operator subset used by the reference paths is:

- logical `&&`, `||`, and `!`;
- comparisons `==`, `!=`, `<`, `<=`, `>`, and `>=`;
- numeric `+`, `-`, unary `-`, and `*`; and
- explicit `int(...)` and `double(...)` conversions.

Division, modulus, membership, ternary expressions, and other functions are rejected with a
correction. Missing names, parse failures, mixed integer/double operations, and non-boolean results
also produce deterministic participant-facing diagnostics. Dataset signs, thresholds, topic names,
and field names remain EventSpec data rather than shared-code branches.

## Declarative derivations

`derive` is an optional top-level mapping. A derived name must be unique across signals and other
derivations. A derivation may reference signals or other derived names; dependencies are
topologically ordered independently of YAML declaration order. Unknown inputs and cycles are
rejected while loading the EventSpec.

### `ewma`

```yaml
derive:
  speed_smooth: {from: speed, op: ewma, alpha: 0.5}
```

`from` names exactly one numeric input. `alpha` is finite and satisfies `0 < alpha <= 1`. The first
output equals the first input. Later outputs use:

```text
alpha * current + (1 - alpha) * previous
```

### `magnitude`

```yaml
derive:
  speed: {from: [velocity_x, velocity_y, velocity_z], op: magnitude}
```

`from` lists at least two numeric inputs. The output is the Euclidean magnitude
`sqrt(sum(input * input))`.

Boolean, non-numeric, and non-finite inputs are invalid for both operations. A non-finite output is
also rejected. Derivations update deterministically when one of their sources changes, and CEL is
not evaluated until every signal and derivation has an initial value.

Issue #17 extends this vocabulary with the local-resource `min_distance_to` operation documented in
`docs/reference/eventspec-resources.md`. It produces a finite distance scalar for the same CEL
activation; resource parsing and geometry do not enlarge the CEL value-type subset.

## Timing and evidence

Derivations change only the values presented to the existing interval detector. `min_duration`,
`merge_gap`, and `max_duration` retain their candidate-contract behavior. Evidence topics remain an
explicit non-empty EventSpec declaration. Derived values are recorded with bound signal values in
the event trigger values; they do not introduce dataset-specific decoders or evidence topics.

## Verification boundary

Human-authored CEL cases cover the numeric, boolean, conversion, handedness, and planned resource
distance expressions used by the two reference paths. Public `civ detect` tests cover EWMA,
magnitude, dependency ordering, the Reims binding/handedness boundary, invalid definitions,
cycles, duplicate names, and non-finite behavior.
