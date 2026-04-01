import { describe, expect, it, vi } from "vitest";

import type { CacheEntryRecord } from "@/domain/models";
import { InMemoryIdentityResolver } from "@/services/identity-resolver";

describe("InMemoryIdentityResolver", () => {
  const resolver = new InMemoryIdentityResolver({
    catalog: [
      {
        ambiguity_level: "none",
        aliases: ["Maria de Souza"],
        canonical_name: "Maria Souza",
        office: "deputado_federal",
        official_ids: {
          tse_id: "111"
        },
        party: "PSB",
        status: "challenger",
        uf: "RJ"
      },
      {
        ambiguity_level: "none",
        aliases: ["Joao da Silva"],
        canonical_name: "Joao Silva",
        office: "deputado_federal",
        official_ids: {
          tse_id: "222"
        },
        party: "PT",
        status: "former",
        uf: "SP"
      },
      {
        ambiguity_level: "none",
        aliases: ["Joao Pereira Silva"],
        canonical_name: "Joao Silva",
        office: "deputado_federal",
        official_ids: {
          tse_id: "333"
        },
        party: "MDB",
        status: "challenger",
        uf: "MG"
      }
    ]
  });

  it("resolves a candidate when hints disambiguate the search", async () => {
    const result = await resolver.resolve({
      name: "maria souza",
      office: "deputado_federal",
      uf: "RJ"
    });

    expect(result.kind).toBe("resolved");
    if (result.kind !== "resolved") {
      throw new Error("expected resolved candidate");
    }

    expect(result.candidate.canonical_name).toBe("Maria Souza");
    expect(result.candidate.uf).toBe("RJ");
    expect(result.match_count).toBe(1);
  });

  it("blocks strong ambiguity when more than one candidate remains", async () => {
    const result = await resolver.resolve({
      name: "joao silva",
      office: "deputado_federal"
    });

    expect(result.kind).toBe("ambiguous");
    expect(result.ambiguity_level).toBe("strong");
    if (result.kind !== "ambiguous") {
      throw new Error("expected ambiguous resolution");
    }

    expect(result.candidates).toHaveLength(2);
    expect(result.requires).toEqual(["uf", "party"]);
  });

  it("merges duplicate matches and keeps the strongest candidate profile", async () => {
    const sourcedResolver = new InMemoryIdentityResolver({
      catalog: [
        {
          ambiguity_level: "none",
          aliases: ["Tabata Amaral de Pontes"],
          canonical_name: "Tabata Amaral",
          office: "deputado_federal",
          official_ids: {
            tse_id: "999"
          },
          party: "PSB",
          status: "challenger",
          uf: "SP"
        }
      ],
      sources: [
        {
          source_name: "mcp-brasil",
          searchCandidates: () =>
            Promise.resolve([
              {
                ambiguity_level: "none",
                canonical_name: "Tabata Amaral",
                office: "deputado_federal",
                official_ids: {
                  camara_id: "204534"
                },
                party: "PSB",
                status: "incumbent",
                uf: "SP"
              }
            ])
        }
      ]
    });

    const result = await sourcedResolver.resolve({
      name: "Tabata Amaral",
      office: "deputado_federal",
      uf: "SP"
    });

    expect(result.kind).toBe("resolved");
    if (result.kind !== "resolved") {
      throw new Error("expected resolved candidate");
    }

    expect(result.candidate.status).toBe("incumbent");
    expect(result.candidate.official_ids).toEqual({
      camara_id: "204534",
      tse_id: "999"
    });
    expect(result.candidate.aliases).toEqual(["Tabata Amaral de Pontes"]);
  });

  it("reuses cached source results for repeated identity queries", async () => {
    const source = {
      source_name: "mcp-brasil",
      searchCandidates: vi.fn().mockResolvedValue([
        {
          ambiguity_level: "none",
          canonical_name: "Erika Hilton",
          office: "deputado_federal",
          official_ids: {
            camara_id: "220639"
          },
          party: "PSOL",
          status: "incumbent",
          uf: "SP"
        }
      ])
    };

    const cachedResolver = new InMemoryIdentityResolver({
      cacheTtlMs: 60_000,
      sources: [source]
    });

    const first = await cachedResolver.resolve({
      name: "Erika Hilton",
      office: "deputado_federal",
      uf: "SP"
    });
    const second = await cachedResolver.resolve({
      name: "Erika Hilton",
      office: "deputado_federal",
      uf: "SP"
    });

    expect(first.kind).toBe("resolved");
    expect(second.kind).toBe("resolved");
    expect(source.searchCandidates).toHaveBeenCalledTimes(1);
  });

  it("expires cached identity results after ttl", async () => {
    vi.useFakeTimers();
    vi.setSystemTime(new Date("2026-04-01T12:00:00.000Z"));

    try {
      const source = {
        source_name: "mcp-brasil",
        searchCandidates: vi.fn().mockResolvedValue([
          {
            ambiguity_level: "none",
            canonical_name: "Erika Hilton",
            office: "deputado_federal",
            official_ids: {
              camara_id: "220639"
            },
            party: "PSOL",
            status: "incumbent",
            uf: "SP"
          }
        ])
      };

      const cachedResolver = new InMemoryIdentityResolver({
        cacheTtlMs: 1_000,
        sources: [source]
      });

      await cachedResolver.resolve({
        name: "Erika Hilton",
        office: "deputado_federal",
        uf: "SP"
      });

      await vi.advanceTimersByTimeAsync(1_500);

      await cachedResolver.resolve({
        name: "Erika Hilton",
        office: "deputado_federal",
        uf: "SP"
      });

      expect(source.searchCandidates).toHaveBeenCalledTimes(2);
    } finally {
      vi.useRealTimers();
    }
  });

  it("accepts an injected cache backend", async () => {
    const cacheRecords = new Map<string, CacheEntryRecord>();
    const cacheStore = {
      get: vi.fn((scope: CacheEntryRecord["scope"], key: string) => {
        return cacheRecords.get(`${scope}:${key}`) ?? null;
      }),
      set: vi.fn((entry: CacheEntryRecord) => {
        cacheRecords.set(`${entry.scope}:${entry.cache_key}`, entry);
      })
    };
    const source = {
      source_name: "mcp-brasil",
      searchCandidates: vi.fn().mockResolvedValue([
        {
          ambiguity_level: "none",
          canonical_name: "Erika Hilton",
          office: "deputado_federal",
          official_ids: {
            camara_id: "220639"
          },
          party: "PSOL",
          status: "incumbent",
          uf: "SP"
        }
      ])
    };

    const resolverWithInjectedCache = new InMemoryIdentityResolver({
      cacheStore,
      cacheTtlMs: 60_000,
      sources: [source]
    });

    await resolverWithInjectedCache.resolve({
      name: "Erika Hilton",
      office: "deputado_federal",
      uf: "SP"
    });

    await resolverWithInjectedCache.resolve({
      name: "Erika Hilton",
      office: "deputado_federal",
      uf: "SP"
    });

    expect(cacheStore.set).toHaveBeenCalledTimes(1);
    expect(cacheStore.get).toHaveBeenCalledTimes(2);
    expect(source.searchCandidates).toHaveBeenCalledTimes(1);
  });
});
