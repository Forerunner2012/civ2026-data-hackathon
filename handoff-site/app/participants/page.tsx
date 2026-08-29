import type { Metadata } from "next";
import { Footer, Topbar } from "../_components/chrome";
import { premise } from "../_content/site";
import {
  bonus,
  brief,
  comeReady,
  commands,
  deliverables,
  deskMaterials,
  extensionTrack,
  journey,
  notYourJob,
  pipeline,
  participantProducts,
  recognition,
  scoring,
  scoringRules,
  theDayPage,
  submissionTree,
  submissionOutcomes,
  submissionSteps,
  youOwn,
  youReceive,
} from "../_content/participants";

export const metadata: Metadata = {
  title: "CIV 2026 Data Hackathon — what to expect",
  description: premise,
};

const nav = [
  { href: "#brief", label: "Brief" },
  { href: "#hours", label: "Three hours" },
  { href: "#deliver", label: "Deliver" },
  { href: "#scoring", label: "Scoring" },
  { href: "#toolkit", label: "Toolkit" },
  { href: "#kit", label: "Kit" },
];

const totalPoints = scoring.reduce((sum, row) => sum + row.points, 0);
const bonusPoints = bonus.reduce((sum, row) => sum + row.points, 0);

export default function Participants() {
  return (
    <main>
      <Topbar nav={nav} pill="Participants" />

      <section className="hero" id="top">
        <div className="hero-copy">
          <p className="kicker">
            <span /> Data Detective · three hours · solo or duo
          </p>
          <h1>
            From raw bag
            <br />
            to <em>defensible proof.</em>
          </h1>
          <p className="lede">{premise}</p>
          <div className="hero-actions">
            <a className="primary-button" href="#hours">
              See how the three hours run <span>→</span>
            </a>
            <a className="text-link" href="#scoring">
              How you are scored
            </a>
          </div>
        </div>
        <div className="hero-system" aria-label="Hackathon transformation">
          <div className="system-caption">THE CORE TRANSFORMATION</div>
          <div className="signal-card raw">
            <span className="signal-index">01</span>
            <div>
              <b>Hours of raw logs</b>
              <small>mixed sensors · ROS 2 · MCAP</small>
            </div>
            <div className="wave" aria-hidden="true">
              <i />
              <i />
              <i />
              <i />
              <i />
              <i />
              <i />
            </div>
          </div>
          <div className="flow-arrow">
            <span>inspect · encode · scale</span>↓
          </div>
          <div className="signal-card proof">
            <span className="signal-index">02</span>
            <div>
              <b>Minutes of evidence</b>
              <small>events · clips · metrics · provenance</small>
            </div>
            <div className="event-bars" aria-hidden="true">
              <i />
              <i />
              <i />
            </div>
          </div>
          <div className="system-footer">
            <span>Human reasoning</span>
            <span>Deterministic core</span>
            <span>Optional AI</span>
          </div>
        </div>
      </section>

      <section className="brief-section" id="brief">
        <div className="section-label">YOUR BRIEF</div>
        <div className="brief-card">
          <p>{brief}</p>
        </div>
        <div className="shift-grid">
          <article>
            <span>01</span>
            <h3>Evidence, not timestamps</h3>
            <p>Every match must carry synchronized context, provenance and a next action.</p>
          </article>
          <article>
            <span>02</span>
            <h3>Reusable, not one-off</h3>
            <p>A threshold shown once is not enough. Your logic runs across every bag.</p>
          </article>
          <article>
            <span>03</span>
            <h3>Failure is a deliverable</h3>
            <p>Expose one ambiguity, false positive, miss or broken signal — and act on it.</p>
          </article>
          <article>
            <span>04</span>
            <h3>AI is optional</h3>
            <p>An agent may accelerate you through bounded tools. Executed evidence still wins.</p>
          </article>
        </div>
      </section>

      <section className="journey-section" id="hours">
        <div className="section-heading">
          <div>
            <span>01 / THE THREE HOURS</span>
            <h2>The rule ladder</h2>
          </div>
          <p>
            You do the reasoning once, then the prepared system scales it. Each stage leaves visible
            evidence behind.
          </p>
        </div>
        <div className="journey-line">
          {journey.map(({ time, title, doing, produces }, index) => (
            <article key={title}>
              <div className="journey-node">
                <span>{index + 1}</span>
              </div>
              <time>{time}</time>
              <h3>{title}</h3>
              <p>{doing}</p>
              <p className="journey-output">
                <i>→</i>
                {produces}
              </p>
            </article>
          ))}
        </div>
        <ul className="rule-list">
          {theDayPage.map((line) => (
            <li key={line}>{line}</li>
          ))}
        </ul>
      </section>

      <section className="perspective-section">
        <div className="perspective-controls">
          <div>
            <span>THE BOUNDARY</span>
            <h2>
              You own the
              <br />
              investigation.
            </h2>
          </div>
        </div>
        <div className="perspective-card">
          <div className="perspective-lead">
            <span>Participant view</span>
            <h3>Your reasoning is the valuable part.</h3>
            <p>
              You turn physical behaviour into executable data logic, test it at scale and
              explain what the evidence actually supports. The plumbing is already built.
            </p>
          </div>
          <div className="list-column">
            <b>YOU OWN</b>
            {youOwn.map((item) => (
              <p key={item}>
                <i>✓</i>
                {item}
              </p>
            ))}
          </div>
          <div className="list-column muted">
            <b>YOU RECEIVE</b>
            {youReceive.map((item) => (
              <p key={item}>
                <i>+</i>
                {item}
              </p>
            ))}
          </div>
        </div>
        <div className="not-your-job">
          <b>YOU WILL NOT HAVE TO</b>
          <ul>
            {notYourJob.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </div>
      </section>

      <section className="deliver-section" id="deliver">
        <div className="section-heading light compact">
          <div>
            <span>02 / WHAT YOU HAND IN</span>
            <h2>
              Ten things,
              <br />
              one command.
            </h2>
          </div>
          <p>
            The submission is the argument. Everything below is produced by the tooling you are
            given — your job is to make it defensible.
          </p>
        </div>
        <div className="deliver-grid">
          {deliverables.map((item, index) => (
            <article key={item}>
              <span>{String(index + 1).padStart(2, "0")}</span>
              <p>{item}</p>
            </article>
          ))}
        </div>
        <pre className="tree-block">{submissionTree}</pre>
        <div className="submission-guide">
          <div>
            <h3>Build and hand in the same bundle on every path</h3>
            <ol>
              {submissionSteps.map((step) => <li key={step}>{step}</li>)}
            </ol>
          </div>
          <div>
            <h3>What each outcome means</h3>
            <dl>
              {submissionOutcomes.map(({ state, action }) => (
                <div key={state}><dt>{state}</dt><dd>{action}</dd></div>
              ))}
            </dl>
          </div>
        </div>
      </section>

      <section className="scoring-section" id="scoring">
        <div className="section-heading compact">
          <div>
            <span>03 / SCORING</span>
            <h2>How the jury reads your work</h2>
          </div>
          <p>Published up front. There are no hidden categories and no points for prompt style.</p>
        </div>
        <table className="score-table">
          <thead>
            <tr>
              <th>Category</th>
              <th>Points</th>
              <th>What the jury looks for</th>
            </tr>
          </thead>
          <tbody>
            {scoring.map(({ category, points, looksFor }) => (
              <tr key={category}>
                <td>{category}</td>
                <td className="score-points">{points}</td>
                <td className="score-note">{looksFor}</td>
              </tr>
            ))}
            <tr className="score-total">
              <td>Common score</td>
              <td className="score-points">{totalPoints}</td>
              <td className="score-note" />
            </tr>
            {bonus.map(({ label, points }) => (
              <tr key={label} className="score-bonus">
                <td>{label}</td>
                <td className="score-points">+{points}</td>
                <td className="score-note">bonus</td>
              </tr>
            ))}
            <tr className="score-total">
              <td>Maximum bonus</td>
              <td className="score-points">+{bonusPoints}</td>
              <td className="score-note" />
            </tr>
          </tbody>
        </table>
        <ul className="rule-list">
          {scoringRules.map((rule) => (
            <li key={rule}>{rule}</li>
          ))}
        </ul>
        <h3>What is recognised at 15:00</h3>
        <ul className="rule-list">
          {recognition.map((line) => (
            <li key={line}>{line}</li>
          ))}
        </ul>
      </section>

      <section className="pipeline-section" id="toolkit">
        <div className="section-heading compact">
          <div>
            <span>04 / YOUR TOOLKIT</span>
            <h2>The prepared spine</h2>
          </div>
          <p>
            The interface is intentionally narrow. One step belongs to you; the rest is built,
            pinned and tested.
          </p>
        </div>
        <div className="pipeline" aria-label="Reference technical pipeline">
          {pipeline.map(({ title, note, owner }, index) => (
            <div className={owner === "you" ? "owned" : ""} key={title}>
              <span>0{index + 1}</span>
              <b>{title}</b>
              <small>{note}</small>
              {owner === "you" && <em>YOU OWN</em>}
            </div>
          ))}
        </div>
        <div className="command-list">
          {commands.map(({ command, note }) => (
            <p key={command}>
              <code>{command}</code>
              <small>{note}</small>
            </p>
          ))}
        </div>
      </section>

      <section className="kit-section" id="kit">
        <div className="section-heading compact">
          <div>
            <span>05 / EXACT KIT REFERENCES</span>
            <h2>Open the supplied products, not a guess.</h2>
          </div>
          <p>These participant-safe paths are the shared baseline for both datasets.</p>
        </div>
        <div className="kit-grid">
          {participantProducts.map(
            ({ dataset, product, plotJugglerLayout, lichtblickLayout, inventory }) => (
              <article key={dataset}>
                <span>{dataset}</span>
                <h3>{product}</h3>
                <p><b>PlotJuggler layout:</b> <code>{plotJugglerLayout}</code></p>
                <p><b>Lichtblick layout:</b> <code>{lichtblickLayout}</code></p>
                <p><b>Visible inventory:</b> {inventory}</p>
              </article>
            ),
          )}
        </div>
        <p>
          On a connected machine, prefer the official no-install{" "}
          <a href="https://lichtblick-suite.github.io/lichtblick/">Lichtblick web app</a>. The kit
          also carries the pinned desktop build for offline use; verify it against the supplied
          checksums before running it.
        </p>
        <div className="desk-links" aria-label="Printable desk materials">
          {deskMaterials.map(({ href, title, note }) => (
            <a href={href} key={href}>
              <span>PRINT MATERIAL</span>
              <b>{title}</b>
              <small>{note}</small>
            </a>
          ))}
        </div>
        <div className="extension-note">
          <b>Optional extension · scored, but not scheduled</b>
          <p>
            The bonus extension is available throughout the session for teams whose core result
            already reproduces. It earns up to 20 bonus points and has no reserved beat or timebox.
          </p>
        </div>
      </section>

      <section className="extension-section" id="extension">
        <div className="section-heading compact">
          <div>
            <span>06 / OPTIONAL EXTENSION</span>
            <h2>Bring knowledge the recording never had.</h2>
          </div>
          <p>{extensionTrack.lesson}</p>
        </div>
        <ul className="rule-list">
          {extensionTrack.placement.map((line) => (
            <li key={line}>{line}</li>
          ))}
        </ul>
        <div className="extension-grid">
          <div>
            <h3>The exercise</h3>
            <ol>
              {extensionTrack.steps.map((step) => (
                <li key={step}>{step}</li>
              ))}
            </ol>
          </div>
          <div>
            <h3>What counts as doing it well</h3>
            <ul>
              {extensionTrack.provenance.map((line) => (
                <li key={line}>{line}</li>
              ))}
            </ul>
          </div>
        </div>
        <p className="extension-budget">{extensionTrack.budget}</p>
        <p className="extension-budget">{extensionTrack.scoredAs}</p>
      </section>

      <section className="next-section" id="ready">
        <div>
          <span>COME READY</span>
          <h2>
            Bring curiosity.
            <br />
            We bring the plumbing.
          </h2>
        </div>
        <ol>
          {comeReady.map((item, index) => (
            <li key={item}>
              <span>{String(index + 1).padStart(2, "0")}</span>
              <div>
                <b>{item}</b>
              </div>
            </li>
          ))}
        </ol>
      </section>

      <Footer note="Participant view · CIV 2026 Data Hackathon" />
    </main>
  );
}
