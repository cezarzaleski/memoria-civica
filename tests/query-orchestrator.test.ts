import { describe, expect, it, vi } from "vitest";

import { QueryOrchestrator } from "@/services/query-orchestrator";
import type {
  EvidenceRecord,
  IdentityResolution,
  ResolvedCandidate
} from "@/domain/models";

describe("QueryOrchestrator", () => {
  it("coordinates identity resolution, persists raw evidence and returns a stable assembled payload", async () => {
    const candidate: ResolvedCandidate = {
      ambiguity_level: "none",
      aliases: ["Erika Santos Silva"],
      canonical_name: "Erika Hilton",
      office: "deputado_federal",
      official_ids: {
        camara_id: "220639",
        tse_id: "1234567890"
      },
      party: "PSOL",
      status: "incumbent",
      uf: "SP"
    };

    const identityResolution: IdentityResolution = {
      ambiguity_level: "none",
      kind: "resolved",
      match_count: 1,
      candidate
    };

    const identityResolver = {
      resolve: vi.fn().mockResolvedValue(identityResolution)
    };

    const evidence: EvidenceRecord[] = [
      {
        collected_at: "2026-03-29T12:00:00.000Z",
        evidence_id: "ev-1",
        evidence_type: "legislative_profile",
        person_id: "camara:220639",
        signal_type: "evidence_level",
        source_name: "camara",
        source_url: "https://dadosabertos.camara.leg.br/api/v2/deputados/220639",
        strength: "strong_official",
        summary: "Cadastro oficial do deputado na Camara."
      },
      {
        collected_at: "2026-03-29T12:00:01.000Z",
        evidence_id: "ev-2",
        evidence_type: "formal_activity_record",
        person_id: "camara:220639",
        signal_type: "coherence",
        source_name: "camara",
        source_url: "https://dadosabertos.camara.leg.br/api/v2/deputados/220639",
        strength: "strong_official",
        summary: "Perfil formal detalhado do deputado na Camara."
      }
    ];

    const evidenceCollector = {
      collect: vi.fn().mockResolvedValue(evidence)
    };
    const evidenceStore = {
      save: vi.fn().mockResolvedValue(evidence)
    };

    const orchestrator = new QueryOrchestrator({
      evidenceCollector,
      evidenceStore,
      identityResolver
    });

    const result = await orchestrator.consult({
      candidate_name: "Erika Hilton",
      uf: "SP",
      user_priorities: ["transparencia"]
    });

    expect(identityResolver.resolve).toHaveBeenCalledWith({
      name: "Erika Hilton",
      office: "deputado_federal",
      party: undefined,
      uf: "SP"
    });
    expect(evidenceCollector.collect).toHaveBeenCalledTimes(1);
    expect(evidenceStore.save).toHaveBeenCalledWith(evidence);
    expect(result.response.candidate.canonical_name).toBe("Erika Hilton");
    expect(result.response.traffic_light).toBe("yellow");
    expect(result.response.confidence).toBe("medium");
    expect(result.response.alerts).toContain("Coleta oficial ainda insuficiente para conclusao final.");
    expect(result.response.alerts).toContain(
      "Coherence ainda depende de atuacao formal da Camara; autoria, relatoria e votos nominais por deputado ainda nao foram integrados."
    );
    expect(result.response.sources).toEqual([
      "https://dadosabertos.camara.leg.br/api/v2/deputados/220639"
    ]);
    expect(result.response.signals.evidence_level.status).toBe("mixed");
    expect(result.response.signals.evidence_level.evidence_ids).toEqual(["ev-1"]);
    expect(result.response.signals.coherence.status).toBe("mixed");
    expect(result.response.signals.coherence.evidence_ids).toEqual(["ev-2"]);
    expect(result.response.signals.integrity.status).toBe("insufficient");
    expect(result.execution.steps).toEqual([
      "request_validated",
      "identity_resolved",
      "collection_planned",
      "evidence_collected",
      "evidence_stored",
      "evidence_classified",
      "signals_computed",
      "response_assembled"
    ]);
  });

  it("keeps a gray response when no evidence is collected", async () => {
    const candidate: ResolvedCandidate = {
      ambiguity_level: "none",
      canonical_name: "Sonia Guajajara",
      office: "deputado_federal",
      official_ids: {
        mcp_brasil_id: "tse:2022:SP:deputado_federal:5080"
      },
      status: "challenger",
      uf: "SP"
    };

    const identityResolver = {
      resolve: vi.fn().mockResolvedValue({
        ambiguity_level: "none",
        kind: "resolved",
        match_count: 1,
        candidate
      } satisfies IdentityResolution)
    };
    const evidenceCollector = {
      collect: vi.fn().mockResolvedValue([])
    };
    const evidenceStore = {
      save: vi.fn().mockResolvedValue([])
    };

    const orchestrator = new QueryOrchestrator({
      evidenceCollector,
      evidenceStore,
      identityResolver
    });

    const result = await orchestrator.consult({
      candidate_name: "Sonia Guajajara",
      uf: "SP"
    });

    expect(result.response.alerts).toContain(
      "Nenhuma evidencia oficial foi coletada para a consulta."
    );
    expect(result.response.signals.evidence_level.status).toBe("insufficient");
    expect(result.response.signals.integrity.status).toBe("insufficient");
    expect(result.execution.status).toBe("completed");
    expect(result.execution.steps).toContain("evidence_collected");
  });

  it("returns explicit identity metadata when the name remains ambiguous", async () => {
    const evidenceCollector = {
      collect: vi.fn()
    };
    const evidenceStore = {
      save: vi.fn()
    };
    const orchestrator = new QueryOrchestrator({
      evidenceCollector,
      evidenceStore,
      identityResolver: {
        resolve: vi.fn().mockResolvedValue({
          ambiguity_level: "strong",
          candidates: [
            {
              ambiguity_level: "none",
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
              canonical_name: "Joao Silva",
              office: "deputado_federal",
              official_ids: {
                tse_id: "333"
              },
              party: "MDB",
              status: "challenger",
              uf: "MG"
            }
          ],
          kind: "ambiguous",
          match_count: 2,
          requires: ["uf", "party"]
        } satisfies IdentityResolution)
      }
    });

    const result = await orchestrator.consult({
      candidate_name: "Joao Silva"
    });

    expect(evidenceCollector.collect).not.toHaveBeenCalled();
    expect(evidenceStore.save).not.toHaveBeenCalled();
    expect(result.response.candidate.ambiguity_level).toBe("strong");
    expect(result.response.candidate.match_count).toBe(2);
    expect(result.response.candidate.requires).toEqual(["uf", "party"]);
    expect(result.response.candidate.resolution_kind).toBe("ambiguous");
    expect(result.response.alerts).toContain(
      "Identidade ambigua. Informe uf e party para continuar."
    );
    expect(result.execution.steps).toEqual([
      "request_validated",
      "identity_ambiguous",
      "response_assembled"
    ]);
  });
});
