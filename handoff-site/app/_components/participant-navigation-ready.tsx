"use client";

import { useEffect } from "react";
import { usePathname } from "next/navigation";

/** Start the classic enhancement only after the online page has hydrated. */
export function ParticipantNavigationReady() {
  const pathname = usePathname();
  useEffect(() => {
    document.documentElement.dataset.participantNavigationHydrated = "true";
    document.dispatchEvent(new Event("civ:participant-navigation-ready"));
  }, [pathname]);
  return null;
}
