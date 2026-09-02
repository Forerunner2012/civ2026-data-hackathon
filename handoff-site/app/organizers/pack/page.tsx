import type { Metadata } from "next";
import { Footer, Topbar } from "../../_components/chrome";
import { SESSION_STAGES } from "../../_content/live-content.server";
import { postEventSolutions } from "../../_content/post-event-solutions.server";
import {
  afternoonRun,
  bonusCategories,
  coachProtocol,
  consentWording,
  feedbackTemplate,
  juryCategories,
  juryProcedure,
  ORGANIZER_PACK_MARKER,
  sweepProtocol,
  troubleshooting,
} from "../../_content/organizer-pack.server";

export const metadata: Metadata = {
  title: "CIV 2026 — organizer operations and jury pack",
  robots: { index: false, follow: false },
};

const checkpoints = SESSION_STAGES.filter((stage) => /^b[1-7]$/.test(stage.id));

function NumberedCards({ items, label }: { items: readonly string[]; label: string }) {
  return (
    <ol className="pack-card-grid">
      {items.map((item, index) => (
        <li key={item}>
          <span>{String(index + 1).padStart(2, "0")}</span>
          <div>
            <b>{label}</b>
            <p>{item}</p>
          </div>
        </li>
      ))}
    </ol>
  );
}

export default function OrganizerPack() {
  return (
    <main>
      <Topbar nav={[{ href: "#coach", label: "Coach" }, { href: "#jury", label: "Jury" }, { href: "#afternoon", label: "Afternoon" }]} pill="Private pack" />
      <div className="internal-banner" role="note"><b>{ORGANIZER_PACK_MARKER}.</b> Organizer-only. Do not screen-share, publish, attach to public issues, or copy into participant media.</div>

      <section className="hero organizer-hero"><div className="hero-copy"><p className="kicker"><span /> Day-of runbook</p><h1>Run the room.<br /><em>Defend every score.</em></h1><p className="lede">One operational contract for coaching, recovery, intake, independent judging, feedback, and the afternoon reveal.</p></div></section>

      <section className="phase-section pack-section" id="coach"><div className="section-heading compact"><div><span>01 / COACH</span><h2>Respond to the hypothesis</h2></div><p>The participant owns the answer. The coach protects momentum and equal access to guidance.</p></div>
        <NumberedCards items={coachProtocol} label="Coach response" />
        <h3 className="pack-subheading">Seven checkpoint calls</h3>
        <div className="phase-list">{checkpoints.map((stage) => <article key={stage.id}><span className="phase-id">{stage.beat}</span><div><h3>{stage.time} · {stage.title}</h3><p><b>By now:</b> {stage.shouldHave}</p><p><b>Call:</b> {stage.action}</p><p className="phase-gate"><b>IF NOT</b>{stage.ifYouDont}</p></div></article>)}</div>
        <h3 className="pack-subheading">Sweep and minimal log</h3>
        <NumberedCards items={sweepProtocol} label="Room operation" />
        <h3 className="pack-subheading">Troubleshooting and recovery tree</h3><div className="decision-list">{troubleshooting.map(([failure, response]) => <article className="made" key={failure}><span>→</span><p><b>{failure}:</b> {response}</p></article>)}</div>
      </section>

      <section className="evaluation-section pack-section" id="jury"><div className="section-heading compact"><div><span>02 / JURY</span><h2>Artifact-verifiable anchors</h2></div><p>55 machine points stay deterministic. Two agents independently score 45 jury points and up to 20 bonus; a human resolves defined disagreements.</p></div>
        <div className="jury-category-list">{juryCategories.map((category, categoryIndex) => <article className="jury-category" key={category.name}><header><span>{String(categoryIndex + 1).padStart(2, "0")}</span><div><h3>{category.name}</h3><p><b>Evidence surface</b>{category.headings}</p></div><strong>15 max</strong></header><div className="jury-bands">{category.anchors.map(([points, anchor]) => <div className={`jury-band jury-band-${points}`} key={points}><b>{points}<small>/15</small></b><p>{anchor}</p></div>)}</div></article>)}</div>
        <h3 className="pack-subheading">Optional bonus · 20 maximum</h3><div className="bonus-grid">{bonusCategories.map(([name, points, anchor]) => <article key={name}><strong>{points}<small> max</small></strong><div><h4>{name}</h4><p>{anchor}</p></div></article>)}</div>
        <h3 className="pack-subheading">Independent scoring, escalation, and trace</h3><NumberedCards items={juryProcedure} label="Jury control" />
        <h3 className="pack-subheading">Written feedback template</h3><pre className="feedback-template">{feedbackTemplate.join("\n")}</pre>
      </section>

      <section className="phase-section"><div className="section-heading compact"><div><span>03 / POST-EVENT</span><h2>Seven approved worked approaches</h2></div><p>Release only after the separate post-event gate. These are organizer solutions, never in-session coaching material.</p></div><div className="phase-list">{postEventSolutions.map((solution) => <article key={solution.beat}><span className="phase-id">{solution.beat}</span><div><h3>{solution.title}</h3><p>{solution.approach}</p></div></article>)}</div></section>

      <section className="next-section" id="afternoon"><div><span>04 / AFTERNOON</span><h2>Explain the field,<br />then show the work.</h2><p><b>Consent wording:</b> {consentWording}</p></div><ol>{afternoonRun.map(([time, action]) => <li key={time}><span>{time}</span><div><p>{action}</p></div></li>)}</ol></section>
      <Footer note="Private organizer operations and jury pack · not for participants" />
    </main>
  );
}
