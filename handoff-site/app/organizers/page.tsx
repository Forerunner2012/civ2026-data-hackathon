import type { Metadata } from "next";
import { Footer, Topbar } from "../_components/chrome";
import { decisionGroups, decisionsMade, historicalDesign, sources } from "../_content/organizers.server";

export const metadata: Metadata = {
  title: "CIV 2026 hackathon design (internal)",
  description: "Historical purpose, workflow, requirements and organizing decisions for CIV 2026.",
  robots: { index: false, follow: false },
};

const nav = historicalDesign.map(({ id, title }) => ({ href: `#${id}`, label: title }));

export default function Organizers() {
  return (
    <main>
      <Topbar nav={nav} pill="Internal" />
      <div className="internal-banner" role="note">
        <b>Organizer view.</b> This historical design includes organizer context. The participant view is <a href="/participants">/participants</a>.
      </div>
      <div className="internal-banner" role="note">
        <b>CIV 2026 historical specification.</b> It does not establish readiness or release approval for another session. Use <code>docs/organizers/README.md</code> for adaptation and preparation.
      </div>
      <section className="hero organizer-hero" id="top">
        <div className="hero-copy">
          <p className="kicker"><span /> Historical design</p>
          <h1>CIV 2026<br /><em>hackathon design</em></h1>
          <p className="lede">This specification describes the agreed CIV 2026 hackathon design and the choices that shaped its material. It provides a reference for understanding and adapting the session.</p>
          <div className="hero-actions">
            <a className="primary-button" href="/organizers/pack">Session operations <span>→</span></a>
            <a className="text-link" href="#decisions">Decisions and sources</a>
          </div>
        </div>
      </section>
      {historicalDesign.map(({ id, title, description }, index) => (
        <section className={`${index % 2 ? "criteria-section" : "phase-section"} historical-spec-section`} id={id} key={id}>
          <div className="section-heading compact">
            <div><span>{String(index + 1).padStart(2, "0")} / HISTORICAL DESIGN</span><h2>{title}</h2></div>
            <p>{description}</p>
          </div>
        </section>
      ))}
      <section className="decision-section" id="decisions">
        <div className="decision-intro">
          <span>DECISIONS AND SOURCES</span><h2>Original design records</h2>
          <p>These records support the historical specification. Original caveats and provisional measurements remain historical evidence, not current readiness or release claims. Current setup and scoring guidance take precedence for an adapted session.</p>
          <p>Use the operations pack for full recovery, intake, scoring and consent procedures.</p>
        </div>
        <div className="decision-column">
          {decisionGroups.map((group) => (
            <div key={group}>
              <b className="decision-heading">{group}</b>
              <div className="decision-list">
                {decisionsMade.filter((item) => item.group === group).map(({ ticket, title, answer, caveat }) => (
                  <article className="made" key={ticket}><span>{ticket}</span><p><b>{title}:</b> {answer}{caveat && <em className="decision-caveat">{caveat}</em>}</p></article>
                ))}
              </div>
            </div>
          ))}
        </div>
      </section>
      <section className="sources-section"><div className="section-label">HISTORICAL SOURCE CONTEXT</div><ol className="source-list">{sources.map((source) => <li key={source}>{source}</li>)}</ol></section>
      <Footer note="Organizer view · historical design · not for participants" />
    </main>
  );
}
