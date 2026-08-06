import {
  advanceLiveStage,
  liveSnapshotAt,
  requestClockFromValue,
} from "../../_content/live-store.server";

function json(data: unknown, init: ResponseInit = {}): Response {
  const headers = new Headers(init.headers);
  headers.set("cache-control", "no-store");
  return Response.json(data, { ...init, headers });
}

function methodNotAllowed(): Response {
  return new Response("Method not allowed", {
    status: 405,
    headers: { allow: "GET, POST", "cache-control": "no-store" },
  });
}

function requestClock(request: Request): number {
  return requestClockFromValue(new URL(request.url).searchParams.get("now"));
}

function isAuthorized(request: Request): boolean {
  const expected = process.env.LIVE_COACH_TOKEN;
  if (!expected) {
    return false;
  }
  return request.headers.get("authorization") === `Bearer ${expected}`;
}

export function GET(request: Request): Response {
  try {
    return json(liveSnapshotAt(requestClock(request)));
  } catch (error) {
    return json({ error: (error as Error).message }, { status: 400 });
  }
}

export async function POST(request: Request): Promise<Response> {
  if (!process.env.LIVE_COACH_TOKEN) {
    return json({ error: "coach advance is not configured" }, { status: 503 });
  }
  if (!isAuthorized(request)) {
    return json({ error: "coach authorization failed" }, { status: 401 });
  }
  try {
    const body = (await request.json()) as Record<string, unknown>;
    if (typeof body.requestId !== "string" || body.requestId.length < 8) {
      return json({ error: "requestId must be at least eight characters" }, { status: 400 });
    }
    if (typeof body.observedStageId !== "string") {
      return json({ error: "observedStageId is required" }, { status: 400 });
    }
    const result = advanceLiveStage(
      requestClock(request),
      body.requestId,
      body.observedStageId,
    );
    return json(result, { status: result.outcome === "stale" ? 409 : 200 });
  } catch (error) {
    return json({ error: (error as Error).message }, { status: 400 });
  }
}

export const PUT = methodNotAllowed;
export const PATCH = methodNotAllowed;
export const DELETE = methodNotAllowed;
