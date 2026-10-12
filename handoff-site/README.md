# CIV 2026 hackathon handoff site

Interactive companion to the [organizer guide](../docs/organizers/README.md), split into two
audience views so organizer material is never shown to participants.

| Route | Audience | Contains |
| --- | --- | --- |
| `/` | attendees in public builds; entry door in local/internal builds | Public participant page, equivalent to `/participants`; the local/internal entry door links audience views. |
| `/participants` | attendees | Brief, the three-hour ladder, ownership boundary, deliverables, the published rubric, toolkit and CLI, submission layout, what to come ready with. |
| `/organizers` | **internal** | Strategy/tactics/operations, success criteria and non-goals, the six preparation phases and gates, readiness workstreams, evaluation internals, facilitation mechanics, the seven driving forces, the open decision queue, source precedence. |
| `/organizers/pack` | organizers and jury, **internal** | Day-of coach, recovery, scoring, feedback, and results runbook; absent from the public production artifact. |
| `/live` | attendees, **local only** | Current session beat, cumulative unlocked guidance, countdown, and static fallback. |
| `/live/coach` | coach, **local only** | One authorized, next-only advance action. |
| `/solutions` | attendees, **post-event local release only** | Human-approved worked approaches; unavailable by default and absent from the public production artifact. |

## How the boundary is enforced

Content lives in `app/_content/`, split by audience:

- `participants.ts` — safe for attendees, may be bundled anywhere.
- `organizers.server.ts` — starts with `import "server-only"`. Importing it from a client component
  is a **build error**, so internal material cannot reach a browser bundle by accident.
- `organizer-pack.server.ts` — private coach, recovery, jury-anchor, score-trace, and results material.
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
> Local/internal audience routes are not access control. Public builds exclude organizer, live and solution routes; keep internal builds in their authorized local scope. This documentation does not change route access or hosting.

## Local preview

```powershell
npm install
npm run dev
```

Then open `http://localhost:3000`.

## Live session operation

The live page and coach API exist in local development and internal acceptance builds only. A normal
`npm run build` produces the participant-facing public artifact and excludes `/live`, `/live/coach`,
`/api/live`, and `/solutions`. The seven production beats expose only the current expectation,
hint, and tip; later beats remain server-only. The three printable desk materials live under
`/desk/` and contain no worked answer.

Copy `.env.example` to `.env` — it carries the configured `SUBMISSION_FORM_URL`, and Wrangler loads
it into the dev worker. Add a private coach token to the same file, then start the local server:

```powershell
Copy-Item .env.example .env
Add-Content .env 'LIVE_COACH_TOKEN=replace-with-a-long-random-value'
npm run dev
```

`.env` is git-ignored and is where secrets belong; `.env.example` holds only the public form URL.

Participants open `/live`; the facilitator opens `/live/coach` and enters the same token. The page
advances from the Tokyo schedule automatically. The coach can only advance it one state early;
advances cannot delay, relock, or reverse the room. The in-memory coach floor survives browser
refreshes but resets when the server restarts.

For rehearsals only, enable a controlled clock and append an ISO-8601 `now` query:

```powershell
Add-Content .env 'LIVE_ALLOW_CONTROLLED_CLOCK=true'
# http://localhost:3000/live?now=2026-09-03T10:40:00%2B09:00
```

The accepted Vinext worker loads these values from `.env`; setting them only in the parent
PowerShell process does not configure the worker routes. Remove the controlled-clock line after the
rehearsal and keep the coach token private.

Leave `LIVE_ALLOW_CONTROLLED_CLOCK` unset on event day. If the local server or network is
unavailable, serve or open `/session-fallback.html`; it is static, script-free, and
participant-safe.

The post-event solution route is separately controlled. Before approval, organizers may build an
internal preview with `POST_EVENT_SOLUTIONS_PREVIEW=true`. Release requires both the checked-in
status to be `approved` and `POST_EVENT_SOLUTIONS_RELEASED=true`; preview and release flags remain
unset during the session. No release flag can add this route to the public production artifact.

`SUBMISSION_FORM_URL` is participant-visible by design. It must be HTTPS and must not contain
credentials. On event day it is the public Tally form URL, currently `https://tally.so/r/81Yy1x`; the
form collects participant identity, the SHA-256 printed by `civ report`, and the unchanged
`submission.zip`, and shows a confirmation containing its unique submission reference. Provider
configuration and the export-to-envelope mapping are in
[`docs/phase1/intake-acceptance.md`](../docs/phase1/intake-acceptance.md). Organizer credentials and
response exports remain outside this site.

## Verification

```powershell
npm run build
node --test tests/rendered-html.test.mjs   # or: npm run test
npm run lint
```

### Participant navigation browser check

After `npm test`, run `npm run test:navigation` from this directory. The check uses an existing Chromium browser, a temporary local server and an isolated browser profile. It exercises the two public routes and both exported files at desktop/mobile sizes, then checks the disk fallback with JavaScript disabled. Receipts and screenshots stay in ignored `tmp/navigation-browser/`.

Windows defaults to the installed Microsoft Edge executable. Set `CIV_BROWSER_EXECUTABLE` to an existing Chrome or Chromium executable on another test host. This browser is test infrastructure; participants do not need it for the CLI workflows.

## Participant content ownership

Canonical commands and recovery belong to `docs/quickstart.md` and `docs/setup.md`; runtime limits belong to `docs/runtime-requirements.md`, and point-resource instructions belong to `docs/extension.md`. Kit inventory and assembly copy those exact files. The website summarizes them and displays kit-relative paths. Update the guide and affected participant summaries together.

The participant page and offline export are static guidance with local section navigation. Room progress comes from the separately supplied live page. Export retains only `participant-navigation.js`; framework JavaScript and organizer/live content remain excluded. Local label qualification does not make a pack available for download or authorize distribution. Use the pack announced for the exact source and event definition.
