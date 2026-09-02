/**
 * Content shared by every audience. Anything placed here is served to both the
 * participant and the organizer route, so it must be safe for participants.
 */

export const eventName = "CIV 2026 Data Hackathon";
export const workingTitle = "Data Detective — from raw bag to defensible proof";

/** The one-line framing both audiences see. */
export const premise =
  "A three-hour ROS 2 data investigation where experienced practitioners turn an observation into reusable event logic, transfer it across different recordings, challenge its failures, and connect evidence to action.";

export type NavLink = { href: string; label: string };
