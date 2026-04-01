import { describe, expect, it } from "vitest";

import { CollectionPlanner } from "@/services/collection-planner";

describe("CollectionPlanner", () => {
  const planner = new CollectionPlanner();

  it("prioritizes Camara then TSE for incumbents", () => {
    const plan = planner.plan({
      candidate: {
        ambiguity_level: "none",
        canonical_name: "Erika Hilton",
        office: "deputado_federal",
        official_ids: {
          camara_id: "220645"
        },
        party: "PSOL",
        status: "incumbent",
        uf: "SP"
      },
      requested_signals: ["evidence_level", "integrity", "coherence"],
      user_priorities: ["transparencia"]
    });

    expect(plan.profile).toBe("incumbent_federal");
    expect(plan.tasks.map((task) => task.source)).toEqual(["camara", "camara", "tse"]);
    expect(plan.tasks.map((task) => task.objective)).toEqual([
      "confirmar_identidade_legislativa",
      "coletar_atuacao_formal",
      "enriquecer_identidade_eleitoral"
    ]);
  });

  it("prioritizes TSE for challengers", () => {
    const plan = planner.plan({
      candidate: {
        ambiguity_level: "none",
        canonical_name: "Maria Souza",
        office: "deputado_federal",
        official_ids: {},
        party: "PSB",
        status: "challenger",
        uf: "RJ"
      },
      requested_signals: ["evidence_level"],
      user_priorities: []
    });

    expect(plan.profile).toBe("challenger");
    expect(plan.tasks.map((task) => task.source)).toEqual(["tse"]);
    expect(plan.tasks[0]).toMatchObject({
      objective: "resolver_identidade_eleitoral",
      params: {
        office: "deputado_federal",
        party: "PSB",
        uf: "RJ"
      }
    });
  });

  it("uses only TSE for distrito federal scope", () => {
    const plan = planner.plan({
      candidate: {
        ambiguity_level: "none",
        canonical_name: "Candidata DF",
        office: "deputado_distrital",
        official_ids: {},
        party: "PSB",
        status: "challenger",
        uf: "DF"
      },
      requested_signals: ["evidence_level"],
      user_priorities: []
    });

    expect(plan.profile).toBe("challenger");
    expect(plan.tasks).toHaveLength(1);
    expect(plan.tasks[0]).toMatchObject({
      source: "tse",
      params: {
        office: "deputado_distrital",
        uf: "DF"
      }
    });
  });

  it("keeps a former parliamentarian on a historic legislative trail before TSE", () => {
    const plan = planner.plan({
      candidate: {
        ambiguity_level: "none",
        canonical_name: "Joao Silva",
        office: "deputado_federal",
        official_ids: {
          camara_id: "220000",
          tse_id: "222"
        },
        party: "PT",
        status: "former",
        uf: "SP"
      },
      requested_signals: ["evidence_level"],
      user_priorities: []
    });

    expect(plan.profile).toBe("former_parliamentarian");
    expect(plan.tasks.map((task) => task.source)).toEqual(["camara", "tse"]);
    expect(plan.tasks.map((task) => task.objective)).toEqual([
      "confirmar_historico_legislativo",
      "resolver_identidade_eleitoral"
    ]);
  });
});
