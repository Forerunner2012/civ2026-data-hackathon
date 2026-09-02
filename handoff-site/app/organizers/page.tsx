import type { Metadata } from "next";
import { Footer, Topbar } from "../_components/chrome";
import { LevelTabs, type LevelPanel } from "../_components/level-tabs";
import {
  blockers,
  decisionGroups,
  decisionsMade,
  drivingForces,
  evaluationDesign,
  eventFacts,
  facilitation,
  nonGoals,
  phases,
  planning,
  readiness,
  sources,
  successCriteria,
} from "../_content/organizers.server";

export const metadata: Metadata = {
  title: "CIV 2026 Data Hackathon — organizer handoff (internal)",
  description: "Internal planning, evaluation design, closed decisions and release gates. Not for participants.",
  robots: { index: false, follow: false },
};

const nav = [
  { href: "#plan", label: "Plan" },
  { href: "#phases", label: "Phases" },
  { href: "#readiness", label: "Readiness" },
  { href: "#evaluation", label: "Evaluation" },
  { href: "#decisions", label: "Decisions" },
];

const panels: LevelPanel[] = (Object.keys(planning) as (keyof typeof planning)[]).map((id) => ({
  id,
  ...planning[id],
}));

export default function Organizers() {
  return (
    <main>
      <Topbar nav={nav} pill="Internal" />

      <div className="internal-banner" role="note">
        <b>Organizer view.</b> Teaching goals, evaluation internals and release gates. Do not screen-share
        this page in a room with participants — the participant view lives at <a href="/participants">/participants</a>.
      </div>

      <div className="event-strip">
        <span>{eventFacts.when}</span>
        <span>{eventFacts.where}</span>
        <span>
          <b>{eventFacts.slot}</b>
        </span>
        <span>{eventFacts.results}</span>
      </div>

      <section className="hero organizer-hero" id="top">
        <div className="hero-copy">
          <p className="kicker">
            <span /> Internal working baseline
          </p>
          <h1>
            You own the
            <br />
            <em>reliable stage.</em>
          </h1>
          <p className="lede">
            Your work makes the full experience boringly dependable, so attendee time is spent on
            data reasoning rather than plumbing. Unknown implementation status is treated as work —
            not as readiness.
          </p>
          <div className="hero-actions">
            <a className="primary-button" href="/organizers/pack">
              Open operations + jury pack <span>→</span>
            </a>
            <a className="primary-button" href="#decisions">
              Jump to the decision queue <span>→</span>
            </a>
            <a className="text-link" href="#next">
              Execution gates
            </a>
          </div>
        </div>
      </section>

      <section className="planning-section" id="plan">
        <div className="section-heading light">
          <div>
            <span>01 / PLAN</span>
            <h2>
              Three levels.
              <br />
              One coherent event.
            </h2>
          </div>
          <p>
            Strategy protects the intent. Tactics shape the learning. Operations make the promise
            real.
          </p>
        </div>
        <LevelTabs panels={panels} />
      </section>

      <section className="criteria-section">
        <div className="criteria-grid">
          <div className="criteria-column">
            <b>STRATEGICALLY SUCCESSFUL IF</b>
            {successCriteria.map((item) => (
              <p key={item}>
                <i>✓</i>
                {item}
              </p>
            ))}
          </div>
          <div className="criteria-column negative">
            <b>EXPLICIT NON-GOALS</b>
            {nonGoals.map((item) => (
              <p key={item}>
                <i>✕</i>
                {item}
              </p>
            ))}
          </div>
        </div>
      </section>

      <section className="phase-section" id="phases">
        <div className="section-heading compact">
          <div>
            <span>02 / PREPARATION</span>
            <h2>Six phases, six gates</h2>
          </div>
          <p>
            Build only what carries an attendee from a bag to a scored evidence package. A phase is
            done when its gate passes, not when it feels finished.
          </p>
        </div>
        <div className="phase-list">
          {phases.map(({ id, title, work, gate }) => (
            <article key={id}>
              <span className="phase-id">{id}</span>
              <div>
                <h3>{title}</h3>
                <p>{work}</p>
                <p className="phase-gate">
                  <b>GATE</b>
                  {gate}
                </p>
              </div>
            </article>
          ))}
        </div>
      </section>

      <section className="readiness-section" id="readiness">
        <div className="section-heading light compact">
          <div>
            <span>03 / READINESS</span>
            <h2>
              What must be true
              <br />
              before the room opens.
            </h2>
          </div>
          <p>The first three rows constrain everything below them.</p>
        </div>
        <div className="readiness-grid">
          {readiness.map(({ name, status, detail }, index) => (
            <article key={name}>
              <span className="readiness-number">{String(index + 1).padStart(2, "0")}</span>
              <div>
                <h3>{name}</h3>
                <p>{detail}</p>
              </div>
              <b className={`status status-${status.toLowerCase().replaceAll(" ", "-").replaceAll("→", "to")}`}>
                {status}
              </b>
            </article>
          ))}
        </div>
      </section>

      <section className="evaluation-section" id="evaluation">
        <div className="section-heading compact">
          <div>
            <span>04 / EVALUATION DESIGN</span>
            <h2>The part participants never see</h2>
          </div>
          <p>
            The published rubric is theirs. The mechanics below are ours — they only work while they
            stay out of attendee-facing material.
          </p>
        </div>
        <div className="mechanics-grid">
          {evaluationDesign.map((item, index) => (
            <article key={item}>
              <span>{String(index + 1).padStart(2, "0")}</span>
              <p>{item}</p>
            </article>
          ))}
        </div>

        <div className="section-heading compact spaced">
          <div>
            <span>FACILITATION MECHANICS</span>
            <h2>Running the room</h2>
          </div>
          <p>Checkpoints and coaching create the pedagogical pressure — not the leaderboard.</p>
        </div>
        <div className="mechanics-grid">
          {facilitation.map((item, index) => (
            <article key={item}>
              <span>{String(index + 1).padStart(2, "0")}</span>
              <p>{item}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="forces-section">
        <div className="section-label">SEVEN DRIVING FORCES</div>
        <div className="forces-grid">
          {drivingForces.map(({ title, effect }, index) => (
            <article key={title}>
              <span>{String(index + 1).padStart(2, "0")}</span>
              <h3>{title}</h3>
              <p>{effect}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="decision-section" id="decisions">
        <div className="decision-intro">
          <span>05 / DECISION QUEUE</span>
          <h2>Grilling complete.</h2>
          <p>
            All {decisionsMade.length} decisions are closed — nothing remains to settle before the
            kit gets built. Detail lives in the wayfinder map under{" "}
            <code>.scratch/civ2026-challenge-spec/</code>: one decision, one ticket, and the
            reasoning that produced it.
          </p>
          <a href="#next">What happens next ↓</a>
        </div>
        <div className="decision-column">
          {decisionGroups.map((group) => {
            const rows = decisionsMade.filter((item) => item.group === group);
            return (
              <div key={group}>
                <b className="decision-heading done">
                  {group} <i>{rows.length}</i>
                </b>
                <div className="decision-list">
                  {rows.map(({ ticket, title, answer, caveat }) => (
                    <article className="made" key={ticket}>
                      <span>{ticket}</span>
                      <p>
                        <b>{title}:</b> {answer}
                        {caveat && <em className="decision-caveat">{caveat}</em>}
                      </p>
                    </article>
                  ))}
                </div>
              </div>
            );
          })}
        </div>
      </section>

      <section className="next-section" id="next">
        <div>
          <span>WHAT HAPPENS NEXT</span>
          <h2>
            Prove the journey
            <br />
            before polishing the event.
          </h2>
        </div>
        <ol>
          {blockers.map(({ title, detail }, index) => (
            <li key={title}>
              <span>{String(index + 1).padStart(2, "0")}</span>
              <div>
                <b>{title}</b>
                <p>{detail}</p>
              </div>
            </li>
          ))}
        </ol>
      </section>

      <section className="sources-section">
        <div className="section-label">SOURCE PRECEDENCE</div>
        <ol className="source-list">
          {sources.map((source) => (
            <li key={source}>{source}</li>
          ))}
        </ol>
      </section>

      <Footer note="Organizer view · internal · not for participants" />
    </main>
  );
}
