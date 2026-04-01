import { describe, expect, it, vi } from "vitest";

import type { ConsultationResponse } from "@/domain/models";
import { routeApiRequest } from "../apps/api/src/app";
import type { ConsultPort } from "../apps/api/src/routes/consultas";

function buildGrayAmbiguousResponse(): ConsultationResponse {
  return {
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
  };
}

describe("API consultas", () => {
  it("returns the functional consultation payload for a valid request", async () => {
    const consult = vi.fn().mockResolvedValue({
      execution: {
        duration_ms: 4,
        started_at: "2026-04-01T00:00:00.000Z",
        status: "completed",
        steps: ["request_validated", "response_assembled"],
        trace_id: "trace-api-1"
      },
      response: {
        alerts: [],
        candidate: {
          ambiguity_level: "none",
          canonical_name: "Tabata Amaral",
          match_count: 1,
          official_ids: { camara_id: "204534" },
          party: "PSB",
          resolution_kind: "resolved",
          status: "incumbent",
          uf: "SP"
        },
        confidence: "high",
        reasons: ["Ha base oficial inicial suficiente para a consulta."],
        signals: {
          coherence: {
            evidence_ids: ["ev-1"],
            reasons: ["Ha cobertura oficial observavel."],
            status: "positive"
          },
          evidence_level: {
            evidence_ids: ["ev-1"],
            reasons: ["Ha 1 evidencia oficial forte."],
            status: "positive"
          },
          integrity: {
            evidence_ids: [],
            reasons: ["Sem alerta grave classificado."],
            status: "mixed"
          },
          values_fit: {
            evidence_ids: [],
            reasons: ["Sem prioridade informada nesta fase."],
            status: "insufficient"
          }
        },
        sources: ["https://dadosabertos.camara.leg.br/api/v2/deputados/204534"],
        summary:
          "A consulta encontrou base oficial inicial para Tabata Amaral, mas a leitura ainda exige cautela.",
        traffic_light: "yellow"
      } satisfies ConsultationResponse
    });

    const response = await routeApiRequest(
      {
        method: "POST",
        pathname: "/consultas",
        payload: {
        candidate_name: "Tabata Amaral",
        office: "deputado_federal",
        uf: "sp"
        }
      },
      { consult } satisfies ConsultPort
    );

    expect(response.statusCode).toBe(200);
    expect(consult).toHaveBeenCalledWith({
      candidate_name: "Tabata Amaral",
      office: "deputado_federal",
      party: undefined,
      uf: "SP",
      user_priorities: []
    });
    expect((response.payload as ConsultationResponse).candidate.canonical_name).toBe(
      "Tabata Amaral"
    );
    expect((response.payload as ConsultationResponse).traffic_light).toBe("yellow");
  });

  it("returns a consistent validation error without leaking stack traces", async () => {
    const consult = vi.fn();
    const response = await routeApiRequest(
      {
        method: "POST",
        pathname: "/consultas",
        payload: {
          office: "deputado_federal"
        }
      },
      { consult } satisfies ConsultPort
    );

    expect(response.statusCode).toBe(400);
    expect(consult).not.toHaveBeenCalled();
    expect(response.payload).toEqual({
      error: {
        code: "VALIDATION_ERROR",
        message: "candidate_name is required"
      }
    });
  });

  it("preserves the ambiguity payload when the orchestrator asks for more context", async () => {
    const consult = vi.fn().mockResolvedValue({
      execution: {
        duration_ms: 2,
        started_at: "2026-04-01T00:00:00.000Z",
        status: "completed",
        steps: ["request_validated", "identity_ambiguous", "response_assembled"],
        trace_id: "trace-api-2"
      },
      response: buildGrayAmbiguousResponse()
    });

    const response = await routeApiRequest(
      {
        method: "POST",
        pathname: "/consultas",
        payload: {
          candidate_name: "Joao Silva"
        }
      },
      { consult } satisfies ConsultPort
    );

    expect(response.statusCode).toBe(200);
    const payload = response.payload as ConsultationResponse;
    expect(payload.candidate.requires).toEqual(["uf", "party"]);
    expect(payload.summary).toBe(
      "A consulta parou na etapa de identidade porque faltou contexto para identificar a pessoa certa."
    );
    expect(payload.alerts).toEqual([
      "Faltou contexto para identificar a pessoa certa. Informe UF e o partido para continuar."
    ]);
  });
});
