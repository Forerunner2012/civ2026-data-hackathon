import type { NavLink } from "../_content/site";

/** Shared page chrome. Server components: no audience content is bundled here. */

export function Topbar({
  home = "/",
  nav = [],
  pill,
  participantNavigation = false,
}: {
  home?: string;
  nav?: NavLink[];
  pill: string;
  participantNavigation?: boolean;
}) {
  return (
    <header className={participantNavigation ? "topbar participant-topbar" : "topbar"} data-participant-navigation={participantNavigation || undefined}>
      <a className="brand" href={home} aria-label="CIV 2026 Data Hackathon home">
        <span className="brand-mark">CIV</span>
        <span>Data Hackathon 2026</span>
      </a>
      {nav.length > 0 && (
        <nav aria-label="Page sections">
          {nav.map(({ href, label }, index) => (
            <a key={href} href={href} aria-current={participantNavigation && index === 0 ? "location" : undefined}>
              {label}
            </a>
          ))}
        </nav>
      )}
      {participantNavigation && (
        <div className="participant-section-controls" hidden>
          <button type="button" data-section-previous aria-label="Previous section" disabled>Previous</button>
          <span data-section-position aria-label="Section position">1/{nav.length}</span>
          <button type="button" data-section-next aria-label="Next section">Next</button>
        </div>
      )}
      <span className="internal-pill">{pill}</span>
    </header>
  );
}

export function Footer({ note, backTo = "#top" }: { note: React.ReactNode; backTo?: string }) {
  return (
    <footer>
      <div className="brand">
        <span className="brand-mark">CIV</span>
        <span>Data Hackathon 2026</span>
      </div>
      <p>{note}</p>
      <a href={backTo}>Back to top ↑</a>
    </footer>
  );
}
