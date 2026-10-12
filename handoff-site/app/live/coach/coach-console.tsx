"use client";

import { useMemo, useState } from "react";
import type { LivePublicSnapshot } from "../../_content/live-state";

export function CoachConsole({
  initialSnapshot,
  controlledNow,
}: {
  initialSnapshot: LivePublicSnapshot;
  controlledNow: string | null;
}) {
  const [token, setToken] = useState("");
  const [snapshot, setSnapshot] = useState(initialSnapshot);
  const [message, setMessage] = useState("");
  const [pending, setPending] = useState(false);
  const apiPath = useMemo(
    () => `/api/live${controlledNow ? `?now=${encodeURIComponent(controlledNow)}` : ""}`,
    [controlledNow],
  );

  async function refresh() {
    try {
      const response = await fetch(apiPath, { cache: "no-store" });
      if (!response.ok) {
        return false;
      }
      setSnapshot((await response.json()) as LivePublicSnapshot);
      return true;
    } catch {
      return false;
    }
  }

  async function advance() {
    setPending(true);
    try {
      const response = await fetch(apiPath, {
        method: "POST",
        headers: {
          authorization: `Bearer ${token}`,
          "content-type": "application/json",
        },
        body: JSON.stringify({
          requestId: crypto.randomUUID(),
          observedStageId: snapshot.stage.id,
        }),
      });
      const body = (await response.json()) as LivePublicSnapshot & {
        error?: string;
        outcome?: string;
      };
      if (response.ok) {
        setSnapshot(body);
        setMessage(
          body.outcome === "already-applied" ? "Advance already applied." : "Room advanced once.",
        );
      } else {
        await refresh();
        setMessage(body.error ?? "Advance failed. State refreshed; check it and try again.");
      }
    } catch {
      const refreshed = await refresh();
      setMessage(
        refreshed
          ? "Advance status was unclear. State refreshed; check it before trying again."
          : "Room control is unreachable. Reload after the local server or network recovers.",
      );
    } finally {
      setPending(false);
    }
  }

  return (
    <section className="coach-console">
      <p className="kicker"><span /> AUTHORIZED ROOM CONTROL</p>
      <h1>Release the<br /><em>next checkpoint</em></h1>
      <p className="lede">
        Check the current room stage, then advance it when the room is ready. Scheduled advancement continues automatically. Released guidance cannot be withdrawn.
      </p>
      <div className="coach-card">
        <label>
          Coach token
          <input
            type="password"
            autoComplete="off"
            value={token}
            onChange={(event) => setToken(event.target.value)}
          />
        </label>
        <div>
          <span>CURRENT ROOM STATE</span>
          <b>{snapshot ? `${snapshot.stage.beat} · ${snapshot.stage.title}` : "Loading…"}</b>
        </div>
        <button type="button" disabled={!token || pending} onClick={() => void advance()}>
          {pending ? "Advancing…" : "Advance room to next state"}
        </button>
        <p role="status">{message}</p>
      </div>
      <aside className="coach-pace-reference">
        <span>DISPLAY ASSISTANCE</span>
        <h2>Keep the room on the evidence chain</h2>
        <p><b>Current attendee action:</b> {snapshot.stage.action}</p>
        <p><b>Expected by now:</b> {snapshot.stage.shouldHave}</p>
        <p><b>Recovery line to display:</b> {snapshot.stage.ifYouDont}</p>
        <code>doctor → inspect → sample → submission-init → detect → clip → score → report</code>
      </aside>
    </section>
  );
}
