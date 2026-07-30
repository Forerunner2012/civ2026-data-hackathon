"use client";

import { useState } from "react";

export type LevelPanel = {
  id: string;
  eyebrow: string;
  title: string;
  summary: string;
  steps: string[][];
};

/**
 * Interactive strategy/tactics/operations switch.
 *
 * Deliberately generic: it renders whatever panels the server passes in, so it
 * carries no organizer content of its own and stays safe to bundle anywhere.
 */
export function LevelTabs({ panels }: { panels: LevelPanel[] }) {
  const [active, setActive] = useState(panels[0]?.id);
  const panel = panels.find((item) => item.id === active) ?? panels[0];

  return (
    <>
      <div className="level-tabs" role="tablist" aria-label="Planning level">
        {panels.map((item, index) => (
          <button
            key={item.id}
            className={panel?.id === item.id ? "active" : ""}
            onClick={() => setActive(item.id)}
            role="tab"
            aria-selected={panel?.id === item.id}
          >
            <span>0{index + 1}</span>
            {item.id}
          </button>
        ))}
      </div>
      <div className="plan-panel">
        <div className="plan-intro">
          <span>{panel?.eyebrow}</span>
          <h3>{panel?.title}</h3>
          <p>{panel?.summary}</p>
        </div>
        <div className="plan-steps">
          {panel?.steps.map(([number, title, text]) => (
            <article key={`${panel.id}-${number}`}>
              <b>{number}</b>
              <div>
                <h4>{title}</h4>
                <p>{text}</p>
              </div>
            </article>
          ))}
        </div>
      </div>
    </>
  );
}
