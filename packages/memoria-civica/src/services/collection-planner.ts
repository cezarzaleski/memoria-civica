import type {
  CollectionPlan,
  CollectionTask,
  ResolvedCandidate,
  SignalName
} from "@/domain/models";

interface CollectionPlanningInput {
  readonly candidate: ResolvedCandidate;
  readonly requested_signals: readonly SignalName[];
  readonly user_priorities: readonly string[];
}

function buildTask(
  source: CollectionTask["source"],
  objective: string,
  priority: number,
  params: Record<string, string | undefined>
): CollectionTask {
  return {
    objective,
    params,
    priority,
    source
  };
}

export class CollectionPlanner {
  public plan(input: CollectionPlanningInput): CollectionPlan {
    if (input.candidate.office === "deputado_distrital" && input.candidate.uf !== "DF") {
      throw new Error("deputado_distrital requires uf=DF");
    }

    if (input.candidate.status === "incumbent") {
      return {
        profile: "incumbent_federal",
        requested_signals: input.requested_signals,
        tasks: [
          buildTask("camara", "confirmar_identidade_legislativa", 1, {
            camara_id: input.candidate.official_ids.camara_id,
            name: input.candidate.canonical_name,
            party: input.candidate.party,
            uf: input.candidate.uf
          }),
          ...(input.requested_signals.includes("coherence")
            ? [
                buildTask("camara", "coletar_atuacao_formal", 2, {
                  camara_id: input.candidate.official_ids.camara_id,
                  name: input.candidate.canonical_name
                }),
                buildTask("camara", "coletar_proposicoes_autorais", 3, {
                  camara_id: input.candidate.official_ids.camara_id,
                  name: input.candidate.canonical_name
                }),
                buildTask("camara", "coletar_votacoes_nominais", 4, {
                  camara_id: input.candidate.official_ids.camara_id,
                  name: input.candidate.canonical_name
                })
              ]
            : []),
          ...(input.candidate.office === "deputado_federal"
            ? [
                buildTask("tse", "enriquecer_identidade_eleitoral", 2, {
                  name: input.candidate.canonical_name,
                  office: input.candidate.office,
                  party: input.candidate.party,
                  uf: input.candidate.uf
                })
              ]
            : [])
        ]
      };
    }

    if (input.candidate.status === "former") {
      return {
        profile: "former_parliamentarian",
        requested_signals: input.requested_signals,
        tasks: [
          ...(input.candidate.official_ids.camara_id !== undefined
            ? [
                buildTask("camara", "confirmar_historico_legislativo", 1, {
                  camara_id: input.candidate.official_ids.camara_id,
                  name: input.candidate.canonical_name,
                  party: input.candidate.party,
                  uf: input.candidate.uf
                })
              ]
            : []),
          buildTask("tse", "resolver_identidade_eleitoral", 1, {
            name: input.candidate.canonical_name,
            office: input.candidate.office,
            party: input.candidate.party,
            uf: input.candidate.uf
          })
        ]
      };
    }

    return {
      profile: "challenger",
      requested_signals: input.requested_signals,
      tasks: [
        buildTask("tse", "resolver_identidade_eleitoral", 1, {
          name: input.candidate.canonical_name,
          office: input.candidate.office,
          party: input.candidate.party,
          uf: input.candidate.uf
        })
      ]
    };
  }
}
