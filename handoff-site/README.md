# CIV 2026 hackathon handoff site

Interactive companion to [`../HACKATHON-HANDOFF.md`](../HACKATHON-HANDOFF.md), split into two
audience views so organizer material is never shown to participants.

| Route | Audience | Contains |
| --- | --- | --- |
| `/` | either | Entry door. Links to both views, carries no audience content of its own. |
| `/participants` | attendees | Brief, the three-hour ladder, ownership boundary, deliverables, the published rubric, toolkit and CLI, submission layout, what to come ready with. |
| `/organizers` | **internal** | Strategy/tactics/operations, success criteria and non-goals, the six preparation phases and gates, readiness workstreams, evaluation internals, facilitation mechanics, the seven driving forces, the open decision queue, source precedence. |

## How the boundary is enforced

Content lives in `app/_content/`, split by audience:

- `participants.ts` — safe for attendees, may be bundled anywhere.
- `organizers.server.ts` — starts with `import "server-only"`. Importing it from a client component
  is a **build error**, so internal material cannot reach a browser bundle by accident.
- `site.ts` — the small neutral set both views share.

Client components (`app/_components/level-tabs.tsx`) are deliberately generic: they render whatever
panels the server passes in and hold no content of their own.

`tests/rendered-html.test.mjs` enforces the boundary at build time. `ORGANIZER_ONLY` lists phrases
that must never appear in the participant route, on the entry door, or in any file under
`dist/client/`. **Add a phrase to that list whenever new internal content lands in
`organizers.server.ts`.**

> [!IMPORTANT]
> The split is a *content* boundary, not access control. `/organizers` is unauthenticated — anyone
> who knows the URL can read it. It is marked `noindex`, but before deploying anywhere participants
> can reach, put a real gate in front of the route (`worker/index.ts` is the place to do it).

## Local preview

```powershell
npm install
npm run dev
```

Then open `http://localhost:3000`.

## Verification

```powershell
npm run build
node --test tests/rendered-html.test.mjs   # or: npm run test
npm run lint
```
