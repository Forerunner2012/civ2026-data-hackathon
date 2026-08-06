# CIV 2026 hackathon handoff site

Interactive companion to [`../HACKATHON-HANDOFF.md`](../HACKATHON-HANDOFF.md), split into two
audience views so organizer material is never shown to participants.

| Route | Audience | Contains |
| --- | --- | --- |
| `/` | either | Entry door. Links to both views, carries no audience content of its own. |
| `/participants` | attendees | Brief, the three-hour ladder, ownership boundary, deliverables, the published rubric, toolkit and CLI, submission layout, what to come ready with. |
| `/organizers` | **internal** | Strategy/tactics/operations, success criteria and non-goals, the six preparation phases and gates, readiness workstreams, evaluation internals, facilitation mechanics, the seven driving forces, the open decision queue, source precedence. |
| `/live` | attendees, **local only** | Current session beat, cumulative unlocked guidance, countdown, and static fallback. |
| `/live/coach` | coach, **local only** | One authorized, next-only advance action. |

## How the boundary is enforced

Content lives in `app/_content/`, split by audience:

- `participants.ts` — safe for attendees, may be bundled anywhere.
- `organizers.server.ts` — starts with `import "server-only"`. Importing it from a client component
  is a **build error**, so internal material cannot reach a browser bundle by accident.
- `live-content.server.ts` — holds the complete time-embargoed live copy behind the same structural
  server-only boundary. Client components receive only the current stage and cumulative unlocked
  guidance selected by `live-store.server.ts`.
- `live-state.ts` — contains content-free schedule and monotonic advance mechanics plus shared types.
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

## Live session operation

The live page and coach API exist in local development and internal acceptance builds only. A normal
`npm run build` produces the participant-facing public artifact and excludes `/live`, `/live/coach`,
and `/api/live`. The current beats and guidance are representative Phase 1 copy for testing every
transition; final teaching-unit authoring remains later-phase work.

Set a private coach token before starting the local server:

```powershell
$env:LIVE_COACH_TOKEN = "replace-with-a-long-random-value"
$env:SUBMISSION_FORM_URL = "https://your-configured-form.example/response"
npm run dev
```

Participants open `/live`; the facilitator opens `/live/coach` and enters the same token. The page
advances from the Tokyo schedule automatically. The coach can only advance it one state early;
advances cannot delay, relock, or reverse the room. The in-memory coach floor survives browser
refreshes but resets when the server restarts.

For rehearsals only, enable a controlled clock and append an ISO-8601 `now` query:

```powershell
$env:LIVE_ALLOW_CONTROLLED_CLOCK = "true"
# http://localhost:3000/live?now=2026-09-03T10:40:00%2B09:00
```

Leave `LIVE_ALLOW_CONTROLLED_CLOCK` unset on event day. If the local server or network is
unavailable, serve or open `/session-fallback.html`; it is static, script-free, and
participant-safe.

`SUBMISSION_FORM_URL` is participant-visible by design. It must be HTTPS and must not contain
credentials. Configure the external form to collect participant identity, the SHA-256 printed by
`civ report`, and the unchanged `submission.zip`, and to show a confirmation containing its server
receipt timestamp. Organizer credentials and response exports remain outside this site.

## Verification

```powershell
npm run build
node --test tests/rendered-html.test.mjs   # or: npm run test
npm run lint
```
