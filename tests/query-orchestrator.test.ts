import { describe, expect, it, vi } from "vitest";

import { QueryOrchestrator } from "@/services/query-orchestrator";
import type {
  EvidenceRecord,
  RawEvidence,
  IdentityResolution,
  ResolvedCandidate
} from "@/domain/models";
import type { CacheStore } from "@/services/cache-store";
import { InMemoryCacheStore } from "@/services/cache-store";

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
      "Coherence usa atuacao formal, proposicoes autorais e votos nominais recentes da Camara; relatoria ainda nao foi integrada e votos nominais seguem parciais."
    );
    expect(result.response.alerts).toContain(
      "Cobertura atual de coherence na Camara: coletados=formal_activity_record; faltam=voting_summary, propositions_summary."
    );
    expect(result.response.sources).toEqual([
      "https://dadosabertos.camara.leg.br/api/v2/deputados/220639"
    ]);
    expect(result.response.signals.evidence_level.status).toBe("mixed");
    expect(result.response.signals.evidence_level.evidence_ids).toEqual(["ev-1"]);
    expect(result.response.signals.coherence.status).toBe("mixed");
    expect(result.response.signals.coherence.evidence_ids).toEqual(["ev-2"]);
    expect(result.response.signals.coherence.reasons).toEqual([
      "Ha cobertura oficial da Camara em 1 bloco de coerencia: formal_activity_record. Ainda faltam: voting_summary, propositions_summary."
    ]);
    expect(result.response.observability?.coherence).toEqual({
      collected_evidence_ids: ["ev-2"],
      collected_types: ["formal_activity_record"],
      expected_types: [
        "formal_activity_record",
        "voting_summary",
        "propositions_summary"
      ],
      limitation:
        "Coherence usa atuacao formal, proposicoes autorais e votos nominais recentes da Camara; relatoria ainda nao foi integrada e votos nominais seguem parciais.",
      missing_types: ["voting_summary", "propositions_summary"],
      scope: "camara",
      status_basis: "mixed"
    });
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
    expect(result.response.observability).toBeUndefined();
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
    expect(result.response.observability).toBeUndefined();
    expect(result.execution.observability?.review_queue).toEqual([
      {
        message: "Consulta parada por ambiguidade forte de identidade; revisao humana necessaria.",
        reason: "identity_ambiguity",
        requires: ["uf", "party"]
      }
    ]);
    expect(result.execution.steps).toEqual([
      "request_validated",
      "identity_ambiguous",
      "response_assembled"
    ]);
  });

  it("records review queue metadata for sensitive integrity evidence", async () => {
    const candidate: ResolvedCandidate = {
      ambiguity_level: "none",
      canonical_name: "Candidato Sensivel",
      office: "deputado_federal",
      official_ids: {
        tse_id: "987654321"
      },
      status: "former",
      uf: "SP"
    };

    const evidence: EvidenceRecord[] = [
      {
        collected_at: "2026-04-01T10:00:00.000Z",
        evidence_id: "ev-integrity-alert",
        evidence_type: "integrity_alert",
        person_id: "tse:987654321",
        signal_type: "integrity",
        source_name: "tre-sp",
        source_url: "https://tre-sp.jus.br/caso/987654321",
        strength: "strong_official",
        summary: "Processo eleitoral com representacao formal em andamento."
      }
    ];

    const orchestrator = new QueryOrchestrator({
      evidenceCollector: {
        collect: vi.fn().mockResolvedValue(evidence)
      },
      evidenceStore: {
        save: vi.fn().mockResolvedValue(evidence)
      },
      identityResolver: {
        resolve: vi.fn().mockResolvedValue({
          ambiguity_level: "none",
          candidate,
          kind: "resolved",
          match_count: 1
        } satisfies IdentityResolution)
      }
    });

    const result = await orchestrator.consult({
      candidate_name: "Candidato Sensivel",
      uf: "SP"
    });

    expect(result.response.traffic_light).toBe("red");
    expect(result.execution.observability?.review_queue).toEqual([
      {
        evidence_ids: ["ev-integrity-alert"],
        message:
          "Consulta marcada para revisao por caso sensivel de integridade detectado nas evidencias coletadas.",
        reason: "integrity_sensitive_case"
      }
    ]);
  });

  it("records review queue metadata when complementary journalism is used", async () => {
    const candidate: ResolvedCandidate = {
      ambiguity_level: "none",
      canonical_name: "Candidata Editorial",
      office: "deputado_federal",
      official_ids: {
        tse_id: "555"
      },
      status: "challenger",
      uf: "RJ"
    };

    const evidence: EvidenceRecord[] = [
      {
        collected_at: "2026-04-01T11:00:00.000Z",
        evidence_id: "ev-journalism-1",
        evidence_type: "news_screening",
        person_id: "tse:555",
        signal_type: "values_fit",
        source_name: "jornal-local",
        source_url: "https://jornal.local/reportagem/1",
        strength: "complementary",
        summary: "Cobertura jornalistica complementar usada como contexto tematico."
      }
    ];

    const orchestrator = new QueryOrchestrator({
      evidenceCollector: {
        collect: vi.fn().mockResolvedValue(evidence)
      },
      evidenceStore: {
        save: vi.fn().mockResolvedValue(evidence)
      },
      identityResolver: {
        resolve: vi.fn().mockResolvedValue({
          ambiguity_level: "none",
          candidate,
          kind: "resolved",
          match_count: 1
        } satisfies IdentityResolution)
      }
    });

    const result = await orchestrator.consult({
      candidate_name: "Candidata Editorial",
      uf: "RJ",
      user_priorities: ["transparencia"]
    });

    expect(result.execution.observability?.review_queue).toEqual([
      {
        evidence_ids: ["ev-journalism-1"],
        message:
          "Consulta marcada para revisao editorial por uso de evidencia complementar como apoio de sinal.",
        reason: "complementary_journalism"
      }
    ]);
    expect(result.response.signals.values_fit.status).toBe("insufficient");
  });

  it("does not mark review queue for complementary non-journalistic evidence", async () => {
    const candidate: ResolvedCandidate = {
      ambiguity_level: "none",
      canonical_name: "Candidato Fonte Complementar",
      office: "deputado_federal",
      official_ids: {
        tse_id: "777"
      },
      status: "challenger",
      uf: "BA"
    };

    const evidence: EvidenceRecord[] = [
      {
        collected_at: "2026-04-01T12:00:00.000Z",
        evidence_id: "ev-complementary-1",
        evidence_type: "external_dataset",
        person_id: "tse:777",
        signal_type: "values_fit",
        source_name: "instituto-parceiro",
        source_url: "https://dados.parceiro.org/base/1",
        strength: "complementary",
        summary: "Base complementar de contexto tematico sem origem jornalistica."
      }
    ];

    const orchestrator = new QueryOrchestrator({
      evidenceCollector: {
        collect: vi.fn().mockResolvedValue(evidence)
      },
      evidenceStore: {
        save: vi.fn().mockResolvedValue(evidence)
      },
      identityResolver: {
        resolve: vi.fn().mockResolvedValue({
          ambiguity_level: "none",
          candidate,
          kind: "resolved",
          match_count: 1
        } satisfies IdentityResolution)
      }
    });

    const result = await orchestrator.consult({
      candidate_name: "Candidato Fonte Complementar",
      uf: "BA",
      user_priorities: ["educacao"]
    });

    expect(result.execution.observability?.review_queue).toBeUndefined();
  });

  it("records cache telemetry by scope across repeated identical consultations", async () => {
    const candidate: ResolvedCandidate = {
      ambiguity_level: "none",
      canonical_name: "Tabata Amaral",
      office: "deputado_federal",
      official_ids: {
        camara_id: "204534"
      },
      party: "PSB",
      status: "incumbent",
      uf: "SP"
    };
    const cacheStore: CacheStore = new InMemoryCacheStore();
    const rawEvidenceCollector = {
      collect: vi.fn().mockResolvedValue([
        {
          collected_at: "2026-04-01T12:00:00.000Z",
          evidence_type: "formal_activity_record",
          person_id: "camara:204534",
          signal_type: "coherence",
          source_name: "camara",
          source_url: "https://dadosabertos.camara.leg.br/api/v2/deputados/204534",
          strength: "strong_official",
          summary: "Perfil formal na Camara."
        }
      ] satisfies RawEvidence[])
    };
    const orchestrator = new QueryOrchestrator({
      cacheStore,
      identityCatalog: [candidate],
      identitySources: [],
      rawEvidenceCollector
    });

    const firstResult = await orchestrator.consult({
      candidate_name: "Tabata Amaral",
      uf: "SP"
    });
    const secondResult = await orchestrator.consult({
      candidate_name: "Tabata Amaral",
      uf: "SP"
    });

    expect(rawEvidenceCollector.collect).toHaveBeenCalledTimes(1);
    expect(firstResult.execution.observability?.cache).toEqual({
      evidence: "miss",
      identity: "miss",
      signal: "miss"
    });
    expect(secondResult.execution.observability?.cache).toEqual({
      evidence: "hit",
      identity: "hit",
      signal: "hit"
    });
  });

});
