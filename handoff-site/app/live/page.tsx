import type { Metadata } from "next";
import { Footer, Topbar } from "../_components/chrome";
import { liveSnapshotAt, requestClockFromValue } from "../_content/live-store.server";
import { LiveSession } from "./live-session";

export const metadata: Metadata = {
  title: "CIV 2026 — live session",
  description: "The current CIV data-hackathon beat, recovery guidance, and countdown.",
  robots: { index: false, follow: false },
};

const nav = [
  { href: "#current", label: "Current beat" },
  { href: "#guidance", label: "Unlocked guidance" },
  { href: "#fallback", label: "Offline fallback" },
];

export default async function Live({
  searchParams,
}: {
  searchParams: Promise<{ now?: string | string[] }>;
}) {
  const rawNow = (await searchParams).now;
  const requestedNow = Array.isArray(rawNow) ? rawNow[0] : rawNow;
  const controlledNow =
    process.env.LIVE_ALLOW_CONTROLLED_CLOCK === "true" ? requestedNow : undefined;
  const snapshot = liveSnapshotAt(requestClockFromValue(requestedNow));

  return (
    <main className="live-page">
      <Topbar nav={nav} pill="Live · participant" />
      <LiveSession initialSnapshot={snapshot} controlledNow={controlledNow ?? null} />
      <Footer
        note="This local session page advances automatically. The participant-safe static fallback is available for network loss."
        backTo="#current"
      />
    </main>
  );
}
