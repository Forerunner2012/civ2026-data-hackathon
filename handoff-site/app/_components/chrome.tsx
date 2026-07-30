import type { NavLink } from "../_content/site";

/** Shared page chrome. Server components: no audience content is bundled here. */

export function Topbar({
  home = "/",
  nav = [],
  pill,
}: {
  home?: string;
  nav?: NavLink[];
  pill: string;
}) {
  return (
    <header className="topbar">
      <a className="brand" href={home} aria-label="CIV 2026 Data Hackathon home">
        <span className="brand-mark">CIV</span>
        <span>Data Hackathon 2026</span>
      </a>
      {nav.length > 0 && (
        <nav aria-label="Page sections">
          {nav.map(({ href, label }) => (
            <a key={href} href={href}>
              {label}
            </a>
          ))}
        </nav>
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
