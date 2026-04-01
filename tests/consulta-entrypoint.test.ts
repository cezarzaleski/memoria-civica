import { describe, expect, it, vi } from "vitest";

import { parseConsultaCliArgs, runConsultaEntrypoint } from "@/cli/consulta-entrypoint";
import type { ConsultationResponse } from "@/domain/models";

function parsePayload(raw: unknown): ConsultationResponse {
  return JSON.parse(typeof raw === "string" ? raw : "{}") as ConsultationResponse;
}

describe("consulta entrypoint", () => {
  it("parses CLI flags into the canonical request shape", () => {
    expect(
      parseConsultaCliArgs([
        "--candidate",
        "Tabata Amaral",
        "--office",
        "deputado_federal",
        "--uf",
        "sp",
        "--party",
        "psb",
        "--priority",
        "educacao",
        "--priority",
        "transparencia"
      ])
    ).toEqual({
      candidate_name: "Tabata Amaral",
      office: "deputado_federal",
      party: "psb",
      uf: "sp",
      user_priorities: ["educacao", "transparencia"]
    });
  });

  it("writes the orchestrated response to stdout as formatted JSON", async () => {
    const stderrWrite = vi.fn();
    const write = vi.fn();

    await runConsultaEntrypoint(
      ["--candidate", "Tabata Amaral", "--office", "deputado_federal"],
      {
        stderr: { write: stderrWrite },
        stdout: { write }
      },
      {
        consult: vi.fn().mockResolvedValue({
          execution: {
            duration_ms: 4,
            started_at: "2026-03-29T00:00:00.000Z",
            status: "completed",
            steps: [
              "request_validated",
              "identity_resolved",
              "collection_planned",
              "response_assembled"
            ],
            trace_id: "trace-1"
          },
          response: {
            alerts: [
              "Coleta oficial ainda insuficiente para conclusao final.",
              "Cobertura atual de coherence na Camara: coletados=formal_activity_record, propositions_summary; faltam=voting_summary."
            ],
            candidate: {
              ambiguity_level: "none",
              canonical_name: "Tabata Amaral",
              match_count: 1,
              official_ids: {
                camara_id: "204534"
              },
              party: "PSB",
              resolution_kind: "resolved",
              status: "incumbent",
              uf: "SP"
            },
            confidence: "high",
            observability: {
              coherence: {
                collected_evidence_ids: ["ev-1", "ev-2"],
                collected_types: [
                  "formal_activity_record",
                  "propositions_summary"
                ],
                expected_types: [
                  "formal_activity_record",
                  "voting_summary",
                  "propositions_summary"
                ],
                limitation:
                  "Coherence usa atuacao formal, proposicoes autorais e votos nominais recentes da Camara; relatoria ainda nao foi integrada e votos nominais seguem parciais.",
                missing_types: ["voting_summary"],
                scope: "camara",
                status_basis: "positive"
              }
            },
            reasons: [
              "Ha 2 evidencias oficiais em 2 fontes independentes.",
              "Ha registro oficial relacionado a integridade, sem alerta grave classificado.",
              "Ha cobertura oficial da Camara em 2 blocos independentes de coerencia: formal_activity_record, propositions_summary."
            ],
            signals: {
              coherence: {
                evidence_ids: ["ev-1", "ev-2"],
                reasons: [
                  "Ha cobertura oficial da Camara em 2 blocos independentes de coerencia: formal_activity_record, propositions_summary."
                ],
                status: "positive"
              },
              evidence_level: {
                evidence_ids: ["ev-3", "ev-4"],
                reasons: ["Ha 2 evidencias oficiais em 2 fontes independentes."],
                status: "positive"
              },
              integrity: {
                evidence_ids: ["ev-5"],
                reasons: [
                  "Ha registro oficial relacionado a integridade, sem alerta grave classificado."
                ],
                status: "mixed"
              },
              values_fit: {
                evidence_ids: [],
                reasons: ["Sem coleta de evidencias nesta fase."],
                status: "insufficient"
              }
            },
            sources: [
              "https://dadosabertos.camara.leg.br/api/v2/deputados/204534",
              "https://dadosabertos.camara.leg.br/api/v2/proposicoes?idDeputadoAutor=204534"
            ],
            summary:
              "A consulta encontrou base oficial inicial para Tabata Amaral, mas a leitura ainda exige cautela.",
            traffic_light: "yellow"
          }
        })
      }
    );

    expect(write).toHaveBeenCalledOnce();
    expect(stderrWrite).toHaveBeenCalledOnce();

    const payload = parsePayload(write.mock.calls[0]?.[0]);

    expect(payload).toMatchObject({
      candidate: {
        canonical_name: "Tabata Amaral",
        official_ids: {
          camara_id: "204534"
        },
        status: "incumbent"
      },
      observability: {
        coherence: {
          collected_types: [
            "formal_activity_record",
            "propositions_summary"
          ],
          missing_types: ["voting_summary"],
          scope: "camara",
          status_basis: "positive"
        }
      },
      signals: {
        coherence: {
          status: "positive"
        },
        evidence_level: {
          status: "positive"
        },
        integrity: {
          status: "mixed"
        },
        values_fit: {
          status: "insufficient"
        }
      },
      summary:
        "A consulta encontrou base oficial inicial para Tabata Amaral, mas a leitura ainda exige cautela.",
      traffic_light: "yellow"
    });

    expect(stderrWrite.mock.calls[0]?.[0]).toContain(
      "[trace=trace-1] status=completed duration_ms=4"
    );
  });

  it("preserves a deterministic gray contract when the orchestrator returns no evidence", async () => {
    const stderrWrite = vi.fn();
    const write = vi.fn();

    await runConsultaEntrypoint(
      ["--candidate", "Nome Teste", "--office", "deputado_federal"],
      {
        stderr: { write: stderrWrite },
        stdout: { write }
      },
      {
        consult: vi.fn().mockResolvedValue({
          execution: {
            duration_ms: 2,
            started_at: "2026-03-29T00:00:00.000Z",
            status: "completed",
            steps: [
              "request_validated",
              "identity_resolved",
              "response_assembled"
            ],
            trace_id: "trace-2"
          },
          response: {
            alerts: ["Nenhuma evidencia oficial foi coletada para a consulta."],
            candidate: {
              canonical_name: "Nome Teste",
              official_ids: {},
              status: "challenger"
            },
            confidence: "low",
            reasons: ["Nao foi possivel coletar evidencias oficiais para sustentar uma conclusao."],
            signals: {
              coherence: { evidence_ids: [], reasons: [], status: "insufficient" },
              evidence_level: {
                evidence_ids: [],
                reasons: ["Sem coleta de evidencias nesta fase."],
                status: "insufficient"
              },
              integrity: { evidence_ids: [], reasons: [], status: "insufficient" },
              values_fit: { evidence_ids: [], reasons: [], status: "insufficient" }
            },
            sources: [],
            summary: "Sem base suficiente para uma conclusao nesta fase.",
            traffic_light: "gray"
          }
        })
      }
    );

    expect(write).toHaveBeenCalledOnce();
    expect(stderrWrite.mock.calls[0]?.[0]).toContain(
      "[trace=trace-2] status=completed duration_ms=2"
    );

    const payload = parsePayload(write.mock.calls[0]?.[0]);

    expect(payload.traffic_light).toBe("gray");
    expect(payload.observability).toBeUndefined();
  });

  it("exposes a concise disambiguation payload for ambiguous identities", async () => {
    const stderrWrite = vi.fn();
    const write = vi.fn();

    await runConsultaEntrypoint(
      ["--candidate", "Joao Silva", "--office", "deputado_federal"],
      {
        stderr: { write: stderrWrite },
        stdout: { write }
      },
      {
        consult: vi.fn().mockResolvedValue({
          execution: {
            duration_ms: 2,
            started_at: "2026-04-01T00:00:00.000Z",
            status: "completed",
            steps: [
              "request_validated",
              "identity_ambiguous",
              "response_assembled"
            ],
            trace_id: "trace-ambiguity-1"
          },
          response: {
            alerts: [
              "Faltou contexto para identificar a pessoa certa. Informe UF e o partido para continuar."
            ],
            candidate: {
              ambiguity_level: "strong",
              canonical_name: "Joao Silva",
              match_count: 2,
              official_ids: {},
              requires: ["uf", "party"],
              resolution_kind: "ambiguous",
              status: "challenger"
            },
            confidence: "low",
            reasons: [
              "Faltou contexto para identificar a pessoa certa. Informe UF e o partido para continuar."
            ],
            signals: {
              coherence: { evidence_ids: [], reasons: [], status: "insufficient" },
              evidence_level: {
                evidence_ids: [],
                reasons: [
                  "Faltou contexto para identificar a pessoa certa. Informe UF e o partido para continuar."
                ],
                status: "insufficient"
              },
              integrity: { evidence_ids: [], reasons: [], status: "insufficient" },
              values_fit: { evidence_ids: [], reasons: [], status: "insufficient" }
            },
            sources: [],
            summary:
              "A consulta parou na etapa de identidade porque faltou contexto para identificar a pessoa certa.",
            traffic_light: "gray"
          }
        })
      }
    );

    expect(write).toHaveBeenCalledOnce();
    expect(stderrWrite.mock.calls[0]?.[0]).toContain(
      "[trace=trace-ambiguity-1] status=completed duration_ms=2"
    );

    const payload = parsePayload(write.mock.calls[0]?.[0]);

    expect(payload.candidate).toMatchObject({
      canonical_name: "Joao Silva",
      requires: ["uf", "party"],
      resolution_kind: "ambiguous"
    });
    expect(payload.summary).toBe(
      "A consulta parou na etapa de identidade porque faltou contexto para identificar a pessoa certa."
    );
    expect(payload.alerts).toEqual([
      "Faltou contexto para identificar a pessoa certa. Informe UF e o partido para continuar."
    ]);
    expect(payload.traffic_light).toBe("gray");
  });

  it("does not leak review queue metadata into the functional stdout payload", async () => {
    const stderrWrite = vi.fn();
    const write = vi.fn();

    await runConsultaEntrypoint(
      ["--candidate", "Nome Sensivel", "--office", "deputado_federal"],
      {
        stderr: { write: stderrWrite },
        stdout: { write }
      },
      {
        consult: vi.fn().mockResolvedValue({
          execution: {
            duration_ms: 3,
            started_at: "2026-04-01T00:00:00.000Z",
            status: "completed",
            steps: [
              "request_validated",
              "identity_resolved",
              "evidence_collected",
              "response_assembled"
            ],
            trace_id: "trace-review-1",
            observability: {
              review_queue: [
                {
                  evidence_ids: ["ev-1"],
                  message:
                    "Consulta marcada para revisao por caso sensivel de integridade detectado nas evidencias coletadas.",
                  reason: "integrity_sensitive_case"
                }
              ]
            }
          },
          response: {
            alerts: ["Coleta oficial ainda insuficiente para conclusao final."],
            candidate: {
              canonical_name: "Nome Sensivel",
              official_ids: {},
              status: "former"
            },
            confidence: "low",
            reasons: ["Foram coletadas 1 evidencias oficiais iniciais."],
            signals: {
              coherence: { evidence_ids: [], reasons: [], status: "insufficient" },
              evidence_level: {
                evidence_ids: ["ev-1"],
                reasons: ["Foram coletadas 1 evidencias oficiais iniciais."],
                status: "mixed"
              },
              integrity: {
                evidence_ids: ["ev-1"],
                reasons: ["Ha registro oficial relacionado a integridade."],
                status: "negative"
              },
              values_fit: { evidence_ids: [], reasons: [], status: "insufficient" }
            },
            sources: ["https://tre.example/caso/1"],
            summary: "A consulta encontrou alerta oficial de integridade para Nome Sensivel.",
            traffic_light: "red"
          }
        })
      }
    );

    const payload = parsePayload(write.mock.calls[0]?.[0]);

    expect(payload.observability).toBeUndefined();
    expect("review_queue" in payload).toBe(false);
    expect(stderrWrite.mock.calls[0]?.[0]).toContain(
      "[trace=trace-review-1] status=completed duration_ms=3"
    );
  });
});
