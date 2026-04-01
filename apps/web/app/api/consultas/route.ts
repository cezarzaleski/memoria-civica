import { NextResponse } from "next/server";

function readApiBaseUrl(): string | null {
  const value = process.env.MEMORIA_CIVICA_API_BASE_URL?.trim();
  return value ? value.replace(/\/$/, "") : null;
}

export async function POST(request: Request): Promise<Response> {
  const apiBaseUrl = readApiBaseUrl();

  if (apiBaseUrl === null) {
    return NextResponse.json(
      {
        error: {
          code: "API_BASE_URL_MISSING",
          message: "MEMORIA_CIVICA_API_BASE_URL nao configurada."
        }
      },
      {
        status: 500
      }
    );
  }

  const payload = (await request.json()) as unknown;
  const upstreamResponse = await fetch(`${apiBaseUrl}/consultas`, {
    body: JSON.stringify(payload),
    headers: {
      "content-type": "application/json"
    },
    method: "POST"
  });
  const upstreamPayload = (await upstreamResponse.json()) as unknown;

  return NextResponse.json(upstreamPayload, {
    status: upstreamResponse.status
  });
}
