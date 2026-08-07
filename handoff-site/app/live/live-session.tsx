"use client";

import { useEffect, useMemo, useState } from "react";
import type { LivePublicSnapshot } from "../_content/live-state";

function countdown(nowMs: number, nextStartMs: number | null): string {
  if (nextStartMs === null) {
    return "CLOSED";
  }
  const remaining = Math.max(0, Math.ceil((nextStartMs - nowMs) / 1_000));
  const minutes = Math.floor(remaining / 60);
  const seconds = remaining % 60;
  return `${String(minutes).padStart(2, "0")}:${String(seconds).padStart(2, "0")}`;
}

export function LiveSession({
  initialSnapshot,
  controlledNow,
  submissionFormUrl,
}: {
  initialSnapshot: LivePublicSnapshot;
  controlledNow: string | null;
  submissionFormUrl: string | null;
}) {
  const [snapshot, setSnapshot] = useState(initialSnapshot);
  const [nowMs, setNowMs] = useState(initialSnapshot.nowMs);
  const apiPath = useMemo(
    () => `/api/live${controlledNow ? `?now=${encodeURIComponent(controlledNow)}` : ""}`,
    [controlledNow],
  );

  useEffect(() => {
    if (controlledNow) {
      return;
    }
    const timer = window.setInterval(() => setNowMs(Date.now()), 1_000);
    return () => window.clearInterval(timer);
  }, [controlledNow]);

  useEffect(() => {
    let active = true;
    async function refresh() {
      const response = await fetch(apiPath, { cache: "no-store" });
      if (response.ok && active) {
        const next = (await response.json()) as LivePublicSnapshot;
        setSnapshot(next);
        if (controlledNow) {
          setNowMs(next.nowMs);
        }
      }
    }
    void refresh();
    const timer = window.setInterval(() => void refresh(), 3_000);
    return () => {
      active = false;
      window.clearInterval(timer);
    };
  }, [apiPath, controlledNow]);

  const stage = snapshot.stage;

  return (
    <>
      <section className="live-hero" id="current">
        <div className="live-stage-copy">
          <p className="kicker">
            <span /> 3 September · {stage.time} JST · {stage.beat}
          </p>
          <div className="live-progress" aria-label={`Stage ${snapshot.stageIndex + 1} of 9`}>
            <i style={{ width: `${((snapshot.stageIndex + 1) / 9) * 100}%` }} />
          </div>
          <p className="live-stage-number">CURRENT STAGE · {snapshot.stageIndex + 1}/9</p>
          <h1>{stage.title}</h1>
          <p className="lede">{stage.action}</p>
          {snapshot.advancedEarly ? (
            <p className="live-advanced" role="status">Released early by the room lead</p>
          ) : null}
        </div>

        <aside className="live-countdown" aria-live="polite">
          <span>{snapshot.nextStartMs === null ? "SESSION STATE" : "NEXT SCHEDULED CHANGE"}</span>
          <b>{countdown(nowMs, snapshot.nextStartMs)}</b>
          <small>{snapshot.nextStartMs === null ? "Submission cutoff reached" : "The page advances automatically"}</small>
        </aside>
      </section>

      <section className="live-checks" aria-label="Current recovery checks">
        <article>
          <span>BY NOW YOU SHOULD HAVE</span>
          <p>{stage.shouldHave}</p>
        </article>
        <article>
          <span>IF YOU DON&apos;T</span>
          <p>{stage.ifYouDont}</p>
        </article>
      </section>

      {stage.reportPrompt ? (
        <section className="live-report-prompt" role="note">
          <span>REPORT PROMPT</span>
          <p>{stage.reportPrompt}</p>
        </section>
      ) : null}

      <section className="live-guidance" id="guidance">
        <div className="section-heading compact">
          <div>
            <span>UNLOCKED SO FAR</span>
            <h2>Hints and tips you may use now</h2>
          </div>
          <p>Everything below is cumulative. Nothing already visible can be held, relocked, or reversed.</p>
        </div>
        <ol>
          {snapshot.unlockedGuidance.map((item, index) => (
            <li key={`${index}-${item}`}>
              <span>{String(index + 1).padStart(2, "0")}</span>
              <p>{item}</p>
            </li>
          ))}
        </ol>
      </section>

      <section className="live-submission" id="submission">
        <div>
          <span>SUBMISSION · METADATA ONLY</span>
          <h2>Submit metadata bundle</h2>
          <ol>
            <li>Run <code>civ report working</code>.</li>
            <li>Copy the printed SHA-256 exactly.</li>
            <li>Send your identity, hash, and unchanged <code>submission.zip</code>.</li>
          </ol>
          <p>Limit: 12 MiB per bundle and 8 MiB per metadata artifact.</p>
        </div>
        <div className="live-submission-action">
          {submissionFormUrl ? (
            <a
              className="primary-button"
              href={submissionFormUrl}
              target="_blank"
              rel="noreferrer"
            >
              Open submission form <span>→</span>
            </a>
          ) : (
            <p role="status">The online form is not configured. Use the USB fallback now.</p>
          )}
          <p>
            Keep the form confirmation with its submission reference. You may submit again; the last
            valid response received by 12:30 JST is authoritative.
          </p>
          <p>
            <b>USB fallback:</b> hand over the identical <code>submission.zip</code>, your identity,
            and the same printed hash. Do not unpack or reformat it.
          </p>
        </div>
      </section>

      <section className="live-fallback" id="fallback">
        <div>
          <span>NETWORK LOSS</span>
          <h2>Keep one safe page on every desk.</h2>
        </div>
        <p>
          Open the static session fallback from the SSD if this page stops refreshing. It contains
          the sanctioned recovery state, no organizer control, and no worked answer.
        </p>
        <a className="primary-button" href="/session-fallback.html">
          Open static fallback <span>→</span>
        </a>
      </section>
    </>
  );
}
