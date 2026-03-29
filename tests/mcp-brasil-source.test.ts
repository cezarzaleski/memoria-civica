import { describe, expect, it, vi } from "vitest";

import {
  McpBrasilEvidenceCollector,
  McpBrasilIdentitySource
} from "@/source-connectors/mcp-brasil";
import type { CollectionPlan, ResolvedCandidate } from "@/domain/models";

describe("McpBrasilIdentitySource", () => {
  it("maps the live camera listing format into resolved candidates", async () => {
    const client = {
      callTool: vi.fn().mockResolvedValue(
        "Deputados federais (pagina 1):\n\n| ID | Nome | Partido | UF | Email |\n| --- | --- | --- | --- | --- |\n| 220645 | Erika Hilton | PSOL | SP | dep.erikahilton@camara.leg.br |"
      )
    };

    const source = new McpBrasilIdentitySource(client);

    const result = await source.searchCandidates({
      name: "Erika Hilton",
      office: "deputado_federal",
      party: "PSOL",
      uf: "SP"
    });

    expect(client.callTool).toHaveBeenCalledWith("camara_listar_deputados", {
      nome: "Erika Hilton",
      sigla_partido: "PSOL",
      sigla_uf: "SP"
    });
    expect(result).toEqual([
      {
        ambiguity_level: "none",
        canonical_name: "Erika Hilton",
        office: "deputado_federal",
        official_ids: {
          camara_id: "220645"
        },
        party: "PSOL",
        status: "incumbent",
        uf: "SP"
      }
    ]);
  });

  it("returns an empty list when the source returns no rows", async () => {
    const client = {
      callTool: vi.fn().mockResolvedValue("Nenhum deputado encontrado.")
    };

    const source = new McpBrasilIdentitySource(client);

    const result = await source.searchCandidates({
      name: "Nome Inexistente",
      office: "deputado_federal"
    });

    expect(result).toEqual([]);
  });

  it("falls back to TSE state results for federal candidates outside the Camara listing", async () => {
    const client = {
      callTool: vi
        .fn()
        .mockResolvedValueOnce("Nenhum deputado encontrado.")
        .mockResolvedValueOnce(
          "Resultado da eleicao para deputado_federal em SP:\n\n| Posicao | Nome | Numero | Votos | Percentual |\n| --- | --- | --- | --- | --- |\n| 1 | Sonia Guajajara | 5080 | 156175 | 0,75% |"
        )
    };

    const source = new McpBrasilIdentitySource(client);

    const result = await source.searchCandidates({
      name: "Sonia Guajajara",
      office: "deputado_federal",
      uf: "SP"
    });

    expect(client.callTool).toHaveBeenNthCalledWith(1, "camara_listar_deputados", {
      nome: "Sonia Guajajara",
      sigla_partido: undefined,
      sigla_uf: "SP"
    });
    expect(client.callTool).toHaveBeenNthCalledWith(2, "tse_resultado_por_estado", {
      ano: 2022,
      cargo: "deputado_federal",
      uf: "SP"
    });
    expect(result).toEqual([
      {
        ambiguity_level: "none",
        canonical_name: "Sonia Guajajara",
        office: "deputado_federal",
        official_ids: {
          mcp_brasil_id: "tse:2022:SP:deputado_federal:5080"
        },
        status: "challenger",
        uf: "SP"
      }
    ]);
  });

  it("uses TSE state results directly for deputado distrital in DF", async () => {
    const client = {
      callTool: vi.fn().mockResolvedValue(
        "Resultado da eleicao para deputado_distrital em DF:\n\n| Posicao | Nome | Numero | Votos | Percentual |\n| --- | --- | --- | --- | --- |\n| 1 | Chico Vigilante | 13123 | 259123 | 1,50% |"
      )
    };

    const source = new McpBrasilIdentitySource(client);

    const result = await source.searchCandidates({
      name: "Chico Vigilante",
      office: "deputado_distrital",
      uf: "DF"
    });

    expect(client.callTool).toHaveBeenCalledWith("tse_resultado_por_estado", {
      ano: 2022,
      cargo: "deputado_distrital",
      uf: "DF"
    });
    expect(result).toEqual([
      {
        ambiguity_level: "none",
        canonical_name: "Chico Vigilante",
        office: "deputado_distrital",
        official_ids: {
          mcp_brasil_id: "tse:2022:DF:deputado_distrital:13123"
        },
        status: "challenger",
        uf: "DF"
      }
    ]);
  });

  it("adds a conservative integrity screening when Transparencia finds no sanctions", async () => {
    const client = {
      callTool: vi.fn((name: string) => {
        if (name === "camara_listar_deputados") {
          return Promise.resolve(
            "Deputados federais (pagina 1):\n\n| ID | Nome | Partido | UF |\n| --- | --- | --- | --- |\n| 220639 | Erika Hilton | PSOL | SP |"
          );
        }

        if (name === "camara_buscar_deputado") {
          return Promise.resolve(
            "**ERIKA HILTON**\n- Partido: PSOL\n- UF: SP\n- Email: dep.erikahilton@camara.leg.br\n- Legislatura: 57"
          );
        }

        if (name === "transparencia_buscar_sancoes") {
          return Promise.resolve(
            "Nenhuma sanção encontrada para 'Erika Hilton' nas bases: ceis, cnep."
          );
        }

        return Promise.resolve("");
      })
    };

    const collector = new McpBrasilEvidenceCollector(client);
    const candidate: ResolvedCandidate = {
      ambiguity_level: "none",
      canonical_name: "Erika Hilton",
      office: "deputado_federal",
      official_ids: {
        camara_id: "220639"
      },
      party: "PSOL",
      status: "incumbent",
      uf: "SP"
    };
    const plan: CollectionPlan = {
      profile: "incumbent_federal",
      requested_signals: ["evidence_level", "integrity", "coherence"],
      tasks: [
        {
          objective: "confirmar_identidade_legislativa",
          params: {
            camara_id: "220639",
            name: "Erika Hilton",
            party: "PSOL",
            uf: "SP"
          },
          priority: 1,
          source: "camara"
        },
        {
          objective: "coletar_atuacao_formal",
          params: {
            camara_id: "220639",
            name: "Erika Hilton"
          },
          priority: 2,
          source: "camara"
        }
      ]
    };

    const result = await collector.collect(candidate, plan);

    expect(client.callTool).toHaveBeenCalledWith("camara_listar_deputados", {
      nome: "Erika Hilton",
      sigla_partido: "PSOL",
      sigla_uf: "SP"
    });
    expect(client.callTool).toHaveBeenCalledWith("camara_buscar_deputado", {
      deputado_id: 220639
    });
    expect(client.callTool).toHaveBeenCalledWith("transparencia_buscar_sancoes", {
      bases: ["ceis", "cnep"],
      consulta: "Erika Hilton",
      pagina: 1
    });
    expect(result).toEqual(
      expect.arrayContaining([
        expect.objectContaining({
          evidence_type: "legislative_profile",
          signal_type: "evidence_level",
          source_name: "camara"
        }),
        expect.objectContaining({
          evidence_type: "formal_activity_record",
          signal_type: "coherence",
          source_name: "camara",
          strength: "strong_official"
        }),
        expect.objectContaining({
          evidence_type: "integrity_screening",
          signal_type: "integrity",
          source_name: "transparencia",
          strength: "strong_official"
        })
      ])
    );

    const integrityEvidence = result.find((item) => item.signal_type === "integrity");

    expect(integrityEvidence).toMatchObject({
      source_url: "https://api.portaldatransparencia.gov.br/api-de-dados/ceis"
    });
    expect(integrityEvidence?.summary).toContain(
      "Limitacao: depende do nome informado"
    );
  });
});
