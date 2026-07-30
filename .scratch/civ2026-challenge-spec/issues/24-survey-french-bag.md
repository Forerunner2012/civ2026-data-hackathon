# Does the French recording contain enough of the target manoeuvre?

Type: task
Status: open

## Question

Tickets 14 and 18 now depend on labelling **left turns** — the manoeuvre that crosses oncoming
traffic in right-hand traffic — in the French-city recording, and **scoring** teams against that
sealed set.

Nobody has confirmed the recording contains enough of them.

What is known: one continuous session of ~38 minutes, 1 102 384 messages, ~18 GB, at
`D:\Bags\Data Hackathon\2025-07-30 Recording sessions`. Yaw rate is available from
`/zed/zed_node/imu/data.angular_velocity.z`; speed from `/fix_velocity`; objects from
`/zed/zed_node/obj_det/objects`.

Establish:

- **How many left turns occur**, and how many are at junctions where oncoming traffic is genuinely
  crossed rather than a quiet turn or a roundabout exit.
- Their distribution across the drive — clustered or spread.
- Whether the count supports a development/sealed split at all, or whether the whole session must
  be the sealed set with no French development data for teams to iterate against.
- Whether `obj_det/objects` carries anything usable for judging conflict, or whether "unprotected"
  stays scenario context here too, as ticket 18 decided for Kashiwa.
- Whether the second, small MCAP in that folder is a fragment or a separate session.

## Why this blocks

A sealed generalisation test cannot rest on an assumption about event counts. If the answer is
"four left turns in 38 minutes", the transfer task needs redesigning — more collection, a
different manoeuvre, or a qualitatively judged rather than scored transfer.

## Method

Decode `/zed/zed_node/imu/data` and `/fix_velocity`, integrate heading, and count sustained
positive yaw-rate excursions above a walking-pace speed floor. Needs `mcap` and
`mcap-ros2-support`; the bag carries its own schemas, so no ROS installation is required.
