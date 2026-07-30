"use client";

import { useState } from "react";

type Level = "strategy" | "tactics" | "operations";
type Perspective = "attendee" | "organizer";

const planning = {
  strategy: {
    eyebrow: "Why this event exists",
    title: "Turn raw robotics logs into reusable engineering knowledge.",
    summary:
      "The north star is not a winning timestamp. It is a compact, defensible and repeatable path from observation to action.",
    steps: [
      ["01", "Lock the mission", "Awareness + capability: attendees experience the complete data workflow and leave with an executable detector."],
      ["02", "Protect the principles", "Evidence-first, local-first, deterministic core, optional agent, open contracts and progressive disclosure."],
      ["03", "Define success", "Teams batch-run, expose one failure, reproduce in one command and name the next operational action."],
      ["04", "Guard the scope", "No platform rebuild, no day-of compilation, no paid key, no mandatory GPU and no infrastructure contest."],
    ],
  },
  tactics: {
    eyebrow: "How the challenge creates learning",
    title: "One ladder: Smart Data warm-up → Data Detective → optional agent.",
    summary:
      "All teams follow the same progression. Advanced methods add ambition without creating three incomparable hackathons.",
    steps: [
      ["01", "Shape the challenge", "Give teams an incomplete incident report and ask for a detector, evidence, limits and an operational response."],
      ["02", "Set the cadence", "Thirty-minute observation, simple rule, temporal context, batch scale, failure review, then transfer pitch."],
      ["03", "Make proof the contract", "Score hypothesis, detection, extraction, quality, visualization and reproducibility—not prompt style."],
      ["04", "Support the room", "Prepared layouts, public checkpoints, hidden labels, coach prompts and a non-ROS fallback pack."],
    ],
  },
  operations: {
    eyebrow: "What must exist before day zero",
    title: "Prove one vertical slice, then freeze and rehearse the kit.",
    summary:
      "Build only what carries the attendee from a bag to a scored evidence package. Everything else waits.",
    steps: [
      ["P0", "Contract", "Scenario, data rights, audience floor, duration, hardware, OSS definition and scoring policy approved."],
      ["P1", "Vertical slice", "One bag completes MCAP → detector → batch → clip → score offline on the minimum laptop."],
      ["P2", "Golden path", "Schemas, CLI, sample, reference detector, pinned runtime and one-page quickstart frozen."],
      ["P3", "Data + score", "Dev/test split, labels, tolerances, quality defects and evaluator calibrated across different detectors."],
      ["P4", "Experience", "Warm-up, layouts, coach guide, submission and fallback pack packaged."],
      ["P5", "Rehearsal", "Fresh install, offline run, concurrent scoring and two-hour internal mini-hackathon passed."],
    ],
  },
} satisfies Record<Level, { eyebrow: string; title: string; summary: string; steps: string[][] }>;

const journey = [
  ["00:00", "Observe", "Open one bag. Find a meaningful occurrence, topic, field and window."],
  ["00:30", "Formalize", "Express the observation as one executable comparison."],
  ["01:00", "Contextualize", "Add a second signal, derived feature, AND/OR, duration or sequence."],
  ["01:45", "Scale", "Run the same detector across several bags and produce standard outputs."],
  ["02:15", "Challenge", "Investigate a false positive, missed event, missing signal or ambiguity."],
  ["02:45", "Transfer", "Pitch the proof, the limit and what should happen after a match."],
];

