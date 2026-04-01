import { describe, expect, it, vi } from "vitest";

import { InMemoryCacheStore } from "@/services/cache-store";

describe("InMemoryCacheStore", () => {
  it("keeps entries isolated by scope", () => {
    vi.useFakeTimers();
    vi.setSystemTime(new Date("2026-04-01T12:00:00.000Z"));

    try {
      const store = new InMemoryCacheStore();

      store.set({
        cache_key: "same-key",
        expires_at: "2026-04-01T12:05:00.000Z",
        payload: {
          value: "identity"
        },
        scope: "identity",
        stored_at: "2026-04-01T12:00:00.000Z"
      });
      store.set({
        cache_key: "same-key",
        expires_at: "2026-04-01T12:05:00.000Z",
        payload: {
          value: "evidence"
        },
        scope: "evidence",
        stored_at: "2026-04-01T12:00:00.000Z"
      });

      const identity = store.get("identity", "same-key");
      const evidence = store.get("evidence", "same-key");

      expect((identity?.payload as { value: string }).value).toBe("identity");
      expect((evidence?.payload as { value: string }).value).toBe("evidence");
    } finally {
      vi.useRealTimers();
    }
  });

  it("evicts expired entries on read", () => {
    vi.useFakeTimers();
    vi.setSystemTime(new Date("2026-04-01T12:00:00.000Z"));

    try {
      const store = new InMemoryCacheStore();

      store.set({
        cache_key: "ttl-key",
        expires_at: "2026-04-01T12:00:01.000Z",
        payload: {
          value: "cached"
        },
        scope: "signal",
        stored_at: "2026-04-01T12:00:00.000Z"
      });

      expect(store.get("signal", "ttl-key")).not.toBeNull();

      vi.setSystemTime(new Date("2026-04-01T12:00:02.000Z"));

      expect(store.get("signal", "ttl-key")).toBeNull();
    } finally {
      vi.useRealTimers();
    }
  });
});
