import type { Metadata } from "next";
import { Footer, Topbar } from "./_components/chrome";
import { premise, workingTitle } from "./_content/site";

export const metadata: Metadata = {
  title: "CIV 2026 Data Hackathon — choose your view",
  description: premise,
};

/**
 * Local entry door for organizers. Production builds scan `public-source/app`
 * and never compile this route or its organizer link.
 */
export default function Home() {
  return (
    <main>
      <Topbar pill="Handoff" />

      <section className="door" id="top">
        <p className="kicker">
          <span /> {workingTitle}
        </p>
        <h1>
          Two rooms.
          <br />
          <em>One event.</em>
        </h1>
        <p className="lede">{premise}</p>

        <div className="door-grid">
          <a className="door-card" href="/participants">
            <span className="door-index">01</span>
            <h2>Participants</h2>
            <p>
              What the challenge is, how the three hours run, what you own, what you submit
              and exactly how it is scored.
            </p>
            <b>
              Open the participant view <span>→</span>
            </b>
          </a>

          <a className="door-card organizer" href="/organizers">
            <span className="door-index">02</span>
            <h2>Organizers</h2>
            <p>
              Strategy, teaching goals, preparation phases and gates, evaluation internals,
              facilitation notes, closed decision history and release gates.
            </p>
            <b>
              Open the organizer view <span>→</span>
            </b>
            <em className="door-warning">Internal · not for participants</em>
          </a>
        </div>
      </section>

      <Footer
        note={
          <>
            This local door exposes both views. Production contains only the participant app;
            organizer material is absent from both server and client artifacts. See{" "}
            <code>docs/organizers/README.md</code> for the current organizer checklist.
          </>
        }
        backTo="#top"
      />
    </main>
  );
}