const perspectives = {
  attendee: {
    label: "Attendee view",
    title: "You own the investigation.",
    intro: "Your team turns physical behaviour into executable data logic, tests it at scale and explains what the evidence supports.",
    owns: [
      "Signals, fields and windows to inspect",
      "Derived features, thresholds or model inference",
      "Boolean and temporal event logic",
      "Debounce, evidence window and retained topics",
      "False-positive / false-negative analysis",
      "Interpretation, limits and downstream action",
    ],
    gets: [
      "A working local bundle and warm-up bag",
      "PlotJuggler 4 layouts and topic inventory",
      "A batch runner, clip extraction and scoring",
      "Development data plus partial feedback",
      "Submission template and one-command path",
      "Optional bounded agent / advanced track",
    ],
  },
  organizer: {
    label: "Organizer view",
    title: "You own the reliable stage.",
    intro: "Your work makes the full experience boringly dependable, so attendee time is spent on data reasoning rather than plumbing.",
    owns: [
      "Authorized data, schemas, labels and manifests",
      "MCAP/ROS decoding and time semantics",
      "Deterministic batch execution and provenance",
      "Clip generation, hidden scoring and reporting",
      "Pinned binaries, dependencies and offline cache",
      "Facilitation, checkpoints and fallback exercise",
    ],
    gets: [
      "Structured, comparable submissions",
      "Visible checkpoints before teams drift",
      "A score that rewards proof and process",
      "An internal vertical slice as the release gate",
      "A clear separation between core and bonuses",
      "Evidence for what to improve after the event",
    ],
  },
} satisfies Record<Perspective, { label: string; title: string; intro: string; owns: string[]; gets: string[] }>;

const readiness = [
  ["Data", "DECIDE FIRST", "Scenario, source rights, sample/dev/test split, hidden truth, laptop-sized subset."],
  ["Contracts", "DRAFT → FREEZE", "EventSpec + CEL, event JSONL, run manifest, detector interface, time semantics."],
  ["Runner", "BUILD", "doctor, inspect, sample, detect, clip, score and report; dry-run and actionable errors."],
  ["Views", "PREPARE", "PlotJuggler 4 primary layouts; Lichtblick only if robotic context is required."],
  ["Dependencies", "PIN", "One ROS 2 distro, MCAP, Polars, CEL runtime, CPU baseline, image/bundle checksums."],
  ["Evaluation", "DESIGN EARLY", "Temporal tolerance, duplicates, missing data, volume reduction and proof quality."],
  ["Experience", "PACKAGE", "Warm-up, start page, coach guide, checkpoints, submission and pitch template."],
  ["Resilience", "REHEARSE", "Fresh install, no Internet, simultaneous scoring, recovery media and non-ROS fallback."],
];

const decisions = [
  "3-hour fixed agenda | 3.5-hour agenda with longer review",
  "authorized URT-Kashiwa subset | CIV-owned/synthetic data | another redistributable ROS 2 dataset",
  "hard-braking/intersection | disengagement sequence | data-quality incident",
  "EventSpec + CEL only | EventSpec plus advanced Python API",
  "cive CLI name | civ CLI name",
  "PlotJuggler 4 only | PlotJuggler 4 + Lichtblick",
  "no supplied model | pinned local model | shared on-site inference",
  "agent demo | agent bonus | separate advanced prize",
  "strict clean room | independent functional reimplementation with provenance review",
];

