import { describe, expect, it } from "vitest";

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
});
