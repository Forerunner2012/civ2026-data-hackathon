import type { Metadata } from "next";
import { Footer, Topbar } from "./_components/chrome";
import { premise, workingTitle } from "./_content/site";

export const metadata: Metadata = {
  title: "CIV 2026 Data Hackathon — choose your view",
  description: premise,
};

/**
 * Entry door. Carries no audience-specific content of its own, so it can be
 * shown to either room while the two views stay separate underneath.
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
              What the challenge is, how the three hours run, what your team owns, what you submit
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
              facilitation notes and everything still to be settled.
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
            The two views are separate routes on purpose. Organizer material is never bundled into
            the participant page — see <code>HACKATHON-HANDOFF.md</code> for the full handoff.
          </>
        }
        backTo="#top"
      />
    </main>
  );
}