export default function Home() {
  const [level, setLevel] = useState<Level>("strategy");
  const [perspective, setPerspective] = useState<Perspective>("attendee");
  const plan = planning[level];
  const view = perspectives[perspective];

  return (
    <main>
      <header className="topbar">
        <a className="brand" href="#top" aria-label="CIV 2026 handoff home">
          <span className="brand-mark">CIV</span>
          <span>Data Hackathon 2026</span>
        </a>
        <nav aria-label="Page sections">
          <a href="#plan">Plan</a>
          <a href="#journey">Experience</a>
          <a href="#readiness">Readiness</a>
          <a href="#decisions">Decisions</a>
        </nav>
        <span className="internal-pill">Internal handoff</span>
      </header>

      <section className="hero" id="top">
        <div className="hero-copy">
          <p className="kicker"><span /> Working baseline · organizer + attendee lens</p>
          <h1>From raw bag<br />to <em>defensible proof.</em></h1>
          <p className="lede">
            A three-hour ROS 2 data investigation where teams turn an observation into reusable event logic, scale it across recordings, challenge its failures, and connect evidence to action.
          </p>
          <div className="hero-actions">
            <a className="primary-button" href="#journey">See the attendee journey <span>→</span></a>
            <a className="text-link" href="#readiness">What must be ready</a>
          </div>
        </div>
        <div className="hero-system" aria-label="Hackathon transformation">
          <div className="system-caption">THE CORE TRANSFORMATION</div>
          <div className="signal-card raw">
            <span className="signal-index">01</span>
            <div><b>Hours of raw logs</b><small>mixed sensors · ROS 2 · MCAP</small></div>
            <div className="wave" aria-hidden="true"><i /><i /><i /><i /><i /><i /><i /></div>
          </div>
          <div className="flow-arrow"><span>inspect · encode · scale</span>↓</div>
          <div className="signal-card proof">
            <span className="signal-index">02</span>
            <div><b>Minutes of evidence</b><small>events · clips · metrics · provenance</small></div>
            <div className="event-bars" aria-hidden="true"><i /><i /><i /></div>
          </div>
          <div className="system-footer">
            <span>Human reasoning</span><span>Deterministic core</span><span>Optional AI</span>
          </div>
        </div>
      </section>

      <section className="shift-section">
        <div className="section-label">THE 2026 SHIFT</div>
        <div className="shift-grid">
          <article><span>01</span><h3>Open, file-first</h3><p>Replace a product workflow with portable contracts, composable tools and local outputs.</p></article>
          <article><span>02</span><h3>Evidence, not timestamps</h3><p>Every match carries synchronized context, provenance, quality warnings and a next action.</p></article>
          <article><span>03</span><h3>Failure is a deliverable</h3><p>Teams must expose one ambiguity, false positive, miss or broken signal—and learn from it.</p></article>
          <article><span>04</span><h3>AI as an enabler</h3><p>Agents may accelerate investigation through bounded tools; executed evidence stays authoritative.</p></article>
        </div>
      </section>

      <section className="planning-section" id="plan">
        <div className="section-heading light">
          <div><span>01 / PLAN</span><h2>Three levels.<br />One coherent event.</h2></div>
          <p>Strategy protects the intent. Tactics shape the learning. Operations make the promise real.</p>
        </div>
        <div className="level-tabs" role="tablist" aria-label="Planning level">
          {(["strategy", "tactics", "operations"] as Level[]).map((item, index) => (
            <button key={item} className={level === item ? "active" : ""} onClick={() => setLevel(item)} role="tab" aria-selected={level === item}>
              <span>0{index + 1}</span>{item}
            </button>
          ))}
        </div>
        <div className="plan-panel">
          <div className="plan-intro">
            <span>{plan.eyebrow}</span>
            <h3>{plan.title}</h3>
            <p>{plan.summary}</p>
          </div>
          <div className="plan-steps">
            {plan.steps.map(([number, title, text]) => (
              <article key={`${level}-${number}`}>
                <b>{number}</b><div><h4>{title}</h4><p>{text}</p></div>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section className="journey-section" id="journey">
        <div className="section-heading">
          <div><span>02 / EXPERIENCE</span><h2>The rule ladder</h2></div>
          <p>Attendees do the reasoning once, then the prepared system scales it. Each stage produces visible evidence.</p>
        </div>
        <div className="journey-line">
          {journey.map(([time, title, text], index) => (
            <article key={title}>
              <div className="journey-node"><span>{index + 1}</span></div>
              <time>{time}</time><h3>{title}</h3><p>{text}</p>
            </article>
          ))}
        </div>
        <div className="driving-strip">
          <span>DRIVING FORCES</span>
          <p>Engineering question</p><i>×</i><p>physical data</p><i>×</i><p>limited time</p><i>×</i><p>hidden truth</p><i>×</i><p>proof contract</p><i>×</i><p>next action</p>
        </div>
      </section>

      <section className="perspective-section">
        <div className="perspective-controls">
          <div>
            <span>SWITCH PERSPECTIVE</span>
            <h2>Same journey.<br />Different ownership.</h2>
          </div>
          <div className="toggle" role="group" aria-label="Perspective">
            {(["attendee", "organizer"] as Perspective[]).map(item => (
              <button key={item} className={perspective === item ? "active" : ""} onClick={() => setPerspective(item)}>{perspectives[item].label}</button>
            ))}
          </div>
        </div>
        <div className="perspective-card">
          <div className="perspective-lead"><span>{view.label}</span><h3>{view.title}</h3><p>{view.intro}</p></div>
          <div className="list-column"><b>YOU OWN</b>{view.owns.map(item => <p key={item}><i>✓</i>{item}</p>)}</div>
          <div className="list-column muted"><b>YOU RECEIVE</b>{view.gets.map(item => <p key={item}><i>+</i>{item}</p>)}</div>
        </div>
      </section>

      <section className="pipeline-section">
        <div className="section-heading compact">
          <div><span>03 / REFERENCE FLOW</span><h2>The prepared spine</h2></div>
          <p>The interface is intentionally narrow. Organizers own the spine; teams own the detector and interpretation.</p>
        </div>
        <div className="pipeline" aria-label="Reference technical pipeline">
          {[
            ["MCAP", "raw recording"], ["PlotJuggler 4", "manual exploration"], ["Polars", "selected signals"], ["EventSpec + CEL", "team logic"], ["Batch runner", "scale + provenance"], ["Evidence", "clips + score"]
          ].map(([title, text], index) => <div className={index === 3 ? "owned" : ""} key={title}><span>0{index + 1}</span><b>{title}</b><small>{text}</small>{index === 3 && <em>TEAM OWNS</em>}</div>)}
        </div>
        <div className="output-code">
          <span>$ cive detect detector.yaml dataset/dev/</span>
          <p><b>events.jsonl</b><b>evidence/*.mcap</b><b>metrics.json</b><b>run-manifest.json</b></p>
        </div>
      </section>

      <section className="readiness-section" id="readiness">
        <div className="section-heading light compact">
          <div><span>04 / READINESS</span><h2>What must be true<br />before the room opens.</h2></div>
          <p>Unknown implementation status is treated as work—not assumed readiness. The first three rows constrain the rest.</p>
        </div>
        <div className="readiness-grid">
          {readiness.map(([name, status, detail], index) => (
            <article key={name}>
              <span className="readiness-number">{String(index + 1).padStart(2, "0")}</span>
              <div><h3>{name}</h3><p>{detail}</p></div>
              <b className={`status status-${status.toLowerCase().replaceAll(" ", "-").replaceAll("→", "to")}`}>{status}</b>
            </article>
          ))}
        </div>
      </section>

      <section className="decision-section" id="decisions">
        <div className="decision-intro">
          <span>05 / DECISION QUEUE</span>
          <h2>⚠️ Grilling required.</h2>
          <p>These choices are deliberately visible. Resolve them in dependency order; do not let them hide inside implementation.</p>
          <a href="#next">Start with the three blockers ↓</a>
        </div>
        <div className="decision-list">
          {decisions.map((decision, index) => (
            <article key={decision}><span>{String(index + 1).padStart(2, "0")}</span><p><b>Possible choices:</b> {decision}</p></article>
          ))}
        </div>
      </section>

      <section className="next-section" id="next">
        <div><span>NEXT 72 HOURS</span><h2>Prove the journey<br />before polishing the event.</h2></div>
        <ol>
          <li><span>01</span><div><b>Resolve the blockers</b><p>Scenario + data rights, target machine, and three-hour contract.</p></div></li>
          <li><span>02</span><div><b>Assign five owners</b><p>Data, runner/contracts, evaluation, attendee experience, release engineering.</p></div></li>
          <li><span>03</span><div><b>Run the one-bag slice</b><p>MCAP → detector → batch → evidence clip → score, offline.</p></div></li>
        </ol>
      </section>

      <footer>
        <div className="brand"><span className="brand-mark">CIV</span><span>Data Hackathon 2026</span></div>
        <p>Internal working handoff · source precedence documented in <code>HACKATHON-HANDOFF.md</code></p>
        <a href="#top">Back to top ↑</a>
      </footer>
    </main>
  );
}

