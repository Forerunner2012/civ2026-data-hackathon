# What do the bespoke Reims bags add, and when is their drop-dead date?

Type: grilling
Status: resolved

## Question

Ticket 01 made the Reims bags additive-only. This ticket makes "additive" concrete before
effort goes into them.

The rig can collect event-based situations to order: localization, signal behaviour, state
transitions, pattern matching.

What has to be settled:

- **What are they for?** Extra development bags, a second sealed test set, a demo for the
  warm-up, or seed data for a future edition? Each implies very different preparation.
- **The drop-dead date.** After which point does bespoke data stop being included at all? It
  has to sit far enough before the Phase 2 freeze that layouts, manifests and inventories can
  still absorb it.
- Do these bags share the Kashiwa topic and schema structure closely enough to reuse the same
  detector and layouts? If not, the "two inventories" cost from ticket 01 gets much larger.
- Right-hand traffic in France versus left-hand in Kashiwa: an unprotected *right* turn is a
  fundamentally different manoeuvre in the two countries. Does that break reuse of the URT
  detector, and is that a problem or a teaching opportunity?
- Do the same redistribution terms apply, or is this data cleanly CIV-owned? (Cross-check
  ticket 05.)

## Why this is on the frontier

Nothing blocks it, and the drop-dead date needs to exist *now* to be meaningful — a deadline
set after the fact is not a deadline.

## Update after tickets 05, 06 and 08

Schedule is explicitly not an argument here. Two substantive points remain, and they pull in
opposite directions:

**Against including them in the scored challenge:**

- **The handedness problem is confirmed by the publisher**, who describe URT as "equivalent to
  unprotected left turns in Europe". France is right-hand traffic, so the Reims bags hold the
  *mirror* manoeuvre. A URT detector written against Kashiwa will not transfer unchanged, and
  neither will the layouts. That breaks the "same detector, more bags" story.
- **Different personal-data posture.** Kashiwa is a controlled campus with staged actors and a
  participating publisher (ticket 19). Reims bags are open public roads — uninvolved
  pedestrians, real plates, real addresses — governed by whatever Heex arranges for its own rig,
  with no CC BY 4.0 umbrella. Solvable, but it is separate work with a different owner.

**For including them, and worth weighing seriously:**

- The mirrored manoeuvre is arguably the *best possible* transfer exercise. "Your detector works
  in Kashiwa — now make it work where the traffic runs the other way" is exactly the reusable-
  logic lesson §2 is trying to teach, and it is a far better use of the rig than extra bags of
  the same thing.
- It would make the bonus/advanced track genuinely about generalisation rather than about
  bolting an agent onto a working detector.

So the real question is not "in or out" but **which role**: additional dev bags (weak — handedness
breaks reuse), a sealed generalisation test (strong), or a demo asset. Decide the role first.

## Answer

**Out of the 2026 main track. Strong candidate for the deferred extra track.**

### What the recordings actually contain

Inspected at `D:\Bags\Data Hackathon\2025-07-30 Recording sessions`: one continuous session of
**38 minutes**, 1 102 384 messages, ~18 GB, MCAP with a rosbag2 `metadata.yaml`.

```
/zed/zed_node/obj_det/objects                    zed_msgs/msg/ObjectsStamped
/zed/zed_node/imu/data                           sensor_msgs/msg/Imu
/zed/zed_node/rgb/image_rect_color/compressed    sensor_msgs/msg/CompressedImage
/zed/zed_node/point_cloud/cloud_registered       sensor_msgs/msg/PointCloud2
/fix                                             sensor_msgs/msg/NavSatFix
/fix_velocity                                    geometry_msgs/msg/TwistWithCovarianceStamped
/tf  /tf_static                                  tf2_msgs/msg/TFMessage
```

### Why this is a different exercise, not more of the same

This corrects the earlier framing in this ticket, which assumed a shared structure and treated
handedness as the obstacle. The real difference is larger: **there is no Autoware stack and no
vehicle bus.** No `/localization/acceleration`, no `/vehicle/status/*`, no
`/perception/object_recognition/*`. It is a ZED stereo rig plus GNSS on a vehicle.

A Kashiwa detector therefore cannot run here at all. The equivalents exist but must be derived:
yaw rate from `/zed/zed_node/imu/data.angular_velocity.z`, speed from `/fix_velocity`, objects
from `zed_msgs/ObjectsStamped` rather than a boolean flag.

Two further mismatches with the main track: it is **one continuous drive**, not staged scenario
routes, so there is no per-route event structure; and **nothing is labelled**.

### Where it belongs

This is an excellent *"port your logic to a different sensor stack"* exercise — arguably a better
transfer lesson than the handedness one, and exactly the kind of thing rung 2's `derive` stage
exists to make possible. It belongs with the deferred extra track and the organizer demo
(ticket 09), to be designed once the main track is complete.

If it is later promoted, it needs: a right-turn survey of the route to confirm the manoeuvre
occurs often enough, a labelling pass, and its own layout and topic inventory.

## Update - REVERSED after tickets 20, 18 and the transfer grill

**The Reims bags are in the main track, scored as a sealed generalisation test.** This
overturns the resolution above, which put them out of scope.

**Why.** Ticket 20 established a cohort of 30 experienced practitioners. Ticket 18 deliberately
made the Kashiwa core a threshold-plus-timing exercise and recorded "detection no longer separates
teams on cleverness" as an accepted cost - tolerable for a mixed room, not for this one. The
Kashiwa core is now the warm-up, and the difficulty moves into transfer.

**The arc.** Manual analysis first, so the room feels how tedious finding events by hand is; then
`civ` is introduced as the facilitator; then the payoff is how easily evidence can be collected
across *two structurally different datasets* - different sensor stack, different topics, mirrored
driving rules.

**What is labelled: left turns.** In right-hand traffic the manoeuvre that crosses oncoming
traffic is the left turn. The publisher describes URT-Kashiwa as "equivalent to unprotected left
turns in Europe". So the transfer is not a sign flip - it requires understanding that the event is
defined by *conflict with oncoming traffic*, not by the word "right". A participant who copied a
threshold fails; one who understood the event adapts. See ticket 18.

**What this costs, all now in scope:**

- A labelling pass on Reims data. Ticket 24 confirms enough events and fixes the split:
  chunks `_0`–`_4` development, `_5`–`_8` sealed with 9 clear left turns.
- A second evaluator calibration on a different sensor stack - ticket 16.
- Distribution of a Reims subset - ticket 17.
- A topic inventory and viewer layout for the ZED/GNSS stack, which shares nothing with Autoware.
