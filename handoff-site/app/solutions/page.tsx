import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { Footer, Topbar } from "../_components/chrome";
import {
  postEventSolutions,
  solutionRelease,
} from "../_content/post-event-solutions.server";

export const metadata: Metadata = {
  title: "CIV 2026 — post-event worked approaches",
  robots: { index: false, follow: false },
};

export default function Solutions() {
  const preview = process.env.POST_EVENT_SOLUTIONS_PREVIEW === "true";
  const released =
    process.env.POST_EVENT_SOLUTIONS_RELEASED === "true" &&
    solutionRelease.status === "approved";
  if (!preview && !released) {
    notFound();
  }

  return (
    <main>
      <Topbar nav={[]} pill={preview ? "Post-event · approval preview" : "Post-event · released"} />
      <section className="phase-section">
        <div className="section-heading compact">
          <div>
            <span>WORKED APPROACHES · SEPARATE RELEASE</span>
            <h1>Seven beats, one defensible workflow.</h1>
          </div>
          <p>
            These approaches explain the method after the event. They do not publish held-back
            labels, private interval coordinates, or infer maneuver handedness.
          </p>
        </div>
        <div className="phase-list">
          {postEventSolutions.map(({ beat, title, approach }) => (
            <article key={beat}>
              <span className="phase-id">{beat}</span>
              <div><h3>{title}</h3><p>{approach}</p></div>
            </article>
          ))}
        </div>
      </section>
      <Footer note="Post-event worked approaches · released only after organizer approval" />
    </main>
  );
}
