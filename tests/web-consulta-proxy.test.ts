import { afterEach, describe, expect, it, vi } from "vitest";

import { POST } from "../apps/web/app/api/consultas/route";

describe("web consulta proxy", () => {
  afterEach(() => {
    delete process.env.MEMORIA_CIVICA_API_BASE_URL;
    vi.restoreAllMocks();
  });

  it("forwards the request to the VPS API", async () => {
    process.env.MEMORIA_CIVICA_API_BASE_URL = "https://api.memoriacivica.test";

    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        json: () => {
          return Promise.resolve({
            summary: "ok"
          });
        },
        status: 200
      })
    );

    const request = new Request("http://localhost/api/consultas", {
      body: JSON.stringify({
        candidate_name: "Tabata Amaral"
      }),
      headers: {
        "content-type": "application/json"
      },
      method: "POST"
    });

    const response = await POST(request);
    const payload = (await response.json()) as { summary: string };

    expect(fetch).toHaveBeenCalledWith("https://api.memoriacivica.test/consultas", {
      body: JSON.stringify({
        candidate_name: "Tabata Amaral"
      }),
      headers: {
        "content-type": "application/json"
      },
      method: "POST"
    });
    expect(response.status).toBe(200);
    expect(payload.summary).toBe("ok");
  });

  it("returns a clear error when the backend URL is missing", async () => {
    const request = new Request("http://localhost/api/consultas", {
      body: JSON.stringify({
        candidate_name: "Tabata Amaral"
      }),
      headers: {
        "content-type": "application/json"
      },
      method: "POST"
    });

    const response = await POST(request);
    const payload = (await response.json()) as {
      error: { code: string; message: string };
    };

    expect(response.status).toBe(500);
    expect(payload.error.code).toBe("API_BASE_URL_MISSING");
  });
});
