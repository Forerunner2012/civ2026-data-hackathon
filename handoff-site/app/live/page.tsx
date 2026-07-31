import type { Metadata } from "next";
import { Footer, Topbar } from "../_components/chrome";
import { rules, status, steps, stillToBuild } from "../_content/live.server";

/**
 * Placeholder for the day's live page — the one participants keep open.
 *
 * Deliberately absent from `public-source/`, so it never reaches a production
 * build. Its job today is to let an organizer read the session minute by minute
 * and see what participants are expected to be doing with the recordings.
 */

export const metadata: Metadata = {
  title: "CIV 2026 — the day, live (placeholder)",
  description: "Preview of the page participants keep open during the session. Not for participants.",
  robots: { index: false, follow: false },
};

const nav = [
  { href: "#steps", label: "The session" },
  { href: "#rules", label: "How it unlocks" },
  { href: "#todo", label: "Still to build" },
];

export default function Live() {
  return (
    <main>
      <Topbar nav={nav} pill="Placeholder" />

      <div className="internal-banner" role="note">
        <b>Not the real page.</b> {status}
      </div>

      <section className="hero" id="top">
        <div className="hero-copy">
          <p className="kicker">
            <span /> 3 September · 09:30–12:30 · the page on every desk
          </p>
          <h1>
            The day,
            <br />
            <em>minute by minute.</em>
          </h1>
          <p className="lede">
            One page carries the room. It states what a participant should be holding by now and,
            more usefully, what to do if they are not — then unlocks the next step on a schedule.
            Nothing else is delivered live except a five-minute briefing.
          </p>
        </div>
      </section>

      <section className="journey-section" id="steps">
        <div className="section-heading">
          <div>
            <span>01 / THE SESSION</span>
            <h2>What they are doing with the recordings</h2>
          </div>
          <p>
            Read the middle column to project yourself into the room. Every row is a moment where a
            participant either has something or needs a way out.
          </p>
        </div>
        <table className="scoring-table">
          <thead>
            <tr>
              <th scope="col">Time</th>
              <th scope="col">Stage</th>
              <th scope="col">On the recordings</th>
              <th scope="col">Should have</th>
              <th scope="col">If they do not</th>
              <th scope="col">Unlocks</th>
            </tr>
          </thead>
          <tbody>
            {steps.map((step) => (
              <tr key={step.time}>
                <td>
                  <b>{step.time}</b>
                  {step.beat ? <small> · {step.beat}</small> : null}
                </td>
                <td>{step.stage}</td>
                <td>{step.onTheData}</td>
                <td>{step.shouldHave}</td>
                <td>{step.ifYouDont}</td>
                <td>{step.unlocks}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>

      <section className="deliver-section" id="rules">
        <div className="section-heading light compact">
          <div>
            <span>02 / HOW IT UNLOCKS</span>
            <h2>Five rules the real page has to keep</h2>
          </div>
          <p>
            The recovery line is the part that carries the design. Every one of them is permission to
            do less, because in a room selected for expertise that is the permission nobody grants
            themselves.
          </p>
        </div>
        <div className="deliver-grid">
          {rules.map((rule, index) => (
            <article key={rule}>
              <span>{String(index + 1).padStart(2, "0")}</span>
              <p>{rule}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="pipeline-section" id="todo">
        <div className="section-heading compact">
          <div>
            <span>03 / STILL TO BUILD</span>
            <h2>What this placeholder is standing in for</h2>
          </div>
        </div>
        <ul className="rule-list">
          {stillToBuild.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      </section>

      <Footer
        note="Placeholder for the live session page. Local development only — never built into the public site."
        backTo="#top"
      />
    </main>
  );
}
