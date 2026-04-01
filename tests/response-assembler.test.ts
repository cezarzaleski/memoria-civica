import { describe, expect, it } from "vitest";

import { ResponseAssembler } from "@/services/response-assembler";
import type { ResolvedCandidate, SignalAssessment } from "@/domain/models";

describe("ResponseAssembler", () => {
  const candidate: ResolvedCandidate = {
    ambiguity_level: "none",
    canonical_name: "Erika Hilton",
    office: "deputado_federal",
    official_ids: {
      camara_id: "220639"
    },
    status: "incumbent",
    uf: "SP"
  };

  it("keeps gray and low confidence when evidence_level is insufficient", () => {
    const assembler = new ResponseAssembler();
    const signals: Record<string, SignalAssessment> = {
      coherence: { evidence_ids: [], reasons: ["Sem base"], status: "insufficient" },
      evidence_level: { evidence_ids: [], reasons: ["Sem base"], status: "insufficient" },
      integrity: { evidence_ids: [], reasons: ["Sem base"], status: "insufficient" },
      values_fit: { evidence_ids: [], reasons: ["Sem base"], status: "insufficient" }
    };

    const response = assembler.assemble({
      alerts: ["Nenhuma evidencia oficial foi coletada para a consulta."],
      candidate,
      signals,
      sources: []
    });

    expect(response.traffic_light).toBe("gray");
    expect(response.confidence).toBe("low");
    expect(response.observability).toBeUndefined();
  });

  it("returns yellow when there is some evidence but no grave integrity alert", () => {
    const assembler = new ResponseAssembler();
    const signals: Record<string, SignalAssessment> = {
      coherence: { evidence_ids: ["ev-1"], reasons: ["Ha base minima"], status: "mixed" },
      evidence_level: {
        evidence_ids: ["ev-1"],
        reasons: ["Ha evidencia oficial, mas de uma unica fonte."],
        status: "mixed"
      },
      integrity: {
        evidence_ids: ["ev-2"],
        reasons: ["Ha registro oficial relacionado a integridade."],
        status: "mixed"
      },
      values_fit: { evidence_ids: [], reasons: ["Sem base"], status: "insufficient" }
    };

    const response = assembler.assemble({
      alerts: ["Coleta oficial ainda insuficiente para conclusao final."],
      candidate,
      observability: {
        coherence: {
          collected_evidence_ids: ["ev-1"],
          collected_types: ["formal_activity_record"],
          expected_types: [
            "formal_activity_record",
            "voting_summary",
            "propositions_summary"
          ],
          limitation: "Limitation",
          missing_types: ["voting_summary", "propositions_summary"],
          scope: "camara",
          status_basis: "mixed"
        }
      },
      signals,
      sources: ["https://dadosabertos.camara.leg.br/api/v2/deputados/220639"]
    });

    expect(response.traffic_light).toBe("yellow");
    expect(response.confidence).toBe("medium");
    expect(response.observability?.coherence?.collected_types).toEqual([
      "formal_activity_record"
    ]);
  });

  it("returns red when integrity has an official alert", () => {
    const assembler = new ResponseAssembler();
    const signals: Record<string, SignalAssessment> = {
      coherence: { evidence_ids: ["ev-1"], reasons: ["Ha base minima"], status: "mixed" },
      evidence_level: {
        evidence_ids: ["ev-1", "ev-2"],
        reasons: ["Ha base em duas fontes."],
        status: "positive"
      },
      integrity: {
        evidence_ids: ["ev-3"],
        reasons: ["Ha alerta oficial de integridade que exige cautela."],
        status: "negative"
      },
      values_fit: { evidence_ids: [], reasons: ["Sem base"], status: "insufficient" }
    };

    const response = assembler.assemble({
      alerts: [],
      candidate,
      signals,
      sources: ["https://dadosabertos.camara.leg.br/api/v2/deputados/220639"]
    });

    expect(response.traffic_light).toBe("red");
    expect(response.confidence).toBe("high");
  });
});
