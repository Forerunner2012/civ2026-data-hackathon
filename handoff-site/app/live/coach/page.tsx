import type { Metadata } from "next";
import { Footer, Topbar } from "../../_components/chrome";
import { liveSnapshotAt, requestClockFromValue } from "../../_content/live-store.server";
import { CoachConsole } from "./coach-console";

export const metadata: Metadata = {
  title: "CIV 2026 — coach advance",
  description: "Local next-only control for the CIV session page.",
  robots: { index: false, follow: false },
};

export default async function CoachPage({
  searchParams,
}: {
  searchParams: Promise<{ now?: string | string[] }>;
}) {
  const rawNow = (await searchParams).now;
  const requestedNow = Array.isArray(rawNow) ? rawNow[0] : rawNow;
  const controlledNow =
    process.env.LIVE_ALLOW_CONTROLLED_CLOCK === "true" ? requestedNow : undefined;

  return (
    <main className="live-page coach-page">
      <Topbar pill="Coach · local only" />
      <CoachConsole
        initialSnapshot={liveSnapshotAt(requestClockFromValue(requestedNow))}
        controlledNow={controlledNow ?? null}
      />
      <Footer note="Next-only local control. There is no hold, relock, delay, or reverse action." />
    </main>
  );
}
