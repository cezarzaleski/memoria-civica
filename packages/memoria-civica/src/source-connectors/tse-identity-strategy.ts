import type { IdentityQuery } from "@/domain/models";

export interface TseIdentityStrategy {
  readonly requiresMunicipalityScope: boolean;
  readonly requiresUf: boolean;
  readonly steps: readonly [
    "tse_listar_eleicoes",
    "tse_listar_cargos",
    "tse_listar_candidatos",
    "tse_buscar_candidato"
  ];
  readonly year: 2022;
}

export function buildTseIdentityStrategy(
  query: IdentityQuery
): TseIdentityStrategy {
  if (
    query.office !== "deputado_federal" &&
    query.office !== "deputado_distrital"
  ) {
    throw new Error("unsupported office for TSE identity strategy");
  }

  if (query.office === "deputado_distrital" && query.uf !== "DF") {
    throw new Error("deputado_distrital requires uf=DF");
  }

  return {
    requiresMunicipalityScope: true,
    requiresUf: true,
    steps: [
      "tse_listar_eleicoes",
      "tse_listar_cargos",
      "tse_listar_candidatos",
      "tse_buscar_candidato"
    ],
    year: 2022
  };
}
