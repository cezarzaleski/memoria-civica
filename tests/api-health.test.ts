import { describe, expect, it } from "vitest";

import { routeApiRequest } from "../apps/api/src/app";

describe("API health", () => {
  it("returns a simple health payload", async () => {
    const response = await routeApiRequest(
      {
        method: "GET",
        pathname: "/health"
      },
      {
        consult: () => {
          throw new Error("consult should not be called");
        }
      }
    );

    expect(response.statusCode).toBe(200);
    expect(response.payload).toEqual({ status: "ok" });
  });
});
