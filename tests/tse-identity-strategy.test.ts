import { describe, expect, it } from "vitest";

import { buildTseIdentityStrategy } from "@/source-connectors/tse-identity-strategy";

describe("buildTseIdentityStrategy", () => {
  it("builds the lookup chain for deputy candidate discovery", () => {
    const strategy = buildTseIdentityStrategy({
      name: "Tabata Amaral",
      office: "deputado_federal",
      party: "PSB",
      uf: "SP"
    });

    expect(strategy.year).toBe(2022);
    expect(strategy.steps).toEqual([
      "tse_listar_eleicoes",
      "tse_listar_cargos",
      "tse_listar_candidatos",
      "tse_buscar_candidato"
    ]);
    expect(strategy.requiresUf).toBe(true);
    expect(strategy.requiresMunicipalityScope).toBe(true);
  });

  it("supports deputado_distrital only in DF", () => {
    const strategy = buildTseIdentityStrategy({
      name: "Candidata DF",
      office: "deputado_distrital",
      uf: "DF"
    });

    expect(strategy.year).toBe(2022);
  });

  it("rejects deputado_distrital outside DF", () => {
    expect(() =>
      buildTseIdentityStrategy({
        name: "Nome Teste",
        office: "deputado_distrital",
        uf: "GO"
      })
    ).toThrow("deputado_distrital requires uf=DF");
  });
});
